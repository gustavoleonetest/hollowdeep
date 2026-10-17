from patch import edit, run

L = 'part_logic.js'

# --- a reusable silhouette, which buys rim light and impact frames both -----
edit(L, """const _tc = document.createElement('canvas'), _tx = _tc.getContext('2d');
function sprBlit(s, sx, sy, sw, sh, dx, dy, dw, dh, tint, ta) {
  const f = s.f;
  if (tint && ta > 0) {
    const w = Math.max(1, Math.round(sw * f)), h = Math.max(1, Math.round(sh * f)); _tc.width = w; _tc.height = h;
    _tx.drawImage(s.src, sx * f, sy * f, sw * f, sh * f, 0, 0, w, h); _tx.globalCompositeOperation = 'source-atop'; _tx.globalAlpha = ta; _tx.fillStyle = tint; _tx.fillRect(0, 0, w, h); _tx.globalAlpha = 1; _tx.globalCompositeOperation = 'source-over';
    ctx.drawImage(_tc, 0, 0, w, h, dx, dy, dw, dh);
  } else ctx.drawImage(s.src, sx * f, sy * f, sw * f, sh * f, dx, dy, dw, dh);
}
// draw one frame of an animated character; (x, fy) is where its feet land
function sprChar(key, x, fy, ang, kind, col, sc, tint, ta) {
  const s = SPR[key]; if (!s || !s.ok) return false;
  const m = s.m, sz = m.sz; if (m[kind] == null) return false;
  const d = (kind === 'die' || kind === 'pick') ? 0 : dirIdx(ang), row = m[kind] + d, ay = kind === 'die' && m.dieAy ? m.dieAy : m.ay, k = SK * (sc || 1);
  sprBlit(s, col * sz, row * sz, sz, sz, x - m.ax * k, fy - ay * k, sz * k, sz * k, tint, ta); return true;
}""",
     """const _tc = document.createElement('canvas'), _tx = _tc.getContext('2d');
const _rc = document.createElement('canvas'), _rx = _rc.getContext('2d');
const fitCv = (c, g, w, h) => { if (c.width !== w || c.height !== h) { c.width = w; c.height = h; } else g.clearRect(0, 0, w, h); };
function sprBlit(s, sx, sy, sw, sh, dx, dy, dw, dh, tint, ta) {
  const f = s.f;
  if (tint && ta > 0) {
    const w = Math.max(1, Math.round(sw * f)), h = Math.max(1, Math.round(sh * f)); fitCv(_tc, _tx, w, h);
    _tx.drawImage(s.src, sx * f, sy * f, sw * f, sh * f, 0, 0, w, h); _tx.globalCompositeOperation = 'source-atop'; _tx.globalAlpha = ta; _tx.fillStyle = tint; _tx.fillRect(0, 0, w, h); _tx.globalAlpha = 1; _tx.globalCompositeOperation = 'source-over';
    ctx.drawImage(_tc, 0, 0, w, h, dx, dy, dw, dh);
  } else ctx.drawImage(s.src, sx * f, sy * f, sw * f, sh * f, dx, dy, dw, dh);
}
/* flat silhouette of a frame, in one colour */
function sprSil(s, sx, sy, sw, sh, dx, dy, dw, dh, col, a) {
  const f = s.f, w = Math.max(1, Math.round(sw * f)), h = Math.max(1, Math.round(sh * f));
  fitCv(_rc, _rx, w, h);
  _rx.globalCompositeOperation = 'source-over';
  _rx.drawImage(s.src, sx * f, sy * f, sw * f, sh * f, 0, 0, w, h);
  _rx.globalCompositeOperation = 'source-in'; _rx.fillStyle = col; _rx.fillRect(0, 0, w, h);
  _rx.globalCompositeOperation = 'source-over';
  const pa = ctx.globalAlpha; ctx.globalAlpha = pa * clamp(a, 0, 1);
  ctx.drawImage(_rc, 0, 0, w, h, dx, dy, dw, dh);
  ctx.globalAlpha = pa;
}
/* Which way the nearest real light falls, and how hard. Valve's TF2 work found
   a rim read separates a figure from the background better than an outline. */
function lightAt(x, y) {
  let bd = 1e9, bx = 0, by = -1, col = null;
  const test = (lx, ly, c) => { const d = Math.hypot(lx - x, ly - y); if (d > 300 || d >= bd) return; bd = d; bx = lx - x; by = ly - y; col = c; };
  for (const t of G.torches) test(t.x, t.y + 10, '#ffcf8a');
  for (const p of G.props) if (p.lit) test(p.x, p.y - 4, '#ffb55a');
  for (const n of G.nests) if (n.hp > 0) test(n.x, n.y, '#ff7a5a');
  if (G.exit) test(G.exit.x, G.exit.y, '#9fdcff');
  const len = Math.hypot(bx, by) || 1, near = col ? clamp(1 - bd / 300, 0, 1) : 0;
  return { dx: bx / len, dy: by / len, col: col || ((G.zone || ZONES[0]).amb), a: .16 + near * .46 };
}
function entLight(e) {
  if (!e._lt || clock - e._lt > .12) { e._lt = clock; e._lr = lightAt(e.x, e.y); }
  return e._lr;
}
// draw one frame of an animated character; (x, fy) is where its feet land
function sprChar(key, x, fy, ang, kind, col, sc, tint, ta, rim) {
  const s = SPR[key]; if (!s || !s.ok) return false;
  const m = s.m, sz = m.sz; if (m[kind] == null) return false;
  const d = (kind === 'die' || kind === 'pick') ? 0 : dirIdx(ang), row = m[kind] + d, ay = kind === 'die' && m.dieAy ? m.dieAy : m.ay, k = SK * (sc || 1);
  const dx0 = x - m.ax * k, dy0 = fy - ay * k, dsz = sz * k;
  if (rim && rim.a > 0 && !reduceMotion) sprSil(s, col * sz, row * sz, sz, sz, dx0 + rim.dx, dy0 + rim.dy, dsz, dsz, rim.col, rim.a);
  sprBlit(s, col * sz, row * sz, sz, sz, dx0, dy0, dsz, dsz, tint, ta); return true;
}""")

