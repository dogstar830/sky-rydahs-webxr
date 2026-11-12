# Palma Nov 12: (1) Rust Claw near/far LOD shots on A copy, (2) heaven (rooftop L) tag spot reachability probe. read-only on game state.
import sys,time,json
src=open('/workspace/v3build/dcsplit2.py').read(); ns={}
exec(src.split("R={}")[0].replace("H,Q,tag=sys.argv[1],sys.argv[2],sys.argv[3]","H,Q,tag='x','',''"),ns)
DAY,HOOK=ns['DAY'],ns['HOOK']
from playwright.sync_api import sync_playwright
H=sys.argv[1]; B=f"http://localhost:8765/v3build/{H}?chars=/skyrydahs-characters/&nofx&seed=1"
PROBE=r"""(()=>{ const out=[]; const WG=(x,z,yh)=>{ try{ const g=WORLD_GROUND(x,z,yh); return g&&isFinite(g.y)?+g.y.toFixed(2):null; }catch(e){ return 'err'; } };
 const decks=(GRAP.pts||[]).map(p=>({label:p.label||p.name,kind:p.kind,x:p.x,z:p.z,y:p.y,d:p.deck||p.d}));
 for(const sp of GRAF.spots.filter(s=>s.heaven)){ const n=[sp.nx,sp.nz], R=sp.roof;
  const inside=[.15,.6,1.5].map(d=>WG(sp.x-n[0]*d,sp.z-n[1]*d,R+1));
  const front=[.3,1,2,3,4,5].map(d=>({d,y:WG(sp.x+n[0]*d,sp.z+n[1]*d,R+1)}));
  const ledge=front.filter(f=>typeof f.y==='number'&&Math.abs(f.y-R)<2.5);
  const inDeck=decks.filter(k=>k.d&&sp.x-n[0]*.3>=k.d.minX-.2&&sp.x-n[0]*.3<=k.d.maxX+.2&&sp.z-n[1]*.3>=k.d.minZ-.2&&sp.z-n[1]*.3<=k.d.maxZ+.2).map(k=>k.label+'@y'+(+k.y).toFixed(1));
  const grapNear=decks.filter(k=>Math.hypot(k.x-sp.x,k.z-sp.z)<11).map(k=>k.label+':'+Math.hypot(k.x-sp.x,k.z-sp.z).toFixed(1)+'m y'+(+k.y).toFixed(1));
  const kicks=(window.WALL_KICKS||[]).filter(w=>Math.hypot(w.center[0]-sp.x,w.center[2]-sp.z)<8).map(w=>w.name+' h'+w.height+' n'+w.normal.join(','));
  const panels=(window.WALL_PANELS||[]).filter(w=>{ const c=w.center||w.pos||[w.x,0,w.z]; return c&&Math.hypot((c[0]||0)-sp.x,(c[2]!=null?c[2]:c[1])-sp.z)<8; }).map(w=>w.name);
  out.push({id:sp.id,district:sp.district,kind:sp.kind,x:+sp.x.toFixed(1),z:+sp.z.toFixed(1),roof:+R.toFixed(2),n,inside,front,ledge:ledge.length,inDeck,grapNear,kicks,panels}); }
 return {spots:out,ndecks:decks.length,deckSample:decks.slice(0,3),jumpInfo:(typeof Ride!=='undefined'?{jv:Ride.jumpV||null}:null)}; })()"""
with sync_playwright() as p:
    br=p.chromium.launch(args=["--use-gl=swiftshader","--enable-webgl","--ignore-gpu-blocklist"])
    pg=br.new_page(viewport={"width":1600,"height":900}); errs=[]; pg.on("pageerror",lambda e: errs.append(str(e)[:200]))
    pg.on("console",lambda m: errs.append("CONSOLE "+m.text[:200]) if m.type=="error" else None)
    pg.goto(B,timeout=180000); t0=time.time()
    while time.time()-t0<240:
        try:
            if pg.evaluate("typeof RIDERS!='undefined'&&RIDERS.ready&&window.GRAF&&GRAF.ready&&GRIND.world"): break
        except Exception: pass
        time.sleep(.5)
    time.sleep(6); pg.keyboard.press("Enter"); time.sleep(1.5)
    pg.evaluate("garages.forEach(g=>g.gate&&(g.gate.dismissed=true));if(typeof GATE!='undefined'){GATE.uiOpen=false;gateUI()};window.__npcPassive=true;window.__npcFreeze=true")
    pg.evaluate("try{grapBuild()}catch(e){}")
    res=pg.evaluate(PROBE); json.dump(res,open('/workspace/v3build/shots/g13_probe.json','w'),indent=1)
    pg.evaluate(HOOK); pg.evaluate(DAY)
    for lab,(lx,ly,lz,tx,ty,tz) in [("near22",(6,3.2,22,0,2.5,3)),("mid120",(30,20,120,0,3,0)),("far200",(40,25,200,0,3,0))]:
        pg.evaluate(f"""(()=>{{const G=garages.find(g=>g.crew==='rustclaw');const a=G.group.localToWorld(new THREE.Vector3({lx},{ly},{lz})),b=G.group.localToWorld(new THREE.Vector3({tx},{ty},{tz}));window.__pin={{rider:[a.x,0,a.z],cam:[a.x,a.y,a.z,b.x,b.y,b.z]}};}})()""")
        time.sleep(3); st=pg.evaluate("KIT_EXT_LODS.map(L=>L.root.name+':'+(L.isFar?'FAR':'near'))")
        pg.screenshot(path=f"/workspace/v3build/shots/cw_rc_lod_{lab}.png"); print("LOD",lab,st,flush=True)
        if lab=="far200":   # same pose with near parts forced (what base draws)
            pg.evaluate("window.__kitlodOff=1;for(const L of KIT_EXT_LODS){L.far.visible=false;L.parts.forEach(o=>o.visible=true);} KIT_EXT_LODS.forEach(L=>L.isFar=true); const t=KIT_EXT_LODS; window.KIT_EXT_LODS_SAVE=t.splice(0)")
            time.sleep(1.5); pg.screenshot(path=f"/workspace/v3build/shots/cw_rc_lod_far200_nearparts.png"); print("LOD far200 forced-near",flush=True)
    br.close()
print("ERRORS",errs[:10]); print(json.dumps(res)[:200])
