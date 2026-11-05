# KTX2 loaders candidate (Rydah Optimizer, 2026-10-29). NOT merged.
This is a candidate only. The live `patch_draco.py`, `build_ikki.sh`, `wardrobe.js`, the built HTML and the live `package_pwa.sh` are unchanged.

## Files
| file | what |
|---|---|
| `v3build/patch_draco.py.ktx2-candidate` | Copy of patch_draco.py. Stage 1 (Draco + meshopt GLTFLoader wrap, IKKI_URL) is byte-identical. Stage 2 adds one `<script>` right after the Draco wrap. That script returns at once unless the URL has `?ktx2=1`. Idempotent (`window.SR_KTX2` marker). It also runs on an already-built HTML, where it applies stage 2 only. Set `SR_HTML=/path` for dry runs. |
| `v3build/libs/ktx2/KTX2Loader.classic.js` | three@0.128.0 `examples/jsm/loaders/KTX2Loader.js` (plus BasisTextureLoader, ktx-parse, zstddec), bundled by esbuild 0.21.5 as an IIFE. `three` is aliased to `shim.js`, which re-exports `window.THREE` members. It registers `THREE.KTX2Loader`. Size **75555 bytes (~74 KB)**. Inputs: `shim.js`, `entry.js`. |
| `v3build/libs/basis/basis_transcoder.{js,wasm}` | Copied unchanged from three@0.128.0 `examples/js/libs/basis/`, the transcoder matched to r128's KTX2Loader. js 62,997 B, sha256 b352d4fb…a964. wasm 440,267 B, sha256 e7dcac72…fb5b. |
| `sky-rydahs-pwa/package_pwa.sh.ktx2-candidate` | Copy of package_pwa.sh. It also ships libs/ktx2 + libs/basis and the -ktx2 GLBs (only those that exist), with precache entries for all of them. |
| `perf/ktx2/default-path.diff` | Built HTML vs the candidate output on a /tmp copy. |

## What ?ktx2=1 does
1. A `document.write` adds `<script src="libs/ktx2/KTX2Loader.classic.js">` while the page is still parsing. That runs after three.min.js and before any game code.
2. It wraps the current (Draco-wrapped) `THREE.GLTFLoader` again. On `load(url)`:
   - It maps the URL through the data table `SR_KTX2.map`, which is generated at patch time from the files that exist. Currently that's 8 entries: `<crew>/<crew>-rider.quest.glb → <crew>-rider.quest2-ktx2.glb` for anubis, behemoth, genesis, kogarasumaru, sleeping-forest, static-angels and tool-toul-to, plus `wardrobe/riders/caali-g.glb → caali-g.quest-ktx2.glb`. URLs that don't match pass through.
   - It waits (one rAF per retry) until the game's `renderer` exists. `detectSupport` needs it, and `renderer` is created in init().
   - Then it attaches one shared `KTX2Loader().setTranscoderPath("libs/basis/").detectSupport(renderer)` via `setKTX2Loader` and calls the original load.

Without the flag nothing is wrapped, written or remapped.

## Static checks done (no browser)
- **Default-path diff:** built `sky-rydahs-v3-ikki.html` vs the candidate output: **0 lines removed or changed, 16 lines added**, all inside the single gated `<script>` after the Draco wrap. A second run says "already applied" (idempotent).
- **Inline scripts:** `node --check` on all 4 inline scripts of the candidate output: **OK**. `node --check` on the bundle: **OK**.
- **Bundle:** **0** `import`/`export` statements; 4 references to `window.THREE`. Evaluated in a node vm with a stub THREE, it registers `THREE.KTX2Loader`. The constructor reached the zstd wasm init, which needs the browser's `fetch`.
- **Gate simulation** (node vm, stub GLTFLoader):
  - `""` and `?fps`: GLTFLoader untouched, 0 document.write.
  - `?ktx2=1&fps`: `genesis-rider.quest.glb → genesis-rider.quest2-ktx2.glb`, ktx2Loader attached, an unmapped URL is left alone.
- **Package dry run:** `SRC=/tmp/ktx2_gate.html OUT=/tmp/pwa_ktx2_test`, exit 0. libs/ktx2 + libs/basis + 8 -ktx2 GLBs were copied and are in sw.js precache.

## Gate test (integrator only, holding .testlock)
1. Build a scratch copy:
   ```
   cp sky-rydahs-v3-ikki.html /tmp/g.html && SR_HTML=/tmp/g.html python3 patch_draco.py.ktx2-candidate
   ```
   Or use it in place of patch_draco.py in a gate build.
