#!/usr/bin/env python3
"""Resize/compress pet-party assets to WebP for joyforest.tw."""
from __future__ import annotations

from pathlib import Path
from PIL import Image

WORKSPACE = Path(__file__).resolve().parents[1]
SRC_DIR = Path(
    "/Users/joyforest/.cursor/projects/Users-joyforest-Documents-joyforest-site-full/assets"
)
OUT_PARTY = WORKSPACE / "assets/images/pet-party"
OUT_PHOTO = WORKSPACE / "assets/images/pet-party-photography"

# (source_glob or name, base_name, dest: "party"|"photo"|"both")
# base_name without extension; output as {base}-full.webp and {base}-thumb.webp
ASSETS: list[tuple[str, str, str]] = [
    ("BBBCDF74-37F0-47A8-A0A4-1C48EDB94F2E_4_5005_c-274ef3a8-c7d6-4efa-8441-31d32d9152bc.png", "pet-photography-studio-shiba-goggles-joyforest", "photo"),
    ("143D4653-A7F1-4347-A174-E46A6AB1AD3F_4_5005_c-591d321b-e25e-4b00-bd00-770fe1cc06b5.png", "pet-photography-studio-owner-two-cats-joyforest", "photo"),
    ("ADC7D76D-4518-4E91-8876-75F38B2CF170_4_5005_c-e7ebf92e-1dc7-480c-95ea-68760e847c7e.png", "pet-photography-studio-cat-pompom-collar-joyforest", "photo"),
    ("EE76B633-26F1-40B1-9ED5-C250C91C9DF3_4_5005_c-36451a76-f10c-426f-b569-136834598020.png", "pet-photography-studio-owner-cat-hug-joyforest", "photo"),
    ("9140707F-82A3-4181-B425-2010885B87A6_4_5005_c-632fa222-4b03-4e99-a1c0-2625c5f85b4b.png", "pet-photography-studio-owner-border-collie-dark-joyforest", "photo"),
    ("DA9FA296-8D2A-45CC-A0C6-430F559B6419_4_5005_c-e5e1df41-0a98-44d1-a503-6f1f4f45ca75.png", "pet-photography-studio-owner-border-collie-floor-joyforest", "photo"),
    ("1D80276F-B3D4-4646-957C-77247321672C_4_5005_c-470628e5-6c9f-4395-9d16-b765141341f7.png", "pet-photography-studio-corgi-birthday-pink-joyforest", "photo"),
    ("775D8D7D-A72A-4D36-BF30-5672F656421B_1_102_o-7279280f-d77a-42ee-8af9-a7e62b1a1f49.png", "pet-photography-studio-border-collie-sunglasses-joyforest", "photo"),
    ("481BC11E-E75D-4BC0-BE15-74887DCD4A80_4_5005_c-d919aabe-165e-462a-a157-de9164907c13.png", "pet-photography-studio-dachshunds-tent-lights-joyforest", "photo"),
    ("E98E106B-4A25-421C-AAA1-603A98CAA8F1_1_105_c-aef69b82-9ffc-4cac-9c3f-00fc46349ac7.png", "pet-photography-studio-corgi-birthday-graphic-joyforest", "photo"),
    ("5B523146-69FB-43EF-A559-DC6107F7D73B-5767cbe6-81b0-4851-b492-7e72599639eb.png", "pet-photography-studio-dogs-cat-teepee-joyforest", "photo"),
    ("E45B2A98-63AF-4B79-8B35-6747DCCC82BC_1_105_c-d12493d6-1933-44b2-b7f1-9642324ebee4.png", "pet-photography-outdoor-golden-owner-grass-dome-joyforest", "both"),
    ("C9E046A4-D353-4B75-ADC1-DD3FA3AA91BC_4_5005_c-1bb84965-6657-43d0-9079-aa07e90c2b94.png", "pet-party-husky-bernese-grass-dome-joyforest", "party"),
    ("997C02AD-B39D-4898-9453-AA9CE3BEB9AA_4_5005_c-0864117a-da6c-4b7d-9674-9580c851043d.png", "pet-party-chihuahua-grass-teepee-dome-joyforest", "party"),
    ("E075A018-707A-44EC-9E4B-94C38E83CB97_4_5005_c-6974bae6-77a0-4442-8786-7a0cab46e4bf.png", "pet-party-dogs-grass-picnic-joyforest", "party"),
]


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


