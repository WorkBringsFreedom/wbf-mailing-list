#!/usr/bin/env python3
"""
Update both WBF files:
1. shop.html - add economics filter, improve modal
2. collections.html - add more collections, improve modal
"""

import re
from pathlib import Path
from collections import defaultdict

shop_html = Path("/Users/openclaw/Desktop/WBF/shop.html").read_text()
coll_html = Path("/Users/openclaw/Desktop/WBF/collections.html").read_text()

# ============ 1. SHOP.HTML: ADD ECONOMICS FILTER ============
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
    print("Added Economics filter to shop.html")

# ============ 2. SHOP.HTML: IMPROVE MODAL ============
old_modal = '''function openModal(id) {
  const b = PRODUCTS.find(x => x.id === id);
  document.getElementById('modalCover').innerHTML = coverHTML(b);
  document.getElementById('modalBody').innerHTML = `
    <div class="meta">// Case File ${String(b.id).padStart(4,'0')} &middot; Published ${b.year}</div>
    <h2>${b.title}</h2>
    <div class="meta">by ${b.author}</div>
    <div class="blurb">${b.blurb}</div>
    <div class="why-box">
      <h5>Product Details</h5>
      <p>${b.reason}</p>
    </div>
    <div class="actions">
      ${b.buyLink ? `<button class="add" onclick="window.open('${b.buyLink}', '_blank')">BUY ON AMAZON</button>` : ''}
      ${b.freeLink ? `<button class="save" onclick="window.open('${b.freeLink}', '_blank')">GET FREE</button>` : ''}
    </div>
  `;
  document.getElementById('modalOverlay').classList.add('open');
  document.body.classList.add('lock');
}'''

new_modal = '''function openModal(id) {
  const b = PRODUCTS.find(x => x.id === id);
  // Show real cover image if available, fallback to CSS cover
  const coverHTML = b.coverImage
    ? `<img src="${b.coverImage}" alt="${b.title}" style="width:100%;height:100%;object-fit:cover;display:block;">`
    : `<div class="cover theme-${b.theme || 1}"><div class="title-area">${b.title}</div><div class="redact-bar"></div><div class="redact-bar short"></div><div class="author">${b.author}</div></div>`;
  document.getElementById('modalCover').innerHTML = coverHTML;
  document.getElementById('modalBody').innerHTML = `
    <div class="meta">// Case File ${String(b.id).padStart(4,'0')} &middot; Published ${b.year}</div>
    <h2>${b.title}</h2>
    <div class="meta">by ${b.author}</div>
    <div class="price" style="font-family:'Bebas Neue',sans-serif;font-size:28px;color:var(--blood);margin:12px 0;">$${b.price.toFixed(2)}</div>
    <div class="blurb">${b.blurb}</div>
    <div class="why-box">
      <h5>Product Details</h5>
      <p>${b.reason}</p>
    </div>
    <div class="actions">
      ${b.buyLink ? `<button class="add" onclick="window.open('${b.buyLink}', '_blank')">BUY ON AMAZON</button>` : ''}
      ${b.freeLink ? `<button class="save" onclick="window.open('${b.freeLink}', '_blank')">GET FREE</button>` : ''}
    </div>
  `;
  document.getElementById('modalOverlay').classList.add('open');
  document.body.classList.add('lock');
}'''

if old_modal in shop_html:
    shop_html = shop_html.replace(old_modal, new_modal)
    print("Improved shop.html modal with real cover images + price")

# ============ 3. PARSE BOOKS FROM SHOP.HTML ============
book_pattern = re.compile(
    r'\{\s*id:\s*(\d+),\s*title:"([^"]+)",\s*author:"([^"]+)",\s*year:([^,]+),\s*cat:"([^"]+)",\s*price:([\d.]+),\s*coverImage:"([^"]+)"(?:,\s*freeLink:"([^"]*)")?(?:,\s*buyLink:"([^"]*)")?,\s*blurb:"([^"]*)",\s*reason:"([^"]*)"\s*\}'
)

books = []
for m in book_pattern.finditer(shop_html):
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

print(f"Parsed {len(books)} books from shop.html")

# Group by category
by_cat = defaultdict(list)
for b in books:
    by_cat[b['cat']].append(b)

