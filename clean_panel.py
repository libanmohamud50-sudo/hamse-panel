import os, shutil, re
BASE = "/data/data/com.termux/files/home/panel-cusub"
os.chdir(BASE)
shutil.copy("public/index.html", "public/index.html.backup_clean_panel")
print("Backup: public/index.html.backup_clean_panel")

with open("public/index.html", "r", encoding="utf-8") as f:
    c = f.read()

NL = chr(10)
print("Ka hor: <script>=" + str(c.count("<script>")) + " lines=" + str(c.count(NL)))

# ===== 1. KA SAAR SECTIONS-KA KALE (kaliya section-worker hay) =====
# Tirtir section-dashboard
start = c.find('<div id="section-dashboard"')
end = c.find('<div id="section-users"')
if start != -1 and end != -1:
    c = c[:start] + c[end:]
    print("1. section-dashboard tirtiray")

# Tirtir section-users
start = c.find('<div id="section-users"')
end = c.find('<div id="section-licenses"')
if start != -1 and end != -1:
    c = c[:start] + c[end:]
    print("2. section-users tirtiray")

# Tirtir section-licenses
start = c.find('<div id="section-licenses"')
end = c.find('<div id="section-referrals"')
if start != -1 and end != -1:
    c = c[:start] + c[end:]
    print("3. section-licenses tirtiray")

# Tirtir section-referrals
start = c.find('<div id="section-referrals"')
end = c.find('<div id="section-server"')
if start != -1 and end != -1:
    c = c[:start] + c[end:]
    print("4. section-referrals tirtiray")

# Tirtir section-server
start = c.find('<div id="section-server"')
end = c.find('<div id="section-worker"')
if start != -1 and end != -1:
    c = c[:start] + c[end:]
    print("5. section-server tirtiray")

# Tirtir section-status
start = c.find('<div id="section-status"')
end = c.find('<div id="section-settings"')
if start != -1 and end != -1:
    c = c[:start] + c[end:]
    print("6. section-status tirtiray")

# Tirtir section-settings
start = c.find('<div id="section-settings"')
end = c.find('</div>' + NL + NL + '<div id="toastBox"')
if start != -1 and end != -1:
    c = c[:start] + c[end:]
    print("7. section-settings tirtiray")

# ===== 2. KA SAAR SIDEBAR LINKS-KA KALE =====
for link_id in ["nav-dashboard", "nav-users", "nav-licenses", "nav-referrals", "nav-server", "nav-status", "nav-settings"]:
    pattern = r'<a[^>]*id="' + link_id + r'"[^>]*>.*?</a>\s*'
    c = re.sub(pattern, "", c, flags=re.DOTALL)
print("8. Sidebar links-ka kale la tirtiray")

# ===== 3. KA SAAR JS-KA WORKER-KA HORE (functions) =====
for fn in ["updateLineNumbers", "syncScroll", "cwSelectAll", "cwCut", "cwCopy", "cwPaste", "cwUndo", "cwRemoveAll", "loadWorkerPage", "cwDeploy"]:
    c = re.sub(r'function\s+' + fn + r'\s*\([^)]*\)\s*\{[^\n]*', '', c)
    c = re.sub(r'async\s+function\s+' + fn + r'\s*\([^)]*\)\s*\{[^\n]*', '', c)
c = re.sub(r'\(function\(\)\s*\{[^}]*window\.showSection[^}]*\}\)\(\);', '', c)
print("9. JS-ka worker-ka hore la tirtiray")

# Tirtir 'async async'
c = c.replace("async async", "async")

# ===== 4. KU DAR SIDEBAR LINK WORKER-KA KALIYA =====
old_nav = '<a onclick="showSection(\'worker\')" id="nav-worker">'
if old_nav not in c:
    marker = '<h2>'
    idx = c.find(marker)
    if idx != -1:
        end_idx = c.find("</a>", c.find("<a", idx)) + 4
        new_nav = NL + '    <a onclick="showSection(\'worker\')" id="nav-worker" class="active">Cloudflare Worker</a>'
        c = c[:end_idx] + new_nav + c[end_idx:]
        print("10. Sidebar link Worker kaliya la daray")

