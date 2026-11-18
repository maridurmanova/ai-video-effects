"""Showcase reel «список»: title + list of all effects, each one lights up and plays in a card, then CTA.

    python3 tools/reel_list.py clip.mp4 music.wav out.mp4 [--word ЭФФЕКТЫ]
"""
import sys, os, json, math, subprocess, argparse
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from lib.core import W, H, FPS, font, clamp, ease_out, ease_back, ease_in_out, prog, lerp, rrect_mask, Clip
from lib.kit import *
from effects import ORDER

TL0 = {"glass-widgets": 1.6, "documentary": 1.4, "orbit": 1.4, "chart-split": 1.4, "spotlight": 1.6, "checklist": 1.4,
       "timeline": 1.2, "text-behind": 1.0, "over-the-shoulder": 1.0, "tier-list": 1.1, "freeze-frame": 0.3, "glass-graph": 1.0,
       "color-grade": 0.5, "exploded-layers": 0.8, "ui-world": 0.9, "digital-zoom": 0.35, "lock-screen": 1.0}
CARD = (245, 800, 835, 1850)
# start points when each effect gets ~2.4 s on screen (its intro animation plays in full)
TL0L = {"glass-widgets": 0.6, "documentary": 0.4, "orbit": 0.3, "chart-split": 0.4, "spotlight": 0.6, "checklist": 0.3,
        "timeline": 0.2, "text-behind": 0.0, "over-the-shoulder": 0.0, "tier-list": 0.0, "freeze-frame": -0.7,
        "glass-graph": 0.0, "color-grade": -0.2, "ui-world": 0.2, "lock-screen": 0.0}       # x0,y0,x1,y1  (590×1050)


