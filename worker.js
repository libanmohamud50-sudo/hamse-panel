export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const path = url.pathname;
    const cors = {
      "Access-Control-Allow-Origin": "*",
      "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
      "Access-Control-Allow-Headers": "Content-Type, User-Agent, Authorization, X-Panel-Token",
    };
    if (request.method === "OPTIONS") {
      return new Response(null, { status: 200, headers: cors });
    }

    // Update / release manifest
    if (url.searchParams.has("client_apk_version") ||
        url.searchParams.has("apk_version") ||
        url.searchParams.has("action") ||
        path.includes("update") ||
        path.includes("release_manifest") ||
        path.includes("api.php")) {
      return new Response(JSON.stringify({
        code: 0, msg: "success", result: 1, status: 1,
        message: "", reason: "", valid: true,
        expire: "2099-12-31 23:59:59",
        latest_apk_version: "4.6.0",
        updateAvailable: false, update_required: false,
        app_update_required: false, library_missing: false,
        latest_file: { version: "4.6.0", url: "https://a.hamse.workers.dev/loader.apk",
          hash: "0000000000000000000000000000000000000000000000000000000000000000",
          file_size: 0, target_app_version: "4.6.0" },
        apk: { version: "4.6.0", url: "https://a.hamse.workers.dev/loader.apk",
          hash: "0000000000000000000000000000000000000000000000000000000000000000",
          file_size: 0, target_app_version: "4.6.0" },
        library: { version: "1.0.0", url: "https://a.hamse.workers.dev/libpubgm.so",
          hash: "0000000000000000000000000000000000000000000000000000000000000000",
          file_size: 0, target_app_version: "4.6.0" },
        data: { valid: true, EXP: "2099-12-31 23:59:59",
          exdate: "2099-12-31 23:59:59",
          expired_date: "2099-12-31 23:59:59",
          expire: "2099-12-31 23:59:59",
          updateAvailable: false, update_required: false,
          library_missing: false, latest_apk_version: "4.6.0",
          app_version: "4.6.0", target_app_version: "4.6.0",
          apk: { version: "4.6.0", url: "https://a.hamse.workers.dev/loader.apk",
            hash: "0000000000000000000000000000000000000000000000000000000000000000",
            file_size: 0, target_app_version: "4.6.0" },
          library: { version: "1.0.0", url: "https://a.hamse.workers.dev/libpubgm.so",
            hash: "0000000000000000000000000000000000000000000000000000000000000000",
            file_size: 0, target_app_version: "4.6.0" } }
      }), { status: 200, headers: { ...cors, "Content-Type": "application/json" } });
    }

    // Key-ga ka soo qaado
    let userKey = "";
    let serial = "";
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

    // Panel-ka verify — key-ga dhabta ah
    let expire = "";
    let valid = false;
    let duration = "";
    const PANEL_URL = env.PANEL_URL || "https://hamse-panel-production.up.railway.app";
    const PANEL_TOKEN = env.PANEL_TOKEN || "";

    if (userKey) {
      try {
        const headers = { "Content-Type": "application/json" };
        if (PANEL_TOKEN) headers["X-Panel-Token"] = PANEL_TOKEN;
        const r = await fetch(PANEL_URL + "/api/verify", {
          method: "POST",
          headers: headers,
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
        valid: false,
        expire: "",
        data: { valid: false, expire: "",
          message: "Uma qalantid inaad heshid Furaha, la xidhiidh @hamsecheatsvip" },
        kv: { license: userKey, expire: "", status: "invalid", licenseCount: 0 }
      }), { status: 200, headers: { ...cors, "Content-Type": "application/json" } });
    }

    // KEY SAX — expire dhabta ah oo panel-ka laga soo qaatay
    return new Response(JSON.stringify({
      code: 0, msg: "success", result: 1, status: 1,
      message: "", reason: "", valid: true,
      expire: expire,
      duration: duration,
      data: { valid: true, expire: expire,
        EXP: expire, exdate: expire, expired_date: expire,
        duration: duration },
      kv: { license: userKey, expire: expire,
        status: "active", licenseCount: 1 }
    }), { status: 200, headers: { ...cors, "Content-Type": "application/json" } });
  }
};
