"""Effect registry: /effects <name> → module. ORDER = all 28 effects."""
import importlib

ORDER = [
    # set 1
    "glass-widgets", "documentary", "orbit", "chart-split", "spotlight", "checklist", "timeline",
    # set 2
    "text-behind", "over-the-shoulder", "tier-list", "freeze-frame", "glass-graph", "color-grade",
    # set 3
    "exploded-layers", "ui-world", "frame-break", "digital-zoom", "phone-mockup", "cinematic-mode", "ai-glow",
    "lift-subject", "type-ring", "dynamic-island", "spatial-window", "liquid-glass", "headline-wall", "photo-wall",
    "lock-screen",
]
FILES = {"over-the-shoulder": "over_shoulder"}


def load(name):
    return importlib.import_module("effects." + FILES.get(name, name.replace("-", "_")))


def all_effects():
    return [load(n) for n in ORDER]
