/* HAMSE License Key Management - iPhone style (v3) */
(function () {
  'use strict';
  var BASE = '';

  /* ---------- helpers ---------- */
  function tok() {
    try { if (typeof TOKEN !== 'undefined' && TOKEN) return TOKEN; } catch (e) {}
    try { return localStorage.getItem('hamse_token') || localStorage.getItem('token') || ''; } catch (e) { return ''; }
  }
  function esc(s) {
    return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }
  function api(method, path, body) {
    var o = { method: method, headers: { 'Authorization': 'Bearer ' + tok() } };
    if (body) { o.headers['Content-Type'] = 'application/json'; o.body = JSON.stringify(body); }
    return fetch(BASE + path, o).then(function (r) {
      return r.text().then(function (t) {
        var d = {}; try { d = t ? JSON.parse(t) : {}; } catch (e) {}
        return { ok: r.ok && !(d && d.error), status: r.status, data: d || {} };
      });
    }).catch(function () { return { ok: false, status: 0, data: {} }; });
  }
  function errMsg(r) {
    if (r.status === 0) return 'No connection to server';
    if (r.status === 401) return 'Session expired - sign in again';
    if (r.status === 404) return 'Server route not found (404)';
    return (r.data && (r.data.error || r.data.message)) || ('Error ' + r.status);
  }
  function parseT(x) {
    if (!x) return null;
    var s = String(x);
    if (!/[zZ]|[+-]\d\d:?\d\d$/.test(s)) s = s.replace(' ', 'T') + 'Z';
    var t = Date.parse(s);
    return isNaN(t) ? null : t;
  }
  function fmt(ms) { return new Date(ms).toISOString().slice(0, 19).replace('T', ' '); }
  function left(ms) {
    var d = ms - Date.now();
    if (d <= 0) return 'expired';
    var m = Math.floor(d / 60000), dd = Math.floor(m / 1440), h = Math.floor((m % 1440) / 60), mm = m % 60;
    if (dd > 3650) return 'lifetime';
    if (dd > 0) return dd + 'd ' + h + 'h left';
    if (h > 0) return h + 'h ' + mm + 'm left';
    return mm + 'm left';
  }
  function buzz() { try { navigator.vibrate && navigator.vibrate(8); } catch (e) {} }
  function statusOf(l) {
    var s = String(l.status || '').toLowerCase();
    if (s === 'disabled' || s === 'banned') return s;
    var e = parseT(l.expires_at);
    if (s !== 'unused' && e && e < Date.now()) return 'expired';
    if (s === 'active') return 'active';
    if (s === 'expired') return 'expired';
    return 'unused';
  }

  /* ---------- css ---------- */
  function css() {
    if (document.getElementById('hl-css')) return;
    var st = document.createElement('style');
    st.id = 'hl-css';
    st.textContent =
      '.hl,.hl *,.hl-ov,.hl-ov *{box-sizing:border-box;-webkit-tap-highlight-color:transparent}' +
      '.hl{font-family:-apple-system,BlinkMacSystemFont,"SF Pro Display","SF Pro Text",Inter,Roboto,sans-serif;color:#fff;padding:0 0 40px}' +
      '.hl-bar{display:flex;gap:10px;margin:6px 0 12px}' +
      '.hl-search{flex:1;min-width:0;background:#1c1c1e;border:1px solid #2c2c2e;border-radius:14px;color:#fff;font-size:17px;padding:13px 16px;outline:none}' +
      '.hl-search::placeholder{color:#6e6e73}' +
      '.hl-new{border:0;border-radius:14px;padding:0 20px;font-size:17px;font-weight:700;color:#fff;background:linear-gradient(135deg,#0a84ff,#5e5ce6);cursor:pointer}' +
      '.hl-new:active{transform:scale(.96)}' +
      '.hl-chips{display:flex;gap:8px;overflow-x:auto;padding:2px 0 12px;scrollbar-width:none}.hl-chips::-webkit-scrollbar{display:none}' +
      '.hl-chip{flex:none;border:1px solid #2c2c2e;background:#1c1c1e;color:#aeaeb2;border-radius:999px;padding:9px 16px;font-size:15px;font-weight:600;cursor:pointer}' +
      '.hl-chip.on{background:#0a84ff;border-color:#0a84ff;color:#fff}' +
      '.hl-card{background:#1c1c1e;border:1px solid #2c2c2e;border-radius:22px;padding:16px;margin:0 0 12px;animation:hlin .25s ease both}' +
      '@keyframes hlin{from{opacity:0;transform:translateY(6px)}to{opacity:1;transform:none}}' +
      '.hl-top{display:flex;align-items:center;justify-content:space-between;gap:10px}' +
      '.hl-key{font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:17px;font-weight:600;word-break:break-all;letter-spacing:.2px}' +
      '.hl-badge{flex:none;border-radius:999px;padding:7px 13px;font-size:12px;font-weight:800;letter-spacing:.6px;text-transform:uppercase}' +
      '.b-active{background:rgba(48,209,88,.18);color:#30d158}.b-unused{background:#2c2c2e;color:#aeaeb2}' +
      '.b-disabled{background:rgba(255,159,10,.18);color:#ff9f0a}.b-banned,.b-expired{background:rgba(255,69,58,.18);color:#ff453a}' +
      '.hl-meta{display:flex;flex-wrap:wrap;gap:6px 18px;margin:12px 0 4px;color:#8e8e93;font-size:15px}.hl-meta b{color:#fff;font-weight:600}' +
      '.hl-acts{display:flex;flex-wrap:wrap;gap:8px;margin-top:12px}' +
      '.hl-acts button{border:0;border-radius:14px;padding:12px 16px;font-size:16px;font-weight:700;color:#fff;background:#2c2c2e;cursor:pointer;flex:1 1 auto}' +
      '.hl-acts button:active,.hl-pri:active,.hl-sec:active{transform:scale(.96);opacity:.85}' +
      '.hl-acts .g{background:#248a3d}.hl-acts .o{background:#c93400}.hl-acts .bl{background:#0a84ff}.hl-acts .r{background:#d70015}' +
      '.hl-empty{text-align:center;color:#8e8e93;padding:50px 10px;font-size:16px}' +
      '.hl-ov{position:fixed;inset:0;z-index:99999;background:rgba(0,0,0,0);display:flex;align-items:flex-end;justify-content:center;transition:background .22s;-webkit-backdrop-filter:blur(0);backdrop-filter:blur(0)}' +
      '.hl-ov.in{background:rgba(0,0,0,.55);-webkit-backdrop-filter:blur(6px);backdrop-filter:blur(6px)}' +
      '.hl-sh{width:100%;max-width:520px;max-height:92vh;overflow:auto;background:#1c1c1e;color:#fff;border-radius:26px 26px 0 0;padding:10px 20px 28px;transform:translateY(100%);transition:transform .3s cubic-bezier(.2,.9,.25,1);font-family:-apple-system,BlinkMacSystemFont,"SF Pro Text",Inter,Roboto,sans-serif}' +
      '.hl-ov.in .hl-sh{transform:none}' +
      '.hl-grab{width:40px;height:5px;border-radius:3px;background:#48484a;margin:0 auto 14px}' +
      '.hl-sh h3{margin:0 0 6px;font-size:24px;font-weight:800}.hl-sub{margin:0 0 14px;color:#8e8e93;font-size:15px;line-height:1.45;word-break:break-all}' +
      '.hl-seg{display:flex;background:#2c2c2e;border-radius:12px;padding:3px;margin:0 0 14px}' +
      '.hl-seg button{flex:1;border:0;background:none;color:#aeaeb2;font-size:16px;font-weight:700;padding:10px 0;border-radius:10px;cursor:pointer}' +
      '.hl-seg button.on{background:#636366;color:#fff}' +
      '.hl-f{margin:0 0 12px;flex:1;min-width:0}.hl-f label{display:block;color:#8e8e93;font-size:13px;font-weight:600;margin:0 0 6px;text-transform:uppercase;letter-spacing:.5px}' +
      '.hl-f input,.hl-f select{width:100%;background:#2c2c2e;border:1px solid #3a3a3c;border-radius:12px;color:#fff;font-size:17px;padding:13px 14px;outline:none;-webkit-appearance:none;appearance:none}' +
      '.hl-row2{display:flex;gap:10px}' +
      '.hl-pri,.hl-sec{display:block;width:100%;border:0;border-radius:15px;padding:15px;font-size:17px;font-weight:700;color:#fff;cursor:pointer;margin-top:8px}' +
      '.hl-pri{background:linear-gradient(135deg,#0a84ff,#5e5ce6)}.hl-sec{background:#2c2c2e}' +
      '.hl-pri.g{background:#248a3d}.hl-pri.r{background:#d70015}' +
      '.hl-qr{display:flex;gap:8px;flex-wrap:wrap;margin:0 0 14px}.hl-qr button{border:0;background:#2c2c2e;color:#fff;border-radius:999px;padding:9px 15px;font-size:15px;font-weight:600;cursor:pointer}' +
      '.hl-two{display:flex;gap:10px}.hl-two .hl-pri{flex:1}' +
      '.hl-step{display:flex;gap:10px;align-items:center;margin:0 0 12px}.hl-step button{width:52px;height:52px;border:0;border-radius:14px;background:#2c2c2e;color:#fff;font-size:26px;font-weight:600;cursor:pointer}' +
      '.hl-step input{flex:1;text-align:center;background:#2c2c2e;border:1px solid #3a3a3c;border-radius:14px;color:#fff;font-size:24px;font-weight:700;padding:11px;outline:none;min-width:0}' +
      '.hl-toast{position:fixed;left:50%;top:16px;transform:translate(-50%,-80px);z-index:100000;background:#2c2c2e;color:#fff;border-radius:999px;padding:12px 22px;font:600 16px -apple-system,BlinkMacSystemFont,Inter,sans-serif;box-shadow:0 8px 30px rgba(0,0,0,.5);transition:transform .3s cubic-bezier(.2,.9,.25,1);max-width:90vw;text-align:center}' +
      '.hl-toast.in{transform:translate(-50%,0)}.hl-toast.bad{background:#d70015}';
    document.head.appendChild(st);
  }

  /* ---------- toast & sheet ---------- */
  var toastT;
  function toast(msg, bad) {
    var t = document.getElementById('hl-toast');
    if (!t) { t = document.createElement('div'); t.id = 'hl-toast'; document.body.appendChild(t); }
    t.className = 'hl-toast' + (bad ? ' bad' : '');
    t.textContent = msg;
    void t.offsetWidth;
    t.classList.add('in');
    clearTimeout(toastT);
    toastT = setTimeout(function () { t.classList.remove('in'); }, bad ? 3200 : 1800);
  }
  function sheet(html) {
    var ov = document.createElement('div');
    ov.className = 'hl-ov';
    ov.innerHTML = '<div class="hl-sh">' + html + '</div>';
    document.body.appendChild(ov);
    var sh = ov.firstChild;
    requestAnimationFrame(function () { requestAnimationFrame(function () { ov.classList.add('in'); }); });
    function close() {
      ov.classList.remove('in');
      setTimeout(function () { if (ov.parentNode) ov.parentNode.removeChild(ov); }, 260);
    }
    ov.addEventListener('click', function (e) {
      if (e.target === ov || (e.target.closest && e.target.closest('[data-close]'))) close();
    });
    return { el: sh, close: close };
  }
  function q(el, sel) { return el.querySelector(sel); }
  function setSeg(seg, v) {
    var bs = seg.querySelectorAll('button');
    for (var i = 0; i < bs.length; i++) bs[i].classList.toggle('on', bs[i].getAttribute('data-v') === v);
  }

  /* ---------- state ---------- */
  var S = { list: [], q: '', f: 'all', loaded: false };
  function root() { return document.getElementById('licensesList'); }

  function byId(id) {
    for (var i = 0; i < S.list.length; i++) if (String(S.list[i].id) === String(id)) return S.list[i];
    return null;
  }
  function authFail() {
    try { localStorage.removeItem('hamse_token'); } catch (e) {}
    try { if (typeof window.licenseAuthFail === 'function') window.licenseAuthFail(); } catch (e) {}
    try { window.dispatchEvent(new CustomEvent('hamse-unauth')); } catch (e) {}
  }

  /* ---------- render ---------- */
  function shell() {
    var r = root();
    if (!r) return null;
    if (r.querySelector('.hl')) return r;
    css();
    r.innerHTML =
      '<div class="hl">' +
      '<div class="hl-bar"><input class="hl-search" type="search" placeholder="Search keys" autocomplete="off" autocapitalize="off" spellcheck="false"><button class="hl-new" data-a="new">+ New</button></div>' +
      '<div class="hl-chips"></div><div class="hl-list"></div></div>';
    var inp = r.querySelector('.hl-search');
    inp.addEventListener('input', function () { S.q = inp.value.trim().toLowerCase(); renderList(); });
    r.querySelector('.hl').addEventListener('click', onClick);
    return r;
  }
  function renderChips() {
    var r = root(); if (!r) return;
    var c = { all: S.list.length, active: 0, unused: 0, disabled: 0, banned: 0, expired: 0 };
    S.list.forEach(function (l) { c[statusOf(l)]++; });
    var names = [['all', 'All'], ['active', 'Active'], ['unused', 'Unused'], ['disabled', 'Disabled'], ['banned', 'Banned'], ['expired', 'Expired']];
    r.querySelector('.hl-chips').innerHTML = names.map(function (n) {
      return '<button class="hl-chip' + (S.f === n[0] ? ' on' : '') + '" data-a="f" data-f="' + n[0] + '">' + n[1] + ' ' + c[n[0]] + '</button>';
    }).join('');
  }
  function renderList() {
    var r = root(); if (!r) return;
    var box = r.querySelector('.hl-list'); if (!box) return;
    if (!S.loaded) { box.innerHTML = '<div class="hl-empty">Loading...</div>'; return; }
    var items = S.list.filter(function (l) {
      if (S.f !== 'all' && statusOf(l) !== S.f) return false;
      if (S.q && String(l.license_key || '').toLowerCase().indexOf(S.q) < 0 && String(l.game || '').toLowerCase().indexOf(S.q) < 0) return false;
      return true;
    });
    if (!items.length) { box.innerHTML = '<div class="hl-empty">No keys</div>'; return; }
    box.innerHTML = items.map(function (l) {
      var s = statusOf(l), e = parseT(l.expires_at);
      var act = s === 'active'
        ? '<button class="o" data-a="deact" data-id="' + esc(l.id) + '">Deactivate</button>'
        : '<button class="g" data-a="act" data-id="' + esc(l.id) + '">Activate</button>';
      return '<div class="hl-card">' +
        '<div class="hl-top"><div class="hl-key">' + esc(l.license_key) + '</div><div class="hl-badge b-' + s + '">' + s + '</div></div>' +
        '<div class="hl-meta"><span>Game <b>' + esc(l.game || '-') + '</b></span><span>Devices <b>' + esc(l.used_devices || 0) + '/' + esc(l.max_devices || 1) + '</b></span></div>' +
        '<div class="hl-meta"><span>Time <b>' + esc(l.expires_at || '-') + '</b></span>' + (e ? '<span>' + esc(left(e)) + '</span>' : '') + '</div>' +
        '<div class="hl-acts">' +
        '<button data-a="copy" data-id="' + esc(l.id) + '">Copy</button>' + act +
        '<button class="bl" data-a="time" data-id="' + esc(l.id) + '">Time</button>' +
        '<button data-a="dev" data-id="' + esc(l.id) + '">Devices</button>' +
        '<button class="r" data-a="del" data-id="' + esc(l.id) + '">Delete</button>' +
        '</div></div>';
    }).join('');
  }
  function render() { if (!shell()) return; renderChips(); renderList(); }

  function load() {
    shell();
    return api('GET', '/api/licenses').then(function (r) {
      if (r.status === 401) { authFail(); return; }
      if (!r.ok) { S.loaded = true; render(); toast(errMsg(r), true); return; }
      S.list = (r.data.licenses || []).slice().sort(function (a, b) { return (b.id || 0) - (a.id || 0); });
      S.loaded = true;
      render();
    });
  }

  /* ---------- actions ---------- */
  function onClick(e) {
    var b = e.target.closest && e.target.closest('[data-a]');
    if (!b) return;
    var a = b.getAttribute('data-a'), id = b.getAttribute('data-id'), l = id ? byId(id) : null;
    buzz();
    if (a === 'new') return openCreate();
    if (a === 'f') { S.f = b.getAttribute('data-f'); return render(); }
    if (!l) return;
    if (a === 'copy') return copy(l.license_key);
    if (a === 'act') return setStatus(l, 'active');
    if (a === 'deact') return setStatus(l, 'disabled');
    if (a === 'time') return openTime(l);
    if (a === 'dev') return openDevices(l);
    if (a === 'del') return openDelete(l);
  }
  function copy(text) {
    function fb() {
      var t = document.createElement('textarea');
      t.value = text; t.style.cssText = 'position:fixed;opacity:0;top:0';
      document.body.appendChild(t); t.focus(); t.select();
      var ok = false; try { ok = document.execCommand('copy'); } catch (e) {}
      document.body.removeChild(t);
      toast(ok ? 'Copied' : 'Copy failed', !ok);
    }
    if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(text).then(function () { toast('Copied'); }, fb);
    else fb();
  }
  function setStatus(l, status) {
    var old = l.status;
    l.status = status; render();
    api('PUT', '/api/admin/licenses/' + l.id + '/update', { status: status }).then(function (r) {
      if (r.status === 401) { authFail(); return; }
      if (!r.ok) { l.status = old; render(); toast(errMsg(r), true); return; }
      toast(status === 'active' ? 'Key activated' : 'Key deactivated');
    });
  }

  function openTime(l) {
    var mult = { m: 1, h: 60, d: 1440 }, unit = 'd';
    var s = sheet('<div class="hl-grab"></div><h3>Time</h3><p class="hl-sub">' + esc(l.license_key) + '<br>Expires <b id="tx">' + esc(l.expires_at || '-') + '</b></p>' +
      '<div class="hl-qr"><button data-n="1" data-u="h">1 hour</button><button data-n="1" data-u="d">1 day</button><button data-n="7" data-u="d">7 days</button><button data-n="30" data-u="d">30 days</button></div>' +
      '<div class="hl-seg" id="tu"><button data-v="m">Minutes</button><button data-v="h">Hours</button><button class="on" data-v="d">Days</button></div>' +
      '<div class="hl-f"><label>Amount</label><input id="tn" type="number" inputmode="decimal" min="0" value="1"></div>' +
      '<div class="hl-two"><button class="hl-pri r" id="trm">Remove</button><button class="hl-pri g" id="tad">Add</button></div>' +
      '<button class="hl-sec" data-close>Close</button>');
    var seg = q(s.el, '#tu'), amt = q(s.el, '#tn');
    seg.addEventListener('click', function (e) { var b = e.target.closest('button'); if (b) { unit = b.getAttribute('data-v'); setSeg(seg, unit); } });
    s.el.querySelector('.hl-qr').addEventListener('click', function (e) {
      var b = e.target.closest('button'); if (!b) return;
      amt.value = b.getAttribute('data-n'); unit = b.getAttribute('data-u'); setSeg(seg, unit);
    });
    function go(sign) {
      var n = parseFloat(amt.value);
      if (!(n > 0)) return toast('Enter an amount', true);
      var m = Math.round(n * mult[unit]) * sign;
      if (!m) return toast('Amount too small', true);
      var btns = s.el.querySelectorAll('.hl-pri'); btns.forEach(function (x) { x.disabled = true; });
      api('PUT', '/api/admin/licenses/' + l.id + '/update', { add_minutes: m }).then(function (r) {
        btns.forEach(function (x) { x.disabled = false; });
        if (r.status === 401) { s.close(); authFail(); return; }
        if (!r.ok) return toast(errMsg(r), true);
        var d = r.data || {}, ne = d.expires_at || (d.license && d.license.expires_at);
        if (!ne) { var e = parseT(l.expires_at); if (e) ne = fmt(e + m * 60000); }
        if (ne) l.expires_at = ne;
        var tx = q(s.el, '#tx'); if (tx) tx.textContent = l.expires_at || '-';
        render();
        toast(sign > 0 ? 'Time added' : 'Time removed');
      });
    }
    q(s.el, '#tad').onclick = function () { buzz(); go(1); };
    q(s.el, '#trm').onclick = function () { buzz(); go(-1); };
  }

  function openDevices(l) {
    var s = sheet('<div class="hl-grab"></div><h3>Devices</h3><p class="hl-sub">' + esc(l.license_key) + '<br>In use: ' + esc(l.used_devices || 0) + '</p>' +
      '<div class="hl-step"><button id="dm">-</button><input id="dv" type="number" inputmode="numeric" min="1" max="1000" value="' + esc(l.max_devices || 1) + '"><button id="dp">+</button></div>' +
      '<div class="hl-qr"><button data-n="1">1</button><button data-n="2">2</button><button data-n="5">5</button><button data-n="10">10</button><button data-n="50">50</button><button data-n="100">100</button></div>' +
      '<button class="hl-pri" id="ds">Save</button><button class="hl-sec" data-close>Cancel</button>');
    var inp = q(s.el, '#dv');
    function val() { var n = parseInt(inp.value, 10); if (isNaN(n)) n = 1; return Math.max(1, Math.min(1000, n)); }
    q(s.el, '#dm').onclick = function () { inp.value = Math.max(1, val() - 1); buzz(); };
    q(s.el, '#dp').onclick = function () { inp.value = Math.min(1000, val() + 1); buzz(); };
    s.el.querySelector('.hl-qr').addEventListener('click', function (e) { var b = e.target.closest('button'); if (b) inp.value = b.getAttribute('data-n'); });
    q(s.el, '#ds').onclick = function () {
      var n = val(), btn = this; btn.disabled = true;
      setMax(l, n).then(function (r) {
        btn.disabled = false;
        if (r.status === 401) { s.close(); authFail(); return; }
        if (!r.ok) return toast(errMsg(r), true);
        l.max_devices = n; render(); s.close(); toast('Devices set to ' + n);
      });
    };
  }
  function setMax(l, n) {
    return api('PUT', '/api/admin/licenses/' + l.id + '/update', { max_devices: n }).then(function (r) {
      if (r.ok) return r;
      return api('PUT', '/api/admin/licenses/' + l.id + '/edit', { max_devices: n });
    });
  }

  function openDelete(l) {
    var s = sheet('<div class="hl-grab"></div><h3>Delete key?</h3><p class="hl-sub">' + esc(l.license_key) + '<br>This cannot be undone.</p>' +
      '<button class="hl-pri r" id="dy">Delete</button><button class="hl-sec" data-close>Cancel</button>');
    q(s.el, '#dy').onclick = function () {
      var btn = this; btn.disabled = true;
      api('DELETE', '/api/admin/licenses/' + l.id).then(function (r) {
        btn.disabled = false;
        if (r.status === 401) { s.close(); authFail(); return; }
        if (!r.ok) return toast(errMsg(r), true);
        S.list = S.list.filter(function (x) { return x !== l; });
        render(); s.close(); toast('Key deleted');
      });
    };
  }

  /* ---------- create ---------- */
  var DUR = [['30m', '30 minutes'], ['1h', '1 hour'], ['2h', '2 hours'], ['6h', '6 hours'], ['12h', '12 hours'], ['1d', '1 day'], ['7d', '7 days'], ['30d', '30 days'], ['90d', '90 days'], ['365d', '365 days'], ['lifetime', 'Lifetime']];
  function rnd(n) {
    var ch = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789', o = '', a = new Uint8Array(n);
    (window.crypto || window.msCrypto).getRandomValues(a);
    for (var i = 0; i < n; i++) o += ch[a[i] % ch.length];
    return o;
  }
  function openCreate() {
    var mode = 'auto';
    var s = sheet('<div class="hl-grab"></div><h3>New Key</h3>' +
      '<div class="hl-seg" id="hm"><button class="on" data-v="auto">Auto</button><button data-v="custom">Custom</button></div>' +
      '<div class="hl-f" id="hcw" style="display:none"><label>Key name (saved exactly as typed)</label><input id="hcn" autocapitalize="off" autocorrect="off" autocomplete="off" spellcheck="false" placeholder="Type your key"></div>' +
      '<div class="hl-row2"><div class="hl-f"><label>Duration</label><select id="hd">' +
      DUR.map(function (d) { return '<option value="' + d[0] + '"' + (d[0] === '1d' ? ' selected' : '') + '>' + d[1] + '</option>'; }).join('') +
      '</select></div><div class="hl-f"><label>Max devices</label><input id="hmx" type="number" inputmode="numeric" min="1" max="1000" value="1"></div></div>' +
      '<div class="hl-row2"><div class="hl-f" id="hqw"><label>Quantity</label><input id="hq" type="number" inputmode="numeric" min="1" max="50" value="1"></div>' +
      '<div class="hl-f"><label>Game</label><input id="hg" value="PUBG MOBILE" autocomplete="off"></div></div>' +
      '<button class="hl-pri" id="hgo">Create</button><button class="hl-sec" data-close>Cancel</button>');
    var seg = q(s.el, '#hm');
    seg.addEventListener('click', function (e) {
      var b = e.target.closest('button'); if (!b) return;
      mode = b.getAttribute('data-v'); setSeg(seg, mode);
      q(s.el, '#hcw').style.display = mode === 'custom' ? '' : 'none';
      q(s.el, '#hqw').style.display = mode === 'custom' ? 'none' : '';
      if (mode === 'custom') q(s.el, '#hcn').focus();
    });
    q(s.el, '#hgo').onclick = function () {
      var btn = this, dur = q(s.el, '#hd').value;
      var mx = Math.max(1, Math.min(1000, parseInt(q(s.el, '#hmx').value, 10) || 1));
      var game = q(s.el, '#hg').value.trim() || 'PUBG MOBILE';
      var keys = [];
      if (mode === 'custom') {
        var name = q(s.el, '#hcn').value.trim();
        if (!name) return toast('Type the key name', true);
        if (/\s/.test(name)) return toast('Key cannot contain spaces', true);
        keys.push(name);
      } else {
        var n = Math.max(1, Math.min(50, parseInt(q(s.el, '#hq').value, 10) || 1));
        for (var i = 0; i < n; i++) keys.push(dur + '-HAMSE-' + rnd(4) + '-' + rnd(4));
      }
      btn.disabled = true; btn.textContent = 'Creating...';
      var okN = 0, lastErr = '', i2 = 0;
      (function next() {
        if (i2 >= keys.length) {
          btn.disabled = false; btn.textContent = 'Create';
          if (okN) { s.close(); toast(okN + ' key(s) created'); }
          if (lastErr) toast(lastErr, true);
          return load().then(function () { fixMax(keys, mx); });
        }
        var k = keys[i2++];
        api('POST', '/api/admin/licenses/bulk', { count: 1, duration: dur, custom_key: k, max_devices: mx, game: game, key_mode: 'custom' }).then(function (r) {
          if (r.status === 401) { s.close(); authFail(); return; }
          if (r.ok) okN++; else lastErr = errMsg(r);
          next();
        });
      })();
    };
  }
  function fixMax(keys, mx) {
    S.list.forEach(function (l) {
      if (keys.indexOf(l.license_key) >= 0 && Number(l.max_devices) !== mx) {
        setMax(l, mx).then(function (r) { if (r.ok) { l.max_devices = mx; render(); } });
      }
    });
  }

  /* ---------- public overrides ---------- */
  window.loadLicenses = function () { return load(); };
  window.openLicenseModal = function () { shell(); openCreate(); };
  window.HLIC = { reload: load, state: S };
})();
