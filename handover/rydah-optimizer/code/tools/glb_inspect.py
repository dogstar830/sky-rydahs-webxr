#!/usr/bin/env python3
"""Read-only GLB inspector for Sky Rydahs (no deps beyond Pillow). Usage: glb_inspect.py file.glb [--json]"""
import json, struct, sys, re, io, os
CT = {5120:'i8',5121:'u8',5122:'i16',5123:'u16',5125:'u32',5126:'f32'}
def read_glb(p):
    b = open(p,'rb').read()
    if b[:4] != b'glTF': raise ValueError('not a GLB')
    off, j, binc = 12, None, b''
    while off < len(b):
        ln, ty = struct.unpack('<II', b[off:off+8]); c = b[off+8:off+8+ln]
        if ty == 0x4E4F534A: j = json.loads(c)
        elif ty == 0x004E4942: binc = c
        off += 8 + ln
    return j, binc
def img_dims(data, mime):
    if data[:12] == b'\xabKTX 20\xbb\r\n\x1a\n':
        w, h = struct.unpack('<II', data[20:28]); scheme = struct.unpack('<I', data[44:48])[0]
        return w, h, 'ktx2-' + {0:'uastc',1:'etc1s(basislz)',2:'zstd'}.get(scheme, str(scheme))
    try:
        from PIL import Image
        im = Image.open(io.BytesIO(data)); return im.size[0], im.size[1], (im.format or mime).lower()
    except Exception: return 0, 0, mime
def gpu_bytes(w, h, fmt):
    bpp = 1.0 if fmt.startswith('ktx2-uastc') else 0.75 if fmt.startswith('ktx2') else 4.0  # UASTC->ASTC4x4 8bpp; ETC1S->ETC2 4-8bpp; raw RGBA8
    return int(w*h*bpp*4/3)  # + full mip chain
