// dc_probe.js - Sky Rydahs draw-call probe (READ-ONLY; not injected anywhere).
// Paste into devtools console of the built demo (desktop, non-XR, post/FX off), or load via
//   var s=document.createElement('script'); s.src='perf/drawcalls/dc_probe.js'; document.head.appendChild(s);
// then call: DC_PROBE.run('causeway_west')   -> prints table + renderer.info; returns the rows.
// Counts what three r128 would issue per frame for the current camera: visible, frustum-passing
// Mesh/Line/Points/Sprite (one draw per object per material group; InstancedMesh = 1), ink hulls
// (inkMat / BackSide children) separately, and shadow passes (castShadow meshes x shadow lights).
(function(){
  const P={};
  function topName(o){ let a=o, last=o; while(a.parent && a.parent.type!=='Scene'){ last=a.parent; a=a.parent; }
    const u=o.userData||{}, n=(last.name||'')+(u.worldPerf?'[world_perf:'+u.worldPerf+']':'');
    if(n) return n;
    if(o.matrixAutoUpdate===false && o.parent && o.parent.type==='Scene') return '[merged tile]';
    return '['+(last.type)+':'+(last.geometry&&last.geometry.type||'')+']'; }
  function matKey(m){ return (m.type||'?')+'#'+(m.name||m.uuid.slice(0,6))+(m.side===1?'/BackSide':'')+(m.map?'/tex':''); }
  P.run=function(label){
    const R=(typeof renderer!=='undefined')?renderer:window.renderer, S=(typeof scene!=='undefined')?scene:window.scene, C=(typeof camera!=='undefined')?camera:window.camera; // top-level let bindings are reachable by bare name if(!R||!S||!C){ console.warn('dc_probe: renderer/scene/camera not global'); return; }
    S.updateMatrixWorld(true); C.updateMatrixWorld(true);
    const fr=new THREE.Frustum(), pm=new THREE.Matrix4().multiplyMatrices(C.projectionMatrix,C.matrixWorldInverse); fr.setFromProjectionMatrix(pm);
    const ink=(typeof inkMat!=='undefined')?inkMat:null, rows={}; let total=0, hulls=0, shadowCasters=0, culledFC=0;
    const lights=[]; S.traverseVisible(o=>{ if(o.isLight&&o.castShadow) lights.push(o); });
    S.traverseVisible(o=>{
      if(!(o.isMesh||o.isLine||o.isPoints||o.isSprite)) return;
      if(o.frustumCulled!==false){ if(o.isSprite? !fr.intersectsSprite(o) : (o.geometry&&!fr.intersectsObject(o))) return; } else culledFC++;
      const mats=Array.isArray(o.material)?o.material:[o.material]; const groups=Array.isArray(o.material)?Math.max(1,(o.geometry.groups||[]).length):1;
      const isHull=(ink&&o.material===ink)||(mats[0]&&mats[0].side===1&&mats[0].color&&mats[0].color.getHex()===0);
      const n=groups, k=topName(o)+' | '+matKey(mats[0])+(o.isInstancedMesh?' (inst x'+o.count+')':'');
      const r=rows[k]||(rows[k]={module:topName(o),material:matKey(mats[0]),objects:0,draws:0,hull:isHull,noFrustum:0}); r.objects++; r.draws+=n; if(o.frustumCulled===false) r.noFrustum++;
      total+=n; if(isHull) hulls+=n; if(o.castShadow&&o.isMesh) shadowCasters+=lights.length; });
    const list=Object.values(rows).sort((a,b)=>b.draws-a.draws);
    R.render(S,C); const info=Object.assign({},R.info.render);
    console.log('%cdc_probe '+(label||'')+' @ cam '+C.position.toArray().map(v=>v.toFixed(1)).join(','),'font-weight:bold');
    console.table(list.slice(0,60));
    const mods={}; list.forEach(r=>{ mods[r.module]=(mods[r.module]||0)+r.draws; });
    console.table(Object.entries(mods).sort((a,b)=>b[1]-a[1]).map(([module,draws])=>({module,draws})));
    const sum={label,estDraws:total,inkHullDraws:hulls,shadowPassDraws:shadowCasters,frustumCulledFalse:culledFC,
      renderer_calls:info.calls,renderer_tris:info.triangles,far:C.far,fog:S.fog&&[S.fog.near,S.fog.far],
      merge:window.__merge, worldPerf:(window.WORLD_PERF&&WORLD_PERF.stats)||null};
    console.log(JSON.stringify(sum)); P.last={sum,list}; return P.last; };
  P.json=function(){ return JSON.stringify(P.last); };
  window.DC_PROBE=P;
})();
