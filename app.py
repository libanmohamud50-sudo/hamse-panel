import os, sqlite3, secrets, json
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, render_template, session, redirect, url_for, g

APP = Flask(__name__)
APP.secret_key = os.environ.get("JWT_SECRET", "hamse_cheats_panel_2026")
DB = os.path.join(os.path.dirname(__file__), "hc.db")

def init():
    c = sqlite3.connect(DB)
    c.execute("""CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user TEXT UNIQUE, pass TEXT, ref TEXT, role TEXT DEFAULT 'Reseller',
        theme TEXT DEFAULT 'dark', accent TEXT DEFAULT 'red', clock TEXT DEFAULT '24',
        created TEXT, last_login TEXT)""")
    c.execute("""CREATE TABLE IF NOT EXISTS keys(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        k TEXT UNIQUE, game TEXT DEFAULT 'PUBG', hrs INTEGER, duration TEXT,
        devices INTEGER DEFAULT 1, st TEXT DEFAULT 'unused',
        exp TEXT, created TEXT, used_by TEXT)""")
    c.execute("""CREATE TABLE IF NOT EXISTS devices(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        license_key TEXT, device_id TEXT,
        first_seen TEXT, last_seen TEXT, status TEXT DEFAULT 'active')""")
    c.execute("""CREATE TABLE IF NOT EXISTS activities(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user TEXT, action TEXT, status TEXT, created TEXT)""")
    c.commit(); c.close()
init()

def db():
    if "db" not in g:
        g.db = sqlite3.connect(DB); g.db.row_factory = sqlite3.Row
    return g.db

@APP.teardown_appcontext
def close(e=None):
    d = g.pop("db", None)
    if d: d.close()

def log(u, a, s="ok"):
    d = db()
    d.execute("INSERT INTO activities(user,action,status,created) VALUES(?,?,?,?)",
              (u, a, s, datetime.now().isoformat()))
    d.commit()

def exp_iso(h):
    return (datetime.now()+timedelta(hours=h)).isoformat()

def st_of(row):
    try:
        if row["st"] == "revoked": return "revoked"
        if datetime.now() > datetime.fromisoformat(row["exp"]): return "expired"
        return row["st"]
    except: return row["st"]

