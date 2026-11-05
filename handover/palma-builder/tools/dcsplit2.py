# dcsplit2: true per-frame draw attribution by wrapping renderer.renderBufferDirect during the main renderer.render(scene,...).
# Camera + rider pinned every frame inside the render wrapper (game camera itself is moved, so base culling sees the pin too).
# usage: RUNS=5 python3 dcsplit2.py <html> <extra-query> <tag>
import sys,time,json,os,statistics as st
from playwright.sync_api import sync_playwright
H,Q,tag=sys.argv[1],sys.argv[2],sys.argv[3]; RUNS=int(os.environ.get("RUNS","5"))
B=f"http://localhost:8765/v3build/{H}?chars=/skyrydahs-characters/&nofx{Q}"
DAY="""(()=>{scene.traverse(o=>{if(o.isHemisphereLight){o.intensity=.85;o.color.set(0xcfe0ff);o.groundColor.set(0x6a6470);}});scene.fog.color.set(0xb8c8e0);_fogBase.set(0xb8c8e0);scene.background.set(0x9ab8e0);if(typeof FACADE!=='undefined')FACADE.setDay(1);if(typeof BRIDGES!=='undefined')BRIDGES.setDay(1);})()"""
HOOK=r"""(()=>{ if(window.__dcHooked) return; window.__dcHooked=1; const R=renderer, oR=R.render.bind(R), oB=R.renderBufferDirect.bind(R);
 const M=new THREE.Matrix4(), P=new THREE.Vector3(), T=new THREE.Vector3(), Qt=new THREE.Quaternion(), Sc=new THREE.Vector3(), UP=new THREE.Vector3(0,1,0);
 function pin(c){ const v=window.__pin; if(!v) return; if(v.rider){ Ride.group.position.set(v.rider[0],v.rider[1],v.rider[2]); if('speed' in Ride) Ride.speed=0; if(typeof GRIND!=='undefined') GRIND.on=null; }
  P.set(v.cam[0],v.cam[1],v.cam[2]); T.set(v.cam[3],v.cam[4],v.cam[5]); M.lookAt(P,T,UP); M.setPosition(P); // desired world matrix
  if(c.parent){ c.parent.updateMatrixWorld(true); M.premultiply(new THREE.Matrix4().copy(c.parent.matrixWorld).invert()); }
  M.decompose(c.position,c.quaternion,Sc); c.updateMatrixWorld(true); }
 const charRoot=o=>{ for(let a=o;a;a=a.parent){ if(a.isSkinnedMesh||(typeof Ride!=='undefined'&&a===Ride.group)||(a.userData&&(a.userData.npc||a.userData.rider))) return true; } return false; };
 const mod=o=>{ if(o.userData&&o.userData.worldPerf) return 'wp:'+o.userData.worldPerf; let a=o; while(a.parent&&a.parent.type!=='Scene') a=a.parent; return (a.name||a.userData&&a.userData.mod||'')+'/'+(o.name||o.type); };
 let cnt=null;
 R.renderBufferDirect=function(cam,sc,geo,mat,obj,grp){ if(cnt){ let k; const isCamChild=(()=>{for(let a=obj;a;a=a.parent) if(a===camera) return true; return false;})();
   if(isCamChild) k='hud'; else if(charRoot(obj)) k='chars'; else if(obj.isPoints||obj.isSprite||(mat.blending===THREE.AdditiveBlending&&!(obj.userData&&obj.userData.worldPerf))) k='fx'; else k='world';
   cnt.C[k]++; cnt.n++; const m=k+'|'+mod(obj); cnt.mods[m]=(cnt.mods[m]||0)+1; }
  return oB(cam,sc,geo,mat,obj,grp); };
 R.render=function(s,c){ if(s===scene) pin(c); if(s===scene&&window.__dcArm){ window.__dcArm=0; const c0=R.info.render.calls; cnt={C:{world:0,chars:0,hud:0,fx:0},n:0,mods:{}};
   const r=oR(s,c); cnt.main_calls=R.info.render.calls-c0; window.__dcLast=cnt; cnt=null; return r; } return oR(s,c); };
})()"""
BRV="""((id)=>{const b=PALMA.bridges.find(q=>q.id===id),mx=(b.a[0]+b.b[0])/2,mz=(b.a[1]+b.b[1])/2,L=Math.hypot(b.b[0]-b.a[0],b.b[1]-b.a[1]),ux=(b.b[0]-b.a[0])/L,uz=(b.b[1]-b.a[1])/L,px=uz,pz=-ux;
 return {rider:[b.a[0]-ux*30,0,b.a[1]-uz*30],cam:[mx-px*L*.6+ux*L*.2,9,mz-pz*L*.6+uz*L*.2,mx,6,mz]};})"""
