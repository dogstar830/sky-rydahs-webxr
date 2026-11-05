# Sky Rydahs character LOD budget report
Generated 2026-10-29 ~04:40 CDT by Rydah Optimizer, read-only on all assets. Regenerate the table with `python3 v3build/tools/lod_report.py`. Data: `lod-budgets.csv`, `lod-budgets.json`.

**Budgets:** Quest has a 150 draw-call cap for the whole frame. Player LOD0 should be 100-120k tris (Quest tier). NPC LOD0 must be 30k tris or less. Draco is the default. Meshopt is only allowed at 16-bit after a visual check. POSITION must never be quantized on riders, and `_WC` must stay in the same format as POSITION.

**How to read this:**
- Tris are counted from index accessors. "LOD0 prims" means draw calls before `riders.js` merges them. rMerge collapses a crew rider to 3 calls: toon body, outline and glow.
- Texture GPU memory is the uncompressed RGBA8 size plus mips. KTX2 cuts it about 4-5x.
- Tier: `desktop` means a `.quest.glb` sibling exists, or the file is HD. `quest` means a Quest file. `both` means one file serves both.
- The "in build" column only checks for a literal filename in the HTML. Crew rider URLs are built at runtime, so a "no" there does not mean the file is unused.
- There is a 32 MB per-asset texture guide for Quest. That is a team guideline I'm proposing, not an agreed budget.

## Summary, worst first
1. **DEPRECATED, FAIL `meshy/ikki-meshy-rigged-opt.glb`:** don't use it. POSITION is quantized (int16), so `_WC` and rMerge would break. It's not in the build. Don't use it. Re-export it as float, or retire it.
2. **WARN `wardrobe/riders/caali-g.glb` (Quest player):** 98.3k LOD0 is about 1.7k under the 100k floor. That's fine and doesn't need to change. POSITION/_WC are float, but `KHR_mesh_quantization` is still declared because NORMAL/UV are quantized. That's allowed, but strip it on the next re-export. The 2048 base + 2048 normal atlas is about 43 MB on the GPU. The pipeline with `--max-normal 1024` cuts it to about 27 MB, and KTX2 to about 5 MB.
3. **WARN `WITHHELD_CHAR/WITHHELD_CHAR-rider.glb`:** it has been rebuilt since the board entry. It's now 80.9k LOD0 (1.93 MB), under the 100k player floor and still a placeholder. Texture memory is 43 MB (2048 colour + 2048 MR). Cap MR at 1024 and the KTX2 demo gets it to 5 MB.
4. **WARN `WITHHELD_CHAR/WITHHELD_CHAR-npc.glb`:** 29.0k LOD0 is under the 30k cap, so tris pass. Texture memory is 43 MB, which is a lot for an NPC. Use 1024 maps, or share the rider atlas.
5. **WARN Ikki Meshy files:** `ikki-meshy-skate(.quest/-v2).glb` LOD0 is about 19.7k. If Ikki is the player he's far under 100k. That's not a perf problem, but it's a fidelity gap, the same situation as WITHHELD_CHAR. The `.quest.glb` is 4.5 MB with **no geometry compression**, and the Draco A/B copy is 0.8 MB. Promote `ikki-meshy-skate.quest-draco.glb` after a visual check, or run it through the pipeline.
6. **WARN wardrobe (Quest) items** (bomber, cargo, head, hair, tee): each has its own 2048 texture set (64 MB per item, 5 items, about 320 MB uncompressed if all are loaded separately). No Draco. Bake them into one atlas, as caali-g.glb already does. The Quest build should load `caali-g.glb`, not the separate items.
7. **WARN skate modules:** `at-skate-meshy.glb` (3.4k tris, 9 prims) and `at-skate-module.glb` (15 prims) each cost one draw call per primitive until they're merged. See the Standard A-T section below.
8. **PASS:**
   - All 8 crew `*-rider.quest.glb` files (13.5-15.4k LOD0, Draco, 2 materials, 512 textures).
   - Crew desktop riders and FP bodies (3k).
   - `caali-g-hd.glb`: 296k LOD0, desktop-only. Quest uses caali-g.glb at 98k, so it's OK. It has 171 MB of 4K textures, so never load it on Quest.
   - All of `wardrobe_hd/` is desktop-only.
9. **Note:** `caali/caali-rider.glb` and `code-e/code-e-rider.glb` are byte-identical (same size and tris). That's probably a placeholder copy. Neither has a `.quest.glb`, which explains the old package_pwa WARN.

