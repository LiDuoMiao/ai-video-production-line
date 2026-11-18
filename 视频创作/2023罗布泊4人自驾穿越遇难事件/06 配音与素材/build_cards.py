# -*- coding: utf-8 -*-
from PIL import Image, ImageDraw, ImageFont
import os

W, H = 1920, 1080
BG = (243, 239, 231)
INK = (35, 33, 30)
SUB = (107, 100, 89)
ACC = (180, 118, 63)
LINE = (214, 204, 190)
WHITE = (252, 250, 246)

FP = "/System/Library/Fonts/Hiragino Sans GB.ttc"
out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "图卡")
os.makedirs(out_dir, exist_ok=True)

def F(size, bold=False):
    try:
        return ImageFont.truetype(FP, size, index=1 if bold else 0)
    except Exception:
        return ImageFont.truetype(FP, size)

def new_card(bg=BG):
    img = Image.new("RGB", (W, H), bg)
    d = ImageDraw.Draw(img)
    # 顶部细则线
    d.line([(120, 96), (W-120, 96)], fill=LINE, width=2)
    return img, d

def footer(d, text):
    d.text((120, H-64), text, font=F(24), fill=SUB)

def kicker(d, text, y=104):
    d.text((120, y), text, font=F(28, True), fill=ACC)

def title(d, text, y=168, size=76):
    d.text((120, y), text, font=F(size, True), fill=INK)

def save(img, name):
    img.save(os.path.join(out_dir, name + ".png"), "PNG")

def wrap(d, text, font, width):
    lines, cur = [], ""
    for ch in text:
        if d.textlength(cur + ch, font=font) <= width:
            cur += ch
        else:
            lines.append(cur); cur = ch
    if cur: lines.append(cur)
    return lines

