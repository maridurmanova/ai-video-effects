"""ui-world — your clip lives inside an app window: file chip, sidebar, then a zoom into the video."""
from PIL import Image, ImageDraw
from lib.core import *
from lib.kit import *

NAME = "ui-world"
DESC = "клип внутри окна приложения, потом наезд в кадр"
SFX = [(0.0, "pop"), (0.6, "key"), (0.75, "key"), (0.9, "chime"), (1.5, "whoosh")]
WIN = (90, 330, 990, 1590)


def render(ctx, tl, ts):
    frame, _ = ctx.src(ts, with_mask=False)
    z = ease_in_out(prog(tl, 1.5, 0.6))
    out = light_bg()
    x0, y0, x1, y1 = WIN
    q = ease_back(prog(tl, 0.0, 0.45), 1.4)
    # window
    win = Image.new("RGBA", (x1 - x0, y1 - y0), (0, 0, 0, 0))
    d = ImageDraw.Draw(win)
    d.rounded_rectangle((0, 0, win.width - 1, win.height - 1), 36, fill=SURFACE, outline=(21, 19, 24, 26), width=2)
    for i, c in enumerate((PINK, VIOLET, ORANGE)):
        d.ellipse((34 + i * 30, 34, 52 + i * 30, 52), fill=c)
    d.text((win.width / 2, 43), "монтаж · clip_001", font=font("mono", 22), fill=MUTED, anchor="mm")
    for i in range(4):
        y = 140 + i * 90
        d.rounded_rectangle((30, y, 90, y + 60), 16, fill=PINK_SOFT if i == 1 else SURFACE2)
    vx0, vy0, vx1, vy1 = 130, 110, win.width - 40, 110 + 860
    vid = frame.resize((vx1 - vx0, int((vx1 - vx0) * H / W)), Image.LANCZOS)
    vid = vid.crop((0, (vid.height - (vy1 - vy0)) // 2, vid.width, (vid.height - (vy1 - vy0)) // 2 + vy1 - vy0))
    win.paste(rounded(vid, 24), (vx0, vy0), rounded(vid, 24))
    # dashed drop zone with file chip
    p = ease_out(prog(tl, 0.5, 0.4))
    if p > 0:
        bx0, by0, bx1, by1 = vx0, vy1 + 40, vx1, vy1 + 200
        for xx in range(bx0, bx1, 26):
            d.line((xx, by0, min(xx + 14, bx1), by0), fill=PINK, width=3); d.line((xx, by1, min(xx + 14, bx1), by1), fill=PINK, width=3)
        for yy in range(by0, by1, 26):
            d.line((bx0, yy, bx0, min(yy + 14, by1)), fill=PINK, width=3); d.line((bx1, yy, bx1, min(yy + 14, by1)), fill=PINK, width=3)
        chip = pill("clip_001.mp4", 30, bg=SURFACE, fg=INK, outline=(21, 19, 24, 40))
        cd = ImageDraw.Draw(chip)
        if tl > 0.9:
            check(cd, chip.width - 22, chip.height / 2, 0)
        cx, cy = (bx0 + bx1) / 2, (by0 + by1) / 2 + 30 * (1 - p)
        win.paste(chip, (int(cx - chip.width / 2), int(cy - chip.height / 2)), chip)
        if tl > 0.9:
            check(d, cx + chip.width / 2 + 34, cy, 22)
    shadow(out, (x0, y0, x1, y1), alpha=45)
    put(out, win, ((x0 + x1) / 2, (y0 + y1) / 2 + 200 * (1 - min(1, q))), q)
    if z > 0:   # zoom into the video area
        vcx, vcy = x0 + (vx0 + vx1) / 2, y0 + (vy0 + vy1) / 2
        vw = vx1 - vx0
        k = 1 + (W / vw - 1) * z
        box = (vcx - W / 2 / k, vcy - H / 2 / k, vcx + W / 2 / k, vcy + H / 2 / k)
        out = out.transform((W, H), Image.AFFINE, (1 / k, 0, box[0], 0, 1 / k, box[1]), Image.BICUBIC, fillcolor=BG)
        if z > 0.9:
            out = Image.blend(out, frame, (z - 0.9) / 0.1)
    return out
