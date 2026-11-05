# Palma Builder handover: dump world data (colliders, WORLD_GROUND grid, WALL_PANELS, WALL_KICKS, KICK_ROUTES, PALMA layout) to JSON.
# usage: bash /workspace/v3build/build_copy.sh /tmp/x.html && python3 dump_world_json.py file:///tmp/x.html <outdir>   (hold .testlock)
import sys,time,json,os
from playwright.sync_api import sync_playwright
U,O=sys.argv[1],sys.argv[2]; os.makedirs(O,exist_ok=True)
JS=r'''(()=>{ const r=v=>Math.round(v*1000)/1000; const clean=o=>JSON.parse(JSON.stringify(o,(k,v)=>typeof v==='number'?r(v):(v&&v.isObject3D?undefined:v)));
 const out={};
 try{ out.colliders=clean((typeof colliders!=='undefined'?colliders:[]).map(c=>{const o={}; for(const k in c){const v=c[k]; if(typeof v==='number'||typeof v==='string'||typeof v==='boolean') o[k]=v;} return o;})); }catch(e){out.colliders_err=''+e}
 try{ out.palma=clean(PALMA); }catch(e){out.palma_err=''+e}
 for(const k of ['WALL_PANELS','WALL_KICKS','KICK_ROUTES','KICK_UNREACHABLE','KICK_BRIDGE']) try{ out[k]=clean(window[k]); }catch(e){out[k+'_err']=''+e}
 try{ const g=[]; const S=4; for(let x=-260;x<=340;x+=S) for(let z=-340;z<=220;z+=S){ const h=WORLD_GROUND(x,z,50); if(h) g.push([x,z,r(h.y),h.surf]); } out.ground={step:S,yHint:50,fields:['x','z','y','surf'],samples:g}; }catch(e){out.ground_err=''+e}
 return out; })()'''
with sync_playwright() as p:
    br=p.chromium.launch(args=["--use-gl=swiftshader","--enable-webgl","--ignore-gpu-blocklist","--allow-file-access-from-files"]); pg=br.new_page(viewport={"width":1280,"height":720})
    pg.goto(U,timeout=180000)
    for i in range(120):
        if pg.evaluate("typeof WORLD_GROUND!='undefined'&&!!window.WALL_KICKS&&!!window.KICK_ROUTES"): break
        time.sleep(1)
    time.sleep(3); d=pg.evaluate(JS); br.close()
for k,v in d.items():
    json.dump(v,open(f"{O}/{k}.json","w"),separators=(',',':')); print(k, len(v) if hasattr(v,'__len__') else v)
