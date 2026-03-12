import io
from PIL import Image, ImageOps

WIDTH = 1200
HEIGHT = 900


def crop_to_4x3(img: Image.Image) -> Image.Image:
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


def process_image(pil_image: Image.Image) -> bytes:
    img = ImageOps.exif_transpose(pil_image)
    img = img.convert("RGB")
    img = crop_to_4x3(img)
    img = img.resize((WIDTH, HEIGHT), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, "WEBP", quality=82, method=6)
    return buf.getvalue()
