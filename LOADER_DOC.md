# HAMSECHEATS VIP LOADER — DOCUMENTATION

## 1. Key Verification
GET https://a.hamse.workers.dev/?key=<KEY>&serial=<HWID>

Response:
{
  "code": 0, "msg": "success", "result": 1, "status": 1,
  "valid": true, "expire": "2026-11-15 00:47:23",
  "duration": "30d", "kv": { "license": "QUARTER", "status": "active" }
}

## 2. PAK Update Check
GET https://hamse-panel-production.up.railway.app/api/pak/check-update

Response:
{
  "status": "ok",
  "name": "modified_game_patch_4.6.0.21572.pak",
  "size": 4693113,
  "download_url": "/api/pak/download/modified_game_patch_4.6.0.21572.pak"
}

## 3. PAK Download
GET https://hamse-panel-production.up.railway.app/api/pak/download/modified_game_patch_4.6.0.21572.pak

Save to: /storage/emulated/0/Android/data/com.pubg.imobile/files/UE4Game/ShadowTrackerExtra/ShadowTrackerExtra/Saved/Paks/

## 4. Loader APK Update
GET https://hamse-panel-production.up.railway.app/api/loader/check-update

## 5. Keys (Admin)
GET https://hamse-panel-production.up.railway.app/api/licenses (admin)

## 6. Admin Login
POST https://hamse-panel-production.up.railway.app/api/login
{"username":"hamsecheatsvip","password":"Hamse@2026VIP"}

## 7. Generate License (Admin)
POST https://hamse-panel-production.up.railway.app/api/admin/licenses/bulk
Header: Authorization: Bearer <TOKEN>
Body: {"count":1,"duration":"30d","max_devices":20,"custom_key":"OPTIONAL"}
