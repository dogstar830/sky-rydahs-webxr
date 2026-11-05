#!/usr/bin/env python3
"""skate_floor_probe.py - per-foot wheel-to-floor gap for the player and crew NPCs (Rydah Rigger, 2026-10-30).

Fixes vs /tmp/skv2_measure.py:
  * CPU skinning with DENORMALISED weights (r128 getX returns raw u8/u16 for normalized skinWeight ->
    boneTransform blows up: that was the CaaliG_LOD1 -1411 mm / LOD0 -208 mm). Weights also renormalised to sum 1.
  * Only meshes that actually render: every ancestor visible (THREE.LOD hides inactive level groups, not the mesh).
  * Feet split per VERTEX by dominant skin bone (Left/Right foot/leg/toe, foot.L/foot.R), fallback rider-local x (+X = rider's left).
  * Skate meshes = material cache key 'crew-at-skate*' or name /ATSkate|at_skate|Skate/. If a rider has none, the
    lowest per-side BODY vertex is reported (baked skate), flagged skate_source='body'.
  * Ground = what the game uses: player -> RIDE_GROUND.groundY (ride_ground follows WORLD_GROUND); NPC -> rider origin y
    (NPC holders are placed at y=0, no ground follow). The rendered surface top WORLD_GROUND(x,z,y+0.3).y is reported too.
Read-only: no state changes except camera. Runs no build and no suites by itself.

Usage (server must serve /workspace, e.g. the integrator's :8765):
  python3 tests/skate_floor_probe.py --port 8765 --html sky-rydahs-v3-ikki.html [--extra '&atskate=legacy'] [--out /tmp/skate_floor.json]
"""
import argparse, json, sys, time
from playwright.sync_api import sync_playwright

ap = argparse.ArgumentParser()
ap.add_argument('--port', type=int, default=8765)
ap.add_argument('--path', default='v3build')            # dir of the html under the server root
ap.add_argument('--html', default='sky-rydahs-v3-ikki.html')
ap.add_argument('--extra', default='')
ap.add_argument('--out', default='/tmp/skate_floor_probe.json')
ap.add_argument('--feet-shot', default='')   # optional png of the player's feet (side view)
ap.add_argument('--tol-mm', type=float, default=3.0)
a = ap.parse_args()
URL = f"http://localhost:{a.port}/{a.path}/{a.html}?chars=/skyrydahs-characters/&tier=hd{a.extra}"

