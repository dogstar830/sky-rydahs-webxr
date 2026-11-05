# Anika rig and integration plan (Rydah Rigger, 2026-10-30)
Refs: caali-anika-2026-10-30/ (ref1-night-fx, ref2-day-clean, ref3-pole-grind). Mesh: Rydah Forge (image-to-3D from ref2). Skeleton: shared/skeleton/rider-skeleton.glb (91 joints).
**Crew: TBD (null).** Gr8yzone is Caali's shirt brand, not a crew. The chest patch on her sailor top is art only. Forge/Oliver pick the crew.

## 1. Height and proportions (read from ref2, scaled against Caali G = 1.916 m)
- Anika's top of head reaches about Caali's eye/brow line in ref2, so target **1.68 m** (±0.03) in skates, about 1.60 m barefoot. Root scale stays 1.0, metres, Y up, facing +Z, same as the skeleton.
- Proportions: slim and long-legged. Crotch at about 0.49 × height, shoulder width about 0.36 m, head about 1/7 of height (stylised, a little larger than Caali's).
- Pigtails hang to about mid-thigh, roughly 0.60 m from the tie to the tip.
- Do NOT scale the skeleton to her. Mixamo retargets bone lengths, while the bind names and hierarchy stay shared.

## 2. Binding to the shared skeleton
Preferred route, **A: retarget onto the shared skeleton**
1. Forge delivers `anika/anika-rider.glb` in T-pose or A-pose (arms at 45°), with feet flat in the Treks, facing +Z and grounded at y=0. One mesh with material slots, POSITION as float, no quantization or meshopt.
2. In Blender 4.3.2, import rider-skeleton.blend. Snap the joints to her landmarks (hips, knees, ankles, shoulders, elbows, wrists, finger joints, neck and head) by editing bone heads and tails only. Names, parents and roll axes stay unchanged.
3. Parent with automatic weights, then fix the weights by hand (see section 4). The twist bones get a gradient: ForeArmTwist takes 0→0.5 from elbow to wrist, and ArmTwist takes the shoulder half.
4. Add the secondary chains (section 3) as extra bones under Head and Hips. These are allowed extras, and the poser ignores unknown bones.
5. Export a GLB with skin, then run `/workspace/tools/deinterleave.py`.

Fallback, **B: Mixamo auto-rig**. Upload the FBX, use 65 joints, and leave "symmetry" on. Then rename and reparent the result onto the shared bone list (rider-skeleton.bones.json): add the 4 twist bones, the AT_L/AT_R roots and the 20 sockets, and copy the weights across with a Data Transfer modifier. Use B only if A's auto-weights fail on her skirt and hair.

## 3. Secondary motion (procedural springs in ikki_skate.js, to add when her GLB lands)
- **Braided pigtails:** two chains, `Anika_BraidL_01..05` and `Anika_BraidR_01..05`, each rooted at the tie point on Head and about 0.12 m per bone.
  - Per bone, a damped spring on the world tip: k=60, damping ζ=0.35, root bones stiffer at k=90, with gravity and the inertia of root velocity.
  - Max swing: 70° at the root and 35° per link.
  - Collision: capsules on Neck, Spine2 (r 0.11), shoulders (r 0.07) and UpLegs (r 0.08). Push out and do not penetrate.
  - Cost is 10 bones of CPU per frame. Turn them off in `lite` and at LOD2 (frozen at rest).
- **Pleated skirt:** 6 bones `Anika_Skirt_00..05` radial around Hips (front, front-L, back-L, back, back-R, front-R), each 0.20 m long and pointing down.
  - Driven by procedural sway (spring k=80, ζ=0.5) plus a rule from the thighs: each bone's swing is pushed out by the UpLeg flex in its sector, with front bones following 0.6× hip flex. That keeps the skirt from clipping in crouch, kick or the polegrind crouch (hip flex up to −86°).
  - Collision against UpLeg capsules (r 0.085, padded 1 cm).
  - The gold chain is rigid on the Hips (weight 1.0). The gold trim follows the skirt bones.

## 4. Weight-painting notes
- **Thigh-highs:** 100% Leg/UpLeg as with skin. The sock top band is held to UpLeg only (no Hips bleed), so the top does not slide under deep crouch. The pink bows are rigid to UpLeg.
- **Skirt:** only skirt bones plus Hips, with no UpLeg weights on the skirt. The thigh rule handles clearance. The hem blends to at most 2 bones.
- **Neckerchief:** knot rigid to Spine2 and Neck at 0.6/0.4. The tails go to Spine2 with a light sway on the neck (no extra bones). The cropped top must not stretch over the midriff gap. Spine1 takes the waistline.
- **Braids:** the hair cap is 100% Head. Each braid segment uses at most 2 chain bones.
- **Hands and fingers:** clean knuckle creases, with one-ring falloff per phalanx. Elbows use the twist gradient so there is no candy-wrapper twisting.
- **Limits:** at most 4 weights per vertex, normalised. The Treks are 100% Foot, or the shared skate is attached (section 6).

## 5. LOD targets
- Player LOD0: 100–120k tris, weighted to face, hands and Treks.
- LOD1: 40k.
- LOD2: 15k, with braid and skirt bones frozen.
- All LODs share one skin and skeleton.

## 6. Skate fit, sockets and color slots
- Uses the shared black-shell `wardrobe/skates/at-skate-meshy.glb`, or the merged default on NPC paths, with the same mask shader.
- Her loadout: paint black, frame black/gold, wheel gold 0xffd700, glow gold 0xffd700, and a pink accent 0xff5fa2 on the jacket rim and UI.
- Mask mapping: R = paint, G = frame, B = wheel + glow (uCrewGlow 0xffd700, uGlowStrength 1.0).
- Sockets: the standard 10 per foot from the spec, unchanged.
- Fit: the Foot bone's ankle sits at the AT_L/AT_R root. Check that the Treks' heel line meets the skate's footbed (±5 mm), and that no thigh-high bow pokes into the cuff socket.

## 7. Feel row: PROPOSED, now in ikki_skate.js `RIDER_FEEL.anika`
`stance .95, crouch .95, armAbd 1.15, arm 'playful', kickSide Left, armSwing 1.25, spineSway 1.2, windup .85, release .85 (trick .92), landDepth .9, landRate 1.3, idleRate 1.25, idleAmp 1.15`
This is light, quick and springy, unlike Caali G's 0.70 windup with quiet arms. It stays within RIDER_JOINT_LIMITS and the 720°/s slew. Forge/Oliver to confirm.

## 8. Roster
- `SR_ROSTER.anika` is in patch_crew_quest.py: key 'anika', name 'Anika', **crew null (TBD)**, glow and wheel 0xffd700, accent 0xff5fa2, url `CHAR_BASE+'anika/anika-rider.glb'` (default path, since Forge hasn't published one).
- It is set to `available:false` until delivery. While false it is never fetched (no 404), and ?player=anika logs a console note and plays Caali G.
- On delivery, flip it to true and rebuild.

## 9. Acceptance checklist
- [ ] GLB exists, has float POSITION, no quantization, has been deinterleaved, and is under 3 MB.
- [ ] Skeleton has 91 shared joints plus 10 braid and 6 skirt bones. Names match bones.json and the bind pose matches the shared rest (±1 mm on shared joints after retarget).
- [ ] Height is 1.68 ±0.03 m and she stands on y=0 in skates.
- [ ] At most 4 weights per vertex. No candy-wrapper twisting at ±90° forearm roll. Clean knuckles at fist pose.
- [ ] No clipping between skirt and thighs or between braids and the body in crouch, kick, trick, wall ride, polegrind_top and polegrind_climb (hero render front and side).
- [ ] Gold wheel glow is on, with 1 skate draw. Her full-detail draws are ≤ the player budget of 5.
- [ ] LOD tris are at most 120k / 40k / 15k.
- [ ] Flip `SR_ROSTER.anika.available`. ?player=anika loads her with no console errors.
- [ ] Oliver signs off on the hero-standard shot.
