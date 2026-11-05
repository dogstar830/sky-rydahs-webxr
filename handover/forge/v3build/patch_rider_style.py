# Rydah Forge: inline rider_style.js (Option 3 stylized-realistic rider shading, OPT-IN ?riderstyle=opt3) before the main loop.
# Standalone; NOT in build_ikki.sh. Usage: python3 patch_rider_style.py /tmp/<copy>.html
import sys, os
f=sys.argv[1] if len(sys.argv)>1 else os.environ['SR_HTML']; src=open(f).read()
if 'const RIDER_STYLE=' in src: print("patch_rider_style: already applied"); sys.exit(0)
js=open('/workspace/v3build/rider_style.js').read(); a='// ===== LOOP =====\n'
assert src.count(a)==1, ("anchor",src.count(a)); src=src.replace(a, js+'\n'+a); open(f,'w').write(src); print("patch_rider_style ok")
