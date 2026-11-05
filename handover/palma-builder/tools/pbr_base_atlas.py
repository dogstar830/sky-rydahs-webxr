# Palma Builder 10/30: building-base atlas page B (2x2): 0,0 Bricks105 | 1,0 Concrete034 (poured) | 0,1 PaintedMetal004 (steel beams/frames) | 1,1 MetalPlates008 (kick plate)
# CC0 ambientCG (sources: /workspace/skyrydahs-ref/pbr/SOURCES.txt). Out: assets/pbr_base/pbrB_albedo (2048), pbrB_nrm (1024, GL), pbrB_orm (1024: R=AO G=rough B=metal), jpg + KTX2.
import os,subprocess
from PIL import Image, ImageOps
S='/tmp/pbrsrc'; O='/workspace/v3build/assets/pbr_base'; KTX='/workspace/v3build/tools/ktx/bin/ktx'
M=[('Bricks105',0,0),('Concrete034',1,0),('PaintedMetal004',0,1),('MetalPlates008',1,1)]
def f(m,k):
    p=f'{S}/{m}/{m}_2K-JPG_{k}.jpg'; return p if os.path.exists(p) else None
def page(sz,fn,mode):
    pg=Image.new(mode,(sz,sz)); t=sz//2
    for m,c,r in M: pg.paste(fn(m).resize((t,t),Image.LANCZOS),(c*t,r*t))
    return pg
alb=page(2048,lambda m:Image.open(f(m,'Color')).convert('RGB'),'RGB')
nrm=page(1024,lambda m:Image.open(f(m,'NormalGL')).convert('RGB'),'RGB')
def orm(m):
    g=lambda k,d: Image.open(f(m,k)).convert('L').resize((2048,2048)) if f(m,k) else Image.new('L',(2048,2048),d)
    return Image.merge('RGB',(g('AmbientOcclusion',255),g('Roughness',200),g('Metalness',0)))
ormp=page(1024,orm,'RGB')
for n,im in (('albedo',alb),('nrm',nrm),('orm',ormp)):
    im.save(f'{O}/pbrB_{n}.jpg',quality=90)
    fl=ImageOps.flip(im); fl.save(f'/tmp/pbrB_{n}_flip.png')   # KTX2 pre-flipped (flipY=false), like pbrG/pbrF
    enc=['--encode','uastc','--uastc-quality','2','--zstd','18'] if n=='nrm' else ['--encode','basis-lz','--qlevel','192']
    cs='srgb' if n=='albedo' else 'linear'
    subprocess.run([KTX,'create','--format','R8G8B8_SRGB' if cs=='srgb' else 'R8G8B8_UNORM','--assign-tf',cs,'--generate-mipmap',*enc,f'/tmp/pbrB_{n}_flip.png',f'{O}/pbrB_{n}.ktx2'],check=True)
print(os.listdir(O))
