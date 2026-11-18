"""Pre-render effect frames for the showcase reels: jobs.json → frames/<key>/000.jpg …"""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from multiprocessing import Pool

CTX = None


def init(video):
    global CTX
    from lib.ctx import Ctx
    CTX = Ctx(video)


def job(j):
    from effects import load
    key, name, tl0, ts0, n, outdir, size = j
    m = load(name)
    d = os.path.join(outdir, key); os.makedirs(d, exist_ok=True)
    for i in range(n):
        p = f"{d}/{i:03d}.jpg"
        if os.path.exists(p):
            continue
        im = m.render(CTX, tl0 + i / 30, min(ts0 + i / 30, CTX.clip.duration - 0.1))
        if size:
            im = im.resize(tuple(size), resample=1)
        im.save(p + ".tmp.jpg", quality=92); os.replace(p + ".tmp.jpg", p)
    return key


if __name__ == "__main__":
    video, jobs = sys.argv[1], json.load(open(sys.argv[2]))
    with Pool(int(sys.argv[3]) if len(sys.argv) > 3 else 4, initializer=init, initargs=(video,)) as p:
        for k in p.imap_unordered(job, jobs):
            print("done", k, flush=True)
