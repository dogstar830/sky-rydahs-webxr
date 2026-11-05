# Anika v2 Quest check (rigged, skate stripped): Draco + KTX2
Rydah Optimizer, 2026-10-30 03:27 CDT. Static checks only: no headset, no browser, no tests. Source GLBs untouched (sha256 rider 00089214…, npc 72d4c7e3…, mtimes 03:23 unchanged). Caali G v2 not touched (on hold).

## 1. Inspection of the 6 inputs (skyrydahs-characters/anika/)
| file | disk | LOD0/1/2 tris | prims/mats | textures | tex GPU (all LODs) | geometry comp. |
|---|---|---|---|---|---|---|
| anika-rider.glb | 16.76 MB (15.98 MiB) | 104,965 / 33,369 / 11,142 | 1 prim per LOD, 3 mats (AnikaAtlas_LOD0/1/2) | webp: LOD0 col 2048, nrm 1024, orm 1024; LOD1 1024/512/512; LOD2 512/256/256 | 42.0 MB | none |
| anika-rider.quest.glb | 18.03 MB | 104,957 / 33,369 / 11,142 | same | same webp | 42.0 MB | none |
| anika-rider.quest-ktx2.glb | 18.60 MB | 104,957 / 33,369 / 11,142 | same | KTX2: col ETC1S, ORM ETC1S, nrm UASTC+zstd, same dims | 7.88 MB | none |
| anika-npc.glb | 5.61 MB | 23,772 / 11,134 / 4,390 | 1 prim per LOD, 2 mats (AnikaAtlas_NPC0 for LOD0+LOD1, AnikaAtlas_LOD2) | webp: NPC0 col/nrm/orm 1024; LOD2 512/256/256 | 18.0 MB | none |
| anika-npc.quest.glb | 6.03 MB | same | same | same webp | 18.0 MB | none |
| anika-npc.quest-ktx2.glb | 6.66 MB | same | same | KTX2 (as above) | 3.38 MB | none |

All 6: attributes POSITION/NORMAL/TEXCOORD_0/_WC/_WA/WEIGHTS_0 float32, JOINTS_0 uint8, COLOR_0 uint16-normalized (float32 in .quest/.quest-ktx2); no morph targets; no KHR_mesh_quantization/Draco/meshopt; extensions only EXT_texture_webp or KHR_texture_basisu. 1 skin, **107 joints** in every file (91 shared + 16 spring). Spring chains (node extras `spring`, lods [0,1,2]): Anika_BraidL_01..05, Anika_BraidR_01..05, Anika_Skirt_00..05. Note: the .quest ("2")/.quest-ktx2 copies have LOD0 104,957 tris (8 fewer than the source) and are *larger* than the source (no geometry compression).

## 2. Outputs (quest_pipeline.py --suffix opt --geometry draco --ktx2, from the uncompressed rigged source)
| output | disk | notes |
|---|---|---|
| anika/anika-rider.opt-ktx2.glb | **3,748,088 B (3.75 MB / 3.57 MiB)** | caps 2048/1024/1024; tex GPU 7.88 MB all LODs, **6.0 MB LOD0 set** |
| anika/anika-npc.opt-ktx2.glb | **2,003,000 B (2.00 MB / 1.91 MiB)** | caps 1024/1024/1024; tex GPU 3.38 MB all LODs, 3.0 MB NPC0 set |
| (side products) anika-rider.opt.glb 3.17 MB, anika-npc.opt.glb 1.37 MB | | Draco + webp; the pipeline always writes these |
Source: anika-rider.glb / anika-npc.glb (not the .quest-ktx2 copies); KTX2 encodings came out identical to the existing .quest-ktx2 textures. Draco edgebreaker, 16-bit position (pipeline default); no meshopt.

