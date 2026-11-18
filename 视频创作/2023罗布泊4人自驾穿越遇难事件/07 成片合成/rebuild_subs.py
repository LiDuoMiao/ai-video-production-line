# -*- coding: utf-8 -*-
"""由时间轴.json 的 P 段时点重建字幕（不重渲画面）。断行优先在标点处，避免断词。"""
import json, os, re

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
S07 = BASE + "/07 成片合成"
SUB = BASE + "/05 脚本分镜/口播稿-字幕显示版.md"

blocks = re.split(r"\nP(\d\d)\n", open(SUB, encoding="utf-8").read())
seg = {int(blocks[i]): re.sub(r"\n", "", blocks[i+1].strip()) for i in range(1, len(blocks), 2)}
P = {k: tuple(v) for k, v in json.load(open(S07 + "/时间轴.json"))["p_times"].items()}

LIMIT = 26
PUNCT = "，。？！；：、"


def split_text(txt):
    parts, cur = [], ""
    for ch in txt:
        cur += ch
        if ch in "。？！" and len(cur) >= 6:
            parts.append(cur); cur = ""
        elif ch in "，；：" and len(cur) >= LIMIT:
            parts.append(cur); cur = ""
    if cur.strip():
        parts.append(cur)
    cues = []
    for p in parts:
        p = p.strip()
        if len(p) <= LIMIT:
            cues.append(p); continue
        mid = len(p) // 2
        cand = [i for i, c in enumerate(p) if c in PUNCT and 8 <= i <= len(p) - 6]
        cut = min(cand, key=lambda i: abs(i - mid)) if cand else mid
        cues.append(p[:cut+1].strip() + "\\N" + p[cut+1:].strip())
    return cues


def srt_t(x):
    h = int(x // 3600); m = int((x % 3600) // 60); s = int(x % 60); ms = int(round((x - int(x)) * 1000))
    if ms == 1000: s += 1; ms = 0
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def ass_t(x):
    tot = int(round(x * 100)); h = tot // 360000; m = (tot // 6000) % 60; s = (tot // 100) % 60; cs = tot % 100
    return f"{h}:{m:02d}:{s:02d}.{cs:02d}"


srt, ass = [], []
head = ["[Script Info]", "ScriptType: v4.00+", "PlayResX: 1920", "PlayResY: 1080", "WrapStyle: 2", "",
        "[V4+ Styles]",
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
        "Style: Narr,Hiragino Sans GB,44,&H00FFFFFF,&H00FFFFFF,&H2A000000,&H2A000000,--0,0,0,0,100,100,0,0,3,8,0,2,90,90,92,1",
        "", "[Events]", "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"]
n = 0
for pk in sorted(P):
    s, e = P[pk]
    cues = split_text(seg[int(pk[1:])])
    total = sum(len(c) for c in cues)
    acc = 0
    for c in cues:
        st = s + (e - s) * acc / total
        acc += len(c)
        en = s + (e - s) * acc / total
        if en - st < 1.0:
            en = min(e, st + 1.0)
        n += 1
        srt.append((n, st, en, c.replace("\\N", "\n")))
        ass.append(f"Dialogue: 0,{ass_t(st)},{ass_t(en)},Narr,,0,0,0,,{c}")

open(S07 + "/字幕.srt", "w", encoding="utf-8").write(
    "".join(f"{i}\n{srt_t(a)} --> {srt_t(b)}\n{t}\n\n" for i, a, b, t in srt))
open(S07 + "/字幕.ass", "w", encoding="utf-8").write("\n".join(head + ass) + "\n")
print("cues", n)
