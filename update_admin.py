import shutil
import os
import re

# Backup server.js
shutil.copy('server.js', 'server.js.backup')
print('✅ Backup la sameeyay: server.js.backup')

# Read server.js
with open('server.js', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace admin username
content = content.replace(
    "const ADMIN_USERNAME = process.env.ADMIN_USERNAME || 'hamse_admin';",
    "const ADMIN_USERNAME = process.env.ADMIN_USERNAME || 'hamsecheatsvip';"
)

# Replace admin password
content = content.replace(
    "const ADMIN_PASSWORD = process.env.ADMIN_PASSWORD || 'Hamse@Vip2026!';",
    "const ADMIN_PASSWORD = process.env.ADMIN_PASSWORD || 'Hamse@2026VIP';"
)

# Write back
with open('server.js', 'w', encoding='utf-8') as f:
    f.write(content)

print('✅ server.js la cusboonaysiiyay')

# Delete old database
if os.path.exists('hamse_vip.db'):
    os.remove('hamse_vip.db')
    print('✅ Database-kii hore la tirtiray')
else:
    print('ℹ️ Database hore ma jirin')

# Verify changes
with open('server.js', 'r', encoding='utf-8') as f:
    new_content = f.read()

if "hamsecheatsvip" in new_content and "Hamse@2026VIP" in new_content:
    print('✅ Isbeddelka waa la xaqiijiyay')
else:
    print('❌ Isbeddelka lama helin — fadlan hubi')

print('')
print('=== HAMBALYO ===')
print('Hadda socodsii: node server.js')
