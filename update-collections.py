#!/usr/bin/env python3
import re
from pathlib import Path
from collections import defaultdict

# Read shop.html to get all books
shop = Path("/Users/openclaw/Desktop/WBF/shop.html").read_text()

# Parse all books
book_pattern = re.compile(
    r'\{\s*id:\s*(\d+),\s*title:"([^"]+)",\s*author:"([^"]+)",\s*year:([^,]+),\s*cat:"([^"]+)",\s*price:([\d.]+),\s*coverImage:"([^"]+)"(?:,\s*freeLink:"([^"]*)")?(?:,\s*buyLink:"([^"]*)")?,\s*blurb:"([^"]*)",\s*reason:"([^"]*)"\s*\}'
)

books = []
for m in book_pattern.finditer(shop):
    books.append({
        'id': int(m.group(1)),
        'title': m.group(2),
        'author': m.group(3),
        'year': m.group(4).strip(),
        'cat': m.group(5),
        'price': float(m.group(6)),
        'cover': m.group(7),
        'freeLink': m.group(8) or '',
        'buyLink': m.group(9) or '',
        'blurb': m.group(10),
        'reason': m.group(11)
    })

print(f"Parsed {len(books)} books from shop.html")

# Define collections with specific book selections
collections_def = [
    {
        'name': 'Foundations of Order',
        'desc': 'The bedrock texts of political philosophy and the origins of Western political thought.',
        'ids': [2, 5, 7, 16]  # Conservative Mind, Reflections, Leviathan, Politics
    },
    {
        'name': 'Critiques of Modernity',
        'desc': 'Books that diagnosed the spiritual and cultural decay of the modern world before most saw it coming.',
        'ids': [1, 6, 8, 10]  # Death of West, Why Liberalism Failed, Men Among Ruins, Suicide of West
    },
    {
        'name': 'American Identity',
        'desc': 'The story of the American experiment -- its promise, its perils, and its unraveling.',
        'ids': [11, 12, 57, 14]  # Federalist, Democracy in America, Grapes of Wrath, Israel Lobby
    },
    {
        'name': 'The Forbidden Shelf',
        'desc': 'The books most frequently banned, censored, or suppressed -- the ones power fears most.',
        'ids': [3, 4, 15, 22]  # Culture of Narcissism, Bowling Alone, Culture of Critique, Rights of Man
    },
    {
        'name': 'Dystopian Warnings',
        'desc': 'Fiction that foresaw the totalitarian future -- surveillance, thoughtcrime, and the death of freedom.',
        'ids': [17, 18, 51, 52, 53, 55]  # 1984, Animal Farm, Brave New World, Fahrenheit 451, Clockwork Orange, Darkness at Noon
    },
    {
        'name': 'Revolution & Resistance',
        'desc': 'The literature of uprising, rebellion, and the struggle against tyranny.',
        'ids': [19, 20, 23, 24, 27, 28]  # Communist Manifesto, Das Kapital, Common Sense, Social Contract, Prince, Discourses on Livy
    },
    {
        'name': 'The Black Experience',
        'desc': 'Black voices that America tried to silence -- from slavery to civil rights to the present.',
        'ids': [59, 60, 61, 62, 63, 64, 65, 66]  # To Kill Mockingbird, Huck Finn, Native Son, Black Boy, Invisible Man, Go Tell It, Fire Next Time, Caged Bird
    },
    {
        'name': 'The Holocaust & Genocide',
        'desc': 'Testimonies to humanity\'s darkest hours -- the books that preserve memory against denial.',
        'ids': [25, 26, 97, 98, 99]  # Gulag Archipelago, Ivan Denisovich, Anne Frank, Night, Maus
    },
    {
        'name': 'War & Its Discontents',
        'desc': 'The brutal truth of war told by those who lived it -- anti-war classics from every era.',
        'ids': [101, 102, 103, 104, 105, 28]  # Things They Carried, Catch-22, Slaughterhouse-Five, Johnny Got His Gun, All Quiet, Homage to Catalonia
    },
    {
        'name': 'Classics of Thought',
        'desc': 'The foundational texts that built Western civilization -- philosophy, statecraft, and ethics.',
        'ids': [29, 30, 31, 41, 42, 43, 47, 49]  # Origins of Totalitarianism, Eichmann, Human Condition, Zarathustra, Beyond Good, Genealogy, Republic, Art of War
    },
]

