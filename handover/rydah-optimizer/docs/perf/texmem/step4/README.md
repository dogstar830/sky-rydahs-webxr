# Step 4.3-4.5 KTX2 (Rydah Optimizer, 2026-10-30 ~01:40 CDT)
All MB are STATIC ESTIMATES from file contents (no headset, no browser, no tests run, no rebuild).
GPU formula (r128 KTX2Loader FORMAT_OPTIONS on Quest 3 = astc+etc2): ETC1S -> ETC2 RGB 0.5 B/px, UASTC -> ASTC 4x4 1 B/px, RGBA8 4 B/px, all x4/3 for mips.

## 4.3 Loader candidate: NOT merged
build_ikki.sh still runs `patch_draco.py` (unchanged since 10-29 03:26); the live html (17:59:57) has no gate. Last board state: Ani 06:40 "blocked" waiting for a green suite pass; no gate result was posted later.
- Rebase: not needed. `patch_draco.py` hasn't changed since the candidate was written. Stage 1 (Draco/meshopt wrap) is identical code (`patch_draco_ktx2_candidate_vs_live.diff`).
- **Bug fixed**: the idempotency check was `'window.SR_KTX2' in src`. But asphalt.js (inlined earlier by patch_asphalt.py) already contains that string, so merging as it was would have printed "already applied" and installed NO gate. Now the check uses a unique marker `/*SR_KTX2_GATE*/`. Dry run on a /tmp copy of the 17:59:57 html: gate installed with 9 map entries, and a second run is idempotent. Backup: `patch_draco.py.ktx2-candidate.bak-202610300133`.
- Map updated to the step 4.4 files (crews -> `*.s4-ktx2.glb`, falling back to quest2-ktx2; caali-g.nonormal.glb -> caali-g.nonormal.ktx2.glb; Ikki quest-draco -> s4-ktx2). There are **no WITHHELD_CHAR entries**, because the map is inlined into index.html and the PUBLIC=1 gate fails on any 'WITHHELD_CHAR' string. ?texfull=1 (caali-g.glb) is deliberately left unmapped.
- Default path: the only addition to the html is one small script that sets `window.SR_KTX2={on:false}` and returns. No loader file is fetched and no URL changes. The html is therefore NOT byte-identical (one extra `<script>`), but the default runtime path is behaviourally identical. asphalt.js already checks `S.on`.
- libs/basis (basis_transcoder.js/.wasm r128) and libs/ktx2 (KTX2Loader.classic.js) exist in v3build. package_pwa.sh already copies them.
- GLTFLoader in the build is r128 `loaders/GLTFLoader.js`, which has `setKTX2Loader` + `KHR_texture_basisu`. The gate wrapper calls `setKTX2Loader(SR_KTX2.loader())` on every GLTFLoader, so all `.s4-ktx2.glb` / `.ktx2.glb` files below load through SR_KTX2.
- Integrator gate needed (Ani): scratch build with the candidate in place of patch_draco.py (`SR_HTML=/tmp/g.html`), then smoke CORE, perf_overlay.py, rider shots (with and without ?ktx2=1, plus a Caali G Portside shot), and perf_seed7 (calls must not rise). Also test ?ktx2=1 with ?notexshare=1 / ?texfull=1 / ?crew=orig.

