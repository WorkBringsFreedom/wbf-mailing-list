#!/usr/bin/env python3
"""
Clean duplicated CSS in shop.html and collections.html.
The modal CSS got injected multiple times. Remove duplicates.
"""
import re
from pathlib import Path

for filename in ['shop.html', 'collections.html']:
    filepath = Path("/Users/openclaw/Desktop/WBF") / filename
    html = filepath.read_text()
    original_len = len(html)
    
    # Find all CSS blocks (from <style> to </style>)
    style_start = html.find('<style>')
    style_end = html.find('</style>', style_start)
    css = html[style_start + 7:style_end]
    
    # Split into rules and deduplicate
    # A CSS rule starts with whitespace + selector and ends with }
    rules = re.findall(r'\s+([^{]+\{[^}]*\})', css)
    
    seen = set()
    unique_rules = []
    for rule in rules:
        # Normalize for comparison
        normalized = re.sub(r'\s+', ' ', rule.strip())
        if normalized not in seen:
            seen.add(normalized)
            unique_rules.append(rule)
    
    # Rebuild CSS
    new_css = '\n'.join(unique_rules)
    new_html = html[:style_start + 7] + '\n' + new_css + '\n  ' + html[style_end:]
    
    filepath.write_text(new_html)
    print(f"{filename}: {original_len} -> {len(new_html)} bytes")
    print(f"  Removed {len(rules) - len(unique_rules)} duplicate CSS rules")
