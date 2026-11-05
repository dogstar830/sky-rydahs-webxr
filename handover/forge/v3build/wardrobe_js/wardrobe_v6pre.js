// ===== Modular wardrobe (shared Meshy skeleton + shared base body; one GLB per piece under wardrobe/<slot>/<item>.glb) =====
// Presets are baked offline (wardrobe_build/assemble_rider.py) into ONE skinned mesh/LOD + one atlas -> 1 draw call per rider.
// Runtime API (rider.userData.wardrobe): equip(slot,item|url) / unequip(slot) / outfit() / apply(str|obj) / presets.
//  * a baked piece can be hidden per-vertex (uHide, _slot attribute); covered body skin is discarded (uCover, body _bm bitmask)
//  * a runtime-equipped piece is its own SkinnedMesh bound by bone name to the rider's skeleton (+1 draw call until re-baked)
//  URL: ?outfit=caali  |  ?outfit=jacket:caali_bomber,hair:none  |  ?outfit=ikki+jacket:caali_bomber   (applied to the player)
const WARDROBE={ base:CHAR_BASE+'wardrobe/', slots:['hair','head','top','jacket','pants','gloves','neck','accessory','skates'],
  presets:{ caali:{hair:'caali_curly_short',top:'caali_gr8yzone_tee',jacket:'caali_bomber',pants:'caali_cargo',gloves:'caali_fingerless',neck:'gold_chain_thick',accessory:'gold_pants_chains',skates:'at-skate-meshy'},
            ikki:{skates:'at-skate-meshy'} },   // Ikki = monolithic Meshy body (own clothes); wardrobe pieces layer on top
  bit(s){ return 1<<this.slots.indexOf(s); }, url(slot,item){ return /[\/.]/.test(item)?item:this.base+slot+'/'+item+'.glb'; },
  parse(str){ const o={}; let pre=null; for(const tok of String(str||'').split(/[+,]/).map(t=>t.trim()).filter(Boolean)){ const [k,v]=tok.split(':'); if(v===undefined){ if(this.presets[k]) pre=k; } else o[k]=(v==='none'||v==='')?null:v; } return {preset:pre,items:o}; } };
// riders built on the wardrobe pipeline (baked GLB + rider identity). AT skate is the same Meshy module for everyone; only glow/paint/frame differ.
const WARDROBE_RIDERS={ caali:{ name:'Caali G', crew:'codee', url:CHAR_BASE+'wardrobe/riders/caali-g.glb', baked:'caali', fx:0, key:'caali-g',
  glow:0xffd700, loadout:{paint:0x2a2620, frame:0xd4a017, wheel:0xffffff}, frameLift:2.4, envI:.6, noNormal:true, defaults:{rim:0xffc940} } };
function wardrobeAttach(root,ctx){ const {host,mat,bones,cover,hide,baked}=ctx, live={}, worn=Object.assign({},baked);
  const strip=n=>n.replace(/^mixamorig:?/,'');
  const recompute=()=>{ let hm=0, cm=0; for(const s of WARDROBE.slots){ if(baked[s]&&(worn[s]!==baked[s])) hm|=WARDROBE.bit(s); if(worn[s]&&s!=='skates') cm|=WARDROBE.bit(s); } hide.value=hm; cover.value=cm; };
  const api={ presets:WARDROBE.presets, outfit:()=>Object.assign({},worn), live,
    async equip(slot,item){ if(!WARDROBE.slots.includes(slot)) throw new Error('unknown slot '+slot); if(slot==='skates') return; // AT module is fixed; use setLoadout() for glow/paint/frame
      if(!item) return api.unequip(slot); if(live[slot]){ live[slot].parent.remove(live[slot]); delete live[slot]; }
      worn[slot]=item; if(baked[slot]===item){ recompute(); return; }   // baked piece: just un-hide
      const g=await new Promise((res,rej)=>new THREE.GLTFLoader().load(WARDROBE.url(slot,item),res,undefined,rej)); let sm=null;
      g.scene.traverse(o=>{ if(o.isSkinnedMesh&&(/LOD0/.test(o.name)||!sm)) sm=o; }); if(!sm) throw new Error('no skinned mesh in '+item);
      const bl=sm.skeleton.bones.map(b=>bones[strip(b.name)]); if(bl.some(b=>!b)) throw new Error(item+': skeleton mismatch');
      const m=new THREE.SkinnedMesh(sm.geometry,new THREE.MeshStandardMaterial({map:sm.material.map,normalMap:sm.material.normalMap,roughnessMap:sm.material.roughnessMap,metalnessMap:sm.material.metalnessMap,
        roughness:sm.material.roughnessMap?1:sm.material.roughness,metalness:sm.material.metalnessMap?(slot==='neck'||slot==='accessory'?1:.15):sm.material.metalness,skinning:true,envMap:mat.envMap,envMapIntensity:1.1}));
      m.position.copy(sm.position); m.quaternion.copy(sm.quaternion); m.scale.copy(sm.scale); m.frustumCulled=false; m.name='wardrobe_'+slot+'_'+item;
      host.add(m); m.bind(new THREE.Skeleton(bl,sm.skeleton.boneInverses),sm.bindMatrix); live[slot]=m; recompute(); return m; },
    unequip(slot){ if(slot==='skates') return; if(live[slot]){ live[slot].parent.remove(live[slot]); delete live[slot]; } worn[slot]=null; recompute(); },
    async apply(spec){ const p=typeof spec==='string'?WARDROBE.parse(spec):{preset:spec.preset||null,items:spec.items||spec};
      if(p.preset){ const P=WARDROBE.presets[p.preset]; for(const s of WARDROBE.slots) if(s!=='skates'&&(P[s]||null)!==(worn[s]||null)) await api.equip(s,P[s]||null); }
      for(const [s,v] of Object.entries(p.items)) await api.equip(s,v); return api.outfit(); } };
  recompute(); return api; }
