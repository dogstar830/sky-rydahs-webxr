# patch_crewhouse_kit (Palma Builder): inline crewhouse_kit.js (shared crew garage interior kit) as its own <script> before </body>.
# Idempotent; unique anchor; run after the bases/crew patches and before patch_world_perf.
# Also registers Volt (The 98 charging station) + Rust Claw (Cove salvage shed) garage entries (Oliver 2026-11-05).
import sys
f=sys.argv[1] if len(sys.argv)>1 else '/workspace/v3build/sky-rydahs-v3-ikki.html'; src=open(f).read()
# ---- early: inject Volt + Rust Claw into PALMA.garages (before createCity) ----
G_OLD='    {crew:"forest",name:"SLEEPING FOREST",pos:[40,-275],face:"S",color:"#7CB342",dark:0xe8e8e0},\n  ],'
G_NEW='    {crew:"forest",name:"SLEEPING FOREST",pos:[40,-275],face:"S",color:"#7CB342",dark:0xe8e8e0},\n    {crew:"volt",name:"VOLT",pos:[288,-74],face:"S",color:"#ff2fa0",dark:0x1a0a14},\n    {crew:"rustclaw",name:"RUST CLAW",pos:[-165,-88],face:"S",color:"#ff6a1a",dark:0x1a1008},\n  ],'
# Match the 8-garage forest close only (Systems TURF placeholders also mention volt/rustclaw elsewhere)
if src.count(G_OLD)==1:
    src=src.replace(G_OLD,G_NEW); print("patch_crewhouse_kit: Volt+RustClaw garage entries into PALMA.garages")
elif src.count(G_NEW)==1 or ('{crew:"volt",name:"VOLT",pos:[288,-74],face:"S",color:"#ff2fa0",dark:0x1a0a14},' in src and G_OLD not in src):
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
