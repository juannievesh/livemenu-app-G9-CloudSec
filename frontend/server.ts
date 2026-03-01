import express from 'express';
import { createServer as createViteServer } from 'vite';
import Database from 'better-sqlite3';
import jwt from 'jsonwebtoken';
import multer from 'multer';
import cors from 'cors';
import path from 'path';
import fs from 'fs';
import QRCode from 'qrcode';

const app = express();
const PORT = 3000;
const JWT_SECRET = 'supersecretkey';

app.use(cors());
app.use(express.json());
app.use('/uploads', express.static(path.join(__dirname, 'uploads')));

// Ensure uploads dir exists
if (!fs.existsSync(path.join(__dirname, 'uploads'))) {
  fs.mkdirSync(path.join(__dirname, 'uploads'));
}

const db = new Database('database.sqlite');

// Init DB
db.exec(`
  CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE,
    password TEXT
  );
  CREATE TABLE IF NOT EXISTS restaurants (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    name TEXT,
    description TEXT,
    address TEXT,
    phone TEXT,
    slug TEXT UNIQUE
  );
  CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    restaurant_id INTEGER,
    name TEXT,
    description TEXT,
    sort_order INTEGER
  );
  CREATE TABLE IF NOT EXISTS dishes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category_id INTEGER,
    name TEXT,
    description TEXT,
    price REAL,
    offer_price REAL,
    available BOOLEAN DEFAULT 1,
    featured BOOLEAN DEFAULT 0,
    image_url TEXT
  );
`);

// Auth Middleware
const authenticate = (req: any, res: any, next: any) => {
  const authHeader = req.headers.authorization;
  if (!authHeader) return res.status(401).json({ error: 'No token provided' });
  const token = authHeader.split(' ')[1];
  try {
    const decoded = jwt.verify(token, JWT_SECRET);
    req.user = decoded;
    next();
  } catch (err) {
    res.status(401).json({ error: 'Invalid token' });
  }
};

// Auth Routes
app.post('/api/v1/auth/register', (req, res) => {
  const { email, password } = req.body;
  try {
    const stmt = db.prepare('INSERT INTO users (email, password) VALUES (?, ?)');
    const info = stmt.run(email, password);
    const token = jwt.sign({ id: info.lastInsertRowid, email }, JWT_SECRET);
    res.json({ token });
  } catch (err) {
    res.status(400).json({ error: 'Email already exists' });
  }
});

app.post('/api/v1/auth/login', (req, res) => {
  const { email, password } = req.body;
  const user = db.prepare('SELECT * FROM users WHERE email = ? AND password = ?').get(email, password) as any;
  if (user) {
    const token = jwt.sign({ id: user.id, email: user.email }, JWT_SECRET);
    res.json({ token });
  } else {
    res.status(401).json({ error: 'Invalid credentials' });
  }
});

// Restaurants Routes
app.get('/api/v1/restaurants', authenticate, (req: any, res) => {
  const restaurants = db.prepare('SELECT * FROM restaurants WHERE user_id = ?').all(req.user.id);
  res.json(restaurants);
});

app.post('/api/v1/restaurants', authenticate, (req: any, res) => {
  const { name, description, address, phone, slug } = req.body;
  const stmt = db.prepare('INSERT INTO restaurants (user_id, name, description, address, phone, slug) VALUES (?, ?, ?, ?, ?, ?)');
  const info = stmt.run(req.user.id, name, description, address, phone, slug);
  res.json({ id: info.lastInsertRowid });
});

app.put('/api/v1/restaurants/:id', authenticate, (req: any, res) => {
  const { name, description, address, phone, slug } = req.body;
  const stmt = db.prepare('UPDATE restaurants SET name = ?, description = ?, address = ?, phone = ?, slug = ? WHERE id = ? AND user_id = ?');
  stmt.run(name, description, address, phone, slug, req.params.id, req.user.id);
  res.json({ success: true });
});

app.delete('/api/v1/restaurants/:id', authenticate, (req: any, res) => {
  db.prepare('DELETE FROM restaurants WHERE id = ? AND user_id = ?').run(req.params.id, req.user.id);
  res.json({ success: true });
});

// Categories Routes
app.get('/api/v1/admin/categories', authenticate, (req: any, res) => {
  const { restaurant_id } = req.query;
  const categories = db.prepare('SELECT * FROM categories WHERE restaurant_id = ? ORDER BY sort_order').all(restaurant_id);
  res.json(categories);
});

app.post('/api/v1/admin/categories', authenticate, (req: any, res) => {
  const { restaurant_id, name, description, sort_order } = req.body;
  const stmt = db.prepare('INSERT INTO categories (restaurant_id, name, description, sort_order) VALUES (?, ?, ?, ?)');
  const info = stmt.run(restaurant_id, name, description, sort_order || 0);
  res.json({ id: info.lastInsertRowid });
});

