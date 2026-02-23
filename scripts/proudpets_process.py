from PIL import Image, ImageOps
from pathlib import Path
import argparse
import re
import shutil

RAW = Path("/Users/toddcole/Image_Shrinker/raw")
OUT = Path("/Users/toddcole/Image_Shrinker/ready")
ARCH = Path("/Users/toddcole/Image_Shrinker/processed_raw")

EXTS = {".jpg", ".jpeg", ".png", ".webp", ".tif", ".tiff"}


def slugify(s: str) -> str:
    s = s.lower().strip()
    s = re.sub(r"\.[a-z0-9]+$", "", s)
    s = re.sub(r"[^a-z0-9]+", "-", s)
    s = re.sub(r"-{2,}", "-", s).strip("-")
    return s or "image"


def crop_to_4x3(img: Image.Image) -> Image.Image:
    w, h = img.size
    target = 4 / 3
    ratio = w / h

    if ratio > target:
        new_w = int(h * target)
        left = (w - new_w) // 2
        return img.crop((left, 0, left + new_w, h))
    else:
        new_h = int(w / target)
        top = (h - new_h) // 2
        return img.crop((0, top, w, top + new_h))


def next_index(out_dir: Path, slug: str) -> int:
    existing = list(out_dir.glob(f"{slug}-*.webp"))
    if not existing:
        return 1

    nums = []
    for p in existing:
        m = re.search(r"-(\d+)\.webp$", p.name)
        if m:
            nums.append(int(m.group(1)))

    return max(nums) + 1 if nums else 1


def process_one(src: Path, width: int, quality: int) -> Path:
    if src.parent != RAW:
        slug = src.parent.name.lower()
    else:
        slug = slugify(src.stem)

    OUT.mkdir(parents=True, exist_ok=True)

    idx = next_index(OUT, slug)
    dst = OUT / f"{slug}-{idx:02d}.webp"

    img = Image.open(src)
    img = ImageOps.exif_transpose(img)
    img = img.convert("RGB")
    img = crop_to_4x3(img)

    new_h = int(width * 3 / 4)
    img = img.resize((width, new_h), Image.Resampling.LANCZOS)
    img.save(dst, "WEBP", quality=quality, method=6)

    return dst


def main():
    ap = argparse.ArgumentParser(description="ProudPets processor")
    ap.add_argument("--keep-raw", action="store_true")
    ap.add_argument("--width", type=int, default=1200)
    ap.add_argument("--quality", type=int, default=85)
    args = ap.parse_args()

    files = [
        p for p in RAW.rglob("*")
        if p.is_file() and p.suffix.lower() in EXTS
    ]

    if not files:
        print(f"No images in {RAW}")
        return

    ok = 0

    for src in files:
        try:
            out = process_one(src, args.width, args.quality)
            ok += 1
            print(f"OK: {src.name} -> {out.name}")

            if not args.keep_raw:
                if src.parent != RAW:
                    dest = ARCH / src.parent.name
                else:
                    dest = ARCH / "unsorted"

                dest.mkdir(parents=True, exist_ok=True)
                shutil.move(str(src), str(dest / src.name))

        except Exception as e:
            print(f"FAIL: {src}: {e}")

    print(f"Done. Processed {ok} image(s).")
    print(f"Output: {OUT}")

    if args.keep_raw:
        print("Raw files kept.")
    else:
        print(f"Raw files moved to: {ARCH}")


if __name__ == "__main__":
    main()