# --- monsters: rim light, an impact frame, and a readable hound ------------
edit(L, """  let tint = null, ta = .85;
  if (e.flash > 0) tint = '#ffffff';
  else if (e.type === 'reaper') { tint = '#eef2ff'; ta = .55; }
  else if (e.type === 'thief') { tint = '#e8c877'; ta = .45; }
  else if (e.type === 'bloat') { tint = e.fuse > 0 ? '#eaffc4' : '#7fbf4a'; ta = e.fuse > 0 ? .72 : .5; }
  else if (e.chill > 0) { tint = '#9fd8ff'; ta = .5; }
  else if (e.elite) { tint = '#ffd98a'; ta = .3; }
  ctx.save(); ctx.translate(x + ox, y + S.fy + bob + oy); ctx.rotate(rot); ctx.scale(sx, sy); ctx.globalAlpha = fade * (ghost ? .92 : 1);
  sprChar(S.key, 0, 0, e.face || 0, kk, kc, S.sc, tint, ta);""",
     """  let tint = null, ta = .85;
  if (e.imp > 0) { tint = '#ffffff'; ta = 1; }
  else if (e.flash > 0) tint = '#ffffff';
  else if (e.type === 'reaper') { tint = '#eef2ff'; ta = .55; }
  else if (e.type === 'thief') { tint = '#e8c877'; ta = .45; }
  else if (e.type === 'bloat') { tint = e.fuse > 0 ? '#eaffc4' : '#7fbf4a'; ta = e.fuse > 0 ? .72 : .5; }
  else if (e.chill > 0) { tint = '#9fd8ff'; ta = .5; }
  else if (e.type === 'hound') { tint = '#e0a860'; ta = .4; }   /* the weakest value read of the set */
  else if (e.elite) { tint = '#ffd98a'; ta = .3; }
  const LT = entLight(e), rimS = 2.4 + (boss ? 1.6 : 0);
  const rim = { dx: LT.dx * rimS, dy: LT.dy * rimS - .8, col: LT.col, a: LT.a * (ghost ? .5 : 1) };
  ctx.save(); ctx.translate(x + ox, y + S.fy + bob + oy); ctx.rotate(rot); ctx.scale(sx, sy); ctx.globalAlpha = fade * (ghost ? .92 : 1);
  sprChar(S.key, 0, 0, e.face || 0, kk, kc, S.sc, tint, ta, rim);""")

# --- heroes get the same treatment ----------------------------------------
edit(L, """  ctx.save(); ctx.translate(x + ox, y + 10 - bob - lift + oy); ctx.rotate(rot);
  if (spin) { ctx.translate(0, -14); ctx.rotate(spin); ctx.translate(0, 14); }
  ctx.scale(sx, sy);
  sprChar(key, 0, 0, fang, kind, col, hsc, P.hurt > 0 ? '#ff2a2a' : null, .5);""",
     """  const PLT = entLight(P);
  ctx.save(); ctx.translate(x + ox, y + 10 - bob - lift + oy); ctx.rotate(rot);
  if (spin) { ctx.translate(0, -14); ctx.rotate(spin); ctx.translate(0, 14); }
  ctx.scale(sx, sy);
  sprChar(key, 0, 0, fang, kind, col, hsc, P.hurt > 0 ? '#ff2a2a' : null, .5, { dx: PLT.dx * 2.6, dy: PLT.dy * 2.6 - .8, col: PLT.col, a: PLT.a });""")

# --- a crit or a kill shows one blown-out frame ---------------------------
edit(L, """  if (crit) { G.fxs.push({ kind: 'crit', x: e.x, y: e.y - 4, t: 0, a: ang }); burstDir(e.x, e.y, ang, '#fff1b8', 10, 330, 1.1, 'spark', .45); G.shake = Math.max(G.shake, .16); sfx('crit'); }""",
     """  if (crit) { G.fxs.push({ kind: 'crit', x: e.x, y: e.y - 4, t: 0, a: ang }); burstDir(e.x, e.y, ang, '#fff1b8', 10, 330, 1.1, 'spark', .45); G.shake = Math.max(G.shake, .16); sfx('crit'); e.imp = .07; }
  if (e.hp <= 0) e.imp = Math.max(e.imp || 0, .09);""")

edit(L, """    e.t += dt; e.flash = Math.max(0, e.flash - dt); e.cd -= dt; e.age += dt; e.fl = Math.max(0, e.fl - dt); e.atk = Math.max(-1, e.atk - dt);""",
     """    e.t += dt; e.flash = Math.max(0, e.flash - dt); e.cd -= dt; e.age += dt; e.fl = Math.max(0, e.fl - dt); e.atk = Math.max(-1, e.atk - dt);
    if (e.imp > 0) e.imp -= dt;""")

run()
