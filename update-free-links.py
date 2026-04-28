#!/usr/bin/env python3
"""Update WBF shop.html: remove FREE badge from cards, update freeLink URLs from book_links.html"""

import re
from pathlib import Path
import html

# Parse book_links.html to extract title -> URL mappings
book_links_path = Path("/Users/openclaw/Desktop/book_links.html")
book_links_html = book_links_path.read_text()

link_map = {}
for m in re.finditer(
    r'<td class="num">\d+</td>\s*<td>(.*?)</td>\s*<td class="author">(.*?)</td>\s*<td>.*?<a href="([^"]+)">Read full text</a>.*?</td>',
    book_links_html, re.DOTALL
):
    title = html.unescape(re.sub(r'<[^>]+>', '', m.group(1)).strip())
    url = m.group(3)
    # Store by normalized title
    norm = re.sub(r'[^\w\s]', '', title.lower()).strip()
    link_map[norm] = url

print(f"Extracted {len(link_map)} title->URL mappings from book_links.html")

# Read shop.html
shop_path = Path("/Users/openclaw/Desktop/WBF/shop.html")
shop_html = shop_path.read_text()

# First, remove the FREE badge from the renderGrid function
# The badge line is in the grid.innerHTML template
old_badge = """${b.freeLink ? '<div style="position:absolute;top:10px;right:10px;background:var(--blood);color:var(--paper);padding:4px 10px;font-size:11px;font-family:Bebas Neue, sans-serif;letter-spacing:2px;">FREE</div>' : ''}"""

if old_badge in shop_html:
    shop_html = shop_html.replace(old_badge, "")
    print("Removed FREE badge from card grid")
else:
    print("Could not find exact FREE badge pattern")

# Now update freeLink URLs. We need to find each product entry.
# Products in shop.html have: title:"...", freeLink:"URL" (some may be missing freeLink)
# Strategy: find each title, then find/update the freeLink in that product entry

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

# Find all product entries and update freeLink
# Each product is: { id:N, title:"TITLE", author:"AUTHOR", ... }
product_pattern = re.compile(
    r'(\{\s*id:\s*\d+,\s*title:"([^"]+)",\s*author:"([^"]+)"[^}]*?)'
    r'(?:freeLink:"([^"]*)")?'
    r'(.*?\})',
    re.DOTALL
)

updated = 0
added = 0
no_match = []

for m in product_pattern.finditer(shop_html):
    full = m.group(0)
    title = m.group(2)
    current_free = m.group(4) or ""
    
    new_url = find_link(title)
    if new_url:
        if current_free:
            # Replace existing freeLink
            old_free = f'freeLink:"{current_free}"'
            new_free = f'freeLink:"{new_url}"'
            if old_free in full:
                new_full = full.replace(old_free, new_free, 1)
                shop_html = shop_html.replace(full, new_full, 1)
                updated += 1
                print(f"  Updated: {title}")
        else:
            # No freeLink exists, add one
            # Insert after coverImage:"..." and before buyLink
            # Find a safe insertion point
            if 'buyLink:' in full:
                new_full = full.replace('buyLink:', f'freeLink:"{new_url}", buyLink:', 1)
                shop_html = shop_html.replace(full, new_full, 1)
                added += 1
                print(f"  Added: {title}")
            else:
                # Add before closing brace
                new_full = full.rstrip()[:-1] + f', freeLink:"{new_url}" ' + '}'
                shop_html = shop_html.replace(full, new_full, 1)
                added += 1
                print(f"  Added: {title}")
    else:
        no_match.append(title)

print(f"\nUpdated {updated} existing freeLink URLs")
print(f"Added {added} new freeLink URLs")
if no_match:
    print(f"No match for: {', '.join(no_match[:10])}{'...' if len(no_match) > 10 else ''}")

# Write back
shop_path.write_text(shop_html)
print(f"\nSaved to {shop_path}")
