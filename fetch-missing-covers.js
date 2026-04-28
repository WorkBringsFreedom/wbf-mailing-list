const fs = require('fs');
const path = require('path');

function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }
function slugify(title) {
  return title.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '').replace(/-+/g, '-');
}

async function fetchJSON(url) {
  try {
    const res = await fetch(url, { timeout: 10000 });
    if (!res.ok) return null;
    return await res.json();
  } catch (e) { return null; }
}

async function downloadImage(url, filepath) {
  try {
    const res = await fetch(url, { timeout: 15000 });
    if (!res.ok) return false;
    const ct = res.headers.get('content-type') || '';
    if (!ct.includes('image')) return false;
    const buf = Buffer.from(await res.arrayBuffer());
    if (buf.length < 2000) return false; // too small, probably a placeholder
    fs.writeFileSync(filepath, buf);
    return true;
  } catch (e) { return false; }
}

async function getCover(title, author) {
  const slug = slugify(title);
  const coverPath = path.join(__dirname, 'covers', `${slug}.jpg`);
  if (fs.existsSync(coverPath)) return `covers/${slug}.jpg`;

  const q = encodeURIComponent(`${title} ${author}`);

  // Source 1: Open Library search -> cover by ISBN
  const ol = await fetchJSON(`https://openlibrary.org/search.json?q=${q}&limit=3`);
  if (ol && ol.docs) {
    for (const doc of ol.docs) {
      if (doc.isbn && doc.isbn[0]) {
        const isbn = doc.isbn[0];
        // Try L then M
        const sizes = ['-L.jpg', '-M.jpg'];
        for (const size of sizes) {
          const ok = await downloadImage(`https://covers.openlibrary.org/b/isbn/${isbn}${size}`, coverPath);
          if (ok) return `covers/${slug}.jpg`;
        }
      }
      if (doc.cover_i) {
        const ok = await downloadImage(`https://covers.openlibrary.org/b/id/${doc.cover_i}-L.jpg`, coverPath);
        if (ok) return `covers/${slug}.jpg`;
      }
    }
  }

  // Source 2: Google Books API -> cover by volume ID
  const gb = await fetchJSON(`https://www.googleapis.com/books/v1/volumes?q=${encodeURIComponent(`intitle:${title} inauthor:${author}`)}&maxResults=3`);
  if (gb && gb.items) {
    for (const item of gb.items) {
      const vol = item.volumeInfo;
      if (vol.imageLinks) {
        const url = vol.imageLinks.thumbnail || vol.imageLinks.smallThumbnail;
        if (url) {
          const ok = await downloadImage(url.replace('http:', 'https:'), coverPath);
          if (ok) return `covers/${slug}.jpg`;
        }
      }
      if (vol.industryIdentifiers) {
        for (const id of vol.industryIdentifiers) {
          if (id.identifier) {
            const sizes = ['-L.jpg', '-M.jpg'];
            for (const size of sizes) {
              const ok = await downloadImage(`https://covers.openlibrary.org/b/isbn/${id.identifier}${size}`, coverPath);
              if (ok) return `covers/${slug}.jpg`;
            }
          }
        }
      }
    }
  }

  // Source 3: Internet Archive cover
  const ia = await fetchJSON(`https://archive.org/advancedsearch.php?q=${encodeURIComponent(`title:${title} creator:${author}`)}&fl[]=identifier&sort[]=downloads+desc&rows=3&output=json`);
  if (ia && ia.response && ia.response.docs) {
    for (const doc of ia.response.docs) {
      const url = `https://archive.org/services/img/${doc.identifier}`;
      const ok = await downloadImage(url, coverPath);
      if (ok) return `covers/${slug}.jpg`;
    }
  }

  return null;
}

async function main() {
  const books = JSON.parse(fs.readFileSync(path.join(__dirname, 'books-100.json'), 'utf8'));
  let found = 0;
  let stillMissing = 0;

  for (const b of books) {
    if (b.coverImage) continue;
    console.log(`Fetching: ${b.title}`);
    const cover = await getCover(b.title, b.author);
    if (cover) {
      b.coverImage = cover;
      found++;
      console.log(`  ✓ Found cover`);
    } else {
      stillMissing++;
      console.log(`  ✗ No cover found`);
    }
    await sleep(400);
  }

  fs.writeFileSync(path.join(__dirname, 'books-100.json'), JSON.stringify(books, null, 2));
  console.log(`\nDone! Found ${found} new covers. Still missing: ${stillMissing}`);
}

main().catch(e => { console.error(e); process.exit(1); });
