const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const DATA_FILE = path.join(__dirname, 'subscribers.json');
const EXPORT_DIR = path.join(__dirname, 'exports');

// Ensure exports directory exists
if (!fs.existsSync(EXPORT_DIR)) {
  fs.mkdirSync(EXPORT_DIR, { recursive: true });
}

// Load subscribers
let subscribers = [];
try {
  const data = fs.readFileSync(DATA_FILE, 'utf8');
  subscribers = JSON.parse(data);
} catch (err) {
  console.log('No subscribers yet or file missing');
  process.exit(0);
}

if (subscribers.length === 0) {
  console.log('No subscribers to export');
  process.exit(0);
}

// Generate CSV
const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
const filename = `subscribers-${timestamp}.csv`;
const filepath = path.join(EXPORT_DIR, filename);

// CSV header
const csvLines = ['Email,Subscribed At,Source'];

// CSV rows
subscribers.forEach(sub => {
  const email = sub.email || '';
  const date = sub.subscribedAt || '';
  const source = sub.source || 'join.html';
  csvLines.push(`"${email}","${date}","${source}"`);
});

fs.writeFileSync(filepath, csvLines.join('\n'));
console.log(`Exported ${subscribers.length} subscribers to ${filepath}`);

// Email the CSV using himalaya if available
try {
  const himalayaPath = execSync('which himalaya', { encoding: 'utf8' }).trim();
  if (himalayaPath) {
    console.log('Himalaya found, attempting to send email...');
    // Note: This would need proper himalaya configuration
    // For now, just log that we would send it
    console.log(`Would email ${filepath} to dispatch@workbringsfreedom.com`);
  }
} catch {
  console.log('Himalaya not found in PATH');
}

console.log('Export complete');
