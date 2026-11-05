# Meshy Batch Plan v2 (Rydah Forge, 2026-10-29) — WRITTEN ONLY, NOTHING GENERATED
Cap: ~960 of ~1,600 credits (60%). Plan total **780 + 120 retry reserve = 900**.

## Credit assumptions (no per-op costs are recorded in production-plan.md or meshy-prompts-crews.md; verify on Meshy's pricing page before the first run)
Text-to-3D preview (mesh) **20** · texture/refine **10** · Image-to-3D (textured) **30** · Retexture **10** · Remesh **5** · Auto-rig **5**. If real costs are higher, cut from the bottom of the list (B4 kits, then B3 accessories) — never B2 heads.
Settings (all gens): latest Meshy model, art style Realistic, PBR on, **target polycount max (~300k)**, symmetry auto, A-pose where a body is present. Remesh/decimate/LOD/UVs done in **Blender (0 credits)**, not Meshy remesh. Shared negative prompt N (from meshy-prompts-crews.md) + add `full body, skates, shoes, base plate` for head/garment items.

## Reused, 0 credits
| Item | Reuse |
|---|---|
| Base body + rig | `wardrobe/body/base.glb` → Rigger adds Mixamo names + arm/forearm twist bones; M/F-slim/petite/bulk via shape keys + bone scale |
| Hands | one cleaned anatomical hand pair (Blender sculpt over base hands), shared |
| Caali kit | `wardrobe/{hair,head,top,jacket,pants,gloves,neck,accessory}/caali_*` + `caali-g.outfit.json` |
| Ikki | split `meshy/ikki-meshy-rigged.glb` (original purple texture) into hair/head/jacket/tee/pants |
| A-T | `wardrobe/skates/at-skate-meshy.glb` (source `meshy/airtreck-meshy.glb`) — add sockets + COLOR_0 slot masks in Blender |
| Crew patches | `shared/crew-logos/<crew>-patch*.png` (albedo/normal/height) |
| Simple parts | halo_clip (torus), high_collar (bomber shape key), leg_hook_straps (curves), cropped bomber (shape key) |

## Batch (dependency order). Cost = credits; Σ = running total
### B0 Base (0) — Rigger: skeleton + twist bones; Forge: hands, neck seam ring, garment masks. Gate for everything below.

### B2 Heads + hair (bust gens, split hair/head in Blender; target head 15–18k, hair 8–12k after decimation)
Prompt template H: `Head and shoulders bust of <desc>, stylized realism, detailed realistic skin PBR, clean separate hair mass, neutral expression, front facing, game-ready, plain grey background`
| # | Item | Mode | <desc> | Cost | Σ |
|---|---|---|---|---|---|
| 1 | Akito | Image-to-3D (`akito/akito-ref.jpg`) + prompt | petite teen boy, shaggy chin-length dark cobalt-blue bob #2F5BD6 with lavender highlights, bangs over right eye, square white gauze eye patch over RIGHT eye with thin strap, amber left eye round pupil, small mole under left eye, gentle closed smile, fair skin | 30 | 30 |
| 2 | Kazu | T2-3D + texture | lanky teen boy, blond fringe under a black knit beanie, relaxed eyes, light skin | 30 | 60 |
| 3 | Kite | T2-3D + texture | slim teen boy, black undercut with cyan-dyed tips, cocky smirk, East Asian | 30 | 90 |
| 4 | Seth | T2-3D + texture | tall teen boy, close-cropped black hair, dark brown skin, calm stern gaze | 30 | 120 |
| 5 | Nova | T2-3D + texture | petite teen girl, silver-lilac short bob, playful grin, light tan skin | 30 | 150 |
| 6 | Moss | T2-3D + texture | sturdy teen boy, shaggy brown hair, sleepy half-closed eyes, Japanese | 30 | 180 |
| 7 | Brick | T2-3D + texture | huge teen boy, blond buzz cut, broken nose, thick neck, pale skin | 30 | 210 |
| 8 | Aurelia | T2-3D + texture | tall elegant teen girl, sleek long black high ponytail, sharp eyeliner, East Asian | 30 | 240 |
| 9 | Gage | T2-3D + texture | stocky teen boy, messy dark hair, grease smudge on cheek, Latino | 30 | 270 |
| 10 | Jolt | T2-3D + texture | wiry teen boy, spiked undercut with yellow tips, wide grin, Latino | 30 | 300 |
| 11 | Marrow | T2-3D + texture | broad teen boy, shaved sides dark hair, scar through eyebrow, quiet stare, Black | 30 | 330 |

