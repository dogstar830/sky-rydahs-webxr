# Sky Rydahs — Character Bible v2 (Rydah Forge, 2026-10-29 04:40 CDT)
Direction (Oliver 04:32 CDT): redesign every rider for Meshy, keep every character, each with own style; **Air Trek gear is one standard set**: style comes only from crew colours + bolt-on add-ons (see `at-standard-spec.md`). Batch/credits: `meshy-batch-plan.md`.
Precedence: Oliver's locked chat facts > Oliver's sheets (caali-g-turnaround.jpg, akito-ref.jpg) > aesthetic brief / visual-pack PROMPT > meshy-prompts-crews.md > jacket-colorways.json. **PROPOSED** = no Oliver source; needs his OK.
IP: Ikki, Kazu, Akito, Kogarasumaru, Sleeping Forest, Behemoth, Genesis, Tool Toul To are Air Gear placeholders built as specified (Oliver's call). **Akito = local demo only (`?player=akito`), never in a public PR/deploy until renamed.**

## 0. Build from the inside out (applies to all)
1. **Base body** `wardrobe/body/base.glb` (Caali rigged Meshy base, reused). Two proportion presets via bone scale + shape keys, not new meshes: `M` (Caali/Ikki height 1.70 m) and `F/slim` (Nova, Aurelia; Akito petite = slim preset at 0.92 scale). Brick = M preset +12% shoulder/chest shape key.
2. **Skeleton**: one Mixamo skeleton (`mixamorig:` names) + twist bones `LeftForeArmTwist`, `RightForeArmTwist`, `LeftArmTwist`, `RightArmTwist` (50% roll share, Rigger). All clothing skinned to this rig; Rigger owns weights.
3. **Hands**: anatomically correct 5-finger hands, 3 phalanges + metacarpal arch, nails, knuckle creases; full Mixamo finger chain. Replace the Meshy hands on base.glb with one sculpted/cleaned hand pair (Blender, 0 credits), reused by every rider. Gloves are shells over these hands.
4. **Head**: per-rider head mesh on shared neck seam (fixed seam ring, 48 verts) so heads swap. Eyes = separate tiny spheres in atlas.
5. **Clothing**: separate meshes in the existing slots (`slots.json`: hair, head, top, jacket, pants, gloves, neck, accessory, skates). Body under clothing is hidden by `base_mask_rigged_verts.npy`-style masks (per-garment bit mask, slot bits from slots.json).
6. **Team jacket**: every crew rider wears the crew bomber (one shared `std_bomber` mesh, colour by atlas) with the crew patch on the back: **embroidered, high contrast, stitched satin edge (merrowed border), raised** = patch albedo `shared/crew-logos/<crew>-patch-noshadow.png` + `-patch-normal.png`/`-patch-height.png` baked into the jacket normal (normalScale 1.0). Exceptions: Ikki (own purple jacket, crow patch still on back), Caali (cropped filigree jacket + phoenix back), Akito (gakuran), Kazu (hoodie with crew patch).
7. **Budgets**: player LOD0 100–120k tris (head+hair 25–30k, hands+A-T 25–30k, body+clothes ~45–60k); NPC LOD0 ≤30k, LOD1 ~40k (player), LOD2 ~15k; ≤3 materials: `M0 rider_atlas` (2048 colour + 1024 normal/ORM), `M1 at_skate` (shared A-T), `M2 rider_fx` (emissive piping/halo, optional). Draco + KTX2; HD behind `?hd`.

## 1. Roster
Colours are hex; "glow" = A-T `glow` slot and jacket neon piping. Mismatch IDs refer to the 11 MISMATCH lines in `v3build/DEMO_STATUS.md` → Rider audit: **M1** NPC skates, **M2** Caali skates+palette, **M3** Caali back logo, **M4** Ikki outfit/off-hex cyan, **M5** Kogarasumaru jacket base, **M6** Anubis, **M7** Behemoth, **M8** Sleeping Forest, **M9** Genesis, **M10** Tool Toul To, **M11** Static Angels shell.

### Caali G — Code : E (founder/leader) — player (MVP) — UPDATED 2026-10-30
- Source (primary): `skyrydahs-ref/characters/caali-anika-2026-10-30/caali-anika-ref2-day-clean.jpg` (+ ref1-night-fx, ref3-pole-grind, README.md). Meshy: `/home/box/Downloads/gr8yzone/caali-meshy.glb` (crop `caali_crop.png`). Secondary: `skyrydahs-ref/caali-g-turnaround.jpg` (back phoenix only, pending Oliver). Plan: `caali-anika-2026-10-30/forge-plan.md`.
- Style: adult, lean athletic, warm brown skin #6B4226, **goatee + moustache #15100D**, calm confident. **Purple cap worn backwards** (#5A3D8A, Oliver exception to M2) + **white over-ear headphones** #EDEDED.
- Modular meshes: hat `caali_cap_headphones` (NEW, slot pending) · head `caali_head` v2 (beard) · hair `caali_curly_short` (mostly hidden under the cap) · top `caali_gr8yzone_tee` black #0B0B0D, **GR8YZONE** gold #FFD700 + gold bolt with blue edge #2E6BFF · jacket `caali_leather_jacket` (NEW, replaces cropped `caali_bomber`): **hip-length black leather #0B0B0D, gold baroque embroidery #FFD700/#C9A227, gold chain trim**, stand collar · pants `caali_cargo` black, single gold side stripe #FFD700, hanging chain `gold_pants_chains` · neck gold chain (thinner) · gloves `caali_fingerless` black.
- A-T: standard black shell, paint #0B0B0D, frame #C9A227, wheel #1C1C20, **glow #FFD700 (gold wheels, no cyan)**.
- Fixes: M2 (gold-only skate palette; purple allowed on the cap only), M3 (phoenix pending Q2), spelling GRB→GR8YZONE.

### Anika — Code : E (with Caali G, per Oliver 2026-10-30) — NEW rider, playable (?player=anika), 2026-10-30. Back patch: Code : E crew patch (shared/crew-logos/code-e-patch.png + -normal/-height), embroidered on the back of her sailor top, per Oliver 01:39 CDT 2026-10-30. Gr8yzone chest patch stays.
- Source: `skyrydahs-ref/characters/caali-anika-2026-10-30/caali-anika-ref2-day-clean.jpg` (+ ref1, ref3, README.md). Meshy: `/home/box/Downloads/gr8yzone/anika-meshy.glb` (crop `anika_crop.png`). Plan: `caali-anika-2026-10-30/forge-plan.md`.
- Style: slim preset, fair skin #E8B894, freckles, friendly smile; **long blonde braided pigtails #D9B56A**.
- Modular meshes: hair `anika_braids` · head `anika_head` · top `anika_sailor_top` pink #E0457B crop, pale-pink sailor collar #F6C9D6, **red neckerchief #C8102E**, GR8YZONE patch/print + gold sleeve emblem · pants slot `anika_pleated_skirt` pink #E85A8C, **gold trim #FFD700** + accessory `anika_skirt_chain` gold · legwear (new slot pending) `anika_thighhighs_bows` white #F4F4F2, **pink bows #F28AB0** · bare hands (shared anatomical hands).
- A-T: standard black shell, paint #0B0B0D, frame #C9A227, wheel #1C1C20, **glow #FFD700**. Pink/cyan/violet light trails = FX only (Q4).


### Simca — 'the Migratory Bird' — free-flying rider (NEW 2026-11-05)
- Source: `skyrydahs-ref/simca/refs-2026-11-05/` (ref1–ref7 + contact.jpg). Meshy: `skyrydahs-characters/simca/meshy/Meshy_AI_Pink_Haired_Cadet_1105160116_texture.glb`. Files: `simca/simca-rider.glb`, `simca/simca-npc.glb` (91-joint shared rider skeleton).
- Role: spots Caali G's potential first; free-flying scout / Migratory Bird.
- Style: slim (≈Anika height or slightly taller), fair skin; **very long bubblegum-pink hair** (split locks for swing bones); **dark green peaked cadet cap with goggles** on brim (rigid head-attached); large expressive eyes.
- Outfit: **white dress/sailor uniform** with **dark green sailor-collar trim** and **red neck ribbon**; dark fingerless gloves; **green knee boots** (A·T boot uppers; shared black-shell v2 skate mounted at runtime). Optional yellow harness straps.
- Crew colours: **white / green** (paint #0B0B0D shared black shell, frame #1F5E36 green, wheel #EEF2EC, glow #2ECC71 PROPOSED — match Sleeping Forest green family until Oliver locks a Simca-specific glow).
- A-T: standard black-shell v2, 2 big wheels; keep green boot uppers to the ankle socket.
- Notes for Rigger: 6 back hair locks + 2 side locks (`Simca_HairBack_00..05`, `Simca_HairSideL_06`, `Simca_HairSideR_07`) cut from the original Meshy hair sheet, with lengthways edge loops (rings≈103–117) for swing-bone chains; cap #1F4A2A + goggles stay rigid on Head. Files also ship `.quest.glb` / `.quest-ktx2.glb`.

### Ikki — Kogarasumaru — leader / mentor (MVP)
- Source: existing `meshy/ikki-meshy-rigged.glb` (original purple texture, NOT the cyan bake) + Oliver lock.
- Style: spiky black hair, wiry, cocky grin; signature: **original purple outfit** (crew-rule exception) + crow patch.
- Modular meshes (split from Ikki mesh, re-skinned to shared rig): hair `ikki_spikes`, head `ikki_head`, jacket `ikki_jacket` **purple, sampled from the original Meshy texture** (fallback #5B2A86 PROPOSED), top `ikki_tee` black #07090B, pants `ikki_pants` purple (same sample), gloves `ikki_wrap` black, back crow patch `kogarasumaru-patch`.
- A-T: paint #07090B, frame #07090B, wheel #0B1418, **glow #00E5FF** (exact; no 0x30d8ff/0x40f0ff). Add-ons: `kg_crow_fin` (heel), `kg_wing_spoiler`.
- Fixes: **M4** (remove vRestY cyan hue-remap of jacket; jacket stays purple; cyan only on A-T/highlights at exact #00E5FF).

### Kazu — Kogarasumaru — 2nd / Flame Road speedster (v1)
- Source: production-plan §1.5 ("beanie + blue hoodie"); look otherwise **PROPOSED**.
- Style: lanky, blond fringe under a **black beanie with cyan crow tab**, relaxed eyes; signature: flame-streak LEDs.
- Meshes: hair `kazu_fringe`, head `kazu_head`, top `std_hoodie` **blue #2A5CC8 PROPOSED** with cyan #00E5FF drawstrings, Kogarasumaru patch on hoodie back, pants `std_slim_pants` black #07090B, accessory `beanie_black`.
- A-T: paint #07090B, frame #07090B, wheel #0B1418, glow #00E5FF (PROPOSED: boost tint #FF7A1A for flame trail VFX only, not a slot). Add-ons: `kg_flame_exhaust` (twin rear exhaust).
- Fixes: new character (no audit row).

### Akito — Kogarasumaru — Fang melee rider (placeholder, LOCAL ONLY)
- Source: `akito/akito-ref.jpg`, `akito-details.md` + Oliver lock (Oliver hex wins over details-md estimates).
- Style: petite (slim preset ×0.92), narrow shoulders; **shaggy dark cobalt-blue bob #2F5BD6, lavender highlights #8A8FE6**, bangs over right eye; **white gauze eye patch #EDEEE2 over RIGHT eye**, dotted tape #9A9C92, thin strap; **amber left eye #C9962E** (rim #6B4A14, round pupil); mole under left eye; soft smile; skin #F6D3C8.
- Meshes: hair `akito_bob`, head `akito_head` (patch modelled on head), jacket `akito_gakuran` **high-collar black #12151F/#1F2433** with single gold button #C8A030 and Kogarasumaru patch on back, pants `std_slim_pants` black, accessory `leg_hook_straps` (black leather shin straps).
- A-T: paint #07090B, frame #07090B, wheel #0B1418, glow #00E5FF. Add-ons: `kg_fang_wheel_housing` (heavy wheel covers, the "Fang" bulk), `kg_cuff_armor`.
- Fixes: none in audit (status OK); this rebuild moves him onto the shared skate/base.

### Kite Aramaki — Kogarasumaru — scout / wingman NPC
- Source: meshy-prompts-crews.md.
- Style: slim agile, **undercut black hair with cyan-dyed tips** PROPOSED, cocky; signature: **crow-feather collar trim**.
- Meshes: `std_bomber` **black #07090B with cyan panels #00E5FF** (sleeve + side panels), rib #0B1418, lining #003B44, hardware #8FA6AD, crow patch back; `feather_collar` add-on mesh; `std_slim_pants` black; `std_gloves_fingerless`.
- A-T: paint #07090B, frame #07090B, wheel #0B1418, glow #00E5FF. Add-ons: `kg_crow_fin`.
- Fixes: **M5** (jacket solid cyan → black with cyan panels), **M1**.

### Seth Okoro — Anubis — captain NPC
- Source: meshy-prompts-crews.md + Oliver lock.
- Style: tall long-limbed, close-cropped hair, dark skin; signature: **jackal-ear hood folded down** + jackal helmet motif.
- Meshes: `std_bomber` **teal #0A3D3A** body, dark trim #031413, **antique-gold trim/collar/hardware #C9A75A**, piping glow #18D6C4, jackal patch back; `jackal_hood` (accessory, folded); `std_cargo` #031413.
- A-T: paint #0A3D3A, frame #C9A75A, wheel #031413, **glow #18D6C4**. Add-ons: `an_jackal_ear_fins` (cuff), `an_gold_emblem_plate`.
- Fixes: **M6** (bright #00BFA5 → teal #0A3D3A, restore antique gold, glow 0x00e0d0 → #18D6C4), **M1**.

### Nova Serra — Static Angels — aerial trickster NPC
- Source: meshy-prompts-crews.md.
- Style: petite (slim preset), silver-lilac bob PROPOSED; signature: **holographic halo clip** above head.
- Meshes: `std_bomber` **purple #3A1670 / #9B4DFF panels**, cyan piping #00E5FF, hardware #C0C6D0, halo+wings patch back; `halo_clip` (M2 fx, emissive #00E5FF); `std_leggings` #3A1670.
- A-T: paint **#0B0B0D (shared black shell, not purple)**, frame #9B4DFF, wheel #3A1670, glow #00E5FF. Add-ons: `sa_wing_fins` (ankle plates).
- Fixes: **M11** (purple skate shell 0x4a2a78 → black shell, purple only on frame slot), **M1**.

### Moss Takeda — Sleeping Forest — guardian NPC
- Source: meshy-prompts-crews.md + Oliver lock.
- Style: sturdy, calm, sleepy eyes; signature: **beanie + scarf** layered.
- Meshes: `std_bomber` **off-white #EEF2EC with deep green panels #1F5E36**, rib #1F5E36, hardware #A8B0A8, pine+moon patch back; `beanie_knit` #1F5E36; `scarf_long` #1F5E36; `std_cargo` #1F5E36.
- A-T: paint #0B0B0D, frame #1F5E36, wheel #EEF2EC, **glow #2ECC71**. Add-ons: `sf_bark_cuff_plates` (wood-grain is now an add-on texture, not the shell).
- Fixes: **M8** (jacket inverted: base off-white, green panels; glow 0x6dffa8 → #2ECC71), **M1**.

### Brick Volkov — Behemoth — tank NPC
- Source: meshy-prompts-crews.md + Oliver lock.
- Style: huge (M preset + bulk shape key), buzz cut, broken nose; signature: **padded shoulder armor**.
- Meshes: `std_bomber` **matte black #0E0B09 body, orange sleeves #FF6A00**, rib #FF6A00, hardware #2B2B2B, bull-skull patch back; `shoulder_pads`; `std_cargo` #0E0B09.
- A-T: paint #0E0B09, frame #2B2B2B, wheel #0E0B09, **glow #FF6A00**. Add-ons: `bh_bull_horn_toe_guards`, `bh_heavy_cuff_armor`.
- Fixes: **M7** (solid orange → black body/orange sleeves; glow 0xff7a12 → #FF6A00), **M1**.

### Aurelia Cho — Genesis — leader / antagonist NPC
- Source: meshy-prompts-crews.md + Oliver lock.
- Style: tall elegant (slim preset ×1.04), sleek long black ponytail PROPOSED; signature: **high collar + gold piping**.
- Meshes: `std_bomber` + `high_collar` add-on: **magenta #FF2BD6** body, **gold trim/piping #FFC94A**, cuff #FF1FD1, sunburst patch back; `std_slim_pants` #14031A.
- A-T: paint #0B0B0D, frame #FFC94A (gold "plating" = frame slot only), wheel #14031A, **glow #FF1FD1**. Add-ons: `gn_sunburst_wheel_covers`, `gn_gold_spoiler`.
- Fixes: **M9** (restore gold trim/piping; glow 0xff2fae → #FF1FD1; base magenta not plum #5A0A52, see C1), **M1**.

### Gage Mendez — Tool Toul To — mechanic-rider NPC
- Source: meshy-prompts-crews.md + Oliver lock.
- Style: stocky, grease smudges; signature: **welding goggles on forehead + tool belt**.
- Meshes: `std_bomber` **steel gray #5B5F63 with rust panels #B7472A**, rib #2E3033, hardware #9AA0A6, patch back; `goggles_forehead`; `tool_belt`; `std_cargo` #2E3033.
- A-T: paint #0B0B0D, frame #5B5F63, wheel #2E3033, **glow #FF5A2A**. Add-ons: `tt_exposed_bolt_motor_housing` ("home-built" look = add-on, not a different skate).
- Fixes: **M10** (solid rust → gray body/rust panels; glow 0xff6a1a → #FF5A2A), **M1**.

### Jolt Ramírez — Volt (file id `team-storm`) — sprint ace (planned)
- Source: meshy-prompts-crews.md (written as "Team Storm, formerly Volt"). **Resolved (Oliver, 2026-10-29): crew name is Volt.**
- Style: lean wiry, **spiked yellow-tipped undercut**; signature: **storm-cloud knee guards**.
- Meshes: `std_bomber` **cropped** variant, **hot pink #FF2D95** body, yellow #FFE600 rib/piping, trim #14050D, storm patch back; `knee_guards_storm`; `std_slim_pants` #14050D.
- A-T: paint #0B0B0D, frame #FF2D95, wheel #14050D, **glow #FFE600**. Add-ons: `vt_bolt_fins`.
- Fixes: brief "Volt has no rider in build" (COLORWAYS line).

### Marrow Kade — Rust Claw — enforcer (planned)
- Source: meshy-prompts-crews.md.
- Style: broad, quiet; signature: **helmet with three claw-scar visor marks**, shredded sleeve hems.
- Meshes: `std_bomber` **orange #FF7A1A accents on rust #8A3416 base**, trim #2A130A, hardware #7A4A2A, claw-gear patch back; `helmet_claw_visor`; `std_cargo` #2A130A.
- A-T: paint #0B0B0D, frame #8A3416, wheel #2A130A, **glow #FF7A1A**. Add-ons: `rc_claw_heel_spurs`.
- Fixes: brief "Rust Claw has no rider in build".

## 2. Shared clothing kit (generate once, colour per rider in atlas)
`std_bomber` (+ `cropped` shape key), `std_hoodie`, `std_cargo`, `std_slim_pants`, `std_leggings` (= slim pants shape key), `std_gloves_fingerless`; rider-specific: `caali_*` (exists), `ikki_*` (split), `akito_gakuran`, accessories listed above. Tri targets (player LOD0 / NPC LOD0): jacket 14k/5k, top 6k/2k, pants 10k/4k, gloves 3k/1k, accessory ≤4k/1.5k, hair 8–12k/3k, head 15–18k/5k.
