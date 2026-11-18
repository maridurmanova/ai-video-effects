"""lock-screen — your clip becomes a phone lock screen: big clock over your head, 'Ролик смонтирован' notification."""
import datetime
from PIL import Image, ImageDraw
from lib.core import *
from lib.kit import *

NAME = "lock-screen"
DESC = "экран блокировки: часы за головой и уведомление «Ролик смонтирован»"
SFX = [(0.0, "whoosh"), (0.9, "chime")]


def render(ctx, tl, ts):
    frame, mask = ctx.src(ts)
    q = ease_out(prog(tl, 0.0, 0.5))
    img = grade(frame, contrast=1.04, bright=-8 * q).convert("RGBA")
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    a = int(255 * q)
    d.text((W / 2, 230), "среда, 18 ноября", font=font("inter", 44, 600), fill=(255, 255, 255, a), anchor="mm")
    d.text((W / 2, 300), "9:41", font=font("inter", 330, 700), fill=(255, 255, 255, a), anchor="mt")
    img.alpha_composite(lay)
    if mask is not None:
        img = person_over(frame, img.convert("RGB"), mask * 0.92).convert("RGBA")
    # widgets row
    wq = ease_back(prog(tl, 0.35, 0.35), 2)
    if wq > 0:
        wl = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dd = ImageDraw.Draw(wl)
        for i, (t, c) in enumerate((("4K", PINK), ("30", VIOLET), ("98%", ORANGE))):
            x = W / 2 + (i - 1) * 150; y = 1290
            r = 56 * wq
            dd.ellipse((x - r, y - r, x + r, y + r), fill=(255, 255, 255, 60), outline=(255, 255, 255, 150), width=3)
            dd.text((x, y), t, font=font("inter", max(8, int(34 * wq)), 800), fill=(255, 255, 255), anchor="mm")
        img.alpha_composite(wl)
    # notification
    nq = ease_back(prog(tl, 0.9, 0.4), 1.5)
    if nq > 0:
        y0 = 1480 + 300 * (1 - min(1, nq))
        glass(img, (70, y0, W - 70, y0 + 170), r=44, alpha=0.3, tint=(30, 26, 34), blur=20, border=0.35, opacity=min(1, nq))
        dd = ImageDraw.Draw(img, "RGBA")
        dd.rounded_rectangle((110, y0 + 40, 200, y0 + 130), 22, fill=PINK_FILL)
        spark(dd, 155, y0 + 85, 26)
        dd.text((230, y0 + 60), "нейросеть", font=font("inter", 30, 500), fill=(220, 218, 226), anchor="lm")
        dd.text((W - 110, y0 + 60), "сейчас", font=font("inter", 28, 500), fill=(200, 198, 206), anchor="rm")
        dd.text((230, y0 + 112), "Ролик смонтирован ✓", font=font("inter", 42, 700), fill=(255, 255, 255), anchor="lm")
        dd.rounded_rectangle((W / 2 - 140, 1830, W / 2 + 140, 1842), 6, fill=(255, 255, 255, 200))
    return img.convert("RGB")
