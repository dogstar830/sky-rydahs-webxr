#!/usr/bin/env python3
"""Sky Rydahs Quest asset pipeline. Never touches the input; refuses to overwrite inputs or existing GLBs (unless --force on non-input outputs).
usage: quest_pipeline.py IN.glb [--out-dir DIR] [--geometry draco|meshopt16|none] [--max-base 2048] [--max-normal 1024] [--max-orm 1024]
       [--keep-crisp 'face|head|skate'] [--crisp-max 2048] [--simplify TRIS] [--ktx2] [--pot near|up] [--no-pot] [--dry-run] [--force]
outputs: DIR/<name>.quest.glb (+ DIR/<name>.quest-ktx2.glb with --ktx2)"""
import argparse, json, os, subprocess, sys, tempfile, shutil
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from glb_inspect import inspect, summary
GT_NM = os.environ.get('GT_NODE_MODULES', '/workspace/tools/gt/node_modules'); GT = os.path.join(GT_NM, '.bin', 'gltf-transform')
KTX = os.path.join(HERE, 'ktx')  # local KTX-Software 4.4.2 (toktx) unpacked from the Khronos .deb
def env():
    e = dict(os.environ); e['PATH'] = os.path.join(KTX, 'bin') + ':' + e['PATH']; e['LD_LIBRARY_PATH'] = os.path.join(KTX, 'lib') + ':' + e.get('LD_LIBRARY_PATH', ''); return e
def ktx_ok():
    try: return subprocess.run(['ktx', '--version'], env=env(), capture_output=True).returncode == 0 and os.path.exists(GT)
    except FileNotFoundError: return False
def plan_dims(W, H, cap, pot):  # mirrors quest_transform.cjs dims()/potN()
    import math
    sc = min(1, cap / max(W, H)); w, h = round(W * sc), round(H * sc)
    def potN(n):
        lo = 2 ** int(math.floor(math.log2(n))); hi = lo * 2
        return lo if n == lo else (hi if pot == 'up' else (lo if n - lo <= hi - n else hi))
    if pot: w, h = min(cap, potN(w)), min(cap, potN(h))
    return w, h