MEASURE = r"""(o)=>{ o.updateMatrixWorld(true);
 const shown=m=>{ for(let q=m;q&&q!==o.parent;q=q.parent){ if(q===o) return true; if(!q.visible) return false; } return true; };   // inside the rider only: distance-culled NPC holders still measured, inactive LOD levels skipped
 const isSk=m=>{ const k=m.material&&m.material.customProgramCacheKey?String(m.material.customProgramCacheKey()):''; return /^crew-at-skate/.test(k)||/ATSkate|at_skate|Skate/.test(m.name)||/at_skate/i.test((m.material&&m.material.name)||''); };
 const sideOf=n=>/Left|\.L$|_L$|^L_|foot\.L|thigh\.L|shin\.L/i.test(n)?'L':/Right|\.R$|_R$|^R_|foot\.R|thigh\.R|shin\.R/i.test(n)?'R':null;
 const inv=new THREE.Matrix4().copy(o.matrixWorld).invert(), v=new THREE.Vector3(), t=new THREE.Vector3(), acc=new THREE.Vector3(), lv=new THREE.Vector3(), M=new THREE.Matrix4();
 const res={skate:{L:1e9,R:1e9},body:{L:1e9,R:1e9},skate_meshes:[],body_meshes:[]};
 o.traverse(m=>{ if(!m.isMesh||!shown(m)||!m.geometry.attributes.position) return; const g=m.geometry, P=g.attributes.position, s=isSk(m), bucket=s?res.skate:res.body;
  (s?res.skate_meshes:res.body_meshes).push(m.name||m.type);
  let SI=null, SW=null, div=1, bones=null; if(m.isSkinnedMesh){ m.skeleton.update(); SI=g.attributes.skinIndex; SW=g.attributes.skinWeight; const ar=SW.isInterleavedBufferAttribute?SW.data.array:SW.array;
    div=SW.normalized&&ar instanceof Uint8Array?255:SW.normalized&&ar instanceof Uint16Array?65535:1; bones=m.skeleton.bones; }
  for(let i=0;i<P.count;i++){ v.fromBufferAttribute(P,i); let side=null;
   if(m.isSkinnedMesh){ t.copy(v).applyMatrix4(m.bindMatrix); acc.set(0,0,0); let ws=0, bj=-1, bw=-1;
     for(let c=0;c<4;c++){ const w=SW.getComponent?SW.getComponent(i,c)/div:[SW.getX(i),SW.getY(i),SW.getZ(i),SW.getW(i)][c]/div; if(w<=0) continue; const j=[SI.getX(i),SI.getY(i),SI.getZ(i),SI.getW(i)][c];
       M.multiplyMatrices(bones[j].matrixWorld,m.skeleton.boneInverses[j]); acc.addScaledVector(lv.copy(t).applyMatrix4(M),w); ws+=w; if(w>bw){bw=w;bj=j;} }
     if(ws<=0) continue; v.copy(acc).multiplyScalar(1/ws).applyMatrix4(m.bindMatrixInverse); side=bj>=0?sideOf(bones[bj].name):null; }
   v.applyMatrix4(m.matrixWorld); if(!side){ lv.copy(v).applyMatrix4(inv); side=lv.x>=0?'L':'R'; }
   if(v.y<bucket[side]) bucket[side]=v.y; } });
 const p=o.getWorldPosition(new THREE.Vector3()); let rendered=null; try{ const r=WORLD_GROUND(p.x,p.z,p.y+0.3); rendered=r?r.y:null; }catch(e){}
 return {pos:[p.x,p.y,p.z],rendered_ground:rendered,...res}; }"""

def frames(pg, n):
    return pg.evaluate(f"new Promise(r=>{{let n=0;function f(){{if(++n<{n})requestAnimationFrame(f);else r(n)}}requestAnimationFrame(f)}})")

