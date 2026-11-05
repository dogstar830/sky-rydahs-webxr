#!/usr/bin/env python3
import json, os, cairosvg
from PIL import Image, ImageDraw, ImageFont
OUT = os.path.dirname(os.path.abspath(__file__))
D = {  # base, secondary/trim, accent, rib, lining, hardware, glow
 'code-e':         ('Code : E',        '#0b0b0d','#1c1c20','#ffd700','#ffd700','#3a2e05','#c9a227','#ffd700'),
 'kogarasumaru':   ('Kogarasumaru',    '#07090b','#00e5ff','#00e5ff','#0b1418','#003b44','#8fa6ad','#00e5ff'),
 'volt':           ('VOLT',             '#ff2d95','#14050d','#ffe600','#ffe600','#2a0a1a','#d8d8d8','#ffe600'),
 'rust-claw':      ('Rust Claw',       '#8a3416','#2a130a','#ff7a1a','#ff7a1a','#3b1a0c','#7a4a2a','#ff7a1a'),
 'anubis':         ('Anubis',          '#0a3d3a','#031413','#18d6c4','#18d6c4','#062624','#c9a75a','#18d6c4'),
 'static-angels':  ('Static Angels',   '#3a1670','#9b4dff','#00e5ff','#00e5ff','#160a2a','#c0c6d0','#00e5ff'),
 'sleeping-forest':('Sleeping Forest', '#eef2ec','#1f5e36','#2ecc71','#1f5e36','#0d2a17','#a8b0a8','#2ecc71'),
 'behemoth':       ('Behemoth',        '#0e0b09','#ff6a00','#ff6a00','#ff6a00','#3a1a05','#2b2b2b','#ff6a00'),
 'genesis':        ('Genesis',         '#5a0a52','#14031a','#ffc94a','#ff1fd1','#2a0626','#ffc94a','#ff1fd1'),
 'tool-toul-to':   ('Tool Toul To',    '#5b5f63','#b7472a','#b7472a','#2e3033','#1e1f21','#9aa0a6','#ff5a2a'),
}
keys = ['base','secondary_trim','accent','cuff_collar_rib','lining','zipper_hardware','emissive_glow']
def ent(h): return {'hex': h, 'int': int(h[1:],16), 'three': '0x'+h[1:]}
out = {'_meta': {'game':'Sky Rydahs','note':'Original crew jacket colorways. "int" is usable directly in THREE.Color(); emissive_glow drives neon piping + Air Treck glow.'}, 'crews': {}}
for slug,(name,*cols) in D.items():
    e = {'name': name}
    e.update({k: ent(c) for k,c in zip(keys, cols)})
    e['logo'] = f'/workspace/skyrydahs-characters/shared/crew-logos/{slug}.png'
    e['logo_svg'] = f'/workspace/skyrydahs-characters/shared/crew-logos/{slug}.svg'
    from gen_crew_patches import TWILL
    P = '/workspace/skyrydahs-characters/shared/crew-logos/'
    e['patch'] = {'albedo_with_shadow': P+f'{slug}-patch.png', 'albedo_decal': P+f'{slug}-patch-noshadow.png',
                  'normal_opengl': P+f'{slug}-patch-normal.png', 'height': P+f'{slug}-patch-height.png',
                  'note': 'noshadow/normal/height are pixel-aligned; normal is tangent-space OpenGL +Y (Three.js default)'}
    e['twill_backing'] = ent(TWILL[slug])
    e['pbr'] = {'patch_embroidery': {'roughness':0.55,'metalness':0.0,'normalScale':1.0}, 'shell_fabric': {'roughness':0.62,'metalness':0.0,'note':'nylon/satin bomber; sheen ~0.3 if MeshPhysicalMaterial'},
                'rib_knit': {'roughness':0.9,'metalness':0.0},
                'hardware': {'roughness':0.3,'metalness':1.0},
                'neon_piping': {'emissiveIntensity':2.0,'roughness':0.4,'metalness':0.0},
                'logo_print': {'roughness':0.5,'metalness':0.0}}
    out['crews'][slug] = e
