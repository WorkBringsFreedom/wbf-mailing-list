const fs = require('fs');
const path = require('path');

const shopPath = path.join(__dirname, 'shop.html');
const current = fs.readFileSync(shopPath, 'utf8');
const newBooks = JSON.parse(fs.readFileSync(path.join(__dirname, 'books-100.json'), 'utf8'));

// Extract existing 16 books from current shop.html
const startIdx = current.indexOf('const PRODUCTS = [');
const endIdx = current.indexOf('];\n\nlet activeFilter');
const existingBlock = current.slice(startIdx, endIdx + 2);
const existingMatch = existingBlock.match(/const PRODUCTS = ([\s\S]*?)\];/);
const existing = new Function('return ' + existingMatch[1] + ']')();
const orig16 = existing.slice(0, 16);

console.log('Original books:', orig16.length);
console.log('New books:', newBooks.length);

const allBooks = [...orig16, ...newBooks];
console.log('Total:', allBooks.length);

function esc(s) {
  return s.replace(/\\/g, '\\\\').replace(/"/g, '\\"').replace(/\n/g, '\\n');
}

const prodStr = 'const PRODUCTS = [\n' + allBooks.map(b => {
  const fields = [];
  fields.push(`id:${b.id}`);
  fields.push(`title:"${esc(b.title)}"`);
  fields.push(`author:"${esc(b.author)}"`);
  fields.push(`year:${b.year}`);
  fields.push(`cat:"${b.cat}"`);
  fields.push(`price:${b.price.toFixed(2)}`);
  if (b.coverImage) fields.push(`coverImage:"${b.coverImage}"`);
  if (b.freeLink) fields.push(`freeLink:"${b.freeLink}"`);
  fields.push(`buyLink:"${b.buyLink}"`);
  fields.push(`blurb:"${esc(b.blurb)}"`);
  fields.push(`reason:"${esc(b.reason)}"`);
  return '  { ' + fields.join(', ') + ' }';
}).join(',\n') + '\n];';

let newHtml = current.slice(0, startIdx) + prodStr + current.slice(endIdx + 2);
newHtml = newHtml.replace(/16 forbidden books/, '116 forbidden books');

fs.writeFileSync(shopPath, newHtml);
console.log('shop.html rebuilt successfully');