### B3 Clothing kits (garment-only gens on invisible mannequin; then fit + skin to base in Blender; atlas colours per bible)
Prompt template G: `Single <garment> only, on invisible A-pose mannequin, no body, no head, realistic fabric PBR, clean seams, game-ready, neutral grey`
| # | Item | Mode | <garment> | Target tris | Cost | Σ |
|---|---|---|---|---|---|---|
| 12 | std_bomber | T2-3D + texture | satin team bomber jacket, rib-knit collar cuffs and hem, sleeve panels, plain back for a patch, zip front | 14k | 30 | 360 |
| 13 | std_hoodie | T2-3D + texture | pullover hoodie, kangaroo pocket, drawstrings, plain back | 12k | 30 | 390 |
| 14 | std_cargo | T2-3D + texture | baggy cargo pants, side pockets, strap loops, side stripe seam | 10k | 30 | 420 |
| 15 | std_slim_pants | T2-3D + texture | slim tapered street pants | 8k | 30 | 450 |
| 16 | akito_gakuran | T2-3D + texture | black Japanese gakuran school jacket, high stand-up collar, single round gold button at chest, plain back | 14k | 30 | 480 |
| 17 | caali_bomber retexture | Retexture (input `wardrobe/jacket/caali_bomber.glb`, ref `caali-g-turnaround.jpg`) | black cropped jacket with ornate gold filigree embroidery, gold cuff bands, large gold phoenix with lightning bolt embroidered on back | keep | 10 | 490 |
| 18 | jackal_hood | T2-3D preview | folded-down hood with tall jackal ears | 3k | 20 | 510 |
| 19 | beanie_scarf | T2-3D preview | knit beanie and long knit scarf set | 4k | 20 | 530 |
| 20 | shoulder_pads | T2-3D preview | padded street armor shoulder pads with strap harness | 4k | 20 | 550 |
| 21 | goggles_toolbelt | T2-3D preview | welding goggles and a leather tool belt with wrenches | 4k | 20 | 570 |
| 22 | helmet_claw_visor | T2-3D preview | skate helmet with smoked visor, three claw scratch marks | 4k | 20 | 590 |
| 23 | knee_guards_storm | T2-3D preview | hard-shell knee guards with forked lightning seams | 2k | 20 | 610 |
| 24 | feather_collar | T2-3D preview | jacket collar trim of stiff black crow feathers | 2k | 20 | 630 |
Accessories are untextured previews: colours come from the atlas, detail from Blender bakes.

### B4 A-T add-on kits (untextured previews; 4–5 parts per gen, split + decimate to the tri budgets in at-standard-spec.md §5; COLOR_0 masks painted in Blender)
Prompt template A: `Kit sheet of separate small bolt-on parts for a futuristic motorized inline skate, hard-surface, premium e-scooter industrial design, panel lines, LED channel grooves, no logos, no text, laid out apart on grey: <parts>`
| # | Kit | <parts> | Cost | Σ |
|---|---|---|---|---|
| 25 | kit A (Code : E, Genesis) | filigree ankle cuff ring, open-lattice wheel cover, lightning emblem plate, sunburst wheel cover, small rear spoiler | 20 | 650 |
| 26 | kit B (Kogarasumaru) | swept crow-feather heel fin, wing spoiler, twin exhaust nozzles, heavy full wheel housing, cuff armor ring | 20 | 670 |
| 27 | kit C (Angels, Anubis, Volt) | three-feather wing ankle plate, twin pointed jackal-ear ankle fins, flat jackal-profile plate, forked-bolt ankle fin | 20 | 690 |
| 28 | kit D (Behemoth, Rust Claw) | bull-horn toe guard, heavy cuff armor, three curved claw heel spurs | 20 | 710 |
| 29 | kit E (Tool Toul To, Forest) | exposed-bolt motor housing with pipes, bark-textured cuff plates | 20 | 730 |
| 30 | A-T hero retexture (optional) | Retexture `meshy/airtreck-meshy.glb`: black armored shell, grey frame, neutral-white LED strips and wheel rims (for slot multiply) | 10 | 740 |
| 31 | Static Angels halo test | skipped (Blender torus) | 0 | 740 |
| 32 | Hand reference (only if Blender sculpt fails) | Image-to-3D of a hand photo, used as sculpt ref | 40 | 780 |

Reserve (retries / failed gens, ~15%): **120 → 900 total** (≤960 cap; leaves ~700 for props/emergency).

## Post (0 credits, Forge + Rigger + Optimizer)
Fit/skin garments to shared rig → per-rider atlas (2048 colour, 1024 normal/ORM, patches baked with height→normal) → LOD0/1/2 → Draco + KTX2 → `wardrobe/riders/<rider>.outfit.json` (+ `atAddons`, `loadout`) → retire `<crew>/<crew>-rider.glb` toon skates. Order of riders for review: Caali, Ikki, Kite, then NPCs, then Kazu/Akito/Volt/Rust Claw.
