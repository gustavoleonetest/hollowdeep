from patch import edit, run

L = 'part_logic.js'

# --- burn ticks down, and can finish a foe -----------------------------------
edit(L, """    e.t += dt; e.flash = Math.max(0, e.flash - dt); e.cd -= dt; e.age += dt; e.fl = Math.max(0, e.fl - dt); e.atk = Math.max(-1, e.atk - dt);""",
     """    e.t += dt; e.flash = Math.max(0, e.flash - dt); e.cd -= dt; e.age += dt; e.fl = Math.max(0, e.fl - dt); e.atk = Math.max(-1, e.atk - dt);
    if (e.burn > 0 && !e.dead) {
      e.burn -= dt; e.burnT -= dt;
      if (Math.random() < .5) G.parts.push({ x: e.x + rnd(-7, 7), y: e.y + rnd(-9, 3), vx: rnd(-.15, .15), vy: -.5, life: .42, max: .42, col: Math.random() < .5 ? '#ffb347' : '#ff7a3a', s: 2, k: 'ember' });
      if (e.burnT <= 0) {
        e.burnT = .4; e.hp -= e.burnDmg; text(e.x + rnd(-7, 7), e.y - e.r - 2, String(Math.round(e.burnDmg)), '#ff9a4a', 11);
        if (e.hp <= 0) { finishFoe(e); continue; }
      }
    }""")

# --- the bloat waddles up, swells, and goes off ------------------------------
edit(L, """    if (e.boss && e.alert) {
      e.ph = e.hp < e.max * .5 ? 2 : 1;
      if (e.st !== 'chase') { e.stt += dt; tx = 0; ty = 0; if (e.stt >= ({ slam: .9, burst: .6, summon: .7 }[e.st] || .6)) bossAct(e); }
      else {
        if (e.ph === 2) { tx *= 1.3; ty *= 1.3; }
        if (e.cd <= 0 && seen) { const pool = e.ph === 2 ? ['slam', 'burst', 'summon', 'burst'] : ['slam', 'burst']; e.st = pool[e.n++ % pool.length]; e.stt = 0; sfx('bone'); }
      }
    }""",
     """    if (e.type === 'bloat' && e.alert) {
      if (e.fuse > 0) {
        e.fuse -= dt; tx = 0; ty = 0;
        if (Math.random() < .7) G.parts.push({ x: e.x + rnd(-9, 9), y: e.y + rnd(-11, 4), vx: 0, vy: -.6, life: .3, max: .3, col: '#d8f0a0', s: 2, k: 'ember' });
        if (e.fuse <= 0) { finishFoe(e); continue; }
      } else if (bd < 48 && seen) { e.fuse = .6; sfx('bone'); G.fxs.push({ kind: 'shock', x: e.x, y: e.y, t: .18, r: 62, c1: '234,255,196', c2: '143,191,90' }); }
    }
    if (e.boss && e.alert) {
      e.ph = e.hp < e.max * .26 ? 3 : e.hp < e.max * .5 ? 2 : 1;
      if (e.st === 'charge') {
        e.stt += dt;
        if (e.stt < .68) { tx = 0; ty = 0; e.ca = e.face; }
        else if (e.stt < 1.42) { tx = Math.cos(e.ca) * e.spd * 5.4; ty = Math.sin(e.ca) * e.spd * 5.4; if (Math.random() < .7) burst(e.x, e.y, '#ff5a46', 2, 80, .6, 'spark'); }
        else bossAct(e);
      }
      else if (e.st !== 'chase') { e.stt += dt; tx = 0; ty = 0; if (e.stt >= ({ slam: .9, burst: .6, summon: .7 }[e.st] || .6)) bossAct(e); }
      else {
        if (e.ph >= 2) { const m2 = e.ph >= 3 ? 1.5 : 1.3; tx *= m2; ty *= m2; }
        if (e.cd <= 0 && seen) { const pool = e.ph >= 3 ? ['charge', 'burst', 'slam', 'summon', 'burst', 'charge'] : e.ph === 2 ? ['slam', 'burst', 'summon', 'burst'] : ['slam', 'burst']; e.st = pool[e.n++ % pool.length]; e.stt = 0; sfx('bone'); }
      }
    }""")

