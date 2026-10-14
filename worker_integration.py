import os, shutil, secrets

BASE = os.path.expanduser('~/panel-cusub')
os.chdir(BASE)

# Backup
backup_dir = 'backup_worker_integration_' + secrets.token_hex(3)
os.makedirs(backup_dir, exist_ok=True)
for f in ['server.js', 'public/index.html']:
    if os.path.exists(f):
        shutil.copy(f, os.path.join(backup_dir, os.path.basename(f)))
print("Backup:", backup_dir)

# ============================================
# 1. PATCH server.js — Ku dar Worker endpoints
# ============================================
with open('server.js', 'r', encoding='utf-8') as f:
    srv = f.read()

if '/api/worker/code' not in srv:
    worker_code = []
    worker_code.append("")
    worker_code.append("// ===== CLOUDFLARE WORKER ENDPOINTS =====")
    worker_code.append("const CF_API = 'https://api.cloudflare.com/client/v4';")
    worker_code.append("")
    worker_code.append("// GET /api/worker/code")
    worker_code.append("app.get('/api/worker/code', authMiddleware, adminMiddleware, async (req, res) => {")
    worker_code.append("  try {")
    worker_code.append("    const token = process.env.CLOUDFLARE_API_TOKEN;")
    worker_code.append("    const accountId = process.env.CLOUDFLARE_ACCOUNT_ID;")
    worker_code.append("    const workerName = process.env.CLOUDFLARE_WORKER_NAME || 'a';")
    worker_code.append("    if (!token || !accountId) return res.status(400).json({ success: false, error: 'Cloudflare credentials ma jiro' });")
    worker_code.append("    const url = CF_API + '/accounts/' + accountId + '/workers/scripts/' + workerName;")
    worker_code.append("    const r = await fetch(url, { headers: { 'Authorization': 'Bearer ' + token } });")
    worker_code.append("    const text = await r.text();")
    worker_code.append("    if (r.ok) {")
    worker_code.append("      let cleanCode = text;")
    worker_code.append("      const exportIdx = cleanCode.indexOf('export default');")
    worker_code.append("      if (exportIdx > 0) cleanCode = cleanCode.substring(exportIdx);")
    worker_code.append("      const lastBoundary = cleanCode.lastIndexOf(String.fromCharCode(10) + '--');")
    worker_code.append("      if (lastBoundary > 0) cleanCode = cleanCode.substring(0, lastBoundary);")
    worker_code.append("      cleanCode = cleanCode.trim();")
    worker_code.append("      res.json({ success: true, code: cleanCode, worker: workerName });")
    worker_code.append("    } else {")
    worker_code.append("      res.status(r.status).json({ success: false, error: text });")
    worker_code.append("    }")
    worker_code.append("  } catch (err) { res.status(500).json({ success: false, error: err.message }); }")
    worker_code.append("});")
    worker_code.append("")
    worker_code.append("// POST /api/worker/code (Deploy)")
    worker_code.append("app.post('/api/worker/code', authMiddleware, adminMiddleware, async (req, res) => {")
    worker_code.append("  try {")
    worker_code.append("    const token = process.env.CLOUDFLARE_API_TOKEN;")
    worker_code.append("    const accountId = process.env.CLOUDFLARE_ACCOUNT_ID;")
    worker_code.append("    const workerName = process.env.CLOUDFLARE_WORKER_NAME || 'a';")
    worker_code.append("    const code = req.body.code;")
    worker_code.append("    if (!token || !accountId) return res.status(400).json({ success: false, error: 'Cloudflare credentials ma jiro' });")
    worker_code.append("    if (!code) return res.status(400).json({ success: false, error: 'Code ma jiro' });")
    worker_code.append("    const url = CF_API + '/accounts/' + accountId + '/workers/scripts/' + workerName;")
    worker_code.append("    const form = new FormData();")
    worker_code.append("    form.append('metadata', new Blob([JSON.stringify({ main_module: 'worker.js', compatibility_date: '2024-01-01' })], { type: 'application/json' }), 'metadata.json');")
    worker_code.append("    form.append('worker.js', new Blob([code], { type: 'application/javascript+module' }), 'worker.js');")
    worker_code.append("    const r = await fetch(url, { method: 'PUT', headers: { 'Authorization': 'Bearer ' + token }, body: form });")
    worker_code.append("    const data = await r.json();")
    worker_code.append("    if (r.ok && data.success) {")
    worker_code.append("      res.json({ success: true, message: 'Worker la cusboonaysiiyay!', data: data.result });")
    worker_code.append("    } else {")
    worker_code.append("      res.status(r.status).json({ success: false, error: JSON.stringify(data.errors || data) });")
    worker_code.append("    }")
    worker_code.append("  } catch (err) { res.status(500).json({ success: false, error: err.message }); }")
    worker_code.append("});")
    worker_code.append("")
    worker_code.append("// GET /api/worker/status")
    worker_code.append("app.get('/api/worker/status', authMiddleware, adminMiddleware, async (req, res) => {")
    worker_code.append("  try {")
    worker_code.append("    const token = process.env.CLOUDFLARE_API_TOKEN;")
    worker_code.append("    const accountId = process.env.CLOUDFLARE_ACCOUNT_ID;")
    worker_code.append("    const workerName = process.env.CLOUDFLARE_WORKER_NAME || 'a';")
    worker_code.append("    if (!token || !accountId) return res.json({ success: true, online: false, error: 'Cloudflare credentials ma jiro' });")
    worker_code.append("    const url = CF_API + '/accounts/' + accountId + '/workers/scripts/' + workerName;")
    worker_code.append("    const r = await fetch(url, { headers: { 'Authorization': 'Bearer ' + token } });")
    worker_code.append("    const text = await r.text();")
    worker_code.append("    const workerUrl = 'https://a.dirxx.workers.dev';")
    worker_code.append("    let workerOnline = false;")
    worker_code.append("    let responseTime = 0;")
    worker_code.append("    try {")
    worker_code.append("      const start = Date.now();")
    worker_code.append("      const wr = await fetch(workerUrl, { method: 'HEAD' });")
    worker_code.append("      responseTime = Date.now() - start;")
    worker_code.append("      workerOnline = wr.ok;")
    worker_code.append("    } catch (e) {}")
    worker_code.append("    if (r.ok) {")
    worker_code.append("      res.json({ success: true, online: true, worker_name: workerName, worker_url: workerUrl, worker_online: workerOnline, response_time: responseTime + 'ms', code_length: text.length, account_id: accountId });")
    worker_code.append("    } else {")
    worker_code.append("      res.json({ success: true, online: false, error: 'Worker code lama helin' });")
    worker_code.append("    }")
    worker_code.append("  } catch (err) { res.status(500).json({ success: false, error: err.message }); }")
    worker_code.append("});")
    worker_code.append("")
    worker_code.append("// ============ FRONTEND ============")

    patch = "\n".join(worker_code)
    srv = srv.replace("// ============ FRONTEND ============", patch)
    print("OK: Worker endpoints la daray")
