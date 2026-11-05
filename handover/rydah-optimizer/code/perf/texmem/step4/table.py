# Static GPU-MB estimate (no headset): RGBA8 4 B/px, ETC1S->ETC2 RGB 0.5 B/px, UASTC->ASTC4x4 1 B/px, x4/3 mips. Per r128 KTX2Loader FORMAT_OPTIONS on Quest (astc+etc2).
import subprocess,re,os,csv
C='/workspace/skyrydahs-characters/'; V='/workspace/v3build/'
def tex(p):
    o=subprocess.run(['python3',V+'tools/glb_inspect.py',p],capture_output=True,text=True).stdout
    r=[]
    for m in re.finditer(r'tex (\S+)\s+(\d+)x(\d+) (\S+)\s.*?\[([^\]]+)\]',o):
        n,w,h,f,s=m.groups(); w,h=int(w),int(h); bpp=0.5 if 'etc1s' in f else (1 if 'ktx2' in f else 4); r.append((n,w,h,f,s,w*h*bpp*4/3/1048576))
    return r
rows=[('Ikki (player cap, IKKI_URL default)','meshy/ikki-meshy-skate.quest-draco.glb','meshy/ikki-meshy-skate.s4-ktx2.glb',True),
      ('Caali G (default player)','wardrobe/riders/caali-g.nonormal.glb','wardrobe/riders/caali-g.nonormal.ktx2.glb',True)]
rows+=[(f'crew {c}',f'{c}/{c}-rider.quest.glb',f'{c}/{c}-rider.s4-ktx2.glb',True) for c in ['anubis','behemoth','genesis','kogarasumaru','sleeping-forest','static-angels','tool-toul-to']]
rows+=[('WITHHELD_CHAR NPC (local-only)','WITHHELD_CHAR/WITHHELD_CHAR-npc.glb','WITHHELD_CHAR/WITHHELD_CHAR-npc.s4-ktx2.glb',True),('WITHHELD_CHAR rider (?player=WITHHELD_CHAR, not at spawn by default)','WITHHELD_CHAR/WITHHELD_CHAR-rider.glb','WITHHELD_CHAR/WITHHELD_CHAR-rider.s4-ktx2.glb',False)]
print('| asset | before file -> after file | textures after | GPU MB before | GPU MB after | disk MB before | disk MB after | at spawn |'); print('|---|---|---|---|---|---|---|---|')
tb=ta=0
for lab,b,a,sp in rows:
    B=tex(C+b); A=tex(C+a)
    if 'caali-g' in b: B=[x for x in B if x[4]!='normal']  # nonormal has none anyway
    gb=sum(x[5] for x in B); ga=sum(x[5] for x in A)
    if sp: tb+=gb; ta+=ga
    print(f"| {lab} | {b} -> {os.path.basename(a)} | {', '.join(f'{x[0]} {x[1]}x{x[2]} {x[3]}' for x in A)} | {gb:.2f} | {ga:.2f} | {os.path.getsize(C+b)/1048576:.2f} | {os.path.getsize(C+a)/1048576:.2f} | {'yes' if sp else 'no'} |")
print(f'| **characters at spawn** | | | **{tb:.2f}** | **{ta:.2f}** | | | |')