## Full table
| status | asset | in build | role | tier | MB | LOD0 / LOD1 / LOD2 tris | LOD0 prims | mats | max tex | tex GPU MB | compression | notes |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| FAIL (DEPRECATED) | meshy/ikki-meshy-rigged-opt.glb | no | player | both | 1.06 | 15,778 / - / - | 1 | 1 | 1024 | 5.3 | webp,quant | quantized POSITION / _WC mismatch; LOD0 15,778 < 100k target (under budget); no geometry compression |
| WARN | wardrobe/riders/caali-g.glb | yes | player | quest | 3.63 | 98,341 / 34,656 / 11,232 | 1 | 1 | 2048 | 42.7 | meshopt,webp,quant | KHR_mesh_quantization declared (POSITION float: OK, but strip on re-export); LOD0 98,341 < 100k target (under budget); tex GPU 43 MB (>32 MB on Quest) |
| WARN | WITHHELD_CHAR/WITHHELD_CHAR-rider.glb | yes | player (placeholder) | both | 1.93 | 80,971 / 43,480 / 15,398 | 1 | 1 | 2048 | 42.7 | webp,draco | LOD0 80,971 < 100k target (under budget); tex GPU 43 MB (>32 MB on Quest) |
| WARN | WITHHELD_CHAR/WITHHELD_CHAR-npc.glb | yes | NPC | both | 1.39 | 28,960 / 14,479 / 6,398 | 1 | 1 | 2048 | 42.7 | webp,draco | tex GPU 43 MB (>32 MB on Quest) |
| WARN | meshy/ikki-meshy-skate-v2.glb | no | player | both | 5.0 | 19,746 / 9,154 / 2,616 | 1 | 1 | 2048 | 64.0 | webp | LOD0 19,746 < 100k target (under budget); tex GPU 64 MB (>32 MB on Quest); no geometry compression |
| WARN | meshy/ikki-meshy-skate.quest.glb | no | player | quest | 4.51 | 19,738 / 9,106 / 2,606 | 1 | 1 | 2048 | 18.2 | webp | LOD0 19,738 < 100k target (under budget); no geometry compression |
| WARN | wardrobe/jacket/caali_bomber.glb | no | wardrobe item | both | 2.0 | 16,000 / 6,000 / 1,999 | 1 | 1 | 2048 | 64.0 | webp | tex GPU 64 MB (>32 MB on Quest); no geometry compression |
| WARN | wardrobe/pants/caali_cargo.glb | no | wardrobe item | both | 1.57 | 16,000 / 6,000 / 1,999 | 1 | 1 | 2048 | 64.0 | webp | tex GPU 64 MB (>32 MB on Quest); no geometry compression |
| WARN | wardrobe/head/caali_head.glb | no | wardrobe item | both | 1.03 | 15,999 / 5,999 / 1,998 | 1 | 1 | 2048 | 64.0 | webp | tex GPU 64 MB (>32 MB on Quest); no geometry compression |
| WARN | meshy/caali-meshy-rigged.glb | no | player | both | 9.16 | 15,778 / - / - | 1 | 1 | 2048 | 64.0 | none | LOD0 15,778 < 100k target (under budget); tex GPU 64 MB (>32 MB on Quest); no geometry compression |
| WARN | meshy/ikki-meshy-cyan.glb | no | player | both | 8.51 | 15,778 / - / - | 1 | 1 | 2048 | 64.0 | none | LOD0 15,778 < 100k target (under budget); tex GPU 64 MB (>32 MB on Quest); no geometry compression |
| WARN | meshy/ikki-meshy-rigged.glb | no | player | both | 9.16 | 15,778 / - / - | 1 | 1 | 2048 | 64.0 | none | LOD0 15,778 < 100k target (under budget); tex GPU 64 MB (>32 MB on Quest); no geometry compression |
| WARN | wardrobe/hair/caali_curly_short.glb | no | wardrobe item | both | 1.29 | 14,000 / 4,000 / 1,200 | 1 | 1 | 2048 | 64.0 | webp | tex GPU 64 MB (>32 MB on Quest); no geometry compression |
| WARN | wardrobe/top/caali_gr8yzone_tee.glb | no | wardrobe item | both | 1.02 | 12,000 / 4,000 / 1,200 | 1 | 1 | 2048 | 64.0 | webp | tex GPU 64 MB (>32 MB on Quest); no geometry compression |
| WARN | shared/at-skate/at-skate-module.glb | no | skate module | both | 0.22 | 3,452 / - / - | 15 | 0 | 0 | 0.0 | none | 15 LOD0 prims (merge to <=3) |
| WARN | wardrobe/skates/at-skate-meshy.glb | no | skate module | both | 0.31 | 3,419 / - / - | 9 | 1 | 0 | 0.0 | none | 9 LOD0 prims (merge to <=3) |
| PASS | wardrobe/riders/caali-g-hd.glb | yes | player | desktop | 6.59 | 296,338 / 34,656 / 11,799 | 1 | 1 | 4096 | 170.7 | meshopt,webp,quant | KHR_mesh_quantization declared (POSITION float: OK, but strip on re-export); desktop tier: tri budget n/a |
| PASS | wardrobe_hd/hair/caali_curly_short.glb | no | wardrobe item | desktop | 3.52 | 60,000 / 4,000 / 1,200 | 1 | 1 | 4096 | 256.0 | webp | no geometry compression |
| PASS | wardrobe_hd/jacket/caali_bomber.glb | no | wardrobe item | desktop | 3.4 | 50,000 / 6,000 / 2,595 | 1 | 1 | 2048 | 64.0 | webp | no geometry compression |
| PASS | wardrobe_hd/head/caali_head.glb | no | wardrobe item | desktop | 2.27 | 49,999 / 5,999 / 1,999 | 1 | 1 | 4096 | 256.0 | webp | no geometry compression |
| PASS | wardrobe_hd/pants/caali_cargo.glb | no | wardrobe item | desktop | 3.8 | 49,999 / 6,000 / 1,999 | 1 | 1 | 4096 | 256.0 | webp | no geometry compression |
| PASS | wardrobe_hd/top/caali_gr8yzone_tee.glb | no | wardrobe item | desktop | 2.2 | 40,000 / 4,000 / 1,200 | 1 | 1 | 4096 | 256.0 | webp | no geometry compression |
| PASS | wardrobe_hd/gloves/caali_fingerless.glb | no | wardrobe item | desktop | 1.31 | 20,000 / 2,500 / 800 | 1 | 1 | 2048 | 64.0 | webp | no geometry compression |
| PASS | meshy/ikki-meshy-skate.glb | yes | player | desktop | 5.03 | 19,738 / 9,106 / 2,606 | 1 | 1 | 3072 | 48.0 | webp | desktop tier: tri budget n/a; no geometry compression |
| PASS | static-angels/static-angels-rider.glb | no | NPC | desktop | 2.65 | 15,438 / 7,987 / 2,777 | 6 | 2 | 512 | 1.7 | none | desktop tier; no geometry compression |
| PASS | static-angels/static-angels-rider.quest.glb | no | NPC | quest | 0.97 | 15,406 / 7,921 / 2,711 | 6 | 2 | 512 | 1.7 | draco |  |
| PASS | kogarasumaru/kogarasumaru-rider.glb | no | NPC | desktop | 2.75 | 15,308 / 7,988 / 2,357 | 6 | 2 | 512 | 1.7 | none | desktop tier; no geometry compression |
| PASS | kogarasumaru/kogarasumaru-rider.quest.glb | no | NPC | quest | 0.98 | 15,296 / 7,976 / 2,345 | 6 | 2 | 512 | 1.7 | draco |  |
| PASS | genesis/genesis-rider.glb | no | NPC | desktop | 2.63 | 15,170 / 7,984 / 2,250 | 6 | 2 | 512 | 1.7 | none | desktop tier; no geometry compression |
| PASS | genesis/genesis-rider.quest.glb | no | NPC | quest | 0.97 | 15,158 / 7,972 / 2,238 | 6 | 2 | 512 | 1.7 | draco |  |
| PASS | tool-toul-to/tool-toul-to-rider.glb | no | NPC | desktop | 2.68 | 15,002 / 7,988 / 2,333 | 6 | 2 | 512 | 1.7 | none | desktop tier; no geometry compression |
| PASS | tool-toul-to/tool-toul-to-rider.quest.glb | no | NPC | quest | 0.93 | 14,918 / 7,904 / 2,321 | 6 | 2 | 512 | 1.7 | draco |  |
| PASS | sleeping-forest/sleeping-forest-rider.glb | no | NPC | desktop | 2.53 | 14,186 / 7,988 / 2,510 | 6 | 2 | 512 | 1.7 | none | desktop tier; no geometry compression |
| PASS | sleeping-forest/sleeping-forest-rider.quest.glb | no | NPC | quest | 0.94 | 14,174 / 7,976 / 2,498 | 6 | 2 | 512 | 1.7 | draco |  |
| PASS | anubis/anubis-rider.glb | no | NPC | desktop | 2.72 | 13,552 / 7,993 / 2,948 | 6 | 2 | 512 | 1.7 | none | desktop tier; no geometry compression |
| PASS | anubis/anubis-rider.quest.glb | no | NPC | quest | 0.75 | 13,488 / 7,933 / 2,888 | 6 | 2 | 512 | 1.7 | draco |  |
| PASS | behemoth/behemoth-rider.glb | no | NPC | desktop | 2.53 | 13,482 / 7,995 / 2,512 | 6 | 2 | 512 | 1.7 | none | desktop tier; no geometry compression |
| PASS | behemoth/behemoth-rider.quest.glb | no | NPC | quest | 0.93 | 13,470 / 7,983 / 2,500 | 6 | 2 | 512 | 1.7 | draco |  |
| PASS | caali/caali-rider.glb | no | NPC | both | 2.52 | 13,434 / 7,988 / 2,727 | 6 | 2 | 512 | 1.7 | none | no geometry compression |
| PASS | code-e/code-e-rider.glb | no | NPC | both | 2.52 | 13,434 / 7,988 / 2,727 | 6 | 2 | 512 | 1.7 | none | no geometry compression |
| PASS | wardrobe_hd/neck/gold_chain_thick.glb | no | wardrobe item | desktop | 1.47 | 10,000 / 1,000 / 570 | 1 | 1 | 2048 | 64.0 | webp | no geometry compression |
| PASS | wardrobe/gloves/caali_fingerless.glb | no | wardrobe item | both | 0.74 | 8,000 / 2,500 / 800 | 1 | 1 | 1024 | 16.0 | webp |  |
| PASS | wardrobe/body/base.glb | no | wardrobe item | both | 1.13 | 7,998 / 2,485 / 886 | 1 | 1 | 1024 | 8.0 | webp | no geometry compression |
| PASS | wardrobe_hd/body/base.glb | no | wardrobe item | desktop | 0.8 | 4,400 / 2,200 / 899 | 1 | 1 | 1024 | 8.0 | webp |  |
| PASS | wardrobe/neck/gold_chain_thick.glb | no | wardrobe item | both | 0.62 | 4,000 / 1,000 / 560 | 1 | 1 | 1024 | 16.0 | webp |  |
| PASS | anubis/anubis-fp.glb | no | player FP body | both | 0.57 | 2,956 / - / - | 2 | 2 | 512 | 1.7 | none |  |
| PASS | behemoth/behemoth-fp.glb | no | player FP body | both | 0.59 | 2,956 / - / - | 2 | 2 | 512 | 1.7 | none |  |
| PASS | caali/caali-fp.glb | no | player FP body | both | 0.59 | 2,956 / - / - | 2 | 2 | 512 | 1.7 | none |  |
| PASS | code-e/code-e-fp.glb | no | player FP body | both | 0.59 | 2,956 / - / - | 2 | 2 | 512 | 1.7 | none |  |
| PASS | genesis/genesis-fp.glb | no | player FP body | both | 0.59 | 2,956 / - / - | 2 | 2 | 512 | 1.7 | none |  |
| PASS | kogarasumaru/kogarasumaru-fp.glb | no | player FP body | both | 0.57 | 2,956 / - / - | 2 | 2 | 512 | 1.7 | none |  |
| PASS | sleeping-forest/sleeping-forest-fp.glb | no | player FP body | both | 0.59 | 2,956 / - / - | 2 | 2 | 512 | 1.7 | none |  |
| PASS | static-angels/static-angels-fp.glb | no | player FP body | both | 0.6 | 2,956 / - / - | 2 | 2 | 512 | 1.7 | none |  |
| PASS | tool-toul-to/tool-toul-to-fp.glb | no | player FP body | both | 0.58 | 2,956 / - / - | 2 | 2 | 512 | 1.7 | none |  |
| PASS | wardrobe/accessory/gold_pants_chains.glb | no | wardrobe item | both | 0.12 | 384 / 192 / 192 | 1 | 1 | 16 | 0.0 | webp |  |
| PASS | wardrobe_hd/accessory/gold_pants_chains.glb | no | wardrobe item | desktop | 0.12 | 384 / 192 / 192 | 1 | 1 | 16 | 0.0 | webp |  |

