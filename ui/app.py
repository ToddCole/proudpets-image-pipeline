import os
import sys
from collections import Counter

import streamlit as st
from PIL import Image
from dotenv import load_dotenv

# Load .env from project root (one level up from ui/)
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_SERVICE_KEY = os.environ.get("SUPABASE_SERVICE_KEY", "")
SUPABASE_BUCKET = os.environ.get("SUPABASE_BUCKET", "breed-images")

# Add ui/ to path so processor.py is importable when launched from project root
sys.path.insert(0, os.path.dirname(__file__))
from processor import process_image  # noqa: E402


# ── Supabase client ────────────────────────────────────────────────────────────

@st.cache_resource
def get_supabase():
    from supabase import create_client
    return create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)


# ── Data loaders ───────────────────────────────────────────────────────────────

@st.cache_data(ttl=300)
def load_breeds() -> list[dict]:
    sb = get_supabase()
    resp = sb.table("breeds").select("id,name,slug").order("name").execute()
    return resp.data


@st.cache_data(ttl=30)
def load_completed_breed_ids() -> set[str]:
    sb = get_supabase()
    resp = sb.table("breed_images").select("breed_id").execute()
    counts = Counter(r["breed_id"] for r in resp.data)
    return {breed_id for breed_id, count in counts.items() if count >= 3}


# ── Upload logic ───────────────────────────────────────────────────────────────

def upload_breed_images(breed: dict, processed_images: list[bytes]) -> list[str]:
    sb = get_supabase()
    slug = breed["slug"]
    breed_id = breed["id"]

    # Remove existing DB records for this breed
    sb.table("breed_images").delete().eq("breed_id", breed_id).execute()

    urls = []
    for i, img_bytes in enumerate(processed_images, start=1):
        path = f"{slug}/{slug}-{i:02d}.webp"

        # Upload to storage (upsert overwrites existing file)
        sb.storage.from_(SUPABASE_BUCKET).upload(
            path=path,
            file=img_bytes,
            file_options={"content-type": "image/webp", "upsert": "true"},
        )

        url = f"{SUPABASE_URL}/storage/v1/object/public/{SUPABASE_BUCKET}/{path}"

        sb.table("breed_images").insert({
            "breed_id": breed_id,
            "image_url": url,
            "display_order": i,
            "is_primary": i == 1,
            "image_type": "gallery",
            "width": 1200,
            "height": 900,
            "file_size": len(img_bytes),
            "alt_text": f"{breed['name']} - Photo {i}",
        }).execute()

        urls.append(url)

    return urls


# ── Main UI ────────────────────────────────────────────────────────────────────

def main():
    st.set_page_config(page_title="Breed Image Pipeline", layout="wide")

    # Validate env
    if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
        st.error(
            "Missing Supabase credentials. Copy `.env.example` → `.env` and fill in "
            "`SUPABASE_URL` and `SUPABASE_SERVICE_KEY`."
        )
        st.stop()

    # Session state defaults
    if "selected_breed_id" not in st.session_state:
        st.session_state.selected_breed_id = None
    if "processed_images" not in st.session_state:
        st.session_state.processed_images = None

    breeds = load_breeds()
    completed_ids = load_completed_breed_ids()

    total = len(breeds)
    complete_count = sum(1 for b in breeds if b["id"] in completed_ids)

    # ── Sidebar ────────────────────────────────────────────────────────────────
    with st.sidebar:
        st.title("Breed Pipeline")
        st.progress(complete_count / total if total else 0)
        st.caption(f"{complete_count} / {total} breeds complete")
        st.divider()

        filter_mode = st.radio("Show", ["All", "Incomplete", "Complete"], horizontal=True)

        if filter_mode == "Incomplete":
            filtered = [b for b in breeds if b["id"] not in completed_ids]
        elif filter_mode == "Complete":
            filtered = [b for b in breeds if b["id"] in completed_ids]
        else:
            filtered = breeds

        for breed in filtered:
            icon = "✅" if breed["id"] in completed_ids else "○"
            is_selected = breed["id"] == st.session_state.selected_breed_id
            label = f"{icon} {breed['name']}"
            if st.button(
                label,
                key=f"btn_{breed['id']}",
                use_container_width=True,
                type="primary" if is_selected else "secondary",
            ):
                if st.session_state.selected_breed_id != breed["id"]:
                    st.session_state.selected_breed_id = breed["id"]
                    st.session_state.processed_images = None
                st.rerun()

    # ── Main area ──────────────────────────────────────────────────────────────
    selected_id = st.session_state.selected_breed_id
    breed = next((b for b in breeds if b["id"] == selected_id), None)

    if breed is None:
        st.title("Breed Image Pipeline")
        st.info("Select a breed from the sidebar to get started.")
        return

    is_complete = breed["id"] in completed_ids
    status_icon = "✅" if is_complete else "○"
    st.title(f"{status_icon} {breed['name']}")
    st.caption(f"slug: `{breed['slug']}`  |  id: `{breed['id']}`")

    if is_complete:
        st.warning("This breed already has 3 images. Uploading will replace them.")

    st.divider()

    # File uploaders
    col1, col2, col3 = st.columns(3)
    uploaders = [col1, col2, col3]
    uploaded_files = []
    for i, col in enumerate(uploaders):
        with col:
            f = st.file_uploader(
                f"Image {i + 1}",
                type=["jpg", "jpeg", "png", "webp"],
                key=f"file_{breed['id']}_{i}",
                label_visibility="visible",
            )
            uploaded_files.append(f)

    valid_files = [f for f in uploaded_files if f is not None]

    if valid_files:
        if st.button("Process & Preview", type="secondary"):
            with st.spinner("Processing…"):
                processed = []
                for f in valid_files:
                    img = Image.open(f)
                    processed.append(process_image(img))
            st.session_state.processed_images = processed

    # Previews
    if st.session_state.processed_images:
        imgs = st.session_state.processed_images
        st.subheader("Preview")
        preview_cols = st.columns(len(imgs))
        for i, (img_bytes, col) in enumerate(zip(imgs, preview_cols)):
            with col:
                st.image(
                    img_bytes,
                    caption=f"{breed['slug']}-{i + 1:02d}.webp  ({len(img_bytes):,} bytes)",
                    use_container_width=True,
                )

        st.divider()
        if st.button(f"Upload {len(imgs)} image(s) to Supabase", type="primary"):
            with st.spinner("Uploading to Supabase…"):
                try:
                    urls = upload_breed_images(breed, imgs)
                    st.success(f"Uploaded {len(urls)} image(s) successfully.")
                    for url in urls:
                        st.code(url)
                    # Refresh completion state
                    load_completed_breed_ids.clear()
                    st.session_state.processed_images = None
                except Exception as e:
                    st.error(f"Upload failed: {e}")


if __name__ == "__main__":
    main()
