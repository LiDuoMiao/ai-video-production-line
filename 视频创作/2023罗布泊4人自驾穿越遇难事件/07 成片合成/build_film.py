# -*- coding: utf-8 -*-
"""07 合成：按实际旁白时点排镜头、图卡与字幕，导出候选片。"""
import re, os, subprocess, json, math

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
S06 = BASE + "/06 配音与素材"
S07 = BASE + "/07 成片合成"
FF = "/opt/homebrew/bin/ffmpeg"
FP = "/opt/homebrew/bin/ffprobe"
FONT = "/System/Library/Fonts/Hiragino Sans GB.ttc"
FPS = 25
os.makedirs(S07 + "/clips", exist_ok=True)

# ---------- 1. 计算 P 段时点（与 06 记录同法） ----------
sub = open(BASE + "/05 脚本分镜/口播稿-字幕显示版.md", encoding="utf-8").read()
blocks = re.split(r"\nP(\d\d)\n", sub)
seg = {}
for i in range(1, len(blocks), 2):
    seg[int(blocks[i])] = re.sub(r"\n", "", blocks[i+1].strip())
scene_map = {1:(1,6),2:(7,10),3:(11,15),4:(16,20),5:(21,22),6:(23,26),7:(27,31),8:(32,37),9:(38,42),10:(43,45)}

def dur(path):
    out = subprocess.run([FP,"-v","error","-show_entries","format=duration","-of","default=nw=1:nk=1",path],
                         capture_output=True, text=True).stdout.strip()
    return float(out)

GAP = 0.4
# 用实际音频的静音位置校准句间切点（保守：预测点 ±3.5 秒内取最近静音）
SIL = json.load(open(S07 + "/静音中点.json"))
t = 0.0
P = {}
for s,(a,b) in scene_map.items():
    D = dur(f"{S06}/配音/S{s:02d}.wav")
    chars = {n: len(seg[n]) for n in range(a,b+1)}
    total = sum(chars.values())
    est, acc = [], 0
    for n in range(a,b+1):
        est.append(acc/total); acc += chars[n]
    bounds = est[1:]                     # 段内 n-1 个切点（相对比例）
    cand = SIL[str(s)]
    preds = [x*D for x in bounds]
    chosen, floor = [], 0.0
    for pv in preds:
        pool = [c for c in cand if c > floor and abs(c - pv) <= 3.5]
        pick = min(pool, key=lambda c: abs(c - pv)) if pool else pv
        pick = max(pick, floor + 1.0)
        chosen.append(pick); floor = pick
    edges = [0.0] + chosen + [D]
    for i, n in enumerate(range(a,b+1)):
        P[f"P{n:02d}"] = (t + edges[i], t + edges[i+1])
    t += D + GAP
VIDEO_END = P["P45"][1] + 1.2

