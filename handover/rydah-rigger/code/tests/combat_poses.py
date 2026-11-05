# Rydah Rigger G0/G1 combat poses harness (sandbox only). Builds nothing; loads a COPY page (default rigger_combat_test.html built by
# build_copy.sh /tmp/rigger_combat.html). Drives the poser manually at dt=1/72 (game's own drive call is muted for the player), per rider:
# G0 static key/limit audit, flag-off no-op, light1/light2/finisher/react_light/react_heavy/knockdown (+heavy provisional), chain, hit-stop.
# Usage: python3 tests/combat_poses.py [riders=caali,anika] ; env RYDAH_PAGE, SHOTS=0 to skip the pose sheets.
import os,sys,time,json
from playwright.sync_api import sync_playwright
BASE=os.environ.get("RYDAH_BASE","http://localhost:8765")+"/v3build/"+os.environ.get("RYDAH_PAGE","rigger_combat_test.html")
RIDERS=(sys.argv[1] if len(sys.argv)>1 else "caali,anika").split(","); SHOTS=os.environ.get("SHOTS","1")!="0"; OUT="/workspace/shots/combat/"
ok=[]
def check(n,c,i=""): ok.append(bool(c)); print(("PASS " if c else "FAIL ")+n,i,flush=True)
def waitfor(pg,e,t=150):
    t0=time.time()
    while time.time()-t0<t:
        try:
            if pg.evaluate(e): return True
        except Exception: pass
        time.sleep(.3)
    return False
