"""headline-wall — magazine headline words stack up behind you on a clean light background."""
from PIL import Image, ImageDraw
from lib.core import *
from lib.kit import *

NAME = "headline-wall"
DESC = "журнальные заголовки складываются за тобой"
WORDS = [("НЕЙРОСЕТЬ", "inter", INK, -5), ("монтирует", "serif", PINK, -5), ("ЗА ТЕБЯ", "inter", INK, -5)]
SFX = [(0.1, "impact"), (0.4, "impact"), (0.7, "impact")]


def render(ctx, tl, ts):
    frame, mask = ctx.src(ts)
    q = ease_out(prog(tl, 0.0, 0.3))
    if mask is None or q <= 0:
        return frame
    bg = light_bg(grid=False)
    bg = Image.blend(frame, bg, q)
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    hx, htop, hw = head_from_mask(mask)
    y = htop - 150
    for i, (w, fam, col, rot) in enumerate(WORDS):
        p = ease_back(prog(tl, 0.1 + i * 0.3, 0.3), 1.8)
        if p <= 0:
            continue
        size = 190 if fam == "inter" else 210
        f = font(fam, size, 850 if fam == "inter" else 600)
        tw_ = d.textlength(w, font=f)
        if tw_ > 1000:
            f = font(fam, int(size * 1000 / tw_), 850 if fam == "inter" else 600)
        g = Image.new("RGBA", (W, 300), (0, 0, 0, 0))
        ImageDraw.Draw(g).text((W / 2, 150), w, font=f, fill=col + (255,), anchor="mm")
        put(lay, g, (W / 2, y + i * 200), 0.6 + 0.4 * p, min(1, p), rot)
    img = bg.convert("RGBA"); img.alpha_composite(lay)
    edge = outline_mask(mask, 12)
    rim = Image.new("RGBA", (W, H), (255, 250, 244, 0)); rim.putalpha(Image.fromarray((edge * 255 * q).astype(np.uint8)))
    img.alpha_composite(rim)
    img.alpha_composite(person_rgba(frame, mask))
    return img.convert("RGB")