# ---------- 2. 画面段（每段一张图，按 P 时间切片） ----------
IMG = S06 + "/画面"; CARD = S06 + "/图卡"
SEG = [
 ("J01", f"{IMG}/J01_荒漠空镜.png",      [("P01",1.0)],  "scene", "in"),
 ("J02", f"{IMG}/J02_沙地人影.png",      [("P02",1.0)],  "scene", "out"),
 ("J03", f"{CARD}/卡-01a_方位示意.png",   [("P03",1.0)],  "card",  "-"),
 ("J04", f"{CARD}/卡-01b_方位示意.png",   [("P04",1.0)],  "card",  "-"),
 ("J05", f"{CARD}/卡-01c_方位示意.png",   [("P05",1.0)],  "card",  "-"),
 ("J06", f"{CARD}/卡-00_核心提问.png",    [("P06",1.0)],  "card",  "-"),
 ("J07", f"{IMG}/J07_车队集结.png",      [("P07",1.0)],  "scene", "lr"),
 ("J08", f"{IMG}/J08_车队群像.png",      [("P08",1.0)],  "scene", "in"),
 ("J09", f"{IMG}/J09_装备后备厢.png",    [("P09",0.55)], "scene", "in"),
 ("J10", f"{CARD}/卡-02_七天路线.png",    [("P09",0.45)], "card",  "-"),
 ("J11", f"{IMG}/J11_两台皮卡.png",      [("P10",1.0)],  "scene", "lr"),
 ("J12", f"{IMG}/J12_保护区航拍.png",    [("P11",1.0)],  "scene", "in"),
 ("J13", f"{CARD}/材料_通告摘句.png",     [("P12",1.0)],  "card",  "-"),
 ("J14", f"{CARD}/卡-03_法条要点.png",    [("P13",1.0)],  "card",  "-"),
 ("J15a",f"{IMG}/J15_按压沙面.png",      [("P14",0.45)], "scene", "in"),
 ("J15b",f"{CARD}/卡-04_物资倍量.png",    [("P14",0.55)], "card",  "-"),
 ("J16", f"{CARD}/材料_警情通报.png",     [("P15",1.0)],  "card",  "-"),
 ("J17", f"{IMG}/J17_车辆陷沙.png",      [("P16",0.45)], "scene", "lr"),
 ("J18", f"{IMG}/J18_加油熄火.png",      [("P16",0.55)], "scene", "in"),
 ("J19", f"{IMG}/J19_围停商议.png",      [("P17",1.0)],  "scene", "out"),
 ("J20", f"{IMG}/J20_断管特写.png",      [("P18",1.0)],  "scene", "in"),
 ("J21", f"{CARD}/卡-05_燃油标号.png",    [("P19",1.0)],  "card",  "-"),
 ("J22", f"{IMG}/J22_静止车队.png",      [("P20",1.0)],  "scene", "lr"),
 ("J23", f"{CARD}/卡-06_分组示意.png",    [("P21",1.0)],  "card",  "-"),
 ("J24", f"{IMG}/J24_陆巡陷沙.png",      [("P22",0.45)], "scene", "in"),
 ("J25a",f"{IMG}/J25_车内等待.png",      [("P22",0.20)], "scene", "in"),
 ("J25b",f"{CARD}/卡-07_两小时.png",      [("P22",0.35)], "card",  "-"),
 ("J26", f"{IMG}/J26_皮卡陷沙坑.png",    [("P23",1.0)],  "scene", "in"),
 ("J27", f"{CARD}/卡-08_三物件.png",      [("P24",1.0)],  "card",  "-"),
 ("J28", f"{IMG}/J28_黄昏远景.png",      [("P25",1.0)],  "scene", "out"),
 ("J29", f"{IMG}/J29_脚印延伸.png",      [("P26",1.0)],  "scene", "in"),
 ("J30", f"{IMG}/J30_脚印分岔.png",      [("P27",1.0)],  "scene", "in"),
 ("J31", f"{CARD}/卡-01d_方位示意.png",   [("P28",1.0)],  "card",  "-"),
 ("J32", f"{IMG}/J32_正午白光.png",      [("P29",1.0)],  "scene", "in"),
 ("J33", f"{IMG}/J33_车内对照.png",      [("P30",1.0)],  "scene", "lr"),
 ("J34", f"{CARD}/卡-09_当时的算术.png",  [("P31",1.0)],  "card",  "-"),
 ("J35", f"{IMG}/J35_沙丘另一侧.png",    [("P32",1.0)],  "scene", "lr"),
 ("J36", f"{IMG}/J36_无人机升空.png",    [("P33",1.0)],  "scene", "in"),
 ("J37a",f"{IMG}/J37_徒步取水.png",      [("P34",0.55)], "scene", "in"),
 ("J37b",f"{CARD}/卡-16_石头摆字.png",    [("P34",0.45)], "card",  "-"),
 ("J38", f"{IMG}/J38_备胎油桶.png",      [("P35",0.60)], "scene", "in"),
 ("J39", f"{IMG}/J39_保障车驶来.png",    [("P35",0.40)], "scene", "in"),
 ("J40", f"{CARD}/卡-10_时间轴.png",      [("P36",1.0)],  "card",  "-"),
 ("J41", f"{CARD}/材料_警情通报.png",     [("P37",1.0)],  "card",  "-"),
 ("J42", f"{CARD}/卡-01e_方位示意.png",   [("P38",1.0)],  "card",  "-"),
 ("J43", f"{CARD}/卡-11a_原因清单.png",   [("P39",0.55)], "card",  "-"),
 ("J44", f"{CARD}/卡-11b_原因清单.png",   [("P39",0.45)], "card",  "-"),
 ("J45", f"{CARD}/卡-12_三种口径.png",    [("P40",1.0)],  "card",  "-"),
 ("J46", f"{CARD}/卡-11c_锁链.png",       [("P41",1.0)],  "card",  "-"),
 ("J47", f"{CARD}/卡-13_责任框架.png",    [("P42",1.0)],  "card",  "-"),
 ("J48", f"{CARD}/卡-14_结论边界.png",    [("P43",1.0)],  "card",  "-"),
 ("J49", f"{CARD}/材料_警情通报.png",     [("P44",1.0)],  "card",  "-"),
 ("J50", f"{IMG}/J50_风吹车辙.png",      [("P45",0.55)], "scene", "in"),
 ("J51", f"{CARD}/卡-15_结尾警句.png",    [("P45",0.45)], "card",  "-"),
]

