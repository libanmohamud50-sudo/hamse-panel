import os, shutil, secrets
BASE = os.path.expanduser('~/panel-cusub')
os.chdir(BASE)
shutil.copy('server.js', 'server.js.bak_dur_' + secrets.token_hex(3))
shutil.copy('public/index.html', 'public/index.html.bak_dur_' + secrets.token_hex(3))
print("Backup la sameeyay")

# ============================================
# 1. SERVER.JS — Hagaaji duration_hours logic
# ============================================
with open('server.js', 'r', encoding='utf-8') as f:
    srv = f.read()

# Beddel calcExpiry function
old_calc = '''function calcExpiry(hours) {
  if (hours === 0) return '2099-12-31 23:59:59';
  const d = new Date(Date.now() + hours * 3600 * 1000);
  const pad = n => String(n).padStart(2, '0');
  return d.getFullYear() + '-' + pad(d.getMonth()+1) + '-' + pad(d.getDate()) + ' ' + pad(d.getHours()) + ':' + pad(d.getMinutes()) + ':' + pad(d.getSeconds());
}'''

new_calc = '''function calcExpiry(hours) {
  if (hours === 0 || hours === '0' || hours === 'lifetime') return '2099-12-31 23:59:59';
  const h = parseInt(hours) || 1;
  const d = new Date(Date.now() + h * 3600 * 1000);
  const pad = n => String(n).padStart(2, '0');
  return d.getFullYear() + '-' + pad(d.getMonth()+1) + '-' + pad(d.getDate()) + ' ' + pad(d.getHours()) + ':' + pad(d.getMinutes()) + ':' + pad(d.getSeconds());
}'''

if old_calc in srv:
    srv = srv.replace(old_calc, new_calc)
    print("OK: calcExpiry la hagaajiyay")
else:
    print("WARN: calcExpiry lama helin")

# Beddel /api/admin/keys/create si uu max_devices u qaato
old_create = "const { custom_name, duration_hours, count, duration_label } = req.body;"
new_create = "const { custom_name, duration_hours, count, duration_label, max_devices } = req.body;\n  const maxDev = parseInt(max_devices) || 1;"
if old_create in srv:
    srv = srv.replace(old_create, new_create)
    print("OK: max_devices la daray create")

# Ku dar max_devices column licenses table
if 'max_devices INTEGER DEFAULT 1' not in srv:
    srv = srv.replace(
        "device_id TEXT, serial TEXT, duration TEXT",
        "device_id TEXT, serial TEXT, max_devices INTEGER DEFAULT 1, used_devices TEXT DEFAULT '[]', duration TEXT"
    )
    # ALTER TABLE
    marker_alter = "try { db.run(\"ALTER TABLE licenses ADD COLUMN serial TEXT\"); } catch (e) {}"
    if marker_alter in srv:
        srv = srv.replace(marker_alter,
            marker_alter + "\n  try { db.run(\"ALTER TABLE licenses ADD COLUMN max_devices INTEGER DEFAULT 1\"); } catch (e) {}\n  try { db.run(\"ALTER TABLE licenses ADD COLUMN used_devices TEXT DEFAULT '[]'\"); } catch (e) {}")
    print("OK: max_devices + used_devices la daray")

# Beddel INSERT licenses si max_devices u qaato
old_insert = "db.run(`INSERT INTO licenses (license_key, name, duration, duration_hours, expires_at, status)\n              VALUES (?, ?, ?, ?, ?, 'unused')`,\n              [keyName, custom_name || null, label, hours, expiresAt]);"
new_insert = "db.run(`INSERT INTO licenses (license_key, name, duration, duration_hours, expires_at, status, max_devices)\n              VALUES (?, ?, ?, ?, ?, 'unused', ?)`,\n              [keyName, custom_name || null, label, hours, expiresAt, maxDev]);"
if old_insert in srv:
    srv = srv.replace(old_insert, new_insert)
    print("OK: INSERT max_devices la daray")

# Beddel /api/verify — isticmaal max_devices
old_verify = '''    if (serial) {
      if (!lic.serial) {
        db.run("UPDATE licenses SET serial=?, device_id=?, status='active', used_at=CURRENT_TIMESTAMP WHERE id=?", [serial, serial, lic.id]);
        saveDB();
      } else if (lic.serial !== serial) {
        return res.json({ valid: false, reason: 'Serial khaldan' });
      }
    }'''

new_verify = '''    if (serial) {
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
    }'''

if old_verify in srv:
    srv = srv.replace(old_verify, new_verify)
    print("OK: verify max_devices la hagaajiyay")

with open('server.js', 'w', encoding='utf-8') as f:
    f.write(srv)
