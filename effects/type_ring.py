"""type-ring — a ring of text spins around your head, passing behind you."""
import math
from PIL import Image, ImageDraw
from lib.core import *
from lib.kit import *

NAME = "type-ring"
DESC = "кольцо текста вращается вокруг головы и уходит за неё"
TEXT = "ЭФФЕКТЫ · МОНТАЖ · "
SFX = [(0.0, "whoosh"), (1.0, "swoosh")]


def render(ctx, tl, ts):
    frame, mask = ctx.src(ts)
    q = ease_out(prog(tl, 0.0, 0.5))
    if q <= 0 or mask is None:
        return frame
    hx, htop, hw = head_from_mask(mask)
    cy = htop + hw * 0.32
    rx, ry = hw * 1.05 * (0.6 + 0.4 * q), hw * 0.22
    back = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    front = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    n = len(TEXT)
    for i, ch in enumerate(TEXT):
        a = -2 * math.pi * i / n - tl * 1.6
        z = math.sin(a)                  # >0 = in front
        x, y = hx + rx * math.cos(a), cy + ry * z - 0 * z
        s = int(78 + 26 * z)
        col = (255, 255, 255, int(255 * q * (0.55 + 0.45 * (z + 1) / 2)))
        tgt = front if z > 0 else back
        g = Image.new("RGBA", (s * 2, s * 2), (0, 0, 0, 0))
        ImageDraw.Draw(g).text((s, s), ch, font=font("inter", s, 800), fill=col, anchor="mm")
        tgt.alpha_composite(g, (int(x - g.width / 2), int(y - g.height / 2)))
    img = frame.convert("RGBA")
    img.alpha_composite(back)
    img = person_over(frame, img.convert("RGB"), mask).convert("RGBA")
    img.alpha_composite(front)
    return img.convert("RGB")
