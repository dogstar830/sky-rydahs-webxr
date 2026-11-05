# Hero render of a rigged GLB in bind pose (LOD0) + runtime v2 skate at 1.25x about its ankle pivot, pivot on each Foot joint
import bpy,sys,math
from mathutils import Vector,Matrix
a=sys.argv[sys.argv.index('--')+1:]; glb,lod,outp,view=a[:4]; SK='/workspace/skyrydahs-characters/wardrobe/skates/at-skate-meshy.v2.glb'
bpy.ops.wm.read_factory_settings(use_empty=True); sc=bpy.context.scene
bpy.ops.import_scene.gltf(filepath=glb)
arm=[o for o in bpy.data.objects if o.type=='ARMATURE'][0]
for o in list(bpy.data.objects):
    if o.type=='MESH' and o.name!=lod: bpy.data.objects.remove(o)
o=bpy.data.objects[lod]
dg=bpy.context.evaluated_depsgraph_get(); H=max((o.matrix_world@v.co).z for v in o.evaluated_get(dg).data.vertices)
feet=[arm.matrix_world@arm.data.bones[n].head_local for n in ('mixamorig:LeftFoot','mixamorig:RightFoot')]
bpy.ops.wm.ply_import(filepath=a[4]); skp=bpy.context.selected_objects[0]; sm=bpy.data.materials.new('sk'); sm.use_nodes=True; bs=sm.node_tree.nodes['Principled BSDF']; bs.inputs['Base Color'].default_value=(.03,.03,.035,1); bs.inputs['Metallic'].default_value=.6; bs.inputs['Roughness'].default_value=.4; skp.data.materials.append(sm)
for poly in skp.data.polygons: poly.use_smooth=True
for m in bpy.data.materials:
    if m.node_tree:
        for n in m.node_tree.nodes:
            if n.type in ('VERTEX_COLOR','ATTRIBUTE') :
                for l in list(n.outputs[0].links)+list(n.outputs[1].links if len(n.outputs)>1 else []): m.node_tree.links.remove(l)
sc.render.engine='CYCLES'; sc.cycles.samples=128; sc.cycles.use_denoising=True; sc.cycles.device='CPU'
sc.render.resolution_x=1440; sc.render.resolution_y=1620; sc.view_settings.view_transform='AgX'; sc.view_settings.look='AgX - Medium High Contrast'
w=bpy.data.worlds.new('w'); sc.world=w; w.use_nodes=True; bg=w.node_tree.nodes['Background']; bg.inputs[0].default_value=(.42,.47,.55,1); bg.inputs[1].default_value=.55
zmin=min((x.matrix_world@v.co).z for x in bpy.data.objects if x.type=='MESH' and x.name!=lod for v in x.data.vertices)
bpy.ops.mesh.primitive_plane_add(size=20,location=(0,0,zmin)); fl=bpy.context.object; fm=bpy.data.materials.new('floor'); fm.use_nodes=True; fb=fm.node_tree.nodes['Principled BSDF']; fb.inputs['Base Color'].default_value=(.36,.34,.32,1); fb.inputs['Roughness'].default_value=.55; fl.data.materials.append(fm)
def light(nm,loc,en,size,col=(1,1,1)):
    L=bpy.data.lights.new(nm,'AREA'); L.energy=en; L.size=size; L.color=col; lo=bpy.data.objects.new(nm,L); sc.collection.objects.link(lo); lo.location=loc
    d=Vector((0,0,H*.55))-Vector(loc); lo.rotation_euler=d.to_track_quat('-Z','Y').to_euler()
light('key',(-2.2,-3.2,3.0),900,2.2,(1,.96,.9)); light('fill',(2.8,-2.6,1.6),260,3,(.85,.9,1)); light('rim',(1.2,3.2,2.8),700,1.5,(1,.92,.85)); light('rimL',(-2.4,2.6,2.2),400,1.5,(.9,.85,1))
cam=bpy.data.objects.new('cam',bpy.data.cameras.new('cam')); sc.collection.objects.link(cam); sc.camera=cam; cam.data.lens=60
# glTF front faces +Z -> Blender -Y
ang=math.radians(0 if view=='front' else 35); dist=(H-zmin)*2.75; mid=(H+zmin)/2
cam.location=(math.sin(ang)*dist,-math.cos(ang)*dist,mid+.02); cam.rotation_euler=(Vector((0,0,mid))-cam.location).to_track_quat('-Z','Y').to_euler()
sc.render.filepath=outp; bpy.ops.render.render(write_still=True); print('HERO',outp)
