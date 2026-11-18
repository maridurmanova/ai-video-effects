"""liquid-glass — a glass lens glides over the frame and refracts it; a glass dock floats at the bottom."""
import math, cv2
from PIL import Image, ImageDraw
from lib.core import *
from lib.kit import *

NAME = "liquid-glass"
DESC = "стеклянная линза скользит по кадру и преломляет его"
SFX = [(0.0, "swoosh"), (0.5, "pop"), (1.4, "swoosh")]
_G = None


def _grid():
    global _G
    if _G is None:
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        _G = (xx, yy)
    return _G


def render(ctx, tl, ts):
    frame, _ = ctx.src(ts, with_mask=False)
    q = ease_out(prog(tl, 0.0, 0.4))
    a = np.asarray(frame)
    xx, yy = _grid()
    R = 190 * q
    out = a
    if R > 5:
        p = ease_in_out(prog(tl, 0.0, 2.6))
        cx = lerp(220, 860, p); cy = 760 + 160 * math.sin(p * math.pi)
        dx, dy = xx - cx, yy - cy
        r = np.sqrt(dx * dx + dy * dy)
        inside = r < R
        k = np.where(inside, 0.5 + 0.5 * (r / R) ** 2.5, 1.0)        # magnify centre, compress rim
        mx = (cx + dx * k).astype(np.float32); my = (cy + dy * k).astype(np.float32)
        out = cv2.remap(a, mx, my, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
        out = out.astype(np.float32)
        rim = np.clip(1 - np.abs(r - R + 4) / 6, 0, 1)[..., None]
        hl = (np.clip(1 - np.hypot(dx + R * .45, dy + R * .45) / (R * .5), 0, 1) ** 2)[..., None] * inside[..., None]
        out = out * (1 - rim * .7) + 255 * rim * .7 + 255 * hl * 0.35
        out = np.clip(out, 0, 255).astype(np.uint8)
    img = Image.fromarray(out)
    # dock
    dq = ease_back(prog(tl, 0.35, 0.45), 1.4)
    if dq > 0:
        y0 = 1660 + 200 * (1 - min(1, dq))
        glass(img, (190, y0, 890, y0 + 130), r=65, alpha=0.18, blur=16, border=0.55)
        d = ImageDraw.Draw(img, "RGBA")
        for i in range(4):
            x = 280 + i * 173; y = y0 + 65
            if i == 0:
                d.rounded_rectangle((x - 52, y - 44, x + 52, y + 44), 40, fill=(255, 255, 255, 70))
            c = (255, 255, 255, 240)
            if i == 0: d.polygon([(x - 22, y), (x, y - 20), (x + 22, y), (x + 22, y + 20), (x - 22, y + 20)], outline=c, width=4)
            if i == 1: d.ellipse((x - 22, y - 22, x + 22, y + 22), outline=c, width=4); d.line((x - 11, y, x + 11, y), fill=c, width=4)
            if i == 2: d.rounded_rectangle((x - 20, y - 20, x + 20, y + 20), 6, outline=c, width=4)
            if i == 3: d.ellipse((x - 12, y - 24, x + 12, y), outline=c, width=4); d.arc((x - 24, y + 2, x + 24, y + 42), 180, 360, fill=c, width=4)
    lab = pill("Liquid Glass", 30, bg=(255, 255, 255, 90), fg=(255, 255, 255))
    put(img, lab, (W / 2, 160), ease_back(prog(tl, 0.2, 0.35), 2))
    return img
