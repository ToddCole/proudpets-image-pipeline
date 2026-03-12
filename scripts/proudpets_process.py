import os
import shutil
from PIL import Image

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

RAW_DIR = os.path.join(BASE_DIR, "raw")
READY_DIR = os.path.join(BASE_DIR, "ready")
PROCESSED_RAW_DIR = os.path.join(BASE_DIR, "processed_raw")

WIDTH = 1200
HEIGHT = 900

os.makedirs(READY_DIR, exist_ok=True)
os.makedirs(PROCESSED_RAW_DIR, exist_ok=True)

def crop_to_4x3(img):
    w, h = img.size
    target_ratio = 4 / 3
    current_ratio = w / h

    if current_ratio > target_ratio:
        new_w = int(h * target_ratio)
        left = (w - new_w) // 2
        img = img.crop((left, 0, left + new_w, h))
    else:
        new_h = int(w / target_ratio)
        top = (h - new_h) // 2
        img = img.crop((0, top, w, top + new_h))

    return img


def process_breed_folder(breed):

    breed_path = os.path.join(RAW_DIR, breed)
    images = [f for f in os.listdir(breed_path)
              if f.lower().endswith((".jpg", ".jpeg", ".png", ".webp"))]

    if not images:
        return

    images.sort()

    for i, filename in enumerate(images, start=1):

        input_path = os.path.join(breed_path, filename)

        with Image.open(input_path) as img:

            img = img.convert("RGB")
            img = crop_to_4x3(img)

            img = img.resize((WIDTH, HEIGHT), Image.LANCZOS)

            output_name = f"{breed}-{i:02d}.webp"
            breed_ready_dir = os.path.join(READY_DIR, breed)
            os.makedirs(breed_ready_dir, exist_ok=True)
            output_path = os.path.join(breed_ready_dir, output_name)

            img.save(output_path, "WEBP", quality=82, method=6)

        archive_dir = os.path.join(PROCESSED_RAW_DIR, breed)
        os.makedirs(archive_dir, exist_ok=True)

        shutil.move(input_path, os.path.join(archive_dir, filename))

        print(f"Processed: {output_name}")


def main():

    if not os.path.exists(RAW_DIR):
        print("Raw folder not found")
        return

    breeds = [d for d in os.listdir(RAW_DIR)
              if os.path.isdir(os.path.join(RAW_DIR, d))]

    if not breeds:
        print("No breed folders in raw/")
        return

    for breed in breeds:
        process_breed_folder(breed)

    print("\nAll done.")


if __name__ == "__main__":
    main()
