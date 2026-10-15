import os, shutil, secrets
BASE = os.path.expanduser('~/panel-cusub')
os.chdir(BASE)
shutil.copy('public/index.html', 'public/index.html.backup_ws')
print("Backup: public/index.html.backup_ws")

with open('public/index.html', 'r', encoding='utf-8') as f:
    c = f.read()

# 1. Nav item — ku dar ka dib Server Edit
old_nav = '<a onclick="showSection(' + chr(39) + 'server' + chr(39) + ')" id="nav-server">'
new_nav = '<a onclick="showSection(' + chr(39) + 'worker' + chr(39) + ')" id="nav-worker">Cloudflare Worker</a>'

if 'nav-worker' in c:
    print("1. Nav item: horey ayuu u jiraa")
elif old_nav in c:
    idx = c.find(old_nav)
    end_idx = c.find('</a>', idx) + 4
    c = c[:end_idx] + chr(10) + '    ' + new_nav + c[end_idx:]
    print("1. Nav item: OK")
else:
    print("1. Nav item: LAMA HELIN")

# 2. Section markup — ku dar ka hor section-status
if 'id="section-worker"' in c:
    print("2. Section: horey ayuu u jiraa")
else:
    sec = []
    sec.append('<div id="section-worker" class="hidden">')
    sec.append('  <div class="card">')
    sec.append('    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px;">')
    sec.append('      <h3 style="margin:0;">Cloudflare Worker</h3>')
    sec.append('      <button class="btn-sm btn-primary" onclick="loadWorkerPage()">Refresh</button>')
    sec.append('    </div>')
    sec.append('    <div class="grid">')
    sec.append('      <div class="card" style="margin:0;"><h3>Status</h3><div class="big" id="cw-status" style="font-size:20px;">-</div></div>')
    sec.append('      <div class="card" style="margin:0;"><h3>Code Size</h3><div class="big" id="cw-code-size" style="font-size:20px;">-</div></div>')
    sec.append('      <div class="card" style="margin:0;"><h3>Response</h3><div class="big" id="cw-response" style="font-size:20px;">-</div></div>')
    sec.append('      <div class="card" style="margin:0;"><h3>URL</h3><div class="big" id="cw-url" style="font-size:12px;word-break:break-all;">-</div></div>')
    sec.append('    </div>')
    sec.append('  </div>')
    sec.append('  <div class="card">')
    sec.append('    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;flex-wrap:wrap;gap:8px;">')
    sec.append('      <h3 style="margin:0;">Worker Code</h3>')
    sec.append('      <div style="display:flex;gap:6px;flex-wrap:wrap;">')
    sec.append('        <button class="btn-sm btn-primary" onclick="cwSelectAll()">Select All</button>')
    sec.append('        <button class="btn-sm btn-outline" onclick="cwCut()">Cut</button>')
    sec.append('        <button class="btn-sm btn-outline" onclick="cwCopy()">Copy</button>')
    sec.append('        <button class="btn-sm btn-outline" onclick="cwPaste()">Paste</button>')
    sec.append('        <button class="btn-sm btn-outline" onclick="cwUndo()">Undo</button>')
    sec.append('        <button class="btn-sm btn-warn" onclick="cwRemoveAll()">Remove All</button>')
    sec.append('        <button class="btn-sm btn-success" onclick="cwDeploy()" id="cw-save-btn">Deploy</button>')
    sec.append('      </div>')
    sec.append('    </div>')
    sec.append('    <div class="editor-wrap">')
    sec.append('      <div class="line-numbers" id="cwLineNumbers">1</div>')
    sec.append('      <textarea id="cw-code" class="code-input" spellcheck="false" oninput="updateLineNumbers(' + chr(39) + 'cw-code' + chr(39) + ',' + chr(39) + 'cwLineNumbers' + chr(39) + ')" onscroll="syncScroll(' + chr(39) + 'cw-code' + chr(39) + ',' + chr(39) + 'cwLineNumbers' + chr(39) + ')"></textarea>')
    sec.append('    </div>')
    sec.append('    <div id="cw-result" style="margin-top:12px;"></div>')
    sec.append('  </div>')
    sec.append('</div>')
    sec_html = chr(10).join(sec)
    marker = '<div id="section-status" class="hidden">'
    if marker in c:
        c = c.replace(marker, sec_html + chr(10) + marker, 1)
        print("2. Section: OK")
    else:
        print("2. Section: LAMA HELIN (marker)")

# 3. CSS
if '.code-input' in c:
    print("3. CSS: horey ayuu u jiraa")
else:
    css = chr(10) + '.editor-wrap{position:relative;border:2px solid #d8e0ec;border-radius:10px;background:#0a1f44;overflow:hidden;}' + chr(10)
    css += '.line-numbers{position:absolute;left:0;top:0;bottom:0;width:50px;background:#061530;color:#4a6a9a;font-family:monospace;font-size:13px;line-height:1.5;padding:16px 8px;text-align:right;overflow:hidden;user-select:none;}' + chr(10)
    css += '.code-input{width:100%;min-height:400px;font-family:monospace;font-size:13px;line-height:1.5;padding:16px 16px 16px 60px;border:none;background:transparent;color:#d4e4ff;resize:vertical;outline:none;white-space:pre;overflow-x:auto;}' + chr(10)
    css += '</style>'
    c = c.replace('</style>', css, 1)
    print("3. CSS: OK")