## 4.4 Characters (files written next to the originals; nothing overwritten)
| asset | before file -> after file | textures after | GPU MB before | GPU MB after | disk MB before | disk MB after | at spawn |
|---|---|---|---|---|---|---|---|
| Ikki (player cap, IKKI_URL default) | meshy/ikki-meshy-skate.quest-draco.glb -> ikki-meshy-skate.s4-ktx2.glb | ikki_atlas_n 684x1024 ktx2-zstd, ikki_atlas 1368x2048 ktx2-etc1s(basislz), ikki_atlas_mr 684x1024 ktx2-etc1s(basislz) | 18.22 | 3.12 | 0.83 | 1.60 | yes |
| Caali G (default player) | wardrobe/riders/caali-g.nonormal.glb -> caali-g.nonormal.ktx2.glb | CaaliG_atlas 2048x2048 ktx2-etc1s(basislz) | 21.33 | 2.67 | 3.63 | 3.77 | yes |
| crew anubis | anubis/anubis-rider.quest.glb -> anubis-rider.s4-ktx2.glb | normal_bake 512x512 ktx2-zstd, atlas 512x128 ktx2-etc1s(basislz) | 1.67 | 0.38 | 0.75 | 0.66 | yes |
| crew behemoth | behemoth/behemoth-rider.quest.glb -> behemoth-rider.s4-ktx2.glb | normal_bake 512x512 ktx2-zstd, atlas 512x128 ktx2-etc1s(basislz) | 1.67 | 0.38 | 0.93 | 0.81 | yes |
| crew genesis | genesis/genesis-rider.quest.glb -> genesis-rider.s4-ktx2.glb | normal_bake 512x512 ktx2-zstd, atlas 512x128 ktx2-etc1s(basislz) | 1.67 | 0.38 | 0.97 | 0.86 | yes |
| crew kogarasumaru | kogarasumaru/kogarasumaru-rider.quest.glb -> kogarasumaru-rider.s4-ktx2.glb | normal_bake 512x512 ktx2-zstd, atlas 512x128 ktx2-etc1s(basislz) | 1.67 | 0.38 | 0.98 | 0.87 | yes |
| crew sleeping-forest | sleeping-forest/sleeping-forest-rider.quest.glb -> sleeping-forest-rider.s4-ktx2.glb | normal_bake 512x512 ktx2-zstd, atlas 512x128 ktx2-etc1s(basislz) | 1.67 | 0.38 | 0.94 | 0.82 | yes |
| crew static-angels | static-angels/static-angels-rider.quest.glb -> static-angels-rider.s4-ktx2.glb | normal_bake 512x512 ktx2-zstd, atlas 512x128 ktx2-etc1s(basislz) | 1.67 | 0.38 | 0.97 | 0.85 | yes |
| crew tool-toul-to | tool-toul-to/tool-toul-to-rider.quest.glb -> tool-toul-to-rider.s4-ktx2.glb | normal_bake 512x512 ktx2-zstd, atlas 512x128 ktx2-etc1s(basislz) | 1.67 | 0.38 | 0.93 | 0.82 | yes |
| WITHHELD_CHAR NPC (local-only) | WITHHELD_CHAR/WITHHELD_CHAR-npc.glb -> WITHHELD_CHAR-npc.s4-ktx2.glb | WITHHELD_CHAR_atlas_c_eyes 2048x2048 ktx2-etc1s(basislz), WITHHELD_CHAR_atlas_mr 1024x1024 ktx2-etc1s(basislz) | 26.67 | 3.33 | 0.94 | 1.12 | yes |
| WITHHELD_CHAR rider (?player=WITHHELD_CHAR, not at spawn by default) | WITHHELD_CHAR/WITHHELD_CHAR-rider.glb -> WITHHELD_CHAR-rider.s4-ktx2.glb | WITHHELD_CHAR_atlas_c_eyes 2048x2048 ktx2-etc1s(basislz), WITHHELD_CHAR_atlas_mr 1024x1024 ktx2-etc1s(basislz) | 26.67 | 3.33 | 1.34 | 1.52 | no |
| **characters at spawn** | | | **77.89** | **11.74** | | | |

Notes:
- Crews and Ikki: `tools/quest_pipeline.py --suffix s4 --ktx2 --geometry draco`, NPC caps 1024. Ikki uses player caps (2048 colour, 1024 normal/ORM, UASTC normal). Draco decodes to float, and `_WC/_WA` + skin are kept. The pipeline FLAG check reported no issues. The `.s4.glb` (webp) side outputs were also written; they are unused.
- Caali G: texture-only (`caali_ktx2.cjs` + `gltf-transform etc1s`, q192, sRGB). Geometry is not re-encoded. **Decoded accessors are byte-identical** before and after (34 lines: type, componentType, normalized, count and sha1 for every attribute incl. _WC/_WA/_BM/_SLOT, plus indices; `caali_acc_before.txt` / `caali_acc_after.txt`, checked with `acc_check.cjs`). KHR_mesh_quantization is kept, and EXT_meshopt_compression is re-applied without re-quantizing.
- WITHHELD_CHAR: full look kept (2048 colour, 1024 ORM, ETC1S q192; he has no normal map, so there is nothing to encode as UASTC). Files stay local-only: public-exclude `WITHHELD_CHAR/*` and `*WITHHELD_CHAR*` drops them (checked with the excluded() function), and there are no WITHHELD_CHAR strings in the shared map.
- Crew 512x128 atlas: riders.js tex-share hashed canvas pixels, so KTX2 (CompressedTexture) would never share. riders.js (ours) now hashes the transcoded level-0 bytes for compressed textures. The default path is unchanged because no compressed textures load without ?ktx2=1. Diff: `riders_ktx2share.applied.diff`, backup `riders.js.bak-ktx2share-202610300136`. The table counts each crew's atlas (~0.04 MB) separately, so the after numbers are slightly conservative.
- gltf-transform validate: **0 errors on all 12 files** (`validate.txt`). The warnings are expected ones: KHR_texture_basisu/Draco not known to the validator (IMAGE_UNRECOGNIZED_FORMAT, UNSUPPORTED_EXTENSION), plus the pre-existing NODE_SKINNED_MESH_NON_ROOT, UNUSED_OBJECT and generated-tangent warnings.
- Disk: Ikki and WITHHELD_CHAR grow (+0.8 / +0.2 MB). ETC1S at 2K is bigger than webp. Crews shrink about 12%.

