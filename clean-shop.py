#!/usr/bin/env python3
import re
from pathlib import Path

shop_html = Path("/Users/openclaw/Desktop/WBF/shop.html.bak2").read_text()
print("Starting from clean backup...")

# 1. REMOVE FREE BADGE
badge = """${b.freeLink ? '<div style="position:absolute;top:10px;right:10px;background:var(--blood);color:var(--paper);padding:4px 10px;font-size:11px;font-family:Bebas Neue, sans-serif;letter-spacing:2px;">FREE</div>' : ''}"""
if badge in shop_html:
    shop_html = shop_html.replace(badge, "")
    print("1. Removed FREE badge")

# 2. ADD ECONOMICS FILTER
old_filters = '''    <button class="chip active" data-filter="all">All</button>
    <button class="chip" data-filter="politics">Politics</button>
    <button class="chip" data-filter="philosophy">Philosophy</button>
    <button class="chip" data-filter="history">History</button>
    <button class="chip" data-filter="sociology">Sociology</button>'''
new_filters = '''    <button class="chip active" data-filter="all">All</button>
    <button class="chip" data-filter="politics">Politics</button>
    <button class="chip" data-filter="philosophy">Philosophy</button>
    <button class="chip" data-filter="history">History</button>
    <button class="chip" data-filter="sociology">Sociology</button>
    <button class="chip" data-filter="economics">Economics</button>'''
if old_filters in shop_html:
    shop_html = shop_html.replace(old_filters, new_filters)
    print("2. Added Economics filter")

# 3. IMPROVE MODAL
old_modal = "document.getElementById('modalCover').innerHTML = coverHTML(b);"
new_modal = """// Show real cover image if available
  const coverHTML_img = b.coverImage
    ? '<img src="' + b.coverImage + '" alt="' + b.title + '" style="width:100%;height:100%;object-fit:cover;display:block;">'
    : coverHTML(b);
  document.getElementById('modalCover').innerHTML = coverHTML_img;"""
if old_modal in shop_html:
    shop_html = shop_html.replace(old_modal, new_modal)
    print("3. Modal shows real cover images")

# Add price
old_author = '<div class="meta">by ${b.author}</div>\n    <div class="blurb">'
new_author = '<div class="meta">by ${b.author}</div>\n    <div class="price" style="font-family:\'Bebas Neue\',sans-serif;font-size:28px;color:var(--blood);margin:12px 0;">${b.price}</div>\n    <div class="blurb">'
if old_author in shop_html:
    shop_html = shop_html.replace(old_author, new_author)
    print("4. Added price to modal")

# 5. UPDATE buyLink URLs
rtf = Path("/Users/openclaw/Desktop/WBF/amazon_links.rtf").read_text()
link_map = {}
lines = rtf.split('\n')
i = 0
while i < len(lines) - 1:
    line = lines[i].strip()
    next_line = lines[i+1].strip()
    if not line or line.startswith('\\') or line.startswith('{') or line == 'AMAZON BOOK LINKS':
        i += 1
        continue
    if next_line.startswith('https://amzn.to/'):
        title = re.sub(r'\\[a-z]+\d*\s*', ' ', line)
        title = re.sub(r'\{[^}]*\}', '', title)
        title = re.sub(r'\s+', ' ', title).strip()
        norm = re.sub(r'[^\w\s]', '', title.lower()).strip()
        link_map[norm] = next_line
        i += 2
        continue
    i += 1

print("5. Parsed %d Amazon links" % len(link_map))

def normalize(t):
    return re.sub(r'[^\w\s]', '', t.lower()).strip()

def find_link(title):
    norm = normalize(title)
    if norm in link_map: return link_map[norm]
    words = norm.split()
    if len(words) >= 3:
        key = ' '.join(words[:3])
        if key in link_map: return link_map[key]
    if len(words) >= 2:
        key = ' '.join(words[:2])
        if key in link_map: return link_map[key]
    for k, v in link_map.items():
        if norm in k or k in norm: return v
    return None

updated = 0
no_match = []
for m in re.finditer(r'(\{\s*id:\s*\d+,\s*title:"([^"]+)"[^}]*?)buyLink:"([^"]+)"', shop_html, re.DOTALL):
    title = m.group(2)
    old_url = m.group(3)
    new_url = find_link(title)
    if new_url:
        old_pattern = 'buyLink:"%s"' % old_url
        new_pattern = 'buyLink:"%s"' % new_url
        shop_html = shop_html.replace(old_pattern, new_pattern, 1)
        updated += 1
    else:
        no_match.append(title)

print("6. Updated %d buyLink URLs" % updated)
if no_match:
    print("   No match for: %s" % ', '.join(no_match[:5]))

# 7. Fix any backslash-quotes
bq = '\\"'
if bq in shop_html:
    shop_html = shop_html.replace(bq, '"')
    print("7. Fixed backslash-quotes")

Path("/Users/openclaw/Desktop/WBF/shop.html").write_text(shop_html)
print("\nSaved shop.html")

# Verify
final = Path("/Users/openclaw/Desktop/WBF/shop.html").read_text()
print("File size: %d bytes" % len(final))
print("Economics: %s" % ('economics' in final))
print("Price in modal: %s" % ('price' in final.split('function openModal')[1].split('function')[0]))
print("CoverImage in modal: %s" % ('coverImage' in final.split('function openModal')[1].split('function')[0]))
print("No bad quotes: %s" % (bq not in final))
