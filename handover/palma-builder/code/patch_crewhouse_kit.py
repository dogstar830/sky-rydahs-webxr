# patch_crewhouse_kit (Palma Builder): inline crewhouse_kit.js (shared crew garage interior kit) as its own <script> before </body>.
# Idempotent; unique anchor; run after the bases/crew patches and before patch_world_perf.
# Also registers Volt (The 98 charging station) + Rust Claw (Cove salvage shed) garage entries (Oliver 2026-11-05).
import sys, re
f=sys.argv[1] if len(sys.argv)>1 else '/workspace/v3build/sky-rydahs-v3-ikki.html'; src=open(f).read()
# ---- early: inject Volt + Rust Claw into PALMA.garages (before createCity) ----
G_OLD='    {crew:"forest",name:"SLEEPING FOREST",pos:[40,-275],face:"S",color:"#7CB342",dark:0xe8e8e0},\n  ],'
G_NEW='    {crew:"forest",name:"SLEEPING FOREST",pos:[40,-275],face:"S",color:"#7CB342",dark:0xe8e8e0},\n    {crew:"volt",name:"VOLT",pos:[288,-74],face:"S",color:"#ff2d95",dark:0x1a0a14},\n    {crew:"rustclaw",name:"RUST CLAW",pos:[-165,-88],face:"S",color:"#ff7a1a",dark:0x1a1008},\n  ],'
# Match the 8-garage forest close only (Systems TURF placeholders also mention volt/rustclaw elsewhere)
if src.count(G_OLD)==1:
    src=src.replace(G_OLD,G_NEW); print("patch_crewhouse_kit: Volt+RustClaw garage entries into PALMA.garages")
elif src.count(G_NEW)==1 or ('{crew:"volt",name:"VOLT",pos:[288,-74],face:"S",color:"#ff2d95",dark:0x1a0a14},' in src and G_OLD not in src):
    print("patch_crewhouse_kit: PALMA.garages already has Volt+RustClaw buildings")
else:
    raise SystemExit("patch_crewhouse_kit: cannot find PALMA.garages forest anchor to inject Volt+RustClaw (G_OLD count=%d)"%src.count(G_OLD))
# gate codes / hints (gates.js owned by Systems; we only append our two crews via string patch)
C_OLD='const GATE_CODES={ codee:"1337", karasu:"8686", static:"4444", behemoth:"6660", anubis:"3000", forest:"2222", genesis:"0001", ttt:"7070" };'
C_NEW='const GATE_CODES={ codee:"1337", karasu:"8686", static:"4444", behemoth:"6660", anubis:"3000", forest:"2222", genesis:"0001", ttt:"7070", volt:"9800", rustclaw:"1984" };'
if 'volt:"9800"' not in src and src.count(C_OLD)==1:
    src=src.replace(C_OLD,C_NEW); print("patch_crewhouse_kit: GATE_CODES volt+rustclaw")
H_OLD='const GATE_HINTS={ codee:"sticky note: 1337 (leet)", karasu:"two crows: 86 86", static:"all channels: 4444", behemoth:"666 and nothing", anubis:"3000 years", forest:"zzzz = 2222", genesis:"born first: 0001", ttt:"tool toul: 7070" };'
H_NEW='const GATE_HINTS={ codee:"sticky note: 1337 (leet)", karasu:"two crows: 86 86", static:"all channels: 4444", behemoth:"666 and nothing", anubis:"3000 years", forest:"zzzz = 2222", genesis:"born first: 0001", ttt:"tool toul: 7070", volt:"the 98: 9800", rustclaw:"salvage year: 1984" };'
if 'volt:"the 98' not in src and src.count(H_OLD)==1:
    src=src.replace(H_OLD,H_NEW); print("patch_crewhouse_kit: GATE_HINTS volt+rustclaw")
