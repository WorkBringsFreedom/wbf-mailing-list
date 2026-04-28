#!/usr/bin/env python3
"""
Standardize modals across all three files to match index.html exactly.
"""
import re
from pathlib import Path

# Read index.html as the reference
idx = Path("/Users/openclaw/Desktop/WBF/index.html").read_text()

# Extract modal CSS from index.html
m = idx.find('/* ===== MODAL')
end = idx.find('/* ===== CART')
idx_modal_css = idx[m:end]
print("Extracted index.html modal CSS (%d chars)" % len(idx_modal_css))

# Extract modal HTML from index.html
m2 = idx.find('<div class="modal" id="modal"')
end2 = idx.find('<!-- CART DRAWER -->')
idx_modal_html = idx[m2:end2].strip()
print("Extracted index.html modal HTML (%d chars)" % len(idx_modal_html))

# Extract modal JS functions from index.html
m3 = idx.find('function openModal(id)')
end3 = idx.find('function closeModal()')
idx_openModal = idx[m3:end3]

m4 = idx.find('function closeModal()')
end4 = idx.find('document.addEventListener', m4)
idx_closeModal = idx[m4:end4]
print("Extracted index.html modal JS (%d chars)" % (len(idx_openModal) + len(idx_closeModal)))

# ============ FIX SHOP.HTML ============
shop = Path("/Users/openclaw/Desktop/WBF/shop.html").read_text()

# Replace modal CSS
old_shop_modal_css = re.search(r'  /\* ===== MODAL.*?/\* =====|\u003c/style>', shop, re.DOTALL)
if old_shop_modal_css:
    old_css = old_shop_modal_css.group(0)
    if old_css.endswith('</style>'):
        old_css = old_css[:-8]
    shop = shop.replace(old_css, idx_modal_css)
    print("Replaced shop.html modal CSS")

# Replace modal HTML
old_shop_modal_html = re.search(r'<div class="modal-overlay" id="modalOverlay".*?></div>\s*<div class="toast"', shop, re.DOTALL)
if old_shop_modal_html:
    shop = shop.replace(old_shop_modal_html.group(0), idx_modal_html + '\n\n<div class="toast"')
    print("Replaced shop.html modal HTML")

# Replace modal JS
old_shop_modal_js = re.search(r'function openModal\(id\)\s*\{.*?\}\s*function closeModal\(\)\s*\{.*?\}', shop, re.DOTALL)
if old_shop_modal_js:
    shop = shop.replace(old_shop_modal_js.group(0), idx_openModal + idx_closeModal)
    print("Replaced shop.html modal JS")

# Update onclick handlers in renderGrid to match index.html style
# index.html uses: onclick="openModal(${b.id})"  (same)
# shop.html already uses the same pattern

Path("/Users/openclaw/Desktop/WBF/shop.html").write_text(shop)
print("Saved shop.html")

# ============ FIX COLLECTIONS.HTML ============
coll = Path("/Users/openclaw/Desktop/WBF/collections.html").read_text()

# Replace modal CSS
old_coll_modal_css = re.search(r'  /\* ===== MODAL.*?/\* =====|\u003c/style>', coll, re.DOTALL)
if old_coll_modal_css:
    old_css = old_coll_modal_css.group(0)
    if old_css.endswith('</style>'):
        old_css = old_css[:-8]
    coll = coll.replace(old_css, idx_modal_css)
    print("Replaced collections.html modal CSS")

# Replace modal HTML
old_coll_modal_html = re.search(r'<div class="modal-overlay" id="modalOverlay".*?></div>\s*<div class="toast"', coll, re.DOTALL)
if old_coll_modal_html:
    coll = coll.replace(old_coll_modal_html.group(0), idx_modal_html + '\n\n<div class="toast"')
    print("Replaced collections.html modal HTML")

# Replace modal JS - need to adapt for collections data
old_coll_modal_js = re.search(r'function openModal\(id\)\s*\{.*?\}\s*function closeModal\(\)\s*\{.*?\}', coll, re.DOTALL)
if old_coll_modal_js:
    # Use index.html's modal but adapt for COLLECTIONS array
    new_coll_modal = idx_openModal.replace(
        'const b = PRODUCTS.find(x => x.id === id);',
        'const b = COLLECTIONS.find(x => x.id === id);'
    ).replace(
        "document.getElementById('modal').classList.add('open');",
        "document.getElementById('modal').classList.add('open');\n  document.body.classList.add('lock');"
    )
    coll = coll.replace(old_coll_modal_js.group(0), new_coll_modal + idx_closeModal)
    print("Replaced collections.html modal JS")

# Update onclick handlers to use openModal (same)
# collections.html already uses onclick="openModal(N)"

Path("/Users/openclaw/Desktop/WBF/collections.html").write_text(coll)
print("Saved collections.html")

print("\nAll files standardized to index.html modal style")
