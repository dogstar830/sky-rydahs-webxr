# usage: blender -b --python export.py -- LODS_BLEND OUT_RAW 'SRC:DST,SRC:DST,...' [decimate SRC:DST:TRIS]
import bpy,sys
a=sys.argv[sys.argv.index('--')+1:]; bl,outp,mp=a[0],a[1],a[2]; dec=a[3] if len(a)>3 else ''
bpy.ops.wm.open_mainfile(filepath=bl)
pairs=[p.split(':') for p in mp.split(',')]; keep=[]
if dec:
    s,d,t=dec.split(':'); o=bpy.data.objects[s]; c=o.copy(); c.data=o.data.copy(); bpy.context.collection.objects.link(c); c.name='__dec'
    bpy.ops.object.select_all(action='DESELECT'); c.select_set(True); bpy.context.view_layer.objects.active=c
    m=c.modifiers.new('d','DECIMATE'); m.ratio=int(t)/sum(len(p.vertices)-2 for p in c.data.polygons); m.use_collapse_triangulate=True; bpy.ops.object.modifier_apply(modifier='d')
    pairs.append(['__dec',d])
names={s for s,_ in pairs}
for o in list(bpy.data.objects):
    if o.name not in names: bpy.data.objects.remove(o)
for s,d in pairs:
    o=bpy.data.objects[s]
    if s!=d and d in bpy.data.objects: bpy.data.objects[d].name='__tmp'
for s,d in pairs:
    o=bpy.data.objects.get(s) or bpy.data.objects.get('__tmp'); o.name=d; o.data.name=d; keep.append(o)
    print('OUT',d,sum(len(p.vertices)-2 for p in o.data.polygons))
bpy.ops.object.select_all(action='DESELECT')
for o in keep: o.select_set(True)
kw=dict(filepath=outp,export_format='GLB',use_selection=True,export_animations=False,export_morph=False,export_image_format='WEBP',export_image_quality=88,export_yup=True,export_attributes=True,export_apply=True)
try: bpy.ops.export_scene.gltf(**kw,export_vertex_color='ACTIVE')
except TypeError: bpy.ops.export_scene.gltf(**kw)
import os; print('EXPORT',outp,os.path.getsize(outp))
