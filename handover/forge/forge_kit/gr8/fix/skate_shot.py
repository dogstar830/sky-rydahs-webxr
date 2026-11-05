# Forge: close in-game shot of a rider's AT skate v2 (screenshot standard: 1920x1080 dsf1.5 ?tier=hd, FX on, >=60 frames)
import sys,time,json
from playwright.sync_api import sync_playwright
OUT=sys.argv[1]; Q=sys.argv[2] if len(sys.argv)>2 else ''
B="http://localhost:8765/v3build/sky-rydahs-v3-ikki.html?chars=/skyrydahs-characters/&tier=hd&seed=1"+Q
FIND=r"""(()=>{ window.__fb=o=>{ const bs=o.skeleton.bones; const f=bs.filter(b=>/foot/i.test(b.name)&&/l/i.test(b.name.replace(/foot/i,""))); const c=f.length?f:bs; let best=c[0],y=1e9; for(const b of c){ const w=b.getWorldPosition(new THREE.Vector3()); if(w.y<y){y=w.y;best=b;} } return best; }; const L=[]; scene.traverse(o=>{ if(o.name==='CrewATSkate_LOD0'&&o.material) L.push(o); }); window.__sk=L;
 return L.map(o=>{ let r=o; while(r.parent&&r.parent!==scene) r=r.parent; const b=window.__fb(o); const p=b.getWorldPosition(new THREE.Vector3());
  const m=o.material; return {bone:window.__fb(o).name,root:r.name, foot:[p.x,p.y,p.z], env:!!m.envMap, envI:m.envMapIntensity, vis:o.visible&&r.visible}; }); })()"""
PIN=r"""(i=>{ const o=window.__sk[i]; const R=renderer,oR=R.render.bind(R); if(window.__ph) return; window.__ph=1;
 window.__npcPassive=true; window.__npcFreeze=true;
 R.render=function(s,c){ if(s===scene&&window.__skp){ const b=window.__fb(o); const F=b.getWorldPosition(new THREE.Vector3()); let r=o; while(r.parent&&r.parent!==scene) r=r.parent;
   const q=r.getWorldQuaternion(new THREE.Quaternion()), side=new THREE.Vector3(1,0,0.55).normalize().applyQuaternion(q); const P=F.clone().addScaledVector(side,0.85); P.y=F.y+0.18; const T=F.clone(); T.y=F.y-0.08;
   c.fov=40; c.updateProjectionMatrix(); const M=new THREE.Matrix4().lookAt(P,T,new THREE.Vector3(0,1,0)); M.setPosition(P);
   if(c.parent){ c.parent.updateMatrixWorld(true); M.premultiply(new THREE.Matrix4().copy(c.parent.matrixWorld).invert()); } M.decompose(c.position,c.quaternion,new THREE.Vector3()); c.updateMatrixWorld(true); }
  return oR(s,c); }; window.__skp=1; })"""
with sync_playwright() as p:
    br=p.chromium.launch(args=["--use-gl=swiftshader","--enable-webgl","--ignore-gpu-blocklist"])
    pg=br.new_page(viewport={"width":1920,"height":1080},device_scale_factor=1.5); errs=[]
    pg.on("pageerror",lambda e: errs.append("PAGEERR "+str(e)[:200])); pg.on("console",lambda m: errs.append(m.text[:200]) if m.type=="error" or 'skate' in m.text else None)
    pg.goto(B,timeout=300000); t0=time.time()
    while time.time()-t0<300:
        try:
            if pg.evaluate("typeof RIDERS!='undefined'&&RIDERS.ready"): break
        except Exception: pass
        time.sleep(1)
    time.sleep(5); pg.keyboard.press("Enter"); time.sleep(2)
    pg.evaluate("try{garages.forEach(g=>g.gate&&(g.gate.dismissed=true));if(typeof GATE!='undefined'){GATE.uiOpen=false;gateUI()}}catch(e){}")
    L=[]; t1=time.time()
    while time.time()-t1<240 and not L: L=pg.evaluate(FIND); time.sleep(3)
    print(json.dumps(L)[:800])
    i=next((k for k,x in enumerate(L) if x['vis']),0); pg.evaluate(PIN+f"({i})")
    pg.evaluate("Array.from(document.body.querySelectorAll('*')).forEach(d=>{ if(d!==renderer.domElement&&!d.contains(renderer.domElement)) d.style.visibility='hidden'; })")
    f0=pg.evaluate("frame"); t1=time.time()
    while pg.evaluate("frame")-f0<62 and time.time()-t1<900: time.sleep(3)
    print("frames",pg.evaluate("frame")-f0, "fx", pg.evaluate("typeof composer!='undefined'&&!!composer"))
    pg.screenshot(path=OUT,timeout=600000); print("errs",errs[:8]); br.close()