def inspect(p):
    j, binc = read_glb(p); ext = j.get('extensionsUsed', []); acc = j.get('accessors', []); bvs = j.get('bufferViews', [])
    meshes, lods, flags = [], {}, []
    users = {}
    for ni, n in enumerate(j.get('nodes', [])):
        if 'mesh' in n: users.setdefault(n['mesh'], []).append(n.get('name', ''))
    for mi, m in enumerate(j.get('meshes', [])):
        name = m.get('name') or (users.get(mi) or [''])[0] or f'mesh{mi}'
        tris = 0; prims = len(m['primitives']); morph = 0; skinned = False; attrs = set()
        for pr in m['primitives']:
            a = pr['attributes']; attrs |= set(a); skinned |= 'JOINTS_0' in a; morph = max(morph, len(pr.get('targets', [])))
            mode = pr.get('mode', 4)
            cnt = acc[pr['indices']]['count'] if 'indices' in pr else acc[a['POSITION']]['count']
            tris += cnt//3 if mode == 4 else max(cnt-2, 0)
            pa = acc[a['POSITION']]
            if pa['componentType'] != 5126: flags.append(f'{name}: POSITION is {CT[pa["componentType"]]} (quantized position!)')
            for k in a:
                if k.startswith('_W') or k == '_WC':
                    ca = acc[a[k]]
                    if ca['componentType'] != pa['componentType'] or ca.get('normalized', False) != pa.get('normalized', False) or ca.get('type') != pa.get('type'):
                        flags.append(f'{name}: {k} {CT[ca["componentType"]]}{ca.get("type")} vs POSITION {CT[pa["componentType"]]}{pa.get("type")} (space/format mismatch)')
        lm = re.search(r'LOD[_-]?(\d)', name, re.I); lod = int(lm.group(1)) if lm else 0
        lods.setdefault(lod, {'tris': 0, 'draws': 0, 'meshes': 0}); L = lods[lod]; L['tris'] += tris; L['draws'] += prims; L['meshes'] += 1
        meshes.append({'name': name, 'lod': lod, 'tris': tris, 'prims': prims, 'skinned': skinned, 'morph_targets': morph, 'custom_attrs': sorted(x for x in attrs if x.startswith('_'))})
    if 'KHR_mesh_quantization' in ext: flags.insert(0, 'KHR_mesh_quantization in extensionsUsed' + ('' if not any('POSITION is' in f for f in flags) else '') )
    texs = []
    for ii, im in enumerate(j.get('images', [])):
        if 'bufferView' in im:
            bv = bvs[im['bufferView']]; d = binc[bv.get('byteOffset', 0): bv.get('byteOffset', 0) + bv['byteLength']]
            w, h, fmt = img_dims(d, im.get('mimeType', '?')); size = bv['byteLength']
        else: w = h = 0; fmt = 'external'; size = 0
        texs.append({'name': im.get('name', f'img{ii}'), 'w': w, 'h': h, 'fmt': fmt, 'bytes': size, 'gpu_bytes': gpu_bytes(w, h, fmt)})
    slots = {}
    for mt in j.get('materials', []):
        pbr = mt.get('pbrMetallicRoughness', {})
        for s, t in [('base', pbr.get('baseColorTexture')), ('orm', pbr.get('metallicRoughnessTexture')), ('normal', mt.get('normalTexture')), ('orm', mt.get('occlusionTexture')), ('emissive', mt.get('emissiveTexture'))]:
            if t is not None:
                src = j['textures'][t['index']]; srcs = [src.get('source')] + [v.get('source') for v in src.get('extensions', {}).values()]
                for si in srcs:
                    if si is not None: slots.setdefault(si, set()).add(s)
    for i, t in enumerate(texs): t['slots'] = sorted(slots.get(i, {'unused'}))
    comp = [e for e in ext if e in ('KHR_draco_mesh_compression', 'EXT_meshopt_compression', 'KHR_mesh_quantization', 'KHR_texture_basisu', 'EXT_texture_webp')]
    lod0 = lods.get(0, {'tris': 0, 'draws': 0})
    return {'file': p, 'bytes': os.path.getsize(p), 'extensions': ext, 'compression': comp, 'meshes': meshes,
            'lods': {k: lods[k] for k in sorted(lods)}, 'lod0_tris': lod0['tris'], 'lod0_draws': lod0['draws'],
            'materials': [m.get('name', f'mat{i}') for i, m in enumerate(j.get('materials', []))], 'textures': texs,
            'tex_gpu_bytes': sum(t['gpu_bytes'] for t in texs), 'skins': len(j.get('skins', [])),
            'animations': len(j.get('animations', [])), 'flags': flags}
def summary(r, label=''):
    mb = lambda x: f'{x/1048576:.2f} MB'; out = [f'== {label}{os.path.basename(r["file"])}  {mb(r["bytes"])}  compression={",".join(r["compression"]) or "none"}']
    out.append('  LODs: ' + '  '.join(f'LOD{k} {v["tris"]:,} tris / {v["draws"]} prims' for k, v in r['lods'].items()))
    for m in r['meshes']: out.append(f'    {m["name"]:<32} LOD{m["lod"]} {m["tris"]:>8,} tris prims={m["prims"]}{" skin" if m["skinned"] else ""}{" morph="+str(m["morph_targets"]) if m["morph_targets"] else ""} {" ".join(m["custom_attrs"])}')
    out.append(f'  materials ({len(r["materials"])}): {", ".join(r["materials"])}')
    out.append(f'  draw-call estimate (LOD0 visible, raw prims): {r["lod0_draws"]}  (riders.js rMerge collapses body to 1 + outline 1 + glow 1)')
    for t in r['textures']: out.append(f'    tex {t["name"]:<28} {t["w"]}x{t["h"]} {t["fmt"]:<16} [{",".join(t["slots"])}] file {t["bytes"]/1024:.0f} KB  gpu ~{mb(t["gpu_bytes"])}')
    out.append(f'  est. texture GPU memory (with mips): {mb(r["tex_gpu_bytes"])}')
    out += [f'  FLAG: {f}' for f in r['flags']] or ['  flags: none (POSITION float, custom attrs match)']
    return '\n'.join(out)
if __name__ == '__main__':
    r = inspect(sys.argv[1]); print(json.dumps(r, indent=1) if '--json' in sys.argv else summary(r))
