const express = require('express');
const crypto = require('crypto');
const jwt = require('jsonwebtoken');
const helmet = require('helmet');
const cors = require('cors');
const path = require('path');

const app = express();
app.use(helmet({ contentSecurityPolicy: false }));
app.use(cors());
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true }));
app.use(express.text({ type: '*/*' }));

const JWT_SECRET = 'HAMSE-PANEL-2026-SECRET';
const ADMIN_EMAIL = 'hamzemahdi14@gmail.com';
const ADMIN_PASS = 'HamseVIP@2026!';
const FIREBASE_URL = 'https://wolf-e99fb-eb99b-default-rtdb.firebaseio.com';

const KEYS_FALLBACK = {
    'ABDI-VIP-7LKB1SFA': { expire: '2026-11-02', status: 'active' },
    'HAMSE-VIP-2026': { expire: '2026-12-31', status: 'active' },
    'MAXIMUS-1D-9HQsBaAjVgwk': { expire: '2026-12-31', status: 'active' }
};

function getKeyInfo(key) {
    return KEYS_FALLBACK[key] || { expire: '2026-12-31', status: 'active' };
}

function getGames() {
    return [
        { gameTitle: 'PUBG MOBILE', gamename: 'PUBG MOBILE', region: 'Global', gameStatus: 'Latest Version', gameVersion: '4.6.0', currentversion: '4.6.0', appVersion: '4.6.0', appVersionString: '4.6.0', gamePackage: 'com.tencent.ig', gameIcon: 'pubg_global.png', gameObb: '', link: 'https://www.pubgmobile.com/' },
        { gameTitle: 'PUBG MOBILE', gamename: 'PUBG MOBILE', region: 'Korea', gameStatus: 'Latest Version', gameVersion: '4.6.0', currentversion: '4.6.0', appVersion: '4.6.0', appVersionString: '4.6.0', gamePackage: 'com.pubg.krmobile', gameIcon: 'pubg_korea.png', gameObb: '', link: 'https://www.pubgmobile.com/' },
        { gameTitle: 'PUBG MOBILE', gamename: 'PUBG MOBILE', region: 'Vietnam', gameStatus: 'Latest Version', gameVersion: '4.6.0', currentversion: '4.6.0', appVersion: '4.6.0', appVersionString: '4.6.0', gamePackage: 'com.vng.pubgmobile', gameIcon: 'pubg_vietnam.png', gameObb: '', link: 'https://www.pubgmobile.com/' },
        { gameTitle: 'PUBG MOBILE', gamename: 'PUBG MOBILE', region: 'Taiwan', gameStatus: 'Latest Version', gameVersion: '4.6.0', currentversion: '4.6.0', appVersion: '4.6.0', appVersionString: '4.6.0', gamePackage: 'com.rekoo.pubgm', gameIcon: 'pubg_taiwan.png', gameObb: '', link: 'https://www.pubgmobile.com/' }
    ];
}

app.post('/1.1/account/verify_credentials.json', (req, res) => {
    const body = req.body || {};
    const key = (body.keysArray && body.keysArray[0]) || body.user_key || body.key || '';
    const info = getKeyInfo(key);
    return res.json({
        code: 0, msg: 'success', result: 1, status: 1,
        data: { valid: true, expire: info.expire, licenseCount: 999 },
        kv: { license: key, expire: info.expire, status: info.status, licenseCount: 999 }
    });
});

app.post('/connect', (req, res) => {
    const body = req.body || {};
    const key = body.user_key || body.license_key || body.key || (body.keysArray && body.keysArray[0]) || '';
    const info = getKeyInfo(key);
    const games = getGames();
    return res.json({
        status: true,
        data: {
            EXP: info.expire,
            appVersion: '4.6.0', appVersionString: '4.6.0',
            firebase_database_url: FIREBASE_URL,
            databaseUrl: FIREBASE_URL,
            GAME_LIST_ICON: games.map(g => g.gameIcon),
            GAME_LIST_PKG: games.map(g => g.gamePackage),
            STATUS_BY: 'Latest Version', USER_ID: key,
            game_list: games, games: games
        }
    });
});

['/config.Config/GetByKeys','/config.Config/InterGetKeys','/config.Config/ClientKV',
 '/config.Config/InterClientKV','/config.Config/GetCosConfig','/config.Config/Config',
 '/config.Config/InterConfig','/config/clientkv'].forEach(ep => {
    app.post(ep, (req, res) => res.json({ code: 0, msg: 'success', result: 1, status: 1, kv: {}, data: {} }));
});

function auth(req, res, next) {
    const t = (req.headers.authorization || '').replace(/^Bearer\s+/i, '');
    if (!t) return res.status(401).json({ code: 1, msg: 'No token' });
    try { req.user = jwt.verify(t, JWT_SECRET); next(); }
    catch { res.status(401).json({ code: 1, msg: 'Invalid' }); }
}

app.post('/api/admin/login', (req, res) => {
    const { email, password } = req.body || {};
    if (email !== ADMIN_EMAIL || password !== ADMIN_PASS)
        return res.json({ code: 1, msg: 'Invalid' });
    const token = jwt.sign({ id: 1, role: 'admin', email }, JWT_SECRET, { expiresIn: '7d' });
    res.json({ code: 0, msg: 'success', token, role: 'admin', email });
});

app.get('/api/admin/keys', auth, (req, res) => {
    const keys = Object.keys(KEYS_FALLBACK).map((k, i) => ({ id: i + 1, key_value: k, ...KEYS_FALLBACK[k] }));
    res.json({ code: 0, keys });
});

app.get('/api/admin/stats', auth, (req, res) => {
    res.json({ code: 0, stats: { total: 3, active: 3, banned: 0, logs: 0 } });
});

app.get('/health', (req, res) => {
    res.json({ status: 'ok', server: 'online', database: 'connected', app: 'MXMDM compatible', version: '1.0.0' });
});

app.use(express.static(path.join(__dirname)));
app.get('/', (req, res) => {
    res.send('<html><body style="background:#0a0a0f;color:#fff;font-family:sans-serif;padding:40px;text-align:center"><h1 style="color:#4ecdc4">Hamse Panel</h1><p>Server online</p></body></html>');
});

const PORT = process.env.PORT || 5000;
app.listen(PORT, () => console.log('HAMSE PANEL running on ' + PORT));
