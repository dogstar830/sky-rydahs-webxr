#!/usr/bin/env python3
"""Caali G personal back emblem (matches skyrydahs-ref/caali-g-turnaround.jpg BACK view):
big gold phoenix, wings raised in a V, profile head facing left, body = lightning bolt. Black + gold only.
Reuses gen_crew_logos.py (badge/poly/mpoly/outline_motif) and gen_crew_patches.py (embroidery build).
Writes ONLY caali-g.svg/.png and caali-g-patch*.png; other crews' files are untouched."""
import os, cairosvg, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gen_crew_logos as L, gen_crew_patches as P
C = L.C; K, G, G2 = '#0b0b0d', '#e8b423', '#a87810'   # turnaround gold (ochre-gold), darker gold shade
def wing(side):
    sg = 1 if side > 0 else -1; s = ''
    # 4 layered primaries fanning up-out from the shoulder, longest on top (turnaround: V-raised, swept)
    for i, (ang, ln, w) in enumerate([(58, 380, 70), (40, 350, 66), (23, 300, 60), (7, 240, 54)]):
        import math
        a = math.radians(ang); x0, y0 = C+sg*40, 440+i*26
        tx, ty = x0+sg*ln*math.cos(a), y0-ln*math.sin(a)
        nx, ny = -math.sin(a)*w*sg, -math.cos(a)*w
        pts = [(x0, y0-14), (tx, ty), (tx-sg*30*math.cos(a)+nx*.2, ty+30*math.sin(a)+w*.9), (x0+sg*20, y0+w*.7)]
        s += L.poly(pts, G if i % 2 == 0 else G2)
    return s
def phoenix():
    s = L.badge(K, G, G2, r1=500, r2=446)   # embroidered crew-patch frame, black twill, gold merrow
    m = wing(1) + wing(-1)
    # head + neck in profile (beak to viewer's left) with swept crest, as on the turnaround
    m += L.poly([(C+26, 452), (C+20, 372), (C+6, 330), (C-22, 314), (C-74, 336), (C-26, 346), (C-12, 372), (C-22, 452)], G)
    m += L.poly([(C+6, 330), (C+56, 262), (C+26, 336)], G2) + L.poly([(C-4, 318), (C+26, 250), (C+14, 324)], G)   # crest flames
    # body = lightning bolt zig-zag down to a point
    m += L.poly([(C-26, 440), (C+40, 440), (C+6, 590), (C+72, 590), (C-50, 860), (C-6, 652), (C-70, 652)], G, f'stroke="{K}" stroke-width="10"')
    return s + L.outline_motif(m, '#5a4508', 18)
if __name__ == '__main__':
    body = phoenix().replace('<!--M-->', '')
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="1024" height="1024" viewBox="0 0 1024 1024">{body}</svg>'
    open(f'{L.OUT}/caali-g.svg', 'w').write(svg)
    cairosvg.svg2png(bytestring=svg.encode(), write_to=f'{L.OUT}/caali-g.png', output_width=1024, output_height=1024)
    P.TWILL['caali-g'] = '#2a2620'   # Code : E twill (same as code-e)
    P.build('caali-g'); print('caali-g emblem + patch written')
