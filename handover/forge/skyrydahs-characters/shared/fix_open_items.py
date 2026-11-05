import re
R='/workspace/skyrydahs-characters/'
def rep(crew, start, newcode):
    p=R+crew+'/src/build_rider.py'; s=open(p).read()
    a=s.index(start); b=s.index("\nmodule(",a+5); s=s[:a]+newcode+s[b+1:]; open(p,'w').write(s)
rep('sleeping-forest',"module('accessory','coattails')",'''module('accessory','coattails')
# SIGNATURE (v2): flared cone-shell longcoat skirt, split front/back/sides into 4 tails with leaf-zigzag hems (was flat panels)
def coat_panel(a0,a1,cols=7,rows=6):
    vs=[]; fs=[]
    for j in range(rows+1):
        t=j/rows; z=1.03-0.58*t; r=0.2+0.07*t**0.8
        for i in range(cols+1):
            az=math.radians(a0+(a1-a0)*i/cols)
            zz=z-(0.035 if (j==rows and i%2==1) else 0)-(0.05*math.sin(math.pi*i/cols) if j==rows else 0)
            vs.append((r*math.sin(az),-r*math.cos(az)*0.8,zz))
    for j in range(rows):
        for i in range(cols): k=j*(cols+1)+i; fs.append((k,k+1,k+cols+2,k+cols+1))
    me=bpy.data.meshes.new("coat"); me.from_pydata(vs,[],fs); o=bpy.data.objects.new("coat",me); bpy.context.scene.collection.objects.link(o)
    bpy.context.view_layer.objects.active=o; m=o.modifiers.new("s",'SOLIDIFY'); m.thickness=0.007; m.offset=1; apply_all(o); finish(o,'jacket',None,True)
for a0,a1 in ((10,82),(98,172),(188,262),(278,350)): coat_panel(a0,a1)
for s in (1,-1):
    flat("hemF",[(-0.004,0),(0.004,0),(0.004,-0.42),(-0.004,-0.42)],'glow2',(0.045*s,-0.168,1.0))       # leaf-vein LED piping
''')
rep('genesis',"module('accessory','shades')",'''module('accessory','shades')
# slim wrap shield shades (v2: thinner band, tighter arc, sits on the face) with fine gold brow bar
bpy.ops.mesh.primitive_cylinder_add(vertices=32,radius=0.119,depth=0.026,location=(0,0.0,1.657)); o=bpy.context.object
bm=bmesh.new(); bm.from_mesh(o.data); bmesh.ops.delete(bm,geom=[v for v in bm.verts if v.co.y>-0.07],context='VERTS'); bm.to_mesh(o.data); bm.free()
m=o.modifiers.new("s",'SOLIDIFY'); m.thickness=0.003; apply_all(o); finish(o,'iris','head',True)
cube((0,-0.119,1.672),(0.13,0.004,0.004),'gold',0,'head')
''')
rep('tool-toul-to',"module('accessory','welder')",'''module('accessory','welder')
# SIGNATURE 1 (v2): flip-up welding helmet that reads as a welding mask: flat-faced metal shield, big dark lens window,
# black ratchet headband, chunky side pivots, flipped only ~58 deg so the face plate stays visible above the brow
sh=cube((0,-0.15,1.665),(0.25,0.03,0.22),'metal',0.02,'head')
bpy.ops.mesh.primitive_cylinder_add(vertices=20,radius=0.135,depth=0.24,location=(0,0.0,1.64)); cyl=bpy.context.object
bm=bmesh.new(); bm.from_mesh(cyl.data); bmesh.ops.delete(bm,geom=[v for v in bm.verts if v.co.y>-0.07],context='VERTS'); bm.to_mesh(cyl.data); bm.free()
m=cyl.modifiers.new("s",'SOLIDIFY'); m.thickness=0.01; apply_all(cyl); finish(cyl,'metal','head')
lens=cube((0,-0.171,1.665),(0.15,0.008,0.07),'hair',0.004,'head'); frame=cube((0,-0.167,1.665),(0.18,0.006,0.095),'skate',0.004,'head')
led=cube((0.08,-0.168,1.58),(0.014,0.006,0.014),'glow2',0,'head')
for o in (sh,RL.PARTS[-4]['obj'] if False else cyl,lens,frame,led): pivot_rot(o,(0,0.0,1.74),-58)
ring("headband",(0,0.0,1.72),0.118,0.016,mat='skate',segs=18,bone='head')
for s in (1,-1):
    bpy.ops.mesh.primitive_cylinder_add(vertices=12,radius=0.034,depth=0.03,location=(0.14*s,0.0,1.72),rotation=(0,math.radians(90),0)); finish(bpy.context.object,'metal','head')
    bpy.ops.mesh.primitive_cylinder_add(vertices=8,radius=0.014,depth=0.04,location=(0.155*s,0.0,1.72),rotation=(0,math.radians(90),0)); finish(bpy.context.object,'skate','head')
''')
