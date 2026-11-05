# Forge plan: Caali G redesign + new rider Anika (GR8YZONE), Rydah Forge, 2026-10-30
Source of truth: `skyrydahs-ref/characters/caali-anika-2026-10-30/` (README.md + `caali-anika-ref1-night-fx.jpg`, `caali-anika-ref2-day-clean.jpg`, `caali-anika-ref3-pole-grind.jpg`). Old sheet `skyrydahs-ref/caali-g-turnaround.jpg` is now SECONDARY (back view / phoenix only). Planning only: Forge spent 0 credits and edited no build files.

**UPDATE 01:30 CDT:** Oliver approved the spend ("Re render caali g's meshy based on these and create a new meshy for Anika"). The parent is running Image to 3D from `/home/box/Downloads/gr8yzone/anika_crop.png` and `caali_crop.png`. The outputs go to `/home/box/Downloads/gr8yzone/anika-meshy.glb` and `caali-meshy.glb`. §(f) below is the post-processing plan for those GLBs, and it overrides the Meshy-generation steps in (b) and (c). Caali's full-body regen replaces the separate cap and jacket gens.
Spelling: **GR8YZONE** (8, no hyphen). Note: the AI images render the tee as "GRB ZONE"/"GR8 ZONE"; we author the decal ourselves as GR8YZONE, never trust Meshy text.

