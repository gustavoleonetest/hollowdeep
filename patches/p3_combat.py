from patch import edit, run

L = 'part_logic.js'

# --- new foe: the bloat, a walking bomb -------------------------------------
edit(L, """  hound: { hp: 30, spd: 1.0, r: 10, dmg: 11, col: '#b9893f', gold: .5 },""",
     """  hound: { hp: 30, spd: 1.0, r: 10, dmg: 11, col: '#b9893f', gold: .5 },
  bloat: { hp: 44, spd: .82, r: 13, dmg: 13, col: '#8fbf5a', gold: .85 },""")

# --- run state for hazards and the kill chain --------------------------------
edit(L, """clsKey: 'bulwark', clsKeys: ['bulwark'], players: [], keys: 0, gold: 0, co: false };""",
     """clsKey: 'bulwark', clsKeys: ['bulwark'], players: [], keys: 0, gold: 0, co: false, hazards: [], combo: 0, comboT: 0, comboBest: 0 };""")

# --- spawn table ------------------------------------------------------------
edit(L, """function pickFoe() {
  const r = Math.random(), L = G.level;
  if (L >= 3 && r < .1) return 'brute';
  if (L >= 2 && r < .22) return 'hound';
  if (L >= 2 && r < .42) return 'bonewalker';
  return r < .7 ? 'gloam' : 'wisp';
}
function spawnFoe(type, x, y) {
  const d = FOES[type], s = 1 + (G.level - 1) * .18;
  G.enemies.push({ type, x, y, r: d.r, hp: d.hp * s, max: d.hp * s, spd: d.spd * (1 + (G.level - 1) * .03), dmg: d.dmg + G.level, col: d.col, t: rnd(0, 6), cd: rnd(1, 2), kx: 0, ky: 0, flash: 0, alert: false, st: 'chase', stt: 0, n: 0, ph: 1, boss: type === 'warden', age: 0, fl: 0, fa: 0, atk: -1 });
}""", """function pickFoe() {
  const r = Math.random(), L = G.level;
  if (L >= 3 && r < .09) return 'brute';
  if (L >= 2 && r < .2) return 'hound';
  if (L >= 2 && r < .3) return 'bloat';
  if (L >= 2 && r < .48) return 'bonewalker';
  return r < .74 ? 'gloam' : 'wisp';
}
function spawnFoe(type, x, y, elite) {
  const d = FOES[type], s = 1 + (G.level - 1) * .18;
  if (elite == null) elite = type !== 'warden' && G.level >= 2 && Math.random() < Math.min(.17, .025 + G.level * .013);
  const hp = d.hp * s * (elite ? 2.7 : 1);
  G.enemies.push({ type, x, y, r: d.r * (elite ? 1.22 : 1), hp, max: hp, spd: d.spd * (1 + (G.level - 1) * .03) * (elite ? .93 : 1), dmg: Math.round((d.dmg + G.level) * (elite ? 1.45 : 1)), col: d.col, elite: !!elite, t: rnd(0, 6), cd: rnd(1, 2), kx: 0, ky: 0, flash: 0, alert: false, st: 'chase', stt: 0, n: 0, ph: 1, boss: type === 'warden', age: 0, fl: 0, fa: 0, atk: -1, burn: 0, burnDmg: 0, burnT: 0, dead: 0, fuse: 0 });
}""")

# --- taking a hit costs half your chain -------------------------------------
edit(L, """  P.hp -= d; P.inv = .55; P.hurt = .25; G.shake = Math.max(G.shake, .3);""",
     """  P.hp -= d; P.inv = .55; P.hurt = .25; G.shake = Math.max(G.shake, .3);
  if (G.combo > 0) { G.combo = Math.floor(G.combo * .5); if (G.combo <= 0) G.comboT = 0; }""")

