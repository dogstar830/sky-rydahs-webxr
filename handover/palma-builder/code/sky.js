// ===== SKY DAY/NIGHT (sky.js, patch_sky.py). The sky sphere previously always drew the neon dusk gradient. It now follows the
// game's day state live. There is no single global flag, so the state is read from the same signals the day toggles set:
// FACADE.uniforms.uDay (FACADE.setDay) and scene.background luminance (the day toggles set a bright blue background, night is 0x120a2a).
// SKY.setDay(d) forces a value (pass null to go back to auto). Same sphere, same material: 0 new draw calls, one uniform.
// Day colours: skyrydahs-ref/beach-sky-palms-research.md section 2 (zenith #3A7BD5, mid #78AEE8, horizon #CFE3F2, sun #FFF6E0).
const SKY=(()=>{ const u={value:0}; let force=null, moonMat=null;
  function target(){ if(force!==null) return force; let d=0;
    if(typeof FACADE!=="undefined"&&FACADE.uniforms&&FACADE.uniforms.uDay) d=Math.max(d,FACADE.uniforms.uDay.value);
    const b=scene&&scene.background; if(b&&b.isColor){ const l=b.r*.3+b.g*.59+b.b*.11; d=Math.max(d,Math.min(1,Math.max(0,(l-.25)/.3))); }
    return d; }
  function tick(){ const t=target(); u.value+=(t-u.value)*.15; if(Math.abs(t-u.value)<.002) u.value=t;
    if(moonMat){ moonMat.opacity=1-u.value; moonMat.visible=u.value<.98; } }
  return { u, tick, hookMoon(m){ moonMat=m; }, setDay(d){ force=d; }, get day(){ return u.value; } };
})();
