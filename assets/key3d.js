/* The key, in the "Move existing keys to post-quantum algorithms" card: a brushed-steel key turns as the
   card scrolls through the screen, its bit is re-cut tooth by tooth from one profile to another, the new
   teeth take an anodized blue, and its tag moves from v1 to v2. The engraved name never changes. Native
   scroll is the only conductor: the same scroll position always gives the same frame, forward or back.
   Three.js r169, self-hosted, loaded only near the card. */
import * as THREE from './vendor/three/three.module.min.js?v=169';

const section = document.getElementById('key');
const stage = section && section.querySelector('.key3d__stage');
const canvas = stage && stage.querySelector('canvas');
if (!section || !canvas) throw new Error('key3d: card missing');

const steps = [...section.querySelectorAll('[data-step]')];
const still = window.matchMedia('(prefers-reduced-motion: reduce)');

// ---- renderer: transparent over the section's Gray 10 ground, ACES, sRGB out
let renderer;
try {
  renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true, powerPreference: 'high-performance' });
} catch (e) {
  section.classList.add('key3d--still');   // CSS shows the poster; the DOM story stays
  throw e;
}
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.05;
renderer.setClearColor(0x000000, 0);
// a shader a strict GPU rejects, or a lost context: show the still poster instead of an empty stage
renderer.debug.onShaderError = () => { section.classList.add('key3d--still'); section.classList.remove('key3d--ready'); };

const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(28, 1, 0.1, 100);

// ---- studio environment: a dark room with bright cards, prefiltered (3d-metal-material)
function studio() {
  const room = new THREE.Scene();
  room.background = new THREE.Color().setRGB(0.16, 0.17, 0.18, THREE.LinearSRGBColorSpace);   // a light page: a mid-grey room, not black
  const card = (w, h, x, y, z, r, g, b) => {
    const m = new THREE.Mesh(new THREE.PlaneGeometry(w, h),
      new THREE.MeshBasicMaterial({ color: new THREE.Color().setRGB(r, g, b, THREE.LinearSRGBColorSpace), side: THREE.DoubleSide, toneMapped: false }));
    m.position.set(x, y, z); m.lookAt(0, 0, 0); room.add(m);
  };
  // a window of panes, a cool side card, a warm back card, a top card, a faint floor bounce
  for (let i = 0; i < 4; i++) for (let j = 0; j < 3; j++) card(1.08, 1.2, -5 + i * 1.3, 2.4 + j * 1.47, 4.8, 3.8, 3.55, 3.05);
  card(3.0, 5.4, 6, 1.6, 2, 0.52, 0.68, 0.9);
  card(2.0, 4.6, 2.5, 2.2, -5.5, 1.5, 1.22, 0.88);
  card(7.5, 2.2, 0, 6, 0, 0.52, 0.55, 0.6);
  card(9, 9, 0, -4, 0, 0.18, 0.12, 0.07);
  card(9, 5, 0, 1, 9, 1.35, 1.38, 1.42);   // a large soft card behind the camera: the faces turned to the viewer mirror it
  const pmrem = new THREE.PMREMGenerator(renderer);
  const env = pmrem.fromScene(room, 0.006).texture;
  pmrem.dispose();
  return env;
}
const env = studio();
scene.environment = env;

