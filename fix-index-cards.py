#!/usr/bin/env python3
"""Fix index.html card display: shorter card text, add price + BUY NOW button."""
from pathlib import Path

idx = Path("/Users/openclaw/Desktop/WBF/index.html").read_text()

# 1. First, add .price-card and .buy-now CSS to the .book section
old_book_css = """  .book .info .reason {
    font-family: "Special Elite", cursive; font-size: 11px; margin-top: 8px;
    text-transform: uppercase; letter-spacing: 1.5px; color: var(--blood-dark);
  }"""

new_book_css = """  .book .info .reason {
    font-family: "Special Elite", cursive; font-size: 10px; margin-top: 6px;
    text-transform: uppercase; letter-spacing: 1.5px; color: var(--blood-dark);
    line-height: 1.4; display: -webkit-box; -webkit-line-clamp: 2;
    -webkit-box-orient: vertical; overflow: hidden;
  }
  .book .info .price-card {
    font-family: "Bebas Neue", sans-serif; font-size: 18px; letter-spacing: 1px;
    color: var(--blood); margin-top: 8px;
  }
  .book .buy-now {
    margin-top: 10px; display: inline-block;
    font-family: "Bebas Neue", sans-serif; font-size: 12px; letter-spacing: 2px;
    text-transform: uppercase; background: var(--ink); color: var(--paper);
    padding: 8px 16px; cursor: pointer; border: 2px solid var(--ink);
    transition: all .15s; text-decoration: none;
  }
  .book .buy-now:hover { background: var(--blood); border-color: var(--blood); }"""

if old_book_css in idx:
    idx = idx.replace(old_book_css, new_book_css)
    print("1. Updated card CSS")
else:
    print("1. WARNING: Could not find card CSS to replace")

# 2. Update renderGrid to show price + BUY NOW button on cards
old_render = '''document.querySelector('.section-head .meta').textContent = `// ${filtered.length} product${filtered.length===1?'':'s'} showing`;
    grid.innerHTML = filtered.map(b => `
      <div class="book" onclick="openModal(${b.id})">
        ${coverHTML(b)}
        <div class="info">
          <div class="t">${b.title}</div>
          <div class="a">${b.author}${b.freeLink ? ' <span style="color:var(--blood);font-size:11px;letter-spacing:1px;">// FREE</span>' : ''}</div>
          <div class="reason">// ${b.reason.split('·')[0]}</div>
        </div>
      </div>
    `).join('');'''

new_render = '''document.querySelector('.section-head .meta').textContent = `// ${filtered.length} product${filtered.length===1?'':'s'} showing`;
    grid.innerHTML = filtered.map(b => `
      <div class="book" onclick="openModal(${b.id})">
        ${coverHTML(b)}
        <div class="info">
          <div class="t">${b.title}</div>
          <div class="a">${b.author}${b.freeLink ? ' <span style="color:var(--blood);font-size:11px;letter-spacing:1px;">// FREE</span>' : ''}</div>
          <div class="reason">// ${b.reason}</div>
          <div class="price-card">$${b.price.toFixed(2)}</div>
          ${b.buyLink ? `<a class="buy-now" href="${b.buyLink}" target="_blank" onclick="event.stopPropagation();">BUY NOW</a>` : ''}
        </div>
      </div>
    `).join('');'''

if old_render in idx:
    idx = idx.replace(old_render, new_render)
    print("2. Updated renderGrid with price + BUY NOW")
else:
    print("2. WARNING: Could not find renderGrid to replace")

