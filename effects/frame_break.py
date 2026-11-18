"""frame-break — you step out of the frame: your head breaks over the top edge of the card."""
import cv2
from PIL import Image, ImageDraw
from lib.core import *
from lib.kit import *

NAME = "frame-break"
DESC = "ты выходишь за границу кадра"
SFX = [(0.0, "whoosh"), (0.45, "impact")]


def render(ctx, tl, ts):
    frame, mask = ctx.src(ts)
    q = ease_back(prog(tl, 0.0, 0.55), 1.3)
    if q <= 0 or mask is None:
        return frame
    hx, htop, hw = head_from_mask(mask)
    out = light_bg()
    top = lerp(0, htop + hw * 0.55, min(1, q))
    side = lerp(0, 70, min(1, q))
    box = (int(side), int(top), int(W - side), int(H - lerp(0, 150, min(1, q))))
    shadow(out, box, alpha=55)
    card = frame.crop(box)
    out.paste(card, box[:2], rrect_mask(card.size, 40))
    ImageDraw.Draw(out).rounded_rectangle(box, 40, outline=SURFACE, width=10)
    # person over the card edge (only outside the card it shows anything new)
    m = np.clip((mask - 0.55) / 0.3, 0, 1)
    xs = np.arange(W)[None, :]
    keep = (np.abs(xs - hx) < hw * 0.62) & (np.arange(H)[:, None] < box[1] + 60)
    m = m * keep
    m = cv2.GaussianBlur(m.astype(np.float32), (0, 0), 1.5)
    out = person_over(frame, out, m)
    return out
