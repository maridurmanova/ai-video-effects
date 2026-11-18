"""ai-glow — a soft pink-violet-orange glow runs around the edges while the AI 'thinks'."""
import math, cv2
from PIL import Image, ImageDraw
from lib.core import *
from lib.kit import *

NAME = "ai-glow"
DESC = "переливающееся свечение по краю кадра, пока нейросеть думает"
SFX = [(0.0, "sparkle"), (1.5, "chime")]
_EDGE = None


def _edge():
    global _EDGE
    if _EDGE is None:
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        dist = np.minimum.reduce([xx, W - 1 - xx, yy, H - 1 - yy])
        ang = np.arctan2(yy - H / 2, xx - W / 2)
        _EDGE = (dist, ang)
    return _EDGE


def render(ctx, tl, ts):
    frame, _ = ctx.src(ts, with_mask=False)
    q = ease_out(prog(tl, 0.0, 0.5)) * (1 - 0.6 * ease_out(prog(tl, 1.6, 0.6)))
    if q <= 0:
        return frame
    dist, ang = _edge()
    cols = np.array([PINK, VIOLET, ORANGE, PINK], np.float32)
    ph = (ang / (2 * math.pi) + 0.5 + tl * 0.35) % 1 * 3
    i = np.floor(ph).astype(int); f = (ph - i)[..., None]
    c = cols[i] * (1 - f) + cols[i + 1] * f
    k = (np.exp(-dist / 60) * 0.95 + np.exp(-dist / 14) * 0.6)[..., None] * q
    a = np.asarray(frame).astype(np.float32)
    out = a * (1 - np.clip(k, 0, 1)) + c * np.clip(k, 0, 1) + (255 - a) * np.clip(np.exp(-dist / 6)[..., None] * q * 0.5, 0, 1)
    img = Image.fromarray(np.clip(out, 0, 255).astype(np.uint8))
    p = pill("нейросеть думает…" if tl < 1.6 else "готово", 34, bg=(21, 19, 24, 200), fg=(255, 255, 255), dot=PINK if tl < 1.6 else ORANGE)
    put(img, p, (W / 2, 1640), ease_back(prog(tl, 0.3, 0.35), 2))
    return img
