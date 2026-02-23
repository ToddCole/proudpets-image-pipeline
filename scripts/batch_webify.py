from PIL import Image, ImageOps
from pathlib import Path
import argparse
import shutil

VALID_EXTS = {".jpg", ".jpeg", ".png", ".tif", ".tiff", ".webp"}

def crop_to_aspect(img: Image.Image, target_w: int, target_h: int, y_bias: float = 0.0) -> Image.Image:
    """
    Centre-crop to aspect ratio.
    y_bias shifts the crop up/down slightly: negative = up, positive = down.
    Range: -0.2 to +0.2 is sensible.
    """
    w, h = img.size
    target_ratio = target_w / target_h
    current_ratio = w / h

    if current_ratio > target_ratio:
        # too wide, crop width
        new_w = int(h * target_ratio)
        left = (w - new_w) // 2
        return img.crop((left, 0, left + new_w, h))
    else:
        # too tall, crop height
        new_h = int(w / target_ratio)
        max_top = h - new_h
        # bias the crop slightly up/down
        top = int((max_top / 2) + (max_top * y_bias))
        top = max(0, min(max_top, top))
        return img.crop((0, top, w, top + new_h))

def make_out_path(in_path: Path, out_dir: Path, fmt: str) -> Path:
    out_ext = ".jpg" if fmt == "jpg" else ".webp"
    return out_dir / f"{in_path.stem}{out_ext}"

def process_one(in_path: Path, out_dir: Path, aspect: str, width: int, height: int, quality: int, fmt: str, y_bias: float) -> Path:
    img = Image.open(in_path)
    img = ImageOps.exif_transpose(img)

    # Convert to RGB for JPEG/WebP output
    if img.mode not in ("RGB", "L"):
        img = img.convert("RGB")

    aw, ah = map(int, aspect.split(":"))
    img = crop_to_aspect(img, aw, ah, y_bias=y_bias)

    # Force exact size
    img = img.resize((width, height), Image.Resampling.LANCZOS)

    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = make_out_path(in_path, out_dir, fmt)

    if fmt == "jpg":
        img.save(out_path, format="JPEG", quality=quality, optimize=True, progressive=True)
    else:
        img.save(out_path, format="WEBP", quality=quality, method=6)

    return out_path

def main():
    ap = argparse.ArgumentParser(description="Batch crop/resize/compress images for web.")
    ap.add_argument("--in", dest="in_dir", required=True, help="Input folder")
    ap.add_argument("--out", dest="out_dir", required=True, help="Output folder")
    ap.add_argument("--aspect", default="4:3", help="Target aspect ratio, eg 4:3")
    ap.add_argument("--width", type=int, default=1600, help="Output width in px")
    ap.add_argument("--height", type=int, default=1200, help="Output height in px")
    ap.add_argument("--quality", type=int, default=80, help="JPEG/WebP quality 1-95")
    ap.add_argument("--fmt", choices=["jpg", "webp"], default="webp", help="Output format")
    ap.add_argument("--recursive", action="store_true", help="Recurse into subfolders")
    ap.add_argument("--skip-existing", action="store_true", help="Skip if output file already exists")
    ap.add_argument("--move-processed-to", default="", help="Move originals here after successful processing")
    ap.add_argument("--y-bias", type=float, default=0.0, help="Vertical crop bias (-0.2 up, +0.2 down)")
    args = ap.parse_args()

    in_dir = Path(args.in_dir).resolve()
    out_dir = Path(args.out_dir).resolve()

    if not in_dir.exists():
        raise SystemExit(f"Input folder not found: {in_dir}")

    mover_dir = Path(args.move_processed_to).resolve() if args.move_processed_to else None
    if mover_dir:
        mover_dir.mkdir(parents=True, exist_ok=True)

    pattern = "**/*" if args.recursive else "*"
    files = [p for p in in_dir.glob(pattern) if p.is_file() and p.suffix.lower() in VALID_EXTS]

    total = len(files)
    done = 0
    skipped = 0
    failed = 0

    print(f"Found {total} images. Processing...")

    for p in files:
        try:
            out_path = make_out_path(p, out_dir, args.fmt)
            if args.skip_existing and out_path.exists():
                skipped += 1
                continue

            process_one(p, out_dir, args.aspect, args.width, args.height, args.quality, args.fmt, args.y_bias)
            done += 1

            if mover_dir:
                # Avoid name collisions in processed folder
                target = mover_dir / p.name
                if target.exists():
                    target = mover_dir / f"{p.stem}_{p.stat().st_mtime_ns}{p.suffix}"
                shutil.move(str(p), str(target))

        except Exception as e:
            failed += 1
            print(f"Failed: {p.name} ({e})")

    print(f"Done. Converted: {done}, skipped: {skipped}, failed: {failed}")

if __name__ == "__main__":
    main()
