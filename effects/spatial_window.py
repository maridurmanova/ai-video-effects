"""spatial-window — your clip floats in a glass window over a blurred room, like a VR headset."""
import math, cv2
from PIL import Image, ImageDraw
from lib.core import *
from lib.kit import *

NAME = "spatial-window"
DESC = "клип в парящем стеклянном окне над размытой комнатой"
SFX = [(0.0, "whoosh"), (0.45, "pop")]


def render(ctx, tl, ts):
    frame, _ = ctx.src(ts, with_mask=False)
    q = ease_out(prog(tl, 0.0, 0.6))
    a = np.asarray(frame).astype(np.float32)
    bg = cv2.GaussianBlur(a, (0, 0), 1 + 30 * q) * (1 - 0.35 * q)
    img = Image.fromarray(np.clip(bg, 0, 255).astype(np.uint8))
    s = 1 - 0.24 * q
    fy = 8 * math.sin(tl * 2.0)
    ww, hh = int(W * s), int(H * s * 0.92)
    cx, cy = W / 2, H / 2 - 30 + fy
    box = (cx - ww / 2, cy - hh / 2, cx + ww / 2, cy + hh / 2)
    win = frame.resize((ww, int(H * s)), Image.LANCZOS).crop((0, int((H * s - hh) / 2), ww, int((H * s - hh) / 2) + hh))
    shadow(img, box, r=48, blur=40, alpha=int(120 * q), color=(0, 0, 0))
    glass(img, (box[0] - 18, box[1] - 18, box[2] + 18, box[3] + 18), r=60, alpha=0.12, blur=20, border=0.5 * q)
    img.paste(win, (int(box[0]), int(box[1])), rrect_mask((ww, hh), 44))
    d = ImageDraw.Draw(img, "RGBA")
    if q > 0.5:
        t = pill("● монтаж", 30, bg=(255, 255, 255, 200), fg=INK)
        put(img, t, (W / 2, box[1] - 70), 1, clamp((q - 0.5) * 2))
        d.rounded_rectangle((W / 2 - 110, box[3] + 50, W / 2 + 110, box[3] + 64), 7, fill=(255, 255, 255, int(220 * q)))
        d.ellipse((W / 2 - 170, box[3] + 47, W / 2 - 150, box[3] + 67), fill=(255, 255, 255, int(200 * q)))
    return img
