// Sky Rydah's — Genesis rider loader. Drop-in for sky-rydahs-v3.html:
//   import { loadRider, loadRiderFP } from './skyrydahs-characters/genesis/loader.js';
//   const rider = await loadRider(scene, 'skyrydahs-characters/genesis/genesis-rider.glb', crewColors, { vr });
//   const fp    = await loadRiderFP(scene, 'skyrydahs-characters/genesis/genesis-fp.glb', crewColors, { vr });
//   every frame: rider.userData.update(camera, dt, boost01)
// crewColors: slot keys or palette roles (primary/secondary/accent/trim/skin); see ../shared/rider_loader.js.
import { loadRider as base, loadRiderFP as baseFP } from '../shared/rider_loader.js';
export const DEFAULTS = { skin: 0xc58c6a, hair: 0x2a0f22, jacket: 0xd0158a, cloth: 0x161218, gold: 0xffc83a, metal: 0xe8d6a0, skate: 0xf2eee6, eyes: 0xffffff, iris: 0xff3cb4, wheelGlow: 0xff2fae, glow2: 0xffd36a, rim: 0xffb3e6, shadow: 0x5a2f7a, outline: 0x14040e };
export const OPTS = { slotRim: { hair: 0.3, skin: 0.2 } };
export const loadRider = (scene, url, crewColors = {}, opts = {}) => base(scene, url, crewColors, { defaults: DEFAULTS, crewName: 'Genesis', ...OPTS, ...opts });
export const loadRiderFP = (scene, url, crewColors = {}, opts = {}) => baseFP(scene, url, crewColors, { defaults: DEFAULTS, crewName: 'Genesis', ...OPTS, ...opts });
