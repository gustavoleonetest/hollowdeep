from patch import edit, run

L = 'part_logic.js'

# --- damage now carries who dealt it, so gear and elite traits can react ----
edit(L, """function hurtPlayer(P, dmg, ang) {
  if (P.down || P.inv > 0 || G.state !== 'play') return;
  const d = Math.max(1, Math.round(dmg * P.cls.armor * P.armMul * (P.shield > 0 ? .3 : 1)));
  P.hp -= d; P.inv = .55; P.hurt = .25; G.shake = Math.max(G.shake, .3);
  if (G.combo > 0) { G.combo = Math.floor(G.combo * .5); if (G.combo <= 0) G.comboT = 0; }
  moveEnt(P, Math.cos(ang) * -6, Math.sin(ang) * -6);
  text(P.x, P.y - 16, '-' + d, '#d9534f'); sfx('hurt'); burst(P.x, P.y, '#d9534f', 6, 70);
  if (P.hp <= 0) {
    P.hp = 0; P.down = true; P.rev = 0; burst(P.x, P.y, P.cls.col, 18, 120); text(P.x, P.y - 22, 'Down!', '#d9534f');
    if (G.players.every(p => p.down)) die();
  }
}""",
     """function downPlayer(P) {
  if (P.down) return;
  P.hp = 0; P.down = true; P.rev = 0; burst(P.x, P.y, P.cls.col, 18, 120); text(P.x, P.y - 22, 'Down!', '#d9534f');
  announceOnce('down' + P.idx, 1.5, P.cls.name + ' has fallen', '#d9534f');
  if (G.players.every(p => p.down)) die();
}
function hurtPlayer(P, dmg, ang, src) {
  if (P.down || P.inv > 0 || G.state !== 'play') return;
  const d = Math.max(1, Math.round(dmg * P.cls.armor * P.armMul * (P.shield > 0 ? .3 : 1)));
  P.hp -= d; P.inv = .55; P.hurt = .25; G.shake = Math.max(G.shake, .3);
  if (G.combo > 0) { G.combo = Math.floor(G.combo * .5); if (G.combo <= 0) G.comboT = 0; }
  moveEnt(P, Math.cos(ang) * -6, Math.sin(ang) * -6);
  text(P.x, P.y - 16, '-' + d, '#d9534f'); sfx('hurt'); burst(P.x, P.y, '#d9534f', 6, 70);
  if (src && src.hp > 0 && !src.dead) {
    if (P.g && P.g.thorns > 0) hurtFoe(src, d * P.g.thorns, ang + Math.PI, false, false, null);
    if (src.eaff) {
      if (src.eaff.indexOf('vamp') >= 0) { src.hp = Math.min(src.max, src.hp + d * .6); burst(src.x, src.y, '#d9534f', 5, 80, .7, 'spark'); }
      if (src.eaff.indexOf('frozen') >= 0) { P.chill = 1.8; burst(P.x, P.y, '#8fd3ff', 8, 90, .8, 'spark'); }
    }
  }
  if (P.hp <= 0) downPlayer(P);
}""")