def dur_label(h):
    if h < 24: return str(h)+"h"
    if h < 720: return str(h//24)+"d"
    return str(h//720)+"m"

def check_device_limit(key_row, device_id):
    """Hubi in device-ku uu ku jiro limit-ka."""
    d = db()
    rows = d.execute("SELECT * FROM devices WHERE license_key=?", (key_row["k"],)).fetchall()
    if len(rows) >= key_row["devices"]:
        # Device cusub ma geli karo
        for r in rows:
            if r["device_id"] == device_id:
                return True
        return False
    return True

# ============================================================
# MXMDM COMPATIBILITY ENDPOINTS
# ============================================================

@APP.route("/1.1/account/verify_credentials.json", methods=["POST"])
def mxmdm_verify():
    """MXMDM app-ku wuxuu u soo diraa keysArray."""
    data = request.get_json() or {}
    keys = data.get("keysArray", [])
    device = data.get("deviceId", "")
    game = data.get("appId", "PUBG")

    if not keys:
        return jsonify({"code": 1, "msg": "Key not found", "result": 0, "status": 0})

    key = keys[0]
    d = db()
    row = d.execute("SELECT * FROM keys WHERE k=?", (key,)).fetchone()

    if not row:
        return jsonify({"code": 1, "msg": "Key not found", "result": 0, "status": 0})

    s = st_of(row)
    if s == "expired":
        return jsonify({"code": 1, "msg": "Key expired", "result": 0, "status": 0})
    if s == "revoked":
        return jsonify({"code": 1, "msg": "Key revoked", "result": 0, "status": 0})

    # Device limit check
    if not check_device_limit(row, device):
        return jsonify({"code": 1, "msg": "Device limit reached", "result": 0, "status": 0})

    # Diiwaangeli device
    now = datetime.now().isoformat()
    d.execute("INSERT OR IGNORE INTO devices(license_key,device_id,first_seen,last_seen) VALUES(?,?,?,?)",
              (key, device, now, now))
    d.execute("UPDATE devices SET last_seen=? WHERE license_key=? AND device_id=?",
              (now, key, device))
    d.execute("UPDATE keys SET st='used', used_by=? WHERE k=?", (device, key))
    d.commit()

    expire = row["exp"].replace("T", " ")[:19]
    return jsonify({
        "code": 0,
        "msg": "success",
        "result": 1,
        "status": 1,
        "data": {
            "valid": True,
            "expire": expire,
            "licenseCount": 999
        },
        "kv": {
            "license": key,
            "expire": expire,
            "status": "active",
            "licenseCount": 999
        }
    })

@APP.route("/connect", methods=["POST"])
def mxmdm_connect():
    """MXMDM loader format (form-urlencoded)."""
    key = request.form.get("user_key", "").strip()
    serial = request.form.get("serial", "").strip()
    game = request.form.get("game", "PUBG")

    if not key:
        return jsonify({"code": 1, "msg": "Key not found"})

    d = db()
    row = d.execute("SELECT * FROM keys WHERE k=?", (key,)).fetchone()

    if not row:
        return jsonify({"code": 1, "msg": "Key not found"})

    s = st_of(row)
    if s == "expired":
        return jsonify({"code": 1, "msg": "Key expired"})
    if s == "revoked":
        return jsonify({"code": 1, "msg": "Key revoked"})

    if not check_device_limit(row, serial):
        return jsonify({"code": 1, "msg": "Device limit reached"})

    now = datetime.now().isoformat()
    d.execute("INSERT OR IGNORE INTO devices(license_key,device_id,first_seen,last_seen) VALUES(?,?,?,?)",
              (key, serial, now, now))
    d.execute("UPDATE keys SET st='used', used_by=? WHERE k=?", (serial, key))
    d.commit()

    return jsonify({
        "code": 0,
        "msg": "success",
        "expire": row["exp"].replace("T", " ")[:19],
        "status": "active"
    })

@APP.route("/config.Config/GetByKeys", methods=["POST"])
def mxmdm_getbykeys():
    return jsonify({"code": 0, "msg": "success", "data": {}})

@APP.route("/config.Config/InterGetKeys", methods=["POST"])
def mxmdm_intergetkeys():
    return jsonify({"code": 0, "msg": "success", "data": {}})

@APP.route("/config.Config/ClientKV", methods=["POST"])
def mxmdm_clientkv():
    return jsonify({"code": 0, "msg": "success", "data": {}})

# ============================================================
# HEALTH CHECK
# ============================================================

@APP.route("/health")
def health():
    return jsonify({"status": "ok", "server": "online", "database": "connected"})

# ============================================================
# PANEL API (hadda jira)
# ============================================================

@APP.route("/api/gen", methods=["POST"])
def gen():
    if "u" not in session: return jsonify({"e":1}),401
    data = request.get_json() or {}
    h = int(data.get("h",1))
    dev = int(data.get("dev",1))
    bulk = int(data.get("bulk",1))
    if h < 1 or h > 100000: return jsonify({"e":"Duration khaldan"}),400
    if dev < 1 or dev > 5000: return jsonify({"e":"Devices 1-5000"}),400
    if bulk < 1 or bulk > 5000: return jsonify({"e":"Bulk 1-5000"}),400
    made = []; d = db()
    for i in range(bulk):
        k = "HC-" + secrets.token_hex(3).upper()
        try:
            d.execute("INSERT INTO keys(k,game,hrs,duration,devices,st,exp,created) VALUES(?,?,?,?,?,?,?,?)",
                      (k,"PUBG",h,dur_label(h),dev,"unused",exp_iso(h),datetime.now().isoformat()))
            made.append(k)
        except: pass
    d.commit()
    log(session["u"],"key_generated", str(bulk)+" keys")
    return jsonify({"ok":1,"keys":made})

@APP.route("/api/verify", methods=["POST"])
def verify_app():
    """App-ku wuxuu u soo diraa key + device."""
    data = request.get_json() or {}
    key = data.get("key","").strip()
    device = data.get("device","").strip()
    if not key:
        return jsonify({"ok": False, "e": "Key ma jiro"}), 400
    d = db()
    row = d.execute("SELECT * FROM keys WHERE k=?", (key,)).fetchone()
    if not row:
        return jsonify({"ok": False, "e": "Key lama helin"}), 404
    s = st_of(row)
    if s == "expired":
        return jsonify({"ok": False, "e": "Key wuu dhamaaday"}), 403
    if s == "revoked":
        return jsonify({"ok": False, "e": "Key waa la revoke-gareeyay"}), 403
    if not check_device_limit(row, device):
        return jsonify({"ok": False, "e": "Device limit"}), 403
    d.execute("UPDATE keys SET st='used', used_by=? WHERE k=?", (device, key))
    d.commit()
    return jsonify({
        "ok": True,
        "duration": row["duration"],
        "expires": row["exp"],
        "game": row["game"]
    })

if __name__ == "__main__":
    print("HAMSE SERVER wuu shaqeynayaa")
    print("Fur: http://127.0.0.1:5000")
    APP.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
@app.route("/api/admin/seed", methods=["POST"])
def admin_seed():
    secret = request.headers.get("X-Admin-Secret", "")
    if secret != os.environ.get("ADMIN_SECRET", "hamse_admin_2026"):
        return jsonify({"e": "Unauthorized"}), 401
    data = request.get_json() or {}
    key = data.get("key", "HC-VIP01")
    hrs = int(data.get("hrs", 8760))
    dev = int(data.get("dev", 1))
    d = db()
    d.execute("INSERT OR REPLACE INTO keys(k,game,hrs,duration,devices,st,exp,created) VALUES(?,?,?,?,?,?,?,?)",
              (key, "PUBG", hrs, dur_label(hrs), dev, "unused",
               exp_iso(hrs), datetime.now().isoformat()))
    d.commit()
    return jsonify({"ok": True, "key": key})
