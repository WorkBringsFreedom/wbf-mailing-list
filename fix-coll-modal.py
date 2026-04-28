#!/usr/bin/env python3
"""Fix collections.html modal to match index.html style."""
from pathlib import Path

coll = Path("/Users/openclaw/Desktop/WBF/collections.html").read_text()
print("collections.html: %d bytes" % len(coll))

# 1. Replace modal CSS class names
coll = coll.replace('.modal-overlay {', '.modal {')
coll = coll.replace('.modal-overlay.open {', '.modal.open {')

# Update .modal-inner
old_inner = '''.modal-inner { background: var(--paper); max-width: 800px; width: 100%; max-height: 90vh; overflow-y: auto; display: grid; grid-template-columns: 280px 1fr; position: relative; border: 3px solid var(--ink); box-shadow: 12px 12px 0 var(--blood); }'''
# Already has the right .modal-inner from index.html style, skip

# Update cover area  
old_cover = '''.modal .cover-area { padding: 30px; background: var(--ink); display: flex; align-items: center; justify-content: center; }
  .modal .cover-area img { width: 100%; max-width: 220px; box-shadow: 6px 6px 0 var(--blood); }'''
new_cover = '''.modal .cover-area { padding: 30px; background: var(--ink); display: flex; align-items: center; }
  .modal .cover-area .cover { width: 100%; box-shadow: 6px 6px 0 var(--blood); }'''
if old_cover in coll:
    coll = coll.replace(old_cover, new_cover)
    print("1. Updated cover-area CSS")

# Update close button
old_close = '''.modal-close { position: absolute; top: 10px; right: 14px; background: var(--ink); color: var(--paper); border: none; width: 36px; height: 36px; cursor: pointer; font-size: 20px; z-index: 3; }
  .modal-close:hover { background: var(--blood); }'''
# Already has modal-close, skip

# 2. Replace modal HTML
old_html = '''<!-- MODAL -->
<div class="modal-overlay" id="modalOverlay" onclick="if(event.target===this)closeModal()">
  <div class="modal-inner">
    <button class="close" onclick="closeModal()">&times;</button>
    <div class="cover-area"><img id="modalCover" src="" alt="" style="width:100%;max-width:220px;box-shadow:6px 6px 0 var(--blood);"></div>
    <div class="body" id="modalBody"></div>
  </div>
</div>'''

new_html = '''<!-- MODAL -->
<div class="modal" id="modal" onclick="if(event.target===this) closeModal()">
  <div class="modal-inner" id="modalInner"></div>
</div>'''

if old_html in coll:
    coll = coll.replace(old_html, new_html)
    print("2. Replaced modal HTML")

# 3. Replace modal JS
old_open = '''function openModal(id) {
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
}'''

new_open = '''function openModal(id) {
  const b = COLLECTIONS.find(x => x.id === id);
  if (!b) return;
  // Build cover HTML
  const coverHTML = '<img src="' + b.cover + '" alt="' + b.title + '" style="width:100%;height:100%;object-fit:cover;display:block;">';
  document.getElementById('modalInner').innerHTML = `
    <button class="modal-close" onclick="closeModal()">✕</button>
    <div class="cover-area">${coverHTML}</div>
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

if old_open in coll:
    coll = coll.replace(old_open, new_open)
    print("3. Replaced openModal JS")

# Update closeModal
old_close_js = '''function closeModal() {
  document.getElementById('modalOverlay').classList.remove('open');
  document.body.style.overflow = '';
}'''
new_close_js = '''function closeModal() {
  document.getElementById('modal').classList.remove('open');
  document.body.classList.remove('lock');
}'''
if old_close_js in coll:
    coll = coll.replace(old_close_js, new_close_js)
    print("4. Replaced closeModal JS")

Path("/Users/openclaw/Desktop/WBF/collections.html").write_text(coll)
print("\ncollections.html SAVED (%d bytes)" % len(coll))

# Verify
final = Path("/Users/openclaw/Desktop/WBF/collections.html").read_text()
print("Verifications:")
print("  .modal class: %s" % ('.modal {' in final))
print("  modal#modal: %s" % ('id="modal"' in final))
print("  modalInner: %s" % ('modalInner' in final))
print("  modal-close: %s" % ('modal-close' in final))
print("  No modalOverlay: %s" % ('modalOverlay' not in final))
