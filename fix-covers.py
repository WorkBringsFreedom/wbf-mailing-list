#!/usr/bin/env python3
"""Fix coverImage references to match actual filenames in covers/ directory."""
import re
from pathlib import Path

covers_dir = Path("/Users/openclaw/Desktop/WBF/covers")
existing = set(f.name for f in covers_dir.glob("*.jpg"))

# Mapping from simplified names to actual filenames
name_map = {
    # index.html books (most popular)
    "1984": "1984.jpg",
    "animalfarm": "animal-farm.jpg",
    "bravenewworld": "brave-new-world.jpg",
    "catch22": "catch-22.jpg",
    "colorpurple": "the-color-purple.jpg",
    "communistmanifesto": "the-communist-manifesto.jpg",
    "fahrenheit451": "fahrenheit-451.jpg",
    "grapesofwrath": "the-grapes-of-wrath.jpg",
    "handmaidstale": "the-handmaid-s-tale.jpg",
    "huckfinn": "the-adventures-of-huckleberry-finn.jpg",
    "jungle": "the-jungle.jpg",
    "ofmiceandmen": "of-mice-and-men.jpg",
    "peopleshistory": "a-people-s-history-of-the-united-states.jpg",
    "slaughterhousefive": "slaughterhouse-five.jpg",
    "tokillamockingbird": "to-kill-a-mockingbird.jpg",
    
    # Additional shop.html books that might have simplified names
    "beloved": "beloved.jpg",
    "thejungle": "the-jungle.jpg",
    "commanifesto": "the-communist-manifesto.jpg",
    "pplhistory": "a-people-s-history-of-the-united-states.jpg",
}

for filename in ["index.html", "shop.html", "collections.html"]:
    filepath = Path("/Users/openclaw/Desktop/WBF") / filename
    html = filepath.read_text()
    original = html
    
    # Find all coverImage references
    refs = set(re.findall(r'coverImage:"([^"]+)"', html))
    refs |= set(re.findall(r'cover:"([^"]+)"', html))
    
    for ref in refs:
        # Extract the base name (without covers/ prefix and .jpg suffix)
        base = ref.replace("covers/", "").replace(".jpg", "")
        
        # Check if this needs mapping
        if base in name_map:
            new_ref = f"covers/{name_map[base]}"
            html = html.replace(ref, new_ref)
            print(f"[{filename}] {ref} → {new_ref}")
        else:
            # Check if the file exists as-is
            actual = f"{base}.jpg"
            if actual not in existing:
                # Try to find a match
                for existing_file in existing:
                    existing_base = existing_file.replace(".jpg", "").replace("-", "").replace("the", "")
                    ref_base = base.replace("-", "").replace("the", "")
                    if existing_base == ref_base or existing_base in ref_base or ref_base in existing_base:
                        new_ref = f"covers/{existing_file}"
                        html = html.replace(ref, new_ref)
                        print(f"[{filename}] {ref} → {new_ref} (fuzzy)")
                        break
    
    if html != original:
        filepath.write_text(html)
        print(f"[{filename}] Saved ({len(original)} → {len(html)} bytes)")
    else:
        print(f"[{filename}] No changes needed")

# Verify
print("\n=== VERIFICATION ===")
for filename in ["index.html", "shop.html", "collections.html"]:
    filepath = Path("/Users/openclaw/Desktop/WBF") / filename
    html = filepath.read_text()
    
    refs = set(re.findall(r'coverImage:"([^"]+)"', html))
    refs |= set(re.findall(r'cover:"([^"]+)"', html))
    
    missing = []
    for ref in refs:
        base = ref.replace("covers/", "")
        if base not in existing:
            missing.append(ref)
    
    print(f"\n{filename}:")
    print(f"  Total covers: {len(refs)}")
    if missing:
        print(f"  Missing: {len(missing)}")
        for m in missing:
            print(f"    ❌ {m}")
    else:
        print(f"  ✅ All covers found!")
