# Ikki Quest optimization pass — 2026-10-28

Source asset: `/workspace/skyrydahs-characters/meshy/ikki-meshy-skate.glb`. I did not modify it. All new files sit next to it.
Every timing below comes from **desktop headless Chromium using SwiftShader (a CPU software renderer). These are NOT real Quest 3 headset numbers.**

## Source asset (before)
- 1 skin (Mixamo rig) and no animations in the file. Clips are applied at runtime.
- 3 skinned meshes: `Ikki_LOD0` 19,738 tris, `Ikki_LOD1` 9,106, `Ikki_LOD2` 2,606. A `THREE.LOD` at 0/9/24 m switches between them, so **1 draw call** for whichever level is active.
- 1 material, `IkkiAtlas` (base, normal, metallicRoughness, double-sided). At runtime there are 2 materials, counting the `CrewPatch_karasu` decal: 2 tris plus a 1024x512 map.
- The file already uses `EXT_texture_webp`. Attributes: POSITION, NORMAL, TEXCOORD_0 (all f32), COLOR_0 u16, JOINTS u8, WEIGHTS f32, plus custom `_WA` and `_WC` (f32 vec3).

## Variants (all in `/workspace/skyrydahs-characters/meshy/`)
| file | size | base color | normal / MR | est. GPU tex mem (RGBA8 + mips) | geometry | runtime test |
|---|---|---|---|---|---|---|
| ikki-meshy-skate.glb (orig) | 5.27 MB | 2048x3072 | 1024x1536 | **50.3 MB** | f32 | baseline |
| ikki-meshy-skate.quest.glb | 4.73 MB | 1365x2048 | 512x768 | **19.1 MB (-62%)** | f32 (unchanged) | OK, looks the same |
| ikki-meshy-skate.quest-draco.glb | **0.87 MB (-83%)** | 1365x2048 | 512x768 | 19.1 MB | Draco (KHR_draco_mesh_compression) | **OK, loads and skins correctly, no visible regression** |
| ikki-meshy-skate.quest-meshopt.glb | 1.20 MB | 1365x2048 | 512x768 | 19.1 MB | meshopt + KHR_mesh_quantization (default: color 8-bit, normal 8-bit, weights 8-bit) | **REGRESSION: jacket/body renders darker and desaturated** (shots/cmp_face.png, third panel) |
| ikki-meshy-skate.quest-meshopt16.glb | 1.33 MB | same | same | 19.1 MB | meshopt, color/normal/weights 16-bit | built but **not browser-tested** (another headless job held the box, so I didn't overlap) |

The memory figures leave out the crew-patch decal (1024x512, ~2.8 MB), which is the same in every variant. Triangles are the same in every variant; I did no decimation.
The darkening in the meshopt variant is probably 8-bit COLOR_0 or normals feeding the toon/tint shader. The 16-bit variant should fix it, but that is unconfirmed. Meshopt also split the 1 skin into 3 because of the quantization node transforms.

## Runtime measurement (headless SwiftShader, `?player=ikki&ikki=<file>`)
Raw data: `results-{orig,quest,quest-draco,quest-meshopt}.json`.
- Textures applied at runtime match the table: map 2048x3072 → 1365x2048, normal/roughness/metalness 1024x1536 → 512x768.
- Load time to `RIDERS.ready` (all 4 ran at the same time, so this is noisy): orig 62 s, quest 30 s, draco 30 s, meshopt 33 s.
- Frame time at a 1832x1920 viewport (one eye's worth of pixels), averaged over 10 frames: 1225 / 943 / 840 / 1131 ms. These are CPU software-render numbers taken while the 4 runs competed for CPU. **They are not meaningful for Quest. Use them only as a rough sign.**
- `renderer.info.render` reported calls=1 and tris=1. That is the final post-processing (EffectComposer) pass, because info resets every pass. So I could not get real scene draw-call counts this way. Ikki's own cost is 1 draw call (2 with the patch decal; +1 with `?ikkiOutline=1`).
- `renderer.info.memory`: about 81–83 textures and 638–656 geometries for the whole scene, the same in every variant.

## Screenshots (`/workspace/v3build/perf/shots/`)
- Per variant: `{orig,quest,quest-meshopt,quest-draco}_{body,face,face34,skates}.png`, all from the same camera hooks.
- Side-by-side strips (orig | quest | meshopt | draco): `cmp_face.png`, `cmp_skates.png`, `cmp_body.png`.
- Face and Air Treks stay crisp at 1365x2048 base color. The lighting differences on the ground in the skate shots are scene/time variance, not the asset.

## Compression and loader support in this build (three r128 via CDN globals)
- **EXT_texture_webp**: already supported and used.
- **Draco: works.** It needs `examples/js/loaders/DRACOLoader.js` plus decoder files from `examples/js/libs/draco/`, then `loader.setDRACOLoader(d)`. The decoder (wasm or js, roughly 300 KB–1 MB) is fetched from `setDecoderPath` at runtime. For the offline PWA, vendor `vendor/three/examples/js/libs/draco/*` and add those files to the `sw.js` precache.
- **Meshopt:** r128 GLTFLoader supports it through `setMeshoptDecoder(MeshoptDecoder)`, using `examples/js/libs/meshopt_decoder.js` (small, the wasm is embedded). The 8-bit default variant has a visual regression, so don't ship it as is.
- **KTX2/Basis: not feasible right now.** r128 ships KTX2Loader only as an ES module (`examples/jsm`). There is no global `examples/js` build, and this page uses global THREE, so it would need a port or shim. `toktx` is also not installed on the box. If it were wired, ETC1S base plus UASTC normal would cut GPU memory to roughly 4–5 MB.

## Test harness
- `perf/sky-rydahs-v3-ikki-quest.html` is a copy of the build output. Its only changes: DRACOLoader and meshopt_decoder script tags, and a `__mkGLTF()` factory that replaces `new THREE.GLTFLoader()` in 3 places.
- `perf/ikki_quest_test.py <glb>` runs it, served from /workspace on port 8793. The server has been stopped.

## Swapping it into the build (not done)
1. **Textures only, zero risk:** point `IKKI_URL` (in `patch_ikki.py` or the source that build_ikki.sh patches) at `meshy/ikki-meshy-skate.quest.glb`, and copy that file into `sky-rydahs-pwa/site/skyrydahs-characters/meshy/`. No loader changes. You can try it now with `?ikki=<url>`.
2. **Recommended:** use `quest-draco.glb` instead. That also means adding the DRACOLoader and decoder script/vendor files, calling `setDRACOLoader` on every GLTFLoader (or using a shared factory), and adding the decoder files to the PWA precache.
3. Optional: meshopt16 after a visual check, if you'd rather avoid the Draco decode cost. Meshopt decodes faster on Quest's CPU.
