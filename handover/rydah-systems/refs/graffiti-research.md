# Sky Rydahs — Graffiti Research & System Proposal
Target: WebXR, Three.js r128, Quest 72 fps, Xbox gamepad (X interact, RT special, LT aim). Inline skates only (no boards or motorcycles). Setting: Palma City (fictional Panama City, FL), 10 crews. Look: stylized realism with a neon grade.

## 1. Real graffiti culture
**Hierarchy (low to high effort and respect):** sticker/slap (a "Hello My Name Is" label or a postal label, placed in seconds) → tag (a one-colour marker or spray signature) → etching (acid or a scribe on glass, permanent) → throw-up/"throwie" (2–3 colours, a fast bubble outline and fill, built for bombing) → stencil (cut template, instant) → roller/blockbuster (big square letters done with rollers or fat caps for maximum coverage) → piece (masterpiece: multicolour, fades, 3D, highlights) → burner (a top-quality piece that "burns" off the wall) → wildstyle (interlocking arrows and letters that are hard to read). **Bombing** means many fast throw-ups or tags in volume. **Heaven spots** are high, dangerous spots (rooftops, billboards, overpasses, water towers) and carry the most prestige.
**Letter styles:** handstyle, bubble, straight letter, semi-wild, wildstyle, 3D/blockbuster, "simple".
**Can control:** caps (skinny or needle caps for outlines and tags, fat caps for fill, soft caps for fades), distance and speed set line width, too slow causes drips (sometimes on purpose), fill first, then the outline, then 3D/shadow, then highlights/"shines" and a background or cloud.
**Etiquette:** never go over a piece with a tag, since going over has to be with something *better* (a throw-up can cover a tag, and a piece can cover a throw-up). Crossing out someone's name starts a beef. Memorials, legends and churches or homes are off-limits by convention. Crews sign "w/ CREW" and give shout-outs.

## 2. Game references
| Game | Tag input | FX | Turf |
|---|---|---|---|
| Jet Set Radio (2000) | Small tag = one tap. Large tags = a chain of analog-stick gestures (half-circles, flicks) | Paint appears in stages per gesture | Rival-gang tags get covered; the area is cleared |
| JSR Future | Mostly one button, with size set by the spot (S/M/L = more presses) | Instant decals | Turf story, rivals spray back |
| Bomb Rush Cyberfunk | Small = tap. Large = a short sequence of stick directions (QTE) | Fast reveal, custom graffiti unlocks | REP and crew battles for districts |
| Getting Up (Marc Ecko) | Hold the trigger and pace the stick motion; going too fast makes drips (fail) | Progressive fill, real artists' styles | Heaven spots, cops, rival "crossing out" |
| THUG | Hold the tag button: a tag is placed at your spot during a combo | Simple decal | Your own tag designer |
| Saints Row (SR2/3/4) | Spray-tag collectables, one press | Decal | Gang-territory map colouring |
| Watch Dogs 2 | Story-placed murals | Cutscene | n/a |
| Splatoon | Shooting ink = coverage | Ink surface shader on a UV-space paint texture | Coverage % decides the win; colours are team-coded |
Takeaways: a JSR stick gesture scaled by spot size, Getting Up's "pace or drip" skill, Splatoon's UV paint maps and team colour readability, and the Saints Row map tint.

## 3. Proposed Sky Rydahs graffiti system
**Spot markers:** a spray-tag icon (can plus a mist puff) shows in the world and on the minimap. Colour = owning crew. Grey = neutral.
**Sizes:**
- S **Tag** (benches, poles, dumpsters): hold X for 0.5 s, then 1 stick flick. +1 turf point.
- M **Throw-up** (walls, shutters, trucks): hold X, then 2–3 stick gestures or a rhythm prompt. +3.
- L **Piece / heaven spot** (billboards, rooftops, water towers): hold X, then 4–6 gestures. Each gesture reveals one layer (fill → outline → 3D → highlights). +10, and it locks for 2 minutes.
**Input:** hold X to enter spray mode, with the camera framing the wall. The right stick traces the shown arc. The gauge rewards steady speed, and going too fast or too slow causes drips and a lower score. Optional rhythm mode: tap RT on the can-shake beats (the RT shake gives a bonus). LT aims a "quick tag" from range (a slap or sticker throw) during combat chases. A perfect gesture chain gives a *Burner* bonus.
**FX:** a GPU-instanced point mist cone (≤64 particles per can) and a mask reveal driven by gesture progress. Drips are a scrolling drip mask strip. Audio: a rattle (ball bearing) when entering spray mode, a looping hiss pitched by stick speed and a cap "pfft" on stop. At night the paint gets an emissive boost from crew colours (fake neon reflection, tied to the grade).
**Turf:** each of the 10 districts has spots. Ownership = the crew with the most points, with a minimum threshold. The world map and minimap tint the district polygon in the crew colour. Rivals can go over (by etiquette, only with an equal or bigger tag size). Crews are AI or other players.
**Police heat (night):** each tag adds heat. Large spots and billboards add more, and cameras or witnesses multiply it. At 3 stars the cops (on skates or in cars) chase you. Lose them by grinding wires or reaching rooftops. Day = low heat but low neon bonus.
**Spot placement and level-design rules:**
1. Every heaven spot needs ≥2 routes (for example a power-cable grind plus a ladder, or a wall ride to a ledge). A clear "lure" line of sight from the street shows the spot in crew-neon.
2. Telephone/power wires: a catenary sag ≤10%, poles every 30–40 m, grind snap within 1.5 m, no break longer than an ollie gap, and each line ends on a roof edge or billboard catwalk.
3. Ladders: a bright yellow rung trim, with X at the bottom to climb (auto-climb at skate speed, 2 s max).
4. Wall-ride panels are marked with a stripe or decal and cover ≤3 s of distance, landing on a ledge ≥2 m deep.
5. A spray stand-pad is 2×2 m and flat, and the painting faces street-level cameras (readability).
6. Benches/park spots are S-size near plazas. Shutters/walls are M along boulevards. Billboards, water towers and the Hathaway-style bridge piers are L.
7. Escape routes from every L spot lead to a downhill or wire exit, for heat play.