# --- the charge lands, and phase three comes faster --------------------------
edit(L, """  const st = e.st; e.st = 'chase'; e.stt = 0; e.cd = e.ph === 2 ? 1.6 : 2.4;
  if (st === 'slam') {""",
     """  const st = e.st; e.st = 'chase'; e.stt = 0; e.cd = e.ph >= 3 ? 1.1 : e.ph === 2 ? 1.6 : 2.4;
  if (st === 'charge') {
    G.fxs.push({ kind: 'shock', x: e.x, y: e.y, t: 0, r: 90, c1: '255,230,200', c2: '255,90,70' });
    G.shake = Math.max(G.shake, .3); sfx('boom'); burst(e.x, e.y, '#3a4152', 8, 100, 1.3, 'smoke'); burst(e.x, e.y, '#fff3d0', 8, 170, .7, 'spark');
    for (const p of G.players) if (!p.down && Math.hypot(p.x - e.x, p.y - e.y) < 90 + p.r) hurtPlayer(p, Math.round(e.dmg * .7), Math.atan2(p.y - e.y, p.x - e.x));
  } else if (st === 'slam') {""")

# --- spike traps: telegraphed floor hazards that cut both ways ---------------
edit(L, """/* ---------- breakable props ---------- */""",
     """/* ---------- floor hazards ----------
   Spikes run on a slow cycle with a visible warning beat. They hurt foes harder
   than they hurt you, so a corridor trap is a tool as much as a threat. */
function makeHazards() {
  G.hazards = [];
  if (G.level < 2 || !G.rooms.length) return;
  const want = Math.min(11, 2 + Math.floor(G.level * .9)), avoid = [[G.exit.x, G.exit.y, 72]];
  for (const P of G.players) avoid.push([P.x, P.y, 96]);
  for (const i of G.items) avoid.push([i.x, i.y, 36]);
  for (const n of G.nests) avoid.push([n.x, n.y, 40]);
  for (let k = want, t = 0; k > 0 && t < 320; t++) {
    const r = G.rooms[rint(1, G.rooms.length - 1)];
    if (r.w < 5 || r.h < 4) continue;
    const tx = rint(r.x + 1, r.x + r.w - 2), ty = rint(r.y + 1, r.y + r.h - 2);
    if (G.map[ty * MW + tx] !== 0) continue;
    const x = tx * T + T / 2, y = ty * T + T / 2;
    if (avoid.some(a => Math.hypot(x - a[0], y - a[1]) < a[2])) continue;
    if (G.props.some(p => Math.hypot(x - p.x, y - p.y) < 28)) continue;
    if (G.hazards.some(h => Math.hypot(x - h.x, y - h.y) < 44)) continue;
    G.hazards.push({ x, y, r: 15, ph: Math.random() * 4, cyc: rnd(2.5, 3.6), dmg: Math.round(8 + G.level * 1.6), hit: new Set(), cy: -1, up: 0, warn: false });
    k--;
  }
}
function updateHazards(dt) {
  for (const h of G.hazards) {
    h.ph += dt;
    const cy = Math.floor(h.ph / h.cyc);
    if (cy !== h.cy) { h.cy = cy; h.hit.clear(); }
    const t = (h.ph % h.cyc) / h.cyc;
    h.warn = t >= .66 && t < .8;
    h.up = t < .8 ? 0 : t < .94 ? Math.min(1, (t - .8) / .05) : Math.max(0, 1 - (t - .94) / .06);
    if (h.warn && Math.random() < .22) G.parts.push({ x: h.x + rnd(-11, 11), y: h.y + rnd(-6, 6), vx: 0, vy: -.3, life: .4, max: .4, col: '#8d93a8', s: 2 });
    if (h.up <= .5) continue;
    if (h.up > .5 && h.rang !== h.cy) { h.rang = h.cy; sfx('bone'); }
    for (const P of G.players) if (!P.down && !h.hit.has(P) && Math.hypot(P.x - h.x, P.y - h.y) < h.r + P.r) { h.hit.add(P); hurtPlayer(P, h.dmg, Math.atan2(P.y - h.y, P.x - h.x)); }
    for (const e of G.enemies.slice()) if (!e.dead && e.hp > 0 && !h.hit.has(e) && Math.hypot(e.x - h.x, e.y - h.y) < h.r + e.r) { h.hit.add(e); hurtFoe(e, h.dmg * 2.4, Math.atan2(e.y - h.y, e.x - h.x)); }
  }
}

/* ---------- breakable props ---------- */""")

