#!/usr/bin/env python3
"""Parse amazon_links.rtf and update buyLink URLs in shop.html and collections.html"""

import re
from pathlib import Path

# Read the RTF file
rtf = Path("/Users/openclaw/Desktop/WBF/amazon_links.rtf").read_text()

# Extract title + URL pairs
# Pattern: Title on one line, URL on next line
link_map = {}
lines = rtf.split('\n')
i = 0
while i < len(lines) - 1:
    line = lines[i].strip()
    next_line = lines[i+1].strip()
    
    # Skip RTF control lines, empty lines, and the header
    if not line or line.startswith('\\') or line.startswith('{') or line == 'AMAZON BOOK LINKS':
        i += 1
        continue
    
    # Check if next line is a URL
    if next_line.startswith('https://amzn.to/'):
        # Clean the title (remove RTF formatting)
        title = re.sub(r'\\[a-z]+\d*\s*', ' ', line)  # Remove RTF commands
        title = re.sub(r'\{[^}]*\}', '', title)  # Remove RTF groups
        title = re.sub(r'\s+', ' ', title).strip()
        url = next_line
        
        # Normalize title for matching
        norm = re.sub(r'[^\w\s]', '', title.lower()).strip()
        link_map[norm] = url
        i += 2
        continue
    
    i += 1

print(f"Parsed {len(link_map)} Amazon links")

# Show some samples
for title, url in list(link_map.items())[:5]:
    print(f"  {title} → {url}")

# Function to find matching URL for a title
def find_amazon_link(title):
    norm = re.sub(r'[^\w\s]', '', title.lower()).strip()
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

# ============ UPDATE SHOP.HTML ============
shop_html = Path("/Users/openclaw/Desktop/WBF/shop.html").read_text()

updated = 0
no_match = []

# Find each product with a buyLink
for m in re.finditer(
    r'(\{\s*id:\s*\d+,\s*title:"([^"]+)"[^}]*?)buyLink:"([^"]+)"',
    shop_html, re.DOTALL
):
    full_before = m.group(1)
    title = m.group(2)
    old_url = m.group(3)
    
    new_url = find_amazon_link(title)
    if new_url:
        # Replace the buyLink URL
        old_pattern = f'buyLink:"{old_url}"'
        new_pattern = f'buyLink:"{new_url}"'
        shop_html = shop_html.replace(old_pattern, new_pattern, 1)
        updated += 1
    else:
        no_match.append(title)

print(f"\n✓ Updated {updated} buyLink URLs in shop.html")
if no_match:
    print(f"✗ No match for {len(no_match)} books")

# ============ UPDATE COLLECTIONS.HTML ============
coll_html = Path("/Users/openclaw/Desktop/WBF/collections.html").read_text()

coll_updated = 0
coll_no_match = []

for m in re.finditer(
    r'(\{\s*id:\s*\d+,\s*title:"([^"]+)"[^}]*?)buyLink:"([^"]*)"',
    coll_html, re.DOTALL
):
    full_before = m.group(1)
    title = m.group(2)
    old_url = m.group(3)
    
    new_url = find_amazon_link(title)
    if new_url:
        if old_url:
            old_pattern = f'buyLink:"{old_url}"'
            new_pattern = f'buyLink:"{new_url}"'
        else:
            # No existing buyLink - need to add it
            old_pattern = f'title:"{title}"'
            new_pattern = f'title:"{title}", buyLink:"{new_url}"'
        
        coll_html = coll_html.replace(old_pattern, new_pattern, 1)
        coll_updated += 1
    else:
        coll_no_match.append(title)

print(f"✓ Updated {coll_updated} buyLink URLs in collections.html")
if coll_no_match:
    print(f"✗ No match for {len(coll_no_match)} books")

# Save both files
Path("/Users/openclaw/Desktop/WBF/shop.html").write_text(shop_html)
Path("/Users/openclaw/Desktop/WBF/collections.html").write_text(coll_html)

print("\n✅ Saved both files")
