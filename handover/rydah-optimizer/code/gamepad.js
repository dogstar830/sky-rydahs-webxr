// ===== SR_PAD: Sky Rydahs standard Xbox gamepad module (Oliver's reference, fixed). =====
// Only pad.mapping==="standard" pads. Polled once per frame from animate() (no separate RAF).
// Radial deadzone 0.12 w/ rescale on LS (axes 0,1) and RS (axes 2,3). LT/RT analog 0..1 reported every frame (0 on release).
// WebXR Quest controllers are NOT handled here (they come via XRSession.inputSources in the game code).
// CONTROL MAP (Xbox, current bindings preserved):
//   LS ........ move / steer; menus+phone+gate keypad nav (also D-pad)     RS ..... camera orbit; LT-aim fine aim / flick target switch
//   A ......... menu select / jump & wall ride / phone select / keypad press
//   B ......... menu back / hold = power slide (crouch) / cancel grind / grind drop / phone back / close gate keypad
//   X ......... context action: pick up can, open gate (hold 0.5s = hack), hold at turf spot = tag
//   Y ......... trick (air spin / shove-it); RT+Y = crew ultimate      LB ..... L special   D-LEFT grapple   LT lock-on only
//   RB ........ melee: tap = light, hold >=0.35s + release = heavy      RT ..... special attack (analog value exposed)
//   LT ........ aim / targeting mode (analog, >0.3)                    L3 ..... boost (press = dash); grind kick
//   R3 ........ crew move                                              MENU ... start / pause
//   VIEW ...... open map                                               D-pad .. Up phone, Down ping, Left grapple (ride), L/R nav in UI
//   XBOX ...... unbound (browser/OS usually reserve it)
// Keyboard remains as fallback (WASD/arrows, Shift boost, T/F tag, Enter/Space select, Esc start/back, J/K/L attacks, G grapple, C drop).
(function(){
  const BUTTONS={A:0,B:1,X:2,Y:3,LB:4,RB:5,LT:6,RT:7,VIEW:8,MENU:9,L3:10,R3:11,DPAD_UP:12,DPAD_DOWN:13,DPAD_LEFT:14,DPAD_RIGHT:15,XBOX:16};
  const DEADZONE=0.12, TRIGGER_PRESS=0.3, N=17;
  const prevButtons=new Map(); // pad.index -> bool[]
  const S={ BUTTONS, DEADZONE, TRIGGER_PRESS, pad:null, connected:false, mute:0, frame:0,
    cur:new Array(N).fill(false), down:new Array(N).fill(false), up:new Array(N).fill(false),
    left:{x:0,y:0}, right:{x:0,y:0}, lt:0, rt:0,
    onButtonDown:null, onButtonUp:null, onTrigger:null, onConnect:null, onDisconnect:null };
  const idx=b=>typeof b==="number"?b:BUTTONS[b];
  function applyDeadzone(x,y){ const m=Math.hypot(x,y); if(m<DEADZONE) return {x:0,y:0}; const s=Math.min(1,(m-DEADZONE)/(1-DEADZONE))/m; return {x:x*s,y:y*s}; }
  function pads(){ try{ return navigator.getGamepads?[...navigator.getGamepads()].filter(p=>p&&p.connected!==false&&p.mapping==="standard"):[]; }catch(e){ return []; } }
  function isDown(p,i){ const b=p.buttons[i]; if(!b) return false; return !!b.pressed||((i===6||i===7)&&(b.value||0)>TRIGGER_PRESS); }
  function update(){ S.frame++; const list=pads(), p=list[0]||null; S.pad=p; S.connected=!!p;
    S.down.fill(false); S.up.fill(false);
    for(const q of list){ const prev=prevButtons.get(q.index)||new Array(N).fill(false), now=new Array(N);
      for(let i=0;i<N;i++){ now[i]=isDown(q,i); if(now[i]&&!prev[i]){ if(q===p) S.down[i]=true; S.onButtonDown&&S.onButtonDown(i,q); } else if(!now[i]&&prev[i]){ if(q===p) S.up[i]=true; S.onButtonUp&&S.onButtonUp(i,q); } }
      prevButtons.set(q.index,now); if(q===p) S.cur=now; }
    for(const k of [...prevButtons.keys()]) if(!list.some(q=>q.index===k)) prevButtons.delete(k);
    if(!p){ S.cur=new Array(N).fill(false); S.left={x:0,y:0}; S.right={x:0,y:0}; S.lt=S.rt=0; return S; }
    const a=p.axes||[]; S.left=applyDeadzone(a[0]||0,a[1]||0); S.right=applyDeadzone(a[2]||0,a[3]||0);
    const tv=i=>{ const b=p.buttons[i]; return b?(b.value||(b.pressed?1:0)):0; }; S.lt=tv(6); S.rt=tv(7);
    S.onTrigger&&S.onTrigger(S.lt,S.rt,p); // every frame, including 0 on release
    return S; }
  // Queries (by BUTTONS name or index). While muted (legacy code paths run via padNoPad) the pad reads as absent.
  S.active=()=>S.connected&&!S.mute;
  S.pressed=b=>S.active()&&!!S.cur[idx(b)];
  S.justPressed=b=>S.active()&&!!S.down[idx(b)];
  S.justReleased=b=>S.active()&&!!S.up[idx(b)];
  S.value=b=>{ if(!S.active()) return 0; const i=idx(b), x=S.pad.buttons[i]; return x?(x.value||(x.pressed?1:0)):0; };
  S.stick=w=>{ const s=w==="right"?S.right:S.left; return S.active()?s:{x:0,y:0}; };
  S.trigger=w=>S.active()?(w==="left"?S.lt:S.rt):0;
  S.withMuted=fn=>{ S.mute++; try{ return fn(); } finally { S.mute--; } };
  S.rumble=(strong,weak,ms)=>{ let n=0; try{ for(const p of (navigator.getGamepads?[...navigator.getGamepads()]:[])) if(p&&p.vibrationActuator&&p.vibrationActuator.playEffect){ p.vibrationActuator.playEffect("dual-rumble",{duration:ms,strongMagnitude:strong,weakMagnitude:weak}); n++; } }catch(e){} return n; };
  // ---- HAPTICS: SR_PAD.haptic(evt, opts) (Rydah Optimizer, plan perf/combat-fx-budget.md §4). Never throws; no per-call allocation. ----
  // opts (optional, may be reused/shared by the caller): {hand:'left'|'right', scale:0..1}. Hand rule: 'atk' events use opts.hand else right;
  // 'both' events pulse both hands; lockOn defaults to left. Comfort: SR_PAD.hapticScale (1 full / .6 reduced / 0 off), ?haptics=full|reduced|off,
  // localStorage 'sr_haptics'; default reduced in XR, full on desktop. Rate limit: <=1 pulse per hand per 40 ms; extras merge (stronger kept, fired at window end).
  const HE=S.hapticEvents={ // [xrIntensity, xrMs, hand(0 atk,1 both,2 left), repeats, gapMs, desktopStrong, desktopWeak, desktopMs, rampFrom]
    attackStart:[.25,20,0,1,0, 0,.25,30, 0], lightHit:[.45,35,0,1,0, .2,.5,50, 0], hit3:[.6,45,0,1,0, .35,.6,60, 0],
    finisher:[.85,70,1,1,0, .7,.8,100, 0], dive:[.85,70,1,1,0, .7,.8,100, 0], stagger:[.9,50,1,2,60, .8,1,120, 0],
    pressured:[.35,25,0,1,0, 0,.4,40, 0], playerHit:[.8,90,1,1,0, 1,.6,120, 0], dodge:[.5,30,0,1,0, .3,.3,40, 0],
    lockOn:[.15,15,2,1,0, 0,.15,20, 0], roadSuper:[1,40,1,3,60, 1,1,200, .6] };
  for(const k in HE) Object.freeze(HE[k]); Object.freeze(HE);
  const H_SCALES={full:1,reduced:.6,off:0}, H_WIN=40, H_LEFT=0, H_RIGHT=1, H_PAD=2;
  const hLast=new Float64Array(3).fill(-1e9), hPendI=new Float64Array(3), hPendMs=new Float64Array(3), hPendW=new Float64Array(3), hPendT=new Int32Array(3), hTimer=[0,0,0];
  const hEff={duration:0,strongMagnitude:0,weakMagnitude:0}; let hExplicit=null;
  try{ const q=new URLSearchParams(location.search).get("haptics"); let v=q&&q.toLowerCase(); if(!(v in H_SCALES)){ v=null; try{ v=localStorage.getItem("sr_haptics"); }catch(e){} }
    if(v in H_SCALES) hExplicit=H_SCALES[v]; }catch(e){}
  function inXR(){ try{ return typeof renderer!=="undefined"&&!!renderer.xr&&!!renderer.xr.isPresenting; }catch(e){ return false; } }
  function xrSession(){ try{ return S.xrSession||(typeof renderer!=="undefined"&&renderer.xr&&renderer.xr.getSession?renderer.xr.getSession():null); }catch(e){ return null; } }
  Object.defineProperty(S,"hapticScale",{enumerable:true,get(){ return hExplicit!=null?hExplicit:(inXR()?.6:1); },set(v){ hExplicit=(v==null)?null:(typeof v==="string"?(H_SCALES[v]!=null?H_SCALES[v]:hExplicit):Math.max(0,Math.min(1,+v||0))); }});
  S.setHaptics=(mode,persist)=>{ if(!(mode in H_SCALES)) return false; hExplicit=H_SCALES[mode]; if(persist!==false) try{ localStorage.setItem("sr_haptics",mode); }catch(e){} return true; };
  S._hapticCount=0; S.hapticNow=()=>performance.now(); // tests may replace hapticNow
  function fireXR(h,i,ms){ const s=xrSession(); if(!s||!s.inputSources) return 0; const L=s.inputSources; let n=0;
    for(let k=0;k<L.length;k++){ const src=L[k], gp=src&&src.gamepad; if(!gp) continue; if((src.handedness==="left"?H_LEFT:H_RIGHT)!==h) continue;
      try{ const a=gp.hapticActuators&&gp.hapticActuators[0];
        if(a&&a.pulse){ a.pulse(i,ms); n++; }
        else if(gp.vibrationActuator&&gp.vibrationActuator.playEffect){ hEff.duration=ms; hEff.strongMagnitude=i; hEff.weakMagnitude=i; gp.vibrationActuator.playEffect("dual-rumble",hEff); n++; } }catch(e){} }
    return n; }
  function firePad(st,wk,ms){ let n=0; try{ const L=navigator.getGamepads?navigator.getGamepads():null; if(!L) return 0;
      for(let k=0;k<L.length;k++){ const p=L[k]; if(p&&p.mapping==="standard"&&p.vibrationActuator&&p.vibrationActuator.playEffect){ hEff.duration=ms; hEff.strongMagnitude=st; hEff.weakMagnitude=wk; try{ p.vibrationActuator.playEffect("dual-rumble",hEff); n++; }catch(e){} } } }catch(e){} return n; }
  function fire(h,i,ms,w){ const n=h===H_PAD?firePad(i,w,ms):fireXR(h,i,ms); if(n) S._hapticCount+=n; return n; }
  function flush(h){ hTimer[h]=0; if(!hPendT[h]) return; hPendT[h]=0; hLast[h]=S.hapticNow(); fire(h,hPendI[h],hPendMs[h],hPendW[h]); }
  const flushFns=[()=>flush(0),()=>flush(1),()=>flush(2)];
  function pulse(h,i,ms,w){ // i = XR intensity or desktop strong; w = desktop weak
    if(!(i>0)&&!(w>0)) return; const now=S.hapticNow(), dt=now-hLast[h];
    if(dt>=H_WIN&&!hPendT[h]){ hLast[h]=now; fire(h,i,ms,w); return; }
    if(!hPendT[h]||Math.max(i,w)>Math.max(hPendI[h],hPendW[h])){ hPendI[h]=i; hPendMs[h]=ms; hPendW[h]=w; } hPendT[h]=1; // merge: keep the stronger
    if(!hTimer[h]) try{ hTimer[h]=setTimeout(flushFns[h],Math.max(0,H_WIN-dt)); }catch(e){} }
  function play(e,mask,sc,r){ const ramp=e[3]>1&&e[8]>0?e[8]+(1-e[8])*r/(e[3]-1):1;
    if(inXR()||xrSession()){ const i=Math.min(1,e[0]*ramp*sc); if(mask&1) pulse(H_LEFT,i,e[1],0); if(mask&2) pulse(H_RIGHT,i,e[1],0); }
    else pulse(H_PAD,Math.min(1,e[5]*ramp*sc),e[7],Math.min(1,e[6]*ramp*sc)); }
  function rep(e,mask,sc,r){ try{ play(e,mask,sc,r); }catch(x){} }
  S.haptic=(evt,opts)=>{ try{ const e=HE[evt]; if(!e) return false; let sc=S.hapticScale; if(opts&&opts.scale!=null) sc*=+opts.scale||0; if(!(sc>0)) return false;
      const hand=opts&&opts.hand; let mask=e[2]===1?3:(hand==="left"?1:hand==="right"?2:(e[2]===2?1:2));
      play(e,mask,sc,0); for(let r=1;r<e[3];r++) setTimeout(rep,e[4]*r,e,mask,sc,r); return true; }catch(x){ return false; } };
  S._hapticReset=()=>{ hLast.fill(-1e9); hPendT.fill(0); for(let h=0;h<3;h++){ if(hTimer[h]) clearTimeout(hTimer[h]); hTimer[h]=0; } S._hapticCount=0; };
  S.update=update; S.applyDeadzone=applyDeadzone;
  addEventListener("gamepadconnected",e=>{ update(); S.onConnect&&S.onConnect(e.gamepad); });
  addEventListener("gamepaddisconnected",e=>{ prevButtons.delete(e.gamepad.index); update(); S.onDisconnect&&S.onDisconnect(e.gamepad); });
  update(); // pick up a pad that was already connected at launch
  window.SR_PAD=S; window.SR_BUTTONS=BUTTONS;
})();
