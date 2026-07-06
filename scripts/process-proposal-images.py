#!/usr/bin/env python3
"""Resize/compress proposal assets to WebP for joyforest.tw/pages/proposal."""
from __future__ import annotations

from pathlib import Path
from PIL import Image

WORKSPACE = Path(__file__).resolve().parents[1]
SRC_DIR = WORKSPACE / "assets/images/proposal/_source"
OUT_DIR = WORKSPACE / "assets/images/proposal"

# (source filename prefix in _source/, output base name without extension)
ASSETS: list[tuple[str, str]] = [
    ("01-friends-preparing-balloons", "joyforest-proposal-friends-preparing-balloons-indoor-01"),
    ("02-groom-ring-ready-red-carpet", "joyforest-outdoor-proposal-groom-ring-ready-red-carpet-01"),
    ("03-themed-backdrop-stitch-ohana", "joyforest-outdoor-proposal-themed-backdrop-stitch-ohana-01"),
    ("04-surprise-kneeling-ohana-forever", "joyforest-outdoor-surprise-proposal-kneeling-ohana-forever-01"),
    ("05-couple-red-carpet-bubbles", "joyforest-outdoor-proposal-couple-red-carpet-bubbles-01"),
    ("06-success-friends-celebration-petals", "joyforest-outdoor-proposal-success-friends-celebration-01"),
    ("07-night-outdoor-party-cinema-lights", "joyforest-proposal-night-outdoor-party-cinema-lights-01"),
    ("08-friends-group-victory-photo", "joyforest-outdoor-proposal-friends-group-victory-photo-01"),
]

HERO_SOURCE = "06-success-friends-celebration-petals"
HERO_OUTPUT = "hero-proposal-outdoor-success-friends-celebration-joyforest.webp"
OG_SOURCE = "04-surprise-kneeling-ohana-forever"


def to_rgb(img: Image.Image) -> Image.Image:
    if img.mode in ("RGBA", "P"):
        bg = Image.new("RGB", img.size, (255, 255, 255))
        if img.mode == "P":
            img = img.convert("RGBA")
        bg.paste(img, mask=img.split()[-1] if img.mode == "RGBA" else None)
        return bg
    return img.convert("RGB")


def resize_max_w(img: Image.Image, max_w: int) -> Image.Image:
    w, h = img.size
    if w <= max_w:
        return img
    nh = int(round(h * (max_w / w)))
    return img.resize((max_w, nh), Image.Resampling.LANCZOS)


def save_webp(img: Image.Image, path: Path, quality: int = 82) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path, format="WEBP", quality=quality, method=6)


def make_og_cover(src: Image.Image, w: int = 1200, h: int = 630) -> Image.Image:
    img = to_rgb(src)
    sw, sh = img.size
    scale = max(w / sw, h / sh)
    nw, nh = int(sw * scale), int(sh * scale)
    img = img.resize((nw, nh), Image.Resampling.LANCZOS)
    left = (nw - w) // 2
    top = (nh - h) // 2
    return img.crop((left, top, left + w, top + h))


def find_source(prefix: str) -> Path | None:
    for ext in (".jpg", ".jpeg", ".png", ".webp", ".heic", ".JPG", ".JPEG", ".PNG"):
        p = SRC_DIR / f"{prefix}{ext}"
        if p.exists():
            return p
    matches = sorted(SRC_DIR.glob(f"{prefix}.*"))
    return matches[0] if matches else None


def process_one(src_path: Path, base: str) -> tuple[int, int]:
    raw = Image.open(src_path)
    rgb = to_rgb(raw)
    full = resize_max_w(rgb, 1600)
    thumb = resize_max_w(rgb.copy(), 640)
    save_webp(full, OUT_DIR / f"{base}-full.webp")
    save_webp(thumb, OUT_DIR / f"{base}-thumb.webp")
    return full.size


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    missing: list[str] = []

    for prefix, base in ASSETS:
        src = find_source(prefix)
        if not src:
            missing.append(prefix)
            continue
        size = process_one(src, base)
        print(f"OK {src.name} -> {base}-*.webp ({size[0]}x{size[1]})")

    if missing:
        print("\nMissing source files in", SRC_DIR)
        for name in missing:
            print(f"  - {name}.jpg (or .jpeg/.png/.webp)")
        raise SystemExit(1)

    hero_src = find_source(HERO_SOURCE)
    if hero_src:
        rgb = to_rgb(Image.open(hero_src))
        hero = resize_max_w(rgb, 2400)
        save_webp(hero, OUT_DIR / HERO_OUTPUT)
        print(f"Hero written: {HERO_OUTPUT}")

    og_src = find_source(OG_SOURCE)
    if og_src:
        og = make_og_cover(Image.open(og_src))
        og.save(OUT_DIR / "og-proposal-joyforest.jpg", format="JPEG", quality=88, optimize=True)
        print("OG written: og-proposal-joyforest.jpg")

    print("Done. Output:", OUT_DIR)


if __name__ == "__main__":
    main()
