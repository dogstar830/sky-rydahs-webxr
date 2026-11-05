import os as _os; _SRC=_os.environ.get('SR_SRC','/workspace/v3build').rstrip('/')+'/'; _OUT=_os.environ.get('SR_HTML','/workspace/v3build/sky-rydahs-v3-ikki.html')  # Systems 10:25: SR_HTML / SR_SRC (default = old paths)
# Pole grind (polegrind.js: spiral climb, Rigger polegrind state, double-helix FX) + pooled trail ribbon (trails.js). Rydah Systems.
# Runs right after patch_grind.py (wraps grindStep/grindTick, uses grindAll/grindLock/grindSpark). Injected just before the main loop marker.
f=_OUT; src=open(f).read()
if 'const PG={ on:false' in src: print("patch_polegrind: already applied"); raise SystemExit
assert 'const GRIND={' in src, "patch_polegrind needs patch_grind first"
js=open(_SRC+'polegrind.js').read()+'\n'+open(_SRC+'trails.js').read()
assert src.count("// ===== LOOP =====")==1
src=src.replace("// ===== LOOP =====",js+"\n// ===== LOOP =====")
open(f,'w').write(src); print("patch_polegrind ok")