# --- elements, leech, immunity ---------------------------------------------
edit(L, """function hurtFoe(e, dmg, ang, crit, burn) {
  if (e.dead) return;
  if (crit) dmg *= 2.25;""",
     """/* Death shrugs off ordinary blows; only a special or a potion counts */
let SMITE = false;
function applyElem(e, P, dmg) {
  const g = P && P.g; if (!g || !g.elem) return;
  const ed = Math.max(1, dmg * g.elemDmg);
  if (g.elem === 'fire') { e.burn = Math.max(e.burn || 0, 2.4); e.burnDmg = Math.max(e.burnDmg || 0, Math.max(2, ed * .45)); }
  else if (g.elem === 'cold') { e.chill = 2; burst(e.x, e.y, '#8fd3ff', 4, 80, .7, 'spark'); }
  else if (g.elem === 'poison') { e.pois = 3.4; e.poisDmg = Math.max(e.poisDmg || 0, Math.max(1.5, ed * .3)); }
  else if (g.elem === 'shock') {
    let n = 0;
    for (const o of G.enemies.slice()) {
      if (n >= 2 || o === e || o.dead || o.hp <= 0) continue;
      if (Math.hypot(o.x - e.x, o.y - e.y) > 115) continue;
      n++; G.bolts.push({ x1: e.x, y1: e.y, x2: o.x, y2: o.y, t: 0 });
      hurtFoe(o, ed, Math.atan2(o.y - e.y, o.x - e.x), false, false, null);
    }
  }
}
function hurtFoe(e, dmg, ang, crit, burn, src) {
  if (e.dead) return;
  if (e.immune && !SMITE) {
    if (!e.immT || clock - e.immT > .9) { e.immT = clock; text(e.x, e.y - e.r - 6, 'Immune', '#cfd4e0', 12); }
    burst(e.x, e.y, '#cfd4e0', 3, 70, .6, 'spark'); return;
  }
  if (e.eaff && e.eaff.indexOf('warded') >= 0 && e.ward > 0) {
    e.ward -= dmg; e.wardFl = .18;
    burst(e.x, e.y, '#ffd24a', 4, 90, .6, 'spark'); text(e.x, e.y - e.r - 4, 'Blocked', '#ffd24a', 12); sfx('hit');
    if (e.ward > 0) return;
    dmg = -e.ward; e.ward = 0;
  }
  if (crit) dmg *= 2.25;""")

edit(L, """  if (dmg >= 40 || e.boss || e.type === 'brute') G.shake = Math.max(G.shake, .08);
  if (e.hp <= 0) finishFoe(e, ang);
}""",
     """  if (dmg >= 40 || e.boss || e.type === 'brute') G.shake = Math.max(G.shake, .08);
  if (src) {
    applyElem(e, src, dmg);
    if (src.g && src.g.leech > 0 && !src.down && src.hp < src.max) {
      src.hp = Math.min(src.max, src.hp + dmg * src.g.leech);
      if (Math.random() < .4) G.parts.push({ x: e.x, y: e.y, vx: (src.x - e.x) * .02, vy: (src.y - e.y) * .02, life: .4, max: .4, col: '#d9534f', s: 2.2 });
    }
  }
  if (e.hp <= 0) finishFoe(e, ang);
}""")

# --- elites roll Diablo-style modifiers ------------------------------------
edit(L, """  const hp = d.hp * s * (elite ? 2.7 : 1);
  G.enemies.push({ type, x, y, r: d.r * (elite ? 1.22 : 1), hp, max: hp, spd: d.spd * (1 + (G.level - 1) * .03) * (elite ? .93 : 1), dmg: Math.round((d.dmg + G.level) * (elite ? 1.45 : 1)), col: d.col, elite: !!elite, t: rnd(0, 6), cd: rnd(1, 2), kx: 0, ky: 0, flash: 0, alert: false, st: 'chase', stt: 0, n: 0, ph: 1, boss: type === 'warden', age: 0, fl: 0, fa: 0, atk: -1, burn: 0, burnDmg: 0, burnT: 0, dead: 0, fuse: 0 });""",
     """  const hp = d.hp * s * (elite ? 2.7 : 1);
  const eaff = [];
  if (elite) {
    const pool = EAFF.slice();
    for (let i = 0, n = G.level >= 7 ? 2 : 1; i < n && pool.length; i++) eaff.push(pool.splice(rint(0, pool.length - 1), 1)[0].id);
  }
  const E = { type, x, y, r: d.r * (elite ? 1.22 : 1), hp, max: hp, spd: d.spd * (1 + (G.level - 1) * .03) * (elite ? .93 : 1), dmg: Math.round((d.dmg + G.level) * (elite ? 1.45 : 1)), col: d.col, elite: !!elite, eaff, t: rnd(0, 6), cd: rnd(1, 2), kx: 0, ky: 0, flash: 0, alert: false, st: 'chase', stt: 0, n: 0, ph: 1, boss: type === 'warden', age: 0, fl: 0, fa: 0, atk: -1, burn: 0, burnDmg: 0, burnT: 0, pois: 0, poisDmg: 0, poisT: 0, chill: 0, dead: 0, fuse: 0, loot: 0, immune: type === 'reaper' };
  if (eaff.indexOf('fast') >= 0) E.spd *= 1.55;
  if (eaff.indexOf('warded') >= 0) { E.wardMax = hp * .45; E.ward = E.wardMax; }
  G.enemies.push(E);""")

