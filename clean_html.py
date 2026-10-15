import os, shutil, secrets, re
BASE = os.path.expanduser('~/panel-cusub')
os.chdir(BASE)
shutil.copy('public/index.html', 'public/index.html.bak_ch_' + secrets.token_hex(3))
print("Backup la sameeyay")

with open('public/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

NL = chr(10)

# ===== 1. TIRTIR DHAMMAAN JS-KA WORKER-KA HORE =====
# Tirtir qoraalka bogga ku soo baxay (function ... ilaa </script>)
for fn in ['updateLineNumbers', 'syncScroll', 'cwSelectAll', 'cwCut', 'cwCopy', 'cwPaste', 'cwUndo', 'cwRemoveAll', 'loadWorkerPage', 'cwDeploy']:
    # Tirtir function oo dhan (ilaa 500 xaraf kadib)
    pattern = r'function\s+' + fn + r'\s*\([^)]*\)\s*\{[^\n]*'
    html = re.sub(pattern, '', html)

# Tirtir "function updateLineNumbers" ilaa "</script>"
idx = html.find('function updateLineNumbers')
if idx != -1:
    end_idx = html.find('</script>', idx)
    if end_idx != -1:
        html = html[:idx] + html[end_idx + len('</script>'):]
        print("OK: JS qoraalka bogga la tirtiray")
    else:
        end_idx = html.find('</body>', idx)
        if end_idx != -1:
            html = html[:idx] + html[end_idx:]
            print("OK: JS qoraalka bogga la tirtiray (ilaa </body>)")

# ===== 2. TIRTIR </script> TAGS-ka xad-dhaafka ah =====
# Haddii ay laba </script> isku xigaan, tirtir mid
while html.count('</script>' + NL + '</script>') > 0:
    html = html.replace('</script>' + NL + '</script>', '</script>')

# ===== 3. KU DAR SECTION-WORKER (haddii aanu jirin) =====
if 'id="section-worker"' not in html:
    s = []
    s.append('<div id="section-worker" class="hidden">')
    s.append('  <div class="card">')
    s.append('    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px;">')
    s.append('      <h3 style="margin:0;">Cloudflare Worker</h3>')
    s.append('      <button class="btn-sm btn-primary" onclick="loadWorkerPage()">Refresh</button>')
    s.append('    </div>')
    s.append('    <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:12px;">')
    s.append('      <div style="background:#f0f4f8;padding:16px;border-radius:10px;text-align:center;">')
    s.append('        <div style="font-size:11px;color:#6b7c93;margin-bottom:6px;">WORKER STATUS</div>')
    s.append('        <div id="cw-status" style="font-size:16px;font-weight:700;color:#0a1f44;">-</div>')
    s.append('      </div>')
    s.append('      <div style="background:#f0f4f8;padding:16px;border-radius:10px;text-align:center;">')
    s.append('        <div style="font-size:11px;color:#6b7c93;margin-bottom:6px;">CODE SIZE</div>')
    s.append('        <div id="cw-code-size" style="font-size:16px;font-weight:700;color:#0a1f44;">-</div>')
    s.append('      </div>')
    s.append('      <div style="background:#f0f4f8;padding:16px;border-radius:10px;text-align:center;">')
    s.append('        <div style="font-size:11px;color:#6b7c93;margin-bottom:6px;">RESPONSE TIME</div>')
    s.append('        <div id="cw-response" style="font-size:16px;font-weight:700;color:#0a1f44;">-</div>')
    s.append('      </div>')
    s.append('      <div style="background:#f0f4f8;padding:16px;border-radius:10px;text-align:center;">')
    s.append('        <div style="font-size:11px;color:#6b7c93;margin-bottom:6px;">WORKER URL</div>')
    s.append('        <div id="cw-url" style="font-size:11px;font-weight:700;color:#0a1f44;word-break:break-all;">-</div>')
    s.append('      </div>')
    s.append('    </div>')
    s.append('  </div>')
    s.append('  <div class="card">')
    s.append('    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;flex-wrap:wrap;gap:8px;">')
    s.append('      <h3 style="margin:0;">Worker Code</h3>')
    s.append('      <div style="display:flex;gap:6px;flex-wrap:wrap;">')
    s.append('        <button class="btn-sm btn-primary" onclick="cwSelectAll()">Select All</button>')
    s.append('        <button class="btn-sm btn-outline" onclick="cwCut()">Cut</button>')
    s.append('        <button class="btn-sm btn-outline" onclick="cwCopy()">Copy</button>')
    s.append('        <button class="btn-sm btn-outline" onclick="cwPaste()">Paste</button>')
    s.append('        <button class="btn-sm btn-outline" onclick="cwUndo()">Undo</button>')
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

# ===== 4. KU DAR JS OO NADIIF AH =====
# Tirtir <script> tag-ga worker-ka hore (haddii uu jiro)
# Ku dar hal <script> tag oo cusub ka hor </body>
js = (
    "<script>" + NL +
    "function updateLineNumbers(a,b){var t=document.getElementById(a),l=document.getElementById(b);if(!t||!l)return;var n=t.value.split(String.fromCharCode(10)).length;var s='';for(var i=1;i<=n;i++)s+=i+String.fromCharCode(10);l.textContent=s;}" + NL +
    "function syncScroll(a,b){var t=document.getElementById(a),l=document.getElementById(b);if(t&&l)l.scrollTop=t.scrollTop;}" + NL +
    "function cwSelectAll(){var t=document.getElementById('cw-code');if(!t)return;t.focus();t.select();showToast('La doortay','info');}" + NL +
    "function cwCut(){var t=document.getElementById('cw-code');if(!t)return;t.focus();document.execCommand('cut');}" + NL +
    "function cwCopy(){var t=document.getElementById('cw-code');if(!t)return;t.select();document.execCommand('copy');showToast('Copy','success');}" + NL +
    "async function cwPaste(){try{var txt=await navigator.clipboard.readText();var t=document.getElementById('cw-code');t.value=txt;updateLineNumbers('cw-code','cwLineNumbers');}catch(e){showToast('Paste ma shaqeyn','error');}}" + NL +
    "function cwUndo(){document.execCommand('undo');}" + NL +
    "function cwRemoveAll(){if(!confirm('Tirtir?'))return;var t=document.getElementById('cw-code');if(!t)return;t.value='';updateLineNumbers('cw-code','cwLineNumbers');}" + NL +
    "async function loadWorkerPage(){try{var t=localStorage.getItem('hamse_token');var r=await fetch('/api/worker/status',{headers:{'Authorization':'Bearer '+t}});var d=await r.json();var sE=document.getElementById('cw-status'),zE=document.getElementById('cw-code-size'),rE=document.getElementById('cw-response'),uE=document.getElementById('cw-url');if(!sE)return;if(d.success&&d.online){sE.innerHTML='Online';sE.style.color='#0a7a3a';zE.textContent=(d.code_length||0)+' bytes';rE.textContent=(d.response_time||'N/A');uE.textContent=(d.worker_url||'N/A');}else{sE.innerHTML='Offline';sE.style.color='#a02020';}var cr=await fetch('/api/worker/code',{headers:{'Authorization':'Bearer '+t}});var cd=await cr.json();var c=document.getElementById('cw-code');if(cd.success&&c){c.value=cd.code||'';updateLineNumbers('cw-code','cwLineNumbers');}else if(c){c.value='// '+(cd.error||'Code lama helin');updateLineNumbers('cw-code','cwLineNumbers');}}catch(e){showToast('Worker: '+e.message,'error');}}" + NL +
    "async function cwDeploy(){var b=document.getElementById('cw-save-btn');var c=document.getElementById('cw-code').value;var rs=document.getElementById('cw-result');if(!c){showToast('Code ma jiro','error');return;}b.disabled=true;b.textContent='Deploying...';rs.innerHTML='<p style=\"color:#6b7c93;\">Deploy socda...</p>';try{var t=localStorage.getItem('hamse_token');var r=await fetch('/api/worker/code',{method:'POST',headers:{'Authorization':'Bearer '+t,'Content-Type':'application/json'},body:JSON.stringify({code:c})});var d=await r.json();if(d.success){rs.innerHTML='<div style=\"padding:15px;background:#d4f4dd;border:1px solid #0a7a3a;border-radius:10px;color:#0a7a3a;\"><b>Deploy Successful!</b> '+(d.message||'')+'</div>';showToast('La deploy-gareeyay!','success');setTimeout(loadWorkerPage,1500);}else{rs.innerHTML='<div style=\"padding:15px;background:#fde0e0;border:1px solid #a02020;border-radius:10px;color:#a02020;\"><b>Failed!</b> '+(d.error||'')+'</div>';showToast('Fail','error');}}catch(e){rs.innerHTML='<div style=\"padding:15px;background:#fde0e0;border-radius:10px;\">Error: '+e.message+'</div>';}b.disabled=false;b.textContent='Deploy';}" + NL +
    "(function(){var o=window.showSection;window.showSection=function(n){if(o)o(n);if(n==='worker'&&typeof loadWorkerPage==='function')loadWorkerPage();};})();" + NL +
    "</script>"
)

# Tirtir </script> iyo </body> ee hore, kadib ku dar JS + </body>
if '</body>' in html:
    html = html.replace('</body>', js + NL + '</body>')
    print("OK: JS nadiif ah la daray")

with open('public/index.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("OK: public/index.html la keydiyay")

# Verify
with open('public/index.html') as f:
    chk = f.read()
print("VERIFY <script> count:", chk.count('<script>'))
print("VERIFY </script> count:", chk.count('</script>'))
print("VERIFY loadWorkerPage:", 'function loadWorkerPage' in chk)
print("VERIFY section-worker:", 'id="section-worker"' in chk)
print("DHAMMAAN - HAMBALYO!")
