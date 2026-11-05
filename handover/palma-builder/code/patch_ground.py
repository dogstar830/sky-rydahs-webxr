# WORLD_GROUND (ground.js): world-side ground height/surface query. Runs right after patch_blockout (uses BLOCKOUT data at runtime).
# Report-only: nothing in the rider changes unless ride_ground.js (Rydah Systems) consumes it.
import sys
f=sys.argv[1] if len(sys.argv)>1 else '/workspace/v3build/sky-rydahs-v3-ikki.html'; src=open(f).read(); js=open('/workspace/v3build/ground.js').read()
a='function createBridge(b){'; assert src.count(a)==1, src.count(a)
src=src.replace(a, js+'\n'+a); open(f,'w').write(src); print("patch_ground ok")
