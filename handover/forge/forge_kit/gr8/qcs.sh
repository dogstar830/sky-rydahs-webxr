blender -b --python qc.py -- $1 $2 x >/dev/null 2>&1; python3 -c "
from PIL import Image
ims=[Image.open(f'/tmp/forge_qc_{v}.png').convert('RGB') for v in ['front','back','q']]
o=Image.new('RGB',(1500,800)); [o.paste(i,(k*500,0)) for k,i in enumerate(ims)]; o.save('$3')"
