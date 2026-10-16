import re, os, sys, shutil

SERVER = "server.js"
INDEX  = "public/index.html"

# ---------- 1. SERVER.JS ----------
src = open(SERVER, "r", encoding="utf-8").read()

if "/api/apps/upload" in src:
    print("server.js: /api/apps/upload already present, skip")
else:
    # anchor: insert before the last "app.listen" or before PAK routes block.
    anchor = re.search(r"\napp\.get\(['\"]\/api\/pak\/list['\"]", src)
    if not anchor:
        print("ERR: anchor /api/pak/list not found in server.js"); sys.exit(1)

    APPS_BLOCK = r'''

/* ===================== ADD APPS / LOADER MANAGER ===================== */
const APPS_DIR = path.join(__dirname, "apps_store");
if (!fs.existsSync(APPS_DIR)) fs.mkdirSync(APPS_DIR, { recursive: true });

// ensure tables
try {
  db.run(`CREATE TABLE IF NOT EXISTS apps (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    package_name TEXT,
    version TEXT,
    size INTEGER DEFAULT 0,
    filename TEXT NOT NULL,
    display_name TEXT,
    branding TEXT,
    icon_path TEXT,
    logo_path TEXT,
    config_json TEXT DEFAULT '{}',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
  )`);
  db.run(`CREATE TABLE IF NOT EXISTS app_assets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    app_id INTEGER NOT NULL,
    kind TEXT NOT NULL,
    filename TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
  )`);
  if (typeof saveDB === "function") saveDB();
} catch (e) { console.log("apps tables: " + e.message); }

const appsStorage = multer.diskStorage({
  destination: function (req, file, cb) { cb(null, APPS_DIR); },
  filename: function (req, file, cb) {
    const safe = (file.originalname || "app.apk").replace(/[^A-Za-z0-9._-]/g, "_");
    cb(null, Date.now() + "_" + safe);
  }
});
const appsUpload = multer({
  storage: appsStorage,
  limits: { fileSize: 300 * 1024 * 1024 },
  fileFilter: function (req, file, cb) {
    if (!/\.(apk|zip|png|jpg|jpeg|webp)$/i.test(file.originalname)) return cb(new Error("bad file type"));
    cb(null, true);
  }
});

app.post("/api/apps/upload", authMiddleware, adminMiddleware, appsUpload.single("apk"), function (req, res) {
  try {
    if (!req.file) return res.status(400).json({ status: "error", msg: "apk required" });
    const original = req.file.originalname || "app.apk";
    const base = original.replace(/\.apk$/i, "");
    const info = { name: base, package_name: null, version: null, size: req.file.size };
    db.run("INSERT INTO apps (name, package_name, version, size, filename) VALUES (?,?,?,?,?)",
      [info.name, info.package_name, info.version, info.size, req.file.filename]);
    if (typeof saveDB === "function") saveDB();
    const row = db.exec("SELECT * FROM apps ORDER BY id DESC LIMIT 1");
    res.json({ status: "ok", app: row[0] ? row[0].values[0] : null });
  } catch (e) { res.status(500).json({ status: "error", msg: e.message }); }
});

app.get("/api/apps/list", authMiddleware, adminMiddleware, function (req, res) {
  try {
    const r = db.exec("SELECT id,name,package_name,version,size,filename,display_name,branding,icon_path,logo_path,config_json,created_at FROM apps ORDER BY id DESC");
    res.json({ status: "ok", apps: r[0] ? r[0].values.map(function (v) {
      return { id:v[0], name:v[1], package_name:v[2], version:v[3], size:v[4], filename:v[5],
               display_name:v[6], branding:v[7], icon_path:v[8], logo_path:v[9],
               config: (function(){ try { return JSON.parse(v[10]||"{}"); } catch(e){ return {}; } })(), created_at:v[11] };
    }) : [] });
  } catch (e) { res.status(500).json({ status: "error", msg: e.message }); }
});

app.get("/api/apps/:id", authMiddleware, adminMiddleware, function (req, res) {
  try {
    const id = parseInt(req.params.id, 10);
    const r = db.exec("SELECT * FROM apps WHERE id = " + id);
    if (!r[0] || !r[0].values.length) return res.status(404).json({ status: "error", msg: "not found" });
    const v = r[0].values[0];
    res.json({ status: "ok", app: { id:v[0], name:v[1], package_name:v[2], version:v[3], size:v[4], filename:v[5],
      display_name:v[6], branding:v[7], icon_path:v[8], logo_path:v[9],
      config: (function(){ try { return JSON.parse(v[10]||"{}"); } catch(e){ return {}; } })(), created_at:v[11] } });
  } catch (e) { res.status(500).json({ status: "error", msg: e.message }); }
});

app.put("/api/apps/:id/config", authMiddleware, adminMiddleware, function (req, res) {
  try {
    const id = parseInt(req.params.id, 10);
    const b = req.body || {};
    const cfg = JSON.stringify(b.config || {});
    db.run("UPDATE apps SET display_name = ?, branding = ?, config_json = ? WHERE id = ?",
      [b.display_name || null, b.branding || null, cfg, id]);
    if (typeof saveDB === "function") saveDB();
    res.json({ status: "ok" });
  } catch (e) { res.status(500).json({ status: "error", msg: e.message }); }
});

app.post("/api/apps/:id/asset", authMiddleware, adminMiddleware, appsUpload.single("asset"), function (req, res) {
  try {
    if (!req.file) return res.status(400).json({ status: "error", msg: "asset required" });
    const id = parseInt(req.params.id, 10);
    const kind = (req.body && req.body.kind) ? String(req.body.kind) : "asset";
    db.run("INSERT INTO app_assets (app_id, kind, filename) VALUES (?,?,?)", [id, kind, req.file.filename]);
    if (kind === "icon") db.run("UPDATE apps SET icon_path = ? WHERE id = ?", [req.file.filename, id]);
    if (kind === "logo") db.run("UPDATE apps SET logo_path = ? WHERE id = ?", [req.file.filename, id]);
    if (typeof saveDB === "function") saveDB();
    res.json({ status: "ok", filename: req.file.filename, kind: kind });
  } catch (e) { res.status(500).json({ status: "error", msg: e.message }); }
});

app.delete("/api/apps/:id", authMiddleware, adminMiddleware, function (req, res) {
  try {
    const id = parseInt(req.params.id, 10);
    const r = db.exec("SELECT filename, icon_path, logo_path FROM apps WHERE id = " + id);
    if (r[0] && r[0].values.length) {
      const v = r[0].values[0];
      [v[0], v[1], v[2]].forEach(function (fn) {
        if (fn) { try { fs.unlinkSync(path.join(APPS_DIR, fn)); } catch (e) {} }
      });
    }
    const assets = db.exec("SELECT filename FROM app_assets WHERE app_id = " + id);
    if (assets[0]) assets[0].values.forEach(function (row) {
      try { fs.unlinkSync(path.join(APPS_DIR, row[0])); } catch (e) {}
    });
    db.run("DELETE FROM app_assets WHERE app_id = " + id);
    db.run("DELETE FROM apps WHERE id = " + id);
    if (typeof saveDB === "function") saveDB();
    res.json({ status: "ok" });
  } catch (e) { res.status(500).json({ status: "error", msg: e.message }); }
});

app.get("/api/apps/:id/download", function (req, res) {
  try {
    const id = parseInt(req.params.id, 10);
    const r = db.exec("SELECT filename, name FROM apps WHERE id = " + id);
    if (!r[0] || !r[0].values.length) return res.status(404).send("not found");
    const file = path.join(APPS_DIR, r[0].values[0][0]);
    if (!fs.existsSync(file)) return res.status(404).send("file missing");
    res.download(file, r[0].values[0][1] + ".apk");
  } catch (e) { res.status(500).send(e.message); }
});

'''
    src = src[:anchor.start()] + APPS_BLOCK + src[anchor.start():]
    open(SERVER, "w", encoding="utf-8").write(src)
    print("server.js: apps block inserted")

