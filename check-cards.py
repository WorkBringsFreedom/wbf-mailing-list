#!/usr/bin/env python3
with open('/Users/openclaw/Desktop/WBF/index.html','r') as f:
    c = f.read()

# Find card template ONLY (not modal code)
m = c.find('grid.innerHTML = filtered.map')
# Find the end of the card template - the closing backtick and .join()
end = c.find("`).join('');", m)
card_template = c[m:end + len("`).join('');")]

print('=== CARD TEMPLATE ONLY ===')
for i, line in enumerate(card_template.split('\n')):
    print(f'{i+1:3d}: {line}')

print()
print('=== DESCRIPTION CHECK IN CARDS ONLY ===')
has_reason_div = '<div class="reason"' in card_template
has_reason_text = '${b.reason}' in card_template
has_blurb = '${b.blurb}' in card_template
print(f'Has <div class="reason">: {has_reason_div}')
print(f'Has b.reason: {has_reason_text}')
print(f'Has b.blurb: {has_blurb}')

if not has_reason_div and not has_reason_text and not has_blurb:
    print()
    print('✅ DESCRIPTION SUCCESSFULLY REMOVED FROM CARDS')
else:
    print()
    print('❌ DESCRIPTION STILL PRESENT IN CARDS')
    
# Also verify modal still has full content
modal_m = c.find('function openModal(id)')
modal_end = c.find('function closeModal', modal_m)
modal_code = c[modal_m:modal_end]
print()
print('=== MODAL VERIFICATION ===')
print(f'Modal has blurb: {"${b.blurb}" in modal_code}')
print(f'Modal has reason: {"${b.reason}" in modal_code}')
print(f'Modal has why-box: {"why-box" in modal_code}')
print(f'Modal has meta-row: {"meta-row" in modal_code}')
