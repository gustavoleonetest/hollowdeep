from patch import edit, run

L = 'part_logic.js'

# --- rarity reads through behaviour, not only hue ------------------------
edit(L, """function drawGear(it) {
  const o = it.item, b = Math.sin(it.t * 3) * 1.8, pu = .5 + .5 * Math.sin(clock * 2.6 + it.t);
  const g = ctx.createLinearGradient(it.x, it.y - 92, it.x, it.y + 8);
  g.addColorStop(0, hexA(o.col, 0)); g.addColorStop(.72, hexA(o.col, .16 + pu * .1)); g.addColorStop(1, hexA(o.col, .42 + pu * .14));
  ctx.fillStyle = g; ctx.fillRect(it.x - 8, it.y - 92, 16, 100);
  glow(it.x, it.y, 32, o.col, .4 + pu * .18); shadow(it.x, it.y + 9, 8, 3, .32);
  const sp = o.slot === 'weapon' ? 'sword' : o.slot === 'armour' ? 'shield' : 'p_pouch';
  if (!sprProp(sp, it.x, it.y + 11 + b, 1.5)) {
    ctx.fillStyle = o.col; ctx.beginPath(); ctx.moveTo(it.x, it.y - 7 + b); ctx.lineTo(it.x + 6, it.y + b); ctx.lineTo(it.x, it.y + 7 + b); ctx.lineTo(it.x - 6, it.y + b); ctx.fill();
  }
  for (let i = 0; i < 3; i++) { const a = clock * 1.6 + i * 2.1; ctx.fillStyle = hexA(o.col, .8); ctx.fillRect(it.x + Math.cos(a) * 13, it.y - 12 + Math.sin(a) * 5 - Math.abs(Math.sin(clock * 2.4 + i)) * 8, 2, 2); }
}""",
     """function drawGear(it) {
  const o = it.item, b = Math.sin(it.t * 3) * 1.8, cursed = o.rar === 'cursed';
  const rank = cursed ? 1 : o.rar === 'fabled' ? 3 : o.rar === 'rare' ? 2 : 1;
  /* each rarity's beam behaves differently, so the tier reads without colour */
  const pu = cursed ? .5 + .5 * Math.sin(clock * 5.5 + it.t)
    : rank >= 3 ? .62 + .38 * Math.sin(clock * 2.2 + it.t)
    : rank === 2 ? .5 + .5 * Math.sin(clock * 1.5 + it.t) : .55;
  const h = 70 + rank * 22, wdt = 6 + rank * 2.5;
  const g = ctx.createLinearGradient(it.x, it.y - h, it.x, it.y + 8);
  g.addColorStop(0, hexA(o.col, 0));
  g.addColorStop(.7, hexA(o.col, (cursed ? .1 : .14) + pu * .1));
  g.addColorStop(1, hexA(o.col, (cursed ? .3 : .4) + pu * .14));
  ctx.fillStyle = g; ctx.fillRect(it.x - wdt, it.y - h, wdt * 2, h + 8);
  if (rank >= 3) {
    /* a slow turning shaft for the best things */
    ctx.save(); ctx.translate(it.x, it.y); ctx.globalAlpha = .16 + pu * .12;
    for (let i = 0; i < 3; i++) {
      const a = clock * .5 + i * (TAU / 3), w2 = Math.abs(Math.cos(a)) * wdt * 1.5 + 1;
      ctx.fillStyle = hexA(o.col, .55); ctx.fillRect(-w2, -h, w2 * 2, h);
    }
    ctx.restore(); ctx.globalAlpha = 1;
  }
  if (cursed) { ctx.globalAlpha = .22 + pu * .2; ctx.fillStyle = '#1a0a10'; ctx.beginPath(); ctx.ellipse(it.x, it.y + 4, 24, 11, 0, 0, TAU); ctx.fill(); ctx.globalAlpha = 1; }
  glow(it.x, it.y, 28 + rank * 7, o.col, (cursed ? .3 : .38) + pu * .18); shadow(it.x, it.y + 9, 8, 3, .32);
  const sp = o.slot === 'weapon' ? 'sword' : o.slot === 'armour' ? 'shield' : 'p_pouch';
  if (!sprProp(sp, it.x, it.y + 11 + b, 1.5)) {
    ctx.fillStyle = o.col; ctx.beginPath(); ctx.moveTo(it.x, it.y - 7 + b); ctx.lineTo(it.x + 6, it.y + b); ctx.lineTo(it.x, it.y + 7 + b); ctx.lineTo(it.x - 6, it.y + b); ctx.fill();
  }
  /* motes fall inward on good loot, scatter outward on cursed */
  const n = 2 + rank;
  for (let i = 0; i < n; i++) {
    const a = clock * (cursed ? -2.4 : 1.6) + i * (TAU / n);
    const rr = cursed ? 9 + Math.abs(Math.sin(clock * 2 + i)) * 13 : 15 - Math.abs(Math.sin(clock * 1.7 + i)) * 9;
    ctx.fillStyle = hexA(o.col, .85);
    ctx.fillRect(it.x + Math.cos(a) * rr, it.y - 12 + Math.sin(a) * rr * .45 - (cursed ? 0 : Math.abs(Math.sin(clock * 2.4 + i)) * 7), 2, 2);
  }
}""")

