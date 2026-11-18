"""dynamic-island — the phone's island expands into a live activity: 'Монтирую…' → 'Монтаж готов ✓'."""
import math
from PIL import Image, ImageDraw
from lib.core import *
from lib.kit import *

NAME = "dynamic-island"
DESC = "«остров» сверху раскрывается в уведомление о монтаже"
SFX = [(0.05, "pop"), (1.3, "chime"), (2.2, "pop")]


def render(ctx, tl, ts):
    frame, _ = ctx.src(ts, with_mask=False)
    img = frame.convert("RGBA")
    e = ease_back(prog(tl, 0.05, 0.45), 1.2) * (1 - ease_in_out(prog(tl, 2.2, 0.4)))
    w = 230 + (940 - 230) * e
    h = 70 + (190 - 70) * e
    x0, y0 = W / 2 - w / 2, 40
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    d.rounded_rectangle((x0, y0, x0 + w, y0 + h), h / 2 if e < 0.3 else 60, fill=(8, 8, 10, 255))
    if e > 0.6:
        a = int(255 * clamp((e - 0.6) / 0.4))
        ix, iy = x0 + 50, y0 + h / 2
        d.rounded_rectangle((ix, iy - 42, ix + 84, iy + 42), 22, fill=PINK_FILL + (a,))
        spark(d, ix + 42, iy, 24, fill=(255, 255, 255, a))
        done = tl > 1.3
        d.text((ix + 112, iy - 24), "нейросеть", font=font("inter", 28, 500), fill=(170, 168, 176, a), anchor="lm")
        d.text((ix + 112, iy + 18), "Монтаж готов" if done else "Монтирую…", font=font("inter", 44, 700), fill=(255, 255, 255, a), anchor="lm")
        rx = x0 + w - 90
        if done:
            check(d, rx, iy, 36, fill=(255, 255, 255, a), fg=(8, 8, 10, a))
        else:
            d.arc((rx - 34, iy - 34, rx + 34, iy + 34), 0, 360, fill=(60, 60, 66, a), width=8)
            st = (tl * 400) % 360
            d.arc((rx - 34, iy - 34, rx + 34, iy + 34), st, st + 100, fill=PINK + (a,), width=8)
    img.alpha_composite(ov)
    return img.convert("RGB")
