"""cinematic-mode — background melts into bokeh, focus box locks on your face, aperture dial turns."""
import cv2
from PIL import Image, ImageDraw
from lib.core import *
from lib.kit import *

NAME = "cinematic-mode"
DESC = "размытый фон, рамка фокуса на лице, диск диафрагмы"
SFX = [(0.0, "tick"), (0.15, "tick"), (0.3, "tick"), (0.45, "tick"), (0.6, "chime")]


def render(ctx, tl, ts):
    frame, mask = ctx.src(ts)
    q = ease_in_out(prog(tl, 0.0, 0.8))
    if mask is None:
        return frame
    a = np.asarray(frame).astype(np.float32)
    b = cv2.GaussianBlur(a, (0, 0), 1 + 16 * q)
    m = cv2.GaussianBlur(mask, (0, 0), 3)[..., None]
    img = Image.fromarray((a * m + b * (1 - m)).astype(np.uint8))
    img = grade(img, sat=1.05, contrast=1.06)
    d = ImageDraw.Draw(img, "RGBA")
    hx, htop, hw = head_from_mask(mask)
    fq = ease_back(prog(tl, 0.35, 0.35), 2)
    s = (1.5 - 0.5 * min(1, fq)) * hw * 0.62
    cy = htop + hw * 0.62
    L = s * 0.35
    if fq > 0:
        for sx, sy in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
            x, y = hx + sx * s, cy + sy * s
            d.line((x, y, x - sx * L, y), fill=ORANGE + (255,), width=6)
            d.line((x, y, x, y - sy * L), fill=ORANGE + (255,), width=6)
    lab = pill("КИНОЭФФЕКТ", 30, bg=(21, 19, 24, 170), fg=ORANGE, weight=800)
    img.paste(lab, ((W - lab.width) // 2, 150), lab)
    # aperture dial
    glass(img, (150, 1600, 930, 1760), r=40, tint=(20, 20, 24), alpha=0.35, blur=18, border=0.3)
    f_val = 16 - (16 - 2.8) * q
    off = q * 260
    for i in range(-30, 31):
        x = 540 + i * 22 - off % 22
        if 170 < x < 910:
            hh = 40 if i % 5 == 0 else 22
            d.line((x, 1720 - hh, x, 1720), fill=(255, 255, 255, 200), width=3)
    d.line((540, 1650, 540, 1730), fill=ORANGE + (255,), width=5)
    d.text((540, 1630), f"ƒ{f_val:.1f}", font=font("inter", 44, 700), fill=ORANGE, anchor="mm")
    return img
