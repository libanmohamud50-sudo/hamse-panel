import os, shutil, secrets

BASE = os.path.expanduser('~/panel-cusub')
os.chdir(BASE)

# Backup
shutil.copy('public/index.html', 'public/index.html.fix_' + secrets.token_hex(3))
print("Backup la sameeyay")

with open('public/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Tir `</body>` iyo `</html>` dhammaadka haddii ay laba jeer ku jiraan
count_body = html.count('</body>')
count_html = html.count('</html>')
print("</body> count:", count_body)
print("</html> count:", count_html)

# Tirtir dhammaan </body> iyo </html>
html = html.replace('</body>', '')
html = html.replace('</html>', '')

# Ku dar hal </body> iyo </html> dhammaadka
# Laakiin haddii <script> ugu dambeeya ku jiro, waa in aan <script> tag furan hayn
# Hubi <script> furan
script_open = html.count('<script>')
script_close = html.count('</script>')
print("<script> count:", script_open)
print("</script> count:", script_close)

# Haddii <script> furan uu ka badan yahay </script>, xir
if script_open > script_close:
    html += '</script>\n'

# Ku dar </body> iyo </html>
html = html.rstrip() + '\n</body>\n</html>\n'

with open('public/index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("OK: HTML la hagaajiyay")

# Verify
with open('public/index.html', 'r', encoding='utf-8') as f:
    check = f.read()
print("Final </body> count:", check.count('</body>'))
print("Final </html> count:", check.count('</html>'))
print("Final <script> count:", check.count('<script>'))
print("Final </script> count:", check.count('</script>'))

if 'function loadServerFiles' in check:
    print("OK: loadServerFiles wuu jiraa")

print("")
print("========================================")
print("DHAMMAAN - HAMBALYO!")
print("========================================")
print("Hadda: node server.js")
