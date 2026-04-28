#!/usr/bin/env python3
"""Fix broken Archive.org links in index.html."""
from pathlib import Path

idx = Path("/Users/openclaw/Desktop/WBF/index.html").read_text()

# Broken → Working
fixes = {
    'https://archive.org/details/ost-english-1984-george-orwell': 'https://archive.org/details/1984novel00orwe_0',
    'https://archive.org/details/animalfarm00orwe_1': 'https://archive.org/details/animalfarm0000orwe',
    'https://archive.org/details/adventureshuckle00twai': 'https://archive.org/details/mark-twain_the-adventures-of-huckleberry-finn',
    'https://archive.org/details/ofmiceandmen00stei': 'https://archive.org/details/ofmicemen0000unse',
    'https://archive.org/details/jungle1906sinc': 'https://archive.org/details/jungle00sinc',
}

for old, new in fixes.items():
    if old in idx:
        idx = idx.replace(old, new)
        print(f"✅ Fixed: {old.split('/')[-1]} → {new.split('/')[-1]}")
    else:
        print(f"⚠️ Not found: {old}")

Path("/Users/openclaw/Desktop/WBF/index.html").write_text(idx)
print(f"\nSaved: {len(idx)} bytes")

# Quick verify the 5 fixed links
import urllib.request
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

print("\n=== VERIFYING FIXED LINKS ===")
for link in fixes.values():
    try:
        req = urllib.request.Request(link, method='HEAD')
        req.add_header('User-Agent', 'Mozilla/5.0')
        resp = urllib.request.urlopen(req, context=ctx, timeout=15)
        print(f"✅ {link.split('/')[-1][:40]:40s} - HTTP {resp.status}")
    except Exception as e:
        print(f"❌ {link.split('/')[-1][:40]:40s} - {str(e)[:40]}")
