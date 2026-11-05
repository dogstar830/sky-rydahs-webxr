// ===== WORLD_GROUND (Palma Builder, ground.js via patch_ground.py). Contract (Rydah Systems):
//   window.WORLD_GROUND(x, z, yHint) -> {y, nx, ny, nz, surf} | null      WORLD_GROUND.version = '1.0'
//   Returns the highest walkable surface whose top is <= yHint + 0.6 (stacked levels resolve by yHint; yHint undefined -> 0).
//   surf: asphalt | concrete | wood | metal | grass | sand | water. null = no data (outside the map).
// Data = analytic copies of what world.js / details.js / bridges.js / blockout.js RENDER (tops measured by raycast, +-3 cm),
// bucketed in an 8 m spatial hash at first call. No raycasts at runtime. Every surface rendered today is level (normal 0,1,0):
// bridge decks are flush with the ground (deck top 0.01 = ground top 0.01, so no approach ramp exists), the Dash road is
// rendered flat (top 0.035), and the underpass deck (top 6.80) has no ramps (reachable from the air only). See plan in report.
// Helpers kept as properties: at(x,z), heightAt(x,z,yHint), surfAt(x,z,yHint), decks, entries, cell.
const WORLD_GROUND=(()=>{
  const CELL=8, H=new Map(), E=[]; let ready=false;
  const GROUND_Y=0.01, WATER_Y=-2.5;                     // asphaltGround / Heights grass top; water plane (createWaterFX)
  // entry: axis rect {k:0,x0,z0,x1,z1,y,s} | oriented rect {k:1,cx,cz,ux,uz,hl,hw,y,s} | capsule polyline seg {k:2,ax,az,bx,bz,r,y,s}
  function add(e,bx0,bz0,bx1,bz1){ E.push(e); for(let i=Math.floor(bx0/CELL);i<=Math.floor(bx1/CELL);i++) for(let j=Math.floor(bz0/CELL);j<=Math.floor(bz1/CELL);j++){ const k=i*4096+j; let L=H.get(k); if(!L) H.set(k,L=[]); L.push(e); } }
  const rect=(x0,z0,x1,z1,y,s)=>add({k:0,x0,z0,x1,z1,y,s},x0,z0,x1,z1);
  function orect(cx,cz,ang,hw,hl,y,s){ const ux=Math.sin(ang), uz=Math.cos(ang), ex=Math.abs(ux)*hl+Math.abs(uz)*hw, ez=Math.abs(uz)*hl+Math.abs(ux)*hw; add({k:1,cx,cz,ux,uz,hl,hw,y,s},cx-ex,cz-ez,cx+ex,cz+ez); }
  function caps(ax,az,bx,bz,r,y,s){ add({k:2,ax,az,bx,bz,r,y,s},Math.min(ax,bx)-r,Math.min(az,bz)-r,Math.max(ax,bx)+r,Math.max(az,bz)+r); }
  const LAND=[]; // base layer: [x0,z0,x1,z1,y,surf]
  function wgInit(){ if(ready) return; ready=true;
    for(const i of PALMA.islands){ const b=i.box; LAND.push([b[0]-4,b[1]-4,b[2]+4,b[3]+4,GROUND_Y,i.id==="north"?"grass":"asphalt"]); }
    // sidewalks + curbs (details.js det("walk"): box top 0.14)
    for(const k in DET){ if(k.split("|")[0]!=="walk") continue; for(const p of DET[k]){ const t=p[1]+p[4]/2; rect(p[0]-p[3]/2,p[2]-p[5]/2,p[0]+p[3]/2,p[2]+p[5]/2,t,"concrete"); } }
    rect(-240,-100,-206,10,0.02,"sand");                                   // Cove beach flat (34 x 110, y .02)
    // bridge decks (createBridge: 8 m deck, L+16 long, top 0.01; parapet band +-4.15..4.55 not walkable -> excluded via onLand corridor)
    G.decks=[]; for(const br of PALMA.bridges){ const [ax,az]=br.a,[bx,bz]=br.b, L=Math.hypot(bx-ax,bz-az); G.decks.push({id:br.id,a:br.a.slice(),b:br.b.slice(),y:0.01,halfLane:3.4,halfWalk:3.8,ends:8,surf:"concrete"});
      orect((ax+bx)/2,(az+bz)/2,Math.atan2(bx-ax,bz-az),4,L/2+8,0.01,"concrete"); }
    if(typeof BLOCKOUT!=="undefined"){ const A=BLOCKOUT.areas||{};
      if(A.beach){ const [x0,,x1,zE]=A.beach.box; LAND.push([x0-2,198,x1+2,zE,0,"sand"]);
        rect(x0,A.beach.road[0],x1,A.beach.road[1],0.02,"asphalt"); rect(x0,A.beach.walk[0],x1,A.beach.walk[1],0.10,"concrete"); rect(x0+4,A.beach.boardwalk[0],x1-4,A.beach.boardwalk[1],0.08,"wood"); }
      if(A.port){ const a=A.port.apron; LAND.push([a[0],a[1],a[2]+2,a[3],0,"concrete"]); }
      if(A.causeway_underpass){ const u=A.causeway_underpass, b=PALMA.bridges.find(q=>q.id==="causeway"), ang=Math.atan2(b.b[0]-b.a[0],b.b[1]-b.a[1]);
        orect(u.centre[0],u.centre[1],ang+Math.PI/2,u.deck[1]/2,u.deck[0]/2,6.8,"concrete"); }
      const P=BLOCKOUT.dashPath; if(P) for(let i=0;i<P.length-1;i++) caps(P[i][0],P[i][1],P[i+1][0],P[i+1][1],3.66,0.035,"asphalt"); } }
  function hit(e,x,z){ if(e.k===0) return x>=e.x0&&x<=e.x1&&z>=e.z0&&z<=e.z1;
    if(e.k===1){ const dx=x-e.cx, dz=z-e.cz; return Math.abs(dx*e.ux+dz*e.uz)<=e.hl&&Math.abs(dx*e.uz-dz*e.ux)<=e.hw; }
    const vx=e.bx-e.ax, vz=e.bz-e.az, l2=vx*vx+vz*vz||1; let t=((x-e.ax)*vx+(z-e.az)*vz)/l2; t=t<0?0:t>1?1:t; const qx=e.ax+vx*t-x, qz=e.az+vz*t-z; return qx*qx+qz*qz<=e.r*e.r; }
  const OUT={y:0,nx:0,ny:1,nz:0,surf:""};
  function G(x,z,yHint){ wgInit(); const lim=(yHint==null?0:yHint)+0.6; let by=-1e9, bs=null;
    const L=H.get(Math.floor(x/CELL)*4096+Math.floor(z/CELL)); if(L) for(let i=0;i<L.length;i++){ const e=L[i]; if(e.y<=lim&&e.y>by&&hit(e,x,z)){ by=e.y; bs=e.s; } }
    if(bs===null){ for(let i=0;i<LAND.length;i++){ const b=LAND[i]; if(x>b[0]&&x<b[2]&&z>b[1]&&z<b[3]&&b[4]>by){ by=b[4]; bs=b[5]; } }
      if(bs===null){ if(x<-420||x>420||z<-460||z>320) return null; by=WATER_Y; bs="water"; } }
    return {y:by,nx:0,ny:1,nz:0,surf:bs}; }
  G.version="1.0"; G.cell=CELL; G.entries=E; G.decks=[];
  G.at=(x,z,yh)=>G(x,z,yh); G.heightAt=(x,z,yh)=>{ const r=G(x,z,yh); return r?r.y:null; }; G.surfAt=(x,z,yh)=>{ const r=G(x,z,yh); return r?r.surf:null; };
  G.init=wgInit; return G;
})();
window.WORLD_GROUND=WORLD_GROUND;
