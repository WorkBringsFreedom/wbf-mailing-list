const fs = require('fs');
const path = require('path');
const nodemailer = require('nodemailer');

const SUBSCRIBERS_FILE = path.join(__dirname, 'subscribers.json');
const SHOP_HTML = path.join(__dirname, 'shop.html');
const SENT_FILE = path.join(__dirname, 'sent-books.json');

// SMTP config for 1984.is
const transporter = nodemailer.createTransport({
  host: 'mail.1984.is',
  port: 587,
  secure: false,
  auth: {
    user: 'dispatch@workbringsfreedom.com',
    pass: 'Pi7Nk3Zo4Lr3Ay7Xv2'
  },
  tls: {
    rejectUnauthorized: true
  }
});

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
  
  const available = books.filter(b => b.freeLink && !sent.includes(b.title));
  
  if (available.length === 0) {
    console.log('All books sent, resetting...');
    saveJSON(SENT_FILE, []);
    return books.find(b => b.freeLink) || null;
  }
  
  const book = available[Math.floor(Math.random() * available.length)];
  sent.push(book.title);
  saveJSON(SENT_FILE, sent);
  
  return book;
}

function getBookLink(title) {
  try {
    const html = fs.readFileSync(SHOP_HTML, 'utf8');
    const bookPattern = new RegExp('title:"' + title.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + '"[^}]*buyLink:"([^"]+)"');
    const match = html.match(bookPattern);
    return match ? match[1] : null;
  } catch {
    return null;
  }
}

function buildHTMLNewsletter(book) {
  const buyLink = getBookLink(book.title) || book.buyLink || 'https://workbringsfreedom.com/shop.html';
  
  return `
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
  body { font-family: Georgia, serif; line-height: 1.6; color: #111; background: #f3ecd8; margin: 0; padding: 20px; }
  .container { max-width: 600px; margin: 0 auto; background: #fff; padding: 30px; border: 3px solid #111; }
  h1 { font-family: 'Bebas Neue', Impact, sans-serif; font-size: 32px; letter-spacing: 2px; margin: 0 0 10px; }
  .tagline { font-family: 'IBM Plex Mono', monospace; font-size: 12px; text-transform: uppercase; letter-spacing: 3px; color: #c8102e; margin-bottom: 30px; }
  h2 { font-family: 'Bebas Neue', Impact, sans-serif; font-size: 24px; letter-spacing: 1px; margin: 30px 0 15px; }
  .book-title { font-size: 22px; font-weight: bold; font-style: italic; margin: 20px 0 5px; }
  .author { font-family: 'IBM Plex Mono', monospace; font-size: 14px; color: #555; margin-bottom: 15px; }
  .blurb { font-size: 16px; margin-bottom: 20px; }
  .reason { background: #f3ecd8; padding: 15px; border-left: 4px solid #c8102e; margin: 20px 0; }
  .reason-label { font-family: 'IBM Plex Mono', monospace; font-size: 11px; text-transform: uppercase; letter-spacing: 2px; color: #c8102e; margin-bottom: 5px; }
  .button { display: inline-block; background: #c8102e; color: #fff; padding: 12px 24px; text-decoration: none; font-family: 'Bebas Neue', Impact, sans-serif; font-size: 16px; letter-spacing: 2px; margin: 10px 0; }
  .button.secondary { background: #111; }
  .social { margin-top: 30px; padding-top: 20px; border-top: 2px solid #111; }
  .social a { display: inline-block; margin-right: 15px; color: #c8102e; text-decoration: none; font-family: 'IBM Plex Mono', monospace; font-size: 13px; }
  .footer { margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd; font-size: 12px; color: #777; font-family: 'IBM Plex Mono', monospace; }
</style>
</head>
<body>
<div class="container">
  <h1>WORK BRINGS FREEDOM</h1>
  <div class="tagline">The Weekly Dispatch · Banned Book of the Week</div>
  
  <h2>📚 Featured Book</h2>
  
  <div class="book-title">"${book.title}"</div>
  <div class="author">by ${book.author} (${book.year})</div>
  
  <div class="blurb">${book.blurb}</div>
  
  <div class="reason">
    <div class="reason-label">Why it was banned</div>
    ${book.reason}
  </div>
  
  <p><a href="${book.freeLink}" class="button">🔗 READ IT FREE</a></p>
  
  <p><a href="${buyLink}" class="button secondary">💰 BUY THE BOOK</a></p>
  
  <p><a href="https://workbringsfreedom.com/shop.html">Visit the Library →</a></p>
  
  <div class="social">
    <a href="https://www.youtube.com/@workbringsfreedom">YouTube</a>
    <a href="https://www.tiktok.com/@workbringsfreedom">TikTok</a>
    <a href="https://www.instagram.com/workbringsfreedom/">Instagram</a>
    <a href="https://workbringsfreedom.substack.com">Substack</a>
  </div>
  
  <div class="footer">
    You received this because you joined the resistance at workbringsfreedom.com<br>
    To unsubscribe, reply with UNSUBSCRIBE<br><br>
    Work Brings Freedom · Built by Grind
  </div>
</div>
</body>
</html>
`;
}

function buildPlainTextNewsletter(book) {
  const buyLink = getBookLink(book.title) || book.buyLink || 'https://workbringsfreedom.com/shop.html';
  
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
${buyLink}

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

async function sendEmail(to, subject, htmlBody, textBody) {
  try {
    await transporter.sendMail({
      from: '"Work Brings Freedom" <dispatch@workbringsfreedom.com>',
      to: to,
      subject: subject,
      text: textBody,
      html: htmlBody
    });
    console.log(`  ✓ Sent to ${to}`);
    return true;
  } catch (err) {
    console.error(`  ✗ Failed to send to ${to}:`, err.message);
    return false;
  }
}

async function main() {
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
  
  const htmlBody = buildHTMLNewsletter(book);
  const textBody = buildPlainTextNewsletter(book);
  const subject = `📚 Banned Book of the Week: ${book.title}`;
  
  let sent = 0;
  let failed = 0;
  
  for (const sub of subscribers) {
    console.log(`Sending to ${sub.email}...`);
    if (await sendEmail(sub.email, subject, htmlBody, textBody)) {
      sent++;
    } else {
      failed++;
    }
    // Rate limit
    await new Promise(r => setTimeout(r, 2000));
  }
  
  console.log(`\nDone! Sent: ${sent}, Failed: ${failed}`);
}

main().catch(console.error);