# 4. JS functions — ku dar hal <script> tag ka hor </body>
if 'function cwDeploy' in c:
    print("4. JS: horey ayuu u jiraa")
else:
    js = []
    js.append('<script>')
    js.append("function updateLineNumbers(a,b){var t=document.getElementById(a),l=document.getElementById(b);if(!t||!l)return;var n=t.value.split(String.fromCharCode(10)).length;var s='';for(var i=1;i<=n;i++)s+=i+String.fromCharCode(10);l.textContent=s;}")
    js.append("function syncScroll(a,b){var t=document.getElementById(a),l=document.getElementById(b);if(t&&l)l.scrollTop=t.scrollTop;}")
    js.append("function cwSelectAll(){var t=document.getElementById('cw-code');if(!t)return;t.focus();t.select();showToast('La doortay','info');}")
    js.append("function cwCut(){var t=document.getElementById('cw-code');if(!t)return;t.focus();document.execCommand('cut');}")
    js.append("function cwCopy(){var t=document.getElementById('cw-code');if(!t)return;t.select();document.execCommand('copy');showToast('Copy','success');}")
    js.append("async function cwPaste(){try{var txt=await navigator.clipboard.readText();var t=document.getElementById('cw-code');if(!t)return;t.value=txt;updateLineNumbers('cw-code','cwLineNumbers');}catch(e){showToast('Paste ma shaqeyn','error');}}")
    js.append("function cwUndo(){document.execCommand('undo');}")
    js.append("function cwRemoveAll(){if(!confirm('Tirtir?'))return;var t=document.getElementById('cw-code');if(!t)return;t.value='';updateLineNumbers('cw-code','cwLineNumbers');}")
    js.append("async function loadWorkerPage(){try{var t=localStorage.getItem('hamse_token');var r=await fetch('/api/worker/status',{headers:{'Authorization':'Bearer '+t}});var d=await r.json();var sE=document.getElementById('cw-status'),zE=document.getElementById('cw-code-size'),rE=document.getElementById('cw-response'),uE=document.getElementById('cw-url');if(!sE)return;if(d.success&&d.online){sE.innerHTML='Online';sE.style.color='#0a7a3a';zE.textContent=(d.code_length||0)+' bytes';rE.textContent=(d.response_time||'N/A');uE.textContent=(d.worker_url||'N/A');}else{sE.innerHTML='Offline';sE.style.color='#a02020';}var cr=await fetch('/api/worker/code',{headers:{'Authorization':'Bearer '+t}});var cd=await cr.json();var codeEl=document.getElementById('cw-code');if(cd.success&&codeEl){codeEl.value=cd.code||'';updateLineNumbers('cw-code','cwLineNumbers');}else if(codeEl){codeEl.value='// '+(cd.error||'Code lama helin');updateLineNumbers('cw-code','cwLineNumbers');}}catch(e){showToast('Worker: '+e.message,'error');}}")
    js.append("async function cwDeploy(){var b=document.getElementById('cw-save-btn');var c=document.getElementById('cw-code').value;var rs=document.getElementById('cw-result');if(!c){showToast('Code ma jiro','error');return;}b.disabled=true;b.textContent='Deploying...';rs.innerHTML='<p style=\"color:#6b7c93;\">Deploy socda...</p>';try{var t=localStorage.getItem('hamse_token');var r=await fetch('/api/worker/code',{method:'POST',headers:{'Authorization':'Bearer '+t,'Content-Type':'application/json'},body:JSON.stringify({code:c})});var d=await r.json();if(d.success){rs.innerHTML='<div style=\"padding:15px;background:#d4f4dd;border:1px solid #0a7a3a;border-radius:10px;color:#0a7a3a;\"><b>Deploy Successful!</b> '+(d.message||'')+'</div>';showToast('La deploy-gareeyay!','success');setTimeout(loadWorkerPage,1500);}else{rs.innerHTML='<div style=\"padding:15px;background:#fde0e0;border:1px solid #a02020;border-radius:10px;color:#a02020;\"><b>Failed!</b> '+(d.error||'')+'</div>';showToast('Fail','error');}}catch(e){rs.innerHTML='<div style=\"padding:15px;background:#fde0e0;border-radius:10px;\">Error: '+e.message+'</div>';}b.disabled=false;b.textContent='Deploy';}")
    js.append("(function(){var o=window.showSection;window.showSection=function(n){if(o)o(n);if(n==='worker'&&typeof loadWorkerPage==='function')loadWorkerPage();};})();")
    js.append('</script>')
    js_html = chr(10).join(js)
    if '</body>' in c:
        c = c.replace('</body>', js_html + chr(10) + '</body>', 1)
        print("4. JS: OK")
    else:
        print("4. JS: LAMA HELIN (body)")

# 5. Keyd
with open('public/index.html', 'w', encoding='utf-8') as f:
    f.write(c)
print("5. Keyd: OK")
print("DHAMMAAN - HAMBALYO!")
