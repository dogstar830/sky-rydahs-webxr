# Shared crew art

Art for the ten Sky Rydahs crews. These files are not wired into the game yet. `v3/index.html`, the root `index.html`, and `v3/sw.js` do not reference this folder.

Volt was renamed Team Storm. The slug is `team-storm`.

Crew slugs: `code-e`, `kogarasumaru`, `team-storm`, `rust-claw`, `anubis`, `static-angels`, `sleeping-forest`, `behemoth`, `genesis`, `tool-toul-to`.

## crew-logos/

| File | What it is |
| --- | --- |
| `<crew>.svg` | Vector logo, 1024×1024 viewBox |
| `<crew>.png` | Flat 1024×1024 decal (RGBA) |
| `<crew>-patch-noshadow.png` | Embroidered patch albedo for in-game decals, 1024×1024, no drop shadow |
| `<crew>-patch-normal.png` | Matching tangent-space normal map, OpenGL +Y (Three.js default), 1024×1024 |
| `jacket-colorways.json` | Per-crew jacket colors (`hex`, `int` for `THREE.Color`, `three` as `0x…`), PBR roughness and metalness, and paths to the logo and patch files |

Paths in `jacket-colorways.json` are relative to `v3/`, for example `skyrydahs-characters/shared/crew-logos/code-e-patch-noshadow.png`.

Shadowed `<crew>-patch.png` albedos, `<crew>-patch-height.png` maps, and preview sheets were left out of this drop. The JSON only points at files in this folder. Color and PBR values are unchanged from the source colorways.

## crew-coins/

| File | What it is |
| --- | --- |
| `<crew>-coin.glb` | Crew token coin: 1,024 triangles, 26.5 mm across and 2 mm thick, textures embedded in the file, each under 1 MB |
| `coins-contact-sheet.png` | Reference contact sheet of all ten coins (2000×1658), for art review |
