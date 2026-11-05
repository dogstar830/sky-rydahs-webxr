        /* pbr: BUILDING BASE (Palma 10/30): masonry (brick/poured concrete) + steel I-beam columns & lintel, framed storefronts (env glass + interior parallax), kick plate/plinth, grime+AO. 0 new draws */
        vec2 qB=vec2(vFace.x,y); vec2 qBx=dFdx(qB), qBy=dFdy(qB);
        if(!roof&&y<P1.z+.01&&y>-.3){
          float qW=max(vFace.y,1.), qs=clamp(vFace.x,0.,qW), qHb=P1.z, qnb=max(1.,floor(qW/(P0.x*1.6)+.5)), qbw=qW/qnb, qbi=min(floor(qs/qbw),qnb-1.), qbx=qs-qbi*qbw, qhb=h21(vec2(qbi,vSeed*3.1));
          bool qBrick=(k==2||k==3||k==6||fm==0||(k==5&&fract(vSeed*.37)<.5));
          float qL1=qHb-1.05, qL0=qL1-.34, qcw=.21, qdc=min(qbx,qbw-qbx), qPl=.38;
          vec3 qA,qN,qO,qSA,qSN,qSO; float qsc=qBrick?1.4:2.6; vec2 qt=qBrick?vec2(0.,0.):vec2(1.,0.);
          PBB(qt,qB/qsc,qsc,qA,qN,qO); PBB(vec2(0.,1.),qB/1.1,1.1,qSA,qSN,qSO);
          vec3 qMas=qA*(qBrick?mix(vec3(1.),vCol/max(dot(vCol,vec3(.3,.59,.11)),.08)*.45,.18)*.95:vec3(.78,.77,.74))*(.9+.2*fract(vSeed*1.73));
          float qsl=dot(qSA,vec3(.3,.59,.11)); vec3 qSt=mix(vec3(.075,.08,.09),vec3(.38,.38,.36),smoothstep(.55,.85,qsl));   /* charcoal painted steel, chips from the texture */
          vec3 qM=qMas; vec3 qNt=qN; float qRo=qO.g, qMe=0., qAO=qO.r, qE=0.; vec3 qEm=vec3(0.); bool qKeep=false;
          bool qCol=qdc<qcw, qLin=y>qL0&&y<qL1&&!qCol, qSign=y>=qL1&&y<qHb-.25&&!qCol, qTop=y>=qHb-.25&&!qCol;
          bool qSolid=qhb<.2||qbw<2.2;
          if(qCol){ float qd=qcw-qdc; qM=qSt; qNt=qSN; qRo=qSO.g*.9; qMe=.6;
            if(qd<.035) { qM*=1.55; qNt=vec3(.5+.35*(qdc<qbx?1.:-1.),.5,1.); } else if(qd<.06) qM*=.55; else { qM*=.82; qAO*=.8; }   /* flange edge catch-light, web shadow */
            if(abs(qd-.13)<.022&&fract(y/.45)<.09) qM*=1.6; }                                                                    /* bolt rows */
          else if(qLin){ float qe=min(y-qL0,qL1-y); qM=qSt*(qe<.04?1.5:qe<.065?.55:.85); qNt=qSN; qRo=qSO.g*.9; qMe=.6; qAO*=qe<.065?.85:1.; }
          else if(qSign) qKeep=true;
          else if(qTop) qM=qMas*.82;
          else if(y<qPl){ if(qSolid){ vec3 cA,cN,cO; PBB(vec2(1.,0.),qB/2.,2.,cA,cN,cO); qM=cA*.62; qNt=cN; qRo=cO.g; } else { vec3 kA,kN,kO; PBB(vec2(1.,1.),qB/.9,.9,kA,kN,kO); qM=kA*.55*(qPl-y<.03?1.6:1.); qNt=kN; qRo=kO.g*.8; qMe=.85; } }
          else {
            float ox=qbx-qcw, ow=qbw-2.*qcw, oy=y-qPl, oh=qL0-qPl, fw=.075; bool inG; float qfr=0.;
            if(qSolid){ float px=abs(ox-ow*.5), py=abs(oy-oh*.55); inG=px<ow*.28&&py<oh*.3; qfr=float(!inG&&px<ow*.28+.07&&py<oh*.3+.07); }
            else { float trn=min(2.45,oh-.45); float mul=ow>3.?abs(ox-ow*.5):99.; qfr=float(ox<fw||ox>ow-fw||oy>oh-fw||abs(oy-trn)<.045||mul<.04||(oy<fw)); inG=qfr<.5; }
            if(qfr>.5){ qM=qSt*.8; qNt=qSN; qRo=.35; qMe=.8; }
            else if(inG){
              vec3 T3=Tn, rd=vec3(dot(V,T3),V.y,dot(V,-n)); float rw=qSolid?ow*.56:ow, rh=qSolid?oh*.6:oh, qD=qSolid?2.4:3.6;
              vec3 ro=vec3(qSolid?ox-(ow*.5-rw*.5):ox, qSolid?oy-(oh*.55-rh*.5):oy, 0.); rd.z=max(rd.z,.02);
              float tx=rd.x>0.?(rw-ro.x)/rd.x:-ro.x/min(rd.x,-1e-4), ty=rd.y>0.?(rh-ro.y)/rd.y:-ro.y/min(rd.y,-1e-4), tz=qD/rd.z; float tt=min(tx,min(ty,tz)); vec3 hp=ro+rd*tt;
              float rn=h21(vec2(qbi+7.,vSeed)); vec3 wc=mix(vec3(.55,.5,.44),vec3(.42,.5,.55),step(.5,rn))*(.7+.3*h21(vec2(qbi,vSeed+5.)));
              vec3 ic; float lg=1.;
              if(tt==tz){ ic=wc; float sh=fract(hp.y/.55); if(hp.y<1.9&&hp.x>.4&&hp.x<rw-.4){ ic=mix(ic*.35,vec3(h21(floor(hp.xy*vec2(3.,1.8))+rn),h21(floor(hp.xy*vec2(3.,1.8))+rn+1.),.6)*.7,step(.18,sh)*step(sh,.8)*.8); } }
              else if(tt==ty){ ic=rd.y<0.?vec3(.16,.14,.12)*(.8+.4*step(.5,fract(floor(hp.x/.6)*.5+floor(hp.z/.6)*.5))):vec3(.75); if(rd.y>0.) lg=1.+3.*step(abs(fract(hp.z/1.2)-.5),.12)*step(abs(hp.x-rw*.5),rw*.35); }
              else ic=wc*.75;
              ic*=1.-.55*smoothstep(0.,qD,hp.z*.8);
              float on=step(rn,P1.y+.35); vec3 lc=mix(LIT,vec3(1.,.92,.8),.5);
              vec3 day=ic*.32*lg, night=ic*lc*(on*1.1+.06)*lg;
              vec3 inter=mix(night,day,uDay);
              vec3 gr=reflect(V,n); vec3 genv=textureCube(uEnv,vec3(-gr.x,gr.y,gr.z)).rgb; float gf=.06+.94*pow(1.-max(0.,dot(-V,n)),5.);
              vec3 gcol=mix(inter,genv*mix(.5,1.,uDay),clamp(gf+.12*uDay,0.,1.));
              qE=1.; qM=gcol; qEm=night*(1.-uDay)*(1.-gf)*1.1; qAO=1.;
              float sm=step(.92,h21(vec2(floor(ox*3.),floor(oy*3.)+qbi)))*.05; qM+=sm;                   /* dirt smudges */
            } else { qM=qMas; }
          }
          if(!qKeep){
            vec2 qnx=(qNt.xy*2.-1.)*1.2; vec3 qpn=normalize(Tn*qnx.x+Bn*qnx.y+n*sqrt(max(.05,1.-dot(qnx,qnx))));
            float qdl=dot(qpn,uSun)-ndl, qdv=dot(qpn,-V)-dot(n,-V); float qsh=band*(1.+qdl*.9+qdv*.7);
            float qao=qAO*(1.-.45*exp(-y/.32))*(1.-.3*exp(-max(qdc-qcw,0.)/.12)*float(!qCol))*(1.-.25*exp(-max(qL0-y,0.)/.15)*float(y<qL0&&!qCol));
            float qg=exp(-y/.9)*.35+.2*smoothstep(.6,1.,h21(vec2(floor(qs*2.3),vSeed)))*smoothstep(1.4,0.,y);   /* base grime + splash */
            if(qE<.5){ vec3 qrv=reflect(V,qpn); vec3 qen=textureCube(uEnv,vec3(-qrv.x,qrv.y,qrv.z)).rgb; float qsp=(1.-qRo)*(1.-qRo)*mix(.1,.9,qMe);
              col=qM*(1.-qg)*qsh*nk*qao+qen*qsp*mix(vec3(.04),qM*1.5,qMe)*.6; emi=vec3(0.); }
            else { col=qM*mix(1.,qao,.5); emi=qEm; }
          }
          wall=qMas*band*nk*.85;
        }