2. **Default path:** load without `?ktx2`. Screenshots must be **pixel-identical** to the current build at spawn, causeway, Portside and 98 Bridge, day and night. Expect the same `?fps` calls/tris and no new console messages. Network: no requests to libs/ktx2 or libs/basis.
3. **`?ktx2=1`** (+ `&fps`):
   - Network shows KTX2Loader.classic.js, basis_transcoder.js and .wasm, and the 7 `*-rider.quest2-ktx2.glb` + `caali-g.quest-ktx2.glb`.
   - The console should have no "setKTX2Loader must be called" error.
   - Compare crew NPC colours against the default (ETC1S on a 512 toon atlas: check for banding). Compare Caali G face, skates and the Gr8yzone logo.
   - Draw calls and tris should be unchanged; texture memory should be lower.
4. **On Quest 3:** the same `?ktx2=1` URL. detectSupport should choose ETC2/ASTC there.
5. **Risk to watch:** these KTX2 files were written by KTX-Software 4.4 and gltf-transform 4.5, and r128's 2021 KTX2Loader is older. If it rejects a file (DFD or supercompression errors), the riders fall back to nothing. Then report the error, and I'll re-encode (e.g. without zstd on the UASTC normals).

---
## Proposed default: KTX2 on Quest (Rydah Optimizer, 2026-10-30 09:35 CDT). Rigger's conditions (Palma + Forge agree)
Status: build_ikki.sh runs patch_draco.py.ktx2-candidate since 09:31, but the gate is still **opt-in** (`?ktx2=1`). Flipping it to Quest-default is one line in our candidate (below) and needs the team OK.

### (a) URL map audit (patch_draco.py.ktx2-candidate, backup .bak-audit-*)
Generated table (files that exist now), 12 entries:
| URL tail | -> KTX2 file | built from |
|---|---|---|
| anika/anika-rider.draco-webp.glb | anika/anika-rider.opt-ktx2.glb (2,981,360 B) | anika-rider.glb (03:30 symmetric-shoulder source) |
| anika/anika-npc.draco-webp.glb | anika/anika-npc.opt-ktx2.glb (1,480,180 B) | anika-npc.glb (03:30) |
| wardrobe/riders/caali-g.nonormal.glb | caali-g.nonormal.ktx2.glb (2,695,512 B, md5 9e73946d…) | caali-g-v2.rigged.glb = live caali-g.glb (md5 b92e2383…) |
| wardrobe/riders/caali-g-hd.glb | caali-g-hd.ktx2.glb (4,221,336 B, md5 81537d96…) | caali-g-v2-hd.rigged.glb (md5 b1bb5893…) |
| <crew>/<crew>-rider.quest.glb ×7, meshy/ikki-meshy-skate.quest-draco.glb | *.s4-ktx2.glb | step 4.4 (unchanged) |
Changes: removed the bare `anika/anika-{rider,npc}.glb` keys (that is the `?texfull=1` raw path; it stays unmapped, like caali-g.glb). Added an assert that refuses any `.quest-ktx2` target, so the stale uncompressed anika-*.quest-ktx2.glb (18.6/6.7 MB, pre-sym) and caali*.quest-ktx2 files can never be mapped. Matching is `endsWith`, no key is a suffix of another.
Anika on Quest (patch_crew_quest.py, Rigger already applied the tiers diff): url = `anika-rider.draco-webp.glb` (default/hd/Quest), `?texfull=1` -> anika-rider.glb. So: KTX2 on -> map -> anika-rider.opt-ktx2.glb; `?ktx2=0` (or gate off) -> anika-rider.draco-webp.glb. npc/npcQuest = anika-npc.draco-webp.glb (-> opt-ktx2 when on; no NPC spawn yet).
**Proposal (ours, not applied):** Quest default gate in the candidate, line `window.SR_KTX2={on:...}`:
`on: /[?&]ktx2=1(&|$)/.test(location.search) || (/OculusBrowser|Quest/i.test(navigator.userAgent) && !/[?&]ktx2=0(&|$)/.test(location.search))`
**Proposal (Rigger, patch_crew_quest.py):** the stale comment "?ktx2=1 maps to *.opt-ktx2 only once SR_KTX2 lands" can now say "SR_KTX2 map: draco-webp -> opt-ktx2".