# --- crits, burn, and a single place where a foe actually dies ---------------
edit(L, """function hurtFoe(e, dmg, ang) {
  dmg = Math.round(dmg); e.hp -= dmg; e.flash = .1; e.alert = true; e.fl = .2; e.fa = ang;
  const kb = e.boss ? .2 : 1; e.kx += Math.cos(ang) * 2.2 * kb; e.ky += Math.sin(ang) * 2.2 * kb;
  text(e.x, e.y - e.r - 4, String(dmg), dmg >= 40 ? '#ffd24a' : '#ebe4d2', Math.min(24, 12 + dmg * .1)); sfx('hit'); G.hitstop = Math.max(G.hitstop, e.boss || e.type === 'brute' ? .035 : .02); burst(e.x, e.y, e.col, 3, 60, .7); burst(e.x, e.y, '#fff3d0', 4, 120, .5, 'spark');
  burstDir(e.x, e.y, ang, '#fff3d0', 5, 230, .9, 'spark', .7); burstDir(e.x, e.y, ang, e.col, 4, 150, 1, 'sq', .9); G.fxs.push({ kind: 'hit', x: e.x, y: e.y, t: 0 });
  if (dmg >= 40 || e.boss || e.type === 'brute') G.shake = Math.max(G.shake, .08);
  if (e.hp <= 0) killFoe(e);
}
function killFoe(e) {
  G.score += { gloam: 10, wisp: 8, bonewalker: 15, brute: 40, hound: 14, warden: 500 }[e.type]; G.hitstop = Math.max(G.hitstop, e.boss ? .14 : e.type === 'brute' ? .07 : .04);""",
     """const comboMult = () => 1 + Math.min(1.6, G.combo * .055);
function hurtFoe(e, dmg, ang, crit, burn) {
  if (e.dead) return;
  if (crit) dmg *= 2.25;
  dmg = Math.round(dmg); e.hp -= dmg; e.flash = .1; e.alert = true; e.fl = crit ? .3 : .2; e.fa = ang;
  const kb = (e.boss ? .2 : 1) * (crit ? 1.5 : 1); e.kx += Math.cos(ang) * 2.2 * kb; e.ky += Math.sin(ang) * 2.2 * kb;
  if (burn) { e.burn = Math.max(e.burn || 0, 2.4); e.burnDmg = Math.max(e.burnDmg || 0, Math.max(2, dmg * .16)); }
  text(e.x, e.y - e.r - 4, crit ? dmg + '!' : String(dmg), crit ? '#fff1b8' : dmg >= 40 ? '#ffd24a' : '#ebe4d2', crit ? Math.min(31, 17 + dmg * .12) : Math.min(24, 12 + dmg * .1));
  sfx('hit'); G.hitstop = Math.max(G.hitstop, crit ? .05 : e.boss || e.type === 'brute' ? .035 : .02); burst(e.x, e.y, e.col, 3, 60, .7); burst(e.x, e.y, '#fff3d0', 4, 120, .5, 'spark');
  burstDir(e.x, e.y, ang, '#fff3d0', 5, 230, .9, 'spark', .7); burstDir(e.x, e.y, ang, e.col, 4, 150, 1, 'sq', .9); G.fxs.push({ kind: 'hit', x: e.x, y: e.y, t: 0 });
  if (crit) { G.fxs.push({ kind: 'crit', x: e.x, y: e.y - 4, t: 0, a: ang }); burstDir(e.x, e.y, ang, '#fff1b8', 10, 330, 1.1, 'spark', .45); G.shake = Math.max(G.shake, .16); }
  if (dmg >= 40 || e.boss || e.type === 'brute') G.shake = Math.max(G.shake, .08);
  if (e.hp <= 0) finishFoe(e, ang);
}
function finishFoe(e) {
  if (e.dead) return; e.dead = 1;
  if (e.type === 'bloat') bloatPop(e); else killFoe(e);
}
/* a bloat going off hurts whatever is nearby, foes included, so a tight pack can chain */
function bloatPop(e) {
  const R = 74, dm = e.dmg * 1.8;
  G.shake = Math.max(G.shake, .34); sfx('boom'); G.hitstop = Math.max(G.hitstop, .05);
  G.slash = { x: e.x, y: e.y, a: 0, life: .24, kind: 'boom', rad: R };
  G.fxs.push({ kind: 'shock', x: e.x, y: e.y, t: 0, r: R + 24, c1: '234,255,196', c2: '143,191,90' });
  burst(e.x, e.y, '#8fbf5a', 24, 175, 1.2); burst(e.x, e.y, '#d8f0a0', 12, 240, .8, 'spark'); burst(e.x, e.y, '#3a4152', 8, 55, 1.5, 'smoke');
  for (const P of G.players) if (!P.down && Math.hypot(P.x - e.x, P.y - e.y) < R + P.r) hurtPlayer(P, dm, Math.atan2(P.y - e.y, P.x - e.x));
  for (const n of G.nests) if (n.hp > 0 && Math.hypot(n.x - e.x, n.y - e.y) < R + n.r) hurtNest(n, dm);
  for (const p of G.props.slice()) if (Math.hypot(p.x - e.x, p.y - e.y) < R + 8) hurtProp(p, dm, Math.atan2(p.y - e.y, p.x - e.x));
  e.hp = 0; killFoe(e);
  for (const o of G.enemies.slice()) if (o !== e && !o.dead && o.hp > 0 && Math.hypot(o.x - e.x, o.y - e.y) < R + o.r) hurtFoe(o, dm * 1.15, Math.atan2(o.y - e.y, o.x - e.x));
}
function killFoe(e) {
  const base = { gloam: 10, wisp: 8, bonewalker: 15, brute: 40, hound: 14, bloat: 22, warden: 500 }[e.type] * (e.elite ? 3 : 1);
  if (!e.boss) { G.combo++; G.comboT = 3.2; if (G.combo > G.comboBest) G.comboBest = G.combo; }
  G.score += Math.round(base * comboMult());
  if (G.combo >= 5 && G.combo % 5 === 0) { text(e.x, e.y - 42, G.combo + ' chain', '#ffd24a', 16); sfx('coin'); }
  G.hitstop = Math.max(G.hitstop, e.boss ? .14 : e.type === 'brute' ? .07 : .04);""")

