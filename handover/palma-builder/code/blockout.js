// ===== BLOCKOUT (Palma Builder, blockout.js via patch_blockout.py): realism step 1 additions as grey-box/mid-detail =====
// Refs: skyrydahs-ref/realism-heat-mapping-research.md §2.4, blockout-research notes in skyrydahs-ref/blockout-research.md.
// Visuals go into the global INST pools (box/cyl/glow/frond) before buildInstances() -> 0 new draw calls (+2 canvas signs).
// Gameplay additions are DEFERRED and ADDITIVE: new colliders, new walkable land and new grind splines are appended only after
// TURF, GRAF and GRIND are fully built, so every existing collider / grind spline / graffiti spot / turf spot keeps its index and
// value. No rnd()/Math.random here (keeps the world rnd sequence and seeded layouts identical).
const PYLON_FIX=[[[46.376, -135.168, 47.776, -133.768], [46.611, -134.934, 47.541, -134.003]], [[40.824, -127.832, 42.224, -126.432], [41.059, -127.597, 41.989, -126.667]], [[-57.224, -213.568, -55.824, -212.168], [-56.989, -213.333, -56.059, -212.403]], [[-62.776, -206.232, -61.376, -204.832], [-62.541, -205.997, -61.611, -205.066]], [[128.452, 161.321, 129.852, 162.721], [128.522, 161.391, 129.782, 162.651]], [[130.148, 152.279, 131.548, 153.679], [130.218, 152.349, 131.478, 153.609]], [[223.723, -171.964, 225.123, -170.564], [223.849, -171.838, 224.997, -170.69]], [[214.877, -169.436, 216.277, -168.036], [215.003, -169.31, 216.151, -168.162]]];
const boWorldB=()=>B; // world building arrays (shadowed by the box helper inside BLOCKOUT)
const BLOCKOUT=(()=>{
  const S={live:false, cols:[], land:[], rails:{}, railDefs:[], areas:{}, warn:[]};
  const ASPH=0x2c2e35, LINE=0xe8e8e0, YEL=0xe8b830, CONC=0x8e8c86, CONC2=0x74736e, SAND=0xEDE8DC, WOOD=0x8a6a48, STEEL=0x6d737c;
  const B=(x,y,z,sx,sy,sz,c,ry)=>inst("box",x,y,z,sx,sy,sz,c,0,ry||0,0), GL=(x,y,z,sx,sy,sz,c,ry)=>inst("glow",x,y,z,sx,sy,sz,c,0,ry||0,0);
  const CY=(x,y,z,r,h,c)=>inst("cyl",x,y,z,r*2,h,r*2,c);
  const col=(x0,z0,x1,z1,tag)=>S.cols.push({minX:Math.min(x0,x1),maxX:Math.max(x0,x1),minZ:Math.min(z0,z1),maxZ:Math.max(z0,z1),bo:tag});
  const BO_RAIL_MIN=.09; // grind.py: ride radius >= 8 cm; we ship 9 cm, and render a steel tube of that radius on the spline
  const rail=(id,pts,r,kind)=>{ r=Math.max(r||BO_RAIL_MIN,BO_RAIL_MIN); S.railDefs.push({id,pts,r,kind:kind||"rail"});
    for(let i=0;i<pts.length-1;i++){ const a=pts[i],b=pts[i+1], L=Math.hypot(b[0]-a[0],b[2]-a[2]); if(L<.01) continue; B((a[0]+b[0])/2,(a[1]+b[1])/2,(a[2]+b[2])/2,r*2,r*2,L+r*2,STEEL,Math.atan2(b[0]-a[0],b[2]-a[2])); } };
  const seg=(ax,az,bx,bz,w,y,h,c,glow)=>{ const L=Math.hypot(bx-ax,bz-az); if(L<.01) return; (glow?GL:B)((ax+bx)/2,y,(az+bz)/2,w,h,L,c,Math.atan2(bx-ax,bz-az)); };
  // ---- free-space test against world colliders + placed props (DET) so blockouts never sit on existing stuff ----
  let PROPS=null;
  const props=()=>{ if(PROPS) return PROPS; PROPS=[]; for(const k in DET){ const kind=k.split("|")[0]; if(kind==="walk"||kind==="glow") continue; for(const p of DET[k]) PROPS.push(p); } return PROPS; };
  function clear(x0,z0,x1,z1,pad){ pad=pad||0;
    for(const c of colliders){ if(c.off) continue; if(x1+pad>c.minX&&x0-pad<c.maxX&&z1+pad>c.minZ&&z0-pad<c.maxZ) return false; }
    for(const c of S.cols){ if(x1+pad>c.minX&&x0-pad<c.maxX&&z1+pad>c.minZ&&z0-pad<c.maxZ) return false; }
    for(const p of props()){ if(p[0]>x0-pad&&p[0]<x1+pad&&p[2]>z0-pad&&p[2]<z1+pad) return false; }
    for(const g of PALMA.garages) if(g.pos[0]>x0-14&&g.pos[0]<x1+14&&g.pos[1]>z0-14&&g.pos[1]<z1+14) return false;
    return true; }
  function propsIn(x0,z0,x1,z1){ let n=0; for(const p of props()) if(p[0]>x0-.5&&p[0]<x1+.5&&p[2]>z0-.5&&p[2]<z1+.5) n++; return n; }
  function colClear(x0,z0,x1,z1,pad){ for(const c of colliders){ if(c.off) continue; if(x1+pad>c.minX&&x0-pad<c.maxX&&z1+pad>c.minZ&&z0-pad<c.maxZ) return false; }
    for(const c of S.cols){ if(x1+pad>c.minX&&x0-pad<c.maxX&&z1+pad>c.minZ&&z0-pad<c.maxZ) return false; }
    for(const g of PALMA.garages) if(g.pos[0]>x0-14&&g.pos[0]<x1+14&&g.pos[1]>z0-14&&g.pos[1]<z1+14) return false; return true; }
  function findSpot(cx,cz,w,d,R,pad,box){ let best=null; for(let r=0;r<=R;r+=2) for(let a=0;a<Math.max(1,r*2);a++){ const t=a/Math.max(1,r*2)*Math.PI*2, x=Math.round(cx+Math.cos(t)*r), z=Math.round(cz+Math.sin(t)*r);
      if(box&&(x-w/2<box[0]||x+w/2>box[2]||z-d/2<box[1]||z+d/2>box[3])) continue; if(!colClear(x-w/2,z-d/2,x+w/2,z+d/2,pad)) continue;
      const n=propsIn(x-w/2,z-d/2,x+w/2,z+d/2), sc=n*25+r; if(!best||sc<best[2]) best=[x,z,sc,n]; }
    if(best) S.warn.push("spot "+best.join(",")+" props_inside="+best[3]); return best; }
  // ---- grid A* (2-3 m cells) used for the Dash road and the boulevard ring; cost rises near obstacles so routes keep to street centres ----
  function route(pts,box,cell,clr){ const nx=Math.ceil((box[2]-box[0])/cell), nz=Math.ceil((box[3]-box[1])/cell), cost=new Float32Array(nx*nz);
    for(let i=0;i<nx;i++) for(let j=0;j<nz;j++){ const x=box[0]+(i+.5)*cell, z=box[1]+(j+.5)*cell; let dmin=99;
      for(const c of colliders){ if(c.off) continue; const dx=Math.max(c.minX-x,0,x-c.maxX), dz=Math.max(c.minZ-z,0,z-c.maxZ); const dd=Math.hypot(dx,dz); if(dd<dmin) dmin=dd; }
      for(const c of S.cols){ const dx=Math.max(c.minX-x,0,x-c.maxX), dz=Math.max(c.minZ-z,0,z-c.maxZ); dmin=Math.min(dmin,Math.hypot(dx,dz)); }
      cost[i*nz+j]=dmin<clr||!onLandBase(x,z)?-1:1+Math.max(0,8-dmin)*.6; }
    const out=[]; for(let k=0;k<pts.length-1;k++){ const p=astar(pts[k],pts[k+1]); if(!p){ S.warn.push("route fail "+pts[k]+"->"+pts[k+1]); return null; } if(out.length) p.shift(); out.push(...p); }
    return out;
    function astar(a,b){ const ci=p=>[Math.max(0,Math.min(nx-1,Math.floor((p[0]-box[0])/cell))),Math.max(0,Math.min(nz-1,Math.floor((p[1]-box[1])/cell)))];
      const snap=([i,j])=>{ if(cost[i*nz+j]>0) return [i,j]; for(let r=1;r<12;r++) for(let di=-r;di<=r;di++) for(let dj=-r;dj<=r;dj++){ const u=i+di,v=j+dj; if(u>=0&&v>=0&&u<nx&&v<nz&&cost[u*nz+v]>0) return [u,v]; } return [i,j]; };
      const [si,sj]=snap(ci(a)), [ti,tj]=snap(ci(b)), N=nx*nz, g=new Float32Array(N).fill(1e9), from=new Int32Array(N).fill(-1), done=new Uint8Array(N); const open=[[0,si*nz+sj]]; g[si*nz+sj]=0;
      
      while(open.length){ let bi=0; for(let q=1;q<open.length;q++) if(open[q][0]<open[bi][0]) bi=q; const [,u]=open[bi]; open[bi]=open[open.length-1]; open.pop(); if(done[u]) continue; done[u]=1;
        const ui=Math.floor(u/nz), uj=u%nz; if(ui===ti&&uj===tj) break;
        for(const [di,dj] of [[1,0],[-1,0],[0,1],[0,-1],[1,1],[1,-1],[-1,1],[-1,-1]]){ const vi=ui+di, vj=uj+dj; if(vi<0||vj<0||vi>=nx||vj>=nz) continue; const v=vi*nz+vj, cv=cost[v]; if(cv<0||done[v]) continue;
          const ng=g[u]+cv*Math.hypot(di,dj); if(ng<g[v]){ g[v]=ng; from[v]=u; open.push([ng+Math.hypot(vi-ti,vj-tj)*.9,v]); } } }
      const t=ti*nz+tj; if(from[t]<0&&t!==si*nz+sj) return null; const P=[]; for(let v=t;v>=0;v=from[v]) P.unshift([box[0]+(Math.floor(v/nz)+.5)*cell,box[1]+(v%nz+.5)*cell]); return P; } }
  function simplify(P,eps){ if(P.length<3) return P; let dm=0,im=0; const [ax,az]=P[0],[bx,bz]=P[P.length-1];
    for(let i=1;i<P.length-1;i++){ const d=segDist(P[i][0],P[i][1],ax,az,bx,bz); if(d>dm){dm=d;im=i;} }
    return dm>eps?simplify(P.slice(0,im+1),eps).slice(0,-1).concat(simplify(P.slice(im),eps)):[P[0],P[P.length-1]]; }
  function chaikin(P,n){ for(let k=0;k<n;k++){ const Q=[P[0]]; for(let i=0;i<P.length-1;i++){ const [ax,az]=P[i],[bx,bz]=P[i+1]; Q.push([ax*.75+bx*.25,az*.75+bz*.25],[ax*.25+bx*.75,az*.25+bz*.75]); } Q.push(P[P.length-1]); P=Q; } return P; }
  const offset=(P,o)=>P.map((p,i)=>{ const a=P[Math.max(0,i-1)], b=P[Math.min(P.length-1,i+1)], L=Math.hypot(b[0]-a[0],b[1]-a[1])||1; return [p[0]+(b[1]-a[1])/L*o,p[1]-(b[0]-a[0])/L*o]; });
  const plen=P=>{ let L=0; for(let i=1;i<P.length;i++) L+=Math.hypot(P[i][0]-P[i-1][0],P[i][1]-P[i-1][1]); return L; };
  const r2=v=>Math.round(v*100)/100;
  let onLandBase=(x,z)=>onLand(x,z);

  // ================= (1) STRIP BEACH BOULEVARD + BOARDWALK (Front Beach Road analog, south edge facing the Gulf) =================
  function beach(){ const x0=168,x1=322, zr0=201, lanes=4, lw=3.05, zr1=zr0+lanes*lw, zs1=zr1+3.05, zb0=zs1+4, zb1=zb0+4, zE=242;
    S.land.push([x0-2,198,x1+2,zE]);
    B((x0+x1)/2,-.75,(200+zE)/2+.25,x1-x0+4,1.5,zE-200-.5,SAND);                                 // sand pad (top y 0)
    B((x0+x1)/2,.01,(zr0+zr1)/2,x1-x0,.02,zr1-zr0,ASPH);                                         // 4 x 10 ft lanes = 12.2 m
    for(let x=x0+2;x<x1-2;x+=9){ B(x+1.5,.025,zr0+lw,.12,.01,3,LINE,Math.PI/2); B(x+1.5,.025,zr0+3*lw,.12,.01,3,LINE,Math.PI/2); }
    B((x0+x1)/2,.025,(zr0+zr1)/2-.12,x1-x0,.01,.1,YEL); B((x0+x1)/2,.025,(zr0+zr1)/2+.12,x1-x0,.01,.1,YEL);
    B((x0+x1)/2,.05,zr1+1.525,x1-x0,.1,3.05,0xc9c3b4);                                           // 10 ft south sidewalk (beige)
    B((x0+x1)/2,.04,(zb0+zb1)/2,x1-x0-8,.08,zb1-zb0,WOOD);                                       // boardwalk deck 4 m (min 6 ft)
    for(let x=x0+4;x<x1-4;x+=1.2) B(x,.085,(zb0+zb1)/2,.04,.01,zb1-zb0,0x6e5236);               // plank seams
    const gaps=[200,245,290]; const inGap=x=>gaps.some(g=>Math.abs(x-g)<2.5);
    for(const z of [zb0-.1,zb1+.1]){ for(let x=x0+4;x<=x1-4;x+=2.4) if(!inGap(x)) B(x,.55,z,.12,1.1,.12,WOOD);
      let s=x0+4; for(const g of gaps.concat([x1-4+2.5])){ const e=g-2.5; if(e-s>2){ B((s+e)/2,1.07,z,e-s,.09,.12,0x9a7a56); if(z>zb1) rail("bo_boardwalk_rail_"+g,[[r2(s),1.07,r2(z)],[r2(e),1.07,r2(z)]],.09); } s=g+2.5; } }
    for(let x=x0+6;x<x1;x+=30){ CY(x,4.5,zr1+.6,.12,9,0x8a8e98); B(x,9,zr1-.6,.25,.2,2.4,0x8a8e98); GL(x,8.85,zr1-1.7,.5,.08,.9,0xffe6b0); halo(x,8.8,zr1-1.7,0xffe6b0,7); }
    for(let x=x0+15;x<x1;x+=30){ CY(x,5,zs1+1.6,.25,10,0xa8a49a); for(let k=0;k<6;k++){ const a=k/6*Math.PI*2; inst("cone",x+Math.sin(a)*1.4,10.2,zs1+1.6+Math.cos(a)*1.4,.8,3.6,.16,0x2e8a4a,Math.cos(a)*1.7,0,-Math.sin(a)*1.7); } }
    // lifeguard stands (PCB-style coloured huts on stilts) on the sand
    for(const [x,c] of [[205,0xff5a3c],[262,0x2ec4d6],[305,0xffd23c]]){ const z=zE-9; for(const dx of [-1,1]) for(const dz of [-1,1]) CY(x+dx,1.2,z+dz,.1,2.4,0xd8d8d0);
      B(x,2.5,z,2.6,.2,2.6,0xd8d8d0); B(x,3.6,z,2.2,2,2.2,c); B(x,4.75,z,2.8,.3,2.8,0xf0f0e8); col(x-1.3,z-1.3,x+1.3,z+1.3,"beach_stand"); }
    GL((x0+x1)/2,.04,zE-.5,x1-x0,.02,.3,0xFF2BD6);                                                 // district edge neon like the others
    S.areas.beach={box:[x0,198,x1,zE],road:[zr0,zr1],walk:[zr1,zs1],boardwalk:[zb0,zb1],rails:gaps.length+1}; }

  // ================= (2) CAUSEWAY: parapet handrails as grind rails + underpass viaduct at the Heights landing =================
  function causeway(){ const b=PALMA.bridges.find(q=>q.id==="causeway"); const [ax,az]=b.a,[bx,bz]=b.b, L=Math.hypot(bx-ax,bz-az), ux=(bx-ax)/L, uz=(bz-az)/L, px=uz, pz=-ux, mx=(ax+bx)/2, mz=(az+bz)/2, E=L/2+8;
    // createBridge: parapet top rail box at local x=+-4.35, y=1.15, length L+16 (world.js). Splines sit exactly on it.
    for(const sd of [-1,1]){ const P=[]; for(let t=-E+1;t<=E-1+1e-6;t+=(2*E-2)/8) P.push([r2(mx+px*sd*4.35+ux*t),1.15,r2(mz+pz*sd*4.35+uz*t)]); rail("bo_causeway_parapet_"+(sd<0?"L":"R"),P,.09); }
    // underpass: 12 m wide elevated deck (soffit 5.5 m) across the approach 16 m inland of the north abutment -> helicopter break
    const cx=bx+ux*16, cz=bz+uz*16, ry=Math.atan2(px,pz), W=12, LEN=48, Y=6.2;
    B(cx,Y,cz,LEN,1.2,W,CONC,ry-Math.PI/2); for(const sd of [-1,1]){ const ox=ux*sd*(W/2-.2), oz=uz*sd*(W/2-.2); B(cx+ox,Y+1.05,cz+oz,LEN,.9,.4,CONC2,ry-Math.PI/2); GL(cx+ux*sd*W/2*1.02,Y-.5,cz+uz*sd*W/2*1.02,LEN,.08,.08,0xFFD700,ry-Math.PI/2); }
    for(const o of [-21,-9,9,21]) for(const sd of [-1,1]){ const x=cx+px*o+ux*sd*4, z=cz+pz*o+uz*sd*4; B(x,Y/2-.3,z,1.6,Y-.6,1.6,CONC2); col(x-.8,z-.8,x+.8,z+.8,"underpass_pier"); }
    for(const o of [-21,-9,9,21]){ const x=cx+px*o, z=cz+pz*o; B(x,Y-.85,z,1.9,.5,9.6,CONC,ry); }
    for(let o=-18;o<=18;o+=6) GL(cx+px*o,Y-.62,cz+pz*o,.6,.05,.6,0xffe6b0);                    // soffit lights
    S.areas.causeway_underpass={centre:[r2(cx),r2(cz)],deck:[LEN,W],soffit:+(Y-.6).toFixed(2),piers:8}; }

  // ================= (3) INDUSTRIAL PORT: new quay apron west of the Port, container maze + STS gantry crane =================
  function port(){ const qx0=-330, qx1=-238, z0=22, z1=198; S.land.push([qx0,z0,qx1+2,z1]);
    B((qx0+qx1)/2,-.75,(z0+z1)/2,qx1-qx0,1.5,z1-z0,0x5a5a5c);                                   // concrete apron, top y 0
    for(let z=z0+3;z<z1;z+=6) B(qx0+.4,.25,z,.5,.3,4.6,0x3a3020);                                // timber bull rail along the quay edge
    rail("bo_port_bullrail",[[qx0+.4,.42,z0+1],[qx0+.4,.42,z1-1]],.12);
    const g1=qx0+4, g2=g1+30.48;                                                                 // crane rails: 100 ft gauge
    for(const x of [g1,g2]){ B(x,.02,(z0+z1)/2,.3,.04,z1-z0-2,0x9a9aa0); }
    // STS crane (Tampa ZPMC: 30.48 m gauge, 39.62 m lift, 53.04 m outreach; Konecranes: 18 m between legs, 14-17 m portal clearance)
    const cz=110, LH=14, H=42, CR=0xd84a2a;
    for(const x of [g1,g2]) for(const sd of [-1,1]){ const z=cz+sd*9.8; B(x,LH/2+14,z,1.6,LH+28,1.6,CR); B(x,1,z,2.6,2,3.4,0x333338); col(x-1.3,z-1.7,x+1.3,z+1.7,"sts_leg"); }
    for(const sd of [-1,1]) B((g1+g2)/2,LH+.8,cz+sd*9.8,g2-g1+1.6,1.6,1.4,CR);                    // portal beams
    for(const x of [g1,g2]) B(x,LH+.8,cz,1.4,1.6,19.6+1.6,CR);                                   // sill/portal ties
    const bx0=g1-53.04, bx1=g2+20; B((bx0+bx1)/2,H,cz,bx1-bx0,2.4,4.4,CR);                       // boom + girder (outreach 53 m, backreach 20 m)
    B((g1+g2)/2,H+9,cz,4,18,4,CR); seg(g1,cz,g1-35,cz,.25,H+9,.25,0xd8d8d0); B(g2+18,H-3.5,cz,8,5,5,0x444448); // A-frame, stays, machinery house
    B(g1-12,H-3,cz,4,2.6,3.4,0xf0f0e8);                                                          // trolley + cab
    for(const x of [bx0+1,g1,g2,bx1-1]) GL(x,H+1.4,cz,.5,.5,.5,0xff2020);                        // aviation reds
    GL(bx0+.5,H,cz,.3,.3,4.6,0xFF6A00); halo(g1,H+10,cz,0xff2020,8);
    // container maze: 40 ft ISO 1AA boxes (12.192 x 2.438 x 2.591 m), stacks 1-3, blocks of 2 side by side, 4 m aisles
    const CL=12.192, CW=2.438, CH=2.591, AIS=4, pal=[0x2a5a8a,0xb03024,0x2e7a3a,0x8a8a88,0xd8782a,0x2a3a5a,0xe0e0dc,0x6a2a6a];
    let nC=0; const hsh=(i,j,k)=>{ let h=(i*73856093)^(j*19349663)^(k*83492791); h=(h^(h>>>13))*1274126177; return ((h^(h>>>16))>>>0)/4294967296; };
    for(const [za,zb] of [[z0+6,cz-16],[cz+16,z1-4]]) for(let i=0,x=g2+4.5;x+CL<=qx1-2;i++,x+=CL+AIS) for(let j=0,z=za;z+2*CW<=zb;j++,z+=2*CW+AIS){
      if((x<g1+2&&x+CL>g1-2)||(x<g2+2&&x+CL>g2-2)) continue;                                     // keep crane rails clear
      const hv=hsh(i,j,za); if(hv<.18) continue;                                                 // open cells = maze turns
      const n=1+Math.floor(hsh(j,i,7)*3);
      for(let w=0;w<2;w++) for(let k=0;k<n-(w&&hv<.5?1:0);k++){ const c=pal[Math.floor(hsh(i+k,j+w,k)*pal.length)]; B(x+CL/2,CH*(k+.5),z+CW*(w+.5),CL-.04,CH-.04,CW-.06,c);
        for(let r=1;r<12;r+=1.2) B(x+r,CH*(k+.5),z+CW*(w+.5)+(w?1:-1)*(CW/2-.01),.12,CH-.3,.04,0x000000+((c>>1)&0x7f7f7f)); nC++; }
      col(x,z,x+CL,z+2*CW,"container"); }
    S.areas.port={apron:[qx0,z0,qx1,z1],crane:{gauge:30.48,legs:[r2(g1),r2(g2)],cz,portal:LH,boom:H,outreach:53.04,backreach:20},containers:nC}; }

  // ================= (4) PORTSIDE LANDMARK TOWER (sightline anchor) =================
  // ---- reserved fixed lots (tower, precinct): always place. Clears what the random world put there: whole generated buildings
  // (B arrays spliced before buildInstancedBuildings, their collider switched off), small street props (DET instances scaled to 0,
  // INST entries dropped, their small colliders off). Anything bigger (garage, landmark, grind rail) is only reported in S.warn.
  function boReserveLot(x0,z0,x1,z1,tag){ const WB=boWorldB(), R={tag,rect:[x0,z0,x1,z1],buildings:0,props:0,inst:0,cols:0,conflicts:[]}; const ov=(a0,b0,a1,b1)=>a1>x0&&a0<x1&&b1>z0&&b0<z1;
    for(let i=WB.pos.length-1;i>=0;i--){ const [x,z]=WB.pos[i], [w,,d]=WB.size[i]; if(!ov(x-w/2,z-d/2,x+w/2,z+d/2)) continue;
      for(const c of colliders) if(!c.off&&Math.abs(c.minX-(x-w/2))<1e-6&&Math.abs(c.maxZ-(z+d/2))<1e-6&&Math.abs(c.maxX-(x+w/2))<1e-6){ c.off=true; break; }
      const mi=miniRects.findIndex(m=>m.x===x&&m.z===z&&m.w===w&&m.d===d); if(mi>=0) miniRects.splice(mi,1);
      for(const k of ["pos","size","col","neon"]) if(WB[k]) WB[k].splice(i,1); for(const k in WB) if(!["pos","size","col","neon"].includes(k)&&Array.isArray(WB[k])&&WB[k].length>i) WB[k].splice(i,1); R.buildings++; }
    const inR=(x,z)=>x>x0&&x<x1&&z>z0&&z<z1, mt=new THREE.Matrix4(), Z=new THREE.Matrix4().makeScale(0,0,0);
    for(const k in DET){ if(k.startsWith("walk")) continue; for(const p of DET[k]){ if(!inR(p[0],p[2])||!p[3]) continue;
      for(const d of DETM){ const m=d.m; if(!m||!m.isInstancedMesh) continue; for(let i=0;i<m.count;i++){ m.getMatrixAt(i,mt); const e=mt.elements; if(Math.abs(e[12]-p[0])<1e-3&&Math.abs(e[13]-p[1])<1e-3&&Math.abs(e[14]-p[2])<1e-3){ m.setMatrixAt(i,Z); m.instanceMatrix.needsUpdate=true; } } }
      p[3]=p[4]=p[5]=0; R.props++; } }
    for(const k in INST){ const L=INST[k]; for(let i=L.length-1;i>=0;i--) if(inR(L[i][0],L[i][2])){ L.splice(i,1); R.inst++; } }
    for(const c of colliders){ if(c.off||!ov(c.minX,c.minZ,c.maxX,c.maxZ)) continue; const a=(c.maxX-c.minX)*(c.maxZ-c.minZ);
      if(a<40&&inR((c.minX+c.maxX)/2,(c.minZ+c.maxZ)/2)){ c.off=true; R.cols++; } else R.conflicts.push("collider "+[c.minX,c.minZ,c.maxX,c.maxZ].map(v=>+v.toFixed(1)).join(",")); }
    for(const g of PALMA.garages) if(ov(g.pos[0]-14,g.pos[1]-14,g.pos[0]+14,g.pos[1]+14)) R.conflicts.push("garage "+g.pos);
    if(typeof GRIND!=="undefined") for(const sp of GRIND.S) if(sp&&sp.pts&&sp.pts.some(q=>inR(q.x,q.z))) R.conflicts.push("rail "+sp.id);
    PROPS=null; (S.lots=S.lots||[]).push(R); if(R.conflicts.length) S.warn.push("lot "+tag+" conflicts: "+R.conflicts.join("; ")); return R; }
  const BO_LOT={ tower:[55,62], precinct:[280,53] }; // fixed reserved lot centres: clear of fixed colliders, garages, water and every grind spline at the shipping seed (1)
  function tower(){ const W=24, [x,z]=BO_LOT.tower; boReserveLot(x-W/2-2,z-W/2-2,x+W/2+2,z+W/2+8,"tower");
    const tiers=[[24,0,62,0x26335c],[19,62,96,0x2c3d6a],[13,96,114,0x34477a]];
    for(const [w,y0,y1,c] of tiers){ B(x,(y0+y1)/2,z,w,y1-y0,w,c); for(let y=y0+4;y<y1;y+=4) GL(x,y,z,w+.12,.18,w+.12,0x7fa8ff); GL(x,y1-.2,z,w+.3,.4,w+.3,0xFFD700); }
    CY(x,124,z,.6,20,0xc8c8d0); GL(x,134.5,z,.8,1,.8,0xff2020); halo(x,135,z,0xff2020,10); halo(x,114,z,0xFFD700,24);
    B(x,3,z+W/2+3,14,.4,6,0x1a1d2e); for(const dx of [-6,6]) CY(x+dx,1.5,z+W/2+5.6,.2,3,0x8a8e98);                     // entry canopy
    GL(x,.05,z+W/2+3,14,.02,.2,0xFFD700);
    col(x-W/2,z-W/2,x+W/2,z+W/2,"tower"); miniRects.push({x,z,w:W,d:W,c:"#FFD700"});
    S.signs.push(["PORTSIDE",16,"#FFD700",x,66,z+W/2*19/24+.3,0]);
    S.areas.portside_tower={centre:[x,z],footprint:W,height:114,spire:134}; }

  // ================= (5) HEIGHTS DOWNHILL DASH ROAD (winding, links causeway north end <-> 98 bridge north end) =================
  function dash(){ const b98=PALMA.bridges.find(q=>q.id==="b98"), cw=PALMA.bridges.find(q=>q.id==="causeway");
    const wp=[[b98.b[0]+2,b98.b[1]-14],[176,-292],[136,-256],[96,-296],[66,-292],[10,-256],[-30,-294],[-70,-258],[cw.b[0]-4,cw.b[1]-14]];
    const P0=route(wp,[-158,-299,238,-241],2,3.2); if(!P0){ S.warn.push("dash: route failed"); return; }
    const P=chaikin(simplify(P0,1.2),3), W=7.32; S.dashPath=P;
    for(let i=0;i<P.length-1;i++){ const [ax,az]=P[i],[bx,bz]=P[i+1]; seg(ax,az,bx,bz,W,.02,.03,ASPH); }
    let acc=0; for(let i=0;i<P.length-1;i++){ const [ax,az]=P[i],[bx,bz]=P[i+1], L=Math.hypot(bx-ax,bz-az); if(Math.floor((acc+L)/6)!==Math.floor(acc/6)&&((acc/6)|0)%2===0) seg(ax,az,bx,bz,.12,.04,.01,YEL); acc+=L; }
    const L1=offset(P,-W/2+.3), R1=offset(P,W/2-.3); for(const E of [L1,R1]) for(let i=0;i<E.length-1;i++) seg(E[i][0],E[i][1],E[i+1][0],E[i+1][1],.12,.04,.01,LINE);
    // W-beam guardrail both sides (MGS 31 in = 0.79 m rail height, posts at 6 ft 3 in = 1.905 m) -> grindable splines
    const GL1=offset(P,-W/2-.8), GR1=offset(P,W/2+.8);
    for(const [E,nm] of [[GL1,"L"],[GR1,"R"]]){ let a=0; for(let i=0;i<E.length-1;i++){ const [ax,az]=E[i],[bx,bz]=E[i+1], L=Math.hypot(bx-ax,bz-az); seg(ax,az,bx,bz,.08,.68,.33,0xa8acb0);
        for(let d=(1.905-a%1.905)%1.905; d<L; d+=1.905){ const t=d/L; B(ax+(bx-ax)*t,.4,az+(bz-az)*t,.15,.8,.15,0x5a5a5e); } a+=L; }
      const step=Math.max(1,Math.floor(E.length/60)); const Q=E.filter((p,i)=>i%step===0||i===E.length-1).map(p=>[r2(p[0]),.79,r2(p[1])]); rail("bo_dash_guard_"+nm,Q,.09); }
    for(let i=0;i<P.length;i+=Math.max(1,Math.floor(P.length/18))){ const [x,z]=GR1[i]; GL(x,.9,z,.25,.25,.25,0x7CB342); }   // reflector beacons
    S.areas.heights_dash={length:Math.round(plen(P)),width:W,points:P.length,from:wp[0],to:wp[wp.length-1]}; }

  // ================= (6) BOULEVARD RING: painted 4-lane spine over existing streets + RING gantries; links via shore + 98 + causeway =================
  function ring(){ const cw=PALMA.bridges.find(q=>q.id==="causeway"), sh=PALMA.bridges.find(q=>q.id==="shore"), b98=PALMA.bridges.find(q=>q.id==="b98");
    const west=route([[cw.a[0]-6,cw.a[1]+8],[60,-40],[62,60],[sh.a[0]-6,sh.a[1]]],[-58,-98,92,198],2,1.8);
    const east=route([[sh.b[0]+6,sh.b[1]],[214,130],[246,40],[b98.a[0],b98.a[1]+10]],[170,-98,320,198],2,1.8);
    S.ringPaths=[]; let tot=0;
    for(const [nm,P0] of [["west",west],["east",east]]){ if(!P0){ S.warn.push("ring "+nm+" failed"); continue; } const P=chaikin(simplify(P0,1.5),2); S.ringPaths.push(P); tot+=plen(P);
      for(const o of [-.12,.12]){ const E=offset(P,o); for(let i=0;i<E.length-1;i++) seg(E[i][0],E[i][1],E[i+1][0],E[i+1][1],.1,.03,.01,YEL); }
      let acc=0; for(let i=0;i<P.length-1;i++){ const [ax,az]=P[i],[bx,bz]=P[i+1], L=Math.hypot(bx-ax,bz-az); for(let d=(24-acc%24)%24; d<L; d+=24){ const t=d/L, x=ax+(bx-ax)*t, z=az+(bz-az)*t, ry=Math.atan2(bx-ax,bz-az);
          GL(x,.035,z,1.6,.01,.25,0xFFD700,ry+.6); GL(x+Math.sin(ry)*.5,.035,z+Math.cos(ry)*.5,1.6,.01,.25,0xFFD700,ry-.6); } acc+=L; } }   // chevrons
    // RING gantries at both bridge heads of each side (posts only collide; beam is 6.5 m up)
    S.ringGantries=[]; for(const P of S.ringPaths) for(const k of [Math.round(P.length*.15),Math.round(P.length*.85)]){ if(k<1||k>=P.length-1) continue; const [x,z]=P[k],[x2,z2]=P[k+1], ry=Math.atan2(x2-x,z2-z), px=Math.cos(ry), pz=-Math.sin(ry);
      const posts=[]; for(const sd of [-1,1]){ let o=sd*3; for(;Math.abs(o)<9;o+=sd*.5){ const qx=x+px*o, qz=z+pz*o; if(!clear(qx-.3,qz-.3,qx+.3,qz+.3,.6)) { o-=sd*.5; break; } } posts.push([x+px*o,z+pz*o]); }
      for(const [qx,qz] of posts){ CY(qx,3.3,qz,.2,6.6,STEEL); col(qx-.25,qz-.25,qx+.25,qz+.25,"ring_gantry"); }
      seg(posts[0][0],posts[0][1],posts[1][0],posts[1][1],.5,6.5,.5,STEEL); const gx=(posts[0][0]+posts[1][0])/2, gz=(posts[0][1]+posts[1][1])/2; B(gx,6.5,gz,3.6,1.3,.2,0x1e7a3a,ry+Math.PI/2); GL(gx,5.75,gz,3.6,.08,.24,0xFFD700,ry+Math.PI/2);
      S.ringGantries.push([r2(gx),r2(gz)]); }
    S.areas.boulevard_ring={painted_m:Math.round(tot),gantries:S.ringGantries.length,links:"west(Portside) + shore bridge + east(East Blocks/Drive) + 98 bridge + Heights Dash road + causeway"}; }

  // ================= (7) G-MEN PRECINCT (police HQ) in The Drive =================
  function precinct(){ const W=30, D=18, [x,z]=BO_LOT.precinct; boReserveLot(x-W/2-2,z-D/2-2,x+W/2+5,z+D/2+21,"precinct");
    B(x,6,z,W,12,D,0xb9b6ae); B(x,12.3,z,W+.6,.6,D+.6,0x8a8884);                                   // 3 storeys (4 m) + parapet cap
    for(let y=2.5;y<12;y+=4) for(const sd of [-1,1]) GL(x,y,z+sd*(D/2+.05),W-4,1.4,.05,0x9fc4ff);    // window bands
    B(x,1.6,z+D/2+.05,8,3.2,.1,0x1a2340); B(x,4,z+D/2+2,10,.4,4,0x1a2340); for(const dx of [-4.6,4.6]) CY(x+dx,2,z+D/2+3.6,.25,4,0xd8d8d0);
    GL(x,4.3,z+D/2+3.9,10,.25,.25,0x3D7BFF); GL(x-3,4.3,z+D/2+3.9,1.2,.3,.3,0xff2020);
    CY(x+W/2+3,7,z+D/2+3,.12,14,0xd8d8d0); halo(x,4.3,z+D/2+4,0x3D7BFF,8);                          // flagpole (no flag)
    col(x-W/2,z-D/2,x+W/2,z+D/2,"precinct");
    // impound lot behind: chain-link with a 6 m gate gap, cruisers as grey-box
    const lz0=z+D/2+7, lz1=lz0+12; for(const [ax,az,bx,bz] of [[x-W/2,lz1,x+W/2,lz1],[x-W/2,lz0,x-W/2,lz1],[x+W/2,lz0,x+W/2,lz1],[x-W/2,lz0,x-3,lz0],[x+3,lz0,x+W/2,lz0]]){
      seg(ax,az,bx,bz,.06,1.1,2.2,0x8a9098); col(Math.min(ax,bx)-.1,Math.min(az,bz)-.1,Math.max(ax,bx)+.1,Math.max(az,bz)+.1,"precinct_fence"); }
    for(let k=0;k<4;k++){ const cx=x-W/2+5+k*6.5; B(cx,.75,lz0+6,1.9,1,4.8,0x1c1f26); B(cx,1.45,lz0+6.2,1.6,.5,2.4,0xe8e8e8); GL(cx,1.78,lz0+6,1.2,.12,.25,k%2?0xff2020:0x3D7BFF); }
    miniRects.push({x,z,w:W,d:D,c:"#3D7BFF"}); S.signs.push(["G-MEN PRECINCT",12,"#3D7BFF",x,9.2,z+D/2+.4,0]);
    S.areas.gmen_precinct={centre:[x,z],footprint:[W,D],height:12.6,lot:[W,12]}; }

  // (8) Sleeping Forest 'ST  FORES': NOT a world sign. It is 3 TURF/graffiti wall tiles (ShaderMaterial InstancedMesh, noMerge,
  // x 37.55/40/42.45, y 2.6, z -291.66) on the back of the crew-base annex; same with ?noperf. Owner graffiti.js/turf -> logged.
  S.signs=[];
  // ---- WALL RIDE panels (place.js createEastBlocks): tag the real ones. Names follow the authored grid slot order
  // (x outer, z inner, 1-based), so a slot keeps its name under any seed (seeds only decide which slots get a panel/side).
  // Matched by the exact collider rect place.js pushes + the tilted 0.5x5x10 panel mesh at the same spot; geometry untouched.
  // ---- spawn run-out (Rydah Systems, 16:06): player spawns at (0,0,16) facing -z and hit the Terminal Plaza holo pad
  // (world.js createPlaza: CylinderGeometry(5,5.4,.4) at (0,.2,0) + collider {-5,5,-5,5}) after 10 m. The pad becomes a flush
  // inlay (top 4 cm, same as the plaza decal; WORLD_GROUND already reads ground there), its collider is parked off-map in place
  // (zero area, so collider indices do not shift), and the cyan ring + hologram sit on the inlay. Concentric plaza layout,
  // gold ring, torus and Terminal tower view are unchanged; the hologram is light (no collision).
  function boSpawnRunout(){ const out={pad:0,ring:0,holo:0,col:-1};
    for(const o of scene.children){ const g=o.geometry, p=g&&g.parameters, at0=Math.abs(o.position.x)<1e-6&&Math.abs(o.position.z)<1e-6;
      if(!at0) continue;
      if(o.isMesh&&g.type==="CylinderGeometry"&&p.radiusTop===5&&p.radiusBottom===5.4&&p.height===.4&&Math.abs(o.position.y-.2)<1e-6){ o.scale.y=.1; o.position.y=.02; out.pad++; }
      else if(o.isMesh&&g.type==="RingGeometry"&&p.innerRadius===4.2&&p.outerRadius===4.8&&Math.abs(o.position.y-.42)<1e-6){ o.position.y=.05; out.ring++; }
      else if(o.isGroup&&Math.abs(o.position.y-.4)<1e-6&&o.children.length>=8&&o.children.every(c=>c.isMesh&&c.geometry.type==="CylinderGeometry")){ o.position.y=.05; out.holo++; } }
    out.col=colliders.findIndex(c=>c.minX===-5&&c.maxX===5&&c.minZ===-5&&c.maxZ===5&&Object.keys(c).length===4);
    if(out.col>=0&&out.pad===1){ const c=colliders[out.col]; c.minX=c.maxX=c.minZ=c.maxZ=-9e5; /* parked off-map: zero area AND unreachable even with rider radius */ c.bo="spawn_runout_emptied"; }
    else S.warn.push("spawn runout: pad "+out.pad+" col "+out.col);
    S.spawnRunout=out; }
  function boWallPanels(){ const out=[]; const d=(PALMA.districts||[]).find(q=>q.id==="eastblocks"); if(!d||!d.box) { S.warn.push("wallpanels: no eastblocks district"); window.WALL_PANELS=out; return; }
    const [x0,z0,x1,z1]=d.box, w=12; let slot=0; const meshes=[]; scene.traverse(o=>{ if(o.isMesh&&o.geometry&&o.geometry.type==="BoxGeometry"){ const p=o.geometry.parameters; if(p.width===.5&&p.height===5&&p.depth===10&&Math.abs(Math.abs(o.rotation.z)-.35)<1e-6) meshes.push(o); } });
    for(let x=x0+10;x<x1-8;x+=17) for(let z=z0+10;z<z1-8;z+=17){ slot++;
      for(const sx of [-1,1]){ const cx=x+sx*(w/2+1.3); const ci=colliders.findIndex(c=>Math.abs(c.minX-(cx-.8))<1e-6&&Math.abs(c.maxX-(cx+.8))<1e-6&&Math.abs(c.minZ-(z-5))<1e-6&&Math.abs(c.maxZ-(z+5))<1e-6); if(ci<0) continue;
        const m=meshes.find(o=>Math.abs(o.position.x-cx)<1e-6&&Math.abs(o.position.z-z)<1e-6&&Math.sign(o.rotation.z)===sx); if(!m) continue;
        const name="wallpanel_eastblocks_"+slot; const c=colliders[ci]; c.wallPanel=true; c.wallPanelName=name; m.userData.wallPanel=true; m.userData.wallPanelName=name;
        out.push({name,colliderIndex:ci,collider:c,mesh:m,center:[cx,2.4,z],normal:[sx,0,0],length:10,height:5,tilt:sx*.35}); } }
    window.WALL_PANELS=out; S.wallPanels=out.map(p=>p.name); }
  // ---- garage sign stand-off: canvas sign planes that sit <12 cm off their wall (e.g. SLEEPING FOREST "CLUBHOUSE" plate at 5 cm)
  // z-fight / clip at distance. Push them out along their normal to a 15 cm gap (+ polygonOffset). Position only, before world_perf packs.
  function boSignGap(){ const fixed=[]; scene.updateMatrixWorld(true); const rc=new THREE.Raycaster(), n=new THREE.Vector3(), c=new THREE.Vector3(), M=[];
    scene.traverse(o=>{ if(o.isMesh&&o.visible&&!o.isInstancedMesh&&!(o.material&&o.material.map&&o.material.map.image instanceof HTMLCanvasElement)&&o.material&&o.material.side!==THREE.BackSide) M.push(o); });
    for(const g of PALMA.garages){ let grp=null,best=1e9; for(const o of scene.children) if(o.type==="Group"){ const d=Math.hypot(o.position.x-g.pos[0],o.position.z-g.pos[1]); if(d<best){best=d;grp=o;} } if(!grp||best>3) continue;
      grp.traverse(o=>{ if(!o.isMesh||o.geometry.type!=="PlaneGeometry"||!o.material.map||!(o.material.map.image instanceof HTMLCanvasElement)) return;
        o.getWorldPosition(c); n.set(0,0,1).transformDirection(o.matrixWorld); rc.set(c.clone().addScaledVector(n,.5),n.clone().negate()); rc.far=.5+.12;
        const h=rc.intersectObjects(M,false).find(q=>q.object!==o); if(!h) return; const gap=h.distance-.5; if(gap>=.12) return;
        const push=.15-gap, local=n.clone().multiplyScalar(push); const inv=new THREE.Matrix4().copy(o.parent.matrixWorld).invert(); const lp=c.clone().add(local).applyMatrix4(inv); o.position.copy(lp); o.updateMatrixWorld(true);
        o.material.polygonOffset=true; o.material.polygonOffsetFactor=-1; o.material.polygonOffsetUnits=-1; fixed.push([g.crew,+gap.toFixed(3),+push.toFixed(3),o.geometry.parameters.width]); }); }
    S.signGap=fixed; }
  S.build=function(){ animated.push(()=>S.tick()); try{ beach(); causeway(); port(); tower(); dash(); ring(); precinct();
      const n0=scene.children.length; for(const s of S.signs) putSign(...s); S.signMeshes=scene.children.slice(n0); S.signMeshes.forEach(o=>o.userData.blockout=true); boSpawnRunout(); boWallPanels(); boSignGap(); }catch(e){ console.warn("blockout build",e); S.err=String(e); } };
  // late, additive gameplay hookup
  S.tick=function(){ if(S.live) return; if(!(window.GRAF&&GRAF.ready&&GRIND.world&&window.TURF)) return;
    // pylon-leg AABBs (createBridge tower legs, rotated 1.4 m boxes) poked 0.2-0.4 m into the deck lane: shrink each about its own
    // centre until no rider centre in the 3.4 m half-lane is within 0.4 m (movement push radius) of it. Matched by exact value, not index.
    S.pylonFix=[]; for(const c of colliders){ const r=v=>Math.round(v*1000)/1000; for(const [b,a] of PYLON_FIX) if(r(c.minX)===b[0]&&r(c.minZ)===b[1]&&r(c.maxX)===b[2]&&r(c.maxZ)===b[3]){ c.minX=a[0]; c.minZ=a[1]; c.maxX=a[2]; c.maxZ=a[3]; S.pylonFix.push(colliders.indexOf(c)); } }
    for(const c of S.cols) colliders.push(c);
    // snag slots: two colliders < 0.8 m apart (rider diameter) along a shared face > 1 m -> the rider jitters/sticks in the slot.
    // Close them with additive filler boxes (gate colliders that toggle .off are skipped).
    let F=[], tot=0; for(let pass=0;pass<1;pass++){ F=[]; const C=colliders.filter(c=>!("off" in c));
    for(let i=0;i<C.length;i++) for(let j=i+1;j<C.length;j++){ const a=C[i], b=C[j]; const gx=Math.max(a.minX-b.maxX,b.minX-a.maxX), gz=Math.max(a.minZ-b.maxZ,b.minZ-a.maxZ);
      if(gx>0&&gx<.8&&gz<0){ const z0=Math.max(a.minZ,b.minZ), z1=Math.min(a.maxZ,b.maxZ); if(z1-z0>1) F.push({minX:Math.min(a.maxX,b.maxX),maxX:Math.max(a.minX,b.minX),minZ:z0,maxZ:z1,bo:"slot_fill"}); }
      else if(gz>0&&gz<.8&&gx<0){ const x0=Math.max(a.minX,b.minX), x1=Math.min(a.maxX,b.maxX); if(x1-x0>1) F.push({minX:x0,maxX:x1,minZ:Math.min(a.maxZ,b.maxZ),maxZ:Math.max(a.minZ,b.minZ),bo:"slot_fill"}); } }
    for(const f of F) colliders.push(f); tot+=F.length; if(!F.length) break; } S.slotFills=tot;
    // land test: islands (+4 m shore) | bridge DECK footprint (createBridge deck = L+16, so ends clamp at +-8 m instead of the old
    // +-15 % of L, which let riders skate ~25 m out over open water past the causeway's south end) | new blockout land
    const base=onLand; onLandBase=base;
    onLand=function(x,z){ for(const i of PALMA.islands){ const b=i.box; if(x>b[0]-4&&x<b[2]+4&&z>b[1]-4&&z<b[3]+4) return true; }
      for(const br of PALMA.bridges){ const ax=br.a[0],az=br.a[1],vx=br.b[0]-ax,vz=br.b[1]-az,L2=vx*vx+vz*vz,L=Math.sqrt(L2),e=8/L; const t=((x-ax)*vx+(z-az)*vz)/L2; if(t<-e||t>1+e) continue;
        if(Math.abs((x-ax)*vz-(z-az)*vx)/L<3.8) return true; }
      for(const b of S.land) if(x>b[0]&&x<b[2]&&z>b[1]&&z<b[3]) return true; return false; };
    S.grindIds=[]; let bw=0; for(const r of S.railDefs){ const s=grindAdd(r.pts,"steel",r.r,{kind:r.kind}); s.bo=r.id; S.grindIds.push([r.id,s.id]);
      // stable names -> runtime IDs (IDs follow GRIND.S.length at registration, so they depend on the base world; use names)
      const nm=r.id.startsWith("bo_boardwalk_rail_")?"boardwalk_"+(++bw):r.id.replace(/^bo_/,"").replace("dash_guard_","dash_").replace("causeway_parapet_","causeway_"); S.rails[nm]=s.id; s.boName=nm; }
    if(S.railDefs.length) grindGridBuild(); try{ boKickWalls(); boKickIndex(); }catch(e){ S.warn.push("kick index "+e); console.warn(e); } S.live=true; window.BLOCKOUT_LIVE=true; };
  // ================= WALL KICKS: kick-up routes to elevated grind cables (Oliver 09:13; Rydah Systems A-kick: <=5 kicks ~ 9.5 m, wall within 4 m) =================
  // live (after kit infill + slot fills, before grid): audit street cables (GRIND.S kind cable/zip) against building faces (world B arrays); spans with no facade/alley route get a
  // concrete kick wall (own InstancedMesh, MeshStandardMaterial, no ink hull, one per pole-line area, bounds-culled).
  // live: index every kickable face -> window.WALL_KICKS / window.KICK_ROUTES, tag collider + mesh userData, and tag noKick colliders.
  const BO_KICK={reach:11, near:4, facade:2.2, alleyMin:3, alleyMax:6, topGap:2.5, minH:3, wallH:8, wallW:4, wallT:.5, off:2.0};
  function boKickBld(){ const W=boWorldB(), m=new Map(); W.pos.forEach((p,i)=>{ const [w,h,d]=W.size[i]; m.set([p[0]-w/2,p[0]+w/2,p[1]-d/2,p[1]+d/2].map(v=>v.toFixed(3)).join(","),h+((W.y&&W.y[i])||0)); }); return m; }
  function boKickH(c,bm){ if(c.kickH!=null) return c.kickH; const h=bm.get([c.minX,c.maxX,c.minZ,c.maxZ].map(v=>v.toFixed(3)).join(",")); return h==null?null:h; }
  // nearest face of AABB c toward point (x,z): {nx,nz, center, width}
  function boKickFace(c,x,z){ const cx=(c.minX+c.maxX)/2, cz=(c.minZ+c.maxZ)/2, w=c.maxX-c.minX, d=c.maxZ-c.minZ; const ex=(x-cx)/(w/2||1), ez=(z-cz)/(d/2||1);
    return Math.abs(ex)>=Math.abs(ez)?{nx:Math.sign(ex)||1,nz:0,fx:ex>0?c.maxX:c.minX,fz:Math.max(c.minZ,Math.min(c.maxZ,z)),width:d}:{nx:0,nz:Math.sign(ez)||1,fx:Math.max(c.minX,Math.min(c.maxX,x)),fz:ez>0?c.maxZ:c.minZ,width:w}; }
  function boKickSpans(){ return GRIND.S.filter(s=>(s.kind==="cable"||s.kind==="zip")&&Math.max(...s.pts.map(p=>p.y))>3); }
  // returns {type, faces:[colliders], low} or null for one spline
  function boKickRoute(s,bm,extra){ const C=colliders.concat(extra||[]); let best=null;
    const P=s.pts.filter(p=>p.y>3); const low=Math.min(...P.map(p=>p.y));
    const near=[]; C.forEach(c=>{ const h=boKickH(c,bm); if(h==null||h<BO_KICK.minH||c.noKick) return; let dm=1e9, pq=null, fq=null; for(const q of P){ const dx=Math.max(c.minX-q.x,0,q.x-c.maxX), dz=Math.max(c.minZ-q.z,0,q.z-c.maxZ), d=Math.hypot(dx,dz); if(d<dm) dm=d; if(d<=BO_KICK.near&&(!pq||q.y<pq.y)) pq=q; if(d<=BO_KICK.facade&&(!fq||q.y<fq.y)) fq=q; } if(dm<=BO_KICK.near) near.push({c,h,d:dm,q:pq,fq}); });
    for(let i=0;i<near.length;i++) for(let j=i+1;j<near.length;j++){ const a=near[i].c,b=near[j].c; const gx=Math.max(a.minX-b.maxX,b.minX-a.maxX), gz=Math.max(a.minZ-b.maxZ,b.minZ-a.maxZ);
      const ov=gx>0?Math.min(a.maxZ,b.maxZ)-Math.max(a.minZ,b.minZ):Math.min(a.maxX,b.maxX)-Math.max(a.minX,b.minX); const g=gx>0?gx:gz;
      if(g>=BO_KICK.alleyMin&&g<=BO_KICK.alleyMax&&ov>=2&&(gx>0)!==(gz>0)){ const cy=Math.min(near[i].q.y,near[j].q.y), top=Math.min(near[i].h,near[j].h); if(cy<=BO_KICK.reach+.05&&top>=cy-BO_KICK.topGap&&(!best||cy<best.cy)) best={type:"alley",faces:[a,b],cy}; } }
    if(!best) for(const n of near) if(n.fq&&n.h>=n.fq.y-BO_KICK.topGap&&n.fq.y<=BO_KICK.reach+.05){ if(!best||n.d<best.d) best={type:"facade",faces:[n.c],d:n.d,cy:n.fq.y}; }
    return best?Object.assign(best,{low}):{type:null,low}; }
  function boKickWalls(){ S.kick={walls:[],plan:[],warn:[]}; const bm=boKickBld(), spans=boKickSpans(); if(!spans.length){ S.warn.push("kick: no cables at build"); return; }
    const add=[]; for(const s of spans){ if(s.kind==="zip") continue; const r=boKickRoute(s,bm,add); if(r.type) continue;
      // mid-span low point, wire direction
      const P=s.pts; let lo=0; for(let i=1;i<P.length;i++) if(P[i].y<P[lo].y) lo=i; const a=P[0],b=P[P.length-1], L=Math.hypot(b.x-a.x,b.z-a.z)||1, ux=(b.x-a.x)/L, uz=(b.z-a.z)/L, q=P[lo];
      if(q.y>BO_KICK.reach+.05){ S.kick.warn.push("span "+s.id+" low "+q.y.toFixed(2)+" > reach"); continue; }
      // already got a wall from a sibling wire of the same span?
      if(add.some(w=>Math.hypot(w.cx-q.x,w.cz-q.z)<3.5)) continue; // sibling wire of a span that already got a wall
      let placed=null; for(const sd of [1,-1]) for(const off of [0,.6,1.2]){ if(placed) break; // centred under the pole line so all three wires are within 1.2 m
        const cx=q.x+uz*sd*off, cz=q.z-ux*sd*off, alongX=Math.abs(ux)>=Math.abs(uz); const hw=(alongX?BO_KICK.wallW:BO_KICK.wallT)/2, hd=(alongX?BO_KICK.wallT:BO_KICK.wallW)/2;
        if(!onLand(cx,cz)||!clear(cx-hw,cz-hd,cx+hw,cz+hd,.6)||add.some(w=>Math.abs(w.cx-cx)<hw+w.hw+.6&&Math.abs(w.cz-cz)<hd+w.hd+.6)) continue;
        placed={cx,cz,hw,hd,alongX,span:s.id}; }
      if(!placed){ S.kick.warn.push("span "+s.id+": no clear spot"); continue; }
      const c={minX:placed.cx-placed.hw,maxX:placed.cx+placed.hw,minZ:placed.cz-placed.hd,maxZ:placed.cz+placed.hd,bo:"kickwall",kickH:BO_KICK.wallH,wallKickWall:true}; placed.c=c; add.push(Object.assign(placed,c)); }
    // designed climb (tests/wallkick.py uses KICK_ROUTES[0]): partner wall 4 m face-to-face across the pole line -> 3-kick alley
    for(const w of add.slice().sort((a,b)=>a.cz-b.cz||a.cx-b.cx)){ if(S.kick.alley) break; const s=GRIND.S.find(t=>t.id===w.span); const a=s.pts[0],b=s.pts[s.pts.length-1], L=Math.hypot(b.x-a.x,b.z-a.z)||1, px=(b.z-a.z)/L, pz=-(b.x-a.x)/L;
      const q=s.pts.reduce((m,p)=>p.y<m.y?p:m), h=(4+BO_KICK.wallT)/2, A=[q.x+px*h,q.z+pz*h], Bp=[q.x-px*h,q.z-pz*h], ok=c=>onLand(c[0],c[1])&&clear(c[0]-w.hw,c[1]-w.hd,c[0]+w.hw,c[1]+w.hd,.6)&&!add.some(o=>o!==w&&Math.abs(o.cx-c[0])<o.hw+w.hw+.6&&Math.abs(o.cz-c[1])<o.hd+w.hd+.6);
      if(!ok(A)||!ok(Bp)||propsIn(Math.min(A[0],Bp[0])-w.hw-1,Math.min(A[1],Bp[1])-w.hd-1,Math.max(A[0],Bp[0])+w.hw+1,Math.max(A[1],Bp[1])+w.hd+1)>0) continue; // empty alley + 1 m approach
      const mk=c=>({minX:c[0]-w.hw,maxX:c[0]+w.hw,minZ:c[1]-w.hd,maxZ:c[1]+w.hd,bo:"kickwall",kickH:BO_KICK.wallH,wallKickWall:true});
      w.c=mk(A); Object.assign(w,w.c,{cx:A[0],cz:A[1]}); const c2=mk(Bp), pw=Object.assign({cx:Bp[0],cz:Bp[1],hw:w.hw,hd:w.hd,alongX:w.alongX,span:w.span,c:c2},c2); add.push(pw); S.kick.alley=[w,pw]; }
    if(!add.length) return; for(const w of add) colliders.push(w.c);
    // geometry: concrete slab + steel cap + kick-plate stripe, one InstancedMesh per area (|x| split), bounds set so it frustum-culls as a group
    const g=new THREE.BoxGeometry(1,1,1), mat=new THREE.MeshStandardMaterial({color:0xffffff,roughness:.85,metalness:.05}); mat.name="bo_kickwall_concrete";
    const groups=[add]; /* one InstancedMesh city-wide: at most +1 draw in any view */ const M=new THREE.Matrix4(), col=new THREE.Color();
    groups.forEach((G,gi)=>{ const n=G.length*3, im=new THREE.InstancedMesh(g.clone(),mat,n); let k=0; const bb=new THREE.Box3();
      for(const w of G){ const sx=w.maxX-w.minX, sz=w.maxZ-w.minZ, H=BO_KICK.wallH;
        const put=(y,h,ex,c)=>{ M.makeScale(sx+ex,h,sz+ex); M.setPosition(w.cx,y,w.cz); im.setMatrixAt(k,M); im.setColorAt(k++,col.set(c)); };
        put(H/2,H,0,0x8e8c86); put(H+.06,.12,.12,0x6d737c); put(2.2,1.2,.04,0x3a3d42); bb.expandByPoint(new THREE.Vector3(w.minX,0,w.minZ)).expandByPoint(new THREE.Vector3(w.maxX,H+.2,w.maxZ)); }
      im.geometry.boundingSphere=bb.getBoundingSphere(new THREE.Sphere()); im.geometry.boundingBox=bb.clone(); im.name="bo_kickwalls_"+gi; im.userData.blockout=true; im.userData.wallKick=true; im.userData.kickNames=[];
      G.forEach(w=>{ w.mesh=im; }); scene.add(im); });
    S.kick.walls=add; }
  function boKickDistrict(x,z){ for(const d of (PALMA.districts||[])){ const b=d.box; if(b&&x>=b[0]&&x<=b[2]&&z>=b[1]&&z<=b[3]) return d.id; } return "palma"; }
  function boKickIndex(){ const bm=boKickBld(); const WK=[], byC=new Map(), cnt={}, nk={};
    const garageNear=c=>PALMA.garages.some(g=>g.pos[0]>c.minX-14&&g.pos[0]<c.maxX+14&&g.pos[1]>c.minZ-14&&g.pos[1]<c.maxZ+14);
    // noKick tagging (kickable: building faces >=2.5 m, WALL_PANELS, kick walls)
    colliders.forEach((c,i)=>{ if(c.wallPanel||c.wallKickWall) return; const h=boKickH(c,bm); let cat=null;
      if(c.bo==="slot_fill") cat="filler"; else if(c.bo==="sts_leg"||c.bo==="container") cat="crane_container"; else if(c.bo==="precinct_fence") cat="under_3m";
      else if(c.bo) cat="blockout_prop:"+c.bo; else if("off" in c) cat="garage_gate"; else if(h==null) cat=garageNear(c)?"garage_box":"base_prop_pylon_boundary"; else if(h<BO_KICK.minH) cat="under_3m";
      if(!cat&&h!=null&&h<BO_KICK.minH) cat="under_3m"; if(cat){ c.noKick=true; c.noKickWhy=cat; nk[cat]=(nk[cat]||0)+1; } });
    const faceOf=(c,x,z,span,dz0)=>{ if(byC.has(c)) { const e=byC.get(c); if(e.servesSpline==null) e.servesSpline=span; return e; } const f=boKickFace(c,x,z), h=c.kickH!=null?c.kickH:(boKickH(c,bm)||5), dist=dz0||boKickDistrict(f.fx,f.fz);
      cnt[dist]=(cnt[dist]||0)+1; const name="wallkick_"+dist+"_"+cnt[dist]; const e={name,colliderIndex:colliders.indexOf(c),collider:c,center:[+f.fx.toFixed(2),+(h/2).toFixed(2),+f.fz.toFixed(2)],normal:[f.nx,0,f.nz],width:+f.width.toFixed(2),height:+h.toFixed(2),servesSpline:span,pairName:null};
      c.wallKick=true; c.wallKickName=name; c.wallKickServes=span; if(c.wallKickWall){ const w=S.kick.walls.find(w=>w.c===c); if(w&&w.mesh){ w.mesh.userData.kickNames.push(name); } }
      byC.set(c,e); WK.push(e); return e; };
    const routes=[], unreach=[]; const spanName=s=>s.boName||("spline_"+s.id);
    for(const s of boKickSpans()){ const r=boKickRoute(s,bm); const cy=+r.low.toFixed(2);
      if(!r.type){ unreach.push({spline:spanName(s),kind:s.kind,cableHeight:cy,why:s.kind==="zip"?"zip line (boarded at its top end)":(r.low>BO_KICK.reach?"above 5-kick reach":"no wall within 4 m")}); continue; }
      const mid=s.pts[Math.floor(s.pts.length/2)], dn=boKickDistrict(mid.x,mid.z); let tx=mid.x, tz=mid.z; if(r.faces.length===2){ tx=r.faces.reduce((a,c)=>a+(c.minX+c.maxX)/4,0); tz=r.faces.reduce((a,c)=>a+(c.minZ+c.maxZ)/4,0); } // alley faces point at each other
      const fs=r.faces.map(c=>faceOf(c,tx,tz,spanName(s),dn));
      if(fs.length===2){ fs.forEach((e,k)=>{ const o=r.faces[1-k], c=r.faces[k], f=boKickFace(c,(o.minX+o.maxX)/2,(o.minZ+o.maxZ)/2); e.center=[+f.fx.toFixed(2),e.center[1],+f.fz.toFixed(2)]; e.normal=[f.nx,0,f.nz]; e.width=+f.width.toFixed(2); e.pairName=fs[1-k].name; });
        r.gap=+Math.max(r.faces[0].minX-r.faces[1].maxX,r.faces[1].minX-r.faces[0].maxX,r.faces[0].minZ-r.faces[1].maxZ,r.faces[1].minZ-r.faces[0].maxZ).toFixed(2); }
      routes.push({spline:spanName(s),splineId:s.id,cableHeight:+(r.cy||cy).toFixed(2),faces:fs.map(f=>f.name),type:r.type,status:"planned",gap:r.gap||null}); }
    // bridge stays/mains: listed separately (pylons/parapets are noKick, so normally unreachable)
    const bridge=GRIND.S.filter(s=>s.kind==="stay"||s.kind==="main").map(s=>{ const r=boKickRoute(s,bm); return {spline:"spline_"+s.id,kind:s.kind,low:+Math.min(...s.pts.map(p=>p.y)).toFixed(1),route:r.type||null}; });
    routes.sort((a,b)=>(a.type==="alley"?0:1)-(b.type==="alley"?0:1)||a.cableHeight-b.cableHeight); if(routes[0]&&routes[0].type==="alley"){ const r0=routes[0]; r0.designed=true; const [A,Bc]=r0.faces.map(n=>WK.find(w=>w.name===n).collider); const alongX=(A.maxX-A.minX)>(A.maxZ-A.minZ);
      const lo=alongX?Math.max(A.minX,Bc.minX):Math.max(A.minZ,Bc.minZ), hi=alongX?Math.min(A.maxX,Bc.maxX):Math.min(A.maxZ,Bc.maxZ), mid=alongX?((Math.min(A.maxZ,Bc.maxZ)+Math.max(A.minZ,Bc.minZ))/2):((Math.min(A.maxX,Bc.maxX)+Math.max(A.minX,Bc.minX))/2);
      for(const sd of [-1,1]){ const e=sd<0?lo:hi, st=e+sd*7.5; let ok=true; for(let t=0;t<=7.5;t+=.5){ const u=e+sd*t, x=alongX?u:mid, z=alongX?mid:u; if(colliders.some(c=>!c.off&&x>c.minX-.5&&x<c.maxX+.5&&z>c.minZ-.5&&z<c.maxZ+.5)||GRIND.S.some(g=>g.vert&&Math.hypot(g.pts[0].x-x,g.pts[0].z-z)<.8)){ ok=false; break; } }
        if(!ok) continue; const x=alongX?st:mid, z=alongX?mid:st, g=typeof WORLD_GROUND==="function"?WORLD_GROUND(x,z,0):null, hx=alongX?-sd:0, hz=alongX?0:-sd;
        r0.start={pos:[+x.toFixed(2),g?+g.y.toFixed(3):0,+z.toFixed(2)],heading:[hx,0,hz],yaw:+Math.atan2(hx,hz).toFixed(4),runUp:7.5,alleyEntry:+e.toFixed(2),alleyCenterline:+mid.toFixed(2)}; break; } }
    window.WALL_KICKS=WK; window.KICK_ROUTES=routes; window.KICK_UNREACHABLE=unreach; window.KICK_BRIDGE=bridge; S.kickSummary={faces:WK.length,routes:routes.length,unreach:unreach.length,noKick:nk,bridgeReach:bridge.filter(b=>b.route).length,bridgeTotal:bridge.length,walls:S.kick?S.kick.walls.length:0,warn:S.kick?S.kick.warn:[]}; }
  return S;
})();
