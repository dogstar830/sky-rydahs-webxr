# Runtime world draw-call pass (world_perf.js). Inserted at top level before the main loop; wraps staticMerge. Runs late in build_ikki.sh.
f=__import__('sys').argv[1] if len(__import__('sys').argv)>1 else '/workspace/v3build/sky-rydahs-v3-ikki.html'; src=open(f).read(); js=open('/workspace/v3build/world_perf.js').read()
a='// ===== LOOP =====\n'
assert src.count(a)==1, ("anchor",src.count(a)); src=src.replace(a, js+'\n'+a)
def rep(a,b):
    global src
    assert src.count(a)==1, ("anchor",a[:70],src.count(a)); src=src.replace(a,b)
# Sleeping Forest garage: dark (wall colour) was 0xe8e8e0 -> near-white walls read as a blown-out 'ST..ORE' box; dark forest green per Rydah Systems
rep('name:"SLEEPING FOREST",pos:[40,-275],face:"S",color:"#7CB342",dark:0xe8e8e0}', 'name:"SLEEPING FOREST",pos:[40,-275],face:"S",color:"#7CB342",dark:0x1c2a20}')
WP_SHIP_SEED=1  # shipping layout seed (chosen 2026-10-29, see DEMO_STATUS); ?seed=N overrides, ?seed=0 = legacy unseeded
rep('function rnd(a,b){ return a+Math.random()*(b-a); }', 'const _RSEED=(location.search.match(/[?&]seed=(\\d+)/)||[])[1]||"%d"; let _rs=(+_RSEED||1)>>>0; const _rr=()=>{ _rs^=_rs<<13; _rs^=_rs>>>17; _rs^=_rs<<5; return (_rs>>>0)/4294967296; };\nfunction rnd(a,b){ return a+(_RSEED!=="0"?_rr():Math.random())*(b-a); }\nfunction wpSeededWorld(fn){ if(_RSEED==="0") return fn(); const mr=Math.random; Math.random=_rr; try{ return fn(); } finally { Math.random=mr; } } // whole createCity() placement (Math.random too) follows the seed'%WP_SHIP_SEED)
rep('makeTextures(); createSky(); createCity();', 'makeTextures(); createSky(); wpSeededWorld(createCity);')
open(f,'w').write(src); print("patch_world_perf ok")
