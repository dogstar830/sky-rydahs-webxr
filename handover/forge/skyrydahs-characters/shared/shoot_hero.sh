#!/bin/bash
# usage: shared/shoot_hero.sh <crew> [ty]  -> renders/keyart.png, face_expressions.png, face_closeup.png (+ shoot.sh set)
D=$1; TY=${2:-1.65}; CH=$(ls -d ~/.cache/ms-playwright/chromium-1248/*/chrome); B=http://localhost:8781
cd /workspace/skyrydahs-characters && bash shared/shoot.sh $D
cd $D; f(){ $CH --headless=new --no-sandbox --use-angle=swiftshader --enable-unsafe-swiftshader --window-size=$1 --virtual-time-budget=$4 --screenshot=$2 "$3" >/dev/null 2>&1; }
f 1600,1000 renders/keyart.png "$B/shared/keyart.html?crew=$D" 30000 &
f 800,800 renders/face_closeup.png "$B/$D/test.html?view=34&dist=0.62&ty=$TY&shot=1" 20000 &
for e in blink smile angry surprised sad smirk mouthOpen focus; do f 360,360 /tmp/fx_${D}_$e.png "$B/$D/test.html?view=front&dist=0.62&ty=$TY&shot=1&expr=$e:1" 20000 & done; wait
python3 - $D <<'P'
import sys; from PIL import Image, ImageDraw
D=sys.argv[1]; E='blink smile angry surprised sad smirk mouthOpen focus'.split(); s=Image.new('RGB',(1440,720))
for i,e in enumerate(E):
    im=Image.open(f'/tmp/fx_{D}_{e}.png').convert('RGB'); ImageDraw.Draw(im).text((8,8),e,fill=(255,255,255)); s.paste(im,((i%4)*360,(i//4)*360))
s.save('renders/face_expressions.png')
P
