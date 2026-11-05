#!/usr/bin/env python3
"""Sky Rydahs crew-token coins: generate 512px PBR maps (baseColor, normal [OpenGL +Y], ORM [R=1,G=rough,B=metal])
for obverse, reverse and reeded edge of each crew coin. Reads crew-logos/ as SOURCE ONLY (no writes there)."""
import sys, os, io, math
sys.dont_write_bytecode = True
import numpy as np, cairosvg
from PIL import Image, ImageFilter
from scipy import ndimage as ndi
LOGOS = '/workspace/skyrydahs-characters/shared/crew-logos'
sys.path.insert(0, LOGOS)
import gen_crew_logos as G                        # read-only use of the emblem geometry
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'textures')
N = 2048; KS = N/1024; C = (N-1)/2; T = 1024        # work res (2x supersample), output res 1K
yy, xx = np.mgrid[0:N, 0:N].astype(np.float32); RR = np.hypot(xx-C, yy-C)/KS   # radius in 1024-design units
def hx(h): return np.array([int(h[i:i+2], 16) for i in (1, 3, 5)], np.float32)/255

# metal: base colour (sRGB), polished roughness, relief roughness ; enamel colours from the crew palette
CFG = {
 'code-e':         dict(metal='#f2c35a', rp=.22, rr=.42, label='polished/frosted gold, no enamel (all-metal proof strike)'),
 'kogarasumaru':   dict(metal='#c3c8cc', rp=.34, rr=.45, brushed=True, label='brushed steel + cyan enamel'),
 'team-storm':           dict(metal='#cfcdc4', rp=.25, rr=.4,  label='nickel + hot-pink, deep-pink & yellow enamel'),   # alias of volt (old TEAM STORM text)
 'volt':           dict(metal='#cfcdc4', rp=.25, rr=.4,  label='nickel + hot-pink, deep-pink & yellow enamel (VOLT, Oliver 2026-10-29)'),
 'rust-claw':      dict(metal='#8e4f30', rp=.3,  rr=.45, wash=0.8, label='dark antiqued copper + bright orange enamel'),
 'anubis':         dict(metal='#7a5a38', rp=.32, rr=.48, label='dark bronze + teal enamel'),
 'static-angels':  dict(metal='#e3e4e8', rp=.2,  rr=.38, label='silver + purple & cyan enamel'),
 'sleeping-forest':dict(metal='#dcdee0', rp=.24, rr=.42, label='silver + green enamel (white trees left as frosted silver)'),
 'behemoth':       dict(metal='#3b3a3a', rp=.38, rr=.5,  label='blackened steel + orange enamel'),
 'genesis':        dict(metal='#f0c060', rp=.22, rr=.42, label='gold + magenta enamel'),
 'tool-toul-to':   dict(metal='#5d6166', rp=.32, rr=.46, label='gunmetal + rust enamel'),
}
# motif colours that are struck METAL rather than enamel (outlines are always metal)
METAL_COLS = {'code-e': ['#ffd700', '#b8860b'], 'genesis': ['#ffc94a'], 'tool-toul-to': ['#9aa0a6'],
              'sleeping-forest': ['#f4f7f2'], 'rust-claw': ['#a0401a']}
ENAMEL_BOOST = {'rust-claw': [('#ff7a1a', '#ff9a1f')]}
BACKING = {'code-e': '#0b0b0d', 'kogarasumaru': '#050708', 'team-storm': '#14050d', 'volt': '#14050d', 'rust-claw': '#140803', 'anubis': '#031413',
           'static-angels': '#0e0618', 'sleeping-forest': '#06140a', 'behemoth': '#0a0705', 'genesis': '#14031a', 'tool-toul-to': '#121212'}

def render(inner):
    png = cairosvg.svg2png(bytestring=f'<svg xmlns="http://www.w3.org/2000/svg" width="{N}" height="{N}" viewBox="0 0 1024 1024">{inner}</svg>'.encode())
    return np.asarray(Image.open(io.BytesIO(png)).convert('RGBA')).astype(np.float32)/255

