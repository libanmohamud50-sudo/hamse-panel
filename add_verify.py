import os, shutil, secrets
BASE = os.path.expanduser('~/panel-cusub')
os.chdir(BASE)
shutil.copy('server.js', 'server.js.bak_verify_' + secrets.token_hex(3))
print("Backup la sameeyay")

with open('server.js', 'r', encoding='utf-8') as f:
    srv = f.read()

if '/api/verify' in srv:
    print("INFO: /api/verify horey ayuu u jiray")
else:
    v = []
    v.append("")
    v.append("// ===== WORKER VERIFY ENDPOINT =====")
    v.append("app.post('/api/verify', async (req, res) => {")
    v.append("  try {")
    v.append("    const tok = req.headers['x-panel-token'] || '';")
    v.append("    const expected = process.env.PANEL_TOKEN || 'HAMSE_PANEL_TOKEN_2026';")
    v.append("    let okToken = false;")
    v.append("    try { okToken = tok.length === expected.length && crypto.timingSafeEqual(Buffer.from(tok), Buffer.from(expected)); } catch(e) {}")
    v.append("    if (!okToken) return res.status(401).json({ valid: false, error: 'Panel token khaldan' });")
    v.append("    const body = req.body || {};")
    v.append("    const key = body.key;")
    v.append("    const serial = body.serial;")
    v.append("    if (!key) return res.json({ valid: false, reason: 'Key ma jiro' });")
    v.append("    const lic = queryOne('SELECT * FROM licenses WHERE license_key = ?', [key]);")
    v.append("    if (!lic) return res.json({ valid: false, reason: 'Key lama helin' });")
    v.append("    if (lic.status === 'banned') return res.json({ valid: false, reason: 'Key waa la xannibay' });")
    v.append("    if (lic.expires_at && lic.expires_at !== '2099-12-31 23:59:59') {")
    v.append("      if (new Date(lic.expires_at) < new Date()) {")
    v.append("        db.run(\"UPDATE licenses SET status='expired' WHERE id=?\", [lic.id]);")
    v.append("        saveDB();")
    v.append("        return res.json({ valid: false, reason: 'Key wuu dhacay', expire: lic.expires_at });")
    v.append("      }")
    v.append("    }")
    v.append("    if (serial) {")
    v.append("      if (!lic.serial) {")
    v.append("        db.run(\"UPDATE licenses SET serial=?, device_id=?, status='active', used_at=CURRENT_TIMESTAMP WHERE id=?\", [serial, serial, lic.id]);")
    v.append("        saveDB();")
    v.append("      } else if (lic.serial !== serial) {")
    v.append("        return res.json({ valid: false, reason: 'Serial khaldan' });")
    v.append("      }")
    v.append("    }")
    v.append("    res.json({ valid: true, expire: lic.expires_at || '2099-12-31 23:59:59', status: 'active', duration: lic.duration });")
    v.append("  } catch (err) { res.status(500).json({ valid: false, error: err.message }); }")
    v.append("});")
    v.append("")
    block = chr(10).join(v)
    marker = "// ============ FRONTEND ============"
    if marker in srv:
        srv = srv.replace(marker, block + marker)
        print("OK: /api/verify la daray")
    else:
        marker2 = "app.get('*', (req, res)"
        if marker2 in srv:
            srv = srv.replace(marker2, block + marker2)
            print("OK: /api/verify la daray (ka hor app.get)")

with open('server.js', 'w', encoding='utf-8') as f:
    f.write(srv)
print("OK: server.js la keydiyay")

with open('server.js') as f:
    chk = f.read()
print("VERIFY /api/verify:", '/api/verify' in chk)
print("DHAMMAAN - HAMBALYO!")
