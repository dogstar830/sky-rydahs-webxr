# Sky Rydahs — Meshy prompt drafts: crew riders (text only, nothing generated)

No existing Meshy prompt files were found under skyrydahs-ref/ or skyrydahs-characters/ (only the locked visual brief), so house style follows `visual-pack/grok-bot-pack/PROMPT-for-grok-bot.md`: stylized realism + neon grade, Air Trecks only.

## Shared settings (apply to every rider)

- Pose: A-pose, full body, front-facing, feet flat on Trecks, arms ~45° down, fingers spread slightly.
- Outfit: crew-color team bomber with the crew logo on the back (`/workspace/skyrydahs-characters/shared/crew-logos/<crew>.png`; apply as decal/texture after generation for clean edges). Colors: `shared/crew-logos/jacket-colorways.json`.
- Footwear: armored Air Trecks (motorized inline skates, in-line wheels, glowing wheel hubs + side piping in per-rider glow color). Never boards, bikes or cars.
- Art style: Meshy 'Realistic' / PBR on; stylized realism, no toon shading. Enable PBR maps (albedo, roughness, metallic, normal); emissive set in Three.js from the glow hex.
- **LOD budget (lead's breakdown):** Player riders on Quest: LOD0 ~100-120k tris total, with face/head 25-30k and hands+Treks 25-30k. LOD1 ~40k. LOD2 ~15k for distant crew NPCs. Desktop gets full detail.
- Meshy target polycount: request high-detail (or ~120k) then remesh/decimate per LOD in Blender; quad remesh for rigging. Rig as humanoid (Meshy auto-rig or Mixamo-compatible) after cleanup.
- Prompt length: each prompt below is under ~800 characters.

## Volt (crew name confirmed by Oliver 2026-10-29; old slug/alias team-storm, "Team Storm") — Jolt Ramírez

- **Concept:** Jolt Ramírez — VOLT's sprint ace / point rider. Silhouette: Lean wiry runner, cropped hot-pink bomber, spiked yellow-tipped undercut, storm-cloud knee guards with forked-lightning seams. Personality: Can't sit still; talks fast, rides faster.
- **Crew palette / glow:** hot pink and yellow; glow yellow (#ffe600), forked-lightning neon piping. Back logo: pink layered thunderhead with three branching yellow lightning forks, ring text VOLT / RIDE THE THUNDERHEAD (`shared/crew-logos/volt.png`; alias `team-storm.png`). Must not read as a single zigzag bolt (that is Code : E).

**Text-to-3D prompt** (628 chars):

```
Full-body 3D character, original teen street skater Jolt Ramírez, VOLT's sprint ace. Lean wiry runner, cropped hot-pink bomber, spiked yellow-tipped undercut, storm-cloud knee guards. Team bomber jacket in hot pink and yellow, crew emblem (pink storm cloud with branching yellow lightning forks) on the back, forked neon piping glowing yellow. Wearing armored futuristic motorized inline skates (Air Trecks) with glowing yellow wheel hubs. Stylized realism, realistic skin and fabric PBR materials, detailed face and hands, strong neon night color grade. A-pose, front view, neutral expression, clean topology, game-ready.
```

**Negative prompt:**

```
toon shading, cel shading, flat colors, anime outlines, chibi, low detail face, extra limbs, fused fingers, motorcycle, car, skateboard, bicycle, roller derby quad skates, weapons, logos of real brands, text artifacts, copyrighted characters, celebrity likeness, T-pose, crouching, cape, blurry textures, baked harsh shadows
```

**Image-to-3D:** Feed none (new rider): first generate text-to-3D, render front A-pose, then use a 2D concept sheet painted over that render for image-to-3D refine. Prefer a clean front A-pose image on a plain mid-gray background, full body head-to-wheels in frame, orthographic-ish camera at chest height; optionally a 2D concept paint-over with the new hot pink and yellow bomber and logo on the back (supply back view as second image if multi-view is available). Keep the face fresh and original, not a likeness of anyone.

**Settings notes:** A-pose, full body, PBR on, no toon. Weight detail to face/head (25-30k) and hands+Treks (25-30k) inside LOD0 100-120k; LOD1 ~40k; LOD2 ~15k (distant NPC). Desktop full detail. Emissive: Treck hubs + jacket piping use `jacket-colorways.json` → `team-storm.emissive_glow`.

## Rust Claw (NEW) — Marrow Kade

- **Concept:** Marrow Kade — Rust Claw enforcer / grinder. Silhouette: Broad-shouldered, heavy orange-rust bomber with shredded sleeve hems, three-scar claw marks painted on helmet visor, chunky scuffed Trecks with claw-shaped heel spurs. Personality: Quiet, scary, loyal to the bone.
- **Crew palette / glow:** burnt orange and rust brown; glow orange (#ff7a1a). Back logo: three claw slashes inside a gear ring (`shared/crew-logos/rust-claw.png`).

**Text-to-3D prompt** (675 chars):

```
Full-body 3D character, original teen street skater Marrow Kade, Rust Claw enforcer. Broad-shouldered, heavy orange-rust bomber with shredded sleeve hems, three-scar claw marks painted on helmet visor, chunky scuffed Trecks with claw-shaped heel spurs. Team bomber jacket in burnt orange and rust brown, crew emblem (three claw slashes inside a gear ring) on the back, neon piping glowing orange. Wearing armored futuristic motorized inline skates (Air Trecks) with glowing orange wheel hubs. Stylized realism, realistic skin and fabric PBR materials, detailed face and hands, strong neon night color grade. A-pose, front view, neutral expression, clean topology, game-ready.
```

**Negative prompt:**

```
toon shading, cel shading, flat colors, anime outlines, chibi, low detail face, extra limbs, fused fingers, motorcycle, car, skateboard, bicycle, roller derby quad skates, weapons, logos of real brands, text artifacts, copyrighted characters, celebrity likeness, T-pose, crouching, cape, blurry textures, baked harsh shadows
```

**Image-to-3D:** Feed none (new rider): same flow as Jolt. Prefer a clean front A-pose image on a plain mid-gray background, full body head-to-wheels in frame, orthographic-ish camera at chest height; optionally a 2D concept paint-over with the new burnt orange and rust brown bomber and logo on the back (supply back view as second image if multi-view is available). Keep the face fresh and original, not a likeness of anyone.

**Settings notes:** A-pose, full body, PBR on, no toon. Weight detail to face/head (25-30k) and hands+Treks (25-30k) inside LOD0 100-120k; LOD1 ~40k; LOD2 ~15k (distant NPC). Desktop full detail. Emissive: Treck hubs + jacket piping use `jacket-colorways.json` → `rust-claw.emissive_glow`.

## Anubis (upgrade) — Seth Okoro

- **Concept:** Seth Okoro — Anubis crew captain. Silhouette: Tall and long-limbed, teal bomber with gold-trimmed collar, jackal-ear hood folded down, slim armored Trecks. Personality: Calm judge of every race; never wastes a word.
- **Crew palette / glow:** deep teal with antique gold hardware; glow teal (#18d6c4). Back logo: front-facing jackal head (`shared/crew-logos/anubis.png`).

**Text-to-3D prompt** (609 chars):

```
Full-body 3D character, original teen street skater Seth Okoro, Anubis crew captain. Tall and long-limbed, teal bomber with gold-trimmed collar, jackal-ear hood folded down, slim armored Trecks. Team bomber jacket in deep teal with antique gold hardware, crew emblem (front-facing jackal head) on the back, neon piping glowing teal. Wearing armored futuristic motorized inline skates (Air Trecks) with glowing teal wheel hubs. Stylized realism, realistic skin and fabric PBR materials, detailed face and hands, strong neon night color grade. A-pose, front view, neutral expression, clean topology, game-ready.
```

**Negative prompt:**

```
toon shading, cel shading, flat colors, anime outlines, chibi, low detail face, extra limbs, fused fingers, motorcycle, car, skateboard, bicycle, roller derby quad skates, weapons, logos of real brands, text artifacts, copyrighted characters, celebrity likeness, T-pose, crouching, cape, blurry textures, baked harsh shadows
```

**Image-to-3D:** Feed /workspace/skyrydahs-characters/anubis/anubis-rider.glb rendered front A-pose (proportions/silhouette only; ignore toon colors). Prefer a clean front A-pose image on a plain mid-gray background, full body head-to-wheels in frame, orthographic-ish camera at chest height; optionally a 2D concept paint-over with the new deep teal with antique gold hardware bomber and logo on the back (supply back view as second image if multi-view is available). Keep the face fresh and original, not a likeness of anyone.

**Settings notes:** A-pose, full body, PBR on, no toon. Weight detail to face/head (25-30k) and hands+Treks (25-30k) inside LOD0 100-120k; LOD1 ~40k; LOD2 ~15k (distant NPC). Desktop full detail. Emissive: Treck hubs + jacket piping use `jacket-colorways.json` → `anubis.emissive_glow`.

## Static Angels (upgrade) — Nova Serra

- **Concept:** Nova Serra — Static Angels aerial trickster. Silhouette: Petite and floaty, purple bomber with cyan neon piping, small holographic halo clip above head, wing-fin ankle plates on Trecks. Personality: Playful prankster who loves height.
- **Crew palette / glow:** violet purple and electric cyan; glow cyan (#00e5ff). Back logo: halo over wings with static zigzag (`shared/crew-logos/static-angels.png`).

**Text-to-3D prompt** (644 chars):

```
Full-body 3D character, original teen street skater Nova Serra, Static Angels aerial trickster. Petite and floaty, purple bomber with cyan neon piping, small holographic halo clip above head, wing-fin ankle plates on Trecks. Team bomber jacket in violet purple and electric cyan, crew emblem (halo over wings with static zigzag) on the back, neon piping glowing cyan. Wearing armored futuristic motorized inline skates (Air Trecks) with glowing cyan wheel hubs. Stylized realism, realistic skin and fabric PBR materials, detailed face and hands, strong neon night color grade. A-pose, front view, neutral expression, clean topology, game-ready.
```

**Negative prompt:**

```
toon shading, cel shading, flat colors, anime outlines, chibi, low detail face, extra limbs, fused fingers, motorcycle, car, skateboard, bicycle, roller derby quad skates, weapons, logos of real brands, text artifacts, copyrighted characters, celebrity likeness, T-pose, crouching, cape, blurry textures, baked harsh shadows
```

**Image-to-3D:** Feed /workspace/skyrydahs-characters/static-angels/static-angels-rider.glb front A-pose render. Prefer a clean front A-pose image on a plain mid-gray background, full body head-to-wheels in frame, orthographic-ish camera at chest height; optionally a 2D concept paint-over with the new violet purple and electric cyan bomber and logo on the back (supply back view as second image if multi-view is available). Keep the face fresh and original, not a likeness of anyone.

**Settings notes:** A-pose, full body, PBR on, no toon. Weight detail to face/head (25-30k) and hands+Treks (25-30k) inside LOD0 100-120k; LOD1 ~40k; LOD2 ~15k (distant NPC). Desktop full detail. Emissive: Treck hubs + jacket piping use `jacket-colorways.json` → `static-angels.emissive_glow`.

## Sleeping Forest (upgrade) — Moss Takeda

- **Concept:** Moss Takeda — Sleeping Forest guardian. Silhouette: Sturdy, layered white bomber with forest-green panels, beanie and scarf, wood-grain textured Treck shells. Personality: Gentle, patient, unbeatable when woken up.
- **Crew palette / glow:** off-white and forest green; glow green (#2ecc71). Back logo: three pine trees under a crescent moon (`shared/crew-logos/sleeping-forest.png`).

**Text-to-3D prompt** (618 chars):

```
Full-body 3D character, original teen street skater Moss Takeda, Sleeping Forest guardian. Sturdy, layered white bomber with forest-green panels, beanie and scarf, wood-grain textured Treck shells. Team bomber jacket in off-white and forest green, crew emblem (three pine trees under a crescent moon) on the back, neon piping glowing green. Wearing armored futuristic motorized inline skates (Air Trecks) with glowing green wheel hubs. Stylized realism, realistic skin and fabric PBR materials, detailed face and hands, strong neon night color grade. A-pose, front view, neutral expression, clean topology, game-ready.
```

**Negative prompt:**

```
toon shading, cel shading, flat colors, anime outlines, chibi, low detail face, extra limbs, fused fingers, motorcycle, car, skateboard, bicycle, roller derby quad skates, weapons, logos of real brands, text artifacts, copyrighted characters, celebrity likeness, T-pose, crouching, cape, blurry textures, baked harsh shadows
```

**Image-to-3D:** Feed /workspace/skyrydahs-characters/sleeping-forest/sleeping-forest-rider.glb front A-pose render. Prefer a clean front A-pose image on a plain mid-gray background, full body head-to-wheels in frame, orthographic-ish camera at chest height; optionally a 2D concept paint-over with the new off-white and forest green bomber and logo on the back (supply back view as second image if multi-view is available). Keep the face fresh and original, not a likeness of anyone.

**Settings notes:** A-pose, full body, PBR on, no toon. Weight detail to face/head (25-30k) and hands+Treks (25-30k) inside LOD0 100-120k; LOD1 ~40k; LOD2 ~15k (distant NPC). Desktop full detail. Emissive: Treck hubs + jacket piping use `jacket-colorways.json` → `sleeping-forest.emissive_glow`.

## Behemoth (upgrade) — Brick Volkov

- **Concept:** Brick Volkov — Behemoth tank / bruiser. Silhouette: Huge frame, black bomber with orange sleeves, padded shoulder armor, oversized heavy Trecks with bull-horn toe guards. Personality: Plows through anything, laughs loudly.
- **Crew palette / glow:** matte black and blaze orange; glow orange (#ff6a00). Back logo: horned bull skull (`shared/crew-logos/behemoth.png`).

**Text-to-3D prompt** (603 chars):

```
Full-body 3D character, original teen street skater Brick Volkov, Behemoth tank. Huge frame, black bomber with orange sleeves, padded shoulder armor, oversized heavy Trecks with bull-horn toe guards. Team bomber jacket in matte black and blaze orange, crew emblem (horned bull skull) on the back, neon piping glowing orange. Wearing armored futuristic motorized inline skates (Air Trecks) with glowing orange wheel hubs. Stylized realism, realistic skin and fabric PBR materials, detailed face and hands, strong neon night color grade. A-pose, front view, neutral expression, clean topology, game-ready.
```

**Negative prompt:**

```
toon shading, cel shading, flat colors, anime outlines, chibi, low detail face, extra limbs, fused fingers, motorcycle, car, skateboard, bicycle, roller derby quad skates, weapons, logos of real brands, text artifacts, copyrighted characters, celebrity likeness, T-pose, crouching, cape, blurry textures, baked harsh shadows
```

**Image-to-3D:** Feed /workspace/skyrydahs-characters/behemoth/behemoth-rider.glb front A-pose render. Prefer a clean front A-pose image on a plain mid-gray background, full body head-to-wheels in frame, orthographic-ish camera at chest height; optionally a 2D concept paint-over with the new matte black and blaze orange bomber and logo on the back (supply back view as second image if multi-view is available). Keep the face fresh and original, not a likeness of anyone.

**Settings notes:** A-pose, full body, PBR on, no toon. Weight detail to face/head (25-30k) and hands+Treks (25-30k) inside LOD0 100-120k; LOD1 ~40k; LOD2 ~15k (distant NPC). Desktop full detail. Emissive: Treck hubs + jacket piping use `jacket-colorways.json` → `behemoth.emissive_glow`.

## Genesis (upgrade) — Aurelia Cho

- **Concept:** Aurelia Cho — Genesis visionary leader. Silhouette: Elegant tall rider, magenta bomber with gold piping and high collar, gold-plated Treck shells with sunburst wheel hubs. Personality: Proud and precise; believes she started the scene.
- **Crew palette / glow:** magenta and gold; glow magenta (#ff1fd1). Back logo: sunburst star with triangle and eye-ring (`shared/crew-logos/genesis.png`).

**Text-to-3D prompt** (627 chars):

```
Full-body 3D character, original teen street skater Aurelia Cho, Genesis visionary leader. Elegant tall rider, magenta bomber with gold piping and high collar, gold-plated Treck shells with sunburst wheel hubs. Team bomber jacket in magenta and gold, crew emblem (sunburst star with triangle and eye-ring) on the back, neon piping glowing magenta. Wearing armored futuristic motorized inline skates (Air Trecks) with glowing magenta wheel hubs. Stylized realism, realistic skin and fabric PBR materials, detailed face and hands, strong neon night color grade. A-pose, front view, neutral expression, clean topology, game-ready.
```

**Negative prompt:**

```
toon shading, cel shading, flat colors, anime outlines, chibi, low detail face, extra limbs, fused fingers, motorcycle, car, skateboard, bicycle, roller derby quad skates, weapons, logos of real brands, text artifacts, copyrighted characters, celebrity likeness, T-pose, crouching, cape, blurry textures, baked harsh shadows
```

**Image-to-3D:** Feed /workspace/skyrydahs-characters/genesis/genesis-rider.glb front A-pose render. Prefer a clean front A-pose image on a plain mid-gray background, full body head-to-wheels in frame, orthographic-ish camera at chest height; optionally a 2D concept paint-over with the new magenta and gold bomber and logo on the back (supply back view as second image if multi-view is available). Keep the face fresh and original, not a likeness of anyone.

**Settings notes:** A-pose, full body, PBR on, no toon. Weight detail to face/head (25-30k) and hands+Treks (25-30k) inside LOD0 100-120k; LOD1 ~40k; LOD2 ~15k (distant NPC). Desktop full detail. Emissive: Treck hubs + jacket piping use `jacket-colorways.json` → `genesis.emissive_glow`.

## Tool Toul To (upgrade) — Gage Mendez

- **Concept:** Gage Mendez — Tool Toul To mechanic-rider. Silhouette: Stocky, gray bomber with rust-red panels, tool belt, welding goggles on forehead, mismatched home-built Trecks with exposed bolts. Personality: Fixes everything, trusts nothing he didn't build.
- **Crew palette / glow:** steel gray and rust red; glow rust-orange (#ff5a2a). Back logo: crossed wrenches over a gear (`shared/crew-logos/tool-toul-to.png`).

**Text-to-3D prompt** (644 chars):

```
Full-body 3D character, original teen street skater Gage Mendez, Tool Toul To mechanic-rider. Stocky, gray bomber with rust-red panels, tool belt, welding goggles on forehead, mismatched home-built Trecks with exposed bolts. Team bomber jacket in steel gray and rust red, crew emblem (crossed wrenches over a gear) on the back, neon piping glowing rust-orange. Wearing armored futuristic motorized inline skates (Air Trecks) with glowing rust-orange wheel hubs. Stylized realism, realistic skin and fabric PBR materials, detailed face and hands, strong neon night color grade. A-pose, front view, neutral expression, clean topology, game-ready.
```

**Negative prompt:**

```
toon shading, cel shading, flat colors, anime outlines, chibi, low detail face, extra limbs, fused fingers, motorcycle, car, skateboard, bicycle, roller derby quad skates, weapons, logos of real brands, text artifacts, copyrighted characters, celebrity likeness, T-pose, crouching, cape, blurry textures, baked harsh shadows
```

**Image-to-3D:** Feed /workspace/skyrydahs-characters/tool-toul-to/tool-toul-to-rider.glb front A-pose render. Prefer a clean front A-pose image on a plain mid-gray background, full body head-to-wheels in frame, orthographic-ish camera at chest height; optionally a 2D concept paint-over with the new steel gray and rust red bomber and logo on the back (supply back view as second image if multi-view is available). Keep the face fresh and original, not a likeness of anyone.

**Settings notes:** A-pose, full body, PBR on, no toon. Weight detail to face/head (25-30k) and hands+Treks (25-30k) inside LOD0 100-120k; LOD1 ~40k; LOD2 ~15k (distant NPC). Desktop full detail. Emissive: Treck hubs + jacket piping use `jacket-colorways.json` → `tool-toul-to.emissive_glow`.

## Kogarasumaru rider (upgrade) — Kite Aramaki

- **Concept:** Kite Aramaki — Kogarasumaru scout / wingman. Silhouette: Slim agile teen, black bomber with cyan panels and cyan neon piping, crow-feather collar trim, sleek black Trecks with cyan wheel glow. Personality: Cocky but loyal; first in, last out.
- **Crew palette / glow:** black and cyan only (no red); glow cyan (#00e5ff). Back logo: crow with spread wings, motto ring (`shared/crew-logos/kogarasumaru.png`).

**Text-to-3D prompt** (638 chars):

```
Full-body 3D character, original teen street skater Kite Aramaki, Kogarasumaru scout. Slim agile teen, black bomber with cyan panels and cyan neon piping, crow-feather collar trim, sleek black Trecks with cyan wheel glow. Team bomber jacket in black and cyan only (no red), crew emblem (crow with spread wings, motto ring) on the back, neon piping glowing cyan. Wearing armored futuristic motorized inline skates (Air Trecks) with glowing cyan wheel hubs. Stylized realism, realistic skin and fabric PBR materials, detailed face and hands, strong neon night color grade. A-pose, front view, neutral expression, clean topology, game-ready.
```

**Negative prompt:**

```
toon shading, cel shading, flat colors, anime outlines, chibi, low detail face, extra limbs, fused fingers, motorcycle, car, skateboard, bicycle, roller derby quad skates, weapons, logos of real brands, text artifacts, copyrighted characters, celebrity likeness, T-pose, crouching, cape, blurry textures, baked harsh shadows
```

**Image-to-3D:** Feed /workspace/skyrydahs-characters/kogarasumaru/kogarasumaru-rider.glb front A-pose render (ignore any red in old textures). Prefer a clean front A-pose image on a plain mid-gray background, full body head-to-wheels in frame, orthographic-ish camera at chest height; optionally a 2D concept paint-over with the new black and cyan only (no red) bomber and logo on the back (supply back view as second image if multi-view is available). Keep the face fresh and original, not a likeness of anyone.

**Settings notes:** A-pose, full body, PBR on, no toon. Weight detail to face/head (25-30k) and hands+Treks (25-30k) inside LOD0 100-120k; LOD1 ~40k; LOD2 ~15k (distant NPC). Desktop full detail. Emissive: Treck hubs + jacket piping use `jacket-colorways.json` → `kogarasumaru.emissive_glow`.
