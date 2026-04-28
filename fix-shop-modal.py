#!/usr/bin/env python3
import re

with open('/Users/openclaw/Desktop/WBF/shop.html','r') as f:
    html = f.read()

# 1. Replace coverHTML with real image in modal
old_cover = "document.getElementById('modalCover').innerHTML = coverHTML(b);"
new_cover = '''// Show real cover image if available, fallback to CSS cover
  const coverHTML_img = b.coverImage
    ? '<img src="' + b.coverImage + '" alt="' + b.title + '" style="width:100%;height:100%;object-fit:cover;display:block;">'
    : coverHTML(b);
  document.getElementById('modalCover').innerHTML = coverHTML_img;'''

if old_cover in html:
    html = html.replace(old_cover, new_cover)
    print('Replaced modal cover with real image')

# 2. Add price after author line
old_author = '<div class="meta">by ${b.author}</div>\n    <div class="blurb">'
new_author = '<div class="meta">by ${b.author}</div>\n    <div class="price" style="font-family:\'Bebas Neue\',sans-serif;font-size:28px;color:var(--blood);margin:12px 0;">$${b.price.toFixed(2)}</div>\n    <div class="blurb">'

if old_author in html:
    html = html.replace(old_author, new_author)
    print('Added price to modal')
else:
    print('Could not find author/blurb pattern')

with open('/Users/openclaw/Desktop/WBF/shop.html','w') as f:
    f.write(html)
print('Saved shop.html')
