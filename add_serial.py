import os, shutil, secrets
BASE = os.path.expanduser('~/panel-cusub')
os.chdir(BASE)
shutil.copy('server.js', 'server.js.bak_serial_' + secrets.token_hex(3))
print("Backup la sameeyay")

with open('server.js', 'r', encoding='utf-8') as f:
    srv = f.read()

# 1. Ku dar serial TEXT table-ka licenses (CREATE TABLE)
old_create = "device_id TEXT, duration TEXT, expires_at DATETIME"
new_create = "device_id TEXT, serial TEXT, duration TEXT, expires_at DATETIME"
if old_create in srv:
    srv = srv.replace(old_create, new_create)
    print("OK: serial column la daray CREATE TABLE")
else:
    print("WARN: CREATE TABLE licenses lama helin")

# 2. Ku dar ALTER TABLE si column-ka loogu daro DB-ga hore (muhiim!)
if 'ALTER TABLE licenses ADD COLUMN serial' not in srv:
    marker = 'CREATE TABLE IF NOT EXISTS licenses'
    idx = srv.find(marker)
    if idx != -1:
        # Ka dib line-ka CREATE TABLE licenses, ku dar try/catch ALTER TABLE
        end_idx = srv.find('");', idx) + 3
        alter = "\n\n  try { db.run(\"ALTER TABLE licenses ADD COLUMN serial TEXT\"); } catch (e) {}"
        srv = srv[:end_idx] + alter + srv[end_idx:]
        print("OK: ALTER TABLE serial la daray")

# 3. Hubi in crypto module uu jiro (waa loo baahan yahay /api/verify)
if "const crypto = require('crypto');" not in srv:
    srv = srv.replace(
        "const bcrypt = require('bcryptjs');",
        "const bcrypt = require('bcryptjs');\nconst crypto = require('crypto');"
    )
    print("OK: crypto module la daray")

with open('server.js', 'w', encoding='utf-8') as f:
    f.write(srv)
print("OK: server.js la keydiyay")

with open('server.js') as f:
    chk = f.read()
print("VERIFY serial TEXT:", 'serial TEXT' in chk)
print("VERIFY ALTER TABLE:", 'ADD COLUMN serial' in chk)
print("VERIFY crypto:", "require('crypto')" in chk)
print("VERIFY /api/verify:", '/api/verify' in chk)
print("DHAMMAAN - HAMBALYO!")
