import os, shutil, secrets, re
BASE = os.path.expanduser('~/panel-cusub')
os.chdir(BASE)
shutil.copy('public/index.html', 'public/index.html.bak_cs_' + secrets.token_hex(3))
print("Backup la sameeyay")

with open('public/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

NL = chr(10)

# 1. Tirtir DHAMMAAN <script> iyo </script> tags-ka
before_script = html.count('<script>')
before_close = html.count('</script>')
print("Ka hor: <script>=" + str(before_script) + " </script>=" + str(before_close))

# Tirtir dhammaan <script> iyo </script> tags (kaliya tags-ka, ma aha content-ka)
# Isticmaal regex si taxadar leh
html = re.sub(r'<script[^>]*>', '', html)
html = re.sub(r'</script>', '', html)
print("OK: dhammaan script tags la tirtiray")

# 2. Ku dar HAL <script> tag oo cusub KA HOR </body>
script_tag = '<script>' + NL
close_tag = '</script>' + NL

# Ku dar ka hor </body>
if '</body>' in html:
    html = html.replace('</body>', script_tag + close_tag + '</body>')
    print("OK: hal <script></script> la daray ka hor </body>")
else:
    html = html + NL + script_tag + close_tag
    print("OK: hal <script></script> la daray (append)")

# 3. Ku dar JS functions-ka worker-ka gudaha <script> tag-ga cusub
js = (
    "function updateLineNumbers(a,b){var t=document.getElementById(a),l=document.getElementById(b);if(!t||!l)return;var n=t.value.split(String.fromCharCode(10)).length;var s='';for(var i=1;i<=n;i++)s+=i+String.fromCharCode(10);l.textContent=s;}" + NL +
    "function syncScroll(a,b){var t=document.getElementById(a),l=document.getElementById(b);if(t&&l)l.scrollTop=t.scrollTop;}" + NL +
    "function cwSelectAll(){var t=document.getElementById('cw-code');if(!t)return;t.focus();t.select();showToast('La doortay','info');}" + NL +
    "function cwCut(){var t=document.getElementById('cw-code');if(!t)return;t.focus();document.execCommand('cut');}" + NL +
    "function cwCopy(){var t=document.getElementById('cw-code');if(!t)return;t.select();document.execCommand('copy');showToast('Copy','success');}" + NL +
    "async function cwPaste(){try{var txt=await navigator.clipboard.readText();var t=document.getElementById('cw-code');if(!t)return;t.value=txt;updateLineNumbers('cw-code','cwLineNumbers');}catch(e){showToast('Paste ma shaqeyn','error');}}" + NL +
    "function cwUndo(){document.execCommand('undo');}" + NL +
    "function cwRemoveAll(){if(!confirm('Tirtir?'))return;var t=document.getElementById('cw-code');if(!t)return;t.value='';updateLineNumbers('cw-code','cwLineNumbers');}" + NL +
    "async function loadWorkerPage(){try{var t=localStorage.getItem('hamse_token');var r=await fetch('/api/worker/status',{headers:{'Authorization':'Bearer '+t}});var d=await r.json();var sE=document.getElementById('cw-status'),zE=document.getElementById('cw-code-size'),rE=document.getElementById('cw-response'),uE=document.getElementById('cw-url');if(!sE)return;if(d.success&&d.online){sE.innerHTML='Online';sE.style.color='#0a7a3a';zE.textContent=(d.code_length||0)+' bytes';rE.textContent=(d.response_time||'N/A');uE.textContent=(d.worker_url||'N/A');}else{sE.innerHTML='Offline';sE.style.color='#a02020';}var cr=await fetch('/api/worker/code',{headers:{'Authorization':'Bearer '+t}});var cd=await cr.json();var c=document.getElementById('cw-code');if(cd.success&&c){c.value=cd.code||'';updateLineNumbers('cw-code','cwLineNumbers');}else if(c){c.value='// '+(cd.error||'Code lama helin');updateLineNumbers('cw-code','cwLineNumbers');}}catch(e){showToast('Worker: '+e.message,'error');}}" + NL +
    "async function cwDeploy(){var b=document.getElementById('cw-save-btn');var c=document.getElementById('cw-code').value;var rs=document.getElementById('cw-result');if(!c){showToast('Code ma jiro','error');return;}b.disabled=true;b.textContent='Deploying...';rs.innerHTML='<p style=\"color:#6b7c93;\">Deploy socda...</p>';try{var t=localStorage.getItem('hamse_token');var r=await fetch('/api/worker/code',{method:'POST',headers:{'Authorization':'Bearer '+t,'Content-Type':'application/json'},body:JSON.stringify({code:c})});var d=await r.json();if(d.success){rs.innerHTML='<div style=\"padding:15px;background:#d4f4dd;border:1px solid #0a7a3a;border-radius:10px;color:#0a7a3a;\"><b>Deploy Successful!</b> '+(d.message||'')+'</div>';showToast('La deploy-gareeyay!','success');setTimeout(loadWorkerPage,1500);}else{rs.innerHTML='<div style=\"padding:15px;background:#fde0e0;border:1px solid #a02020;border-radius:10px;color:#a02020;\"><b>Failed!</b> '+(d.error||'')+'</div>';showToast('Fail','error');}}catch(e){rs.innerHTML='<div style=\"padding:15px;background:#fde0e0;border-radius:10px;\">Error: '+e.message+'</div>';}b.disabled=false;b.textContent='Deploy';}" + NL +
    "(function(){var o=window.showSection;window.showSection=function(n){if(o)o(n);if(n==='worker'&&typeof loadWorkerPage==='function')loadWorkerPage();};})();" + NL
)

# Ku dar JS gudaha <script> tag-ga cusub
html = html.replace('<script>' + NL + '</script>', '<script>' + NL + js + '</script>')
print("OK: JS la daray gudaha <script> tag-ga")

with open('public/index.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("OK: public/index.html la keydiyay")

# Verify
with open('public/index.html') as f:
    chk = f.read()
after_script = chk.count('<script>')
after_close = chk.count('</script>')
print("Ka dib: <script>=" + str(after_script) + " </script>=" + str(after_close))
print("VERIFY loadWorkerPage:", 'function loadWorkerPage' in chk)
print("VERIFY cwDeploy:", 'function cwDeploy' in chk)
print("DHAMMAAN - HAMBALYO!")
