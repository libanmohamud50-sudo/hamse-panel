#!/usr/bin/env python3
import sys, os, json, zipfile, hashlib, shutil, time
from pathlib import Path

def sha256(p):
    h = hashlib.sha256()
    with open(p,'rb') as f:
        for c in iter(lambda: f.read(65536), b''): h.update(c)
    return h.hexdigest()

def detect(pak_path):
    with open(pak_path,'rb') as f: m = f.read(16)
    if m[:4] == b'PK\x03\x04': return 'zip'
    if m[:4] == bytes.fromhex('E1126F5A'): return 'unreal'
    return 'unknown'

def inject_zip(pak_path, bypass_path, out_path):
    with zipfile.ZipFile(pak_path,'r') as zin:
        names = zin.namelist()
        target = None
        for n in names:
            ln = n.lower()
            if ln.endswith('.lua') and ('main' in ln or 'init' in ln or 'load' in ln):
                target = n; break
        if not target:
            for n in names:
                if n.lower().endswith('.lua'): target = n; break
        if not target:
            target = 'BypassV11.lua'
        with zipfile.ZipFile(out_path,'w',zipfile.ZIP_DEFLATED) as zout:
            for item in zin.infolist():
                zout.writestr(item, zin.read(item.filename))
            zout.write(bypass_path, target)
    return {'status':'ok','target':target,'method':'zip_append'}

def main():
    if len(sys.argv) < 4:
        print(json.dumps({'status':'error','msg':'usage: inject.py <pak> <bypass> <out>'})); sys.exit(1)
    pak, bypass, out = sys.argv[1], sys.argv[2], sys.argv[3]
    if not os.path.isfile(pak): print(json.dumps({'status':'error','msg':'pak missing'})); sys.exit(1)
    if not os.path.isfile(bypass): print(json.dumps({'status':'error','msg':'bypass missing'})); sys.exit(1)
    fmt = detect(pak)
    result = {'format':fmt,'pak_sha256':sha256(pak),'bypass_sha256':sha256(bypass)}
    if fmt == 'zip':
        result.update(inject_zip(pak, bypass, out))
    else:
        result.update({'status':'error','msg':'format '+fmt+' — encrypted or unsupported','method':'none'})
    if os.path.isfile(out):
        result['out_sha256'] = sha256(out)
        result['out_size'] = os.path.getsize(out)
    print(json.dumps(result))

if __name__ == '__main__': main()
