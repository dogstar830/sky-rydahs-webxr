p='/workspace/v3build/pbr_world.js'; s=open(p).read()
g=open('/tmp/bb_glsl.txt').read()
assert '`' not in g and '${' not in g
# 1 textures
a="const U={ gA:{value:null}, gN:{value:null}, gO:{value:null}, fA:{value:null}, fN:{value:null} };"
assert s.count(a)==1; s=s.replace(a,"const U={ gA:{value:null}, gN:{value:null}, gO:{value:null}, fA:{value:null}, fN:{value:null}, bA:{value:null}, bN:{value:null}, bO:{value:null} }; /* bX: building-base page B (assets/pbr_base) */")
a="tex('pbrF_nrm','fN');"; assert s.count(a)==1; s=s.replace(a,a+" tex('../pbr_base/pbrB_albedo','bA'); tex('../pbr_base/pbrB_nrm','bN'); tex('../pbr_base/pbrB_orm','bO');")
# 2 facade shader: uniforms, vertex varying, fragment block
a="      m.uniforms.pbrFA=U.fA; m.uniforms.pbrFN=U.fN;"; assert s.count(a)==1
s=s.replace(a,a+"""
      m.uniforms.pbrBA=U.bA; m.uniforms.pbrBN=U.bN; m.uniforms.pbrBO=U.bO;
      { let v=m.vertexShader; const va='vY=wp.y-instanceMatrix[3].y;'; if(v.indexOf(va)<0) S.warn.push('base vtx anchor'); else { m.vertexShader=v.replace('varying vec3 vWP,','varying vec2 vFace; varying vec3 vWP,').replace(va,va+' { vec3 isc=vec3(length(instanceMatrix[0].xyz),length(instanceMatrix[1].xyz),length(instanceMatrix[2].xyz)); vFace=abs(normal.x)>.5?vec2((.5+position.z*sign(normal.x))*isc.z,isc.z):vec2((.5-position.x*sign(normal.z))*isc.x,isc.x); }'); } }""")
a="      { const a2='vec3 o=mix(col*.92+emi*.62,avg,aa*.85);';"; assert s.count(a)==1
s=s.replace(a,"""      { const a3='emi*=mix(1.,.25,uDay); float aa='; if(f.indexOf(a3)<0) S.warn.push('base frag anchor'); else { f=f.replace('varying vec3 vWP, vN, vCol;','varying vec2 vFace; varying vec3 vWP, vN, vCol;').replace('uniform sampler2D uFA, uFN, pbrFA, pbrFN;','uniform sampler2D uFA, uFN, pbrFA, pbrFN, pbrBA, pbrBN, pbrBO;\\n      #define PBB(T,UV,SCL,A,N,O) { vec2 f_=fract(UV); vec2 a_=(T*vec2(1.,-1.)+vec2(0.,1.)+PAD+f_*(1.-2.*PAD))*.5; vec2 g1_=qBx/SCL*.5*(1.-2.*PAD), g2_=qBy/SCL*.5*(1.-2.*PAD); A=texture2DGradEXT(pbrBA,a_,g1_,g2_).rgb; N=texture2DGradEXT(pbrBN,a_,g1_,g2_).rgb; O=texture2DGradEXT(pbrBO,a_,g1_,g2_).rgb; }').replace(a3,`"""+g.replace('\\','\\\\')+"""        `+a3); st.conv.bldg_base=1; } }
"""+a)
open(p,'w').write(s); print('ok')
