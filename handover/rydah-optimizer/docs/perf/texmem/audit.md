# Texture memory audit + Step 4 (KTX2 + downsizing) plan (Rydah Optimizer, 2026-10-29)
All numbers are STATIC ESTIMATES from build html / GLB JSON / PIL dimensions. No real headset and no browser run were used, and no tests were run.
GPU model: RGBA8 + full mip chain = w*h*4*1.33. KTX2 after transcode: UASTC -> ASTC 4x4 ~1 B/px, ETC1S -> ETC2 RGB ~0.5 B/px (ETC2 RGBA / ASTC = 1 B/px if alpha), both with mips x1.33.
Per-texture data: `inventory.csv` (sha column flags duplicates).

## 1. Verdict on the ?perf=1 "~393 MB"
**About right, but a little HIGH. Static total at spawn is ~295 MB (range ~270-340, depending on how many sign canvases exist), and that is still over the 256 MB Quest budget.**
How perf_overlay.js `texMem()` counts (dc_meter.js does not count texture MB; it only passes along `renderer.info.memory.textures`):
- It walks `scene.traverse` (hidden objects too) over the enumerable material properties, and a Set de-dups by Texture object. So it does **not** double-count a shared Texture. Identical images in *separate* Texture objects (for example the 512x128 crew atlas, sha 75200a21b7cc, in all 7 NPC GLBs) are counted 7x. three r128 also uploads them 7x, so that part of the count is correct and is a dedup opportunity.
- **Over-counts:** (a) The ~30 original `textTex` sign canvases (1024x256) are hidden after the world_perf sign atlas packs them. They stay in the scene and get counted, but three only uploads a texture on first draw, so most are not GPU-resident at spawn. They upload later inside 28 m and are never freed. (b) The mip factor keys only off `generateMipmaps`, not minFilter. (c) It applies 4 B/px to every texture, so once KTX2 lands, **CompressedTexture would be over-counted 4-8x**. The overlay has to learn per-format bpp in step 4.
- **Under-counts / misses:** ShaderMaterial `uniforms.*.value` textures (graffiti atlas 1024^2, graf noise, any shader-uniform turf/grind maps), textures not attached to scene objects (cached, or the dropped Caali G normal), and render targets/composer buffers (post is excluded by design). Shadow maps: none (no castShadow / shadowMap in the build). Canvas and Data textures ARE counted (image.width/height).
- Net effect: the over-counts (hidden sign originals) outweigh the misses (~5-7 MB of shader uniforms), so 393 sits ~60-100 MB above my static sum. The order of magnitude and the conclusion (over budget) still stand.
- Biggest surprise: **~59% of the memory is procedural canvas textures (~174 MB)**, not GLBs (~120 MB). The sign system alone is ~104 MB.

Live confirmation (integrator only, under .testlock. I did NOT run this). Open `sky-rydahs-v3-ikki.html?perf=1&seed=7` at spawn and evaluate in the page:
```
(()=>{const T=THREE,B={[T.RGB_ETC1_Format]:.5,[T.RGB_ETC2_Format]:.5,[T.RGBA_ETC2_EAC_Format]:1,[T.RGBA_ASTC_4x4_Format]:1,[T.RGB_S3TC_DXT1_Format]:.5,[T.RGBA_S3TC_DXT1_Format]:.5,[T.RGBA_S3TC_DXT3_Format]:1,[T.RGBA_S3TC_DXT5_Format]:1,[T.RGBA_BPTC_Format]:1,[T.RGB_PVRTC_4BPPV1_Format]:.5,[T.RGBA_PVRTC_4BPPV1_Format]:.5};const MM=[T.NearestMipmapNearestFilter,T.NearestMipmapLinearFilter,T.LinearMipmapNearestFilter,T.LinearMipmapLinearFilter];const s=new Set(),L=[];scene.traverse(o=>{[].concat(o.material||[]).forEach(m=>{const vs=[...Object.values(m),...Object.values(m.uniforms||{}).map(u=>u&&u.value)];vs.forEach(t=>{if(t&&t.isTexture&&!s.has(t)){s.add(t);const i=t.image||{},w=i.width||0,h=i.height||0,c=!!t.isCompressedTexture,bpp=c?(B[t.format]??1):4,mip=c?((t.mipmaps||[]).length>1):(t.generateMipmaps&&MM.includes(t.minFilter)),f=mip?1.33:1;L.push([t.name||(i.src||'').slice(-40)||(i.constructor&&i.constructor.name),w,h,c?'c'+t.format:'rgba8',!!renderer.properties.get(t).__webglTexture,(w*h*bpp*f/1048576).toFixed(2)]);}})})});L.sort((a,b)=>b[5]-a[5]);console.table(L);return L.filter(r=>r[4]).reduce((a,r)=>a+ +r[5],0);})()
```
KTX2-aware (2026-10-30): CompressedTexture uses its real bpp (ETC1S->ETC2 RGB 0.5, UASTC->ASTC4x4 1.0, BC1 0.5, BC3/BC7 1.0, PVRTC 0.5), RGBA8 4; the x1.33 mip factor applies only when mips exist (compressed: mipmaps.length>1; RGBA8: generateMipmaps + a mipmap minFilter). The old snippet assumed 4 B/px x1.33 for everything, so it over-read KTX2 textures 4-8x.
The returned number is the MB actually uploaded (`__webglTexture` set), uniforms included. Compare it with the overlay's MB.