# --- fire-enchanted elites go off when they die ----------------------------
edit(L, """  if (e.elite) {
    coinSpray(e.x, e.y, 10); G.shake = Math.max(G.shake, .26); sfx('boom');""",
     """  if (e.eaff && e.eaff.indexOf('fiery') >= 0) {
    const R = 92, dm = e.dmg * 1.5;
    G.fxs.push({ kind: 'shock', x: e.x, y: e.y, t: 0, r: R + 20, c1: '255,240,200', c2: '255,106,60' });
    G.slash = { x: e.x, y: e.y, a: 0, life: .22, kind: 'boom', rad: R };
    burst(e.x, e.y, '#ff6a3d', 22, 180, 1.2, 'ember'); G.shake = Math.max(G.shake, .3); sfx('boom');
    for (const p of G.players) if (!p.down && Math.hypot(p.x - e.x, p.y - e.y) < R + p.r) hurtPlayer(p, dm, Math.atan2(p.y - e.y, p.x - e.x));
  }
  if (e.elite) {
    coinSpray(e.x, e.y, 10); G.shake = Math.max(G.shake, .26); sfx('boom');""")

# --- every damage call now names its source --------------------------------
edit(L, """  for (const e of G.enemies.slice()) if (e.hp > 0 && Math.hypot(e.x - s.x, e.y - s.y) < s.rad + e.r) hurtFoe(e, s.dmg * .7, Math.atan2(e.y - s.y, e.x - s.x), s.crit, true);""",
     """  for (const e of G.enemies.slice()) if (e.hp > 0 && Math.hypot(e.x - s.x, e.y - s.y) < s.rad + e.r) hurtFoe(e, s.dmg * .7, Math.atan2(e.y - s.y, e.x - s.x), s.crit, true, s.own);""")

edit(L, """        s.hit.add(e); hurtFoe(e, s.dmg, Math.atan2(s.vy, s.vx), s.crit, s.kind === 'fire');""",
     """        s.hit.add(e); hurtFoe(e, s.dmg, Math.atan2(s.vy, s.vx), s.crit, s.kind === 'fire', s.own);""")

edit(L, """    for (const e of G.enemies.slice()) if (e.hp > 0 && inArc(e, e.r)) hurtFoe(e, dm, a, cr);""",
     """    for (const e of G.enemies.slice()) if (e.hp > 0 && inArc(e, e.r)) hurtFoe(e, dm, a, cr, false, P);""")

edit(L, """  const mk = ang => ({ x: P.x + Math.cos(a) * 12, y: P.y + Math.sin(a) * 12, vx: Math.cos(ang) * c.shot, vy: Math.sin(ang) * c.shot, dmg: dm, life: c.atk === 'arrow' ? 1.3 : c.atk === 'fire' ? 1.5 : .8, r: c.atk === 'fire' ? 7 : 4, kind: c.atk, col: c.col, pierce: c.atk === 'arrow' ? 2 + P.mast : 0, rad: (c.rad || 0) + 9 * P.mast, hit: new Set(), trail: [], crit: cr });""",
     """  const mk = ang => ({ x: P.x + Math.cos(a) * 12, y: P.y + Math.sin(a) * 12, vx: Math.cos(ang) * c.shot, vy: Math.sin(ang) * c.shot, dmg: dm, life: c.atk === 'arrow' ? 1.3 : c.atk === 'fire' ? 1.5 : .8, r: c.atk === 'fire' ? 7 : 4, kind: c.atk, col: c.col, pierce: c.atk === 'arrow' ? 2 + P.mast : 0, rad: (c.rad || 0) + 9 * P.mast, hit: new Set(), trail: [], crit: cr, own: P });""")

