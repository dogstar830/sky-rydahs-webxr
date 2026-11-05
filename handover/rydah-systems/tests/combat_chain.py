# Combat slice C1/C2 (Rydah Systems 10:55): KH 3-hit chain on J, A/B cancel on hits 1-2, finisher, 0.6 s chain timeout,
# sim-only hit-stop (entities only, Ride/camera/clock never frozen), CombatFX.emit events, draw delta 0 outside FX. Game-time waits; RYDAH_BASE.
import os,time,json
_src=open(os.path.join(os.path.dirname(os.path.abspath(__file__)),"attacks.py")).read(); exec(_src[:_src.index("def calls")])   # shared B/HELP/load/check/waitfor
from playwright.sync_api import sync_playwright
def gw(pg,cond,g=3,cap=150):   # wait on GAME time: cond true, or g game-seconds passed
    pg.evaluate("window.__g0=clock"); t0=time.time()
    while time.time()-t0<cap:
        if pg.evaluate(f"({cond})||clock>__g0+{g}"): return pg.evaluate(f"!!({cond})")
        time.sleep(.1)
    return False
SPY="""window.__ev=[];if(window.CombatFX&&!CombatFX.__spy){const o=CombatFX.emit.bind(CombatFX);CombatFX.emit=(e,d)=>{const ms=o(e,d);__ev.push([e,ms,d&&d.crew,!!(d&&d.target),+clock.toFixed(2),d&&d.fxName||null]);window.__evObj=window.__evObj||d;window.__sameObj=(window.__sameObj??true)&&__evObj===d;return ms;};CombatFX.__spy=1;
  window.__hf=[];const fh=CombatFX.fromHitFrame&&CombatFX.fromHitFrame.bind(CombatFX); if(fh) CombatFX.fromHitFrame=(ev,e,c)=>{__hf.push([e,ev&&ev.fxName,ev&&ev.fxCharge,+clock.toFixed(2)]);return fh(ev,e,c);};
  window.__hap=[];if(window.SR_PAD&&SR_PAD.haptic){const hh=SR_PAD.haptic.bind(SR_PAD);SR_PAD.haptic=(e,o)=>{__hap.push(e);return hh(e,o);};}
  window.__fxd=0;(function f(){ if(CombatFX.stats) __fxd=Math.max(__fxd,CombatFX.stats.draws||0); requestAnimationFrame(f); })();}
window.__J=()=>{WIN.p.KeyJ=true;};window.__A=()=>{WIN.p.Space=true;};window.__Bk=()=>{WIN.p.KeyB=true;};
window.__reset=()=>{ATK.act=null;ATK.cd=[0,0,0];CHAIN.n=0;CHAIN.last=-9;HITSTOP.att=0;if(ATK.commit)atkCommitEnd('test');ATK.lock=null;};0"""
with sync_playwright() as p:
    b=p.chromium.launch(args=["--use-gl=angle","--use-angle=swiftshader","--enable-unsafe-swiftshader"])
    pg=b.new_page(viewport={"width":1280,"height":720}); errs=[]; pg.on("pageerror",lambda e: errs.append(str(e)[:200]))
    if os.environ.get("CC_ONLY")!="poses":
        load(pg,B); pg.evaluate(NOPAD); pg.evaluate(SPY)
        check("CombatFX present + HITSTOP default scale 0.5, parse full=1 off=0",pg.evaluate("!!window.CombatFX&&HITSTOP.scale===.5&&HITSTOP.parse('full')===1&&HITSTOP.parse('off')===0"),pg.evaluate("[!!window.CombatFX,HITSTOP.scale]"))
        pg.evaluate("window.__T=__npc('static');__near(__T)"); waitfor(pg,"__T.holder.visible&&atkTargets().includes(__T)",30)
        pg.evaluate("__freeze(true);__face(__T,1.6);__cam(__T);__reset();__T.knockLog=[];__T.hitN=0;__ev.length=0;__hf.length=0;__hap.length=0"); gw(pg,"false",.3); pg.evaluate("__face(__T,1.6)")
        dc0=pg.evaluate("__DC0()")
        # ---- full 3-hit chain: J pressed in-page (game time) each time the current hit is >=0.2 s old
        pg.evaluate("""window.__cl={d:[],hits:[],kv:[],ref:[],ride:[],cam:[],clk:[],hsF:0};__T.hsFrames=0;(function f(){ const A=ATK.act;
          if(CHAIN.n<3&&(!A&&CHAIN.n===0||A&&A.t>=.2&&A.ch===CHAIN.n&&!__cl['p'+CHAIN.n])){ __cl['p'+CHAIN.n]=1; if(CHAIN.n>0) __face(__T,1.6); __J(); __cl.d.push(+Ride.group.position.distanceTo(__T.holder.position).toFixed(2)); }
          const C=ATK.commit; if(ATK.act){ __cl.ref.push(C&&C.ref?(C.ref===__T?1:2):0); __cl.ride.push(Ride.group.position.x.toFixed(3)+','+Ride.group.position.z.toFixed(3)+','+Ride.speed.toFixed(2)); __cl.cam.push(camera.position.x.toFixed(3)+','+camera.position.z.toFixed(3)+','+camera.position.y.toFixed(3)); __cl.clk.push(+clock.toFixed(3)); }
          if(__T.kv&&__cl.kv.length<CHAIN.n) __cl.kv.push(+__T.kv.length().toFixed(2));
          if(!(CHAIN.n===3&&!ATK.act)&&__cl.ref.length<400) requestAnimationFrame(f); })()""")
        fin=gw(pg,"CHAIN.n===3&&!ATK.act",4)
        r=pg.evaluate("JSON.stringify({n:CHAIN.n,log:CHAIN.log.slice(-3),hits:__T.hitN||0,d:__cl.d,inT:atkTargets().includes(__T),vis:__T.holder.visible,kv:__T.knockLog||[],ev:__ev.map(e=>e[0]),hs:HITSTOP.log.slice(-3),hsF:__T.hsFrames,ref:[...new Set(__cl.ref)],same:window.__sameObj})"); print("chain",r,flush=True); R=json.loads(r)
        check("3-hit chain lands (3 chain steps, 3 hits on the target)",fin and R["n"]==3 and (R["hits"] or 0)>=3,r)
        check("hit 3 is a finisher (emit 'finisher', bigger knockback than hit 1)","finisher" in R["ev"] and len(R["kv"])>=2 and R["kv"][-1]>R["kv"][0]*1.5,R["kv"])
        check("emit events: attackStart x3 + lightHit x2 + finisher, one reused data object",R["ev"].count("attackStart")>=3 and R["ev"].count("lightHit")>=2 and R["same"],R["ev"])
        check("commit lock held on the same target for the whole chain (no switch)",R["ref"] in ([1],[0,1],[1,0],[0,1,0][:2]) and 2 not in R["ref"],R["ref"])
        fx=pg.evaluate("JSON.stringify({ev:__ev.map(e=>[e[0],e[5]]),hap:__hap.filter(h=>/Hit|finisher|hit3|dive/.test(h)),hf:__hf.length,hits:__T.hitN||0,fxd:__fxd})"); print("fx3 off",fx,flush=True); F=json.loads(fx)
        check("v3: fxName passed per move (codee dash = foot kick on attackStart + hits)",all(x[1] and x[1].startswith("foot") for x in F["ev"] if x[0] in("attackStart","lightHit","finisher")),F["ev"])
        check("v3 off: one emit + one haptic per hit (no doubles)",len([x for x in F["ev"] if x[0] in("lightHit","finisher")])==F["hits"] and len(F["hap"])==F["hits"] and F["hf"]==0,F)
        check("v3: attackStart before each hit event",[x[0] for x in F["ev"]][:2]==["attackStart","lightHit"],F["ev"][:4])
        check("v3: CombatFX draws <= 3 while FX live",0<F["fxd"]<=3,F["fxd"])
        hs=R["hs"]; check("hit-stop ms = CombatFX ms x HITSTOP_SCALE 0.5 (lightHit 20, finisher 55)",any(h[0]=="lightHit" and abs(h[1]-20)<.5 for h in hs) and any(h[0]=="finisher" and abs(h[1]-55)<.5 for h in hs),hs)
        check("hit-stop freezes the target (anim/knockback frozen frames > 0)",R["hsF"]>0,R["hsF"])
        mv=pg.evaluate("(()=>{const r=__cl.ride,c=__cl.cam,k=__cl.clk;let rs=0,cs=0,ks=0;for(let i=1;i<r.length;i++){if(r[i]===r[i-1])rs++;if(c[i]===c[i-1])cs++;if(k[i]<=k[i-1])ks++;}return [r.length,rs,cs,ks]})()")
        check("Ride movement, camera and world clock never frozen during the chain",mv[0]>3 and mv[1]==0 and mv[3]==0 and mv[2]==0,mv)
        gw(pg,"false",1.0); gw(pg,"!window.CombatFX||!CombatFX.stats||!CombatFX.stats.draws",3)
        # same view, same frame: CombatFX pool meshes on vs forced hidden -> idle FX cost must be 0 draws
        dd=pg.evaluate("(()=>{const M=[CombatFX.add&&CombatFX.add.mesh,CombatFX.ink&&CombatFX.ink.mesh].filter(Boolean);scene.traverse(o=>{if(o.isMesh&&o.name&&/cfx|combat/i.test(o.name))M.push(o)});const v=M.map(m=>m.visible);const a=__DC0();M.forEach(m=>m.visible=false);const b=__DC0();M.forEach((m,i)=>m.visible=v[i]);return [a,b,M.length,CombatFX.stats.draws]})()")
        check("draw delta 0 after the FX (idle; CombatFX pools on vs hidden, same view)",dd[0]==dd[1] and dd[3]==0,dd)
        # ---- A cancel after hit 1, B cancel after hit 2, finisher not cancellable
        pg.evaluate("__reset();__face(__T,1.6)"); gw(pg,"false",.2); c0=pg.evaluate("CHAIN.cancels")
        pg.evaluate("__J()"); gw(pg,"ATK.act&&ATK.act.ch===1&&ATK.act.t>.05",2); pg.evaluate("__A()"); a1=gw(pg,"!ATK.act",.5)
        check("A cancels hit 1",a1 and pg.evaluate(f"CHAIN.cancels>{c0}&&CHAIN.cancelLog[0]==='A'"),pg.evaluate("JSON.stringify(CHAIN.cancelLog)"))
        pg.evaluate("__reset();__face(__T,1.6)"); gw(pg,"false",.2)
        pg.evaluate("__J()"); gw(pg,"ATK.act&&ATK.act.ch===1&&ATK.act.t>.2",2); pg.evaluate("__J()"); gw(pg,"ATK.act&&ATK.act.ch===2&&ATK.act.t>.05",2); pg.evaluate("__Bk()"); b2=gw(pg,"!ATK.act",.5)
        check("B cancels hit 2",b2 and pg.evaluate("CHAIN.cancelLog[0]==='B'&&CHAIN.cancelLog[1]===2"),pg.evaluate("JSON.stringify(CHAIN.cancelLog)"))
        pg.evaluate("__reset();__face(__T,1.6)"); gw(pg,"false",.2)
        pg.evaluate("__J()"); gw(pg,"ATK.act&&ATK.act.ch===1&&ATK.act.t>.2",2); pg.evaluate("__J()"); gw(pg,"ATK.act&&ATK.act.ch===2&&ATK.act.t>.2",2); pg.evaluate("__J()"); gw(pg,"ATK.act&&ATK.act.ch===3",2)
        pg.evaluate("__Bk()"); gw(pg,"false",.1); check("finisher (hit 3) commits: B does not cancel it",pg.evaluate("CHAIN.cancelLog[1]!==3&&(ATK.act?ATK.act.ch===3:CHAIN.n===3)"),pg.evaluate("JSON.stringify([CHAIN.cancelLog,ATK.act&&ATK.act.ch])"))
        # ---- chain timeout 0.6 s
        pg.evaluate("__reset();__face(__T,1.6)"); gw(pg,"false",.2); r0=pg.evaluate("CHAIN.resets")
        pg.evaluate("__J()"); gw(pg,"CHAIN.n===1",1); gw(pg,"false",1.0)
        pg.evaluate("__J()"); gw(pg,"false",.1)
        check("chain resets after ~0.6 s without input (next J = hit 1 again)",pg.evaluate(f"CHAIN.resets>{r0}&&(!ATK.act||ATK.act.ch===1)"),pg.evaluate("JSON.stringify([CHAIN.n,CHAIN.resets,ATK.act&&ATK.act.ch])"))
        # ---- hitstop=off at runtime: no entity freeze
        pg.evaluate("__reset();__face(__T,1.6);HITSTOP.scale=0;__T.hsFrames=0;HITSTOP.log.length=0"); gw(pg,"false",.2); pg.evaluate("__J()"); gw(pg,"!ATK.act&&ATK.act!==undefined&&__T.hitN>0",1.5)
        check("HITSTOP_SCALE 0 (?hitstop=off) -> no freeze",pg.evaluate("HITSTOP.log.length===0&&__T.hsFrames===0"),pg.evaluate("JSON.stringify([HITSTOP.log,__T.hsFrames])")); pg.evaluate("HITSTOP.scale=.5")

    if os.environ.get("CC_ONLY")!="off":
        # ================= combat poses ON (?combatposes=1, Rigger ikki_skate poser) =================
        load(pg,B+"&combatposes=1&player=ikki"); pg.evaluate(NOPAD); pg.evaluate(SPY)
        pv=pg.evaluate("JSON.stringify({flag:CP.flag(),u:!!CP.player(),api:!!(CP.player()&&CP.player().onCombat)})"); print("poser",pv,flush=True)
        check("poses: flag on + player poser API present",'"u":true' in pv and '"api":true' in pv,pv)
        pg.evaluate("window.__T=__npc('static');__near(__T)"); waitfor(pg,"__T.holder.visible&&atkTargets().includes(__T)",30)
        pg.evaluate("__freeze(true);__face(__T,1.6);__cam(__T);__reset();CP.log.length=0;__T.knockLog=[];__T.hitN=0;__ev.length=0;__hf.length=0;__hap.length=0"); gw(pg,"false",.3); pg.evaluate("__face(__T,1.6)")
        pg.evaluate("""window.__pl={src:[],q:[]};(function f(){ const A=ATK.act; if(A&&A.hitSrc&&__pl.src[A.ch]===undefined) __pl.src[A.ch]=A.hitSrc;
          if(CHAIN.n<3&&(!A&&CHAIN.n===0||A&&A.ch===CHAIN.n&&A.hitOpen&&CP.cancelOK(A,'chain')&&!__pl['p'+CHAIN.n])){ __pl['p'+CHAIN.n]=1; __J(); }
          if(!(CHAIN.n===3&&!ATK.act)&&__pl.q.length<600){ __pl.q.push(1); requestAnimationFrame(f); } })()""")
        gw(pg,"CHAIN.n===3&&!ATK.act",8)
        r=pg.evaluate("JSON.stringify({log:CP.log.filter(l=>l[0]==='setState'||l[0]==='hit').map(l=>l.slice(0,3)),src:__pl.src,hits:__T.hitN||0,n:CHAIN.n})"); print("poses chain",r,flush=True); R=json.loads(r)
        st=[l for l in R["log"] if l[0]=="setState" and l[1]=="atk"]
        fp=pg.evaluate("JSON.stringify({ev:__ev.filter(e=>e[0]!=='attackStart').map(e=>e[0]),st:__ev.filter(e=>e[0]==='attackStart').map(e=>e[4]),hf:__hf,hap:__hap.filter(h=>/Hit|finisher|hit3|dive/.test(h)),hits:__T.hitN||0,hfT:CP.log.filter(l=>l[0]==='hit').map(l=>l[3]),fxd:__fxd})"); print("fx3 poses",fp,flush=True); FP=json.loads(fp)
        check("v3 poses: hit FX via fromHitFrame once per hit, haptic once per hit, no extra emit",len(FP["hf"])==FP["hits"] and len(FP["hap"])==FP["hits"] and not FP["ev"] and all(h[1] for h in FP["hf"]),FP)
        check("v3 poses: attackStart emitted before the hit frame (wind-up)",FP["st"] and FP["hfT"] and FP["st"][0]<FP["hfT"][0],[FP["st"][:3],FP["hfT"][:3]])
        check("poses: setState('atk',{step}) per chain hit in order 0,1,2",[l[2] for l in st][:3]==[0,1,2],st)
        check("poses: hit window opened on onHitFrame (not fallback) and hits land",R["hits"]>=3 and all(x=="onHitFrame" for x in R["src"][1:4] if x),R)
        # cancel gating: A pressed right after hit-1 start (before onCancelOpen) is ignored; after cancelOpen it cancels
        pg.evaluate("__reset();__face(__T,1.6);CP.log.length=0"); gw(pg,"false",.2); c0=pg.evaluate("CHAIN.cancels")
        pg.evaluate("__J()"); gw(pg,"ATK.act&&ATK.act.pose",1); pg.evaluate("__A()"); gw(pg,"false",.05)
        early=pg.evaluate(f"CHAIN.cancels==={c0}")
        gw(pg,"!ATK.act||(CP.u.combatQuery()||{}).cancelOpen",2); co=pg.evaluate("!!ATK.act&&!!(CP.u.combatQuery()||{}).cancelOpen")
        if co: pg.evaluate("__A()"); gw(pg,"!ATK.act",.5)
        check("poses: A cancel gated by onCancelOpen (ignored before, cancels after)",early and (not co or pg.evaluate(f"CHAIN.cancels>{c0}")),[early,co,pg.evaluate("JSON.stringify(CHAIN.cancelLog)")])
        # root motion clamps (14 m/s, 6 m, XR 3 m, no vertical): fake poser query, real CP.root
        rm=pg.evaluate("""(()=>{const save=CP.u, P=Ride.group.position, y0=P.y, out={}; const fake={combatQuery:()=>({root:{fwdVel:40}})}; CP.u=fake; const bk=CP.blocked; CP.blocked=()=>false;
          let A={rm:0}; const p0=P.clone(); for(let i=0;i<60;i++) CP.root(A,.05); out.desk=[+A.rm.toFixed(2),+(A.rmV||0).toFixed(1),+P.distanceTo(p0).toFixed(2),+(P.y-y0).toFixed(3)];
          const xr=renderer.xr, d=Object.getOwnPropertyDescriptor(xr,'isPresenting'); Object.defineProperty(xr,'isPresenting',{value:true,configurable:true});
          A={rm:0}; const p1=P.clone(); for(let i=0;i<60;i++) CP.root(A,.05); out.xr=[+A.rm.toFixed(2),+(A.rmV||0).toFixed(1),+P.distanceTo(p1).toFixed(2)];
          if(d) Object.defineProperty(xr,'isPresenting',d); else delete xr.isPresenting; CP.u=save; CP.blocked=bk; P.copy(p0); return out;})()""")
        check("poses: root motion clamps 14 m/s + 6 m, XR 3 m, no vertical",rm["desk"][0]<=6.001 and rm["desk"][1]<=14 and abs(rm["desk"][3])<1e-6 and rm["xr"][0]<=3.001,rm)
        # react on a poser victim: an NPC hits the (poser) player
        pg.evaluate("CP.log.length=0;ATK.stun=0;__face(__T,2.0)"); pg.evaluate("npcAttack(__T)"); gw(pg,"false",.1)
        rc=pg.evaluate("JSON.stringify({log:CP.log.filter(l=>l[1]==='react'),cs:CP.player().combatState()})")
        check("poses: react on a poser victim (player hit -> setState('react'), combatState 'react')",'"react"' in rc,rc)
        # heavy: hold J -> heavy charge, auto-release at 1.0 s, 2x knock scaled by charge
        pg.evaluate("__reset();ATK.stun=0;__face(__T,1.6);CP.log.length=0;__T.knockLog=[];window.__hold=true;(function f(){ if(!window.__hold) return; WIN.k.KeyJ=true; requestAnimationFrame(f); })();__J()")
        gw(pg,"ATK.act&&ATK.act.heavy",2); pg.evaluate("__face(__T,1.4)"); gw(pg,"CP.log.some(l=>l[0]==='release')",2.5); pg.evaluate("window.__hold=false;WIN.k.KeyJ=false"); gw(pg,"!ATK.act",2)
        hv=pg.evaluate("JSON.stringify({log:CP.log.filter(l=>l[0]==='setState'||l[0]==='release').map(l=>l.slice(0,4)),knock:__T.knockLog})"); print("heavy",hv,flush=True); H=json.loads(hv)
        rel=[l for l in H["log"] if l[0]=="release"]; hs=[l for l in H["log"] if l[0]=="setState" and l[2]=="heavy"]
        hc=pg.evaluate("JSON.stringify(__hf.slice(-1))"); check("v3 poses: heavy charge passed as fxCharge (ours, ~1.0)",'1' in hc and pg.evaluate("(__hf.slice(-1)[0]||[])[2]>=.9"),hc)
        check("poses: hold J >=0.35 s -> heavy charge, auto-release at ~1.0 s, knock 2x scaled by charge",hs and rel and rel[0][1]=="auto" and (rel[0][2]-hs[0][3])>=.9 and H["knock"] and max(H["knock"])>=H["knock"][0]*1.9,hv)
        # air float: a landed hit while airborne -> >=0.25 s float at reduced gravity
        fl=pg.evaluate("""new Promise(res=>{ __reset(); ATK.stun=0; wallLaunch(0,0,0,false); WALL.air.y=Ride.group.position.y+2; WALL.air.vy=-2; const S=atkSet(); const A={pose:true,hitOpen:true,hit:new Set(),m:Object.assign({},S.moves[0]),S,ch:1};
          atkHit(A,__T,1,0); const y0=WALL.air.y, c0=clock, f0=ATK.floatT; (function f(){ if(clock-c0<.25&&WALL.air) return requestAnimationFrame(f); res([+(f0||0).toFixed(2),+(y0-(WALL.air?WALL.air.y:0)).toFixed(3),+(clock-c0).toFixed(2),ATK.floats||0]); })(); })""")
        check("poses: air hit floats >=0.25 s game time (reduced gravity, drop < 0.4 m)",fl[0]>=.25 and fl[1]<.4 and fl[3]>0,fl)
        pg.evaluate("CP.teardown()"); check("poses: onCombat handlers unsubscribed on teardown",pg.evaluate("CP.unsub.length===0&&CP.u===null"))
    check("no page errors / cfx errors",not errs and not pg.evaluate("ATK.cfxErr||ATK.cpErr||null"),(errs[:3],pg.evaluate("ATK.cfxErr||null")))
    b.close()
print("RESULT",sum(ok),"/",len(ok)); import sys; sys.exit(0 if all(ok) else 1)