## 3. Verification (decoded with draco3dgltf via glTF-Transform, vs source)
- All attributes decode to Float32 (JOINTS_0 uint8; COLOR_0 now float32), _WC/_WA present on every LOD, same metre space.
- Bounding boxes match within 0.008 mm. Vertex match (position + weight map): **max |ΔPOSITION| 0.011 mm** on all 6 meshes, |Δ_WC| 0.001 mm, |Δ_WA| 0.000 mm, max joint-weight diff 0.0000 (0 verts changed). Tris identical per LOD. Draco dropped 5-19 unreferenced verts per mesh (harmless) and splits ~1-4 % verts at attribute seams.
- No morph targets in source or output. Skin: 107 joints, names identical in order; 16 spring nodes with identical extras.
- gltf-transform validate: **0 errors** on both outputs (warnings are only the validator's known image/ktx2 mimeType/unrecognised-format notes and generated tangents, same as before). 0.011 mm << 1 mm, so no bit increase needed.

## 4. Budgets, before (anika-*.glb source; .quest-ktx2 for KTX2 GPU) → after (.opt-ktx2)
| item | budget | rider before | rider after | NPC before | NPC after |
|---|---|---|---|---|---|
| LOD0 tris (no skate) | P 100-120k / NPC ≤30k | 104,965 PASS | 104,965 PASS | 23,772 PASS (Forge: 30k cap is body-only) | 23,772 PASS |
| draws per drawn LOD | 1 (+shared skate) | 1 PASS | 1 PASS | 1 PASS | 1 PASS |
| disk ≤3 MB | 3 MB | 16.76 FAIL | 3.75 MB **FAIL** (3.57 MiB) | 5.61 FAIL | 2.00 PASS |
| disk (anika doc) | P ≤4 MB / NPC ≤1.5 MB | FAIL | 3.75 **PASS** | FAIL | 2.00 **FAIL** |
| tex GPU KTX2 | P ~5.6 / NPC ~3 MB | 42.0 (webp) FAIL; .quest-ktx2 7.88 WARN | LOD0 set 6.0 WARN, all LODs 7.88 WARN | 18.0 FAIL; 3.38 WARN | NPC0 set 3.0 PASS, all 3.38 WARN |
| tex caps | P 2K col / 1K nrm,ORM; NPC 1K | PASS | PASS | PASS | PASS |
| geometry comp. | Draco | none FAIL | Draco PASS | none FAIL | Draco PASS |
Forge's ~7.9 MB claim is right for all LODs; 5.6 MB assumed a 0.75 B/px 2K colour (2.8+…) – the inspector counts ETC1S 2K at 4.0 MB with mips.

## 5. Problems / asks
- **Rider disk 3.75 MB > 3 MB.** Biggest single item: UASTC+zstd normals (LOD0 882 KB, LOD1 270 KB, LOD2 74 KB = 1.2 MB). Options (Forge/Optimizer): LOD0 normal to ETC1S or UASTC with RDO (`--uastc-rdo`), or drop LOD1/2 normals (−0.34 MB), or a 512 LOD1/2 ORM/normal share. Any one of the first two should get under 3 MB; needs a visual check.
- **NPC disk 2.0 MB vs the doc's ≤1.5 MB** (NPC0 normal UASTC 965 KB). Same fix; or reuse the player atlas when both are on screen.
- GPU 7.88 vs 5.6 target: LOD0 set is 6.0 MB; to hit 5.6 the 2K colour needs to be ≤1.5K or drop mips on LOD2.
- NPC LOD0: Forge confirmed the 30k cap is body-only → PASS.
- .quest/.quest-ktx2 copies are uncompressed and bigger than the source, and LOD0 is 8 tris short of the source: re-generate them from the current source at ship, or replace with .opt-ktx2.
- Runtime: needs DRACOLoader + KTX2Loader (SR_KTX2 not yet in live build).
- Caali G v2: waiting on Rigger (shards).

---
## v2 (03:30-03:36 CDT): normal-map pass + regen from Rigger's symmetric-shoulder sources
Sources now: anika-{rider,npc}.glb (03:30, shoulders ±0.135, new IBMs; IBMs differ from *.presym-20261030-0331.glb by up to 0.0197). Earlier outputs kept as **anika-{rider,npc}.opt-ktx2.v1.glb**.

### Normal-map variants (trial files only in /tmp/anika_nrm/; PSNR vs the source webp normal, RGB, full res)
| variant | LOD0 rider size / PSNR | NPC0 size / PSNR |
|---|---|---|
| UASTC q2 zstd18 (v1) | 903 KB / 38.25 dB | 988 KB / 36.76 dB |
| UASTC RDO λ1.0 zstd20 | 811 KB / 37.61 | 906 KB / 36.24 |
| RDO λ1.5 | 789 KB / 37.04 | 883 KB / 35.78 |
| RDO λ2.0 | 770 KB / 36.45 | 863 KB / 35.27 |
| RDO λ3/5/8 | 740/701/666 KB / 35.3/33.6/32.1 | 832/789/751 KB / 34.3/32.8/31.4 |
| **768² UASTC RDO λ1.0 zstd20 (chosen)** | **490 KB / 34.28 (36.38 encode-only vs 768² ref)** | **542 KB / 32.33 (34.83 encode-only)** |
| 640² RDO λ1.0 | 352 KB / 32.89 | 387 KB / 30.96 |
| 512² UASTC | 251 KB / 30.76 | 267 KB / 29.03 |
| ETC1S q255 (RGB) | 225 KB / 27.08 (blocky in crops) | 252 KB / 26.66 |
ETC1S `--normal-mode` is unusable in r128 (2-channel RG, B=0, needs a shader change). LOD1/LOD2 normals: **UVs are NOT shared** with LOD0 (resized colour atlas PSNR 9-10 dB), so they cannot point at the LOD0 normal; they are **dropped** (LOD1 9 m+, LOD2 14 m+/24 m+).
Crops (face/braids/skirt, decoded normal + N·L lit proxy, no browser/offline render): /tmp/anika_nrm/rider_nrm_crops.png, npc_nrm_crops.png. RDO λ1-2 and 768² are visually indistinguishable from the source at crop scale; ETC1S shows 4×4 blocking on braids.

**~38 dB is not reachable inside the caps**: RDO alone saves ≤15 %. Full-res UASTC (≥37.6 dB) + dropped LOD1/2 normals gives rider 3.30 MB / NPC 1.84 MB (both over). Picked the smallest variant that meets both caps with the highest PSNR: 768² RDO λ1.0 (rider 2.98 MB, NPC 1.48 MB). Alternative tried: Draco qPos14/qGeneric12 with full-res RDO = 3.10 MB (still over; not used, team rule is 16-bit).
Regenerate in one step: **/workspace/v3build/perf/anika_regen.sh** (uses quest_pipeline.py `--suffix opt --geometry draco --ktx2`, then perf/anika_nrm_swap.cjs for the normal swap/drop + Draco 16/16 re-encode; refuses to overwrite).

### v2 outputs (regenerated from the new sources)
| file | size | LOD0 tris | tex GPU (all LODs) |
|---|---|---|---|
| anika/anika-rider.opt-ktx2.glb | **2,981,360 B (2.98 MB) PASS ≤3 MB** | 104,965 | ~7.6 MB (LOD0 set ~5.6) |
| anika/anika-npc.opt-ktx2.glb | **1,480,180 B (1.48 MB) PASS ≤1.5 MB** | 23,772 | ~3.0 MB |
Checks vs the NEW sources: validate 0 errors; 107 joints, names identical; IBMs identical (max diff 0); joint TRS ≤7e-7; 16 spring nodes, extras identical; POSITION/_WC/_WA/NORMAL/UV Float32, max |ΔPOS| 0.011 mm, |Δ_WC| 0.001 mm; weights 0 changed; no morphs.

## Caali G v2 (cleared by Rigger, STAGED only: live caali-g.glb / game files / URLs untouched)
Sources: wardrobe/riders/caali-g-v2.rigged.glb (14.84 MB, LOD0/1/2 104,192/33,082/11,034, 1 prim + 1 atlas mat per LOD, 2K/1K/1K webp), caali-g-v2-hd.rigged.glb (26.91 MB, LOD0 250,300, 4K col/2K nrm+ORM). 91 joints (shared skeleton), **no spring chains** (none expected), no morphs. Attributes: _WC, _WA (no _BM/_SLOT present).
| output | recipe | size | tex GPU |
|---|---|---|---|
| wardrobe/riders/caali-g-v2.opt-ktx2.glb | pipeline player caps 2048/1024/1024 + same normal recipe (LOD0 768² RDO λ1.0, LOD1/2 normal dropped; pipeline-only was 3.48 MB) | **2,695,512 B (2.70 MB)** | ~7.6 MB |
| wardrobe/riders/caali-g-v2-hd.opt-ktx2.glb | pipeline 2048/2048/2048 (desktop HD), full normals | **6,377,108 B (6.38 MB)** | 13.9 MB |
Caali LOD0 normal 768²: 35.95 dB vs 1024 source, 38.02 dB encode-only. Pipeline intermediates in /tmp/caali_opt/.
Checks: validate 0 errors (both); 91 joints identical names, IBMs identical, TRS ≤7e-7; POSITION/_WC/_WA decode to **Float32 in metres** (POSITION y 0.135-1.700; _WC y −0.152..0, same metre scale, no ×100 units bug); max |ΔPOS| 0.012 mm, |Δ_WC| 0.001 mm; weights 0 changed; tris identical.
| budget | caali-g-v2 player before (rigged) | after (.opt-ktx2) | hd after |
|---|---|---|---|
| LOD0 100-120k | 104,192 PASS | PASS | 250,300 n/a (desktop HD) |
| 1 draw per LOD | 1 PASS | 1 PASS | 1 PASS |
| disk ≤3 MB | 14.84 FAIL | 2.70 PASS | 6.38 FAIL vs 3 MB (desktop, no cap given) |
| tex caps 2K/1K/1K | PASS (webp 42 MB GPU) | PASS, KTX2 | 2K/2K/2K as asked |
| Draco | FAIL | PASS | PASS |
Note: _WA is all zero and _WC only spans y −0.152..0 on the body (skates stripped); fine if the runtime reads wheels from the shared skate.

---
## Caali G v2 LIVE slots (08:37-08:50 CDT, Forge ask; Oliver approved)
Waited for `.testlock` (Rydah Systems attacks_full then wallride on /tmp/wkb, which symlinks to the live characters dir) to clear; replaced at 08:48:26 CDT; all live files were >2 min old. Swaps are cp to .tmp + mv (atomic).
wardrobe.js: `noNormal:true` is on the caali entry and is not tier-gated, so the normal map is dropped at runtime on **both** quest and hd tiers (`normalMap:opt.noNormal?null:...`). So normals are stripped in all three outputs. Draco: DRACOLoader is live (patch_draco GLTFLoader trap).

| live file | before | after | md5 after | backup (md5) |
|---|---|---|---|---|
| caali-g.nonormal.glb (default/quest) | 14,840,912 B raw v2 | **2,431,844 B** Draco16 + webp (2K col, 1K ORM, no normal), tex GPU 35.0 MB | 450e571902552d5d90f327a353f58220 | caali-g.nonormal.v2raw-20261030-0848.glb (b92e2383…) |
| caali-g-hd.glb (desktop hd) | 26,905,956 B raw v2 | **4,464,936 B** Draco16 + webp (4K col, 2K ORM, no normal), tex GPU 115 MB | cabe06217f4c295cd4957129989e71cc | caali-g-hd.v2raw-20261030-0848.glb (b1bb5893…) |
| caali-g-hd.ktx2.glb | 7,417,120 B **v1 hd** (stale, 296k LOD0, meshopt) | **4,221,336 B** Draco16 + KTX2 ETC1S (4K col, 2K ORM, no normal), tex GPU 21.6 MB | 81537d9636ea500c022cabe2b88a6581 | caali-g-hd.ktx2.v1-20261030-0848.glb (714772ab…) |
| caali-g.nonormal.ktx2.glb | unchanged, 2,695,512 B | already v2 (md5 = caali-g-v2.opt-ktx2.glb; 91 joints, 104,192/33,082/11,034 tris, IBMs = v2 raw) | 9e73946dbc0c27372ac57f25d6d7ca77 | n/a |
vs v1 default (3.80 MB, meshopt+quantized, 98k LOD0, one 2K atlas 216 KB webp, 21 MB GPU): v2 is **2.43 MB** (−36 %), LOD0 104k, textures are Forge's v2 webp bytes copied as-is (no re-encode → no texture quality loss), only extra is the 1K ORM (+GPU 13.7 MB with LOD1/2 atlases). The v2 default no longer uses KHR_mesh_quantization (float POSITION).
Checks (all 4): validate 0 errors; 91 joints identical names; IBMs identical (0 diff), joint TRS ≤7e-7; POSITION/_WC/_WA Float32 metres (POSITION y 0.135-1.700, _WC y −0.152..0), max |ΔPOS| 0.012 mm, |Δ_WC| 0.001 mm, weights unchanged, tris identical. Not touched: caali-g.glb (?texfull=1, still 14.8 MB raw v2; Forge's call).
Note: caali-g.nonormal.ktx2.glb still carries the 768 LOD0 normal (~490 KB) that runtime drops; stripping it would give ~2.2 MB.

## Anika tiers
- Anika is NOT in wardrobe.js; she's in SR_ROSTER (patch_crew_quest.py, Rigger) and `WARDROBE_RIDERS.anika=Object.assign({},caali,…)` → she inherits **noNormal:true** (normals dropped on every tier).
- **Problem:** Quest UA loads `anika-rider.opt-ktx2.glb` unconditionally, but the SR_KTX2 gate/KTX2Loader is not in the live build → KTX2 textures will fail on Quest. Desktop hd loads the 16.8 MB uncompressed anika-rider.glb. npc/npcQuest are not read anywhere yet.
- New Draco+webp tiers (normals stripped, from the symmetric-shoulder sources): anika/anika-rider.draco-webp.glb **2,849,928 B** (md5 6827307e2719e8317e0448ff9691e4c9), anika/anika-npc.draco-webp.glb **1,086,532 B** (5ba883d0cc9e476eaa8c4bb56b1e8e6d). Validate 0 errors, 107 joints + IBMs identical, 16 springs, 0.011 mm.
- Proposed diff for Rigger: perf/anika_roster_tiers.proposed.diff (default/hd → draco-webp, ?texfull=1 → raw; KTX2 only through the ?ktx2=1 map). Not applied (Rigger's file).
- patch_draco.py.ktx2-candidate (ours, backup .bak-anika-*): map entries anika/anika-{rider,npc}.glb and anika/anika-{rider,npc}.draco-webp.glb → anika/anika-{rider,npc}.opt-ktx2.glb.

## 14-quad chain in XR (static read of sky-rydahs-v3-ikki.html, 08:30 build)
The chain is the **EffectComposer from setupFX() (line 270-275)**: RenderPass (scene → rt) + UnrealBloomPass (high-pass 1 + 5 mips × 2 blur = 10 + composite 1 + copy back 1 = 13 offscreen quads) + GradeShader to canvas (1). DashShader is disabled, edge pass only with ?edge=1. **It does not run in XR:** the only call is line 4839 `if(FX.on&&!xr&&!window.__noFX) FX.composer.render(); else renderer.render(scene,camera);`, and XRFXMEM disposes rt1/rt2 on sessionstart (C.render is also guarded to plain render while freed). If 14 quads were seen with FX.on false, it's not this code path in the XR loop; most likely the capture was desktop (FX.on true) or taken before sessionstart. Cost if it ever did run in XR: ~3 full-res + bloom mips (~1.3× full-res fill total) ≈ 4-5 full-screen equivalents per eye ≈ 2-3 ms GPU/frame on Quest 3 + 14 draws per eye; this is why it is desktop-only today.