JS=r"""(()=>{ const u=RIDERS.player.userData; if(!u.__drive){ u.__drive=u.drive; u.drive=function(){}; } window.__rcT=window.__rcT||0;
 const B={}; RIDERS.player.traverse(o=>{ if(o.isBone) B[o.name.replace(/^mixamorig:?/,'')]=o; });
 const LIM=RIDER_JOINT_LIMITS, R2D=180/Math.PI;
 const lim=n=>LIM[n.replace(/^(Left|Right)/,'')];
 const step=(n,sp)=>{ for(let i=0;i<n;i++){ __rcT+=1/72; u.__drive.call(u,1/72,sp||0,false,__rcT,0); } };
 const footY=()=>{ const C=u.atContact, gy=RIDERS.player.parent.matrixWorld.elements[13], sc=new THREE.Vector3().setFromMatrixScale(RIDERS.player.matrixWorld).y, v=new THREE.Vector3(); RIDERS.player.updateMatrixWorld(true);
   if(!C||!C.length) return [B.LeftFoot.getWorldPosition(v).y,B.RightFoot.getWorldPosition(v).y]; const o=[Infinity,Infinity];
   for(const c of C){ v.copy(c.q).applyMatrix4(c.b.matrixWorld); const i=/Left/.test(c.b.name)?0:1; o[i]=Math.min(o[i],v.y-c.r*sc-gy); } return o; };
 const EXT=['Spine','Spine1','Spine2','Neck','Head','LeftShoulder','RightShoulder','LeftArm','RightArm','LeftUpLeg','RightUpLeg','LeftLeg','RightLeg'];
 const snapQ=()=>{ const o={}; for(const n of EXT) if(B[n]) o[n]=B[n].quaternion.clone(); return o; };
 const limViol=()=>{ const v=[]; const D=u.poseDbg; for(const n in D){ if(/Hand(Thumb|Index|Middle|Ring|Pinky)/.test(n)) continue; const L=lim(n); if(!L) continue; const m=n.startsWith('Right');
   ['x','y','z'].forEach((ax,j)=>{ const r=L[ax]; if(!r) return; const lo=(m&&ax!=='x')?-r[1]:r[0], hi=(m&&ax!=='x')?-r[0]:r[1], val=D[n][j]; if(!(val>=lo-.01&&val<=hi+.01)) v.push(n+'.'+ax+'='+val.toFixed(1)); }); } return v; };
 // G0 static: authored keys x every combat-feel row, sampled at each key frame, strictly inside limits (pre soft-clamp); spine twist total <= 40
 window.__rcStatic=()=>{ const bad=[]; for(const mk in RIDER_COMBAT_MOVES){ const m=RIDER_COMBAT_MOVES[mk]; for(const fk in RIDER_COMBAT_FEEL){ const cf=riderCombatFeel(fk), TL=riderCombatTimeline(m,cf);
     for(const [f] of TL.keys){ const o=riderCombatSample(m,TL,f,'Left',cf,1), o2=riderCombatSample(m,TL,f,'Right',cf,-1);
       for(const S of [o,o2]){ for(const n in S){ const L=lim(n); if(!L){ bad.push(mk+':'+n+' no limit'); continue; } const mr=n.startsWith('Right'); ['x','y','z'].forEach((ax,j)=>{ const r0=L[ax], r=r0&&(mr&&ax!=='x')?[-r0[1],-r0[0]]:r0; if(r&&(S[n][j]<r[0]-1e-6||S[n][j]>r[1]+1e-6)) bad.push(mk+'/'+fk+'@'+f+' '+n+'.'+ax+'='+S[n][j].toFixed(1)); }); }
         const tw=Math.abs((S.Spine||[0,0])[1]+(S.Spine1||[0,0])[1]+(S.Spine2||[0,0])[1]); if(tw>LIM.spineTwistTotal+1e-6) bad.push(mk+'/'+fk+' twist '+tw.toFixed(1)); } }
     if(m.hit.some(h=>h<m.A||h>=m.A+m.X)) bad.push(mk+' hit outside X'); } }
   return {bad:bad.slice(0,12),n:bad.length,moves:Object.keys(RIDER_COMBAT_MOVES),W:['atk','react'].every(k=>k in u.weights),feel:Object.keys(RIDER_COMBAT_FEEL)}; };
 window.__rcFlagOff=()=>{ window.SR_COMBAT_POSES=false; const s0=u.stateName(), r=u.setState('atk',{step:0}), r2=u.setState('react',{kind:'light'}); step(3); const out={ret:[r,r2],state:[s0,u.stateName()],w:[u.weights.atk,u.weights.react],q:u.combatQuery()}; window.SR_COMBAT_POSES=true; return out; };
 // run one move from idle; per-frame audit
 window.__rcRun=(n,o,opts)=>{ opts=opts||{}; window.SR_COMBAT_POSES=true; if(u.combatQuery()) u.combatCancel(); step(opts.settle||100,opts.sp||0); const f0=footY(), dc0=window.__DC0?__DC0():-1, ch0=scene.children.length;
   const ev=[], unsub=['onHitFrame','onCancelOpen','onCancelClose','onRecover'].map(t=>u.onCombat(t,e=>ev.push({t,f:e.frame,s:k,hit:e.hitIndex,pos:!!e.pos,int:e.interrupted,kinds:e.kinds})));
   u.combatEvents.onHitFrame=null; let k=0; const ok0=u.setState(n,o); const q0=u.combatQuery(); const R={ok:ok0,q0,lim:[],nan:0,slewOver:[],feet:0,feetN:0,maxBase:0,maxLead:0,phases:{},w:[],dc:[],state:u.stateName(),side:q0&&q0.side,hsFrozen:null};
   u._combatSlew.max=0;u._combatSlew.maxLead=0;u._combatSlew.over=0; let prev=snapQ(); const end=q0?q0.frames.end:0, plant=q0&&q0.plant, sSide=q0&&(q0.side==='Left'?1:0);
   let hsAt=-1, hsF=[];
   while(k<end+12){ k++; step(1,opts.sp||0); const q=u.combatQuery();
     if(opts.hitstop&&ev.some(e=>e.t==='onHitFrame')&&hsAt<0){ hsAt=k; u.combatHitStop(opts.hitstop); }
     if(hsAt>0&&k<=hsAt+8&&q) hsF.push(q.frame);
     if(q){ R.phases[q.phase]=(R.phases[q.phase]||0)+1; R.w.push(+q.weight.toFixed(2)); }
     const lv=limViol(); if(lv.length) R.lim.push(k+':'+lv.slice(0,3).join(','));
     RIDERS.player.traverse(b=>{ if(b.isBone&&!(isFinite(b.quaternion.x)&&isFinite(b.quaternion.w)&&isFinite(b.position.y))) R.nan++; });
     const cur=snapQ(), inX=q&&q.phase==='X', LD=q&&RIDER_COMBAT_MOVES[q.move].lead, lead=LD==='KArm'?[q.side+'Shoulder',q.side+'Arm']:LD==='BArm'?['LeftShoulder','LeftArm','RightShoulder','RightArm']:LD==='KLeg'?[q.side+'UpLeg',q.side+'Leg']:[];
     for(const b in cur){ const d=2*Math.acos(Math.min(1,Math.abs(cur[b].dot(prev[b]))))*R2D*72, isL=inX&&lead.includes(b), cap=isL?RIDER_POSE_ACTIVE_DEG_S:720; if(isL) R.maxLead=Math.max(R.maxLead,d); else R.maxBase=Math.max(R.maxBase,d); if(d>cap*1.01+1) R.slewOver.push(k+':'+b+'='+d.toFixed(0)); }
     prev=cur;
     if(q&&plant&&plant!=='off'){ const fy=footY(); const strike=q.phase!=='R'||q.frame<q.frames.a+q.frames.x+3; const idx=plant==='both'?[0,1]:[q.side==='Left'?1:0];
       if(strike&&plant==='any'){ const lo=Math.min(fy[0],fy[1]), hi=Math.max(Math.abs(fy[0]-f0[0]),Math.abs(fy[1]-f0[1])); R.feet=Math.max(R.feet,Math.abs(lo-Math.min(f0[0],f0[1]))*1000,Math.max(0,hi*1000-7)); R.feetN++; }
       else if(strike) for(const i of idx){ R.feet=Math.max(R.feet,Math.abs(fy[i]-f0[i])*1000); R.feetN++; }
       R.ground=Math.max(R.ground||0,Math.abs(Math.min(fy[0],fy[1])-Math.min(f0[0],f0[1]))*1000); }   // planted foot +-3 mm through A..X+2; any foot on the deck through recovery
     if(q&&q.frames.hit.includes(q.frame)&&window.__DC0) R.dc.push(__DC0()); }
   unsub.forEach(f=>f()); R.ev=ev; R.end=end; R.dc0=dc0; R.ch=[ch0,scene.children.length]; R.int=u._combatSlew; R.hs=hsF; R.hsAt=hsAt; R.lim=R.lim.slice(0,5); R.slewOver=R.slewOver.slice(0,5); return R; };
 window.__rcPose=(n,o,frame)=>{ window.SR_COMBAT_POSES=true; if(u.combatQuery()) u.combatCancel(); step(100,0); u.setState(n,o); let k=0; while(k<frame){ step(1,0); k++; } return u.combatQuery(); };
 window.__rcChain=()=>{ window.SR_COMBAT_POSES=true; if(u.combatQuery()) u.combatCancel(); step(100,0); const log=[]; u.setState('atk',{step:0}); let k=0, st=0, wmin=1, sides=[];
   sides.push(u.combatQuery().side); const un=u.onCombat('onCancelOpen',e=>{ if(st<2){ st++; u.setState('atk',{step:st}); sides.push(u.combatQuery().side); log.push(['chain',st,e.frame]); } });
   const un2=u.onCombat('onRecover',e=>log.push(['rec',e.move,e.frame,!!e.interrupted]));
   let prev=snapQ(), over=0; while(k<120&&u.combatQuery()){ k++; step(1,0); const q=u.combatQuery(); if(q&&k>8&&(q.phase==='A'||q.phase==='X')) wmin=Math.min(wmin,q.weight); const cur=snapQ(); for(const b in cur){ const d=2*Math.acos(Math.min(1,Math.abs(cur[b].dot(prev[b]))))*R2D*72; if(d>RIDER_POSE_ACTIVE_DEG_S*1.01+1||(d>720*1.01+1&&!/Arm|Shoulder/.test(b))) over++; } prev=cur; }
   un(); un2(); return {log,sides,wmin,over,frames:k}; };
 return Object.keys(u).filter(k=>/combat/.test(k)); })()"""