# --- opening a chest is worth a beat -------------------------------------
edit(L, """function drawChestFx(f) {
  const t = f.t / .8, al = 1 - t, s = f.big ? 1.25 : 1;
  ctx.save(); ctx.translate(f.x, f.y); ctx.scale(s, s); ctx.globalAlpha = Math.min(1, al * 1.6);
  if (!sprProp('chest_open', 0, 10 / s * 1, 1.7)) { chestBody(f.big); ctx.save(); ctx.translate(0, -6); ctx.rotate(-Math.min(1, t * 3) * 1.1); chestLid(f.big); ctx.restore(); }
  const g = ctx.createLinearGradient(0, -6, 0, -50); g.addColorStop(0, 'rgba(255,225,140,' + al * .8 + ')'); g.addColorStop(1, 'rgba(255,225,140,0)');
  ctx.fillStyle = g; ctx.beginPath(); ctx.moveTo(-9, -6); ctx.lineTo(9, -6); ctx.lineTo(16, -50); ctx.lineTo(-16, -50); ctx.fill();
  ctx.restore();
}""",
     """function drawChestFx(f) {
  const t = f.t / .8, al = 1 - t, s = f.big ? 1.25 : 1;
  const open = Math.min(1, t * 2.6), crack = Math.min(1, t * 7);
  ctx.save(); ctx.translate(f.x, f.y); ctx.scale(s, s); ctx.globalAlpha = Math.min(1, al * 1.6);
  /* light escapes the seam before the lid is up */
  if (crack < 1) { ctx.globalAlpha = Math.min(1, al * 1.6) * crack; ctx.fillStyle = 'rgba(255,245,205,.95)'; ctx.fillRect(-10, -8, 20, 3 + crack * 3); ctx.globalAlpha = Math.min(1, al * 1.6); }
  if (!sprProp('chest_open', 0, 10 / s * 1, 1.7)) { chestBody(f.big); ctx.save(); ctx.translate(0, -6); ctx.rotate(-open * 1.45); chestLid(f.big); ctx.restore(); }
  const gh = 46 + open * 26;
  const g = ctx.createLinearGradient(0, -6, 0, -gh); g.addColorStop(0, 'rgba(255,230,155,' + al * .9 + ')'); g.addColorStop(.55, 'rgba(255,225,140,' + al * .4 + ')'); g.addColorStop(1, 'rgba(255,225,140,0)');
  ctx.fillStyle = g; ctx.beginPath(); ctx.moveTo(-9, -6); ctx.lineTo(9, -6); ctx.lineTo(14 + open * 8, -gh); ctx.lineTo(-14 - open * 8, -gh); ctx.fill();
  /* a flare on the moment it gives */
  if (t < .3) { const q = 1 - t / .3; ctx.globalAlpha = q * .8; glow(0, -8, 38 * (1 + (1 - q)), '#fff3cc', .9); ctx.globalAlpha = 1; }
  ctx.restore();
}""")

