# Import Meshy GLB, normalise (height H, grounded, centred), report profile, quick textured workbench renders.
import bpy,sys,math,numpy as np
from mathutils import Vector
n,H=sys.argv[-2],float(sys.argv[-1]); G='/workspace/forge_kit/gr8/'
bpy.ops.wm.read_factory_settings(use_empty=True); bpy.ops.import_scene.gltf(filepath=f'/home/box/Downloads/gr8yzone/{n}-meshy.glb')
hi=[o for o in bpy.data.objects if o.type=='MESH'][0]; hi.name='HI'
bpy.context.view_layer.objects.active=hi; hi.select_set(True); bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
co=np.zeros(len(hi.data.vertices)*3); hi.data.vertices.foreach_get('co',co); co=co.reshape(-1,3)
mn,mx=co.min(0),co.max(0); s=H/(mx[2]-mn[2]); c=np.array([(mn[0]+mx[0])/2,(mn[1]+mx[1])/2,mn[2]])
co=(co-c)*s; hi.data.vertices.foreach_set('co',co.ravel()); hi.data.update()
print('SCALE',s,'bbox',co.min(0).round(3),co.max(0).round(3))
# width profile per 2cm band
for z in np.arange(0,H,0.04):
    b=co[(co[:,2]>=z)&(co[:,2]<z+0.04)]
    if len(b): 
        L=b[b[:,0]>0.0]; 
        print('Z %.2f w %.3f..%.3f y %.3f..%.3f n %d'%(z,b[:,0].min(),b[:,0].max(),b[:,1].min(),b[:,1].max(),len(b)))
bpy.ops.wm.save_as_mainfile(filepath=G+n+'_hi.blend')
sc=bpy.context.scene; sc.render.engine='BLENDER_WORKBENCH'; sc.display.shading.light='FLAT'; sc.display.shading.color_type='TEXTURE'
sc.render.resolution_x=700; sc.render.resolution_y=1200
cam=bpy.data.objects.new('cam',bpy.data.cameras.new('cam')); sc.collection.objects.link(cam); sc.camera=cam; cam.data.type='ORTHO'; cam.data.ortho_scale=H*1.05
for nm,pos,rot in (('front',(0,-5,H/2),(90,0,0)),('back',(0,5,H/2),(90,0,180)),('side',(5,0,H/2),(90,0,90))):
    cam.location=pos; cam.rotation_euler=[math.radians(a) for a in rot]; sc.render.filepath=G+f'{n}_{nm}.png'; bpy.ops.render.render(write_still=True)
