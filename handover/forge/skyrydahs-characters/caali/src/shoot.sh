CH=$(ls -d ~/.cache/ms-playwright/chromium-1248/*/chrome)
for v in front 34 side back; do $CH --headless=new --no-sandbox --use-angle=swiftshader --enable-unsafe-swiftshader --window-size=600,1000 --virtual-time-budget=20000 --screenshot=renders/$v.png "http://localhost:8799/test.html?view=$v&shot=1" >/dev/null 2>&1; done
python3 - <<'P'
from PIL import Image
ims=[Image.open(f"renders/{v}.png") for v in ("front","34","side","back")]
w,h=ims[0].size; s=Image.new("RGB",(w*4,h))
for i,im in enumerate(ims): s.paste(im,(i*w,0))
s.save("renders/turnaround.png"); s.resize((w*2,h//2)).save("/tmp/ta_small.png")
P