**Skipped:**

- WITHHELD_CHAR/WITHHELD_CHAR-npc-raw.glb (6.6 MB): -raw source
- WITHHELD_CHAR/WITHHELD_CHAR-rider-raw.glb (15.0 MB): -raw source
- meshy/airtreck-meshy.glb (56.1 MB): Meshy A-T source (1.8M tris, build input only)
- meshy/ikki-meshy-skate.quest-draco.glb (0.8 MB): compression A/B test copy
- meshy/ikki-meshy-skate.quest-meshopt.glb (1.1 MB): compression A/B test copy
- meshy/ikki-meshy-skate.quest-meshopt16.glb (1.3 MB): compression A/B test copy
- shared/crew-coins/_archive/volt-coin.glb (0.7 MB): archive
- shared/crew-coins/anubis-coin.glb (0.7 MB): crew coin prop (not a character)
- shared/crew-coins/behemoth-coin.glb (0.7 MB): crew coin prop (not a character)
- shared/crew-coins/code-e-coin.glb (0.9 MB): crew coin prop (not a character)
- shared/crew-coins/genesis-coin.glb (0.9 MB): crew coin prop (not a character)
- shared/crew-coins/kogarasumaru-coin.glb (0.9 MB): crew coin prop (not a character)
- shared/crew-coins/rust-claw-coin.glb (0.9 MB): crew coin prop (not a character)
- shared/crew-coins/sleeping-forest-coin.glb (0.8 MB): crew coin prop (not a character)
- shared/crew-coins/static-angels-coin.glb (0.9 MB): crew coin prop (not a character)
- shared/crew-coins/team-storm-coin.glb (0.8 MB): crew coin prop (not a character)
- shared/crew-coins/tool-toul-to-coin.glb (0.7 MB): crew coin prop (not a character)
- wardrobe/body/base-v1.glb (0.9 MB): -v1 (superseded)
- wardrobe/riders/caali-g-4k.glb (15.2 MB): -4k
- wardrobe/riders/caali-g-flatnormals.glb (15.2 MB): flatnormals backup
- wardrobe/riders/caali-g-hd-raw.glb (29.4 MB): -raw source
- wardrobe/riders/caali-g-raw.glb (15.3 MB): -raw source
- wardrobe/riders/caali-g-v1.glb (5.5 MB): -v1 (superseded)
- wardrobe/v1_items/caali_bomber.glb (0.5 MB): v1 wardrobe items (superseded)
- wardrobe/v1_items/caali_cargo.glb (0.4 MB): v1 wardrobe items (superseded)
- wardrobe/v1_items/caali_curly_short.glb (0.2 MB): v1 wardrobe items (superseded)
- wardrobe/v1_items/caali_fingerless.glb (0.2 MB): v1 wardrobe items (superseded)
- wardrobe/v1_items/caali_gr8yzone_tee.glb (0.2 MB): v1 wardrobe items (superseded)
- wardrobe/v1_items/gold_chain_thick.glb (0.2 MB): v1 wardrobe items (superseded)
- wardrobe/v1_items/gold_pants_chains.glb (0.1 MB): v1 wardrobe items (superseded)
- wardrobe_hd/riders/caali-g-hd-raw.glb (28.3 MB): -raw source

