#!/usr/bin/env python3
"""Sky Rydahs crew back-logo generator. Original procedural vector emblems.
Outputs <crew>.svg + <crew>.png (1024, transparent) for each crew."""
import math, cairosvg, os, re
OUT = os.path.dirname(os.path.abspath(__file__))
C = 512

def mirror(pts):  # list of (x,y) on right half -> closed symmetric polygon
    return pts + [(2*C-x, y) for x, y in reversed(pts)]
def poly(pts, fill, extra=''):
    return f'<polygon points="{" ".join(f"{x:.1f},{y:.1f}" for x,y in pts)}" fill="{fill}" {extra}/>'
def mpoly(pts, fill, extra=''):  # right-side shape + mirrored copy
    return poly(pts, fill, extra) + poly([(2*C-x, y) for x, y in pts], fill, extra)

_FONTS = {}
def _font(name, size):
    import subprocess
    from PIL import ImageFont
    if name not in _FONTS:
        _FONTS[name] = subprocess.run(['fc-match', '-f', '%{file}', name], capture_output=True, text=True).stdout
    return ImageFont.truetype(_FONTS[name], size)

def _arc_letters(txt, pid, plen, col, font, size, ls):
    """Place each glyph individually along an arc path (avoids cairosvg's crowded first-glyph
    spacing on textPath, which made 'FIRST' read as 'ARST')."""
    f = _font(font, size)
    adv = [f.getlength(ch) for ch in txt]
    total = sum(adv)+ls*(len(txt)-1); pos = plen/2-total/2; out = ''
    for ch, w in zip(txt, adv):
        if ch.strip():
            out += (f'<text font-family="{font}" font-size="{size}" fill="{col}" text-anchor="middle">'
                    f'<textPath href="#{pid}" startOffset="{pos+w/2:.1f}">{ch}</textPath></text>')
        pos += w+ls
    return out

def ring_text(top, bottom, col, font, size=64, r=None, ls=6, bfont=None):
    # keep cap tops clear of the cream stitch line (r~446): baseline drops as the font grows
    r = r or int(432 - 0.92*size)
    bfont = bfont or font
    rb = r+size*0.55; bs = int(size*0.62)
    s = '<!--T-->' + f'''<defs><path id="ta" d="M {C-r},{C} A {r},{r} 0 0 1 {C+r},{C}"/>
<path id="tb" d="M {C-rb},{C} A {rb},{rb} 0 0 0 {C+rb},{C}"/></defs>'''
    s += _arc_letters(top, 'ta', math.pi*r, col, font, size, ls)
    if bottom:
        s += _arc_letters(bottom, 'tb', math.pi*rb, col, bfont, bs, ls+4)
    return s

CREAM = '#f5ecd7'
def badge(dark, border, line2=None, r1=500, r2=300):
    """Embroidered-patch look: bright merrowed border, dark backing, cream stitch line."""
    s = f'<circle cx="{C}" cy="{C}" r="{r1}" fill="{border}"/>'
    s += f'<circle cx="{C}" cy="{C}" r="{r1-19}" fill="none" stroke="#000" stroke-opacity=".22" stroke-width="34" stroke-dasharray="3 6"/>'
    s += f'<circle cx="{C}" cy="{C}" r="{r1-40}" fill="{dark}"/>'
    s += f'<circle cx="{C}" cy="{C}" r="{r1-54}" fill="none" stroke="{CREAM}" stroke-width="5" stroke-dasharray="16 10"/>'
    s += f'<circle cx="{C}" cy="{C}" r="{r2}" fill="none" stroke="{line2 or border}" stroke-width="8"/>'
    return s + '<!--M-->'

def outline_motif(m, col, w=None):
    w = w or (10 if col == '#fff2f8' else 26)   # thinner satin outline for Team Storm's tapered forks
    """Duplicate the emblem behind itself as a thick satin outline."""
    d = re.sub(r'fill="#[0-9a-fA-F]{6}"', f'fill="{col}"', m)
    d = re.sub(r'stroke="#[0-9a-fA-F]{6}"', f'stroke="{col}"', d)
    d = re.sub(r'stroke-width="(\d+)"', lambda g: f'stroke-width="{int(g.group(1))+w}"', d)
    d = re.sub(r'clip-path="url\(#up\)"', '', d)
    d = d.replace('<clipPath id="up">', '<clipPath id="upx">')
    return f'<g stroke="{col}" stroke-width="{w}" stroke-linejoin="round" stroke-linecap="round">{d}</g>' + m

