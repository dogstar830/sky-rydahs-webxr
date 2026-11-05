# patch_crewhouse_kit (Palma Builder): inline crewhouse_kit.js (shared crew garage interior kit) as its own <script> before </body>.
# Idempotent; unique anchor; run after the bases/crew patches and before patch_world_perf.
import sys
f=sys.argv[1] if len(sys.argv)>1 else '/workspace/v3build/sky-rydahs-v3-ikki.html'; src=open(f).read()
if 'CREWHOUSE KIT (Palma Builder)' in src: print("patch_crewhouse_kit: already applied"); raise SystemExit
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
