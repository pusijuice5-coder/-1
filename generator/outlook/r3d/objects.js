// Procedural glossy 3D icons for the Outlook course (rendered to PNG by render.js).
let T, B, CG;

function rrShape(w, h, r, cx = 0, cy = 0) {
  const s = new T.Shape();
  const x = cx - w / 2, y = cy - h / 2;
  s.moveTo(x + r, y);
  s.lineTo(x + w - r, y); s.absarc(x + w - r, y + r, r, -Math.PI / 2, 0, false);
  s.lineTo(x + w, y + h - r); s.absarc(x + w - r, y + h - r, r, 0, Math.PI / 2, false);
  s.lineTo(x + r, y + h); s.absarc(x + r, y + h - r, r, Math.PI / 2, Math.PI, false);
  s.lineTo(x, y + r); s.absarc(x + r, y + r, r, Math.PI, Math.PI * 1.5, false);
  return s;
}
function extrude(shape, depth, bevel = 0.12, seg = 10) {
  const g = new T.ExtrudeGeometry(shape, { depth, bevelEnabled: true, bevelThickness: bevel, bevelSize: bevel, bevelSegments: seg, curveSegments: 40 });
  g.translate(0, 0, -depth / 2);
  return g;
}
// rounded box with a dense grid and "pillow" bulge on the big faces, so reflections sweep across it
function pillow(w, h, d, r, puff = 0.45, n = 56) {
  let g = new T.BoxGeometry(w, h, d, n, n, 10);
  g.deleteAttribute('normal'); g.deleteAttribute('uv');
  g = B.mergeVertices(g, 1e-4);
  const p = g.attributes.position, v = new T.Vector3(), c = new T.Vector3();
  const ix = w / 2 - r, iy = h / 2 - r, iz = Math.max(d / 2 - r, 0);
  const rz = Math.min(r, d / 2);
  for (let i = 0; i < p.count; i++) {
    v.fromBufferAttribute(p, i);
    c.set(Math.max(-ix, Math.min(ix, v.x)), Math.max(-iy, Math.min(iy, v.y)), Math.max(-iz, Math.min(iz, v.z)));
    const o = v.clone().sub(c);
    if (o.lengthSq() > 1e-10) { o.normalize(); v.set(c.x + o.x * r, c.y + o.y * r, c.z + o.z * rz); }
    const fx = 1 - (v.x / (w / 2)) ** 2, fy = 1 - (v.y / (h / 2)) ** 2;
    v.z *= 1 + puff * Math.max(0, fx) * Math.max(0, fy);
    p.setXYZ(i, v.x, v.y, v.z);
  }
  g.computeVertexNormals();
  return g;
}
function pillowZ(w, h, d, puff, x, y) {   // front surface z of a pillow at (x, y)
  return (d / 2) * (1 + puff * Math.max(0, 1 - (x / (w / 2)) ** 2) * Math.max(0, 1 - (y / (h / 2)) ** 2));
}
function tube(points, radius, closed = false) {
  const curve = new T.CatmullRomCurve3(points.map(p => new T.Vector3(...p)), closed, 'catmullrom', 0.12);
  const g = new T.TubeGeometry(curve, 160, radius, 20, closed);
  return g;
}
function capsule(a, b, radius) {    // capsule between two points
  const A = new T.Vector3(...a), Bv = new T.Vector3(...b);
  const len = A.distanceTo(Bv);
  const g = new T.CapsuleGeometry(radius, len, 12, 28);
  const m = new T.Matrix4();
  const dir = Bv.clone().sub(A).normalize();
  const q = new T.Quaternion().setFromUnitVectors(new T.Vector3(0, 1, 0), dir);
  m.compose(A.clone().add(Bv).multiplyScalar(0.5), q, new T.Vector3(1, 1, 1));
  g.applyMatrix4(m);
  return g;
}
const mesh = (g, m) => new T.Mesh(g, m);

