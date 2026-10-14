import os, shutil, secrets
BASE = os.path.expanduser('~/panel-cusub')
os.chdir(BASE)
shutil.copy('worker.js', 'worker.js.bak_' + secrets.token_hex(3))
print("Backup la sameeyay")

with open('worker.js', 'r', encoding='utf-8') as f:
    code = f.read()

# Ku beddel PANEL_URL iyo PANEL_TOKEN
import re
code = re.sub(r'env\.PANEL_URL \|\| "[^"]*"', 'env.PANEL_URL || "https://hamse-panel-production.up.railway.app"', code)
code = re.sub(r'env\.PANEL_URL \|\| \'[^\']*\'', 'env.PANEL_URL || "https://hamse-panel-production.up.railway.app"', code)

with open('worker.js', 'w', encoding='utf-8') as f:
    f.write(code)
print("OK: worker.js la cusboonaysiiyay")

# Hubi
with open('worker.js') as f:
    chk = f.read()
if 'hamse-panel-production.up.railway.app' in chk:
    print("VERIFY: PANEL_URL wuu jiraa")
else:
    print("WARN: PANEL_URL lama helin — hubi manual")

print("DHAMMAAN - HAMBALYO!")