app.put('/api/v1/admin/categories/:id', authenticate, (req: any, res) => {
  const { name, description } = req.body;
  db.prepare('UPDATE categories SET name = ?, description = ? WHERE id = ?').run(name, description, req.params.id);
  res.json({ success: true });
});

app.delete('/api/v1/admin/categories/:id', authenticate, (req: any, res) => {
  db.prepare('DELETE FROM categories WHERE id = ?').run(req.params.id);
  res.json({ success: true });
});

app.patch('/api/v1/admin/categories/reorder', authenticate, (req: any, res) => {
  const { order } = req.body; // array of { id, sort_order }
  const stmt = db.prepare('UPDATE categories SET sort_order = ? WHERE id = ?');
  const transaction = db.transaction((items) => {
    for (const item of items) stmt.run(item.sort_order, item.id);
  });
  transaction(order);
  res.json({ success: true });
});

// Dishes Routes
app.get('/api/v1/admin/dishes', authenticate, (req: any, res) => {
  const { category_id } = req.query;
  let query = 'SELECT * FROM dishes';
  let params: any[] = [];
  if (category_id) {
    query += ' WHERE category_id = ?';
    params.push(category_id);
  }
  const dishes = db.prepare(query).all(...params);
  res.json(dishes);
});

app.post('/api/v1/admin/dishes', authenticate, (req: any, res) => {
  const { category_id, name, description, price, offer_price, available, featured, image_url } = req.body;
  const stmt = db.prepare('INSERT INTO dishes (category_id, name, description, price, offer_price, available, featured, image_url) VALUES (?, ?, ?, ?, ?, ?, ?, ?)');
  const info = stmt.run(category_id, name, description, price, offer_price, available ? 1 : 0, featured ? 1 : 0, image_url);
  res.json({ id: info.lastInsertRowid });
});

app.put('/api/v1/admin/dishes/:id', authenticate, (req: any, res) => {
  const { category_id, name, description, price, offer_price, available, featured, image_url } = req.body;
  const stmt = db.prepare('UPDATE dishes SET category_id = ?, name = ?, description = ?, price = ?, offer_price = ?, available = ?, featured = ?, image_url = ? WHERE id = ?');
  stmt.run(category_id, name, description, price, offer_price, available ? 1 : 0, featured ? 1 : 0, image_url, req.params.id);
  res.json({ success: true });
});

app.delete('/api/v1/admin/dishes/:id', authenticate, (req: any, res) => {
  db.prepare('DELETE FROM dishes WHERE id = ?').run(req.params.id);
  res.json({ success: true });
});

app.patch('/api/v1/admin/dishes/:id/availability', authenticate, (req: any, res) => {
  const { available } = req.body;
  db.prepare('UPDATE dishes SET available = ? WHERE id = ?').run(available ? 1 : 0, req.params.id);
  res.json({ success: true });
});

// Upload Route
const upload = multer({ dest: 'uploads/' });
app.post('/api/v1/admin/upload', authenticate, upload.single('file'), (req: any, res) => {
  const { dish_id } = req.body;
  const file = req.file;
  if (!file) return res.status(400).json({ error: 'No file uploaded' });
  const imageUrl = \`/uploads/\${file.filename}\`;
  if (dish_id) {
    db.prepare('UPDATE dishes SET image_url = ? WHERE id = ?').run(imageUrl, dish_id);
  }
  res.json({ image_url: imageUrl });
});

// QR Route
app.get('/api/v1/admin/qr', authenticate, async (req: any, res) => {
  const { format = 'png', size = 'M', url = 'https://livemenu.com/demo' } = req.query;
  const sizeMap: any = { S: 300, M: 500, L: 1000, XL: 2000 };
  const width = sizeMap[size as string] || 500;
  
  try {
    if (format === 'svg') {
      const svg = await QRCode.toString(url, { type: 'svg', width });
      res.type('svg').send(svg);
    } else {
      const buffer = await QRCode.toBuffer(url, { width });
      res.type('png').send(buffer);
    }
  } catch (err) {
    res.status(500).json({ error: 'Failed to generate QR code' });
  }
});

async function startServer() {
  if (process.env.NODE_ENV !== 'production') {
    const vite = await createViteServer({
      server: { middlewareMode: true },
      appType: 'spa',
    });
    app.use(vite.middlewares);
  } else {
    app.use(express.static('dist'));
    app.get('*', (req, res) => {
      res.sendFile(path.resolve(__dirname, 'dist', 'index.html'));
    });
  }

  app.listen(PORT, '0.0.0.0', () => {
    console.log(\`Server running on http://localhost:\${PORT}\`);
  });
}

startServer();
