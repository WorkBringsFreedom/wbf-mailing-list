#!/usr/bin/env python3
"""Fix WBF shop.html: deduplicate freeLink fields and correct URLs from book_links.html"""

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

# Read shop.html
shop_path = Path("/Users/openclaw/Desktop/WBF/shop.html")
shop_html = shop_path.read_text()

# Remove the FREE badge from renderGrid
old_badge = """${b.freeLink ? '<div style="position:absolute;top:10px;right:10px;background:var(--blood);color:var(--paper);padding:4px 10px;font-size:11px;font-family:Bebas Neue, sans-serif;letter-spacing:2px;">FREE</div>' : ''}"""
if old_badge in shop_html:
    shop_html = shop_html.replace(old_badge, "")
    print("✓ Removed FREE badge from cards")

# Fix products with duplicate freeLink fields
# Each product entry looks like:
# { id:1, title:"...", ..., freeLink:"URL1", freeLink:"URL2", buyLink:"...", blurb:"...", reason:"..." },
# We need to keep only ONE correct freeLink

# Extract the PRODUCTS array
start = shop_html.find('const PRODUCTS = [')
end = shop_html.find('];', start) + 2
products_block = shop_html[start:end]

# Process each product entry
# Find entries: { id:N, title:"TITLE", ..., }
product_re = re.compile(
    r'\{\s*id:\s*(\d+),\s*title:"([^"]+)"([^}]*)\}',
    re.DOTALL
)

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

fixed = 0
no_match = []

for m in product_re.finditer(products_block):
    full = m.group(0)
    pid = m.group(1)
    title = m.group(2)
    body = m.group(3)
    
    # Find all freeLink occurrences
    free_links = re.findall(r'freeLink:"([^"]+)"', body)
    
    # Get correct URL
    correct_url = find_link(title)
    
    if correct_url:
        # Remove all existing freeLink entries
        cleaned_body = re.sub(r',?\s*freeLink:"[^"]+"', '', body)
        # Add the correct one
        # Insert after coverImage if present, otherwise after price
        if 'coverImage:' in cleaned_body:
            cleaned_body = cleaned_body.replace('coverImage:', f'freeLink:"{correct_url}", coverImage:', 1)
        else:
            cleaned_body = f'freeLink:"{correct_url}",{cleaned_body}'
        
        new_entry = f'{{ id:{pid}, title:"{title}"{cleaned_body}}}'
        products_block = products_block.replace(full, new_entry, 1)
        fixed += 1
    else:
        # No match in book_links.html - remove all freeLink fields
        cleaned_body = re.sub(r',?\s*freeLink:"[^"]+"', '', body)
        new_entry = f'{{ id:{pid}, title:"{title}"{cleaned_body}}}'
        products_block = products_block.replace(full, new_entry, 1)
        no_match.append(title)

# Put the fixed PRODUCTS array back
shop_html = shop_html[:start] + products_block + shop_html[end:]

print(f"\n✓ Fixed {fixed} products with corrected freeLink URLs")
if no_match:
    print(f"✗ No match for {len(no_match)} books (freeLink removed): {', '.join(no_match[:5])}{'...' if len(no_match) > 5 else ''}")

# Write back
shop_path.write_text(shop_html)
print(f"\n✅ Saved to {shop_path}")
