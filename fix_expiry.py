import os, shutil, secrets
BASE = os.path.expanduser('~/panel-cusub')
os.chdir(BASE)
shutil.copy('server.js', 'server.js.bak_exp_' + secrets.token_hex(3))
print("Backup la sameeyay")

with open('server.js', 'r', encoding='utf-8') as f:
    srv = f.read()

# 1. Ku dar calcExpiry function ka hor app.post('/api/login')
if 'function calcExpiry' not in srv:
    calc_fn = '''
function calcExpiry(hours) {
  if (!hours || hours === 0 || hours === '0' || hours === 'lifetime') return '2099-12-31 23:59:59';
  const h = parseInt(hours);
  if (isNaN(h)) return '2099-12-31 23:59:59';
  const d = new Date(Date.now() + h * 3600 * 1000);
  const pad = n => String(n).padStart(2, '0');
  return d.getFullYear() + '-' + pad(d.getMonth()+1) + '-' + pad(d.getDate()) + ' ' + pad(d.getHours()) + ':' + pad(d.getMinutes()) + ':' + pad(d.getSeconds());
}

'''
    marker = "app.post('/api/login'"
    if marker in srv:
        srv = srv.replace(marker, calc_fn + marker)
        print("OK: calcExpiry la daray")
    else:
        marker2 = "// ============ ROUTES ============"
        if marker2 in srv:
            srv = srv.replace(marker2, marker2 + "\n" + calc_fn)
            print("OK: calcExpiry la daray (routes)")
        else:
            # Ku dar ka hor /api/health
            marker3 = "app.get('/api/health'"
            if marker3 in srv:
                srv = srv.replace(marker3, calc_fn + marker3)
                print("OK: calcExpiry la daray (health)")

# 2. Beddel INSERT si expires_at loo xisaabiyo
old_insert = "const expiresAt = calcExpiry(hours);"
new_insert = "const expiresAt = calcExpiry(hours);\n    console.log('Key:', keyName, 'Hours:', hours, 'Expires:', expiresAt);"
if old_insert in srv:
    srv = srv.replace(old_insert, new_insert)
    print("OK: INSERT log la daray")

# 3. Hubi max_devices column-ka si sax ah
if 'max_devices' not in srv:
    print("WARN: max_devices column lama helin")

with open('server.js', 'w', encoding='utf-8') as f:
    f.write(srv)
print("OK: server.js la keydiyay")

# Verify
with open('server.js') as f:
    chk = f.read()
print("VERIFY calcExpiry:", 'function calcExpiry' in chk)
print("VERIFY max_devices:", 'max_devices' in chk)
print("DHAMMAAN - HAMBALYO!")
