"""exploded-layers — the frame tilts in 3D and splits into layers: background, you, graphics."""
from PIL import Image, ImageDraw
from lib.core import *
from lib.kit import *

NAME = "exploded-layers"
DESC = "кадр разбирается на слои в 3D: фон, ты, графика"
SFX = [(0.0, "whoosh"), (0.55, "pop"), (0.7, "pop"), (0.85, "pop"), (1.9, "whoosh")]


def render(ctx, tl, ts):
    frame, mask = ctx.src(ts)
    q = ease_in_out(prog(tl, 0.0, 0.6))           # tilt in
    s = ease_out(prog(tl, 0.45, 0.6)) - ease_in_out(prog(tl, 2.3, 0.5))   # separation
    if q <= 0:
        return frame
    out = light_bg()
    sc = 1 - 0.45 * q
    w, h = W * sc, H * sc
    yaw = 26 * q
    layers = []
    bg = frame.convert("RGBA")
    layers.append(rounded(bg, 40))
    if mask is not None:
        layers.append(person_rgba(frame, mask))
    g = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gp = pill("субтитры · графика · звук", 46, bg=(255, 255, 255, 235), fg=INK)
    g.paste(gp, ((W - gp.width) // 2, 1500), gp)
    gp2 = pill("● монтаж", 40, bg=PINK_FILL)
    g.paste(gp2, (90, 140), gp2)
    layers.append(g)
    n = len(layers)
    for i, L in enumerate(layers):
        k = i - (n - 1) / 2
        cx = W / 2 + 120 * s * k + 30 * q
        cy = H / 2 + 40 - 70 * s * k
        quad = tilt_quad(cx, cy, w, h, yaw=yaw, pitch=-6 * q)
        im = warp_quad(L, quad)
        if s > 0.02:
            fr = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            ImageDraw.Draw(fr).polygon([tuple(p) for p in quad], outline=PINK + (int(220 * min(1, s * 2)),), width=4)
            if i == 0:
                shadow(out, (min(p[0] for p in quad), min(p[1] for p in quad), max(p[0] for p in quad), max(p[1] for p in quad)), alpha=50)
            out.paste(im, (0, 0), im)
            out.paste(fr, (0, 0), fr)
        else:
            out.paste(im, (0, 0), im)
    return out
