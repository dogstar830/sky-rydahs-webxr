# Crew NPC riders -> Draco "<crew>-rider.quest.glb" (Quest pass; Draco decodes to Float32 so riders.js rMerge/morph code is safe;
# do NOT use meshopt/KHR_mesh_quantization for riders: rMerge concatenates raw attribute arrays and would collapse quantized parts).
# ?crew=orig -> original GLBs. The Code:E/Caali player rider is untouched. Idempotent. Run after patch_draco.py (needs the Draco hook).
import os; f=os.environ.get('SR_HTML','/workspace/v3build/sky-rydahs-v3-ikki.html'); src=open(f).read()   # SR_HTML: build copies write their own html (Ani build rule 09:48)
if 'SR_CREW_GLB' in src: print("patch_crew_quest: already applied"); raise SystemExit
A='CHAR_BASE+cr.dir+"/"+cr.file+"-rider.glb",{wheelGlow:new THREE.Color(g.color)'
assert src.count(A)==1, src.count(A)
src=src.replace(A,'SR_CREW_GLB(cr),{wheelGlow:new THREE.Color(g.color)')
B='const CHAR_BASE=(new URLSearchParams(location.search).get("chars"))||"skyrydahs-characters/";'
assert src.count(B)==1
src=src.replace(B,B+'\nconst SR_CREW_Q=new Set(["anubis","behemoth","genesis","kogarasumaru","sleeping-forest","static-angels","tool-toul-to"]);\nconst SR_CREW_GLB=cr=>CHAR_BASE+cr.dir+"/"+cr.file+((new URLSearchParams(location.search).get("crew")==="orig"||!SR_CREW_Q.has(cr.dir))?"-rider.glb":"-rider.quest.glb"); // patch_crew_quest (only crews with a .quest.glb)')

# ---- rider audit fixes (Rydah Rigger, 2026-10-29; lead-approved): shared Meshy skate for crew NPCs, Caali G default player + height ref
def rep(a,b):
    global src; assert src.count(a)==1,(src.count(a),a[:80]); src=src.replace(a,b)
# 1) crew NPC riders: collect the toon *_skates parts instead of merging them; attach the shared black-shell Meshy AT (jackets.js crewSkates)
rep("if(m) (levels[m[1]]=levels[m[1]]||{body:[],glow:[]})[m[2]==='glow'?'glow':'body'].push(o); }",
    "if(m&&m[2]==='skates'&&!fp&&typeof SR_SKATE!=='undefined'&&SR_SKATE.on()) (root.userData._toonSk=root.userData._toonSk||[]).push(o); else if(m&&m[2]==='glow'&&!fp&&!opts.vr&&typeof srGlowToBody==='function'&&srGlowToBody(root,o)) (levels[m[1]]=levels[m[1]]||{body:[],glow:[]}).body.push(o); else if(m) (levels[m[1]]=levels[m[1]]||{body:[],glow:[]})[m[2]==='glow'?'glow':'body'].push(o); }")
rep("if(!/nojacket/.test(location.search)) try{ crewJacket(root,opts.crewName,fp); }",
    "if(root.userData._glowMerged){ const E=sh.slots.uSlotEmi.value; E[RSLOTS.indexOf('wheelGlow')]=Math.max(E[RSLOTS.indexOf('wheelGlow')],SR_GLOW_EMI); E[RSLOTS.indexOf('glow2')]=Math.max(E[RSLOTS.indexOf('glow2')],SR_GLOW_EMI); }\n  if(!fp&&root.userData._toonSk) try{ const cr=CREWS.find(q=>q.crew===opts.crewName); await crewSkates(root,cr?crewBrand(cr.garage).glow:c.wheelGlow,cr&&cr.garage); }catch(e){ console.warn('crew skates failed',e); }\n  if(typeof srDetailInstall==='function') srDetailInstall(root);\n  if(!/nojacket/.test(location.search)) try{ crewJacket(root,opts.crewName,fp); }")
