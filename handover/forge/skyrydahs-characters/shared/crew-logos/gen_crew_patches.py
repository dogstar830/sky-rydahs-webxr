#!/usr/bin/env python3
"""Sky Rydahs: turn the flat crew decals (<crew>.png) into embroidered patch renders.
Outputs per crew: <crew>-patch.png (with drop shadow), <crew>-patch-noshadow.png,
<crew>-patch-normal.png (tangent-space, OpenGL +Y), <crew>-patch-height.png.
Run after gen_crew_logos.py. All outputs 1024x1024, aligned."""
import os, numpy as np
from PIL import Image, ImageFilter
from scipy import ndimage as ndi
OUT = os.path.dirname(os.path.abspath(__file__))
N, C, S = 1024, 511.5, 0.90             # canvas, center, patch scale
R_TW, R_B0, R_B1 = 506*S, 500*S, 462*S   # twill edge, merrow outer, merrow inner
TWILL = {'code-e':'#2a2620','kogarasumaru':'#1d2629','team-storm':'#2a2a26','volt':'#2a2a26','rust-claw':'#3a2a20','anubis':'#22302e',
         'static-angels':'#2a2434','sleeping-forest':'#e4e2d6','behemoth':'#2a2622','genesis':'#2e2230','tool-toul-to':'#3a3a3a'}
LIGHT = np.array([-0.45, 0.55, 0.70]); LIGHT /= np.linalg.norm(LIGHT)   # x right, y UP, z out
yy, xx = np.mgrid[0:N, 0:N].astype(np.float32)
dx, dy = xx-C, yy-C; RR = np.hypot(dx, dy); PHI = np.arctan2(dy, dx)
rng = np.random.default_rng(7)
def hx(h): return np.array([int(h[i:i+2], 16) for i in (1, 3, 5)], np.float32)/255
def h1(a):  # cheap hash -> [0,1)
    return np.modf(np.sin(a*12.9898+78.233)*43758.5453)[0]%1.0

def satin(angle, period=4.2):
    """Satin stitch: parallel strands running along `angle`; returns height, strand id."""
    ux, uy = -np.sin(angle), np.cos(angle)          # across-strand axis
    v = xx*np.cos(angle)+yy*np.sin(angle)
    u = xx*ux+yy*uy + 0.7*np.sin(v/19.0)
    sid = np.floor(u/period); f = u/period - sid
    prof = np.sin(np.pi*f).clip(0)**0.6
    return prof, sid

def tatami(angle, row=4.0, length=13.0, step=5.0):
    """Fill stitch: short staggered stitches in rows."""
    s = xx*np.cos(angle)+yy*np.sin(angle); t = -xx*np.sin(angle)+yy*np.cos(angle)
    r = np.floor(t/row); ft = t/row-r
    pos = (s + r*step)/length; fs = pos-np.floor(pos)
    prof = np.sin(np.pi*ft).clip(0)**0.6 * np.where(fs < 0.09, 0.35, 1.0) * (0.9+0.1*np.sin(np.pi*fs))
    return prof, r*131+np.floor(pos)

