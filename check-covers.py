#!/usr/bin/env python3
import re
from pathlib import Path

covers_dir = Path("/Users/openclaw/Desktop/WBF/covers")
existing = set(f.name for f in covers_dir.glob("*.jpg"))

for filename in ["index.html", "shop.html", "collections.html"]:
    filepath = Path("/Users/openclaw/Desktop/WBF") / filename
    html = filepath.read_text()
    
    # Extract coverImage references
    covers = set(re.findall(r'coverImage:\"([^\"]+)\"', html))
    covers |= set(re.findall(r'cover:\"([^\"]+)\"', html))
    
    # Clean up paths
    covers = {c.replace("covers/", "") for c in covers}
    
    missing = covers - existing
    
    print(f"\n=== {filename} ===")
    print(f"  Total covers referenced: {len(covers)}")
    print(f"  Missing: {len(missing)}")
    if missing:
        for c in sorted(missing):
            print(f"    ❌ {c}")
    else:
        print("    ✅ All covers found")

print("\n=== SUMMARY ===")
print(f"Total images in covers/: {len(existing)}")
