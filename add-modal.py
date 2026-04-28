#!/usr/bin/env python3
"""Add modal popup to collections.html matching index.html behavior."""

import re
from pathlib import Path

html = Path("/Users/openclaw/Desktop/WBF/collections.html").read_text()

# === 1. PARSE BOOKS FROM COLLECTIONS HTML ===
# Each book-card has: cover img with alt, title div, author div, price div
book_pattern = re.compile(
    r'<div class="book-card">\s*'
    r'<div class="cover"><img src="([^"]+)" alt="([^"]*)"[^/]*/?></div>\s*'
    r'<div class="info"><div class="t">([^<]+)</div>\s*'
    r'<div class="a">([^<]+)</div>\s*'
    r'<div class="price">([^<]+)</div>'
)

books = []
for i, m in enumerate(book_pattern.finditer(html), 1):
    cover, alt, title, author, price = m.groups()
    price_val = float(price.strip().replace('$','').replace(',',''))
    books.append({
        'id': i,
        'cover': cover.strip(),
        'alt': alt.strip(),
        'title': title.strip(),
        'author': author.strip(),
        'price': price_val
    })

print(f"Found {len(books)} books in collections.html")

# === 2. ADD MODAL CSS ===
modal_css = """
  /* ===== MODAL ===== */
  .modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.85); z-index: 100; display: none; align-items: center; justify-content: center; padding: 20px; }
  .modal-overlay.open { display: flex; }
  .modal-inner { background: var(--paper); max-width: 900px; width: 100%; max-height: 90vh; overflow-y: auto; display: grid; grid-template-columns: 280px 1fr; position: relative; border: 3px solid var(--ink); box-shadow: 12px 12px 0 var(--blood); }
  .modal-close { position: absolute; top: 10px; right: 14px; background: var(--ink); color: var(--paper); border: none; width: 36px; height: 36px; cursor: pointer; font-size: 20px; z-index: 3; }
  .modal-close:hover { background: var(--blood); }
  .modal .cover-area { padding: 30px; background: var(--ink); display: flex; align-items: center; justify-content: center; }
  .modal .cover-area img { width: 100%; max-width: 220px; box-shadow: 6px 6px 0 var(--blood); }
  .modal .body { padding: 30px 36px; }
  .modal .body .meta-row { font-family: "Special Elite", cursive; font-size: 12px; letter-spacing: 2px; text-transform: uppercase; color: var(--blood-dark); margin-bottom: 10px; }
  .modal .body h3 { font-family: "Playfair Display", serif; font-size: 34px; line-height: 1.1; margin-bottom: 6px; }
  .modal .body .author { font-family: "IBM Plex Mono", monospace; margin-bottom: 20px; font-size: 14px; }
  .modal .body .price { font-family: "Bebas Neue", sans-serif; font-size: 28px; letter-spacing: 2px; color: var(--blood); margin-bottom: 14px; }
  .modal .body .actions { display: flex; gap: 10px; margin-top: 10px; flex-wrap: wrap; }
  .modal .body .actions button { font-family: "Bebas Neue", sans-serif; letter-spacing: 2px; font-size: 14px; padding: 12px 20px; cursor: pointer; transition: all .15s; border: 2px solid var(--ink); }
  .modal .body .actions .buy { background: var(--blood); color: var(--paper); border-color: var(--blood); }
  .modal .body .actions .buy:hover { background: var(--blood-dark); }
  .modal .body .actions .save { background: var(--paper); color: var(--ink); }
  .modal .body .actions .save:hover { background: var(--cream); }

  .toast {
    position: fixed; bottom: 20px; left: 50%; transform: translateX(-50%) translateY(100px);
    background: var(--ink); color: var(--paper); padding: 14px 22px; font-family: "IBM Plex Mono", monospace;
    font-size: 13px; letter-spacing: 1px; border-left: 4px solid var(--blood); z-index: 300;
    transition: transform .3s; text-transform: uppercase;
  }
  .toast.show { transform: translateX(-50%) translateY(0); }

  @media (max-width: 900px) {
    .modal-inner { grid-template-columns: 1fr; }
    .modal .cover-area { padding: 20px; }
    .modal .cover-area img { max-width: 200px; }
  }
"""

if '.modal-overlay' not in html:
    html = html.replace('</style>', modal_css + '\n</style>')
    print("✓ Added modal CSS")

# === 3. ADD onclick TO EACH BOOK-CARD ===
counter = [0]
def add_click(match):
    counter[0] += 1
    return f'<div class="book-card" onclick="openModal({counter[0]})"'

html = re.sub(r'<div class="book-card">', add_click, html)
print(f"✓ Added onclick to {counter[0]} book cards")

# === 4. BUILD JS DATA ARRAY ===
js_books = []
for b in books:
    js_books.append(f'  {{ id:{b["id"]}, title:"{b["title"]}", author:"{b["author"]}", price:{b["price"]:.2f}, cover:"{b["cover"]}" }}')

js_data = ',\n'.join(js_books)

# === 5. ADD MODAL HTML + JS BEFORE </body> ===
modal_html = f"""
<!-- MODAL -->
<div class="modal-overlay" id="modalOverlay" onclick="if(event.target===this)closeModal()">
  <div class="modal-inner">
    <button class="modal-close" onclick="closeModal()">✕</button>
    <div class="cover-area"><img id="modalCover" src="" alt="" style="width:100%;max-width:220px;box-shadow:6px 6px 0 var(--blood);"></div>
    <div class="body" id="modalBody"></div>
  </div>
</div>
<div class="toast" id="toast"></div>

<script>
const COLLECTIONS = [
{js_data}
];

function openModal(id) {{
  const b = COLLECTIONS.find(x => x.id === id);
  if (!b) return;
  document.getElementById('modalCover').src = b.cover;
  document.getElementById('modalCover').alt = b.title;
  document.getElementById('modalBody').innerHTML = `
    <div class="meta-row">// Collection Item ${{String(b.id).padStart(4,'0')}}</div>
    <h3>${{b.title}}</h3>
    <div class="author">by ${{b.author}}</div>
    <div class="price">$${{b.price.toFixed(2)}}</div>
    <div class="actions">
      <button class="buy" onclick="showToast('BUY ON AMAZON — coming soon')">BUY ON AMAZON</button>
      <button class="save" onclick="showToast('SAVED TO WISHLIST')">SAVE FOR LATER</button>
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

if '<!-- MODAL -->' not in html and '</body>' in html:
    html = html.replace('</body>', modal_html + '\n</body>')
    print("✓ Added modal HTML + JS")

Path("/Users/openclaw/Desktop/WBF/collections.html").write_text(html)
print("\n✅ Saved collections.html")
