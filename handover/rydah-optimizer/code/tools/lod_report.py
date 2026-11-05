#!/usr/bin/env python3
"""Inventory character GLBs and write perf/lod-budgets.{csv,json} + the table part of lod-budgets.md (read-only on assets)."""
import os, re, sys, json, csv
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); from glb_inspect import inspect
ROOT = '/workspace/skyrydahs-characters'; OUT = '/workspace/v3build/perf'
SKIP = [(r'-v1\.glb$', '-v1 (superseded)'), (r'-raw\.glb$', '-raw source'), (r'-4k\.glb$', '-4k'), (r'flatnormals', 'flatnormals backup'),
        (r'/v1_items/', 'v1 wardrobe items (superseded)'), (r'/_archive/', 'archive'), (r'/crew-coins/', 'crew coin prop (not a character)'),
        (r'\.quest-(draco|meshopt|meshopt16)\.glb$', 'compression A/B test copy'), (r'airtreck-meshy\.glb$', 'Meshy A-T source (1.8M tris, build input only)')]
def role(p):
    b = os.path.basename(p)
    if '/wardrobe/riders/' in p or '/meshy/' in p: return 'player'
    if '/WITHHELD_CHAR/' in p: return 'NPC' if 'npc' in b else 'player (placeholder)'
    if b.endswith('-fp.glb'): return 'player FP body'
    if '/skates/' in p or '/at-skate/' in p: return 'skate module'
    if '/wardrobe' in p: return 'wardrobe item'
    return 'NPC'
def tier(p, files):
    if '-hd' in p or '/wardrobe_hd/' in p: return 'desktop'
    if p.endswith('.quest.glb') or '/wardrobe/riders/caali-g.glb' in p: return 'quest'
    if p.replace('.glb', '.quest.glb') in files: return 'desktop'
    return 'both'
def judge(r, ro, ti):
    t, d = r['lod0_tris'], r['lod0_draws']; notes = []; st = 'PASS'
    if any('POSITION is' in f or 'mismatch' in f for f in r['flags']): st = 'FAIL'; notes.append('quantized POSITION / _WC mismatch')
    elif r['flags']: notes.append('KHR_mesh_quantization declared (POSITION float: OK, but strip on re-export)')
    if ro.startswith('player') and ro != 'player FP body':
        if ti == 'desktop': notes.append('desktop tier: tri budget n/a')
        elif t > 120000: st = 'FAIL'; notes.append(f'LOD0 {t:,} > 120k')
        elif t < 100000: st = 'WARN' if st == 'PASS' else st; notes.append(f'LOD0 {t:,} < 100k target (under budget)')
    elif ro == 'NPC':
        if ti != 'desktop' and t > 30000: st = 'FAIL'; notes.append(f'LOD0 {t:,} > 30k')
        if ti == 'desktop': notes.append('desktop tier (Quest uses .quest.glb)' if t > 30000 else 'desktop tier')
    if d > 6 and ro != 'wardrobe item': st = 'WARN' if st == 'PASS' else st; notes.append(f'{d} LOD0 prims (merge to <=3)')
    mx = max([max(x['w'], x['h']) for x in r['textures']] or [0])
    if ti != 'desktop' and r['tex_gpu_bytes'] > 32 << 20: st = 'WARN' if st == 'PASS' else st; notes.append(f'tex GPU {r["tex_gpu_bytes"]/1048576:.0f} MB (>32 MB on Quest)')
    if 'KHR_draco_mesh_compression' not in r['compression'] and 'EXT_meshopt_compression' not in r['compression'] and r['bytes'] > 1 << 20: notes.append('no geometry compression')
    return st, notes, mx
HTML = open('/workspace/v3build/sky-rydahs-v3-ikki.html', errors='ignore').read()
files = sorted(os.path.join(dp, f) for dp, _, fs in os.walk(ROOT) for f in fs if f.endswith('.glb')); fset = set(files)
rows, skipped = [], []
for p in files:
    rel = os.path.relpath(p, ROOT); why = next((w for rx, w in SKIP if re.search(rx, p)), None)
    if why: skipped.append((rel, os.path.getsize(p), why)); continue
    r = inspect(p); ro = role(p); ti = tier(p, fset); st, notes, mx = judge(r, ro, ti)
    rows.append(dict(asset=rel, in_build=('yes' if os.path.basename(p) in HTML else 'no'), role=ro, tier=ti, mb=round(r['bytes']/1048576, 2), lods=len(r['lods']), **{f'lod{k}_tris': r['lods'].get(k, {}).get('tris', '') for k in range(3)},
                     lod0_prims=r['lod0_draws'], materials=len(r['materials']), textures=';'.join(f'{t["w"]}x{t["h"]}:{t["fmt"]}:{"/".join(t["slots"])}' for t in r['textures']),
                     max_tex=mx, tex_gpu_mb=round(r['tex_gpu_bytes']/1048576, 1), compression=','.join(r['compression']) or 'none', status=st, notes='; '.join(notes), flags=' | '.join(r['flags'])))
order = {'FAIL': 0, 'WARN': 1, 'PASS': 2}; rows.sort(key=lambda x: (order[x['status']], -(x['lod0_tris'] or 0)))
json.dump({'rows': rows, 'skipped': skipped}, open(f'{OUT}/lod-budgets.json', 'w'), indent=1)
with open(f'{OUT}/lod-budgets.csv', 'w', newline='') as f: w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
md = ['| status | asset | in build | role | tier | MB | LOD0 / LOD1 / LOD2 tris | LOD0 prims | mats | max tex | tex GPU MB | compression | notes |', '|---|---|---|---|---|---|---|---|---|---|---|---|---|']
fmt = lambda v: f'{v:,}' if isinstance(v, int) else '-'
for r in rows: md.append(f'| {r["status"]} | {r["asset"]} | {r["in_build"]} | {r["role"]} | {r["tier"]} | {r["mb"]} | {fmt(r["lod0_tris"])} / {fmt(r["lod1_tris"])} / {fmt(r["lod2_tris"])} | {r["lod0_prims"]} | {r["materials"]} | {r["max_tex"]} | {r["tex_gpu_mb"]} | {r["compression"].replace("KHR_draco_mesh_compression","draco").replace("EXT_meshopt_compression","meshopt").replace("KHR_mesh_quantization","quant").replace("EXT_texture_webp","webp")} | {r["notes"]} |')
md += ['', '**Skipped:**', ''] + [f'- {s[0]} ({s[1]/1048576:.1f} MB): {s[2]}' for s in skipped]
open(f'{OUT}/.lod-table.md', 'w').write('\n'.join(md)); print('\n'.join(md))