CREWJS=r"""(()=>{ const out=[]; window.SR_COMBAT_POSES=false; const R2D=180/Math.PI;
 // G0 static: crew additive table (rad -> deg) inside RIDER_JOINT_LIMITS via the 19->Mixamo map (approximate: crew rig axes follow rPose conventions)
 const MAP={spine:'Spine',chest:'Spine1',head:'Head',upperarmL:'Arm',upperarmR:'Arm',forearmL:'ForeArm',forearmR:'ForeArm',thighL:'UpLeg',thighR:'UpLeg',shinL:'Leg',shinR:'Leg'}, bad=[];
 for(const k in SR_CREW_REACT) for(const [f,v] of SR_CREW_REACT[k].keys) for(const n in v){ const L=RIDER_JOINT_LIMITS[MAP[n]]; ['x','y','z'].forEach((ax,j)=>{ const d=v[n][j]*R2D, r=L&&L[ax]; if(r&&(d<r[0]-1e-6||d>r[1]+1e-6)&&!(n.endsWith('R')&&ax!=='x'&&-d>=r[0]&&-d<=r[1])) bad.push(k+'@'+f+' '+n+'.'+ax+'='+d.toFixed(0)); }); }
 return bad; })()"""

FXJS=r"""(R)=>{ const U=R.userData, H=R.parent, out={names:Object.keys(U.fx||{}).sort(), par:{}, y:{}, fwd:{}, draws:0};
  R.updateMatrixWorld(true); const loc=v=>H.worldToLocal(v.clone()), fq=new THREE.Quaternion();
  for(const n in (U.fx||{})){ const o=U.fx[n]; out.par[n]=o.parent&&o.parent.name; if(o.isMesh||o.children.length) out.draws++; if(o.name!=='srFX_'+n) out.draws+=100; }
  for(const s of ['L','R']){ const w=U.fx&&U.fx['wheel'+s], f=U.fx&&U.fx['foot'+s]; if(!w||!f) continue; const pw=loc(w.getWorldPosition(new THREE.Vector3())), pf=loc(f.getWorldPosition(new THREE.Vector3()));
    out.y[s]=+(pw.y*1000).toFixed(1); const fz=new THREE.Vector3(0,0,1).applyQuaternion(R.getWorldQuaternion(fq)).applyQuaternion(H.getWorldQuaternion(new THREE.Quaternion()).invert()); out.fwd[s]=+(pw.clone().sub(pf).dot(fz)*1000).toFixed(0); out['d'+s]=+(pw.distanceTo(pf)*1000).toFixed(0); }
  out.sc=U.atSkateFit||null; return out; }"""
