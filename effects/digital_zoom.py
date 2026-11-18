"""digital-zoom — punch-in zooms on the beat with a camera viewfinder."""
from PIL import Image, ImageDraw
from lib.core import *
from lib.kit import *

NAME = "digital-zoom"
DESC = "резкие наезды камеры с видоискателем"
SFX = [(0.25, "impact"), (1.05, "impact"), (1.85, "whoosh")]


def render(ctx, tl, ts):
    z = 1 + 0.6 * ease_out(prog(tl, 0.25, 0.18)) + 0.7 * ease_out(prog(tl, 1.05, 0.18)) - 1.3 * ease_in_out(prog(tl, 1.85, 0.35))
    _, m0 = ctx.src(ts)
    hx, htop, hw = head_from_mask(m0) if m0 is not None else (540, 500, 300)
    img, _ = ctx.src(ts, zoom=z, anchor=(hx, htop + hw * 0.7), with_mask=False)
    d = ImageDraw.Draw(img)
    L, m, wdt = 90, 70, 6
    for (x, y, sx, sy) in ((m, 260, 1, 1), (W - m, 260, -1, 1), (m, H - 260, 1, -1), (W - m, H - 260, -1, -1)):
        d.line((x, y, x + L * sx, y), fill=(255, 255, 255), width=wdt)
        d.line((x, y, x, y + L * sy), fill=(255, 255, 255), width=wdt)
    if int(tl * 2) % 2 == 0:
        d.ellipse((W - 210, 180, W - 186, 204), fill=PINK)
    d.text((W - 170, 192), "REC", font=font("mono", 30, 700), fill=(255, 255, 255), anchor="lm")
    d.text((W - 120, H - 300), f"{z:.1f}×", font=font("mono", 44, 700), fill=(255, 255, 255), anchor="rm")
    return img
