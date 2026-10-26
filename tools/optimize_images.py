"""Build web-sized WebP images for the site from the source photo library.

Reads originals from brand-assets/ and writes to public/assets/img/.
Run once after adding or swapping photos:  python3 tools/optimize_images.py
"""
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "brand-assets"
OUT = ROOT / "public" / "assets" / "img"

# output name -> (source path relative to brand-assets, widths)
PHOTOS = {
    "hero-steaks": ("photos/outlaw_spice-3.jpg", (900, 1800)),
    "flame-grill": ("photos/outlaw_spice-8.jpg", (900, 1800)),
    "lineup": ("photos/49764_L_Group1.JPG", (900, 1800)),
    "lineup-2": ("photos/49764_L_Group2.JPG", (900, 1800)),
    "flatlay": ("photos/OutlawSpice_WW_Flatlays_19.JPG", (900, 1800)),
    "grillside": ("photos/OutlawSpice_WW_Grilling_13.JPG", (900, 1800)),
    "grillside-2": ("photos/OutlawSpice_WW_Grilling_12.JPG", (900,)),
    "grill-veg": ("photos/OutlawSpice_WW_Grilling_41.JPG", (900,)),
    "cutting-board": ("photos/49766_L_03.JPG", (900, 1600)),
    "sliced-steak": ("photos/outlaw_spice-10.jpg", (900, 1800)),
    "brisket-smoker": ("photos/AdobeStock_334128229.jpg", (900, 1800)),
    "ribs": ("photos/AdobeStock_1069933454.JPG", (900, 1800)),
    "shrimp": ("photos/AdobeStock_946685589.JPG", (900, 1800)),
    "pork-chops": ("photos/AdobeStock_890137743.JPG", (900, 1800)),
    "veggies": ("photos/AdobeStock_868542034.JPG", (900, 1800)),
    "kebabs": ("photos/AdobeStock_1015298577.JPG", (900, 1800)),
    "salmon": ("photos/AdobeStock_848029838.JPG", (900, 1800)),
    "mixed-grill": ("photos/AdobeStock_145461088.jpg", (900, 1800)),
    "steaks-dark": ("photos/AdobeStock_109317084.jpg", (900, 1800)),
}

# product id -> slug; each has _01.._04 square shots
PRODUCTS = {
    "49764": "sweet-and-spicy",
    "49765": "ranch-hand",
    "49766": "nashville-hot-chicken",
    "49767": "cowboy-coffee-rub",
    "49768": "whole-hog",
    "49771": "roadhouse-rub",
    "53056": "hoppin-honey-mustard",
    "53057": "jerky-seasoning",
    "53058": "apple-honey-hoedown",
    "53059": "where-theres-hickory-smoke",
    "53060": "kansas-city-best",
}


def save(img, dest, width, quality=80):
    if img.width > width:
        img = img.resize((width, round(img.height * width / img.width)), Image.LANCZOS)
    dest.parent.mkdir(parents=True, exist_ok=True)
    img.save(dest, "WEBP", quality=quality, method=6)


def main():
    for name, (rel, widths) in PHOTOS.items():
        img = Image.open(SRC / rel).convert("RGB")
        for w in widths:
            save(img, OUT / f"{name}-{w}.webp", w)
    for pid, slug in PRODUCTS.items():
        folder = next((SRC / "products").glob(f"{pid} - *"))
        for n in range(1, 5):
            img = Image.open(folder / f"{pid}_0{n}.jpg").convert("RGB")
            save(img, OUT / "products" / f"{slug}-{n}.webp", 900, 82)
            if n == 1:
                save(img, OUT / "products" / f"{slug}-1-480.webp", 480, 82)
    # Transparent jar cutouts for the homepage slider (keep alpha).
    for pid, slug in PRODUCTS.items():
        cut = Image.open(SRC / "products" / "cutouts" / f"{pid}.avif").convert("RGBA")
        dest = OUT / "products" / f"{slug}-cutout.webp"
        cut.save(dest, "WEBP", quality=90, method=6)
    logo = Image.open(SRC / "logo/outlaw-spices-logo-white.png")
    save(logo, OUT / "logo-white.webp", 900, 90)
    logo.save(OUT / "logo-white.png", optimize=True)
    print("done")


if __name__ == "__main__":
    main()
