"""
HAMSE APP SERVER — MXMDM COMPATIBILITY LAYER
Panel: https://hamse-panel-production.up.railway.app
App Server: https://hp.cc.cd
"""
import os, sqlite3, secrets, json, time, hashlib
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, g

APP = Flask(__name__)
DB = os.path.join(os.path.dirname(__file__), "hc.db")

def db():
    if "db" not in g:
        g.db = sqlite3.connect(DB)
        g.db.row_factory = sqlite3.Row
    return g.db

@APP.teardown_appcontext
def close(e=None):
    d = g.pop("db", None)
    if d: d.close()

def init_db():
    d = sqlite3.connect(DB)
    d.executescript("""
    CREATE TABLE IF NOT EXISTS keys (
        k TEXT PRIMARY KEY,
        st TEXT DEFAULT 'unused',
        exp TEXT,
        used_by TEXT,
        devices INTEGER DEFAULT 1,
        created TEXT
    );
    CREATE TABLE IF NOT EXISTS devices (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        license_key TEXT,
        device_id TEXT,
        first_seen TEXT,
        last_seen TEXT,
        UNIQUE(license_key, device_id)
    );
    CREATE TABLE IF NOT EXISTS logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        k TEXT,
        action TEXT,
        ip TEXT,
        ts TEXT
    );
    """)
    d.commit()
    d.close()

def st_of(row):
    try:
        if row["st"] == "revoked": return "revoked"
        if datetime.now() > datetime.fromisoformat(row["exp"]): return "expired"
        return row["st"]
    except: return row["st"]

def check_device_limit(key_row, device_id):
    d = db()
    rows = d.execute("SELECT * FROM devices WHERE license_key=?", (key_row["k"],)).fetchall()
    if len(rows) >= key_row["devices"]:
        for r in rows:
            if r["device_id"] == device_id:
                return True
        return False
    return True

# ============================================================
# 1. MXMDM VERIFY (JSON)
# ============================================================
@APP.route("/1.1/account/verify_credentials.json", methods=["POST"])
def verify_credentials():
    data = request.get_json() or {}
    keys = data.get("keysArray", [])
    device = data.get("deviceId", "")

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
        return jsonify({"code": 1, "msg": "Key banned", "result": 0, "status": 0})

    if not check_device_limit(row, device):
        return jsonify({"code": 1, "msg": "Device limit reached", "result": 0, "status": 0})

    now = datetime.now().isoformat()
    d.execute("INSERT OR IGNORE INTO devices(license_key,device_id,first_seen,last_seen) VALUES(?,?,?,?)",
              (key, device, now, now))
    d.execute("UPDATE devices SET last_seen=? WHERE license_key=? AND device_id=?",
              (now, key, device))
    d.execute("UPDATE keys SET st='used', used_by=? WHERE k=?", (device, key))
    d.commit()

    expire = row["exp"].replace("T", " ")[:19]

    return jsonify({
        "code": 0, "msg": "success", "result": 1, "status": 1,
        "data": {"valid": True, "expire": expire, "licenseCount": 999},
        "kv": {"license": key, "expire": expire, "status": "active", "licenseCount": 999}
    })

# ============================================================
# 2. MXMDM CONNECT (FORM)
# ============================================================
@APP.route("/connect", methods=["POST"])
def connect():
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
        return jsonify({"code": 1, "msg": "Key banned"})

    if not check_device_limit(row, serial):
        return jsonify({"code": 1, "msg": "Device limit reached"})

    now = datetime.now().isoformat()
    d.execute("INSERT OR IGNORE INTO devices(license_key,device_id,first_seen,last_seen) VALUES(?,?,?,?)",
              (key, serial, now, now))
    d.execute("UPDATE keys SET st='used', used_by=? WHERE k=?", (serial, key))
    d.commit()

    return jsonify({
        "code": 0, "msg": "success",
        "expire": row["exp"].replace("T", " ")[:19],
        "status": "active"
    })

# ============================================================
# 3. CONFIG ENDPOINTS
# ============================================================
@APP.route("/config.Config/GetByKeys", methods=["POST"])
def get_by_keys():
    return jsonify({"code": 0, "msg": "success", "data": {}})

@APP.route("/config.Config/InterGetKeys", methods=["POST"])
def inter_get_keys():
    return jsonify({"code": 0, "msg": "success", "data": {}})

@APP.route("/config.Config/ClientKV", methods=["POST"])
def client_kv():
    return jsonify({"code": 0, "msg": "success", "data": {}})

@APP.route("/config.Config/InterClientKV", methods=["POST"])
def inter_client_kv():
    return jsonify({"code": 0, "msg": "success", "data": {}})

@APP.route("/config.Config/GetCosConfig", methods=["POST"])
def get_cos_config():
    return jsonify({"code": 0, "msg": "success", "data": {}})

@APP.route("/config.Config/Config", methods=["POST"])
def config():
    return jsonify({"code": 0, "msg": "success", "data": {}})

@APP.route("/config.Config/InterConfig", methods=["POST"])
def inter_config():
    return jsonify({"code": 0, "msg": "success", "data": {}})

@APP.route("/config.Config/clientkv", methods=["POST"])
def clientkv():
    return jsonify({"code": 0, "msg": "success", "data": {}})

@APP.route("/config.Config/ShortLink", methods=["POST"])
def shortlink():
    return jsonify({"code": 0, "msg": "success", "data": {}})

# ============================================================
# 4. HEALTH
# ============================================================
@APP.route("/health")
def health():
    return jsonify({
        "status": "ok",
        "server": "online",
        "database": "connected",
        "app": "MXMDM compatible",
        "version": "1.0.0"
    })

if __name__ == "__main__":
    init_db()
    print("HAMSE APP SERVER — MXMDM COMPAT")
    print("URL: http://127.0.0.1:5000")
    APP.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
