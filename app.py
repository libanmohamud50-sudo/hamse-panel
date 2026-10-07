import os, sqlite3, secrets
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, render_template, session, redirect, url_for, g

APP = Flask(__name__)
APP.secret_key = "hamse_cheats_panel_xyz_2026_v2"
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
    c.execute("""CREATE TABLE IF NOT EXISTS activities(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user TEXT, action TEXT, status TEXT, created TEXT)""")
    c.execute("""CREATE TABLE IF NOT EXISTS notifications(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user TEXT, msg TEXT, type TEXT, seen INTEGER DEFAULT 0, created TEXT)""")
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

def get_user():
    d = db()
    return d.execute("SELECT * FROM users WHERE user=?",(session["u"],)).fetchone()

@APP.route("/")
def home():
    if "u" in session: return redirect(url_for("dash"))
    return render_template("login.html")

@APP.route("/login", methods=["POST"])
def login():
    u = request.form.get("u","").strip()
    p = request.form.get("p","").strip()
    if not u or not p:
        return render_template("login.html", err="Dhammaan goobaha waa lagama maarmaan")
    d = db()
    row = d.execute("SELECT * FROM users WHERE user=?",(u,)).fetchone()
    if row and row["pass"] != p:
        log(u,"login","fail")
        return render_template("login.html", err="Password khaldan")
    if not row:
        d.execute("INSERT INTO users(user,pass,ref,role,created,last_login) VALUES(?,?,?,?,?,?)",
                  (u,p,"HAMSECHEATS","Reseller",datetime.now().isoformat(),datetime.now().isoformat()))
        d.commit(); log(u,"register")
    else:
        d.execute("UPDATE users SET last_login=? WHERE user=?",(datetime.now().isoformat(),u))
        d.commit(); log(u,"login")
    session["u"] = u
    return redirect(url_for("dash"))

@APP.route("/logout")
def logout():
    if "u" in session: log(session["u"],"logout")
    session.clear()
    return redirect(url_for("home"))

def base_ctx():
    user = get_user()
    return dict(u=session["u"],
        user_role=user["role"] if user else "Reseller",
        theme=user["theme"] if user else "dark",
        accent=user["accent"] if user else "red",
        clock=user["clock"] if user else "24")

@APP.route("/dashboard")
def dash():
    if "u" not in session: return redirect(url_for("home"))
    d = db()
    rows = d.execute("SELECT * FROM keys ORDER BY id DESC").fetchall()
    keys=[]; total=unused=used=expired=revoked=0
    for r in rows:
        s = st_of(r); rr = dict(r); rr["st"] = s; keys.append(rr)
        total += 1
        if s=="unused": unused+=1
        elif s=="used": used+=1
        elif s=="expired": expired+=1
        elif s=="revoked": revoked+=1
    users = d.execute("SELECT COUNT(*) c FROM users").fetchone()["c"]
    ctx = base_ctx(); ctx.update(dict(keys=keys, total=total, unused=unused, used=used,
        expired=expired, revoked=revoked, users=users))
    return render_template("dash.html", **ctx)

@APP.route("/generate")
def generate_page():
    if "u" not in session: return redirect(url_for("home"))
    return render_template("generate.html", **base_ctx())

@APP.route("/keymanager")
def keymanager():
    if "u" not in session: return redirect(url_for("home"))
    d = db()
    rows = d.execute("SELECT * FROM keys ORDER BY id DESC").fetchall()
    keys=[]
    for r in rows:
        rr = dict(r); rr["st"] = st_of(r); keys.append(rr)
    ctx = base_ctx(); ctx["keys"] = keys
    return render_template("keymanager.html", **ctx)

@APP.route("/users")
def users_page():
    if "u" not in session: return redirect(url_for("home"))
    d = db()
    rows = d.execute("""SELECT u.id, u.user, u.role, u.created, u.last_login,
                        (SELECT COUNT(*) FROM keys WHERE used_by=u.user) as kcount
                        FROM users u ORDER BY u.id DESC""").fetchall()
    users=[]
    for r in rows:
        rr = dict(r); users.append(rr)
    ctx = base_ctx(); ctx["users_list"] = users
    return render_template("users.html", **ctx)

