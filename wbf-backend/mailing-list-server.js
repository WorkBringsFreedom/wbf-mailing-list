const http = require('http');
const url = require('url');
const { MongoClient } = require('mongodb');

const PORT = process.env.PORT || 3456;
const MONGODB_URI = process.env.MONGODB_URI || 'mongodb+srv://workbringsfreedom_db_user:hItvyjfwzKFhKgr5@openclaw.ch8upzs.mongodb.net/wbf?retryWrites=true&w=majority';
const ALLOWED_ORIGINS = (process.env.ALLOWED_ORIGINS || 'http://localhost:3000,http://127.0.0.1:3000').split(',');

let db = null;
let client = null;

// Connect to MongoDB
async function connectDB() {
  if (db) return db;
  if (!MONGODB_URI) {
    console.error('ERROR: MONGODB_URI not set');
    process.exit(1);
  }
  client = new MongoClient(MONGODB_URI, { maxPoolSize: 10 });
  await client.connect();
  db = client.db('wbf');
  console.log('Connected to MongoDB Atlas');
  return db;
}

// Simple email validation
function isValidEmail(email) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

// CORS headers helper
function setCORS(res, origin) {
  if (origin && ALLOWED_ORIGINS.includes(origin)) {
    res.setHeader('Access-Control-Allow-Origin', origin);
  } else {
    res.setHeader('Access-Control-Allow-Origin', '*');
  }
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
}

const server = http.createServer(async (req, res) => {
  const parsed = url.parse(req.url, true);
  const origin = req.headers.origin;
  
  setCORS(res, origin);
  
  if (req.method === 'OPTIONS') {
    res.writeHead(200);
    res.end();
    return;
  }
  
  try {
    await connectDB();
  } catch (err) {
    console.error('MongoDB connection failed:', err.message);
    res.writeHead(500, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ error: 'Database unavailable' }));
    return;
  }
  
  // Health check
  if (parsed.pathname === '/health') {
    const subsCount = await db.collection('subscribers').countDocuments();
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ status: 'ok', subscribers: subsCount }));
    return;
  }
  
  // Subscribe endpoint
  if (parsed.pathname === '/subscribe' && req.method === 'POST') {
    let body = '';
    req.on('data', chunk => body += chunk);
    req.on('end', async () => {
      try {
        const data = JSON.parse(body);
        const email = data.email?.trim().toLowerCase();
        
        if (!email || !isValidEmail(email)) {
          res.writeHead(400, { 'Content-Type': 'application/json' });
          res.end(JSON.stringify({ error: 'Invalid email address' }));
          return;
        }
        
        // Check for duplicates
        const existing = await db.collection('subscribers').findOne({ email });
        if (existing) {
          res.writeHead(409, { 'Content-Type': 'application/json' });
          res.end(JSON.stringify({ error: 'Email already subscribed' }));
          return;
        }
        
        await db.collection('subscribers').insertOne({
          email,
          name: data.name || '',
          address: data.address || '',
          genre: data.genre || 'any',
          subscribedAt: new Date().toISOString(),
          source: data.source || 'WBF2'
        });
        
        const total = await db.collection('subscribers').countDocuments();
        
        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ 
          success: true, 
          message: 'Subscribed successfully',
          subscribers: total 
        }));
        
      } catch (err) {
        console.error('Subscribe error:', err.message);
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
    const subs = await db.collection('subscribers').find().toArray();
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ 
      count: subs.length,
      subscribers: subs 
    }));
    return;
  }
  
  // Stats endpoint
  if (parsed.pathname === '/stats' && req.method === 'GET') {
    const subsCount = await db.collection('subscribers').countDocuments();
    const downloadsCol = db.collection('downloads');
    const totalDownloads = await downloadsCol.aggregate([
      { $group: { _id: null, total: { $sum: '$count' } } }
    ]).toArray();
    
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ 
      subscribers: subsCount,
      totalDownloads: totalDownloads[0]?.total || 0,
      books: 115,
      collections: 5
    }));
    return;
  }
  
  // Reset endpoint - clear all subscribers
  if (parsed.pathname === '/reset' && req.method === 'POST') {
    const secretKey = parsed.query.key;
    if (secretKey !== process.env.ADMIN_KEY) {
      res.writeHead(403, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ error: 'Forbidden' }));
      return;
    }
    await db.collection('subscribers').deleteMany({});
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ success: true, message: 'All subscribers cleared' }));
    return;
  }

  // POST /download?book=1984
  if (parsed.pathname === '/download' && req.method === 'POST') {
    const book = parsed.query.book || 'unknown';
    await db.collection('downloads').updateOne(
      { book },
      { $inc: { count: 1 }, $setOnInsert: { book } },
      { upsert: true }
    );
    const doc = await db.collection('downloads').findOne({ book });
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ success: true, book, downloads: doc?.count || 1 }));
    return;
  }

  // GET /stats/downloads
  if (parsed.pathname === '/stats/downloads' && req.method === 'GET') {
    const top = await db.collection('downloads')
      .find()
      .sort({ count: -1 })
      .limit(10)
      .project({ _id: 0, book: 1, count: 1 })
      .toArray();
    
    // Format as [[book, count], ...] to match original API
    const formatted = top.map(d => [d.book, d.count]);
    
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ top: formatted }));
    return;
  }

  // 404
  res.writeHead(404, { 'Content-Type': 'application/json' });
  res.end(JSON.stringify({ error: 'Not found' }));
});

server.listen(PORT, () => {
  console.log(`WBF mailing list server running on port ${PORT}`);
  console.log(`Using MongoDB Atlas for persistent storage`);
});

// Graceful shutdown
process.on('SIGTERM', async () => {
  console.log('SIGTERM received, closing MongoDB connection...');
  if (client) await client.close();
  process.exit(0);
});
