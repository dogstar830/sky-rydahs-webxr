import os as _os; _SRC=_os.environ.get('SR_SRC','/workspace/v3build').rstrip('/')+'/'; _OUT=_os.environ.get('SR_HTML','/workspace/v3build/sky-rydahs-v3-ikki.html')  # Systems 10:25: SR_HTML / SR_SRC (default = old paths)
# Graffiti system (graffiti.js): S/M/L tag spots, Xbox-pad gesture tagging, mask-reveal paint per surface, shared mist pool,
# procedural can audio, night crew glow, TURF bridge (window.TURF) and window.HEAT. Runs just before patch_phone.py in build_ikki.sh.
# Idempotent: skips if already applied. Anchors are asserted to be unique so a drifted base fails loudly instead of half-patching.
f=_OUT; src=open(f).read(); js=open(_SRC+'graffiti.js').read()+'\n'+open(_SRC+'heat.js').read()+'\n'+open(_SRC+'perf/drawcalls/dc_meter.js').read()+'\n'+open(_SRC+'perf_overlay.js').read()  # heat.js (POLICE HEAT v1) appended after graffiti.js
if 'const GRAF={' in src: print("patch_graffiti: already applied"); raise SystemExit
def rep(a,b):
    global src
    assert src.count(a)==1, ("anchor",a[:70],src.count(a)); src=src.replace(a,b)
assert 'const TURF=' in src, "patch_graffiti needs patch_turf (TURF) applied first"
rep('// ===== LOOP =====', js+'\n// ===== LOOP =====')
R='  if(FX.on&&!xr&&!window.__noFX) FX.composer.render(); else renderer.render(scene,camera);'
rep(R,'  if(window.grafTick) window.grafTick(dt,xr);\n  if(window.heatTick) window.heatTick(dt,xr);\n  if(window.perfTick) window.perfTick(dt,xr);\n'+R)
open(f,'w').write(src); print("patch_graffiti ok")
