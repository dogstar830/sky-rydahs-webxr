from PIL import Image,ImageDraw,ImageFont,ImageFilter
G='/workspace/forge_kit/gr8/'; L='/workspace/skyrydahs-characters/shared/crew-logos/'
FB='/usr/share/fonts/truetype/sand-box/google/Barlow Condensed/BarlowCondensed-Bold.ttf'
# 1) GR8YZONE tee print (black backdrop hides Meshy's 'GR8 ZONE'), 1000x1350 = 0.20 x 0.27 m
W,H=1000,1350; im=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(im)
bd=Image.new('L',(W,H),0); ImageDraw.Draw(bd).rounded_rectangle((40,40,W-40,H-40),120,fill=255); bd=bd.filter(ImageFilter.GaussianBlur(28))
im.paste(Image.new('RGBA',(W,H),(11,11,13,255)),(0,0),bd)
bolt=[(560,130),(330,720),(500,720),(400,1220),(700,560),(530,560),(660,130)]
d.polygon(bolt,outline=(46,107,255,255)); 
ImageDraw.Draw(im).line(bolt+[bolt[0]],fill=(46,107,255,255),width=34,joint='curve')
d.polygon(bolt,fill=(255,215,0,255))
for y in range(130,1220):  # gold gradient on bolt
    pass
f=ImageFont.truetype(FB,205)
def txt(s,x,y):
    for dx in range(-9,10,3):
        for dy in range(-9,10,3): d.text((x+dx,y+dy),s,font=f,fill=(10,10,12,255))
    d.text((x,y),s,font=f,fill=(255,215,0,255))
txt('GR8Y',90,480); txt('ZONE',535,570)
im.save(G+'decal_gr8yzone_tee.png'); print('tee decal ok')
# 2) Caali back: black backdrop over Meshy's back 'GRB ZONE' + gold phoenix patch on top, 1024 sq = 0.34 m
P=Image.open(L+'caali-g-patch-noshadow.png').convert('RGBA'); W=1024
im=Image.new('RGBA',(W,W),(0,0,0,0)); bd=Image.new('L',(W,W),0); ImageDraw.Draw(bd).rounded_rectangle((170,110,854,940),90,fill=255); bd=bd.filter(ImageFilter.GaussianBlur(30))
im.paste(Image.new('RGBA',(W,W),(11,11,13,255)),(0,0),bd); im.alpha_composite(P.resize((W,W)))
im.save(G+'decal_caali_back.png')
# 3) Anika back: Code : E crew patch as is
Image.open(L+'code-e-patch.png').convert('RGBA').save(G+'decal_anika_back.png'); print('ok')
