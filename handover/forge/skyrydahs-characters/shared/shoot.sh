#!/bin/bash
# usage: shared/shoot.sh <crewdir>   (server must serve /workspace/skyrydahs-characters on :8781)
D=$1; CH=$(ls -d ~/.cache/ms-playwright/chromium-1248/*/chrome); U=http://localhost:8781/$D/test.html
cd /workspace/skyrydahs-characters/$D
s(){ $CH --headless=new --no-sandbox --use-angle=swiftshader --enable-unsafe-swiftshader --window-size=$1 --virtual-time-budget=20000 --screenshot=$2 "$U?$3" >/dev/null 2>&1; }
for v in front 34 side back; do s 600,1000 renders/$v.png "view=$v&shot=1"; done
s 900,700 renders/fp_view.png "fp=1&shot=1"
s 600,1000 renders/vr_34.png "view=34&shot=1&vr=1"
s 600,1000 renders/lod1_34.png "view=34&shot=1&lod=1"
s 600,1000 renders/lod2_34.png "view=34&shot=1&lod=2"
s 600,1000 renders/sil_34.png "view=34&shot=1&sil=1"
s 600,1000 renders/sil_back.png "view=back&shot=1&sil=1"
python3 - <<'P'
from PIL import Image
ims=[Image.open(f"renders/{v}.png") for v in ("front","34","side","back")]
w,h=ims[0].size; s=Image.new("RGB",(w*4,h))
for i,im in enumerate(ims): s.paste(im,(i*w,0))
s.save("renders/turnaround.png")
P
