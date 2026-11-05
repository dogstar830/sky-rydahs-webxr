# Rydah Forge: CombatFX (combat_fx.js) attack FX module. Inert unless called (pools prewarmed + hidden = 0 draws); ?fxdemo=1 loops every effect x crew; ?nocfx disables.
# Usage: python3 patch_combat_fx.py [html]  (or SR_HTML=path)  (default = the real build). Idempotent. Runs LAST in build_ikki.sh (needs scene/camera/renderer/animated globals).
import sys,os
f=sys.argv[1] if len(sys.argv)>1 else os.environ.get('SR_HTML','/workspace/v3build/sky-rydahs-v3-ikki.html')
src=open(f).read(); js=open('/workspace/v3build/combat_fx.js').read()
A,B='<script>/* patch_combat_fx */','/* /patch_combat_fx */</script>'
if A in src: src=src[:src.index(A)]+src[src.index(B)+len(B):]
assert src.count('</body>')==1,'patch_combat_fx: </body> miss'
src=src.replace('</body>',A+'\n'+js+'\n'+B+'\n</body>',1)
open(f,'w').write(src); print('patch_combat_fx ok')
