import os, shutil, secrets
BASE = os.path.expanduser('~/panel-cusub')
os.chdir(BASE)
shutil.copy('public/index.html', 'public/index.html.bak_js_' + secrets.token_hex(3))
print("Backup la sameeyay")
with open('public/index.html', 'r', encoding='utf-8') as f:
    html = f.read()
if 'function loadWorkerPage' in html:
    print("INFO: JS horey ayay u jireen")
else:
    js = (
        "function updateLineNumbers(a,b){var t=document.getElementById(a),l=document.getElementById(b);if(!t||!l)return;var n=t.value.split(String.fromCharCode(10)).length;var s='';for(var i=1;i<=n;i++)s+=i+String.fromCharCode(10);l.textContent=s;}\n"
        "function syncScroll(a,b){var t=document.getElementById(a),l=document.getElementById(b);if(t&&l)l.scrollTop=t.scrollTop;}\n"
        "function cwSelectAll(){var t=document.getElementById('cw-code');t.focus();t.select();showToast('La doortay','info');}\n"
        "function cwRemoveAll(){if(!confirm('Tirtir?'))return;document.getElementById('cw-code').value='';updateLineNumbers('cw-code','cwLineNumbers');}\n"
        "async function loadWorkerPage(){try{var t=localStorage.getItem('hamse_token');var r=await fetch('/api/worker/status',{headers:{'Authorization':'Bearer '+t}});var d=await r.json();var sE=document.getElementById('cw-status'),zE=document.getElementById('cw-code-size'),rE=document.getElementById('cw-response'),uE=document.getElementById('cw-url');if(d.success&&d.online){sE.innerHTML='Online';zE.textContent=(d.code_length||0)+' bytes';rE.textContent=(d.response_time||'N/A');uE.textContent=(d.worker_url||'N/A');}else{sE.innerHTML='Offline';}var cr=await fetch('/api/worker/code',{headers:{'Authorization':'Bearer '+t}});var cd=await cr.json();var c=document.getElementById('cw-code');if(cd.success&&c){c.value=cd.code||'';updateLineNumbers('cw-code','cwLineNumbers');}else if(c){c.value='// '+(cd.error||'Code lama helin');updateLineNumbers('cw-code','cwLineNumbers');}}catch(e){showToast('Worker: '+e.message,'error');}}\n"
        "async function cwDeploy(){var b=document.getElementById('cw-save-btn');var c=document.getElementById('cw-code').value;var rs=document.getElementById('cw-result');if(!c){showToast('Code ma jiro','error');return;}b.disabled=true;b.textContent='Deploying...';rs.innerHTML='<p>Deploy socda...</p>';try{var t=localStorage.getItem('hamse_token');var r=await fetch('/api/worker/code',{method:'POST',headers:{'Authorization':'Bearer '+t,'Content-Type':'application/json'},body:JSON.stringify({code:c})});var d=await r.json();if(d.success){rs.innerHTML='<div style=\"padding:15px;background:#d4f4dd;border:1px solid #0a7a3a;border-radius:10px;color:#0a7a3a;\"><b>Deploy Successful!</b> '+(d.message||'')+'</div>';showToast('La deploy-gareeyay!','success');setTimeout(loadWorkerPage,1500);}else{rs.innerHTML='<div style=\"padding:15px;background:#fde0e0;border:1px solid #a02020;border-radius:10px;color:#a02020;\"><b>Failed!</b> '+(d.error||'')+'</div>';showToast('Fail','error');}}catch(e){rs.innerHTML='<div style=\"padding:15px;background:#fde0e0;border-radius:10px;\">Error: '+e.message+'</div>';}b.disabled=false;b.textContent='Deploy';}\n"
        "(function(){var o=window.showSection;window.showSection=function(n){if(o)o(n);if(n==='worker')loadWorkerPage();if(n==='server'&&typeof loadServerFiles==='function')loadServerFiles();};})();\n"
    )
    marker = "if (TOKEN && CURRENT_USER) enterPanel();"
    if marker in html:
        html = html.replace(marker, js + marker)
        print("OK: JS Worker la daray")
    else:
        html = html.replace('</body>', '<script>' + js + '</script>\n</body>')
        print("OK: JS Worker la daray (append)")
with open('public/index.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("OK: public/index.html la keydiyay")
with open('public/index.html') as f:
    chk = f.read()
print("VERIFY loadWorkerPage:", 'function loadWorkerPage' in chk)
print("VERIFY cwDeploy:", 'function cwDeploy' in chk)
print("VERIFY updateLineNumbers:", 'function updateLineNumbers' in chk)
print("")
print("DHAMMAAN - HAMBALYO!")
print("Hadda: node server.js")
