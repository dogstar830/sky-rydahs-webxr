// ===== TICKGUARD late install (Rydah Systems, patch_tickguard.py) — needs SR_GUARD from tickguard.js (head) =====
(function(){ const G=window.SR_GUARD; if(!G||window.SR_TICKGUARD) return; const TG=window.SR_TICKGUARD={wrapped:[],passes:0,loop:false};
  // per-frame systems called from animate(): disabled on throw. KEEP = core input/movement: keep calling (logged once) so the game stays playable.
  const SYS=["gatesPre","wallAtkPre","wallAtkPost","grindStep","updateRiders","districtMood","turfUpdate","dashUpdate","updateSpeedLines","drawMinimap","turfMinimap","cullDetails","cullFar","heatTick","perfTick","grafTickCore","grafTick","turfFlush","minimapTick","phoneTick","kitTick","crewhouseTick","rideGroundTick","targetTick","padTick"];
  const KEEP=["poll","wallStep","updateRide","updateParticles","menuInput","drawMenu"];
  function swap(n,keep){ try{ const f=(0,eval)("typeof "+n+"==='function'?"+n+":null"); if(!f||f.__srg) return; const g=G(n,f,{keep}); (0,eval)(n+"=window.__srTmp"); }catch(e){} }
  function pass(){ TG.passes++;
    for(const n of SYS){ window.__srTmp=null; try{ const f=(0,eval)("typeof "+n+"==='function'?"+n+":null"); if(f&&!f.__srg){ window.__srTmp=G(n,f); (0,eval)(n+"=window.__srTmp"); TG.wrapped.push(n); } }catch(e){} }
    for(const n of KEEP){ window.__srTmp=null; try{ const f=(0,eval)("typeof "+n+"==='function'?"+n+":null"); if(f&&!f.__srg){ window.__srTmp=G(n,f,{keep:true}); (0,eval)(n+"=window.__srTmp"); TG.wrapped.push(n+"*"); } }catch(e){} }
    try{ if(window.SR_PAD&&typeof SR_PAD.update==="function"&&!SR_PAD.update.__srg){ SR_PAD.update=G("SR_PAD.update",SR_PAD.update.bind(SR_PAD),{keep:true}); TG.wrapped.push("SR_PAD.update*"); } }catch(e){}
    try{ const A=(0,eval)("typeof animated!=='undefined'?animated:null"); if(A&&Array.isArray(A)){
      const nm=(f,i)=>"animated:"+(f.name||("#"+i))+(f.__srSrc?"("+f.__srSrc+")":"");
      for(let i=0;i<A.length;i++) if(typeof A[i]==="function"&&!A[i].__srg) A[i]=G(nm(A[i],i),A[i]);
      if(!A.__srPush){ const P=A.push; A.push=function(...fs){ return P.apply(A,fs.map((f,k)=>typeof f==="function"&&!f.__srg?G(nm(f,A.length+k),f):f)); }; A.__srPush=true; TG.wrapped.push("animated[]"); } } }catch(e){}
    delete window.__srTmp; }
  // last-resort frame guard: wrap whatever callback is handed to setAnimationLoop (now and later, incl. XR re-sets)
  function guardLoop(){ const R=(0,eval)("typeof renderer!=='undefined'?renderer:null"); if(!R||R.__srLoop) return !!R; const S=R.setAnimationLoop.bind(R);
    R.setAnimationLoop=function(cb){ if(typeof cb!=="function") return S(cb); let n=0; const w=function(t,xf){ if(n<4){ n++; pass(); } try{ return cb(t,xf); }catch(e){ window.__srRecord("frame",e,false); } }; return S(w); };
    R.__srLoop=true; TG.loop=true;
    // loop already started before this install (init finished first: minimap ctx `mm` is set right before setAnimationLoop(animate)) -> re-arm it guarded
    try{ const A=(0,eval)("typeof animate==='function'?animate:null"), mm=(0,eval)("typeof mm!=='undefined'?mm:null"); if(A&&mm&&!R.xr.isPresenting){ R.setAnimationLoop(A); TG.rearmed=true; } }catch(e){}
    return true; }
  pass(); guardLoop(); addEventListener("load",()=>{ pass(); guardLoop(); }); })();
