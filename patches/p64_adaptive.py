from patch import edit, run

L = 'part_logic.js'

# --- the game measures the device it is actually on ----------------------
# Measured here, the heaviest scene the game produces (the Hollow Heart in
# phase three) costs about 4ms a frame, with a 12.9ms worst case. But that is
# a desktop CPU: the browser's phone emulation changes the viewport, not the
# processor, so a mid-range phone is several times slower and cannot be
# measured from here at all. So the game watches its own frame time and
# thins the cosmetics when it is struggling.
#
# This only ever touches decoration. Nothing here changes what spawns, what
# it does, or what the simulation sees, so a slow device plays the same game.
edit(L, """let spTouch = false, dashTouch = false, bombTouch = false, btnsOn = false, clock = 0, reduceMotion = false;""",
     """let spTouch = false, dashTouch = false, bombTouch = false, btnsOn = false, clock = 0, reduceMotion = false;
/* 0 = draw everything, 1 = thinned, 2 = sparse. Raised only by sustained slow
   frames and lowered again by sustained quick ones, with a wide gap between
   the two so it cannot flutter between levels. */
let fxLevel = 0;
const PERF = { ring: [], at: 0, hold: 0, n: 90 };
function perfTick(ms) {
  if (G.state !== 'play') return;          /* menus and overlays are not the game */
  const p = PERF;
  p.ring[p.at++ % p.n] = ms;
  if (p.ring.length < p.n) return;
  p.hold -= 1;
  if (p.hold > 0) return;
  const s = p.ring.slice().sort((a, b) => a - b), med = s[s.length >> 1];
  /* 22ms is about 45fps: slower than that and the drop is worth more than
     the particles. 11ms leaves room to climb back without immediately
     falling over again. */
  if (med > 22 && fxLevel < 2) { fxLevel++; p.hold = p.n * 3; }
  else if (med < 11 && fxLevel > 0) { fxLevel--; p.hold = p.n * 3; }
}
const fxThin = () => fxLevel === 0 ? 1 : fxLevel === 1 ? .5 : .25;""")

# --- the places decoration is born --------------------------------------
edit(L, """function burst(x, y, col, n, sp, life, kind) {
  if (reduceMotion) n = Math.max(1, Math.round(n * .4));""",
     """function burst(x, y, col, n, sp, life, kind) {
  if (reduceMotion) n = Math.max(1, Math.round(n * .4));
  if (fxLevel) n = Math.max(1, Math.round(n * fxThin()));""")

edit(L, """  const cap = reduceMotion ? 450 : 1400;""",
     """  const cap = Math.round((reduceMotion ? 450 : 1400) * fxThin());""")

# --- and measured from the one place every frame passes through ----------
edit(L, """function frame(now) {
  const dt = Math.min(.05, (now - last) / 1000); last = now; clock += dt;""",
     """function frame(now) {
  const dt = Math.min(.05, (now - last) / 1000); last = now; clock += dt;
  const _t0 = performance.now();""")

edit(L, """  requestAnimationFrame(frame);""",
     """  perfTick(performance.now() - _t0);
  requestAnimationFrame(frame);""")

run()
