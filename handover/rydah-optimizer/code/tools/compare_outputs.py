#!/usr/bin/env python3
"""Compare original vs pipeline outputs: size, tex GPU, tris, materials, material colour params, POSITION/_WC float. Read-only."""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); from glb_inspect import inspect, read_glb
def matparams(p):
    j, _ = read_glb(p); out = []
    for m in j.get('materials', []):
        pbr = m.get('pbrMetallicRoughness', {}); ex = m.get('extensions', {})
        out.append({'name': m.get('name'), 'baseColorFactor': pbr.get('baseColorFactor', [1,1,1,1]), 'metallic': pbr.get('metallicFactor', 1), 'roughness': pbr.get('roughnessFactor', 1),
                    'emissiveFactor': m.get('emissiveFactor', [0,0,0]), 'emissive_strength': ex.get('KHR_materials_emissive_strength', {}).get('emissiveStrength', 1),
                    'alphaMode': m.get('alphaMode', 'OPAQUE'), 'alphaCutoff': m.get('alphaCutoff', .5), 'doubleSided': m.get('doubleSided', False),
                    'normalScale': m.get('normalTexture', {}).get('scale', 1), 'occlStrength': m.get('occlusionTexture', {}).get('strength', 1), 'extras': m.get('extras'),
                    'tex_slots': sorted(k for k in ('normalTexture','occlusionTexture','emissiveTexture') if k in m) + sorted(k for k in ('baseColorTexture','metallicRoughnessTexture') if k in pbr)})
    return out
def vcol(p):  # COLOR_0 presence per mesh (vertex colours carry slot masks)
    j, _ = read_glb(p); return {m.get('name'): sorted({k for pr in m['primitives'] for k in pr['attributes'] if k.startswith('COLOR')}) for m in j['meshes']}
rows = []
for orig, new in [l.split() for l in open(sys.argv[1]) if l.strip()]:
    a, b = inspect(orig), inspect(new); ma, mb = matparams(orig), matparams(new)
    mat_ok = ma == mb; vc_ok = vcol(orig) == vcol(new)
    flt = not any('POSITION is' in f or 'mismatch' in f for f in b['flags']); q = 'KHR_mesh_quantization' in b['extensions']
    rows.append(dict(orig=orig, new=new, mb_before=round(a['bytes']/1048576, 2), mb_after=round(b['bytes']/1048576, 2), tex_before=round(a['tex_gpu_bytes']/1048576, 1), tex_after=round(b['tex_gpu_bytes']/1048576, 1),
        tris_before='/'.join(str(v['tris']) for v in a['lods'].values()), tris_after='/'.join(str(v['tris']) for v in b['lods'].values()), mats_before=len(a['materials']), mats_after=len(b['materials']),
        tex_after_dims=' '.join(f'{t["w"]}:{t["fmt"].replace("ktx2-","")}' for t in b['textures']), comp=','.join(b['compression']), mat_params='SAME' if mat_ok else 'DIFF', vcol='SAME' if vc_ok else 'DIFF',
        float_pos='yes' if flt else 'NO', quant_ext='yes' if q else 'no', custom=';'.join(sorted({x for m in b['meshes'] for x in m['custom_attrs']})),
        diff=None if mat_ok else [x for x in zip(ma, mb) if x[0] != x[1]]))
json.dump(rows, open(sys.argv[2], 'w'), indent=1)
for r in rows: print(r['new'].split('characters/')[-1], r['mb_before'], r['mb_after'], r['tex_before'], r['tex_after'], r['tris_before'] == r['tris_after'], r['mat_params'], r['vcol'], r['float_pos'], r['quant_ext'], r['custom'], r['tex_after_dims'])
