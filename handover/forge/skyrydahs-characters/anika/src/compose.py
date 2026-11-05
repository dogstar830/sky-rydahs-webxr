import sys
from PIL import Image,ImageDraw,ImageFont
r,ref,out,label=sys.argv[1:5]
R=Image.open(r).convert('RGB'); C=Image.open(ref).convert('RGB'); W,H=2880,1620
o=Image.new('RGB',(W,H),(18,18,22)); o.paste(R,(0,0))
s=min(1440/C.width,1620/C.height); C=C.resize((int(C.width*s),int(C.height*s)),Image.LANCZOS); o.paste(C,(1440+(1440-C.width)//2,(1620-C.height)//2))
d=ImageDraw.Draw(o); f=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',30)
d.text((30,24),label,font=f,fill=(255,215,0)); d.text((1470,24),'Oliver ref crop (ref2-day-clean)',font=f,fill=(255,215,0)); o.save(out); print(out,o.size)