# --- elites pay out ---------------------------------------------------------
edit(L, """  if (Math.random() < FOES[e.type].gold) G.items.push({ kind: 'gold', x: e.x, y: e.y, t: 0 });
  if (Math.random() < .07) G.items.push({ kind: 'food', x: e.x, y: e.y, t: 0 });""",
     """  if (e.elite) {
    coinSpray(e.x, e.y, 10); G.shake = Math.max(G.shake, .26); sfx('boom');
    G.fxs.push({ kind: 'shock', x: e.x, y: e.y, t: 0, r: 110, c1: '255,245,205', c2: '240,190,70' });
    for (let i = 0; i < 3; i++) G.items.push({ kind: 'gold', x: e.x + rnd(-20, 20), y: e.y + rnd(-16, 16), t: 0 });
    G.items.push(Math.random() < .45 ? { kind: 'chest', x: e.x, y: e.y, t: 0 } : { kind: 'gem', x: e.x, y: e.y, t: 0 });
    text(e.x, e.y - 30, 'Elite slain', '#ffd24a', 15);
  }
  if (Math.random() < FOES[e.type].gold) G.items.push({ kind: 'gold', x: e.x, y: e.y, t: 0 });
  if (Math.random() < .07) G.items.push({ kind: 'food', x: e.x, y: e.y, t: 0 });""")

# --- fire leaves a burn -----------------------------------------------------
edit(L, """  for (const e of G.enemies) if (e.hp > 0 && Math.hypot(e.x - s.x, e.y - s.y) < s.rad + e.r) hurtFoe(e, s.dmg * .7, Math.atan2(e.y - s.y, e.x - s.x));""",
     """  for (const e of G.enemies.slice()) if (e.hp > 0 && Math.hypot(e.x - s.x, e.y - s.y) < s.rad + e.r) hurtFoe(e, s.dmg * .7, Math.atan2(e.y - s.y, e.x - s.x), s.crit, true);""")

