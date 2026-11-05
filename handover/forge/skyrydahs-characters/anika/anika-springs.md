# Anika spring bones (Rydah Rigger, 2026-10-30)
These live in anika-rider*.glb and anika-npc*.glb as extra joints after the 91 shared joints (joints 91..106). Bone axis is +Y (head to tail). Each node has extras.spring {chain,index,kind,tail}, and skin.extras.springChains holds the solver params.
- Anika_BraidL_01..05 and Anika_BraidR_01..05: parent chain mixamorig:Head -> _01 -> ... -> _05. Each chain is about 0.18 m (the braids reach the chest, not mid-thigh as the plan assumed), so the bones are about 0.036 m each. Plan params: k 60 (root 90), damping 0.35, max swing 70/35 deg, collide with Neck, Spine2 r.11, shoulders r.07, UpLegs r.08.
- Anika_Skirt_00..05: parent mixamorig:Hips. 00 front, 01 front-L, 02 back-L, 03 back, 04 back-R, 05 front-R, pointing down from the waistband to the hem. k 80, damping 0.5, thigh push-out rule, UpLeg capsules r .085.
- Find them with name.replace(/^mixamorig:?/,'') and the regex /^Anika_(Braid[LR]|Skirt)_\d\d$/. The GLTFLoader keeps these names unchanged.
- LOD0, LOD1 and LOD2 all carry the braid and skirt chain weights (LOD2 is no longer folded into Head/Hips).
- Forge split the braids from the top. Braid verts are weighted to their Braid chain + Head only (no body bones), and the leftover braid-to-collar bridge triangles were removed, so a spring swing does not drag the collar. Braid tips can still clip the chest in deep crouch (accepted for now).


## Update 03:25 CDT
- Springs are weighted on LOD0, LOD1 and LOD2 (LOD2 no longer folded). Split braids are Braid chain + Head only. Skirt springs on LOD2 have been re-sprung.
- Collar-bridging triangles between braids and top were removed (rider 215/135/46, npc 104/54/22 per LOD).
- Without a spring solver the braids are rigid to Head. In a deep crouch the tips swing into the chest.

## Runtime solver (21:35 CDT)
- The poser now runs a generic spring solver, `riderSpringsInstall()` in ikki_skate.js. It reads each bone's `userData.spring` (glTF node extras) and runs after pose()+plant() when the camera is within 12 m. It adds no draws.
- Defaults by kind: braid stiffness 60, damping .3, gravity 1, drag .3, swing 70/35°; skirt 90/.45/.5/.4, swing 40°. Per-bone extras (`stiffness`, `damping`, `gravity`, `drag`, `maxSwing`, `maxLink`) override them.
- Gravity is relative to the bind, so the rest pose is the equilibrium. Colliders: hips, chest, 2 per thigh and 1 per shin, plus the deck plane. A collider radius is capped at the rest distance, so nothing starts inside one.
- The skirt sectors are siblings under Hips, so each one is a 1-bone chain.
