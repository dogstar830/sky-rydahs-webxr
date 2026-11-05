#!/usr/bin/env python3
# Rider style opt3 perf gate (Rydah Optimizer). DESKTOP HEADLESS ONLY - no real headset; Quest-like = ?tier=quest, 1832x1920-ish per-eye NOT emulated.
# Usage (only after Forge posts 'ready for rebuild'):
#   bash /workspace/v3build/build_copy.sh /tmp/opt-rstyle.html
#   python3 /workspace/v3build/perf/render-style/rider_style_opt3_gate.py /tmp/opt-rstyle.html
# Takes /workspace/v3build/.testlock (refuses if held), runs ONE chromium, releases lock. No pkill, no suites.
import sys, os, json, time, shutil, subprocess, socket, http.server, threading, functools
from playwright.sync_api import sync_playwright
V3='/workspace/v3build'; LOCK=V3+'/.testlock'; SRC=sys.argv[1] if len(sys.argv)>1 else '/tmp/opt-rstyle.html'
assert os.path.realpath(SRC)!=os.path.realpath(V3+'/sky-rydahs-v3-ikki.html'), 'refusing real html'
PAGE='_rstyle_gate.html'; OUT=V3+'/perf/render-style/gate-results.json'; FRAMES=int(os.environ.get('FRAMES','240'))
VARIANTS={'base':'?tier=quest&pbr=1','opt3':'?tier=quest&pbr=1&riderstyle=opt3'}
PROBE=open(V3+'/perf/drawcalls/dc_probe.js').read()
MEASURE='''async(n)=>{ const r=renderer; await new Promise(res=>{let k=0;(function f(){ if(++k>=60) res(); else requestAnimationFrame(f);})();}); // warm
 const t=[]; let p=performance.now(); await new Promise(res=>{let k=0;(function f(){ const q=performance.now(); t.push(q-p); p=q; if(++k>=n) res(); else requestAnimationFrame(f);})();});
 t.sort((a,b)=>a-b); const med=t[t.length>>1], p95=t[Math.floor(t.length*.95)];
 r.info.autoReset=true; await new Promise(res=>requestAnimationFrame(()=>requestAnimationFrame(res)));
 let tex=0; try{ const s=new Set(); scene.traverse(o=>{ const ms=[].concat(o.material||[]); for(const m of ms) for(const k in m){ const v=m[k]; if(v&&v.isTexture&&!s.has(v)){ s.add(v); const im=v.image||{}; const w=(im.width||(v.mipmaps&&v.mipmaps[0]&&v.mipmaps[0].width)||0), h=(im.height||(v.mipmaps&&v.mipmaps[0]&&v.mipmaps[0].height)||0); const bpp=v.isCompressedTexture?1:4; tex+=w*h*bpp*(v.isCubeTexture?6:1)*1.33; } } }); }catch(e){}
 let dc=null; try{ dc=window.DC_PROBE?DC_PROBE.run('gate'):null; dc=dc?dc.length:null; }catch(e){}
 return {calls:r.info.render.calls, tris:r.info.render.triangles, programs:(r.info.programs||[]).length, textures:r.info.memory.textures, texMBest:+(tex/1048576).toFixed(2), dcProbeRows:dc, frameMsMed:+med.toFixed(3), frameMsP95:+p95.toFixed(3), errors:window.__gateErr||[]}; }'''
def free_port():
    s=socket.socket(); s.bind(('127.0.0.1',0)); p=s.getsockname()[1]; s.close(); return p
def main():
    try: fd=os.open(LOCK,os.O_CREAT|os.O_EXCL|os.O_WRONLY)
    except FileExistsError: print('LOCK HELD:',open(LOCK).read().strip()); sys.exit(9)
    os.write(fd,f'Rydah Optimizer rider_style_opt3_gate pid={os.getpid()} {time.strftime("%H:%M")} CDT\n'.encode()); os.close(fd)
    srv=None
    try:
        shutil.copy(SRC,V3+'/'+PAGE); port=free_port()
        H=functools.partial(http.server.SimpleHTTPRequestHandler,directory=V3); H.log_message=lambda *a:None
        srv=http.server.ThreadingHTTPServer(('127.0.0.1',port),H); threading.Thread(target=srv.serve_forever,daemon=True).start()
        res={'label':'desktop headless Chromium (SwiftShader/ANGLE), Quest-like ?tier=quest; NO real headset','frames':FRAMES,'src':SRC,'when':time.strftime('%Y-%m-%d %H:%M CDT')}
        with sync_playwright() as pw:
            b=pw.chromium.launch(args=['--use-gl=angle','--enable-unsafe-swiftshader','--ignore-gpu-blocklist'])
            for name,q in VARIANTS.items():
                pg=b.new_page(viewport={'width':1920,'height':1080},device_scale_factor=1.0)
                pg.add_init_script('window.__gateErr=[];addEventListener("error",e=>__gateErr.push(String(e.message)))')
                pg.goto(f'http://127.0.0.1:{port}/{PAGE}{q}',wait_until='load',timeout=120000)
                pg.wait_for_function("typeof renderer!=='undefined'&&typeof scene!=='undefined'",timeout=120000); pg.wait_for_timeout(15000)  # GLB/KTX2 loads
                pg.evaluate(PROBE); res[name]=pg.evaluate(MEASURE,FRAMES); print(name,json.dumps(res[name])); pg.close()
            b.close()
        B,O=res['base'],res['opt3']
        chk={'draws_+0':O['calls']-B['calls']<=0,'programs_<=+2':O['programs']-B['programs']<=2,
             'frame_ms_<=+5%':O['frameMsMed']<=B['frameMsMed']*1.05,'texmem_<=+2MB':O['texMBest']-B['texMBest']<=2.0,'no_new_errors':len(O['errors'])<=len(B['errors'])}
        res['checks']=chk; res['PASS']=all(chk.values()); json.dump(res,open(OUT,'w'),indent=1); print('GATE','PASS' if res['PASS'] else 'FAIL',chk,'->',OUT)
    finally:
        if srv: srv.shutdown()
        try: os.remove(V3+'/'+PAGE)
        except OSError: pass
        os.remove(LOCK)
if __name__=='__main__': main()
