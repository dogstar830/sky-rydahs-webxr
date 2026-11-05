# usage: python3 perf_measure.py <html-name-in-v3build> <tag>  -> per-module draw calls at the worst views (json + shots/perf_<tag>_<view>_<mode>.png)
import sys,time,json,re
from playwright.sync_api import sync_playwright
H=sys.argv[1]; tag=sys.argv[2]; B=f"http://localhost:8765/v3build/{H}?chars=/skyrydahs-characters/&nofx"
src=open(f"/workspace/v3build/{H}").read().split("\n")
heads=[(i+1,l.strip()[:70]) for i,l in enumerate(src) if re.match(r"^// (=====|----) ",l)]
def sec(line):
    line=line
    h="?"
    for n,t in heads:
        if n<=line: h=t
        else: break
    return h
INIT=r"""(()=>{ let _s=123456789; Math.random=()=>{ _s^=_s<<13; _s^=_s>>>17; _s^=_s<<5; return ((_s>>>0)%1e9)/1e9; }; let T; const inst=()=>{ if(!T||!T.Object3D||T.__hk) return; T.__hk=1; const add=T.Object3D.prototype.add; const RX=/"""+re.escape(H)+r"""[^:]*:(\d+):/;
 T.Object3D.prototype.add=function(...a){ const st=(new Error().stack||'').split('\n'); let ln=0; for(const s of st){ const m=s.match(RX); if(m){ ln=+m[1]; break; } }
  for(const o of a) if(o&&o.userData&&!o.userData.__ln) o.userData.__ln=ln; return add.apply(this,a); }; };
 Object.defineProperty(window,'THREE',{configurable:true,get(){return T;},set(v){ T=v; queueMicrotask(inst); }}); })()"""
COUNT="""new Promise(res=>{ const C={}, T={}; const objs=[]; scene.traverse(o=>{ if(o.isMesh||o.isPoints||o.isLine||o.isSprite){ objs.push(o);} });
 const wrap=o=>{ const f=o.onBeforeRender; o.__f=f; o.onBeforeRender=function(r,s,c,g,m,gr){ let ln=0; for(let a=this;a;a=a.parent){ if(a.userData.__ln){ ln=a.userData.__ln; break; } }
   const k=ln+'|'+(this.isInstancedMesh?'inst':this.isPoints?'pts':this.isSprite?'sprite':this.isLine?'line':'mesh'); C[k]=(C[k]||0)+1;
   const idx=g.index?g.index.count:(g.attributes.position?g.attributes.position.count:0); T[k]=(T[k]||0)+idx/3*(this.isInstancedMesh?this.count:1); return f.apply(this,arguments); }; };
 objs.forEach(wrap); renderer.info.reset(); renderer.info.autoReset=false; requestAnimationFrame(()=>{ for(const k in C){C[k]=0;T[k]=0;} renderer.info.reset();
  requestAnimationFrame(()=>{ const calls=renderer.info.render.calls, tris=renderer.info.render.triangles; renderer.info.autoReset=true; objs.forEach(o=>{o.onBeforeRender=o.__f;});
   res({calls,tris,C,T}); }); }); })"""
DAY="""(()=>{scene.traverse(o=>{if(o.isHemisphereLight){o.intensity=.85;o.color.set(0xcfe0ff);o.groundColor.set(0x6a6470);}});
scene.fog.color.set(0xb8c8e0);_fogBase.set(0xb8c8e0);scene.background.set(0x9ab8e0);if(typeof FACADE!=='undefined')FACADE.setDay(1);if(typeof BRIDGES!=='undefined')BRIDGES.setDay(1);})()"""
BR="""((id)=>{GRIND.on=null;const b=PALMA.bridges.find(q=>q.id===id),mx=(b.a[0]+b.b[0])/2,mz=(b.a[1]+b.b[1])/2,L=Math.hypot(b.b[0]-b.a[0],b.b[1]-b.a[1]),
 ux=(b.b[0]-b.a[0])/L,uz=(b.b[1]-b.a[1])/L,px=uz,pz=-ux; Ride.group.position.set(b.a[0]-ux*30,0,b.a[1]-uz*30);
 const V=[mx-px*L*.6+ux*L*.2,9,mz-pz*L*.6+uz*L*.2, mx,6,mz]; window.__camHook=()=>{camera.position.set(V[0],V[1],V[2]);camera.lookAt(V[3],V[4],V[5]);};})"""
V={"street":"GRIND.on=null;Ride.group.position.set(-60,0,-30);Ride.yaw=Math.PI;window.__camHook=()=>{camera.position.set(-59.2,1.7,-17);camera.lookAt(-60,6,-44);}",
 "causeway":BR+"('causeway')","b98":BR+"('b98')",
 "aerial":"GRIND.on=null;Ride.group.position.set(0,0,60);window.__camHook=()=>{camera.position.set(0,40,120);camera.lookAt(0,0,0)}"}