V=[("causeway",BRV+"('causeway')"),("b98",BRV+"('b98')"),("aerial","({rider:[0,0,60],cam:[0,40,120,0,0,0]})"),("street","({rider:[-60,0,-30],cam:[-59.2,1.7,-17,-60,6,-44]})")]
R={}
with sync_playwright() as p:
    br=p.chromium.launch(args=["--use-gl=swiftshader","--enable-webgl","--ignore-gpu-blocklist"])
    for run in range(RUNS):
        pg=br.new_page(viewport={"width":1280,"height":720}); errs=[]; pg.on("pageerror",lambda e: errs.append(str(e)[:200]))
        pg.goto(B,timeout=180000); t0=time.time()
        while time.time()-t0<200:
            try:
                if pg.evaluate("typeof RIDERS!='undefined'&&RIDERS.ready&&window.GRAF&&GRAF.ready&&GRIND.world"): break
            except Exception: pass
            time.sleep(.5)
        time.sleep(6); pg.keyboard.press("Enter"); time.sleep(1.5)
        pg.evaluate("garages.forEach(g=>g.gate&&(g.gate.dismissed=true));if(typeof GATE!='undefined'){GATE.uiOpen=false;gateUI()};window.__npcPassive=true;window.__npcFreeze=true")
        pg.evaluate("new Promise(r=>{const s=document.createElement('script');s.src='perf/drawcalls/dc_probe.js';s.onload=r;document.head.appendChild(s);})"); pg.evaluate(DAY); pg.evaluate(HOOK)
        for lab,js in V:
            pg.evaluate(f"window.__pin={js}"); time.sleep(3)
            pg.evaluate("window.__dcLast=null;window.__dcArm=1"); time.sleep(.6)
            d=pg.evaluate("window.__dcLast"); probe=pg.evaluate(f"(()=>{{ DC_PROBE.run('{lab}'); return DC_PROBE.last.sum.renderer_calls; }})()")
            d["probe_calls"]=probe; d["cam"]=pg.evaluate("camera.getWorldPosition(new THREE.Vector3()).toArray().map(v=>+v.toFixed(2))")
            R.setdefault(lab,[]).append(d)
            if run==0: pg.screenshot(path=f"/workspace/v3build/shots/dc2_{tag}_{lab}.png")
        R.setdefault("errors",[]).extend(errs[:3]); pg.close()
    br.close()
out={"errors":R.pop("errors",[])}
for lab,runs in R.items():
    row={}
    for k in ("world","chars","hud","fx","n","main_calls","probe_calls"):
        xs=[(r["C"][k] if k in r["C"] else r[k]) for r in runs]; row[k]=[min(xs),round(st.mean(xs),1),max(xs)]
    row["per_run_world"]=[r["C"]["world"] for r in runs]; row["cams"]=[r["cam"] for r in runs]
    agg={}
    for r in runs:
        for m,v in r["mods"].items(): agg[m]=agg.get(m,0)+v/len(runs)
    row["mods"]=sorted(((m,round(v,1)) for m,v in agg.items()),key=lambda x:-x[1])[:40]
    out[lab]=row
json.dump(out,open(f"/workspace/v3build/shots/dc2_{tag}.json","w"),indent=1)
print(json.dumps({k:({c:v[c] for c in ("world","chars","fx","n","main_calls","probe_calls")} if k!="errors" else v) for k,v in out.items()}))
