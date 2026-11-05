# Palma Builder: inline pbr_base.js (PBR building-base band) right AFTER the pbr_world.js block, before the main loop.
# NOT in build_ikki.sh yet (chain slot pending Ani). Run after patch_pbr_world.py. Test copies: python3 patch_pbr_base.py /tmp/<copy>.html
import sys, os
f=sys.argv[1] if len(sys.argv)>1 else os.environ.get('SR_HTML','/workspace/v3build/sky-rydahs-v3-ikki.html'); src=open(f).read()
if 'const PBR_BASE=' in src: print("patch_pbr_base: already applied"); sys.exit(0)
assert 'const PBR_WORLD=' in src, "patch_pbr_base: run patch_pbr_world.py first"
js=open(os.environ.get('SR_SRC','/workspace/v3build').rstrip('/')+'/pbr_base.js').read(); a='// ===== LOOP =====\n'
assert src.count(a)==1, ("anchor",src.count(a)); src=src.replace(a, js+'\n'+a)
open(f,'w').write(src); print("patch_pbr_base ok")