## 2. Top offenders (static, at spawn)
| # | asset | owner | res | format | MB now | proposed target | MB after | visual risk |
|---|---|---|---|---|---|---|---|---|
| 1 | SIGN atlas pages (world_perf.js, <=3 pages) | world | 3x 2048^2 | runtime canvas | 63.8 | pre-bake static signs offline -> KTX2 UASTC 2048 (alpha) | 16.0 | low |
| 2 | textTex sign originals (sign(), ~30, estimated count) | world/UI | 1024x256 | canvas | ~39.9 | 512x128, or dispose after pack and recreate inside NEAR | ~10.0 | low far, medium close-up |
| 3 | wardrobe/riders/caali-g.glb CaaliG_atlas (player) | character | 2048^2 | webp | 21.3 | 2K ETC1S (player cap 2K) | 2.7 | low |
| 4 | WITHHELD_CHAR/WITHHELD_CHAR-npc.glb WITHHELD_CHAR_atlas_c_eyes | character (NPC) | 2048^2 | webp | 21.3 | 1K ETC1S (NPC cap) | 0.7 | medium (eyes in the atlas: check face close-up) |
| 5 | asphaltMaps map/rough/normal | world | 3x 1024^2 | canvas | 16.0 | bake offline: ETC1S color+rough, UASTC normal, 1K | 2.7 | low |
| 6 | meshy/ikki-meshy-skate.quest-draco.glb ikki_atlas | character (NPC) | 1365x2048 | webp | 14.2 | 683x1024 ETC1S | 0.4 | medium |
| 7 | cvTex misc (18 sites) | world/FX | up to 1024^2 | canvas | 13.0 | cap 512 | 5.3 | low |
| 8 | textures/facade_albedo.jpg (base64 in html) | world (hero) | 2048x1024 | jpg | 10.6 | keep 2048x1024, ETC1S | 1.3 | low |
| 9 | textures/facade_nr.jpg (packed normal+rough) | world (hero) | 2048x1024 | jpg | 10.6 | keep res, UASTC linear | 2.7 | medium (rough channel) |
| 10 | emblemTex crew emblems (~8) | world | 512^2 | canvas | 10.6 | 256^2 or one shared atlas | 2.7 | low |
| 11 | MAP world map | UI | 1600x900 no mips | canvas | 5.5 | 1024x576 | 1.7 | low |
| 12 | WITHHELD_CHAR_atlas_mr / turfAtlas / patch / skate 1K x3 / grafAtlas | char/world/FX | 1K-2K | webp/png/canvas | 5.3 each | NPC ORM 512 ETC1S; turf 1024x256; skate 1K ETC1S + UASTC normal; patch 512 UASTC; grafAtlas keep RGBA8 (channel masks) | 0.2-1.3 each | low |
| 13 | 7 crew normal_bake (512^2) + 7x crew atlas | character (NPC) | 512^2 / 512x128 | png | 9.3 + 2.3 | UASTC 512; ONE shared atlas Texture | 2.3 + 0.04 | low |

Duplicates / waste:
- **Crew atlas 512x128 (sha 75200a21b7cc) is embedded in all 7 NPC .quest.glb (plus caali-rider/fp)** and uploaded once per rider. Share one Texture in the loader, cache by image hash/URI.
- **caali-g.glb CaaliG_atlas_n (2048^2, 7 KB, i.e. flat)** gets downloaded and decoded, but `noNormal:true` drops it. Strip it from the GLB (saves decode time and ~21 MB of transient CPU RAM).
- The 7 crew normal_bakes differ (different sha): no dedup.
- Hidden sign originals duplicate the pixels already copied into the atlas pages (~40 MB).
- Materials: every GLTFLoader load creates its own Material/Texture objects, so the 7 crew riders get 7 identical toon/atlas material sets. A shared-material cache keyed on the texture hash would also help batching.

