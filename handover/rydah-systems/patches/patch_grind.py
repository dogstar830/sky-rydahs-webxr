# Locked-in grind (grind.js): thick textured cables/poles/bridge cables, palm trunk + frond splines, spline lock/ride/pop, FX.
# Runs just before patch_phone.py in build_ikki.sh (needs wallatk + pad hooks; phone controls text patched at runtime via PH_CTRL).
f=__import__('os').environ.get('SR_HTML','/workspace/v3build/sky-rydahs-v3-ikki.html'); src=open(f).read(); js=open('/workspace/v3build/grind.js').read()
if 'const GRIND={' in src: print("patch_grind: already applied"); raise SystemExit
def rep(a,b):
    global src
    assert src.count(a)==1, ("patch_grind anchor",a[:70],src.count(a)); src=src.replace(a,b)
rep("// ===== LOOP =====",js+"\n// ===== LOOP =====")
rep("let w=false; try{ w=wallStep(dt); }","let w=false; try{ w=grindStep(dt)||wallStep(dt); }")
R='  if(FX.on&&!xr&&!window.__noFX) FX.composer.render(); else renderer.render(scene,camera);'
rep(R,'  if(window.grindTick) grindTick(dt,xr);\n'+R)
rep("function sagWire(a,b,sag){ ","function sagWire(a,b,sag){ grindWire(a,b,sag); ")
rep('scene.add(new THREE.LineSegments(wg,new THREE.LineBasicMaterial({color:0x14141c})));','grindBuildCables();')
rep('det("cyl",x,5.2,z,.3,10.4,.3,0x5a4632);','grindPole(x,z,10.4,.17,"wood");')
rep('det("cyl",x,4.5,z,.22,9,.22,0x6a6e78);','grindPole(x,z,9,.12,"galv");')
rep('g.add(new THREE.LineSegments(cg,new THREE.LineBasicMaterial({color:new THREE.Color(b.color).lerp(new THREE.Color(0xffffff),.35)})));','grindBridgeSeg(seg,g,b);')
rep('const g=new THREE.BufferGeometry(); g.setAttribute("position",new THREE.Float32BufferAttribute([90,30,-360,-100,3,-246, 90,30,-360,90,9,-360],3)); scene.add(new THREE.LineSegments(g,new THREE.LineBasicMaterial({color:0xFFD700})));',
    'grindZip([90,30,-360],[-100,3,-246]); GRIND.tubes.hanger.push({pts:[new THREE.Vector3(90,30,-360),new THREE.Vector3(90,9,-360)],r:.07});')
rep('det("cyl",x,h/2,z,.55,h,.55,0xa8a49a);','det("cyl",x,h/2,z,.55,h,.55,0xa8a49a); grindTrunk(x,z,x,h+1.8,z,.3,0);')
rep('for(let k=0;k<9;k++){ const a=k/9*Math.PI*2; det("cone",x+Math.sin(a)*1.6,h+1.7','for(let k=0;k<9;k++){ const a=k/9*Math.PI*2; if(k%3===0) grindFrond(x,h+1.7,z,a,3.6); det("cone",x+Math.sin(a)*1.6,h+1.7')
rep('const tx=x+lx*h, tz=z+lz*h;','const tx=x+lx*h, tz=z+lz*h; grindTrunk(x,z,tx,h,tz,.24,1);')
rep('for(let k=0;k<8;k++){ const a=k/8*Math.PI*2; det("cone",tx+Math.sin(a)*1.7','for(let k=0;k<8;k++){ const a=k/8*Math.PI*2; if(k%2===0) grindFrond(tx,h-.1,tz,a,3.4); det("cone",tx+Math.sin(a)*1.7')
rep('const tx=x-Math.sin(lean)*h/2*1.0, ty=h;','const tx=x-Math.sin(lean)*h/2*1.0, ty=h; grindTrunk(x,z,tx,h,z,.24,1);')
rep('new THREE.CylinderGeometry(.07,.07,len,6),toon(0xc0c0d0)','new THREE.CylinderGeometry(.09,.09,len,8),toon(0xc0c0d0)')
rep('if(Math.hypot(p.x-qx,p.z-qz)<.7&&R.speed>5&&t>0&&t<1)','if(!window.GRIND&&Math.hypot(p.x-qx,p.z-qz)<.7&&R.speed>5&&t>0&&t<1)')
open(f,'w').write(src); print("patch_grind ok")
