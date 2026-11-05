# Step 5 prep: scanned PBR, atlases, bakes, env maps, in-material grade and fog (Palma Builder, 2026-10-29 06:45 CDT)
Status: PLAN ONLY. The build is unchanged until Rydah Optimizer posts the step-4 KTX2/Draco wiring on DEMO_STATUS.md.
Inputs: realism-heat-mapping-research.md §3, perf/drawcalls/realism-at-72fps.md (no post in XR, world <=110 draws, 13.9 ms), beach-sky-palms-research.md (sand #EDE8DC, Gulf haze), graffiti-research.md §5 (surfaces brick/metal/glass/asphalt), tools/quest_pipeline.py (ETC1S colour/ORM/emissive, UASTC normals, max base 2048 / normal 1024 / ORM 1024).
Tags: [M] measured in the 05:53 build + blockout (scene traversal, 388 materials), [S] sourced, [OURS] plan/estimate.

## 1. Inventory of world materials [M]
Totals: 240 MeshBasic, 116 MeshToon, 13 ShaderMaterial, 12 MeshStandard, 1 Lambert, plus 4 Line and 2 Points. No world mesh has uv2 today. No renderer toneMapping is set (NoToneMapping). Fog is linear THREE.Fog 70..360, night 0x1a1036; sky.js/FACADE.uDay drive day/night.
| Surface | Module | Material today | Maps today | Instanced / merged |
|---|---|---|---|---|
| Asphalt (district ground, 10 districts) | asphalt.js (asphaltGround) | MeshStandard, per-district tint | canvas map + normal + roughness, 1024² each | 1 mesh per district, merged by world_perf (asphalt 2->1) |
| Street paint, crosswalks | world.js / details.js | toon/basic flat colour | none (TEX.street 512 canvas legacy) | DET instanced, per 90 m cell |
| Sidewalks + 15 cm curbs | details.js det("walk") | toon flat 0xb4b4b8 | none (TEX.walk 256 canvas unused on these) | DET instanced |
| Plaza | world.js createPlaza | toon | TEX.plaza 1024² canvas | single |
| Facades, by district (Portside navy/purple, Cove pastel, Strip pink, Drive cyan, East Blocks concrete, 98 billboard, Yard/Port industrial) | facades.js (FACADE ShaderMaterial) + kits instanced buildings | ShaderMaterial (uDay, window emissive), 159 instances | embedded JPEG atlas (data URI) + TEX.facade/windows/glass 256x512 canvas | instanced (1 call per kit) |
| Building toon shells / kits | world.js buildInstancedBuildings | MeshToon + map | 256² canvas, 22 meshes / 129 instances | instanced |
| Roofs | world.js (box tops) | toon flat | none | INST box pool |
| Concrete: bridge deck, parapets, piers, caps, girders, barriers, underpass | world.js createBridge + bridges.js + blockout.js | toon flat (0x85847f, 0x9b9890, 0x6a6c74) | none | INST box/cyl pools + per-bridge fine InstancedMesh |
| Metal: rails, lamp poles, crane, gantries, guardrails | world.js addRail, bridges.js, blockout.js, grind.js tubes | toon flat, grind tubes MeshStandard (0xaab2bc normal 128²) | grind normal 128² canvas | INST pools; grind tubes merged |
| Containers (Port maze, 136) + old port boxes | blockout.js / world.js | toon flat, 8 shipping colours | none | INST box pool |
| Sand (Cove beach, Strip beach) | world.js flat() / blockout.js | toon 0x9a8a70 + TEX.sand 256²; blockout sand toon flat #EDE8DC | 256² canvas | single + INST |
| Grass (Heights) | world.js | toon + TEX.grass 256² | 256² | single (3 tiles) |
| Water | world.js createWaterFX + shore FX | ShaderMaterial (water), TEX.water 256², foam 512x64, shallow 16x128 | canvas | single |
| Boardwalk wood | blockout.js | toon flat 0x8a6a48 | none | INST box |
| Palms: trunk / fronds | world.js royalPalm/coconutPalm (DET cyl/cone), blockout (INST cyl/cone) | toon flat | none | instanced |
| Trees (Heights pines, street oaks) | world.js tree(), streetTree | toon flat | none | DET/INST |
| Signage | putSign/sign() canvas, world_perf sign atlas | MeshBasic + canvas map, 1024x256 / 512x256 / 512x128 | 4 world_perf atlas pages at 2048² RGBA + ~120 near-LOD originals | atlas far / originals near |
| Glass / windows | FACADE shader windows; TEX.glass 256x512 | shader | canvas | instanced |
| Neon / glow | MeshBasic flat colours (≈200 materials, many merged into vertex colour by world_perf) | none | merged per 810 m tile |
| Ink hulls | inkMat (MeshBasic black BackSide) | none | 547 meshes / 9058 instances (one shared material) |
| Props (benches, hydrants, bins) | details.js / place.js | MeshStandard 256² canvas (b8a690 ×26, d0d6dc ×79 instances) | 256² | instanced |
| Chain-link fences | FENCEMAT MeshBasic alphaTest | TEX.chain 64² | | DET |
| Blockout areas (beach, causeway underpass, port quay/crane/containers, Portside tower, Dash road, ring paint, G-Men precinct) | blockout.js | toon/glow INST pools (0 new materials) + 2 canvas signs | none | INST pools |
Not world (leave alone): graffiti_* ShaderMaterials (Rydah Systems), heat_cops Lambert, riders/HUD/minimap.

## 2. CC0 scan choice per surface [S] (downloaded to skyrydahs-ref/pbr/, 2K JPG zips, ambientCG CC0 1.0: https://docs.ambientcg.com/license/)
Maps used: Color (albedo, sRGB), NormalGL (OpenGL +Y, matches three), ORM packed by us = R AO (or 1.0) / G Roughness / B Metalness (or 0). Displacement is not used (parallax costs too much on Quest).
| Surface | Source | Maps in zip | Desktop target | Quest target |
|---|---|---|---|---|
| Asphalt + street | Asphalt031 | Color, NormalGL, Roughness, AO | 1024 tile in a 4096 page | 512 tile in a 2048 page |
| Sidewalk, curbs, roofs, plaza, quay apron | Concrete034 | Color, NormalGL, Roughness | 1024 | 512 |
| Bridge/pier/barrier/underpass concrete | Concrete046 | Color, NormalGL, Roughness | 1024 | 512 |
| Stucco facades (Cove, Strip, Drive, precinct) | PaintedPlaster017 (tinted per district by vertex colour) | Color, NormalGL, Roughness | 1024 | 512 |
| Brick facades (Yard, Port, East Blocks) | Bricks105 | Color, NormalGL, Roughness, AO | 1024 | 512 |
| Sand (Cove + Strip beach) | Ground080 (tags: beach, sand) | Color, NormalGL, Roughness, AO | 1024 | 512 |
| Boardwalk wood | Planks037A | Color, NormalGL, Roughness, AO, Metalness | 1024 | 512 |
| Palm trunk | Bark001 (pale grey-tinted; royal palm trunks are smooth grey) | Color, NormalGL, Roughness | 512 | 256 |
| Containers | CorrugatedSteel005 (tinted per instance via instanceColor) | Color, NormalGL, Roughness, Metalness, AO | 1024 | 512 |
| Crane, gantries, lamp poles, guardrail | PaintedMetal004 | Color, NormalGL, Roughness, Metalness | 512 | 256 |
| Rails, deck plates, grates | MetalPlates008 | Color, NormalGL, Roughness, Metalness | 512 | 256 |
| Palm fronds, tree canopies | no scan: keep flat toon + vertex colour (an alpha-tested leaf card would add overdraw on Quest) | – | – | – |
| Glass | no scan: FACADE shader windows + env map (§6) | – | – | – |
| Water | no scan: keep the shader; add the env map + a 256² tiling normal (procedural) | – | – | – |
| Signage / neon | keep canvas text; move it into the emissive slot of the sign atlas pages | – | – | – |

## 3. Atlas layout (fits the existing merge keys, world <=110) [OURS]
Merge keys today: world_perf merges by material, the INST pools are one material per kind, and asphalt is 1 merged mesh. An atlas page keeps "1 material = 1 merge key", so the call count stays flat.
- **Page G, ground (4096 desktop / 2048 Quest, 2x2 tiles):** asphalt | concrete034 | sand | planks. Used by: merged asphalt (1 mesh), DET walk/curbs, plaza, blockout sand/apron/boardwalk/Dash road. UV: world-space planar (x,z)/tileSize wrapped inside the sub-rect in the shader (fract + rect offset, with a 2 px gutter/padding to avoid mip bleed). This is cheaper than re-UVing and works for merged geometry. 0 draw delta.
- **Page S, structure (4096 / 2048, 4x2 tiles):** concrete046 | plaster | bricks | painted metal | metal plates | corrugated | bark | (spare: roof gravel). Used by: the INST box/cyl/cone pools (bridges, blockout, kits), the toon building shells, and the containers. Tile selection per instance comes from a new per-instance attribute `aTile` (1 float) next to instanceColor. Triplanar-lite projection (2 fetches, dominant axis) because the box pools have unit-cube UVs. 0 draw delta.
- **Page F, facades:** keep FACADE's own atlas (already 1 call per kit). Add page S plaster/brick as a detail normal at 4x tiling. 0 delta.
- **Page E, emissive/signs:** the existing 4 world_perf sign pages (2048² RGBA canvas) become 2 KTX2 ETC1S pages (repack at 0.75x). This draw-negative change saves 1-2 calls.
- **uv2 / lightmaps:** the merged static tiles (world_perf 810 m tiles, asphalt, bridge decks) need a second UV set: xatlas or Blender Smart UV Project at export, with a 4-8 px margin at 1024. Instanced pools get NO uv2. Instead they get a per-instance AO term (§5) plus a ground-contact AO decal. Lightmap sampling is per 270 m tile = 1 extra texture per merged tile material, so the tiles need a per-tile material clone. To stay draw-neutral, keep tiles = draws (already the case for the 810 m tiles: 1 tile = 1 merge = 1 call).
Draw delta for the whole plan: 0 to -2 (sign page repack). Budget holds at today's world numbers (≈ 76-99 world at the 4 views).

## 4. Quest texture memory (KTX2) [OURS estimate]
GPU bytes: ETC1S -> ETC2 RGB(A) = 4 bpp (0.5 B/px); UASTC -> ASTC 4x4 = 8 bpp (1 B/px); mip chain x1.33.
| Item | Size (Quest) | Codec | MB |
|---|---|---|---|
| Page G albedo / ORM | 2048² each | ETC1S | 2.8 + 2.8 |
| Page G normal | 2048² | UASTC | 5.6 |
| Page S albedo / ORM | 2048² each | ETC1S | 2.8 + 2.8 |
| Page S normal | 2048² | UASTC | 5.6 |
| Sign/emissive pages (2) | 2048² | ETC1S (UASTC if text smears) | 5.6 (11.2) |
| Lightmaps day+night, ~9 tiles | 1024² | UASTC (ETC1S bands on smooth gradients) | 9 x 2 x 1.4 = 25 |
| AO (packed into the lightmap alpha) | – | – | 0 |
| Env maps: 2 live cubes (current district day/night), 128²/face, RGBM8 | – | uncompressed | 2 x 0.5 = 1 |
| Water normal 256², misc | – | ETC1S/UASTC | <1 |
| **Total new world textures** | | | **≈ 55 MB (≈ 61 MB with UASTC signs)** |
Today, for comparison [M]: the 4 sign atlas pages alone are 2048² RGBA canvas = 4 x 16.8 MB x 1.33 ≈ 89 MB, the 10 asphalt 1024² canvases x3 maps ≈ 167 MB, and FACADE + others are small. Step 5 therefore cuts world texture memory from about 270 MB to about 60 MB, well inside Optimizer's 256 MB total budget.
Desktop: 4096 pages with BC7 via UASTC transcode (1 B/px) ≈ 22 MB per map, so about 135 MB for G+S. Lightmaps go to 2048.

## 5. Bake plan [OURS]
- Tools on the box: **Blender 4.3.2** at /home/box/.local/bin/blender (headless `blender -b -P bake.py`, Cycles CPU). KTX tools come from tools/ktx (quest_pipeline env) and gltf-transform from quest_transform.cjs. No GPU is needed.
- Export: a page-side exporter (THREE.GLTFExporter r128, IIFE like the KTX2 loader) dumps the static merged tiles (asphalt, 810 m merge tiles, bridge decks/piers, blockout INST boxes baked to a mesh, building shells as low-poly boxes as occluders) per 270 m tile with `?seed=1`. Layout must be deterministic. Today buildings/trees use unseeded Math.random, so either seed the shipping build (Ani's call) or bake only seed-independent geometry (ground, bridges, blockout, garages, landmarks). The latter is the recommended start.
- Blender: xatlas/Smart UV -> uv2 (margin 4 px @1024), then bake on the ground and large static meshes only:
  - **Day lightmap** = sun (azimuth/elevation from sky.js day) + sky hemisphere (Gulf blue #9ab8e0) + bounce. 64-128 samples + OIDN denoise.
  - **Night lightmap** = the city's emissive (neon strips, lamps, sign planes as emissive meshes at their crew colours) + moon/sky fill. The "neon colour baked into the night lightmap" is the NFS look.
  - **AO** (0.6 m distance, contact shadows at kerbs/walls/piers), stored in the lightmap alpha.
- Runtime: lightMap = day KTX2 and a second sampler for night, lerped by FACADE.uDay in onBeforeCompile (1 extra fetch; switching is live like the sky), or swapped at the dusk/dawn midpoint if the 2nd fetch costs too much on Quest. Instanced pools: a per-instance AO scalar computed at bake time (sampled ground AO at the instance base) + a cheap vertical gradient in the toon shader.
- Grind/gameplay: bakes touch materials only. Geometry, colliders and grind splines are unchanged.

## 6. Per-district env maps, in-material grade and fog [OURS, colours from in-repo research]
Env: one prefiltered cube per district + bridges, baked in Blender from the district centre at 6 m height (day + night), stored as RGBM8 KTX2 (or PNG) 128²/face, PMREM'd once at load on desktop. On Quest, pre-filtered offline and swapped when the rider crosses the district box (districtAt) with a 1 s cross-fade in the shader. Used by: asphalt (wet-night spec), glass, metal, water, containers.
Grade (in-material, works in XR): the shared patchToon/patchStandard onBeforeCompile gets a `gradeFrag` before `#include <tonemapping_fragment>`: exposure, ACES-fitted curve (Narkowicz), lift/gamma/gain and a 16³ LUT as a 256x16 sampler (Optimizer #7). Glow/neon MeshBasic gets the same chunk, but skips the curve's shoulder so the neon stays saturated.
| District | Day env / grade | Night env / grade | Fog day (colour, near-far) | Fog night |
|---|---|---|---|---|
| Portside Terminal (gold/cyan, navy) | clear Gulf sky, exposure 1.0, neutral | navy-violet sky, gold+cyan sign pools, exposure 1.15, slight teal shadows | #b8c8e0, 80-380 | #1a1036, 70-360 (today) |
| The Cove (purple/cyan sunset) | warm pastel, +5% warmth | purple dominant, cyan rim | #c8c4dc 80-380 | #241040 60-340 |
| Industrial Port (orange) | hazy, -10% saturation, sodium tint in shade | sodium orange + crane reds | #c4c0b4 60-340 (port haze) | #20140e 50-320 |
| The Yard (rust) | dusty warm | rust/amber | #c8bca8 70-360 | #1e1410 60-330 |
| The Drive (cyan) | cool bright | cyan + police blue (precinct) | #b4c8e4 80-380 | #0e1830 70-360 |
| The Strip + beach (pink) | Gulf emerald + sand bounce (#EDE8DC), +0.1 exposure | magenta neon on sand (sand is a neutral reflector) | #c4dcec 90-400 (sea air) | #2a0e2e 70-360 |
| The Heights (green) | soft green bounce | moss/lantern gold, darkest district | #b8ccc0 80-380 | #0e1a14 60-330 |
| East Blocks / 98 Billboard Mile | concrete neutral | billboard yellow + white | #bcc4d4 80-380 | #1a1626 70-360 |
| Bridges (causeway, shore, b98) | open water, highest exposure, longest fog | crew-colour deck strips + blue pier uplights over black water | #c0d4ea 100-420 | #141030 80-380 |
Height fog: exp fog plus a height falloff (dense below 4 m over water, thin above 40 m) in the same fog_fragment patch. The fog colour lerps between district values over 20 m at district borders. It must match sky.js horizon colours so far tiles fade into the sky.

## 7. What step 5 needs from Optimizer's step 4
1. KTX2Loader IIFE + basis transcoder wired for **world** textures (not only GLBs): a `loadKTX2(url)` helper that returns a THREE.CompressedTexture, with detectSupport(renderer) done once.
2. quest_pipeline option for **loose textures** (not inside a GLB): ETC1S for albedo/ORM/lightmap-alpha, UASTC for normals and lightmaps, max sizes as in §4.
3. Draco/meshopt for the exported baked tiles (if the tiles ship as GLB instead of runtime-merged).
4. The ?tier=quest switch, to pick the 2048 vs 4096 pages.
5. Confirmation that the 4 sign atlas canvases can be replaced by KTX2 pages (they're built at runtime from canvas text today, so they need a bake step or ETC1S runtime encode = too slow; plan is an offline bake).

## 8. Notes / blockers
- Unseeded Math.random building/tree layout blocks a full-city bake (see §5). Decision needed from Ani: seed the shipping layout, or bake only seed-independent geometry.
- Toon materials ignore lightMap/aoMap; they need an onBeforeCompile hook (polish.js owns patchToon? to confirm) or a switch to MeshLambert + grade.
- Later, per Ani: the Portside North police spot near (60,-70) stays as a G-Men substation, and The Drive precinct is the main HQ. Nothing to change now.
