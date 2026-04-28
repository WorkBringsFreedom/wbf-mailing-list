import json, re

with open('/Users/openclaw/Desktop/WBF/shop.html') as f:
    html = f.read()

with open('/Users/openclaw/Desktop/WBF/books-100.json') as f:
    new_books = json.load(f)

# Extract existing 16 books blocks (IDs 1-16) from current html
prod_section = html.split('const PRODUCTS =')[1].split('];')[0]
existing_blocks = []
for m in re.finditer(r'\{[^}]*id:(\d+)[^}]*\}', prod_section):
    bid = int(m.group(1))
    if 1 <= bid <= 16:
        existing_blocks.append((bid, m.group(0)))

existing_blocks.sort(key=lambda x: x[0])
print(f'Extracted {len(existing_blocks)} original books')

# Build fresh array
all_books = [b[1] for b in existing_blocks]

for b in new_books:
    fields = []
    fields.append(f'id:{b["id"]}')
    fields.append(f'title:"{b["title"].replace(chr(92), chr(92)+chr(92)).replace(chr(34), chr(92)+chr(34))}"')
    fields.append(f'author:"{b["author"].replace(chr(92), chr(92)+chr(92)).replace(chr(34), chr(92)+chr(34))}"')
    fields.append(f'year:{b["year"]}')
    fields.append(f'cat:"{b["cat"]}"')
    fields.append(f'price:{b["price"]:.2f}')
    if b.get('coverImage'):
        fields.append(f'coverImage:"{b["coverImage"]}"')
    if b.get('freeLink'):
        fields.append(f'freeLink:"{b["freeLink"]}"')
    fields.append(f'buyLink:"{b["buyLink"]}"')
    fields.append(f'blurb:"{b["blurb"].replace(chr(92), chr(92)+chr(92)).replace(chr(34), chr(92)+chr(34))}"')
    fields.append(f'reason:"{b["reason"].replace(chr(92), chr(92)+chr(92)).replace(chr(34), chr(92)+chr(34))}"')
    all_books.append('  { ' + ', '.join(fields) + ' }')

prod_str = 'const PRODUCTS = [\n' + ',\n'.join(all_books) + '\n];'

# Replace the old array
start = html.index('const PRODUCTS = [')
end = html.index('];\n\nlet activeFilter')
if end == -1:
    end = html.index('];\n\nfunction renderGrid')
new_html = html[:start] + prod_str + html[end+2:]

# Update header
new_html = new_html.replace('16 forbidden books', '116 forbidden books')

with open('/Users/openclaw/Desktop/WBF/shop.html', 'w') as f:
    f.write(new_html)

print('shop.html rebuilt successfully')

# Verify
with open('/Users/openclaw/Desktop/WBF/shop.html') as f:
    verify = f.read()
ids = re.findall(r'id:(\d+)', verify.split('const PRODUCTS =')[1].split('];')[0])
print(f'Total IDs: {len(ids)}')
new_with_cover = sum(1 for m in re.finditer(r'id:(\d+).*?coverImage', verify.split('const PRODUCTS =')[1].split('];')[0]) if int(m.group(1)) >= 17)
print(f'New books with covers: {new_with_cover}/100')
