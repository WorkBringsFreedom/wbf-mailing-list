const fs = require('fs');
const path = require('path');

// Read current shop.html
const shopPath = path.join(__dirname, 'shop.html');
const current = fs.readFileSync(shopPath, 'utf8');

// Read new books
const newBooks = JSON.parse(fs.readFileSync(path.join(__dirname, 'books-100.json'), 'utf8'));

// Extract existing PRODUCTS array content
const startIdx = current.indexOf('const PRODUCTS = [');
const endIdx = current.indexOf('];\n\nlet activeFilter');
if (startIdx === -1 || endIdx === -1) {
  console.error('Could not find PRODUCTS array boundaries');
  process.exit(1);
}

const existingBlock = current.slice(startIdx, endIdx + 2);

// Parse existing using a quick eval in a safe way
const existingMatch = existingBlock.match(/const PRODUCTS = ([\s\S]*?)\];/);
if (!existingMatch) {
  console.error('Could not extract array');
  process.exit(1);
}

// Use Function constructor to safely eval the JS array
let existing;
try {
  existing = new Function('return ' + existingMatch[1] + ']')();
} catch(e) {
  console.error('Failed to eval existing:', e.message);
  process.exit(1);
}

console.log('Existing books:', existing.length);
console.log('New books:', newBooks.length);

// Combine
const allBooks = [...existing, ...newBooks];
console.log('Total books:', allBooks.length);

// Build PRODUCTS array string
const prodStr = 'const PRODUCTS = [\n' + allBooks.map(b => {
  const fields = [];
  fields.push(`  id:${b.id}`);
  fields.push(`title:"${b.title.replace(/"/g, '\\"')}"`);
  fields.push(`author:"${b.author.replace(/"/g, '\\"')}"`);
  fields.push(`year:${b.year}`);
  fields.push(`cat:"${b.cat}"`);
  fields.push(`price:${b.price.toFixed(2)}`);
  if (b.coverImage) fields.push(`coverImage:"${b.coverImage}"`);
  if (b.freeLink) fields.push(`freeLink:"${b.freeLink}"`);
  fields.push(`buyLink:"${b.buyLink}"`);
  fields.push(`blurb:"${b.blurb.replace(/"/g, '\\"')}"`);
  fields.push(`reason:"${b.reason.replace(/"/g, '\\"')}"`);
  return '  { ' + fields.join(', ') + ' }';
}).join(',\n') + '\n];';

// Replace PRODUCTS in shop.html
let newHtml = current.slice(0, startIdx) + prodStr + current.slice(endIdx + 2);

// Update header text
newHtml = newHtml.replace(/16 forbidden books they didn't want you to read/, '116 forbidden books they didn\'t want you to read');
newHtml = newHtml.replace(/The Library/, 'The Library');

fs.writeFileSync(shopPath, newHtml);
console.log('shop.html updated successfully');

// Also update the JSON reference
fs.writeFileSync(path.join(__dirname, 'books-100.json'), JSON.stringify(newBooks, null, 2));
console.log('books-100.json updated');