## Swap list (all behind ?ktx2=1; the default stays unchanged)
| asset | where the URL is set | owner | swap |
|---|---|---|---|
| 7 crews | patch_crew_quest.py `SR_CREW_GLB` -> `<crew>-rider.quest.glb` | Rydah Optimizer (Rigger also edited it 01:33) | via SR_KTX2.map in patch_draco.py.ktx2-candidate (ours), so no edit needed |
| Caali G | wardrobe.js:15 `WARDROBE_RIDERS.caali.url` (caali-g.nonormal.glb) | Rydah Forge / Rydah Rigger | via SR_KTX2.map, so no wardrobe.js edit needed |
| Ikki | patch_draco.py `IKKI_URL` (quest-draco) | Rydah Optimizer | via SR_KTX2.map |
| WITHHELD_CHAR NPC | patch_wardrobe.py `WITHHELD_CHARNpc ... url:CHAR_BASE+'WITHHELD_CHAR/WITHHELD_CHAR-npc.glb'` | Rydah Forge / Rydah Rigger | PROPOSED `patch_wardrobe_WITHHELD_CHAR_ktx2.proposed.diff` (inside the block that PUBLIC=1 strips) |
| WITHHELD_CHAR rider | wardrobe.js:18 `WARDROBE_RIDERS.WITHHELD_CHAR.url` | Rydah Forge / Rydah Rigger | PROPOSED `wardrobe_WITHHELD_CHAR_ktx2.proposed.diff` (?ktx2=1 regex; PUBLIC strips the whole entry) |
| facades | facades.js `ld('__FACADE_ALB__')`/`ld('__FACADE_NR__')` (base64 jpg via patch_facades.py) | Palma Builder (world; please confirm) | PROPOSED `facades_ktx2.proposed.diff` |
| kit PBR | crewhouse_kit.js:84 `tx()` -> assets/kit/*.jpg | Palma Builder | PROPOSED `crewhouse_kit_ktx2.proposed.diff` |
package_pwa.sh (ours, backup `.bak-ktx2chars-202610300136`): guarded copies of all `*.s4-ktx2.glb`, `caali-g.nonormal.ktx2.glb` and `assets/world_ktx2/`. The WITHHELD_CHAR files go through `cpa`, so PUBLIC=1 excludes them. `bash -n` passes. Not packaged or run.

## 4.5 World (assets/world_ktx2/, pre-flipped vertically because the KTX2 path uses flipY=false; `ktx validate` OK on all 11)
| texture | before | after | GPU MB before -> after | disk |
|---|---|---|---|---|
| facade_albedo 2048x1024 (hero) | jpg RGBA8 | ETC1S q192 sRGB, mips | 10.64 -> 1.33 | 0.28 -> 0.33 MB (+33% base64 removed from html) |
| facade_nr 2048x1024 (RG normal + B rough, linear) | jpg RGBA8 | UASTC q2 + zstd 18, linear, mips | 10.64 -> 2.67 | 0.29 -> 1.75 MB |
| kit Concrete034/046, PaintedMetal004 x (Color, NormalGL, Roughness), 512 | jpg RGBA8 | colour ETC1S sRGB, rough ETC1S linear, normal UASTC | 12.0 -> 2.0 (not in inventory.csv; crewhouse, spawn residency unknown) | 0.31 -> 0.89 MB |
The world list comes from inventory.csv: facades are the only world image files. Everything else is a procedural canvas (signs, turf, emblems, cvTex, map) and is handled by steps 4.2C/4.6 or the owners' caps. Asphalt was already done (16.0 -> 2.7). kit_logos.png is drawn into a canvas, so it was skipped. Facade sampling: the shader reads raw texel values (TextureLoader, encoding Linear), and ETC2/ASTC from KTX2 also return the stored bytes, so the proposal leaves encoding unset to keep the look the same.

## 4. Projected spawn texture MB with ?ktx2=1 (static, after all swaps land)
| | inventory.csv static | anchored to the 324 MB overlay |
|---|---|---|
| now | 294.5 | ~324 |
| characters 77.9 -> 11.7 | -66.2 | |
| facades 21.3 -> 4.0 | -17.3 | |
| asphalt 16.0 -> 2.7 (already in asphalt.js) | -13.3 | |
| **after** | **~198 MB** | **~227 MB** (under the 256 MB budget, ~29 MB headroom) |
Further, not counted: kit PBR -10 if resident at spawn, Palma's sign originals (4.2C) ~-30..40, and sign atlas pages (4.6) ~-48. The first real number comes from OVR Metrics on a Quest 3 after the integrator gate.

## Gate round 2 RED -> fixes for round 3 (2026-10-30 ~04:50 CDT, static analysis only; no tests, no browser)
1. **seed7 +2 draws.** This is not a texture or material split. Every KTX2 swap sets textures in place on the existing shared materials: asphalt.js `m[key]=nu[key]`; facades `swapU` on `FACADE.uniforms`; kit `txSwap` over `MAT`. No new material, mesh or program key is created, and the default path (lazy kit placeholders, facade jpg) uses the same materials. Tex-share runs inside `rLoad` before `loadRiderR128` builds `rToon`/`rGlowMat`/`rMerge`, and texture identity doesn't affect rider draw count anyway (body + outline + glow per rider in both paths). The pattern points to moving objects: causeway night 107=107 but day 107->109, street +2/+1, b98 -1, aerial -1. Mixed signs at the same camera across day/night = roaming NPC riders (2-3 draws each) whose start is shifted by KTX2 transcode latency. Proposal for Ani/Systems: compare seed7 with dc_meter's category split (scene minus riders), or wait for RIDERS.ready plus a fixed NPC clock before sampling. No world_perf.js diff is proposed because nothing there keys on texture identity.
2. **perf_overlay 5% check.** `tests/perf_overlay.py` is Rydah Systems' file, so I wrote a proposed diff: `perf_overlay_ktx2.proposed.diff`. The audit snippet (audit.md section 1, ours) is fixed: per-format bpp (ETC2 RGB/ETC1 0.5, ASTC 4x4 1, BC1 0.5, BC3/BC7 1, PVRTC 0.5, RGBA8 4) and x1.33 only when mips exist. Backup `audit.md.bak-<ts>`. The old snippet's 250 MB vs the overlay's 186 MB is this 4 B/px over-read.
3. **Caali KTX2 never requested.** The map did key `caali-g.nonormal.glb`, but the gate runs headless desktop Chrome. There `WARDROBE_TIER` defaults to `'hd'` (non-Quest UA), so wardrobe loads `caali-g-hd.glb` (4096 webp, ~85 MB colour), which wasn't mapped. On a Quest UA the tier is 'quest', so nonormal.ktx2 would have loaded. Fix: new `caali-g-hd.ktx2.glb`, texture-only (4096 ETC1S colour ~10.7 MB GPU; the unused normal is dropped because wardrobe `noNormal:true` discards it anyway). Decoded accessors are byte-identical (`caali_hd_acc_*.txt`), validate reports 0 errors, and a map entry was added. Static check on /tmp/g3.html: hd -> hd.ktx2, nonormal -> nonormal.ktx2, caali-g.glb (?texfull=1) unchanged.
4. **PUBLIC=1.** Already passes, no change needed: SRC=/tmp/g3.html PUBLIC=1 OUT=/tmp/pwa_pub_r3 -> both WITHHELD_CHAR s4-ktx2 files excluded, 20 -> 0 refs in index.html, GATE OK, 0 names / 0 contents.
5. **Black NPC.** Matched against lineup.png (flat cap + pipe on the back), it is the **tool-toul-to crew rider** in The Yard. Its s4-ktx2 file is fine: geometry/attribute stats are identical to tool-toul-to-rider.quest.glb, and the atlas and normal_bake decode to the same means as the png originals (atlas 205 vs 206, normal 128/128/243). The solid black with no glow looks like only the outline hull is showing (olM, frustumCulled=false) and the toon body/glow aren't drawing visibly. That is a runtime state I can't reproduce without a browser. Requested probe for Ani (?ktx2=1, at The Yard): for the tool-toul-to rider's LOD meshes, log material.type, map.isCompressedTexture, map.format, map.mipmaps.length, !!renderer.properties.get(map).__webglTexture, visible, and layers.mask.

## Round 3 blocker: the "black Tool Toul To" (2026-10-30 ~09:05 CDT; static + node-only checks, no browser)
**Root cause: it isn't Tool Toul To. It's the Ikki NPC, and its KTX2 textures were non-power-of-two.**
- In ktx2_facade_on.png, the real TTT NPC is the textured rider at the left fence (hammer-logo backpack, orange trim, same as the off shot). The black figure has Ikki's cap silhouette (compare shots/attack_ikki.png).
- `ikki-meshy-skate.s4-ktx2.glb` had colour 1368x2048 and normal/ORM 684x1024 (the pipeline kept the source aspect). Every other rider/world KTX2 is POT.
- The headless gate transcodes ETC1S/UASTC to BC7 (format 36492; r128 KTX2Loader picks BPTC before ETC2 on desktop). The BC7/S3TC WebGL extensions require each level to be a multiple of 4. The 1368 chain hits 342, and 684 hits 171, so the upload fails and the texture stays incomplete. It samples black, the body and glow render black, and the black back-face outline makes the silhouette.
- On Quest (ASTC/ETC2) this might not have broken, but POT is our convention (audit section 5) and it has to work on desktop too.
- **Why the probe pointed at TTT:** NPC idx 6 had `visibleChain:false` (off camera), so its map simply hadn't been rendered yet (`uploaded:false`). It is the canonical shared crew atlas, and it uploads on first draw like the other crews.

**Hypotheses ruled out**
- (a) Visibility race: the outline is added to the same LOD group as the body (riders.js:93), so they toggle together.
- (b) Tex-share: a node simulation of riders.js `rShareTextures` with 8 mock crews (shared atlas bytes, map plus emissive referencing the same texture, 3 LODs) shows every crew ends on texture #1, the canonical is never disposed (disposed=0), and only duplicates are disposed (`/tmp/ts_sim.cjs`). `?notexshare=1` bypasses it entirely.
- (c) Nothing touches compressed map.image as a canvas: `_rTexKey` takes the compressed branch first.
- (d) BC7 is the desktop format for every crew. It isn't the root cause by itself; NPOT plus BC7 is.
- The "Custom UV set 1 for texture normalMap" x8 warning is pre-existing and not a pipeline bug. All 7 crews plus code-e have `normalTexture.texCoord=1` identically in the original rider.glb, the .quest.glb and the .s4-ktx2.glb, and rToon doesn't use the normal map.

**Fix**
- `tools/quest_pipeline.py` / `quest_transform.cjs`: new `--pot [near|up]` (default off, so behaviour is unchanged without it) snaps each axis to a power of two. `up` never loses detail and is capped by --max-*. Backups `*.bak-pot-202610300904`.
- Ikki regenerated with `--pot up`: colour 2048x2048 ETC1S, normal 1024x1024 UASTC, ORM 1024x1024 ETC1S. Geometry/attribute stats are identical to the previous file, and validate reports 0 errors. Static GPU 3.12 -> 4.67 MB (+1.55). Projected spawn with ?ktx2=1 is ~200 MB inventory / ~229 MB anchored, still under 256.
- Old file kept: `meshy/ikki-meshy-skate.s4-ktx2.npot-bak-202610300905.glb`.
- POT scan of every mapped KTX2 (characters + assets/*): all POT except Forge's v2 `caali-g.nonormal.ktx2.glb` caali_LOD0_nrm 768x768. That one is harmless today because WARDROBE_RIDERS.caali `noNormal:true` drops the normal map before upload, but Forge should make it 512 or 1024 if it ever ships.

**After gate GREEN, swap the candidate in (NOT done yet)**, build_ikki.sh line 22:
`-python3 patch_draco.py`
`+python3 patch_draco.py.ktx2-candidate   # Rydah Optimizer: Draco/meshopt wrap + opt-in ?ktx2=1 KTX2 gate (KTX2 gate GREEN)`
(Backup build_ikki.sh first. The candidate writes the live html by default, SR_HTML unset.)
