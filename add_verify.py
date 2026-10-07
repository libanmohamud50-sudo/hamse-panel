import re

with open("app.py", "r", encoding="utf-8") as f:
    code = f.read()

route = '''
@APP.route("/api/verify", methods=["POST"])
def api_verify():
    data = request.get_json(silent=True) or request.form
    key = (data.get("key") or data.get("user_key") or "").strip()
    if not key:
        return jsonify({"valid": False, "status": "invalid", "message": "Missing key"})
    d = db()
    row = d.execute("SELECT * FROM keys WHERE k=?", (key,)).fetchone()
    if not row:
        return jsonify({"valid": False, "status": "invalid", "message": "Invalid license key"})
    status = st_of(row)
    if status in ("revoked", "expired"):
        return jsonify({"valid": False, "status": status, "message": "License " + status})
    try:
        exp14 = datetime.fromisoformat(row["exp"]).strftime("%Y%m%d%H%M%S")
    except Exception:
        exp14 = "20991231235959"
    if row["st"] == "unused":
        d.execute("UPDATE keys SET st='used' WHERE id=?", (row["id"],))
        d.commit()
    return jsonify({"valid": True, "status": "active", "expire": exp14, "message": "", "reason": ""})

'''

marker = 'if __name__ == "__main__":'
if "/api/verify" in code:
    print("already added")
else:
    code = code.replace(marker, route + marker, 1)
    with open("app.py", "w", encoding="utf-8") as f:
        f.write(code)
    print("added /api/verify")
