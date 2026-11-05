// dc_meter.js - Sky Rydahs draw-call METER mode (Rydah Optimizer). Companion to dc_probe.js; test-injected only
// (page.add_script_tag after load). Never edits the game: read-only traversal + renderer.info reads.
// window.DC_METER.sample(label) -> Promise<{calls,triangles,geometries,textures,world,chars,fx,est,byModule:[...]}>
//   calls/triangles = renderer.info.render of the LAST completed frame (autoReset, post off => 1 renderer.render/frame).
//   chars/fx = estimated draws of visible, frustum-passing objects under a character/FX root (dc_probe rules);
//   world = calls - chars - fx (so world+chars+fx == calls exactly; sky/background lands in world).
(function(){
  const CHAR_RE=/rider|player|ikki|wardrobe|skate|WITHHELD_CHAR|caali|npc|jacket/i, FX_RE=/trail|fx|particle|spark|sprite|aura|speedline|reticle/i;
  function G(n){ try{ return eval(n); }catch(e){ return window[n]; } } // top-level let bindings
  function roots(){ const ch=new Set(), fx=new Set(); const Rd=G('Ride'), RI=G('RIDERS'), GR=G('GRIND');
    if(Rd&&Rd.group) ch.add(Rd.group);
    if(RI){ (RI.npcs||[]).forEach(n=>n.holder&&ch.add(n.holder)); if(RI.ikkiNpc&&RI.ikkiNpc.holder) ch.add(RI.ikkiNpc.holder); if(RI.ref&&RI.ref.holder) ch.add(RI.ref.holder); }
    if(GR&&GR.spk&&GR.spk.pts) fx.add(GR.spk.pts); return {ch,fx}; }
  function topName(o){ let a=o,last=o; while(a.parent&&a.parent.type!=='Scene'){ last=a.parent; a=a.parent; } return last.name||('['+last.type+':'+((last.geometry&&last.geometry.type)||'')+']'); }
  function classify(o,R){ let a=o; while(a){ if(R.fx.has(a)) return 'fx'; if(R.ch.has(a)) return 'chars'; a=a.parent; }
    a=o; while(a&&a.type!=='Scene'){ const n=a.name||''; if(FX_RE.test(n)) return 'fx'; if(CHAR_RE.test(n)) return 'chars'; a=a.parent; }
    if(o.isSprite) return 'fx'; return 'world'; }
  function estimate(){ const S=G('scene'), C=G('camera'); S.updateMatrixWorld(true); C.updateMatrixWorld(true);
    const fr=new THREE.Frustum().setFromProjectionMatrix(new THREE.Matrix4().multiplyMatrices(C.projectionMatrix,C.matrixWorldInverse));
    const R=roots(), mods={}, cls={world:0,chars:0,fx:0};
    S.traverseVisible(o=>{ if(!(o.isMesh||o.isLine||o.isPoints||o.isSprite)) return;
      if(o.frustumCulled!==false){ if(o.isSprite?!fr.intersectsSprite(o):(o.geometry&&!fr.intersectsObject(o))) return; }
      if(o.isInstancedMesh&&o.count===0) return;
      const n=Array.isArray(o.material)?Math.max(1,(o.geometry.groups||[]).length):1, c=classify(o,R), m=topName(o)+' ['+c+']';
      cls[c]+=n; const r=mods[m]||(mods[m]={module:m,cls:c,draws:0,objects:0}); r.draws+=n; r.objects++; });
    return {cls,byModule:Object.values(mods).sort((a,b)=>b.draws-a.draws)}; }
  function frame(){ return new Promise(r=>requestAnimationFrame(()=>r())); }
  async function sample(label){ await frame(); const Rr=G('renderer'), i=Rr.info; const e=estimate();
    const calls=i.render.calls, chars=e.cls.chars, fx=e.cls.fx;
    return {label:label||'',calls,triangles:i.render.triangles,geometries:i.memory.geometries,textures:i.memory.textures,
      world:Math.max(0,calls-chars-fx),chars,fx,est:e.cls.world+chars+fx,estWorld:e.cls.world,byModule:e.byModule}; }
  window.DC_METER={sample,estimate,version:1};
})();
