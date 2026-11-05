// ===== BRIDGES: full-structure pass (refs: skyrydahs-ref/bridges-research.md — Hathaway segmental box, DuPont multi-beam bents,
// Sunshine Skyway / Dames Point cable-stayed, Golden Gate suspension). Additive only: createBridge() and its cable LineSegments
// (= grind splines via grindBridgeSeg) are untouched. Coarse parts go into the global INST pools (0 new draw calls);
// fine parts (bearings, cable bands, stay anchors, cable lights) go into one toon + one glow InstancedMesh per bridge,
// LOD-culled by camera distance (<=2 extra calls per nearby bridge). Concrete is pale buff-grey (Hathaway photo), night accents
// are the bridge's crew colour (deck-edge strips, tower uplights, cable lights) plus Hathaway-style blue pier uplights.
const BRIDGES=(()=>{
  const CONC=0x85847f, CONC2=0x74736e, STEEL=0x6d737c, PARA=0x9b9890, BLUE=0x3D7BFF, AMBER=0xffd9a0, RED=0xff2a20, GREEN=0x2aff6a;
  const list=[], fineLOD=170; let day=0;
  function build(b){
    const [ax,az]=b.a, [bx,bz]=b.b, L=Math.hypot(bx-ax,bz-az), ang=Math.atan2(bx-ax,bz-az), mx=(ax+bx)/2, mz=(az+bz)/2;
    const ux=Math.sin(ang), uz=Math.cos(ang), px=uz, pz=-ux, E=L/2+8;
    const W=(lx,lz)=>[mx+px*lx+ux*lz, mz+pz*lx+uz*lz];
    const I=(k,lx,y,lz,sx,sy,sz,c)=>{ const [x,z]=W(lx,lz); inst(k,x,y,z,sx,sy,sz,c,0,ang,0); };
    const F=[], G=[]; const f=(lx,y,lz,sx,sy,sz,c)=>F.push([...W(lx,lz),y,sx,sy,sz,c]), gl=(lx,y,lz,s,c)=>G.push([...W(lx,lz),y,s,s,s,c]);
    // existing piers -> concrete (createBridge pushes them as 3x11x3 boxes at y=-6)
    for(const p of INST.box||[]) if(p[1]===-6&&p[4]===11&&p[6]===0x3a3d4a&&Math.abs((p[0]-mx)*px+(p[2]-mz)*pz)<.5) p[6]=CONC;
    // existing parapets/deck in the bridge group -> FDOT-style light concrete parapet
    for(const o of scene.children) if(o.isGroup&&Math.abs(o.position.x-mx)<.01&&Math.abs(o.position.z-mz)<.01&&Math.abs(o.rotation.y-ang)<1e-4)
      o.traverse(m=>{ if(m.isMesh&&m.geometry.parameters&&m.geometry.parameters.height===.8&&m.geometry.parameters.width===.4) m.material=toon(PARA); });
    // superstructure: 4 precast girders + fascia + diaphragms every 8 m (DuPont-style multi-beam; Hathaway box reads the same from the water)
    for(const lx of [-3,-1,1,3]) I("box",lx,-1.15,0,.55,.75,2*E,CONC);
    for(const sd of [-1,1]){ I("box",sd*4.05,-.5,0,.14,.75,2*E,CONC2); I("glow",sd*4.13,-.82,0,.05,.09,2*E,b.color); } // deck-edge neon strip
    for(let lz=-E+4;lz<E;lz+=8) I("box",0,-1.1,lz,7.4,.5,.25,CONC2);
    // substructure at each existing pier: hammerhead cap, bearings, pile cap at waterline, blue uplight (Hathaway)
    for(let t=-L/2+10;t<L/2-5;t+=16){ I("box",0,-1.85,t,9,.7,2.2,CONC); I("box",0,-2.35,t,5,.5,5,CONC2);
      for(const lx of [-3,-1,1,3]) f(lx,-1.53,t,.6,.12,.6,0x2b2b2b);
      for(const sd of [-1,1]){ gl(sd*1.9,-2.0,t-1.9,.3,BLUE); const [x,z]=W(sd*1.9,t-1.9); halo(x,-1.3,z,BLUE,10); } }
    // channel dolphins (Skyway-style ship-impact protection) at the two mid piers
    let tm=-L/2+10; while(tm+16<0) tm+=16; for(const t of [tm,tm+16]) if(t<L/2-5) for(const sd of [-1,1]){ I("cyl",sd*7,-1.9,t,2.4,1.4,2.4,CONC2); gl(sd*7,-1.05,t,.3,sd<0?RED:GREEN); }
    // abutments + wing walls + approach ramp lip at both ends
    for(const e of [-1,1]){ I("box",0,-1.6,e*(E-.6),9.4,2.4,1.4,CONC); for(const sd of [-1,1]) I("box",sd*4.75,-1.4,e*(E-3),.5,2.8,5,CONC2); }
    // lamp mast arms + luminaire heads on the existing 30 m poles
    for(let lz=-L/2;lz<=L/2;lz+=30) for(const sd of [-1,1]){ I("box",sd*3.5,7.95,lz,1.5,.12,.12,STEEL); I("glow",sd*2.85,7.85,lz,.55,.12,.28,AMBER); }
    if(b.id==="causeway"){ // suspension: towers at +-T, H=26 (createBridge); anchorages at cable ends, pedestals, saddles, bands, lights
      const T=L*.28, H=26;
      for(const e of [-1,1]){ I("box",0,-2.2,e*T,12,1,4,CONC2); for(const sd of [-4.6,4.6]){ I("box",sd,-1.2,e*T,1.3,2.4,1.3,CONC); I("box",sd,H+.25,e*T,1.5,.6,2.2,STEEL);
          gl(sd,H+.75,e*T,.35,RED); const [x,z]=W(sd,e*T); halo(x,.6,z,b.color,9); halo(x,H+.8,z,RED,4); gl(sd*1.12,.5,e*T,.4,b.color); } }
      for(const e of [-1,1]) for(const sd of [-4.9,4.9]) I("box",sd,.3,e*(E-1.5),1.6,2.2,4,CONC);
      for(const sd of [-4.6,4.6]) for(let lz=-E;lz<=E+.01;lz+=2){ const y=Math.abs(lz)<=T? 3+(H-3)*(lz*lz)/(T*T) : H-(Math.abs(lz)-T)/(E-T)*(H-1);
        if(Math.abs(lz)<T&&Math.round(lz)%6===0) f(sd,y,lz,.55,.45,.55,STEEL);                       // cable bands at hangers
        if(Math.round(lz)%4===0) gl(sd*1.04,y-.32,lz,.22,b.color); }                                 // cable lights (offset, never on the spline)
    } else { // cable-stayed: single inverted-Y pylon (createBridge); footing, leg stubs, anchor heads, stay anchors + lights
      const H=Math.round(L*.38);
      I("box",0,-2.2,0,13,.8,5,CONC2); for(const sd of [-4.6,4.6]) I("box",sd,-1.2,0,1.1,2.4,1.1,CONC);
      I("box",0,H+.3,0,1.5,.6,1.5,STEEL); gl(0,H+.8,0,.4,RED); { const [x,z]=W(0,0); halo(x,H+.8,z,RED,5); halo(x,.8,z,b.color,12); for(const sd of [-4.6,4.6]){ const [x2,z2]=W(sd,0); halo(x2,.5,z2,b.color,8); } }
      for(let lz=6;lz<L/2+6;lz+=6) for(const e of [-1,1]) for(const sd of [-4.2,4.2]){ const ty=H*.68+Math.min(lz,40)*.12*H/40;
        f(sd,.45,e*lz,.45,.5,.7,STEEL); gl(sd*1.06,.95,e*lz,.18,b.color);
        for(const t of [.3,.6]) gl(sd*(1-t)+Math.sign(sd)*.3,(.4+(ty-.4)*t)-.3,e*lz*(1-t),.2,b.color); }      // lights hung just below each stay
      for(let k=0;k<6;k++) f(0,H*.7+k*H*.05,0,1.5,.3,1.5,STEEL);                                         // stay anchor heads in pylon
    }
    list.push({b,mx,mz,L,F,G});
  }
  function finish(){ // after buildInstances: one toon + one glow InstancedMesh per bridge, distance LOD
    const geo=new THREE.BoxGeometry(1,1,1), mt=makeToonMat({color:0xffffff}), mg=new THREE.MeshBasicMaterial({color:0xffffff});
    const m=new THREE.Matrix4(), q=new THREE.Quaternion(), e=new THREE.Euler(), v=new THREE.Vector3(), s=new THREE.Vector3(), c=new THREE.Color();
    for(const r of list){ const ang=Math.atan2(r.b.b[0]-r.b.a[0],r.b.b[1]-r.b.a[1]); r.meshes=[];
      for(const [arr,mat] of [[r.F,mt],[r.G,mg]]){ if(!arr.length) continue; const im=new THREE.InstancedMesh(geo,mat,arr.length);
        arr.forEach((p,i)=>{ q.setFromEuler(e.set(0,ang,0)); m.compose(v.set(p[0],p[2],p[1]),q,s.set(p[3],p[4],p[5])); im.setMatrixAt(i,m); im.setColorAt(i,c.set(p[6])); });
        im.userData.glow=mat===mg; scene.add(im); r.meshes.push(im); } }
    const _bv=new THREE.Vector3(); animated.push(()=>{ if(typeof camera==="undefined") return; const cp=camera.getWorldPosition(_bv);
      for(const r of list){ const near=Math.hypot(cp.x-r.mx,cp.z-r.mz)<fineLOD+r.L*.5; for(const im of r.meshes) im.visible=near&&!(im.userData.glow&&day>.5); } });
  }
  return { build, finish, list, setDay(d){ day=d; } };
})();
