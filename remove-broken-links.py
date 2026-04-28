#!/usr/bin/env python3
"""Remove broken freeLink entries from shop.html so only working links remain."""
import re
import urllib.request
import ssl
from pathlib import Path

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

shop = Path("/Users/openclaw/Desktop/WBF/shop.html").read_text()

# Find all freeLink URLs
free_links = set(re.findall(r'freeLink:"([^"]+)"', shop))

print(f"Checking {len(free_links)} free links...")

broken = []
for link in sorted(free_links):
    try:
        req = urllib.request.Request(link, method='HEAD')
        req.add_header('User-Agent', 'Mozilla/5.0')
        resp = urllib.request.urlopen(req, context=ctx, timeout=15)
        print(f"  ✅ {link.split('/')[-1][:50]}")
    except Exception as e:
        print(f"  ❌ {link.split('/')[-1][:50]}")
        broken.append(link)

print(f"\nBroken links to remove: {len(broken)}")

# Remove broken freeLink lines from shop.html
for link in broken:
    # Pattern: freeLink:"URL",
    pattern = f'freeLink:"{link}",\n'
    if pattern in shop:
        shop = shop.replace(pattern, '\n')
        print(f"  Removed: {link.split('/')[-1][:50]}")
    else:
        # Try without newline
        pattern2 = f'freeLink:"{link}",'
        if pattern2 in shop:
            shop = shop.replace(pattern2, '')
            print(f"  Removed: {link.split('/')[-1][:50]}")

Path("/Users/openclaw/Desktop/WBF/shop.html").write_text(shop)
print(f"\nSaved: {len(shop)} bytes")

# Verify remaining free links
remaining = set(re.findall(r'freeLink:"([^"]+)"', shop))
print(f"\nRemaining free links: {len(remaining)}")

# Final check
final_broken = []
for link in remaining:
    try:
        req = urllib.request.Request(link, method='HEAD')
        req.add_header('User-Agent', 'Mozilla/5.0')
        resp = urllib.request.urlopen(req, context=ctx, timeout=15)
    except Exception as e:
        final_broken.append(link)

if final_broken:
    print(f"Still broken: {len(final_broken)}")
    for link in final_broken:
        print(f"  {link}")
else:
    print("All remaining links working!")
