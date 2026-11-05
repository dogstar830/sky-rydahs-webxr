# Rydah Forge: per-crew FX colour check. FX pixels = |shot - base| > 60 (base = same view, FX cleared+paused). Core-edge band = 70-95th pct of brightness among FX pixels.
import numpy as np, colorsys, json, sys
MODE=sys.argv[1] if len(sys.argv)>1 else 'final'
from PIL import Image
H="/workspace/v3build/shots/hero/"; PAL={"codee":0xffb000,"karasu":0xff1020,"static":0xa040ff,"anubis":0x00d6b4,"forest":0x12a845,"behemoth":0xff5a00,"genesis":0xff2bd6,"ttt":0xd0602a,"volt":0xff3fa8,"rustclaw":0xff6a10}
ALT={"static":0x5ff4ff,"volt":0xfff23a,"anubis":0xffd889,"genesis":0xffd36a,"ttt":0xb8bcc4,"forest":0xe8ffe8,"codee":0xffd84a}
def hue(h): return colorsys.rgb_to_hsv(((h>>16)&255)/255,((h>>8)&255)/255,(h&255)/255)[0]*360
rows=[]
for c,h in PAL.items():
    import os
    if not os.path.exists(f"/workspace/v3build/perf/forge/cfx_base_combat_fx_{c}.png"): continue
    im=np.asarray(Image.open(H+f"combat_fx_{c}.png").convert("RGB")).astype(float)/255
    base=np.asarray(Image.open(f"/workspace/v3build/perf/forge/cfx_base_combat_fx_{c}.png").convert("RGB")).astype(float)/255
    dl=im-base; m=(dl.max(2)>.22); Hh,Ww=m.shape; roi=np.zeros_like(m); roi[int(Hh*.38):int(Hh*.9),int(Ww*.3):int(Ww*.95)]=True; m&=roi  # ROI = FX zone (excludes window flicker on facades + HUD)
    px=np.clip(dl[m],0,1) if MODE=='delta' else im[m]; v=px.max(1); lo,hi=np.percentile(v,70),np.percentile(v,95); band=px[(v>=lo)&(v<=hi)]
    mx=band.max(1); mn=band.min(1); sat=np.where(mx>0,(mx-mn)/np.maximum(mx,1e-6),0)
    hs=np.array([colorsys.rgb_to_hsv(*p)[0] for p in band[sat>.25][:20000]])*2*np.pi
    mh=(np.degrees(np.arctan2(np.sin(hs).mean(),np.cos(hs).mean()))%360) if len(hs) else float('nan')
    # dominant hue (histogram peak) is more robust than mean when 2-colour palettes mix
    hist,edges=np.histogram(np.degrees(hs)%360,bins=36,range=(0,360)); peak=edges[hist.argmax()]+5 if len(hs) else float('nan')
    tgt=hue(h); dd=lambda a:min(abs(a-tgt),360-abs(a-tgt)); alt=hue(ALT[c]) if c in ALT else None
    err=dd(peak); erra=min(abs(peak-alt),360-abs(peak-alt)) if alt is not None else 999
    ok=(min(err,erra)<=10) and np.median(sat)>=.6
    rows.append(dict(crew=c,target=round(tgt),alt=round(alt) if alt is not None else None,peak=round(peak),mean=round(mh),sat=round(float(np.median(sat)),2),n=int(m.sum()),err=round(min(err,erra)),PASS=bool(ok)))
for r in rows: print(r)
json.dump(rows,open("/workspace/v3build/perf/forge/combat-fx-hue-"+MODE+".json","w"),indent=1)
