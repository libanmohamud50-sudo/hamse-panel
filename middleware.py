"""
HAMSE MIDDLEWARE — Panel ↔ MXMDM APK Bridge
Key-ga panel-ka ka soo qaado, MXMDM APK u gudbiyo
"""
import os, sqlite3, json
from datetime import datetime, timedelta
from flask import Flask, request, jsonify

APP = Flask(__name__)
DB = os.path.join(os.path.dirname(__file__), "hc.db")

# ============================================================
# MIDDLEWARE ENDPOINT — MXMDM APK
# ============================================================
@APP.route("/1.1/account/verify_credentials.json", methods=["POST"])
def mxmdm_verify():
    """MXMDM APK wuxuu u soo diraa key-ga, middleware wuxuu hubiyaa panel-ka"""
    data = request.get_json() or {}
    keys = data.get("keysArray", [])
    device = data.get("deviceId", "")

    if not keys:
        return jsonify({"code": 1, "msg": "Key not found", "result": 0, "status": 0})

    key = keys[0]
    db = sqlite3.connect(DB)
    db.row_factory = sqlite3.Row
    row = db.execute("SELECT * FROM keys WHERE k=?", (key,)).fetchone()

    if not row:
        db.close()
        return jsonify({"code": 1, "msg": "Key not found", "result": 0, "status": 0})

    # Check expiry
    try:
        exp = datetime.fromisoformat(row["exp"])
        if datetime.now() > exp:
            db.close()
            return jsonify({"code": 1, "msg": "Key expired", "result": 0, "status": 0})
    except: pass

    # Check banned
    if row["st"] == "revoked":
        db.close()
        return jsonify({"code": 1, "msg": "Key banned", "result": 0, "status": 0})

    # Register device
    now = datetime.now().isoformat()
    db.execute("INSERT OR IGNORE INTO devices(license_key,device_id,first_seen,last_seen) VALUES(?,?,?,?)",
               (key, device, now, now))
    db.execute("UPDATE devices SET last_seen=? WHERE license_key=? AND device_id=?",
               (now, key, device))
    db.execute("UPDATE keys SET st='used', used_by=? WHERE k=?", (device, key))
    db.commit()
    db.close()

    expire = row["exp"].replace("T", " ")[:19]

    return jsonify({
        "code": 0, "msg": "success", "result": 1, "status": 1,
        "data": {"valid": True, "expire": expire, "licenseCount": 999},
        "kv": {"license": key, "expire": expire, "status": "active", "licenseCount": 999}
    })

# ============================================================
# MIDDLEWARE ENDPOINT — LOADER
# ============================================================
@APP.route("/connect", methods=["POST"])
def mxmdm_connect():
    key = request.form.get("user_key", "").strip()
    serial = request.form.get("serial", "").strip()

    if not key:
        return jsonify({"code": 1, "msg": "Key not found"})

    db = sqlite3.connect(DB)
    db.row_factory = sqlite3.Row
    row = db.execute("SELECT * FROM keys WHERE k=?", (key,)).fetchone()

    if not row:
        db.close()
        return jsonify({"code": 1, "msg": "Key not found"})

    try:
        exp = datetime.fromisoformat(row["exp"])
        if datetime.now() > exp:
            db.close()
            return jsonify({"code": 1, "msg": "Key expired"})
    except: pass

    if row["st"] == "revoked":
        db.close()
        return jsonify({"code": 1, "msg": "Key banned"})

    now = datetime.now().isoformat()
    db.execute("INSERT OR IGNORE INTO devices(license_key,device_id,first_seen,last_seen) VALUES(?,?,?,?)",
               (key, serial, now, now))
    db.execute("UPDATE keys SET st='used', used_by=? WHERE k=?", (serial, key))
    db.commit()
    db.close()

    return jsonify({
        "code": 0, "msg": "success",
        "expire": row["exp"].replace("T", " ")[:19],
        "status": "active"
    })

# ============================================================
# HEALTH
# ============================================================
@APP.route("/health")
def health():
    return jsonify({"status": "ok", "server": "middleware online", "app": "MXMDM compatible"})

if __name__ == "__main__":
    print("HAMSE MIDDLEWARE — MXMDM Bridge")
    APP.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