def bold(txt, w=5):
    return txt.replace('<text ', f'<text stroke="#ffffff" stroke-width="{w}" stroke-linejoin="round" ')

def parts(k):
    body = G.CREWS[k](); pre, rest = body.split('<!--M-->', 1); mot, txt = rest.split('<!--T-->', 1)
    return G.fit_motif(G.outline_motif(mot, G.OUTLINE[k]), txt, k), bold(txt)

def face(k, motif_svg, text_svg, outfile_prefix):
    cfg = CFG[k]; metal = hx(cfg['metal'])
    M = render(motif_svg); Tm = render(text_svg)[..., 3]
    ma = M[..., 3]; mc = M[..., :3]
    enamel_cols = []
    # classify motif pixels
    back = hx(BACKING[k]); outline = hx(G.OUTLINE[k])
    def near(c, tol=0.12): return np.abs(mc-c).max(-1) < tol
    is_cut = near(back, 0.08) & (ma > .5)
    is_out = near(outline, 0.1) & (ma > .5)
    is_metal = is_out.copy()
    for h in METAL_COLS.get(k, []): is_metal |= near(hx(h), 0.1) & (ma > .5)
    is_en = (ma > .5) & ~is_metal & ~is_cut
    # --- height (0..1 => 0..0.25 mm)
    rim_in = 462
    field = 0.30+0.07*(1-np.clip(RR/rim_in, 0, 1)**2)
    H = field.copy()
    dmet = ndi.distance_transform_edt(is_metal)
    lum = mc.mean(-1)
    H = np.where(is_metal, field+0.26+0.08*lum+0.10*np.clip(dmet/(6*KS), 0, 1), H)
    H = np.where(is_en, field+0.24, H)                         # enamel sits just below the metal walls
    H = np.where(is_cut, field-0.03, H)
    dtx = ndi.distance_transform_edt(Tm > .5)
    H = np.where(Tm > .5, field+0.30+0.10*np.clip(dtx/(3*KS), 0, 1), H)
    # beaded ring + raised rim
    ang = np.arctan2(yy-C, xx-C); bead = (np.abs(RR-448) < 7) & (np.cos(ang*120) > 0.1)
    H = np.where(bead, field+0.22, H)
    rim = np.clip((RR-rim_in)/14, 0, 1); H = np.maximum(H, rim*(0.95+0.05*np.cos(np.clip((RR-490)/30, 0, 1)*np.pi)))
    H = ndi.gaussian_filter(H, 0.8*KS)
    # --- material maps
    cav = np.clip(ndi.gaussian_filter(H, 7*KS)-H, 0, 1)*6          # antique wash in recesses
    base = np.ones((N, N, 3), np.float32)*metal
    rough = np.full((N, N), cfg['rp'], np.float32); metl = np.ones((N, N), np.float32)
    raised = (is_metal | (Tm > .5) | bead)
    rough[raised] = cfg['rr']
    if cfg.get('brushed'):
        rng = np.random.default_rng(3); stripes = ndi.gaussian_filter1d(rng.random((N, N)).astype(np.float32), 30*KS, axis=1)
        rough += (stripes-0.5)*0.5; base *= (0.95+0.1*(stripes-0.5)[..., None])
    wash = np.clip(cav, 0, 1)[..., None]
    base = base*(1-cfg.get('wash', 0.6)*wash); rough = rough+0.35*wash[..., 0]
    base[is_en] = mc[is_en]; rough[is_en] = 0.1; metl[is_en] = 0.0
    base[RR > 511] = metal
    if k in ENAMEL_BOOST:
        for src, dst in ENAMEL_BOOST[k]: base[is_en & near(hx(src), 0.1)] = hx(dst)
    # --- normal map (OpenGL +Y), physical-ish scale
    gy, gx = np.gradient(H*10.0*KS)
    n = np.stack([-gx, gy, np.ones_like(gx)], -1); n /= np.linalg.norm(n, axis=-1, keepdims=True)
    def save(arr, name, mode='RGB', **kw):
        im = Image.fromarray((np.clip(arr, 0, 1)*255).round().astype(np.uint8), mode).resize((T, T), Image.LANCZOS)
        if name.endswith('-normal.jpg'):          # renormalise after downsampling
            a = np.asarray(im).astype(np.float32)/127.5-1; a /= np.linalg.norm(a, axis=-1, keepdims=True)
            im = Image.fromarray(((a+1)*127.5).round().clip(0, 255).astype(np.uint8))
        im.save(f'{OUT}/{name}', **kw)
    for old in ('basecolor.png', 'orm.png'):
        p = f'{OUT}/{outfile_prefix}-{old}'
        if os.path.exists(p): os.remove(p)      # replaced by JPEG versions
    save(base, f'{outfile_prefix}-basecolor.jpg', quality=88, subsampling=0)
    p = f'{OUT}/{outfile_prefix}-normal.png'
    if os.path.exists(p): os.remove(p)
    save(n*0.5+0.5, f'{outfile_prefix}-normal.jpg', quality=93, subsampling=0)
    save(np.dstack([np.ones_like(rough), np.clip(rough, .05, 1), metl]), f'{outfile_prefix}-orm.jpg', quality=85, subsampling=0)
    save(H, f'{outfile_prefix}-height.png', 'L')

