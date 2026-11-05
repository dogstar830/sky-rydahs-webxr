# Palma Builder: bake the Portside district env cube (day + night) from the DEFAULT build at (0,6,22) (plaza edge, outside the holo tower), 128^2/face -> assets/pbr/env_portside_{day,night}.png (6x1 strip px,nx,py,ny,pz,nz)
import sys,time,base64
from playwright.sync_api import sync_playwright
H=sys.argv[1] if len(sys.argv)>1 else 'sky-rydahs-v3-ikki.html'
B=f"http://localhost:8765/v3build/{H}?chars=/skyrydahs-characters/&nofx&seed=1"
DAY=open('/workspace/v3build/dcsplit2.py').read().split('DAY="""')[1].split('"""')[0]
CAP=r"""(()=>{ const S=128, rt=new THREE.WebGLRenderTarget(S,S); const cam=new THREE.PerspectiveCamera(90,1,.5,2000); cam.position.set(0,6,22);
 const D=[[1,0,0,0,-1,0],[-1,0,0,0,-1,0],[0,1,0,0,0,1],[0,-1,0,0,0,-1],[0,0,1,0,-1,0],[0,0,-1,0,-1,0]];
 const hide=[]; if(typeof Ride!=='undefined'&&Ride.group) hide.push(Ride.group); hide.forEach(o=>o.visible=false);
 const cv=document.createElement('canvas'); cv.width=S*6; cv.height=S; const x=cv.getContext('2d'), px=new Uint8Array(S*S*4); const prev=renderer.getRenderTarget();
 for(let f=0;f<6;f++){ const d=D[f]; cam.up.set(d[3],d[4],d[5]); cam.lookAt(d[0],6+d[1],22+d[2]); cam.updateMatrixWorld(true); renderer.setRenderTarget(rt); renderer.clear(); renderer.render(scene,cam); renderer.readRenderTargetPixels(rt,0,0,S,S,px);
   const id=x.createImageData(S,S); for(let r=0;r<S;r++) id.data.set(px.subarray((S-1-r)*S*4,(S-r)*S*4),r*S*4); for(let k=3;k<id.data.length;k+=4) id.data[k]=255; x.putImageData(id,f*S,0); }
 renderer.setRenderTarget(prev); hide.forEach(o=>o.visible=true); rt.dispose(); return cv.toDataURL('image/png'); })()"""
with sync_playwright() as p:
    br=p.chromium.launch(args=["--use-gl=swiftshader","--enable-webgl","--ignore-gpu-blocklist"]); pg=br.new_page(viewport={"width":800,"height":600})
    pg.goto(B,timeout=180000); t0=time.time()
    while time.time()-t0<200:
        try:
            if pg.evaluate("typeof RIDERS!='undefined'&&RIDERS.ready&&GRIND.world"): break
        except Exception: pass
        time.sleep(.5)
    time.sleep(6); pg.keyboard.press("Enter"); time.sleep(2)
    for tag in ("night","day"):
        if tag=="day": pg.evaluate(DAY); time.sleep(2)
        d=pg.evaluate(CAP); open(f'/workspace/v3build/assets/pbr/env_portside_{tag}.png','wb').write(base64.b64decode(d.split(',')[1])); print(tag,'ok')
    br.close()
