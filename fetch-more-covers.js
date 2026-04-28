const fs = require('fs');
const path = require('path');

function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

function slugify(title) {
  return title.toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '')
    .replace(/-+/g, '-');
}

async function fetchOL(title, author) {
  const q = encodeURIComponent(`${title} ${author}`);
  try {
    const res = await fetch(`https://openlibrary.org/search.json?q=${q}&limit=1`, { timeout: 10000 });
    const data = await res.json();
    if (data.docs && data.docs[0] && data.docs[0].isbn && data.docs[0].isbn[0]) {
      return data.docs[0].isbn[0];
    }
  } catch (e) {}
  return null;
}

async function downloadCover(isbn, filepath) {
  try {
    const res = await fetch(`https://covers.openlibrary.org/b/isbn/${isbn}-L.jpg`, { timeout: 15000 });
    if (res.ok) {
      const ct = res.headers.get('content-type') || '';
      if (ct.includes('image')) {
        const buf = Buffer.from(await res.arrayBuffer());
        if (buf.length > 1000) {
          fs.writeFileSync(filepath, buf);
          return true;
        }
      }
    }
  } catch (e) {}
  return false;
}

async function main() {
  const books = JSON.parse(fs.readFileSync(path.join(__dirname, 'books-100.json'), 'utf8'));
  const coversDir = path.join(__dirname, 'covers');
  let found = 0;

  for (const b of books) {
    if (b.coverImage) continue; // already has cover
    const slug = slugify(b.title);
    const coverPath = path.join(coversDir, `${slug}.jpg`);

    const isbn = await fetchOL(b.title, b.author);
    if (isbn) {
      const ok = await downloadCover(isbn, coverPath);
      if (ok) {
        b.coverImage = `covers/${slug}.jpg`;
        found++;
        console.log(`Cover found: ${b.title} -> ${isbn}`);
      }
    }
    await sleep(300);
  }

  fs.writeFileSync(path.join(__dirname, 'books-100.json'), JSON.stringify(books, null, 2));
  console.log(`Extra covers found: ${found}`);
}

main().catch(e => { console.error(e); process.exit(1); });