def build(slug):
    flat = Image.open(f'{OUT}/{slug}.png').convert('RGBA')
    sm = int(round(N*S)); off = (N-sm)//2
    src = Image.new('RGBA', (N, N)); src.paste(flat.resize((sm, sm), Image.LANCZOS), (off, off))
    a = np.asarray(src).astype(np.float32)/255; rgb = a[..., :3]
    inner = RR < R_B1-3
    # palette = most frequent exact colours inside the patch
    q = (rgb[inner]*255).round().astype(np.int32); keys = q[:, 0]*65536+q[:, 1]*256+q[:, 2]
    u, cnt = np.unique(keys, return_counts=True); top = u[np.argsort(-cnt)][:8]
    pal = np.stack([top//65536, (top//256) % 256, top % 256], 1).astype(np.float32)/255
    pal = pal[[i for i in range(len(pal)) if cnt[np.argsort(-cnt)][i] > 400]]
    keep = []
    for p in pal:
        if all(np.abs(p-k).max() > 0.06 for k in keep): keep.append(p)
    pal = np.array(keep)
    backing = pal[0]
    # nearest NON-backing colour, then keep it if the pixel is >35% of the way from backing to it
    # (preserves thin anti-aliased lettering after the resize)
    fgp = pal[1:]; dvec = fgp-backing
    t = ((rgb[..., None, :]-backing)*dvec).sum(-1)/np.maximum((dvec**2).sum(-1), 1e-6)
    proj = backing+t.clip(0, 1)[..., None]*dvec
    err = ((rgb[..., None, :]-proj)**2).sum(-1)
    best = err.argmin(-1); tb = np.take_along_axis(t, best[..., None], -1)[..., 0]
    lab = np.where(tb > 0.35, best+1, 0)
    d = np.zeros((N, N, 1), np.float32)
    border_col = rgb[(RR > R_B1+6) & (RR < R_B0-6)].mean(0)
    alb = np.zeros((N, N, 3), np.float32); H = np.zeros((N, N), np.float32)
    # --- background tatami fill
    tp, tid = tatami(np.radians(30)); bgmask = inner & (lab == 0)
    jit = (h1(tid)-0.5)*0.08
    alb[bgmask] = (backing*(0.82+0.3*tp[..., None]+jit[..., None]))[bgmask]
    H[bgmask] = (0.18+0.05*tp)[bgmask]
    # --- satin / fill regions for every non-background colour
    fg = inner & (lab != 0)
    comps = []
    for ci in range(1, len(pal)):
        lbl, n = ndi.label(fg & (lab == ci))
        sl = ndi.find_objects(lbl)
        for k in range(1, n+1): comps.append((ci, lbl, k, sl[k-1]))
    for k, (ci, lbl, kk, sl) in enumerate(comps):
        m = lbl == kk
        if m.sum() < 12: continue
        ys, xs = np.nonzero(m); col = pal[ci]
        dist = ndi.distance_transform_edt(np.pad(m, 1))[1:-1, 1:-1]
        width = 2*dist[m].max()
        if len(xs) > 2:
            cov = np.cov(np.stack([xs, ys]).astype(np.float32)); w, v = np.linalg.eigh(cov)
            major = np.arctan2(v[1, 1], v[0, 1])
        else: major = 0
        if width > 70:      # too wide for satin -> tatami fill in thread colour
            prof, sid = tatami(major+np.pi/2, row=3.6, length=16, step=6); base_h = 0.42
        else:               # satin: strands run ACROSS the shape (perpendicular to its long axis)
            prof, sid = satin(major+np.pi/2); base_h = 0.50
        ang = major+np.pi/2
        sheen = 0.86+0.26*abs(np.sin(ang-np.radians(-50)))            # anisotropic sheen per stitch direction
        strand = 0.94+0.12*h1(sid+k*17)
        bevel = 1-np.exp(-dist/5.0)
        lum = (0.74+0.34*prof)*strand*sheen
        alb[m] = (col*lum[..., None]).clip(0, 1)[m]
        H[m] = (base_h*bevel+0.18+0.08*prof*bevel)[m]
    # anti-aliased gaps between regions: dark thread gaps
    # --- merrowed border: wrapped diagonal overlock stitches around a rolled edge
    bm = (RR >= R_B1-3) & (RR <= R_B0)
    arc = PHI*R_B0; rr = (RR-R_B1)/(R_B0-R_B1)
    uu = arc + (RR-R_B1)*1.1; per = 7.0
    sidb = np.floor(uu/per); fb = uu/per-sidb
    profb = np.sin(np.pi*fb).clip(0)**0.8
    tube = np.sqrt(np.clip(1-(2*rr-1)**2, 0, 1))
    strand = 0.92+0.16*h1(sidb)
    alb[bm] = (border_col*(0.45+0.6*profb*tube+0.1*tube)[..., None]*strand[..., None]).clip(0, 1)[bm]
    H[bm] = (0.55+0.45*tube*(0.85+0.15*profb))[bm]
    # --- twill backing visible at the outer edge
    tw = (RR > R_B0) & (RR <= R_TW)
    tt = ((xx+yy)/3.0) % 1.0; ww = (np.floor(xx/2)+np.floor(yy/2)) % 2
    twc = hx(TWILL[slug])
    alb[tw] = (twc*(0.8+0.25*np.sin(np.pi*tt)[..., None]*(0.8+0.2*ww[..., None])))[tw]
    H[tw] = (0.08+0.03*np.sin(np.pi*tt))[tw]
    alpha = np.clip(R_TW+0.5-RR, 0, 1)
    # --- lighting from height
    Hs = ndi.gaussian_filter(H, 0.7)*14.0
    gy, gx = np.gradient(Hs)
    nrm = np.stack([-gx, gy, np.ones_like(gx)], -1); nrm /= np.linalg.norm(nrm, axis=-1, keepdims=True)
    ndl = (nrm@LIGHT).clip(0)
    shade = 0.45+0.55*ndl/LIGHT[2]
    hvec = LIGHT+np.array([0, 0, 1]); hvec /= np.linalg.norm(hvec)
    spec = (nrm@hvec).clip(0)**40*0.18
    ao = 1-0.35*np.clip(ndi.gaussian_filter(H, 6)-H, 0, 1)*3
    col = (alb*shade[..., None]*ao[..., None]+spec[..., None]).clip(0, 1)
    rgba = np.dstack([col, alpha])
    ns = Image.fromarray((rgba*255).astype(np.uint8), 'RGBA')
    ns.save(f'{OUT}/{slug}-patch-noshadow.png')
    # shadow
    sh = Image.fromarray((alpha*255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(9))
    sha = np.zeros((N, N), np.float32); sa = np.asarray(sh).astype(np.float32)/255
    sha[10:, 6:] = sa[:-10, :-6]*0.55
    outa = alpha+sha*(1-alpha)
    outc = (col*alpha[..., None])/np.maximum(outa, 1e-6)[..., None]
    Image.fromarray((np.dstack([outc, outa])*255).astype(np.uint8), 'RGBA').save(f'{OUT}/{slug}-patch.png')
    # normal + height (aligned to noshadow)
    nm = (nrm*0.5+0.5)*255; nm[alpha <= 0] = (128, 128, 255)
    Image.fromarray(nm.round().astype(np.uint8), 'RGB').save(f'{OUT}/{slug}-patch-normal.png')
    Image.fromarray((np.clip(H, 0, 1)*255).astype(np.uint8), 'L').save(f'{OUT}/{slug}-patch-height.png')

CREWS = ['code-e', 'kogarasumaru', 'volt', 'rust-claw',   # 'team-storm' = alias slug (build it explicitly)
         'anubis', 'static-angels', 'sleeping-forest', 'behemoth', 'genesis', 'tool-toul-to']
if __name__ == '__main__':
    import sys
    for c in ([a for a in sys.argv[1:] if a != '--sheet-only'] if len(sys.argv) > 1 else CREWS): build(c); print('patched', c)
    sheet = Image.new('RGBA', (5*420, 2*420), (40, 40, 48, 255))
    for i, k in enumerate(CREWS):
        if os.path.exists(f'{OUT}/{k}-patch.png'):
            sheet.alpha_composite(Image.open(f'{OUT}/{k}-patch.png').resize((400, 400), Image.LANCZOS), (i % 5*420+10, i//5*420+10))
    sheet.save(f'{OUT}/logos-contact-sheet.png')