## Conflicts found
- **K1 Crew: RESOLVED (Oliver via Ani, 2026-10-30):** Gr8yzone is Caali's shirt brand, NOT a crew. Caali G stays Code : E (founder, black + gold). Anika is Code : E (codee) with Caali G, per Oliver 2026-10-30.
- **K2 Purple:** bible fix M2 says "drop purple, gold only" for Caali; new ref gives him a **purple backwards cap**. New ref wins for the cap (garment); M2 still applies to skate/palette (A-T stays black/gold).
- **K3 Wheels:** old turnaround = cyan wheel glow; new = **gold** (#FFD700). Matches bible glow; drop all cyan from Caali's wheels. Anika's night trails pink/cyan/violet = FX only, not her glow slot (Q4).
- **K4 Jacket cut:** bible/kit = *cropped* filigree jacket; new ref = **hip-length** black leather moto/bomber with baroque gold embroidery + gold chain trim. Phoenix back not visible in new refs (Q2).
- **K5 Hair/face:** bible = short curls + taper, clean-shaven, stud earring; new ref = hair hidden under cap, **goatee/short beard + moustache**, no visible earring, adult face (older than the turnaround).
- **K6 Slots:** `slots.json` has no `hat`, `headphones`, `skirt` or `legwear` slot. Proposal (Rigger/Optimizer to approve, not edited): add `hat` (512), `legwear` (1024); skirt uses `pants`; headphones ride in `hat` as one mesh with the cap.
- **K7 Anika's tee patch:** README says GR8YZONE patch; image shows a GR8YZONE + bolt print on the top's chest (under the neckerchief) and a small gold emblem on the left sleeve. Build both as decals.
- **K8 Text to 3D retires Oct 31** (tomorrow): any Text-to-3D step must run today or be redone as Image-to-3D (cost unknown, assumed 30).

## (a) Caali G: new ref vs bible v2 + kit
| Piece | Bible v2 / kit | New ref (ref2 primary) | Hex | Action |
|---|---|---|---|---|
| Hair `caali_curly_short` | short black curls, taper | hidden under cap; short black hair at nape/temples only | #0E0B0A | **Keep** mesh, hidden by cap mask; trim a cap-compatible variant in Blender (0 cr) |
| Cap (new) | none | purple baseball cap worn backwards, black brim edge | crown #5A3D8A, brim #1A1420 | **Regenerate** (new piece, slot `hat`) |
| Headphones (new) | none | white over-ear, grey band/cushions | #EDEDED, #9A9A9A | **Regenerate** with cap (one mesh) |
| Head `caali_head` | clean-shaven, stud earring, young | goatee + moustache, adult, warm brown skin, calm confident | skin #6B4226 (keep), beard #15100D | **Retexture + refit**: keep topology/neck seam, add beard as card/shell + albedo; if Meshy retexture loses likeness, regenerate head from ref2 crop |
| Tee `caali_gr8yzone_tee` | black, "GRB ZONE" gold + bolt | black, **GR8YZONE** gold letters, gold bolt with blue outline | #0B0B0D, #FFD700, bolt edge #2E6BFF | **Retexture** (decal swap in Blender, 0 cr; fix spelling) |
| Jacket `caali_bomber` | cropped, filigree, phoenix back | hip-length black leather, gold baroque embroidery on chest/sleeves/shoulders, gold chain trim along front & hem, stand collar, gold zip | #0B0B0D, #FFD700 / #C9A227 | **Regenerate** (length/cut change; retexture can't lengthen). Phoenix back kept pending Q2 |
| Pants `caali_cargo` | black, gold side stripes, buckle straps | black baggy cargo, single gold side stripe, cargo pocket w/ buckle, tapered into skate | #0B0B0D, #FFD700 | **Keep + retexture** (Blender, 0 cr) |
| Accessory `gold_pants_chains` | pants chains | one hanging chain hip→pocket | #FFD700 | **Keep** (refit drape) |
| Neck `gold_chain_thick` | thick chain | thinner gold chain necklace | #FFD700 | **Refit** (scale chain links down ~40%) |
| Gloves `caali_fingerless` | black + gold knuckle plate | black fingerless | #0B0B0D | **Keep** |
| Skates | A-T black/gold | standard A-T, gold accents, gold wheels | paint #0B0B0D, frame #C9A227, wheel #1C1C20 hub/#FFD700 tyre glow, glow #FFD700 | **Keep** `at-skate-meshy.glb` |

## (b) Anika plan (new rider, GR8YZONE)
**Look (ref2):** young woman, fair/light-tan skin #E8B894, freckles, blonde #D9B56A long braided pigtails (to chest), friendly smile; pink sailor crop top #E0457B with pale pink/white sailor collar stripes #F6C9D6, **red neckerchief #C8102E**, GR8YZONE + bolt chest print, small gold sleeve emblem, cuffs with gold band; pink pleated mini skirt #E85A8C with **gold hem trim #FFD700** and a **gold chain** across the hip; white thigh-highs #F4F4F2 with **pink satin bows #F28AB0**; standard A-T, gold wheels, glow #FFD700.

**Step 1 – input image:** `caali-anika-ref2-day-clean.jpg`. Meshy wants one subject: crop Anika (left ~0–50% width, full height) to `caali-anika-ref2-day-clean.anika-crop.png`, background removed, upscaled to ≥1024 px tall. (Crop is local prep, 0 cr.)
**Step 2 – Meshy Image to 3D** (one run):
- Settings: latest Meshy model, art style **Realistic**, **PBR on**, symmetry **off** (asymmetric pose/neckerchief), polycount max (no UI control; expect 150k–1.6M), pose A-pose if offered, texture prompt on.
- Prompt: `realistic young woman inline skater, long blonde braided pigtails, freckles, pink cropped sailor top with pale pink striped sailor collar and red neckerchief, GR8YZONE lightning bolt print on chest, pink pleated mini skirt with gold trim and a gold chain at the hip, white thigh-high socks with pink satin bows, black armored inline skates with gold accents and gold wheels, PBR, photoreal fabric, A-pose, full body`
- Negative: shared N + `cartoon, toon, anime, cel shading, extra fingers, fused fingers, text artifacts, background, pole, second person`.
- Fallback if the crop gen fails: rerun once with an A-pose re-draw of the crop (retry row).
**Step 3 – Blender (0 cr, `forge_kit/gk/bake.py` workflow):** import raw → align to `rider-skeleton.blend` (height ref 1.916, slim preset) → split by material/selection into modular meshes, each remeshed/decimated and baked onto the shared base:
| Piece (slot) | Source | LOD0 player / NPC | Notes |
|---|---|---|---|
| `anika_braids` (hair) | Meshy hair | 10k / 3k | braid chain gets 3–4 spring bones per pigtail (Rigger, optional) |
| `anika_head` (head) | Meshy head, retopo to shared 48-vert neck seam | 16k / 5k | eyes = separate spheres |
| `anika_sailor_top` (top) + neckerchief | Meshy torso | 7k / 2.5k | neckerchief is a separate sub-mesh in same file for cloth jiggle |
| `anika_pleated_skirt` (pants) + `anika_skirt_chain` (accessory) | Meshy skirt | 6k+1k / 2k+0.5k | pleats in normal map; chain as rigid strip on Hips |
| `anika_thighhighs_bows` (legwear, new slot K6) | shrink-wrapped to base legs, bows from Meshy | 3k / 1k | base legs show only between skirt and sock |
| gloves | none (bare hands = shared anatomical hands) | – | |
- **Body:** use `wardrobe/body/base.glb` with the F/slim preset; Meshy body is reference only (drop it). Body masks from slot bits.
- **Strip Meshy skates:** delete everything below the sock cuff top / ankle; cap the leg; fit the standard `wardrobe/skates/at-skate-meshy.glb` (rigid to LeftFoot/RightFoot via `L_AT_Root`/`R_AT_Root`, pivot A=(0,0.12,−0.06)), loadout paint #0B0B0D, frame #C9A227, glow #FFD700.
- **Textures/materials:** M0 `anika_atlas` 2048 colour + 1024 normal/ORM; M1 shared at_skate; M2 fx optional. Decals (GR8YZONE print, sleeve emblem) authored by us, baked in.
- **Retarget/handoff to Rydah Rigger:** deliver unskinned-but-aligned pieces in `rider-skeleton.blend` bind pose + `riders/anika.outfit.json` draft; Rigger skins to the 91-joint rig (≤4 weights, twist 50%, bones.json joint order), Optimizer does LOD0/1/2 + Draco (float positions, de-interleaved) + KTX2.
- **Budget (player LOD0):** head+hair ~26k, hands+A-T ~28k, body+clothes ~50k → ~104k. NPC LOD0 ≤30k.

## (c) Caali refresh steps (shared body + skeleton)
1. Keep `body/base.glb` (M preset) and `rider-skeleton.glb` unchanged (Caali's bind is the skeleton source).
2. Crop Caali from ref2 (right half) → `…ref2-day-clean.caali-crop.png`.
3. Cap+headphones: Meshy Text to 3D **today** (before Oct 31 retirement) — prompt `realistic purple baseball cap worn backwards with white over-ear headphones over it, no head, PBR` — or Image to 3D from a head crop. Fit to `caali_head`, slot `hat`, ~4k tris; hair masked under cap.
4. Head: Blender beard/goatee (hair cards + albedo) on `caali_head` (0 cr); if likeness fails, Meshy Image to 3D from the face crop and transfer onto the existing topology.
5. Jacket: Meshy Image to 3D from Caali crop with prompt `realistic hip-length black leather jacket, ornate gold baroque embroidery on chest shoulders and sleeves, gold chain trim along front and hem, stand collar, gold zipper, PBR, no body` → strip body, retopo ~14k, bake; phoenix back decal per Q2.
6. Tee: replace decal with authored GR8YZONE + gold/blue bolt (Blender, 0 cr).
7. Pants: retexture single gold stripe; refit chain; thin the neck chain (Blender, 0 cr).
8. A-T: shared skate, gold loadout; drop all cyan (M2/K3).
9. Rigger re-skins changed pieces; Optimizer rebuilds `caali-g.glb` / `.quest*.glb`; update `caali-g.outfit.json` (+ `hat`) — owned by Rigger/Optimizer, not edited here.

## (d) Credits (balance 1,440; Text to 3D = 20 mesh + 10 PBR; Image to 3D ASSUMED 30, unverified ⚠)
| # | Step | Op | Cost | Σ minimal | Σ recommended |
|---|---|---|---|---|---|
| 1 | Anika full body | Image to 3D (ref2 crop) | 30⚠ | 30 | 30 |
| 2 | Anika retry / face close-up | Image to 3D | 30⚠ | – | 60 |
| 3 | Caali cap + headphones | Text to 3D + PBR (today) | 30 | 60 | 90 |
| 4 | Caali jacket (new cut) | Image to 3D | 30⚠ | – | 120 |
| 5 | Caali jacket fallback | Retexture existing `caali_bomber` | 10 | 70 | – |
| 6 | Caali head w/ beard (if Blender fails) | Image to 3D | 30⚠ | – | 150 |
| 7 | Retry reserve | – | 60 | – | 210 |
- **Minimal: 70 credits** (Anika ×1, cap/headphones, jacket retexture-only keeping cropped cut ⇒ jacket not faithful to ref). Balance after: 1,370.
- **Recommended: 210 credits** incl. 60 reserve (150 planned). Balance after: 1,230 (≥1,290 if reserve unused). If Image to 3D actually costs more than 30, every ⚠ row scales.
- Tee, pants, chains, beard, skates, LODs, baking: Blender, 0 credits.

## (e) Questions only Oliver can answer
1. RESOLVED: Gr8yzone is a shirt brand, not a crew. RESOLVED: Anika is Code : E with Caali G (Oliver, 2026-10-30). Back patch: Code : E crew patch (code-e-patch.png + normal/height) baked into her atlas on the back of the sailor top, per Oliver 01:39 CDT; the Gr8yzone chest patch stays.
2. Does Caali's new hip-length jacket keep the big gold phoenix-with-lightning back embroidery from the old turnaround?
3. Purple cap: OK as an exception to the "gold only, no purple" Caali palette (M2)? Exact purple?
4. Anika's wheel glow: gold (#FFD700, as in ref2) with pink/cyan/violet as trail FX only, or a pink glow slot?
5. Anika's role (player-selectable or NPC), age range, and tagline; any IP/likeness concern with the reference faces is your call.
6. Approve new wardrobe slots `hat` and `legwear` (needs Rigger/Optimizer + slots.json change).
7. Approve running the Text to 3D cap step today before the Oct 31 retirement, and the minimal vs recommended budget.

## (f) Post-processing anika-meshy.glb + caali-meshy.glb (0 credits, Blender, `forge_kit/gk/bake.py`)
1. **Ingest:** copy both GLBs to `skyrydahs-characters/meshy/gr8yzone/` as `*-raw.glb` (read-only originals). Log the face count, materials and texture sizes (expect 150k–1.6M faces).
2. **Align:** open `shared/skeleton/rider-skeleton.blend` (link the armature, don't edit it). Scale and translate each raw mesh to the bind A-pose: Caali uses the M preset at refH 1.916, Anika the slim preset. If the Meshy pose isn't A-pose, pose-match it with a temp armature before splitting.
3. **Split into modular pieces** (select by material/UV island and by hand, then separate):
   - Caali: `caali_cap_headphones` (hat), `caali_head` v2 (beard; snap to the 48-vert neck seam), hair only if visible, `caali_gr8yzone_tee` v2, `caali_leather_jacket` (hip-length, baroque gold, chain trim), `caali_cargo` v2 (gold stripe) + `gold_pants_chains`, neck chain, `caali_fingerless`.
   - Anika: `anika_braids`, `anika_head`, `anika_sailor_top` + neckerchief, `anika_pleated_skirt` + `anika_skirt_chain`, `anika_thighhighs_bows`.
   - Drop the Meshy body and hands. Fit the clothes over `wardrobe/body/base.glb` with its shared anatomical hands, and generate the body masks per slot bit.
4. **Strip the Meshy skates:** cut below the ankle (pants hem for Caali, sock cuff for Anika), close the hole, and delete the skate geometry. Fit the standard `wardrobe/skates/at-skate-meshy.glb` rigid to `L_AT_Root`/`R_AT_Root` (pivot A=(0,0.12,−0.06), mirror X for R). Loadout: paint #0B0B0D, frame #C9A227 gold accents, wheel #1C1C20, glow **#FFD700** gold wheels. Both use Code : E add-ons `ce_*`.
5. **Retopo/decimate per piece** to the LOD0 player targets: head 15–18k, hair 8–12k, jacket 14k, top 6–7k, pants/skirt 6–10k, accessories ≤4k, cap+phones ~4k. Total is ~100–120k including hands and A-T.
6. **Bake** high→low with bake.py: 2048 colour + 1024 normal/ORM into one `M0 <rider>_atlas`, plus M1 at_skate and optional M2 fx, so ≤3 materials. Re-author the GR8YZONE decals ourselves because Meshy text is garbled, then bake them in. Aim for realistic PBR: leather roughness 0.45, gold metallic 1.0 at roughness 0.3, cotton 0.85.
7. **Retarget/skin (Rydah Rigger):** pieces get skinned to the 91-joint shared skeleton in bones.json order, ≤4 weights, 50% twist roll share. Braids get optional spring bones. Any Meshy auto-rig is discarded.
8. **LODs (Optimizer):** player LOD0 100–120k, LOD1 ~40k, LOD2 ~15k; NPC LOD0 ≤30k. Draco with float positions, de-interleaved, + KTX2 → `wardrobe/riders/caali-g*.glb`, `anika*.glb` + outfit.json.
9. **QA:** compare renders against ref2, checking the hex list in (a)/(b). Check hands have 5 fingers each and that the skates are identical across both riders.

Credits now: about 60 (2 × Image to 3D, assumed 30 each ⚠), spent by the parent, which leaves ~1,380. Table (d) is superseded. Recommended reserve: 60 for one retry each.

## (g) Executed 2026-10-30 02:34 CDT (Rydah Forge)
Built from the Meshy 7.1 outputs. Anika: `skyrydahs-characters/anika/anika-rider.glb` + `anika-npc.glb` (+ .quest, .quest-ktx2). Caali G v2 is STAGED as `wardrobe/riders/caali-g-v2.glb`, `-v2-hd.glb` and `.quest` / `.quest-ktx2`; live caali-g.glb is untouched. Sources and scripts: `anika/src/` (build_gr8.py, *_lods.blend, *_pieces.blend) and `wardrobe_build/forge-caali-v2/`. Meshes are unskinned and in A-pose, so the retarget and spring bones go to Rydah Rigger.
