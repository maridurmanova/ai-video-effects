"""lift-subject — you lift off the background: soft white halo, background dims and blurs."""
import cv2
from PIL import Image, ImageDraw
from lib.core import *
from lib.kit import *

NAME = "lift-subject"
DESC = "ты отделяешься от фона: белое свечение, фон уходит"
SFX = [(0.0, "sparkle"), (0.35, "pop")]


def render(ctx, tl, ts):
    frame, mask = ctx.src(ts)
    q = ease_out(prog(tl, 0.0, 0.6))
    if mask is None or q <= 0:
        return frame
    a = np.asarray(frame).astype(np.float32)
    bg = cv2.GaussianBlur(a, (0, 0), 6 * q) * (1 - 0.35 * q)
    halo = cv2.GaussianBlur(outline_mask(mask, 14), (0, 0), 10)[..., None] * q
    out = bg * (1 - halo) + 255 * halo
    m = mask[..., None]
    out = a * m + out * (1 - m)
    img = Image.fromarray(np.clip(out, 0, 255).astype(np.uint8))
    s = 1 + 0.04 * q
    img = img.resize((int(W * s), int(H * s)), Image.LANCZOS).crop((int(W * (s - 1) / 2), int(H * (s - 1) / 2), int(W * (s - 1) / 2) + W, int(H * (s - 1) / 2) + H))
    d = ImageDraw.Draw(img)
    hx, htop, hw = head_from_mask(mask)
    for i, (dx, dy, r) in enumerate(((-hw * .9, 60, 16), (hw * .95, 160, 12), (-hw * .7, 520, 10), (hw * 1.1, 640, 14))):
        p = ease_back(prog(tl, 0.3 + i * 0.12, 0.3), 2)
        if p > 0:
            spark(d, hx + dx, htop + dy, r * p * 1.6, fill=(255, 255, 255))
    return img