else:
    print("INFO: Worker endpoints horey ayay u jireen")

with open('server.js', 'w', encoding='utf-8') as f:
    f.write(srv)
print("OK: server.js la keydiyay")

# ============================================
# 2. Update .env
# ============================================
env_lines = []
if os.path.exists('.env'):
    with open('.env', 'r') as f:
        env_lines = f.read().splitlines()

env_dict = {}
for line in env_lines:
    if '=' in line and not line.strip().startswith('#'):
        k, v = line.split('=', 1)
        env_dict[k.strip()] = v.strip()

if 'CLOUDFLARE_API_TOKEN' not in env_dict:
    env_dict['CLOUDFLARE_API_TOKEN'] = 'cfut_YOUR_TOKEN_HERE'
if 'CLOUDFLARE_ACCOUNT_ID' not in env_dict:
    env_dict['CLOUDFLARE_ACCOUNT_ID'] = 'YOUR_ACCOUNT_ID_HERE'
if 'CLOUDFLARE_WORKER_NAME' not in env_dict:
    env_dict['CLOUDFLARE_WORKER_NAME'] = 'a'

with open('.env', 'w') as f:
    for k, v in env_dict.items():
        f.write(k + '=' + v + '\n')
print("OK: .env la cusboonaysiiyay")

# ============================================
# 3. PATCH public/index.html — Ku dar Worker page
# ============================================
with open('public/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 3A. Ku dar sidebar link
if 'nav-worker' not in html:
    old_link = '<a onclick="showSection(\'server\')" id="nav-server">'
    if old_link not in html:
        old_link = '<a onclick="showSection(\'users\')" id="nav-users">'
        new_link = '<a onclick="showSection(\'worker\')" id="nav-worker">\u2601\ufe0f Cloudflare Worker</a>\n    ' + old_link
    else:
        new_link = old_link.replace('id="nav-server">', 'id="nav-server">') + '\n    <a onclick="showSection(\'worker\')" id="nav-worker">\u2601\ufe0f Cloudflare Worker</a>'
        # Better: insert after server link
        idx = html.find(old_link)
        if idx != -1:
            end_idx = html.find('</a>', idx) + 4
            html = html[:end_idx] + '\n    <a onclick="showSection(\'worker\')" id="nav-worker">\u2601\ufe0f Cloudflare Worker</a>' + html[end_idx:]
            print("OK: Sidebar link Worker la daray")

# 3B. Ku dar section-worker markup
if 'id="section-worker"' not in html:
    section = []
    section.append('<div id="section-worker" class="hidden">')
    section.append('  <div class="card">')
    section.append('    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px;">')
    section.append('      <h3 style="margin:0;">\u2601\ufe0f Cloudflare Worker</h3>')
    section.append('      <button class="btn-sm btn-primary" onclick="loadWorkerPage()">\U0001f504 Refresh</button>')
    section.append('    </div>')
    section.append('    <div class="grid" style="margin-bottom:16px;">')
    section.append('      <div class="card" style="margin:0;"><h3>Status</h3><div class="big" id="cw-status" style="font-size:20px;">-</div></div>')
    section.append('      <div class="card" style="margin:0;"><h3>Code Size</h3><div class="big" id="cw-code-size" style="font-size:20px;">-</div></div>')
    section.append('      <div class="card" style="margin:0;"><h3>Response Time</h3><div class="big" id="cw-response" style="font-size:20px;">-</div></div>')
    section.append('      <div class="card" style="margin:0;"><h3>Worker URL</h3><div class="big" id="cw-url" style="font-size:12px;word-break:break-all;">-</div></div>')
    section.append('    </div>')
    section.append('  </div>')
    section.append('  <div class="card">')
    section.append('    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;">')
    section.append('      <h3 style="margin:0;">\U0001f4bb Worker Code</h3>')
    section.append('      <div class="toolbar" style="margin:0;">')
    section.append('        <button class="btn-sm btn-primary" onclick="selectAllWorkerCode()">Select All</button>')
    section.append('        <button class="btn-sm btn-warn" onclick="removeAllWorkerCode()">Remove All</button>')
    section.append('        <button class="btn-sm btn-success" onclick="saveWorkerCode()" id="cw-save-btn">\U0001f680 Deploy</button>')
    section.append('      </div>')
    section.append('    </div>')
    section.append('    <div class="editor-wrap">')
    section.append('      <div class="line-numbers" id="cwLineNumbers">1</div>')
    section.append('      <textarea id="cw-code" class="code-input" spellcheck="false" placeholder="// Worker code halkan..." oninput="updateLineNumbers(\'cw-code\', \'cwLineNumbers\')" onscroll="syncScroll(\'cw-code\', \'cwLineNumbers\')"></textarea>')
    section.append('    </div>')
    section.append('    <div id="cw-result" style="margin-top:12px;"></div>')
    section.append('  </div>')
    section.append('</div>')

    section_html = "\n".join(section)
    marker = '<div id="section-status" class="hidden">'
    if marker in html:
        html = html.replace(marker, section_html + '\n' + marker)
        print("OK: Section Worker la daray")

# 3C. Ku dar JS functions
if 'function loadWorkerPage' not in html:
    js = []
    js.append("")
    js.append("// ===== CLOUDFLARE WORKER PAGE =====")
    js.append("async function loadWorkerPage() {")
    js.append("  try {")
    js.append("    var t = localStorage.getItem('hamse_token');")
    js.append("    var r = await fetch('/api/worker/status', { headers: { 'Authorization': 'Bearer ' + t } });")
    js.append("    var d = await r.json();")
    js.append("    var statusEl = document.getElementById('cw-status');")
    js.append("    var sizeEl = document.getElementById('cw-code-size');")
    js.append("    var respEl = document.getElementById('cw-response');")
    js.append("    var urlEl = document.getElementById('cw-url');")
    js.append("    if (d.success && d.online) {")
    js.append("      statusEl.innerHTML = '<span style=\"color:#0a7a3a;\">\u25cf</span> Online';")
    js.append("      sizeEl.textContent = (d.code_length || 0) + ' bytes';")
    js.append("      respEl.textContent = (d.response_time || 'N/A');")
    js.append("      urlEl.textContent = (d.worker_url || 'N/A');")
    js.append("    } else {")
    js.append("      statusEl.innerHTML = '<span style=\"color:#a02020;\">\u25cf</span> Offline';")
    js.append("      sizeEl.textContent = '0 bytes';")
    js.append("      respEl.textContent = 'N/A';")
    js.append("      urlEl.textContent = 'N/A';")
    js.append("    }")
    js.append("    var cr = await fetch('/api/worker/code', { headers: { 'Authorization': 'Bearer ' + t } });")
    js.append("    var cd = await cr.json();")
    js.append("    var codeEl = document.getElementById('cw-code');")
    js.append("    if (cd.success && codeEl) {")
    js.append("      codeEl.value = cd.code || '';")
    js.append("      updateLineNumbers('cw-code', 'cwLineNumbers');")
    js.append("    } else if (codeEl) {")
    js.append("      codeEl.value = '// Khalad: ' + (cd.error || 'Code lama helin');")
    js.append("      updateLineNumbers('cw-code', 'cwLineNumbers');")
    js.append("    }")
    js.append("  } catch (e) { showToast('Worker page error: ' + e.message, 'error'); }")
    js.append("}")
    js.append("")
    js.append("function selectAllWorkerCode() {")
    js.append("  var ta = document.getElementById('cw-code');")
    js.append("  ta.focus(); ta.select();")
    js.append("  showToast('Worker code la doortay', 'info');")
    js.append("}")
    js.append("")
    js.append("function removeAllWorkerCode() {")
    js.append("  if (!confirm('Tirtir worker code oo dhan?')) return;")
    js.append("  document.getElementById('cw-code').value = '';")
    js.append("  updateLineNumbers('cw-code', 'cwLineNumbers');")
    js.append("  showToast('Worker code la tirtiray', 'info');")
    js.append("}")
    js.append("")
    js.append("async function saveWorkerCode() {")
    js.append("  var btn = document.getElementById('cw-save-btn');")
    js.append("  var code = document.getElementById('cw-code').value;")
    js.append("  var result = document.getElementById('cw-result');")
    js.append("  if (!code) { showToast('Code ma jiro', 'error'); return; }")
    js.append("  btn.disabled = true;")
    js.append("  btn.innerHTML = '\u23f3 Deploying...';")
    js.append("  result.innerHTML = '<p style=\"color:#6b7c93;\">Worker-ka waa la deploy-gareynayaa...</p>';")
    js.append("  try {")
    js.append("    var t = localStorage.getItem('hamse_token');")
    js.append("    var r = await fetch('/api/worker/code', {")
    js.append("      method: 'POST',")
    js.append("      headers: { 'Authorization': 'Bearer ' + t, 'Content-Type': 'application/json' },")
    js.append("      body: JSON.stringify({ code: code })")
    js.append("    });")
    js.append("    var d = await r.json();")
    js.append("    if (d.success) {")
    js.append("      result.innerHTML = '<div style=\"padding:15px;background:#d4f4dd;border:1px solid #0a7a3a;border-radius:10px;\"><strong style=\"color:#0a7a3a;\">\u2705 Deploy Successful!</strong><div style=\"font-size:13px;color:#6b7c93;margin-top:6px;\">' + (d.message || 'Worker la cusboonaysiiyay') + '</div></div>';")
    js.append("      showToast('Worker la deploy-gareeyay!', 'success');")
    js.append("      setTimeout(function() { loadWorkerPage(); }, 1500);")
    js.append("    } else {")
    js.append("      result.innerHTML = '<div style=\"padding:15px;background:#fde0e0;border:1px solid #a02020;border-radius:10px;\"><strong style=\"color:#a02020;\">\u274c Deploy Failed!</strong><div style=\"font-size:13px;color:#6b7c93;margin-top:6px;word-break:break-all;\">' + (d.error || 'Unknown') + '</div></div>';")
    js.append("      showToast('Deploy wuu guuldareystay', 'error');")
    js.append("    }")
    js.append("  } catch (e) {")
    js.append("    result.innerHTML = '<div style=\"padding:15px;background:#fde0e0;border-radius:10px;\"><strong style=\"color:#a02020;\">Error: ' + e.message + '</strong></div>';")
    js.append("  }")
    js.append("  btn.disabled = false;")
    js.append("  btn.innerHTML = '\U0001f680 Deploy';")
    js.append("}")
    js.append("")
    js.append("(function() {")
    js.append("  var orig = window.showSection;")
    js.append("  window.showSection = function(name) {")
    js.append("    if (orig) orig(name);")
    js.append("    if (name === 'worker') loadWorkerPage();")
    js.append("    if (name === 'server') loadServerFiles();")
    js.append("  };")
    js.append("})();")

    js_block = "\n".join(js)
    marker = "if (TOKEN && CURRENT_USER) enterPanel();"
    if marker in html:
        html = html.replace(marker, js_block + "\n" + marker)
        print("OK: Worker JS la daray")

with open('public/index.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("OK: public/index.html la keydiyay")

print("")
print("========================================")
print("DHAMMAAN - HAMBALYO!")
print("========================================")
print("")
print("TALLAABADA XIGTA:")
print("  1. Fur .env oo geli:")
print("     CLOUDFLARE_API_TOKEN=cfut_...")
print("     CLOUDFLARE_ACCOUNT_ID=...")
print("     CLOUDFLARE_WORKER_NAME=a")
print("  2. node server.js")
print("  3. http://localhost:3000")
print("  4. Login: hamsecheatsvip / Hamse@2026VIP")
print("  5. Sidebar -> Cloudflare Worker")