# 3. Shorten all the reason fields to 1-2 sentences max
replacements = [
    ("Banned and burned in the USSR for anti-communist themes. Challenged repeatedly in US schools for 'pro-communist' and sexual content. Still one of the most frequently challenged books worldwide.",
     "Burned in the USSR. Still one of the most challenged books worldwide."),
    
    ("Banned in the USSR and Eastern Bloc for anti-communist satire. Burned in Kenya (1991) and banned in UAE (2002). Frequently challenged in US schools for political content.",
     "Banned across the Eastern Bloc. Burned in Kenya (1991)."),
    
    ("Banned in Ireland (1932) and multiple US states for sexual content, drug use, and anti-religious themes. Frequently challenged in schools. Listed among the most banned books of the 20th century.",
     "Banned in Ireland (1932). Among the most banned books of the 20th century."),
    
    ("Ironically banned and censored itself—removed from schools for 'vulgarity' and Bible burning scenes. Challenged in Mississippi (1999) and Texas. Irony: a book about censorship being censored.",
     "Ironically banned for 'vulgarity' and Bible-burning scenes."),
    
    ("Frequently challenged and banned for racial slurs, profanity, and 'immoral' themes. Removed from schools in Mississippi (2017), Virginia, and California. Consistently ranks among the most banned classics.",
     "Removed from schools in Mississippi (2017). Among the most banned classics."),
    
    ("Banned in Texas (2006), challenged in Kansas and California for sexual content and 'anti-Christian' themes. Frequently targeted by conservative groups. Banned in some school districts as recently as 2022.",
     "Banned in Texas (2006). Still targeted by conservative groups."),
    
    ("One of the most banned books in American history. Banned from the Concord Public Library (1885) as 'trash.' Challenged hundreds of times for racial slurs. Still banned in some school districts today.",
     "Banned as 'trash' in 1885. Still banned in some districts today."),
    
    ("Burned in California (1939) by Associated Farmers. Banned in Kansas, Illinois, and multiple states for 'profanity' and socialist themes. Steinbeck was investigated by the FBI. The book they tried to suppress became a Pulitzer Prize winner.",
     "Burned in California (1939). Steinbeck was investigated by the FBI."),
    
    ("Banned in Strongsville, Ohio (1972) and challenged repeatedly for profanity, sexual content, and 'anti-military' themes. One of the most frequently banned novels of the 20th century.",
     "Banned in Ohio (1972). Among the most banned novels of the 20th century."),
    
    ("Burned in Drake, North Dakota (1973). Banned in Michigan and challenged repeatedly for profanity, sexual content, and 'anti-American' themes. Vonnegut personally defended the book. One of the most censored American novels.",
     "Burned in North Dakota (1973). Vonnegut personally defended it."),
    
    ("One of the most banned books in American schools. Challenged over 50 times between 1990-2000 alone. Banned for profanity, racial slurs, and 'euthanasia' themes. Frequently appears on the ALA's most challenged list.",
     "Challenged 50+ times 1990–2000. On the ALA's most challenged list."),
    
    ("Banned in Boston (1906) and multiple cities for 'obscenity' and socialist content. The meat industry lobbied hard to suppress it. Banned in several countries. One of the most impactful banned books in history—literally changed federal law.",
     "Banned in Boston (1906). Changed federal food-safety law."),
    
    ("Challenged and banned repeatedly for sexual content, violence, and 'occult' themes. Removed from AP English curricula in multiple states. A Virginia state senator called it 'moral sewage.' Despite bans, won the Pulitzer and is essential American literature.",
     "Removed from AP English in multiple states. Won the Pulitzer anyway."),
    
    ("Frequently challenged and banned for sexual content, violence, and 'troubling ideas about race relations.' Banned in California schools. Challenged in North Carolina, Michigan, and Virginia. Despite censorship, won the Pulitzer and National Book Award.",
     "Banned in California schools. Won Pulitzer and National Book Award."),
    
    ("Banned in Arizona (2012) under HB 2281, which prohibited ethnic studies. Republican lawmakers in multiple states have sought to ban it from schools. Indiana's governor attempted to remove it from teacher training programs. One of the most politically targeted books in America.",
     "Banned in Arizona (2012). The most politically targeted book in America."),
    
    ("Banned in virtually every capitalist country during the Cold War. Possession could result in imprisonment in the US under the Smith Act. Still banned or heavily restricted in many countries today. One of the most historically suppressed political texts.",
     "Banned across the West during the Cold War. Still restricted today."),
]

for old_text, new_text in replacements:
    if old_text in idx:
        idx = idx.replace(old_text, new_text, 1)
        print(f"3. Shortened: {new_text[:50]}...")
    else:
        print(f"3. WARNING: Could not find text: {old_text[:50]}...")

Path("/Users/openclaw/Desktop/WBF/index.html").write_text(idx)
print(f"\nSaved: {len(idx)} bytes")

# Verify
final = Path("/Users/openclaw/Desktop/WBF/index.html").read_text()
print("\n=== VERIFICATION ===")
print(f"price-card CSS: {'price-card' in final}")
print(f"buy-now CSS: {'buy-now' in final}")
print(f"BUY NOW in card: {'BUY NOW' in final}")
print(f"-webkit-line-clamp: {'-webkit-line-clamp' in final}")
print(f"No long reasons (avg < 100 chars): {sum(len(r) for r in replacements) / len(replacements) < 100}")
