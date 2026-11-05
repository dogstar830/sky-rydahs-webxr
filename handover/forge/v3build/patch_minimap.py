# MINIMAP_V2: Watch Dogs-style tilted minimap + minimal direction markers (minimap_v2.js). Runs after patch_phone.py (needs map.js/icons.js). ?minimap=old keeps old HUD.
# GPS (heading-up, centred player, N on rim, rim-clamped waypoints, window.MINIMAP.state) — minimap_v2.js
import sys
f=__import__('os').environ.get('SR_HTML','/workspace/v3build/sky-rydahs-v3-ikki.html'); src=open(f).read()
if 'const MM2={' in src: print("patch_minimap: already applied"); raise SystemExit
js=open('/workspace/v3build/minimap_v2.js').read()
def rep(a,b):
    global src
    n=src.count(a)
    if n!=1: sys.exit("patch_minimap: ANCHOR MISMATCH (%d) for: %r"%(n,a[:80]))
    src=src.replace(a,b)
rep('\nfunction init(){', '\n'+js+'\nfunction init(){')
rep('  if(window.mapTick) mapTick(dt,xr);\n','  if(window.mapTick) mapTick(dt,xr);\n  if(window.mm2Tick) mm2Tick(dt,xr);\n')
rep('if(MAP.miniAcc>=.1&&!MAP.open)','if(MAP.miniAcc>=.1&&!MAP.open&&!window.__mmV2)')   # old minimap stops drawing when v2 is on
open(f,'w').write(src); print("patch_minimap ok")
