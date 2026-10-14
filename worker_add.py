import os, shutil, secrets
NL = chr(10)
BASE = os.path.expanduser('~/panel-cusub')
os.chdir(BASE)
shutil.copy('server.js', 'server.js.bak_wa')
shutil.copy('public/index.html', 'public/index.html.bak_wa')
print("Backup la sameeyay")
with open('server.js', 'r', encoding='utf-8') as f:
    srv = f.read()
if '/api/worker/code' not in srv:
    w = []
    w.append("// ===== CLOUDFLARE WORKER =====")
    w.append("const CF_API = 'https://api.cloudflare.com/client/v4';")
    w.append("app.get('/api/worker/code', authMiddleware, adminMiddleware, async (req, res) => {")
    w.append("  try {")
    w.append("    const token = process.env.CLOUDFLARE_API_TOKEN;")
    w.append("    const accountId = process.env.CLOUDFLARE_ACCOUNT_ID;")
    w.append("    const workerName = process.env.CLOUDFLARE_WORKER_NAME || 'a';")
    w.append("    if (!token || !accountId) return res.status(400).json({ success: false, error: 'CF credentials ma jiro' });")
    w.append("    const url = CF_API + '/accounts/' + accountId + '/workers/scripts/' + workerName;")
    w.append("    const r = await fetch(url, { headers: { 'Authorization': 'Bearer ' + token } });")
    w.append("    const text = await r.text();")
    w.append("    if (r.ok) {")
    w.append("      let c = text;")
    w.append("      const e = c.indexOf('export default');")
    w.append("      if (e > 0) c = c.substring(e);")
    w.append("      const b = c.lastIndexOf(NL + '--');")
    w.append("      if (b > 0) c = c.substring(0, b);")
    w.append("      res.json({ success: true, code: c.trim(), worker: workerName });")
    w.append("    } else { res.status(r.status).json({ success: false, error: text }); }")
    w.append("  } catch (err) { res.status(500).json({ success: false, error: err.message }); }")
    w.append("});")
    w.append("app.post('/api/worker/code', authMiddleware, adminMiddleware, async (req, res) => {")
    w.append("  try {")
    w.append("    const token = process.env.CLOUDFLARE_API_TOKEN;")
    w.append("    const accountId = process.env.CLOUDFLARE_ACCOUNT_ID;")
    w.append("    const workerName = process.env.CLOUDFLARE_WORKER_NAME || 'a';")
    w.append("    const code = req.body.code;")
    w.append("    if (!token || !accountId) return res.status(400).json({ success: false, error: 'CF credentials ma jiro' });")
    w.append("    if (!code) return res.status(400).json({ success: false, error: 'Code ma jiro' });")
    w.append("    const url = CF_API + '/accounts/' + accountId + '/workers/scripts/' + workerName;")
    w.append("    const form = new FormData();")
    w.append("    form.append('metadata', new Blob([JSON.stringify({ main_module: 'worker.js', compatibility_date: '2024-01-01' })], { type: 'application/json' }), 'metadata.json');")
    w.append("    form.append('worker.js', new Blob([code], { type: 'application/javascript+module' }), 'worker.js');")
    w.append("    const r = await fetch(url, { method: 'PUT', headers: { 'Authorization': 'Bearer ' + token }, body: form });")
    w.append("    const data = await r.json();")
    w.append("    if (r.ok && data.success) res.json({ success: true, message: 'La cusboonaysiiyay!', data: data.result });")
    w.append("    else res.status(r.status).json({ success: false, error: JSON.stringify(data.errors || data) });")
    w.append("  } catch (err) { res.status(500).json({ success: false, error: err.message }); }")
    w.append("});")
    w.append("app.get('/api/worker/status', authMiddleware, adminMiddleware, async (req, res) => {")
    w.append("  try {")
    w.append("    const token = process.env.CLOUDFLARE_API_TOKEN;")
    w.append("    const accountId = process.env.CLOUDFLARE_ACCOUNT_ID;")
    w.append("    const workerName = process.env.CLOUDFLARE_WORKER_NAME || 'a';")
    w.append("    if (!token || !accountId) return res.json({ success: true, online: false });")
    w.append("    const url = CF_API + '/accounts/' + accountId + '/workers/scripts/' + workerName;")
    w.append("    const r = await fetch(url, { headers: { 'Authorization': 'Bearer ' + token } });")
    w.append("    const text = await r.text();")
    w.append("    const wUrl = 'https://a.hamse.workers.dev';")
    w.append("    let on = false, rt = 0;")
    w.append("    try { const s = Date.now(); const wr = await fetch(wUrl, { method: 'HEAD' }); rt = Date.now() - s; on = wr.ok; } catch (e) {}")
    w.append("    if (r.ok) res.json({ success: true, online: true, worker_url: wUrl, worker_online: on, response_time: rt + 'ms', code_length: text.length });")
    w.append("    else res.json({ success: true, online: false });")
    w.append("  } catch (err) { res.status(500).json({ success: false, error: err.message }); }")
    w.append("});")
    w.append("")
    block = NL.join(w)
    marker = "app.get('*', (req, res)"
    if marker in srv:
        srv = srv.replace(marker, block + NL + marker)
        print("OK: Worker endpoints la daray")
