"""phone-mockup — your clip plays inside a phone on a soft lilac background."""
import math
from PIL import Image, ImageDraw
from lib.core import *
from lib.kit import *

NAME = "phone-mockup"
DESC = "клип внутри телефона, как в рекламе приложения"
SFX = [(0.0, "whoosh"), (0.5, "pop")]


def render(ctx, tl, ts):
    frame, _ = ctx.src(ts, with_mask=False)
    q = ease_out(prog(tl, 0.0, 0.6))
    out = light_bg(grid=False)
    tint = Image.new("RGB", (W, H), (226, 220, 244))
    out = Image.blend(out, tint, 0.55)
    pw, ph = 640, 1300
    ph_im = Image.new("RGBA", (pw + 40, ph + 40), (0, 0, 0, 0))
    d = ImageDraw.Draw(ph_im)
    d.rounded_rectangle((0, 0, pw + 39, ph + 39), 96, fill=(20, 20, 24))
    d.rounded_rectangle((4, 4, pw + 35, ph + 35), 92, outline=(90, 90, 100), width=3)
    cw = H * pw / ph; scr = frame.resize((pw, ph), Image.LANCZOS, box=((W - cw) / 2, 0, (W + cw) / 2, H))
    ph_im.paste(scr, (20, 20), rrect_mask((pw, ph), 78))
    d.rounded_rectangle(((pw + 40) / 2 - 90, 44, (pw + 40) / 2 + 90, 92), 24, fill=(10, 10, 12))
    rot = -7 * q + 3 * (1 - q) + 1.5 * math.sin(tl * 1.4)
    cy = H / 2 + 40 + 900 * (1 - q)
    shadow(out, (W / 2 - pw / 2, cy - ph / 2, W / 2 + pw / 2, cy + ph / 2), r=90, blur=40, alpha=70, dy=40)
    put(out, ph_im, (W / 2, cy), 1.0, 1.0, rot)
    return out
