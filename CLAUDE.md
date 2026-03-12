# Proud Pets Image Pipeline

## Project Overview
A pipeline that processes breed images: crop to 4:3, resize to 1200x900, convert to WebP, and upload to Supabase storage.

## Structure
- `scripts/proudpets_process.py` — batch CLI processor (reads from `raw/`, writes to `ready/`)
- `scripts/batch_webify.py` — batch WebP conversion utility
- `scripts/rename_ready_to_2digits.py` — renames files to 2-digit format
- `ui/app.py` — Streamlit UI for per-breed image upload to Supabase
- `ui/processor.py` — image processing logic (crop, resize, WebP encode)

## Output Structure
Processed images must go into a **breed subfolder**, not the root:
- Local: `ready/{breed}/{breed}-01.webp`
- Supabase: `{slug}/{slug}-01.webp` (e.g. `bloodhound/bloodhound-01.webp`)

This was a bug that was fixed — `bloodhound-01.webp` was landing next to the `bloodhound/` folder instead of inside it.

## Supabase
- Credentials in `.env` (`SUPABASE_URL`, `SUPABASE_SERVICE_KEY`, `SUPABASE_BUCKET`)
- Default bucket: `breed-images`
- Images stored as `{slug}/{slug}-{nn}.webp`
- DB table: `breed_images` with fields: `breed_id`, `image_url`, `display_order`, `is_primary`, `image_type`, `width`, `height`, `file_size`, `alt_text`
- DB table: `breeds` with fields: `id`, `name`, `slug`

## Image Specs
- Crop: center-crop to 4:3 ratio
- Resize: 1200x900
- Format: WebP, quality=82, method=6
