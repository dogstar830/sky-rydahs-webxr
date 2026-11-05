# kit_shots.py (Palma Builder): pinned-camera night shots + draw counts of the crewhouse kit. usage: python3 kit_shots.py <html> <json-spec>
import sys,time,json
from playwright.sync_api import sync_playwright
H=sys.argv[1]; SPEC=json.loads(open(sys.argv[2]).read())
B=f"http://localhost:8765/v3build/{H}?chars=/skyrydahs-characters/&nofx"
HOOK=r"""(()=>{ if(window.__kh) return; window.__kh=1; const R=renderer,oR=R.render.bind(R),oB=R.renderBufferDirect.bind(R); let cnt=null;
 R.renderBufferDirect=function(c,s,g,m,o,gr){ if(cnt){ cnt.n++; let k=0; for(let a=o;a;a=a.parent) if(a.name&&a.name.startsWith('kit_')){k=1;break;} if(k){cnt.kit++; cnt.names[o.name]=(cnt.names[o.name]||0)+1;} } return oB(c,s,g,m,o,gr); };
 R.render=function(s,c){ if(s===scene&&window.__kp){ const v=window.__kp, G=garages.find(g=>g.crew===v.crew); const P=G.group.localToWorld(new THREE.Vector3(...v.cam)), T=G.group.localToWorld(new THREE.Vector3(...v.at));
   Ride.group.position.set(P.x,0,P.z); if('speed' in Ride) Ride.speed=0; c.fov=v.fov||60; c.updateProjectionMatrix(); const M=new THREE.Matrix4().lookAt(P,T,new THREE.Vector3(0,1,0)); M.setPosition(P);
   if(c.parent){ c.parent.updateMatrixWorld(true); M.premultiply(new THREE.Matrix4().copy(c.parent.matrixWorld).invert()); } M.decompose(c.position,c.quaternion,new THREE.Vector3()); c.updateMatrixWorld(true); }
  if(s===scene&&window.__arm){ window.__arm=0; cnt={n:0,kit:0,names:{}}; const r=oR(s,c); window.__last=cnt; cnt=null; return r; } return oR(s,c); }; })()"""
NIGHT="""(()=>{ try{SKY.setDay(0)}catch(e){} try{FACADE.setDay(0)}catch(e){} try{BRIDGES.setDay(0)}catch(e){} })()"""
out={}
with sync_playwright() as p:
    br=p.chromium.launch(args=["--use-gl=swiftshader","--enable-webgl","--ignore-gpu-blocklist"])
    pg=br.new_page(viewport={"width":SPEC.get("w",1280),"height":SPEC.get("h",853)}); errs=[]
    pg.on("pageerror",lambda e: errs.append("PAGEERR "+str(e)[:300])); pg.on("console",lambda m: errs.append(m.type+": "+m.text[:300]) if m.type in("error","warning") else None)
    pg.goto(B,timeout=180000); t0=time.time()
    while time.time()-t0<200:
        try:
            if pg.evaluate("typeof RIDERS!='undefined'&&RIDERS.ready&&window.KIT_READY"): break
        except Exception: pass
        time.sleep(.5)
    time.sleep(5); pg.keyboard.press("Enter"); time.sleep(1.5)
    pg.evaluate("garages.forEach(g=>g.gate&&(g.gate.dismissed=true));if(typeof GATE!='undefined'){GATE.uiOpen=false;gateUI()};window.__npcPassive=true;window.__npcFreeze=true")
    pg.evaluate(NIGHT); pg.evaluate(HOOK); pg.evaluate("Ride.group.visible=false;camera.children.forEach(c=>c.visible=false);Array.from(document.body.querySelectorAll(\"*\")).forEach(d=>{ if(d!==renderer.domElement&&!d.contains(renderer.domElement)) d.style.visibility=\"hidden\"; })")
    for sh in SPEC["shots"]:
        pg.evaluate(f"window.KIT_FORCE={json.dumps(sh.get('crew'))};window.KIT_FLOOR={json.dumps(sh.get('floor'))};window.__kp={json.dumps(sh)}"); [time.sleep(.5) for _ in range(120) if not pg.evaluate("!!(KIT.propsReady&&KIT.skates)")]; pg.evaluate(sh["pre"]) if sh.get("pre") else None; time.sleep(sh.get("wait",3))
        pg.evaluate("window.__last=null;window.__arm=1"); time.sleep(.8); d=pg.evaluate("window.__last")
        if sh.get("eval"): print("EVAL",pg.evaluate(sh["eval"]),flush=True)
        if sh.get("out"): pg.screenshot(path=sh["out"])
        out[sh["name"]]=d; print(sh["name"],d and d["n"],d and d["kit"],flush=True)
    out["errors"]=errs; br.close()
json.dump(out,open(SPEC["json"],"w"),indent=1); print("errors:",len(errs)); [print(e) for e in errs[:25]]
