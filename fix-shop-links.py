#!/usr/bin/env python3
"""Fix broken freeLink URLs in shop.html by stripping /page/n1/mode/2up suffixes."""
import re
from pathlib import Path

shop = Path("/Users/openclaw/Desktop/WBF/shop.html").read_text()

# Find all archive.org links with /page/n1/mode/2up suffix
pattern = r'https://archive\.org/details/([^/]+)/page/n1/mode/2up'
matches = list(re.finditer(pattern, shop))

print(f"Found {len(matches)} archive.org viewer URLs to fix")

for m in matches:
    old = m.group(0)
    item_id = m.group(1)
    new = f"https://archive.org/details/{item_id}"
    shop = shop.replace(old, new)
    print(f"  Fixed: ...{old[-40:]} → ...{new[-40:]}")

# Also fix the external marxists.org link
old_marx = "https://www.marxists.org/subject/africa/fanon/wretched-of-the-earth.htm"
new_marx = "https://archive.org/details/wretchedearth00fano"
if old_marx in shop:
    shop = shop.replace(old_marx, new_marx)
    print(f"  Fixed: marxists.org → archive.org")

Path("/Users/openclaw/Desktop/WBF/shop.html").write_text(shop)
print(f"\nSaved: {len(shop)} bytes")

# Verify all free links now
import urllib.request
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

free_links = set(re.findall(r'freeLink:"([^"]+)"', shop))
print(f"\n=== Verifying {len(free_links)} free links ===")

broken = []
for link in sorted(free_links):
    try:
        req = urllib.request.Request(link, method='HEAD')
        req.add_header('User-Agent', 'Mozilla/5.0')
        resp = urllib.request.urlopen(req, context=ctx, timeout=15)
        print(f"  ✅ {link.split('/')[-1][:45]:45s} - HTTP {resp.status}")
    except Exception as e:
        print(f"  ❌ {link.split('/')[-1][:45]:45s} - {str(e)[:40]}")
        broken.append(link)

print(f"\n{'All links working!' if not broken else f'BROKEN: {len(broken)}'}")
if broken:
    for link in broken:
        print(f"  {link}")
