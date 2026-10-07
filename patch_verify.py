import re, os

APP = "app.py"

with open(APP, "r", encoding="utf-8") as f:
    code = f.read()

# 1. Saar /api/verify hore (haddii jiro)
pattern = r'@APP\.route\("/api/verify".*?\n(?=@APP\.route|if __name__)'
code = re.sub(pattern, '', code, flags=re.DOTALL)

# 2. Route cusub
route = '''@APP.route("/api/verify", methods=["POST"])
def api_verify():
    data = request.get_json(silent=True) or request.form
    key = (data.get("key") or data.get("user_key") or "").strip()
    serial = (data.get("serial") or "").strip()
    if not key:
        return jsonify({"valid": False, "status": "invalid", "message": "Missing key"})
    d = db()
    row = d.execute("SELECT * FROM keys WHERE k=?", (key,)).fetchone()
    if not row:
        return jsonify({"valid": False, "status": "invalid", "message": "Invalid license key"})
    status = st_of(row)
    if status == "revoked":
        return jsonify({"valid": False, "status": "revoked", "message": "License revoked"})
    if status == "expired":
        return jsonify({"valid": False, "status": "expired", "message": "License expired"})
    max_dev = row["devices"] or 1
    if max_dev > 1:
        used = d.execute("SELECT COUNT(DISTINCT used_by) c FROM keys WHERE k=? AND used_by != ''", (key,)).fetchone()["c"]
        if used >= max_dev and row["used_by"] != serial:
            return jsonify({"valid": False, "status": "max_devices", "message": "Max devices reached"})
    try:
        exp14 = datetime.fromisoformat(row["exp"]).strftime("%Y%m%d%H%M%S")
    except Exception:
        exp14 = "20991231235959"
    if row["st"] == "unused":
        d.execute("UPDATE keys SET st='used', used_by=? WHERE id=?", (serial, row["id"]))
        d.commit()
    return jsonify({"valid": True, "status": "active", "expire": exp14,
                    "duration": row["duration"], "device_limit": max_dev,
                    "message": "", "reason": ""})

'''

marker = 'if __name__ == "__main__":'
if marker not in code:
    print("ERROR: marker not found")
    exit(1)

code = code.replace(marker, route + marker, 1)

with open(APP, "w", encoding="utf-8") as f:
    f.write(code)

print("app.py updated")
print("size:", os.path.getsize(APP))

# Verify
import subprocess
r = subprocess.run(["grep", "-n", "api/verify", APP], capture_output=True, text=True)
print("matches:")
print(r.stdout)
