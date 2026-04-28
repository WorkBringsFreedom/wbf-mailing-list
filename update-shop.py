#!/usr/bin/env python3
"""Update WBF shop.html freeLink URLs from book_links.html. Remove FREE badge."""

import re
from pathlib import Path
import html

# Parse book_links.html
book_links_html = Path("/Users/openclaw/Desktop/book_links.html").read_text()

link_map = {}
for m in re.finditer(
    r'<td class="num">\d+</td>\s*<td>(.*?)</td>\s*<td class="author">(.*?)</td>\s*<td>.*?<a href="([^"]+)">Read full text</a>.*?</td>',
    book_links_html, re.DOTALL
):
    title = html.unescape(re.sub(r'<[^>]+>', '', m.group(1)).strip())
    url = m.group(3)
    norm = re.sub(r'[^\w\s]', '', title.lower()).strip()
    link_map[norm] = url

print(f"Loaded {len(link_map)} URLs from book_links.html")

# Read clean backup
shop_html = Path("/Users/openclaw/Desktop/WBF/shop.html.backup").read_text()

# Step 1: Remove FREE badge from card grid (if present)
badge = """\${b.freeLink ? '<div style="position:absolute;top:10px;right:10px;background:var(--blood);color:var(--paper);padding:4px 10px;font-size:11px;font-family:Bebas Neue, sans-serif;letter-spacing:2px;">FREE</div>' : ''}"""
if badge in shop_html:
    shop_html = shop_html.replace(badge, "")
    print("✓ Removed FREE badge from cards")

# Step 2: Update freeLink URLs

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

# Find all products with freeLink
updated = 0
removed = 0
no_match = []

# Match each product entry
for m in list(re.finditer(
    r'(\{\s*id:\s*(\d+),\s*title:"([^"]+)".*?)(freeLink:"[^"]+")(.*?\})',
    shop_html, re.DOTALL
)):
    full = m.group(1) + m.group(4) + m.group(5)
    pid = m.group(2)
    title = m.group(3)
    old_free = m.group(4)
    
    new_url = find_link(title)
    if new_url:
        new_free = f'freeLink:"{new_url}"'
        new_full = m.group(1) + new_free + m.group(5)
        shop_html = shop_html.replace(full, new_full, 1)
        updated += 1
    else:
        # Remove freeLink - no match in book_links.html
        new_full = m.group(1) + m.group(5)
        # Clean up double commas
        new_full = re.sub(r',\s*,', ',', new_full)
        new_full = re.sub(r',\s*}', '}', new_full)
        shop_html = shop_html.replace(full, new_full, 1)
        removed += 1
        no_match.append(title)

print(f"\n✓ Updated {updated} freeLink URLs from book_links.html")
print(f"✓ Removed freeLink from {removed} books (no match in book_links.html)")
if no_match:
    print(f"  Unmatched: {', '.join(no_match[:10])}{'...' if len(no_match) > 10 else ''}")

# Write to both locations
Path("/Users/openclaw/Desktop/WBF/shop.html").write_text(shop_html)
print(f"\n✅ Saved to /Users/openclaw/Desktop/WBF/shop.html")
