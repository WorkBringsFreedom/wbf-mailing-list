#!/usr/bin/env python3
"""Clean fix: remove all freeLink fields, then add correct one. Remove FREE badge."""

import re
from pathlib import Path
import html

# Parse book_links.html
book_html = Path("/Users/openclaw/Desktop/book_links.html").read_text()
link_map = {}
for m in re.finditer(
    r'<td class="num">\d+</td>\s*<td>(.*?)</td>\s*<td class="author">(.*?)</td>\s*<td>.*?<a href="([^"]+)">Read full text</a>.*?</td>',
    book_html, re.DOTALL
):
    title = html.unescape(re.sub(r'<[^>]+>', '', m.group(1)).strip())
    url = m.group(3)
    norm = re.sub(r'[^\w\s]', '', title.lower()).strip()
    link_map[norm] = url

# Read clean backup
shop_html = Path("/Users/openclaw/Desktop/WBF/shop.html.backup").read_text()

# 1. Remove FREE badge from cards
badge = """\${b.freeLink ? '<div style="position:absolute;top:10px;right:10px;background:var(--blood);color:var(--paper);padding:4px 10px;font-size:11px;font-family:Bebas Neue, sans-serif;letter-spacing:2px;">FREE</div>' : ''}"""
if badge in shop_html:
    shop_html = shop_html.replace(badge, "")
    print("✓ Removed FREE badge from cards")

# 2. Fix each product: remove all freeLink fields, add correct one

def normalize(t):
    return re.sub(r'[^\w\s]', '', t.lower()).strip()

def find_link(title):
    norm = normalize(title)
    if norm in link_map:
        return link_map[norm]
    words = norm.split()
    if len(words) >= 3:
        key = ' '.join(words[:3])
        if key in link_map:
            return link_map[key]
    if len(words) >= 2:
        key = ' '.join(words[:2])
        if key in link_map:
            return link_map[key]
    for k, v in link_map.items():
        if norm in k or k in norm:
            return v
    return None

updated = 0
removed = 0

# Find each product entry
entries = list(re.finditer(r'\{\s*id:\s*(\d+),\s*title:"([^"]+)"[^}]*\}', shop_html, re.DOTALL))
print(f"Found {len(entries)} products")

for m in entries:
    full = m.group(0)
    title = m.group(2)
    
    # Remove ALL existing freeLink fields (handle both leading and trailing comma)
    cleaned = re.sub(r',\s*freeLink:"[^"]+"', '', full)
    cleaned = re.sub(r'freeLink:"[^"]+",\s*', '', cleaned)
    cleaned = re.sub(r'freeLink:"[^"]+"', '', cleaned)
    
    # Clean up double commas and comma-before-brace
    cleaned = re.sub(r',\s*,', ',', cleaned)
    cleaned = re.sub(r',\s*}', '}', cleaned)
    
    new_url = find_link(title)
    if new_url:
        # Insert freeLink before buyLink
        if 'buyLink:' in cleaned:
            cleaned = cleaned.replace('buyLink:', f'freeLink:"{new_url}", buyLink:', 1)
        elif 'blurb:' in cleaned:
            cleaned = cleaned.replace('blurb:', f'freeLink:"{new_url}", blurb:', 1)
        else:
            cleaned = cleaned.rstrip()[:-1] + f', freeLink:"{new_url}"' + '}'
        updated += 1
    else:
        removed += 1
    
    shop_html = shop_html.replace(full, cleaned, 1)

print(f"✓ Updated {updated} products with correct freeLink URLs")
print(f"✓ Removed freeLink from {removed} products (no match)")

# 3. Verify no duplicates remain
dupes = re.findall(r'title:"([^"]+)"[^}]*freeLink:"[^"]+"[^}]*freeLink:', shop_html)
if dupes:
    print(f"⚠ Still {len(dupes)} duplicate freeLinks: {dupes[:3]}")
else:
    print("✓ No duplicate freeLinks found")

Path("/Users/openclaw/Desktop/WBF/shop.html").write_text(shop_html)
print("\n✅ Saved")
