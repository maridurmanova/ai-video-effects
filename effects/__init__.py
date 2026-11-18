"""Effect registry: /effects <name> → module. ORDER = all 28 effects."""
import importlib

ORDER = [  # newest and most trending first
    "lock-screen",
    "exploded-layers",
    "type-ring",
    "dynamic-island",
    "liquid-glass",
    "cinematic-mode",
    "ai-glow",
    "frame-break",
    "headline-wall",
    "lift-subject",
    "spatial-window",
    "phone-mockup",
    "digital-zoom",
    "ui-world",
    "photo-wall",
    "text-behind",
    "freeze-frame",
    "orbit",
    "glass-widgets",
    "over-the-shoulder",
    "tier-list",
    "glass-graph",
    "spotlight",
    "documentary",
    "checklist",
    "color-grade",
    "chart-split",
    "timeline",
]
FILES = {"over-the-shoulder": "over_shoulder"}


def load(name):
    return importlib.import_module("effects." + FILES.get(name, name.replace("-", "_")))


def all_effects():
    return [load(n) for n in ORDER]
