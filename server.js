require('dotenv').config();
const express = require('express');
const cors = require('cors');
const bodyParser = require('body-parser');
const path = require('path');
const fs = require('fs');
const jwt = require('jsonwebtoken');
const bcrypt = require('bcryptjs');
const crypto = require('crypto');
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
    try {
      const buf = fs.readFileSync(DB_FILE);
      db = new SQL.Database(buf);
      console.log('DB loaded: ' + buf.length + ' bytes');
      const test = db.exec("SELECT COUNT(*) FROM licenses");
      console.log('Licenses: ' + (test[0] ? test[0].values[0][0] : 0));
      return;
    } catch(e) { console.log('loadDB error: ' + e.message); }
  }
  db = new SQL.Database();
  db.run("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE NOT NULL, password TEXT NOT NULL, fullname TEXT, role TEXT DEFAULT 'user', license_key TEXT, referral_code TEXT UNIQUE, referred_by TEXT, status TEXT DEFAULT 'active', created_at DATETIME DEFAULT CURRENT_TIMESTAMP)");
  db.run("CREATE TABLE IF NOT EXISTS licenses (id INTEGER PRIMARY KEY AUTOINCREMENT, license_key TEXT UNIQUE NOT NULL, user_id INTEGER, device_id TEXT, serial TEXT, max_devices INTEGER DEFAULT 1, used_devices TEXT DEFAULT '[]', duration TEXT, expires_at DATETIME, game TEXT, status TEXT DEFAULT 'unused', used_at DATETIME)");
  try { db.run("ALTER TABLE licenses ADD COLUMN serial TEXT"); } catch (e) {}
  try { db.run("ALTER TABLE licenses ADD COLUMN max_devices INTEGER DEFAULT 1"); } catch (e) {}
  try { db.run("ALTER TABLE licenses ADD COLUMN used_devices TEXT DEFAULT '[]'"); } catch (e) {}
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


