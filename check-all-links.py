#!/usr/bin/env python3
"""Check all freeLink URLs across all HTML files."""
import re
import urllib.request
import ssl
from pathlib import Path

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

for filename in ['index.html', 'shop.html', 'collections.html']:
    filepath = Path("/Users/openclaw/Desktop/WBF") / filename
    html = filepath.read_text()
    
    # Extract all freeLink URLs
    free_links = set(re.findall(r'freeLink:"([^"]+)"', html))
    
    print(f"\n=== {filename} - {len(free_links)} free links ===")
    
    broken = []
    for link in sorted(free_links):
        try:
            req = urllib.request.Request(link, method='HEAD')
            req.add_header('User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36')
            resp = urllib.request.urlopen(req, context=ctx, timeout=15)
            status = f"HTTP {resp.status}"
            print(f"  ✅ {link.split('/')[-1][:45]:45s} - {status}")
        except Exception as e:
            err = str(e)[:40]
            print(f"  ❌ {link.split('/')[-1][:45]:45s} - {err}")
            broken.append(link)
    
    if broken:
        print(f"\n  BROKEN: {len(broken)}")
        for link in broken:
            print(f"    {link}")
    else:
        print(f"  All links working!")