# --- specials are a smite, so they bite Death ------------------------------
edit(L, """  text(P.x, P.y - 30, SPECIALS[c.key], c.col, 14);""",
     """  text(P.x, P.y - 30, SPECIALS[c.key], c.col, 14);
  SMITE = true;""")

edit(L, """    near(115, (e, ang) => { hurtFoe(e, dm * 1.9, ang, cr); e.kx += Math.cos(ang) * (e.boss ? 1 : 9); e.ky += Math.sin(ang) * (e.boss ? 1 : 9); });""",
     """    near(115, (e, ang) => { hurtFoe(e, dm * 1.9, ang, cr, false, P); e.kx += Math.cos(ang) * (e.boss ? 1 : 9); e.ky += Math.sin(ang) * (e.boss ? 1 : 9); });""")

edit(L, """    near(145, (e, ang) => { hurtFoe(e, dm * 1.3, ang, cr); e.root = e.boss ? 1.2 : 3.2; });""",
     """    near(145, (e, ang) => { hurtFoe(e, dm * 1.3, ang, cr, false, P); e.root = e.boss ? 1.2 : 3.2; });""")

edit(L, """    explode({ x: P.x, y: P.y, rad: 125, dmg: dm * 3, crit: cr });""",
     """    explode({ x: P.x, y: P.y, rad: 125, dmg: dm * 3, crit: cr, own: P });""")

edit(L, """    for (let i = 0; i < 10; i++) { const ang = i / 10 * TAU; G.shots.push({ x: P.x + Math.cos(ang) * 14, y: P.y + Math.sin(ang) * 14, vx: Math.cos(ang) * 5, vy: Math.sin(ang) * 5, dmg: dm * .9, life: .9, r: 7, kind: 'fire', col: c.col, pierce: 0, rad: 44, hit: new Set(), trail: [], crit: cr }); }""",
     """    for (let i = 0; i < 10; i++) { const ang = i / 10 * TAU; G.shots.push({ x: P.x + Math.cos(ang) * 14, y: P.y + Math.sin(ang) * 14, vx: Math.cos(ang) * 5, vy: Math.sin(ang) * 5, dmg: dm * .9, life: .9, r: 7, kind: 'fire', col: c.col, pierce: 0, rad: 44, hit: new Set(), trail: [], crit: cr, own: P }); }""")

edit(L, """    for (let i = 0; i < 10; i++) { const ang = i / 10 * TAU; G.shots.push({ x: P.x, y: P.y, vx: Math.cos(ang) * 9, vy: Math.sin(ang) * 9, dmg: dm * 2, life: .5, r: 4, kind: 'dagger', col: c.col, pierce: 0, rad: 0, hit: new Set(), trail: [], crit: cr }); }""",
     """    for (let i = 0; i < 10; i++) { const ang = i / 10 * TAU; G.shots.push({ x: P.x, y: P.y, vx: Math.cos(ang) * 9, vy: Math.sin(ang) * 9, dmg: dm * 2, life: .5, r: 4, kind: 'dagger', col: c.col, pierce: 0, rad: 0, hit: new Set(), trail: [], crit: cr, own: P }); }""")

edit(L, """    burst(P.x, P.y, '#9bd16a', 18, 150, 1, 'spark');
  }
}""", """    burst(P.x, P.y, '#9bd16a', 18, 150, 1, 'spark');
  }
  SMITE = false;
}""")

run()
