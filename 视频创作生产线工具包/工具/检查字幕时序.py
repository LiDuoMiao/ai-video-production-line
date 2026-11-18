#!/usr/bin/env python3
"""Read-only timing checks for one narration subtitle track; standard library only."""

import argparse
from collections import defaultdict
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
import hashlib
import json
from pathlib import Path
import re
import sys


VERSION = "1.0"
EPSILON = Decimal("0.000001")  # Numerical noise only; never a frame-sized allowance.


class InputError(ValueError):
    pass


@dataclass(frozen=True)
class Cue:
    source: str
    start: Decimal
    end: Decimal
    text: str
    track: str = "narration"


def seconds(value, label):
    if isinstance(value, bool) or not isinstance(value, (str, int, float, Decimal)):
        raise InputError(f"{label} 必须是有限秒数")
    try:
        result = Decimal(str(value))
    except InvalidOperation as exc:
        raise InputError(f"{label} 不是有效秒数") from exc
    if not result.is_finite():
        raise InputError(f"{label} 必须是有限秒数")
    return result


def number(value):
    return format(value.normalize(), "f")


def timecode(value, kind, source):
    pattern = (r"(\d{2,}):([0-5]\d):([0-5]\d),(\d{3})"
               if kind == "srt" else r"(\d+):([0-5]\d):([0-5]\d)\.(\d{2})")
    match = re.fullmatch(pattern, value.strip())
    if not match:
        raise InputError(f"{source} 的{kind.upper()}时间码无效：{value}")
    h, m, s, fraction = match.groups()
    return (Decimal(int(h) * 3600 + int(m) * 60 + int(s))
            + Decimal(fraction) / (1000 if kind == "srt" else 100))


def checked_text(value, source):
    if not isinstance(value, str) or not value.strip():
        raise InputError(f"{source} 缺少非空字幕文本")
    return value


def reject_constant(value):
    raise InputError(f"JSON含非有限数值：{value}")


def read_json(text, tracks):
    data = json.loads(text, parse_float=Decimal, parse_constant=reject_constant)
    duration = data.get("duration") if isinstance(data, dict) else None
    rows = data.get("subtitles") if isinstance(data, dict) else data
    if not isinstance(rows, list):
        raise InputError("JSON须是字幕列表，或包含subtitles列表的时间轴")
    wanted = set(tracks or [])
    available = set()
    cues = []
    for i, row in enumerate(rows, 1):
        source = f"subtitles[{i}]"
        if not isinstance(row, dict):
            raise InputError(f"{source} 必须是对象")
        track = row.get("track", "narration")
        if not isinstance(track, str) or not track.strip():
            raise InputError(f"{source}.track 必须是非空轨名")
        available.add(track)
        if wanted and track not in wanted:
            continue
        if "start" not in row or "end" not in row:
            raise InputError(f"{source} 缺少start或end")
        cues.append(Cue(source, seconds(row["start"], source + ".start"),
                        seconds(row["end"], source + ".end"),
                        checked_text(row.get("text"), source), track))
    if wanted - available:
        raise InputError("未找到JSON轨：" + ", ".join(sorted(wanted - available)))
    return cues, duration, len(rows) - len(cues)


def read_srt(text):
    cues = []
    for i, block in enumerate(re.split(r"\n[ \t]*\n", text.strip()), 1):
        lines = block.splitlines()
        if lines and lines[0].strip().isdigit():
            lines = lines[1:]
        source = f"SRT条目[{i}]"
        if len(lines) < 2 or lines[0].count("-->") != 1:
            raise InputError(f"{source} 缺少时间行或文本")
        start, end = lines[0].split("-->")
        cues.append(Cue(source, timecode(start, "srt", source),
                        timecode(end, "srt", source),
                        checked_text("\n".join(lines[1:]), source)))
    return cues


def read_ass(text, styles):
    if not styles:
        raise InputError("ASS须用--ass-style明确选择互斥的口播字幕样式")
    wanted = set(styles)
    found = set()
    columns = None
    in_events = False
    cues = []
    ignored = 0
    for line_no, line in enumerate(text.splitlines(), 1):
        stripped = line.strip()
        if stripped.startswith("[") and stripped.endswith("]"):
            in_events = stripped.lower() == "[events]"
            columns = None
            continue
        if not in_events or ":" not in stripped:
            continue
        key, value = stripped.split(":", 1)
        if key.lower() == "format":
            columns = [field.strip().lower() for field in value.split(",")]
            required = {"start", "end", "style", "text"}
            if (not required.issubset(columns) or columns[-1] != "text"
                    or len(set(columns)) != len(columns)):
                raise InputError("ASS Events Format须含Start/End/Style且Text位于最后")
        elif key.lower() == "dialogue":
            source = f"ASS行[{line_no}]"
            if columns is None:
                raise InputError(f"{source} 之前没有有效的Events Format")
            fields = value.lstrip().split(",", len(columns) - 1)
            if len(fields) != len(columns):
                raise InputError(f"{source} 字段数量不符")
            row = dict(zip(columns, fields))
            style = row["style"].strip()
            if style not in wanted:
                ignored += 1
                continue
            found.add(style)
            cues.append(Cue(source, timecode(row["start"], "ass", source),
                            timecode(row["end"], "ass", source),
                            checked_text(row["text"], source)))
    if wanted - found:
        raise InputError("未找到ASS口播样式事件：" + ", ".join(sorted(wanted - found)))
    return cues, ignored


