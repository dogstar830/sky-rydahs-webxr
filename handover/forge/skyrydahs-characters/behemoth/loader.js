// Sky Rydah's — Behemoth rider loader. Drop-in for sky-rydahs-v3.html:
//   import { loadRider, loadRiderFP } from './skyrydahs-characters/behemoth/loader.js';
//   const rider = await loadRider(scene, 'skyrydahs-characters/behemoth/behemoth-rider.glb', crewColors, { vr });
//   const fp    = await loadRiderFP(scene, 'skyrydahs-characters/behemoth/behemoth-fp.glb', crewColors, { vr });
//   every frame: rider.userData.update(camera, dt, boost01)
// crewColors: slot keys or palette roles (primary/secondary/accent/trim/skin); see ../shared/rider_loader.js.
import { loadRider as base, loadRiderFP as baseFP } from '../shared/rider_loader.js';
export const DEFAULTS = { skin: 0xa8765a, hair: 0x18161a, jacket: 0x222226, cloth: 0x2b2a2e, gold: 0xff7a12, metal: 0xd6dbe2, skate: 0x2c2c30, eyes: 0xffffff, iris: 0xff8a20, wheelGlow: 0xff7a12, glow2: 0xffa040, rim: 0xff8a20, shadow: 0x4a3f7a, outline: 0x080608 };
export const OPTS = { slotRim: { hair: 0.3, skin: 0.2 } };
export const loadRider = (scene, url, crewColors = {}, opts = {}) => base(scene, url, crewColors, { defaults: DEFAULTS, crewName: 'Behemoth', ...OPTS, ...opts });
export const loadRiderFP = (scene, url, crewColors = {}, opts = {}) => baseFP(scene, url, crewColors, { defaults: DEFAULTS, crewName: 'Behemoth', ...OPTS, ...opts });