import sys
if '--preview-only' in sys.argv:   # redraw the preview from the CURRENT json (keeps hand edits, e.g. genesis/anubis per brief); json untouched
    J = json.load(open(f'{OUT}/jacket-colorways.json'))['crews']
    D = {k: (e['name'], *[e[q]['hex'] for q in keys]) for k, e in J.items() if os.path.exists(f'{OUT}/{k}-patch.png')}
else:
    json.dump(out, open(f'{OUT}/jacket-colorways.json','w'), indent=2)

def jacket_svg(c):
    b,s,a,r,l,h,g = c
    body = "M300,250 L420,205 Q512,235 604,205 L724,250 L860,330 L905,700 L835,715 L790,470 L770,760 L254,760 L234,470 L189,715 L119,700 L164,330 Z"
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1024" height="900" viewBox="0 0 1024 900">
<defs><filter id="gl"><feGaussianBlur stdDeviation="9"/></filter>
<linearGradient id="sh" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#fff" stop-opacity=".16"/><stop offset=".55" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity=".35"/></linearGradient></defs>
<path d="{body}" fill="none" stroke="{g}" stroke-width="18" filter="url(#gl)" opacity=".8"/>
<path d="{body}" fill="{b}"/>
<path d="M164,330 L300,250 L330,470 L234,470 Z M860,330 L724,250 L694,470 L790,470 Z" fill="{s}" opacity=".9"/>
<path d="M234,470 L189,715 M790,470 L835,715" stroke="{g}" stroke-width="6"/>
<rect x="254" y="720" width="516" height="50" rx="10" fill="{r}"/>
<path d="M119,700 L189,715 L184,750 L112,736 Z M905,700 L835,715 L840,750 L912,736 Z" fill="{r}"/>
<path d="M420,205 Q512,235 604,205 L590,180 Q512,205 434,180 Z" fill="{r}"/>
<path d="M254,700 L770,700" stroke="{g}" stroke-width="5"/>
<path d="{body}" fill="url(#sh)"/>
<path d="{body}" fill="none" stroke="{a}" stroke-width="4" opacity=".7"/>
</svg>'''
W,H = 560, 760
sheet = Image.new('RGB',(5*W, 2*H+140),(18,18,24)); d = ImageDraw.Draw(sheet)
F = '/usr/share/fonts/truetype/dejavu/'
def font(n,sz):
    import subprocess
    p = subprocess.run(['fc-match','-f','%{file}',n],capture_output=True,text=True).stdout
    return ImageFont.truetype(p, sz)
fT, fN, fS = font('Russo One',64), font('Russo One',40), font('DejaVu Sans Mono',17)
d.text((40,40),'SKY RYDAHS — CREW JACKET COLORWAYS (back view)',font=fT,fill=(240,240,240))
for i,(slug,(name,*cols)) in enumerate(D.items()):
    x0,y0 = i%5*W, 140+i//5*H
    d.rounded_rectangle((x0+12,y0+12,x0+W-12,y0+H-12),24,fill=(28,28,36))
    png = cairosvg.svg2png(bytestring=jacket_svg(cols).encode(), output_width=520)
    import io; jk = Image.open(io.BytesIO(png)).convert('RGBA')
    logo = Image.open(f'{OUT}/{slug}-patch.png').resize((260,260),Image.LANCZOS)
    jk.alpha_composite(logo,(260-130, 170))
    sheet.paste(jk,(x0+20,y0+40),jk)
    d.text((x0+30,y0+500),name.upper(),font=fN,fill=tuple(int(cols[6][k:k+2],16) for k in (1,3,5)))
    for j,(k,c) in enumerate(zip(keys,cols)):
        cx,cy = x0+30+(j%2)*260, y0+560+(j//2)*44
        d.rounded_rectangle((cx,cy,cx+36,cy+36),6,fill=c,outline=(90,90,100))
        d.text((cx+44,cy+2),k.replace('_',' '),font=fS,fill=(200,200,210))
        d.text((cx+44,cy+19),c,font=fS,fill=(150,150,160))
sheet.save(f'{OUT}/jacket-colorways-preview.png')