## 4. Quest performance recipes (r128)
- **Spots are fixed quads** (a pre-placed PlaneGeometry slightly off the wall, polygonOffset -1/-1), not runtime DecalGeometry projection. Use DecalGeometry only for player free-tags, capped at about 20 with the oldest recycled.
- **Atlas:** all crew tag designs sit in a 2048² KTX2/basis atlas (ETC1S), 256² per S, 512² per M and 1024² per L. A heaven-spot piece can use its own 1024 texture.
- **Mask-reveal shader** (onBeforeCompile on MeshStandardMaterial or a cheap ShaderMaterial): `uniform float uProgress; float m = texture2D(revealMask, vUv).r; float a = smoothstep(uProgress-0.05, uProgress, 1.0-m) * art.a;` The reveal mask is a noise-plus-stroke-order grayscale baked per design. Layer reveals use the R, G, B and A channels as fill, outline, 3D and highlight.
- **Drips:** the alpha strip below the tag scrolls V by time × dripAmount and stops at a baked length.
- **Particles:** one shared THREE.Points of 256 max, additive, 8×8 soft sprite, CPU-updated ring buffer. No more than 64 per active can and 1 active can at a time (plus a remote player's).
- **Budget:** ≤100 draw calls and ≤150k tris per view. Avoid transparent overdraw (use alphaTest 0.5 for tags and blend only the mist). Fixed foveated rendering is on, framebufferScale 1.0. Night neon uses emissive maps plus a vertex-colour fake bounce, with no real-time lights (≤1 dynamic light) and no post bloom (fake the glow with a soft additive halo quad).
- Persist turf as a compact state (spotId → crew, size, timestamp).

## 5. Spray paint textures, palettes and surfaces
### Brand palettes (reference)
- **Montana BLACK** (high pressure, about 180+ colours): bold saturated primaries, a "Shock" series of very vivid tones and a strong fat-cap output. Good for bombing and throw-ups.
- **Montana GOLD** (low pressure, about 190+ colours): a smooth artist range with fine fade steps (greys, skins, pastels) for pieces and 3D.
- **MTN 94 (Montana Colors, Barcelona)** (low pressure, matte, about 200+ colours): famous for matte finish and families of greens, blues and violets with 3–5 shade steps per hue. Ideal for fades.
- **MTN Hardcore**: high pressure, gloss, fast cover.
- **Molotow Premium/Belton** (about 200 colours): a cool-toned art range, plus the Molotow "neon/fluorescent" and "chrome" effect cans and markers. Use these to reference the game's neon.
- **Ironlak** (Australia, about 180 colours): a warm, earthy-to-vivid range with low odour and named-colour culture (e.g. "Bondi", "Pistachio").
Swatch convention: chart cards show 3–6 steps per hue (dark → base → light → pastel) plus a shine white. Mirror that in the game: each crew gets a 5-step ramp.

### Suggested crew palettes (base / dark / light / accent / neon emissive)
| Crew | Base | Dark | Light | Accent | Neon |
|---|---|---|---|---|---|
| Gulf Breakers | #00A6C8 | #005B73 | #7FE3F2 | #FFFFFF | #00F0FF |
| Sunset Strip | #FF5A36 | #9E2A14 | #FFB199 | #FFD23F | #FF3D00 |
| Panhandle Kings | #FFC400 | #8A6A00 | #FFE27A | #1A1A1A | #FFEA00 |
| Bayou Hex | #6A2C91 | #35134D | #B98BD6 | #9DFF00 | #C400FF |
| Pier Rats | #2EBD59 | #145C2A | #94E8AE | #FF2E88 | #39FF14 |
| Neon Gators | #A4E400 | #4D6B00 | #D9FF7A | #00332B | #CCFF00 |
| Hurricane Alley | #5E6B7D | #2B313A | #B4BFCC | #FF1E1E | #E0E8FF |
| Coral Saints | #FF6F91 | #9C2948 | #FFC2D1 | #00C2A8 | #FF4FA3 |
| Tyndall Ghosts | #F2F2F2 | #8C8C8C | #FFFFFF | #0047FF | #9FB8FF |
| Lagoon Royals | #0038A8 | #001E5C | #6F8FE0 | #FFB000 | #2E6BFF |
Rule: neighbouring districts should differ by about 60°+ in hue. Neon is used only as an emissive tint at night.

### Paint on each surface (and at night)
- **Brick and mortar:** the paint covers the brick faces, but the recessed mortar gets thin or no coverage ("skips"). The surface is porous and matte, with an uneven, mottled density and soft overspray. At night the neon glow sits only on brick faces, and the mortar lines read dark, which gives a natural grid texture.
- **Aluminum siding and metal panels:** a glossy wet look. Runs and drips are long (the paint does not soak in). Paint breaks at the panel seams, and the ribbing gives stripes of highlight and shadow. It fades by chalking. At night it picks up sharp specular neon reflections and streaks along the ribs.
- **Glass:** a translucent thin film with visible streaks and a speckled overspray halo. Backlight passes through (looking like stained glass), and etching shows as a frosted scratch. At night interior lights shine through the paint and give a coloured glow onto the floor (fake it with a projected quad).
- **Asphalt:** absorbs paint, so it is matte, darker and desaturated. The grit shows through as speckles, and it wears away along tyre/skate lines (fading). At night it is barely reflective except when wet: rain gives a puddle sheen where neon smears.
- **Overspray:** a soft low-alpha halo of 5–15% of the stroke width (bigger on fat caps). **Drips:** strongest on smooth, non-porous surfaces (metal, glass), short on brick, none on asphalt (it is horizontal). **Fading:** UV sun bleaching (Florida!) cuts saturation by 30–50% after "days", with reds and fluorescents fading first. Simulate it with a per-spot age uniform.

### Three.js r128 surface recipes (Quest)
One shared paint material is used with per-surface uniforms (a define switch, not separate shaders, to limit program count):
```glsl
// fragment additions (onBeforeCompile on MeshStandardMaterial)
uniform sampler2D paintMap;   // atlas region (rgb + a)
uniform sampler2D surfHeight; // the wall's height/AO map (shared with base mat)
uniform float uProgress, uPorosity, uAge, uNight, uHeightCut;
float h = texture2D(surfHeight, vUv2).r;          // 0 = groove, 1 = face
float cover = smoothstep(uHeightCut, uHeightCut+0.1, h); // mortar/seam skip
vec4 p = texture2D(paintMap, vUv);
float a = p.a * cover * reveal(uProgress);
a *= mix(1.0, noise(vUv*40.0), uPorosity);        // mottling (cheap tex noise)
vec3 col = mix(p.rgb, vec3(dot(p.rgb,vec3(.33))), uAge*0.4);  // fade
diffuseColor.rgb = mix(diffuseColor.rgb, col, a);
roughnessFactor = mix(roughnessFactor, uPaintRough, a);
totalEmissiveRadiance += col * a * uNight * uNeon;
```
| Surface | uHeightCut | uPorosity | Paint roughness | Metalness | Drips | Notes |
|---|---|---|---|---|---|---|
| Brick | 0.35 (from AO/height) | 0.5 | 0.9 | 0 | short | the brick height map masks the mortar |
| Metal siding | 0.15 (seams only) | 0.1 | 0.35 | keep 0.6 under paint → 0.2 | long | rib normal map stays, so specular follows the ribs |
| Glass | 0 | 0.2 | 0.2 | 0 | medium | `transparent:true`, paint alpha × 0.7, depthWrite false, render after the opaques. Add backlight with a cheap emissive term × an interior light factor. No refraction. |
| Asphalt | 0 | 0.7 | 1.0 | 0 | none | multiply by (1 − wear mask) and darken 20%; wet = roughness 0.3 in puddle mask zones |
Quest tips: reuse the base wall's AO/height texture (no extra fetch if it is packed into one ORM texture: AO = R, roughness = G, metal = B, height in A). Keep glass paint to a few panels per view (overdraw). Use alphaTest for tags on opaque surfaces, and blend only on glass. Use noise from a 64² tiled texture, not procedural noise.

## References (images)
See `graffiti/SOURCES.txt` (Wikimedia Commons, with each file's license: CC0, PD, CC BY and CC BY-SA. Attribute the BY and BY-SA ones if you redistribute them).