if 'server_config' not in srv:
    dm = "db.run(`CREATE TABLE IF NOT EXISTS referrals"
    if dm in srv:
        ex = "  db.run(`CREATE TABLE IF NOT EXISTS server_config (id INTEGER PRIMARY KEY AUTOINCREMENT, key TEXT UNIQUE, value TEXT, updated_at DATETIME DEFAULT CURRENT_TIMESTAMP)`);" + NL + "  db.run(`CREATE TABLE IF NOT EXISTS deploy_log (id INTEGER PRIMARY KEY AUTOINCREMENT, action TEXT, status TEXT, message TEXT, created_at DATETIME DEFAULT CURRENT_TIMESTAMP)`);" + NL + NL
        srv = srv.replace(dm, ex + dm)
        print("OK: DB tables la daray")
with open('server.js', 'w', encoding='utf-8') as f:
    f.write(srv)
print("OK: server.js la keydiyay")
ev = {}
if os.path.exists('.env'):
    with open('.env') as f:
        for ln in f.read().splitlines():
            if '=' in ln and not ln.strip().startswith('#'):
                k, v = ln.split('=', 1)
                ev[k.strip()] = v.strip()
if 'CLOUDFLARE_API_TOKEN' not in ev: ev['CLOUDFLARE_API_TOKEN'] = 'cfut_YOUR_TOKEN_HERE'
if 'CLOUDFLARE_ACCOUNT_ID' not in ev: ev['CLOUDFLARE_ACCOUNT_ID'] = 'YOUR_ACCOUNT_ID_HERE'
if 'CLOUDFLARE_WORKER_NAME' not in ev: ev['CLOUDFLARE_WORKER_NAME'] = 'a'
with open('.env', 'w') as f:
    for k, v in ev.items():
        f.write(k + '=' + v + NL)
print("OK: .env la cusboonaysiiyay")
with open('public/index.html', 'r', encoding='utf-8') as f:
    html = f.read()
if '.code-input' not in html:
    css = NL + ".editor-wrap{position:relative;border:2px solid #d8e0ec;border-radius:10px;background:#0a1f44;overflow:hidden;}" + NL + ".line-numbers{position:absolute;left:0;top:0;bottom:0;width:50px;background:#061530;color:#4a6a9a;font-family:monospace;font-size:13px;line-height:1.5;padding:16px 8px;text-align:right;overflow:hidden;}" + NL + ".code-input{width:100%;min-height:400px;font-family:monospace;font-size:13px;line-height:1.5;padding:16px 16px 16px 60px;border:none;background:transparent;color:#d4e4ff;resize:vertical;outline:none;white-space:pre;overflow-x:auto;}" + NL + ".toolbar{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:12px;}" + NL
    html = html.replace('</style>', css + '</style>')
    print("OK: CSS la daray")
if 'nav-worker' not in html:
    sl = '<a onclick="showSection(' + chr(39) + 'server' + chr(39) + ')" id="nav-server">'
    i = html.find(sl)
    if i != -1:
        e = html.find('</a>', i) + 4
        wk = NL + '    <a onclick="showSection(' + chr(39) + 'worker' + chr(39) + ')" id="nav-worker">Cloudflare Worker</a>'
        html = html[:e] + wk + html[e:]
        print("OK: Sidebar Worker la daray")
if 'id="section-worker"' not in html:
    s = []
    s.append('<div id="section-worker" class="hidden">')
    s.append('  <div class="card">')
    s.append('    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px;">')
    s.append('      <h3 style="margin:0;">Cloudflare Worker</h3>')
    s.append('      <button class="btn-sm btn-primary" onclick="loadWorkerPage()">Refresh</button>')
    s.append('    </div>')
    s.append('    <div class="grid">')
    s.append('      <div class="card" style="margin:0;"><h3>Status</h3><div class="big" id="cw-status" style="font-size:20px;">-</div></div>')
    s.append('      <div class="card" style="margin:0;"><h3>Code Size</h3><div class="big" id="cw-code-size" style="font-size:20px;">-</div></div>')
    s.append('      <div class="card" style="margin:0;"><h3>Response</h3><div class="big" id="cw-response" style="font-size:20px;">-</div></div>')
    s.append('      <div class="card" style="margin:0;"><h3>URL</h3><div class="big" id="cw-url" style="font-size:12px;word-break:break-all;">-</div></div>')
    s.append('    </div>')
    s.append('  </div>')
    s.append('  <div class="card">')
    s.append('    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;">')
    s.append('      <h3 style="margin:0;">Worker Code</h3>')
    s.append('      <div class="toolbar" style="margin:0;">')
    s.append('        <button class="btn-sm btn-primary" onclick="cwSelectAll()">Select All</button>')
    s.append('        <button class="btn-sm btn-warn" onclick="cwRemoveAll()">Remove All</button>')
    s.append('        <button class="btn-sm btn-success" onclick="cwDeploy()" id="cw-save-btn">Deploy</button>')
    s.append('      </div>')
    s.append('    </div>')
    s.append('    <div class="editor-wrap">')
    s.append('      <div class="line-numbers" id="cwLineNumbers">1</div>')
    s.append('      <textarea id="cw-code" class="code-input" spellcheck="false" oninput="updateLineNumbers(' + chr(39) + 'cw-code' + chr(39) + ',' + chr(39) + 'cwLineNumbers' + chr(39) + ')" onscroll="syncScroll(' + chr(39) + 'cw-code' + chr(39) + ',' + chr(39) + 'cwLineNumbers' + chr(39) + ')"></textarea>')
    s.append('    </div>')
    s.append('    <div id="cw-result" style="margin-top:12px;"></div>')
    s.append('  </div>')
    s.append('</div>')
    sec = NL.join(s)
    m = '<div id="section-status" class="hidden">'
    if m in html:
        html = html.replace(m, sec + NL + m)
        print("OK: Section Worker la daray")
