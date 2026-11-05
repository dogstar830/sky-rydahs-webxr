import sys; sys.path.insert(0,'/workspace/forge_kit/gr8/fix'); from glbio import *
f=sys.argv[1]; j,b=load(f); W=worlds(j); sk=j['skins'][0]; jn=[j['nodes'][i]['name'] for i in sk['joints']]
p=j['meshes'][0]['primitives'][0]; P=acc(j,b,p['attributes']['POSITION']); UV=acc(j,b,p['attributes']['TEXCOORD_0'])
J=acc(j,b,p['attributes']['JOINTS_0']).astype(int); Wt=acc(j,b,p['attributes']['WEIGHTS_0'])
IBM=acc(j,b,sk['inverseBindMatrices']).reshape(-1,4,4).transpose(0,2,1)
pos=lambda n: np.linalg.inv(IBM[jn.index('mixamorig:'+n)])[:3,3]
def wsum(names):
    ids=[jn.index(n) for n in jn if any(n.endswith(x) for x in names)]
    return sum(Wt[:,k]*np.isin(J[:,k],ids) for k in range(4))
top=P[UV[:,0]<.75][:,1].max()
for sd,sg in (('Left',1),('Right',-1)):
    hand=[sd+'Hand'+x for x in ['','Thumb1','Thumb2','Thumb3','Thumb4','Index1','Index2','Index3','Index4','Middle1','Middle2','Middle3','Middle4','Ring1','Ring2','Ring3','Ring4','Pinky1','Pinky2','Pinky3','Pinky4']]
    wh=wsum(hand); wf=wsum([sd+'ForeArm',sd+'ForeArmTwist']); wu=wsum([sd+'Arm',sd+'ArmTwist'])
    S,E,Wr=pos(sd+'Arm'),pos(sd+'ForeArm'),pos(sd+'Hand')
    hv=P[(wh>.5)&(UV[:,0]<.75)]; tip=hv[np.argmin(hv[:,1])]
    ax=(tip-E)/np.linalg.norm(tip-E); arm=P[((wf+wh)>.5)&(UV[:,0]<.75)]; t=(arm-E)@ax
    prof=[]
    for tt in np.arange(0.05,np.linalg.norm(tip-E)-0.06,0.01):
        q=arm[(t>=tt)&(t<tt+.01)]
        if len(q)<8: continue
        c=q.mean(0); r=np.linalg.norm((q-c)-np.outer((q-c)@ax,ax),axis=1); prof.append((tt,np.percentile(r,50)))
    prof=np.array(prof); wi=prof[np.argmin(prof[:,1]+ (prof[:,0]<0.15)*9)]   # narrowest = wrist
    wrist=E+ax*wi[0]
    print(f'{sd}: shoulderJ {S.round(3)} elbowJ {E.round(3)} handJ {Wr.round(3)} mesh wrist(narrowest) {wrist.round(3)} r {wi[1]:.3f} fingertip {tip.round(3)}')
    print(f'   upper(J) {np.linalg.norm(E-S):.3f} fore(J) {np.linalg.norm(Wr-E):.3f} fore(mesh elbowJ->wrist) {wi[0]:.3f} hand(mesh wrist->tip) {np.linalg.norm(tip-wrist):.3f} arm(shoulderJ->tip) {np.linalg.norm(tip-S):.3f}')
print('top',top.round(3),'hips',pos('Hips').round(3),'UpLeg',pos('LeftUpLeg').round(3),'knee',pos('LeftLeg').round(3),'ankle',pos('LeftFoot').round(3),'toe',pos('LeftToeBase').round(3))
