"""One-shot: upgrade a crew build script to hero level (hero_face head + clumped hair + painted atlas + normal bake + expressions)."""
import re, sys
CREW = {}
CREW['static-angels'] = dict(cfg="'painted': True, 'bake': True, 'wheels4': True, 'bulk': (0.93, 0.95)",
 face="dict(jaw=0.5, width=0.87, nose=0.8, mouth_w=0.9, lips=1, cheek=0.8, eye=dict(w=1.2, h=0.62, rot=12, iris=0.95, lash=1.45, flick=1.7, lower=1.2), brow=dict(inner=1.689, mid=1.696, outer=1.693, thick=0.7))",
 hair='''module('hair')
# Halo (sheet 10): navy twin tails high on the head, soft swept bangs, side locks; halo ring; purple ties; earrings
hair_cap(0.035)
bangs([(-0.045,0.07,-0.3),(-0.02,0.055,0.0),(0.008,0.055,0.1),(0.034,0.085,0.3),(0.062,0.075,0.5),(-0.07,0.072,-0.5)],0.034,0.011)
rnd=random.Random(5)
for i in range(12):
    az=2*math.pi*i/12; d=Vector((math.sin(az)*0.75,-math.cos(az)*0.6+0.25,0.75))
    clump(d,Vector((d.x*0.9,d.y*0.9+0.3,-0.35)),rnd.uniform(0.08,0.11),0.055,0.014,bend=Vector((0,0,-0.3)))
for i in range(8):
    az=math.radians(110+i*20); d=Vector((math.sin(az),-math.cos(az),0.1))
    clump(d,d*0.4+Vector((0,0.1,-1)),rnd.uniform(0.1,0.13),0.045,0.015,bend=Vector((0,0,-0.05)))
for s in (1,-1):
    clump(Vector((0.92*s,-0.1,0.25)),Vector((0.12*s,0.05,-1)),0.14,0.028,0.01,bend=Vector((0,0,0)))
    tie=Vector((0.118*s,0.04,0.085)); L=tie.length
    for k,(ox,oy) in enumerate(((0,0),(0.012,0.01),(-0.01,0.012),(0.006,-0.008),(0.0,0.02),(0.02,0))):
        clump(tie,Vector((0.6*s+ox*10,0.3+oy*10,-0.35)),rnd.uniform(0.42,0.52),0.065,0.04,bend=Vector((-0.15*s,0,-0.6)),segs=7,root_r=(L,L,L))
    bpy.ops.mesh.primitive_torus_add(major_radius=0.026,minor_radius=0.01,major_segments=12,minor_segments=4,location=(0.122*s,0.055,1.762),rotation=(0,math.radians(70*s),0)); finish(bpy.context.object,'gold','head')
bpy.ops.mesh.primitive_torus_add(major_radius=0.13,minor_radius=0.009,major_segments=32,minor_segments=6,location=(0,0.03,1.93),rotation=(math.radians(-10),0,0)); finish(bpy.context.object,'glow2','head')
for sx in (1,-1):
    bpy.ops.mesh.primitive_torus_add(major_radius=0.008,minor_radius=0.002,major_segments=8,minor_segments=3,location=(0.094*sx,0.0,1.615),rotation=(0,math.radians(90),0)); finish(bpy.context.object,'metal','head')
''', drop=["module('accessory','wings')","module('accessory','battery')"])
CREW['kogarasumaru'] = dict(cfg="'painted': True, 'bake': True, 'bulk': (0.96, 0.97)",
 face="dict(jaw=0.45, chin=0.004, nose=1.1, width=0.89, eye=dict(w=1.2, h=0.46, rot=16, iris=0.85, lash=1.1, flick=1.3), brow=dict(inner=1.682, mid=1.693, outer=1.697, thick=1.1))",
 hair='''module('hair')
# black crow-crest: back-swept spiky clumps, long "tail-feather" locks at the nape, sharp short bangs
hair_cap(0.03)
bangs([(-0.04,0.075,-0.35),(-0.012,0.085,-0.05),(0.016,0.08,0.15),(0.045,0.07,0.4),(0.07,0.06,0.6)],0.03,0.011)
rnd=random.Random(9)
for i in range(16):
    az=math.radians(rnd.uniform(-80,80)); el=math.radians(rnd.uniform(35,70))
    d=Vector((math.cos(el)*math.sin(az),-math.cos(el)*math.cos(az)*0.5,math.sin(el)))
    clump(d,Vector((d.x*0.6,0.9,0.35)),rnd.uniform(0.13,0.18),0.05,0.016,bend=Vector((0,0.1,-0.15)))
for i in range(10):
    az=math.radians(rnd.uniform(100,260)); el=math.radians(rnd.uniform(-20,25))
    d=Vector((math.sin(az)*math.cos(el),-math.cos(az)*math.cos(el),math.sin(el)))
    clump(d,d*0.6+Vector((0,0.5,-0.7)),rnd.uniform(0.12,0.2),0.045,0.014,bend=Vector((0,0.15,-0.1)))
for s in (1,-1): clump(Vector((0.85*s,-0.35,0.3)),Vector((0.2*s,-0.2,-1)),0.09,0.026,0.01,bend=Vector((0,0,-0.1)))
''')
CREW['behemoth'] = dict(cfg="'painted': True, 'bake': True",
 face="dict(jaw=0.2, width=0.95, chin=0.006, nose=1.3, mouth_w=1.15, cheek=1.5, ear=1.1, browridge=2.0, eye=dict(x=0.036, w=1.0, h=0.45, rot=6, iris=0.8, lash=0.8, flick=0.5), brow=dict(inner=1.683, mid=1.69, outer=1.689, thick=1.6))",
 hair='''module('hair')
# shaved sides + tall clumped mohawk; dust-mask gaiter pulled down to the neck so the face reads
hair_cap(0.06, 0.109)
for k in range(9):
    t=k/8; d=Vector((0,-0.65+1.45*t,1.0-0.45*abs(t-0.35)))
    clump(d,Vector((0,0.25*t-0.05,1)),0.1-0.03*abs(t-0.35),0.022,0.03,bend=Vector((0,0.25,-0.1)))
bpy.ops.mesh.primitive_torus_add(major_radius=0.078,minor_radius=0.032,major_segments=18,minor_segments=6,location=(0,0.005,1.5)); o=bpy.context.object
o.scale=(1,0.95,0.8); bpy.ops.object.transform_apply(scale=True); finish(o,'cloth','chest')
''')
CREW['sleeping-forest'] = dict(cfg="'painted': True, 'bake': True, 'bulk': (0.97, 0.97)",
 face="dict(jaw=0.45, width=0.88, nose=0.9, eye=dict(w=1.15, h=0.42, rot=4, iris=0.9, lash=1.0, flick=0.8), brow=dict(inner=1.688, mid=1.692, outer=1.689, thick=0.8))",
 hair='''module('hair')
# long sleek swept-back hair in clumps + a low clumped ponytail (calm, elite)
hair_cap(0.04)
bangs([(-0.05,0.07,-0.6),(-0.02,0.08,-0.4),(0.03,0.08,0.4),(0.06,0.07,0.6)],0.03,0.01)
rnd=random.Random(4)
for i in range(14):
    az=math.radians(rnd.uniform(-75,75)); el=math.radians(rnd.uniform(30,70))
    d=Vector((math.cos(el)*math.sin(az),-math.cos(el)*math.cos(az)*0.5,math.sin(el)))
    clump(d,Vector((d.x*0.4,1,-0.15)),rnd.uniform(0.13,0.17),0.05,0.012,bend=Vector((0,0,-0.25)))
for s in (1,-1):
    for k in range(2): clump(Vector((0.85*s,-0.3+0.15*k,0.25)),Vector((0.15*s,0.1,-1)),0.16-0.03*k,0.03,0.01,bend=Vector((0,0,0)))
tie=Vector((0,0.105,-0.02)); L=tie.length
for k,(ox,oy) in enumerate(((0,0),(0.02,0.01),(-0.02,0.01),(0,0.02),(0.01,-0.01))):
    clump(tie,Vector((ox*5,0.25+oy*5,-1)),rnd.uniform(0.3,0.36),0.035,0.024,bend=Vector((0,0.05,0)),segs=6,root_r=(L,L,L))
ring("tie",(0,0.123,1.655),0.028,0.022,rot=(math.radians(25),0,0),mat='gold',segs=10,bone='head')
''')
CREW['genesis'] = dict(cfg="'painted': True, 'bake': True, 'bulk': (1.03, 1.0)",
 face="dict(jaw=0.4, chin=0.003, mouth_w=1.1, lips=0.6, eye=dict(w=1.18, h=0.58, rot=14, iris=0.9, lash=1.25, flick=1.4), brow=dict(inner=1.686, mid=1.698, outer=1.69, thick=0.9))",
 hair='''module('hair')
# tall glossy pompadour built from big swept clumps rolling up-and-back, slicked sides
hair_cap(0.05)
rnd=random.Random(2)
for i,x in enumerate((-0.06,-0.035,-0.012,0.012,0.035,0.06)):
    d=Vector((x*6,-0.8,0.55))
    clump(d,Vector((x*2,-0.25,1)),0.15+0.02*(1-abs(x)/0.06),0.045,0.022,bend=Vector((0,0.55,-0.1)))
for i in range(10):
    az=math.radians(rnd.uniform(70,290)); el=math.radians(rnd.uniform(0,35))
    d=Vector((math.sin(az)*math.cos(el),-math.cos(az)*math.cos(el),math.sin(el)))
    clump(d,Vector((d.x*0.25,0.9,-0.25)),rnd.uniform(0.09,0.12),0.05,0.012,bend=Vector((0,0,-0.15)))
''')
CREW['tool-toul-to'] = dict(cfg="'painted': True, 'bake': True, 'bulk': (1.08, 1.08)",
 face="dict(jaw=0.38, width=0.92, nose=1.15, mouth_w=1.1, cheek=1.2, eye=dict(w=1.05, h=0.6, rot=6, iris=1.0, lash=0.9, flick=0.6), brow=dict(inner=1.692, mid=1.697, outer=1.689, thick=1.2))",
 hair='''module('hair')
# messy short clumps poking out under a rust bandana
hair_cap(0.045)
rnd=random.Random(8)
for i in range(16):
    az=2*math.pi*i/16+rnd.uniform(-0.2,0.2); el=math.radians(rnd.uniform(5,55))
    d=Vector((math.sin(az)*math.cos(el),-math.cos(az)*math.cos(el),math.sin(el)))
    clump(d,d+Vector((rnd.uniform(-0.3,0.3),0.2,0.1)),rnd.uniform(0.06,0.09),0.04,0.014,bend=Vector((0,0,-0.1)))
bangs([(-0.04,0.065,-0.4),(-0.01,0.07,0.2),(0.025,0.06,-0.1),(0.055,0.06,0.5)],0.032,0.011)
ring("bandana",(0,0.012,1.712),0.116,0.032,rot=(math.radians(-10),0,0),mat='gold',segs=18,bone='head')
''')