def process_one(src_path: Path, base: str, out_dir: Path) -> tuple[int, int]:
    raw = Image.open(src_path)
    rgb = to_rgb(raw)
    full = resize_max_w(rgb, 1600)
    thumb = resize_max_w(rgb.copy(), 640)
    save_webp(full, out_dir / f"{base}-full.webp")
    save_webp(thumb, out_dir / f"{base}-thumb.webp")
    return full.size


def split_collage(src_path: Path, out_photo: Path, out_party: Path) -> None:
    raw = Image.open(src_path)
    rgb = to_rgb(raw)
    w, h = rgb.size
    cw, ch = w // 2, h // 2
    tiles = [
        (0, 0, cw, ch, "pet-photography-studio-pomeranian-dress-stool-joyforest", "photo"),
        (cw, 0, w, ch, "pet-photography-outdoor-pomeranian-grass-fence-joyforest", "photo"),
        (0, ch, cw, h, "pet-photography-outdoor-chihuahua-grass-teepee-dome-joyforest", "both"),
        (cw, ch, w, h, "pet-photography-outdoor-chihuahua-flowers-dome-joyforest", "photo"),
    ]
    for x1, y1, x2, y2, base, dest in tiles:
        crop = rgb.crop((x1, y1, x2, y2))
        dirs = []
        if dest == "both":
            dirs = [out_photo, out_party]
        elif dest == "photo":
            dirs = [out_photo]
        else:
            dirs = [out_party]
        for d in dirs:
            process_image_obj(crop, d, base)


def process_image_obj(rgb: Image.Image, out_dir: Path, base: str) -> None:
    full = resize_max_w(rgb, 1600)
    thumb = resize_max_w(rgb.copy(), 640)
    save_webp(full, out_dir / f"{base}-full.webp")
    save_webp(thumb, out_dir / f"{base}-thumb.webp")


def main() -> None:
    OUT_PARTY.mkdir(parents=True, exist_ok=True)
    OUT_PHOTO.mkdir(parents=True, exist_ok=True)

    for fname, base, dest in ASSETS:
        src = SRC_DIR / fname
        if not src.exists():
            print("MISSING", src)
            continue
        if dest == "party":
            process_one(src, base, OUT_PARTY)
        elif dest == "photo":
            process_one(src, base, OUT_PHOTO)
        else:
            process_one(src, base, OUT_PARTY)
            process_one(src, base, OUT_PHOTO)

    collage = SRC_DIR / "D5B8BADF-82ED-4A29-B0CA-6EAD4FC58F2C_1_102_o-d0f7b456-bd7f-4c42-9981-e79984aadfd3.png"
    if collage.exists():
        split_collage(collage, OUT_PHOTO, OUT_PARTY)

    # OG images (JPEG for maximum compatibility + user asked jpg path)
    hero_party_src = SRC_DIR / "E075A018-707A-44EC-9E4B-94C38E83CB97_4_5005_c-6974bae6-77a0-4442-8786-7a0cab46e4bf.png"
    hero_photo_src = SRC_DIR / "5B523146-69FB-43EF-A559-DC6107F7D73B-5767cbe6-81b0-4851-b492-7e72599639eb.png"
    if hero_party_src.exists():
        og = make_og_cover(Image.open(hero_party_src))
        og.save(OUT_PARTY / "og-pet-party-joyforest.jpg", format="JPEG", quality=88, optimize=True)
    if hero_photo_src.exists():
        og = make_og_cover(Image.open(hero_photo_src))
        og.save(OUT_PHOTO / "og-pet-party-photography-joyforest.jpg", format="JPEG", quality=88, optimize=True)

    # Hero webp sources (2400 max width)
    def hero_webp(src_name: str, out_path: Path) -> None:
        p = SRC_DIR / src_name
        if not p.exists():
            return
        rgb = to_rgb(Image.open(p))
        im = resize_max_w(rgb, 2400)
        save_webp(im, out_path)

    hero_webp(
        "E075A018-707A-44EC-9E4B-94C38E83CB97_4_5005_c-6974bae6-77a0-4442-8786-7a0cab46e4bf.png",
        OUT_PARTY / "hero-pet-party-grass-picnic-joyforest.webp",
    )
    hero_webp(
        "5B523146-69FB-43EF-A559-DC6107F7D73B-5767cbe6-81b0-4851-b492-7e72599639eb.png",
        OUT_PHOTO / "hero-pet-party-photography-teepee-joyforest.webp",
    )

    print("Done. Output:", OUT_PARTY, OUT_PHOTO)


if __name__ == "__main__":
    main()