def wings(col, col2, y0=470, n=6, span=420, drop=260, inner=70):
    s = ''
    for i in range(n):
        t = i/(n-1)
        ang = math.radians(-25 + 75*t)
        L = span*(1-0.45*t)
        x0 = C+inner; yb = y0 + 25*i
        tip = (x0 + L*math.cos(ang), yb - 140 + L*math.sin(ang)*0.9 - 40*(1-t))
        pts = [(x0, yb-30), tip, (tip[0]-40, tip[1]+38), (x0, yb+30)]
        s += mpoly(pts, col if i % 2 == 0 else col2)
    return s

def bolt(cx, cy, h, col, extra=''):
    k = h/600
    pts = [(40,-300),(-110,20),(5,20),(-60,300),(120,-60),(5,-60),(70,-300)]
    return poly([(cx+x*k, cy+y*k) for x, y in pts], col, extra)

LOGOS = {}

def code_e():
    K, G, G2 = '#0b0b0d', '#ffd700', '#b8860b'
    s = badge(K, G, G2)
    s += wings(G, G2, y0=520, n=6, span=360)
    s += mpoly([(C, 330), (C+70, 400), (C+40, 470), (C, 440)], G)   # head crest
    s += mpoly([(C+50,330),(C+95,250),(C+70,345)], G2)                # crest flames
    s += bolt(C, 560, 440, G, f'stroke="{K}" stroke-width="10"')
    s += mpoly([(C+20,700),(C+110,800),(C+40,770),(C,830)], G2)          # tail flames
    s += ring_text('CODE : E', 'RIDE THE STORM', G, 'Black Ops One', 72)
    return s
def kogarasumaru():
    K, Cy, Cy2 = '#050708', '#00e5ff', '#008ba3'
    s = badge(K, Cy, Cy2)
    # crow spread wings (angular, swept down) + head with beak facing front
    for i in range(7):
        t = i/6
        x0, y0 = C+60, 450+18*i
        tip = (C+80+330*(1-0.35*t), 330+120*t+40*i)
        s += mpoly([(x0, y0-25), tip, (tip[0]-25, tip[1]+45), (x0, y0+35)], Cy if i % 2 == 0 else Cy2)
    s += mpoly([(C, 340), (C+62, 380), (C+70, 470), (C+50, 640), (C, 700)], Cy)  # body
    s += mpoly([(C+20,700),(C+70,800),(C,770)], Cy2)                       # tail
    s += poly([(C-26,410),(C+26,410),(C,500)], K)                          # beak cutout
    s += mpoly([(C+22,385),(C+48,392),(C+30,402)], K)                       # eyes
    s += ring_text('KOGARASUMARU', 'SHADOW · HONOR · PURPOSE', Cy, 'Russo One', 64)
    return s
