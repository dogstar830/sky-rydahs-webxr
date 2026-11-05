// team jacket: Meshy texture's purple jacket texels are hue-remapped to Kogarasumaru cyan (value kept, so folds/shading survive)
const IKKI_JACKET_GLSL=`{ vec3 q=diffuseColor.rgb; float mx=max(q.r,max(q.g,q.b)), mn=min(q.r,min(q.g,q.b)), sat=(mx-mn)/max(mx,1e-3);
   float purple=step(q.g,min(q.r,q.b))*step(q.r*.55,q.b)*smoothstep(.18,.32,sat)*step(.08,mx);  // blue-dominant-or-magenta with low green = jacket purple
   vec3 cy=uJacketC*(mx*1.35); diffuseColor.rgb=mix(q,mix(cy,vec3(mn*.6),.15),purple*(1.-fSk)*smoothstep(.86,.92,vRestY)*(1.-smoothstep(1.44,1.48,vRestY))); }`  // torso+arms band only: pants keep Meshy purple;
// AT e-blade materials by module id: 1 lacquer shell, 2 crew-cyan plate, 3 chrome, 4 brushed alloy, 5 cyan glow, 6 tyre, 7 heel thruster, 8 strap/cable, 9 buckle, 10 panel line
const IKKI_AT_MAT=`float sid=floor(vFlag.r*16.+.5); float fSk=step(.5,sid); float atChrome=float(sid==3.||sid==9.), atBrushed=float(sid==4.), atShell=float(sid==1.||sid==2.), atGlow=float(sid==5.||sid==7.);
  vec3 atC=sid==1.?vec3(.10,.105,.14):sid==2.?uJacketC*.8:sid==3.?vec3(.82,.86,.92):sid==4.?vec3(.42,.45,.52):sid==6.?vec3(.05,.05,.065):sid==8.?vec3(.035,.035,.045):sid==9.?vec3(.85,.88,.92):sid==10.?vec3(.01,.01,.02):diffuseColor.rgb;
  diffuseColor.rgb=mix(diffuseColor.rgb,atC,fSk);
  float led=.75+.25*sin(uTime*9.-vRestY*90.);                                   // LED strips chase
  float arc=step(.82,fract(sin(floor(uTime*24.)*17.3+vRestY*400.)*43758.5))*uBoost;   // boost: crackling arcs on the thruster core
  vec3 atEmit=sid==7.?mix(uGlowC*.35,vec3(.8,1.,1.)*2.6,clamp(uBoost*1.2+arc,0.,1.)):uGlowC*(1.25+uBoost*1.4)*led;`;
const IKKI_AT_VERT=(vs,toon)=>vs.replace('#include <common>','#include <common>\n attribute vec4 color; attribute vec3 _wc; attribute vec3 _wa; uniform float uSpin; uniform float uComp;'+(toon?' varying vec3 vFlag; varying float vRestY;':'')+'\n vec3 atSpin(vec3 v,vec3 k,float a){ return v*cos(a)+cross(k,v)*sin(a)+k*dot(k,v)*(1.-cos(a)); }')
  .replace('#include <beginnormal_vertex>','#include <beginnormal_vertex>\n bool atW=dot(_wa,_wa)>.25; if(atW) objectNormal=atSpin(objectNormal,_wa,uSpin);')
  .replace('#include <begin_vertex>','#include <begin_vertex>\n'+(toon?' vFlag=color.rgb; vRestY=position.y;':'')+' if(atW) transformed=_wc+atSpin(transformed-_wc,_wa,uSpin); transformed.y+=color.g*uComp;');
const IKKI_DECK_REST=.152; // AT module scaled to the Meshy shoe (k~1.33): ground -> sole height in rest units
// small procedural neon environment for PBR reflections (one PMREM, cached): night sky gradient + cyan/white/magenta light strips
let _ikkiEnv=null; function ikkiEnv(){ if(_ikkiEnv) return _ikkiEnv; // 6 small canvas faces -> CubeTexture (PMREM output blew out to white under swiftshader/r128); night gradient + neon strips
  const face=(i)=>{ const cv=document.createElement('canvas'); cv.width=cv.height=128; const x=cv.getContext('2d');
    if(i===2){ x.fillStyle='#141c38'; x.fillRect(0,0,128,128); x.fillStyle='#8feeff'; x.fillRect(20,56,88,6); return cv; }   // +Y sky with a cyan light bar
    if(i===3){ x.fillStyle='#030305'; x.fillRect(0,0,128,128); return cv; }                                                    // -Y ground
    const g=x.createLinearGradient(0,0,0,128); g.addColorStop(0,'#141c38'); g.addColorStop(.47,'#16203c'); g.addColorStop(.5,'#0d4d5c'); g.addColorStop(.53,'#07090f'); g.addColorStop(1,'#030305'); x.fillStyle=g; x.fillRect(0,0,128,128);
    const st=[['#00d8f0',18,30,6,40],['#e8f0ff',70,40,30,10],['#ff4fa8',40,52,24,3],['#7fefff',96,20,4,38]][i%4]; x.fillStyle=st[0]; x.fillRect(st[1],st[2],st[3],st[4]); return cv; };
  _ikkiEnv=new THREE.CubeTexture([0,1,2,3,4,5].map(face)); _ikkiEnv.needsUpdate=true; return _ikkiEnv; }
// ===== RIDER_JOINT_LIMITS: per-joint rotation limits, degrees, per axis, from skyrydahs-ref/anatomy/anatomy-rigging-guide.md §4/§6 =====
// Body bones: poser model-space Euler deltas (YXZ). Conventions (char faces +Z, +X = his left), authored for the LEFT side; Right mirrors y/z.
//  Spine*/Neck/Head x+ = flex (forward), y = twist, z = lateral.  UpLeg x- = hip flex, x+ = ext, z+ = abduction.  Leg x+ = knee flex (0 = straight, no hyperext).
//  Foot x- = DORSIFLEX, x+ = plantarflex.  Shoulder z+ = elevation.  Arm x- = flex (forward), x+ = EXTENSION (back swing), z+ = abduction.  ForeArm x- = elbow flex.
// Finger bones: flex (+ toward palm) / spread (+ away from middle finger) about axes derived from the rest-pose hand geometry.
const RIDER_JOINT_LIMITS={ spineTwistTotal:40, spineTwistSplit:{Spine:.4,Spine1:.3,Spine2:.3}, softKnee:8,
  Hips:{x:[-30,30],y:[-90,90],z:[-20,20]},                       // root orientation (stance yaw for grind), not an anatomical joint
  Spine:{x:[-10,27],y:[-16,16],z:[-12,12]}, Spine1:{x:[-10,27],y:[-12,12],z:[-12,12]}, Spine2:{x:[-10,26],y:[-12,12],z:[-11,11]}, // sum: flex 80, ext 30, rot 40, lat 35
  Neck:{x:[-30,22],y:[-35,35],z:[-22,22]}, Head:{x:[-30,25],y:[-40,40],z:[-22,22]},   // sum: flex 47, ext 60, rot 75, lat 44
  Shoulder:{x:[-15,15],y:[-15,15],z:[-10,30]},                   // clavicle/scapula share of abduction (2:1 rhythm, ~60 total)
  Arm:{x:[-170,50],y:[-70,90],z:[-30,120]},                      // flex 170 / ext 50, GH abduction 120 (+ scapula), IR 70 / ER 90
  ForeArm:{x:[-145,0],y:[-80,85],z:[-3,3]},                      // hinge: flex 145, no hyperext; y = pronation/supination
  Hand:{x:[-70,70],y:[-10,10],z:[-30,20]},                       // wrist flex 70 / ext 70, ulnar 30 / radial 20
  UpLeg:{x:[-125,18],y:[-40,45],z:[-25,42]},                     // hip flex 125, ext 18, add 25, abd 42, IR 40 / ER 45
  Leg:{x:[0,140],y:[-20,20],z:[-3,3]},                           // knee hinge 0..140, tibial rotation when flexed
  Foot:{x:[-25,50],y:[-12,12],z:[-18,30]},                       // dorsiflex 25 (boot), plantar 50, eversion 18 / inversion 30
  ToeBase:{x:[-40,70],y:[0,0],z:[0,0]},                          // MTP flex 40 / ext 70 (not driven)
  // fingers [flex lo,hi], [spread lo,hi]
  Thumb1:{flex:[-20,15],spread:[0,55],opp:[0,45]}, Thumb2:{flex:[-10,55]}, Thumb3:{flex:[-20,80]},
  Index1:{flex:[-30,90],spread:[-20,20]}, Middle1:{flex:[-30,95],spread:[-15,15]}, Ring1:{flex:[-30,100],spread:[-20,20]}, Pinky1:{flex:[-30,110],spread:[-20,25]},
  Index2:{flex:[0,105]}, Middle2:{flex:[0,108]}, Ring2:{flex:[0,108]}, Pinky2:{flex:[0,110]},
  Index3:{flex:[-5,80]}, Middle3:{flex:[-5,85]}, Ring3:{flex:[-5,85]}, Pinky3:{flex:[-10,90]} };
// finger poses (deg): relaxed curl rises index->pinky (MCP 20-35, PIP 30-45, DIP 15-25), thumb slightly opposed; fist for grabs/tucks
const RIDER_HAND_POSES={ relaxed:{ Index:[20,30,15,-4], Middle:[25,35,18,0], Ring:[30,40,21,4], Pinky:[35,45,25,9], Thumb:[6,18,12,15,18] },  // [MCP,PIP,DIP,spread]; thumb [CMC flex,MCP,IP,abd,opp]
  fist:{ Index:[80,100,60,-2], Middle:[85,102,62,0], Ring:[90,102,62,2], Pinky:[95,100,60,4], Thumb:[10,45,40,20,40] },
  open:{ Index:[5,8,5,0], Middle:[5,8,5,0], Ring:[6,8,5,2], Pinky:[8,10,6,4], Thumb:[0,5,5,10,10] } };   // combat parry/blade (plan §3.4; not driven in G1)
// soft clamp: identity inside the range, tanh knee over the last `k` degrees so the joint eases into its limit (C1, never snaps)
// ===== Twist bones (shared rider skeleton: mixamorig:{Left,Right}{ArmTwist,ForeArmTwist}; shared/skeleton/README.md) =====
// Forearm roll (pronation/supination) is taken OFF the ForeArm bone (elbow-side skin stays put) and given to the Hand (full) and ForeArmTwist (share),
// so the forearm skin twists progressively instead of candy-wrapping. Upper-arm roll: ArmTwist counter-rolls by -share so the shoulder end stays calm.
// Missing twist bones -> old behaviour (roll stays on ForeArm/Arm). Shares follow character-bible §0.2 (50% roll share).
RIDER_JOINT_LIMITS.twist={ ForeArmTwist:{of:'ForeArm',share:.5}, ArmTwist:{of:'Arm',share:.5} };

// ===== Per-rider feel (stance width, crouch depth, arm style). Keys = WARDROBE_RIDERS key / 'ikki'. Others fall back to 'default' (hook: add a row). =====
const RIDER_FEEL={
  default:{ stance:1,   crouch:1,   armAbd:1,   arm:'balance', kickSide:'Left',  wallBack:false, armSwing:1, spineSway:1, windup:1, release:1, landDepth:1, landRate:1, idleRate:1, idleAmp:1 },
  ikki:   { stance:1.15,crouch:1,   armAbd:1.3, arm:'wing',    kickSide:'Left',  wallBack:true  },  // §7.2 Ikki: "open, airy silhouette: arms like wings", "backward-skating wall ride" (1800 Wall Ride)
  // APPROVED by Oliver via Forge 14:39 CDT (Lightning Dash Strike, Storm Line ending in Chain Shock): Caali G 'controlled power' = hero/leader, compact. Lean athletic; stance lower (crouch 1.08) + narrower (.90 vs Ikki 1.15);
  // quiet upper body (arms close .72, arm swing .65, spine sway .6); explosive bursts: short hard windup (x.70 time) -> lightning release (x.80 time; Wheel Spin Drop x.88 so its dropkick stays <=720 deg/s);
  // clean landings (dip depth .75, recovers 1.7x faster, no overshoot: exponential ease); calm idle (breathing/sway rate .65, amplitude .55).
  'caali-g':{ stance:.90,crouch:1.08,armAbd:.72, arm:'tight', kickSide:'Right', wallBack:false, armSwing:.65, spineSway:.6, windup:.70, release:.80, releaseBy:{trick:.88}, landDepth:.75, landRate:1.7, idleRate:.65, idleAmp:.55 },
  // APPROVED by Oliver via Forge 14:39 CDT (Ribbon Pirouette, Braid Cyclone): Anika = light, quick, playful (distinct from Caali G's controlled power). Wider bouncy arms, faster idle, springy landings.
  anika:  { stance:.95, crouch:.95, armAbd:1.15, arm:'playful', kickSide:'Left', wallBack:false, armSwing:1.25, spineSway:1.2, windup:.85, release:.85, releaseBy:{trick:.92}, landDepth:.9, landRate:1.3, idleRate:1.25, idleAmp:1.15 },
  kazu:   { stance:.9,  crouch:1.2, armAbd:.6,  arm:'tuck',    kickSide:'Left',  wallBack:false } }; // §7.2 Kazu: "minimal, compact form; long low tuck" (hook, no rider yet)
const riderFeel=k=>Object.assign({},RIDER_FEEL.default,RIDER_FEEL[k]||{});

