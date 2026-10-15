import shutil, re
BASE = "/data/data/com.termux/files/home/panel-cusub"
shutil.copy(BASE + "/public/index.html", BASE + "/public/index.html.backup_final3")
print("Backup: public/index.html.backup_final3")

with open(BASE + "/public/index.html", "r", encoding="utf-8") as f:
    c = f.read()

# 1. Tirtir functions-ka worker-ka hore
for fn in ["updateLineNumbers", "syncScroll", "cwSelectAll", "cwCut", "cwCopy", "cwPaste", "cwUndo", "cwRemoveAll", "loadWorkerPage", "cwDeploy"]:
    c = re.sub(r"function\s+" + fn + r"\s*\([^)]*\)\s*\{[^\n]*", "", c)
    c = re.sub(r"async\s+function\s+" + fn + r"\s*\([^)]*\)\s*\{[^\n]*", "", c)

# 2. Tirtir showSection wrapper
c = re.sub(r"\(function\(\)\s*\{[^}]*window\.showSection[^}]*\}\)\(\);", "", c)

# 3. Tirtir 'async async'
c = c.replace("async async", "async")

print("1. Tirtiray functions + async async")
print("   <script> count: " + str(c.count("<script>")))
print("   </script> count: " + str(c.count("</script>")))

# 4. Ku dar JS cusub hal <script> tag
NL = chr(10)
js_lines = []
js_lines.append("<script>")
js_lines.append("function updateLineNumbers(a,b){var t=document.getElementById(a),l=document.getElementById(b);if(!t||!l)return;var n=t.value.split(String.fromCharCode(10)).length;var s='';for(var i=1;i<=n;i++)s+=i+String.fromCharCode(10);l.textContent=s;}")
js_lines.append("function syncScroll(a,b){var t=document.getElementById(a),l=document.getElementById(b);if(t&&l)l.scrollTop=t.scrollTop;}")
js_lines.append("function cwSelectAll(){var t=document.getElementById('cw-code');if(!t)return;t.focus();t.select();showToast('La doortay','info');}")
js_lines.append("function cwCut(){var t=document.getElementById('cw-code');if(!t)return;t.focus();document.execCommand('cut');}")
js_lines.append("function cwCopy(){var t=document.getElementById('cw-code');if(!t)return;t.select();document.execCommand('copy');showToast('Copy','success');}")
js_lines.append("async function cwPaste(){try{var txt=await navigator.clipboard.readText();var t=document.getElementById('cw-code');if(!t)return;t.value=txt;updateLineNumbers('cw-code','cwLineNumbers');}catch(e){showToast('Paste ma shaqeyn','error');}}")
js_lines.append("function cwUndo(){document.execCommand('undo');}")
js_lines.append("function cwRemoveAll(){if(!confirm('Tirtir?'))return;var t=document.getElementById('cw-code');if(!t)return;t.value='';updateLineNumbers('cw-code','cwLineNumbers');}")
js_lines.append("async function loadWorkerPage(){try{var t=localStorage.getItem('hamse_token');var r=await fetch('/api/worker/status',{headers:{'Authorization':'Bearer '+t}});var d=await r.json();var sE=document.getElementById('cw-status'),zE=document.getElementById('cw-code-size'),rE=document.getElementById('cw-response'),uE=document.getElementById('cw-url');if(!sE)return;if(d.success&&d.online){sE.innerHTML='Online';sE.style.color='#0a7a3a';zE.textContent=(d.code_length||0)+' bytes';rE.textContent=(d.response_time||'N/A');uE.textContent=(d.worker_url||'N/A');}else{sE.innerHTML='Offline';sE.style.color='#a02020';}var cr=await fetch('/api/worker/code',{headers:{'Authorization':'Bearer '+t}});var cd=await cr.json();var codeEl=document.getElementById('cw-code');if(cd.success&&codeEl){codeEl.value=cd.code||'';updateLineNumbers('cw-code','cwLineNumbers');}else if(codeEl){codeEl.value='// '+(cd.error||'Code lama helin');updateLineNumbers('cw-code','cwLineNumbers');}}catch(e){showToast('Worker: '+e.message,'error');}}")
js_lines.append("(function(){var o=window.showSection;window.showSection=function(n){if(o)o(n);if(n==='worker'&&typeof loadWorkerPage==='function')loadWorkerPage();};})();")
js_lines.append("</script>")
js_block = NL.join(js_lines)

# Ku dar ka hor </body>
c = c.replace("</body>", js_block + NL + "</body>", 1)
print("2. JS cusub la daray")

# 5. Keyd
with open(BASE + "/public/index.html", "w", encoding="utf-8") as f:
    f.write(c)
print("3. Keyd: OK")
print("Final <script>: " + str(c.count("<script>")) + " </script>: " + str(c.count("</script>")))
print("VERIFY loadWorkerPage: " + str("function loadWorkerPage" in c))
print("VERIFY cwDeploy: " + str("function cwDeploy" in c))
print("VERIFY login form: " + str("loginUsername" in c or "loginForm" in c))
print("DHAMMAAN - HAMBALYO!")
