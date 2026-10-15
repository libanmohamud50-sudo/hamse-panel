import os, shutil, secrets, re
BASE = os.path.expanduser('~/panel-cusub')
os.chdir(BASE)
shutil.copy('public/index.html', 'public/index.html.backup_cwj')
print("Backup: public/index.html.backup_cwj")

with open('public/index.html', 'r', encoding='utf-8') as f:
    c = f.read()

NL = chr(10)

before_script = c.count('<script>')
before_close = c.count('</script>')
print("Ka hor: <script>=" + str(before_script) + " </script>=" + str(before_close))

# Tirtir JS-ka worker-ka hore (functions)
for fn in ['updateLineNumbers', 'syncScroll', 'cwSelectAll', 'cwCut', 'cwCopy', 'cwPaste', 'cwUndo', 'cwRemoveAll', 'loadWorkerPage', 'cwDeploy']:
    pattern = r'(?:async\s+)?function\s+' + fn + r'\s*\([^)]*\)\s*\{(?:[^{}]|\{(?:[^{}]|\{[^{}]*\})*\})*\}'
    c = re.sub(pattern, '', c)

# Tirtir showSection wrapper worker-ka
pattern2 = r'\(function\(\)\s*\{[^}]*window\.showSection[^}]*\}\)\(\);'
c = re.sub(pattern2, '', c)

print("1. JS-ka worker-ka hore la tirtiray")

# Ku dar JS-ka worker-ka hal <script> tag
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
js_html = NL.join(js)

if '</body>' in c:
    c = c.replace('</body>', js_html + NL + '</body>', 1)
    print("2. JS-ka worker-ka cusub la daray")

with open('public/index.html', 'w', encoding='utf-8') as f:
    f.write(c)
print("3. Keyd: OK")

with open('public/index.html') as f:
    chk = f.read()
print("Ka dib: <script>=" + str(chk.count('<script>')) + " </script>=" + str(chk.count('</script>')))
print("VERIFY loadWorkerPage: " + str('function loadWorkerPage' in chk))
print("VERIFY cwDeploy: " + str('function cwDeploy' in chk))
print("VERIFY login form: " + str('loginUsername' in chk or 'loginForm' in chk))
print("DHAMMAAN - HAMBALYO!")
