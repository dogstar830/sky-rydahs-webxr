# Quest asset pipeline (Rydah Optimizer)
Local tooling only. Nothing here is wired into the game, and these tools never modify an existing GLB.

## Files
- `quest_pipeline.py`, with the `quest_pipeline.sh` wrapper: takes an input GLB and writes `<name>.quest.glb`, plus `<name>.quest-ktx2.glb` if you pass `--ktx2`.
- `quest_transform.cjs`: the glTF-Transform API worker. `quest_pipeline.py` calls it.
- `glb_inspect.py`: a read-only inspector. It shows tris per mesh/LOD, prims, materials, texture dims and slots, estimated GPU memory, and flags.
- `lod_report.py`: regenerates `perf/lod-budgets.{csv,json}` and prints the markdown table.
- `ktx/`: KTX-Software 4.4.2 (`ktx`, `toktx`), unpacked locally from the Khronos .deb. Nothing was installed system-wide.
- glTF-Transform 4.5.1 (CLI + API + sharp + draco3dgltf + meshoptimizer) lives in `/workspace/tools/gt/node_modules`. Override that location with `GT_NODE_MODULES`.

## Usage
```
tools/quest_pipeline.sh IN.glb --out-dir OUT/            # Draco, base 2048 / normal 1024 / ORM 1024
  --geometry draco|meshopt16|none                        # meshopt16 needs a visual check before shipping
  --max-base 2048 --max-normal 1024 --max-orm 1024
  --keep-crisp 'face|head|skate' --crisp-max 2048        # regex on texture/material names; matches keep up to crisp-max
  --simplify 110000                                      # target LOD0 tris (meshes named *LOD0*), off by default
  --ktx2                                                 # also write .quest-ktx2.glb (UASTC normals, ETC1S colour/ORM/emissive)
  --pot [near|up]                                        # snap texture dims to powers of two (bare --pot = near); capped by --max-*
                                                         # DEFAULT with --ktx2: 'up' for the .quest-ktx2.glb passes (desktop BC7 needs every mip a multiple of 4)
  --no-pot                                               # with --ktx2: keep source (possibly NPOT) dims
  --dry-run                                              # print the before summary and plan, write nothing
  --force                                                # replace an earlier pipeline OUTPUT (never the input)
```

**Power of two (KTX2):** with `--ktx2` and no `--pot`, the KTX2 output rounds every texture axis UP to a power of two, capped by `--max-base/--max-normal/--max-orm` (e.g. 684x342 -> 1024x512). The plain `.quest.glb` is unchanged unless you pass `--pot` explicitly. `--dry-run` now prints a per-texture `plan` line (src -> dst, POT/NPOT) for each output.

**Safety:**
- It refuses to run when the output path equals the input.
- It refuses when the output already exists (unless you pass `--force`).
- It refuses when the input is itself a `.quest*.glb` (idempotency).
- If you don't pass `--out-dir`, the output goes next to the original with the new `.quest` suffix.

**Geometry:**
- Input meshopt, Draco or quantization is removed first, so you always start from float.
- *Draco*: edgebreaker with 16-bit position and generic quantization *inside Draco only*. It decodes back to float32, so `_WC`/`_WA` stay in the same float space as POSITION.
- Skin joints and weights are kept. Primitives with morph targets are left uncompressed (KHR_draco can't store targets), and the log says so.
- *meshopt16*: reorder plus EXT_meshopt_compression. POSITION and every `_*` custom attribute stay float32. In the demo, `quantize` didn't actually change NORMAL/UV either, so the output carried no KHR_mesh_quantization.
- Check every output with the summary FLAG lines: `KHR_mesh_quantization`, a non-float POSITION, a `_WC` format mismatch, or a lost custom attribute.

**Summary contents:** size, tris per mesh/LOD, prims (the raw draw-call estimate; riders.js merges a rider to 3), materials, texture dims and format, and estimated GPU memory (RGBA8 + mips, or about 1 B/px for UASTC and 0.75 B/px for ETC1S).

## KTX2 in three.js r128 with classic scripts
**Tooling:** this works locally. glTF-Transform 4.5 needs KTX-Software 4.4 or newer (`ktx create --assign-tf`). 4.3.2 fails silently, so the pipeline now warns if the output has no `KHR_texture_basisu`. In the demo, texture GPU memory dropped about 5x (26.7 MB to 5.0 MB).

**Runtime:** r128 ships `KTX2Loader` only as an ES module (`examples/jsm/loaders/KTX2Loader.js`). There is no `examples/js` copy. The options:
1. **Bundle KTX2Loader as a UMD/IIFE with esbuild:**
   ```
   esbuild entry.js --bundle --format=iife --global-name=KTX2Shim
   ```
   `entry.js` imports `KTX2Loader` from `three/examples/jsm/...` and assigns it to `THREE.KTX2Loader`. Mark `three` as external, mapped to the global `THREE`, so the page keeps a single three.js instance.
   Then call `gltfLoader.setKTX2Loader(new THREE.KTX2Loader().setTranscoderPath('libs/basis/').detectSupport(renderer))`.
   You also need `basis_transcoder.js` and `basis_transcoder.wasm` from the **same r128 tag**, because the transcoder version must match. The r128 GLTFLoader (examples/js) already understands `KHR_texture_basisu` through `setKTX2Loader`.
2. **`examples/js/loaders/BasisTextureLoader.js`** (it exists in r128 as a classic script) **with `.basis` files**. This loads standalone textures only, not KHR_texture_basisu inside a GLB. It would mean shipping textures beside the GLBs and re-binding maps in JS after load. That's more code in riders.js and wardrobe.js, and the .basis format is deprecated upstream.

**Recommendation:** option 1.
- It's one small bundled file, `libs/ktx2loader.r128.iife.js`, plus the r128 transcoder in `libs/basis/`.
- The GLBs stay self-contained, the same way `libs/draco` is used today.
- The `.quest-ktx2.glb` outputs drop straight in.
- On Quest 3, ETC1S transcodes to ETC2 and UASTC to ASTC 4x4.

Keep `.quest.glb` (webp/png) as the fallback until the bundle passes the integrator's smoke test on a real Quest. Wiring all this up belongs to whoever owns the loaders. It was not done here.
