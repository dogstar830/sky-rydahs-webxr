# Facade material atlas (facades.js) wired into the single instanced building ShaderMaterial. Runs after patch_asphalt/wardrobe, before patch_phone.
import base64
f='/workspace/v3build/sky-rydahs-v3-ikki.html'; src=open(f).read(); js=open('/workspace/v3build/facades.js').read()
for n,k in [('albedo','__FACADE_ALB__'),('nr','__FACADE_NR__')]:
    js=js.replace(k,'data:image/jpeg;base64,'+base64.b64encode(open(f'/workspace/v3build/textures/facade_{n}.jpg','rb').read()).decode())
def rep(a,b):
    global src
    assert src.count(a)==1, ("anchor",a[:70],src.count(a)); src=src.replace(a,b)
rep('function buildInstancedBuildings(){', js+'\nfunction buildInstancedBuildings(){ if(typeof ikkiEnv==="function") FACADE.uniforms.uEnv.value=ikkiEnv();')
rep('const aKit=new Float32Array(n), aSeed=new Float32Array(n);','const aKit=new Float32Array(n), aSeed=new Float32Array(n), aMat=new Float32Array(n); ig.setAttribute("aMat",new THREE.InstancedBufferAttribute(aMat,1));')
rep('aKit[i]=k; aSeed[i]=rr()*100;','aKit[i]=k; aSeed[i]=rr()*100; aMat[i]=FACADE.pick(k,h,x,z);')
rep("fog:true, extensions:{derivatives:true}, uniforms:Object.assign({ uP0:","fog:true, extensions:{derivatives:true,shaderTextureLOD:true}, uniforms:Object.assign(FACADE.uniforms,{ uP0:")
rep("vertexShader:`attribute float aKit; attribute float aSeed; varying vec3 vWP, vN, vCol; varying float vKit, vSeed, vH, vY;",
    "vertexShader:`attribute float aKit; attribute float aSeed; attribute float aMat; varying float vMat; varying vec3 vWP, vN, vCol; varying float vKit, vSeed, vH, vY;")
rep("vKit=aKit; vSeed=aSeed;","vKit=aKit; vSeed=aSeed; vMat=aMat;")
rep("uniform vec3 uSun, uSkyA, uSkyB; uniform float uTime;\n",
    "uniform vec3 uSun, uSkyA, uSkyB; uniform float uTime; uniform sampler2D uFA, uFN; uniform vec4 uFT[8]; uniform samplerCube uEnv; uniform float uDay; varying float vMat;\n")
FRAG=r"""
        // --- FACADE MATERIAL: world-space box UVs into the 4x2 atlas, explicit gradients so tile wrap has no mip seams
        int fm=int(vMat+.5); vec4 ft=uFT[0]; for(int i=0;i<8;i++){ if(i==fm) ft=uFT[i]; }
        bool roof=abs(n.y)>.5; vec2 tuv=(roof?vWP.xz:vec2(u,vWP.y))/ft.z; const float PAD=.012; vec2 SC=vec2(.25,.5)*(1.-2.*PAD);
        vec2 auv=(ft.xy-vec2(0.,1.)+PAD+fract(tuv)*(1.-2.*PAD))*vec2(.25,.5); vec2 gx=dFdx(tuv)*SC, gy=dFdy(tuv)*SC;
        vec3 alb=texture2DGradEXT(uFA,auv,gx,gy).rgb; vec3 nr=texture2DGradEXT(uFN,auv,gx,gy).rgb;
        vec3 Tn=roof?vec3(1.,0.,0.):(abs(n.x)>.5?vec3(0.,0.,sign(n.x)):vec3(-sign(n.z),0.,0.)); vec3 Bn=roof?vec3(0.,0.,-1.):vec3(0.,1.,0.);
        vec2 nxy=(nr.xy*2.-1.)*1.3; vec3 pn=normalize(Tn*nxy.x+Bn*nxy.y+n*sqrt(max(.05,1.-dot(nxy,nxy)))); float rough=nr.b;
        float lv=max(dot(vCol,vec3(.3,.59,.11)),.08); vec3 tint=mix(vec3(1.),vCol/lv*.85,clamp(ft.w*4.,0.,1.)*.25);
        vec3 base=fm==6?alb*vCol*1.35:alb*tint;                                              // stucco takes the pastel building colour
        float bv=.86+.28*fract(vSeed*1.73); base*=bv;                                         // per-building tone variation
        if(fm==0){ vec2 bc=floor(vec2(u/.215,y/.075)+vec2(step(1.,mod(floor(y/.075),2.))*.5,0.)); base*=.88+.24*h21(bc+vSeed); } // varied brick tones
        if(fm<3||fm==7){ float g=exp(-y/2.2)*.3+.18*smoothstep(.55,1.,h21(vec2(floor(u*1.3),vSeed)))*fract(-y/P0.y); base*=1.-g; } // base grime + rain streaks
        float dl=dot(pn,uSun)-dot(n,uSun), dv=dot(pn,-V)-dot(n,-V); float shade=band*(1.+dl*.9+dv*.7);
        float nk=mix(.62,1.05,uDay);                                                          // night grade: keep facades low so neon carries
        vec3 rv=reflect(V,pn); vec3 envc=textureCube(uEnv,vec3(-rv.x,rv.y,rv.z)).rgb; float fres=.04+.96*pow(1.-max(0.,dot(-V,pn)),5.);
        float spec=(1.-rough)*(1.-rough)*(fm==3||fm==7?.9:fm==4||fm==5?.55:.12);
        vec3 wall=base*shade*nk+envc*spec*(fm==3||fm==7?base*1.6:vec3(mix(fres,1.,.25)))*.7, col=wall, emi=vec3(0.);
        sky=mix(sky,envc*1.3+sky*.3,.55);                                                     // glass reflects the shared ikkiEnv cube
"""
rep("vec3 wall=vCol*band, col=wall, emi=vec3(0.);", FRAG.strip())
# glass sampling the real env (flat glass normal, not the wall normal)
rep("if(abs(n.y)>.5){ col=vCol*.5; }","if(abs(n.y)>.5){ col=wall*.6; }")
# window frames / sills as trim around punched windows (light cast-stone on brick, steel elsewhere); curtain-wall mullions = brushed metal
rep("else { col=wall; if(P1.x<.5){","else { col=wall; float frm=step(abs(f.x-.5),P0.z*.5+.035)*step(abs(f.y-.55),P0.w*.5+.045); if(P1.x<.5&&frm>.5){ col=(fm==0||fm==6?vec3(.82,.79,.74):vec3(.55,.57,.6))*band*nk*(1.+dl*.5); } if(P1.x<.5){")
# emissive window masks: night only; daytime glass reads as reflection
rep("float aa=clamp(max(fwidth(u),fwidth(y))/max(.5,P0.x*.35)-.15,0.,1.);","emi*=mix(1.,.25,uDay); float aa=clamp(max(fwidth(u),fwidth(y))/max(.5,P0.x*.35)-.15,0.,1.);")
open(f,'w').write(src); print("patch_facades ok")
