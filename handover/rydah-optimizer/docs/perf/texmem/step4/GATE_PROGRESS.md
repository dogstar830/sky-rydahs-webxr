# KTX2 gate progress (Ani integrator)
- 01:42 CDT scratch build /tmp/g.html via /tmp/gbuild (sed copies of all patches, html path -> /tmp/g.html, candidate in place of patch_draco.py). Real html/build_ikki.sh/patch_draco.py untouched. Served via symlink v3build/g_ktx2_scratch.html -> /tmp/g.html.
- 02:21 CDT rebuilt /tmp/g.html to pick up facades.js KTX2 path (world_ktx2 refs: 3).
- smoke CORE default (02:21-02:26): 22/22 PASS, 0 console errors, 0 404s.
- smoke CORE ?ktx2=1 (02:28-02:30): CRASH — "page loaded" returned null, then ReferenceError: State is not defined (game never initialised).
- perf_overlay default (02:30-02:34): 15/15, texture 248.7 MB (49 uploaded), draws 93 scene.
- perf_overlay ?ktx2=1 (02:37-03:02): HUNG, killed by 1500 s timeout (EXIT 124), no output -> RIDERS.ready never true.
- perf_seed7 default (03:05-03:07): street 87/88, causeway 107, b98 95/94, aerial 100/99 calls (night/day); peak 107.
- seed7 ?ktx2=1 (03:09-03:12): CRASH, ReferenceError garages is not defined (game not initialised). shot_off 03:20-03:23 OK: shots/hero/ktx2_rider_off.png, ktx2_facade_off.png, 0 errors, 0 404s, facades jpg (default).
- shot_on ?ktx2=1 (03:25-03:28): CRASH, State not defined -> no ktx2_rider_on.png / ktx2_facade_on.png.
- probe ?ktx2=1 (03:39-03:40): ROOT CAUSE pageerror "Cannot set properties of undefined (setting 'k2')" at facades.js:6 `t.userData.k2=k` — THREE r128 Texture has no userData, so the FACADE IIFE throws and the rest of init dies ("garages is not defined"). Only fetches: libs/ktx2/KTX2Loader.classic.js; NO world_ktx2/facade_* requests, 0 404s.
- Note: pre-facades build (01:42) smoke ?ktx2=1 = 22/22 PASS, 0 console errors, 0 404s -> the loader candidate itself boots; the break is the 02:16 facades.js change.
- VERDICT 03:41 CDT: RED. Fix suggestion for Palma: `(t.userData||(t.userData={})).k2=k` or store on a closure var. Symlink removed.
- 03:48 CDT round 2: rebuilt /tmp/g.html from current sources after Palma's 03:49 facades fix; rerunning ?ktx2=1 side only.
- smoke_ktx done: 404s: [] SUMMARY 22/22 pass EXIT 0 03:59 
- po_ktx done: TEXMB overlay 186.4 MB (uploaded 50, skipped 27, GL 72) vs audit snippet 250.0 MB perf_overlay.py: 14/15 passed EXIT 0 04:03 
- seed_ktx done: street_night 89 291360 causeway_night 107 249759 b98_night 94 231775 aerial_night 99 256493 street_day 89 291360 causeway_day 109 249061 b98_day 93 231689 aerial_day 98 256407 EXIT 0 04:22 
- shot_on done: 1024, "src": ""}, {"compressed": true, "w": 2048, "h": 1024, "src": ""}], "frames_waited": 172, "errs": [], "404": [], "ktx_fetches": ["&tier=hd&ktx2=1", "Concrete034_Color.ktx2", "Concrete034_NormalGL.ktx2", "Concrete034_Roughness.ktx2", "Concrete046_Color.ktx2", "Concrete046_NormalGL.ktx2", "Concrete046_Roughness.ktx2", "KTX2Loader.classic.js", "PaintedMetal004_Color.ktx2", "PaintedMetal004_NormalGL.ktx2", "PaintedMetal004_Roughness.ktx2", "WITHHELD_CHAR-npc.s4-ktx2.glb", "anubis-rider.s4-ktx2.glb", "asphalt_albedo.ktx2", "asphalt_normal.ktx2", "asphalt_rough.ktx2", "basis_transcoder.js", "basis_transcoder.wasm", "behemoth-rider.s4-ktx2.glb", "facade_albedo.ktx2", "facade_nr.ktx2", "genesis-rider.s4-ktx2.glb", "ikki-meshy-skate.s4-ktx2.glb", "kogarasumaru-rider.s4-ktx2.glb", "sleeping-forest-rider.s4-ktx2.glb", "static-angels-rider.s4-ktx2.glb", "tool-toul-to-rider.s4-ktx2.glb"]} EXIT 0 04:28 
- Shots reviewed: rider on vs off look the same (no visible loss). Facade shot: facades textured. Unseeded world layout differs between runs, and the ?ktx2=1 shot has one all-black NPC silhouette (unconfirmed).
- seed7 ?ktx2=1 peak 109 (causeway_day) > default 107; street 89 > 87. Rule broken -> RED. Symlink removed.
## Round 3 (04:38 CDT): rebuilt /tmp/g.html from current sources; queue smoke_ktx, seed default+ktx (with no-riders count), tool-toul-to probe, seed=1 shots.
- smoke ?ktx2=1 (04:39-04:43): 22/22 PASS, 0 console errors, 404s []. Caali hd.ktx2 request check queued (caali_req), waiting on .testlock held by skatev2 job since 04:49.
- 05:41 CDT BLOCKED: .testlock held since 04:49 by pid 835963 (/tmp/skv2_wait.sh: takes lock then 'sleep 99999'), not mine, not killed. Pending in my queue (still waiting, auto-resumes on release): caali_req, seed_def, seed_ktx (minus-riders), ttt probe+shot, seed=1 shots.
## Final step (09:06 CDT): rebuilt /tmp/g.html (Ikki s4-ktx2 regenerated POT); queue ikki on/off probe+shots, smoke ktx.
- ik_on done 09:10
- ik_off done 09:16
- smoke_ktx: 404s: [] SUMMARY 22/22 pass EXIT 0 09:23 
- Ikki NPC ?ktx2=1 probe (09:07-09:10): on camera; Ikki_LOD0/1/2 MeshStandardMaterial, compressed, format 36492 (BPTC/BC7), 2048x2048, 12 mips, uploaded; LOD0 visible (LOD1/2 hidden by LOD). 0 404s, no errors. Shot ktx2_ikki_npc_on.png textured (not black), matches ktx2_ikki_npc_off.png.
- VERDICT 09:31 CDT: GREEN for swapping candidate into build_ikki.sh (swap not done). Symlink removed.