# --- wire hazards and the chain timer into the level build and the step ------
edit(L, """  G.enemies = []; G.nests = []; G.shots = []; G.eshots = []; G.items = []; G.parts = []; G.texts = []; G.torches = []; G.slash = null; G.decals = []; G.dying = []; G.fxs = []; G.props = [];""",
     """  G.enemies = []; G.nests = []; G.shots = []; G.eshots = []; G.items = []; G.parts = []; G.texts = []; G.torches = []; G.slash = null; G.decals = []; G.dying = []; G.fxs = []; G.props = []; G.hazards = []; G.combo = 0; G.comboT = 0;""")

edit(L, """  makeProps();
  G.flowT = 0;""", """  makeProps(); makeHazards();
  G.flowT = 0;""")

edit(L, """  updateRevive(dt); updateEnemies(dt); updateNests(dt); updateShots(dt); updateItems(dt); updateFx(dt);""",
     """  updateRevive(dt); updateEnemies(dt); updateNests(dt); updateShots(dt); updateItems(dt); updateHazards(dt); updateFx(dt);""")

edit(L, """function updateFx(dt) {
  const k = 60 * dt;""", """function updateFx(dt) {
  const k = 60 * dt;
  if (G.comboT > 0) { G.comboT -= dt; if (G.comboT <= 0) G.combo = 0; }""")

# --- arenas are busier, vaults are worth the walk ---------------------------
edit(L, """    const nn = Math.min(3, rint(1, 1 + Math.floor(G.level / 2)) + (r.w * r.h > 60 ? 1 : 0));
    for (let k = 0; k < nn; k++) { const p = roomPoint(r); G.nests.push({ x: p.x, y: p.y, r: 15, hp: 70 + G.level * 14, max: 70 + G.level * 14, t: rnd(.5, 2.5), flash: 0 }); }
    for (let k = rint(1, 3); k > 0; k--) { const p = roomPoint(r); spawnFoe(pickFoe(), p.x, p.y); }""",
     """    const nn = Math.min(3, rint(1, 1 + Math.floor(G.level / 2)) + (r.w * r.h > 60 ? 1 : 0) + (r.kind === 'arena' ? 1 : 0));
    for (let k = 0; k < nn; k++) { const p = roomPoint(r); G.nests.push({ x: p.x, y: p.y, r: 15, hp: 70 + G.level * 14, max: 70 + G.level * 14, t: rnd(.5, 2.5), flash: 0 }); }
    for (let k = rint(1, 3) + (r.kind === 'arena' ? 2 : 0); k > 0; k--) { const p = roomPoint(r); spawnFoe(pickFoe(), p.x, p.y); }
    if (r.kind === 'arena' && G.level >= 2) { const p = roomPoint(r); spawnFoe(pickFoe(), p.x, p.y, true); }
    if (r.kind === 'cells') for (let k = rint(1, 2); k > 0; k--) { const p = roomPoint(r); G.items.push({ kind: 'gold', x: p.x, y: p.y, t: Math.random() * 6 }); }""")

run()
