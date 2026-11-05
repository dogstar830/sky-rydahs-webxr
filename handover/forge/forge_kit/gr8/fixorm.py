import bpy,sys,numpy as np
from PIL import Image as PI
bl=sys.argv[-1]; bpy.ops.wm.open_mainfile(filepath=bl)
for im in bpy.data.images:
    if not im.name.endswith('_orm'): continue
    Rr=im.size[0]; cw,ch=Rr//4,Rr//2; a=np.empty(Rr*Rr*4,dtype=np.float32); im.pixels.foreach_get(a); a=a.reshape(Rr,Rr,4)
    s=np.array(PI.open('/workspace/skyrydahs-characters/shared/at-skate/at-skate-meshy-1k-mr.png').convert('RGBA').resize((cw,ch)),dtype=np.float32)[::-1]/255.
    s[...,0]=1.; s[...,1]=np.maximum(s[...,1],.4); s[...,2]=np.minimum(s[...,2],.5); a[Rr-ch:Rr,Rr-cw:Rr]=s
    im.pixels.foreach_set(a.ravel()); im.filepath_raw='/workspace/forge_kit/gr8/tex/'+im.name+'.png'; im.file_format='PNG'; im.save(); im.pack(); print('FIX',im.name)
bpy.ops.wm.save_mainfile()
