/* HAMSE VIP - Licenses app (iPhone-style key management) */
(function () {
  var BASE = 'https://hamse-panel-production.up.railway.app';
  var DURATIONS = [
    ['30m', '30 min'], ['1h', '1 hour'], ['2h', '2 hours'], ['6h', '6 hours'],
    ['12h', '12 hours'], ['1d', '1 day'], ['7d', '7 days'], ['30d', '30 days'],
    ['90d', '90 days'], ['365d', '365 days'], ['lifetime', 'Lifetime']
  ];
  var cache = [];
  var filter = 'all';
  var query = '';

  function toast(m, t) { try { showToast(m, t || 'success'); } catch (e) { console.log(m); } }
  function tok() { try { return TOKEN; } catch (e) { return ''; } }

  function call(method, path, body) {
    return fetch(BASE + path, {
      method: method,
      headers: { 'Content-Type': 'application/json', 'Authorization': 'Bearer ' + tok() },
      body: body ? JSON.stringify(body) : undefined
    }).then(function (r) {
      return r.json().catch(function () { return {}; }).then(function (d) {
        if (!r.ok || d.error) throw new Error(d.error || ('HTTP ' + r.status));
        return d;
      });
    });
  }

  function esc(s) {
    return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }

  var css = '' +
    '.lx{font-family:-apple-system,BlinkMacSystemFont,"SF Pro Display",Segoe UI,sans-serif;color:#f2f2f7}' +
    '.lx-top{display:flex;gap:8px;align-items:center;margin-bottom:10px}' +
    '.lx-search{flex:1;background:#1c1c1e;border:1px solid #2c2c2e;border-radius:12px;color:#fff;padding:10px 12px;font-size:14px;outline:none}' +
    '.lx-add{background:linear-gradient(135deg,#0a84ff,#5e5ce6);border:0;color:#fff;border-radius:12px;padding:10px 14px;font-weight:600;font-size:14px;cursor:pointer}' +
    '.lx-chips{display:flex;gap:6px;overflow-x:auto;margin-bottom:12px;padding-bottom:2px}' +
    '.lx-chip{background:#1c1c1e;border:1px solid #2c2c2e;color:#aeaeb2;border-radius:999px;padding:6px 12px;font-size:12px;white-space:nowrap;cursor:pointer}' +
    '.lx-chip.on{background:#0a84ff;border-color:#0a84ff;color:#fff}' +
    '.lx-card{background:#1c1c1e;border:1px solid #2c2c2e;border-radius:16px;padding:12px;margin-bottom:10px}' +
    '.lx-row{display:flex;justify-content:space-between;align-items:center;gap:8px}' +
    '.lx-key{font-family:ui-monospace,Menlo,monospace;font-size:12.5px;word-break:break-all;color:#fff}' +
    '.lx-badge{font-size:10.5px;font-weight:700;padding:3px 8px;border-radius:999px;text-transform:uppercase;letter-spacing:.3px;white-space:nowrap}' +
    '.st-active{background:#12361f;color:#30d158}.st-unused{background:#2a2a2e;color:#aeaeb2}' +
    '.st-disabled{background:#3a2a10;color:#ff9f0a}.st-banned{background:#3d1517;color:#ff453a}.st-expired{background:#3d1517;color:#ff6961}' +
    '.lx-meta{display:flex;gap:14px;flex-wrap:wrap;margin:8px 0 10px;font-size:12px;color:#8e8e93}' +
    '.lx-meta b{color:#e5e5ea;font-weight:600}' +
    '.lx-acts{display:grid;grid-template-columns:repeat(5,1fr);gap:6px}' +
    '.lx-b{border:0;border-radius:10px;padding:9px 0;font-size:11.5px;font-weight:600;color:#fff;cursor:pointer;background:#2c2c2e}' +
    '.lx-b.go{background:#248a3d}.lx-b.off{background:#b25000}.lx-b.del{background:#d70015}.lx-b.t{background:#0a84ff}' +
    '.lx-empty{text-align:center;color:#8e8e93;padding:30px 0;font-size:14px}' +
    '.lx-ov{position:fixed;inset:0;background:rgba(0,0,0,.55);z-index:99999;display:flex;align-items:flex-end;justify-content:center}' +
    '.lx-sheet{background:#1c1c1e;width:100%;max-width:480px;border-radius:22px 22px 0 0;padding:16px;max-height:88vh;overflow:auto;color:#f2f2f7}' +
    '.lx-sheet h3{margin:0 0 12px;font-size:17px}' +
    '.lx-l{display:block;font-size:12px;color:#8e8e93;margin:10px 0 5px}' +
    '.lx-in{width:100%;box-sizing:border-box;background:#2c2c2e;border:1px solid #3a3a3c;border-radius:12px;color:#fff;padding:11px 12px;font-size:15px;outline:none}' +
    '.lx-sw{display:flex;justify-content:space-between;align-items:center;margin-top:12px;font-size:14px}' +
    '.lx-sw input{width:44px;height:26px}' +
    '.lx-two{display:grid;grid-template-columns:1fr 1fr;gap:8px}' +
    '.lx-pri{width:100%;margin-top:16px;background:linear-gradient(135deg,#0a84ff,#5e5ce6);border:0;color:#fff;border-radius:14px;padding:13px;font-size:15px;font-weight:700;cursor:pointer}' +
    '.lx-sec{width:100%;margin-top:8px;background:#2c2c2e;border:0;color:#fff;border-radius:14px;padding:12px;font-size:14px;cursor:pointer}';
  var st = document.createElement('style');
  st.textContent = css;
  document.head.appendChild(st);
  var st2 = document.createElement('style');
  st2.textContent = '.lx-seg{display:grid;grid-template-columns:1fr 1fr;background:#2c2c2e;border-radius:12px;padding:3px;gap:3px}.lx-seg button{border:0;background:transparent;color:#aeaeb2;border-radius:10px;padding:10px 0;font-size:15px;font-weight:600}.lx-seg button.on{background:#0a84ff;color:#fff}';
  document.head.appendChild(st2);

  function usedCount(k) {
    try { return JSON.parse(k.used_devices || '[]').length; } catch (e) { return 0; }
  }
  function remaining(k) {
    try { if (typeof countdown === 'function') return countdown(k.expires_at); } catch (e) {}
    return k.expires_at ? String(k.expires_at) : '-';
  }
  function randPart(n) {
    var c = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789', s = '';
    for (var i = 0; i < n; i++) s += c[Math.floor(Math.random() * c.length)];
    return s;
  }
  function autoKey(dur) { return dur + '-HAMSE-' + randPart(4) + '-' + randPart(4); }

  function render() {
    var host = document.getElementById('licensesList');
    if (!host) return;
    var list = cache.filter(function (k) {
      if (filter !== 'all' && k.status !== filter) return false;
      if (query && String(k.license_key || '').toLowerCase().indexOf(query) === -1) return false;
      return true;
    });
    var counts = { all: cache.length };
    cache.forEach(function (k) { counts[k.status] = (counts[k.status] || 0) + 1; });
    var chips = ['all', 'active', 'unused', 'disabled', 'banned', 'expired'].map(function (s) {
      return '<span class="lx-chip' + (filter === s ? ' on' : '') + '" data-f="' + s + '">' +
        s.charAt(0).toUpperCase() + s.slice(1) + ' ' + (counts[s] || 0) + '</span>';
    }).join('');

    var h = '<div class="lx">' +
      '<div class="lx-top"><input class="lx-search" id="lxSearch" placeholder="Search keys" value="' + esc(query) + '">' +
      '<button class="lx-add" data-a="gen">+ New</button></div>' +
      '<div class="lx-chips">' + chips + '</div>';

    if (!list.length) h += '<div class="lx-empty">No keys found</div>';
    list.forEach(function (k) {
      var on = k.status === 'active';
      h += '<div class="lx-card" data-id="' + k.id + '">' +
        '<div class="lx-row"><div class="lx-key">' + esc(k.license_key) + '</div>' +
        '<span class="lx-badge st-' + esc(k.status) + '">' + esc(k.status) + '</span></div>' +
        '<div class="lx-meta"><span>Game <b>' + esc(k.game || 'PUBG MOBILE') + '</b></span>' +
        '<span>Devices <b>' + usedCount(k) + '/' + (k.max_devices || 1) + '</b></span>' +
        '<span>Time <b>' + esc(remaining(k)) + '</b></span></div>' +
        '<div class="lx-acts">' +
        '<button class="lx-b" data-a="copy">Copy</button>' +
        (on ? '<button class="lx-b off" data-a="deact">Disable</button>'
            : '<button class="lx-b go" data-a="act">Activate</button>') +
        '<button class="lx-b t" data-a="time">Time</button>' +
        '<button class="lx-b" data-a="dev">Devices</button>' +
        '<button class="lx-b del" data-a="del">Delete</button></div></div>';
    });
    h += '</div>';
    host.innerHTML = h;
  }

  function load() {
    return call('GET', '/api/licenses').then(function (d) {
      cache = d.licenses || d.keys || d.data || (Array.isArray(d) ? d : []);
      render();
    }).catch(function (e) { toast(e.message, 'error'); });
  }

  function sheet(html) {
    closeSheet();
    var ov = document.createElement('div');
    ov.className = 'lx-ov';
    ov.id = 'lxOv';
    ov.innerHTML = '<div class="lx-sheet">' + html + '<button class="lx-sec" data-a="close">Cancel</button></div>';
    ov.addEventListener('click', function (e) {
      if (e.target === ov || (e.target.getAttribute && e.target.getAttribute('data-a') === 'close')) closeSheet();
    });
    document.body.appendChild(ov);
    return ov;
  }
  function closeSheet() {
    var o = document.getElementById('lxOv');
    if (o) o.remove();
  }
  function q(id) { return document.getElementById(id); }

  function keyWithPrefix(dur, key) {
    key = String(key).trim();
    return key.toLowerCase().indexOf(dur.toLowerCase() + '-') === 0 ? key : dur + '-' + key;
  }

  function genSheet() {
    var mode = 'auto';
    var opts = DURATIONS.map(function (d) {
      return '<option value="' + d[0] + '"' + (d[0] === '30d' ? ' selected' : '') + '>' + d[1] + '</option>';
    }).join('');
    sheet(
      '<h3>Generate License</h3>' +
      '<label class="lx-l">Duration</label><select class="lx-in" id="lxDur">' + opts + '</select>' +
      '<label class="lx-l">Key name</label>' +
      '<div class="lx-seg"><button type="button" class="on" id="lxSegA">Auto</button><button type="button" id="lxSegC">Custom</button></div>' +
      '<div id="lxCustomWrap" style="display:none"><label class="lx-l">Your key name (letters, numbers, - and _)</label>' +
      '<input class="lx-in" id="lxCustom" placeholder="e.g. HAMSE-VIP-001" autocomplete="off" autocapitalize="characters"></div>' +
      '<div class="lx-two"><div><label class="lx-l">Max devices (1-1000)</label>' +
      '<input class="lx-in" id="lxMax" type="number" min="1" max="1000" value="1"></div>' +
      '<div><label class="lx-l">Quantity (Auto only)</label>' +
      '<input class="lx-in" id="lxCnt" type="number" min="1" max="50" value="1"></div></div>' +
      '<label class="lx-l">Game</label><input class="lx-in" id="lxGame" value="PUBG MOBILE">' +
      '<div class="lx-l" id="lxPrev" style="color:#0a84ff"></div>' +
      '<button class="lx-pri" id="lxGo">Generate</button>');

    function prev() {
      var d = q('lxDur').value;
      q('lxPrev').textContent = (mode === 'auto' ? 'Example: ' + autoKey(d) : 'Final key: ' + keyWithPrefix(d, q('lxCustom').value.trim() || 'YOURNAME'));
    }
    function setMode(m) {
      mode = m;
      q('lxSegA').className = m === 'auto' ? 'on' : '';
      q('lxSegC').className = m === 'custom' ? 'on' : '';
      q('lxCustomWrap').style.display = m === 'custom' ? 'block' : 'none';
      q('lxCnt').disabled = (m === 'custom');
      if (m === 'custom') { q('lxCnt').value = 1; q('lxCustom').focus(); }
      prev();
    }
    q('lxSegA').onclick = function () { setMode('auto'); };
    q('lxSegC').onclick = function () { setMode('custom'); };
    q('lxDur').onchange = prev;
    q('lxCustom').oninput = prev;
    prev();

    q('lxGo').onclick = function () {
      var dur = q('lxDur').value;
      var max = parseInt(q('lxMax').value, 10);
      if (!(max >= 1 && max <= 1000)) return toast('Max devices must be 1-1000', 'error');
      var game = (q('lxGame').value || 'PUBG MOBILE').trim();
      var jobs = [];
      if (mode === 'auto') {
        var n = Math.min(Math.max(parseInt(q('lxCnt').value, 10) || 1, 1), 50);
        for (var i = 0; i < n; i++) jobs.push(autoKey(dur));
      } else {
        var c = (q('lxCustom').value || '').trim();
        if (!c) return toast('Type your key name', 'error');
        if (!/^[A-Za-z0-9_-]{2,40}$/.test(c)) return toast('Key name: letters, numbers, - and _ only (2-40)', 'error');
        jobs.push(keyWithPrefix(dur, c));
      }
      q('lxGo').disabled = true;
      q('lxGo').textContent = 'Working...';
      var created = [], failed = 0, lastErr = '';
      jobs.reduce(function (p, key) {
        return p.then(function () {
          return call('POST', '/api/admin/licenses/bulk', {
            count: 1, duration: dur, custom_key: key, max_devices: max, game: game, key_mode: 'custom'
          }).then(function () { created.push(key); })
            .catch(function (e) { failed++; lastErr = e.message; });
        });
      }, Promise.resolve()).then(function () {
        if (!created.length) return;
        return call('GET', '/api/licenses').then(function (d) {
          var list = d.licenses || d.keys || d.data || [];
          var fixes = [];
          created.forEach(function (key) {
            var rec = list.filter(function (x) { return String(x.license_key).toLowerCase() === key.toLowerCase(); })[0];
            if (rec && Number(rec.max_devices) !== max) {
              fixes.push(call('PUT', '/api/admin/licenses/' + rec.id + '/update', { max_devices: max }));
            }
          });
          return Promise.all(fixes);
        }).catch(function () {});
      }).then(function () {
        closeSheet();
        if (failed) toast(created.length + ' created, ' + failed + ' failed: ' + lastErr, 'error');
        else toast(created.length + ' key(s) created');
        load();
      });
    };
  }

  function timeSheet(k) {
    sheet(
      '<h3>Add / subtract time</h3><div class="lx-key" style="margin-bottom:6px">' + esc(k.license_key) + '</div>' +
      '<div class="lx-two"><div><label class="lx-l">Amount</label>' +
      '<input class="lx-in" id="lxAmt" type="number" min="1" value="1"></div>' +
      '<div><label class="lx-l">Unit</label><select class="lx-in" id="lxUnit">' +
      '<option value="1">Minutes</option><option value="60">Hours</option><option value="1440" selected>Days</option></select></div></div>' +
      '<div class="lx-two" style="margin-top:12px">' +
      '<button class="lx-pri" style="background:#248a3d" id="lxPlus">+ Add</button>' +
      '<button class="lx-pri" style="background:#d70015" id="lxMinus">- Subtract</button></div>');
    function go(sign) {
      var n = parseInt(q('lxAmt').value, 10);
      if (!(n > 0)) return toast('Enter a valid amount', 'error');
      var mins = sign * n * parseInt(q('lxUnit').value, 10);
      call('PUT', '/api/admin/licenses/' + k.id + '/update', { add_minutes: mins })
        .then(function () { closeSheet(); toast('Time updated'); load(); })
        .catch(function (e) { toast(e.message, 'error'); });
    }
    q('lxPlus').onclick = function () { go(1); };
    q('lxMinus').onclick = function () { go(-1); };
  }

  function devSheet(k) {
    sheet(
      '<h3>Max devices</h3><div class="lx-key" style="margin-bottom:6px">' + esc(k.license_key) + '</div>' +
      '<label class="lx-l">Max devices (1-1000)</label>' +
      '<input class="lx-in" id="lxDv" type="number" min="1" max="1000" value="' + (k.max_devices || 1) + '">' +
      '<button class="lx-pri" id="lxDvGo">Save</button>');
    q('lxDvGo').onclick = function () {
      var n = parseInt(q('lxDv').value, 10);
      if (!(n >= 1 && n <= 1000)) return toast('Must be 1-1000', 'error');
      call('PUT', '/api/admin/licenses/' + k.id + '/update', { max_devices: n })
        .then(function () { closeSheet(); toast('Max devices updated'); load(); })
        .catch(function (e) { toast(e.message, 'error'); });
    };
  }

  function setStatus(k, status, msg) {
    call('PUT', '/api/admin/licenses/' + k.id + '/update', { status: status })
      .then(function () { toast(msg); load(); })
      .catch(function (e) { toast(e.message, 'error'); });
  }

  function del(k) {
    sheet('<h3>Delete key?</h3><div class="lx-key" style="margin-bottom:6px">' + esc(k.license_key) +
      '</div><div class="lx-l">This cannot be undone.</div>' +
      '<button class="lx-pri" style="background:#d70015" id="lxDel">Delete</button>');
    q('lxDel').onclick = function () {
      call('DELETE', '/api/admin/licenses/' + k.id)
        .then(function () { closeSheet(); toast('Key deleted'); load(); })
        .catch(function (e) { toast(e.message, 'error'); });
    };
  }

  document.addEventListener('click', function (e) {
    var host = document.getElementById('licensesList');
    if (!host || !host.contains(e.target)) return;
    var chip = e.target.closest && e.target.closest('.lx-chip');
    if (chip) { filter = chip.getAttribute('data-f'); render(); return; }
    var btn = e.target.closest && e.target.closest('[data-a]');
    if (!btn) return;
    var a = btn.getAttribute('data-a');
    if (a === 'gen') return genSheet();
    var card = btn.closest('.lx-card');
    if (!card) return;
    var id = card.getAttribute('data-id');
    var k = cache.filter(function (x) { return String(x.id) === String(id); })[0];
    if (!k) return;
    if (a === 'copy') {
      try { navigator.clipboard.writeText(k.license_key); toast('Copied: ' + k.license_key); }
      catch (err) { toast('Copy failed', 'error'); }
    } else if (a === 'act') setStatus(k, 'active', 'Key activated');
    else if (a === 'deact') setStatus(k, 'disabled', 'Key disabled');
    else if (a === 'time') timeSheet(k);
    else if (a === 'dev') devSheet(k);
    else if (a === 'del') del(k);
  });
  document.addEventListener('input', function (e) {
    if (e.target && e.target.id === 'lxSearch') {
      query = e.target.value.toLowerCase();
      var pos = e.target.selectionStart;
      render();
      var s = q('lxSearch');
      if (s) { s.focus(); try { s.setSelectionRange(pos, pos); } catch (x) {} }
    }
  });

  window.loadLicenses = load;
  window.openLicenseModal = genSheet;
})();