# 2) Caali G (wardrobe/riders/caali-g.glb) is the default player + height reference; Forge caali/caali-rider.glb stays on disk,
#    loaded only with ?player=forge or as a failure fallback
rep('const PLAYER_MODE=(new URLSearchParams(location.search).get("player")||"").toLowerCase();',
    'const PLAYER_MODE=(new URLSearchParams(location.search).get("player")||"caali").toLowerCase(); // default player = Caali G (wardrobe); ?player=forge -> old Forge Caali\n'
    "const SR_CAALI_REF_H=1.916; // Caali G height reference (the Forge Caali bbox height Caali G was fitted at, so every rider keeps its scale)")
FB='const fr=await loadRiderR128(Ride.group,CHAR_BASE+cr.dir+"/"+cr.file+"-rider.glb",{wheelGlow:0xffd700},Object.assign({defaults:cr.defaults,crewName:cr.crew},cr.opts));'
rep('const fr=await loadRiderR128(ref,CHAR_BASE+cr.dir+"/"+cr.file+"-rider.glb",{wheelGlow:0xffd700},Object.assign({defaults:cr.defaults,crewName:cr.crew},cr.opts)); RIDERS.ref={r:fr,holder:ref,h:riderHeight(fr)};',
    'RIDERS.ref={r:null,holder:ref,h:SR_CAALI_REF_H}; // Caali G = height reference (Forge caali-rider.glb not loaded)')
rep('catch(e){ console.warn("wardrobe player failed, falling back to Forge Caali: "+(e&&e.message||e)); ref.remove(fr); Ride.group.add(fr); RIDERS.player=fr;',
    'catch(e){ console.warn("wardrobe player failed, falling back to Forge Caali: "+(e&&e.message||e)); '+FB+' RIDERS.player=fr;')
rep('const ref=new THREE.Group(); ref.visible=false; scene.add(ref); const fr=await loadRiderR128(ref,CHAR_BASE+cr.dir+"/"+cr.file+"-rider.glb",{wheelGlow:0xffd700},Object.assign({defaults:cr.defaults,crewName:cr.crew},cr.opts));\n          RIDERS.ref={r:fr,holder:ref,h:riderHeight(fr)};',
    'const ref=new THREE.Group(); ref.visible=false; scene.add(ref); RIDERS.ref={r:null,holder:ref,h:SR_CAALI_REF_H}; // Caali G height reference')
rep('catch(e){ console.warn("ikki player failed, falling back to Caali: "+(e&&e.message||e)); ref.remove(fr); Ride.group.add(fr); RIDERS.player=fr;',
    'catch(e){ console.warn("ikki player failed, falling back to Caali: "+(e&&e.message||e)); '+FB+' RIDERS.player=fr;')
# 3) Caali G wears her own gold phoenix back patch (jackets.js srCaaliGPatch) instead of the shared codee atlas cell
rep("patch=jacketDecal(opt.crew||'karasu',1);",
    "patch=(opt.key==='caali-g'&&typeof srCaaliGPatch==='function')?srCaaliGPatch():jacketDecal(opt.crew||'karasu',1);")