// ---- brushed steel: a conductor whose roughness varies along the grain (a small canvas map)
function brushedMap() {
  const c = document.createElement('canvas'); c.width = 512; c.height = 64;
  const g = c.getContext('2d');
  g.fillStyle = 'rgb(118,118,118)'; g.fillRect(0, 0, 512, 64);
  let s = 1;
  const rnd = () => (s = (s * 16807) % 2147483647) / 2147483647;   // seeded: the same streaks every load
  for (let i = 0; i < 900; i++) {
    const y = rnd() * 64, v = 90 + rnd() * 80, a = 0.15 + rnd() * 0.35;
    g.fillStyle = `rgba(${v},${v},${v},${a})`; g.fillRect(0, y, 512, 0.6 + rnd() * 0.8);
  }
  const t = new THREE.CanvasTexture(c);
  t.wrapS = t.wrapT = THREE.RepeatWrapping; t.repeat.set(2, 6); t.colorSpace = THREE.NoColorSpace;
  t.anisotropy = Math.min(8, renderer.capabilities.getMaxAnisotropy());
  return t;
}
const grain = brushedMap();
const steelF0 = new THREE.Color().setRGB(0.56, 0.57, 0.58, THREE.LinearSRGBColorSpace);
const steel = new THREE.MeshPhysicalMaterial({
  color: steelF0, metalness: 1, roughness: 0.3, roughnessMap: grain,
  anisotropy: 0.8, envMap: env, envMapIntensity: 1.25
});
// anodized blue (Carbon Blue 60 as a dielectric coat over metal) for the newly cut teeth
const blue = new THREE.Color('#0f62fe');
const anodized = (k) => {
  const m = steel.clone();
  m.color = steelF0.clone().lerp(new THREE.Color().setRGB(0.12, 0.36, 1.0, THREE.LinearSRGBColorSpace), k);
  m.metalness = 1 - 0.15 * k; m.roughness = 0.3 - 0.06 * k; m.clearcoat = 0.5 * k; m.clearcoatRoughness = 0.15;
  m.envMap = env;
  return m;
};

