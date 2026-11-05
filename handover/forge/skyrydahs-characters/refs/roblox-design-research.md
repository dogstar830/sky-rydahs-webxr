# Roblox avatar/skin design research → Sky Rydah's riders
Researched 2026-10-28. Techniques only; no Roblox items copied.

## Sources
- Character body specs (R15, tri budgets, attachments, skin-tone alpha, outer cage): https://create.roblox.com/docs/art/characters/specifications
- Rigid accessory specs (4k tris, attachment names, shoulder vs collar, size boxes): https://create.roblox.com/docs/art/accessories/specifications
- Layered accessory specs (inner/outer cages, 4k tris, shared UV-matched cages): https://create.roblox.com/docs/en-us/avatar/layered-accessories/specifications.md
- Create cages in Blender: https://create.roblox.com/docs/en-us/art/modeling/cage-meshes/create-cages.md
- General mesh specs (20k tri/mesh cap, watertight, quads): https://create.roblox.com/docs/art/modeling/specifications
- Custom thumbnails: https://create.roblox.com/docs/en-us/marketplace/custom-thumbnails.md
- UGC selling guide (rolearn.dev, third-party): https://rolearn.dev/guidance/roblox-ugc-item-creation-selling-guide/
- UGC catalog trends 2026 (third-party; stats unverified): https://rolearn.dev/trend-reports/roblox-ugc-catalog-2026-categories-trends-top-creators/
- UGC marketplace trends 2026 (third-party): https://rolearn.dev/trend-reports/roblox-ugc-marketplace-trends-2026/
- Bundles announcement: https://www.gamedeveloper.com/business/roblox-will-soon-let-creators-list-item-bundles-to-grow-their-earnings-

## Key technical facts
- **R15 body = 15 meshes → 6 assets.** Tri caps: head 4,000; torso 1,750; each limb 1,248; whole body ~10,742. Each accessory (rigid or layered) ≤4,000 tris; 2048² max texture (auto-downscaled).
- **Rig:** Root→HumanoidRootNode→LowerTorso→UpperTorso→Head/arms; legs from LowerTorso. ≤4 bone influences per vertex, none on Root, symmetric weights. Optional "advanced R15" adds up to 37 bones (spine/chest/clavicles/fingers).
- **Named attachment sockets:** Hat, Hair, FaceFront, FaceCenter (head); Neck, L/R Collar, BodyFront, BodyBack (upper torso); Root, WaistFront/Center/Back (lower torso); L/R Shoulder (arm); L/R Grip (hand, oriented perpendicular to forearm); L/R Foot. Sockets sit half-buried in the surface. **Shoulder sockets follow the arm, collar sockets do not** — a useful distinction for pads vs. scarves.
- **Per-slot size boxes** stop accessories from wrecking silhouette/collisions (e.g., hat ~1.9×2.5×1.9, back up to ~9.9×8.6×4.9 studs on Normal scale).
- **Layered clothing via cages:** body has an _OuterCage; each garment has _InnerCage (fits to what's beneath) and _OuterCage (what goes over it). All cages share one template topology/UVs so any garment fits any body; vertex correspondence is by UV.
- **Skin-tone via alpha:** skin regions left transparent in texture; engine fills a user tint underneath; shading as low-opacity black so it works on any tint. Same idea = mask-driven recolor.
- **Dynamic Heads:** FACS-pose-driven face rig (head budget 4k tris) — expression via a fixed pose set, plus face accessories (brows/lashes) bundled with heads.
- **Body scale standards** (Classic/Normal/Slender) are fixed so gameplay and accessories stay consistent.

## What sells (design/economy)
- Read at thumbnail scale (~64px): bold silhouette + strong color contrast beats geometric detail; low poly that looks clean beats max-budget detail.
- Look good from the back — players mostly see avatars from behind in gameplay (directly relevant to a third-person/skating view).
- Hair and full "looks" carry identity; bundles (matched body+clothes+accessories) outperform singles per seller; mix-and-match keeps buyers in-ecosystem.
- Emotes/animations are the fastest-growing category; consistent creator "brand style" drives repeat purchases; drops timed to events.
- Name + thumbnail must match; custom thumbnails at a strong angle.

## Apply to Sky Rydah's riders
1. **Adopt a fixed socket list on our rig** (Three.js Object3D children of bones): Hat, Hair, FaceFront, Neck, BodyBack, BodyFront, L/R Collar (torso-bound), L/R Shoulder (arm-bound), WaistBack, L/R Grip, L/R Foot (skate mount). Name them in Blender as `*_Att` empties and parent at load.
2. **Budget split for ~20k tris:** body 9–10k (head ≤3k incl. face), hair ≤2.5k, jacket/top layer ≤3k, skates ≤2k pair, 2–3 accessories ≤1k each, small board/emblem slack. Enforce in a CI/import check.
3. **Per-slot bounding boxes** so cosmetics can't blow out silhouette or clip the skate/stride; reject on import.
4. **Simplified "cage" for layered clothing:** one shared low-res body proxy cage; author jackets/pants pre-fit to it and skinned to the same skeleton (copy weights from body). Hide body faces under garments via per-slot hidden-region masks instead of runtime wrap deformation (cheap on Quest 3).
5. **Mask-driven recolor (the skin-tone trick generalized):** grey-banded atlas where band index → crew palette slot (primary, secondary, accent, trim, skin). One shared material + palette uniform/texture row per crew → recolor without new textures, one draw call.
6. **Merge everything into one skinned mesh at equip time** (BufferGeometryUtils merge of body+cosmetics sharing the atlas) → 1–2 draw calls/rider; keep rigid head-socket items as child meshes only if animated separately.
7. **Silhouette first, per crew:** give each crew one signature shape readable at 64px/30m: e.g., crow-feather collar/hood (Kogarasumaru), tall jackal ears/headpiece (Anubis), halo/wing back piece (Static Angels), heavy oversized shoulders (Behemoth), leafy/hooded layered cloak (Sleeping Forest), crown/sun-disc motif (Genesis), tool-belt/strap rig (Tool Toul To), clean visor/gold chain (Code : E). Test as black silhouettes.
8. **Color blocking by large zones**, 2 crew colors + 1 neutral + 1 accent; avoid noise; keep value contrast so crews read in grayscale and for colorblind players.
9. **Design the back view first** — chase cam sees backs: crew emblem on BodyBack, back-socket item, hair/hood shape.
10. **Skates as a first-class cosmetic slot** (Foot sockets): swappable boots/wheels/trails with emissive accent band from crew palette.
11. **Face via small expression set** (FACS-lite): 6–8 morph targets or texture-swap eyes/mouth (neutral, grin, focus, shout, wince, blink) driving emotes; keeps head budget low.
12. **Body scale standards:** 1–2 fixed proportion presets so all cosmetics fit and gameplay hitboxes stay fair.
13. **Bundles = crew kits + mix-and-match:** sell/unlock full crew looks, but every piece is slot-standard so players combine across crews; recolor makes any piece wear any crew's palette.
14. **Emotes/tricks as cosmetics:** celebratory trick animations and taunts are high-value, low-tri content; ship a starter set per crew.
15. **Thumbnail/locker previews:** auto-render each item at a fixed strong angle on a grey mannequin + crew tint for the in-game locker.
