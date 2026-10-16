#!/usr/bin/env python3
"""HAMSECHEATS VIP LOADER — TERMUX TEST"""
import subprocess, json, sys, os, uuid

PANEL_URL = "https://hamse-panel-production.up.railway.app"
WORKER_URL = "https://a.hamse.workers.dev"
PANEL_TOKEN = "hM3pK7vN9qL2xB5sT8wR4yZ6cF1jH0dG"

def get_hwid():
    # Use UUID-based HWID (persistent per install)
    hwid_file = os.path.expanduser("~/.hamse_hwid")
    if os.path.exists(hwid_file):
        return open(hwid_file).read().strip()
    hwid = "TERMUX-" + str(uuid.uuid4())[:8].upper()
    with open(hwid_file, "w") as f:
        f.write(hwid)
    return hwid

def verify_key(key, hwid):
    print(f"\n[1] KEY VERIFY")
    print(f"    Key: {key}")
    print(f"    HWID: {hwid}")
    r = subprocess.run(["curl", "-s", f"{WORKER_URL}/?key={key}&serial={hwid}"], capture_output=True, text=True)
    try:
        d = json.loads(r.stdout)
        valid = d.get("valid", False)
        print(f"    Status: {'✅ VALID' if valid else '❌ INVALID'}")
        print(f"    Expire: {d.get('expire')}")
        print(f"    Duration: {d.get('duration')}")
        return valid
    except:
        print(f"    ERROR: {r.stdout[:200]}")
        return False

def check_pak_update():
    print(f"\n[2] PAK UPDATE CHECK")
    r = subprocess.run(["curl", "-s", f"{PANEL_URL}/api/pak/check-update"], capture_output=True, text=True)
    try:
        d = json.loads(r.stdout)
        if d.get("status") == "ok":
            print(f"    PAK: {d.get('name')}")
            print(f"    Size: {d.get('size')} bytes")
            print(f"    URL: {PANEL_URL}{d.get('download_url')}")
            return d
        else:
            print(f"    No PAK: {d}")
    except:
        print(f"    ERROR: {r.stdout[:200]}")
    return None

def download_pak(d, output):
    if not d: return False
    print(f"\n[3] PAK DOWNLOAD")
    url = PANEL_URL + d["download_url"]
    print(f"    Downloading: {url}")
    r = subprocess.run(["curl", "-sL", "-o", output, url], capture_output=True, text=True)
    if os.path.exists(output):
        size = os.path.getsize(output)
        # Check if it's JSON error
        with open(output, 'rb') as f:
            first = f.read(20)
        if first.startswith(b'{'):
            print(f"    ❌ Error response: {first}")
            return False
        print(f"    ✅ Saved: {output} ({size} bytes)")
        return True
    print(f"    ❌ Failed")
    return False

def loader_test():
    print("=" * 60)
    print("  HAMSECHEATS VIP LOADER — TEST")
    print("=" * 60)

    KEY = "30days-HAMSE-RD010D-3S7090"
    HWID = get_hwid()

    if not verify_key(KEY, HWID):
        print("\n❌ Key invalid — exit")
        return

    pak_info = check_pak_update()
    download_pak(pak_info, os.path.expanduser("~/panel-cusub/test_pak.pak"))

    print("\n" + "=" * 60)
    print("  ✅ LOADER TEST COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    loader_test()
