#!/usr/bin/env python3
"""
Careful targeted fixes for shop.html and collections.html.
Only change specific known patterns, avoid regex that could corrupt.
"""
from pathlib import Path

# ========== FIX SHOP.HTML ==========
shop = Path("/Users/openclaw/Desktop/WBF/shop.html").read_text()
print("shop.html: %d bytes" % len(shop))

# 1. Remove FREE badge from cards
badge = "${b.freeLink ? '<div style=\"position:absolute;top:10px;right:10px;background:var(--blood);color:var(--paper);padding:4px 10px;font-size:11px;font-family:Bebas Neue, sans-serif;letter-spacing:2px;\">FREE</div>' : ''}"
if badge in shop:
    shop = shop.replace(badge, "")
    print("1. Removed FREE badge")

# 2. Add Economics filter
old_f = '''    <button class="chip active" data-filter="all">All</button>
    <button class="chip" data-filter="politics">Politics</button>
    <button class="chip" data-filter="philosophy">Philosophy</button>
    <button class="chip" data-filter="history">History</button>
    <button class="chip" data-filter="sociology">Sociology</button>'''
new_f = '''    <button class="chip active" data-filter="all">All</button>
    <button class="chip" data-filter="politics">Politics</button>
    <button class="chip" data-filter="philosophy">Philosophy</button>
    <button class="chip" data-filter="history">History</button>
    <button class="chip" data-filter="sociology">Sociology</button>
    <button class="chip" data-filter="economics">Economics</button>'''
if old_f in shop:
    shop = shop.replace(old_f, new_f)
    print("2. Added Economics filter")

# 3. Replace modal CSS class names
shop = shop.replace('.modal-overlay {', '.modal {')
shop = shop.replace('.modal-overlay.open {', '.modal.open {')

# Update .modal-inner
old_inner = '''.modal-inner { background: var(--paper); max-width: 800px; width: 100%; max-height: 90vh; overflow-y: auto; display: grid; grid-template-columns: 1fr 1.2fr; position: relative; border: 3px solid var(--ink); }'''
new_inner = '''.modal-inner { background: var(--paper); max-width: 900px; width: 100%; max-height: 90vh; overflow-y: auto; display: grid; grid-template-columns: 280px 1fr; position: relative; border: 3px solid var(--ink); box-shadow: 12px 12px 0 var(--blood); }'''
if old_inner in shop:
    shop = shop.replace(old_inner, new_inner)
    print("3. Updated .modal-inner CSS")

# Update cover area
old_cover = '''.modal .cover-area { background: var(--ink); padding: 40px; display: flex; align-items: center; justify-content: center; }
  .modal .cover-area .cover { width: 100%; max-width: 220px; aspect-ratio: 2/3; }'''
new_cover = '''.modal .cover-area { padding: 30px; background: var(--ink); display: flex; align-items: center; }
  .modal .cover-area .cover { width: 100%; box-shadow: 6px 6px 0 var(--blood); }'''
if old_cover in shop:
    shop = shop.replace(old_cover, new_cover)
    print("4. Updated .cover-area CSS")

# Update close button
old_close = '''.modal .close { position: absolute; top: 10px; right: 14px; background: none; border: none; font-size: 28px; cursor: pointer; color: var(--ink); }'''
new_close = '''.modal-close { position: absolute; top: 10px; right: 14px; background: var(--ink); color: var(--paper); border: none; width: 36px; height: 36px; cursor: pointer; font-size: 20px; z-index: 3; }
  .modal-close:hover { background: var(--blood); }'''
if old_close in shop:
    shop = shop.replace(old_close, new_close)
    print("5. Updated close button CSS")

# Update body
old_body = '''.modal .body { padding: 30px; }
  .modal .body h2 { font-family: "Playfair Display", serif; font-size: 28px; margin-bottom: 8px; }
  .modal .body .meta { font-size: 13px; opacity: 0.7; margin-bottom: 16px; }'''
new_body = '''.modal .body { padding: 30px 36px; }
  .modal .body .meta-row { font-family: "Special Elite", cursive; font-size: 12px; letter-spacing: 2px; text-transform: uppercase; color: var(--blood-dark); margin-bottom: 10px; }
  .modal .body h3 { font-family: "Playfair Display", serif; font-size: 34px; line-height: 1.1; margin-bottom: 6px; }
  .modal .body .author { font-family: "IBM Plex Mono", monospace; margin-bottom: 20px; font-size: 14px; }'''
if old_body in shop:
    shop = shop.replace(old_body, new_body)
    print("6. Updated .body CSS")

# Update why-box
old_why = '''.modal .body .reason { font-size: 12px; border-left: 3px solid var(--blood); padding-left: 12px; margin-bottom: 20px; }'''
new_why = '''.modal .body .why-box { background: var(--ink); color: var(--paper); padding: 16px 18px; margin-bottom: 20px; border-left: 6px solid var(--blood); }
  .modal .body .why-box h5 { font-family: "Bebas Neue", sans-serif; letter-spacing: 3px; font-size: 14px; color: var(--blood); margin-bottom: 6px; }
  .modal .body .why-box p { font-size: 13px; line-height: 1.5; }'''
if old_why in shop:
    shop = shop.replace(old_why, new_why)
    print("7. Updated why-box CSS")

