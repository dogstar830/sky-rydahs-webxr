import bpy,numpy as np,sys
bpy.ops.wm.open_mainfile(filepath=sys.argv[-2]); o=bpy.data.objects[sys.argv[-1]]
co=np.array([v.co[:] for v in o.data.vertices]); print('DBG n',len(co),'legs',(co[:,2]<.75).sum(),'face',((co[:,2]>1.45)&(co[:,1]<-.05)).sum(), 'mods',[m.type for m in o.modifiers], 'hide',o.hide_render, [x.name for x in bpy.data.objects])
