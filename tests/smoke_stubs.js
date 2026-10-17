/* Minimal DOM/canvas stubs so the real game script can run under node.
   Sprite metadata mirrors the shape of the real atlases but carries no pixels,
   so both the sprite render paths and the procedural fallbacks get exercised. */
let drawCalls = 0;

function ctx2d() {
  const grad = { addColorStop() {} };
  const real = {
    canvas: null,
    createRadialGradient: () => grad,
    createLinearGradient: () => grad,
    createPattern: () => grad,
    createImageData: (w, h) => ({ width: w, height: h, data: new Uint8ClampedArray(w * h * 4) }),
    getImageData: (x, y, w, h) => ({ width: w, height: h, data: new Uint8ClampedArray(w * h * 4) }),
    measureText: () => ({ width: 10 }),
    drawImage() { drawCalls++; },
    setTransform() {}, save() {}, restore() {},
  };
  return new Proxy(real, {
    get(t, k) {
      if (k in t) return t[k];
      if (typeof k === 'symbol') return undefined;
      return (t[k] = function () {});
    },
    set(t, k, v) { t[k] = v; return true; },
  });
}

function el(id) {
  const e = {
    id, style: { setProperty() {}, removeProperty() {} }, dataset: { m: '1' },
    /* a real one: a no-op classList makes every test that asks about a
       class pass whatever the code does, which is worse than no test */
    classList: (() => {
      const set = new Set();
      return {
        add: (...c) => c.forEach(x => set.add(x)),
        remove: (...c) => c.forEach(x => set.delete(x)),
        toggle: (c, on) => { const want = on === undefined ? !set.has(c) : !!on; if (want) set.add(c); else set.delete(c); return want; },
        contains: c => set.has(c),
        get length() { return set.size; },
        toString: () => [...set].join(' '),
      };
    })(),
    children: [], innerHTML: '', textContent: '', value: '', title: '',
    hidden: false, disabled: false, type: '', className: '',
    clientWidth: 960, clientHeight: 600, width: 160, height: 160,
    addEventListener() {}, removeEventListener() {}, appendChild(c) { this.children.push(c); return c; },
    focus() {}, blur() {}, setPointerCapture() {}, releasePointerCapture() {},
    getBoundingClientRect: () => ({ left: 0, top: 0, width: 960, height: 600, right: 960, bottom: 600 }),
    querySelector: () => el('q'), querySelectorAll: () => [],
    getContext: () => ctx2d(),
  };
  return e;
}

const nodes = {};
globalThis.document = {
  getElementById: id => (nodes[id] || (nodes[id] = el(id))),
  createElement: tag => el(tag),
  querySelectorAll: () => [],
  querySelector: () => el('q'),
  addEventListener() {},
};
globalThis.window = globalThis;
globalThis.addEventListener = () => {};
globalThis.devicePixelRatio = 2;
globalThis.ResizeObserver = class { observe() {} disconnect() {} };
globalThis.Image = class {
  constructor() { this.width = 1280; this.height = 1280; this.onload = null; }
  set src(v) { this._src = v; }
  get src() { return this._src; }
};
globalThis.requestAnimationFrame = () => 0;
/* a real in-memory store: a no-op one cannot exercise saving or loading */
globalThis.localStorage = (() => {
  const m = new Map();
  return {
    getItem: k => (m.has(String(k)) ? m.get(String(k)) : null),
    setItem: (k, v) => { m.set(String(k), String(v)); },
    removeItem: k => { m.delete(String(k)); },
    clear: () => m.clear(),
    key: i => [...m.keys()][i] ?? null,
    get length() { return m.size; },
  };
})();
if (!globalThis.performance) globalThis.performance = { now: () => Date.now() };

/* sprite metadata: same keys as the real atlases, no image data */
const charAnim = { sz: 160, ax: 80, ay: 110, walk: 0, atk: 8, die: 16, idle: 17, roll: 25, hit: 33, pick: 41 };
const foeAnim = { sz: 160, ax: 80, ay: 110, walk: 0, atk: 8, die: 16, dieAy: 100 };
/* These two lists are injected from part_data.txt when the test bundle is
   built. They used to be typed out by hand and had drifted 24 frames behind
   the real atlas, so anything newly drawn silently rendered nothing here. */
const propNames = __PROP_NAMES__;
const prop2Names = __PROP2_NAMES__;
const frames = names => {
  const f = {};
  names.forEach((nm, i) => { f[nm] = { x: (i % 8) * 160, y: ((i / 8) | 0) * 160, w: 160, h: 160, ax: 80, ay: 140 }; });
  return f;
};

globalThis.SPR_META = {
  hero_bulwark: charAnim, hero_ember: charAnim, hero_sable: charAnim, hero_thistle: charAnim,
  foe_skeleton: foeAnim, foe_ghost: foeAnim, foe_orc: foeAnim, foe_zombie: foeAnim,
  boss_vampire: foeAnim, npc_keeper: foeAnim,
  props: { sz: 160, ax: 80, ay: 140, frames: frames(propNames) },
};
globalThis.SPR_META2 = {
  hero_bulwark: charAnim, hero_ember: charAnim, hero_sable: charAnim, hero_thistle: charAnim,
  foe_puglin: foeAnim, foe_imp: foeAnim,
  props2: { sz: 160, ax: 80, ay: 140, frames: frames(prop2Names) },
};
globalThis.SPR_SRC = {}; globalThis.SPR_SRC2 = {};
for (const k in SPR_META) SPR_SRC[k] = 'stub';
for (const k in SPR_META2) SPR_SRC2[k] = 'stub';
globalThis.TEX_SRC = { fl_std: 'stub', fl_sq: 'stub', fl_dia: 'stub', fl_big: 'stub', wl_std: 'stub', wl_brk: 'stub' };
globalThis.__drawCalls = () => drawCalls;
