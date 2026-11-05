# Realism step 1 blockouts + collision additions (blockout.js). Runs after patch_sky, before patch_world_perf (so world_perf merges it).
# Additive: existing colliders / grind splines / graffiti + turf spots untouched; new gameplay data is appended late (BLOCKOUT.tick).
import sys
f=sys.argv[1] if len(sys.argv)>1 else '/workspace/v3build/sky-rydahs-v3-ikki.html'; src=open(f).read(); js=open('/workspace/v3build/blockout.js').read()
def rep(a,b):
    global src
    assert src.count(a)==1, ("anchor",a[:70],src.count(a)); src=src.replace(a,b)
rep('function createBridge(b){', js+'\nfunction createBridge(b){')
rep('createShoreFX(); buildInstancedBuildings();', 'createShoreFX(); BLOCKOUT.build(); buildInstancedBuildings();')
# SKYLINE GRIND story marker sat inside the TERMINAL tower collider [-6,-52,6,-40]; moved 8 m south onto clear land (Rydah Systems verified)
rep('{type:"story",title:"SKYLINE GRIND",pos:[0,-46]}', '{type:"story",title:"SKYLINE GRIND",pos:[0,-54]}')
open(f,'w').write(src); print("patch_blockout ok")