# ===== 5. KU DAR JS-KA WORKER-KA (hal <script> tag) =====
js_lines = []
js_lines.append("<script>")
js_lines.append("function updateLineNumbers(a,b){var t=document.getElementById(a),l=document.getElementById(b);if(!t||!l)return;var n=t.value.split(String.fromCharCode(10)).length;var s='';for(var i=1;i<=n;i++)s+=i+String.fromCharCode(10);l.textContent=s;}")
js_lines.append("function syncScroll(a,b){var t=document.getElementById(a),l=document.getElementById(b);if(t&&l)l.scrollTop=t.scrollTop;}")
js_lines.append("function cwSelectAll(){var t=document.getElementById('cw-code');if(!t)return;t.focus();t.select();}")
js_lines.append("function cwCut(){var t=document.getElementById('cw-code');if(!t)return;t.focus();document.execCommand('cut');}")
js_lines.append("function cwCopy(){var t=document.getElementById('cw-code');if(!t)return;t.select();document.execCommand('copy');}")
js_lines.append("function cwPaste(){var t=document.getElementById('cw-code');if(!t)return;t.focus();document.execCommand('paste');}")
js_lines.append("function cwUndo(){document.execCommand('undo');}")
js_lines.append("function cwRedo(){document.execCommand('redo');}")
js_lines.append("function cwRemoveAll(){if(!confirm('Tirtir?'))return;var t=document.getElementById('cw-code');if(!t)return;t.value='';updateLineNumbers('cw-code','cwLineNumbers');}")
js_lines.append("async function loadWorkerPage(){try{var t=localStorage.getItem('hamse_token');var r=await fetch('/api/worker/status',{headers:{'Authorization':'Bearer '+t}});var d=await r.json();var sE=document.getElementById('cw-status'),zE=document.getElementById('cw-code-size'),rE=document.getElementById('cw-response'),uE=document.getElementById('cw-url');if(!sE)return;if(d.success&&d.online){sE.innerHTML='Online';sE.style.color='#0a7a3a';zE.textContent=(d.code_length||0)+' bytes';rE.textContent=(d.response_time||'N/A');uE.textContent=(d.worker_url||'N/A');}else{sE.innerHTML='Offline';sE.style.color='#a02020';}var cr=await fetch('/api/worker/code',{headers:{'Authorization':'Bearer '+t}});var cd=await cr.json();var codeEl=document.getElementById('cw-code');if(cd.success&&codeEl){codeEl.value=cd.code||'';updateLineNumbers('cw-code','cwLineNumbers');}else if(codeEl){codeEl.value='// '+(cd.error||'Code lama helin');updateLineNumbers('cw-code','cwLineNumbers');}}catch(e){console.log('Worker error:',e.message);}}")
js_lines.append("async function cwDeploy(){var b=document.getElementById('cw-save-btn');var code=document.getElementById('cw-code').value;var rs=document.getElementById('cw-result');if(!code){alert('Code ma jiro');return;}b.disabled=true;b.textContent='Deploying...';rs.innerHTML='<p>Deploy socda...</p>';try{var t=localStorage.getItem('hamse_token');var r=await fetch('/api/worker/code',{method:'POST',headers:{'Authorization':'Bearer '+t,'Content-Type':'application/json'},body:JSON.stringify({code:code})});var d=await r.json();if(d.success){rs.innerHTML='<div style=\"padding:15px;background:#d4f4dd;border:1px solid #0a7a3a;border-radius:10px;color:#0a7a3a;\"><b>Deploy Successful!</b> '+(d.message||'')+'</div>';setTimeout(loadWorkerPage,1500);}else{rs.innerHTML='<div style=\"padding:15px;background:#fde0e0;border:1px solid #a02020;border-radius:10px;color:#a02020;\"><b>Failed!</b> '+(d.error||'')+'</div>';}}catch(e){rs.innerHTML='<div style=\"padding:15px;background:#fde0e0;border-radius:10px;\">Error: '+e.message+'</div>';}b.disabled=false;b.textContent='Deploy';}")
js_lines.append("loadWorkerPage();")
js_lines.append("</script>")
js_block = NL.join(js_lines)

# Ku dar ka hor </body>
c = c.replace("</body>", js_block + NL + "</body>", 1)
print("11. JS-ka worker-ka cusub la daray")

# ===== 6. KEYD =====
with open("public/index.html", "w", encoding="utf-8") as f:
    f.write(c)
print("12. Keyd: OK")

# ===== 7. VERIFY =====
with open("public/index.html") as f:
    chk = f.read()
print("VERIFY <script>: " + str(chk.count("<script>")) + " </script>: " + str(chk.count("</script>")))
print("VERIFY section-worker: " + str('id="section-worker"' in chk))
print("VERIFY section-dashboard: " + str('id="section-dashboard"' in chk))
print("VERIFY loadWorkerPage: " + str("function loadWorkerPage" in chk))
print("VERIFY cwDeploy: " + str("function cwDeploy" in chk))
print("VERIFY nav-worker: " + str("nav-worker" in chk))
print("DHAMMAAN - HAMBALYO!")