edit(L, """        s.hit.add(e); hurtFoe(e, s.dmg, Math.atan2(s.vy, s.vx));""",
     """        s.hit.add(e); hurtFoe(e, s.dmg, Math.atan2(s.vy, s.vx), s.crit, s.kind === 'fire');""")

# --- crit rolls at the moment you commit to a swing or a shot ----------------
edit(L, """  const dm = c.dmg * P.dmgMul, rg = (c.range || 0) + 9 * P.mast, arc = Math.min(3.6, (c.arc || 0) + .18 * P.mast);
  const a = P.aim;""",
     """  const dm = c.dmg * P.dmgMul, rg = (c.range || 0) + 9 * P.mast, arc = Math.min(3.6, (c.arc || 0) + .18 * P.mast);
  const a = P.aim, cr = Math.random() < P.crit;""")

edit(L, """    for (const e of G.enemies) if (e.hp > 0 && inArc(e, e.r)) hurtFoe(e, dm, a);""",
     """    for (const e of G.enemies.slice()) if (e.hp > 0 && inArc(e, e.r)) hurtFoe(e, dm, a, cr);""")

edit(L, """  const mk = ang => ({ x: P.x + Math.cos(a) * 12, y: P.y + Math.sin(a) * 12, vx: Math.cos(ang) * c.shot, vy: Math.sin(ang) * c.shot, dmg: dm, life: c.atk === 'arrow' ? 1.3 : c.atk === 'fire' ? 1.5 : .8, r: c.atk === 'fire' ? 7 : 4, kind: c.atk, col: c.col, pierce: c.atk === 'arrow' ? 2 + P.mast : 0, rad: (c.rad || 0) + 9 * P.mast, hit: new Set(), trail: [] });""",
     """  const mk = ang => ({ x: P.x + Math.cos(a) * 12, y: P.y + Math.sin(a) * 12, vx: Math.cos(ang) * c.shot, vy: Math.sin(ang) * c.shot, dmg: dm, life: c.atk === 'arrow' ? 1.3 : c.atk === 'fire' ? 1.5 : .8, r: c.atk === 'fire' ? 7 : 4, kind: c.atk, col: c.col, pierce: c.atk === 'arrow' ? 2 + P.mast : 0, rad: (c.rad || 0) + 9 * P.mast, hit: new Set(), trail: [], crit: cr });""")

# --- specials crit too ------------------------------------------------------
edit(L, """  const c = P.cls, dm = c.dmg * P.dmgMul, a = P.aim; P.spCd = SP_CD; P.swing = P.swm = .34; P.cast = .4; P.cd = Math.max(P.cd, .25);""",
     """  const c = P.cls, dm = c.dmg * P.dmgMul, a = P.aim, cr = Math.random() < P.crit; P.spCd = SP_CD; P.swing = P.swm = .34; P.cast = .4; P.cd = Math.max(P.cd, .25);""")

edit(L, """    near(115, (e, ang) => { hurtFoe(e, dm * 1.9, ang); e.kx += Math.cos(ang) * (e.boss ? 1 : 9); e.ky += Math.sin(ang) * (e.boss ? 1 : 9); });""",
     """    near(115, (e, ang) => { hurtFoe(e, dm * 1.9, ang, cr); e.kx += Math.cos(ang) * (e.boss ? 1 : 9); e.ky += Math.sin(ang) * (e.boss ? 1 : 9); });""")

edit(L, """    near(145, (e, ang) => { hurtFoe(e, dm * 1.3, ang); e.root = e.boss ? 1.2 : 3.2; });""",
     """    near(145, (e, ang) => { hurtFoe(e, dm * 1.3, ang, cr); e.root = e.boss ? 1.2 : 3.2; });""")

