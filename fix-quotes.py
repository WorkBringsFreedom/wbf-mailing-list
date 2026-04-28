#!/usr/bin/env python3
with open('/Users/openclaw/Desktop/WBF/shop.html','r') as f:
    html = f.read()

# Fix broken buyLink URLs: \" should be "
# The pattern is: buyLink:"URL\", blurb:
# Should be: buyLink:"URL", blurb:
html = html.replace('\\"', '"')

with open('/Users/openclaw/Desktop/WBF/shop.html','w') as f:
    f.write(html)

print('Fixed backslash-quote issue in buyLink URLs')
