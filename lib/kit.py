"""Shared helpers for the light «maria.aiart» style effects (pink / violet / orange on warm white)."""
import math
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFilter
from .core import W, H, font, rrect_mask, clamp, ease_out, prog

BG = (244, 242, 240)
SURFACE = (255, 255, 255)
SURFACE2 = (236, 233, 230)
INK = (21, 19, 24)
INK2 = (85, 82, 92)
MUTED = (103, 99, 110)
PINK = (232, 55, 154)
PINK_FILL = (212, 42, 138)
PINK_SOFT = (252, 227, 240)
VIOLET = (106, 86, 160)
VIOLET_SOFT = (233, 228, 244)
ORANGE = (224, 154, 98)
GLOW_PINK = (247, 205, 229)
GLOW_VIOLET = (221, 213, 238)
GLOW_ORANGE = (246, 220, 198)


def light_bg(size=(W, H), grid=True, glows=True):
    """Warm white background with a soft grid and pink/violet glows."""
    w, h = size
    a = np.full((h, w, 3), BG, np.float32)
    if glows:
        yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
        for (cx, cy, r, c, k) in ((w * .82, h * .30, w * .55, GLOW_PINK, .8), (w * .15, h * .72, w * .6, GLOW_VIOLET, .7),
                                  (w * .55, h * 1.0, w * .5, GLOW_ORANGE, .5)):
            g = np.exp(-(((xx - cx) ** 2 + (yy - cy) ** 2) / (2 * r * r)))[..., None] * k
            a = a * (1 - g) + np.array(c, np.float32) * g
    im = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
    if grid:
        d = ImageDraw.Draw(im, "RGBA")
        s = 54
        for x in range(0, w, s):
            d.line((x, 0, x, h), fill=(21, 19, 24, 12))
        for y in range(0, h, s):
            d.line((0, y, w, y), fill=(21, 19, 24, 12))
    return im


def shadow(dst, box, r=36, blur=30, alpha=40, dy=24, color=(70, 40, 80)):
    """Soft card shadow under box on an RGB/RGBA image (in place)."""
    x0, y0, x1, y1 = [int(v) for v in box]
    pad = blur * 3
    sh = Image.new("RGBA", (x1 - x0 + 2 * pad, y1 - y0 + 2 * pad), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle((pad, pad + dy, pad + x1 - x0, pad + y1 - y0 + dy), r, fill=color + (alpha,))
    sh = sh.filter(ImageFilter.GaussianBlur(blur))
    dst.paste(sh, (x0 - pad, y0 - pad), sh)


def rounded(img, r):
    """RGBA copy of img with rounded corners."""
    out = img.convert("RGBA")
    out.putalpha(rrect_mask(img.size, r))
    return out


def pill(text, size=34, bg=PINK_FILL, fg=(255, 255, 255), dot=None, pad=30, weight=650, h=None, outline=None):
    """Pill label as RGBA image."""
    f = font("inter", size, weight)
    tw = ImageDraw.Draw(Image.new("L", (1, 1))).textlength(text, font=f)
    hh = h or int(size * 2.0)
    dw = int(size * 0.9) if dot else 0
    w = int(tw + 2 * pad + dw)
    im = Image.new("RGBA", (w, hh), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, w - 1, hh - 1), hh // 2, fill=bg, outline=outline, width=2 if outline else 0)
    x = pad
    if dot:
        r = size * 0.22
        d.ellipse((x, hh / 2 - r, x + 2 * r, hh / 2 + r), fill=dot)
        x += dw
    d.text((x, hh / 2), text, font=f, fill=fg, anchor="lm")
    return im


def put(dst, im, center, scale=1.0, alpha=1.0, rot=0.0):
    """Paste RGBA im centred, scaled, faded, rotated (in place, dst RGB or RGBA)."""
    if scale <= 0.01 or alpha <= 0.01:
        return
    if rot:
        im = im.rotate(rot, resample=Image.BICUBIC, expand=True)
    if scale != 1:
        im = im.resize((max(2, int(im.width * scale)), max(2, int(im.height * scale))), Image.LANCZOS)
    if alpha < 1:
        im = im.copy(); im.putalpha(im.split()[3].point(lambda v: int(v * alpha)))
    dst.paste(im, (int(center[0] - im.width / 2), int(center[1] - im.height / 2)), im)


def outline_mask(mask, px):
    """Dilated version of a float mask (sticker outline)."""
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * px + 1, 2 * px + 1))
    m = cv2.dilate((mask > 0.5).astype(np.uint8), k).astype(np.float32)
    return cv2.GaussianBlur(m, (0, 0), 2)


def person_rgba(frame, mask):
    out = frame.convert("RGBA")
    out.putalpha(Image.fromarray((np.clip(mask, 0, 1) * 255).astype(np.uint8)))
    return out


def warp_quad(img, quad, size=(W, H)):
    """Perspective-warp an RGBA image onto quad [(x,y)*4: tl,tr,br,bl] of a canvas."""
    w, h = img.size
    src = np.float32([[0, 0], [w, 0], [w, h], [0, h]])
    M = cv2.getPerspectiveTransform(src, np.float32(quad))
    a = cv2.warpPerspective(np.asarray(img.convert("RGBA")), M, size, flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0, 0))
    return Image.fromarray(a)


def tilt_quad(cx, cy, w, h, yaw=0.0, pitch=0.0, persp=0.0009):
    """Corners of a w×h card centred at (cx,cy) rotated by yaw/pitch degrees with simple perspective."""
    ya, pa = math.radians(yaw), math.radians(pitch)
    pts = []
    for (x, y) in ((-w / 2, -h / 2), (w / 2, -h / 2), (w / 2, h / 2), (-w / 2, h / 2)):
        x1, z1 = x * math.cos(ya), x * math.sin(ya)
        y1, z2 = y * math.cos(pa), y * math.sin(pa)
        z = z1 + z2
        s = 1 / (1 + z * persp)
        pts.append((cx + x1 * s, cy + y1 * s))
    return pts


def check(d, cx, cy, r, fill=PINK, fg=(255, 255, 255)):
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=fill)
    d.line((cx - r * .45, cy, cx - r * .1, cy + r * .38, cx + r * .5, cy - r * .35), fill=fg, width=max(2, int(r * .28)), joint="curve")


def spark(d, cx, cy, r, fill=(255, 255, 255), n=8):
    for i in range(n):
        a = math.pi * 2 * i / n
        d.line((cx, cy, cx + r * math.cos(a), cy + r * math.sin(a)), fill=fill, width=max(2, int(r / 4)))