edit(L, """    explode({ x: P.x, y: P.y, rad: 125, dmg: dm * 3 });
    for (let i = 0; i < 10; i++) { const ang = i / 10 * TAU; G.shots.push({ x: P.x + Math.cos(ang) * 14, y: P.y + Math.sin(ang) * 14, vx: Math.cos(ang) * 5, vy: Math.sin(ang) * 5, dmg: dm * .9, life: .9, r: 7, kind: 'fire', col: c.col, pierce: 0, rad: 44, hit: new Set(), trail: [] }); }""",
     """    explode({ x: P.x, y: P.y, rad: 125, dmg: dm * 3, crit: cr });
    for (let i = 0; i < 10; i++) { const ang = i / 10 * TAU; G.shots.push({ x: P.x + Math.cos(ang) * 14, y: P.y + Math.sin(ang) * 14, vx: Math.cos(ang) * 5, vy: Math.sin(ang) * 5, dmg: dm * .9, life: .9, r: 7, kind: 'fire', col: c.col, pierce: 0, rad: 44, hit: new Set(), trail: [], crit: cr }); }""")

edit(L, """    for (let i = 0; i < 10; i++) { const ang = i / 10 * TAU; G.shots.push({ x: P.x, y: P.y, vx: Math.cos(ang) * 9, vy: Math.sin(ang) * 9, dmg: dm * 2, life: .5, r: 4, kind: 'dagger', col: c.col, pierce: 0, rad: 0, hit: new Set(), trail: [] }); }""",
     """    for (let i = 0; i < 10; i++) { const ang = i / 10 * TAU; G.shots.push({ x: P.x, y: P.y, vx: Math.cos(ang) * 9, vy: Math.sin(ang) * 9, dmg: dm * 2, life: .5, r: 4, kind: 'dagger', col: c.col, pierce: 0, rad: 0, hit: new Set(), trail: [], crit: cr }); }""")

# --- the crit upgrade, in chests and in the stall ---------------------------
edit(L, """const UP_IDS = ['vit', 'swift', 'power', 'haste', 'ward', 'dash', 'master'];""",
     """const UP_IDS = ['vit', 'swift', 'power', 'haste', 'ward', 'dash', 'crit', 'master'];""")

edit(L, """    dash: ['Light Step', 'Dash recharges ' + r(20) + '% faster.', '#8fd3ff'],""",
     """    dash: ['Light Step', 'Dash recharges ' + r(20) + '% faster.', '#8fd3ff'],
    crit: ['Keen Edge', '+' + r(8) + '% chance to strike critically for double damage.', '#ffd24a'],""")

edit(L, """  else if (u.id === 'dash') P.dashMul = Math.max(.4, P.dashMul * (1 - .2 * m));""",
     """  else if (u.id === 'dash') P.dashMul = Math.max(.4, P.dashMul * (1 - .2 * m));
  else if (u.id === 'crit') P.crit = Math.min(.7, P.crit + .08 * m);""")

edit(L, """  { id: 'dash', name: 'Light Step', desc: 'Dash recharges 20% faster.', col: '#8fd3ff', base: 55, per: 12, grow: 1.45, max: 4 },""",
     """  { id: 'dash', name: 'Light Step', desc: 'Dash recharges 20% faster.', col: '#8fd3ff', base: 55, per: 12, grow: 1.45, max: 4 },
  { id: 'crit', name: 'Keen Edge', desc: '+8% chance to strike critically for double damage.', col: '#ffd24a', base: 75, per: 15, grow: 1.5, max: 6 },""")

edit(L, """dmgMul: 1, spdMul: 1, cdMul: 1, armMul: 1, dashMul: 1, mast: 0, spCd: 3, shield: 0, cast: 0 }; });""",
     """dmgMul: 1, spdMul: 1, cdMul: 1, armMul: 1, dashMul: 1, crit: .1, mast: 0, spCd: 3, shield: 0, cast: 0 }; });""")

run()
