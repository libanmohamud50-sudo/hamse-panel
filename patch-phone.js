const fs = require('fs');
const P = 'docs/phone.html';
let h = fs.readFileSync(P, 'utf8');
if (h.includes('id="licv"')) { console.log('Already patched'); process.exit(0); }
fs.writeFileSync(P + '.bak3', h);

let ep = '/api/login';
try {
  const idx = fs.readFileSync('public/index.html', 'utf8');
  const m = idx.match(/['"`](\/api\/[A-Za-z\/_-]*login[A-Za-z\/_-]*)['"`]/);
  if (m) ep = m[1];
} catch (e) {}
console.log('Login endpoint:', ep);

function must(re, what) {
  if (!re.test(h)) { console.log('NOT FOUND: ' + what); process.exit(1); }
}
const reA = /(?:var|let|const)\s+APPS\s*=\s*\[[\s\S]*?\n\];/;
const reD = /(?:var|let|const)\s+DOCK\s*=\s*\[[\s\S]*?\n\];/;
must(reA, 'APPS array');
must(reD, 'DOCK array');
must(/<div id="appv" class="screen">/, 'appv');
must(/<\/body>/, 'body end');
must(/<\/head>/, 'head end');

h = h.replace(reA, function () {
  return "var APPS=[{n:'Licenses',i:'&#128273;',c:'linear-gradient(135deg,#0a84ff,#5e5ce6)',s:'licenses'}];";
});
h = h.replace(reD, function () { return 'var DOCK=[];'; });

const CSS = `<style>
.wg,.srch,.dock{display:none!important}
#home .grid{margin-top:90px}
#licv{display:none;position:absolute;left:0;top:0;right:0;bottom:0;background:#000;z-index:5;flex-direction:column;color:#fff;font-family:-apple-system,BlinkMacSystemFont,"SF Pro Display",sans-serif}
.lv-nav{padding:54px 16px 4px;flex:none}
.lv-back{color:#0a84ff;font-size:17px;cursor:pointer;display:inline-block;padding:6px 0}
.lv-big{font-size:34px;font-weight:700;padding:2px 16px 10px;flex:none}
.lv-body{flex:1;overflow-y:auto;padding:0 14px 60px;-webkit-overflow-scrolling:touch}
.lv-login{padding:20px 4px}
.lv-login input{display:block;width:100%;box-sizing:border-box;background:#1c1c1e;border:1px solid #2c2c2e;border-radius:12px;color:#fff;padding:13px 14px;font-size:16px;margin-bottom:10px;outline:none}
.lv-login button{width:100%;background:linear-gradient(135deg,#0a84ff,#5e5ce6);border:0;color:#fff;border-radius:14px;padding:13px;font-size:16px;font-weight:700;margin-top:6px}
</style>`;

const MARKUP = '<div id="licv"><div class="lv-nav"><span class="lv-back" onclick="goHome()">&#8249; Home</span></div><div class="lv-big">Licenses</div><div class="lv-body"><div id="licensesList"></div></div></div>';

const GLUE = `<script>
(function(){
var BASE='https://hamse-panel-production.up.railway.app';
var LOGIN_EP='${ep}';
function g(i){return document.getElementById(i);}
window.showToast=function(m,t){
  try{
    var d=document.createElement('div');
    d.textContent=m;
    d.style.cssText='position:fixed;top:14px;left:50%;transform:translateX(-50%);max-width:90%;background:rgba(44,44,46,.96);color:'+(t==='error'?'#ff453a':'#fff')+';padding:10px 16px;border-radius:18px;font-size:14px;z-index:100000;box-shadow:0 6px 24px rgba(0,0,0,.4)';
    document.body.appendChild(d);
    setTimeout(function(){d.remove();},2400);
  }catch(e){}
  if(t==='error'&&/401|token|unauthor|expired|invalid/i.test(String(m))){showLogin();}
};
function showLogin(){
  try{localStorage.removeItem('hamse_token');}catch(e){}
  window.TOKEN='';
  g('licensesList').innerHTML='<div class="lv-login">'+
    '<div style="font-size:15px;color:#8e8e93;margin-bottom:12px">Sign in to manage keys</div>'+
    '<input id="lvU" placeholder="Username" autocapitalize="off" autocomplete="username">'+
    '<input id="lvP" type="password" placeholder="Password" autocomplete="current-password">'+
    '<button id="lvGo">Sign in</button>'+
    '<div id="lvErr" style="color:#ff453a;font-size:13px;margin-top:10px"></div></div>';
  g('lvGo').onclick=doLogin;
}
function doLogin(){
  var u=g('lvU').value.trim(),p=g('lvP').value;
  g('lvErr').textContent='';
  if(!u||!p){g('lvErr').textContent='Enter username and password';return;}
  fetch(BASE+LOGIN_EP,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({username:u,password:p})})
    .then(function(r){return r.json().catch(function(){return {};}).then(function(d){
      if(!r.ok||!d.token)throw new Error(d.error||('Login failed ('+r.status+')'));
      return d;});})
    .then(function(d){
      try{localStorage.setItem('hamse_token',d.token);}catch(e){}
      window.TOKEN=d.token;
      window.loadLicenses();})
    .catch(function(e){g('lvErr').textContent=e.message;});
}
var _open=window.openApp;
window.openApp=function(s){
  if(s!=='licenses'){g('licv').style.display='none';g('app').style.display='';return _open(s);}
  var tk='';
  try{tk=localStorage.getItem('hamse_token')||'';}catch(e){}
  window.TOKEN=tk;
  g('app').style.display='none';
  g('licv').style.display='flex';
  g('appv').classList.add('open');
  if(tk){window.loadLicenses();}else{showLogin();}
};
})();
</script>`;

h = h.replace('</head>', function () { return CSS + '</head>'; });
h = h.replace(/<div id="appv" class="screen">/, function (m) { return m + MARKUP; });
const i = h.lastIndexOf('</body>');
h = h.slice(0, i) + '<script src="licenses-app.js"></script>\n' + GLUE + '\n' + h.slice(i);

let bad = false;
[...h.matchAll(/<script>([\s\S]*?)<\/script>/g)].forEach(function (m, n) {
  try { new Function(m[1]); } catch (e) { console.log('SYNTAX ERROR in script ' + n + ': ' + e.message); bad = true; }
});
if (bad) { console.log('Not written. Original is untouched.'); process.exit(1); }
fs.writeFileSync(P, h);
console.log('DONE. Backup: ' + P + '.bak3');
