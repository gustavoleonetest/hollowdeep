from patch import edit, run

L = 'part_logic.js'

# A canvas gradient or arc with a negative radius throws, and because it throws
# inside the draw it kills the whole frame, every frame. Guard the radii at the
# few places that compute one, so no future tuning can reintroduce it.
edit(L, """function glow(x, y, r, col, a) {
  const g = ctx.createRadialGradient(x, y, 0, x, y, r); g.addColorStop(0, col); g.addColorStop(1, 'rgba(0,0,0,0)');
  ctx.globalAlpha = a; ctx.fillStyle = g; ctx.beginPath(); ctx.arc(x, y, r, 0, TAU); ctx.fill(); ctx.globalAlpha = 1;
}""",
     """function glow(x, y, r, col, a) {
  r = r > 0 ? r : 0; if (!(r > 0) || !isFinite(x) || !isFinite(y)) return;
  const g = ctx.createRadialGradient(x, y, 0, x, y, r); g.addColorStop(0, col); g.addColorStop(1, 'rgba(0,0,0,0)');
  ctx.globalAlpha = clamp(a, 0, 1); ctx.fillStyle = g; ctx.beginPath(); ctx.arc(x, y, r, 0, TAU); ctx.fill(); ctx.globalAlpha = 1;
}""")

edit(L, """function shadow(x, y, rx, ry, a) {
  a = a || .35; ctx.save(); ctx.translate(x, y); ctx.scale(1, ry / rx);""",
     """function shadow(x, y, rx, ry, a) {
  rx = Math.max(.5, rx || 0); ry = Math.max(.25, ry || 0);
  a = a || .35; ctx.save(); ctx.translate(x, y); ctx.scale(1, ry / rx);""")

edit(L, """  if (s && s.kind === 'arc') {
    const t = 1 - s.life / .16, h = s.a - 1.15 + 2.3 * Math.min(1, t * 1.6), tail = Math.max(s.a - 1.15, h - 1.3), R = s.rad * .95, al = 1 - t * .8;""",
     """  if (s && s.kind === 'arc') {
    const t = 1 - s.life / .16, h = s.a - 1.15 + 2.3 * Math.min(1, t * 1.6), tail = Math.max(s.a - 1.15, h - 1.3), R = Math.max(1, s.rad * .95), al = clamp(1 - t * .8, 0, 1);""")

edit(L, """  } else if (s && s.kind === 'boom') {
    const t = 1 - s.life / .22, R = s.rad * (.35 + .8 * t), al = 1 - t;""",
     """  } else if (s && s.kind === 'boom') {
    const t = clamp(1 - s.life / .22, 0, 1), R = Math.max(1, (s.rad || 60) * (.35 + .8 * t)), al = clamp(1 - t, 0, 1);""")

edit(L, """  const p = Math.min(1, f.t / .35), al = Math.max(0, 1 - f.t / .8), R = f.r * (.3 + .7 * p);""",
     """  const p = Math.min(1, f.t / .35), al = Math.max(0, 1 - f.t / .8), R = Math.max(1, (f.r || 80) * (.3 + .7 * p));""")

# the bloat's blast used a life longer than the curve it is drawn against
edit(L, """  G.slash = { x: e.x, y: e.y, a: 0, life: .24, kind: 'boom', rad: R };""",
     """  G.slash = { x: e.x, y: e.y, a: 0, life: .22, kind: 'boom', rad: R };""")

run()
