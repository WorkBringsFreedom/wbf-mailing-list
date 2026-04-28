#!/usr/bin/env python3
"""Final fix for both files - clean modal JS."""
from pathlib import Path

# ========== FIX SHOP.HTML ==========
shop = Path("/Users/openclaw/Desktop/WBF/shop.html").read_text()

# Check what's in the modal openModal
m = shop.find('function openModal(id)')
end = shop.find('function closeModal', m)
open_modal = shop[m:end]

# Replace coverHTML(b) with actual image
old_cover = 'document.getElementById(\'modalInner\').innerHTML = `\n    <button class="modal-close" onclick="closeModal()">✕</button>\n    <div class="cover-area">${coverHTML(b)}</div>'
new_cover = 'document.getElementById(\'modalInner\').innerHTML = `\n    <button class="modal-close" onclick="closeModal()">✕</button>\n    <div class="cover-area">${b.coverImage ? \'<img src="\' + b.coverImage + \'" alt="\' + b.title + \'" style="width:100%;height:100%;object-fit:cover;display:block;">\' : coverHTML(b)}</div>'

if old_cover in open_modal:
    shop = shop.replace(old_cover, new_cover)
    print("[shop] Updated cover to use real image")

# Check for modalCover reference
if 'modalCover' in shop:
    # Shouldn't exist - check if it's a leftover
    print("[shop] WARNING: still has modalCover reference")
    # Find and show
    idx = shop.find('modalCover')
    print("  at position", idx)
    print("  context:", repr(shop[idx-20:idx+30]))

Path("/Users/openclaw/Desktop/WBF/shop.html").write_text(shop)
print("[shop] Saved")

# ========== FIX COLLECTIONS.HTML ==========
coll = Path("/Users/openclaw/Desktop/WBF/collections.html").read_text()

# Replace old modal HTML completely
old_modal_html = '''<!-- MODAL -->
<div class="modal-overlay" id="modalOverlay" onclick="if(event.target===this)closeModal()">
  <div class="modal-inner">
    <button class="modal-close" onclick="closeModal()">✕</button>
    <div class="cover-area"><img id="modalCover" src="" alt="" style="width:100%;max-width:220px;box-shadow:6px 6px 0 var(--blood);"></div>
    <div class="body" id="modalBody"></div>
  </div>
</div>'''

new_modal_html = '''<!-- MODAL -->
<div class="modal" id="modal" onclick="if(event.target===this) closeModal()">
  <div class="modal-inner" id="modalInner"></div>
</div>'''

if old_modal_html in coll:
    coll = coll.replace(old_modal_html, new_modal_html)
    print("[coll] Replaced modal HTML")

# Replace old modal JS
old_js = '''function openModal(id) {
  const b = COLLECTIONS.find(x => x.id === id);
  if (!b) return;
  document.getElementById('modalCover').src = b.cover;
  document.getElementById('modalCover').alt = b.title;
  document.getElementById('modalBody').innerHTML = `
    <div class="meta-row">// Collection Item ${String(b.id).padStart(4,'0')}</div>
    <h3>${b.title}</h3>
    <div class="author">by ${b.author}</div>
    <div class="price">$${b.price.toFixed(2)}</div>
    <div class="actions">
      <button class="buy" onclick="showToast('BUY ON AMAZON — coming soon')">BUY ON AMAZON</button>
      <button class="save" onclick="showToast('SAVED TO WISHLIST')">SAVE FOR LATER</button>
    </div>
  `;
  document.getElementById('modalOverlay').classList.add('open');
  document.body.style.overflow = 'hidden';
}'''

new_js = '''function openModal(id) {
  const b = COLLECTIONS.find(x => x.id === id);
  if (!b) return;
  const coverHTML = '<img src="' + b.cover + '" alt="' + b.title + '" style="width:100%;height:100%;object-fit:cover;display:block;">';
  document.getElementById('modalInner').innerHTML = `
    <button class="modal-close" onclick="closeModal()">✕</button>
    <div class="cover-area">${coverHTML}</div>
    <div class="body">
      <div class="meta-row">// Collection Item ${String(b.id).padStart(4,'0')}</div>
      <h3>${b.title}</h3>
      <div class="author">by ${b.author}</div>
      <div class="price">$${b.price.toFixed(2)}</div>
      <div class="actions">
        <button class="buy" onclick="showToast('BUY ON AMAZON — coming soon')">BUY ON AMAZON</button>
        <button class="save" onclick="showToast('SAVED TO WISHLIST')">SAVE FOR LATER</button>
      </div>
    </div>
  `;
  document.getElementById('modal').classList.add('open');
  document.body.classList.add('lock');
}'''

if old_js in coll:
    coll = coll.replace(old_js, new_js)
    print("[coll] Replaced modal JS")

# Fix closeModal
old_close = '''function closeModal() {
  document.getElementById('modal').classList.remove('open');
  document.body.classList.remove('lock');
}'''
new_close = '''function closeModal() {
  document.getElementById('modal').classList.remove('open');
  document.body.classList.remove('lock');
}'''

if old_close in coll:
    # It's already correct! But check for modalOverlay version
    pass

# Also fix the modalOverlay version
old_close2 = '''function closeModal() {
  document.getElementById('modalOverlay').classList.remove('open');
  document.body.style.overflow = '';
}'''
new_close2 = '''function closeModal() {
  document.getElementById('modal').classList.remove('open');
  document.body.classList.remove('lock');
}'''
if old_close2 in coll:
    coll = coll.replace(old_close2, new_close2)
    print("[coll] Fixed closeModal")

Path("/Users/openclaw/Desktop/WBF/collections.html").write_text(coll)
print("[coll] Saved")

# Verify both
with open('/Users/openclaw/Desktop/WBF/shop.html', 'r') as f:
    s = f.read()
with open('/Users/openclaw/Desktop/WBF/collections.html', 'r') as f:
    c = f.read()

print("\n=== FINAL VERIFICATION ===")
print("shop.html:")
print("  modalOverlay: %s" % ('modalOverlay' not in s))
print("  modalInner: %s" % ('modalInner' in s))
print("  modal#modal: %s" % ('id="modal"' in s))
print("  Real image in modal: %s" % ('b.coverImage' in s))
print("  BUY/GET buttons: %s" % ('BUY ON AMAZON' in s and 'GET FREE' in s))

print("collections.html:")
print("  modalOverlay: %s" % ('modalOverlay' not in c))
print("  modalInner: %s" % ('modalInner' in c))
print("  modal#modal: %s" % ('id="modal"' in c))
print("  BUY/SAVE buttons: %s" % ('BUY ON AMAZON' in c))
print("  No modalCover: %s" % ('modalCover' not in c))
print("  No modalBody: %s" % ('modalBody' not in c))