print("OK: server.js la keydiyay")

# ============================================
# 2. INDEX.HTML — Ka saar Worker Edit qaybta + ku dar duration options
# ============================================
with open('public/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Ka saar sidebar Worker link
import re
html = re.sub(r'<a[^>]*onclick="showSection\(\'worker\'\)"[^>]*>[^<]*Cloudflare Worker</a>\s*', '', html)
html = re.sub(r'<a[^>]*id="nav-worker"[^>]*>[^<]*</a>\s*', '', html)

# Ka saar section-worker markup
start = html.find('<div id="section-worker"')
if start != -1:
    end = html.find('<div id="section-status"')
    if end != -1:
        html = html[:start] + html[end:]
        print("OK: Worker section la saaray")

# Ka saar JS Worker functions
for fn in ['loadWorkerPage', 'cwDeploy', 'cwSelectAll', 'cwRemoveAll']:
    # Regex tirtir function oo dhan
    pattern = r'async function ' + fn + r'\([^)]*\)\s*\{[^}]*(?:\{[^}]*\}[^}]*)*\}\s*'
    html = re.sub(pattern, '', html)

# Sidebar link navigation — ka saar worker reference
html = html.replace("if (name === 'worker') loadWorkerPage();", "")
html = html.replace("if(n==='worker')loadWorkerPage();", "")

# Beddel duration options modal — ku dar 1hour, 1day, 7day, 30day, custom
old_durations = html.find('id="durationGrid"')
if old_durations != -1:
    # Ka hel dhammaadka div-ka
    end_div = html.find('</div>', html.find('data-hours="custom"', old_durations))
    end_div = html.find('</div>', end_div + 6) + 6
    new_dur = '''<div class="duration-grid" id="durationGrid">
        <div class="duration-btn" data-hours="1" data-label="1h" onclick="selectDuration(this)">1 Hour<small>1 saac</small></div>
        <div class="duration-btn" data-hours="24" data-label="1d" onclick="selectDuration(this)">1 Day<small>24 saac</small></div>
        <div class="duration-btn" data-hours="72" data-label="3d" onclick="selectDuration(this)">3 Days<small>72 saac</small></div>
        <div class="duration-btn selected" data-hours="168" data-label="7d" onclick="selectDuration(this)">7 Days<small>toddobaad</small></div>
        <div class="duration-btn" data-hours="720" data-label="30d" onclick="selectDuration(this)">30 Days<small>bil</small></div>
        <div class="duration-btn" data-hours="2160" data-label="90d" onclick="selectDuration(this)">90 Days<small>3 bilood</small></div>
        <div class="duration-btn" data-hours="0" data-label="lifetime" onclick="selectDuration(this)">Lifetime<small>weligeed</small></div>
        <div class="duration-btn" data-hours="custom" data-label="custom" onclick="selectDuration(this)">Custom<small>geli saacadaha</small></div>
      </div>
      <div id="customHoursBox" class="hidden" style="margin-top:8px;">
        <label style="font-size:12px;">Custom Hours</label>
        <input type="number" id="customHours" value="12" min="1">
      </div>
      <div style="margin-top:8px;">
        <label style="font-size:12px;">Max Devices (qaabka key-ga)</label>
        <input type="number" id="maxDevices" value="1" min="1" max="1000">
      </div>'''
    html = html[:old_durations - len('id="durationGrid"')] + new_dur + html[end_div:]

# Beddel createKeys function si max_devices u qaato
old_create_js = "body: JSON.stringify({\n      custom_name: name || null,\n      duration_hours: hours,\n      duration_label: label,\n      count: count\n    })"
new_create_js = "body: JSON.stringify({\n      custom_name: name || null,\n      duration_hours: hours,\n      duration_label: label,\n      count: count,\n      max_devices: parseInt(document.getElementById('maxDevices').value) || 1\n    })"
if old_create_js in html:
    html = html.replace(old_create_js, new_create_js)
    print("OK: createKeys max_devices la daray")

# Ku dar if(a==='custom') logic createKeys
old_sel = "let hours = SELECTED_DURATION.hours;"
new_sel = "let hours = SELECTED_DURATION.hours;\n  if (SELECTED_DURATION.label === 'custom') { hours = parseInt(document.getElementById('customHours').value) || 12; }"
if old_sel in html:
    html = html.replace(old_sel, new_sel)
    print("OK: custom hours logic la daray")

with open('public/index.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("OK: public/index.html la keydiyay")

# Delete old DB
if os.path.exists('hamse_vip.db'):
    os.remove('hamse_vip.db')
    print("OK: Database hore la tirtiray")

print("")
print("========================================")
print("DHAMMAAN - HAMBALYO!")
print("========================================")