def upgrade(name):
    p=f'/workspace/skyrydahs-characters/{name}/src/build_rider.py'; s=open(f'/workspace/skyrydahs-characters/legacy/hero7/{name}-build_rider.py').read()
    C=CREW.get(name, {})
    s=s.replace("from rider_lib import *\n","from rider_lib import *\nimport rider_lib as RL\nfrom hero_face import *\nimport hero_face as HF\n",1)
    for fn in ('hair_cap(','clump(','bangs(','hero_head(','add_expressions('): C={**C,'hair':C['hair'].replace(fn,'HF.'+fn).replace('HF.HF.','HF.')}
    s=re.sub(r"(CFG = \{.*?)\}\n", lambda m: m.group(1)+", "+C['cfg']+"}\n" if 'bulk' not in m.group(1) or 'bulk' not in C['cfg'] else m.group(1).replace("'bulk': (1.22, 1.18)","")+", "+C['cfg']+"}\n", s, count=1)
    if name!='anubis':
        h=s.index("# ---------- head ----------"); a=s.rindex("module('body')",0,h); b=s.index("\nmodule(",h)
        s=s[:a]+"module('body')\nFACE = HF.hero_head("+C['face']+")\n"+s[b+1:]
        a=s.index("module('hair')"); b=s.index("\nmodule(",a+5)
        s=s[:a]+C['hair']+s[b+1:]
    for d in C.get('drop',[]):
        a=s.index(d); b=s.find("\nmodule(",a+5); b=b if b>0 else s.index("\nbuild_skates(",a); s=s[:a]+s[b+1:]
    s=s.replace("\nbuild_skates()","\nHF.add_expressions(FACE)\nbuild_skates()",1)
    open(p,'w').write(s)
if __name__=='__main__':
    for n in sys.argv[1:]: upgrade(n); print('upgraded',n)