# ---- Rider roster (Rydah Rigger 2026-10-30): Anika (Code : E). available:false -> never fetched (no 404), not offered; ?player=anika -> Caali G + console note
rep('const PLAYER_MODE=(new URLSearchParams(location.search).get("player")||"caali").toLowerCase();',
    """const SR_ROSTER={ caali:{ key:'caali', name:'Caali G', available:true },
  anika:{ key:'anika', name:'Anika', crew:'codee' /* Code : E with Caali G (Oliver 2026-10-30). Gr8yzone is Caali's shirt brand, not a crew */, glow:0xffd700, wheel:0xffd700, accent:0xff5fa2, url:CHAR_BASE+'anika/'+(/[?&]texfull=1/.test(location.search)?'anika-rider.glb':'anika-rider.draco-webp.glb'), npc:CHAR_BASE+'anika/anika-npc.draco-webp.glb', npcQuest:CHAR_BASE+'anika/anika-npc.draco-webp.glb', /* Optimizer 08:50 tiers: draco-webp default; the SR_KTX2 gate/loader is now in the build (?ktx2=1), and its SR_KTX2.map rewrites anika-rider/anika-npc .draco-webp.glb -> .opt-ktx2.glb under ?ktx2=1 (Optimizer); without the gate she loads draco-webp */ feel:'PROPOSED', available:true /* Oliver approved 2026-10-30 (via Ani) */, status:'available' } };
const PLAYER_MODE=(q=>SR_ROSTER[q]&&!SR_ROSTER[q].available?(console.info('[roster] '+SR_ROSTER[q].name+': '+SR_ROSTER[q].status+' -> playing Caali G'),'caali'):q)((new URLSearchParams(location.search).get("player")||"caali").toLowerCase());""")
rep("const RIDERS={ player:null, fp:null, npcs:[] };",
    "if(typeof WARDROBE_RIDERS!=='undefined'&&SR_ROSTER.anika.available&&WARDROBE_RIDERS.caali) WARDROBE_RIDERS.anika=Object.assign({},WARDROBE_RIDERS.caali,{ name:'Anika', crew:'codee', url:SR_ROSTER.anika.url, key:'anika' }); /* back patch = Code : E cell in her atlas (codee) */ (()=>{ /* rider select (title screen): available roster entries -> reload with ?player=<key> */ const mk=()=>{ if(document.getElementById('srRiderSel')) return; const d=document.createElement('div'); d.id='srRiderSel'; d.style.cssText='position:fixed;left:50%;bottom:8%;transform:translateX(-50%);z-index:9999;display:flex;gap:12px;font:600 16px system-ui';   for(const k in SR_ROSTER){ const R=SR_ROSTER[k]; if(!R.available) continue; const b=document.createElement('button'); b.textContent=R.name; b.dataset.key=k; const on=PLAYER_MODE===k; b.style.cssText='padding:10px 18px;border-radius:8px;border:2px solid #ffd700;cursor:pointer;color:'+(on?'#000':'#ffd700')+';background:'+(on?'#ffd700':'rgba(0,0,0,.6)');     b.onclick=e=>{ e.stopPropagation(); const u=new URL(location.href); u.searchParams.set('player',k); location.href=u.toString(); }; d.appendChild(b); }   document.body.appendChild(d); setInterval(()=>{ d.style.display=(typeof State!=='undefined'&&State.mode==='ride')?'none':'flex'; },250); };   if(document.body) mk(); else addEventListener('DOMContentLoaded',mk); })();\nconst RIDERS={ player:null, fp:null, npcs:[] };")
# NPC ground (Rigger 09:2x; mirrors riders.js): crew NPC roots on WORLD_GROUND at spawn instead of y 0 (asphalt top is 0.01)
rep("n.ph+=dt; if(n.mode===0){ const a=n.ph*.45; n.holder.position.set(cx+Math.cos(a)*3.2,0,cz+Math.sin(a)*3.2);",
    "if(n.gy===undefined){ let g=null; try{ g=typeof WORLD_GROUND==='function'?WORLD_GROUND(cx,cz,.5):null; }catch(e){} n.gy=g&&isFinite(g.y)&&Math.abs(g.y)<1.5?g.y:0; }   /* Rigger: NPC root on rendered asphalt, once at spawn */ n.ph+=dt; if(n.mode===0){ const a=n.ph*.45; n.holder.position.set(cx+Math.cos(a)*3.2,n.gy,cz+Math.sin(a)*3.2);")
rep("else { n.holder.position.set(cx,0,cz);","else { n.holder.position.set(cx,n.gy,cz);")
rep('sub:"RIDER: CAALI  ·  PALMA CITY  ·  AIR TRECK"', 'sub:"RIDER: "+((typeof SR_ROSTER!=="undefined"&&SR_ROSTER[PLAYER_MODE])||{name:"Caali G"}).name.toUpperCase()+"  ·  PALMA CITY  ·  AIR TRECK"')   # title shows the selected rider (Rigger 09:2x)
open(f,'w').write(src); print("patch_crew_quest: NPC crew riders -> .quest.glb (?crew=orig fallback)")
