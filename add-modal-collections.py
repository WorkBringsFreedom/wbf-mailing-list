#!/usr/bin/env python3
"""Add modal popup to collections.html matching shop.html behavior."""

import re
from pathlib import Path

html_path = Path("/Users/openclaw/Desktop/WBF/collections.html")
html = html_path.read_text()

# Step 1: Add modal CSS (before closing </style>)
modal_css = """
  /* ===== MODAL ===== */
  .modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.85); z-index: 100; display: none; align-items: center; justify-content: center; padding: 20px; }
  .modal-overlay.open { display: flex; }
  .modal-inner { background: var(--paper); max-width: 800px; width: 100%; max-height: 90vh; overflow-y: auto; display: grid; grid-template-columns: 1fr 1.2fr; position: relative; border: 3px solid var(--ink); }
  .modal .cover-area { background: var(--ink); padding: 40px; display: flex; align-items: center; justify-content: center; }
  .modal .cover-area .cover { width: 100%; max-width: 220px; aspect-ratio: 2/3; }
  .modal .body { padding: 30px; }
  .modal .body h2 { font-family: "Playfair Display", serif; font-size: 28px; margin-bottom: 8px; }
  .modal .body .meta { font-size: 13px; opacity: 0.7; margin-bottom: 16px; }
  .modal .body .price { font-family: "Bebas Neue", sans-serif; font-size: 28px; color: var(--blood); }
  .modal .body .blurb { font-size: 14px; line-height: 1.6; margin: 16px 0; }
  .modal .body .reason { font-size: 12px; border-left: 3px solid var(--blood); padding-left: 12px; margin-bottom: 20px; }
  .modal .body .actions { display: flex; gap: 12px; }
  .modal .body .actions button {
    flex: 1; padding: 14px; font-family: "Bebas Neue", sans-serif; font-size: 16px;
    letter-spacing: 2px; text-transform: uppercase; cursor: pointer; border: 2px solid var(--ink);
  }
  .modal .body .actions .buy { background: var(--blood); color: var(--paper); border-color: var(--blood); }
  .modal .body .actions .buy:hover { background: var(--ink); }
  .modal .body .actions .free { background: var(--paper); color: var(--ink); }
  .modal .body .actions .free:hover { background: var(--cream); }
  .modal .close { position: absolute; top: 10px; right: 14px; background: none; border: none; font-size: 28px; cursor: pointer; color: var(--ink); }
  .toast {
    position: fixed; bottom: 30px; left: 50%; transform: translateX(-50%) translateY(100px);
    background: var(--ink); color: var(--paper); padding: 14px 28px;
    font-family: "IBM Plex Mono", monospace; font-size: 13px; letter-spacing: 2px;
    text-transform: uppercase; z-index: 300; opacity: 0; transition: all .3s ease;
    border: 2px solid var(--blood);
  }
  .toast.show { transform: translateX(-50%) translateY(0); opacity: 1; }
  @media (max-width: 700px) {
    .modal-inner { grid-template-columns: 1fr; }
    .modal .cover-area { padding: 20px; }
  }
"""

# Insert before closing </style>
if '</style>' in html and '.modal-overlay' not in html:
    html = html.replace('</style>', modal_css + '\n</style>')
    print("✓ Added modal CSS")

# Step 2: Add onclick to each book-card
# Change: <div class="book-card"> → <div class="book-card" onclick="openModal('TITLE')">
# But first we need to extract the book data

# Parse all book cards to build the product data
book_cards = re.findall(
    r'<div class="book-card">\s*<div class="cover">.*?alt="([^"]+)".*?'
    r'<div class="info">\s*<div class="t">([^<]+)</div>\s*<div class="a">([^<]+)</div>\s*<div class="price">([^<]+)</div>\s*</div>\s*</div>',
    html, re.DOTALL
)