export const OBJECTS = {
  // ---------------------------------------------------------------- mail
  envelope(ctx) {
    ({ THREE: T, BGU: B, ConvexGeometry: CG } = ctx); const { MAT, root } = ctx;
    const W = 4.8, H = 3.3, D = 0.62, PF = 0.55;
    root.add(mesh(pillow(W, H, D, 0.42, PF), MAT.chrome));
    const z = (x, y) => pillowZ(W, H, D, PF, x, y) + 0.015;
    const pts = [];
    const a = [-W / 2 + 0.34, H / 2 - 0.36], c = [0, -0.28], b = [W / 2 - 0.34, H / 2 - 0.36];
    for (let i = 0; i <= 20; i++) { const t = i / 20; const x = a[0] + (c[0] - a[0]) * t, y = a[1] + (c[1] - a[1]) * t; pts.push([x, y, z(x, y)]); }
    for (let i = 1; i <= 20; i++) { const t = i / 20; const x = c[0] + (b[0] - c[0]) * t, y = c[1] + (b[1] - c[1]) * t; pts.push([x, y, z(x, y)]); }
    root.add(mesh(tube(pts, 0.085), MAT.dark));
    // lower fold lines
    const l1 = [], l2 = [];
    for (let i = 0; i <= 12; i++) { const t = i / 12; let x = -W / 2 + 0.36 + t * 1.35, y = -H / 2 + 0.36 + t * 0.95; l1.push([x, y, z(x, y)]); x = W / 2 - 0.36 - t * 1.35; l2.push([x, y, z(x, y)]); }
    root.add(mesh(tube(l1, 0.06), MAT.dark)); root.add(mesh(tube(l2, 0.06), MAT.dark));
    const ring = mesh(new T.TorusGeometry(2.95, 0.085, 24, 200), MAT.chrome);
    ring.rotation.set(1.3, 0.22, 0.1); ring.position.set(0, -0.15, 0.1); root.add(ring);
    root.rotation.set(-0.3, -0.5, 0.14);
  },
  // ---------------------------------------------------------------- calendar
  calendar(ctx) {
    ({ THREE: T, BGU: B, ConvexGeometry: CG } = ctx); const { MAT, root } = ctx;
    const W = 4.0, H = 4.1, D = 0.7;
    root.add(mesh(pillow(W, H, D, 0.5, 0.25), MAT.dark));
    const head = mesh(pillow(W - 0.02, 1.15, D + 0.14, 0.42, 0.3), MAT.chrome);
    head.position.set(0, H / 2 - 0.62, 0.02); root.add(head);
    for (const x of [-1.05, 1.05]) {
      const r = mesh(capsule([x, H / 2 - 0.25, 0.52], [x, H / 2 + 0.38, 0.52], 0.16), MAT.white); root.add(r);
    }
    const cw = 0.86, ch = 0.66, gx = 0.2, gy = 0.2;
    for (let r = 0; r < 3; r++) for (let c = 0; c < 3; c++) {
      const x = (c - 1) * (cw + gx), y = 0.42 - r * (ch + gy);
      const today = (r === 1 && c === 1);
      const t = mesh(pillow(cw, ch, 0.24, 0.16, 0.5, 14), today ? MAT.glow : MAT.deep);
      t.position.set(x, y, D / 2 + 0.1 + (today ? 0.08 : 0)); root.add(t);
    }
    root.rotation.set(-0.22, 0.55, -0.1);
  },
  // ---------------------------------------------------------------- search
  search(ctx) {
    ({ THREE: T, BGU: B, ConvexGeometry: CG } = ctx); const { MAT, root } = ctx;
    root.add(mesh(new T.TorusGeometry(1.55, 0.34, 40, 160), MAT.chrome));
    const lens = mesh(new T.SphereGeometry(1.42, 64, 48), MAT.dark); lens.scale.set(1, 1, 0.22); root.add(lens);
    const hl = mesh(tube([[-0.85, 0.35, 0.36], [-0.55, 0.8, 0.33], [-0.05, 1.02, 0.3]], 0.07), MAT.white); root.add(hl);
    root.add(mesh(capsule([1.45, -1.45, 0], [2.9, -2.9, 0], 0.36), MAT.deep));
    root.add(mesh(capsule([1.25, -1.25, 0], [1.6, -1.6, 0], 0.25), MAT.chrome));
    root.rotation.set(-0.35, -0.45, 0.05);
  },
  // ---------------------------------------------------------------- folder
  folder(ctx) {
    ({ THREE: T, BGU: B, ConvexGeometry: CG } = ctx); const { MAT, root } = ctx;
    const W = 4.6, H = 3.3;
    const back = mesh(pillow(W, H, 0.4, 0.36, 0.2), MAT.deep); back.position.set(0, 0.12, -0.42); root.add(back);
    const tab = mesh(pillow(1.9, 0.9, 0.4, 0.3, 0.2, 20), MAT.deep); tab.position.set(-W / 2 + 1.1, H / 2 + 0.22, -0.42); root.add(tab);
    const paper = mesh(pillow(W - 0.7, H - 0.3, 0.1, 0.2, 0.0, 12), MAT.white); paper.position.set(0.1, 0.42, -0.1); paper.rotation.z = -0.05; root.add(paper);
    const front = mesh(pillow(W, H - 0.45, 0.42, 0.38, 0.5), MAT.chrome); front.position.set(0, -0.25, 0.3); front.rotation.x = 0.16; root.add(front);
    root.rotation.set(-0.18, -0.5, 0.08);
  },
  // ---------------------------------------------------------------- bell
  bell(ctx) {
    ({ THREE: T, BGU: B, ConvexGeometry: CG } = ctx); const { MAT, root } = ctx;
    const pr = [[0.0, 2.05], [0.32, 2.02], [0.62, 1.82], [0.9, 1.3], [1.08, 0.5], [1.28, -0.35], [1.75, -0.95], [1.95, -1.25], [1.9, -1.45], [1.5, -1.5], [0, -1.5]];
    const curve = new T.SplineCurve(pr.map(p => new T.Vector2(p[0], p[1])));
    root.add(mesh(new T.LatheGeometry(curve.getPoints(80), 96), MAT.chrome));
    const rim = mesh(new T.TorusGeometry(1.9, 0.16, 24, 120), MAT.deep); rim.rotation.x = Math.PI / 2; rim.position.y = -1.38; root.add(rim);
    const knob = mesh(new T.SphereGeometry(0.3, 40, 30), MAT.deep); knob.position.y = 2.2; root.add(knob);
    const clap = mesh(new T.SphereGeometry(0.5, 48, 36), MAT.glow); clap.position.y = -1.78; root.add(clap);
    root.rotation.set(0.12, 0.3, -0.3);
  },
  // ---------------------------------------------------------------- shield
  shield(ctx) {
    ({ THREE: T, BGU: B, ConvexGeometry: CG } = ctx); const { MAT, root } = ctx;
    const s = new T.Shape();
    s.moveTo(0, 2.3);
    s.bezierCurveTo(0.9, 1.75, 1.6, 1.55, 2.0, 1.55);
    s.bezierCurveTo(2.1, -0.4, 1.4, -1.7, 0, -2.4);
    s.bezierCurveTo(-1.4, -1.7, -2.1, -0.4, -2.0, 1.55);
    s.bezierCurveTo(-1.6, 1.55, -0.9, 1.75, 0, 2.3);
    root.add(mesh(extrude(s, 0.3, 0.3, 16), MAT.chrome));
    const s2 = new T.Shape();
    s2.moveTo(0, 1.72);
    s2.bezierCurveTo(0.7, 1.32, 1.2, 1.18, 1.5, 1.16);
    s2.bezierCurveTo(1.55, -0.3, 1.05, -1.25, 0, -1.8);
    s2.bezierCurveTo(-1.05, -1.25, -1.55, -0.3, -1.5, 1.16);
    s2.bezierCurveTo(-1.2, 1.18, -0.7, 1.32, 0, 1.72);
    const inner = mesh(extrude(s2, 0.12, 0.1, 10), MAT.dark); inner.position.z = 0.44; root.add(inner);
    root.add(mesh(tube([[-0.72, -0.05, 0.72], [-0.2, -0.6, 0.72], [0.82, 0.6, 0.72]], 0.15), MAT.glow));
    root.rotation.set(-0.15, -0.55, 0.08);
  },
  // ---------------------------------------------------------------- clock
  clock(ctx) {
    ({ THREE: T, BGU: B, ConvexGeometry: CG } = ctx); const { MAT, root } = ctx;
    root.add(mesh(new T.TorusGeometry(2.0, 0.36, 40, 160), MAT.chrome));
    const face = mesh(new T.SphereGeometry(1.9, 64, 48), MAT.dark); face.scale.set(1, 1, 0.16); root.add(face);
    root.add(mesh(capsule([0, 0, 0.36], [0, 1.15, 0.36], 0.11), MAT.white));
    root.add(mesh(capsule([0, 0, 0.36], [0.82, -0.42, 0.36], 0.11), MAT.glow));
    const hub = mesh(new T.SphereGeometry(0.2, 32, 24), MAT.white); hub.position.z = 0.38; root.add(hub);
    for (let i = 0; i < 12; i++) {
      const a = i / 12 * Math.PI * 2, r = 1.5;
      const d = mesh(new T.SphereGeometry(i % 3 === 0 ? 0.1 : 0.055, 20, 16), MAT.deep); d.position.set(Math.sin(a) * r, Math.cos(a) * r, 0.26); root.add(d);
    }
    root.rotation.set(-0.25, 0.5, 0.0);
  },
  // ---------------------------------------------------------------- paper plane (send)
  plane(ctx) {
    ({ THREE: T, BGU: B, ConvexGeometry: CG } = ctx); const { MAT, root } = ctx;
    const V = (a) => new T.Vector3(...a);
    // classic paper dart: two wings + a keel, each a thin faceted wedge
    const N = [0, 0, 3.0];
    for (const sgn of [-1, 1]) {
      const tip = [sgn * 2.7, 0.35, -2.0], inL = [sgn * 0.5, 0.0, -1.55], inF = [sgn * 0.12, 0.0, 1.2];
      root.add(mesh(new CG([V(N), V(tip), V(inL), V(inF), V([sgn * 1.3, -0.12, -1.7]), V([sgn * 0.5, -0.2, -1.5])]), MAT.facet));
      root.add(mesh(new CG([V(N), V([sgn * 0.5, 0.0, -1.55]), V([0, -1.15, -1.35]), V([0, -0.15, -1.2]), V([sgn * 0.12, 0.0, 1.2])]), MAT.facet));
    }
    const trail = mesh(new T.TorusGeometry(2.3, 0.07, 20, 160, Math.PI * 1.1), MAT.chrome);
    trail.rotation.set(1.45, 0.0, 2.3); trail.position.set(0.0, -0.9, -1.2); root.add(trail);
    root.rotation.set(0.95, -0.7, 0.42);
  },
  // ---------------------------------------------------------------- people (meeting)
  people(ctx) {
    ({ THREE: T, BGU: B, ConvexGeometry: CG } = ctx); const { MAT, root } = ctx;
    const person = (x, z, s, mat) => {
      const g = new T.Group();
      const head = mesh(new T.SphereGeometry(0.72, 56, 40), mat); head.position.y = 1.25; g.add(head);
      const body = mesh(new T.SphereGeometry(1.25, 64, 48, 0, Math.PI * 2, 0, Math.PI / 2), mat); body.scale.set(1, 1.15, 0.72); body.position.y = -1.15; g.add(body);
      const base = mesh(new T.CylinderGeometry(1.25, 1.25, 0.02, 64), mat); base.scale.set(1, 1, 0.72); base.position.y = -1.15; g.add(base);
      g.position.set(x, 0, z); g.scale.setScalar(s); root.add(g);
    };
    person(-1.75, -0.7, 0.8, MAT.deep);
    person(1.75, -0.7, 0.8, MAT.deep);
    person(0, 0.5, 1.0, MAT.chrome);
    root.rotation.set(-0.12, -0.4, 0.03);
  },
  // ---------------------------------------------------------------- check (done)
  check(ctx) {
    ({ THREE: T, BGU: B, ConvexGeometry: CG } = ctx); const { MAT, root } = ctx;
    root.add(mesh(new T.TorusGeometry(2.05, 0.3, 40, 180), MAT.chrome));
    const disc = mesh(new T.SphereGeometry(1.95, 64, 48), MAT.dark); disc.scale.set(1, 1, 0.14); root.add(disc);
    root.add(mesh(tube([[-0.95, 0.0, 0.42], [-0.3, -0.72, 0.42], [1.05, 0.82, 0.42]], 0.2), MAT.glow));
    root.rotation.set(-0.2, -0.5, 0.05);
  },
};
