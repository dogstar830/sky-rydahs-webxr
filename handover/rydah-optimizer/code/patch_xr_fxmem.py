# XR FX memory (Rydah Optimizer, owner of setupFX/EffectComposer). On renderer.xr 'sessionstart' dispose the EffectComposer
# renderTarget1/2 (+ depthTexture via rt.dispose) and every pass's internal targets (UnrealBloomPass bright + 5 H + 5 V); on
# 'sessionend' composer.setPixelRatio()+setSize(). Verified on r128 source: WebGLRenderTarget.dispose() -> deallocateRenderTarget
# deletes GL texture/FBO/depth and drops properties; the JS objects stay, and setupRenderTarget/setupDepthTexture re-upload
# lazily on next setRenderTarget, so setSize alone restores identical desktop FX (no composer rebuild needed).
# The main loop already renders direct while presenting (FX.on&&!xr); we also no-op composer.render while freed as a guard.
# v2 (02:2x): only composer rt1/rt2 + depth disposed (~33 MB @1080p); bloom kept unless ?xrfxbloom=1; generic pass.dispose() dropped.
# ?xrfxkeep=1 disables. Exposes window.__XRFXMEM={disposed,restored,bytesFreedEst,freed}. Run after patch_ikki_skate.py (setupFX). Idempotent.
f=__import__('sys').argv[1] if len(__import__('sys').argv)>1 else '/workspace/v3build/sky-rydahs-v3-ikki.html'; src=open(f).read()
# --- FXBLOOM stage (Palma Builder proposal perf/fx/setupFX_bloom.proposed.diff, reviewed+landed by Rydah Optimizer 30 Oct):
# patch only UnrealBloomPass's high-pass shader after cmp.addPass(bloom): bloom only from hot pixels (luma>=~.9) or saturated near-1 emitters.
# 0 draws/passes/targets; falls back to stock bloom if the r128 shader anchor is missing; FX.bloomHot=true when active. Idempotent (/*FXBLOOM*/).
FXB_A='cmp.addPass(bloom); cmp.addPass(new THREE.ShaderPass(GradeShader));'
if '/* FXBLOOM */' in src: print("patch_xr_fxmem(fxbloom): already applied")
else:
    assert src.count(FXB_A)==1, ("fxbloom anchor", src.count(FXB_A))
    src=src.replace(FXB_A, FXB_A+r'''
  { const hp=bloom.materialHighPassFilter, K='float alpha = smoothstep( luminosityThreshold, luminosityThreshold + smoothWidth, v );';
    if(hp&&hp.fragmentShader.indexOf(K)>=0){ hp.uniforms.uFxbHot={value:new THREE.Vector4(.88,.97,.97,1.0)};
      hp.fragmentShader='uniform vec4 uFxbHot;\n'+hp.fragmentShader.replace(K,'float mx = max( texel.r, max( texel.g, texel.b ) ); float sat = ( mx - min( texel.r, min( texel.g, texel.b ) ) ) / max( mx, 1e-3 ); float alpha = max( smoothstep( max( luminosityThreshold, uFxbHot.x ), max( uFxbHot.y, max( luminosityThreshold, uFxbHot.x ) + .02 ), v ), smoothstep( uFxbHot.z, uFxbHot.w, mx ) * smoothstep( .6, .75, sat ) ); /* FXBLOOM */');
      hp.needsUpdate=true; FX.bloomHot=true; } else console.warn('[fxbloom] high-pass anchor missing; bloom unchanged'); }''',1)
    print("patch_xr_fxmem(fxbloom): high-pass patched")
MARK='/* XRFXMEM v2 */'
if MARK in src: open(f,'w').write(src); print("patch_xr_fxmem already applied"); raise SystemExit(0)
_o='/* XRFXMEM v1 */'; _e='if(renderer.xr.isPresenting) M.onStart(); }'
if _o in src:  # upgrade an html that already carries v1 (normal builds start from the clean base and never hit this)
    i=src.index(_o); j=src.index(_e,i)+len(_e); src=src[:i]+'}'+src[j:]
a='cmp.setPixelRatio(Math.min(devicePixelRatio,1.25)); cmp.setSize(W,H); FX.composer=cmp; FX.on=true; FX.bloom=bloom; }'
assert src.count(a)==1, ("anchor setupFX tail", src.count(a))
js=MARK+r''' try{ xrFxMemInit(); }catch(e){ console.warn("xrfxmem",e); } }
function xrFxMemInit(){ const M=window.__XRFXMEM=window.__XRFXMEM||{disposed:0,restored:0,bytesFreedEst:0,freed:false,off:/[?&]xrfxkeep=1/.test(location.search)};
  if(M.off||M.hooked||!FX.composer||!renderer.xr) return; M.hooked=true; const C=FX.composer, PR=()=>Math.min(devicePixelRatio,1.25);
  const _cr=C.render.bind(C); C.render=function(dt){ if(M.freed) return renderer.render(scene,camera); return _cr(dt); }; // guard: never touch freed targets
  const BL=/[?&]xrfxbloom=1/.test(location.search); // v2: bloom targets (~2 MB) kept by default, opt-in dispose only
  const targets=()=>{ const L=[C.renderTarget1,C.renderTarget2]; if(BL) for(const p of C.passes){ if(p.renderTargetBright) L.push(p.renderTargetBright); if(p.renderTargetsHorizontal) L.push(...p.renderTargetsHorizontal); if(p.renderTargetsVertical) L.push(...p.renderTargetsVertical); } return L.filter(Boolean); };
  const bytes=rt=>(rt.width*rt.height*((rt.texture&&rt.texture.type===THREE.HalfFloatType)?8:(rt.texture&&rt.texture.type===THREE.FloatType)?16:4))+(rt.depthTexture?rt.width*rt.height*4:(rt.depthBuffer?rt.width*rt.height*4:0));
  M.onStart=function(){ if(M.freed) return; M.freed=true; let n=0,b=0;
    for(const rt of targets()){ b+=bytes(rt); n+=1+(rt.depthTexture?1:0); rt.dispose(); } // GL texture+FBO(+depthTexture) freed; objects kept for lazy re-upload
    M.disposed+=n; M.bytesFreedEst=b; M.lastStart=performance.now(); };
  M.onEnd=function(){ if(!M.freed) return; M.freed=false; C.writeBuffer=C.renderTarget1; C.readBuffer=C.renderTarget2; C.setPixelRatio(PR()); C.setSize(innerWidth,innerHeight); M.restored++; }; // r128 setSize -> rt.setSize; targets realloc on next render
  renderer.xr.addEventListener("sessionstart",M.onStart); renderer.xr.addEventListener("sessionend",M.onEnd);
  if(renderer.xr.isPresenting) M.onStart(); }'''
src=src.replace(a, a[:-1]+js)
open(f,'w').write(src); print("patch_xr_fxmem ok")
