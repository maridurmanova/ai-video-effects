"""photo-wall — framed shots of you pin themselves to the wall behind you."""
import math, cv2
from PIL import Image, ImageDraw
from lib.core import *
from lib.kit import *

NAME = "photo-wall"
DESC = "стена с фото-кадрами из твоего же видео за спиной"
SLOTS = [(170, 330, 230, -6), (420, 230, 200, 4), (860, 300, 240, 5), (140, 760, 210, 3), (930, 800, 200, -4), (650, 140, 180, -3)]
SFX = [(0.1 + i * 0.16, "pop") for i in range(6)]


def render(ctx, tl, ts):
    frame, mask = ctx.src(ts)
    if mask is None:
        return frame
    a = np.asarray(frame).astype(np.float32)
    q = ease_out(prog(tl, 0.0, 0.4))
    img = Image.fromarray(np.clip(cv2.GaussianBlur(a, (0, 0), 1 + 6 * q) * (1 - 0.25 * q), 0, 255).astype(np.uint8)).convert("RGBA")
    dur = ctx.clip.duration
    for i, (x, y, w, rot) in enumerate(SLOTS):
        p = ease_back(prog(tl, 0.1 + i * 0.16, 0.35), 2)
        if p <= 0:
            continue
        sh = (ts * 0 + 1.3 + i * 2.7) % max(1, dur - 0.5)
        th = ctx.clip.frame(sh)
        h = int(w * 1.25)
        th = th.resize((w, int(w * H / W)), Image.LANCZOS).crop((0, (int(w * H / W) - h) // 2, w, (int(w * H / W) - h) // 2 + h))
        card = Image.new("RGBA", (w + 24, h + 24), SURFACE + (255,))
        card.paste(th, (12, 12))
        ImageDraw.Draw(card).rectangle((0, 0, w + 23, h + 23), outline=PINK + (255,) if i % 2 == 0 else VIOLET + (255,), width=5)
        put(img, card, (x, y), p, 1, rot)
    img = person_over(frame, img.convert("RGB"), mask)
    return img