// ===== Skate animation set (procedural keyframes, model-space Euler deg, same conventions as RIDER_JOINT_LIMITS; authored for the LEFT side) =====
// Leg/arm keys use roles: K* = kicking/push side, S* = support side (mapped to Left/Right per kickSide; Right mirrors y/z).
// Source lines: skyrydahs-ref/airgear-deep-reference.md §7 (clip list: kick_L/R, crouch_charge, grind_soul, wallride_fwd/back, wheel_spin_drop).
const RIDER_SKATE_STATES={
  // kick_L/R. §7.1 "Motor assists the kick; speed proportional to leg power ... Kick anim drives acceleration" + "[FAN] Kicks are a wide side push, not a skateboard push".
  // 0.70 s stroke: load onto support (anticipation) -> side push with full extension -> recovery under the hip. impulse window .20-.44 (userData.kickImpulse).
  kick:{ dur:.70, loop:false, impulse:[.20,.44], rel:1, keys:[
    [0,  {Hips:[0,0,0],  Spine:[14,0,0],Spine1:[8,0,0], SUpLeg:[-38,0,4], SLeg:[66,0,0],SFoot:[-24,0,0], KUpLeg:[-38,0,4], KLeg:[66,0,0],KFoot:[-24,0,0], KArm:[-10,0,14],SArm:[-10,0,14],KForeArm:[-20,0,0],SForeArm:[-20,0,0]}],
    [.18,{Hips:[0,6,-7], Spine:[20,0,4],Spine1:[10,0,0],SUpLeg:[-50,0,2], SLeg:[88,0,0],SFoot:[-25,0,-3],KUpLeg:[-44,0,10],KLeg:[74,0,0],KFoot:[-22,0,4], KArm:[-34,0,12],SArm:[22,0,20], KForeArm:[-38,0,0],SForeArm:[-18,0,0]}], // weight onto S, knees load
    [.40,{Hips:[0,10,-9],Spine:[24,0,5],Spine1:[12,0,0],SUpLeg:[-56,0,0], SLeg:[96,0,0],SFoot:[-25,0,-4],KUpLeg:[-8,0,30], KLeg:[16,0,0],KFoot:[-6,0,14], KArm:[34,0,24], SArm:[-46,0,6], KForeArm:[-14,0,0],SForeArm:[-62,0,0]}], // drive: K extends wide, arms counter
    [.46,{Hips:[0,9,-8], Spine:[23,0,4],Spine1:[12,0,0],SUpLeg:[-55,0,0], SLeg:[94,0,0],SFoot:[-25,0,-4],KUpLeg:[-4,0,34], KLeg:[8,0,0], KFoot:[0,0,16], KArm:[40,0,26], SArm:[-50,0,4], KForeArm:[-12,0,0],SForeArm:[-66,0,0]}], // full extension (toe-roll)
    [.70,{Hips:[0,0,0],  Spine:[14,0,0],Spine1:[8,0,0], SUpLeg:[-38,0,4], SLeg:[66,0,0],SFoot:[-24,0,0], KUpLeg:[-46,0,6], KLeg:[78,0,0],KFoot:[-24,0,0], KArm:[-10,0,14],SArm:[-10,0,14],KForeArm:[-20,0,0],SForeArm:[-20,0,0]}]]},  // recovery: K knee lifts back under hip
  // crouch_charge. §7.1 Gravity Control "Hold A: CoG drops at takeoff ... jump height +15% with a held crouch"; Cushion system "knee bend 30-60°" (landing, already in land dip).
  // 0.38 s load with a small counter-rise (anticipation), then hold; arms swing back to load the jump.
  crouch:{ dur:.38, loop:'hold', rel:1, keys:[
    [0,  {Spine:[14,0,0],Spine1:[8,0,0],Neck:[-8,0,0], SUpLeg:[-38,0,5],SLeg:[66,0,0],SFoot:[-24,0,0],KUpLeg:[-38,0,5],KLeg:[66,0,0],KFoot:[-24,0,0], KArm:[-10,0,14],SArm:[-10,0,14],KForeArm:[-20,0,0],SForeArm:[-20,0,0]}],
    [.08,{Spine:[10,0,0],Spine1:[6,0,0],Neck:[-6,0,0], SUpLeg:[-30,0,5],SLeg:[52,0,0],SFoot:[-20,0,0],KUpLeg:[-30,0,5],KLeg:[52,0,0],KFoot:[-20,0,0], KArm:[-24,0,16],SArm:[-24,0,16],KForeArm:[-26,0,0],SForeArm:[-26,0,0]}], // counter-rise
    [.38,{Spine:[26,0,0],Spine1:[20,0,0],Spine2:[14,0,0],Neck:[-26,0,0],Head:[-18,0,0], SUpLeg:[-92,0,8],SLeg:[116,0,0],SFoot:[-25,0,0],KUpLeg:[-92,0,8],KLeg:[116,0,0],KFoot:[-25,0,0], KArm:[44,0,16],SArm:[44,0,16],KForeArm:[-38,0,0],SForeArm:[-38,0,0]}]]},  // full load: knees 116 (<=140 even at crouch x1.15), eyes up
  // wallride_fwd/back. §7.1 "Wall ride holds speed for ~1.5 s; spin input on exit adds 360° increments" + §7.2 Ikki "1800 Wall Ride: alternates skating backwards up a wall",
  // Buccha "heavy, momentum-driven wall rides". Wall side = K (= userData.wallSide, +1 wall on rider's left). 0.25 s entry, then a 1.5 s breathing hold loop.
  wall:{ dur:1.5, loop:'cycle', enter:.25, keys:[
    [0,  {Hips:[0,0,16],Spine:[18,0,8],Spine1:[10,0,4],Neck:[-14,0,-10],Head:[-10,0,-8], KUpLeg:[-62,0,4],KLeg:[98,0,0],KFoot:[-25,0,-10], SUpLeg:[-30,0,14],SLeg:[54,0,0],SFoot:[-18,0,8], KArm:[-20,0,72],SArm:[-34,0,52],KForeArm:[-28,0,0],SForeArm:[-36,0,0]}],
    [.75,{Hips:[0,0,19],Spine:[20,0,9],Spine1:[11,0,4],Neck:[-15,0,-11],Head:[-11,0,-9], KUpLeg:[-66,0,4],KLeg:[104,0,0],KFoot:[-25,0,-11],SUpLeg:[-32,0,16],SLeg:[58,0,0],SFoot:[-19,0,9], KArm:[-16,0,78],SArm:[-30,0,56],KForeArm:[-24,0,0],SForeArm:[-32,0,0]}], // weight sinks into the wall (g-load)
    [1.5,{Hips:[0,0,16],Spine:[18,0,8],Spine1:[10,0,4],Neck:[-14,0,-10],Head:[-10,0,-8], KUpLeg:[-62,0,4],KLeg:[98,0,0],KFoot:[-25,0,-10], SUpLeg:[-30,0,14],SLeg:[54,0,0],SFoot:[-18,0,8], KArm:[-20,0,72],SArm:[-34,0,52],KForeArm:[-28,0,0],SForeArm:[-36,0,0]}]]},
  // wheel_spin_drop. §7.2 Ikki "Wheel Spin Drop: spins the wheels while standing still, then a rip-start dropkick"; Xbox "X hold/release = Wheel Spin Drop".
  // hold: low coil + wheel spin (sh.spin); release (userData.trickRelease() or 0.8 s): sink (anticipation) -> rip-start dropkick with K leg -> land in a cushion crouch.
  trick:{ dur:1.25, loop:false, hold:[0,.30], rel:1, keys:[
    [0,  {Hips:[0,0,0],Spine:[22,-6,0],Spine1:[14,-5,0],Spine2:[10,-5,0], SUpLeg:[-80,0,8],SLeg:[104,0,0],SFoot:[-25,0,0],KUpLeg:[-80,0,8],KLeg:[104,0,0],KFoot:[-25,0,0], KArm:[30,0,20],SArm:[30,0,20],KForeArm:[-90,0,0],SForeArm:[-90,0,0]}], // coiled, wheels spinning
    [.30,{Hips:[0,0,0],Spine:[24,-8,0],Spine1:[16,-6,0],Spine2:[12,-6,0], SUpLeg:[-88,0,8],SLeg:[114,0,0],SFoot:[-25,0,0],KUpLeg:[-88,0,8],KLeg:[114,0,0],KFoot:[-25,0,0], KArm:[38,0,22],SArm:[38,0,22],KForeArm:[-96,0,0],SForeArm:[-96,0,0]}], // sink (anticipation)
    [.56,{Hips:[-14,14,0],Spine:[-8,8,0],Spine1:[-6,6,0],Spine2:[-4,6,0],Neck:[-10,0,0], SUpLeg:[-24,0,6],SLeg:[42,0,0],SFoot:[-20,0,0],KUpLeg:[-100,0,4],KLeg:[14,0,0],KFoot:[34,0,0], KArm:[46,0,44],SArm:[40,0,40],KForeArm:[-30,0,0],SForeArm:[-34,0,0]}], // rip start: K drives forward, chest opens back
    [.74,{Hips:[-16,16,0],Spine:[-10,9,0],Spine1:[-7,7,0],Spine2:[-5,7,0],Neck:[-12,0,0], SUpLeg:[-20,0,6],SLeg:[36,0,0],SFoot:[-18,0,0],KUpLeg:[-104,0,4],KLeg:[6,0,0],KFoot:[40,0,0], KArm:[48,0,48],SArm:[44,0,44],KForeArm:[-26,0,0],SForeArm:[-30,0,0]}], // full extension (impact)
    [.98,{Hips:[0,4,0],Spine:[22,2,0],Spine1:[12,2,0], SUpLeg:[-60,0,8],SLeg:[92,0,0],SFoot:[-25,0,0],KUpLeg:[-56,0,8],KLeg:[88,0,0],KFoot:[-24,0,0], KArm:[-20,0,30],SArm:[-20,0,30],KForeArm:[-40,0,0],SForeArm:[-40,0,0]}], // cushion landing (§7.1 knee 30-60 + crouch)
    [1.25,{Hips:[0,0,0],Spine:[14,0,0],Spine1:[8,0,0], SUpLeg:[-38,0,4],SLeg:[66,0,0],SFoot:[-24,0,0],KUpLeg:[-38,0,4],KLeg:[66,0,0],KFoot:[-24,0,0], KArm:[-10,0,14],SArm:[-10,0,14],KForeArm:[-20,0,0],SForeArm:[-20,0,0]}]]},
  // polegrind (ref3-pole-grind, Oliver 2026-10-30): vertical pole grind, two variants. K = pole side (opts.side, default rider's LEFT = +X).
  // §7.1 "Grinds on any rail, even vertical ones (Upper Soul 23 Roll corkscrews up a flagpole)". Entry .30 s, hold = 1.6 s breathing loop, exit .25 s (weight fade).
  // Gameplay owns the root: Rydah Systems places/rotates the rider around userData.poleAxis; the spiral vortex FX is Optimizer's.
  polegrind_top:{ dur:1.6, loop:'cycle', enter:.30, exit:.25, keys:[   // ref3-pole-grind: Anika crouched ON TOP of the crossarm, both skates on the beam, arms flung out for balance
    [0,  {Hips:[0,0,0], Spine:[12,0,0],Spine1:[6,0,0],Spine2:[4,0,0], Neck:[10,0,0],Head:[8,0,4],   // ref3-pole-grind: torso near-upright, chin dipped, looking down at the camera, playful head tilt
          KUpLeg:[-82,0,-4],KLeg:[104,0,0],KFoot:[-22,0,0], SUpLeg:[-82,0,-4],SLeg:[104,0,0],SFoot:[-22,0,0],   // ref3-pole-grind: deep two-foot crouch, knees together (slight adduction), feet close on the beam
          KArm:[-30,0,78],SArm:[-30,0,78], KForeArm:[-28,0,0],SForeArm:[-28,0,0], KHand:[-10,0,0],SHand:[-10,0,0]}],  // ref3-pole-grind: both arms out to the sides and a bit forward, soft elbows
    [.8, {Hips:[0,0,0], Spine:[14,0,0],Spine1:[7,0,0],Spine2:[5,0,0], Neck:[11,0,0],Head:[9,0,5],
          KUpLeg:[-86,0,-4],KLeg:[110,0,0],KFoot:[-23,0,0], SUpLeg:[-86,0,-4],SLeg:[110,0,0],SFoot:[-23,0,0],
          KArm:[-26,0,84],SArm:[-34,0,74], KForeArm:[-24,0,0],SForeArm:[-32,0,0], KHand:[-12,0,0],SHand:[-8,0,0]}],   // balance correction: one arm up, one down
    [1.6,{Hips:[0,0,0], Spine:[12,0,0],Spine1:[6,0,0],Spine2:[4,0,0], Neck:[10,0,0],Head:[8,0,4],
          KUpLeg:[-82,0,-4],KLeg:[104,0,0],KFoot:[-22,0,0], SUpLeg:[-82,0,-4],SLeg:[104,0,0],SFoot:[-22,0,0],
          KArm:[-30,0,78],SArm:[-30,0,78], KForeArm:[-28,0,0],SForeArm:[-28,0,0], KHand:[-10,0,0],SHand:[-10,0,0]}]]},
  polegrind_climb:{ dur:1.6, loop:'cycle', enter:.30, exit:.25, keys:[   // ref3-pole-grind: Caali climbing the pole (pole on his K side), facing out to camera
    [0,  {Hips:[0,10,-12], Spine:[14,0,-8],Spine1:[8,0,-4],Spine2:[6,6,-3], Neck:[-6,0,4],Head:[-4,-14,4],   // ref3-pole-grind: hips/torso lean AWAY from the pole, chest open to camera, head turned to camera
          KUpLeg:[-92,0,8],KLeg:[112,0,0],KFoot:[-20,0,-8],   // ref3-pole-grind: pole-side leg high, thigh ~horizontal, skate wheels planted on the pole (soul-grind contact)
          SUpLeg:[-16,0,4],SLeg:[26,0,0],SFoot:[18,0,0],      // ref3-pole-grind: other leg hangs down along the pole, nearly straight, toe pointed
          KArm:[-62,0,46],KForeArm:[-84,0,0],KHand:[-20,0,0], // ref3-pole-grind: pole-side hand grips the pole at head height (elbow bent ~85)
          SArm:[-8,0,90],SForeArm:[-8,0,0],SHand:[6,0,0]}],   // ref3-pole-grind: free arm flung straight out sideways, palm open
    [.8, {Hips:[0,11,-13], Spine:[15,0,-9],Spine1:[8,0,-4],Spine2:[6,7,-3], Neck:[-6,0,4],Head:[-4,-15,4],
          KUpLeg:[-96,0,8],KLeg:[116,0,0],KFoot:[-21,0,-8], SUpLeg:[-18,0,4],SLeg:[28,0,0],SFoot:[20,0,0],
          KArm:[-64,0,44],KForeArm:[-88,0,0],KHand:[-22,0,0], SArm:[-10,0,92],SForeArm:[-10,0,0],SHand:[6,0,0]}],   // corkscrew pulse: pull in to the pole
    [1.6,{Hips:[0,10,-12], Spine:[14,0,-8],Spine1:[8,0,-4],Spine2:[6,6,-3], Neck:[-6,0,4],Head:[-4,-14,4],
          KUpLeg:[-92,0,8],KLeg:[112,0,0],KFoot:[-20,0,-8], SUpLeg:[-16,0,4],SLeg:[26,0,0],SFoot:[18,0,0],
          KArm:[-62,0,46],KForeArm:[-84,0,0],KHand:[-20,0,0], SArm:[-8,0,90],SForeArm:[-8,0,0],SHand:[6,0,0]}]]},
 };
// grind_soul keeps the existing 'grind' state (§7.1 "Grinds on any rail ... Power lines are grind rails"); feel params now apply to it too.
// Sample a state at time t (s) -> {LeftUpLeg:[x,y,z] deg, ...}. kSide = 'Left'|'Right' (K role). Pure: also used by the node limit check.
// feel timing: keys up to S.rel (windup) scale by feel.windup, the release segment (rel -> rel+1) by feel.release, the rest keeps its length.
function riderStateTiming(name,feel){ const S=RIDER_SKATE_STATES[name], f=Object.assign({},RIDER_FEEL.default,feel||{}); const rl=(f.releaseBy&&f.releaseBy[name])||f.release; if(S.rel===undefined||(f.windup===1&&rl===1)) return {keys:S.keys,dur:S.dur,impulse:S.impulse};
  const T=S.keys.map(k=>k[0]), o=[0]; for(let i=1;i<T.length;i++){ const d=T[i]-T[i-1]; o[i]=o[i-1]+d*(i<=S.rel?f.windup:i===S.rel+1?rl:1); }
  const map=x=>{ let i=0; while(i<T.length-2&&x>T[i+1]) i++; return o[i]+(x-T[i])/(T[i+1]-T[i])*(o[i+1]-o[i]); };
  return {keys:S.keys.map((k,i)=>[o[i],k[1]]), dur:o[o.length-1], impulse:S.impulse&&S.impulse.map(map)}; }
function riderStateSample(name,t,kSide,feel){ const S0=RIDER_SKATE_STATES[name]; if(!S0) return null; const f=Object.assign({},RIDER_FEEL.default,feel||{}), TM=riderStateTiming(name,f), S=Object.assign({},S0,TM), K=S.keys;
  let u=t; if(S.loop==='hold') u=Math.min(t,S.dur); else if(S.loop==='cycle') u=t%S.dur; else u=Math.min(t,S.dur);
  let i=0; while(i<K.length-2&&u>K[i+1][0]) i++; const a=K[i], b=K[i+1], x=Math.min(1,Math.max(0,(u-a[0])/Math.max(1e-6,b[0]-a[0]))), e=x*x*(3-2*x), out={};
  const sSide=kSide==='Left'?'Right':'Left', mapN=n=>n[0]==='K'&&/^K[A-Z]/.test(n)?kSide+n.slice(1):n[0]==='S'&&/^S(UpLeg|Leg|Foot|Arm|ForeArm|Hand|Shoulder)$/.test(n)?sSide+n.slice(1):n;
  const keys=new Set([...Object.keys(a[1]),...Object.keys(b[1])]);
  for(const n of keys){ const p=a[1][n]||b[1][n], q=b[1][n]||a[1][n]; let v=[0,1,2].map(j=>p[j]+(q[j]-p[j])*e); const nm=mapN(n);
    if(/UpLeg$/.test(nm)){ v[0]*=f.crouch; v[2]*=f.stance; } else if(/Leg$/.test(nm)) v[0]*=f.crouch; else if(/Arm$/.test(nm)&&!/Fore/.test(nm)) v[2]*=f.armAbd;
    if(nm.startsWith('Right')){ v[1]=-v[1]; v[2]=-v[2]; } else if(!/^Left/.test(nm)&&kSide==='Right'){ v[1]=-v[1]; v[2]=-v[2]; }  // centre bones mirror with the kick side
    out[nm]=v; }
  return out; }
// ===== COMBAT POSES G0/G1 (Rydah Rigger 2026-10-30; plan skyrydahs-ref/combat-anim-plan.md). FLAG-GATED: nothing changes in game until
// window.SR_COMBAT_POSES=true or ?combatposes=1. Gameplay (Rydah Systems) stays authoritative for hits/cancels; the poser only animates,
// fires frame events and REPORTS root motion (never moves the root). Frames at 72 fps; keys = model-space Euler deg (RIDER_SKATE_STATES conventions),
// K* = lead side (`side`), S* = other side; Right mirrors y/z; centre bones mirror with side. Timing: authored A/X/R phases, feel-scaled piecewise.
const RIDER_COMBAT_FPS=72, RIDER_POSE_ACTIVE_DEG_S=1800;   // 1800 deg/s (25 deg/frame) ONLY on the move's lead limb during its active (X) frames; all else 720
const riderCombatOn=()=>!!((typeof window!=='undefined'&&window.SR_COMBAT_POSES)||(typeof location!=='undefined'&&/[?&]combatposes=1(&|$)/.test(location.search)));
const RIDER_COMBAT_LEAD={ KArm:['Shoulder','Arm','ForeArm','Hand'], KLeg:['UpLeg','Leg','Foot'] };   // lead limb chains (side-prefixed at start)
const RIDER_COMBAT_LOWER=/(^Hips$|UpLeg$|Leg$|Foot$|ToeBase$)/;   // mask:'upper' skips these (legs keep the skating layer)
// Per-rider combat feel (timing scale per phase, lead-limb amplitude, spine/neck twist, root-motion multiplier). Keys = RIDER_FEEL keys.
const RIDER_COMBAT_FEEL={
  default:  { windup:1,   release:1,   recover:1,   amp:1,    twist:1,    root:1,   over:1   },   // over = overshoot past the hit pose ('over' keys)
  'caali-g':{ windup:.70, release:.80, recover:.80, amp:.92,  twist:.75,  root:1.25, over:.3 },  // controlled power: short hard windup, still torso, clean stop, longer drive
  anika:    { windup:.85, release:.85, recover:1.10,amp:1.08, twist:1.2,  root:.90, over:1.4 },  // APPROVED by Oliver via Forge 14:39 CDT: flowing, more rotation, flair recovery
  ikki:     { windup:1,   release:.90, recover:1,   amp:1.05, twist:1.1,  root:1.10, over:1.1 }, };
