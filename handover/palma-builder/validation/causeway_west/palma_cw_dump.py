# Palma Builder Nov 12: per-draw world dump at causeway_west (dcsplit2 hook + optional gate NPC fan). usage: python3 palma_cw_dump.py <html> <tag>
import sys,time,json
src=open('/workspace/v3build/dcsplit2.py').read(); ns={}
exec(src.split("R={}")[0].replace("H,Q,tag=sys.argv[1],sys.argv[2],sys.argv[3]","H,Q,tag='x','',''"),ns)
DAY,HOOK,BRV=ns['DAY'],ns['HOOK'],ns['BRV']
from playwright.sync_api import sync_playwright
H,tag=sys.argv[1],sys.argv[2]
B=f"http://localhost:8765/v3build/{H}?chars=/skyrydahs-characters/&nofx&seed=1"
# per-draw recorder layered over dcsplit2 hook: wraps renderBufferDirect again, records a descriptor per world draw
REC=r"""(()=>{ const R=renderer, oB=R.renderBufferDirect.bind(R), oR=R.render.bind(R); let rec=null;
 const top=o=>{ let a=o; while(a.parent&&a.parent.type!=='Scene') a=a.parent; return a; };
 const charRoot=o=>{ for(let a=o;a;a=a.parent){ if(a.isSkinnedMesh||(typeof Ride!=='undefined'&&a===Ride.group)||(a.userData&&(a.userData.npc||a.userData.rider))) return true; } return false; };
 const npcRoot=o=>{ const N=[...((typeof RIDERS!=='undefined'&&RIDERS.npcs)||[]),typeof RIDERS!=='undefined'?RIDERS.ikkiNpc:null].filter(n=>n&&n.holder).map(n=>n.holder); for(let a=o;a;a=a.parent) if(N.includes(a)) return true; return false; };
 R.renderBufferDirect=function(cam,sc,geo,mat,obj,grp){ if(rec){ const t=top(obj); const p=new THREE.Vector3(); obj.getWorldPosition(p);
   let k; if(charRoot(obj)) k='chars'; else if(obj.isPoints||obj.isSprite||(mat.blending===THREE.AdditiveBlending&&!(obj.userData&&obj.userData.worldPerf))) k='fx'; else k='world';
   rec.push({k,npc:npcRoot(obj),top:(t.name||'')+'|'+t.type+'|'+(t.userData&&t.userData.mod||'')+'@'+t.position.x.toFixed(0)+','+t.position.z.toFixed(0),name:obj.name||'',type:obj.type,geo:geo.type,mat:mat.type+':'+(mat.name||'')+':'+mat.uuid.slice(0,6),map:!!mat.map,inst:!!obj.isInstancedMesh,wp:obj.userData&&obj.userData.worldPerf||null,mod:obj.userData&&obj.userData.mod||null,noMerge:!!(obj.userData&&obj.userData.noMerge),pos:[+p.x.toFixed(1),+p.y.toFixed(1),+p.z.toFixed(1)]}); }
  return oB(cam,sc,geo,mat,obj,grp); };
 R.render=function(s,c){ if(s===scene&&window.__fanTick) window.__fanTick(); if(s===scene&&window.__recArm){ window.__recArm=0; rec=[]; const r=oR(s,c); window.__recLast=rec; rec=null; return r; } return oR(s,c); };
})()"""
FAN=r"""(()=>{ const pin0=window.__pin; window.__fanOn=true; const old=window.__fanTick; if(old) return;
 window.__fanTick=()=>{ if(!window.__fanOn||!window.__pin) return; const v=window.__pin.cam; const N=[...(RIDERS.npcs||[]),RIDERS.ikkiNpc].filter(n=>n&&n.holder); const dx=v[3]-v[0],dz=v[5]-v[2],l=Math.hypot(dx,dz)||1,fx=dx/l,fz=dz/l;
  N.forEach((n,i)=>{const d=8+(i%3)*6,s=(i-(N.length-1)/2)*2.2;n.holder.visible=true;n.holder.position.set(v[0]+fx*d-fz*s,0,v[2]+fz*d+fx*s);}); };
 })()"""
out={}; errs=[]
with sync_playwright() as p:
    br=p.chromium.launch(args=["--use-gl=swiftshader","--enable-webgl","--ignore-gpu-blocklist"])
    pg=br.new_page(viewport={"width":1280,"height":720}); pg.on("pageerror",lambda e: errs.append(str(e)[:200]))
    pg.on("console",lambda m: errs.append("CONSOLE "+m.text[:200]) if m.type=="error" else None)
    pg.goto(B,timeout=180000); t0=time.time()
    while time.time()-t0<240:
        try:
            if pg.evaluate("typeof RIDERS!='undefined'&&RIDERS.ready&&window.GRAF&&GRAF.ready&&GRIND.world"): break
        except Exception: pass
        time.sleep(.5)
    time.sleep(6); pg.keyboard.press("Enter"); time.sleep(1.5)
    pg.evaluate("garages.forEach(g=>g.gate&&(g.gate.dismissed=true));if(typeof GATE!='undefined'){GATE.uiOpen=false;gateUI()};window.__npcPassive=true;window.__npcFreeze=true")
    pg.evaluate(HOOK); pg.evaluate(REC)
    out["npcs"]=pg.evaluate("[(RIDERS.npcs||[]).length,!!RIDERS.ikkiNpc]")
    out["counts"]=pg.evaluate("({colliders:colliders.length,kicks:(typeof WALL_KICKS!=='undefined'?WALL_KICKS.length:null),panels:(typeof WALL_PANELS!=='undefined'?WALL_PANELS.length:null)})")
    for lab,day,fan in [("night_nofan",0,0),("night_fan",0,1),("day_nofan",1,0),("day_fan",1,1)]:
        if day and not out.get("_day"): pg.evaluate(DAY); out["_day"]=1
        pg.evaluate(f"window.__pin={BRV}('causeway')")
        if fan: pg.evaluate(FAN)
        else: pg.evaluate("window.__fanOn=false")
        time.sleep(3); frames=[]
        for i in range(5):
            pg.evaluate("window.__recArm=1"); time.sleep(.5); r=pg.evaluate("window.__recLast"); 
            if r: frames.append(r)
        best=max(frames,key=lambda f:sum(1 for d in f if d['k']=='world'))
        w=[d for d in best if d['k']=='world']
        out[lab]={"world_per_frame":[sum(1 for d in f if d['k']=='world') for f in frames],"chars_per_frame":[sum(1 for d in f if d['k']=='chars') for f in frames],
                  "fx":sum(1 for d in best if d['k']=='fx'),"total":len(best),"info_calls":pg.evaluate("renderer.info.render.calls"),
                  "world_npc_rooted":sum(1 for d in w if d['npc']),"draws":best}
        pg.screenshot(path=f"/workspace/v3build/shots/cw_{tag}_{lab}.png")
    br.close()
out["errors"]=errs[:20]; out.pop("_day",None)
json.dump(out,open(f"/workspace/v3build/shots/cw_{tag}.json","w"),indent=1)
print(json.dumps({k:(v if not isinstance(v,dict) or 'draws' not in v else {a:b for a,b in v.items() if a!='draws'}) for k,v in out.items()}))