def fx_check(pg,label,expr):
    F=pg.evaluate("(()=>{ const R="+expr+"; return ("+FXJS+")(R); })()")
    ok_=F["names"]==sorted(["handL","handR","footL","footR","wheelL","wheelR"]) and F["draws"]==0 and all(abs(F["y"].get(s,99))<=40 for s in "LR") and all(F["fwd"].get(s,-1)>20 for s in "LR")
    check(label+": srFX_* attach points exist (6), empty Object3Ds, wheel points at deck height (+-40 mm) and forward of the foot (front wheel, scaled skate)",ok_,json.dumps(F))
    return F
def crew_tests(pg,rider):
    bad=pg.evaluate(CREWJS); check(rider+": crew G0 additive react table inside RIDER_JOINT_LIMITS (19-bone -> Mixamo map)",not bad,json.dumps(bad[:6]))
    pg.evaluate("""window.__crewSel=RIDERS.npcs.filter(n=>n.r&&n.r.userData&&!n.r.userData.ikki&&n.r.userData.bones).slice(0,3); window.__rpOrig=window.__rpOrig||rPose;
      rPose=function(R){ if(R.userData.__testOwn&&!window.__crewTestCall) return; return __rpOrig.apply(this,arguments); };
      window.__crewPose=(n)=>{ window.__crewTestCall=true; try{ rPose(n.r,0,0,.05,.02,0,clock); } finally{ window.__crewTestCall=false; } };
      window.__crewAt=(n,d)=>{ n.holder.position.set(-6,0,40-d); n.holder.rotation.y=0; n.holder.visible=true; n.r.visible=true; n.holder.updateMatrixWorld(true); };
      window.__camHook=()=>{ camera.position.set(-6,1.6,43); camera.lookAt(-6,1.0,30); };0""")
    names=pg.evaluate("__crewSel.map((n,i)=>(n.g&&(n.g.crew||n.g.name))||('npc'+i))"); check(rider+": 3 crew NPCs available",len(names)==3,json.dumps(names))
    pg.evaluate("__crewSel.forEach(n=>srCrewCombatInstall(n.r))")
    for i,cn in enumerate(names): fx_check(pg,f"{rider}/crew {cn}",f"__crewSel[{i}].r")
    for i,cn in enumerate(names):
        R=pg.evaluate("""(i)=>{ const n=__crewSel[i], U=n.r.userData; U.__testOwn=true; __crewAt(n,6); __camHook(); camera.updateMatrixWorld(true); window.__crewCombatManual=true; srCrewCombatInstall(n.r); const C=U.crCombat; C.mdt=1/72;
          const api=['setState','combatHitStop','combatQuery','combatState','onCombat'].every(k=>typeof U[k]==='function');
          window.SR_COMBAT_POSES=false; const offRet=U.setState('react',{kind:'light'}); window.SR_COMBAT_POSES=true;
          camera.updateMatrixWorld(true); for(let k=0;k<20;k++) __crewPose(n);
          const fy=()=>{ const v=new THREE.Vector3(); return Math.min(n.holder.worldToLocal(U.bones.footL.getWorldPosition(v)).y, n.holder.worldToLocal(U.bones.footR.getWorldPosition(new THREE.Vector3())).y); };
          const base=fy(), dc0=__DC0(), ch0=scene.children.length, res={api,offRet};
          for(const kind of ['light','knockdown']){ const ev=[]; const un=U.onCombat('onRecover',e=>ev.push([e.move,e.frame,e.interrupted,k])); let k=0; C.slewMax=0;
            const ok=U.setState('react',{kind,dir:new THREE.Vector3(0,0,1)}); const q0=U.combatQuery(); let feet=0,nan=0,lods=new Set(),dc=[];
            while(k<(q0?q0.frames.end:0)+6){ k++; U.combatStep(1/72); __crewPose(n); const q=U.combatQuery(); if(q) lods.add(q.lod); feet=Math.max(feet,Math.abs(fy()-base)*1000);
              n.r.traverse(b=>{ if(b.isBone&&!(isFinite(b.quaternion.x)&&isFinite(b.quaternion.w))) nan++; }); if(k===8) dc.push(__DC0()); }
            un(); res[kind]={ok,frames:q0&&q0.frames,ev,feet:+feet.toFixed(2),nan,slew:+C.slewMax.toFixed(0),lods:[...lods],dc}; }
          // hit-stop: freezes the clock
          U.setState('react',{kind:'light'}); for(let k=0;k<2;k++){ U.combatStep(1/72); __crewPose(n); } U.combatHitStop(70); const hs=[]; for(let k=0;k<6;k++){ U.combatStep(1/72); __crewPose(n); hs.push(U.combatQuery().frame); } res.hs=hs;
          // LOD: 20 m -> keys, 40 m -> off (no overlay: pose identical to plain rPose)
          for(let k=0;k<20;k++){ U.combatStep(1/72); __crewPose(n); }
          U.setState('react',{kind:'knockdown'}); __crewAt(n,20); for(let k=0;k<10;k++){ U.combatStep(1/72); __crewPose(n); } res.lod20=U.combatQuery().lod;
          __crewAt(n,40); U.combatStep(1/72); __crewPose(n); const qOff=U.bones.spine.quaternion.clone(); res.lod40=U.combatQuery().lod; window.SR_COMBAT_POSES=false; const st=U.crCombat.S; U.crCombat.S=null; U.crCombat.tail=0; __crewPose(n); res.offSame=qOff.angleTo(U.bones.spine.quaternion)<1e-4; U.crCombat.S=st; window.SR_COMBAT_POSES=true;
          for(let k=0;k<80;k++) U.combatStep(1/72); __crewPose(n); res.dc1=__DC0(); res.dc0=dc0; res.ch=[ch0,scene.children.length]; U.__testOwn=false; window.__crewCombatManual=false; return res; }""",i)
        L,K=R["light"],R["knockdown"]
        check(f"{rider}/crew {cn}: API present, flag off -> no-op",R["api"] and R["offRet"] is False,json.dumps([R['api'],R['offRet']]))
        for nm,X in (("react_light",L),("knockdown",K)):
            evok=X["ok"] and len(X["ev"])==1 and X["ev"][0][1]==X["frames"]["end"] and not X["ev"][0][2]
            check(f"{rider}/crew {cn} {nm}: onRecover once on end frame, NaN 0, slew <=720, feet +-3 mm (srCrewPlant), LOD full, draws unchanged",
                  evok and X["nan"]==0 and X["slew"]<=727 and X["feet"]<=3.0 and X["lods"]==["full"] and all(d==R["dc0"] for d in X["dc"]),json.dumps(X))
        check(f"{rider}/crew {cn}: hit-stop freezes clock; LOD 20 m keys, 40 m off (pose == plain rPose); scene unchanged",
              len(set(R["hs"][:4]))==1 and R["lod20"]=="keys" and R["lod40"]=="off" and R["offSame"] and R["ch"][0]==R["ch"][1] and R["dc1"]==R["dc0"],json.dumps({k:R[k] for k in ("hs","lod20","lod40","offSame","ch","dc0","dc1")}))
    pg.evaluate("rPose=__rpOrig; window.__camHook=null")