FP="""JSON.stringify(GRIND.S.map(s=>[s.kind,s.pts.length,+s.L.toFixed(3),...[s.pts[0],s.pts[s.pts.length-1]].map(p=>[+p.x.toFixed(3),+p.y.toFixed(3),+p.z.toFixed(3)])]))"""
GP="""JSON.stringify({col:colliders.length,colh:colliders.reduce((a,c)=>a+c.minX*1.3+c.maxZ*.7+(c.wallPanel?100:0),0).toFixed(2),graf:(window.GRAF&&GRAF.spots||[]).map(s=>s.id+':'+s.x.toFixed(2)+','+s.z.toFixed(2)).join(';'),turf:!!window.TURF,gates:garages.length,rails:rails.length})"""
out={"views":{}}
with sync_playwright() as p:
    br=p.chromium.launch(args=["--use-gl=swiftshader","--enable-webgl","--ignore-gpu-blocklist"]); pg=br.new_page(viewport={"width":1280,"height":720})
    errs=[]; pg.on("pageerror",lambda e: errs.append(str(e)[:200]))
    pg.add_init_script(INIT)
    pg.goto(B,timeout=180000)
    t0=time.time()
    while time.time()-t0<200:
        try:
            if pg.evaluate("typeof RIDERS!='undefined'&&RIDERS.ready&&window.GRAF&&GRAF.ready&&GRIND.world"): break
        except Exception: pass
        time.sleep(.5)
    time.sleep(6); pg.keyboard.press("Enter"); time.sleep(1.5)
    pg.evaluate("garages.forEach(g=>g.gate&&(g.gate.dismissed=true));if(typeof GATE!='undefined'){GATE.uiOpen=false;gateUI()};window.__npcPassive=true;window.__npcFreeze=true")
    open(f"/workspace/v3build/shots/perf_{tag}_grind.json","w").write(pg.evaluate(FP)); open(f"/workspace/v3build/shots/perf_{tag}_gameplay.json","w").write(pg.evaluate(GP))
    for mode in ["night","day"]:
        if mode=="day": pg.evaluate(DAY)
        for v,js in V.items():
            pg.evaluate(js); time.sleep(2.5); pg.screenshot(path=f"/workspace/v3build/shots/perf_{tag}_{v}_{mode}.png")
            r=pg.evaluate(COUNT); agg={}
            if __import__('os').environ.get('DUMP') and v=='causeway' and mode=='night':
                info=pg.evaluate("""(()=>{const L=[];const fc=new Set((typeof FARCULL!=='undefined'?FARCULL:[]).map(f=>f.o));scene.traverse(o=>{ if(!(o.isMesh)||!o.visible) return; for(let a=o;a;a=a.parent) if(!a.visible) return; let ln=0; for(let a=o;a;a=a.parent){ if(a.userData.__ln){ln=a.userData.__ln;break;} }
                  const m=o.material; L.push([ln,o.geometry.type,o.geometry.attributes.position.count,m.type,!!m.map,m.map&&m.map.image?(m.map.image.width+'x'+m.map.image.height+(m.map.image instanceof HTMLCanvasElement?'c':'i')):'',m.transparent,m.opacity,m.blending,fc.has(o),o.parent===scene,m.vertexColors,o.frustumCulled]); }); return L;})()""")
                json.dump([[sec(x[0])[:40]]+x for x in info],open('/tmp/dump.json','w'))
            for k,c in r["C"].items():
                ln,kind=k.split("|"); s=sec(int(ln)) if int(ln) else "(no add-site)"; a=agg.setdefault(s+" ["+kind+"]",[0,0]); a[0]+=c; a[1]+=int(r["T"][k])
            out["views"][f"{v}_{mode}"]={"calls":r["calls"],"tris":r["tris"],"by":dict(sorted(agg.items(),key=lambda x:-x[1][0]))}
    try:
        pg.evaluate("new Promise(r=>{const s=document.createElement('script');s.src='perf/drawcalls/dc_probe.js';s.onload=r;document.head.appendChild(s);})")
        for v,lab in [("causeway","causeway_west_day"),("b98","b98_day")]:
            pg.evaluate(V[v]); time.sleep(2.5); r=pg.evaluate(f"(()=>{{const x=DC_PROBE.run('{lab}'); return JSON.stringify(DC_PROBE.last||x).slice(0,1500);}})()"); out["dcprobe_"+lab]=r
    except Exception as e: out["dcprobe_err"]=str(e)[:300]
    out["errors"]=errs[:8]; out["merge"]=pg.evaluate("window.__merge||null"); out["wp"]=pg.evaluate("window.WORLD_PERF?WORLD_PERF.stats:(typeof WORLD_PERF!='undefined'?WORLD_PERF.stats:null)"); br.close()
json.dump(out,open(f"/workspace/v3build/shots/perf_{tag}.json","w"),indent=1)
for v,d in out["views"].items(): print(v,d["calls"],d["tris"])
