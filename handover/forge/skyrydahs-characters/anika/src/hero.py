# Hero render (Blender Cycles): model panel 1440x1620 + ref crop panel -> 2880x1620 (= 1920x1080 @ dsf 1.5)
import bpy,sys,math
from mathutils import Vector
a=sys.argv[sys.argv.index('--')+1:]; bl,ob,outp,view=a[0],a[1],a[2],a[3]
bpy.ops.wm.open_mainfile(filepath=bl); sc=bpy.context.scene
for o in list(bpy.data.objects):
    if o.name!=ob: bpy.data.objects.remove(o)
o=bpy.data.objects[ob]; H=max(v.co.z for v in o.data.vertices)
# wheel glow 0xffd700 from the _WC wheel-centre attribute (same verts the runtime shader lights)
m=o.data.materials[0]; nt=m.node_tree; b=nt.nodes['Principled BSDF']
at=nt.nodes.new('ShaderNodeAttribute'); at.attribute_name='_WC'; vl=nt.nodes.new('ShaderNodeVectorMath'); vl.operation='LENGTH'
gt=nt.nodes.new('ShaderNodeMath'); gt.operation='GREATER_THAN'; gt.inputs[1].default_value=1e-4
mu=nt.nodes.new('ShaderNodeMath'); mu.operation='MULTIPLY'; mu.inputs[1].default_value=2.5
nt.links.new(at.outputs['Vector'],vl.inputs[0]); nt.links.new(vl.outputs['Value'],gt.inputs[0]); nt.links.new(gt.outputs[0],mu.inputs[0])
b.inputs['Emission Color'].default_value=(1,.68,0,1); nt.links.new(mu.outputs[0],b.inputs['Emission Strength'])
sc.render.engine='CYCLES'; sc.cycles.samples=160; sc.cycles.use_denoising=True; sc.cycles.device='CPU'
sc.render.resolution_x=1440; sc.render.resolution_y=1620; sc.view_settings.view_transform='AgX'; sc.view_settings.look='AgX - Medium High Contrast'
w=bpy.data.worlds.new('w'); sc.world=w; w.use_nodes=True; bg=w.node_tree.nodes['Background']; bg.inputs[0].default_value=(.42,.47,.55,1); bg.inputs[1].default_value=.55
bpy.ops.mesh.primitive_plane_add(size=20); fl=bpy.context.object; fm=bpy.data.materials.new('floor'); fm.use_nodes=True; fb=fm.node_tree.nodes['Principled BSDF']; fb.inputs['Base Color'].default_value=(.36,.34,.32,1); fb.inputs['Roughness'].default_value=.55; fl.data.materials.append(fm)
def light(nm,loc,en,size,col=(1,1,1)):
    L=bpy.data.lights.new(nm,'AREA'); L.energy=en; L.size=size; L.color=col; lo=bpy.data.objects.new(nm,L); sc.collection.objects.link(lo); lo.location=loc
    d=Vector((0,0,H*.55))-Vector(loc); lo.rotation_euler=d.to_track_quat('-Z','Y').to_euler()
light('key',(-2.2,-3.2,3.0),900,2.2,(1,.96,.9)); light('fill',(2.8,-2.6,1.6),260,3,(.85,.9,1)); light('rim',(1.2,3.2,2.8),700,1.5,(1,.92,.85)); light('rimL',(-2.4,2.6,2.2),400,1.5,(.9,.85,1))
cam=bpy.data.objects.new('cam',bpy.data.cameras.new('cam')); sc.collection.objects.link(cam); sc.camera=cam; cam.data.lens=60
ang=math.radians(0 if view=='front' else 35); dist=H*2.75
cam.location=(math.sin(ang)*dist,-math.cos(ang)*dist,H*.52); t=Vector((0,0,H*.5)); cam.rotation_euler=(t-cam.location).to_track_quat('-Z','Y').to_euler()
sc.render.filepath=outp; bpy.ops.render.render(write_still=True); print('HERO',outp)
