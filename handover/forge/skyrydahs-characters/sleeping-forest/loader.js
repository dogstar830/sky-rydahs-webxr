// Sky Rydah's — Sleeping Forest rider loader. Drop-in for sky-rydahs-v3.html:
//   import { loadRider, loadRiderFP } from './skyrydahs-characters/sleeping-forest/loader.js';
//   const rider = await loadRider(scene, 'skyrydahs-characters/sleeping-forest/sleeping-forest-rider.glb', crewColors, { vr });
//   const fp    = await loadRiderFP(scene, 'skyrydahs-characters/sleeping-forest/sleeping-forest-fp.glb', crewColors, { vr });
//   every frame: rider.userData.update(camera, dt, boost01)
// crewColors: slot keys or palette roles (primary/secondary/accent/trim/skin); see ../shared/rider_loader.js.
import { loadRider as base, loadRiderFP as baseFP } from '../shared/rider_loader.js';
export const DEFAULTS = { skin: 0xe8c4a8, hair: 0x1d4a36, jacket: 0xeef0ea, cloth: 0x123a2b, gold: 0x3fae6a, metal: 0xb9c2bb, skate: 0xd9ddd5, eyes: 0xffffff, iris: 0x3fd987, wheelGlow: 0x6dffa8, glow2: 0xa8ffd0, rim: 0x9effc8, shadow: 0x3e4f7a, outline: 0x061a10 };
export const OPTS = { slotRim: { hair: 0.3, skin: 0.2 } };
export const loadRider = (scene, url, crewColors = {}, opts = {}) => base(scene, url, crewColors, { defaults: DEFAULTS, crewName: 'Sleeping Forest', ...OPTS, ...opts });
export const loadRiderFP = (scene, url, crewColors = {}, opts = {}) => baseFP(scene, url, crewColors, { defaults: DEFAULTS, crewName: 'Sleeping Forest', ...OPTS, ...opts });
