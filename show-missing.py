#!/usr/bin/env python3
import re

# Parse the RTF
rtf = open('/Users/openclaw/Desktop/WBF/amazon_links.rtf').read()
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

def find_link(title):
    norm = re.sub(r'[^\w\s]', '', title.lower()).strip()
    if norm in link_map: return True
    words = norm.split()
    if len(words) >= 3:
        if ' '.join(words[:3]) in link_map: return True
    if len(words) >= 2:
        if ' '.join(words[:2]) in link_map: return True
    for k in link_map:
        if norm in k or k in norm: return True
    return False

# Check shop.html
shop = open('/Users/openclaw/Desktop/WBF/shop.html').read()
shop_missing = []
for m in re.finditer(r'title:"([^"]+)"', shop):
    title = m.group(1)
    if not find_link(title):
        shop_missing.append(title)

# Check collections.html
coll = open('/Users/openclaw/Desktop/WBF/collections.html').read()
coll_missing = []
for m in re.finditer(r'title:"([^"]+)"', coll):
    title = m.group(1)
    if not find_link(title):
        coll_missing.append(title)

# Remove duplicates
shop_missing = list(dict.fromkeys(shop_missing))
coll_missing = list(dict.fromkeys(coll_missing))

print('=== MISSING FROM SHOP.HTML ===')
for t in shop_missing:
    print(f'  • {t}')

print()
print('=== MISSING FROM COLLECTIONS.HTML ===')
for t in coll_missing:
    print(f'  • {t}')

both = set(shop_missing) & set(coll_missing)
if both:
    print(f'\n=== IN BOTH FILES ({len(both)} books) ===')
    for t in sorted(both):
        print(f'  • {t}')