function loadDB() {
  try {
    if (fs.existsSync(DB_FILE)) {
      const buf = fs.readFileSync(DB_FILE);
      db = new SQL.Database(buf);
      console.log('DB loaded: ' + buf.length + ' bytes');
    }
  } catch(e) {
    console.log('loadDB error: ' + e.message);
  }
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


function calcExpiry(hours) {
  if (!hours || hours === 0 || hours === '0' || hours === 'lifetime') return '2099-12-31 23:59:59';
  const h = parseInt(hours);
  if (isNaN(h)) return '2099-12-31 23:59:59';
  const d = new Date(Date.now() + h * 3600 * 1000);
  const pad = n => String(n).padStart(2, '0');
  return d.getFullYear() + '-' + pad(d.getMonth()+1) + '-' + pad(d.getDate()) + ' ' + pad(d.getHours()) + ':' + pad(d.getMinutes()) + ':' + pad(d.getSeconds());
}

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

app.post("/api/admin/licenses/bulk", authMiddleware, adminMiddleware, (req, res) => {
  const count = req.body.count || 1;
  const duration = req.body.duration || '30d';
  const custom_key = (req.body.custom_key || '').trim();
  const max_devices = parseInt(req.body.max_devices) || 1;
  const game = req.body.game || 'PUBG MOBILE';
  const keyMode = req.body.key_mode || (custom_key ? 'custom' : 'auto');
  const created = [];
  var now = new Date();
  var ms = 0;
  if (duration === '30m') ms = 30 * 60 * 1000;
  else if (duration === '1h') ms = 60 * 60 * 1000;
  else if (duration === '2h') ms = 2 * 60 * 60 * 1000;
  else if (duration === '6h') ms = 6 * 60 * 60 * 1000;
  else if (duration === '12h') ms = 12 * 60 * 60 * 1000;
  else if (duration === '1d') ms = 24 * 60 * 60 * 1000;
  else if (duration === '7d') ms = 7 * 24 * 60 * 60 * 1000;
  else if (duration === '30d') ms = 30 * 24 * 60 * 60 * 1000;
  else if (duration === '90d') ms = 90 * 24 * 60 * 60 * 1000;
  else if (duration === '365d') ms = 365 * 24 * 60 * 60 * 1000;
  else ms = 30 * 24 * 60 * 60 * 1000;
  var durationLabel = duration === 'lifetime' ? 'lifetime' : (duration === '30m' ? '30mins' : duration === '1h' ? '1hour' : duration === '2h' ? '2hours' : duration === '6h' ? '6hours' : duration === '12h' ? '12hours' : duration === '1d' ? '1day' : duration === '7d' ? '7days' : duration === '30d' ? '30days' : duration === '90d' ? '90days' : duration === '365d' ? '1year' : '30days');
  for (let i = 0; i < count; i++) {
    let key;
    if (keyMode === 'custom' && custom_key) {
      key = custom_key.toUpperCase();
    } else {
      key = durationLabel + '-HAMSE-' + Math.random().toString(36).substring(2, 8).toUpperCase() + '-' + Math.random().toString(36).substring(2, 8).toUpperCase();
    }
    var expiresAt;
    if (duration === 'lifetime') {
      expiresAt = '2099-12-31 23:59:59';
    } else {
      var exp = new Date(now.getTime() + ms);
      expiresAt = exp.toISOString().replace('T', ' ').substring(0, 19);
    }
    try {
      db.run("INSERT INTO licenses (license_key, duration, max_devices, status, expires_at, game) VALUES (?, ?, ?, 'unused', ?, ?)", [key, duration, max_devices, expiresAt, game]);
      created.push({ key: key, game: game, max_devices: max_devices, expires_at: expiresAt });
    } catch(e) {
      created.push({ error: e.message, key: key });
    }
  }
  saveDB();
  res.json({ success: true, count: created.length, licenses: created });
});
app.get('/api/licenses', authMiddleware, (req, res) => {
  res.json({ licenses: queryAll('SELECT * FROM licenses ORDER BY id DESC') });
});

app.put('/api/admin/licenses/:id/edit', authMiddleware, adminMiddleware, (req, res) => {
  const max_devices = parseInt(req.body.max_devices);
  if (!max_devices || max_devices < 1) return res.status(400).json({ success: false, error: 'max_devices waa inuu ka weyn yahay 0' });
  try {
    db.run('UPDATE licenses SET max_devices = ? WHERE id = ?', [max_devices, req.params.id]);
    saveDB();
    res.json({ success: true, message: 'Max devices la beddelay' });
  } catch(e) {
    res.status(500).json({ success: false, error: e.message });
  }
});

app.delete('/api/admin/licenses/:id', authMiddleware, adminMiddleware, (req, res) => {
  db.run('DELETE FROM licenses WHERE id = ?', [req.params.id]);
  saveDB();
  res.json({ success: true, message: 'License la tirtiray' });
});

app.get('/api/admin/referrals', authMiddleware, adminMiddleware, (req, res) => {
  res.json({ referrals: queryAll('SELECT * FROM referrals ORDER BY id DESC') });
});

// ===== CLOUDFLARE WORKER =====
const CF_API = 'https://api.cloudflare.com/client/v4';
app.get('/api/worker/code', authMiddleware, adminMiddleware, async (req, res) => {
  try {
    const token = process.env.CLOUDFLARE_API_TOKEN;
    const accountId = process.env.CLOUDFLARE_ACCOUNT_ID;
    const workerName = process.env.CLOUDFLARE_WORKER_NAME || 'a';
    if (!token || !accountId) return res.status(400).json({ success: false, error: 'CF credentials ma jiro' });
    const url = CF_API + '/accounts/' + accountId + '/workers/scripts/' + workerName;
    const r = await fetch(url, { headers: { 'Authorization': 'Bearer ' + token } });
    const text = await r.text();
    if (r.ok) {
      let c = text;
      const e = c.indexOf('export default');
      if (e > 0) c = c.substring(e);
      const b = c.lastIndexOf(NL + '--');
      if (b > 0) c = c.substring(0, b);
      res.json({ success: true, code: c.trim(), worker: workerName });
    } else { res.status(r.status).json({ success: false, error: text }); }
  } catch (err) { res.status(500).json({ success: false, error: err.message }); }
});
app.post('/api/worker/code', authMiddleware, adminMiddleware, async (req, res) => {
  try {
    const token = process.env.CLOUDFLARE_API_TOKEN;
    const accountId = process.env.CLOUDFLARE_ACCOUNT_ID;
    const workerName = process.env.CLOUDFLARE_WORKER_NAME || 'a';
    const code = req.body.code;
    if (!token || !accountId) return res.status(400).json({ success: false, error: 'CF credentials ma jiro' });
    if (!code) return res.status(400).json({ success: false, error: 'Code ma jiro' });
    const url = CF_API + '/accounts/' + accountId + '/workers/scripts/' + workerName;
    const form = new FormData();
    form.append('metadata', new Blob([JSON.stringify({ main_module: 'worker.js', compatibility_date: '2024-01-01' })], { type: 'application/json' }), 'metadata.json');
    form.append('worker.js', new Blob([code], { type: 'application/javascript+module' }), 'worker.js');
    const r = await fetch(url, { method: 'PUT', headers: { 'Authorization': 'Bearer ' + token }, body: form });
    const data = await r.json();
    if (r.ok && data.success) res.json({ success: true, message: 'La cusboonaysiiyay!', data: data.result });
    else res.status(r.status).json({ success: false, error: JSON.stringify(data.errors || data) });
  } catch (err) { res.status(500).json({ success: false, error: err.message }); }
});
app.get('/api/worker/status', authMiddleware, adminMiddleware, async (req, res) => {
  try {
    const token = process.env.CLOUDFLARE_API_TOKEN;
    const accountId = process.env.CLOUDFLARE_ACCOUNT_ID;
    const workerName = process.env.CLOUDFLARE_WORKER_NAME || 'a';
    if (!token || !accountId) return res.json({ success: true, online: false });
    const url = CF_API + '/accounts/' + accountId + '/workers/scripts/' + workerName;
    const r = await fetch(url, { headers: { 'Authorization': 'Bearer ' + token } });
    const text = await r.text();
    const wUrl = 'https://a.hamse.workers.dev';
    let on = false, rt = 0;
    try { const s = Date.now(); const wr = await fetch(wUrl, { method: 'HEAD' }); rt = Date.now() - s; on = wr.ok; } catch (e) {}
    if (r.ok) res.json({ success: true, online: true, worker_url: wUrl, worker_online: on, response_time: rt + 'ms', code_length: text.length });
    else res.json({ success: true, online: false });
  } catch (err) { res.status(500).json({ success: false, error: err.message }); }
});


// ===== WORKER VERIFY ENDPOINT =====
app.post('/api/verify', async (req, res) => {
  try {
    const tok = req.headers['x-panel-token'] || '';
    const expected = process.env.PANEL_TOKEN || 'HAMSE_PANEL_TOKEN_2026';
    let okToken = false;
    try { okToken = tok.length === expected.length && crypto.timingSafeEqual(Buffer.from(tok), Buffer.from(expected)); } catch(e) {}
    if (!okToken) return res.status(401).json({ valid: false, error: 'Panel token khaldan' });
    const body = req.body || {};
    const key = body.key;
    const serial = body.serial;
    if (!key) return res.json({ valid: false, reason: 'Key ma jiro' });
    const lic = queryOne('SELECT * FROM licenses WHERE license_key = ?', [key]);
    if (!lic) return res.json({ valid: false, reason: 'Key lama helin' });
    if (lic.status === 'banned') return res.json({ valid: false, reason: 'Key waa la xannibay' });
    if (lic.expires_at && lic.expires_at !== '2099-12-31 23:59:59') {
      if (new Date(lic.expires_at) < new Date()) {
        db.run("UPDATE licenses SET status='expired' WHERE id=?", [lic.id]);
        saveDB();
        return res.json({ valid: false, reason: 'Key wuu dhacay', expire: lic.expires_at });
      }
    }
    if (serial) {
      var maxDev = parseInt(lic.max_devices) || 1;
      var used = [];
      try { used = JSON.parse(lic.used_devices || '[]'); } catch(e) { used = []; }
      if (used.indexOf(serial) === -1) {
        if (used.length >= maxDev) {
          return res.json({ valid: false, reason: 'Device limit (' + maxDev + ') gaartay' });
        }
        used.push(serial);
        db.run("UPDATE licenses SET used_devices=?, status='active', used_at=CURRENT_TIMESTAMP WHERE id=?", [JSON.stringify(used), lic.id]);
        saveDB();
      }
    }
    res.json({ valid: true, expire: lic.expires_at || '2099-12-31 23:59:59', status: 'active', duration: lic.duration });
  } catch (err) { res.status(500).json({ valid: false, error: err.message }); }
});
app.post("/api/telegram/send", authMiddleware, adminMiddleware, async (req, res) => {
  const BOT_TOKEN = "7579506309:AAGe6jM6Z2K7yA6DqCWWq48pd0o9SKzQlZE";
  const ADMIN_CHAT_ID = "6320069127";
  const text = req.body.text || "Test message";
  try {
    const r = await fetch("https://api.telegram.org/bot" + BOT_TOKEN + "/sendMessage", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ chat_id: ADMIN_CHAT_ID, text: text })
    });
    const j = await r.json();
    if (j.ok) res.json({ success: true, message: "Telegram message la diray" });
    else res.status(400).json({ success: false, error: j.description });
  } catch(e) {
    res.status(500).json({ success: false, error: e.message });
  }
});

app.get("/api/telegram/status", authMiddleware, adminMiddleware, async (req, res) => {
  const BOT_TOKEN = "7579506309:AAGe6jM6Z2K7yA6DqCWWq48pd0o9SKzQlZE";
  try {
    const r = await fetch("https://api.telegram.org/bot" + BOT_TOKEN + "/getMe");
    const j = await r.json();
    if (j.ok) res.json({ success: true, online: true, bot: j.result });
    else res.json({ success: true, online: false, error: j.description });
  } catch(e) {
    res.json({ success: true, online: false, error: e.message });
  }
});

app.get('*', (req, res) => res.sendFile(path.join(__dirname, 'public', 'index.html')));

initDB().then(() => {
  app.listen(PORT, () => {
    console.log('HAMSE CHEATS VIP PANEL socda port ' + PORT);
    console.log('Admin: ' + ADMIN_USERNAME);
  });
}).catch(err => console.error('DB init error:', err));
