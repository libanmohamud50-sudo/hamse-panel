require('dotenv').config();
const express = require('express');
const cors = require('cors');
const bodyParser = require('body-parser');
const path = require('path');
const fs = require('fs');
const jwt = require('jsonwebtoken');
const bcrypt = require('bcryptjs');
const initSqlJs = require('sql.js');

const app = express();
const PORT = process.env.PORT || 3000;
const JWT_SECRET = process.env.JWT_SECRET || 'HAMSE_VIP_SECRET_2026';
const ADMIN_USERNAME = process.env.ADMIN_USERNAME || 'hamsecheatsvip';
const ADMIN_PASSWORD = process.env.ADMIN_PASSWORD || 'Hamse@2026VIP';

app.use(cors());
app.use(bodyParser.json({ limit: '10mb' }));
app.use(bodyParser.urlencoded({ extended: true }));
app.use(express.static(path.join(__dirname, 'public')));

let db;
const DB_FILE = path.join(__dirname, 'hamse_vip.db');

async function initDB() {
  const SQL = await initSqlJs();
  if (fs.existsSync(DB_FILE)) {
    db = new SQL.Database(fs.readFileSync(DB_FILE));
  } else {
    db = new SQL.Database();
  }
  db.run("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE NOT NULL, password TEXT NOT NULL, fullname TEXT, role TEXT DEFAULT 'user', license_key TEXT, referral_code TEXT UNIQUE, referred_by TEXT, status TEXT DEFAULT 'active', created_at DATETIME DEFAULT CURRENT_TIMESTAMP)");
  db.run("CREATE TABLE IF NOT EXISTS licenses (id INTEGER PRIMARY KEY AUTOINCREMENT, license_key TEXT UNIQUE NOT NULL, user_id INTEGER, device_id TEXT, duration TEXT, expires_at DATETIME, status TEXT DEFAULT 'unused', used_at DATETIME)");
  db.run("CREATE TABLE IF NOT EXISTS referrals (id INTEGER PRIMARY KEY AUTOINCREMENT, referrer_code TEXT, referred_user TEXT, created_at DATETIME DEFAULT CURRENT_TIMESTAMP)");
  const adminExists = db.exec("SELECT id FROM users WHERE username = '" + ADMIN_USERNAME + "'");
  if (!adminExists.length || !adminExists[0].values.length) {
    const hashedPassword = bcrypt.hashSync(ADMIN_PASSWORD, 10);
    const adminRefCode = 'HAMSE' + Math.floor(1000 + Math.random() * 9000);
    db.run("INSERT INTO users (username, password, fullname, role, referral_code, status) VALUES (?, ?, ?, 'admin', ?, 'active')", [ADMIN_USERNAME, hashedPassword, 'Hamse Admin', adminRefCode]);
    console.log('Admin account created: ' + ADMIN_USERNAME);
  }
  saveDB();
  console.log('Database initialized');
}

function saveDB() {
  fs.writeFileSync(DB_FILE, Buffer.from(db.export()));
}

function queryAll(sql, params) {
  params = params || [];
  const stmt = db.prepare(sql);
  stmt.bind(params);
  const rows = [];
  while (stmt.step()) rows.push(stmt.getAsObject());
  stmt.free();
  return rows;
}

function queryOne(sql, params) {
  const rows = queryAll(sql, params);
  return rows[0] || null;
}

function authMiddleware(req, res, next) {
  const authHeader = req.headers['authorization'];
  const token = authHeader && authHeader.split(' ')[1];
  if (!token) return res.status(401).json({ error: 'Token ma jiro' });
  try { req.user = jwt.verify(token, JWT_SECRET); next(); }
  catch (err) { return res.status(401).json({ error: 'Token khaldan' }); }
}

function adminMiddleware(req, res, next) {
  if (req.user.role !== 'admin') return res.status(403).json({ error: 'Admin kaliya' });
  next();
}

app.get('/api/health', (req, res) => res.json({ status: 'ok', panel: 'HAMSE CHEATS VIP PANEL', time: new Date().toISOString() }));
app.get('/api/worker-check', (req, res) => res.json({ status: 'online', worker: 'cloudflare', time: new Date().toISOString() }));

app.post('/api/register', (req, res) => {
  const { username, password, fullname, referral_code } = req.body;
  if (!username || !password) return res.status(400).json({ error: 'Username iyo password waa loo baahan yahay' });
  if (!referral_code) return res.status(400).json({ error: 'Referral code waa loo baahan yahay' });
  const referrer = queryOne('SELECT * FROM users WHERE referral_code = ?', [referral_code]);
  if (!referrer) return res.status(400).json({ error: 'Referral code khaldan' });
  if (queryOne('SELECT id FROM users WHERE username = ?', [username])) return res.status(400).json({ error: 'Username hore ayaa loo qaatay' });
  const hashedPassword = bcrypt.hashSync(password, 10);
  const newRefCode = 'HAMSE' + Math.floor(1000 + Math.random() * 9000);
  db.run("INSERT INTO users (username, password, fullname, role, referral_code, referred_by, status) VALUES (?, ?, ?, 'user', ?, ?, 'active')", [username, hashedPassword, fullname || username, newRefCode, referral_code]);
  db.run("INSERT INTO referrals (referrer_code, referred_user) VALUES (?, ?)", [referral_code, username]);
  saveDB();
  res.json({ success: true, message: 'Isdiiwaangelinta guuleystay', referral_code: newRefCode });
});