@APP.route("/settings")
def settings_page():
    if "u" not in session: return redirect(url_for("home"))
    return render_template("settings.html", **base_ctx())

@APP.route("/api/theme", methods=["POST"])
def set_theme():
    if "u" not in session: return jsonify({"e":1}),401
    data = request.get_json() or {}
    d = db()
    if "theme" in data: d.execute("UPDATE users SET theme=? WHERE user=?",(data["theme"],session["u"]))
    if "accent" in data: d.execute("UPDATE users SET accent=? WHERE user=?",(data["accent"],session["u"]))
    if "clock" in data: d.execute("UPDATE users SET clock=? WHERE user=?",(data["clock"],session["u"]))
    d.commit()
    return jsonify({"ok":1})

@APP.route("/api/password", methods=["POST"])
def change_password():
    if "u" not in session: return jsonify({"e":1}),401
    data = request.get_json() or {}
    cur = data.get("cur","")
    new = data.get("new","")
    d = db()
    row = d.execute("SELECT * FROM users WHERE user=?",(session["u"],)).fetchone()
    if not row or row["pass"] != cur:
        return jsonify({"e":"Password hore khaldan"}),400
    if len(new) < 4:
        return jsonify({"e":"Password cusub waa 4+ xaraf"}),400
    d.execute("UPDATE users SET pass=? WHERE user=?",(new,session["u"])); d.commit()
    log(session["u"],"password_changed")
    return jsonify({"ok":1})

@APP.route("/api/gen", methods=["POST"])
def gen():
    if "u" not in session: return jsonify({"e":1}),401
    data = request.get_json() or {}
    h = int(data.get("h",1))
    dev = int(data.get("dev",1))
    bulk = int(data.get("bulk",1))
    custom = data.get("custom","").strip()
    if h < 1 or h > 100000: return jsonify({"e":"Duration khaldan"}),400
    if dev < 1 or dev > 5000: return jsonify({"e":"Devices 1-5000"}),400
    if bulk < 1 or bulk > 5000: return jsonify({"e":"Bulk 1-5000"}),400
    made = []; d = db()
    for i in range(bulk):
        k = custom if (custom and bulk == 1) else ("HC-" + secrets.token_hex(3).upper())
        try:
            d.execute("INSERT INTO keys(k,game,hrs,duration,devices,st,exp,created) VALUES(?,?,?,?,?,?,?,?)",
                      (k,"PUBG",h,dur_label(h),dev,"unused",exp_iso(h),datetime.now().isoformat()))
            made.append(k)
        except: pass
    d.commit()
    log(session["u"],"key_generated", str(bulk)+" keys")
    return jsonify({"ok":1,"keys":made})

@APP.route("/api/del/<int:i>", methods=["POST"])
def dele(i):
    if "u" not in session: return jsonify({"e":1}),401
    d = db(); d.execute("DELETE FROM keys WHERE id=?",(i,)); d.commit()
    return jsonify({"ok":1})

@APP.route("/api/revoke/<int:i>", methods=["POST"])
def revoke(i):
    if "u" not in session: return jsonify({"e":1}),401
    d = db(); d.execute("UPDATE keys SET st='revoked' WHERE id=?",(i,)); d.commit()
    return jsonify({"ok":1})

@APP.route("/api/extend/<int:i>", methods=["POST"])
def extend(i):
    if "u" not in session: return jsonify({"e":1}),401
    hrs = int((request.get_json() or {}).get("h",24))
    d = db()
    row = d.execute("SELECT * FROM keys WHERE id=?",(i,)).fetchone()
    if not row: return jsonify({"e":2}),404
    cur = row["exp"] or datetime.now().isoformat()
    new_exp = (datetime.fromisoformat(cur)+timedelta(hours=hrs)).isoformat()
    d.execute("UPDATE keys SET exp=? WHERE id=?",(new_exp,i)); d.commit()
    return jsonify({"ok":1})


@APP.route("/api/verify", methods=["POST"])
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
    if max_dev >= 1:
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

if __name__ == "__main__":
    print("Hamse cheats panel wuu shaqeynayaa")
    print("Fur: http://127.0.0.1:5000")
    APP.run(host="0.0.0.0", port=5000)