const riderCombatFeel=k=>Object.assign({},RIDER_COMBAT_FEEL.default,RIDER_COMBAT_FEEL[k]||{});
// Move table. A/X/R = anticipation/active/recovery frames; hit = absolute authored frames (inside X); cancel = {open,kinds} (open = frame, NOT feel-scaled:
// Systems' A/B cancel after 0.16 s = f12; closes at move end); root = desired forward metres between authored frames [from,to] (reported only);
// mask 'upper'|'full'; plant 'both'|'S'|'any'|'off' (which foot must stay on the deck; plant() itself is unchanged); hand {K,S} 'fist'|'relaxed';
// hold = charge at end of A until combatRelease() (cap holdMax s). Keys: [authoredFrame,{bone:[x,y,z]}].
const RIDER_COMBAT_MOVES={
  // step 0: lead jab-drive (tuned 13:2x). Pullback (chest opens, torso turns away + lifts, fist chambers, shoulder retracts) -> snap: chest/spine
  // rotate into the punch, shoulder drives, slight forward lean, eyes on target -> 'over' key (overshoot, scaled by feel.over) -> settle.
  light1:{ kind:'atk', step:0, A:6, X:5, R:11, hit:[10], cancel:{open:12,kinds:['chain','dash','jump']}, root:{fwd:.3,from:4,to:10}, lead:'KArm', mask:'upper', plant:'both', hand:{K:'fist',S:'fist'}, keys:[
    [0, {Spine:[16,3,0],Spine1:[10,2,0],Spine2:[6,2,0],Neck:[-12,-4,0],Head:[-8,-4,0], KShoulder:[0,0,0],KArm:[-25,0,18],KForeArm:[-100,0,0],KHand:[0,0,0], SArm:[-40,0,20],SForeArm:[-105,0,0]}],
    [4, {Spine:[10,13,0],Spine1:[6,10,0],Spine2:[4,10,0],Neck:[-8,-16,0],Head:[-6,-18,0], KShoulder:[-12,-12,0],KArm:[-50,0,22],KForeArm:[-95,0,0],KHand:[10,0,0], SArm:[-62,0,18],SForeArm:[-60,0,0]}],   // held anticipation (2 f)
    [6, {Spine:[10,13,0],Spine1:[6,10,0],Spine2:[4,10,0],Neck:[-8,-16,0],Head:[-6,-18,0], KShoulder:[-12,-12,0],KArm:[-50,0,22],KForeArm:[-95,0,0],KHand:[10,0,0], SArm:[-62,0,18],SForeArm:[-60,0,0]}],   // pullback: torso winds away, lead fist cocked at the chin, rear hand reaches out (aim)
    [10,{Spine:[27,-11,0],Spine1:[22,-8,0],Spine2:[18,-8,0],Neck:[-24,14,0],Head:[-14,16,0], KShoulder:[12,13,6],KArm:[-125,0,6],KForeArm:[-4,0,0],KHand:[0,0,-8], SArm:[-30,0,28],SForeArm:[-118,0,0]}],   // hit: full reach (arm flex is relative to the leaning chest: ~-125 = level with the shoulder)
    [11,{Spine:[27,-12.5,0],Spine1:[23,-9,0],Spine2:[19,-9,0],Neck:[-24,15,0],Head:[-15,17,0], KShoulder:[13,14,6],KArm:[-130,0,4],KForeArm:[-2,0,0],KHand:[0,0,-9], SArm:[-28,0,28],SForeArm:[-120,0,0]},'over'],
    [13,{Spine:[19,-8,0],Spine1:[13,-6,0],Spine2:[9,-6,0],Neck:[-16,10,0],Head:[-12,11,0], KShoulder:[8,9,4],KArm:[-105,0,10],KForeArm:[-20,0,0],KHand:[0,0,-4], SArm:[-34,0,26],SForeArm:[-115,0,0]}],   // settle
    [22,{Spine:[16,2,0],Spine1:[10,2,0],Spine2:[6,2,0],Neck:[-12,-2,0],Head:[-8,-2,0], KShoulder:[0,0,0],KArm:[-30,0,18],KForeArm:[-95,0,0],KHand:[0,0,0], SArm:[-40,0,20],SForeArm:[-105,0,0]}]]},
  // step 1: other-side back-hand hook (side flips automatically; tuned 13:2x): wide pullback, chest whips through, shoulder drives, overshoot + settle.
  light2:{ kind:'atk', step:1, A:5, X:5, R:12, hit:[9], cancel:{open:12,kinds:['chain','dash','jump']}, root:{fwd:.3,from:3,to:9}, lead:'KArm', mask:'upper', plant:'both', hand:{K:'fist',S:'fist'}, keys:[
    [0, {Spine:[16,3,0],Spine1:[10,2,0],Spine2:[6,2,0],Neck:[-12,-4,0],Head:[-8,-4,0], KShoulder:[0,0,0],KArm:[-25,0,18],KForeArm:[-100,0,0],KHand:[0,0,0], SArm:[-40,0,20],SForeArm:[-105,0,0]}],
    [3, {Spine:[10,13,4],Spine1:[6,10,2],Spine2:[4,10,0],Neck:[-8,-16,0],Head:[-6,-18,0], KShoulder:[-10,-12,4],KArm:[-45,-5,70],KForeArm:[-95,0,0],KHand:[0,0,0], SArm:[-60,0,18],SForeArm:[-60,0,0]}],   // held anticipation (2 f)
    [5, {Spine:[10,13,4],Spine1:[6,10,2],Spine2:[4,10,0],Neck:[-8,-16,0],Head:[-6,-18,0], KShoulder:[-10,-12,4],KArm:[-45,-5,70],KForeArm:[-95,0,0],KHand:[0,0,0], SArm:[-60,0,18],SForeArm:[-60,0,0]}],   // wide pullback: elbow out, rear hand reaches out
    [9, {Spine:[27,-11,-6],Spine1:[22,-8,-4],Spine2:[18,-8,0],Neck:[-24,14,4],Head:[-14,16,4], KShoulder:[12,13,10],KArm:[-110,-30,40],KForeArm:[-70,0,0],KHand:[0,0,-10], SArm:[-30,0,30],SForeArm:[-118,0,0]}],   // hook lands across
    [10,{Spine:[27,-12.5,-7],Spine1:[23,-9,-5],Spine2:[19,-9,0],Neck:[-24,15,4],Head:[-15,17,4], KShoulder:[13,14,10],KArm:[-114,-36,36],KForeArm:[-72,0,0],KHand:[0,0,-10], SArm:[-28,0,30],SForeArm:[-120,0,0]},'over'],
    [12,{Spine:[18,-8,-4],Spine1:[13,-6,-2],Spine2:[9,-6,0],Neck:[-15,10,2],Head:[-11,11,2], KShoulder:[8,9,6],KArm:[-95,-20,36],KForeArm:[-75,0,0],KHand:[0,0,-4], SArm:[-34,0,26],SForeArm:[-112,0,0]}],   // settle
    [22,{Spine:[16,2,0],Spine1:[10,2,0],Spine2:[6,2,0],Neck:[-12,-2,0],Head:[-8,-2,0], KShoulder:[0,0,0],KArm:[-30,0,18],KForeArm:[-95,0,0],KHand:[0,0,0], SArm:[-40,0,20],SForeArm:[-105,0,0]}]]},
  // step 2: finisher (2.4x knockback, commits, no cancel; tuned 13:2x). Load on the front (S) skate with the torso wound back -> lunge: hips turn through,
  // spine dives forward (~65 deg total), head leads (neck extends to keep eyes on target), lead fist at full reach + shoulder drive, rear arm thrown back
  // for counterbalance; rear (K) skate stays drawn up under the hip (off the deck). Feet: S skate planted. 'over' = overshoot (feel.over) then settle.
  finisher:{ kind:'atk', step:2, A:8, X:6, R:22, hit:[13], cancel:null, root:{fwd:1.2,from:6,to:14}, lead:'KArm', mask:'full', plant:'S', hand:{K:'fist',S:'fist'}, keys:[
    [0, {Hips:[0,0,0],Spine:[16,4,0],Spine1:[10,3,0],Spine2:[6,3,0],Neck:[-12,-5,0],Head:[-8,-5,0], SUpLeg:[-40,0,5],SLeg:[70,0,0],SFoot:[-24,0,0], KUpLeg:[-40,0,5],KLeg:[70,0,0],KFoot:[-24,0,0], KShoulder:[0,0,0],KArm:[-20,0,18],KForeArm:[-100,0,0], SArm:[-40,0,20],SForeArm:[-105,0,0]}],
    [6, {Hips:[0,26,0],Spine:[14,13,0],Spine1:[10,10,0],Spine2:[6,10,0],Neck:[-12,-18,0],Head:[-10,-20,0], SUpLeg:[-70,0,6],SLeg:[95,0,0],SFoot:[-25,0,0], KUpLeg:[-92,0,6],KLeg:[128,0,0],KFoot:[-25,0,0], KShoulder:[-12,-12,-4],KArm:[-45,0,26],KForeArm:[-105,0,0],KHand:[10,0,0], SArm:[-55,0,22],SForeArm:[-35,0,0]}],   // held anticipation (2 f)
    [8, {Hips:[0,26,0],Spine:[14,13,0],Spine1:[10,10,0],Spine2:[6,10,0],Neck:[-12,-18,0],Head:[-10,-20,0], SUpLeg:[-70,0,6],SLeg:[95,0,0],SFoot:[-25,0,0], KUpLeg:[-92,0,6],KLeg:[128,0,0],KFoot:[-25,0,0], KShoulder:[-12,-12,-4],KArm:[-45,0,26],KForeArm:[-105,0,0],KHand:[10,0,0], SArm:[-55,0,22],SForeArm:[-35,0,0]}],   // load + wind back: fist cocked at the ribs, rear hand reaches at the target
    [13,{Hips:[0,-36,0],Spine:[27,-11,0],Spine1:[27,-8,0],Spine2:[26,-8,0],Neck:[-28,14,0],Head:[-20,16,0], SUpLeg:[-62,0,4],SLeg:[88,0,0],SFoot:[-25,0,0], KUpLeg:[-62,0,10],KLeg:[122,0,0],KFoot:[-25,0,0], KShoulder:[13,13,6],KArm:[-150,0,4],KForeArm:[-2,0,0],KHand:[0,0,-8], SArm:[50,0,40],SForeArm:[-8,0,0]}],   // lunge (hit)
    [14,{Hips:[0,-38,0],Spine:[27,-12.5,0],Spine1:[27,-9,0],Spine2:[26,-9,0],Neck:[-28,15,0],Head:[-21,17,0], SUpLeg:[-62,0,4],SLeg:[88,0,0],SFoot:[-25,0,0], KUpLeg:[-62,0,10],KLeg:[122,0,0],KFoot:[-25,0,0], KShoulder:[14,14,6],KArm:[-153,0,3],KForeArm:[-1,0,0],KHand:[0,0,-9], SArm:[50,0,42],SForeArm:[-6,0,0]},'over'],
    [18,{Hips:[0,-26,0],Spine:[22,-9,0],Spine1:[20,-7,0],Spine2:[16,-7,0],Neck:[-22,11,0],Head:[-17,12,0], SUpLeg:[-62,0,4],SLeg:[88,0,0],SFoot:[-25,0,0], KUpLeg:[-62,0,10],KLeg:[122,0,0],KFoot:[-25,0,0], KShoulder:[8,8,4],KArm:[-130,0,6],KForeArm:[-10,0,0],KHand:[0,0,-4], SArm:[42,0,34],SForeArm:[-25,0,0]}],   // settle, hold the line
    [26,{Hips:[0,-8,0],Spine:[18,-4,0],Spine1:[12,-3,0],Spine2:[8,-3,0],Neck:[-14,5,0],Head:[-10,6,0], SUpLeg:[-40,0,5],SLeg:[70,0,0],SFoot:[-24,0,0], KUpLeg:[-40,0,5],KLeg:[70,0,0],KFoot:[-24,0,0], KShoulder:[4,4,2],KArm:[-55,0,14],KForeArm:[-60,0,0],KHand:[0,0,0], SArm:[-10,0,25],SForeArm:[-100,0,0]}],   // both skates back on the deck together
    [36,{Hips:[0,0,0],Spine:[16,2,0],Spine1:[10,2,0],Spine2:[6,2,0],Neck:[-12,-2,0],Head:[-8,-2,0], SUpLeg:[-40,0,5],SLeg:[70,0,0],SFoot:[-24,0,0], KUpLeg:[-40,0,5],KLeg:[70,0,0],KFoot:[-24,0,0], KShoulder:[0,0,0],KArm:[-30,0,18],KForeArm:[-95,0,0],KHand:[0,0,0], SArm:[-40,0,20],SForeArm:[-105,0,0]}]]},
  // heavy (PROVISIONAL, Systems: hold J >= 0.35 s, charge cap 1.0 s, fires on release): chambered wheel push-kick off the support skate.
  heavy:{ kind:'atk', step:-1, A:14, X:5, R:24, hit:[17], cancel:null, root:{fwd:.6,from:14,to:19}, lead:'KLeg', mask:'full', plant:'S', hand:{K:'fist',S:'fist'}, hold:true, holdMax:1.0, keys:[
    [0, {Spine:[16,0,0],Spine1:[10,0,0],Neck:[-12,0,0],Head:[-8,0,0], SUpLeg:[-40,0,5],SLeg:[70,0,0],SFoot:[-24,0,0], KUpLeg:[-40,0,5],KLeg:[70,0,0],KFoot:[-24,0,0], KArm:[-20,0,18],KForeArm:[-90,0,0], SArm:[-40,0,20],SForeArm:[-100,0,0]}],
    [14,{Spine:[24,0,0],Spine1:[16,0,0],Spine2:[8,0,0],Neck:[-22,0,0],Head:[-14,0,0], SUpLeg:[-70,0,5],SLeg:[95,0,0],SFoot:[-25,0,0], KUpLeg:[-100,0,8],KLeg:[125,0,0],KFoot:[-15,0,0], KArm:[35,0,32],KForeArm:[-90,0,0], SArm:[-55,0,30],SForeArm:[-100,0,0]}],   // chamber (charge hold)
    [17,{Spine:[-6,0,0],Spine1:[-4,0,0],Spine2:[0,0,0],Neck:[-6,0,0],Head:[-2,0,0], SUpLeg:[-52,0,4],SLeg:[77,0,0],SFoot:[-25,0,0], KUpLeg:[-86,0,6],KLeg:[6,0,0],KFoot:[-20,0,0], KArm:[45,0,42],KForeArm:[-60,0,0], SArm:[-40,0,48],SForeArm:[-70,0,0]}],   // push-kick extension (hit)
    [19,{Spine:[-6,0,0],Spine1:[-4,0,0],Spine2:[0,0,0],Neck:[-6,0,0],Head:[-2,0,0], SUpLeg:[-52,0,4],SLeg:[77,0,0],SFoot:[-25,0,0], KUpLeg:[-84,0,6],KLeg:[10,0,0],KFoot:[-20,0,0], KArm:[45,0,42],KForeArm:[-60,0,0], SArm:[-40,0,48],SForeArm:[-70,0,0]}],
    [31,{Spine:[12,0,0],Spine1:[8,0,0],Spine2:[2,0,0],Neck:[-10,0,0],Head:[-6,0,0], SUpLeg:[-40,0,5],SLeg:[70,0,0],SFoot:[-24,0,0], KUpLeg:[-55,0,6],KLeg:[105,0,0],KFoot:[-20,0,0], KArm:[10,0,28],KForeArm:[-80,0,0], SArm:[-40,0,30],SForeArm:[-90,0,0]}],   // support back to stance, kick skate still lifted
    [43,{Spine:[16,0,0],Spine1:[10,0,0],Spine2:[4,0,0],Neck:[-12,0,0],Head:[-8,0,0], SUpLeg:[-40,0,5],SLeg:[70,0,0],SFoot:[-24,0,0], KUpLeg:[-40,0,5],KLeg:[70,0,0],KFoot:[-24,0,0], KArm:[-20,0,18],KForeArm:[-90,0,0], SArm:[-40,0,20],SForeArm:[-100,0,0]}]]},
  // reacts (victim; Systems calls setState('react',{kind,dir}); dir = push direction, world). Authored for a hit from the front (pushed back);
  // a hit from behind flips the centre-bone pitch, the lateral side follows dir. No hit events, no cancel, no root (Systems owns knockback).
  react_light:{ kind:'react', dirFlip:true, A:2, X:2, R:10, hit:[], cancel:null, root:null, lead:null, mask:'upper', plant:'both', hand:{K:'relaxed',S:'relaxed'}, keys:[
    [0, {Spine:[-8,0,8],Spine1:[-6,0,6],Spine2:[-4,0,4],Neck:[-14,0,10],Head:[-14,0,10], KArm:[25,0,35],KForeArm:[-45,0,0], SArm:[20,0,28],SForeArm:[-45,0,0]}],
    [4, {Spine:[-8,0,8],Spine1:[-6,0,6],Spine2:[-4,0,4],Neck:[-14,0,10],Head:[-14,0,10], KArm:[25,0,35],KForeArm:[-45,0,0], SArm:[20,0,28],SForeArm:[-45,0,0]}],
    [14,{Spine:[8,0,2],Spine1:[4,0,1],Spine2:[2,0,0],Neck:[-6,0,2],Head:[-4,0,2], KArm:[0,0,20],KForeArm:[-40,0,0], SArm:[0,0,20],SForeArm:[-40,0,0]}]]},
  react_heavy:{ kind:'react', dirFlip:true, A:4, X:6, R:26, hit:[], cancel:null, root:null, lead:null, mask:'full', plant:'any',   // skid: lowest skate on the deck +-3 mm, other <= 10 mm (deep crouch shows the mesh's L/R asymmetry)
    hand:{K:'relaxed',S:'relaxed'}, keys:[
    [0, {Hips:[0,0,0],Spine:[-10,0,12],Spine1:[-8,0,8],Spine2:[-6,0,6],Neck:[-26,0,16],Head:[-22,0,14], SUpLeg:[-65,0,8],SLeg:[90,0,0],SFoot:[-25,0,0], KUpLeg:[-65,0,8],KLeg:[90,0,0],KFoot:[-25,0,0], KArm:[35,0,85],KForeArm:[-30,0,0], SArm:[20,0,70],SForeArm:[-35,0,0]}],
    [10,{Hips:[0,0,0],Spine:[-10,0,12],Spine1:[-8,0,10],Spine2:[-6,0,8],Neck:[-28,0,18],Head:[-24,0,16], SUpLeg:[-75,0,8],SLeg:[100,0,0],SFoot:[-25,0,0], KUpLeg:[-75,0,8],KLeg:[100,0,0],KFoot:[-25,0,0], KArm:[40,0,95],KForeArm:[-25,0,0], SArm:[25,0,80],SForeArm:[-30,0,0]}],   // skid low, arms thrown out
    [36,{Hips:[0,0,0],Spine:[18,0,0],Spine1:[10,0,0],Spine2:[4,0,0],Neck:[-12,0,0],Head:[-8,0,0], SUpLeg:[-48,0,6],SLeg:[72,0,0],SFoot:[-24,0,0], KUpLeg:[-48,0,6],KLeg:[72,0,0],KFoot:[-24,0,0], KArm:[-10,0,25],KForeArm:[-50,0,0], SArm:[-10,0,25],SForeArm:[-50,0,0]}]]},
  // knockdown: fall (A 6) -> down, curled, forearms cover head (X 40) -> get-up (R 24). Systems owns root pitch/position; plant off.
  knockdown:{ kind:'react', A:6, X:40, R:24, hit:[], cancel:{open:50,kinds:['roll']}, root:null, lead:null, mask:'full', plant:'off', hand:{K:'fist',S:'fist'}, keys:[
    [0, {Hips:[-20,0,0],Spine:[-10,0,0],Spine1:[-8,0,0],Spine2:[-6,0,0],Neck:[-20,0,0],Head:[-20,0,0], SUpLeg:[-30,0,10],SLeg:[40,0,0],SFoot:[10,0,0], KUpLeg:[-60,0,10],KLeg:[70,0,0],KFoot:[10,0,0], KArm:[30,0,80],KForeArm:[-30,0,0], SArm:[30,0,80],SForeArm:[-30,0,0]}],
    [6, {Hips:[25,0,0],Spine:[26,0,0],Spine1:[24,0,0],Spine2:[22,0,0],Neck:[18,0,0],Head:[12,0,0], SUpLeg:[-105,0,10],SLeg:[128,0,0],SFoot:[-10,0,0], KUpLeg:[-110,0,10],KLeg:[130,0,0],KFoot:[-10,0,0], KArm:[-110,0,30],KForeArm:[-135,0,0], SArm:[-110,0,30],SForeArm:[-135,0,0]}],   // curled, arms cover
    [46,{Hips:[25,0,0],Spine:[26,0,0],Spine1:[24,0,0],Spine2:[22,0,0],Neck:[18,0,0],Head:[12,0,0], SUpLeg:[-105,0,10],SLeg:[128,0,0],SFoot:[-10,0,0], KUpLeg:[-110,0,10],KLeg:[130,0,0],KFoot:[-10,0,0], KArm:[-110,0,30],KForeArm:[-135,0,0], SArm:[-110,0,30],SForeArm:[-135,0,0]}],
    [58,{Hips:[10,0,0],Spine:[27,0,0],Spine1:[20,0,0],Spine2:[12,0,0],Neck:[-10,0,0],Head:[-10,0,0], SUpLeg:[-110,0,8],SLeg:[132,0,0],SFoot:[-25,0,0], KUpLeg:[-90,0,8],KLeg:[120,0,0],KFoot:[-25,0,0], KArm:[-30,0,40],KForeArm:[-60,0,0], SArm:[-30,0,40],SForeArm:[-60,0,0]}],   // push up to a crouch
    [70,{Hips:[0,0,0],Spine:[18,0,0],Spine1:[10,0,0],Spine2:[4,0,0],Neck:[-12,0,0],Head:[-8,0,0], SUpLeg:[-45,0,6],SLeg:[80,0,0],SFoot:[-24,0,0], KUpLeg:[-45,0,6],KLeg:[80,0,0],KFoot:[-24,0,0], KArm:[-10,0,20],KForeArm:[-40,0,0], SArm:[-10,0,20],SForeArm:[-40,0,0]}]]} };
