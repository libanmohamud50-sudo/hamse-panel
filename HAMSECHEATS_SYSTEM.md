# HAMSECHEATS VIP SYSTEM — FULL DOCUMENTATION

## SYSTEM STATUS: ✅ FULLY WORKING

### 1. PANEL
- URL: https://hamse-panel-production.up.railway.app
- Login: hamsecheatsvip / Hamse@2026VIP
- DB: /data/hamse_vip.db (Railway Volume) OR __dirname/hamse_vip.db
- Admin Token: required for admin routes

### 2. WORKER (Cloudflare)
- URL: https://a.hamse.workers.dev
- Key Verify: GET /?key=<KEY>&serial=<HWID>
- Response: { code, msg, result, status, valid, expire, duration, data, kv }

### 3. KEY SYSTEM
- Format: <duration>-HAMSE-XXXX-YYYY
- Durations: 30m, 1h, 2h, 6h, 12h, 1d, 7d, 30d, 90d, 365d, lifetime
- HWID binding: multi-device (max_devices field)
- Status: unused | active | expired | banned

### 4. PAK UPDATE
- Check: GET /api/pak/check-update
- Download: GET /api/pak/download/<name>
- Current PAK: modified_game_patch_4.6.0.21572.pak (4.69 MB, 15 Lua files)
- Game path: /storage/emulated/0/Android/data/com.pubg.imobile/files/UE4Game/ShadowTrackerExtra/ShadowTrackerExtra/Saved/Paks/

### 5. LOADER APK UPDATE
- Check: GET /api/loader/check-update
- Download: GET /api/loader/download

### 6. ADMIN ENDPOINTS
- POST /api/login {username, password}
- POST /api/admin/licenses/bulk {count, duration, max_devices, custom_key?}
- GET /api/licenses (bearer token)
- POST /api/telegram/send {text}
- GET /api/telegram/status

### 7. LOADER FLOW (Termux/Android)
1. Loader APK opens → key input
2. Key → https://a.hamse.workers.dev/?key=X&serial=HWID
3. If valid → download PAK from /api/pak/check-update
4. Save PAK to game Paks folder
5. Launch game (KeySystem.lua checks key again)

### 8. TEST KEYS
- 1day-HAMSE-J303YM-F9DN02
- 7days-HAMSE-6UZZF1-9TV42N
- 30days-HAMSE-8G5AU5-1LEBL8
- lifetime-HAMSE-3EB1TE-P3S07C
