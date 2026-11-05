# 'Gr8yzone' chest logo: real font (Barlow Condensed ExtraBold/Black italic-skewed), gold gradient, dark outline, lightning bolts, soft glow. RGBA 1024x320.
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import glob
F=[f for f in glob.glob('/usr/share/fonts/truetype/sand-box/google/Barlow Condensed/*.ttf') if 'BlackItalic' in f or 'ExtraBoldItalic' in f]; F=sorted(F)[0]
W,H=1024,320; TXT='Gr8yzone'
f=ImageFont.truetype(F,230); m=Image.new('L',(W,H),0); d=ImageDraw.Draw(m); bb=d.textbbox((0,0),TXT,font=f); tw=bb[2]-bb[0]
x0=(W-tw)//2-bb[0]+20; y0=(H-(bb[3]-bb[1]))//2-bb[1]; d.text((x0,y0),TXT,font=f,fill=255)
bolt=lambda cx,cy,s:[(cx+.15*s,cy-.5*s),(cx-.25*s,cy+.06*s),(cx-.02*s,cy+.06*s),(cx-.18*s,cy+.5*s),(cx+.28*s,cy-.1*s),(cx+.04*s,cy-.1*s)]
d.polygon(bolt(x0-60,H//2,190),fill=255); d.polygon(bolt(x0+tw+50,H//2,150),fill=255)
grad=Image.new('RGB',(W,H)); gd=ImageDraw.Draw(grad)
for y in range(H): t=y/H; gd.line([(0,y),(W,y)],fill=(int(255-30*t),int(236-90*t),int(120-110*t)))
out=Image.new('RGBA',(W,H),(0,0,0,0))
glow=m.filter(ImageFilter.GaussianBlur(14)); out.paste(Image.new('RGBA',(W,H),(255,200,40,150)),(0,0),glow.point(lambda v:int(v*.6)))
ol=m.filter(ImageFilter.MaxFilter(9)); out.paste(Image.new('RGBA',(W,H),(20,14,4,255)),(0,0),ol)
out.paste(grad,(0,0),m); out.save('/workspace/skyrydahs-characters/wardrobe/top/gr8yzone_logo.png'); print('font',F)
