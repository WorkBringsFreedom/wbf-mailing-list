const express = require('express');
const cors = require('cors');
const fs = require('fs');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 3000;
const DATA_FILE = path.join(__dirname, 'subscribers.json');

app.use(cors());
app.use(express.json());

// Ensure subscribers file exists
if (!fs.existsSync(DATA_FILE)) {
  fs.writeFileSync(DATA_FILE, JSON.stringify([], null, 2));
}

function loadSubscribers() {
  try {
    return JSON.parse(fs.readFileSync(DATA_FILE, 'utf8'));
  } catch {
    return [];
  }
}

function saveSubscribers(subs) {
  fs.writeFileSync(DATA_FILE, JSON.stringify(subs, null, 2));
}

// Health check
app.get('/', (req, res) => {
  res.json({ status: 'WBF mailing list API running' });
});

// Subscribe
app.post('/subscribe', (req, res) => {
  const { name, email, genre } = req.body;

  if (!email || !email.includes('@')) {
    return res.status(400).json({ error: 'valid email required' });
  }

  const subscribers = loadSubscribers();

  if (subscribers.some(s => s.email.toLowerCase() === email.toLowerCase())) {
    return res.status(409).json({ error: 'email already subscribed' });
  }

  const entry = {
    id: Date.now().toString(36) + Math.random().toString(36).slice(2, 6),
    name: (name || 'anon').trim(),
    email: email.trim().toLowerCase(),
    genre: genre || 'any',
    subscribedAt: new Date().toISOString()
  };

  subscribers.push(entry);
  saveSubscribers(subscribers);

  res.json({ success: true, id: entry.id });
});

// List all subscribers (protected by secret key)
app.get('/subscribers', (req, res) => {
  const key = req.headers['x-api-key'];
  if (key !== process.env.ADMIN_KEY) {
    return res.status(401).json({ error: 'unauthorized' });
  }
  res.json(loadSubscribers());
});

app.listen(PORT, () => {
  console.log(`WBF API listening on port ${PORT}`);
});