// ===== Crew K/L specials (Rydah Rigger 2026-10-30): one RIDER_COMBAT_MOVES entry per wallatk MOVESETS crew + key, named `${ATK.set}_${K|L}`
// (K = moves[1], L = moves[2]; J stays the light chain, hold-J heavy stays the shared 'heavy'). Built from 6 kind templates (wallatk kinds
// dash/slam/cone/chain/sweep/dive) x a per-crew style row (Air Gear reference §7.2 where the crew has canon: Ikki wings = wide arms, Buccha/Behemoth
// = heavy mass, low predatory crews low; others original). Data only: templates are key tables, styles scale windup / arm spread / lean / root.
const RIDER_COMBAT_TEMPLATES=(()=>{ const B="SUpLeg:[-40,0,5],SLeg:[70,0,0],SFoot:[-24,0,0], KUpLeg:[-40,0,5],KLeg:[70,0,0],KFoot:[-24,0,0]", P=s=>Function('return {'+s+'}')();
  const LC="SUpLeg:[-70,0,6],SLeg:[95,0,0],SFoot:[-25,0,0], KUpLeg:[-92,0,6],KLeg:[128,0,0],KFoot:[-25,0,0]", LH="SUpLeg:[-62,0,4],SLeg:[88,0,0],SFoot:[-25,0,0], KUpLeg:[-62,0,10],KLeg:[122,0,0],KFoot:[-25,0,0]";
  const N="Spine:[16,2,0],Spine1:[10,2,0],Spine2:[6,2,0],Neck:[-12,-2,0],Head:[-8,-2,0], KShoulder:[0,0,0],KArm:[-25,0,18],KForeArm:[-95,0,0],KHand:[0,0,0], SShoulder:[0,0,0],SArm:[-30,0,18],SForeArm:[-95,0,0],SHand:[0,0,0]";
  return {
  // dash: committed lunge-strike (finisher geometry: S skate planted, rear skate tucked), longer travel
  dash:{ A:8, X:6, R:22, hit:[13], root:{fwd:2.5,from:6,to:14}, lead:'KArm', mask:'full', plant:'S', keys:[
    [0,P("Hips:[0,0,0],"+N+","+B)],
    [8,P("Hips:[0,24,0],Spine:[14,12,0],Spine1:[10,9,0],Spine2:[6,9,0],Neck:[-12,-16,0],Head:[-10,-18,0], KShoulder:[-12,-12,-4],KArm:[-45,0,26],KForeArm:[-105,0,0],KHand:[10,0,0], SShoulder:[0,0,0],SArm:[-55,0,22],SForeArm:[-35,0,0],SHand:[0,0,0],"+LC)],
    [13,P("Hips:[0,-28,0],Spine:[24,-11,0],Spine1:[22,-8,0],Spine2:[18,-8,0],Neck:[-24,14,0],Head:[-18,16,0], KShoulder:[13,13,6],KArm:[-145,0,6],KForeArm:[-3,0,0],KHand:[0,0,-8], SShoulder:[0,0,0],SArm:[45,0,22],SForeArm:[-45,0,0],SHand:[0,0,0],"+LH)],
    [18,P("Hips:[0,-24,0],Spine:[21,-8,0],Spine1:[18,-6,0],Spine2:[14,-6,0],Neck:[-20,10,0],Head:[-15,11,0], KShoulder:[8,8,4],KArm:[-125,0,8],KForeArm:[-12,0,0],KHand:[0,0,-4], SShoulder:[0,0,0],SArm:[32,0,24],SForeArm:[-60,0,0],SHand:[0,0,0],"+LH)],
    [26,P("Hips:[0,-8,0],Spine:[18,-4,0],Spine1:[12,-3,0],Spine2:[8,-3,0],Neck:[-14,5,0],Head:[-10,6,0], KShoulder:[4,4,2],KArm:[-55,0,14],KForeArm:[-60,0,0],KHand:[0,0,0], SShoulder:[0,0,0],SArm:[-10,0,22],SForeArm:[-100,0,0],SHand:[0,0,0],"+B)],
    [36,P("Hips:[0,0,0],"+N+","+B)]]},
  // slam: lowered-shoulder charge (Shoulder Slam / Genesis Flare): load, then drive the K shoulder through, lead arm tucked, head tucked behind it
  slam:{ A:10, X:6, R:22, hit:[15], root:{fwd:2.0,from:8,to:16}, lead:'KArm', mask:'full', plant:'S', keys:[
    [0,P("Hips:[0,0,0],"+N+","+B)],
    [10,P("Hips:[0,22,0],Spine:[18,10,0],Spine1:[12,8,0],Spine2:[8,8,0],Neck:[-14,-14,0],Head:[-10,-16,0], KShoulder:[-10,-10,6],KArm:[-20,0,30],KForeArm:[-120,0,0],KHand:[0,0,0], SShoulder:[0,0,0],SArm:[-40,0,25],SForeArm:[-90,0,0],SHand:[0,0,0],"+LC)],
    [15,P("Hips:[0,-30,0],Spine:[24,-12,6],Spine1:[22,-9,6],Spine2:[18,-9,4],Neck:[-20,14,-8],Head:[-14,16,-8], KShoulder:[14,14,-8],KArm:[-35,0,12],KForeArm:[-125,0,0],KHand:[0,0,0], SShoulder:[0,0,0],SArm:[40,0,28],SForeArm:[-80,0,0],SHand:[0,0,0],"+LH)],
    [20,P("Hips:[0,-24,0],Spine:[22,-9,4],Spine1:[19,-7,4],Spine2:[15,-7,2],Neck:[-18,10,-4],Head:[-12,11,-4], KShoulder:[8,9,-4],KArm:[-35,0,16],KForeArm:[-115,0,0],KHand:[0,0,0], SShoulder:[0,0,0],SArm:[28,0,26],SForeArm:[-85,0,0],SHand:[0,0,0],"+LH)],
    [28,P("Hips:[0,-8,0],Spine:[18,-4,0],Spine1:[12,-3,0],Spine2:[8,-3,0],Neck:[-14,5,0],Head:[-10,6,0], KShoulder:[4,4,0],KArm:[-35,0,18],KForeArm:[-95,0,0],KHand:[0,0,0], SShoulder:[0,0,0],SArm:[-10,0,22],SForeArm:[-100,0,0],SHand:[0,0,0],"+B)],
    [38,P("Hips:[0,0,0],"+N+","+B)]]},
  // cone: two-hand forward blast/claw (Crow Rush, Halo Slash, Jackal Fang, Halo Kick, Rivet Burst): both hands chamber at the chest, then thrust together
  cone:{ A:7, X:5, R:16, hit:[11], root:{fwd:.5,from:5,to:12}, lead:'BArm', mask:'upper', plant:'both', keys:[
    [0,P(N)],
    [7,P("Spine:[8,0,0],Spine1:[4,0,0],Spine2:[2,0,0],Neck:[-6,0,0],Head:[-6,0,0], KShoulder:[-10,-10,0],KArm:[-40,0,30],KForeArm:[-110,0,0],KHand:[15,0,0], SShoulder:[-10,-10,0],SArm:[-40,0,30],SForeArm:[-110,0,0],SHand:[15,0,0]")],
    [11,P("Spine:[22,0,0],Spine1:[16,0,0],Spine2:[12,0,0],Neck:[-18,0,0],Head:[-14,0,0], KShoulder:[12,12,4],KArm:[-120,0,14],KForeArm:[-8,0,0],KHand:[-30,0,0], SShoulder:[12,12,4],SArm:[-120,0,14],SForeArm:[-8,0,0],SHand:[-30,0,0]")],
    [16,P("Spine:[19,0,0],Spine1:[13,0,0],Spine2:[9,0,0],Neck:[-15,0,0],Head:[-11,0,0], KShoulder:[8,8,2],KArm:[-105,0,16],KForeArm:[-18,0,0],KHand:[-20,0,0], SShoulder:[8,8,2],SArm:[-105,0,16],SForeArm:[-18,0,0],SHand:[-20,0,0]")],
    [28,P(N)]]},
  // chain: casting point (Chain Shock, Scales of Judgement, Lullaby Leaves): torso winds, lead arm drives up-forward to aim the arc, rear arm sweeps back
  chain:{ A:8, X:5, R:18, hit:[12], root:null, lead:'KArm', mask:'upper', plant:'both', keys:[
    [0,P(N)],
    [8,P("Spine:[10,12,0],Spine1:[6,9,0],Spine2:[4,9,0],Neck:[-8,-14,0],Head:[-6,-16,0], KShoulder:[-10,-10,0],KArm:[-50,0,40],KForeArm:[-115,0,0],KHand:[10,0,0], SShoulder:[0,0,0],SArm:[-45,0,30],SForeArm:[-60,0,0],SHand:[0,0,0]")],
    [12,P("Spine:[16,-11,0],Spine1:[10,-8,0],Spine2:[6,-8,0],Neck:[-14,14,0],Head:[-12,16,0], KShoulder:[12,13,8],KArm:[-145,0,20],KForeArm:[-5,0,0],KHand:[-35,0,0], SShoulder:[0,0,0],SArm:[35,0,40],SForeArm:[-40,0,0],SHand:[0,0,0]")],
    [18,P("Spine:[15,-8,0],Spine1:[9,-6,0],Spine2:[5,-6,0],Neck:[-13,10,0],Head:[-11,11,0], KShoulder:[8,9,6],KArm:[-135,0,22],KForeArm:[-10,0,0],KHand:[-25,0,0], SShoulder:[0,0,0],SArm:[25,0,38],SForeArm:[-50,0,0],SHand:[0,0,0]")],
    [31,P(N)]]},
  // sweep: crescent leg sweep off the support skate (Angel Wing Burst, Wrench Spin, Rebirth Spiral); the 360 is root yaw (Systems), arms open wide
  sweep:{ A:10, X:6, R:20, hit:[15], root:null, lead:'KLeg', mask:'full', plant:'S',   /* pivots on the planted support skate; no hip yaw (spine carries the twist); the sweeping K skate stays above the deck */ keys:[
    [0,P("Hips:[0,0,0],"+N+","+B)],
    [10,P("Hips:[0,0,0],Spine:[22,10,0],Spine1:[14,8,0],Spine2:[8,8,0],Neck:[-18,-12,0],Head:[-12,-14,0], KShoulder:[0,0,0],KArm:[-20,0,60],KForeArm:[-60,0,0],KHand:[0,0,0], SShoulder:[0,0,0],SArm:[-30,0,60],SForeArm:[-60,0,0],SHand:[0,0,0], SUpLeg:[-70,0,5],SLeg:[95,0,0],SFoot:[-25,0,0], KUpLeg:[-95,0,10],KLeg:[125,0,0],KFoot:[-20,0,0]")],
    [15,P("Hips:[0,0,0],Spine:[14,-11,-8],Spine1:[10,-8,-6],Spine2:[6,-8,-4],Neck:[-12,14,6],Head:[-10,16,6], KShoulder:[0,0,0],KArm:[-10,0,85],KForeArm:[-20,0,0],KHand:[0,0,0], SShoulder:[0,0,0],SArm:[-10,0,85],SForeArm:[-20,0,0],SHand:[0,0,0], SUpLeg:[-58,0,4],SLeg:[85,0,0],SFoot:[-25,0,0], KUpLeg:[-75,0,36],KLeg:[60,0,0],KFoot:[-20,0,0]")],
    [21,P("Hips:[0,0,0],Spine:[15,-8,-6],Spine1:[10,-6,-4],Spine2:[6,-6,-2],Neck:[-12,10,4],Head:[-10,11,4], KShoulder:[0,0,0],KArm:[-10,0,75],KForeArm:[-30,0,0],KHand:[0,0,0], SShoulder:[0,0,0],SArm:[-10,0,75],SForeArm:[-30,0,0],SHand:[0,0,0], SUpLeg:[-58,0,4],SLeg:[85,0,0],SFoot:[-25,0,0], KUpLeg:[-75,0,30],KLeg:[80,0,0],KFoot:[-20,0,0]")],
    [28,P("Hips:[0,0,0],"+N+", SUpLeg:[-45,0,5],SLeg:[75,0,0],SFoot:[-24,0,0], KUpLeg:[-60,0,8],KLeg:[105,0,0],KFoot:[-20,0,0]")],
    [36,P("Hips:[0,0,0],"+N+","+B)]]},
  // dive: aerial dive kick / stomp (Thunder Drop, Raven Dive Kick, Static Fall, Ground Pound, Ankh Dive, Canopy Drop, Tool Drop): tuck, then the
  // K leg spears down-forward, S leg tucked, arms thrown up-back. Airborne: plant off (Systems owns the arc and the landing).
  dive:{ A:8, X:8, R:18, hit:[14], root:null, lead:'KLeg', mask:'full', plant:'off', keys:[
    [0,P("Hips:[0,0,0],"+N+","+B)],
    [8,P("Hips:[0,0,0],Spine:[26,0,0],Spine1:[20,0,0],Spine2:[12,0,0],Neck:[-20,0,0],Head:[-14,0,0], KShoulder:[0,0,0],KArm:[-60,0,30],KForeArm:[-110,0,0],KHand:[0,0,0], SShoulder:[0,0,0],SArm:[-60,0,30],SForeArm:[-110,0,0],SHand:[0,0,0], SUpLeg:[-100,0,8],SLeg:[120,0,0],SFoot:[-15,0,0], KUpLeg:[-100,0,8],KLeg:[120,0,0],KFoot:[-15,0,0]")],
    [14,P("Hips:[0,0,0],Spine:[10,0,0],Spine1:[6,0,0],Spine2:[4,0,0],Neck:[-14,0,0],Head:[-12,0,0], KShoulder:[0,0,0],KArm:[30,0,70],KForeArm:[-40,0,0],KHand:[0,0,0], SShoulder:[0,0,0],SArm:[30,0,70],SForeArm:[-40,0,0],SHand:[0,0,0], SUpLeg:[-95,0,8],SLeg:[120,0,0],SFoot:[-15,0,0], KUpLeg:[-55,0,6],KLeg:[5,0,0],KFoot:[-20,0,0]")],
    [16,P("Hips:[0,0,0],Spine:[10,0,0],Spine1:[6,0,0],Spine2:[4,0,0],Neck:[-14,0,0],Head:[-12,0,0], KShoulder:[0,0,0],KArm:[32,0,72],KForeArm:[-38,0,0],KHand:[0,0,0], SShoulder:[0,0,0],SArm:[32,0,72],SForeArm:[-38,0,0],SHand:[0,0,0], SUpLeg:[-95,0,8],SLeg:[120,0,0],SFoot:[-15,0,0], KUpLeg:[-55,0,6],KLeg:[5,0,0],KFoot:[-20,0,0]")],
    [26,P("Hips:[0,0,0],Spine:[20,0,0],Spine1:[12,0,0],Spine2:[6,0,0],Neck:[-14,0,0],Head:[-10,0,0], KShoulder:[0,0,0],KArm:[-20,0,40],KForeArm:[-80,0,0],KHand:[0,0,0], SShoulder:[0,0,0],SArm:[-20,0,40],SForeArm:[-80,0,0],SHand:[0,0,0], SUpLeg:[-60,0,6],SLeg:[95,0,0],SFoot:[-25,0,0], KUpLeg:[-60,0,6],KLeg:[95,0,0],KFoot:[-25,0,0]")],
    [34,P("Hips:[0,0,0],"+N+","+B)]]} }; })();