# Build PRODUCTS data array
products = []
for i, (alt, title, author, price_str) in enumerate(book_cards, 1):
    price = float(price_str.replace('$','').replace(',',''))
    # Try to find matching data from shop.html for freeLink/buyLink/blurb/reason
    products.append({
        'id': i,
        'title': title.strip(),
        'author': author.strip(),
        'price': price,
        'alt': alt.strip()
    })

print(f"Found {len(products)} book cards")

# Now add onclick to each card
for p in products:
    old_card = f'<div class="book-card">\n      <div class="cover"><img src="covers/'
    # Need a more flexible replace - use the alt text to identify
    pattern = f'<div class="book-card">\s*<div class="cover"><img src="[^"]*{re.escape(p["alt"].replace(" ", "").lower())}[^"]*"[^>]*>'
    # Actually, simpler approach: replace the book-card divs sequentially

# Better approach: add onclick to ALL book-card divs
# Count how many book-card divs exist
card_count = html.count('<div class="book-card">')
print(f"Total book-card divs: {card_count}")

# Replace each <div class="book-card"> with <div class="book-card" onclick="openModal(N)">
# We need to number them sequentially
counter = [0]
def add_onclick(match):
    counter[0] += 1
    return f'<div class="book-card" onclick="openModal({counter[0]})">'

html = re.sub(r'<div class="book-card">', add_onclick, html)
print(f"✓ Added onclick handlers to {counter[0]} cards")

# Step 3: Extract cover image sources for each card
covers = re.findall(r'<div class="book-card"[^>]*>\s*<div class="cover"><img src="([^"]+)"', html)
print(f"Found {len(covers)} cover images")

# Step 4: Build JS data from the card content
js_products = []
for i, p in enumerate(products):
    cover = covers[i] if i < len(covers) else ""
    js_products.append(
        f'{{ id:{p["id"]}, title:"{p["title"]}", author:"{p["author"]}", price:{p["price"]:.2f}, cover:"{cover}" }}'
    )

# Step 5: Add modal HTML and JS before closing </body>
modal_html = f"""
<!-- MODAL -->
<div class="modal-overlay" id="modalOverlay" onclick="if(event.target===this)closeModal()">
  <div class="modal-inner">
    <button class="close" onclick="closeModal()">&times;</button>
    <div class="cover-area"><img id="modalCover" src="" alt="" style="width:100%;max-width:220px;aspect-ratio:2/3;object-fit:cover;display:block;"></div>
    <div class="body" id="modalBody"></div>
  </div>
</div>
<div class="toast" id="toast"></div>

<script>
const COLLECTIONS = [
{',\n'.join(js_products)}
];

function openModal(id) {{
  const b = COLLECTIONS.find(x => x.id === id);
  if (!b) return;
  document.getElementById('modalCover').src = b.cover;
  document.getElementById('modalCover').alt = b.title;
  document.getElementById('modalBody').innerHTML = `
    <div class="meta">// Collection Item ${{String(b.id).padStart(4,'0')}}</div>
    <h2>${{b.title}}</h2>
    <div class="meta">by ${{b.author}}</div>
    <div class="price">$${{b.price.toFixed(2)}}</div>
    <div class="actions">
      <button class="buy" onclick="showToast('BUY ON AMAZON — coming soon')">BUY ON AMAZON</button>
    </div>
  `;
  document.getElementById('modalOverlay').classList.add('open');
  document.body.style.overflow = 'hidden';
}}

function closeModal() {{
  document.getElementById('modalOverlay').classList.remove('open');
  document.body.style.overflow = '';
}}

function showToast(msg) {{
  const t = document.getElementById('toast');
  t.textContent = msg;
  t.classList.add('show');
  setTimeout(() => t.classList.remove('show'), 2500);
}}

document.addEventListener('keydown', e => {{ if (e.key === 'Escape') closeModal(); }});
</script>
"""

# Insert before closing </body>
if '</body>' in html:
    html = html.replace('</body>', modal_html + '\n</body>')
    print("✓ Added modal HTML + JavaScript")

html_path.write_text(html)
print("\n✅ Saved collections.html")