def check(cues, duration):
    if not cues:
        raise InputError("没有选中可检查的字幕；不能将空检查记为通过")
    issues = []
    groups = defaultdict(list)
    last_start = {}
    for cue in cues:
        if cue.start < last_start.get(cue.track, cue.start) - EPSILON:
            issues.append({"code": "out_of_order", "event": cue.source,
                           "track": cue.track, "at": number(cue.start)})
        last_start[cue.track] = cue.start
        if cue.end <= cue.start:
            issues.append({"code": "invalid_interval", "event": cue.source,
                           "start": number(cue.start), "end": number(cue.end)})
            continue
        if cue.start < -EPSILON or cue.end > duration + EPSILON:
            issues.append({"code": "out_of_bounds", "event": cue.source,
                           "start": number(cue.start), "end": number(cue.end)})
        groups[cue.track].append(cue)
    for track, group in groups.items():
        active = []
        for cue in sorted(group, key=lambda row: row.start):
            active = [other for other in active if other.end > cue.start + EPSILON]
            for other in active:
                overlap = min(other.end, cue.end) - cue.start
                if overlap > EPSILON:
                    issues.append({"code": "overlap", "track": track,
                                   "previous_event": other.source, "event": cue.source,
                                   "at": number(cue.start),
                                   "overlap_ms": number(overlap * 1000),
                                   "previous_text": other.text[:60], "text": cue.text[:60]})
            active.append(cue)
    summary = {code: sum(item["code"] == code for item in issues)
               for code in ("invalid_interval", "out_of_bounds", "out_of_order", "overlap")}
    return {"ok": not issues, "checked_events": len(cues),
            "tracks": sorted({cue.track for cue in cues}),
            "summary": summary, "issues": issues}


def main(argv=None):
    parser = argparse.ArgumentParser(description="只读检查口播字幕时序；不判断可读性、同步或听感")
    parser.add_argument("input", type=Path, help="最终SRT/ASS或已含实际显示时点的JSON")
    parser.add_argument("--duration", help="导出总长（秒）；SRT/ASS必填，JSON可用duration字段")
    parser.add_argument("--ass-style", action="append", help="ASS互斥口播样式，可重复；不选角标样式")
    parser.add_argument("--track", action="append", help="JSON轨名，可重复；多轨分别检查")
    args = parser.parse_args(argv)
    source = str(args.input.resolve())
    try:
        raw = args.input.read_bytes()
        text = raw.decode("utf-8-sig").replace("\r\n", "\n").replace("\r", "\n")
        kind = args.input.suffix.lower().lstrip(".")
        if kind != "ass" and args.ass_style:
            raise InputError("--ass-style只适用于ASS")
        if kind != "json" and args.track:
            raise InputError("--track只适用于JSON")
        embedded_duration = None
        ignored = 0
        if kind == "json":
            cues, embedded_duration, ignored = read_json(text, args.track)
        elif kind == "srt":
            cues = read_srt(text)
        elif kind == "ass":
            cues, ignored = read_ass(text, args.ass_style)
        else:
            raise InputError("仅支持UTF-8的JSON、SRT、ASS文件")
        value = args.duration if args.duration is not None else embedded_duration
        if value is None:
            raise InputError("缺少实际导出总长：请提供--duration，或JSON的duration字段")
        duration = seconds(value, "duration")
        if duration <= 0:
            raise InputError("duration必须大于0")
        report = check(cues, duration)
        report.update(tool_version=VERSION, input=source, format=kind,
                      input_sha256=hashlib.sha256(raw).hexdigest(),
                      duration_seconds=number(duration), ignored_events=ignored,
                      selection={"ass_styles": sorted(set(args.ass_style or [])),
                                 "json_tracks": sorted(set(args.track or []))})
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0 if report["ok"] else 1
    except (InputError, OSError, UnicodeError, json.JSONDecodeError) as exc:
        print(json.dumps({"ok": False, "tool_version": VERSION, "input": source,
                          "error": "input_error", "message": str(exc)},
                         ensure_ascii=False, indent=2))
        return 2


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main())
