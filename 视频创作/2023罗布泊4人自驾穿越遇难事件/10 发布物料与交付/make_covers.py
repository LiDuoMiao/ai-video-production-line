# -*- coding: utf-8 -*-
from PIL import Image, ImageDraw, ImageFont

FONT = "/System/Library/Fonts/Hiragino Sans GB.ttc"


def F(sz, bold=False):
    return ImageFont.truetype(FONT, sz, index=1 if bold else 0)


base = Image.open("../06 配音与素材/画面/J28_黄昏远景.png").convert("RGB")


def cover(size, out, lines, kicker, credit):
    W, H = size
    img = base.copy()
    r = max(W / img.width, H / img.height)
    img = img.resize((int(img.width * r) + 2, int(img.height * r) + 2), Image.LANCZOS)
    x = (img.width - W) // 2
    y = (img.height - H) // 2
    img = img.crop((x, y, x + W, y + H))

    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d0 = ImageDraw.Draw(ov)
    top_h = int(H * 0.30)
    for i in range(top_h):
        a = int(120 * (1 - i / top_h))
        d0.rectangle([0, i, W, i + 1], fill=(10, 8, 6, a))
    bot_h = int(H * 0.62)
    for i in range(bot_h):
        a = int(215 * ((i / bot_h) ** 0.8))
        d0.rectangle([0, H - i - 1, W, H - i], fill=(8, 6, 5, a))
    img = Image.alpha_composite(img.convert("RGBA"), ov).convert("RGB")

    d = ImageDraw.Draw(img)
    m = int(W * 0.07)
    d.text((m, int(H * 0.075)), kicker, font=F(int(W * 0.036)), fill=(228, 208, 180))

    sz = min(int(W * 0.105), int(H * 0.155))
    while sz > 24 and max(d.textlength(l, font=F(sz, True)) for l in lines) > W - 2 * m:
        sz -= 2
    f = F(sz, True)
    lh = int(sz * 1.26)
    total = lh * (len(lines) - 1) + sz
    top = int(H * 0.87) - total
    for i, l in enumerate(lines):
        d.text((m, top + i * lh), l, font=f, fill=(247, 241, 231))
    d.text((m, H - int(H * 0.035)), credit, font=F(int(W * 0.034)), fill=(205, 190, 168), anchor="ls")
    img.save(out, quality=92)
    print(out, img.size, "title", sz)


cover((1080, 1440), "抖音/封面_抖音_1080x1440.jpg",
      ["3 小时的路", "四个人没走出来"], "2023 罗布泊 · 4 人穿越遇难", "案间回声 · 案件纪实")
cover((1280, 720), "YouTube/缩略图_YouTube_1280x720.jpg",
      ["3 小时的路，", "四个人没走出来"], "2023 罗布泊 · 4 人穿越遇难", "案间回声 · 案件纪实")
