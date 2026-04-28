#!/usr/bin/env python3
import re
from pathlib import Path

shop = Path("/Users/openclaw/Desktop/WBF/shop.html").read_text()

book_pattern = re.compile(
    r'\{\s*id:\s*(\d+),\s*title:"([^"]+)",\s*author:"([^"]+)",\s*year:([^,]+),\s*cat:"([^"]+)",\s*price:([\d.]+),\s*coverImage:"([^"]+)"(?:,\s*freeLink:"([^"]*)")?(?:,\s*buyLink:"([^"]*)")?,\s*blurb:"([^"]*)",\s*reason:"([^"]*)"\s*\}'
)

books = []
for m in book_pattern.finditer(shop):
    books.append({
        'id': int(m.group(1)),
        'title': m.group(2),
        'author': m.group(3),
        'year': m.group(4).strip(),
        'cat': m.group(5),
        'price': float(m.group(6)),
        'cover': m.group(7),
        'freeLink': m.group(8) or '',
        'buyLink': m.group(9) or '',
        'blurb': m.group(10),
        'reason': m.group(11)
    })

print("Parsed %d books" % len(books))

by_id = {b['id']: b for b in books}

collections_def = [
    {'name': 'Foundations of Order', 'desc': 'The bedrock texts of political philosophy.', 'ids': [2, 5, 7, 16]},
    {'name': 'Critiques of Modernity', 'desc': 'Books that diagnosed the spiritual and cultural decay of the modern world.', 'ids': [1, 6, 8, 10]},
    {'name': 'American Identity', 'desc': 'The story of the American experiment.', 'ids': [11, 12, 57, 14]},
    {'name': 'The Forbidden Shelf', 'desc': 'The books most frequently banned, censored, or suppressed.', 'ids': [3, 4, 15, 22]},
    {'name': 'Dystopian Warnings', 'desc': 'Fiction that foresaw the totalitarian future.', 'ids': [17, 18, 51, 52, 53, 55]},
    {'name': 'Revolution & Resistance', 'desc': 'The literature of uprising, rebellion, and the struggle against tyranny.', 'ids': [19, 20, 23, 24, 27, 28]},
    {'name': 'The Black Experience', 'desc': 'Black voices that America tried to silence.', 'ids': [59, 60, 61, 62, 63, 64, 65, 66]},
    {'name': 'The Holocaust & Genocide', 'desc': 'Testimonies to humanity\'s darkest hours.', 'ids': [25, 26, 97, 98, 99]},
    {'name': 'War & Its Discontents', 'desc': 'The brutal truth of war told by those who lived it.', 'ids': [101, 102, 103, 104, 105, 28]},
    {'name': 'Classics of Thought', 'desc': 'The foundational texts that built Western civilization.', 'ids': [29, 30, 31, 41, 42, 43, 47, 49]},
]

sections = []
next_id = 1
id_map = {}

for coll in collections_def:
    selected = [by_id[bid] for bid in coll['ids'] if bid in by_id]
    if not selected:
        continue
    cards = []
    for b in selected:
        id_map[next_id] = b
        cards.append(
            '    <div class="book-card" onclick="openModal(%d)">\n'
            '      <div class="cover"><img src="%s" alt="%s" style="width:100%%;height:100%%;object-fit:cover;display:block;border:none;"></div>\n'
            '      <div class="info"><div class="t">%s</div><div class="a">%s</div></div>\n'
            '    </div>' % (next_id, b['cover'], b['title'], b['title'], b['author'])
        )
        next_id += 1
    
    section = (
        '<section class="collection">\n'
        '  <div class="collection-header">\n'
        '    <div>\n'
        '      <h2>%s</h2>\n'
        '      <p style="text-align:left; margin-top:8px;">%s</p>\n'
        '    </div>\n'
        '  </div>\n'
        '  <div class="collection-grid">\n'
        '%s\n'
        '  </div>\n'
        '</section>' % (coll['name'], coll['desc'], '\n'.join(cards))
    )
    sections.append(section)

coll_html = Path("/Users/openclaw/Desktop/WBF/collections.html").read_text()

# Replace collections
old_match = re.search(r'(<section class="collection">.*?</section>)\s*(?=<footer>)', coll_html, re.DOTALL)
if old_match:
    coll_html = coll_html.replace(old_match.group(1), '\n\n'.join(sections))
    print("Replaced: %d sections, %d books" % (len(sections), next_id - 1))

# Remove price CSS
coll_html = re.sub(r'\s+\.book-card \.info \.price \{[^}]+\}', '', coll_html)
print("Removed price CSS")

# Build JS data
js_books = []
for bid, b in id_map.items():
    js_books.append(
        '  { id:%d, title:"%s", author:"%s", year:%s, price:%.2f, cover:"%s", freeLink:"%s", buyLink:"%s", blurb:"%s", reason:"%s" }' % (
            bid, b['title'], b['author'], b['year'], b['price'], b['cover'],
            b['freeLink'], b['buyLink'], b['blurb'], b['reason']
        )
    )

# Replace JS
old_js = re.search(r'const COLLECTIONS = \[.*?\];.*?function openModal\(id\)\s*\{.*?\}\s*function closeModal', coll_html, re.DOTALL)
if old_js:
    new_js = 'const COLLECTIONS = [\n' + ',\n'.join(js_books) + '\n];\n\nfunction openModal(id) {\n  const b = COLLECTIONS.find(x => x.id === id);\n  if (!b) return;\n  document.getElementById(\'modalCover\').src = b.cover;\n  document.getElementById(\'modalCover\').alt = b.title;\n  document.getElementById(\'modalBody\').innerHTML = `\n    <div class="meta-row">// Case File ${String(b.id).padStart(4,\'0\')} &middot; Published ${b.year}</div>\n    <h3>${b.title}</h3>\n    <div class="author">by ${b.author}</div>\n    <div class="price">$${b.price.toFixed(2)}</div>\n    <div class="blurb">${b.blurb}</div>\n    <div class="why-box">\n      <h5>Product Details</h5>\n      <p>${b.reason}</p>\n    </div>\n    <div class="actions">\n      ${b.buyLink ? `<button class="buy" onclick="window.open(\'${b.buyLink}\', \'_blank\')">BUY ON AMAZON</button>` : \'\'}\n      ${b.freeLink ? `<button class="save" onclick="window.open(\'${b.freeLink}\', \'_blank\')">GET FREE</button>` : \'\'}\n    </div>\n  `;\n  document.getElementById(\'modalOverlay\').classList.add(\'open\');\n  document.body.style.overflow = \'hidden\';\n}\n\nfunction closeModal'
    coll_html = coll_html.replace(old_js.group(0), new_js)
    print("Updated modal JS")

Path("/Users/openclaw/Desktop/WBF/collections.html").write_text(coll_html)
print("Saved")

final = Path("/Users/openclaw/Desktop/WBF/collections.html").read_text()
print("Price divs in cards: %d" % final.count('<div class="price">'))
print("Sections: %d" % len(re.findall(r'<section class="collection">', final)))
print("Onclick cards: %d" % len(re.findall(r'onclick="openModal\(\d+\)"', final)))
