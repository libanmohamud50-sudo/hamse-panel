import os, shutil, secrets

BASE = os.path.expanduser('~/panel-cusub')
os.chdir(BASE)

# Backup
shutil.copy('public/index.html', 'public/index.html.fixall_' + secrets.token_hex(3))
print("Backup la sameeyay")

with open('public/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# ============================================
# 1. TIRTIR DHAMMAAN </body>, </html>, </script> ee DHAXDA
# ============================================
# Raadi </body> ugu horreeya
first_body = html.find('</body>')
if first_body != -1:
    # Gooy wax kasta oo ka dambeeya </body> ugu horreeya
    html = html[:first_body]
    print("OK: wax kasta oo ka dambeeya </body> ugu horreeya la tirtiray")

# Tirtir </script> dhammaadka (haddii uu furan yahay)
# Kadib ku dar </body> iyo </html> hal mar

# ============================================
# 2. TIRTIR QAYBTA SERVER-SECTION HORE
# ============================================
start = html.find('<div id="section-server"')
end = html.find('<div id="section-status"')

if start != -1 and end != -1 and end > start:
    html = html[:start] + html[end:]
    print("OK: Section server hore la tirtiray")

# ============================================
# 3. KUDAR SECTION CUSUB (Server Edit + Worker Editor)
# ============================================
section_new = []
section_new.append('<div id="section-server" class="hidden">')

# A. Server Files Editor
section_new.append('  <div class="card">')
section_new.append('    <h3>Server Files (Edit Code)</h3>')
section_new.append('    <p style="margin:8px 0;color:#6b7c93;font-size:13px;">Fayl dooro, code beddel, kadibna Save.</p>')
section_new.append('    <div class="file-list" id="fileList"></div>')
section_new.append('    <div class="form-group"><label>Faylka la doortay</label><input type="text" id="currentFile" readonly style="background:#f0f4f8;"></div>')
section_new.append('    <div class="toolbar">')
section_new.append('      <button class="btn-sm btn-primary" onclick="selectAllCode()">Select All</button>')
section_new.append('      <button class="btn-sm btn-warn" onclick="removeAllCode()">Remove All</button>')
section_new.append('      <button class="btn-sm btn-success" onclick="copyCode()">Copy</button>')
section_new.append('      <button class="btn-sm btn-outline" onclick="pasteCode()">Paste</button>')
section_new.append('    </div>')
section_new.append('    <div class="editor-wrap">')
section_new.append('      <div class="line-numbers" id="lineNumbers">1</div>')
section_new.append('      <textarea id="codeEditor" class="code-input" spellcheck="false" placeholder="Dooro fayl..." oninput="updateLineNumbers(\'codeEditor\', \'lineNumbers\')" onscroll="syncScroll(\'codeEditor\', \'lineNumbers\')"></textarea>')
section_new.append('    </div>')
section_new.append('    <div class="worker-actions">')
section_new.append('      <button class="btn btn-primary" style="width:auto;padding:10px 20px;" onclick="saveFile()">Save File</button>')
section_new.append('      <button class="btn btn-outline" style="width:auto;padding:10px 20px;" onclick="loadDeployLog()">Deploy Log</button>')
section_new.append('    </div>')
section_new.append('  </div>')

# B. Cloudflare Worker Editor (sida ABDI VIP PANEL)
section_new.append('  <div class="card">')
section_new.append('    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;">')
section_new.append('      <h3 style="margin:0;">Cloudflare Worker</h3>')
section_new.append('      <button class="btn-sm btn-primary" onclick="deployWorker()">Deploy</button>')
section_new.append('    </div>')
section_new.append('    <p style="margin:8px 0;color:#6b7c93;font-size:13px;">Worker code toos ka edit, kadibna Deploy riix.</p>')
section_new.append('    <div class="worker-stats" id="workerStats" style="display:flex;gap:12px;margin-bottom:12px;flex-wrap:wrap;">')
section_new.append('      <div class="stat-box"><div style="font-size:11px;color:#6b7c93;">Status</div><div id="wsStatus" style="font-weight:700;color:#0a7a3a;">Online</div></div>')
section_new.append('      <div class="stat-box"><div style="font-size:11px;color:#6b7c93;">Code Size</div><div id="wsSize" style="font-weight:700;">-</div></div>')
section_new.append('      <div class="stat-box"><div style="font-size:11px;color:#6b7c93;">Worker URL</div><div id="wsUrl" style="font-weight:700;font-size:11px;">-</div></div>')
section_new.append('    </div>')
section_new.append('    <div class="toolbar">')
section_new.append('      <button class="btn-sm btn-primary" onclick="selectAllWorker()">Select All</button>')
section_new.append('      <button class="btn-sm btn-warn" onclick="removeAllWorker()">Remove All</button>')
section_new.append('      <button class="btn-sm btn-outline" onclick="reloadWorker()">Reload</button>')
section_new.append('    </div>')
section_new.append('    <div class="editor-wrap">')
section_new.append('      <div class="line-numbers" id="workerLineNumbers">1</div>')
section_new.append('      <textarea id="workerEditor" class="code-input" spellcheck="false" placeholder="// worker.js code halkan..." oninput="updateLineNumbers(\'workerEditor\', \'workerLineNumbers\')" onscroll="syncScroll(\'workerEditor\', \'workerLineNumbers\')"></textarea>')
section_new.append('    </div>')
section_new.append('    <div class="worker-actions">')
section_new.append('      <button class="btn btn-primary" style="width:auto;padding:10px 20px;" onclick="saveWorkerCode()">Save Worker Code</button>')
section_new.append('      <button class="btn btn-success" style="width:auto;padding:10px 20px;" onclick="deployWorker()">Deploy</button>')
section_new.append('    </div>')
section_new.append('  </div>')

# C. Cloudflare Credentials
section_new.append('  <div class="card">')
section_new.append('    <h3>Cloudflare Credentials</h3>')
section_new.append('    <div class="form-group"><label>Worker URL</label><input type="text" id="envWorkerUrl" placeholder="https://a.hamse.workers.dev"></div>')
section_new.append('    <div class="form-group"><label>Cloudflare Account ID</label><input type="text" id="envCfAccount"></div>')
section_new.append('    <div class="form-group"><label>Cloudflare API Token</label><input type="password" id="envCfToken"></div>')
section_new.append('    <div class="form-group"><label>Worker Name</label><input type="text" id="envCfWorkerName" placeholder="a"></div>')
section_new.append('    <div class="form-group"><label>PANEL_TOKEN</label><input type="text" id="envPanelToken"></div>')
section_new.append('    <div class="form-group"><label>Railway Webhook URL</label><input type="text" id="envRailwayWebhook"></div>')
section_new.append('    <button class="btn btn-primary" style="width:auto;padding:10px 20px;" onclick="saveAllEnv()">Save All Env</button>')
section_new.append('  </div>')

# D. Deploy Log
section_new.append('  <div class="card" id="deployLogCard" style="display:none;">')
section_new.append('    <h3>Deploy Log</h3>')
section_new.append('    <div id="deployLogContent" style="margin-top:12px;font-family:monospace;font-size:12px;"></div>')
section_new.append('  </div>')
section_new.append('</div>')

section_html = "\n".join(section_new)

# Kudar section-server kahor section-status
marker = '<div id="section-status" class="hidden">'
if marker in html:
    html = html.replace(marker, section_html + '\n' + marker)
    print("OK: Section cusub la daray")

# ============================================
# 4. KUDAR CSS (line numbers, code editor)
# ============================================
if '.code-input' not in html:
    css_add = (
        "\n.code-editor { width: 100%; min-height: 400px; font-family: 'Courier New', monospace; font-size: 13px; padding: 16px; border: 2px solid #d8e0ec; border-radius: 10px; background: #0a1f44; color: #d4e4ff; line-height: 1.5; resize: vertical; }\n"
        ".file-list { display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 12px; }\n"
        ".file-list button { padding: 8px 16px; border: 2px solid #d8e0ec; background: #fff; border-radius: 8px; cursor: pointer; font-weight: 600; font-size: 13px; }\n"
        ".file-list button.active { background: #0a1f44; color: #fff; border-color: #0a1f44; }\n"
        ".file-list button.missing { opacity: 0.4; }\n"
        ".toolbar { display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 12px; }\n"
        ".editor-wrap { position: relative; border: 2px solid #d8e0ec; border-radius: 10px; background: #0a1f44; overflow: hidden; }\n"
        ".line-numbers { position: absolute; left: 0; top: 0; bottom: 0; width: 50px; background: #061530; color: #4a6a9a; font-family: 'Courier New', monospace; font-size: 13px; line-height: 1.5; padding: 16px 8px; text-align: right; overflow: hidden; user-select: none; }\n"
        ".code-input { width: 100%; min-height: 400px; font-family: 'Courier New', monospace; font-size: 13px; line-height: 1.5; padding: 16px 16px 16px 60px; border: none; background: transparent; color: #d4e4ff; resize: vertical; outline: none; white-space: pre; overflow-wrap: normal; overflow-x: auto; }\n"
        ".worker-actions { display: flex; gap: 8px; flex-wrap: wrap; margin-top: 12px; }\n"
        ".stat-box { background: #f0f4f8; padding: 10px 14px; border-radius: 8px; min-width: 100px; }\n"
    )
    html = html.replace('</style>', css_add + '</style>')
    print("OK: CSS la daray")

# ============================================
# 5. KUDAR JS FUNCTIONS
# ============================================
js_lines = []
js_lines.append("")
js_lines.append("<script>")
js_lines.append("function updateLineNumbers(taId, lnId) {")
js_lines.append("  var ta = document.getElementById(taId);")
js_lines.append("  var ln = document.getElementById(lnId);")
js_lines.append("  if (!ta || !ln) return;")
js_lines.append("  var n = ta.value.split(String.fromCharCode(10)).length;")
js_lines.append("  var s = '';")
js_lines.append("  for (var i = 1; i <= n; i++) s += i + String.fromCharCode(10);")
js_lines.append("  ln.textContent = s;")
js_lines.append("}")
js_lines.append("function syncScroll(taId, lnId) {")
js_lines.append("  var ta = document.getElementById(taId);")
js_lines.append("  var ln = document.getElementById(lnId);")
js_lines.append("  if (ta && ln) ln.scrollTop = ta.scrollTop;")
js_lines.append("}")
js_lines.append("var CURRENT_FILE = '';")
js_lines.append("async function loadServerFiles() {")
js_lines.append("  try {")
js_lines.append("    var data = await api('/api/admin/server/files');")
js_lines.append("    var fl = document.getElementById('fileList');")
js_lines.append("    if (fl) fl.innerHTML = data.files.map(function(f) {")
js_lines.append("      var cls = f.missing ? 'missing' : '';")
js_lines.append("      var label = f.name + (f.missing ? ' (ma jiro)' : '');")
js_lines.append("      return '<button onclick=\"loadFile(\\'' + f.name + '\\')\" class=\"' + cls + '\">' + label + '</button>';")
js_lines.append("    }).join('');")
js_lines.append("  } catch (e) { showToast(e.message, 'error'); }")
js_lines.append("  loadWorkerCode();")
js_lines.append("  loadEnv();")
js_lines.append("}")
js_lines.append("async function loadFile(name) {")
js_lines.append("  try {")
js_lines.append("    var data = await api('/api/admin/server/file?name=' + encodeURIComponent(name));")
js_lines.append("    document.getElementById('currentFile').value = data.name;")
js_lines.append("    document.getElementById('codeEditor').value = data.content;")
js_lines.append("    CURRENT_FILE = name;")
js_lines.append("    updateLineNumbers('codeEditor', 'lineNumbers');")
js_lines.append("    showToast('Fayl la furay: ' + name, 'success');")
js_lines.append("  } catch (e) { showToast(e.message, 'error'); }")
js_lines.append("}")
js_lines.append("function selectAllCode() { var ta = document.getElementById('codeEditor'); ta.focus(); ta.select(); showToast('La doortay', 'info'); }")
js_lines.append("function removeAllCode() { if (!confirm('Tirtir?')) return; document.getElementById('codeEditor').value = ''; updateLineNumbers('codeEditor', 'lineNumbers'); showToast('La tirtiray', 'info'); }")
js_lines.append("function copyCode() { document.getElementById('codeEditor').select(); document.execCommand('copy'); showToast('Copy', 'success'); }")
js_lines.append("async function pasteCode() { try { var t = await navigator.clipboard.readText(); document.getElementById('codeEditor').value = t; updateLineNumbers('codeEditor', 'lineNumbers'); showToast('Paste', 'success'); } catch (e) { showToast('Paste fail', 'error'); } }")
js_lines.append("async function saveFile() {")
js_lines.append("  var name = document.getElementById('currentFile').value;")
js_lines.append("  var content = document.getElementById('codeEditor').value;")
js_lines.append("  if (!name) return showToast('Dooro fayl', 'error');")
js_lines.append("  try { await api('/api/admin/server/file', 'POST', { name: name, content: content }); showToast('La keydiyay', 'success'); }")
js_lines.append("  catch (e) { showToast(e.message, 'error'); }")
js_lines.append("}")
js_lines.append("async function loadWorkerCode() {")
js_lines.append("  try {")
js_lines.append("    var data = await api('/api/admin/worker/code');")
js_lines.append("    var we = document.getElementById('workerEditor');")
js_lines.append("    if (we) { we.value = data.code; updateLineNumbers('workerEditor', 'workerLineNumbers'); }")
js_lines.append("    var ws = document.getElementById('wsStatus');")
js_lines.append("    if (ws) ws.textContent = 'Online';")
js_lines.append("    var sz = document.getElementById('wsSize');")
js_lines.append("    if (sz) sz.textContent = (data.code ? data.code.length : 0) + ' bytes';")
js_lines.append("    var u = document.getElementById('wsUrl');")
js_lines.append("    if (u) u.textContent = (document.getElementById('envWorkerUrl') ? document.getElementById('envWorkerUrl').value : '') || '-';")
js_lines.append("  } catch (e) { showToast('Worker load: ' + e.message, 'error'); }")
js_lines.append("}")
js_lines.append("function selectAllWorker() { var ta = document.getElementById('workerEditor'); ta.focus(); ta.select(); showToast('La doortay', 'info'); }")
js_lines.append("function removeAllWorker() { if (!confirm('Tirtir?')) return; document.getElementById('workerEditor').value = ''; updateLineNumbers('workerEditor', 'workerLineNumbers'); showToast('La tirtiray', 'info'); }")
js_lines.append("function reloadWorker() { loadWorkerCode(); showToast('Dib loo soo dejiyay', 'info'); }")
js_lines.append("async function saveWorkerCode() {")
js_lines.append("  var code = document.getElementById('workerEditor').value;")
js_lines.append("  try { await api('/api/admin/worker/code', 'POST', { code: code }); showToast('Worker code la keydiyay', 'success'); }")
js_lines.append("  catch (e) { showToast(e.message, 'error'); }")
js_lines.append("}")
js_lines.append("async function deployWorker() {")
js_lines.append("  if (!confirm('Deploy Worker Cloudflare?')) return;")
js_lines.append("  try {")
js_lines.append("    showToast('Deploy socda...', 'info');")
js_lines.append("    await saveWorkerCode();")
js_lines.append("    var data = await api('/api/admin/server/deploy', 'POST');")
js_lines.append("    var r = data.result;")
js_lines.append("    var msg = '';")
js_lines.append("    if (r.worker && r.worker.ok) msg += 'Worker OK. ';")
js_lines.append("    else if (r.worker) msg += 'Worker: ' + (r.worker.error || 'fail');")
js_lines.append("    if (r.railway && r.railway.ok) msg += 'Railway OK. ';")
js_lines.append("    showToast(msg || 'Deploy dhammaad', 'success');")
js_lines.append("    loadDeployLog();")
js_lines.append("  } catch (e) { showToast(e.message, 'error'); }")
js_lines.append("}")
js_lines.append("async function loadEnv() {")
js_lines.append("  try {")
js_lines.append("    var data = await api('/api/admin/env');")
js_lines.append("    var map = { panel_token: 'envPanelToken', worker_url: 'envWorkerUrl', cf_account_id: 'envCfAccount', cf_api_token: 'envCfToken', cf_worker_name: 'envCfWorkerName', railway_webhook: 'envRailwayWebhook' };")
js_lines.append("    for (var k in map) { if (data.env[k]) { var el = document.getElementById(map[k]); if (el) el.value = data.env[k]; } }")
js_lines.append("    var u = document.getElementById('wsUrl');")
js_lines.append("    if (u && data.env.worker_url) u.textContent = data.env.worker_url;")
js_lines.append("  } catch (e) {}")
js_lines.append("}")
js_lines.append("async function saveAllEnv() {")
js_lines.append("  var fields = [['panel_token','envPanelToken'],['worker_url','envWorkerUrl'],['cf_account_id','envCfAccount'],['cf_api_token','envCfToken'],['cf_worker_name','envCfWorkerName'],['railway_webhook','envRailwayWebhook']];")
js_lines.append("  try {")
js_lines.append("    for (var i = 0; i < fields.length; i++) {")
js_lines.append("      var val = document.getElementById(fields[i][1]).value.trim();")
js_lines.append("      if (val) await api('/api/admin/env', 'POST', { key: fields[i][0], value: val });")
js_lines.append("    }")
js_lines.append("    showToast('Env la keydiyay', 'success');")
js_lines.append("  } catch (e) { showToast(e.message, 'error'); }")
js_lines.append("}")
js_lines.append("async function loadDeployLog() {")
js_lines.append("  try {")
js_lines.append("    var data = await api('/api/admin/server/deploy-log');")
js_lines.append("    var box = document.getElementById('deployLogCard');")
js_lines.append("    var content = document.getElementById('deployLogContent');")
js_lines.append("    if (!box || !content) return;")
js_lines.append("    box.style.display = 'block';")
js_lines.append("    content.innerHTML = data.logs.map(function(l) { return '<div style=\"padding:6px;border-bottom:1px solid #e5eaf1;\"><b>[' + l.created_at + ']</b> ' + l.action + ' ' + l.status + '</div>'; }).join('') || 'Ma jiro log';")
js_lines.append("  } catch (e) {}")
js_lines.append("}")
js_lines.append("(function() {")
js_lines.append("  var orig = window.showSection;")
js_lines.append("  window.showSection = function(name) {")
js_lines.append("    if (orig) orig(name);")
js_lines.append("    if (name === 'server') loadServerFiles();")
js_lines.append("  };")
js_lines.append("})();")
js_lines.append("</script>")

js_block = "\n".join(js_lines)

# Kudar JS kahor </body>
html = html.rstrip() + "\n" + js_block + "\n</body>\n</html>\n"

with open('public/index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("OK: public/index.html la keydiyay")

# Verify
with open('public/index.html', 'r', encoding='utf-8') as f:
    check = f.read()
print("</body> count:", check.count('</body>'))
print("</html> count:", check.count('</html>'))
print("<script> count:", check.count('<script>'))
print("</script> count:", check.count('</script>'))
if 'function loadServerFiles' in check:
    print("OK: loadServerFiles")
if 'function deployWorker' in check:
    print("OK: deployWorker")
if 'id="section-server"' in check:
    print("OK: section-server")
if 'id="workerEditor"' in check:
    print("OK: workerEditor")

print("")
print("========================================")
print("DHAMMAAN - HAMBALYO!")
print("========================================")
print("Hadda: node server.js")