// ---- the key: a rounded square bow with a hole, a chamfered blade, a bit of eight teeth
const key = new THREE.Group();
// the pivot: the key's own middle (bow at -2.8, tip at +1.75), so it turns in place and stays in frame
const pivot = new THREE.Group();
pivot.add(key); key.position.x = 0.52;
scene.add(pivot);
const extrude = (shape, depth, bevel) => {
  const g = new THREE.ExtrudeGeometry(shape, { depth, bevelEnabled: true, bevelThickness: bevel, bevelSize: bevel, bevelSegments: 4, curveSegments: 32 });
  g.translate(0, 0, -depth / 2); g.computeVertexNormals();
  return g;
};
const T = 0.16;   // thickness of the key
{
  const s = 1.5, r = 0.32, x0 = -s / 2, y0 = -s / 2;
  const bow = new THREE.Shape();
  bow.moveTo(x0 + r, y0); bow.lineTo(x0 + s - r, y0); bow.quadraticCurveTo(x0 + s, y0, x0 + s, y0 + r);
  bow.lineTo(x0 + s, y0 + s - r); bow.quadraticCurveTo(x0 + s, y0 + s, x0 + s - r, y0 + s);
  bow.lineTo(x0 + r, y0 + s); bow.quadraticCurveTo(x0, y0 + s, x0, y0 + s - r);
  bow.lineTo(x0, y0 + r); bow.quadraticCurveTo(x0, y0, x0 + r, y0);
  const hole = new THREE.Path(); hole.absarc(-0.18, 0, 0.3, 0, Math.PI * 2, true);
  bow.holes.push(hole);
  const m = new THREE.Mesh(extrude(bow, T, 0.04), steel);
  m.position.set(-2.05, 0, 0);
  key.add(m);
}
{
  const blade = new THREE.Shape();
  blade.moveTo(-1.35, -0.22); blade.lineTo(1.55, -0.22); blade.lineTo(1.75, 0); blade.lineTo(1.55, 0.22); blade.lineTo(-1.35, 0.22); blade.lineTo(-1.35, -0.22);
  const m = new THREE.Mesh(extrude(blade, T, 0.03), steel);
  key.add(m);
}
// engraved name on the blade face, and the version tag on the bow
function label(text, w, h, px, ink) {
  const c = document.createElement('canvas'); c.width = w; c.height = h;
  const g = c.getContext('2d');
  const draw = (t, a) => {
    g.clearRect(0, 0, w, h); g.globalAlpha = 1;
    g.fillStyle = ink; g.font = `500 ${px}px "IBM Plex Mono", Menlo, monospace`; g.textBaseline = 'middle'; g.textAlign = 'center';
    g.globalAlpha = a; g.fillText(t, w / 2, h / 2 + 2);
  };
  draw(text, 1);
  const tex = new THREE.CanvasTexture(c); tex.colorSpace = THREE.SRGBColorSpace; tex.anisotropy = 8;
  return { tex, draw: (t, a) => { draw(t, a); tex.needsUpdate = true; } };
}
const name = label('contract-signing-key', 1024, 96, 64, 'rgba(22,22,22,0.82)');
{
  const m = new THREE.Mesh(new THREE.PlaneGeometry(2.55, 0.24), new THREE.MeshBasicMaterial({ map: name.tex, transparent: true, depthWrite: false, toneMapped: false }));
  m.position.set(0.15, 0.01, T / 2 + 0.031);
  key.add(m);
}
const tag = label('v1', 256, 256, 150, '#ffffff');
const tagMat = new THREE.MeshBasicMaterial({ map: tag.tex, transparent: true, depthWrite: false, toneMapped: false });
const tagBack = new THREE.MeshBasicMaterial({ color: 0x161616, toneMapped: false });
{
  const plate = new THREE.Mesh(new THREE.PlaneGeometry(0.44, 0.44), tagBack);
  plate.position.set(-1.6, 0.38, T / 2 + 0.042);
  const text = new THREE.Mesh(new THREE.PlaneGeometry(0.44, 0.44), tagMat);
  text.position.copy(plate.position); text.position.z += 0.002;
  key.add(plate, text);
}
// the bit: eight teeth hanging under the blade; profile A (ECDSA) is re-cut to profile B (ML-DSA)
const A = [0.36, 0.78, 0.5, 0.92, 0.42, 0.7, 0.58, 0.86];
const B = [0.88, 0.44, 0.76, 0.32, 0.84, 0.52, 0.96, 0.4];
const MAXH = 0.46, TW = 0.26, X0 = -0.95;
const teeth = A.map((h, i) => {
  const shape = new THREE.Shape();
  shape.moveTo(-TW / 2, 0); shape.lineTo(TW / 2, 0); shape.lineTo(TW / 2, -1); shape.lineTo(-TW / 2, -1); shape.lineTo(-TW / 2, 0);
  const g = new THREE.ExtrudeGeometry(shape, { depth: T, bevelEnabled: true, bevelThickness: 0.02, bevelSize: 0.012, bevelSegments: 3 });
  g.translate(0, 0, -T / 2);
  const mats = [0, 0.25, 0.5, 0.75, 1].map(anodized);
  const m = new THREE.Mesh(g, mats[0]);
  m.position.set(X0 + i * (TW + 0.06), -0.2, 0);
  m.userData = { mats };
  key.add(m);
  return m;
});
// a soft contact shadow under the key
{
  const c = document.createElement('canvas'); c.width = c.height = 256;
  const g = c.getContext('2d'), grd = g.createRadialGradient(128, 128, 8, 128, 128, 128);
  grd.addColorStop(0, 'rgba(0,0,0,0.22)'); grd.addColorStop(1, 'rgba(0,0,0,0)');
  g.fillStyle = grd; g.fillRect(0, 0, 256, 256);
  const shadow = new THREE.Mesh(new THREE.PlaneGeometry(4.8, 1.1), new THREE.MeshBasicMaterial({ map: new THREE.CanvasTexture(c), transparent: true, depthWrite: false }));
  shadow.rotation.x = -Math.PI / 2; shadow.position.set(0, -1.05, 0);
  scene.add(shadow);
}
// key light for shading the flat faces (the environment carries the reflections)
const keyLight = new THREE.DirectionalLight(0xffffff, 1.1); keyLight.position.set(-3, 5, 6); scene.add(keyLight);

