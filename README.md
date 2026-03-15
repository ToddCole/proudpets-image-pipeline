Image Pipeline

Automated image processing pipeline for generation of consistent image size: crop to 4:3, resize, convert to WebP, and archive originals.

## 📁 Folder Structure

```
Image_Shrinker/
├── scripts/              # Python processing scripts
│   ├── proudpets_process.py      # Main processor
│   ├── rename_ready_to_2digits.py  # One-time renamer
│   └── batch_webify.py            # Batch converter for custom needs
├── raw/                  # Input images (by breed folder)
├── ready/                # Output WebP files (4:3, 1200x900, breed-01.webp)
├── processed_raw/        # Archived originals after processing
└── web_4x3/              # Optional web-optimized exports
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip3 install Pillow
```

### 2. Add Images to Process

Place images in `raw/` organized by breed folders:

```
raw/
├── bullmastiff/
│   ├── IMG_001.jpg
│   └── IMG_002.jpg
├── pug/
│   └── photo.png
└── golden-retriever/
    └── dog.jpg
```

### 3. Run the Processor

```bash
python3 scripts/proudpets_process.py
```

**What it does:**

- Crops all images to 4:3 aspect ratio (center crop)
- Resizes to 1200×900px
- Converts to WebP format with 85% quality
- Names output files: `breed-01.webp`, `breed-02.webp`, etc.
- Automatically increments numbers if files already exist
- Moves processed originals to `processed_raw/breed-name/`

**Output:** All processed WebP files in `ready/`

### 4. (Optional) Rename Existing Files to 2-Digit Format

If you have existing files with single-digit numbers (e.g., `pug-1.webp`), run this once:

```bash
python3 scripts/rename_ready_to_2digits.py
```

Renames `pug-1.webp` → `pug-01.webp`

## ⚙️ Advanced Options

### Custom Width/Quality

```bash
python3 scripts/proudpets_process.py --width 1600 --quality 90
```

### Keep Original Files (Don't Archive)

```bash
python3 scripts/proudpets_process.py --keep-raw
```

### Batch Convert with Custom Aspect Ratios

For special web exports (e.g., 16:9, different sizes):

```bash
python3 scripts/batch_webify.py \
  --in ready/ \
  --out web_16x9/ \
  --aspect 16:9 \
  --width 1920 \
  --height 1080 \
  --quality 80 \
  --fmt webp
```

## 🔄 Typical Workflow

1. **Sync images from Supabase** → `raw/breed-folders/`
2. **Run processor:** `python3 scripts/proudpets_process.py`
3. **Verify output:** Check `ready/` folder
4. **Upload to production** from `ready/`
5. **Originals archived** in `processed_raw/`

## 📋 Output File Naming

Format: `{breed-slug}-{number}.webp`

- **Slug:** Folder name converted to lowercase with dashes
- **Number:** 2-digit zero-padded (01, 02, 03...)
- **Extension:** `.webp`

Examples:

- `raw/golden-retriever/photo.jpg` → `ready/golden-retriever-01.webp`
- `raw/pug/IMG_5432.jpg` → `ready/pug-01.webp`

## 🛠️ Troubleshooting

### "No images in raw/"

- Ensure images are in `raw/` or subfolders
- Check file extensions: `.jpg`, `.jpeg`, `.png`, `.webp`, `.tif`, `.tiff`

### Numbers not incrementing correctly

- Run `scripts/rename_ready_to_2digits.py` to fix existing files
- Check `ready/` folder for naming conflicts

### Image quality issues

- Increase quality: `--quality 95` (larger file size)
- Increase resolution: `--width 1600` (outputs 1600×1200)

## 🔐 Git Best Practices

**Never commit:**

- Raw images (in `.gitignore`)
- Processed images (in `.gitignore`)
- API keys or credentials (in `.gitignore`)

**Always commit:**

- Python scripts in `scripts/`
- README updates
- Configuration changes

## 📦 Requirements

- Python 3.7+
- Pillow (PIL)

```bash
pip3 install Pillow
```

## 📝 Notes

- **Auto-numbering:** Script automatically finds the next available number
- **Safe processing:** Originals are moved only after successful processing
- **EXIF handling:** Auto-rotates images based on EXIF orientation
- **Format:** WebP offers 25-35% smaller files than JPEG with similar quality
- **4:3 Aspect:** Standard aspect ratio for Proud Pets product images

---

**Questions?** Check the script comments or adjust paths in the Python files.
