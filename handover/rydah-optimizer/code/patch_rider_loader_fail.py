# Rydah Optimizer: Claude cold-review rider-loader fixes (via Systems). Sets RIDERS.fail so harness
# never treats a null player as ready; prefers vendored r128 GLTFLoader/BufferGeometryUtils/meshopt
# under vendor/three/examples/js/ with CDN fallback. Idempotent. Runs AFTER patch_wardrobe.py
# (which expands the go() tail and injects meshopt into L/need).
import os
f = os.environ.get('SR_HTML', '/workspace/v3build/sky-rydahs-v3-ikki.html')
src = open(f).read()
def rep(o, n, cnt=1):
    global src
    if o not in src:
        if n in src or (isinstance(n, str) and n[:40] in src):
            print('patch_rider_loader_fail: already applied (skip)', o[:60]); return False
        raise AssertionError('missing anchor: '+o[:120])
    src = src.replace(o, n, cnt); return True
n = 0
if rep("const RIDERS={ player:null, fp:null, npcs:[] };",
       "const RIDERS={ player:null, fp:null, npcs:[], fail:false };"): n += 1
# Prefer local vendor; keep CDN as fallback. L/need already include meshopt from patch_wardrobe.
old_base = 'const L=["libs/meshopt_decoder.js","loaders/GLTFLoader.js","utils/BufferGeometryUtils.js"], base="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/";'
new_base = ('const L=["libs/meshopt_decoder.js","loaders/GLTFLoader.js","utils/BufferGeometryUtils.js"];'
            ' const bases=["vendor/three/examples/js/","https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/"]; let base=bases[0];')
if 'const bases=["vendor/three/examples/js/"' in src:
    print('patch_rider_loader_fail: bases already present')
elif old_base in src:
    src = src.replace(old_base, new_base, 1); n += 1
else:
    # wardrobe may not have run / meshopt not injected — fall back to 2-file form
    old_base2 = 'const L=["loaders/GLTFLoader.js","utils/BufferGeometryUtils.js"], base="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/";'
    new_base2 = ('const L=["loaders/GLTFLoader.js","utils/BufferGeometryUtils.js"];'
                 ' const bases=["vendor/three/examples/js/","https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/"]; let base=bases[0];')
    if rep(old_base2, new_base2): n += 1

# go() catch on the next() entry
old_go = 'if(i>=L.length){ go(); return; }'
new_go = 'if(i>=L.length){ go().catch(e=>{ RIDERS.fail="go:"+(e&&e.message||e); console.error("riders go() failed",e); }); return; }'
if 'go().catch(e=>{ RIDERS.fail="go:"' in src:
    print('patch_rider_loader_fail: go().catch already present')
elif old_go in src:
    # only the initRiders next() — that string appears once there
    src = src.replace(old_go, new_go, 1); n += 1
else:
    raise AssertionError('missing go() next anchor')

# script onerror -> RIDERS.fail, with multi-base retry
# Current (post-wardrobe) next body after go() catch applied above:
old_onerr = 's.onerror=()=>console.warn("rider loader script failed "+L[i]);'
new_onerr = 's.onerror=()=>{ RIDERS.fail="cdn:"+L[i]; console.warn("rider loader script failed "+L[i]); };'
# Upgrade whole next() to tryBase across bases when bases[] exists
# Find the next= block for riders (unique: rider loader script failed)
import re
m = re.search(
    r'const next=i=>\{ if\(i>=L\.length\)\{ go\(\)\.catch\(e=>\{ RIDERS\.fail="go:"\+\(e&&e\.message\|\|e\); console\.error\("riders go\(\) failed",e\); \}\); return; \} if\(THREE\[need\[i\]\](?:\|\|window\[need\[i\]\])?\)\{ next\(i\+1\); return; \} const s=document\.createElement\("script"\); s\.src=base\+L\[i\]; s\.onload=\(\)=>next\(i\+1\); s\.onerror=\(\)=>console\.warn\("rider loader script failed "\+L\[i\]\); document\.head\.appendChild\(s\); \}; next\(0\);',
    src)
if m:
    new_next = (
      'const next=i=>{ if(i>=L.length){ go().catch(e=>{ RIDERS.fail="go:"+(e&&e.message||e); console.error("riders go() failed",e); }); return; }'
      ' if(THREE[need[i]]||window[need[i]]){ next(i+1); return; }'
      ' let bi=0; const tryBase=()=>{ const s=document.createElement("script"); s.src=bases[bi]+L[i];'
      ' s.onload=()=>{ base=bases[bi]; next(i+1); };'
      ' s.onerror=()=>{ if(bi+1<bases.length){ bi++; tryBase(); }'
      ' else { RIDERS.fail="cdn:"+L[i]; console.warn("rider loader script failed "+L[i]); } };'
      ' document.head.appendChild(s); }; tryBase(); }; next(0);')
    src = src[:m.start()] + new_next + src[m.end():]; n += 1
elif 'tryBase=()=>' in src and 'RIDERS.fail="cdn:"' in src:
    print('patch_rider_loader_fail: tryBase already present')
elif old_onerr in src:
    src = src.replace(old_onerr, new_onerr, 1); n += 1
else:
    if 'RIDERS.fail="cdn:"' in src:
        print('patch_rider_loader_fail: onerror fail already present')
    else:
        raise AssertionError('missing rider onerror anchor')

# no-player fail just before ready
old_ready = '    RIDERS.ready=true; };'
new_ready = '    RIDERS.fail=RIDERS.fail||(!RIDERS.player&&"no-player"); RIDERS.ready=true; };'
if 'RIDERS.fail=RIDERS.fail||(!RIDERS.player&&"no-player")' in src:
    print('patch_rider_loader_fail: no-player already present')
elif old_ready in src:
    src = src.replace(old_ready, new_ready, 1); n += 1
else:
    raise AssertionError('missing RIDERS.ready anchor')

open(f,'w').write(src)
print(f'patch_rider_loader_fail: applied {n} edits -> {f}')
