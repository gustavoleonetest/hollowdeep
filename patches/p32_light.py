from patch import edit, run

L = 'part_logic.js'

# --- light takes the colour of whatever casts it --------------------------
edit(L, """  for (const s of G.shots) tint(s.x, s.y, s.kind === 'fire' ? 120 : 70, s.col, .32);
  for (const s of G.eshots) tint(s.x, s.y, 40, '#ebe4d2', .2);
  for (const e of G.enemies) { if (fz(e.x, e.y)) continue; if (e.type === 'wisp') tint(e.x, e.y, 90, e.col, .3); else if (e.boss && e.st !== 'chase') tint(e.x, e.y, 130, '#ff5a46', .25); }
  for (const i of G.items) if ((i.kind === 'key' || i.kind === 'chest') && !fz(i.x, i.y)) tint(i.x, i.y, 70, '#f0a23c', .3);""",
     """  for (const s of G.shots) { const ec = s.own && s.own.g && s.own.g.elem ? ELEM_COL[s.own.g.elem] : s.col; tint(s.x, s.y, s.kind === 'fire' ? 120 : 74, ec, .34); }
  for (const s of G.eshots) tint(s.x, s.y, 42, '#ebe4d2', .2);
  for (const b of G.bolts) { const a = Math.max(0, 1 - b.t / .22); if (a > 0) { tint(b.x1, b.y1, 96, '#c9b6ff', .5 * a); tint(b.x2, b.y2, 80, '#c9b6ff', .4 * a); } }
  for (const e of G.enemies) {
    if (fz(e.x, e.y)) continue;
    if (e.type === 'wisp') tint(e.x, e.y, 90, e.col, .3);
    else if (e.type === 'reaper') tint(e.x, e.y - 6, 120, '#dfe4ef', .26);
    else if (e.type === 'bloat' && e.fuse > 0) tint(e.x, e.y, 90 + (1 - e.fuse / .6) * 50, '#d8f0a0', .45);
    else if (e.type === 'thief' && e.loot > 0) tint(e.x, e.y, 70, '#f0a23c', .28);
    else if (e.boss && e.st !== 'chase') tint(e.x, e.y, 130, (BOSSES[e.kind] || BOSSES.count).glow, .26);
    if (e.burn > 0) tint(e.x, e.y, 54, '#ff8a3a', .22);
    else if (e.chill > 0) tint(e.x, e.y, 48, '#8fd3ff', .18);
    else if (e.pois > 0) tint(e.x, e.y, 48, '#9bd16a', .18);
  }
  for (const i of G.items) {
    if (fz(i.x, i.y)) continue;
    if (i.kind === 'gear') tint(i.x, i.y - 10, 86, i.item.col, .4 + Math.sin(clock * 2.6 + i.t) * .1);
    else if (i.kind === 'bomb') tint(i.x, i.y, 66, '#b98cff', .34);
    else if (i.kind === 'key' || i.kind === 'chest') tint(i.x, i.y, 70, '#f0a23c', .3);
  }
  for (const h of G.hazards) if (h.up > .1 && !fz(h.x, h.y)) tint(h.x, h.y, 60, '#cfd6e6', .16 * h.up);
  if (G.event) { const r = G.event.room, pu = .5 + .5 * Math.sin(clock * 4); tint((r.cx + .5) * T, (r.cy + .5) * T, Math.max(r.w, r.h) * T * .6, '#ff8a3a', .07 + pu * .04); }""")

# --- and the dark is pierced by those same sources ------------------------
edit(L, """  for (const hz of G.hazards) if ((hz.warn || hz.up > .1) && !fz(hz.x, hz.y)) hole(hz.x, hz.y, 60, .45);""",
     """  for (const hz of G.hazards) if ((hz.warn || hz.up > .1) && !fz(hz.x, hz.y)) hole(hz.x, hz.y, 60, .45);
  for (const i of G.items) if ((i.kind === 'gear' || i.kind === 'bomb') && !fz(i.x, i.y)) hole(i.x, i.y, i.kind === 'gear' ? 96 : 72, .7);
  for (const b of G.bolts) if (b.t < .22) { hole(b.x1, b.y1, 100, .8); hole(b.x2, b.y2, 84, .7); }
  for (const e of G.enemies) if (e.type === 'bloat' && e.fuse > 0) hole(e.x, e.y, 120, .8);""")

# --- shadows fall away from the light, which is what sells height ---------
edit(L, """function shadow(x, y, rx, ry, a) {""",
     """/* An entity's shadow leaning away from the nearest flame does more for depth
   than any amount of extra detail on the sprite. */
function shadowL(x, y, rx, ry, a, LT) {
  if (!LT) return shadow(x, y, rx, ry, a);
  const o = 3 + LT.a * 6;
  shadow(x - LT.dx * o, y - LT.dy * o * .45, rx * (1 + LT.a * .12), ry, a);
}
function shadow(x, y, rx, ry, a) {""")

edit(L, """  const bob = ghost ? Math.sin(e.t * 3) * 2.5 - 5 : 0;
  shadow(x, y + S.fy + 1, e.r * (boss ? 1.15 : .95), e.r * .42, ghost ? .2 : .4);""",
     """  const bob = ghost ? Math.sin(e.t * 3) * 2.5 - 5 : 0;
  shadowL(x, y + S.fy + 1, e.r * (boss ? 1.15 : .95), e.r * .42, ghost ? .2 : .4, entLight(e));""")

edit(L, """  ctx.globalAlpha = A; shadow(x, y + 10, 12 - lift * .5, 5 - lift * .2); glow(x, y, 32, c.col, .16);""",
     """  ctx.globalAlpha = A; shadowL(x, y + 10, 12 - lift * .5, 5 - lift * .2, .4, entLight(P)); glow(x, y, 32, c.col, .16);""")

# --- walls sit deeper on the floor ----------------------------------------
edit(L, """  if (wallAt(tx, ty - 1)) { b.fillStyle = 'rgba(0,0,0,.3)'; b.fillRect(px, py, T, 7); b.fillStyle = 'rgba(0,0,0,.15)'; b.fillRect(px, py + 7, T, 6); }""",
     """  if (wallAt(tx, ty - 1)) {
    b.fillStyle = 'rgba(0,0,0,.42)'; b.fillRect(px, py, T, 6);
    b.fillStyle = 'rgba(0,0,0,.24)'; b.fillRect(px, py + 6, T, 6);
    b.fillStyle = 'rgba(0,0,0,.11)'; b.fillRect(px, py + 12, T, 6);
  }""")

run()