def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('input'); ap.add_argument('--out-dir'); ap.add_argument('--geometry', default='draco', choices=['draco', 'meshopt16', 'none'])
    ap.add_argument('--max-base', type=int, default=2048); ap.add_argument('--max-normal', type=int, default=1024); ap.add_argument('--max-orm', type=int, default=1024)
    ap.add_argument('--keep-crisp', default='', help="regex on texture/material name, e.g. 'face|head|skate'"); ap.add_argument('--crisp-max', type=int, default=2048)
    ap.add_argument('--simplify', type=int, default=0, help='target LOD0 tris (off by default)'); ap.add_argument('--ktx2', action='store_true'); ap.add_argument('--pot', nargs='?', const='near', default=None, choices=['near','up'], help='snap texture dims to powers of two (KTX2/BC7-safe mips); up = round up (no detail loss), capped by --max-*. DEFAULT with --ktx2: up'); ap.add_argument('--no-pot', action='store_true', help='with --ktx2: keep source (possibly NPOT) dims')
    ap.add_argument('--suffix', default='quest', help='output suffix: quest -> .quest.glb, quest2 -> .quest2.glb'); ap.add_argument('--dry-run', action='store_true', help='inspect + plan only, write nothing'); ap.add_argument('--force', action='store_true', help='allow replacing an existing *.quest*.glb output (never the input)')
    a = ap.parse_args()
    user_pot = None if a.no_pot else a.pot  # the plain .quest.glb keeps exactly what was asked (unchanged behaviour)
    if a.no_pot: a.pot = None
    elif a.ktx2 and a.pot is None: a.pot = 'up'  # KTX2 default: POT round-up capped by --max-* (desktop BC7 needs every mip a multiple of 4)
    print(f'POT: {a.pot or "off"}' + (' (KTX2 default)' if a.ktx2 and not a.no_pot else ''))
    src = os.path.abspath(a.input); name = os.path.basename(src)[:-4]
    if name.endswith('.' + a.suffix) or ('.' + a.suffix + '-') in name: sys.exit(f'refusing: {name}.glb already looks like a pipeline output (idempotency guard)')
    if a.suffix != 'quest' and name.endswith('.quest'): name = name[:-6]  # foo.quest.glb -> foo.quest2.glb
    od = os.path.abspath(a.out_dir or os.path.dirname(src)); out = os.path.join(od, name + '.' + a.suffix + '.glb'); outk = os.path.join(od, name + '.' + a.suffix + '-ktx2.glb')
    if a.geometry == 'meshopt16': print('NOTE: meshopt16 = visual check required before shipping (team rule). POSITION and _* custom attrs stay float32.')
    before = inspect(src); print(summary(before, 'BEFORE '))
    for o in [out] + ([outk] if a.ktx2 else []):
        if os.path.abspath(o) == src: sys.exit('refusing: output == input')
        if os.path.exists(o) and not a.force: sys.exit(f'refusing: {o} exists (use --out-dir, or --force to replace a previous pipeline output)')
    if a.ktx2 and not ktx_ok(): print('WARN: --ktx2 requested but toktx/gltf-transform unavailable -> skipping KTX2 output')
    if a.dry_run:
        print(f'DRY RUN: would write {out}' + (f' and {outk}' if a.ktx2 else ''))
        caps = dict(base=a.max_base, normal=a.max_normal, orm=a.max_orm, emissive=a.max_base, other=a.max_base, unused=a.max_base)
        for lab, pot in [('quest', user_pot)] + ([('quest-ktx2', a.pot)] if a.ktx2 else []):
            for t in before['textures']:
                if str(t['fmt']).startswith('ktx2'): continue
                cap = max(caps.get(x, a.max_base) for x in t['slots'])
                if a.keep_crisp and __import__('re').search(a.keep_crisp, t['name'] or '', __import__('re').I): cap = max(cap, a.crisp_max)  # plan matches on texture name only
                w, h = plan_dims(t['w'], t['h'], cap, pot); ok = all(v & (v - 1) == 0 for v in (w, h))
                print(f'  plan {lab:<10} tex {t["name"]:<28} {t["w"]}x{t["h"]} -> {w}x{h}  {"POT" if ok else "NPOT"}')
        return
    os.makedirs(od, exist_ok=True)
    opts = dict(geometry=a.geometry, maxBase=a.max_base, maxNormal=a.max_normal, maxOrm=a.max_orm, keepCrisp=a.keep_crisp, crispMax=a.crisp_max, simplify=a.simplify, pot=user_pot); optk = dict(opts, pot=a.pot)  # POT default applies to the KTX2 passes only
    with tempfile.TemporaryDirectory() as td:
        tmp = os.path.join(td, 'o.glb'); r = subprocess.run(['node', os.path.join(HERE, 'quest_transform.cjs'), src, tmp, json.dumps(opts)], capture_output=True, text=True)
        print(r.stdout.strip()); 
        if r.returncode: sys.exit('transform failed:\n' + r.stderr)
        shutil.move(tmp, out)
        if a.ktx2 and ktx_ok():
            # UASTC for normal maps (keeps detail), ETC1S for colour/ORM/emissive. Sources are resized already.
            k0, k1, k2 = (os.path.join(td, x) for x in ('k0.glb', 'k1.glb', 'k2.glb'))
            # pass A: same resize, PNG sources, no geometry compression -> toktx -> pass B: geometry compression on the KTX2 file
            subprocess.run(['node', os.path.join(HERE, 'quest_transform.cjs'), src, k0, json.dumps(dict(optk, geometry='none', forcePng=True))], check=True, capture_output=True)
            cmds = [[GT, 'uastc', k0, k1, '--slots', 'normalTexture', '--level', '2', '--zstd', '18'],
                                                     [GT, 'etc1s', k1, k2, '--slots', '{baseColorTexture,emissiveTexture,metallicRoughnessTexture,occlusionTexture}', '--quality', '192']]
            for c in cmds:
                rr = subprocess.run(c, env=env(), capture_output=True, text=True)
                if rr.returncode: print('WARN: KTX2 step failed:', rr.stderr[-800:]); break
            else:
                rb = subprocess.run(['node', os.path.join(HERE, 'quest_transform.cjs'), k2, outk, json.dumps(dict(optk, simplify=0))], capture_output=True, text=True)
                if rb.returncode: print('WARN: KTX2 geometry pass failed:', rb.stderr[-800:])
    if os.path.exists(outk) and 'KHR_texture_basisu' not in inspect(outk)['extensions']: print('WARN: KTX2 output has no KHR_texture_basisu (toktx/ktx too old? gltf-transform 4.5 needs KTX-Software >= 4.4)')
    for o in [out] + ([outk] if os.path.exists(outk) else []):
        aft = inspect(o); print(summary(aft, 'AFTER  ')); print(f'  size {before["bytes"]/1048576:.2f} -> {aft["bytes"]/1048576:.2f} MB, tex GPU {before["tex_gpu_bytes"]/1048576:.1f} -> {aft["tex_gpu_bytes"]/1048576:.1f} MB, LOD0 tris {before["lod0_tris"]:,} -> {aft["lod0_tris"]:,}')
        lost = {m['name']: m['custom_attrs'] for m in before['meshes']}; 
        for m in aft['meshes']:
            if m['name'] in lost and set(lost[m['name']]) - set(m['custom_attrs']): print(f'  FLAG: {m["name"]} lost custom attrs {set(lost[m["name"]]) - set(m["custom_attrs"])}')
if __name__ == '__main__': main()
