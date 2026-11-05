# Crew rider diag + Quest pass (2026-10-29, CDT)

## Repro: NOT reproduced
- Current build (`sky-rydahs-v3-ikki.html?player=ikki`), a copy without the patch_draco hook (`nodraco.html`), and the PWA build (`sky-rydahs-pwa/site/index.html`, 00:17) all render the 7 NPC crew riders correctly in headless Chromium/SwiftShader. LOD0, LOD1 and LOD2 were each forced at 3 m and look correct.
- Skinning on the CPU (boneTransform over the merged SkinnedMesh) gives sane boxes about 1.8 m tall, with feet at y=0, for every rider. The skeleton has 19 bones, bindMatrix det=1, and the IBMs look sane.
- The hook made no visible difference to the riders: shots/compare-hook-before_nodraco_pwa.png. Pixel differences come only from ground-texture streaming.
- The GLBs are plain. They use float32 attributes and UNSIGNED_BYTE joints, have no Draco, meshopt or quantization, and embed their PNGs (512² normal_bake and a 512×128 atlas). The only extension is KHR_materials_emissive_strength. The md5 of the source, PWA and deploy copies match, and the source files are unchanged since 10-28 08:07–08:11 (caali 03:14).
- Root cause: unknown. It is most likely specific to the device or XR, because the riders are fine on desktop with SwiftShader. There is one real trap: riders.js `rMerge` concatenates raw attribute arrays across primitives and edits `position.array` for expressions. Any quantized or meshopt rider GLB (KHR_mesh_quantization, which has a per-primitive dequant transform) would collapse into clumps or shards. Don't ship quantized/meshopt riders. That is why the Quest pass uses Draco, which decodes to Float32.
- Gotcha for the patch_wardrobe owner (I didn't edit it): in initRiders, `need` has 2 entries but `L` has 3 after the meshopt_decoder insert. The checks are off by one. They work today only because THREE.BufferGeometryUtils isn't preloaded.
- Harmless warning: "GLTFLoader: Custom UV set 1 for texture normalMap". riders.js replaces the materials anyway.
- Distance culling leaves far NPC holders at (0,0,0) while they are hidden. They are not rendered there.

## Fix / Quest pass
- `<crew>-rider.quest.glb` (gltf-transform 4.5.1 `draco`, defaults) sits next to each original. Node names, the skin, the 8 morph targets and both textures are preserved. The textures are already ≤512 and were not resized. caali-rider.glb and code-e-rider.glb were skipped (Caali-related, and code-e isn't in CREWS).
- `patch_crew_quest.py` is appended to build_ikki.sh (backup build_ikki.sh.bak-crewquest-*). NPC crew riders now load the .quest.glb, and `?crew=orig` loads the originals. The player/Code:E rider is untouched.

| rider | orig | quest (Draco) |
|---|---|---|
| anubis | 2.85 MB | 0.79 MB |
| behemoth | 2.65 MB | 0.97 MB |
| genesis | 2.76 MB | 1.02 MB |
| kogarasumaru | 2.88 MB | 1.02 MB |
| sleeping-forest | 2.65 MB | 0.98 MB |
| static-angels | 2.78 MB | 1.02 MB |
| tool-toul-to | 2.81 MB | 0.97 MB |
- Tris across LOD0+1+2: about 24–26k per file (LOD0 13.4–15.4k). Draco dropped 0–1% as degenerates.
- Texture memory: decoded RGBA+mips is about 1.75 MB per rider. Only the 512×128 atlas (~0.35 MB) is sampled by the toon shader.

## Test
- Rebuilt; patch_crew_quest applied. AFTER: 7/7 .quest.glb loaded (200), 0 page errors, 0 console errors. The 9 warnings are the AudioContext autoplay warning and 8× the UV-set warning, same as BEFORE.
- Skinned boxes match BEFORE within 1–2 cm.
- Shots: shots/before-*.png, shots/after-*.png, shots/compare-before_after-d3.png. BEFORE is not broken, see above.
- WITHHELD_CHAR: 0 case-insensitive hits in the built HTML, and no WITHHELD_CHAR files in skyrydahs-characters or the PWA site.
- Scripts: diag.py, pos.py, probe.py, nodraco.html.

## Follow-up 2026-10-29 (CDT): Portside clumps with ?player=caali, ROOT CAUSE FOUND
- Repro: `?player=caali` with `&tier=quest` and with `&tier=hd`. Player parked at Portside (-6,0,40) after a 4 s W-ride, same camera as caalig.py "34". Dark clumps float beside the player, and the skates show shards.
- They are NOT crew NPC riders. Hiding `RIDERS.player` removes them, and hiding all NPCs, the ref Caali or the Ikki NPC changes nothing. In the onlyRiders/player-hidden test the clumps go away only when the player is hidden. NPC skeletons: 19 bones each, 0 bone uuids shared with the player, bindDet 1, sane bounds. The only visible skinned mesh in Ride.group is CaaliG_LOD0.
- Cause: caali-g.glb and caali-g-hd.glb are KHR_mesh_quantization files. POSITION is i16_norm with values in [-1,1], and the dequant is folded into the skin IBMs. Offline I computed D = meshWorld⁻¹·boneWorld·IBM; it is constant over all 70 joints (dev 5e-6): scale 0.9335, t=(0.0039, 0.7802, -0.0308). The custom `_WC` wheel-centre attribute is float **metres** (y≈-0.065), but the wheel verts sit at quantized y≈-0.9. IKKI_AT_VERT spins wheel verts around `_wc` in mesh space, so every wheel orbits a pivot ~0.8 m away and turns into the floating clumps and skate shards. `uComp` and `vRestY` are also in the wrong units. Ikki's GLBs use float positions, so Ikki is fine.
- Fix: new `patch_quant_fix.py`, appended to build_ikki.sh (backup build_ikki.sh.bak-quantfix-*). It adds `SR_DEQUANT(root)` at the top of loadIkki. For skinned meshes with non-float POSITION and a `_wc` attribute, it rewrites POSITION as Float32 = D·q and sets each boneInverse *= D⁻¹, so the skinned result is identical. D measured in game: 0.9335/0.7802 (LOD0), which matches the offline value. `?dequant=0` gives the old behaviour (used for the BEFORE shots). patch_wardrobe.py was not touched, and no diff is needed (see patch_wardrobe.proposed.diff for the asset-side alternative).
- Shots in shots/caali-portside/: before|after-caali-quest, before|after-caali-hd, after-ikki, after-caali-quest-crew-orig, compare-before_after.png. Clumps are present in BEFORE and gone in AFTER on both tiers. Ikki is clean; ?crew=orig changes nothing. The camera is fixed in code, but backgrounds differ slightly between some pairs because the player isn't at exactly the same spot after the W-ride.
- Errors: 0 page / 0 console errors in all 6 runs. 9 warnings (AudioContext autoplay + GLTFLoader UV-set) in each.
- Side effect: vRestY is now in metres for Caali G, so the IKKI_AT face/neck skin term (`step(1.3,vRestY)`) now applies to Caali G as designed. This is a slight shading change on the face.
- gamepad: 33/33 (perf/gamepad-diag/run3-after-quantfix.log). WITHHELD_CHAR: 0 hits in the build. package_pwa.sh was not rerun: no new assets, and the patch lives in the HTML.