// ---- the conductor: section scroll -> progress 0..1, smoothed for the camera only
const ease = (t) => (t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2);
const clamp = (v, a = 0, b = 1) => Math.min(b, Math.max(a, v));
let target = 0, shown = 0, w = 0, h = 0, raf = 0, visible = false, lastStep = -1;
// 0 when the card's top enters the lower fifth of the screen, 1 when its middle reaches the upper third
function progress() {
  const r = section.getBoundingClientRect(), vh = window.innerHeight;
  const start = vh * 0.85, end = vh * 0.33 - r.height / 2;
  return clamp((start - r.top) / (start - end));
}
function stepOf(p) { return p < 0.34 ? 0 : p < 0.67 ? 1 : 2; }
function apply(p) {
  // turn: from three-quarter view to a gentle opposite three-quarter view
  pivot.rotation.y = -0.62 + 1.0 * ease(p);   // a clear turn across the card's scroll
  pivot.rotation.x = 0.24 - 0.14 * p;
  pivot.position.y = 0.12 + 0.05 * Math.sin(p * Math.PI);
  // re-cut: each tooth moves from A to B in turn between 30% and 70% of the scroll
  teeth.forEach((t, i) => {
    const a = 0.3 + i * 0.03, k = ease(clamp((p - a) / 0.16));
    const hgt = MAXH * (A[i] + (B[i] - A[i]) * k);
    t.scale.y = hgt;
    t.material = t.userData.mats[Math.round(k * 4)];
  });
  // tag: v1 until the cut is half done, then v2, crossfaded over a short span
  const v = clamp((p - 0.43) / 0.03);   // a short crossfade, so the tag always reads v1 or v2
  tag.draw(v < 0.5 ? 'v1' : 'v2', v < 0.5 ? 1 - v * 2 : (v - 0.5) * 2);
  tagBack.color.set(v < 0.5 ? 0x161616 : 0x0f62fe);
  const s = stepOf(p);
  if (s !== lastStep) { steps.forEach((el, i) => el.classList.toggle('is-on', i === s)); lastStep = s; section.dataset.step = String(s); }
}
function size() {
  const r = stage.getBoundingClientRect();
  w = Math.max(1, Math.round(r.width)); h = Math.max(1, Math.round(r.height));
  renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
  renderer.setSize(w, h, false);
  camera.aspect = w / h;
  // frame the whole key: pull back on tall, narrow stages
  // fit the whole key: the camera pulls back as the stage narrows (the key is about 4.6 units long)
  const fit = Math.max(1, 1.55 / camera.aspect);
  camera.position.set(0, 0.55, 7.9 * fit);
  camera.lookAt(0, 0.02, 0);
  camera.updateProjectionMatrix();
  render();
}
function render() { renderer.render(scene, camera); }
let last = 0;
function frame(now) {
  raf = 0;
  const dt = last ? Math.min(0.25, (now - last) / 1000) : 1 / 60; last = now;   // real time, so a slow GPU does not lag behind scroll
  target = progress();
  shown = still.matches ? target : shown + (target - shown) * (1 - Math.exp(-6 * dt));
  apply(shown);
  render();
  if (visible && !document.hidden && Math.abs(target - shown) > 0.0005) raf = requestAnimationFrame(frame);
  else last = 0;
}
const kick = () => { if (!raf && visible) raf = requestAnimationFrame(frame); };
window.addEventListener('scroll', kick, { passive: true });
window.addEventListener('resize', kick);
new ResizeObserver(size).observe(stage);
new IntersectionObserver((es) => { visible = es[es.length - 1].isIntersecting; kick(); }, { rootMargin: '200px 0px' }).observe(section);
document.addEventListener('visibilitychange', kick);
still.addEventListener('change', kick);
canvas.addEventListener('webglcontextlost', (e) => { e.preventDefault(); section.classList.add('key3d--still'); });

target = shown = progress();
size();
apply(shown);
render();
// ready only once a frame has drawn without a shader error
if (!section.classList.contains('key3d--still')) section.classList.add('key3d--ready');
// a test hook: the current progress, for the browser checks
window.__key3d = { progress: () => shown };