app.post('/api/login', (req, res) => {
  const { username, password } = req.body;
  if (!username || !password) return res.status(400).json({ error: 'Username iyo password waa loo baahan yahay' });
  const user = queryOne('SELECT * FROM users WHERE username = ?', [username]);
  if (!user) return res.status(400).json({ error: 'Username ama password khaldan' });
  if (user.status === 'banned') return res.status(403).json({ error: 'Account-kaaga waa la xannibay' });
  if (!bcrypt.compareSync(password, user.password)) return res.status(400).json({ error: 'Username ama password khaldan' });
  const token = jwt.sign({ id: user.id, username: user.username, role: user.role }, JWT_SECRET, { expiresIn: '7d' });
  res.json({ success: true, token, user: { id: user.id, username: user.username, fullname: user.fullname, role: user.role, referral_code: user.referral_code, license_key: user.license_key, status: user.status, created_at: user.created_at } });
});

app.get('/api/stats', authMiddleware, (req, res) => {
  res.json({
    totalUsers: queryOne('SELECT COUNT(*) as c FROM users').c,
    totalLicenses: queryOne('SELECT COUNT(*) as c FROM licenses').c,
    activeLicenses: queryOne("SELECT COUNT(*) as c FROM licenses WHERE status = 'active'").c,
    totalReferrals: queryOne('SELECT COUNT(*) as c FROM referrals').c,
    bannedUsers: queryOne("SELECT COUNT(*) as c FROM users WHERE status = 'banned'").c
  });
});

app.get('/api/admin/users', authMiddleware, adminMiddleware, (req, res) => {
  res.json({ users: queryAll('SELECT id, username, fullname, role, license_key, referral_code, referred_by, status, created_at FROM users ORDER BY id DESC') });
});

app.put('/api/admin/users/:id', authMiddleware, adminMiddleware, (req, res) => {
  const { role, status } = req.body;
  const user = queryOne('SELECT * FROM users WHERE id = ?', [req.params.id]);
  if (!user) return res.status(404).json({ error: 'User lama helin' });
  if (role) db.run('UPDATE users SET role = ? WHERE id = ?', [role, req.params.id]);
  if (status) db.run('UPDATE users SET status = ? WHERE id = ?', [status, req.params.id]);
  saveDB();
  res.json({ success: true, message: 'User la cusboonaysiiyay' });
});

app.delete('/api/admin/users/:id', authMiddleware, adminMiddleware, (req, res) => {
  db.run('DELETE FROM users WHERE id = ?', [req.params.id]);
  saveDB();
  res.json({ success: true, message: 'User la tirtiray' });
});

app.post('/api/admin/licenses/bulk', authMiddleware, adminMiddleware, (req, res) => {
  const count = req.body.count || 1;
  const duration = req.body.duration || '30d';
  const created = [];
  for (let i = 0; i < count; i++) {
    const key = 'HAMSE-' + Math.random().toString(36).substring(2, 8).toUpperCase() + '-' + Math.random().toString(36).substring(2, 8).toUpperCase();
    db.run("INSERT INTO licenses (license_key, duration, status) VALUES (?, ?, 'unused')", [key, duration]);
    created.push(key);
  }
  saveDB();
  res.json({ success: true, count: created.length, licenses: created });
});

app.get('/api/licenses', authMiddleware, (req, res) => {
  res.json({ licenses: queryAll('SELECT * FROM licenses ORDER BY id DESC') });
});

app.delete('/api/admin/licenses/:id', authMiddleware, adminMiddleware, (req, res) => {
  db.run('DELETE FROM licenses WHERE id = ?', [req.params.id]);
  saveDB();
  res.json({ success: true, message: 'License la tirtiray' });
});

app.get('/api/admin/referrals', authMiddleware, adminMiddleware, (req, res) => {
  res.json({ referrals: queryAll('SELECT * FROM referrals ORDER BY id DESC') });
});

app.get('*', (req, res) => res.sendFile(path.join(__dirname, 'public', 'index.html')));

initDB().then(() => {
  app.listen(PORT, () => {
    console.log('HAMSE CHEATS VIP PANEL socda port ' + PORT);
    console.log('Admin: ' + ADMIN_USERNAME);
  });
}).catch(err => console.error('DB init error:', err));