# ============ 4. BUILD NEW COLLECTIONS ============
collection_defs = [
    ("Foundations of Order", "philosophy", "The bedrock texts of political philosophy and the origins of Western political thought."),
    ("Critiques of Modernity", "politics", "Books that diagnosed the spiritual and cultural decay of the modern world before most saw it coming."),
    ("American Identity", "history", "The story of the American experiment -- its promise, its perils, and its unraveling."),
    ("The Forbidden Shelf", "sociology", "The books most frequently banned, censored, or suppressed -- the ones power fears most."),
    ("Economics & Power", "economics", "How wealth, markets, and power shape civilization -- and who controls them."),
    ("Revolution & Resistance", "politics", "The literature of uprising, rebellion, and the struggle against tyranny."),
]

sections = []
book_id_map = {}
next_id = 1

for name, cat, desc in collection_defs:
    cat_books = by_cat.get(cat, [])
    if not cat_books:
        continue
    selected = cat_books[:4]
    cards = []
    for b in selected:
        book_id_map[next_id] = b
        cards.append(
            '    <div class="book-card" onclick="openModal(%d)">\n'
            '      <div class="cover"><img src="%s" alt="%s" style="width:100%%;height:100%%;object-fit:cover;display:block;border:none;"></div>\n'
            '      <div class="info"><div class="t">%s</div><div class="a">%s</div><div class="price">$%.2f</div></div>\n'
            '    </div>' % (next_id, b['cover'], b['title'], b['title'], b['author'], b['price'])
        )
        next_id += 1
    
    section = '<section class="collection">\n  <div class="collection-header">\n    <div>\n      <h2>%s</h2>\n      <p style="text-align:left; margin-top:8px;">%s</p>\n    </div>\n  </div>\n  <div class="collection-grid">\n%s\n  </div>\n</section>' % (name, desc, '\n'.join(cards))
    sections.append(section)

# Replace collections
old_match = re.search(r'(<section class="collection">.*?</section>)\s*(?=<footer>)', coll_html, re.DOTALL)
if old_match:
    coll_html = coll_html.replace(old_match.group(1), '\n\n'.join(sections))
    print("Replaced collections: %d sections, %d books" % (len(sections), next_id - 1))

# ============ 5. IMPROVE COLLECTIONS MODAL ============
js_books = []
for bid, b in book_id_map.items():
    js_books.append(
        '  { id:%d, title:"%s", author:"%s", year:%s, price:%.2f, cover:"%s", freeLink:"%s", buyLink:"%s", blurb:"%s", reason:"%s" }' % (
            bid, b['title'], b['author'], b['year'], b['price'], b['cover'],
            b['freeLink'], b['buyLink'], b['blurb'], b['reason']
        )
    )

js_data = ',\n'.join(js_books)

old_js = re.search(r'const COLLECTIONS = \[.*?\];.*?function openModal\(id\)\s*\{.*?\}\s*function closeModal', coll_html, re.DOTALL)
if old_js:
    new_js = '''const COLLECTIONS = [
''' + js_data + '''
];

function openModal(id) {
  const b = COLLECTIONS.find(x => x.id === id);
  if (!b) return;
  document.getElementById('modalCover').src = b.cover;
  document.getElementById('modalCover').alt = b.title;
  document.getElementById('modalBody').innerHTML = `
    <div class="meta-row">// Case File ${String(b.id).padStart(4,'0')} &middot; Published ${b.year}</div>
    <h3>${b.title}</h3>
    <div class="author">by ${b.author}</div>
    <div class="price">$${b.price.toFixed(2)}</div>
    <div class="blurb">${b.blurb}</div>
    <div class="why-box">
      <h5>Product Details</h5>
      <p>${b.reason}</p>
    </div>
    <div class="actions">
      ${b.buyLink ? `<button class="buy" onclick="window.open('${b.buyLink}', '_blank')">BUY ON AMAZON</button>` : ''}
      ${b.freeLink ? `<button class="save" onclick="window.open('${b.freeLink}', '_blank')">GET FREE</button>` : ''}
    </div>
  `;
  document.getElementById('modalOverlay').classList.add('open');
  document.body.style.overflow = 'hidden';
}

function closeModal'''
    coll_html = coll_html.replace(old_js.group(0), new_js)
    print("Improved collections modal with full book data")

Path("/Users/openclaw/Desktop/WBF/shop.html").write_text(shop_html)
Path("/Users/openclaw/Desktop/WBF/collections.html").write_text(coll_html)
print("Saved both files")