# ---------- 卡-01 方位示意 ----------
def card01(name, state):
    img, d = new_card()
    kicker(d, "方 位 示 意")
    title(d, "八公里之外", y=160, size=60)
    footer(d, "依据：成都商报、红星新闻对救援者的采访；比例为示意，非实际测绘。数字为救援者判断。", )
    # 坐标系区域
    x0, y0, x1, y1 = 120, 290, W-120, 880
    d.rectangle([x0, y0, x1, y1], outline=LINE, width=2)
    # 网格点
    for gx in range(x0+60, x1, 120):
        for gy in range(y0+60, y1, 120):
            d.ellipse([gx-1, gy-1, gx+1, gy+1], fill=(225, 215, 200))
    car = (520, 660)
    d.ellipse([car[0]-16, car[1]-16, car[0]+16, car[1]+16], fill=INK)
    d.text((car[0]-40, car[1]+26), "皮卡（陷沙）", font=F(30), fill=INK)
    body = (1080, 660)
    d.line([(car[0]+18, car[1]), (body[0]-18, body[1])], fill=ACC, width=3)
    d.ellipse([body[0]-14, body[1]-14, body[0]+14, body[1]+14], outline=ACC, width=3)
    d.text(((car[0]+body[0])//2-40, car[1]-58), "正东 8 公里", font=F(34, True), fill=ACC)
    d.text((body[0]-34, body[1]-72), "贾宁", font=F(28), fill=INK)
    if state >= 2:
        vil = (1480, 660)
        d.line([(body[0]+16, body[1]), (vil[0]-16, vil[1])], fill=SUB, width=2)
        d.rectangle([vil[0]-14, vil[1]-14, vil[0]+14, vil[1]+14], outline=SUB, width=2)
        d.text((vil[0]-52, vil[1]-62), "再 12 公里", font=F(30), fill=SUB)
        d.text((vil[0]-46, vil[1]+22), "望舒村", font=F(30), fill=SUB)
        d.text((160, 930), "往雅丹地质公园方向：正常两三个小时可出沙漠", font=F(30), fill=SUB)
    if state >= 3:
        three = (1080, 830)
        d.rectangle([three[0]-12, three[1]-12, three[0]+12, three[1]+12], fill=ACC)
        d.text((three[0]+22, three[1]-18), "三名遇难者：偏东南 7.8 公里", font=F(30), fill=INK)
        d.line([(body[0], body[1]+16), (three[0], three[1]-14)], fill=ACC, width=1)
        d.text((body[0]-176, body[1]+92), "相距 3.2 公里", font=F(28), fill=SUB)
    if state >= 4:
        d.line([(car[0], car[1]+20), (car[0]+340, y1-60)], fill=SUB, width=2)
        d.line([(car[0], car[1]+20), (car[0]+160, y1-40)], fill=SUB, width=2)
        d.text((car[0]+180, y1-90), "两条外走路径", font=F(28), fill=SUB)
    save(img, name)

for i in range(1, 6):
    card01(f"卡-01{chr(96+i)}_方位示意", i)

# ---------- 卡-02 路线 ----------
img, d = new_card()
kicker(d, "路 线 示 意")
title(d, "七天，五个节点", y=150, size=64)
footer(d, "依据：随行队员向中国新闻周刊的讲述；节点位置为示意。")
nodes = ["库木塔格\n沙漠", "彭加木失踪\n纪念地", "小泉沟", "飞机残骸", "花土沟方向\n出"]
xs = [240, 560, 880, 1200, 1560]
y = 560
for i, (x, n) in enumerate(zip(xs, nodes)):
    if i: d.line([(xs[i-1]+34, y), (x-34, y)], fill=LINE, width=3)
    d.ellipse([x-26, y-26, x+26, y+26], outline=ACC, width=3)
    d.text((x-22, y-16), f"{i+1}", font=F(30, True), fill=ACC)
    for j, ln in enumerate(n.split("\n")):
        d.text((x-90, y+52+j*42), ln, font=F(30), fill=INK)
save(img, "卡-02_七天路线")

# ---------- 卡-03 法条 ----------
img, d = new_card()
kicker(d, "事 发 时 施 行 的 版 本")
title(d, "规则写得很清楚", y=150, size=64)
items = ["核心区：禁止任何人进入", "未经批准进入：责令改正，可以罚款",
         "情节严重的，追究刑事责任"]
yy = 340
for it in items:
    d.rectangle([120, yy, 136, yy+8], fill=ACC)
    d.text((170, yy-24), it, font=F(46), fill=INK)
    yy += 120
footer(d, "依据：《中华人民共和国自然保护区条例》事发时施行的条文；具体条号依 2026 年修订后已调整，此处只述要点。")
save(img, "卡-03_法条要点")

# ---------- 卡-04 物资倍量 ----------
img, d = new_card()
kicker(d, "物 资 倍 量")
title(d, "三天的路，八天的粮", y=150, size=64)
d.text((180, 400), "行程", font=F(38), fill=SUB)
d.text((180, 470), "3 天", font=F(110, True), fill=INK)
d.line([(430, 420), (430, 620)], fill=LINE, width=3)
d.text((520, 400), "建议准备", font=F(38), fill=SUB)
d.text((520, 470), "6 – 8 天", font=F(110, True), fill=ACC)
d.text((180, 660), "水、食物、油料，都要按这个倍数备", font=F(40), fill=INK)
footer(d, "依据：齐鲁晚报刊登的业内人士判断；夏季地表温度可达 70℃ 左右。")
save(img, "卡-04_物资倍量")

# ---------- 卡-05 燃油标号 ----------
img, d = new_card()
kicker(d, "燃 油 标 号")
title(d, "不是车不行，是油不对", y=150, size=64)
d.rounded_rectangle([140, 340, 880, 700], 18, outline=LINE, width=2)
d.text((190, 380), "车辆要求", font=F(34), fill=SUB)
d.text((190, 450), "95 号以上", font=F(86, True), fill=INK)
d.rounded_rectangle([1000, 340, 1740, 700], 18, outline=ACC, width=3)
d.text((1050, 380), "实际备了", font=F(34), fill=SUB)
d.text((1050, 450), "92 号", font=F(86, True), fill=ACC)
d.text((140, 760), "同一批油，也让一同加油的陆巡出现了同样反应", font=F(36), fill=INK)
footer(d, "依据：封面新闻报道中参与救援者的分析，属事后判断。")
save(img, "卡-05_燃油标号")

# ---------- 卡-06 分组示意 ----------
img, d = new_card()
kicker(d, "分 组 示 意")
title(d, "四个人的车，走了另一条路", y=150, size=58)
cx, cy = 520, 560
d.ellipse([cx-18, cy-18, cx+18, cy+18], fill=INK)
d.text((cx-120, cy+30), "7 月 24 日分车", font=F(30), fill=SUB)
paths = [((520, 300), "大部队继续向北", "一台霸王龙车主"),
         ((980, 560), "原地等待救援", "陆巡 · 车上 3 人"),
         ((900, 860), "向雅丹方向撤出", "贾宁 + 2 名游客 + 汽修工")]
for (p, lab, sub2) in paths:
    d.line([(cx+20, cy), p], fill=ACC, width=3)
    d.ellipse([p[0]-12, p[1]-12, p[0]+12, p[1]+12], outline=ACC, width=3)
    d.text((p[0]+26, p[1]-34), lab, font=F(32, True), fill=INK)
    d.text((p[0]+26, p[1]+6), sub2, font=F(28), fill=SUB)
footer(d, "依据：成都商报、中国新闻周刊对救援者与随行队员的采访；车辆位置为示意。")
save(img, "卡-06_分组示意")

# ---------- 卡-07 两小时 ----------
img, d = new_card(WHITE)
kicker(d, "承 诺")
d.text((120, 300), "两个小时", font=F(190, True), fill=INK)
d.text((130, 560), "“说自己很快派人来救他们”", font=F(44), fill=ACC)
d.text((130, 660), "据车上人员事后回忆转述", font=F(30), fill=SUB)
d.line([(130, 760), (W-130, 760)], fill=LINE, width=2)
d.text((130, 800), "两天后，这辆车和车上的人等来的不是救援", font=F(40), fill=INK)
save(img, "卡-07_两小时")

# ---------- 卡-08 三物件 ----------
img, d = new_card()
kicker(d, "救 援 者 看 到 的 车")
title(d, "车没坏，水没了", y=150, size=64)
cols = [("空调", "正常", "出风口有风", INK), ("油料", "充足", "油箱还满", INK), ("饮用水", "耗尽", "一滴不剩", ACC)]
for i, (a, b, c, col) in enumerate(cols):
    x = 160 + i*600
    d.rounded_rectangle([x, 330, x+500, 720], 20, outline=LINE, width=2)
    d.text((x+40, 370), a, font=F(34), fill=SUB)
    d.text((x+40, 430), b, font=F(84, True), fill=col)
    d.text((x+40, 560), c, font=F(32), fill=SUB)
    if i == 2:
        d.rounded_rectangle([x, 330, x+500, 720], 20, outline=ACC, width=4)
d.text((160, 790), "这台车只是陷在沙里开不动", font=F(44), fill=INK)
footer(d, "依据：红星新闻采访的协助救援者现场观察；非官方勘验结论。")
save(img, "卡-08_三物件")

# ---------- 卡-09 算术 ----------
img, d = new_card()
kicker(d, "当 时 的 算 术")
title(d, "没有一样是确定的", y=150, size=64)
rows = ["水：不够撑到救援到来", "救援：不知道什么时候来", "路：据说只有 3 小时"]
yy = 360
for r in rows:
    d.line([(140, yy+70), (140, yy+150)], fill=ACC, width=4)
    d.text((190, yy), r, font=F(52), fill=INK)
    yy += 170
d.text((140, 880), "这是事后判断；当时他们手里只有这些变量", font=F(32), fill=SUB)
save(img, "卡-09_当时的算术")

# ---------- 卡-10 时间轴 ----------
img, d = new_card()
kicker(d, "7 月 2 6 日 至 2 7 日")
title(d, "救援窗口在流失", y=150, size=64)
tw = [("05:00", "补给车出发"), ("08:00", "抵达霸王龙"), ("10:00", "驶出沙漠 · 报警"), ("13:00", "接到转警")]
y = 560
d.line([(200, y), (1720, y)], fill=LINE, width=4)
for i, (t, lab) in enumerate(tw):
    x = 220 + i*480
    d.ellipse([x-14, y-14, x+14, y+14], fill=ACC)
    d.text((x-52, y-90), t, font=F(42, True), fill=INK)
    d.text((x-90, y+36), lab, font=F(30), fill=SUB)
footer(d, "依据：中国新闻周刊对随行队员的采访与若羌县公安局 7 月 28 日警情通报。")
save(img, "卡-10_时间轴")

# ---------- 卡-11 原因清单（两态 + 锁链）----------
reasons = ["不遵守法律法规，未经批准非法穿越",
           "没有周详的探险方案和应急救援预案",
           "对目的地的地理、气候了解不足",
           "探险装备及物资准备不足",
           "向导非有资质领队，无野外生存与救援能力",
           "不熟悉卫星地图与 GPS，未配备合格卫星电话",
           "沙漠驾驶技术不合格，陷车后处理不当"]
for st, n in (("a", 4), ("b", 7)):
    img, d = new_card()
    kicker(d, "中 国 探 险 协 会")
    title(d, "七项并列的原因", y=140, size=58)
    yy = 280
    for i, r in enumerate(reasons[:n]):
        d.text((140, yy), f"{i+1:02d}", font=F(34, True), fill=ACC)
        d.text((210, yy-6), r, font=F(36), fill=INK)
        yy += 92
    footer(d, "依据：中国探险协会官网公开文章中的事故原因归纳。")
    save(img, f"卡-11{st}_原因清单")

img, d = new_card()
kicker(d, "叠 加")
title(d, "每一环都留了缺口", y=150, size=64)
yy = 380
for i in range(7):
    x = 240 + i*200
    d.rounded_rectangle([x, yy, x+150, yy+70], 12, outline=ACC, width=3)
    if i: d.line([(x-50, yy+35), (x, yy+35)], fill=ACC, width=3)
d.text((240, yy+140), "串成一条锁链", font=F(56, True), fill=INK)
footer(d, "依据：《最终资料调查报告》第 09 段条目；此处为对并列原因的图示化。")
save(img, "卡-11c_锁链")

# ---------- 卡-12 三种口径 ----------
img, d = new_card()
kicker(d, "同 一 件 事，三 种 说 法")
title(d, "各有出处，不必裁决", y=150, size=60)
cards = [("车队成员", "全队带了 4 台\n卫星电话"), ("救援者所见", "贾宁身上\n没有卫星电话"), ("协会表述", "未配备\n合格的卫星电话")]
for i, (h, b) in enumerate(cards):
    x = 150 + i*570
    d.rounded_rectangle([x, 320, x+500, 660], 16, outline=LINE, width=2)
    d.text((x+36, 350), h, font=F(32, True), fill=ACC)
    for j, ln in enumerate(b.split("\n")):
        d.text((x+36, 420+j*64), ln, font=F(42), fill=INK)
d.text((150, 760), "带了几台，与是否随身、是否合格，是两件不同的事", font=F(34), fill=SUB)
footer(d, "依据：中国新闻周刊转述、红星新闻采访、中国探险协会公开文章。")
save(img, "卡-12_三种口径")

# ---------- 卡-13 责任 ----------
img, d = new_card()
kicker(d, "律 师 意 见")
title(d, "两条不同的路", y=150, size=64)
d.rounded_rectangle([140, 320, 920, 760], 16, outline=ACC, width=4)
d.text((180, 350), "有偿组织", font=F(36, True), fill=ACC)
d.text((180, 420), "组织者多一层委托关系，", font=F(34), fill=INK)
d.text((180, 470), "须尽安全注意义务", font=F(34), fill=INK)
d.text((180, 540), "未尽义务造成损害，", font=F(34), fill=INK)
d.text((180, 590), "依《民法典》第 1198 条，", font=F(34), fill=INK)
d.text((180, 640), "可能承担侵权责任", font=F(34), fill=INK)
d.rounded_rectangle([1000, 320, 1780, 760], 16, outline=LINE, width=2)
d.text((1040, 350), "自助结伴", font=F(36, True), fill=SUB)
d.text((1040, 420), "无盈利、风险自担，", font=F(34), fill=INK)
d.text((1040, 470), "相互之间不负责", font=F(34), fill=INK)
d.text((140, 830), "本次行程每人收费 9800 元 —— 属于哪一类，观众可以自己判断", font=F(32), fill=SUB)
footer(d, "依据：齐鲁晚报刊登的律师意见，属个人观点，不构成裁判结论。")
save(img, "卡-13_责任框架")

# ---------- 通报（全文重排）----------
img, d = new_card((246, 243, 237))
d.rectangle([150, 90, W-150, H-90], outline=(200, 60, 50), width=3)
d.text((W//2-100, 150), "警 情 通 报", font=F(72, True), fill=(150, 40, 32))
body = ("7 月 27 日 13 时许，若羌县公安局接敦煌市公安局转警称，一自驾车队于 22 日自"
        "敦煌市出发，未经批准穿越若羌境内国家级野骆驼自然保护区，26 日 1 车 4 人失联。"
        "经搜救，于 27 日发现失联车辆，3 人已无生命体征，1 人失踪。车队其余人员已安全"
        "返回敦煌市。接报后，若羌县公安局立即与医疗、应急等部门成立救援队伍，全力与敦"
        "煌市有关部门联合开展搜救工作。目前，搜救工作仍在进行中。")
yy = 300
for ln in wrap(d, body, F(38), W-360):
    d.text((180, yy), ln, font=F(38), fill=(45, 42, 38))
    yy += 68
d.text((W-520, H-320), "若羌县公安局", font=F(36), fill=(45, 42, 38))
d.text((W-520, H-260), "2023 年 7 月 28 日", font=F(36), fill=(45, 42, 38))
d.text((160, H-56), "来源：若羌县公安局警情通报（2023-07-28），依原文重排", font=F(24), fill=SUB)
save(img, "材料_警情通报")

# ---------- 通告 ----------
img, d = new_card()
kicker(d, "保 护 区 管 理 局 通 告")
title(d, "严禁进入", y=150, size=76)
d.text((140, 340), "“严禁一切社会团体、单位或个人进入保护区", font=F(44), fill=INK)
d.text((140, 400), "开展旅游、探险活动，一经发现将依法予以处罚，", font=F(44), fill=INK)
d.text((140, 460), "情节严重的将追究刑事责任。”", font=F(44), fill=INK)
d.text((140, 600), "2017 年以来，保护区管理局多次发布同类通告", font=F(34), fill=SUB)
footer(d, "依据：媒体对新疆罗布泊野骆驼国家级自然保护区管理局通告的转述；原文图片未取得，此处按报道重排。")
save(img, "材料_通告摘句")

# ---------- 黑场提问 ----------
img = Image.new("RGB", (W, H), (18, 17, 16))
d = ImageDraw.Draw(img)
d.text((160, 300), "六七十公里，正常 3 个小时", font=F(64), fill=(235, 230, 222))
d.text((160, 400), "四个人，一个都没走出去", font=F(64), fill=(235, 230, 222))
d.line([(160, 520), (760, 520)], fill=(180, 118, 63), width=3)
d.text((160, 580), "这段路，是在哪一步变成了绝路？", font=F(54), fill=(180, 118, 63))
save(img, "卡-00_核心提问")

# ---------- 空白版面 + 三问 ----------
img, d = new_card((250, 248, 243))
d.text((150, 300), "2023 年 8 月以后，公开报道中未见后续", font=F(48), fill=INK)
d.text((150, 380), "官方结论仍停在通报里", font=F(34), fill=SUB)
d.line([(150, 470), (900, 470)], fill=LINE, width=2)
d.text((150, 520), "人民网当时提出的问题", font=F(32), fill=ACC)
qs = ["谁组织的？", "谁提议擅闯保护区的？", "除了遇难的 4 人，还有谁参与？"]
for j, q in enumerate(qs):
    d.text((150, 590+j*70), "· " + q, font=F(40), fill=INK)
footer(d, "检索范围为 2023 年 8 月至 2026 年 11 月的中文公开报道。")
save(img, "卡-14_结论边界")

# ---------- 结尾 ----------
img = Image.new("RGB", (W, H), (243, 239, 231))
d = ImageDraw.Draw(img)
d.text((140, 300), "这条路上最贵的不是车，是水", font=F(60), fill=INK)
d.line([(140, 420), (820, 420)], fill=ACC, width=3)
d.text((140, 480), "最危险的，不是沙，", font=F(60), fill=INK)
d.text((140, 580), "是“应该没事”这四个字", font=F(70, True), fill=ACC)
save(img, "卡-15_结尾警句")


# ---------- 卡-16 石头摆字 ----------
img, d = new_card((236, 226, 210))
kicker(d, "据 救 援 者 转 述 的 再 现")
d.text((150, 240), "山坡上，石头摆出两个字", font=F(46), fill=SUB)
d.text((150, 420), "救　命", font=F(220, True), fill=(120, 96, 66))
footer(d, "报道原文：用石头在霸王龙旁边山坡上摆出了救命的字样。")
save(img, "卡-16_石头摆字")

print("done", len(os.listdir(out_dir)))