edit(L, """function openChest(P, it) {
  sfx('door'); G.shake = Math.max(G.shake, .15);""",
     """function openChest(P, it) {
  sfx('door'); G.shake = Math.max(G.shake, it.big ? .3 : .18); G.hitstop = Math.max(G.hitstop, .04);""")

# --- props crack before they break ---------------------------------------
edit(L, """  const wob = p.wob > 0 ? Math.sin(p.wob * 60) * 1.6 * (p.wob / .18) : 0;
  sprProp(p.k, p.x + wob, p.y + 8, p.sc, p.fl > 0 ? '#ffffff' : null, .6);
  if (p.hp < p.max) { ctx.fillStyle = '#0a0c11'; ctx.fillRect(p.x - 9, p.y + 12, 18, 3); ctx.fillStyle = '#d9b44a'; ctx.fillRect(p.x - 9, p.y + 12, 18 * Math.max(0, p.hp) / p.max, 3); }""",
     """  const dmg = 1 - Math.max(0, p.hp) / p.max;
  const wob = p.wob > 0 ? Math.sin(p.wob * 60) * (1.6 + dmg * 2.2) * (p.wob / .18) : 0;
  /* a prop near breaking leans and shivers, so you can tell one more hit will do */
  const lean = dmg > .5 ? Math.sin(clock * 3 + p.ph) * dmg * .05 : 0;
  if (lean) { ctx.save(); ctx.translate(p.x, p.y + 8); ctx.rotate(lean); ctx.translate(-p.x, -(p.y + 8)); }
  sprProp(p.k, p.x + wob, p.y + 8, p.sc * (1 - dmg * .05), p.fl > 0 ? '#ffffff' : null, .6);
  if (lean) ctx.restore();
  if (dmg > .28) {
    /* cracks that spread with the damage */
    ctx.save(); ctx.globalAlpha = Math.min(.75, dmg * .9); ctx.strokeStyle = 'rgba(16,12,10,.95)'; ctx.lineWidth = 1.2;
    const n = dmg > .66 ? 3 : 2;
    for (let i = 0; i < n; i++) {
      const sx2 = p.x + (hr(i, 1, 9) - .5) * 13 * p.sc, sy2 = p.y + 2 - hr(i, 2, 9) * 11 * p.sc;
      ctx.beginPath(); ctx.moveTo(sx2, sy2);
      let cx2 = sx2, cy2 = sy2;
      for (let j = 0; j < 3; j++) { cx2 += (hr(i, j + 3, 9) - .5) * 7; cy2 += 3.4 * p.sc; ctx.lineTo(cx2, cy2); }
      ctx.stroke();
    }
    ctx.restore();
  }
  if (p.hp < p.max) { ctx.fillStyle = '#0a0c11'; ctx.fillRect(p.x - 9, p.y + 12, 18, 3); ctx.fillStyle = dmg > .66 ? '#e0734a' : '#d9b44a'; ctx.fillRect(p.x - 9, p.y + 12, 18 * Math.max(0, p.hp) / p.max, 3); }""")

edit(L, """function hurtProp(p, dmg, ang) {
  p.hp -= dmg; p.fl = .1; p.wob = .18; sfx('hit'); const cols = MATCOL[propMat(p.k)];""",
     """function hurtProp(p, dmg, ang) {
  p.hp -= dmg; p.fl = .1; p.wob = p.hp / p.max < .4 ? .26 : .18; sfx('hit'); const cols = MATCOL[propMat(p.k)];""")

run()