# ---------- 2. INDEX.HTML ----------
html = open(INDEX, "r", encoding="utf-8").read()

if 'id="section-add-apps"' in html:
    print("index.html: section-add-apps already present, skip")
else:
    # 2a. sidebar nav
    nav_anchor = '<a onclick="showSection(\'loader_mgr\')" id="nav-loader_mgr">'
    if nav_anchor not in html:
        print("ERR: nav-loader_mgr anchor missing"); sys.exit(1)
    nav_new = ('<a onclick="showSection(\'add-apps\')" id="nav-add-apps"> '
               '<i data-lucide="plus-square"></i> <span>Add Apps</span></a>\n        ' + nav_anchor)
    html = html.replace(nav_anchor, nav_new, 1)

    # 2b. sections array
    html = html.replace(
      "var sections = ['dashboard', 'users', 'licenses', 'referrals', 'status', 'telegram', 'worker', 'apk', 'loader', 'pak', 'loader_mgr', 'settings'];",
      "var sections = ['dashboard', 'users', 'licenses', 'referrals', 'status', 'telegram', 'worker', 'apk', 'loader', 'pak', 'loader_mgr', 'add-apps', 'settings'];",
      1)

    # 2c. section HTML before settings section
    sec_anchor = '<div id="section-settings" class="hidden">'
    if sec_anchor not in html:
        print("ERR: section-settings anchor missing"); sys.exit(1)

    SEC = '''
    <div id="section-add-apps" class="hidden">
      <div style="background:#0d1117;border:1px solid #30363d;border-radius:8px;padding:16px;margin-bottom:16px;">
        <h3 style="font-size:14px;margin-bottom:12px;color:#58a6ff;">Add Apps — Upload APK</h3>
        <input type="file" id="appsApk" accept=".apk" style="display:none" onchange="appsPick()">
        <button onclick="document.getElementById('appsApk').click()" style="background:#238636;color:#fff;border:none;padding:10px 18px;border-radius:6px;font-size:14px;cursor:pointer;">📦 SELECT APK</button>
        <div id="appsInfo" style="margin-top:12px;font-size:13px;color:#8b949e;">No file selected</div>
        <button id="appsUploadBtn" onclick="appsUpload()" disabled style="margin-top:12px;background:#6e7681;color:#fff;border:none;padding:10px 18px;border-radius:6px;font-size:14px;cursor:not-allowed;">UPLOAD APK</button>
        <div id="appsStatus" style="margin-top:12px;font-size:13px;color:#8b949e;"></div>
      </div>

      <div style="background:#0d1117;border:1px solid #30363d;border-radius:8px;padding:16px;margin-bottom:16px;">
        <h3 style="font-size:14px;margin-bottom:12px;color:#58a6ff;">Uploaded Apps</h3>
        <button onclick="appsReload()" style="background:#21262d;color:#c9d1d9;border:1px solid #30363d;padding:8px 14px;border-radius:6px;font-size:13px;cursor:pointer;">🔄 Refresh</button>
        <div id="appsList" style="margin-top:12px;font-size:13px;color:#8b949e;">Loading...</div>
      </div>

      <div id="appsConfigBox" style="background:#0d1117;border:1px solid #30363d;border-radius:8px;padding:16px;display:none;">
        <h3 style="font-size:14px;margin-bottom:12px;color:#58a6ff;">Customize App <span id="appsCfgName" style="color:#8b949e;font-weight:normal;"></span></h3>
        <label style="display:block;font-size:12px;color:#8b949e;margin-bottom:4px;">Display Name</label>
        <input id="appsCfgDisplay" style="width:100%;background:#161b22;border:1px solid #30363d;color:#c9d1d9;padding:8px;border-radius:6px;margin-bottom:10px;">
        <label style="display:block;font-size:12px;color:#8b949e;margin-bottom:4px;">Branding / Title</label>
        <input id="appsCfgBrand" style="width:100%;background:#161b22;border:1px solid #30363d;color:#c9d1d9;padding:8px;border-radius:6px;margin-bottom:10px;">
        <label style="display:block;font-size:12px;color:#8b949e;margin-bottom:4px;">Config JSON</label>
        <textarea id="appsCfgJson" rows="6" style="width:100%;background:#161b22;border:1px solid #30363d;color:#c9d1d9;padding:8px;border-radius:6px;margin-bottom:10px;font-family:monospace;font-size:12px;"></textarea>
        <input type="file" id="appsIcon" accept="image/*" style="display:none" onchange="appsAsset('icon')">
        <input type="file" id="appsLogo" accept="image/*" style="display:none" onchange="appsAsset('logo')">
        <button onclick="document.getElementById('appsIcon').click()" style="background:#21262d;color:#c9d1d9;border:1px solid #30363d;padding:8px 14px;border-radius:6px;font-size:13px;cursor:pointer;margin-right:8px;">🖼 Upload Icon</button>
        <button onclick="document.getElementById('appsLogo').click()" style="background:#21262d;color:#c9d1d9;border:1px solid #30363d;padding:8px 14px;border-radius:6px;font-size:13px;cursor:pointer;margin-right:8px;">🏷 Upload Logo</button>
        <button onclick="appsSave()" style="background:#238636;color:#fff;border:none;padding:8px 14px;border-radius:6px;font-size:13px;cursor:pointer;margin-right:8px;">💾 Save Config</button>
        <button onclick="appsDelete()" style="background:#da3633;color:#fff;border:none;padding:8px 14px;border-radius:6px;font-size:13px;cursor:pointer;">🗑 Delete App</button>
        <div id="appsCfgStatus" style="margin-top:10px;font-size:13px;color:#8b949e;"></div>
      </div>
    </div>

'''
    html = html.replace(sec_anchor, SEC + sec_anchor, 1)

    # 2d. JS handlers before </body>
    JS = '''
<script>
(function(){
  var appsFileSel = null, appsCurrent = null;
  function tok(){ return localStorage.getItem("token") || ""; }
  function base(){ return window.location.origin; }
  function toast(m){ try { if (typeof showToast === "function") showToast(m); } catch(e){} }

  window.appsPick = function(){
    var f = document.getElementById("appsApk").files[0];
    if (!f) return;
    appsFileSel = f;
    document.getElementById("appsInfo").innerHTML = "<b style='color:#e6edf3'>"+f.name+"</b> — "+(f.size/1024/1024).toFixed(2)+" MB";
    var b = document.getElementById("appsUploadBtn");
    b.disabled = false; b.style.background = "#1f6feb"; b.style.cursor = "pointer";
  };
  window.appsUpload = async function(){
    if (!appsFileSel) return;
    var st = document.getElementById("appsStatus");
    st.textContent = "Uploading..."; st.style.color = "#8b949e";
    try {
      var fd = new FormData(); fd.append("apk", appsFileSel);
      var r = await fetch(base()+"/api/apps/upload", { method:"POST", headers:{ "Authorization":"Bearer "+tok() }, body: fd });
      var j = await r.json();
      if (!r.ok || j.status !== "ok") { st.textContent = "❌ " + (j.msg||"failed"); st.style.color="#f85149"; return; }
      st.textContent = "✅ Uploaded"; st.style.color="#3fb950";
      toast("APK uploaded");
      appsReload();
    } catch(e){ st.textContent = "❌ " + e.message; st.style.color="#f85149"; }
  };
  window.appsReload = async function(){
    var el = document.getElementById("appsList");
    el.textContent = "Loading...";
    try {
      var r = await fetch(base()+"/api/apps/list", { headers:{ "Authorization":"Bearer "+tok() } });
      var j = await r.json();
      if (!r.ok || j.status !== "ok") { el.textContent = "Error: "+(j.msg||r.status); return; }
      if (!j.apps.length) { el.textContent = "No apps uploaded."; return; }
      el.innerHTML = j.apps.map(function(a){
        return "<div style='border:1px solid #30363d;border-radius:6px;padding:10px;margin-bottom:8px;background:#161b22;'>"
          + "<b style='color:#e6edf3'>"+(a.display_name||a.name)+"</b> "
          + "<span style='color:#8b949e;font-size:12px;'>#" + a.id + " — " + (a.size/1024/1024).toFixed(2) + " MB</span><br>"
          + "<span style='color:#8b949e;font-size:12px;'>" + (a.filename||"") + "</span><br>"
          + "<button onclick='appsManage("+a.id+")' style='margin-top:6px;background:#1f6feb;color:#fff;border:none;padding:6px 10px;border-radius:4px;font-size:12px;cursor:pointer;'>Manage</button> "
          + "<a href='"+base()+"/api/apps/"+a.id+"/download' style='margin-top:6px;display:inline-block;background:#21262d;color:#c9d1d9;border:1px solid #30363d;padding:6px 10px;border-radius:4px;font-size:12px;text-decoration:none;'>Download</a>"
          + "</div>";
      }).join("");
    } catch(e){ el.textContent = "Error: "+e.message; }
  };
  window.appsManage = async function(id){
    try {
      var r = await fetch(base()+"/api/apps/"+id, { headers:{ "Authorization":"Bearer "+tok() } });
      var j = await r.json();
      if (!r.ok || j.status !== "ok") { toast("Load failed"); return; }
      appsCurrent = j.app;
      document.getElementById("appsConfigBox").style.display = "block";
      document.getElementById("appsCfgName").textContent = "#" + id;
      document.getElementById("appsCfgDisplay").value = j.app.display_name || "";
      document.getElementById("appsCfgBrand").value = j.app.branding || "";
      document.getElementById("appsCfgJson").value = JSON.stringify(j.app.config || {}, null, 2);
      document.getElementById("appsCfgStatus").textContent = "";
    } catch(e){ toast("Error: "+e.message); }
  };
  window.appsSave = async function(){
    if (!appsCurrent) return;
    var st = document.getElementById("appsCfgStatus"); st.textContent = "Saving...";
    var cfg = {};
    try { cfg = JSON.parse(document.getElementById("appsCfgJson").value || "{}"); } catch(e){ st.textContent = "❌ invalid JSON"; st.style.color="#f85149"; return; }
    try {
      var r = await fetch(base()+"/api/apps/"+appsCurrent.id+"/config", {
        method:"PUT",
        headers:{ "Authorization":"Bearer "+tok(), "Content-Type":"application/json" },
        body: JSON.stringify({ display_name: document.getElementById("appsCfgDisplay").value, branding: document.getElementById("appsCfgBrand").value, config: cfg })
      });
      var j = await r.json();
      if (!r.ok || j.status !== "ok") { st.textContent = "❌ "+(j.msg||"failed"); st.style.color="#f85149"; return; }
      st.textContent = "✅ Saved"; st.style.color="#3fb950"; toast("Config saved");
    } catch(e){ st.textContent = "❌ "+e.message; st.style.color="#f85149"; }
  };
  window.appsAsset = async function(kind){
    if (!appsCurrent) return;
    var input = document.getElementById(kind === "icon" ? "appsIcon" : "appsLogo");
    var f = input.files[0]; if (!f) return;
    var st = document.getElementById("appsCfgStatus"); st.textContent = "Uploading "+kind+"...";
    try {
      var fd = new FormData(); fd.append("asset", f); fd.append("kind", kind);
      var r = await fetch(base()+"/api/apps/"+appsCurrent.id+"/asset", { method:"POST", headers:{ "Authorization":"Bearer "+tok() }, body: fd });
      var j = await r.json();
      if (!r.ok || j.status !== "ok") { st.textContent = "❌ "+(j.msg||"failed"); st.style.color="#f85149"; return; }
      st.textContent = "✅ "+kind+" uploaded"; st.style.color="#3fb950"; toast(kind+" uploaded");
    } catch(e){ st.textContent = "❌ "+e.message; st.style.color="#f85149"; }
  };
  window.appsDelete = async function(){
    if (!appsCurrent) return;
    if (!confirm("Delete app #"+appsCurrent.id+"? This cannot be undone.")) return;
    var st = document.getElementById("appsCfgStatus"); st.textContent = "Deleting...";
    try {
      var r = await fetch(base()+"/api/apps/"+appsCurrent.id, { method:"DELETE", headers:{ "Authorization":"Bearer "+tok() } });
      var j = await r.json();
      if (!r.ok || j.status !== "ok") { st.textContent = "❌ "+(j.msg||"failed"); st.style.color="#f85149"; return; }
      st.textContent = "✅ Deleted"; st.style.color="#3fb950"; toast("App deleted");
      document.getElementById("appsConfigBox").style.display = "none";
      appsCurrent = null; appsReload();
    } catch(e){ st.textContent = "❌ "+e.message; st.style.color="#f85149"; }
  };

  window.addEventListener("load", function(){ setTimeout(function(){ try { appsReload(); } catch(e){} }, 800); });
})();
</script>
'''
    html = html.replace("</body>", JS + "</body>", 1)
    open(INDEX, "w", encoding="utf-8").write(html)
    print("index.html: section + nav + JS inserted")

print("DONE")
