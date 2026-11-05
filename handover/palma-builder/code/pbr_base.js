// ===== PBR BUILDING BASE (Palma Builder, pbr_base.js via patch_pbr_base.py; layers on pbr_world.js, PBR path only) =====
// Ground-floor band (0..baseH, ~3.2-5 m) on the single instanced building ShaderMaterial, after pbr_world converted it: brick / poured concrete
// per kit, painted-steel I-beam columns + lintel, concrete fascia with inset sign panel, framed storefronts (env-cube glass + interior parallax
// card, lit at night), steel kick plate / concrete plinth, base grime + AO. Atlas page B (assets/pbr_base/pbrB_*, CC0 ambientCG, see SOURCES.txt).
// Shader-only: 0 new meshes / draws; colliders, WALL_PANELS, WALL_KICKS, tag spots untouched. OPT-IN: ?pbrbase=1 (needs the PBR world, so ?toon=1 / ?pbr=0 -> no-op). Contrast/scale pass 2026-11-05: larger masonry modules, thicker I-beams/frames, stronger brick mortar + glass + grime; distance-AA wall←col mix so beams/windows survive 15-40 m.
const PBR_BASE=(()=>{ const S={on:false,warn:[],stats:{}}; if(typeof PBR_WORLD==='undefined'||!PBR_WORLD.on||!/[?&]pbrbase=1(&|$)/.test(location.search)) return S; S.on=true; /* OPT-IN ?pbrbase=1 until Ani's look check + Oliver's before/after */
  const BASE='assets/pbr_base/', K2=window.SR_KTX2&&window.SR_KTX2.on, U={bA:{value:null},bN:{value:null},bO:{value:null}};
  function tex(n,u){ const t=new THREE.TextureLoader().load(BASE+n+'.jpg'); t.wrapS=t.wrapT=THREE.ClampToEdgeWrapping; t.anisotropy=8; t.generateMipmaps=true; t.minFilter=THREE.LinearMipmapLinearFilter; U[u].value=t; if(!K2) return;
    let tries=0; const go=()=>{ try{ const L=typeof window.SR_KTX2.loader==='function'&&window.SR_KTX2.loader(); if(!L){ if(++tries>300){ S.warn.push('ktx2 no loader '+n); return; } return requestAnimationFrame(go); }
      L.load(BASE+n+'.ktx2',c=>{ c.wrapS=c.wrapT=THREE.ClampToEdgeWrapping; c.anisotropy=8; c.minFilter=THREE.LinearMipmapLinearFilter; c.generateMipmaps=false; c.flipY=false; c.encoding=THREE.LinearEncoding; c.needsUpdate=true; U[u].value=c; S.stats['ktx2_'+n]=1; },undefined,()=>S.warn.push('ktx2 fallback jpg '+n)); }catch(e){ S.warn.push('ktx2 err '+n); } }; requestAnimationFrame(go); }
  tex('pbrB_albedo','bA'); tex('pbrB_nrm','bN'); tex('pbrB_orm','bO');
  const GL=`        /* pbr: BUILDING BASE (Palma 10/30): masonry (brick/poured concrete) + steel I-beam columns & lintel, framed storefronts (env glass + interior parallax), kick plate/plinth, grime+AO. 0 new draws */
        vec2 qB=vec2(vFace.x,y); vec2 qBx=dFdx(qB), qBy=dFdy(qB);
        if(!roof&&y<P1.z+.01&&y>-.3){
          float qW=max(vFace.y,1.), qs=clamp(vFace.x,0.,qW), qHb=P1.z, qnb=max(1.,floor(qW/(P0.x*2.05)+.5)), qbw=qW/qnb, qbi=min(floor(qs/qbw),qnb-1.), qbx=qs-qbi*qbw, qhb=h21(vec2(qbi,vSeed*3.1));
          bool qBrick=(k==2||k==3||k==6||fm==0||(k==5&&fract(vSeed*.37)<.5));
          float qL1=qHb-1.05, qL0=qL1-.42, qcw=.30, qdc=min(qbx,qbw-qbx), qPl=.48;
          vec3 qA,qN,qO,qSA,qSN,qSO; float qsc=qBrick?.95:1.7; vec2 qt=qBrick?vec2(0.,0.):vec2(1.,0.);
          PBB(qt,qB/qsc,qsc,qA,qN,qO); PBB(vec2(0.,1.),qB/.95,.95,qSA,qSN,qSO);
          vec3 qAc=max(vec3(0.),(qA-dot(qA,vec3(.33)))*1.75+dot(qA,vec3(.33))*(qBrick?mix(.42,1.22,smoothstep(.28,.52,dot(qA,vec3(.33)))):1.08)); vec3 qMas=qAc*(qBrick?mix(vec3(1.),vCol/max(dot(vCol,vec3(.3,.59,.11)),.08)*.55,.22)*1.05:vec3(.86,.84,.80))*(.88+.24*fract(vSeed*1.73));
          float qsl=dot(qSA,vec3(.3,.59,.11)); vec3 qSt=mix(vec3(.09,.10,.12),vec3(.48,.47,.44),smoothstep(.5,.88,qsl));   /* charcoal painted steel; contrast pass 11/05 for 15-40 m */
          float qSignIn=0.; vec3 qM=qMas; vec3 qNt=qN; float qRo=qO.g, qMe=0., qAO=qO.r, qE=0.; vec3 qEm=vec3(0.); bool qKeep=false;
          bool qCol=qdc<qcw, qLin=y>qL0&&y<qL1&&!qCol, qSign=y>=qL1&&y<qHb-.25&&!qCol, qTop=y>=qHb-.25&&!qCol;
          bool qSolid=qhb<.2||qbw<2.2;
          if(qCol){ float qd=qcw-qdc; qM=qSt; qNt=qSN; qRo=qSO.g*.9; qMe=.6;
            if(qd<.045) { qM*=1.9; qNt=vec3(.5+.42*(qdc<qbx?1.:-1.),.5,1.); } else if(qd<.08) qM*=.42; else { qM*=.78; qAO*=.72; }   /* flange edge catch-light, web shadow */
            if(abs(qd-.16)<.028&&fract(y/.5)<.11) qM*=1.85; }                                                                    /* bolt rows */
          else if(qLin){ float qe=min(y-qL0,qL1-y); qM=qSt*(qe<.05?1.75:qe<.08?.4:.88); qNt=qSN; qRo=qSO.g*.9; qMe=.65; qAO*=qe<.08?.8:1.; }
          else if(qSign){ vec3 fA,fN,fO; PBB(vec2(1.,0.),qB/2.2,2.2,fA,fN,fO); float sx=qbx/qbw, sy=(y-qL1)/(qHb-.25-qL1); bool ins=sx>.1&&sx<.9&&sy>.18&&sy<.82; qM=ins?vec3(.05,.05,.06):fA*.85; qNt=ins?vec3(.5,.5,1.):fN; qRo=ins?.3:fO.g; qMe=ins?.5:0.; if(!ins) emi=vec3(0.); qSignIn=ins?1.:0.; }
          else if(qTop){ vec3 tA,tN,tO; PBB(vec2(1.,0.),qB/2.2,2.2,tA,tN,tO); qM=tA*(y>qHb-.08?1.:.9)*(y<qHb-.2?.55:1.); qNt=tN; qRo=tO.g; }
          else if(y<qPl){ if(qSolid){ vec3 cA,cN,cO; PBB(vec2(1.,0.),qB/1.5,1.5,cA,cN,cO); qM=cA*.72; qNt=cN; qRo=cO.g; } else { vec3 kA,kN,kO; PBB(vec2(1.,1.),qB/.75,.75,kA,kN,kO); qM=kA*.68*(qPl-y<.04?1.85:1.); qNt=kN; qRo=kO.g*.75; qMe=.9; } }
          else {
            float ox=qbx-qcw, ow=qbw-2.*qcw, oy=y-qPl, oh=qL0-qPl, fw=.11; bool inG; float qfr=0.;
            if(qSolid){ float px=abs(ox-ow*.5), py=abs(oy-oh*.55); inG=px<ow*.28&&py<oh*.3; qfr=float(!inG&&px<ow*.28+.07&&py<oh*.3+.07); }
            else { float trn=min(2.45,oh-.45); float mul=ow>3.?abs(ox-ow*.5):99.; qfr=float(ox<fw||ox>ow-fw||oy>oh-fw||abs(oy-trn)<.045||mul<.04||(oy<fw)); inG=qfr<.5; }
            if(qfr>.5){ qM=qSt*.8; qNt=qSN; qRo=.35; qMe=.8; }
            else if(inG){
              vec3 T3=Tn, rd=vec3(dot(V,T3),V.y,dot(V,-n)); float rw=qSolid?ow*.56:ow, rh=qSolid?oh*.6:oh, qD=qSolid?2.4:3.6;
              vec3 ro=vec3(qSolid?ox-(ow*.5-rw*.5):ox, qSolid?oy-(oh*.55-rh*.5):oy, 0.); rd.z=max(rd.z,.02);
              float tx=rd.x>0.?(rw-ro.x)/rd.x:-ro.x/min(rd.x,-1e-4), ty=rd.y>0.?(rh-ro.y)/rd.y:-ro.y/min(rd.y,-1e-4), tz=qD/rd.z; float tt=min(tx,min(ty,tz)); vec3 hp=ro+rd*tt;
              float rn=h21(vec2(qbi+7.,vSeed)); vec3 wc=mix(vec3(.55,.5,.44),vec3(.42,.5,.55),step(.5,rn))*(.7+.3*h21(vec2(qbi,vSeed+5.)));
              vec3 ic; float lg=1.;
              if(tt==tz){ ic=wc*(.85+.15*smoothstep(0.,rh,hp.y)); if(hp.y<1.95&&hp.x>.35&&hp.x<rw-.35){ float sy=fract(hp.y/.5), shelf=smoothstep(.0,.04,sy)*smoothstep(.12,.06,sy); vec3 pc=.45+.3*cos(6.2832*(vec3(0.,.33,.67)+rn+hp.x*.35)); float pr=smoothstep(.15,.25,sy)*smoothstep(.95,.8,sy)*(.6+.4*sin(hp.x*9.+rn*20.)); ic=mix(ic,pc*.55,pr*.55); ic=mix(ic,vec3(.08),shelf*.9); } }
              else if(tt==ty){ ic=rd.y<0.?vec3(.16,.14,.12)*(.8+.4*step(.5,fract(floor(hp.x/.6)*.5+floor(hp.z/.6)*.5))):vec3(.75); if(rd.y>0.) lg=1.+3.*step(abs(fract(hp.z/1.2)-.5),.12)*step(abs(hp.x-rw*.5),rw*.35); }
              else ic=wc*.75;
              ic*=1.-.55*smoothstep(0.,qD,hp.z*.8);
              float on=step(rn,P1.y+.35); vec3 lc=mix(LIT,vec3(1.,.92,.8),.5);
              vec3 day=ic*.38*lg, night=ic*lc*(on*1.25+.08)*lg;
              vec3 inter=mix(night,day,uDay);
              vec3 gr=reflect(V,n); vec3 genv=textureCube(uEnv,vec3(-gr.x,gr.y,gr.z)).rgb; float gf=.06+.94*pow(1.-max(0.,dot(-V,n)),5.);
              vec3 gcol=mix(inter,genv*mix(.55,1.15,uDay),clamp(gf+.45*uDay,0.,1.));
              qE=1.; qM=gcol; qEm=night*(1.-uDay)*(1.-gf)*1.35; qAO=1.;
              float sm=step(.92,h21(vec2(floor(ox*3.),floor(oy*3.)+qbi)))*.05; qM+=sm;                   /* dirt smudges */
            } else { qM=qMas; }
          }
          if(!qKeep){
            vec2 qnx=(qNt.xy*2.-1.)*1.65; vec3 qpn=normalize(Tn*qnx.x+Bn*qnx.y+n*sqrt(max(.05,1.-dot(qnx,qnx))));
            float qdl=dot(qpn,uSun)-ndl, qdv=dot(qpn,-V)-dot(n,-V); float qsh=band*(1.+qdl*1.15+qdv*.85); qsh=mix(qsh,max(qsh,1.05),.55*uDay); vec3 qamb=textureCube(uEnv,vec3(-qpn.x,qpn.y,qpn.z)).rgb*.28*uDay;
            float qao=qAO*(1.-.55*exp(-y/.28))*(1.-.4*exp(-max(qdc-qcw,0.)/.1)*float(!qCol))*(1.-.32*exp(-max(qL0-y,0.)/.12)*float(y<qL0&&!qCol));
            float qg=exp(-y/.75)*.48+.28*smoothstep(.55,1.,h21(vec2(floor(qs*2.3),vSeed)))*smoothstep(1.6,0.,y);   /* base grime + splash; stronger for street read */
            if(qE<.5){ vec3 qrv=reflect(V,qpn); vec3 qen=textureCube(uEnv,vec3(-qrv.x,qrv.y,qrv.z)).rgb; float qsp=(1.-qRo)*(1.-qRo)*mix(.12,1.,qMe);
              col=qM*(1.-qg)*(qsh*nk+qamb)*qao+qen*qsp*mix(vec3(.05),qM*1.7,qMe)*.75; if(qSignIn<.5) emi=vec3(0.); }
            else { col=qM*mix(1.,qao,.5); emi=qEm; }
          }
          /* CRITICAL 11/05: facades distance-AA does o=mix(col, avg=wall*.7+..., aa).
             Old wall=flat masonry made beams/windows vanish at 15-40 m (the "too subtle" bug).
             Keep structured col in wall so AA preserves I-beams, frames, glass. */
          wall=mix(qMas*band*nk*.85, col, .92);
        }
`, DEF='#define PBB(T,UV,SCL,A,N,O) { vec2 f_=fract(UV); vec2 a_=(T*vec2(1.,-1.)+vec2(0.,1.)+PAD+f_*(1.-2.*PAD))*.5; vec2 g1_=qBx/SCL*.5*(1.-2.*PAD), g2_=qBy/SCL*.5*(1.-2.*PAD); A=texture2DGradEXT(pbrBA,a_,g1_,g2_).rgb; N=texture2DGradEXT(pbrBN,a_,g1_,g2_).rgb; O=texture2DGradEXT(pbrBO,a_,g1_,g2_).rgb; }';
  function patch(m){ const va='vY=wp.y-instanceMatrix[3].y;', a3='emi*=mix(1.,.25,uDay); float aa=', ua='uniform sampler2D uFA, uFN, pbrFA, pbrFN;';
    if(m.vertexShader.indexOf(va)<0||m.fragmentShader.indexOf(a3)<0||m.fragmentShader.indexOf(ua)<0){ S.warn.push('anchor'); return false; }
    m.uniforms.pbrBA=U.bA; m.uniforms.pbrBN=U.bN; m.uniforms.pbrBO=U.bO;
    m.vertexShader=m.vertexShader.replace('varying vec3 vWP,','varying vec2 vFace; varying vec3 vWP,').replace(va,va+' { vec3 isc=vec3(length(instanceMatrix[0].xyz),length(instanceMatrix[1].xyz),length(instanceMatrix[2].xyz)); vFace=abs(normal.x)>.5?vec2((.5+position.z*sign(normal.x))*isc.z,isc.z):vec2((.5-position.x*sign(normal.z))*isc.x,isc.x); }');
    m.fragmentShader=m.fragmentShader.replace('varying vec3 vWP, vN, vCol;','varying vec2 vFace; varying vec3 vWP, vN, vCol;').replace(ua,'uniform sampler2D uFA, uFN, pbrFA, pbrFN, pbrBA, pbrBN, pbrBO;\n      '+DEF+'\n      ').replace(a3,GL+'        '+a3);
    m.userData.pbrBase=1; m.needsUpdate=true; return true; }
  let n=0; (function loop(){ let found=false; try{ if(typeof scene!=='undefined'&&scene) scene.traverse(o=>{ const m=o.material; if(!o.isMesh||!m||!m.isShaderMaterial||!m.uniforms||!m.uniforms.uFA) return; found=true;
      if(m.userData.pbrWorld==='facade'&&!m.userData.pbrBase){ if(patch(m)) S.stats.facade=(S.stats.facade||0)+1; } }); }catch(e){ S.warn.push('patch '+e); }
    if(S.stats.facade||++n>3600) return; requestAnimationFrame(loop); })();
  return S; })();
