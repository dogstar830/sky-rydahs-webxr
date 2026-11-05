# Draco geometry decoding for the Quest Ikki GLB: local r128 DRACOLoader (classic global script) + decoder in libs/draco/.
# Coexists with patch_wardrobe.py's meshopt hook in ANY patch order: instead of rewriting call sites, we trap the
# THREE.GLTFLoader global (GLTFLoader.js is loaded later, dynamically, by initRiders) and replace it ONCE with a subclass
# whose constructor attaches the shared DRACOLoader + window.MeshoptDecoder (if present). Call-site chains such as
# `new THREE.GLTFLoader().setMeshoptDecoder(window.MeshoptDecoder)` (patch_wardrobe) keep working unchanged.
# IKKI_URL -> quest-draco GLB (?ikki=orig -> original GLB, ?ikki=<url> override). Idempotent.
import re
f='/workspace/v3build/sky-rydahs-v3-ikki.html'; src=open(f).read()
if 'window.SR_GLTF_WRAP' in src: print("patch_draco: already applied"); raise SystemExit
def rep(a,b):
    global src
    assert src.count(a)==1, ("anchor",a[:70],src.count(a)); src=src.replace(a,b)
T='<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>'
rep(T, T+'''
<script src="libs/draco/DRACOLoader.js"></script>
<script>/* patch_draco: every THREE.GLTFLoader gets the shared DRACOLoader + MeshoptDecoder (whenever/however it is created) */
(function(){ if(window.SR_GLTF_WRAP) return; window.SR_GLTF_WRAP=true; window.SR_DRACO=null;
  function draco(){ if(!window.SR_DRACO&&THREE.DRACOLoader){ window.SR_DRACO=new THREE.DRACOLoader(); window.SR_DRACO.setDecoderPath("libs/draco/"); } return window.SR_DRACO; }
  function wrap(Orig){ if(!Orig||Orig.__srWrapped) return Orig;
    class SRGLTFLoader extends Orig{ constructor(m){ super(m); const d=draco(); if(d&&!this.dracoLoader) this.setDRACOLoader(d);
      if(window.MeshoptDecoder&&!this.meshoptDecoder&&this.setMeshoptDecoder) this.setMeshoptDecoder(window.MeshoptDecoder); } }
    SRGLTFLoader.__srWrapped=true; SRGLTFLoader.__srOrig=Orig; return SRGLTFLoader; }
  let cur=wrap(THREE.GLTFLoader);
  Object.defineProperty(THREE,"GLTFLoader",{configurable:true,enumerable:true,get(){return cur;},set(v){cur=wrap(v);}});
  window.SR_GLTF=function(){ return new THREE.GLTFLoader(); }; })();</script>''')
# legacy call sites from an earlier patch_draco revision (SR_GLTF()) still work; no call-site rewrites needed
rep('const IKKI_URL=(new URLSearchParams(location.search).get("ikki"))||(CHAR_BASE+"meshy/ikki-meshy-skate.glb");',
    'const IKKI_URL=(q=>q==="orig"?CHAR_BASE+"meshy/ikki-meshy-skate.glb":q)(new URLSearchParams(location.search).get("ikki"))||(CHAR_BASE+"meshy/ikki-meshy-skate.quest-draco.glb");')
open(f,'w').write(src); print("patch_draco: GLTFLoader wrap installed; sites:",len(re.findall(r'new THREE\.GLTFLoader\(',src)))
