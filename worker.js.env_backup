export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const path = url.pathname;
    const cors = {
      "Access-Control-Allow-Origin": "*",
      "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
      "Access-Control-Allow-Headers": "Content-Type, User-Agent, Authorization, X-Panel-Token",
    };
    if (request.method === "OPTIONS") return new Response(null, { status: 200, headers: cors });

    let userKey = "", serial = "";
    try {
      const ct = (request.headers.get("content-type") || "").toLowerCase();
      if (ct.includes("application/json")) {
        const j = await request.clone().json();
        userKey = (j.user_key || j.key || "").toString().trim();
        serial = (j.serial || "").toString().trim();
      } else {
        const body = await request.clone().text();
        const p = new URLSearchParams(body);
        userKey = (p.get("user_key") || p.get("key") || "").toString().trim();
        serial = (p.get("serial") || "").toString().trim();
      }
    } catch (e) {}

    let expire = "", valid = false, duration = "";
    const PANEL_URL = env.PANEL_URL || "https://hamse-panel-production.up.railway.app";
    const PANEL_TOKEN = env.PANEL_TOKEN || "";

    if (userKey) {
      try {
        const headers = { "Content-Type": "application/json" };
        if (PANEL_TOKEN) headers["X-Panel-Token"] = PANEL_TOKEN;
        const r = await fetch(PANEL_URL + "/api/verify", {
          method: "POST", headers,
          body: JSON.stringify({ key: userKey, serial: serial })
        });
        const j = await r.json();
        if (j && j.valid === true) {
          expire = j.expire || "";
          duration = j.duration || "";
          valid = true;
        }
      } catch (e) { valid = false; }
    }

    if (!valid) {
      return new Response(JSON.stringify({
        code: 1,
        msg: "Uma qalantid inaad heshid Furaha, la xidhiidh @hamsecheatsvip",
        result: 0, status: 0,
        message: "Uma qalantid inaad heshid Furaha, la xidhiidh @hamsecheatsvip",
        reason: "Invalid key",
        valid: false, expire: "",
        data: { valid: false, expire: "", message: "Uma qalantid inaad heshid Furaha, la xidhiidh @hamsecheatsvip" },
        kv: { license: userKey, expire: "", status: "invalid", licenseCount: 0 }
      }), { status: 200, headers: { ...cors, "Content-Type": "application/json" } });
    }

    return new Response(JSON.stringify({
      code: 0, msg: "success", result: 1, status: 1,
      message: "", reason: "", valid: true,
      expire: expire, duration: duration,
      data: { valid: true, expire: expire, EXP: expire, exdate: expire, expired_date: expire, duration: duration },
      kv: { license: userKey, expire: expire, status: "active", licenseCount: 1 }
    }), { status: 200, headers: { ...cors, "Content-Type": "application/json" } });
  }
};
