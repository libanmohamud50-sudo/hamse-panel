const fs = require('fs');
const BASE = 'https://hamse-panel-production.up.railway.app';
const U = process.env.U, PW = process.env.PW;
if (!U || !PW) { console.log('Usage: U=user PW=pass node test-keys.js'); process.exit(1); }
let ep = '/api/login';
try {
  const idx = fs.readFileSync('public/index.html', 'utf8');
  const m = idx.match(/['"`](\/api\/[A-Za-z\/_-]*login[A-Za-z\/_-]*)['"`]/);
  if (m) ep = m[1];
} catch (e) {}
let T = '';
async function call(m, p, b) {
  const r = await fetch(BASE + p, { method: m, headers: { 'Content-Type': 'application/json', Authorization: 'Bearer ' + T }, body: b ? JSON.stringify(b) : undefined });
  let d = {};
  try { d = await r.json(); } catch (e) {}
  return { ok: r.ok, status: r.status, d: d };
}
(async function () {
  try {
    const lg = await fetch(BASE + ep, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ username: U, password: PW }) });
    const ld = await lg.json().catch(function () { return {}; });
    if (!ld.token) { console.log('LOGIN FAILED', lg.status, JSON.stringify(ld).slice(0, 200)); return; }
    T = ld.token;
    console.log('Login OK via', ep);
    let r = await call('GET', '/api/licenses');
    const before = r.d.licenses || [];
    console.log('Existing keys:', before.length, '| response fields:', Object.keys(r.d).join(','));
    const durs = ['30m', '1h', '2h', '6h', '12h', '1d', '7d', '30d', '90d', '365d', 'lifetime'];
    const tag = Math.random().toString(36).slice(2, 6).toUpperCase();
    const made = [];
    for (const d of durs) {
      const key = d + '-TEST-' + tag;
      const x = await call('POST', '/api/admin/licenses/bulk', { count: 1, duration: d, custom_key: key, max_devices: 7, game: 'PUBG MOBILE', key_mode: 'custom' });
      if (!x.ok) console.log('create FAIL', d, x.status, JSON.stringify(x.d).slice(0, 80));
      made.push(key);
    }
    r = await call('GET', '/api/licenses');
    const list = r.d.licenses || [];
    const recs = [];
    for (const key of made) {
      const rec = list.find(function (k) { return String(k.license_key).toLowerCase() === key.toLowerCase(); });
      if (!rec) { console.log('MISSING', key); continue; }
      recs.push(rec);
      console.log(key.split('-')[0].padEnd(8), 'max=' + rec.max_devices, rec.status, 'exp=' + rec.expires_at, 'dur=' + rec.duration);
    }
    if (recs[0]) console.log('Fields:', Object.keys(recs[0]).join(','));
    const t = recs.find(function (x) { return /^7d/i.test(x.license_key); });
    if (t) {
      const up = function (b) { return call('PUT', '/api/admin/licenses/' + t.id + '/update', b); };
      let u = await up({ status: 'active' });
      console.log('activate:', u.ok ? 'ok' : 'FAIL ' + JSON.stringify(u.d).slice(0, 80));
      r = await call('GET', '/api/licenses');
      const a1 = (r.d.licenses || []).find(function (k) { return k.id === t.id; });
      await up({ max_devices: 25 });
      await up({ add_minutes: 60 });
      await up({ add_minutes: -30 });
      await up({ status: 'disabled' });
      r = await call('GET', '/api/licenses');
      const a2 = (r.d.licenses || []).find(function (k) { return k.id === t.id; });
      const diff = (new Date(a2.expires_at) - new Date(a1.expires_at)) / 60000;
      console.log('after: max=' + a2.max_devices + ' (want 25)', a2.status + ' (want disabled)', 'time diff=' + diff + ' min (want 30)');
    }
    for (const rec of recs) await call('DELETE', '/api/admin/licenses/' + rec.id);
    console.log('cleanup: deleted ' + recs.length + ' test keys');
  } catch (e) { console.log('ERROR', e.message); }
})();
