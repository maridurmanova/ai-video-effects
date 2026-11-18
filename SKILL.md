---
name: effects
description: 28 talking-head reel effects in one skill. The command /effects plus an effect name (for example /effects text-behind, /effects lock-screen, /effects cinematic-mode) applies that effect to the user's vertical clip; /effects list shows all of them. Use when the user attaches a video and types /effects.
---

# /effects — one command, one edit

```
/effects text-behind         (+ a video attached or a path)
/effects list                — all 28 effects with a one-line description
```

Scripts live next to this file. In Claude Code that is `~/.claude/skills/effects/`; when the skill was
uploaded in the app (Settings → Skills) it is wherever this SKILL.md sits in the sandbox — `cd` there first.
Needs Python 3.10+, ffmpeg and `pip install -r requirements.txt` (add `--break-system-packages` if pip refuses).
The first run downloads a person-segmentation model (~170 MB, once, from github.com).

## Effects

| # | name | what it does |
|---|---|---|
| 01 | `lock-screen` | phone lock screen: big clock behind the head, «Ролик смонтирован ✓» notification |
| 02 | `exploded-layers` | the frame tilts in 3D and splits into layers: background, you, graphics |
| 03 | `type-ring` | a ring of text spins around the head, passing behind it |
| 04 | `dynamic-island` | the phone's island expands: «Монтирую…» → «Монтаж готов ✓» |
| 05 | `liquid-glass` | a glass lens glides over the frame and refracts it, glass dock below |
| 06 | `cinematic-mode` | background melts into bokeh, focus box on the face, aperture dial |
| 07 | `ai-glow` | pink-violet-orange glow runs around the edges while the AI «thinks» |
| 08 | `frame-break` | the head breaks out over the top edge of the frame |
| 09 | `headline-wall` | magazine headline words stack up behind the speaker |
| 10 | `lift-subject` | the speaker lifts off the background with a white halo |
| 11 | `spatial-window` | the clip floats in a glass window over a blurred room |
| 12 | `phone-mockup` | the clip plays inside a phone on a lilac background |
| 13 | `digital-zoom` | punch-in zooms with a camera viewfinder, REC and zoom readout |
| 14 | `ui-world` | the clip lives in an app window with a file chip, then zooms in |
| 15 | `photo-wall` | framed shots from the same clip pin themselves to the wall behind |
| 16 | `text-behind` | a huge word rises behind the speaker's head |
| 17 | `freeze-frame` | flash, freeze, dimmed background, white sticker outline, name tag |
| 18 | `orbit` | mini reels orbit around the speaker, passing behind and in front |
| 19 | `glass-widgets` | glass widgets (counters, render bar, profile) float around the speaker |
| 20 | `over-the-shoulder` | push-in, two proof cards (before / after, counting up) beside the head |
| 21 | `tier-list` | glass S/A/B/C/D ranking fills itself |
| 22 | `glass-graph` | glass card on the chest, % counts up, graph climbs |
| 23 | `spotlight` | dark stage, neon word behind the head, spotlight on the speaker |
| 24 | `documentary` | b/w documentary card: big title, name plate, «subscribe» click |
| 25 | `checklist` | glass card ticks off every editing step |
| 26 | `color-grade` | flat → cinematic grade with a before/after wipe |
| 27 | `chart-split` | split screen: bar chart on top, speaker below |
| 28 | `timeline` | editor timeline with tracks and a render progress bar |

All on-screen texts are Russian by default and sit at the top of each `effects/*.py` file
(constants like `WORD`, `WORDS`, `TEXT`, `BEFORE`, `AFTER`, `HEADER`, `LABEL`). Name and @handle are in `config.json`.

## How to run it (you, the assistant)

1. Find the clip. If it is 4K, HEVC or over 100 MB, make a proxy first:
   `ffmpeg -i in.mov -vf "scale=1080:1920,fps=30" -c:v libx264 -crf 16 -an clip.mp4`
2. Ask once for the name / @handle to show (or read `config.json`) and the words for the cards, if the effect has any.
3. **Preview first:** `python3 run.py EFFECT clip.mp4 --preview 1.0,2.0,4.0` → show the PNGs, adjust texts on request.
4. Render: `python3 run.py EFFECT clip.mp4 -o out.mp4` (keeps the voice; `--no-voice --music` for music only;
   `--start 3` starts the effect at 3 s).
5. Before handing over: look at a few frames and run `ffmpeg -i out.mp4 -vf blackdetect -f null -`.