out = {"url": URL, "riders": {}}; errs = []; bad = []
with sync_playwright() as p:
    b = p.chromium.launch(args=["--use-gl=angle", "--use-angle=swiftshader", "--enable-unsafe-swiftshader"])
    pg = b.new_page(viewport={"width": 1280, "height": 720}); pg.set_default_timeout(300000)
    pg.on("pageerror", lambda e: errs.append("pageerror: " + str(e)))
    pg.on("console", lambda m: errs.append("console." + m.type + ": " + m.text[:300]) if m.type == "error" else None)
    pg.on("response", lambda r: bad.append(f"{r.status} {r.url}") if r.status >= 400 else None)
    pg.goto(URL, timeout=300000)
    for _ in range(240):
        if pg.evaluate("typeof RIDERS!='undefined'&&RIDERS.ready"): break
        time.sleep(1)
    time.sleep(3)
    for _ in range(6):
        if pg.evaluate("State.mode") == "ride": break
        pg.keyboard.press("Enter"); time.sleep(2)
    pg.evaluate("Ride.speed=0")
    frames(pg, 70)
    out["draws"] = pg.evaluate("new Promise(r=>{const I=renderer.info;I.autoReset=false;I.reset();requestAnimationFrame(()=>requestAnimationFrame(()=>{const c={calls:I.render.calls,triangles:I.render.triangles,programs:(I.programs||[]).length};I.autoReset=true;r(c)}))})")   # one full frame, default game camera
    out["skate_fit"] = pg.evaluate("(()=>{const o={};const f=(k,r)=>{if(r&&r.userData&&r.userData.atSkateFit)o[k]=r.userData.atSkateFit};f('player',RIDERS.player);(RIDERS.npcs||[]).forEach((n,i)=>f('npc'+i,n.r));if(RIDERS.ikkiNpc)f('ikkiNpc',RIDERS.ikkiNpc.r);return o})()")
    out["skate"] = pg.evaluate("({scale:typeof SR_SKATE_SCALE!=='undefined'?SR_SKATE_SCALE:null,lift:typeof SR_SKATE_LIFT!=='undefined'?SR_SKATE_LIFT:null,sideDy:typeof SR_SKATE_SIDE_DY!=='undefined'?SR_SKATE_SIDE_DY:null,module:SR_SKATE.url(),player_ground:window.RIDE_GROUND?RIDE_GROUND.groundY:null})")
    targets = [("player", "RIDERS.player", "player")]
    n = pg.evaluate("(RIDERS.npcs||[]).length")
    for i in range(n):
        if pg.evaluate(f"!!(RIDERS.npcs[{i}]&&(RIDERS.npcs[{i}].r||RIDERS.npcs[{i}].holder))"):
            targets.append((f"npc{i}", f"(RIDERS.npcs[{i}].r||RIDERS.npcs[{i}].holder)", "npc"))
    for name, expr, kind in targets:
        R = pg.evaluate(f"(()=>{{const o={expr};return o&&o.isObject3D?({MEASURE})(o):null}})()")
        if not R: out["riders"][name] = None; continue
        src = "skate" if R["skate_meshes"] else "body"
        low = R[src]
        game_ground = out["skate"]["player_ground"] if kind == "player" and out["skate"]["player_ground"] is not None else R["pos"][1]
        rg = R["rendered_ground"]
        rec = {"kind": kind, "pos": [round(x, 4) for x in R["pos"]], "skate_source": src, "skate_meshes": R["skate_meshes"],
               "game_ground_y": round(game_ground, 4), "rendered_ground_y": rg,
               "lowL_y": round(low["L"], 5), "lowR_y": round(low["R"], 5),
               "gapL_mm": round((low["L"] - game_ground) * 1000, 2), "gapR_mm": round((low["R"] - game_ground) * 1000, 2),
               "gapL_vs_rendered_mm": None if rg is None else round((low["L"] - rg) * 1000, 2),
               "gapR_vs_rendered_mm": None if rg is None else round((low["R"] - rg) * 1000, 2)}
        if src == "skate":
            rec["boot_minus_wheel_mm"] = {s: round((R["body"][s] - R["skate"][s]) * 1000, 1) for s in "LR" if R["body"][s] < 1e8}
        rec["ok"] = all(abs(rec[k]) <= a.tol_mm for k in ("gapL_mm", "gapR_mm"))
        out["riders"][name] = rec
    if a.feet_shot:
        pg.evaluate("(()=>{const o=RIDERS.player;window.__camHook=()=>{const p=o.getWorldPosition(new THREE.Vector3());const e=new THREE.Euler().setFromQuaternion(o.getWorldQuaternion(new THREE.Quaternion()),'YXZ');const y=e.y+1.5708;camera.position.set(p.x+Math.sin(y)*1.1,p.y+.2,p.z+Math.cos(y)*1.1);camera.lookAt(p.x,p.y+.1,p.z)}})()")
        frames(pg, 10); pg.screenshot(path=a.feet_shot); pg.evaluate("window.__camHook=null")
    out["errs"] = errs[:40]; out["http_bad"] = bad[:40]
    b.close()
json.dump(out, open(a.out, "w"), indent=1)
for k, r in out["riders"].items():
    if r: print(f"{k:8s} {r['skate_source']:5s} L {r['gapL_mm']:+7.2f} mm  R {r['gapR_mm']:+7.2f} mm  (vs rendered top: L {r['gapL_vs_rendered_mm']} R {r['gapR_vs_rendered_mm']})  {'OK' if r['ok'] else 'CHECK'}")
print("errors:", len(out["errs"]), "http>=400:", len(out["http_bad"]), "->", a.out)
