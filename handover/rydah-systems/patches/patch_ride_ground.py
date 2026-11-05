import os as _os; _SRC=_os.environ.get('SR_SRC','/workspace/v3build').rstrip('/')+'/'; _OUT=_os.environ.get('SR_HTML','/workspace/v3build/sky-rydahs-v3-ikki.html')  # Systems 10:25: SR_HTML / SR_SRC (default = old paths)
# RIDE_GROUND (ride_ground.js, Rydah Systems): rider y follows WORLD_GROUND. Must run right AFTER patch_ground.py
# (anchors on ground.js's export line) and before patch_grind/graffiti (so grapple/pad/aim wrappers stay outermost).
import sys
f=sys.argv[1] if len(sys.argv)>1 else _OUT; src=open(f).read(); js=open(_SRC+'ride_ground.js').read()
assert 'RIDE_GROUND (Rydah Systems' not in src, 'already patched'
a='window.WORLD_GROUND=WORLD_GROUND;'; assert src.count(a)==1, src.count(a)
src=src.replace(a, a+'\n'+js); open(f,'w').write(src); print("patch_ride_ground ok")
