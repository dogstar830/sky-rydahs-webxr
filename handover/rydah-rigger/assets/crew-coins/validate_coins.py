#!/usr/bin/env python3
"""Parse each <crew>-coin.glb directly: tri count, bounds (m), embedded images, material wiring."""
import json, struct, os, glob
D = os.path.dirname(os.path.abspath(__file__)); rows = []
for f in sorted(glob.glob(f'{D}/*-coin.glb')):
    b = open(f, 'rb').read(); assert b[:4] == b'glTF'
    jl = struct.unpack('<I', b[12:16])[0]; j = json.loads(b[20:20+jl])
    tris = 0; mn = [1e9]*3; mx = [-1e9]*3
    for m in j['meshes']:
        for p in m['primitives']:
            tris += j['accessors'][p['indices']]['count']//3
            a = j['accessors'][p['attributes']['POSITION']]
            mn = [min(x, y) for x, y in zip(mn, a['min'])]; mx = [max(x, y) for x, y in zip(mx, a['max'])]
    imgs = [(i.get('name'), i.get('mimeType'), 'bufferView' in i) for i in j.get('images', [])]
    mats = [(m['name'], 'normalTexture' in m, 'metallicRoughnessTexture' in m.get('pbrMetallicRoughness', {})) for m in j['materials']]
    size = [round(x-y, 5) for x, y in zip(mx, mn)]
    rows.append((os.path.basename(f), tris, os.path.getsize(f), size, len(imgs), all(e for _, _, e in imgs), mats))
for r in rows:
    print(f'{r[0]:28s} tris={r[1]:5d} bytes={r[2]:8d} size_m={r[3]} images={r[4]} embedded={r[5]} mats={[(m[0], m[1], m[2]) for m in r[6]]}')