// per-crew style: A = windup scale, arm = Arm z spread scale, lean = Spine/Spine1 x add (deg), root = travel scale
const RIDER_COMBAT_CREW_STYLE={
  codee:   { A:.8,  arm:.9,  lean:0,  root:1.2, note:'Code : E (Caali G) lightning: short sharp windup, tight arms, long dash' },
  karasu:  { A:1,   arm:1.3, lean:-2, root:1.1, note:'Kogarasumaru (Ikki, Wing Road §7.2): open, airy, arms like wings' },
  static:  { A:1,   arm:1.15,lean:-2, root:1,   note:'Static Angels: upright, high open arms (halo)' },
  behemoth:{ A:1.4, arm:.8,  lean:3,  root:.8,  note:'Behemoth (Buccha-style mass §7.2): long heavy windup, compact, leaning in' },
  anubis:  { A:.8,  arm:.9,  lean:3,  root:1,   note:'Anubis: low predatory jackal, quick' },
  forest:  { A:1.1, arm:1.1, lean:0,  root:1,   note:'Sleeping Forest (Thorn Road, Ringo): flowing, slightly wide' },
  genesis: { A:1,   arm:1,   lean:1,  root:1,   note:'Genesis: neutral template' },
  ttt:     { A:.9,  arm:.9,  lean:2,  root:1,   note:'Tool Toul To: mechanic, compact and blunt' } };
const RIDER_COMBAT_CREW_MOVES={   // wallatk.js MOVESETS (read-only copy of set -> [K, L] = [moves[1], moves[2]] name + kind)
  codee:[['Chain Shock','chain'],['Thunder Drop','dive']], karasu:[['Crow Rush','cone'],['Raven Dive Kick','dive']], static:[['Angel Wing Burst','sweep'],['Static Fall','dive']],
  behemoth:[['Horn Rush','dash'],['Ground Pound','dive']], anubis:[['Scales of Judgement','chain'],['Ankh Dive','dive']], forest:[['Lullaby Leaves','chain'],['Canopy Drop','dive']],
  genesis:[['Rebirth Spiral','sweep'],['Genesis Flare','slam']], ttt:[['Rivet Burst','cone'],['Tool Drop','dive']] };
RIDER_COMBAT_LEAD.BArm=['Shoulder','Arm','ForeArm','Hand'];   // both arms (cone): the S side is added in combatStart
for(const set in RIDER_COMBAT_CREW_MOVES) RIDER_COMBAT_CREW_MOVES[set].forEach(([label,kind],i)=>{ const T=RIDER_COMBAT_TEMPLATES[kind], st=RIDER_COMBAT_CREW_STYLE[set]||{A:1,arm:1,lean:0,root:1}, A=Math.max(4,Math.round(T.A*st.A)), d=A-T.A;
  const keys=T.keys.map(([f,v])=>{ const o={}; for(const n in v){ const q=v[n].slice(); if(/Arm$/.test(n)&&!/Fore/.test(n)) q[2]=+(q[2]*st.arm).toFixed(1); if(n==='Spine'||n==='Spine1'){ const L=RIDER_JOINT_LIMITS[n].x; q[0]=+Math.min(L[1],Math.max(L[0],q[0]+st.lean)).toFixed(1); } o[n]=q; } return [f===0?0:f+d,o]; });
  RIDER_COMBAT_MOVES[set+'_'+(i?'L':'K')]={ kind:'atk', step:-1, crew:set, key:i?'L':'K', label, tkind:kind, A, X:T.X, R:T.R, hit:T.hit.map(h=>h+d), cancel:null,
    root:T.root?{fwd:+(T.root.fwd*st.root).toFixed(2),from:T.root.from+d,to:T.root.to+d}:null, lead:T.lead, mask:T.mask, plant:T.plant, hand:{K:'fist',S:kind==='cone'||kind==='sweep'?'relaxed':'fist'}, keys }; });
const RIDER_COMBAT_STEP_MOVES=['light1','light2','finisher'];   // Systems chain CHAIN.n 0/1/2 -> move (hit 3 IS the finisher; no 4th hit)
const RIDER_COMBAT_REACT={ light:'react_light', heavy:'react_heavy', knockdown:'knockdown' };
// frame timeline for a move under a combat-feel row: authored A/X/R -> scaled a/x/r, piecewise key remap, events
function riderCombatTimeline(m,cf){ const a=Math.max(1,Math.round(m.A*cf.windup)), x=Math.max(1,Math.round(m.X*cf.release)), r=Math.max(2,Math.round(m.R*cf.recover)), end=a+x+r;
  const map=f=>f<=m.A?f*a/m.A:f<=m.A+m.X?a+(f-m.A)*x/m.X:a+x+(f-m.A-m.X)*r/m.R;
  const hit=(m.hit||[]).map(h=>a+Math.min(x-1,Math.round((h-m.A)*cf.release)));
  const cancel=m.cancel?{open:Math.max(m.cancel.open,(hit.length?hit[hit.length-1]+1:0)),close:end-1,kinds:m.cancel.kinds.slice()}:null;
  const root=m.root?{fwd:m.root.fwd*cf.root,from:map(m.root.from),to:map(m.root.to)}:null;
  const keys=m.keys.map((k,i)=>{ if(k[2]!=='over'||!i) return [map(k[0]),k[1]]; const p=m.keys[i-1][1], v={};   // overshoot key: hit pose + (authored overshoot) x feel.over
    for(const n in k[1]){ const a=p[n]||k[1][n]; v[n]=k[1][n].map((x,j)=>a[j]+(x-a[j])*cf.over); } return [map(k[0]),v]; });
  return {a,x,r,end,hit,cancel,root,keys}; }
// sample a timeline at fractional frame ff -> {bone:[x,y,z] deg} with side mapping/mirroring, lead amp, twist, react pitch flip (fb)
function riderCombatSample(m,TL,ff,side,cf,fb){ const K=TL.keys; let i=0; while(i<K.length-2&&ff>K[i+1][0]) i++;
  const a=K[i], b=K[i+1], u=Math.min(1,Math.max(0,(ff-a[0])/Math.max(1e-6,b[0]-a[0]))), e=u*u*(3-2*u), out={}, sSide=side==='Left'?'Right':'Left', leadP=m.lead?m.lead[1]:null;
  for(const n in b[1]){ const p=a[1][n]||b[1][n], q=b[1][n]; const v=[0,1,2].map(j=>p[j]+(q[j]-p[j])*e);
    const role=/^K(?=[A-Z])/.test(n)?'K':/^S(?=(UpLeg|Leg|Foot|Arm|ForeArm|Hand|Shoulder)$)/.test(n)?'S':null, base=role?n.slice(1):n, nm=role==='K'?side+base:role==='S'?sSide+base:n;
    if((role==='K'||(role==='S'&&m.lead==='BArm'))&&m.lead&&RIDER_COMBAT_LEAD[m.lead].includes(base)&&/^(Arm|ForeArm|UpLeg|Leg)$/.test(base)){ v[0]*=cf.amp; v[2]*=cf.amp; }
    if(!role&&/^(Spine|Spine1|Spine2|Neck|Head)$/.test(n)){ v[1]*=cf.twist; if(fb<0&&m.dirFlip&&v[0]<0) v[0]=-v[0]*.75; }   // hit from behind: extension -> forward flex
    if(nm.startsWith('Right')||(!role&&side==='Right')){ v[1]=-v[1]; v[2]=-v[2]; }
    out[nm]=v; }
  return out; }
function riderSoftClamp(v,lo,hi,k){ if(hi-lo<1e-6) return lo; k=Math.min(k,(hi-lo)*.25); const a=lo+k, b=hi-k; return v>b?b+k*Math.tanh((v-b)/k):v<a?a-k*Math.tanh((a-v)/k):v; }
// ===== generic spring-bone solver (Rydah Rigger 2026-10-30; no rider names). Reads bone userData.spring {chain,index,kind,tail,stiffness,damping,gravity,drag}
// (glTF node extras). Verlet per chain, kinematic rest target from the parent, gravity relative to the bind (rest pose = equilibrium), length + swing limits,
// sphere colliders (hips, chest, thighs, shins) + deck plane. Runs after pose()+plant(); only when the camera is within RIDER_SPRING_DIST; no draws.
const RIDER_SPRING_KIND={ braid:{stiffness:60,damping:.3,gravity:1,drag:.3,maxSwing:70,maxLink:35}, skirt:{stiffness:90,damping:.45,gravity:.5,drag:.4,maxSwing:40,maxLink:40},
  strap:{stiffness:45,damping:.35,gravity:1,drag:.8,maxSwing:50,maxLink:25} }, RIDER_SPRING_DIST=12;
const RIDER_SPRING_COLL=[['Hips','Spine',0,.12],['Spine2','Neck',.3,.13],['LeftUpLeg','LeftLeg',.3,.085],['LeftUpLeg','LeftLeg',.68,.075],['RightUpLeg','RightLeg',.3,.085],['RightUpLeg','RightLeg',.68,.075],
  ['LeftLeg','LeftFoot',.3,.06],['RightLeg','RightFoot',.3,.06]];   // [bone, toward bone, t, radius in rider metres (x root scale)]
function riderSpringsInstall(root,bones,ground){ const list=[]; root.traverse(o=>{ if(o.isBone&&o.userData&&o.userData.spring) list.push(o); }); if(!list.length) return null;
  root.updateMatrixWorld(true); const V=()=>new THREE.Vector3(), Q=()=>new THREE.Quaternion(), sc=new THREE.Vector3().setFromMatrixScale(root.matrixWorld).y;
  const by={}; for(const b of list){ const c=b.userData.spring.chain||b.name; (by[c]=by[c]||[]).push(b); }
  const chains=[]; for(const k in by){ const L=by[k].sort((a,b)=>(a.userData.spring.index||0)-(b.userData.spring.index||0)); let cur=null;
    for(const b of L){ if(!cur||b.parent!==cur[cur.length-1]){ cur=[b]; chains.push(cur); } else cur.push(b); } }   // serial chains; siblings (skirt sectors) -> 1-bone chains
  const coll=RIDER_SPRING_COLL.filter(c=>bones[c[0]]&&bones[c[1]]).map(c=>({a:bones[c[0]],b:bones[c[1]],t:c[2],r:c[3]*sc,c:V()}));
  const _pa=V(), _pb=V(), _m=new THREE.Matrix4(), _m2=new THREE.Matrix4(), _one=new THREE.Vector3(1,1,1), _d=V(), _r=V(), _q=Q(), _q2=Q(), _q3=Q(), G=new THREE.Vector3(0,-9.81,0), _g=V(), _v=V();
  const placeC=()=>{ for(const c of coll){ c.a.getWorldPosition(_pa); c.b.getWorldPosition(_pb); c.c.copy(_pa).lerp(_pb,c.t); } };
  placeC();
  const C=chains.map(bs=>{ const sp=bs[0].userData.spring, K=Object.assign({},RIDER_SPRING_KIND[sp.kind]||RIDER_SPRING_KIND.strap);
      for(const k of ['stiffness','damping','gravity','drag','maxSwing','maxLink']) if(typeof sp[k]==='number') K[k]=sp[k];
      const tails=bs.map((b,i)=>i<bs.length-1?bs[i+1].position.clone():new THREE.Vector3().fromArray(b.userData.spring.tail||[0,.05,0]));
      const ch={bs,K,parent:bs[0].parent,restQ:bs.map(b=>b.quaternion.clone()),tails,dirL:tails.map(t=>t.clone().normalize()),len:[],p:bs.map(V),pp:bs.map(V),tg:bs.map(V),hd:bs.map(V),q0:Q(),rad:[]};
      ch.parent.getWorldQuaternion(ch.q0); kin(ch); ch.p.forEach((p,i)=>{ p.copy(ch.tg[i]); ch.pp[i].copy(p); ch.len[i]=ch.tg[i].distanceTo(ch.hd[i]); });
      ch.rad=ch.p.map(p=>coll.map(c=>Math.min(c.r,p.distanceTo(c.c)*.95)));   // never start inside a collider: radius capped at the rest distance
      return ch; });
  function kin(ch){ _m.copy(ch.parent.matrixWorld); for(let i=0;i<ch.bs.length;i++){ const b=ch.bs[i]; _m2.compose(b.position,ch.restQ[i],_one); _m.multiply(_m2); ch.hd[i].setFromMatrixPosition(_m); ch.tg[i].copy(ch.tails[i]).applyMatrix4(_m); } }
  function rest(ch){ ch.bs.forEach((b,i)=>b.quaternion.copy(ch.restQ[i])); ch.bs[0].updateMatrixWorld(true); kin(ch); ch.p.forEach((p,i)=>{ p.copy(ch.tg[i]); ch.pp[i].copy(p); }); }
  const S={chains:C, coll, on:true, active:false, ms:0, msAvg:0, n:0, resets:0, nan:0,
    step(dt,camDist){ if(!this.on||!(dt>0)) return; const far=camDist!==undefined&&camDist>RIDER_SPRING_DIST;
      if(far){ if(this.active){ for(const ch of C) rest(ch); this.active=false; } return; }
      const t0=performance.now(); if(!this.active){ for(const ch of C) rest(ch); this.active=true; }
      dt=Math.min(dt,1/20); const ns=dt>1/50?2:1, h=dt/ns; placeC(); const gy=ground?ground():-1e9;
      for(const ch of C){ kin(ch); const K=ch.K; ch.parent.getWorldQuaternion(_q); _q2.copy(ch.q0).invert().premultiply(_q);   // parent rotation since bind
        _g.copy(G).sub(_v.copy(G).applyQuaternion(_q2)).multiplyScalar(K.gravity);   // gravity minus the bind gravity carried by the parent
        if(ch.p[0].distanceToSquared(ch.tg[0])>4*sc*sc){ rest(ch); this.resets++; continue; }   // teleport
        for(let s=0;s<ns;s++){ const kd=Math.pow(1-K.damping,h*60)*Math.exp(-K.drag*h);
          for(let i=0;i<ch.bs.length;i++){ const p=ch.p[i], pp=ch.pp[i]; _v.copy(p).sub(pp).multiplyScalar(kd); pp.copy(p);
            _d.copy(ch.tg[i]).sub(p).multiplyScalar(K.stiffness).add(_g); p.add(_v).addScaledVector(_d,h*h);
            }
          for(let it=0;it<2;it++){ let hx=ch.hd[0];   // length + swing limits root -> tip, then colliders + deck; 2 passes so the length pass cannot pull a particle back inside
            for(let i=0;i<ch.bs.length;i++){ const p=ch.p[i]; _d.copy(p).sub(hx); const l=_d.length(); _r.copy(ch.tg[i]).sub(ch.hd[i]).normalize(); if(l<1e-7) _d.copy(_r); else _d.divideScalar(l);
              const mx=(i?K.maxLink:K.maxSwing)*Math.PI/180, a=Math.acos(THREE.MathUtils.clamp(_d.dot(_r),-1,1)); if(a>mx){ _q3.setFromUnitVectors(_r,_d); _q.identity().slerp(_q3,mx/a); _d.copy(_r).applyQuaternion(_q); }
              p.copy(hx).addScaledVector(_d,ch.len[i]);
              for(let j=0;j<coll.length;j++){ const r=ch.rad[i][j]; if(r<=0) continue; _d.copy(p).sub(coll[j].c); const l2=_d.length(); if(l2<r&&l2>1e-6) p.addScaledVector(_d,(r-l2)/l2); }
              if(p.y<gy+.01*sc) p.y=gy+.01*sc; hx=p; } } }
        let bad=false; for(const p of ch.p) if(!Number.isFinite(p.x+p.y+p.z)) bad=true; if(bad){ this.nan++; rest(ch); continue; }
        // write rotations: bone i points its rest tail at the solved particle
        ch.parent.getWorldQuaternion(_q); for(let i=0;i<ch.bs.length;i++){ const b=ch.bs[i]; _q2.copy(_q).multiply(ch.restQ[i]);   // rest world rot
          const head=i?ch.p[i-1]:ch.hd[0]; _d.copy(ch.p[i]).sub(head).normalize(); _r.copy(ch.dirL[i]).applyQuaternion(_q2);
          _q3.setFromUnitVectors(_r,_d).multiply(_q2); b.quaternion.copy(_q).invert().multiply(_q3); _q.copy(_q3); }
        ch.bs[0].updateMatrixWorld(true); }
      const ms=performance.now()-t0; this.ms=ms; this.n++; this.msAvg+=(ms-this.msAvg)/Math.min(this.n,120); },
    reset(){ for(const ch of C) rest(ch); } };
  return S; }
