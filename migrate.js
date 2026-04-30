const { MongoClient } = require('mongodb');
const fs = require('fs');
const path = require('path');

const MONGODB_URI = process.env.MONGODB_URI;

async function migrate() {
  if (!MONGODB_URI) {
    console.error('Set MONGODB_URI env var first');
    process.exit(1);
  }

  const client = new MongoClient(MONGODB_URI);
  await client.connect();
  const db = client.db('wbf');

  // Migrate subscribers
  const subsFile = path.join(__dirname, 'subscribers.json');
  if (fs.existsSync(subsFile)) {
    const subs = JSON.parse(fs.readFileSync(subsFile, 'utf8'));
    if (subs.length > 0) {
      await db.collection('subscribers').deleteMany({});
      await db.collection('subscribers').insertMany(subs);
      console.log(`Migrated ${subs.length} subscribers`);
    }
  }

  // Migrate downloads
  const dlFile = path.join(__dirname, 'downloads.json');
  if (fs.existsSync(dlFile)) {
    const downloads = JSON.parse(fs.readFileSync(dlFile, 'utf8'));
    const docs = Object.entries(downloads).map(([book, count]) => ({ book, count }));
    if (docs.length > 0) {
      await db.collection('downloads').deleteMany({});
      await db.collection('downloads').insertMany(docs);
      console.log(`Migrated ${docs.length} download records`);
    }
  }

  console.log('Migration complete');
  await client.close();
}

migrate().catch(console.error);
