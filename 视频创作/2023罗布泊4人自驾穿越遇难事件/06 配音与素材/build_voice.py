import re, subprocess, os, json

base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
d = base + "/06 配音与素材/配音"
sub = base + "/05 脚本分镜/口播稿-字幕显示版.md"

# 1. parse P segments from subtitle version
text = open(sub, encoding="utf-8").read()
blocks = re.split(r"\nP(\d\d)\n", text)
seg = {}
for i in range(1, len(blocks), 2):
    n = int(blocks[i]); body = blocks[i+1].strip()
    body = re.sub(r"\n", "", body)
    seg[n] = body

scene_map = {1:(1,6),2:(7,10),3:(11,15),4:(16,20),5:(21,22),6:(23,26),7:(27,31),8:(32,37),9:(38,42),10:(43,45)}

def dur(f):
    out = subprocess.run(["/opt/homebrew/bin/ffprobe","-v","error","-show_entries","format=duration","-of","default=nw=1:nk=1", f],
                         capture_output=True, text=True)
    return float(out.stdout.strip())

GAP = 0.4
rows = []
t = 0.0
scene_times = {}
for s,(a,b) in scene_map.items():
    f = f"{d}/S{s:02d}.wav"
    D = dur(f)
    scene_times[s] = (t, t+D)
    chars = {n: len(seg[n]) for n in range(a,b+1)}
    total = sum(chars.values())
    acc = 0
    for n in range(a,b+1):
        st = t + D*acc/total
        en = t + D*(acc+chars[n])/total
        rows.append((n, st, en))
        acc += chars[n]
    t += D + GAP

# 2. build concat with gaps, normalize to 48k stereo
inputs = []
filt = []
for i,s in enumerate(sorted(scene_map)):
    inputs += ["-i", f"{d}/S{s:02d}.wav"]
sil = "anullsrc=r=48000:cl=stereo"
n = 10
fc = []
for i in range(n):
    fc.append(f"[{i}:a]aresample=48000,aformat=channel_layouts=stereo[a{i}]")
    fc.append(f"{sil}:d={GAP}[g{i}]")
    fc.append(f"[a{i}][g{i}]acrossfade=d=0:nofade=1[c{i}]")
# simply concatenate all with gap
chain = "".join(f"[c{i}]" for i in range(n))
fc.append(f"{chain}concat=n={2*n}:v=0:a=1[out]")
outfile = d + "/全片旁白.wav"
cmd = ["/opt/homebrew/bin/ffmpeg","-y","-v","error"] + inputs + ["-filter_complex", ";".join(fc), "-map","[out]","-ar","48000","-ac","2", outfile]

# simpler approach: concat list file
concat = d + "/concat.txt"
with open(concat, "w") as fh:
    for s in sorted(scene_map):
        fh.write(f"file 'S{s:02d}.wav'\nfile 'gap.wav'\n")

subprocess.run(["/opt/homebrew/bin/ffmpeg","-y","-v","error","-f","concat","-safe","0","-i",concat,
                "-ar","48000","-ac","2", outfile], check=True)
total_dur = dur(outfile)

# 3. write timing markdown
def fmt(x):
    h=int(x//3600); m=int((x%3600)//60); s=x%60
    return f"{h:02d}:{m:02d}:{s:06.3f}"

md = ["# 配音与语句时点记录", "",
      "- 本期选题：2023 年罗布泊\"4 人自驾穿越遇难\"事件",
      "- 采用的朗读版：05 脚本分镜/口播稿-配音朗读版.txt",
      "- 采用的配音音轨：06 配音与素材/配音/全片旁白.wav（分段生成：S01–S10.wav 顺序拼接，段间 0.4s 间隔）",
      "- 配音工具、音色与参数：text_to_audio_plus，中文男声旁白（低沉克制、纪录片质感、语速偏慢），48kHz 立体声输出；分段 S01–S10 各一次生成，未指定时长",
      f"- 音轨时长：{fmt(total_dur)}",
      "- 时点来源：分段音轨实际时长 + 段内按 P 段字数比例分配（估算），需 07 按最终字幕与音轨复核",
      "- 核对范围与限制：每段均核对可读取、时长与尾部静音边界（结尾有静音，无截断）；未做逐字听审，姓名、地名、数字读音的最终确认留 08 人工听审", "",
      "| 口播段号与语句 | 音轨时点 | 需特别留时或注意的事项 |",
      "| --- | --- | --- |"]
notes = {
 1:"开场空镜与静默，P06 后需留 0.5 秒黑场",
 6:"P26 单独一句，前后各留停顿",
 4:"P18 三动作信息密集，画面需逐项对应",
 7:"P28 三个数字需与方位图逐一点亮同步",
 8:"P34 取水与摆字信息密集，建议本段语速稍缓",
 9:"P39 七项清单，逐条出现需留阅读时间",
 10:"P45 末句后音乐即停，留 1 秒黑场",
}
for n,st,en in rows:
    key = seg[n]
    short = key if len(key) <= 28 else key[:28] + "……"
    nt = notes.get(n, "") or ""
    if n in (4,6,7,8,9,10) and not nt:
        nt = "注意本段语速与停顿"
    md.append(f"| P{n:02d} · {short} | {fmt(st)}–{fmt(en)} | {nt} |")

open(base + "/06 配音与素材/配音与语句时点记录.md","w",encoding="utf-8").write("\n".join(md)+"\n")
print("total", fmt(total_dur), "scenes", {k:(round(v[0],2),round(v[1],2)) for k,v in scene_times.items()})
print("chars total", sum(len(v) for v in seg.values()))
