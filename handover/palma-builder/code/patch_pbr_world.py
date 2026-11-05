# Palma Builder: inline pbr_world.js (realism step 5 slice 1, DEFAULT ON; ?toon=1 / ?pbr=0 = old look) right after world_perf.js, before the main loop. Run after patch_world_perf.py.
import sys, os
f=sys.argv[1] if len(sys.argv)>1 else os.environ.get('SR_HTML','/workspace/v3build/sky-rydahs-v3-ikki.html'); src=open(f).read()  # build_copy.sh sets SR_HTML
if 'const PBR_WORLD=' in src: print("patch_pbr_world: already applied"); sys.exit(0)
js=open(os.environ.get('SR_SRC','/workspace/v3build').rstrip('/')+'/pbr_world.js').read(); a='// ===== LOOP =====\n'
assert src.count(a)==1, ("anchor",src.count(a)); src=src.replace(a, js+'\n'+a)
open(f,'w').write(src); print("patch_pbr_world ok")