# ---------- 3. 逐段生成画面 ----------
def render(idx, name, img, start, end, kind, motion):
    frames = max(2, int(round((end-start)*FPS)))
    out = f"{S07}/clips/{idx:02d}_{name}.mp4"
    label = ""
    if kind == "scene":
        label = (",drawtext=fontfile='%s':text='AI 情景再现':fontsize=24:fontcolor=white@0.8:"
                 "box=1:boxcolor=black@0.35:boxborderw=10:x=w-tw-40:y=36" % FONT)
    if kind == "card":
        vf = f"scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2:color=0xf3efe7"
    elif motion == "in":
        vf = ("scale=2880:-2,zoompan=z='min(1.001+0.0009*on,1.09)':x='iw/2-(iw/zoom/2)':"
              "y='ih/2-(ih/zoom/2)':d=%d:s=1920x1080:fps=%d" % (frames, FPS))
    elif motion == "out":
        vf = ("scale=2880:-2,zoompan=z='max(1.10-0.0009*on,1.001)':x='iw/2-(iw/zoom/2)':"
              "y='ih/2-(ih/zoom/2)':d=%d:s=1920x1080:fps=%d" % (frames, FPS))
    else:  # lr 缓慢平移
        vf = ("scale=2880:-2,zoompan=z='1.06':x='iw/2-(iw/zoom/2)+(on/%d-0.5)*60':"
              "y='ih/2-(ih/zoom/2)':d=%d:s=1920x1080:fps=%d" % (frames, frames, FPS))
    vf = vf + label + ",fade=t=in:st=0:d=0.35,fade=t=out:st=%.3f:d=0.35" % max(0.0,(end-start)-0.4)
    cmd = [FF,"-y","-v","error","-loop","1","-i",img,"-vf",vf,"-frames:v",str(frames),
           "-c:v","libx264","-preset","veryfast","-crf","18","-pix_fmt","yuv420p","-r",str(FPS),out]
    subprocess.run(cmd, check=True)
    return out

# 同一 P 段被多段共用时，按所有占用段的权重归一分配
plan = []
for jid,img,parts,kind,motion in SEG:
    for pk,ratio in parts:
        plan.append([jid,img,pk,ratio,kind,motion])
from collections import defaultdict
weights = defaultdict(float)
for row in plan:
    weights[row[2]] += row[3]
used = defaultdict(float)
order = []
i = 0
for row in plan:
    i += 1
    jid,img,pk,ratio,kind,motion = row
    s,e = P[pk]
    w = ratio/weights[pk]
    st = s + (e-s)*used[pk]
    en = st + (e-s)*w
    used[pk] += w
    path = render(i*10, re.sub(r"[^0-9A-Za-z]", "", jid)+"_0", img, st, en, kind, motion)
    order.append((jid,path,st,en))

# ---------- 4. 拼接 ----------
lst = S07 + "/clips/concat_list.txt"
with open(lst,"w") as f:
    for _,p,_,_ in order: f.write(f"file '{p}'\n")
base_mp4 = S07 + "/candidate_base.mp4"
subprocess.run([FF,"-y","-v","error","-f","concat","-safe","0","-i",lst,
                "-c:v","libx264","-preset","veryfast","-crf","19","-pix_fmt","yuv420p","-r",str(FPS),base_mp4], check=True)

# ---------- 5. 字幕 ----------
def ass_time(x):
    total=int(round(x*100)); h=total//360000; m=(total//6000)%60; s=(total//100)%60; cs=total%100
    return f"{h:d}:{m:02d}:{s:02d}.{cs:02d}"