# Update actions
old_actions = '''.modal .body .actions { display: flex; gap: 12px; }
  .modal .body .actions button {
    flex: 1; padding: 14px; font-family: "Bebas Neue", sans-serif; font-size: 16px;
    letter-spacing: 2px; text-transform: uppercase; cursor: pointer; border: 2px solid var(--ink);
  }
  .modal .body .actions .add { background: var(--blood); color: var(--paper); border-color: var(--blood); }
  .modal .body .actions .add:hover { background: var(--ink); }'''
new_actions = '''.modal .body .actions { display: flex; gap: 10px; margin-top: 10px; flex-wrap: wrap; }
  .modal .body .actions button {
    font-family: "Bebas Neue", sans-serif; letter-spacing: 2px; font-size: 14px; padding: 12px 20px;
    cursor: pointer; transition: all .15s; border: 2px solid var(--ink);
  }
  .modal .body .actions .buy { background: var(--blood); color: var(--paper); border-color: var(--blood); }
  .modal .body .actions .buy:hover { background: var(--blood-dark); }
  .modal .body .actions .save { background: var(--paper); color: var(--ink); }
  .modal .body .actions .save:hover { background: var(--cream); }'''
if old_actions in shop:
    shop = shop.replace(old_actions, new_actions)
    print("8. Updated actions CSS")

# Update price
old_price = '''.modal .body .price { font-family: "Bebas Neue", sans-serif; font-size: 28px; color: var(--blood); }'''
new_price = '''.modal .body .price { font-family: "Bebas Neue", sans-serif; font-size: 28px; letter-spacing: 2px; color: var(--blood); margin-bottom: 14px; }'''
if old_price in shop:
    shop = shop.replace(old_price, new_price)
    print("9. Updated price CSS")

# 10. Replace modal HTML
old_html = '''<div class="modal-overlay" id="modalOverlay" onclick="if(event.target===this)closeModal()">
  <div class="modal-inner">
    <button class="close" onclick="closeModal()">&times;</button>
    <div class="cover-area"><div class="cover" id="modalCover"></div></div>
    <div class="body" id="modalBody"></div>
  </div>
</div>'''
new_html = '''<!-- MODAL -->
<div class="modal" id="modal" onclick="if(event.target===this) closeModal()">
  <div class="modal-inner" id="modalInner"></div>
</div>'''
if old_html in shop:
    shop = shop.replace(old_html, new_html)
    print("10. Replaced modal HTML")

# 11. Replace modal JS
old_open = '''function openModal(id) {
  const b = PRODUCTS.find(x => x.id === id);
  // Show real cover image if available
  const coverHTML_img = b.coverImage
    ? '<img src="' + b.coverImage + '" alt="' + b.title + '" style="width:100%;height:100%;object-fit:cover;display:block;">'
    : coverHTML(b);
  document.getElementById('modalCover').innerHTML = coverHTML_img;
  document.getElementById('modalBody').innerHTML = `
    <div class="meta">// Case File ${String(b.id).padStart(4,'0')} &middot; Published ${b.year}</div>
    <h2>${b.title}</h2>
    <div class="meta">by ${b.author}</div>
    <div class="price" style="font-family:'Bebas Neue',sans-serif;font-size:28px;color:var(--blood);margin:12px 0;">$${b.price}</div>
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

new_open = '''function openModal(id) {
  const b = PRODUCTS.find(x => x.id === id);
  if (!b) return;
  document.getElementById('modalInner').innerHTML = `
    <button class="modal-close" onclick="closeModal()">✕</button>
    <div class="cover-area">${coverHTML(b)}</div>
    <div class="body">
      <div class="meta-row">// Case File ${String(b.id).padStart(4,'0')} &middot; Published ${b.year}</div>
      <h3>${b.title}</h3>
      <div class="author">by ${b.author}</div>
      <div class="price">$${b.price.toFixed(2)}</div>
      <p class="blurb">${b.blurb}</p>
      <div class="why-box">
        <h5>Product Details</h5>
        <p>${b.reason}</p>
      </div>
      <div class="actions">
        ${b.buyLink ? `<button class="buy" onclick="window.open('${b.buyLink}', '_blank')">BUY ON AMAZON</button>` : ''}
        ${b.freeLink ? `<button class="save" onclick="window.open('${b.freeLink}', '_blank')">GET FREE</button>` : ''}
      </div>
    </div>
  `;
  document.getElementById('modal').classList.add('open');
  document.body.classList.add('lock');
}'''

if old_open in shop:
    shop = shop.replace(old_open, new_open)
    print("11. Replaced openModal JS")

# Update closeModal
old_close_js = '''function closeModal() {
  document.getElementById('modalOverlay').classList.remove('open');
  document.body.classList.remove('lock');
}'''
new_close_js = '''function closeModal() {
  document.getElementById('modal').classList.remove('open');
  document.body.classList.remove('lock');
}'''
if old_close_js in shop:
    shop = shop.replace(old_close_js, new_close_js)
    print("12. Replaced closeModal JS")

Path("/Users/openclaw/Desktop/WBF/shop.html").write_text(shop)
print("\nshop.html SAVED (%d bytes)" % len(shop))

# Verify
final = Path("/Users/openclaw/Desktop/WBF/shop.html").read_text()
print("Verifications:")
print("  .modal class: %s" % ('.modal {' in final))
print("  modal#modal: %s" % ('id="modal"' in final))
print("  modalInner: %s" % ('modalInner' in final))
print("  modal-close: %s" % ('modal-close' in final))
print("  BUY ON AMAZON: %s" % ('BUY ON AMAZON' in final))
print("  GET FREE: %s" % ('GET FREE' in final))
print("  No modalOverlay: %s" % ('modalOverlay' not in final))