def run(rider):
    with sync_playwright() as p:
        b=p.chromium.launch(args=["--use-gl=angle","--use-angle=swiftshader","--enable-unsafe-swiftshader"])
        pg=b.new_page(viewport={"width":720,"height":900}); errs=[]; pg.on("pageerror",lambda e: errs.append(str(e)[:200]))
        pg.goto(BASE+"?chars=/skyrydahs-characters/&player="+rider,timeout=180000)
        check(rider+": page ready",waitfor(pg,"typeof RIDERS!='undefined'&&RIDERS.ready&&RIDERS.player&&RIDERS.player.userData.ikki",240))
        for _ in range(8):
            if pg.evaluate("State.mode==='ride'"): break
            pg.keyboard.press("Enter"); time.sleep(2)
        pg.evaluate("window.__hideIkkiNpc=true; Ride.group.position.set(-6,0,40); Ride.yaw=Math.PI; Ride.speed=0;")
        pg.evaluate("window.__DC0=()=>{const a=renderer.info.autoReset;renderer.info.autoReset=false;renderer.info.reset();renderer.render(scene,camera);const c=renderer.info.render.calls;renderer.info.autoReset=a;return c};")
        api=pg.evaluate(JS); key=pg.evaluate("RIDERS.player.userData.riderId"); print(rider,"riderId",key,"api",api,"feel",json.dumps(pg.evaluate("RIDERS.player.userData.combatFeel")),flush=True)
        # flag default OFF in this page (no ?combatposes) -> the game is unchanged until Systems flips it
        check(rider+": flag default off",pg.evaluate("!window.SR_COMBAT_POSES&&!/combatposes=1/.test(location.search)&&RIDERS.player.userData.combatOn()===false"))
        S=pg.evaluate("__rcStatic()"); check(rider+": G0 authored keys x feel rows inside RIDER_JOINT_LIMITS, twist<=40, hits inside X, W has atk/react",S["n"]==0 and S["W"],json.dumps(S))
        F=pg.evaluate("__rcFlagOff()"); check(rider+": flag off -> setState atk/react no-op",F["ret"]==[False,False] and F["w"]==[0,0] and F["q"] is None and F["state"][0]==F["state"][1],json.dumps(F))
        fx_check(pg,rider+" poser","RIDERS.player")
        FF=pg.evaluate("""(()=>{ const u=RIDERS.player.userData; const d=n=>u.fx[n].getWorldPosition(new THREE.Vector3()).distanceTo(u.fx[n].parent.getWorldPosition(new THREE.Vector3())); const a0=u.fxPos('handL'), d0=d('handL'), w0=d('wheelL');
          let ev=null; const un=u.onCombat('onHitFrame',e=>{ ev={fxName:e.fxName,pos:e.pos&&e.pos.toArray(),fx:Object.keys(e.fx||{}).sort()}; }); const r=__rcRun('atk',{step:0}); un(); u.setState('atk',{step:0}); const q=u.combatQuery(); u.combatCancel();
          return {moved:+(a0.distanceTo(u.fxPos('handL'))*1000).toFixed(0), rigid:+(Math.abs(d('handL')-d0)+Math.abs(d('wheelL')-w0)).toFixed(5), ev, q:Object.keys((q&&q.fx)||{}).sort()}; })()""")
        six=sorted(["handL","handR","footL","footR","wheelL","wheelR"])
        check(rider+": srFX points follow their bones (rigid offset), onHitFrame carries fxName/pos/fx, combatQuery.fx has all 6",FF["rigid"]<1e-4 and FF["ev"] and FF["ev"]["fxName"] in ("handL","handR") and FF["ev"]["pos"] and FF["ev"]["fx"]==six and FF["q"]==six,json.dumps(FF))
        # (local-only persona cases removed for the public handover)
        cases=[("light1",{"step":0}),("light2",{"step":1}),("finisher",{"step":2}),("heavy",{"move":"heavy","charge":False}),("react_light",{"kind":"light"}),("react_heavy",{"kind":"heavy"}),("knockdown",{"kind":"knockdown"})]
        res={}
        for name,o in cases:
            kind="react" if name.startswith("react") or name=="knockdown" else "atk"
            R=pg.evaluate("([n,o])=>__rcRun(n,o)",[kind,o]); res[name]=R; q=R["q0"] or {}
            F_=q.get("frames",{}); hits=[e for e in R["ev"] if e["t"]=="onHitFrame"]; rec=[e for e in R["ev"] if e["t"]=="onRecover"]
            co=[e for e in R["ev"] if e["t"]=="onCancelOpen"]; cc=[e for e in R["ev"] if e["t"]=="onCancelClose"]
            evok=(q.get("move")==name and [e["f"] for e in hits]==F_.get("hit") and all(abs(e["s"]-e["f"])<=1 for e in R["ev"]) and all(e["pos"] for e in hits)
                  and len(rec)==1 and rec[0]["f"]==F_.get("end") and ((F_.get("cancel") is None and not co) or (F_.get("cancel") and [e["f"] for e in co]==[F_["cancel"][0]] and [e["f"] for e in cc]==[F_["cancel"][1]])))
            info=json.dumps({"frames":F_,"ev":[(e["t"][2:],e["f"],e["s"]) for e in R["ev"]],"side":R["side"]})
            check(f"{rider}/{name}: events on authored frames (+-1), hitFrame pos, one recover",evok,info)
            check(f"{rider}/{name}: joint-limit violations 0, NaN 0",not R["lim"] and R["nan"]==0,json.dumps([R["lim"],R["nan"]]))
            check(f"{rider}/{name}: slew <=720 deg/s (base) / <=1800 lead limb in X only",not R["slewOver"] and R["int"]["over"]==0,json.dumps({"maxBase":round(R["maxBase"]),"maxLead":round(R["maxLead"]),"int":R["int"],"over":R["slewOver"]}))
            if q.get("plant")!="off": check(f"{rider}/{name}: planted foot within +-3 mm ({q.get('plant')}, strike frames) + a skate on the deck through recovery",R["feet"]<=3.0 and R["feetN"]>0 and R.get("ground",0)<=3.0,f"strike max {R['feet']:.2f} mm over {R['feetN']} samples; recovery lowest-foot max {R.get('ground',0):.2f} mm")
            check(f"{rider}/{name}: draws unchanged, scene children unchanged",all(d==R["dc0"] for d in R["dc"]) and R["ch"][0]==R["ch"][1],json.dumps([R["dc0"],R["dc"],R["ch"]]))
        SP=pg.evaluate("Object.keys(RIDER_COMBAT_MOVES).filter(k=>RIDER_COMBAT_MOVES[k].crew)")
        spfail=[]
        for mv in SP:
            st,ky=mv.rsplit("_",1); R=pg.evaluate("([n,o])=>__rcRun(n,o)",["atk",{"set":st,"key":ky}]); q=R["q0"] or {}; F_=q.get("frames",{})
            hits=[e for e in R["ev"] if e["t"]=="onHitFrame"]; rec=[e for e in R["ev"] if e["t"]=="onRecover"]
            ok_=(q.get("move")==mv and [e["f"] for e in hits]==F_.get("hit") and all(abs(e["s"]-e["f"])<=1 for e in R["ev"]) and len(rec)==1 and rec[0]["f"]==F_.get("end")
                 and not R["lim"] and R["nan"]==0 and not R["slewOver"] and R["int"]["over"]==0 and (q.get("plant")=="off" or (R["feet"]<=3.0 and R.get("ground",0)<=3.0)) and all(d==R["dc0"] for d in R["dc"]))
            if not ok_: spfail.append([mv,F_,[(e["t"][2:],e["f"],e["s"]) for e in R["ev"]],R["lim"][:2],R["slewOver"][:2],round(R["feet"],1),round(R.get("ground",0),1)])
        if SP: check(f"{rider}: {len(SP)} crew K/L specials (set_K/set_L): events on frames, limits 0, NaN 0, slew caps, planted feet +-3 mm, draws unchanged",len(SP)==16 and not spfail,json.dumps(spfail)[:900])
        if rider==RIDERS[0]: crew_tests(pg,rider)
        # light2 side flips vs light1 when chained; full chain via onCancelOpen
        C=pg.evaluate("__rcChain()"); check(rider+": chain light1->light2->finisher on cancelOpen, side flips, weight stays up, caps held",
            [l[1] for l in C["log"] if l[0]=="chain"]==[1,2] and C["sides"][0]!=C["sides"][1] and C["wmin"]>.9 and C["over"]==0,json.dumps(C))
        # hit-stop freezes the move clock: 83 ms ~ 6 frames at 72 fps; recover shifts by the same
        H=pg.evaluate("([n,o,x])=>__rcRun(n,o,x)",["atk",{"step":2},{"hitstop":83}]); rec=[e for e in H["ev"] if e["t"]=="onRecover"]
        fr=H["hs"]; frozen=len(fr)>=6 and len(set(fr[:5]))==1
        check(rider+": hit-stop 83 ms freezes move clock (pose does not advance), recover delayed ~6 f",frozen and rec and rec[0]["s"]-rec[0]["f"] in (5,6,7),json.dumps({"hs":fr,"rec":[(e["f"],e["s"]) for e in rec]}))
        check(rider+": no page errors",not errs,json.dumps(errs[:3]))
        if SHOTS:
            pg.evaluate("window.__camHook=()=>{const p=Ride.group.position; Ride.group.position.set(-6,0,40); const y=Ride.yaw+(window.__camA??.9); camera.position.set(p.x+Math.sin(y)*(window.__camD??3.0),1.15,p.z+Math.cos(y)*(window.__camD??3.0)); camera.lookAt(p.x,.85,p.z);}")
            poses=[("light1_coil","atk",{"step":0},"a"),("light1_hit","atk",{"step":0},"hit"),("light2_hit","atk",{"step":1},"hit"),("finisher_coil","atk",{"step":2},"a"),("finisher_hit","atk",{"step":2},"hit"),
                   ("heavy_chamber","atk",{"move":"heavy","charge":False},"a"),("heavy_hit","atk",{"move":"heavy","charge":False},"hit"),("react_light","react",{"kind":"light"},3),("react_heavy","react",{"kind":"heavy"},8),("knockdown","react",{"kind":"knockdown"},20)]
            for lab,k,o,fr in poses:
                q=pg.evaluate("([k,o])=>{ const u=RIDERS.player.userData; u.setState(k,o); const q=u.combatQuery(); u.combatCancel(); return q; }",[k,o])
                f=q["frames"]["a"] if fr=="a" else q["frames"]["hit"][0] if fr=="hit" else fr
                for ang in (.6,1.57):
                    pg.evaluate(f"window.__camA={ang}"); pg.evaluate("([k,o,f])=>__rcPose(k,o,f)",[k,o,f]); time.sleep(1.6)
                    for _try in range(3):
                        try: pg.screenshot(path=f"{OUT}{rider}_{lab}_{'front34' if ang<1 else 'side'}.png",timeout=90000); break
                        except Exception as e: print("shot retry",lab,str(e)[:80],flush=True); time.sleep(3)
            pg.evaluate("window.__camHook=null")
        b.close()
for r in RIDERS: run(r)
print(f"RESULT {sum(ok)} / {len(ok)}",flush=True)