def edge(k):
    """Reeded edge: 64 grooves across 512px (UV repeats 3x => 192 reeds); rows 0-9% and 91-100% flat for bevels."""
    W, Hh = 512, 64; x = np.arange(W)[None, :].repeat(Hh, 0).astype(np.float32); y = np.arange(Hh)[:, None].repeat(W, 1)
    h = 0.5+0.5*np.cos(x/W*64*2*np.pi)
    band = ((y > Hh*0.12) & (y < Hh*0.88)).astype(np.float32); h *= band
    gx = np.gradient(h*2.5, axis=1)
    n = np.stack([-gx, np.zeros_like(gx), np.ones_like(gx)], -1); n /= np.linalg.norm(n, axis=-1, keepdims=True)
    metal = hx(CFG[k]['metal']); base = metal*(0.75+0.25*h[..., None]) if True else None
    Image.fromarray((base*255).astype(np.uint8)).save(f'{OUT}/{k}-edge-basecolor.png')
    Image.fromarray(((n*0.5+0.5)*255).astype(np.uint8)).save(f'{OUT}/{k}-edge-normal.png')
    orm = np.dstack([np.ones_like(h), np.full_like(h, CFG[k]['rp']+0.1)+0.15*(1-h), np.ones_like(h)])
    Image.fromarray((orm*255).astype(np.uint8)).save(f'{OUT}/{k}-edge-orm.png')

COIN_NAME = {'volt': 'VOLT'}   # reverse ring label where the logo fn name isn't the crew name
def reverse_svg(k):
    SC = 511.5   # SVG design-space centre (viewBox 0..1024)
    body = G.CREWS[k](); pre, rest = body.split('<!--M-->', 1); mot, txt = rest.split('<!--T-->', 1)
    m = G.outline_motif(mot, G.OUTLINE[k])
    mark = f'<g transform="translate({SC},{SC}) scale(0.52) translate({-SC},{-SC})">{m}</g>'
    ring = G.ring_text('SKY RYDAHS · CHAPTER', '· ' + COIN_NAME.get(k, G.CREWS[k].__name__.replace('_', ' ').upper().replace('CODE E', 'CODE : E')) + ' ·', '#ffffff', 'Russo One', 66, ls=8)
    ring = ring.replace('<!--T-->', '')
    rings = f'<circle cx="{SC}" cy="{SC}" r="300" fill="none" stroke="#ffffff" stroke-width="7"/>'
    return mark, bold(ring) + rings

if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    for k in (sys.argv[1:] or list(CFG)):
        m, t = parts(k); face(k, m, t, f'{k}-front')
        m2, t2 = reverse_svg(k); face(k, m2, t2, f'{k}-back')
        edge(k); print('textures', k, flush=True)