def team_storm(name='TEAM STORM'):
    """VOLT (alias slug team-storm, old name TEAM STORM): layered thunderhead with forked, branching lightning raining from its base."""
    K, P, P2, Y = '#14050d', '#ff2d95', '#a3125c', '#ffe600'
    s = badge(K, Y, P)
    def cloud(blobs, col):
        return ''.join(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{col}"/>' for x, y, r in blobs)
    back = [(C-185, 400, 82), (C-70, 350, 108), (C+70, 335, 118), (C+190, 392, 88), (C, 420, 120)]
    front = [(C-230, 470, 62), (C-130, 455, 85), (C, 470, 92), (C+130, 452, 85), (C+235, 474, 60)]
    s += cloud(back, P2)
    s += f'<rect x="{C-290}" y="470" width="580" height="60" rx="30" fill="{P}"/>' + cloud(front, P)
    def fork(pts, w0):
        """Tapered jagged lightning channel: width w0 at the cloud, sharp point at the tip."""
        n = len(pts); L, R = [], []
        for i, (x, y) in enumerate(pts):
            x0, y0 = pts[max(i-1, 0)]; x1, y1 = pts[min(i+1, n-1)]
            dx, dy = x1-x0, y1-y0; l = math.hypot(dx, dy) or 1
            nx, ny = -dy/l, dx/l; w = w0*(1-i/(n-1))**0.8/2
            L.append((x+nx*w, y+ny*w)); R.append((x-nx*w, y-ny*w))
        return poly(L+R[::-1], Y)
    # three main forks from the cloud base, each splitting into side branches
    s += fork([(C-150, 515), (C-175, 570), (C-140, 585), (C-190, 650), (C-160, 662), (C-215, 760)], 34)
    s += fork([(C-176, 572), (C-230, 610), (C-215, 622), (C-268, 672)], 16)
    s += fork([(C-188, 652), (C-130, 700), (C-140, 712), (C-100, 745)], 12)
    s += fork([(C+15, 520), (C-15, 585), (C+25, 598), (C-12, 670), (C+22, 682), (C-8, 790)], 38)
    s += fork([(C+22, 598), (C+70, 640), (C+58, 652), (C+105, 715)], 16)
    s += fork([(C-12, 670), (C-60, 712), (C-50, 722), (C-85, 760)], 12)
    s += fork([(C+165, 515), (C+190, 568), (C+150, 582), (C+200, 648), (C+168, 660), (C+225, 745)], 32)
    s += fork([(C+190, 570), (C+245, 602), (C+232, 615), (C+280, 655)], 15)
    s += ring_text(name, 'RIDE THE THUNDERHEAD', Y, 'Bungee', 74, ls=12)
    return s
def rust_claw():
    K, O, R = '#140803', '#ff7a1a', '#a0401a'
    s = badge(K, O, R)
    # gear ring
    s += ''.join(f'<rect x="{C-26}" y="{C-330}" width="52" height="80" fill="{R}" transform="rotate({i*20} {C} {C})"/>' for i in range(18))
    s += f'<circle cx="{C}" cy="{C}" r="275" fill="{R}"/><circle cx="{C}" cy="{C}" r="235" fill="{K}"/>'
    for dx in (-110, 0, 110):
        s += poly([(C+dx+80, 285), (C+dx+60, 470), (C+dx-5, 640), (C+dx-75, 745), (C+dx-45, 560), (C+dx+15, 400)], O)
    s += ring_text('RUST CLAW', 'TEAR IT UP', O, 'Anton', 76, ls=14)
    return s
def anubis():
    K, T, T2 = '#031413', '#18d6c4', '#0a7d73'
    s = badge(K, T, T2)
    # front-facing jackal head: tall ears, narrow snout
    s += mpoly([(C, 300), (C+60, 330), (C+150, 200), (C+170, 430), (C+120, 560), (C+50, 700), (C, 740)], T)
    s += mpoly([(C+75,340),(C+140,250),(C+148,400)], T2)        # inner ears
    s += mpoly([(C+40, 470), (C+120, 450), (C+70, 505)], K)      # eyes
    s += mpoly([(C, 560), (C+45, 600), (C+20, 690), (C, 700)], T2)  # snout
    s += poly([(C-22,690),(C+22,690),(C,725)], K)
    s += mpoly([(C+0,380),(C+16,380),(C+8,440)], K)  # brow mark
    s += ring_text('ANUBIS', 'WEIGH YOUR SOUL', T, 'Russo One', 84, ls=18)
    return s
def static_angels():
    K, Pu, Cy = '#0e0618', '#9b4dff', '#00e5ff'
    s = badge(K, Cy, Pu)
    s += f'<ellipse cx="{C}" cy="320" rx="150" ry="42" fill="none" stroke="{Cy}" stroke-width="22"/>'
    s += wings(Pu, Cy, y0=560, n=5, span=380, inner=40)
    s += mpoly([(C, 420), (C+40, 470), (C+55, 640), (C, 720)], Pu)
    # static zigzag through center
    zz = [(C-190, 540), (C-110, 500), (C-50, 580), (C+20, 490), (C+90, 575), (C+190, 520)]
    s += f'<polyline points="{" ".join(f"{x},{y}" for x,y in zz)}" fill="none" stroke="{Cy}" stroke-width="16" stroke-linejoin="miter"/>'
    s += ring_text('STATIC ANGELS', 'NOISE FROM ABOVE', Cy, 'Orbitron', 62, ls=8)
    return s
def sleeping_forest():
    K, W, G = '#06140a', '#f4f7f2', '#2ecc71'
    s = badge(K, G, W)
    s += f'<circle cx="{C+70}" cy="330" r="85" fill="{W}"/><circle cx="{C+105}" cy="305" r="78" fill="{K}"/>'
    for dx, h, col in ((-150, 300, G), (150, 300, G), (0, 400, W)):
        base = 720
        for k in range(3):
            w = (130 - 25*k) * h/400; y = base - k*h*0.28
            s += poly([(C+dx-w, y), (C+dx, y-h*0.45), (C+dx+w, y)], col)
        s += f'<rect x="{C+dx-12}" y="{base}" width="24" height="40" fill="{col}"/>'
    s += ring_text('SLEEPING FOREST', 'SILENT · DEEP · ROOTED', W, 'Oswald', 64, ls=10)
    return s
def behemoth():
    K, O = '#0a0705', '#ff6a00'
    s = badge(K, O, '#7a3300')
    # horned skull
    s += mpoly([(C+110, 400), (C+260, 330), (C+330, 200), (C+300, 360), (C+160, 470)], O)  # horns
    s += mpoly([(C, 350), (C+150, 380), (C+170, 500), (C+110, 620), (C+70, 740), (C, 760)], O)
    s += mpoly([(C+40, 470), (C+125, 450), (C+110, 530), (C+55, 530)], K)  # eye sockets
    s += mpoly([(C+15, 600), (C+45, 650), (C+15, 660)], K)                 # nostrils
    for i in range(4): s += f'<rect x="{C-80+i*42}" y="690" width="26" height="45" fill="{K}"/>'
    s += ring_text('BEHEMOTH', 'UNSTOPPABLE', O, 'Anton', 78, ls=18)
    return s
def genesis():
    K, M, G = '#14031a', '#ff1fd1', '#ffc94a'
    s = badge(K, G, M)
    for i in range(9):
        a = math.radians(i*22.5 - 180); L = 290 if i % 2 == 0 else 200
        p = (C+L*math.cos(a), C+L*math.sin(a))
        b1 = (C+160*math.cos(a+0.12), C+40+160*math.sin(a+0.12)); b2 = (C+160*math.cos(a-0.12), C+40+160*math.sin(a-0.12)); p=(p[0], p[1]+40)
        s += poly([b1, p, b2], G if i % 2 == 0 else M)
    # rising sun over a split horizon (no eye, no triangle)
    s += f'<circle cx="{C}" cy="{C+40}" r="150" fill="{K}" stroke="{M}" stroke-width="10"/>'
    s += f'<clipPath id="up"><rect x="0" y="0" width="1024" height="{C+40}"/></clipPath>'
    s += f'<circle cx="{C}" cy="{C+40}" r="120" fill="{G}" clip-path="url(#up)"/>'
    s += f'<rect x="{C-230}" y="{C+55}" width="210" height="20" fill="{M}"/><rect x="{C+20}" y="{C+55}" width="210" height="20" fill="{M}"/>'
    s += f'<rect x="{C-170}" y="{C+95}" width="150" height="16" fill="{G}"/><rect x="{C+20}" y="{C+95}" width="150" height="16" fill="{G}"/>'
    s += f'<rect x="{C-100}" y="{C+130}" width="80" height="12" fill="{M}"/><rect x="{C+20}" y="{C+130}" width="80" height="12" fill="{M}"/>'
    s += ring_text('GENESIS', 'FIRST LIGHT', G, 'Orbitron', 80, ls=16, bfont='Russo One')
    return s
def tool_toul_to():
    K, R, Gy = '#121212', '#b7472a', '#9aa0a6'
    s = badge(K, R, Gy)
    def wrench(rot):
        return (f'<g transform="rotate({rot} {C} {C})"><rect x="{C-22}" y="{C-230}" width="44" height="460" rx="14" fill="{Gy}"/>'
                f'<circle cx="{C}" cy="{C-250}" r="70" fill="{Gy}"/><rect x="{C-26}" y="{C-340}" width="52" height="100" fill="{K}"/>'
                f'<circle cx="{C}" cy="{C+250}" r="60" fill="{Gy}"/><circle cx="{C}" cy="{C+250}" r="28" fill="{K}"/></g>')
    s += wrench(45) + wrench(-45)
    s += ''.join(f'<rect x="{C-30}" y="{C-150}" width="60" height="60" fill="{R}" transform="rotate({i*45} {C} {C})"/>' for i in range(8))
    s += f'<circle cx="{C}" cy="{C}" r="120" fill="{R}"/><circle cx="{C}" cy="{C}" r="55" fill="{K}"/>'
    s += ring_text('TOOL TOUL TO', 'BUILT NOT BOUGHT', R, 'Black Ops One', 68, ls=10)
    return s

OUTLINE = {'code-e':'#f5ecd7','kogarasumaru':'#e6fbff','team-storm':'#fff2f8','volt':'#fff2f8','rust-claw':'#f5ecd7','anubis':'#f5ecd7','static-angels':'#f2eaff','sleeping-forest':'#000000','behemoth':'#f5ecd7','genesis':'#fff3d6','tool-toul-to':'#f5ecd7'}
CREWS = {'code-e': code_e, 'kogarasumaru': kogarasumaru, 'team-storm': team_storm, 'volt': lambda: team_storm('VOLT'), 'rust-claw': rust_claw,
         'anubis': anubis, 'static-angels': static_angels, 'sleeping-forest': sleeping_forest,
         'behemoth': behemoth, 'genesis': genesis, 'tool-toul-to': tool_toul_to}
def _alpha(inner):
    import numpy as np, io
    from PIL import Image
    png = cairosvg.svg2png(bytestring=f'<svg xmlns="http://www.w3.org/2000/svg" width="512" height="512" viewBox="0 0 1024 1024">{inner}</svg>'.encode())
    return np.asarray(Image.open(io.BytesIO(png)).convert('RGBA'))[..., 3] > 20

def fit_motif(motif, txt, k, gap=14):
    """Shrink the emblem (about its centre, nudged toward the middle) until it keeps a clear band
    of >= gap px from the ring lettering. Keeps the lettering legible on every patch."""
    from scipy import ndimage as ndi
    import numpy as np
    tmask = ndi.binary_dilation(_alpha(txt), iterations=gap//2)   # 512px render -> gap/2 px
    yy, xx = np.mgrid[0:512, 0:512]
    tmask |= np.hypot(xx-255.75, yy-255.75) > 428/2               # keep clear of stitch line + border
    s = 1.0
    while s > 0.6:
        g = f'<g transform="translate({C},{C}) scale({s:.3f}) translate({-C},{-C})">{motif}</g>'
        if not (_alpha(g) & tmask).any():
            print(f'{k}: emblem scale {s:.2f}'); return g
        s -= 0.02
    print(f'{k}: WARNING still overlapping at {s:.2f}'); return g

# Oliver 2026-10-29: crew name is VOLT. Slug 'volt' is primary; 'team-storm' is kept as an alias output (old TEAM STORM ring text, files untouched).
# Usage: gen_crew_logos.py [slug ...]  (no args = every crew). Contact sheet shows VOLT in the storm slot.
SHEET = [k for k in CREWS if k != 'team-storm']
if __name__ == '__main__':
    import sys
    for k, f in [(k, CREWS[k]) for k in (sys.argv[1:] or CREWS)]:
        body = f()
        pre, rest = body.split('<!--M-->', 1); mot, txt = rest.split('<!--T-->', 1)
        body = pre + fit_motif(outline_motif(mot, OUTLINE[k]), txt, k) + txt
        svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="1024" height="1024" viewBox="0 0 1024 1024">{body}</svg>'
        open(f'{OUT}/{k}.svg', 'w').write(svg)
        cairosvg.svg2png(bytestring=svg.encode(), write_to=f'{OUT}/{k}.png', output_width=1024, output_height=1024)
    from PIL import Image
    sheet = Image.new('RGBA', (5*420, 2*420), (40, 40, 48, 255))
    for i, k in enumerate(SHEET):
        im = Image.open(f'{OUT}/{k}-patch.png' if os.path.exists(f'{OUT}/{k}-patch.png') else f'{OUT}/{k}.png').resize((400, 400), Image.LANCZOS)
        sheet.alpha_composite(im, (i % 5*420+10, i//5*420+10))
    sheet.save(f'{OUT}/logos-contact-sheet.png')