### (b) Re-verified mapped KTX2 vs current sources (09:35)
| file | joints | names | IBM max diff | springs | tris per LOD |
|---|---|---|---|---|---|
| anika-rider.opt-ktx2.glb | 107=107 | identical | 0 | 16=16 identical | 104,965/33,369/11,142 same |
| anika-npc.opt-ktx2.glb | 107=107 | identical | 0 | 16=16 identical | 23,772/11,134/4,390 same |
| caali-g.nonormal.ktx2.glb | 91=91 | identical | 0 | none (v2 has none) | 104,192/33,082/11,034 same |
| caali-g-hd.ktx2.glb | 91=91 | identical | 0 | none | 250,300/33,082/11,034 same |
(Earlier today: validate 0 errors, decode error ≤0.012 mm, _WC/_WA Float32 metres on all four.)

### (c) Shared v2 skate textures (jackets.js `SR_SKATE.tex()` = shared/at-skate/at-skate-meshy-v2-1k + ''|'-mr'|'-normal' + '.png', TextureLoader, flipY false, albedo sRGBEncoding, others Linear)
Sources: 3 × 1024² RGB PNG (POT): 1,129,247 + 924,246 + 1,033,212 = **3.09 MB disk, ~16 MB GPU** (RGBA8 + mips).
KTX2 built (new files, PNGs untouched) in shared/at-skate/ktx2/:
| file | encoding | size | PSNR vs PNG | md5 |
|---|---|---|---|---|
| at-skate-meshy-v2-1k.ktx2 | ETC1S q192, **sRGB transfer** (`--assign-tf srgb`, = toktx --assign_oetf srgb), 11 mips | 182,435 B | 35.3 dB | 8c41cfe6b7ba99cc07419f8f0ab5162f |
| at-skate-meshy-v2-1k-mr.ktx2 | UASTC q2 RDO 1.0 zstd 20, linear | 619,855 B | 43.3 dB | d30bafad5a651dee61db81791cbd36c7 |
| at-skate-meshy-v2-1k-normal.ktx2 | UASTC q2 RDO 1.0 zstd 20, linear | 783,077 B | 39.3 dB | 1a930016af66646f16a171d0e5378b42 |
Total **1.59 MB disk (−1.5 MB), ~3 MB GPU (−13 MB)**. Recommend KTX2 on Quest: one shared material for every rider, so the 13 MB is saved once. Loader diff for Rigger: perf/ktx2/jackets_skate_ktx2.proposed.diff (r128 KTX2Loader does not set encoding: the diff sets sRGBEncoding/LinearEncoding explicitly, PNG fallback on error). PWA packaging must also ship shared/at-skate/ktx2/.

### Update 09:47 CDT: Quest default APPLIED in the candidate + normal strip
- **Gate (applied, backup patch_draco.py.ktx2-candidate.bak-questdefault-*):** the gate script runs at line ~77 of the built html, **before** `const WARDROBE_TIER` (line ~804), so it cannot key on the variable. It mirrors WARDROBE_TIER verbatim: `?tier=hd|quest` wins, else `/OculusBrowser|Quest|Android|iPhone|iPad/i` on the UA -> 'quest', else 'hd'. `on = ?ktx2=1 || (tier==='quest' && ?ktx2!=='0')`; `SR_KTX2.tier` is exposed. Note: like WARDROBE_TIER, Android/iOS count as 'quest'. (The earlier one-liner in this README used a narrower Quest-only regex; superseded.)
- Verified on /tmp/ktx2q.html (live html copy + candidate, live html NOT rebuilt): node --check 7/7 inline scripts OK; diff vs live = 0 lines removed/changed, 16 added (gate only). Gate simulation (node vm): Quest UA none -> on, 1 loader write, 12 map entries; Quest ?ktx2=0 -> off; Quest ?tier=hd -> off; desktop none -> off, 0 writes, nothing wrapped (default path unchanged); desktop ?tier=quest -> on; ?tier=quest&ktx2=0 -> off; desktop ?ktx2=1 -> on.
- **Normal strip (JSON-only + BIN compaction, perf/glb_strip_normals.py):** Anika inherits `noNormal:true` (`WARDROBE_RIDERS.anika=Object.assign({},WARDROBE_RIDERS.caali,{…})`), Caali has it directly. normalTexture + its texture/image/bufferView removed; every accessor (meta+bytes), Draco bufferView bytes, meshes, skins, nodes identical. anika-rider.opt-ktx2.glb 2,981,360 -> **2,491,112 B**, anika-npc.opt-ktx2.glb 1,480,180 -> **938,348 B**, caali-g.nonormal.ktx2.glb 2,695,512 -> **2,190,296 B**. anika_regen.sh now ends with the same strip.