## 3. Totals
| | MB (static est.) |
|---|---|
| GLB + standalone images, GPU-resident | 120.2 |
| Procedural canvas/data | ~174.3 |
| **Now** | **~295** (overlay says 393) |
| Same set, KTX2 only (no resize): all UASTC / all ETC1S | 74 / 37 (GLB+file part only gains; canvases need baking) |
| **After step 4 plan (caps + KTX2 + sign/canvas fixes)** | **~74** (GLB/files ~14, procedural ~60) |
Measured KTX2 samples (toktx 4.4.2, /tmp only, nothing swapped): WITHHELD_CHAR color 2048^2 ETC1S q128 + mips = 425 KB file (GPU ~2.7 MB as ETC2). at-skate 1K normal UASTC q1 + zstd18 + mips = 922 KB file (GPU ~1.3 MB as ASTC). 11 mip levels, so mips are confirmed.

## 4. Step 4 plan (order of work)
1. **Overlay fix first** (tiny, owner Rydah Systems / me): `texMem()` also walks `m.uniforms`, uses per-format bpp (CompressedTexture: ASTC/ETC2 = 1 or 0.5, RGBA8 = 4), uses the mip factor only when minFilter is a mipmap filter, and reports both "uploaded" (`renderer.properties.get(t).__webglTexture`) and "attached". Gate: tests/perf_overlay.py.
2. **Free wins, no art change:** share the crew atlas Texture across riders, strip the flat CaaliG normal, and dispose or downsize the hidden sign originals (512x128) with a rebuild inside NEAR. ~-50 MB. Gate: demo_smoke CORE, graffiti.py (signs/tags), riders render shots.
3. **Merge the KTX2 loader:** `perf/patch_draco.py.ktx2-candidate` (opt-in `?ktx2=1`, maps .quest.glb -> .quest2-ktx2.glb, libs/ktx2/KTX2Loader.classic.js + libs/basis/). Make sure libs/ktx2 and libs/basis are copied by package_pwa.sh. Gate: smoke with and without ?ktx2=1, ikki_quest_test, before/after shots (SWAP_PENDING.md list).
4. **Re-encode characters with `tools/quest_pipeline.py`** (KTX2+Draco, per-slot caps): player caali-g 2K color ETC1S (normal dropped), WITHHELD_CHAR/Ikki NPC 1K color + 512-1K ORM ETC1S + UASTC normal, crews UASTC normal 512, skates 1K. Outputs stay next to the originals (refuses to overwrite). compare_outputs.py material diff. ~-100 MB.
5. **World textures:** facade albedo ETC1S + facade_nr UASTC (hero, keep 2048x1024; patch_facades.py base64 -> KTX2 data URI or file). Asphalt baked offline to KTX2 1K. Turf 1024x256, emblems 256 or shared, cvTex cap 512, MAP 1024x576. ~-35 MB. Owners: Palma (world) / Systems (graffiti/turf/map); I provide the encoder commands.
6. **Sign atlas pages** pre-baked offline to KTX2 UASTC (static text only, dynamic signs stay canvas). ~-48 MB. Gate: day/night sign shots, perf_seed7 draw calls unchanged.
7. **Make ?ktx2=1 the default** after integrator sign-off, then measure on a real Quest 3 (OVR Metrics GPU memory). That is the first non-static number.
Integrator gate tests needed: perf_overlay.py, demo_smoke CORE, graffiti.py, heat.py (signs/FX), gamepad + attacks unaffected, rider bodyshots / before-after colour shots, perf_seed7 (calls must not rise).
Expected: ~295 -> ~74 MB static (~70% under the 256 MB budget, which leaves room for step 5 PBR).

## 5. What Palma's step 5 PBR needs from step 4
- The **KTX2Loader wired into every GLTFLoader site** (candidate gate -> default), the basis transcoder shipped in libs/basis/, and a `SR_KTX2.loader()` she can call for standalone `.ktx2` (non-GLB) world textures.
- **Conventions:** baseColor + emissive = sRGB (`--assign_oetf srgb`, texture.encoding=sRGBEncoding), ETC1S. **ORM packed glTF-style: R=AO, G=roughness, B=metalness**, linear, ETC1S at q>=128 (UASTC if banding). **Normals: tangent-space OpenGL +Y (glTF), linear, UASTC + zstd, 2-channel-safe, never ETC1S**. No flipY for KTX2 (flipY=false). Mips always (genmipmap). Power-of-two preferred.
- **Caps:** player 2K color / 1K normal+ORM, NPC 1K, world 1K or 512 (hero surfaces such as the facade atlas may stay 2K), UI/decals as needed. Budget target for step 5 additions: <=100 MB on top of ~74.
- The fixed overlay MB (step 4.1) so her CC0 PBR sets can be checked against the budget.