if 'function cwDeploy' not in html:
    js = (
        NL + "function updateLineNumbers(a,b){var t=document.getElementById(a),l=document.getElementById(b);if(!t||!l)return;var n=t.value.split(String.fromCharCode(10)).length;var s='';for(var i=1;i<=n;i++)s+=i+String.fromCharCode(10);l.textContent=s;}" + NL +
        "function syncScroll(a,b){var t=document.getElementById(a),l=document.getElementById(b);if(t&&l)l.scrollTop=t.scrollTop;}" + NL +
        "function cwSelectAll(){var t=document.getElementById('cw-code');t.focus();t.select();showToast('La doortay','info');}" + NL +
        "function cwRemoveAll(){if(!confirm('Tirtir?'))return;document.getElementById('cw-code').value='';updateLineNumbers('cw-code','cwLineNumbers');}" + NL +
        "async function loadWorkerPage(){try{var t=localStorage.getItem('hamse_token');var r=await fetch('/api/worker/status',{headers:{'Authorization':'Bearer '+t}});var d=await r.json();var sE=document.getElementById('cw-status'),zE=document.getElementById('cw-code-size'),rE=document.getElementById('cw-response'),uE=document.getElementById('cw-url');if(d.success&&d.online){sE.innerHTML='Online';zE.textContent=(d.code_length||0)+' bytes';rE.textContent=(d.response_time||'N/A');uE.textContent=(d.worker_url||'N/A');}else{sE.innerHTML='Offline';}var cr=await fetch('/api/worker/code',{headers:{'Authorization':'Bearer '+t}});var cd=await cr.json();var c=document.getElementById('cw-code');if(cd.success&&c){c.value=cd.code||'';updateLineNumbers('cw-code','cwLineNumbers');}else if(c){c.value='// '+(cd.error||'Code lama helin');updateLineNumbers('cw-code','cwLineNumbers');}}catch(e){showToast('Worker: '+e.message,'error');}}" + NL +
        "async function cwDeploy(){var b=document.getElementById('cw-save-btn');var c=document.getElementById('cw-code').value;var rs=document.getElementById('cw-result');if(!c){showToast('Code ma jiro','error');return;}b.disabled=true;b.textContent='Deploying...';rs.innerHTML='<p>Deploy socda...</p>';try{var t=localStorage.getItem('hamse_token');var r=await fetch('/api/worker/code',{method:'POST',headers:{'Authorization':'Bearer '+t,'Content-Type':'application/json'},body:JSON.stringify({code:c})});var d=await r.json();if(d.success){rs.innerHTML='<div style=\"padding:15px;background:#d4f4dd;border:1px solid #0a7a3a;border-radius:10px;color:#0a7a3a;\"><b>Deploy Successful!</b> '+(d.message||'')+'</div>';showToast('La deploy-gareeyay!','success');setTimeout(loadWorkerPage,1500);}else{rs.innerHTML='<div style=\"padding:15px;background:#fde0e0;border:1px solid #a02020;border-radius:10px;color:#a02020;\"><b>Failed!</b> '+(d.error||'')+'</div>';showToast('Fail','error');}}catch(e){rs.innerHTML='<div style=\"padding:15px;background:#fde0e0;border-radius:10px;\">Error: '+e.message+'</div>';}b.disabled=false;b.textContent='Deploy';}" + NL +
        "(function(){var o=window.showSection;window.showSection=function(n){if(o)o(n);if(n==='worker')loadWorkerPage();if(n==='server'&&typeof loadServerFiles==='function')loadServerFiles();};})();" + NL
    )
    m = "if (TOKEN && CURRENT_USER) enterPanel();"
    if m in html:
        html = html.replace(m, js + NL + m)
        print("OK: JS Worker la daray")
with open('public/index.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("OK: public/index.html la keydiyay")
if os.path.exists('hamse_vip.db'):
    os.remove('hamse_vip.db')
    print("OK: Database hore la tirtiray")
print("")
print("========================================")
print("DHAMMAAN - HAMBALYO!")
print("========================================")
print("Hadda socodsii: python3 worker_add.py")
