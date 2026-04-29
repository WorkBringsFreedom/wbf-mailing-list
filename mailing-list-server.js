const http = require('http');
const fs = require('fs');
const path = require('path');
const url = require('url');

const DATA_FILE = path.join(__dirname, 'subscribers.json');
const PORT = process.env.PORT || 3456;
const ALLOWED_ORIGINS = (process.env.ALLOWED_ORIGINS || 'http://localhost:3000,http://127.0.0.1:3000').split(',');

// Load existing subscribers
function loadSubscribers() {
  try {
    const data = fs.readFileSync(DATA_FILE, 'utf8');
    return JSON.parse(data);
  } catch {
    return [];
  }
}

// Save subscribers
function saveSubscribers(subs) {
  fs.writeFileSync(DATA_FILE, JSON.stringify(subs, null, 2));
}

// Simple email validation
function isValidEmail(email) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

const server = http.createServer((req, res) => {
  const parsed = url.parse(req.url, true);
  const origin = req.headers.origin;
  
  // CORS headers
  if (origin && ALLOWED_ORIGINS.includes(origin)) {
    res.setHeader('Access-Control-Allow-Origin', origin);
  } else {
    res.setHeader('Access-Control-Allow-Origin', '*');
  }
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  
  if (req.method === 'OPTIONS') {
    res.writeHead(200);
    res.end();
    return;
  }
  
  // Health check
  if (parsed.pathname === '/health') {
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ status: 'ok', subscribers: loadSubscribers().length }));
    return;
  }
  
  // Subscribe endpoint
  if (parsed.pathname === '/subscribe' && req.method === 'POST') {
    let body = '';
    req.on('data', chunk => body += chunk);
    req.on('end', () => {
      try {
        const data = JSON.parse(body);
        const email = data.email?.trim().toLowerCase();
        
        if (!email || !isValidEmail(email)) {
          res.writeHead(400, { 'Content-Type': 'application/json' });
          res.end(JSON.stringify({ error: 'Invalid email address' }));
          return;
        }
        
        const subscribers = loadSubscribers();
        
        // Check for duplicates
        if (subscribers.some(s => s.email === email)) {
          res.writeHead(409, { 'Content-Type': 'application/json' });
          res.end(JSON.stringify({ error: 'Email already subscribed' }));
          return;
        }
        
        subscribers.push({
          email,
          name: data.name || '',
          address: data.address || '',
          genre: data.genre || 'any',
          subscribedAt: new Date().toISOString(),
          source: data.source || 'WBF2'
        });
        
        saveSubscribers(subscribers);
        
        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ 
          success: true, 
          message: 'Subscribed successfully',
          subscribers: subscribers.length 
        }));
        
      } catch (err) {
        res.writeHead(500, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ error: 'Server error' }));
      }
    });
    return;
  }
  
  // Get subscribers (protected - require secret key)
  if (parsed.pathname === '/subscribers' && req.method === 'GET') {
    const secretKey = parsed.query.key;
    if (secretKey !== process.env.ADMIN_KEY) {
      res.writeHead(403, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ error: 'Forbidden' }));
      return;
    }
    const subs = loadSubscribers();
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ 
      count: subs.length,
      subscribers: subs 
    }));
    return;
  }
  
// Stats endpoint
  if (parsed.pathname === '/stats' && req.method === 'GET') {
    // Count collections from collections.html
    let collections = 5;
    try {
      const collectionsHtml = fs.readFileSync(path.join(__dirname, 'collections.html'), 'utf8');
      const matches = collectionsHtml.match(/<section class="collection"/g);
      if (matches) collections = matches.length;
    } catch (e) {
      // fallback to 5
    }
    
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ 
      books: 115,
      collections: collections
    }));
    return;
  }
  
  // Not found
  // Reset endpoint - clear all subscribers
  if (parsed.pathname === '/reset' && req.method === 'POST') {
    const secretKey = parsed.query.key;
    if (secretKey !== 'RESET123') {
      res.writeHead(403, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ error: 'Forbidden' }));
      return;
    }
    saveSubscribers([]);
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ success: true, message: 'All subscribers cleared' }));
    return;
  }

  // 404
  res.writeHead(404, { 'Content-Type': 'application/json' });
  res.end(JSON.stringify({ error: 'Not found' }));
});

server.listen(PORT, () => {
  console.log(`WBF mailing list server running on port ${PORT}`);
  console.log(`Subscribers stored in: ${DATA_FILE}`);
});

