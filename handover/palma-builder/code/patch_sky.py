# Sky follows day/night (sky.js). Runs right after patch_bridges.
f='/workspace/v3build/sky-rydahs-v3-ikki.html'; src=open(f).read(); js=open('/workspace/v3build/sky.js').read()
def rep(a,b):
    global src
    assert src.count(a)==1, ("anchor",a[:70],src.count(a)); src=src.replace(a,b)
rep('function createSky(){', js+'\nfunction createSky(){')
rep('uniforms:{uTime:TOONU.uTime,uTint:SKYTINT},', 'uniforms:{uTime:TOONU.uTime,uTint:SKYTINT,uDay:SKY.u},')
rep('varying vec3 vD; uniform float uTime; uniform vec3 uTint;', 'varying vec3 vD; uniform float uTime; uniform vec3 uTint; uniform float uDay;')
rep("""        gl_FragColor=vec4(c,1.); }` });""",
"""        vec3 dz=vec3(.227,.482,.835), dm=vec3(.471,.682,.91), dh=vec3(.812,.89,.949);        // Gulf Coast day: #3A7BD5 / #78AEE8 / #CFE3F2
        vec3 d=mix(dh,dm,smoothstep(0.,.25,y)); d=mix(d,dz,smoothstep(.25,.85,y));
        vec3 sd=normalize(vec3(.45,.8,.35)); float sun=max(dot(vD,sd),0.); d+=vec3(1.,.965,.878)*(smoothstep(.9985,.9992,sun)*1.5+pow(sun,64.)*.35);
        if(y<0.) d=mix(d,vec3(.55,.68,.78),smoothstep(0.,-.1,y));
        gl_FragColor=vec4(mix(c,d,uDay),1.); }` });""")
rep('scene.add(sky); animated.push(()=>sky.position.copy(camera.getWorldPosition(_skyv)));',
    'scene.add(sky); animated.push(()=>{ sky.position.copy(camera.getWorldPosition(_skyv)); SKY.tick(); });')
rep('moon.scale.set(90,90,1); scene.add(moon);','moon.scale.set(90,90,1); scene.add(moon); SKY.hookMoon(moon.material);')
open(f,'w').write(src); print("patch_sky ok")