# Build lookup by id
by_id = {b['id']: b for b in books}

# Build collection HTML sections
sections = []
next_modal_id = 1
book_id_map = {}

for coll in collections_def:
    selected = []
    for bid in coll['ids']:
        if bid in by_id:
            selected.append(by_id[bid])
    
    if not selected:
        continue
    
    cards = []
    for b in selected:
        book_id_map[next_modal_id] = b
        cards.append(
            '    <div class="book-card" onclick="openModal(%d)">\n'
            '      <div class="cover"><img src="%s" alt="%s" style="width:100%%;height:100%%;object-fit:cover;display:block;border:none;"></div>\n'
            '      <div class="info"><div class="t">%s</div><div class="a">%s</div></div>\n'
            '    </div>' % (
                next_modal_id, b['cover'], b['title'], b['title'], b['author']
            )
        )
        next_modal_id += 1
    
    section = (
        '<section class="collection">\n'
        '  <div class="collection-header">\n'
        '    <div>\n'
        '      <h2>%s</h2>\n'
        '      <p style="text-align:left; margin-top:8px;">%s</p>\n'
        '    </div>\n'
        '  </div>\n'
        '  <div class="collection-grid">\n'
        '%s\n'
        '  </div>\n'
        '</section>' % (coll['name'], coll['desc'], '\n'.join(cards))
    )
    sections.append(section)

# Read current collections.html
coll_html = Path("/Users/openclaw/Desktop/WBF/collections.html").read_text()

# Replace all collection sections (from first <section class="collection"> to before <footer>)
old_match = re.search(r'(<section class="collection">.*?</section>)\s*(?=<footer>)', coll_html, re.DOTALL)
if old_match:
    coll_html = coll_html.replace(old_match.group(1), '\n\n'.join(sections))
    print(f"Replaced collections: {len(sections)} sections, {next_modal_id - 1} books")

# Remove price CSS
if '.book-card .info .price' in coll_html:
    coll_html = re.sub(
        r'\s+\.book-card \.info \.price \{[^}]+\}',
        '',
        coll_html
    )
    print("Removed price CSS")

# Build new JS data array
js_books = []
for bid, b in book_id_map.items():
    js_books.append(
        '  { id:%d, title:"%s", author:"%s", year:%s, price:%.2f, cover:"%s", freeLink:"%s", buyLink:"%s", blurb:"%s", reason:"%s" }' % (
            bid, b['title'], b['author'], b['year'], b['price'], b['cover'],
            b['freeLink'], b['buyLink'], b['blurb'], b['reason']
        )
    )

js_data = ',\n'.join(js_books)

# Replace JS
old_js = re.search(r'const COLLECTIONS = \[.*?\];.*?function openModal\(id\)\s*\{.*?\}\s*function closeModal', coll_html, re.DOTALL)
if old_js:
    new_js = '''const COLLECTIONS = [
''' + js_data + '''
];

function openModal(id) {
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
}

function closeModal'''
    coll_html = coll_html.replace(old_js.group(0), new_js)
    print("Updated modal JS")

Path("/Users/openclaw/Desktop/WBF/collections.html").write_text(coll_html)
print("\nSaved collections.html")

# Verify
final = Path("/Users/openclaw/Desktop/WBF/collections.html").read_text()
print("Price divs in cards: %d" % final.count('<div class="price">'))
print(f"Collection sections: {len(re.findall(r'<section class=\"collection\">', final))}")
print(f"Books with onclick: {len(re.findall(r'onclick=\"openModal\\(\\d+\\)\"', final))}")
