// Sky Rydah's — Tool Toul To rider loader. Drop-in for sky-rydahs-v3.html:
//   import { loadRider, loadRiderFP } from './skyrydahs-characters/tool-toul-to/loader.js';
//   const rider = await loadRider(scene, 'skyrydahs-characters/tool-toul-to/tool-toul-to-rider.glb', crewColors, { vr });
//   const fp    = await loadRiderFP(scene, 'skyrydahs-characters/tool-toul-to/tool-toul-to-fp.glb', crewColors, { vr });
//   every frame: rider.userData.update(camera, dt, boost01)
// crewColors: slot keys or palette roles (primary/secondary/accent/trim/skin); see ../shared/rider_loader.js.
import { loadRider as base, loadRiderFP as baseFP } from '../shared/rider_loader.js';
export const DEFAULTS = { skin: 0xd2a07c, hair: 0x3a2a22, jacket: 0x6b6f74, cloth: 0x4a4d52, gold: 0xb8501e, metal: 0xa7adb3, skate: 0x8a3a1a, eyes: 0xffffff, iris: 0xff7a2a, wheelGlow: 0xff6a1a, glow2: 0xffb040, rim: 0xff8a3a, shadow: 0x4a3f6a, outline: 0x0a0705 };
export const OPTS = { slotRim: { hair: 0.3, skin: 0.2 } };
export const loadRider = (scene, url, crewColors = {}, opts = {}) => base(scene, url, crewColors, { defaults: DEFAULTS, crewName: 'Tool Toul To', ...OPTS, ...opts });
export const loadRiderFP = (scene, url, crewColors = {}, opts = {}) => baseFP(scene, url, crewColors, { defaults: DEFAULTS, crewName: 'Tool Toul To', ...OPTS, ...opts });
