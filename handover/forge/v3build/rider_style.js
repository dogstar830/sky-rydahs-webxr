// ===== RIDER_STYLE (Rydah Forge, 2026-10-30): Oliver's Option 3 "stylized realistic" rider shading. OPT-IN ?riderstyle=opt3 (off by default) =====
// Per Optimizer's opt3 direction (perf/rider-style-opt3-constraints.md): PBR consistent with pbr_world (shared Portside PMREM from PBR_WORLD.ENV[cur],
// renderer ACES + PBR_WORLD.GR exposure, toneMapped), crew-colour fresnel rim on the GEOMETRIC normal, hair spec, gentle shadow tint, skin warmth,
// rim+spec capped so lit riders stay < .85 luma (FXBLOOM hot band), NO outline. Crew NPCs: toon -> PBR, inverted hull disabled (3 -> 2 draws each).
// Colour convention unchanged (renderer outputEncoding Linear; body maps Linear as ikki_skate sets them) so body/skate/crew don't drift apart.
// Fixed program keys per original shader ('rider-opt3|'+origKey); per-rider colours are uniforms only. Prewarmed with renderer.compile after each swap.
const RIDER_STYLE=(()=>{ const q=new URLSearchParams(location.search), S={on:q.get('riderstyle')==='opt3', mats:[], stats:{body:0,skate:0,crew:0,other:0,hullOff:0,skip:0}, envKey:null};
  const OPT3=`
{ vec3 rsV=normalize(vViewPosition); float rsNdv=clamp(dot(rsGN,rsV),0.,1.); float rsFr=pow(1.-rsNdv,3.);
  float rsL=dot(outgoingLight,vec3(.2126,.7152,.0722));
  outgoingLight=mix(outgoingLight,outgoingLight*vec3(.86,.9,1.06)+diffuseColor.rgb*vec3(.012,.016,.03),1.-smoothstep(.0,.16,rsL));   // gentle cool shadow tint
  vec3 dc=diffuseColor.rgb; float rsSkin=smoothstep(.05,.2,dc.r-dc.b)*step(dc.g,dc.r)*smoothstep(.2,.4,dc.r);
  outgoingLight+=dc*vec3(.09,.03,.015)*rsSkin*(.5+.5*rsFr);                                                                     // subsurface-ish warmth
  float rsH=uRsHair*pow(clamp(1.-abs(rsGN.y-.45)*2.2,0.,1.),6.)*(1.-.6*roughnessFactor);                                       // hair spec band
  vec3 rsAdd=uRsRim*min(rsFr*.25,.25)+vec3(min(rsH*.3,.3));
  float rsRoom=max(.85-dot(outgoingLight,vec3(.2126,.7152,.0722)),0.); float rsAL=dot(rsAdd,vec3(.2126,.7152,.0722));
  outgoingLight+=rsAdd*min(1.,rsRoom/max(rsAL,1e-4)); }                                                                          // cap: lit rider < .85 luma
#include <output_fragment>`;
  function inject(s,U){ Object.assign(s.uniforms,U);
    s.fragmentShader=s.fragmentShader.replace('#include <common>','#include <common>\n uniform vec3 uRsRim; uniform float uRsHair;')
      .replace('#include <normal_fragment_begin>','#include <normal_fragment_begin>\n vec3 rsGN=normal;')
      .replace('#include <output_fragment>',OPT3); }
  function rimOf(root){ const u=root.userData||{}; for(const k of ['rim','rimColor']) if(u[k]!=null) return new THREE.Color(u[k]);
    const d=u.defaults||(u.def&&u.def.defaults)||(u.cfg&&u.cfg.defaults); if(d&&d.rim!=null) return new THREE.Color(d.rim); if(u.glow!=null) return new THREE.Color(u.glow); return null; }
  function track(m){ m.toneMapped=true; S.mats.push(m); const P=window.PBR_WORLD; if(P&&P.on&&P.mats&&!P.mats.includes(m)) P.mats.push(m); }
  // body / skate / wardrobe items: keep the original material (Rigger's onBeforeCompile), chain opt3 after it
  function upStd(m,kind,rim){ if(m.userData.rs) return; const prev=m.onBeforeCompile, key=(m.customProgramCacheKey&&m.customProgramCacheKey!==THREE.Material.prototype.customProgramCacheKey)?m.customProgramCacheKey.call(m):'';
    const U={uRsRim:{value:rim||new THREE.Color(0x9fd8ff)},uRsHair:{value:kind==='hair'?1:0}}; m.userData.rs=U;
    m.onBeforeCompile=function(s,r){ if(prev) prev.call(this,s,r); inject(s,U); }; m.customProgramCacheKey=()=>'rider-opt3|'+key; m.needsUpdate=true; track(m); }
  // crew toon (riders.js rToon): capture its shared slot uniforms by running its onBeforeCompile on a stub, rebuild as MeshStandard with the same slot recolour
  function upToon(o,rim){ const t=o.material, cap={uniforms:{},vertexShader:'',fragmentShader:''}; try{ t.onBeforeCompile(cap); }catch(e){ S.stats.skip++; return; }
    const SU=cap.uniforms; if(!SU.uSlotColor){ S.stats.skip++; return; }
    const m=new THREE.MeshStandardMaterial({color:0xffffff,map:t.map,roughness:.6,metalness:0,skinning:true,side:t.side});
    const U={uRsRim:{value:rim||(SU.uRimColor&&SU.uRimColor.value)||new THREE.Color(0x9fd8ff)},uRsHair:{value:0}}; m.userData.rs=U;
    m.onBeforeCompile=s=>{ Object.assign(s.uniforms,{uSlotColor:SU.uSlotColor,uSlotRim:SU.uSlotRim,uSlotSpec:SU.uSlotSpec,uSlotEmi:SU.uSlotEmi,uSlotHL:SU.uSlotHL,uPainted:SU.uPainted});
      s.fragmentShader=s.fragmentShader.replace('#include <common>','#include <common>\n'+RSLOT_GLSL)
        .replace('#include <map_fragment>',`#include <map_fragment>
 int sl=riderSlot(vUv); vec3 slc=uSlotColor[0]; float semi=0., shl=0., sspec=0.;
 for(int i=0;i<NSLOTS;i++){ if(i==sl){ slc=uSlotColor[i]; semi=uSlotEmi[i]; shl=uSlotHL[i]; sspec=uSlotSpec[i]; } }
 float hlMask=uPainted*smoothstep(.9,.98,texelColor.r); diffuseColor.rgb*=slc;`)
        .replace('#include <roughnessmap_fragment>','#include <roughnessmap_fragment>\n roughnessFactor=mix(.68,.32,clamp(sspec,0.,1.));')
        .replace('#include <emissivemap_fragment>','#include <emissivemap_fragment>\n totalEmissiveRadiance+=slc*semi+mix(vec3(1.),slc,.3)*hlMask*shl*.6;');
      inject(s,U); };
    m.customProgramCacheKey=()=>'rider-opt3|crew'; o.material=m; track(m); S.stats.crew++; }
  function hull(o){ const m=o.material; return m&&m.isShaderMaterial&&m.side===THREE.BackSide&&m.uniforms&&m.uniforms.uThick; }
  function convert(o,root,rim){ const m=o.material; if(!m||Array.isArray(m)||m.userData.rs){ return; }
    if(hull(o)){ m.visible=false; m.userData.rs=1; S.stats.hullOff++; return; }                    // no outline pass in opt3 (material.visible=false -> 0 draws)
    if(m.isMeshToonMaterial){ if(m.customProgramCacheKey&&m.customProgramCacheKey()==='rider-toon-r128') upToon(o,rim); else S.stats.skip++; return; }
    if(m.isMeshStandardMaterial&&!m.transparent){ const key=m.customProgramCacheKey?m.customProgramCacheKey.call(m):''; const hair=/hair|braid|pigtail/i.test(o.name+' '+(m.name||''));
      const kind=hair?'hair':/ikki-pbr/.test(key)?'body':/skate/.test(key)?'skate':'other'; upStd(m,kind,rim); S.stats[kind==='hair'?'other':kind]++; return; }
    S.stats.skip++; }   // glow (MeshBasic), sprites, blob shadows stay as they are
  function roots(){ const R=typeof RIDERS!=='undefined'?RIDERS:window.RIDERS, out=[]; if(!R) return out;
    for(const k of ['player','fp','ikkiNpc','akitoNpc']) if(R[k]&&R[k].isObject3D) out.push(R[k]);
    for(const n of (R.npcs||[])){ const g=n&&(n.isObject3D?n:(n.group||n.root||n.mesh)); if(g&&g.isObject3D) out.push(g); } return out; }
  function sweep(){ const n0=S.mats.length; for(const r of roots()){ let rim=null; r.traverse(o=>{ if(!rim) rim=rimOf(o); }); r.traverse(o=>{ if(o.isMesh&&!o.isSprite) convert(o,r,rim); }); }
    if(S.mats.length>n0){ S.envKey=null; try{ renderer.compile(scene,camera); }catch(e){} } }   // prewarm: new programs compile here, never mid-gameplay per frame
  function env(){ const P=window.PBR_WORLD; if(!(P&&P.on&&P.ENV)) return; const k=P.ENV.cur||'night', t=P.ENV[k]; if(!t) return; const key=k+'|'+S.mats.length; if(S.envKey===key) return;
    S.envKey=key; for(const m of S.mats){ m.envMap=t; m.envMapIntensity=Math.min(m.envMapIntensity||1,1.0); m.needsUpdate=true; } S.envSrc='PBR_WORLD.'+k; }
  S.sweep=sweep; S.env=env;
  if(S.on){ let f=0; (function rsLoop(){ try{ if(f++%30===0) sweep(); env(); }catch(e){ S.err=String(e); } requestAnimationFrame(rsLoop); })(); }
  return S; })();
window.RIDER_STYLE=RIDER_STYLE;
