import os, shutil, secrets
BASE = os.path.expanduser('~/panel-cusub')
os.chdir(BASE)
shutil.copy('worker.js', 'worker.js.bak_' + secrets.token_hex(3))
print("Backup la sameeyay")

with open('worker.js', 'r', encoding='utf-8') as f:
    code = f.read()

# Beddel expire fallback — ha isticmaalin 2099-12-31
old = 'expire = j.expire || "2099-12-31 23:59:59";'
new = 'expire = j.expire || "";'
if old in code:
    code = code.replace(old, new)
    print("OK: expire fallback la beddelay")

# Beddel marka key valid yahay — ha isticmaalin 2099-12-31
old2 = 'expire = j.expire || "2099-12-31 23:59:59";'
old3 = "expire = j.expire || '2099-12-31 23:59:59';"
new3 = "expire = j.expire || '';"
if old3 in code:
    code = code.replace(old3, new3)
    print("OK: expire fallback (single quote) la beddelay")

with open('worker.js', 'w', encoding='utf-8') as f:
    f.write(code)

# Verify
with open('worker.js') as f:
    chk = f.read()
print("VERIFY: '2099-12-31' count:", chk.count('2099-12-31'))
print("DHAMMAAN - HAMBALYO!")