def schedule(beat, off, n):
    cuts = [0.0, off]
    for k in range(1, n):
        cuts.append(cuts[-1] + (beat / 2 if k % 2 == 1 else beat))
    return cuts            # effect k plays cuts[k] … cuts[k+1]; CTA from cuts[n]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("video"); ap.add_argument("music"); ap.add_argument("out")
    ap.add_argument("--beat", type=float, default=0.7895); ap.add_argument("--offset", type=float, default=0.655)
    ap.add_argument("--word", default="ЭФФЕКТЫ")
    ap.add_argument("--frames", default="frames_list")
    ap.add_argument("--part", type=int, default=-1, help="0..3: show only that quarter, 3 beats per effect")
    ap.add_argument("--parts", type=int, default=4)
    ap.add_argument("--avatar", help="photo for the round avatar (face crop box x0,y0,x1,y1 after ':')")
    a = ap.parse_args()
    names = ORDER
    n = len(names)
    if a.part >= 0:
        P = math.ceil(n / a.parts); base = a.part * P; P = min(P, n - base)
        cuts = [0.0] + [a.offset + 3 * a.beat * j for j in range(1, P + 1)]
    else:
        P, base = n, 0
        cuts = schedule(a.beat, a.offset, n)
    cw, ch = CARD[2] - CARD[0], CARD[3] - CARD[1]
    jobs = []
    for j in range(P):
        k = base + j; nm = names[k]
        nf = int((cuts[j + 1] - cuts[j]) * FPS) + 3
        tl0 = TL0.get(nm, 0.55) if a.part < 0 else TL0L.get(nm, 0.0)
        jobs.append([f"{k:02d}", nm, tl0, 1.0 + (k * 0.71) % 17, nf, a.frames, [cw, ch]])
    jp = a.frames + ".json"; os.makedirs(a.frames, exist_ok=True); json.dump(jobs, open(jp, "w"))
    subprocess.check_call([sys.executable, os.path.join(ROOT, "tools", "prerender.py"), a.video, jp, "4"])
    dur = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", a.music]))
    clip = Clip(a.video)

    # ---------- static pieces
    bg = light_bg()
    if a.avatar:
        pth, box = a.avatar.split(":")
        avatar = Image.open(pth).convert("RGB").crop(tuple(int(v) for v in box.split(","))).resize((150, 150), Image.LANCZOS)
    else:
        avatar = clip.frame(3.0).crop((300, 380, 780, 860)).resize((150, 150), Image.LANCZOS)
    av = Image.new("RGBA", (170, 170), (0, 0, 0, 0)); ad = ImageDraw.Draw(av)
    ad.ellipse((0, 0, 169, 169), fill=(255, 255, 255))
    m = Image.new("L", (150, 150), 0); ImageDraw.Draw(m).ellipse((0, 0, 149, 149), fill=255)
    av.paste(avatar, (10, 10), m)

    def title(d):
        f1, f2 = font("inter", 70, 800), font("serif", 86, 600)
        l1a, l1b = f"{n}", " эффектов для видео,"
        x = W / 2 - (d.textlength(l1a, font=f1) + d.textlength(l1b, font=f1)) / 2
        d.text((x, 150), l1a, font=f1, fill=PINK, anchor="ls")
        d.text((x + d.textlength(l1a, font=f1), 150), l1b, font=f1, fill=INK, anchor="ls")
        l2a, l2b = "которые делает ", "нейросеть"
        x = W / 2 - (d.textlength(l2a, font=f1) + d.textlength(l2b, font=f2)) / 2
        d.text((x, 240), l2a, font=f1, fill=INK, anchor="ls")
        d.text((x + d.textlength(l2a, font=f1), 240), l2b, font=f2, fill=PINK, anchor="ls")

    def topbar(d, t):
        d.ellipse((W / 2 - 150, 40, W / 2 - 134, 56), fill=PINK)
        fs = int(t * FPS) % FPS
        part = f" · часть {a.part + 1}/{a.parts}" if a.part >= 0 else ""
        d.text((W / 2 - 122, 48), f"maria.aiart · 00:00:{int(t):02d}:{fs:02d}{part}", font=font("mono", 22), fill=MUTED, anchor="lm")

    ROWS = math.ceil(n / 2)
    LY, LH = 290, 34

    def listing(d, cur):
        f, fb, fn = font("inter", 27, 500), font("inter", 27, 700), font("mono", 19)
        for i, nm in enumerate(names):
            col, r = divmod(i, ROWS)
            x = 120 if col == 0 else 580
            y = LY + r * LH
            if i == cur:
                d.rounded_rectangle((x - 12, y - 17, x + 400, y + 17), 9, fill=PINK_SOFT, outline=PINK, width=2)
            d.text((x, y), f"{i + 1:02d}", font=fn, fill=(160, 156, 166), anchor="lm")
            fc = INK if i <= cur else (178, 174, 184)
            d.text((x + 38, y), nm, font=fb if i == cur else f, fill=fc, anchor="lm")
            if i < cur:
                tx = x + 38 + d.textlength(nm, font=f) + 14
                d.line((tx, y, tx + 7, y + 7, tx + 19, y - 8), fill=PINK, width=4, joint="curve")

    def card_frame(k, t):
        d_ = os.path.join(a.frames, f"{k:02d}")
        i = int(clamp((t - cuts[k - base]) * FPS, 0, len(os.listdir(d_)) - 1))
        return Image.open(f"{d_}/{i:03d}.jpg").convert("RGB")

    # ---------- CTA pieces
    def profile_row(d, img, y, subscribed, press):
        x0, x1 = 120, 960
        shadow(img, (x0, y, x1, y + 130), r=65, alpha=35)
        d.rounded_rectangle((x0, y, x1, y + 130), 65, fill=SURFACE)
        put(img, av, (x0 + 75, y + 65), 0.62)
        d.text((x0 + 145, y + 48), "maria.aiart", font=font("inter", 32, 700), fill=INK, anchor="lm")
        d.text((x0 + 145, y + 90), "Мария Дурманова | AI без хаоса", font=font("inter", 24, 500), fill=MUTED, anchor="lm")
        bw = 250; bx = x1 - 22 - bw
        s = 1 - 0.06 * press
        if subscribed:
            d.rounded_rectangle((bx, y + 25, bx + bw, y + 105), 40, fill=SURFACE2)
            d.text((bx + bw / 2, y + 65), "Вы подписаны ✓", font=font("inter", 28, 650), fill=INK, anchor="mm")
        else:
            cx, cy = bx + bw / 2, y + 65
            d.rounded_rectangle((cx - bw / 2 * s, cy - 40 * s, cx + bw / 2 * s, cy + 40 * s), 40, fill=PINK_FILL)
            d.text((cx, cy), "Подписаться", font=font("inter", 30, 700), fill=(255, 255, 255), anchor="mm")
        return bx + bw / 2, y + 65

    def list_card(img, y, typed, sent):
        x0, x1, h = 90, 990, 920
        shadow(img, (x0, y, x1, y + h), r=40, alpha=40)
        d = ImageDraw.Draw(img)
        d.rounded_rectangle((x0, y, x1, y + h), 40, fill=SURFACE)
        d.rounded_rectangle((x0 + 40, y + 36, x0 + 92, y + 88), 14, fill=PINK_FILL); spark(d, x0 + 66, y + 62, 16)
        d.text((x0 + 112, y + 62), f"{n} эффектов", font=font("inter", 38, 800), fill=INK, anchor="lm")
        d.rounded_rectangle((x1 - 260, y + 42, x1 - 40, y + 82), 20, outline=(200, 196, 204), width=2)
        d.text((x1 - 150, y + 62), "ПОЛНЫЙ СПИСОК", font=font("mono", 18, 700), fill=MUTED, anchor="mm")
        f, fn = font("inter", 25, 600), font("mono", 17)
        for i, nm in enumerate(names):
            col, r = divmod(i, ROWS)
            x = x0 + 40 + col * 440; yy = y + 130 + r * 49
            d.text((x, yy), f"{i + 1:02d}", font=fn, fill=(160, 156, 166), anchor="lm")
            d.text((x + 36, yy), nm, font=f, fill=INK, anchor="lm")
            check(d, x + 390, yy, 14)
        by = y + h - 100
        d.rounded_rectangle((x0 + 30, by, x1 - 30, by + 72), 36, fill=SURFACE2)
        d.rounded_rectangle((x0 + 46, by + 14, x0 + 90, by + 58), 12, fill=VIOLET)
        d.rounded_rectangle((x0 + 56, by + 24, x0 + 80, by + 48), 7, outline=(255, 255, 255), width=3)
        if sent:
            d.text((x0 + 110, by + 36), f"✓ «{a.word}» отправлено", font=font("inter", 30, 700), fill=PINK_FILL, anchor="lm")
        else:
            d.text((x0 + 110, by + 36), typed, font=font("inter", 30, 600), fill=INK, anchor="lm")
            cx_ = x0 + 112 + d.textlength(typed, font=font("inter", 30, 600))
            d.line((cx_, by + 18, cx_, by + 54), fill=PINK, width=3)
        d.ellipse((x1 - 100, by + 8, x1 - 44, by + 64), fill=PINK_FILL)
        d.line((x1 - 72, by + 50, x1 - 72, by + 22), fill=(255, 255, 255), width=5)
        d.line((x1 - 84, by + 34, x1 - 72, by + 22, x1 - 60, by + 34), fill=(255, 255, 255), width=5)

    LINES = [f"Пиши «{a.word}»", "в комментариях —", "и я пришлю тебе", f"все {n} эффектов", "в директ.", "подписаться!"]

    def cta(t):
        img = bg.copy(); d = ImageDraw.Draw(img)
        topbar(d, cuts[P] + t); title(d)
        seg = (dur - cuts[P] - 0.3) / len(LINES)
        li = min(len(LINES) - 1, int(t / seg))
        lq = ease_out(prog(t - li * seg, 0, 0.18))
        line = LINES[li]
        f = font("inter", 54, 800)
        if "«" in line:
            pre, w_, post = line.partition(f"«{a.word}»")
            x = W / 2 - (d.textlength(pre, font=f) + d.textlength(w_, font=f)) / 2
            d.text((x, 340 + 14 * (1 - lq)), pre, font=f, fill=INK, anchor="lm")
            d.text((x + d.textlength(pre, font=f), 340 + 14 * (1 - lq)), w_, font=f, fill=PINK, anchor="lm")
        else:
            d.text((W / 2, 340 + 14 * (1 - lq)), line, font=f, fill=INK, anchor="mm")
        q = ease_back(prog(t, 0.0, 0.4), 1.4)
        sub = t > (len(LINES) - 1) * seg + 0.6
        press = math.exp(-((t - ((len(LINES) - 1) * seg + 0.55)) / 0.06) ** 2)
        bx, by = profile_row(d, img, 440 + 60 * (1 - min(1, q)), sub, press)
        word = a.word.lower()
        ty = clamp((t - 0.6) / 1.2)
        typed = word[:int(len(word) * ty)]
        list_card(img, 620 + 200 * (1 - min(1, q)), typed, t > 2.0)
        # cursor click on subscribe
        if t > (len(LINES) - 1) * seg - 0.4:
            k = ease_in_out(prog(t, (len(LINES) - 1) * seg - 0.4, 0.9))
            cx, cy = lerp(bx + 220, bx + 10, k), lerp(by + 260, by + 12, k)
            d.polygon([(cx, cy), (cx, cy + 46), (cx + 12, cy + 34), (cx + 22, cy + 56), (cx + 30, cy + 52), (cx + 20, cy + 31), (cx + 36, cy + 31)], fill=INK, outline=(255, 255, 255))
        return img

    def frame(t):
        if t >= cuts[P]:
            return cta(t - cuts[P])
        j = max(i for i in range(P) if cuts[i] <= t); k = base + j
        img = bg.copy(); d = ImageDraw.Draw(img)
        topbar(d, t); title(d); listing(d, k)
        x0, y0, x1, y1 = CARD
        p = ease_out(prog(t - cuts[j], 0, 0.12))
        shadow(img, CARD, r=40, alpha=55)
        fr = card_frame(k, t)
        img.paste(fr, (x0, y0), rrect_mask(fr.size, 40))
        d = ImageDraw.Draw(img, "RGBA")
        chip = f"{k + 1:02d}/{n}"
        d.rounded_rectangle((x0 + 26, y0 + 26, x0 + 156, y0 + 72), 23, fill=(21, 19, 24, 170))
        d.text((x0 + 91, y0 + 49), chip, font=font("mono", 22, 700), fill=(255, 255, 255), anchor="mm")
        pl = pill(names[k], 40, bg=PINK_FILL, weight=700)
        put(img, pl, (W / 2, y1 - 6), 0.9 + 0.1 * p)
        put(img, av, (x1 + 20, y1 - 110), 0.8)
        return img

    tmp = a.out + ".v.mp4"
    ff = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                           "-i", a.music, "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-preset", "medium", "-crf", "17", "-pix_fmt", "yuv420p",
                           "-c:a", "aac", "-b:a", "256k", "-shortest", "-movflags", "+faststart", a.out], stdin=subprocess.PIPE)
    N = int(dur * FPS)
    for i in range(N):
        ff.stdin.write(np.asarray(frame(i / FPS).convert("RGB")).tobytes())
        if i % 90 == 0:
            print("frame", i, N, flush=True)
    ff.stdin.close(); ff.wait()
    if len(sys.argv) and os.environ.get("PREVIEW"):
        pass
    print("done", a.out)


if __name__ == "__main__":
    main()
