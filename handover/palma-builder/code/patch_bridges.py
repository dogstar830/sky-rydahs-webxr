# Full bridge structures (bridges.js). Runs after patch_facades, before patch_grind. Additive: grind cables untouched.
f='/workspace/v3build/sky-rydahs-v3-ikki.html'; src=open(f).read(); js=open('/workspace/v3build/bridges.js').read()
def rep(a,b):
    global src
    assert src.count(a)==1, ("anchor",a[:70],src.count(a)); src=src.replace(a,b)
rep('function createBridge(b){', js+'\nfunction createBridge(b){')
rep('PALMA.bridges.forEach(createBridge);', 'PALMA.bridges.forEach(createBridge); PALMA.bridges.forEach(BRIDGES.build);')
rep('buildInstances(); buildHalos();', 'buildInstances(); BRIDGES.finish(); buildHalos();')
open(f,'w').write(src); print("patch_bridges ok")