async function loadIkki(parent,refH,fresh){ const c=rResolve(IKKI_DEFAULTS,{});
  const gltf=await (fresh?new Promise((res,rej)=>new THREE.GLTFLoader().load(IKKI_URL,res,undefined,rej)):rLoad(IKKI_URL)); // separate parse per instance (no SkeletonUtils.clone in r128 core)
  const root=gltf.scene, lv=[], bones={};
  root.traverse(o=>{ if(o.isSkinnedMesh){ const m=o.name.match(/LOD(\d)/); lv[m?+m[1]:lv.length]=o; } if(o.isBone) bones[o.name.replace(/^mixamorig:?/,'')]=o; });
  if(!lv[0]) throw new Error("ikki: no skinned mesh");
  // v3 (locked brief): stylized realism, NOT toon. MeshStandard PBR with the Meshy maps (atlas: body + AT skate), env reflections, neon emissive, scene bloom/grade.
  const src=lv[0].material, Q=new URLSearchParams(location.search), hx=(k,d)=>new THREE.Color(parseInt(Q.get(k)||d,16));
  for(const t of [src.map,src.normalMap,src.roughnessMap,src.metalnessMap]) if(t){ t.encoding=THREE.LinearEncoding; t.anisotropy=4; t.needsUpdate=true; }
  // A·T loadout slots (Midnight Club style): paint = boot shell tint, frame = chassis tint, wheel = wheel/hub tint, glow = all skate neon. ?atPaint=&atFrame=&atWheel=&atGlow=
  const sh={ glowC:{value:hx('atGlow',IKKI_WHEEL_GLOW.toString(16).padStart(6,'0'))}, paintC:{value:hx('atPaint','ffffff')}, frameC:{value:hx('atFrame','ffffff')}, wheelC:{value:hx('atWheel','ffffff')},
    rimColor:{value:new THREE.Color(c.rim)}, spin:{value:0}, comp:{value:0}, boost:{value:0}, time:{value:0}, lightDirV:{value:new THREE.Vector3()} };
  const mat=new THREE.MeshStandardMaterial({color:0xffffff,map:src.map,normalMap:src.normalMap,normalScale:src.normalScale,roughnessMap:src.roughnessMap,metalnessMap:src.metalnessMap,roughness:1,metalness:1,skinning:true,envMap:ikkiEnv(),envMapIntensity:1.3});
  mat.onBeforeCompile=s=>{ Object.assign(s.uniforms,{uSpin:sh.spin,uComp:sh.comp,uBoost:sh.boost,uTime:sh.time,uGlowC:sh.glowC,uPaint:sh.paintC,uFrame:sh.frameC,uWheel:sh.wheelC,uRimColor:sh.rimColor});
    s.vertexShader=IKKI_AT_VERT(s.vertexShader,true);
    s.fragmentShader=s.fragmentShader.replace('#include <common>','#include <common>\n uniform float uBoost; uniform float uTime; uniform vec3 uGlowC; uniform vec3 uPaint; uniform vec3 uFrame; uniform vec3 uWheel; uniform vec3 uRimColor; varying vec3 vFlag; varying float vRestY;')
     .replace('#include <map_fragment>',`#include <map_fragment>
       float sid=floor(vFlag.r*16.+.5); float atSk=step(10.5,sid); vec3 atT=diffuseColor.rgb;
       float atGlowM=atSk*smoothstep(.1,.28,min(atT.g,atT.b)-atT.r)*smoothstep(.25,.5,max(atT.g,atT.b));   // the Meshy neon panels/rims
       diffuseColor.rgb*=sid==11.?uPaint:sid==12.?uWheel:sid==13.?uFrame:vec3(1.);
       diffuseColor.rgb=mix(diffuseColor.rgb,vec3(.02),atGlowM*.8);
       float atShellM=float(sid==11.||sid==13.)*(1.-atGlowM);   // v4: lift near-black navy shell to dark gunmetal
       diffuseColor.rgb=mix(diffuseColor.rgb,max(diffuseColor.rgb*1.6,vec3(.17,.18,.21)),atShellM);
       { vec3 q=diffuseColor.rgb; float mx=max(q.r,max(q.g,q.b)), mn=min(q.r,min(q.g,q.b)); float blu=(1.-atSk)*step(q.r+.05,q.b)*step(q.r,q.g)*smoothstep(.15,.35,(mx-mn)/max(mx,1e-3))*smoothstep(.86,.92,vRestY)*(1.-smoothstep(1.44,1.48,vRestY));
         diffuseColor.rgb=mix(q,vec3(0.,.898,1.)*clamp(mx*1.7,.25,1.),blu*0.); }   /* Oliver 2026-10-29: Ikki's purple jacket stays purple (jacket->cyan remap OFF; blu kept for patch anchors) */
       vec3 sk0=diffuseColor.rgb; float atSkin=(1.-atSk)*step(sk0.b+.04,sk0.g)*step(sk0.g+.03,sk0.r)*smoothstep(.25,.45,sk0.r)*step(1.3,vRestY);   // v6: face/neck skin   // jacket steel-blue -> vivid #00E5FF`)
     .replace('#include <roughnessmap_fragment>','#include <roughnessmap_fragment>\n roughnessFactor=mix(max(roughnessFactor,.55),roughnessFactor,atSk); roughnessFactor=mix(roughnessFactor,.28,atShellM); roughnessFactor=mix(roughnessFactor,.75,atSkin);')
     .replace('#include <metalnessmap_fragment>','#include <metalnessmap_fragment>\n metalnessFactor*=mix(.15,1.,atSk); metalnessFactor=mix(metalnessFactor,.75,atShellM); metalnessFactor*=1.-atSkin;   // Meshy body MR reads as chrome; cloth/skin stay dielectric, skate keeps its metal')
     .replace('#include <emissivemap_fragment>',`#include <emissivemap_fragment>
       float led=.8+.2*sin(uTime*8.-vRestY*70.); float arc=step(.86,fract(sin(floor(uTime*24.)*17.3+vRestY*400.)*43758.5))*uBoost;
       totalEmissiveRadiance+=uGlowC*atGlowM*(1.5+uBoost*2.2+arc*3.)*led;
       { vec3 Vd=normalize(vViewPosition); float fr=1.-clamp(dot(normalize(normal),Vd),0.,1.); float low=1.-smoothstep(.55,.9,vRestY); totalEmissiveRadiance+=diffuseColor.rgb*atSkin*.18;  // soft face fill
       totalEmissiveRadiance+=uRimColor*(pow(fr,4.)*.12+pow(fr,2.5)*low*.55); totalEmissiveRadiance+=vec3(.75,.9,1.)*atShellM*pow(fr,5.)*.35; }  // v4: strong cyan rim on boots/lower body + light shell edge  // faint city-neon rim`); };
  mat.customProgramCacheKey=()=>'ikki-pbr-v3';
  const outline=/ikkiOutline=1/.test(location.search); const olM=outline?rOutline(c,{outlineThick:{value:.0012},outlineFar:{value:14}}):null;
  if(olM){ olM.uniforms.uSpin=sh.spin; olM.uniforms.uComp=sh.comp; olM.vertexShader=IKKI_AT_VERT(olM.vertexShader,false); }
  // THREE.LOD chain: 0-9 m 19.7k tris, 9-24 m 9.1k, 24 m+ 2.6k. One draw call per level (+1 only with ?ikkiOutline=1).
  const lod=new THREE.LOD(), dists=[0,9,24], host=lv[0].parent, tris=[];
  lv.forEach((m,i)=>{ m.material=mat; m.frustumCulled=false; m.parent.remove(m); const g=new THREE.Group(); g.add(m);
    if(olM&&i<1){ const ol=new THREE.SkinnedMesh(m.geometry,olM); ol.bind(m.skeleton,m.bindMatrix); ol.frustumCulled=false; g.add(ol); }
    tris.push(m.geometry.index?m.geometry.index.count/3:m.geometry.attributes.position.count/3); lod.addLevel(g,dists[i]??40); });
  host.add(lod);
  // v4 ground read: one decal quad per rider = dark contact blob + soft cyan wheel-light pools under each skate (custom blend: darken then add)
  const gU={uF0:{value:new THREE.Vector2()},uF1:{value:new THREE.Vector2()},uC:{value:sh.glowC.value},uB:{value:0}};
  const gnd=new THREE.Mesh(new THREE.PlaneGeometry(2.4,2.4).rotateX(-Math.PI/2),new THREE.ShaderMaterial({uniforms:gU,transparent:true,depthWrite:false,polygonOffset:true,polygonOffsetFactor:-2,
    blending:THREE.CustomBlending,blendSrc:THREE.OneFactor,blendDst:THREE.OneMinusSrcAlphaFactor,
    vertexShader:'varying vec2 p; void main(){ p=position.xz; gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.); }',
    fragmentShader:'uniform vec2 uF0; uniform vec2 uF1; uniform vec3 uC; uniform float uB; varying vec2 p; void main(){ float d0=length(p-uF0), d1=length(p-uF1); float sh=.55*exp(-pow(length(p-(uF0+uF1)*.5)/.42,2.))+.35*(exp(-d0*d0/.012)+exp(-d1*d1/.012)); float pool=exp(-d0*d0/.09)+exp(-d1*d1/.09); gl_FragColor=vec4(uC*pool*(.35+uB*.5),clamp(sh,0.,.8)); }'}));
  gnd.renderOrder=1; gnd.userData.noMerge=true; scene.add(gnd);
  const H=1.7, s=Math.max(.5,(refH||1.78))/(H+IKKI_DECK_REST), deck=IKKI_DECK_REST*s; // rest pose is measured unscaled
  // ---- procedural skate poser: deltas authored as model-space Euler (char faces +Z, +X = his left), conjugated into each bone's rest frame
  root.updateMatrixWorld(true); const inv=new THREE.Matrix4().copy(root.matrixWorld).invert(), P={}, _m=new THREE.Matrix4(), _p=new THREE.Vector3(), _s=new THREE.Vector3();
  const FING=['Thumb','Index','Middle','Ring','Pinky'], NAMES=['Hips','Spine','Spine1','Spine2','Neck','Head'];
  for(const sd of ['Left','Right']){ NAMES.push(...['UpLeg','Leg','Foot','ToeBase','Shoulder','Arm','ForeArm','Hand'].map(k=>sd+k)); for(const f of FING) for(let i=1;i<=3;i++) NAMES.push(sd+'Hand'+f+i); }
  const missing=NAMES.filter(n=>!bones[n]); if(missing.length) console.warn('rider poser: missing bones (skipped):',missing.join(','));
  for(const n of NAMES){ const b=bones[n]; if(!b) continue; const w=new THREE.Quaternion(); _m.multiplyMatrices(inv,b.matrixWorld).decompose(_p,w,_s); P[n]={b,rest:b.quaternion.clone(),w,wi:w.clone().invert()}; }
  const hips=bones.Hips, hipRest=hips.position.clone(), footL=bones.LeftFoot, footR=bones.RightFoot, _a=new THREE.Vector3(), _b=new THREE.Vector3(), _q=new THREE.Quaternion(), _e=new THREE.Euler();
  let patch=null; if(typeof jacketDecal==='function'&&bones.Spine2&&!/nojacket/.test(location.search)){ const F=Object.assign({back:.15,up:.03,size:.24},typeof JACKET_FIT!=='undefined'?JACKET_FIT:{}, window.__ikkiPatch||{});
    const sp=bones.Spine2, bp=new THREE.Vector3().setFromMatrixPosition(_m.multiplyMatrices(inv,sp.matrixWorld)); patch=jacketDecal('karasu',1); const o=new THREE.Object3D(); root.add(o); o.position.set(bp.x,bp.y+F.up-.13,bp.z-F.back); o.rotation.y=Math.PI; root.updateMatrixWorld(true);
    const pm=new THREE.Matrix4().copy(sp.matrixWorld).invert().multiply(o.matrixWorld); root.remove(o); sp.add(patch); pm.decompose(patch.position,patch.quaternion,patch.scale); patch.scale.multiplyScalar(F.size); }
  root.scale.setScalar(s); root.position.y=deck; root.updateMatrixWorld(true);
  const footRest=Math.min(footL.getWorldPosition(_a).y,footR.getWorldPosition(_b).y)-root.getWorldPosition(new THREE.Vector3()).y;
  const LIM=RIDER_JOINT_LIMITS, D2R=Math.PI/180, R2D=180/Math.PI, KN=LIM.softKnee, dbg={};
  const lim=n=>{ const k=n.replace(/^(Left|Right)/,'').replace(/^Hand(?=Thumb|Index|Middle|Ring|Pinky)/,''); return LIM[k]; };
  const sc=(v,r,mir)=>{ if(!r) return v; const lo=mir?-r[1]:r[0], hi=mir?-r[0]:r[1]; return riderSoftClamp(v*R2D,lo,hi,KN)*D2R; };
  const FEEL=riderFeel((typeof opt!=='undefined'&&opt&&opt.key)||'ikki'); let OV=null, OW=0;   // per-rider feel; active anim-state overlay (riderStateSample) + its weight
  const rot=(n,x,y,z)=>{ const p=P[n]; if(!p) return; const L=lim(n), m=n.startsWith('Right');
    if(/UpLeg$/.test(n)){ x*=FEEL.crouch; z*=FEEL.stance; } else if(/Leg$/.test(n)) x*=FEEL.crouch; else if(/Arm$/.test(n)&&!/Fore/.test(n)) z*=FEEL.armAbd;
    const o=OV&&OW>1e-3&&OV[n]; if(o){ x+=(o[0]*D2R-x)*OW; y+=(o[1]*D2R-y)*OW; z+=(o[2]*D2R-z)*OW; }
    const co=CV&&CW>1e-3&&CV[n]; if(co&&!(CS&&CS.m.mask==='upper'&&RIDER_COMBAT_LOWER.test(n.replace(/^(Left|Right)/,'')))){ x+=(co[0]*D2R-x)*CW; y+=(co[1]*D2R-y)*CW; z+=(co[2]*D2R-z)*CW; }   // combat overlay on top (mask 'upper' keeps the skating legs)   // states blend in model-space Euler, THEN the limits clamp
    if(L){ x=sc(x,L.x,false); y=sc(y,L.y,m); z=sc(z,L.z,m); } dbg[n]=[x*R2D,y*R2D,z*R2D];
    _q.setFromEuler(_e.set(x,y,z,'YXZ')); p.b.quaternion.copy(p.rest).multiply(_q.premultiply(p.wi).multiply(p.w)); };
  // finger frames: flex axis = dir x palmNormal (rotates the phalanx toward the palm), spread axis = dir x side, in each bone's local frame
  const HF={}, _v=new THREE.Vector3(), mp=n=>bones[n]?new THREE.Vector3().setFromMatrixPosition(_m.multiplyMatrices(inv,bones[n].matrixWorld)):null;
  for(const sd of ['Left','Right']){ const h=mp(sd+'Hand'), i1=mp(sd+'HandIndex1'), p1=mp(sd+'HandPinky1'), m1=mp(sd+'HandMiddle1'); if(!h||!i1||!p1||!m1) continue;
    const nrm=new THREE.Vector3().crossVectors(i1.clone().sub(h),p1.clone().sub(h)).normalize(), t2=mp(sd+'HandThumb2'), m4=mp(sd+'HandMiddle4');
    let vote=0; if(t2) vote+=t2.clone().sub(h).dot(nrm); if(m4) vote+=m4.clone().sub(m1).dot(nrm); if(vote<0) nrm.negate();   // palm side, from thumb + rest curl
    const ctr=h.clone().lerp(m1,.75).addScaledVector(nrm,.02);
    for(const f of FING) for(let k=1;k<=3;k++){ const n=sd+'Hand'+f+k, p=P[n], a=mp(n), c=mp(sd+'Hand'+f+(k+1)); if(!p||!a||!c) continue;
      const dir=c.clone().sub(a).normalize(), toL=v=>v.applyQuaternion(p.wi).normalize(), e={b:p.b,rest:p.rest,L:lim(n)};
      const fm=new THREE.Vector3().crossVectors(dir,nrm).normalize(), pa=k===1?h:mp(sd+'Hand'+f+(k-1)), pd=a.clone().sub(pa).normalize();
      e.r0=(f==='Thumb'&&k===1)?0:Math.atan2(new THREE.Vector3().crossVectors(pd,dir).dot(fm),pd.dot(dir))*R2D;   // rest-pose curl already baked in the mesh (poses are ABSOLUTE joint angles)
      e.flex=toL(fm.clone()); if(e.flex.lengthSq()<.5) continue;
      if(f!=='Thumb'&&f!=='Middle'&&k===1){ const sdv=a.clone().sub(m1); sdv.addScaledVector(dir,-sdv.dot(dir)); if(sdv.lengthSq()>1e-8) e.spread=toL(new THREE.Vector3().crossVectors(dir,sdv.normalize())); }
      if(f==='Thumb'&&k===1){ e.spread=toL(new THREE.Vector3().crossVectors(dir,h.clone().sub(m1).cross(nrm).normalize().multiplyScalar(sd==='Left'?1:-1)));
        const tc=ctr.clone().sub(a); tc.addScaledVector(dir,-tc.dot(dir)); if(tc.lengthSq()>1e-8) e.opp=toL(new THREE.Vector3().crossVectors(dir,tc.normalize())); }
      HF[n]=e; } }
  const _qa=new THREE.Quaternion(), _qb=new THREE.Quaternion();
  const finger=(n,flex,spread,opp)=>{ const e=HF[n]; if(!e) return; const L=e.L||{};   // degrees in, soft-clamped per table
    flex=riderSoftClamp(flex,(L.flex||[-90,90])[0],(L.flex||[-90,90])[1],KN)-(e.r0||0); spread=e.spread&&L.spread?riderSoftClamp(spread||0,L.spread[0],L.spread[1],KN):0; opp=e.opp&&L.opp?riderSoftClamp(opp||0,L.opp[0],L.opp[1],KN):0;
    dbg[n]=[flex+(e.r0||0),spread,opp,e.r0||0]; e.b.quaternion.copy(e.rest).multiply(_qa.setFromAxisAngle(e.flex,flex*D2R));
    if(spread) e.b.quaternion.multiply(_qa.setFromAxisAngle(e.spread,spread*D2R)); if(opp) e.b.quaternion.multiply(_qb.setFromAxisAngle(e.opp,opp*D2R)); };
  const HP=RIDER_HAND_POSES, hand=(sd,fist,t)=>{ for(const f of ['Index','Middle','Ring','Pinky']){ const r=HP.relaxed[f], g=HP.fist[f], br=Math.sin(t*.9*FEEL.idleRate+f.length)*1.2*FEEL.idleAmp*(1-fist);   // tiny breathing drift
      for(let k=0;k<3;k++) finger(sd+'Hand'+f+(k+1),r[k]+(g[k]-r[k])*fist+br,k?0:r[3]+(g[3]-r[3])*fist); }
    const r=HP.relaxed.Thumb, g=HP.fist.Thumb, l=k=>r[k]+(g[k]-r[k])*fist; finger(sd+'HandThumb1',l(0),l(3),l(4)); finger(sd+'HandThumb2',l(1)); finger(sd+'HandThumb3',l(2)); };
  // state pose params (radians): crouch=knee depth, lean=spine pitch, abd/ext=push leg out/back, lift=recovery knee lift, arm swing etc.
  const ST=['idle','stride','tuck','grind','air'], W={idle:1,stride:0,tuck:0,grind:0,air:0,kick:0,crouch:0,wall:0,trick:0,polegrind_top:0,polegrind_climb:0,atk:0,react:0}; /* atk/react = combat overlay weights (flag-gated, driven by combatAdvance) */ let OS=null, phase=0, vy=0, lastY=null, land=0, landK=0, forced=null, fistL=0, fistR=0;
  const sm=(e0,e1,x)=>{ const t=THREE.MathUtils.clamp((x-e0)/(e1-e0),0,1); return t*t*(3-2*t); };
  // ===== combat poses runtime (G1; flag-gated by riderCombatOn(); see RIDER_COMBAT_MOVES) =====
  const CFEEL=riderCombatFeel((typeof opt!=='undefined'&&opt&&opt.key)||'ikki'), CBS={onHitFrame:[],onCancelOpen:[],onCancelClose:[],onRecover:[]}, CLOG=[];
  let CS=null, CV=null, CW=0, CPEND=[];
  const cEmit=(type,ev)=>{ CLOG.push([type,ev.move,ev.frame]); if(CLOG.length>64) CLOG.shift(); const ud=root.userData, h=ud&&ud.combatEvents&&ud.combatEvents[type];
    for(const f of [h,...CBS[type]]) if(typeof f==='function') try{ f(ev); }catch(e){ console.warn('combat '+type+' listener failed',e); } };
  const cEv=(type,f,extra)=>Object.assign({type,rider:root,riderId:(typeof opt!=='undefined'&&opt&&opt.key)||'ikki',move:CS.name,kind:CS.kind,step:CS.step,side:CS.side,frame:f,t:f/RIDER_COMBAT_FPS,target:CS.target||null},extra||{});
  function combatStart(n,o){ if(!riderCombatOn()) return false; o=o||{}; let name;
    if(n==='atk') name=o.set&&o.key&&RIDER_COMBAT_MOVES[o.set+'_'+o.key]?o.set+'_'+o.key:o.move&&RIDER_COMBAT_MOVES[o.move]?o.move:RIDER_COMBAT_STEP_MOVES[Math.max(0,Math.min(2,o.step|0))];
    else name=RIDER_COMBAT_REACT[o.kind]||(RIDER_COMBAT_MOVES[o.kind]&&o.kind)||'react_light';
    const m=RIDER_COMBAT_MOVES[name]; if(!m) return false;
    if(CS&&!CS.done){ CPEND.push(['onRecover',cEv('onRecover',CS.f,{interrupted:true,by:name})]); }
    let side=o.side, fb=1;
    if(m.kind==='react'){ const d=o.dir; if(d&&d.isVector3){ const lq=root.getWorldQuaternion(new THREE.Quaternion()).invert(), l=d.clone().applyQuaternion(lq); fb=l.z>0?-1:1; side=side||(l.x>=0?'Left':'Right'); } side=side||'Left'; }
    else if(!side){ const prev=CS&&CS.kind==='atk'&&!CS.done?CS.side:null; side=m.step===1?(prev?(prev==='Left'?'Right':'Left'):(FEEL.kickSide==='Left'?'Right':'Left')):(FEEL.kickSide||'Left'); }
    const TL=riderCombatTimeline(m,CFEEL), lead=new Set(); if(m.lead) for(const sd of m.lead==='BArm'?['Left','Right']:[side]) for(const k of RIDER_COMBAT_LEAD[m.lead]){ const p=P[sd+k]; if(p) lead.add(p.b); }
    for(const k of ['atk','react']) if(k!==m.kind) W[k]=0;
    CS={name,m,TL,kind:m.kind,step:m.step,side,fb,target:o.target||null,t:0,f:-1,done:false,stop:0,charging:!!m.hold&&o.charge!==false,charge:0,lead,w0:W[m.kind]||0,inX:false,cOpen:false};
    return true; }
  function combatAdvance(dt){ if(!CS) return; const TL=CS.TL, F=RIDER_COMBAT_FPS;
    if(CS.stop>0){ CS.stop-=dt; if(CS.stop>0) dt=0; else { dt=-CS.stop; CS.stop=0; } }   // hit-stop: move clock frozen (slew may still settle)
    if(dt>0&&!CS.done){ if(CS.charging&&CS.t*F>=TL.a){ CS.charge+=dt; if(CS.charge>=(CS.m.holdMax||1)) CS.charging=false; } else CS.t+=dt; }
    let f=Math.floor(CS.t*F+1e-6); if(CS.charging&&f>=TL.a) f=TL.a;
    for(let k=CS.f+1;k<=f&&!CS.done;k++){
      TL.hit.forEach((h,i)=>{ if(h===k) CPEND.push(['onHitFrame',cEv('onHitFrame',k,{hitIndex:i,fxCharge:CS.charge}   /* FX-only (Systems owns gameplay charge/knockback) */)]); });
      if(TL.cancel&&k===TL.cancel.open){ CS.cOpen=true; CPEND.push(['onCancelOpen',cEv('onCancelOpen',k,{kinds:TL.cancel.kinds.slice()})]); }
      if(TL.cancel&&k===TL.cancel.close){ CS.cOpen=false; CPEND.push(['onCancelClose',cEv('onCancelClose',k)]); }
      if(k===TL.end){ CS.done=true; CPEND.push(['onRecover',cEv('onRecover',k,{interrupted:false})]); } }
    CS.f=Math.max(CS.f,f); CS.inX=!CS.done&&f>=TL.a&&f<TL.a+TL.x;
    // weight: ramp in over anticipation (from the current weight -> chains stay at 1), hold, ramp out over the last 50% of recovery
    const ff=CS.charging?TL.a:CS.t*F, rin=Math.max(2,TL.a), w0=CS.w0, outS=TL.a+TL.x+TL.r*.5, wi=w0+(1-w0)*sm(0,rin,ff), wo=1-sm(outS,TL.end,ff);
    W[CS.kind]=CS.done?0:Math.min(wi,wo); if(CS.done){ W[CS.kind]=0; CS=null; } }
  function combatDispatch(){ if(!CPEND.length) return; const q=CPEND; CPEND=[]; for(const [type,ev] of q){ if(type==='onHitFrame'){ const b=ev.side&&P[ev.side+(RIDER_COMBAT_MOVES[ev.move].lead==='KLeg'?'Foot':'Hand')]; ev.pos=b?b.b.getWorldPosition(new THREE.Vector3()):null; const U=root.userData, ld=RIDER_COMBAT_MOVES[ev.move].lead, sd=ev.side==='Right'?'R':'L'; ev.fxName=ld==='KLeg'?'foot'+sd:'hand'+sd; ev.fxPos=U.fxPos?U.fxPos(ev.fxName):null; if(ev.fxPos) ev.pos=ev.fxPos; ev.fx=U.fxAll?U.fxAll():{}; } cEmit(type,ev); } }
  const combatApi={
    // generic stance/feel hooks (no rider names here): mirrorStance(true) flips kickSide (K/S roles, planted foot, combat lead side swap);
    // combatFeelMods({windup:x,...}) multiplies the rider's combat feel row (null restores). Rider-specific wiring lives in local-only files via SR_RIDER_HOOKS.
    mirrorStance(on){ if(!this.__msBase) this.__msBase=FEEL.kickSide||'Left'; const B=this.__msBase; FEEL.kickSide=on?(B==='Left'?'Right':'Left'):B; return FEEL.kickSide; },
    combatFeelMods(mods){ if(!this.__cfBase) this.__cfBase=Object.assign({},CFEEL); Object.assign(CFEEL,this.__cfBase); if(mods) for(const k in mods){ const v=mods[k]; if(typeof CFEEL[k]==='number') CFEEL[k]=Array.isArray(v)?Math.min(v[1],CFEEL[k]*v[0]):CFEEL[k]*v; } return CFEEL; },
    kickSide:()=>FEEL.kickSide,
    combatOn:()=>riderCombatOn(), combatState:()=>CS&&!CS.done?CS.kind:null,   // stateName() keeps the locomotion name for planted moves so the v2-skate ground contact stays on
 combatMoves:RIDER_COMBAT_MOVES, combatFeel:CFEEL, combatLog:CLOG,
    combatEvents:{ onHitFrame:null, onCancelOpen:null, onCancelClose:null, onRecover:null },   // assign a function, or use onCombat()
    onCombat(type,fn){ if(!CBS[type]||typeof fn!=='function') return ()=>{}; CBS[type].push(fn); return ()=>{ const i=CBS[type].indexOf(fn); if(i>=0) CBS[type].splice(i,1); }; },
    combatHitStop(ms){ if(!CS) return false; CS.stop=Math.max(CS.stop,(+ms||0)/1000); return true; },
    combatRelease(){ if(CS&&CS.charging){ CS.charging=false; return true; } return false; },
    combatCancel(){ if(!CS) return false; CPEND.push(['onRecover',cEv('onRecover',CS.f,{interrupted:true,by:null})]); W[CS.kind]=0; CS=null; combatDispatch(); return true; },
    combatQuery(){ if(!CS) return null; const TL=CS.TL, f=CS.f, R=TL.root, inR=R&&f>=R.from&&f<R.to, v=inR?R.fwd/((R.to-R.from)/RIDER_COMBAT_FPS):0;
      return { kind:CS.kind, move:CS.name, step:CS.step, side:CS.side, frame:f, phase:CS.charging&&f>=TL.a?'hold':f<TL.a?'A':f<TL.a+TL.x?'X':'R', charge:CS.charge, hitStop:CS.stop,
        frames:{a:TL.a,x:TL.x,r:TL.r,end:TL.end,hit:TL.hit.slice(),cancel:TL.cancel?[TL.cancel.open,TL.cancel.close]:null}, cancelOpen:CS.cOpen, cancelKinds:CS.cOpen?TL.cancel.kinds.slice():[],
        root:{ fwdVel:v, up:0, total:R?R.fwd:0, applied:false }, weight:W[CS.kind]||0, target:CS.target, plant:CS.m.plant, mask:CS.m.mask, fx:root.userData.fxAll?root.userData.fxAll():{} }; },
    _combatSlew:{max:0,maxLead:0,over:0} };
  // cross-fade guard (dt-based, frame-rate independent): every posed joint slews toward its target at <= RIDER_POSE_MAX_DEG_S (720 deg/s = 10 deg per 72 fps frame)
  const RIDER_POSE_MAX_DEG_S=720, RIDER_BLEND_RATE=12, slewQ={}, slewB=[...Object.values(P).map(p=>p.b)]; for(const k in HF) if(!slewB.includes(HF[k].b)) slewB.push(HF[k].b); let poseDt=0;
  const slew=()=>{ const mx0=RIDER_POSE_MAX_DEG_S*D2R*Math.max(poseDt,1e-4), mxA=RIDER_POSE_ACTIVE_DEG_S*D2R*Math.max(poseDt,1e-4), act=CS&&CS.inX&&CS.lead.size?CS.lead:null, SD=root.userData._combatSlew;
    for(const b of slewB){ const q=slewQ[b.uuid]; if(!q){ slewQ[b.uuid]=b.quaternion.clone(); continue; } const isA=!!(act&&act.has(b)), mx=isA?mxA:mx0;   // lead limb gets 1800 deg/s during active frames only
      const d=2*Math.acos(Math.min(1,Math.abs(q.dot(b.quaternion)))); if(d>mx) q.slerp(b.quaternion,mx/d); else q.copy(b.quaternion); b.quaternion.copy(q);
      if(SD&&poseDt>0){ const st=Math.min(d,mx)/poseDt*R2D; if(isA) SD.maxLead=Math.max(SD.maxLead,st); else SD.max=Math.max(SD.max,st); if(st>(isA?RIDER_POSE_ACTIVE_DEG_S:RIDER_POSE_MAX_DEG_S)+.5) SD.over++; } } };
  // twist distribution (RIDER_JOINT_LIMITS.twist): swing-twist split of the slewed ForeArm/Arm local delta about the bone axis (+Y, Mixamo)
  const TW=[], _tq=new THREE.Quaternion(), _sq=new THREE.Quaternion(), _yA=new THREE.Vector3(0,1,0);
  for(const sd of ['Left','Right']) for(const k in RIDER_JOINT_LIMITS.twist){ const tb=bones[sd+k], c=RIDER_JOINT_LIMITS.twist[k], pb=P[sd+c.of]; if(tb&&pb) TW.push({tb,rest:tb.quaternion.clone(),pb,share:c.share,fore:c.of==='ForeArm',hand:P[sd+'Hand']}); }
  if(!TW.length) console.info('rider poser: no twist bones, forearm roll stays on ForeArm (fallback)');
  const twist=()=>{ for(const w of TW){ _sq.copy(w.pb.rest).invert().multiply(w.pb.b.quaternion);   // local delta of the parent
      _tq.set(0,_sq.y,0,_sq.w); if(_tq.lengthSq()<1e-9) continue; _tq.normalize(); const ang=2*Math.atan2(_tq.y,_tq.w);
      if(w.fore){ w.pb.b.quaternion.multiply(_tq.clone().invert());   // ForeArm keeps swing only (elbow-side skin stays put) ...
        if(w.hand) w.hand.b.quaternion.premultiply(_tq);              // ... hand gets the full roll (about the forearm axis, in the parent frame)
        w.tb.quaternion.copy(w.rest).multiply(_sq.setFromAxisAngle(_yA,ang*w.share)); }   // twist bone carries the share -> progressive twist
      else w.tb.quaternion.copy(w.rest).multiply(_sq.setFromAxisAngle(_yA,-ang*w.share)); } };   // upper arm: counter-roll the shoulder half
  function pose(t,sp,boost){ CV=null; CW=0; if(CS){ CV=riderCombatSample(CS.m,CS.TL,CS.charging&&CS.t*RIDER_COMBAT_FPS>=CS.TL.a?CS.TL.a:CS.t*RIDER_COMBAT_FPS,CS.side,CFEEL,CS.fb); CW=W[CS.kind]||0; }
    const L=Math.max(0,Math.sin(phase)), R=Math.max(0,-Math.sin(phase)), sw=Math.sin(phase), cw=Math.cos(phase);
    OW=0; OV=null; if(OS){ OV=riderStateSample(OS.name,OS.t,OS.kSide,FEEL); OW=W[OS.name]||0; }
    const w=W, idle=w.idle, st=w.stride, tu=w.tuck, gr=w.grind, ai=w.air;
    const crouch=idle*.16+st*(.34+.12*sp)+tu*.62+gr*.55+ai*.95+land*.35*FEEL.landDepth;
    const lean=idle*.04+st*(.32+.12*sp)+tu*.62+gr*.12+ai*.3+land*.15;
    const push=st*(.85+.15*sp)+tu*.55; // stroke depth
    const hipYaw=gr*1.25+(st+tu)*sw*.12, spYaw=-gr*.85-(st+tu)*sw*.1*FEEL.spineSway, hipRoll=(st+tu)*sw*.06*FEEL.spineSway;
    rot('Hips',0,hipYaw,hipRoll);
    const spT=riderSoftClamp(spYaw*R2D,-LIM.spineTwistTotal,LIM.spineTwistTotal,KN)*D2R, SS=LIM.spineTwistSplit;   // total thoracolumbar twist <= 40 deg
    rot('Spine',lean*.45,spT*SS.Spine,-hipRoll*.6); rot('Spine1',lean*.3+Math.sin(t*1.7*FEEL.idleRate)*.012*FEEL.idleAmp*idle,spT*SS.Spine1,0); rot('Spine2',lean*.25,spT*SS.Spine2,0);
    rot('Neck',-lean*.4,0,0); rot('Head',-lean*.35+ai*.1,idle*Math.sin(t*.45*FEEL.idleRate)*.35*FEEL.idleAmp-spYaw*.3*FEEL.spineSway,0);
    for(const [side,u,sgn] of [['Left',L,1],['Right',R,-1]]){ const rec=(st+tu)*Math.max(0,u>0?0:(sgn>0?-cw:cw)); // recovery = foot coming back in under the hip
      const a=crouch*(1-push*u*.55);  // push leg straightens
      const abd=sgn*(push*u*.42+gr*.16+idle*.05+ai*.08), ext=push*u*.22-rec*.25;
      const knee=2*a+rec*.6+ai*.4, thigh=-a-rec*.15+ext+ai*.35;
      rot(side+'UpLeg',thigh,0,abd); rot(side+'Leg',knee,0,0); rot(side+'Foot',-(knee+thigh)*.55-gr*.05,0,-abd*.7); }
    // arms: Meshy rest pose has the arms HANGING DOWN (palms in). v1 assumed an A-pose and twisted them about Y (= backwards). Now, like the legs:
    // fore/aft swing = rot X (negative = hand forward), abduction = rot Z (+ left / - right outward), elbow = forearm rot X negative (bends forward).
    // Speed-skater swing: arm opposite the pushing leg drives forward and across, the other sweeps back and out; elbows soften at the front.
    const amp=(st*(.75+.35*sp)+tu*.25)*FEEL.armSwing, swL=-sw*amp, swR=sw*amp;            // L leg pushes (sw>0) -> L arm back, R arm forward
    const fL=-(swL+st*.12+ai*.75+gr*.25+idle*.06)+tu*.95, fR=-(swR+st*.12+ai*.6+gr*.25+idle*.06)-tu*.15; // tuck: left arm trails behind the back
    const abL=idle*.1+st*(.14+Math.max(0,-swL)*.25)+tu*.12+gr*1.15+ai*.85, abR=idle*.1+st*(.14+Math.max(0,-swR)*.25)+tu*.32+gr*1.0+ai*.95;
    const crossL=Math.max(0,swL)*.22, crossR=Math.max(0,swR)*.22;          // forward arm reaches across the chest
    rot('LeftShoulder',0,0,gr*.12+ai*.15); rot('RightShoulder',0,0,-gr*.12-ai*.15);
    rot('LeftArm',fL,0,abL-crossL); rot('RightArm',fR,0,-(abR-crossR));
    const eL=.3+Math.max(0,swL)*.75+tu*.55+gr*.25+ai*.55+idle*.05, eR=.3+Math.max(0,swR)*.75+tu*.35+gr*.25+ai*.55+idle*.05;
    rot('LeftForeArm',-eL,0,0); rot('RightForeArm',-eR,0,0);
    rot('LeftHand',-.1*st,0,0); rot('RightHand',-.1*st,0,0);
    hand('Left',fistL,t); hand('Right',fistR,t);
    slew(); twist();
    // feet to deck: drop hips by crouch, shift over support leg; snap the lowest foot to the skate deck height
    hips.position.copy(hipRest); root.updateMatrixWorld(true); const gy=root.getWorldPosition(_s).y;
    footL.getWorldPosition(_a); footR.getWorldPosition(_b); const low=Math.min(_a.y,_b.y)-gy, dy=(ai>.5?Math.min(0,low-footRest-.12*ai):low-footRest);
    hips.getWorldPosition(_p); _p.y-=dy; const rx=new THREE.Vector3(1,0,0).transformDirection(root.matrixWorld); _p.addScaledVector(rx,(st+tu)*-sw*.05*s); hips.position.copy(hips.parent.worldToLocal(_p)); root.updateMatrixWorld(true); plant(ai); }
  // Rigger: planted-foot sole levelling (stride/kick/idle). Rotates the planted Foot about its own joint so its rest-pose sole axis is world-up again -> the lowest wheel
  // stays at deck height instead of the toe/heel wheel dipping. Weight = how planted (<=1 cm above the lower foot -> 1, >=4 cm -> 0), off in the air.
  // Correction angle soft-capped by RIDER_JOINT_LIMITS.Foot (pitch range) and slewed at RIDER_POSE_MAX_DEG_S (10 deg/frame @72 fps). ?noplant=1 disables.
  const PL={Left:0,Right:0}, _rq=new THREE.Quaternion(), _fq=new THREE.Quaternion(), _pq=new THREE.Quaternion(), _dq=new THREE.Quaternion(), _up=new THREE.Vector3(), _Y=new THREE.Vector3(0,1,0), NOPL=/noplant=1/.test(location.search);
  const plantCap=(()=>{ const F=LIM.Foot&&LIM.Foot.x; return F?Math.max(Math.abs(F[0]),Math.abs(F[1])):35; })();
  function plant(ai){ if(NOPL) return; root.getWorldQuaternion(_rq).invert(); const yL=footL.getWorldPosition(_a).y, yR=footR.getWorldPosition(_b).y, lo=Math.min(yL,yR), mx=RIDER_POSE_MAX_DEG_S*D2R*Math.max(poseDt,1e-4);
    for(const [sd,f,y] of [['Left',footL,yL],['Right',footR,yR]]){ const wp=(1-sm(.01*s,.04*s,y-lo))*(1-sm(.3,.7,ai)), p=P[sd+'Foot']; if(!p) continue;
      f.getWorldQuaternion(_fq).premultiply(_rq); _up.copy(_Y).applyQuaternion(p.wi).applyQuaternion(_fq);   // rest sole-up axis, current model space
      _dq.setFromUnitVectors(_up.normalize(),_Y); let ang=2*Math.acos(Math.min(1,Math.abs(_dq.w))); const want=Math.min(ang,plantCap*D2R)*wp;
      const a=PL[sd]+THREE.MathUtils.clamp(want-PL[sd],-mx,mx); PL[sd]=a; if(ang<1e-5||a<1e-5) continue; _dq.copy(_pq.identity().slerp(_dq,a/ang));
      f.parent.getWorldQuaternion(_pq); _pq.premultiply(_rq);   // parent model quat
      f.quaternion.copy(_pq.clone().invert().multiply(_dq.multiply(_fq))); }
    root.updateMatrixWorld(true); }
  Object.assign(root.userData,{ ikki:true, crew:'Ikki', expressions:[], setExpression(){}, colors:c, shared:sh, lod, lodTris:tris, bones:{footL,footR}, handFrames:HF, rest:{}, poseDbg:dbg, jointLimits:RIDER_JOINT_LIMITS, fist:()=>[fistL,fistR], scaleFit:s, refH, weights:W, mixer:null, actions:{},
    skates:[], crow:{visible:false}, patch, ground:gnd, brand:{id:'karasu'}, setWheelGlow(hex){ sh.glowC.value.setHex(hex); }, loadout:{}, setLoadout(o){ for(const k of ['paint','frame','wheel','glow']) if(o[k]!==undefined){ sh[k+'C'].value.set(o[k]); this.loadout[k]=o[k]; } }, setState(n,o){ if(n==='atk'||n==='react') return combatStart(n,o); o=o||{}; if(n==='polegrind'){ n='polegrind_'+(o.variant==='top'?'top':'climb'); this.poleAxis=o.poleAxis||this.poleAxis||null; this.poleVariant=n.slice(10); }   // ref3-pole-grind hook for Rydah Systems: setState('polegrind',{variant:'top'|'climb',poleAxis:THREE.Vector3,side:'Left'|'Right'})
      if(RIDER_SKATE_STATES[n]){ const side=n==='wall'?((o.side!==undefined?o.side:this.wallSide||1)>0?'Left':'Right'):(o.side||FEEL.kickSide);
        if(OS&&OS.name!==n) W[OS.name]=0; OS={name:n,t:0,kSide:side,released:n!=='trick',hold:0,done:false}; return; } if(!n&&OS) OS.done=true; forced=n||null; },
    trickRelease(){ if(OS&&OS.name==='trick') OS.released=true; }, kickImpulse:0, wallSide:1, feel:FEEL, animStates:Object.keys(RIDER_SKATE_STATES), stateName(){ return CS&&!CS.done&&CS.m.plant==='off'?CS.kind:OS&&!OS.done?OS.name:ST.reduce((a,k)=>W[k]>W[a]?k:a,'idle'); },
    drive(dt,sp,grinding,t,boost){ boost=boost||0; const y=parent.position.y; if(lastY!==null&&dt>0) vy=THREE.MathUtils.lerp(vy,(y-lastY)/dt,.3); lastY=y;
      const air=!grinding&&(vy>1.2||y>.25&&!grinding);
      const tgt={idle:0,stride:0,tuck:0,grind:0,air:0}; const k=forced||(air?'air':grinding?'grind':sp<.04?'idle':(sp>.78||boost>.3)?'tuck':'stride');
      if(k==='stride'||k==='tuck'){ const m=sm(.0,.12,sp); tgt.idle=1-m; tgt[k]=m; if(k==='tuck'){ tgt.stride=.25*m; tgt.tuck=.75*m; } } else tgt[k]=1;
      const wasAir=W.air>.5, kk=1-Math.exp(-dt*RIDER_BLEND_RATE); /* state weights: exponential, ~0.25 s to 95% */ for(const n of ST) W[n]+=(tgt[n]-W[n])*kk;
      if(OS){ const D=RIDER_SKATE_STATES[OS.name]; if(OS.name==='trick'&&!OS.released){ OS.hold+=dt; if(OS.hold>.8) OS.released=true; } else OS.t+=dt;   // trick: hold coil (wheels spin) until release / 0.8 s
        const DT=riderStateTiming(OS.name,FEEL); if(!D.loop&&OS.t>=DT.dur) OS.done=true; const ow=OS.done?0:1; W[OS.name]+=(ow-W[OS.name])*(1-Math.exp(-dt*(OS.done?(D.exit?3/D.exit:RIDER_BLEND_RATE):(D.enter?3/D.enter:RIDER_BLEND_RATE))));
        this.kickImpulse=OS.name==='kick'&&DT.impulse&&OS.t>=DT.impulse[0]&&OS.t<=DT.impulse[1]?1:0;
        if(OS.done&&W[OS.name]<.01){ W[OS.name]=0; OS=null; this.kickImpulse=0; } } if(wasAir&&W.air<.5) landK=1; landK=Math.max(0,landK-dt*3*FEEL.landRate); land+=(landK-land)*(1-Math.exp(-dt*20));   // landing dip eases in (no 1-frame snap)
      const fk=1-Math.exp(-dt*6), gT=Math.min(1,W.air*.9+W.tuck*.55+(window.__riderFist||0)); fistL+=(gT-fistL)*fk; fistR+=(Math.min(1,W.air*.75+W.tuck*.3+(window.__riderFist||0))-fistR)*fk;   // grab fist (L grabs harder) / tuck
      // cadence: long slow strokes cruising, quicker when accelerating; glides (lower cadence) when tucked
      if(CS){ combatAdvance(dt); if(CS){ const hk=CS.m.hand, kk2=1-Math.exp(-dt*30), wv=W[CS.kind]||0, tL=(CS.side==='Left'?hk.K:hk.S)==='fist'?1:0, tR=(CS.side==='Right'?hk.K:hk.S)==='fist'?1:0; CS.fL=(CS.fL??fistL)+(tL-(CS.fL??fistL))*kk2; CS.fR=(CS.fR??fistR)+(tR-(CS.fR??fistR))*kk2; fistL+=(CS.fL-fistL)*wv; fistR+=(CS.fR-fistR)*wv; } }   // combat clock + hand pose (move's own fist track, weighted)
      phase+=dt*Math.PI*2*(.55+sp*.75)*(1-W.tuck*.45)*(W.stride+W.tuck>.01?1:0); poseDt=dt; pose(t,sp,boost); combatDispatch();
      if(SPR) SPR.step(dt,root.userData.camDist);   // spring bones after pose()+plant()
      sh.spin.value=(sh.spin.value+dt*Math.min(42,sp*24/(.078*s)+W.grind*6+W.air*14+(OS&&OS.name==='trick'&&!OS.released?40:0)))%(Math.PI*2000); // wheel rad/s from ground speed (r=.078 rest)
      sh.comp.value=.03*Math.min(1,land*1.4)+W.grind*.012+Math.sin(t*23)*.0015*sp; sh.time.value=t; sh.boost.value=boost; },
    update:(cam,dt,boost)=>{ const vis=root.visible&&parent.visible&&(!parent.parent||parent.parent.visible!==false); if(cam&&cam.position){ parent.getWorldPosition(_p); root.userData.camDist=_p.distanceTo(cam.isObject3D?cam.getWorldPosition(_a):cam.position); }   // world camera position (the camera can sit inside a rig/dolly: local .position is not world) gnd.visible=vis&&root.userData.detail!=='lite'; if(!vis) return; parent.getWorldPosition(_p); gnd.position.set(_p.x,(parent.parent===scene?0:0)+.025,_p.z);
      footL.getWorldPosition(_a); footR.getWorldPosition(_b); gU.uF0.value.set(_a.x-_p.x,_a.z-_p.z); gU.uF1.value.set(_b.x-_p.x,_b.z-_p.z); gU.uB.value=boost||0; }, });
  const SPR=riderSpringsInstall(root,bones,()=>parent.getWorldPosition(_s).y); root.userData.springs=SPR;   // null when the GLB has no spring bones
  Object.assign(root.userData,combatApi);   // combat poses API (flag-gated; see RIDER_COMBAT_MOVES)
  for(const f of (window.SR_RIDER_HOOKS||[])) try{ f(root.userData,(typeof opt!=='undefined'&&opt&&opt.key)||'ikki'); }catch(e){ console.warn('rider hook',e); }   // local-only per-rider extensions
  if(typeof srDetailInstall==='function') srDetailInstall(root);   // setDetail('full'|'lite')
  parent.add(root); return root; }
