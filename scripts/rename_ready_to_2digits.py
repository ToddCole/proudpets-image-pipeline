#!/usr/bin/env python3
"""
One-time script to rename existing files in ready/ from single-digit to 2-digit format.
Example: bullmastiff-1.webp -> bullmastiff-01.webp
"""

from pathlib import Path
import re

READY_DIR = Path("/Users/toddcole/Image_Shrinker/ready")


def main():
    # Find all webp files with single or multi-digit numbers
    files = list(READY_DIR.glob("*.webp"))
    
    if not files:
        print(f"No .webp files found in {READY_DIR}")
        return
    
    renamed = 0
    already_ok = 0
    
    for p in files:
        # Match pattern: breed-name-N.webp where N is one or more digits
        m = re.match(r"^(.+)-(\d+)\.webp$", p.name)
        if not m:
            print(f"Skip: {p.name} (doesn't match pattern)")
            continue
        
        prefix = m.group(1)
        num = int(m.group(2))
        
        # Check if already 2+ digits
        if len(m.group(2)) >= 2:
            already_ok += 1
            continue
        
        # Generate new name with 2-digit zero-padded number
        new_name = f"{prefix}-{num:02d}.webp"
        new_path = READY_DIR / new_name
        
        if new_path.exists():
            print(f"Skip: {p.name} (target {new_name} already exists)")
            continue
        
        p.rename(new_path)
        renamed += 1
        print(f"Renamed: {p.name} -> {new_name}")
    
    print(f"\nDone! Renamed: {renamed}, Already 2-digit: {already_ok}")


if __name__ == "__main__":
    main()