# ---- MARINA sign facing (Ani review 2026-11-05): lives in baked base HTML (putSign from world layout / patch4.py, NOT in build chain as a source).
# PlaneGeometry faces +Z; ry=Math.PI made the front face north, so the Cove street view (looking north from Rust Claw) saw the DoubleSide back = mirrored "ANIRAM".
# Flip to ry=0 (face south / +Z) so it reads MARINA from the street. Palma-owned world sign.
M_OLD='putSign("MARINA",10,"#AA00FF",-180,4,-101,Math.PI);'
M_NEW='putSign("MARINA",10,"#AA00FF",-180,4,-101,0); /* Palma: face south so Cove street reads MARINA */'
if src.count(M_OLD)==1:
    src=src.replace(M_OLD,M_NEW); print("patch_crewhouse_kit: MARINA facing PI->0 (south)")
elif M_NEW in src or 'putSign("MARINA",10,"#AA00FF",-180,4,-101,0)' in src:
    print("patch_crewhouse_kit: MARINA facing already south")
else:
    print("patch_crewhouse_kit: WARN MARINA putSign not found (count=%d)"%src.count('putSign("MARINA"'))
# ---- CREW_RIVALS from crews.js (Rydah Systems; rivals kept out of CREWS so riders.js skips missing GLBs) ----
# kitTheme reads CREW_RIVALS for Volt/Rust Claw wheelGlow/gold. Inject after the baked CREWS array if missing.
_crews=open('/workspace/v3build/crews.js').read()
_m=re.search(r'const CREW_RIVALS=\[[\s\S]*?\];',_crews)
if not _m: raise SystemExit('patch_crewhouse_kit: CREW_RIVALS not found in crews.js')
RIVALS_JS=_m.group(0)
if 'const CREW_RIVALS=' in src:
    print("patch_crewhouse_kit: CREW_RIVALS already in html")
else:
    # Anchor: close of baked CREWS array (8 playable crews; ends before RIDERS comment)
    C_ANCHOR='  {dir:"tool-toul-to",file:"tool-toul-to",crew:"Tool Toul To",garage:"ttt",'
    # find the ]; that closes CREWS after ttt entry
    i=src.find(C_ANCHOR)
    if i<0: raise SystemExit('patch_crewhouse_kit: CREWS ttt anchor missing')
    j=src.find('];', i)
    if j<0: raise SystemExit('patch_crewhouse_kit: CREWS close missing')
    src=src[:j+2]+'\n'+RIVALS_JS+'\n'+src[j+2:]
    print("patch_crewhouse_kit: CREW_RIVALS injected after CREWS")

# ---- kit inline ----
if 'CREWHOUSE KIT (Palma Builder)' in src: print("patch_crewhouse_kit: kit already applied"); open(f,'w').write(src); raise SystemExit
js=open('/workspace/v3build/crewhouse_kit.js').read(); a='</body>'
assert src.count(a)==1,("anchor",src.count(a))
# the kit replaces the old dressBase interiors + the old interior emblem/A-T rack (?oldbase brings them back for A/B)
for x,y in [("if(!/nobase/.test(location.search)) try{ dressBase(G,g,W,col2,col); }","if(/oldbase/.test(location.search)) try{ dressBase(G,g,W,col2,col); } /* patch_crewhouse_kit: kit replaces old interior */"),
            ("  emblem(G.crew,G.color,4,0,2.8,-9.55,0,g);","  if(/oldbase/.test(location.search)) emblem(G.crew,G.color,4,0,2.8,-9.55,0,g); // kit interior"),
            ("  box(.5,2.2,4,0x2a2a2a,-5.3,1.1,-5,g,.03);","  if(/oldbase/.test(location.search)) box(.5,2.2,4,0x2a2a2a,-5.3,1.1,-5,g,.03);")]:
    assert src.count(x)==1,("anchor",x[:50]); src=src.replace(x,y)
for k in range(3):
    x="  for(let k=0;k<3;k++){ box(.4,.3,.6,0x333333,-5.2,.8+k*.6,-6.3+k*1.3,g,.02); box(.42,.06,.62,col,-5.2,.66+k*.6,-6.3+k*1.3,g,0); }"
    if src.count(x)==1: src=src.replace(x,"  if(/oldbase/.test(location.search)) "+x.strip())
src=src.replace(a,'<script>/* patch_crewhouse_kit */\n'+js+'\n</script>\n'+a); open(f,'w').write(src); print("patch_crewhouse_kit: kit inlined")