## Recommended action per asset
| asset | action |
|---|---|
| wardrobe/riders/caali-g-hd.glb | 296k LOD0 is desktop-only. The Quest tier (caali-g.glb, 98k) is OK. Gate it by tier so Quest never fetches it. |
| wardrobe/riders/caali-g.glb | OK. Optional pass: `quest_pipeline.py --max-normal 1024 --ktx2` (once KTX2 is wired in). Drop the KHR_mesh_quantization declaration on the next export. |
| WITHHELD_CHAR/WITHHELD_CHAR-rider.glb, WITHHELD_CHAR-npc.glb | Placeholder. Wait for Ani's new mesh before chasing 100k. Cap the MR map at 1024. Keep it out of public builds. |
| meshy/ikki-meshy-skate.quest.glb | No geometry compression (4.5 MB). Switch to the Draco copy (0.8 MB) after a visual check. |
| meshy/ikki-meshy-rigged-opt.glb | **DEPRECATED**: quantized POSITION. Do not use. Archive it. |
| meshy/*-rigged.glb, ikki-meshy-cyan.glb, caali-meshy-rigged.glb | Source or old rigs, not in the build. Leave them or archive them. |
| crew *-rider.quest.glb (8) | PASS. With the standard A-T, remove the per-crew `_skates` part (about 2k tris, 1 prim each). |
| caali/, code-e/ rider | Identical placeholders with no .quest. Run `quest_pipeline.py` to get a Draco `.quest.glb` if they are spawned on Quest. |
| wardrobe/* items | Quest should use the baked caali-g.glb. Separate items are desktop or editor only, or they need atlasing plus the pipeline (Draco, 1024). |
| wardrobe_hd/* | Desktop only. |
| at-skate-meshy.glb | Merge its 9 prims into 1 and add LOD1/LOD2 (see below). |

## Pipeline demo (outputs only in perf/pipeline-demo/, originals untouched)
| input | mode | before | after (.quest) | after (.quest-ktx2) |
|---|---|---|---|---|
| wardrobe/riders/caali-g-hd.glb | draco, keep-crisp face/head/skate, --ktx2 | 6.59 MB, meshopt+quant, 171 MB tex GPU | 2.67 MB, Draco, no quantization ext, 26.7 MB tex | 2.65 MB, 5.0 MB tex GPU |
| WITHHELD_CHAR/WITHHELD_CHAR-rider.glb | draco, --ktx2 | 1.93 MB, 42.7 MB tex | 1.81 MB, 26.7 MB tex | 1.97 MB, 5.0 MB tex GPU |
| meshy/ikki-meshy-skate.glb | meshopt16 + --simplify 110000 (no-op: already 19.7k) | 5.03 MB | 2.04 MB, POSITION/_WC float | - |
| genesis/genesis-rider.glb | --dry-run | 2.63 MB | (plan only) | - |

The `_WC`, `_WA`, `_BM`, `_SLOT`, skin and morph data all survived (the pipeline checks for lost custom attributes). Logs are `pipeline-demo/*.log`. Re-running onto an existing output, or feeding a `.quest.glb` back in, is refused (`idempotency.log`). These are **not visually checked** in a browser yet: that's for the integrator, who holds .testlock.

## Standard Air Trek (one skate for every rider): planning
Source: `skyrydahs-ref/characters/at-standard-spec.md` v1. This section is planning only. No assets were built or changed.

### (d) Baseline: what skates cost today
| asset | tris | prims (draw calls) | materials | textures | notes |
|---|---|---|---|---|---|
| wardrobe/skates/at-skate-meshy.glb (the standard runtime skate, one skate) | 3,419 | **9** | 1 (AT_bake) | 3 external 1024 PNGs (colour, MR, normal). About 16 MB GPU raw, about 3 MB as KTX2 | No LODs and no Draco (0.31 MB). Not skinned in the file. Used by wardrobe.js (`skates:'at-skate-meshy'`). |
| pair, unmerged, as loaded today | 6,838 | **18 per rider** | 1 | shared | This is the big risk: 8 riders = 144 calls just for skates. |
| shared/at-skate/at-skate-module.glb (Forge module from ikki_skate/build_at_skate.py) | 3,452 | 15 | 0 (COLOR_0 material ids) | none | Shell/Cuff/Chassis/Wheel objects. The cuff is skinned to the shin. Superseded by the Meshy skate under the spec. |
| meshy/airtreck-meshy.glb (source) | 1,815,196 | 1 | 1 | 4096 (64 MB) | Build input only. Never ship it. |
| crew `*_LOD0_skates` in rider.quest.glb (retired) | 1.9-2k per rider | merged into the body by rMerge (0 extra) | toon | shared 512 atlas | Cheap, but these are the toon skates being retired. |
| Ikki / Caali / WITHHELD_CHAR monolithic bodies | skates baked into the body mesh | 0 extra | atlas | in the body atlas | Under the spec these bodies lose their baked skates and gain the standard one. |

ikki_skate/ holds JS (the poser, joint limits) plus Blender build scripts (build_at_skate.py, build_lod.py). It has no runtime geometry of its own.

### (a) One geometry and one material for all riders
- Load `at-skate-meshy.glb` **once**. Pre-merge its 9 prims into one BufferGeometry, either at export or at load with `THREE.BufferGeometryUtils.mergeBufferGeometries` (r128 `examples/js/utils/BufferGeometryUtils.js`, a classic script). Build one `M1 at_skate` material per *crew* that **shares the same textures and shader program**. Only the 4 uniforms change (`uPaint/uFrame/uWheel/uGlowC`, slot masks in COLOR_0 as in the spec). In r128 that means a cloned ShaderMaterial or onBeforeCompile with the same program key, so there's one compile and zero extra texture memory. Crew colour must not mean a separate texture or a separate material *look*.
- Per-instance uniforms are the cheapest and match the existing `setLoadout` API. A palette texture (4x16 px, one row per crew, looked up by a crew-id uniform) is the fallback if we later want to batch several riders into one draw call. Plain vertex colour can't vary per crew without duplicating geometry, so use COLOR_0 only for the slot masks.
- **Attach:** the spec says the shell is 100% rigid to `LeftFoot`/`RightFoot`. So the cheapest option that still looks right is a skinned mesh whose two skates (L and R merged into one geometry) bind to the rider's skeleton with skinIndex = foot bone and weight 1. That's 1 draw call for both feet, and it reuses the rider's bone texture. Rigid `Foot.add(mesh)` children cost 2 calls per rider (one per foot) and they don't merge, so they're only worth it for a quick prototype.

### (b) Socket add-ons inside the skate draw call
For each crew, at load: clone the add-on geometry, bake the socket matrix (mirror X for L), set skinIndex to that foot's bone, then run `mergeBufferGeometries([skateL, skateR, ...addonsL, ...addonsR])`. The result is one SkinnedMesh with the M1 material. Add-on UVs sit in the reserved 512 corner of the skate atlas. Cache one merged geometry per crew, so NPCs of the same crew share it (GPU memory per crew is about 0.5 MB at 9k verts). There are **zero** extra draw calls per add-on. Add-ons have no materials or textures of their own. All merged parts need the same attribute set: give the add-ons COLOR_0, UV, NORMAL, skinIndex and skinWeight.

### (c) Budgets
| item | LOD0 | LOD1 | LOD2 |
|---|---|---|---|
| standard skate, **per foot** | ≤ 9,000 tris (today 3,419: OK) | ≤ 3,000 | ≤ 750 |
| pair | ≤ 18,000 | ≤ 6,000 | ≤ 1,500 |
| add-ons per foot (all sockets combined) | ≤ 2,000 (largest is Code:E at 1,350: OK) | ≤ 700 (about 35%) | 0 (dropped) |
| add-ons per rider (both feet) | ≤ 4,000 | ≤ 1,400 | 0 |
| add-on, single part | ≤ 900 per foot (largest in the catalog is kg_fang_wheel_housing at 900) | ≤ 300 | 0 |

NPC total stays at 30k or less at LOD0, with the skates included. Example: a 15k crew body minus its 2k retired toon skates, plus a 6.8k pair today, plus 2.7k add-ons, comes to about 22.5k. That's OK. If the skate grows to the full 18k pair, an NPC body has to stay at or under 8k LOD0, so we should keep the Quest skate at about 7-9k per pair and save 18k for desktop or the player.

**Draw calls per rider:**
| rider | body | outline | glow | skates (both feet + add-ons) | skate outline | total |
|---|---|---|---|---|---|---|
| player (LOD0) | 1 | 1 | 1 | 1 | 1 (optional) | **4-5** |
| NPC LOD0/LOD1 (≤32 m) | 1 | 1 | 1 | 1 | 0 | **4** |
| NPC LOD2 (>32 m) | 1 | 0 | 0 | 1 (or folded into the body) | 0 | **2** |

Shadows: every shadow-casting mesh adds 1 call per shadow pass. Keep rider shadows off on Quest, or use a blob decal (+1, shared).

**Math against the 150 Quest cap (WebXR multiview assumed, OCULUS_multiview, so stereo doesn't double the calls):**
- Player 5 + 8 NPCs x 4 = **37** calls, if all NPCs are close. A realistic mix (3 close, 5 far) is 5 + 3x4 + 5x2 = **27**.
- That leaves **113-123 for the world, HUD, FX, sky and minimap**. Today the world peaks at 267 at the causeway (day) and 243 at 98 Bridge, already 80-120 over the whole-frame cap *before* riders. The world has to come down to about 110 at those spots.
- Unmerged skates as loaded today (18 per rider) would cost 9 x 18 = 162 calls, over budget from skates alone. **Merging is mandatory.**
- Without per-crew caching, crews sharing a material is fine: draw calls count meshes, not unique materials. But material *switches* cost CPU, so sort riders by crew.

---
## Rydah Optimizer notes
- KTX2 tooling installed locally: gltf-transform 4.5.1 at /workspace/tools/gt, plus KTX-Software 4.4.2 unpacked into v3build/tools/ktx. 4.3.2 failed: gltf-transform 4.5 needs `ktx create --assign-tf`. The game is not wired to KTX2. See tools/README.md.

## Pipeline run 2 (04:50 CDT): new files next to originals, nothing swapped
Scope (lead-approved):
- `wardrobe/riders/caali-g.glb`.
- The 9 separate `wardrobe/*` items (accessory, body, gloves, hair, head, jacket, neck, pants, top).
- The 7 crew `*-rider.quest.glb` files. Only 7 exist: caali/ and code-e/ have none.

WITHHELD_CHAR, Ikki and every other file were untouched. `wardrobe/skates/at-skate-meshy.glb` was left out because it's covered by the A-T spec.

Settings: Draco (edgebreaker, 16-bit pos/generic inside Draco, decodes to float), base colour max 2048, normal and ORM 1024, `--keep-crisp 'face|head|skate'` (keeps those at 2048), and KTX2 variants (UASTC normal, ETC1S colour/ORM).

Checks run by `tools/compare_outputs.py` (data: `pipeline-out/compare.json`):
- **Material params:** diffed baseColorFactor, metallic/roughness, emissiveFactor, KHR_materials_emissive_strength, alphaMode/cutoff, doubleSided, normal scale, occlusion strength, extras, and texture slots. **All 27 outputs: SAME.**
- **COLOR_0 vertex-colour sets:** **SAME.**
- **POSITION/_WC:** float32 in every output. No output declares KHR_mesh_quantization.
- **caali-g `_WC`:** decoded and checked. The `_WC` bbox is identical to the original, and mean |_WC−POSITION| is 1.09239 vs 1.09223, so it's in the same space. Draco adds 20 seam vertices (92,976 → 92,996).
- **Tri counts:** unchanged, except anubis (−20 LOD0) and static-angels (−14 LOD1/2). Draco edgebreaker drops degenerate zero-area triangles there, so there's no visual change.
- **Texture changes:** resize only (lanczos), with the same image format (webp stays webp), or KTX2 in the -ktx2 variant. No colour or material edits.

Crew riders: the plain re-Draco `.quest2.glb` gave **no win** (+0.01 MB, textures already 512), so I deleted those and **kept only `.quest2-ktx2.glb`**. That's about 0.1 MB smaller and cuts texture GPU memory from 1.7 to 0.3 MB per rider.

Notes:
- `gold_chain_thick.quest-ktx2.glb` is a bigger *file* (0.94 MB vs 0.26) but uses less GPU memory (16 → 3 MB). That's a file-size vs GPU-memory trade.
- caali-g: 3.63 → 1.50 MB, textures 42.7 → 26.7 MB (normal 2048 → 1024, base atlas kept 2048 for the face/skates), or **5.0 MB** with KTX2.
- Wardrobe items total: about 360 MB → 200 MB texture GPU memory, or about 37 MB with KTX2.

| new file | before MB | after MB | tex GPU MB before → after | tris (LOD0/1/2) after | mats | textures after | compression | material params | COLOR_0 | POSITION/_WC float | KHR_mesh_quant |
|---|---|---|---|---|---|---|---|---|---|---|---|
| anubis/anubis-rider.quest2-ktx2.glb | 0.75 | 0.66 | 1.7 → 0.3 | 13468/7933/2888 (was 13488/7933/2888) | 2→2 | 512:zstd 512:etc1s(basislz) | draco,ktx2 | SAME | SAME | yes | no |
| behemoth/behemoth-rider.quest2-ktx2.glb | 0.93 | 0.82 | 1.7 → 0.3 | 13470/7983/2500 | 2→2 | 512:zstd 512:etc1s(basislz) | draco,ktx2 | SAME | SAME | yes | no |
| genesis/genesis-rider.quest2-ktx2.glb | 0.97 | 0.87 | 1.7 → 0.3 | 15158/7972/2238 | 2→2 | 512:zstd 512:etc1s(basislz) | draco,ktx2 | SAME | SAME | yes | no |
| kogarasumaru/kogarasumaru-rider.quest2-ktx2.glb | 0.98 | 0.88 | 1.7 → 0.3 | 15296/7976/2345 | 2→2 | 512:zstd 512:etc1s(basislz) | draco,ktx2 | SAME | SAME | yes | no |
| sleeping-forest/sleeping-forest-rider.quest2-ktx2.glb | 0.94 | 0.83 | 1.7 → 0.3 | 14174/7976/2498 | 2→2 | 512:zstd 512:etc1s(basislz) | draco,ktx2 | SAME | SAME | yes | no |
| static-angels/static-angels-rider.quest2-ktx2.glb | 0.97 | 0.86 | 1.7 → 0.3 | 15406/7907/2697 (was 15406/7921/2711) | 2→2 | 512:zstd 512:etc1s(basislz) | draco,ktx2 | SAME | SAME | yes | no |
| tool-toul-to/tool-toul-to-rider.quest2-ktx2.glb | 0.93 | 0.83 | 1.7 → 0.3 | 14918/7904/2321 | 2→2 | 512:zstd 512:etc1s(basislz) | draco,ktx2 | SAME | SAME | yes | no |
| wardrobe/accessory/gold_pants_chains.quest-ktx2.glb | 0.12 | 0.03 | 0.0 → 0.0 | 384/192/192 | 1→1 | 16:etc1s(basislz) | draco,ktx2 | SAME | SAME | yes | no |
| wardrobe/accessory/gold_pants_chains.quest.glb | 0.12 | 0.03 | 0.0 → 0.0 | 384/192/192 | 1→1 | 16:webp | webp,draco | SAME | SAME | yes | no |
| wardrobe/body/base.quest-ktx2.glb | 1.13 | 0.52 | 8.0 → 1.5 | 7998/2485/886 | 1→1 | 512:zstd 1024:etc1s(basislz) 512:etc1s(basislz) | draco,ktx2 | SAME | SAME | yes | no |
| wardrobe/body/base.quest.glb | 1.13 | 0.28 | 8.0 → 8.0 | 7998/2485/886 | 1→1 | 512:webp 1024:webp 512:webp | webp,draco | SAME | SAME | yes | no |
| wardrobe/gloves/caali_fingerless.quest-ktx2.glb | 0.74 | 0.42 | 16.0 → 3.0 | 8000/2500/800 | 1→1 | 1024:zstd 1024:etc1s(basislz) 1024:etc1s(basislz) | draco,ktx2 | SAME | SAME | yes | no |
| wardrobe/gloves/caali_fingerless.quest.glb | 0.74 | 0.2 | 16.0 → 16.0 | 8000/2500/800 | 1→1 | 1024:webp 1024:webp 1024:webp | webp,draco | SAME | SAME | yes | no |
| wardrobe/hair/caali_curly_short.quest-ktx2.glb | 1.29 | 0.55 | 64.0 → 6.0 | 14000/4000/1200 | 1→1 | 1024:zstd 2048:etc1s(basislz) 1024:etc1s(basislz) | draco,ktx2 | SAME | SAME | yes | no |
| wardrobe/hair/caali_curly_short.quest.glb | 1.29 | 0.28 | 64.0 → 32.0 | 14000/4000/1200 | 1→1 | 1024:webp 2048:webp 1024:webp | webp,draco | SAME | SAME | yes | no |
| wardrobe/head/caali_head.quest-ktx2.glb | 1.03 | 0.4 | 64.0 → 6.0 | 15999/5999/1998 | 1→1 | 1024:zstd 2048:etc1s(basislz) 1024:etc1s(basislz) | draco,ktx2 | SAME | SAME | yes | no |
| wardrobe/head/caali_head.quest.glb | 1.03 | 0.22 | 64.0 → 32.0 | 15999/5999/1998 | 1→1 | 1024:webp 2048:webp 1024:webp | webp,draco | SAME | SAME | yes | no |
| wardrobe/jacket/caali_bomber.quest-ktx2.glb | 2.0 | 1.23 | 64.0 → 6.0 | 16000/6000/1999 | 1→1 | 1024:zstd 2048:etc1s(basislz) 1024:etc1s(basislz) | draco,ktx2 | SAME | SAME | yes | no |
| wardrobe/jacket/caali_bomber.quest.glb | 2.0 | 0.9 | 64.0 → 32.0 | 16000/6000/1999 | 1→1 | 1024:webp 2048:webp 1024:webp | webp,draco | SAME | SAME | yes | no |
| wardrobe/neck/gold_chain_thick.quest-ktx2.glb | 0.62 | 0.94 | 16.0 → 3.0 | 4000/1000/560 | 1→1 | 1024:zstd 1024:etc1s(basislz) 1024:etc1s(basislz) | draco,ktx2 | SAME | SAME | yes | no |
| wardrobe/neck/gold_chain_thick.quest.glb | 0.62 | 0.26 | 16.0 → 16.0 | 4000/1000/560 | 1→1 | 1024:webp 1024:webp 1024:webp | webp,draco | SAME | SAME | yes | no |
| wardrobe/pants/caali_cargo.quest-ktx2.glb | 1.57 | 0.87 | 64.0 → 6.0 | 16000/6000/1999 | 1→1 | 1024:zstd 2048:etc1s(basislz) 1024:etc1s(basislz) | draco,ktx2 | SAME | SAME | yes | no |
| wardrobe/pants/caali_cargo.quest.glb | 1.57 | 0.53 | 64.0 → 32.0 | 16000/6000/1999 | 1→1 | 1024:webp 2048:webp 1024:webp | webp,draco | SAME | SAME | yes | no |
| wardrobe/riders/caali-g.quest-ktx2.glb | 3.63 | 1.65 | 42.7 → 5.0 | 98341/34656/11232 | 1→1 | 1024:zstd 2048:etc1s(basislz) | draco,ktx2 | SAME | SAME | yes | no |
| wardrobe/riders/caali-g.quest.glb | 3.63 | 1.5 | 42.7 → 26.7 | 98341/34656/11232 | 1→1 | 1024:webp 2048:webp | webp,draco | SAME | SAME | yes | no |
| wardrobe/top/caali_gr8yzone_tee.quest-ktx2.glb | 1.02 | 0.31 | 64.0 → 6.0 | 12000/4000/1200 | 1→1 | 1024:zstd 2048:etc1s(basislz) 1024:etc1s(basislz) | draco,ktx2 | SAME | SAME | yes | no |
| wardrobe/top/caali_gr8yzone_tee.quest.glb | 1.02 | 0.25 | 64.0 → 32.0 | 12000/4000/1200 | 1→1 | 1024:webp 2048:webp 1024:webp | webp,draco | SAME | SAME | yes | no |

Swap list: `perf/pipeline-out/SWAP_PENDING.md`. Nothing goes in until the integrator does a before/after colour-match shoot, and the KTX2 variants also need the KTX2 loader (tools/README.md).

## PBR rider budget on Quest (new default, replacing toon)
Oliver's direction is CoD / NFS Heat / GTA-level realism. That means PBR skin, cloth and A-T materials, baked normals, and lighting shared with the world.

**The spec:**
- Textures: KTX2. Base colour 2048, face crisp. Normal and ORM 1024.
- Materials: at most 3 per rider (skin, cloth/gear, A-T skate). The A-T material and textures are shared by every rider.
- Shader: `MeshStandardMaterial`. MeshPhysical is too costly on Quest. Skin gets a cheap wrap-light/SSS fake via `onBeforeCompile` (about +4 ALU).
- Lighting: one env map (PMREM) shared with the world. At most 1 shadow-casting light, or blob shadows.

### Draws: locked budget of 40 for characters + FX (multiview, so per eye = per frame)
| item | draws |
|---|---|
| FX (from airgear-render-style.md) | 6 |
| Player LOD0: skin + cloth/gear + merged A-T skate (with add-ons) | 3 (the 3rd material *is* the skate) |
| NPC LOD0, 3 materials | 3 each |
| NPC LOD1: single-material atlas (skin+cloth baked into one 1024 set), skate merged in | **1** |
| NPC LOD2: single atlas, add-ons dropped | 1 |
| Outlines, if kept (player + LOD0 NPCs only) | +1 each |
| Player shadow: 1 merged shadow-proxy draw in the shadow pass | +1 |
| NPC blob shadows: 1 InstancedMesh | +1 |

**Math:**
- Naive (everyone at 3 materials): FX 6 + player 3 + 8×3 = **33**, +outlines 9 = 42, +shadows 2 = **44. Over.**
- Plan: FX 6 + player 3 + **at most 3 NPCs at LOD0** (3×3 = 9) + 5 NPCs at LOD1/2 (5×1 = 5) + shadows 2 = **25**. With outlines kept on the player and LOD0 NPCs (+4): **29**. That leaves 11 spare for crowd/extra riders or a rival Road at the high FX tier.
- Hard worst case, 8 NPCs all inside 10 m: the LOD0 cap forces the nearest 3 to LOD0 and the rest to LOD1 by distance rank, so it stays at 25–29.

**What has to give to fit 40:**
1. Distant LODs have to use a single material and a single atlas. Plain 3-material LODs at every distance would cost 27 for 9 riders before FX.
2. A rank cap of 3 NPCs at LOD0. The rider-count cap on screen stays at 8 (beyond that: an impostor or cull at more than 50 m).
3. Outlines are optional. If the realistic look drops the inverted hull, save 4 draws and the doubled LOD0 vertex skinning.
4. No per-NPC shadow casting.

### Per-pixel GPU (Quest 3, estimates, measure with ovrgpuprofiler)
A rider at about 3 m covers about 5% of each eye (about 230k px per eye at 2064×2208, about 0.46 M px per frame). With 3 close riders that's about 1.4 M shaded px.

| shading | approx. ALU/px | 3 near riders | all 9 riders (6 small) |
|---|---|---|---|
| toon (ramp + rim) + hull | ~25 + hull | 0.2–0.3 ms | 0.3–0.5 ms |
| MeshStandard + normal + ORM + env IBL + 1 dir light | ~90–120 | 0.5–0.8 ms | 0.7–1.1 ms |
| + skin wrap/SSS fake | +5% | +0.03 ms | +0.05 ms |
| + 1 shadow map sample (player-only caster, receive on world) | +0.1–0.2 ms frame-wide | | |

Characters move from about 1.0–1.5 ms (toon, previous plan) to about **1.2–1.8 ms with PBR**. That still fits the 13.9 ms frame next to world 5–6 ms and FX ≤ 1 ms, but foveation (level 2–3) and `framebufferScaleFactor` 0.9 become the standard knobs, not emergency ones.

### Texture memory (with mips)
| set | RGBA8 / PNG decoded | KTX2 (ETC1S colour/ORM, UASTC normal) |
|---|---|---|
| one material: base 2048 + normal 1024 + ORM 1024 | 21.3 + 5.3 + 5.3 = **32 MB** | 4.0 + 1.4 + 1.0 = **6.4 MB** |
| player: skin + cloth (2 unique materials) | 64 MB | 12.8 MB |
| NPC LOD0: 2 unique materials, base at 1024 for NPCs | 2 × 16 = 32 MB | 2 × 3.4 = 6.8 MB |
| NPC LOD1/2 atlas (1024 set) | 16 MB | 3.4 MB |
| shared A-T (1024 set, all riders) | 16 MB | 3.4 MB |
| **player + 8 NPCs (all crews unique)** | 64 + 8×(32+16) + 16 = **464 MB** | 12.8 + 8×(6.8+3.4) + 3.4 = **98 MB** |

**KTX2 is mandatory for PBR on Quest.** About 460 MB of raw RGBA is not viable next to the world. Crews that share a body texture set (NPCs of the same crew) cut this further.

### LOD switch distances (PBR)
| level | distance | content |
|---|---|---|
| LOD0 | 0–10 m (only the 3 nearest NPCs) | 3 materials, NPC ≤ 30k tris (player 100–120k), normal map |
| LOD1 | 10–25 m | 1 atlas material, about 40% tris, normal map kept at 512 |
| LOD2 | 25–50 m | 1 atlas, about 12% tris, no normal map, no add-ons |
| beyond | >50 m | impostor billboard (1 instanced draw for all) or cull |

These are tighter than today's 0/14/32 m because PBR LOD0 is the expensive tier. Re-tune them on the headset with the quest-test-path checklist.

## Character draw budget, locked split (04:57 CDT 2026-10-29, Rydah Optimizer + Rydah Rigger)
- API: `rider.userData.setDetail('full'|'lite')` (jackets.js, ikki_skate.js), visibility-only toggle.
- Crew NPC: full = body + outline + merged skate + patch = **4** (separate glow mesh dropped; skate emissive covers wheels). lite = body + skate = **2** (no outline/patch/ground shadow).
- Player (Ikki / Caali G / WITHHELD_CHAR): full = body(+skates) + patch + ground shadow = 3 (4 with ?ikkiOutline=1); lite = 1.
- Sorter: 3 nearest NPCs full, rest lite, re-sorted ~4x/s.
- Total: player 3-4 + 3x4 + 5x2 + FX 6 = **31-32** of 40; spare ~8 for 3-star police.
- Skate mask is COLOR_0 ('color' in r128; R paint, G frame, B wheel). COLOR_1 unused legacy. _WC loads as '_wc'.
