const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const SUBSCRIBERS_FILE = path.join(__dirname, 'subscribers.json');
const SHOP_HTML = path.join(__dirname, 'shop.html');
const SENT_FILE = path.join(__dirname, 'sent-books.json');
const ACCOUNT = 'wbf';

function loadJSON(file, defaultVal = []) {
  try {
    return JSON.parse(fs.readFileSync(file, 'utf8'));
  } catch {
    return defaultVal;
  }
}

function saveJSON(file, data) {
  fs.writeFileSync(file, JSON.stringify(data, null, 2));
}

function parseBooksFromShop() {
  try {
    const html = fs.readFileSync(SHOP_HTML, 'utf8');
    
    // Find the PRODUCTS array in the HTML
    const match = html.match(/const\s+PRODUCTS\s*=\s*(\[[\s\S]*?\]);/);
    if (!match) {
      console.log('Could not find PRODUCTS array in shop.html');
      return [];
    }
    
    // Parse the array - need to handle the JS object format
    let jsArray = match[1];
    
    // Convert JS object syntax to valid JSON
    // Replace single quotes with double quotes for property names and string values
    // This is a simplified approach - handles the basic format
    jsArray = jsArray.replace(/([{,]\s*)(\w+):/g, '$1"$2":');
    
    // Handle the specific format in the file
    const books = [];
    const bookPattern = /\{\s*id:\s*(\d+),\s*title:"([^"]+)",\s*author:"([^"]+)",\s*year:([^,]+),\s*cat:"([^"]+)"(?:,\s*tags:\[([^\]]*)\])?,?\s*coverImage:"([^"]+)"(?:,\s*freeLink:"([^"]+)")?(?:,\s*buyLink:"([^"]+)")?,?\s*blurb:"([^"]+)",\s*reason:"([^"]+)"\s*\}/g;
    
    let m;
    while ((m = bookPattern.exec(html)) !== null) {
      books.push({
        id: parseInt(m[1]),
        title: m[2],
        author: m[3],
        year: m[4].trim(),
        cat: m[5],
        tags: m[6] ? m[6].replace(/"/g, '').split(',') : [],
        coverImage: m[7],
        freeLink: m[8] || null,
        buyLink: m[9] || null,
        blurb: m[10],
        reason: m[11]
      });
    }
    
    return books;
  } catch (err) {
    console.error('Error parsing shop.html:', err.message);
    return [];
  }
}

function getNextBook() {
  const books = parseBooksFromShop();
  const sent = loadJSON(SENT_FILE, []);
  
  if (books.length === 0) {
    console.log('No books found in shop.html');
    return null;
  }
  
  console.log(`Found ${books.length} books in shop.html`);
  
  // Find books with free links that haven't been sent
  const available = books.filter(b => b.freeLink && !sent.includes(b.title));
  
  if (available.length === 0) {
    // Reset if all sent
    console.log('All books sent, resetting...');
    saveJSON(SENT_FILE, []);
    return books.find(b => b.freeLink) || null;
  }
  
  console.log(`${available.length} books available (with free links, not yet sent)`);
  
  // Pick a random book
  const book = available[Math.floor(Math.random() * available.length)];
  sent.push(book.title);
  saveJSON(SENT_FILE, sent);
  
  return book;
}

function buildNewsletter(book) {
  return `WORK BRINGS FREEDOM

THE WEEKLY DISPATCH
Banned Book of the Week

📚 FEATURED BOOK

"${book.title}"
by ${book.author} (${book.year})

${book.blurb}

Why it was banned:
${book.reason}

🔗 READ IT FREE
${book.freeLink}

💰 BUY THE BOOK
${book.buyLink || 'https://workbringsfreedom.com/shop.html'}

Visit the library:
https://workbringsfreedom.com/shop.html

Follow us:
https://www.youtube.com/@workbringsfreedom
https://www.tiktok.com/@workbringsfreedom
https://www.instagram.com/workbringsfreedom/
https://workbringsfreedom.substack.com

You received this because you joined the resistance at workbringsfreedom.com
To unsubscribe, reply with UNSUBSCRIBE

Work Brings Freedom
Built by Grind
`;
}

function getBookLink(title) {
  try {
    const html = fs.readFileSync(SHOP_HTML, 'utf8');
    // Find the specific book entry and extract buyLink
    const bookPattern = new RegExp('title:"' + title.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + '"[^}]*buyLink:"([^"]+)"');
    const match = html.match(bookPattern);
    return match ? match[1] : null;
  } catch {
    return null;
  }
}

function sendEmail(to, subject, body) {
  try {
    execSync(`himalaya message send --account ${ACCOUNT} <<'EOF'
From: dispatch@workbringsfreedom.com
To: ${to}
Subject: ${subject}

${body}
EOF`, { stdio: 'inherit' });
    return true;
  } catch (err) {
    console.error(`Failed to send to ${to}:`, err.message);
    return false;
  }
}

function main() {
  const subscribers = loadJSON(SUBSCRIBERS_FILE, []);
  
  if (subscribers.length === 0) {
    console.log('No subscribers yet.');
    return;
  }
  
  const book = getNextBook();
  if (!book) {
    console.log('No books with free links available.');
    return;
  }
  
  console.log(`Selected book: ${book.title} by ${book.author}`);
  console.log(`Free link: ${book.freeLink}`);
  
  const buyLink = getBookLink(book.title) || book.buyLink || 'https://workbringsfreedom.com/shop.html';
  
  const body = buildNewsletter({...book, buyLink});
  const subject = `📚 Banned Book of the Week: ${book.title}`;
  
  let sent = 0;
  let failed = 0;
  
  for (const sub of subscribers) {
    console.log(`Sending to ${sub.email}...`);
    if (sendEmail(sub.email, subject, body)) {
      sent++;
    } else {
      failed++;
    }
    // Rate limit
    execSync('sleep 2');
  }
  
  console.log(`\nDone! Sent: ${sent}, Failed: ${failed}`);
}

main();