def srt_time(x):
    h=int(x//3600); m=int((x%3600)//60); s=int(x%60); ms=int(round((x-int(x))*1000))
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

def split_text(txt, limit=18):
    parts, cur = [], ""
    for ch in txt:
        cur += ch
        if ch in "。？！" and len(cur) >= 8:
            parts.append(cur.strip()); cur = ""
        elif len(cur) >= limit and ch in "，、；":
            parts.append(cur.strip()); cur = ""
    if cur.strip(): parts.append(cur.strip())
    # 折成两行
    cues = []
    for p in parts:
        if len(p) > limit:
            mid = len(p)//2
            # 优先在标点处断
            cand = [i for i,c in enumerate(p) if c in "，、；：" and 6 <= i <= len(p)-6]
            cut = min(cand, key=lambda i: abs(i-mid)) if cand else mid
            cues.append(p[:cut+1] + "\\N" + p[cut+1:].lstrip())
        else:
            cues.append(p)
    return cues

ass = ['[Script Info]', 'ScriptType: v4.00+', 'PlayResX: 1920', 'PlayResY: 1080', 'WrapStyle: 2', '',
       '[V4+ Styles]',
       'Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding',
       'Style: Narr,Hiragino Sans GB,44,&H00FFFFFF,&H00FFFFFF,&H2A000000,&H2A000000,--0,0,0,0,100,100,0,0,3,8,0,2,90,90,92,1',
       'Style: Tag,Hiragino Sans GB,26,&H00D9C7B0,&H00D9C7B0,&H00201008,&H64000000,--0,0,0,0,100,100,0,0,1,1.6,0,2,60,60,120,1',
       '', '[Events]', 'Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text']
srt_entries = []
for pk,(s,e) in P.items():
    cues = split_text(seg[int(pk[1:])])
    total = sum(len(c) for c in cues)
    acc = 0
    for c in cues:
        st = s + (e-s)*acc/total; en = s + (e-s)*(acc+len(c))/total
        acc += len(c)
        st = max(s, st); en = min(e, en)
        if en - st < 1.0: en = st + 1.0
        ass.append(f"Dialogue: 0,{ass_time(st)},{ass_time(en)},Narr,,0,0,0,,{c}")
        srt_entries.append((len(srt_entries)+1, st, min(en,e), c.replace("\\N","\n")))

open(S07 + "/字幕.ass","w",encoding="utf-8").write("\n".join(ass)+"\n")
with open(S07 + "/字幕.srt","w",encoding="utf-8") as f:
    for i,st,en,txt in srt_entries:
        f.write(f"{i}\n{srt_time(st)} --> {srt_time(en)}\n{txt}\n\n")

# ---------- 6. 音频与终导出 ----------
narr = S06 + "/配音/全片旁白.wav"
wind = S06 + "/音乐/环境风声.m4a"
final = S07 + "/候选片_v1.mp4"
fc = (f"[0:v]ass={S07}/字幕.ass[v];"
      f"[1:a]volume=1.0[na];"
      f"[2:a]volume=0.11,afade=t=in:st=0:d=2.5,afade=t=out:st={VIDEO_END-6:.2f}:d=6[wi];"
      "[na][wi]amix=inputs=2:duration=first:dropout_transition=0,apad[a]")
cmd = [FF,"-y","-v","warning","-i",base_mp4,"-i",narr,"-stream_loop","-1","-i",wind,
       "-filter_complex",fc,"-map","[v]","-map","[a]",
       "-c:v","libx264","-preset","medium","-crf","19","-pix_fmt","yuv420p",
       "-c:a","aac","-b:a","192k","-t",f"{VIDEO_END:.3f}",
       "-metadata","title=2023罗布泊4人自驾穿越遇难事件", final]
subprocess.run(cmd, check=True)

# 时间轴记录
rows = []
for jid,p,st,en in order:
    rows.append({"shot":jid,"file":os.path.basename(p),"start":round(st,3),"end":round(en,3),"dur":round(en-st,3)})
json.dump({"video_end":VIDEO_END,"shots":rows,"p_times":{k:[round(v[0],3),round(v[1],3)] for k,v in P.items()}},
          open(S07+"/时间轴.json","w",encoding="utf-8"), ensure_ascii=False, indent=1)
print("VIDEO_END", round(VIDEO_END,3), "clips", len(order))
print("final", dur(final))
