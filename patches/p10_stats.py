from patch import edit, run

L = 'part_logic.js'

# --- stats now come in layers: class base, earned upgrades, worn gear.
#     Everything downstream keeps reading the same derived fields. --------
edit(L, """  G.players = list.map((k, i) => { const c = CLASSES[k]; return { idx: i, x: 0, y: 0, r: 11, cls: c, hp: c.hp, max: c.hp, cd: 0, inv: 0, dash: 0, dashCd: 0, face: 0, aim: 0, hurt: 0, dx: 0, dy: 0, down: false, rev: 0, dmgMul: 1, spdMul: 1, cdMul: 1, armMul: 1, dashMul: 1, crit: .1, mast: 0, spCd: 3, shield: 0, cast: 0 }; });""",
     """  G.players = list.map((k, i) => {
    const c = CLASSES[k];
    const P = { idx: i, x: 0, y: 0, r: 11, cls: c, hp: c.hp, max: c.hp, cd: 0, inv: 0, dash: 0, dashCd: 0, face: 0, aim: 0, hurt: 0, dx: 0, dy: 0, down: false, rev: 0,
      dmgMul: 1, spdMul: 1, cdMul: 1, armMul: 1, dashMul: 1, crit: .1, mast: 0, spCd: 3, shield: 0, cast: 0, chill: 0,
      up: { dmg: 1, spd: 1, cd: 1, arm: 1, dash: 1, crit: .1, hp: 0 },
      gear: { weapon: null, armour: null, trinket: null },
      xp: 0, plvl: 1, buys: {} };
    recalc(P); P.hp = P.max; return P;
  });""")

# --- the layering itself, plus levelling -----------------------------------
edit(L, """/* ---------- combat ---------- */""",
     """/* ---------- character sheet ---------- */
function recalc(P) {
  const g = { dmg: 1, cd: 1, crit: 0, spd: 1, hp: 0, arm: 1, leech: 0, thorns: 0, gold: 0, sp: 0, dash: 1, elem: null, elemDmg: 0 };
  for (const slot of SLOTS) {
    const it = P.gear[slot]; if (!it) continue;
    const s = it.s;
    if (s.dmg) g.dmg *= 1 + s.dmg;
    if (s.cd) g.cd *= 1 + s.cd;
    if (s.crit) g.crit += s.crit;
    if (s.spd) g.spd *= 1 + s.spd;
    if (s.hp) g.hp += s.hp;
    if (s.arm) g.arm *= 1 - s.arm;
    if (s.leech) g.leech += s.leech;
    if (s.thorns) g.thorns += s.thorns;
    if (s.gold) g.gold += s.gold;
    if (s.sp) g.sp += s.sp;
    if (s.dash) g.dash *= 1 + s.dash;
    if (s.elem && slot === 'weapon') { g.elem = s.elem; g.elemDmg = s.elemDmg || .4; }
  }
  P.g = g;
  P.dmgMul = P.up.dmg * g.dmg;
  P.cdMul = Math.max(.3, P.up.cd * g.cd);
  P.spdMul = P.up.spd * g.spd;
  P.armMul = Math.max(.32, P.up.arm * g.arm);
  P.dashMul = Math.max(.35, P.up.dash * g.dash);
  P.crit = Math.min(.75, P.up.crit + g.crit);
  const nm = Math.round(P.cls.hp + P.up.hp + g.hp), d = nm - P.max;
  P.max = nm; if (d > 0) P.hp += d;
  P.hp = Math.min(P.hp, P.max);
}
function equip(P, it) {
  const old = P.gear[it.slot];
  P.gear[it.slot] = it; recalc(P);
  text(P.x, P.y - 26, it.name, it.col, 13); sfx('stairs');
  burst(P.x, P.y, it.col, 18, 120, 1, 'spark');
  G.fxs.push({ kind: 'shock', x: P.x, y: P.y, t: 0, r: 80, c1: '255,250,230', c2: '200,200,255' });
  return old;
}
const xpNeed = l => Math.round(36 + l * 30 + l * l * 7);
function gainXp(amt) {
  for (const P of G.players) {
    if (P.down) continue;
    P.xp += amt;
    let guard = 0;
    while (P.xp >= xpNeed(P.plvl) && guard++ < 20) {
      P.xp -= xpNeed(P.plvl); P.plvl++;
      P.up.hp += 7; recalc(P); P.hp = Math.min(P.max, P.hp + P.max * .35);
      announceOnce('lvl' + P.idx, .6, P.cls.name + ' reaches level ' + P.plvl, P.cls.col);
      G.fxs.push({ kind: 'shock', x: P.x, y: P.y, t: 0, r: 130, c1: '255,245,210', c2: '240,190,70' });
      burst(P.x, P.y, '#ffd24a', 26, 180, 1.2, 'spark'); sfx('stairs');
      queueOffer({ kind: 'up', P, opts: rollOffer(false) });
    }
  }
}
/* one card at a time, the rest wait their turn */
function queueOffer(o) { G.offerQ.push(o); nextOffer(); }
function nextOffer() {
  if (G.offer || !G.offerQ.length || (G.state !== 'play' && G.state !== 'offer')) return;
  G.offer = G.offerQ.shift(); G.state = 'offer';
}
function closeOffer() {
  G.offer = null;
  if (G.offerQ.length) { G.offer = G.offerQ.shift(); G.state = 'offer'; }
  else G.state = 'play';
}

/* ---------- combat ---------- */""")

# --- upgrades write to the upgrade layer, then recompute -------------------
edit(L, """function applyUp(P, id, m) {
  const u = { id };
  if (u.id === 'vit') { const v = Math.round(25 * m); P.max += v; P.hp = Math.min(P.max, P.hp + v); }
  else if (u.id === 'swift') P.spdMul *= 1 + .1 * m;
  else if (u.id === 'power') P.dmgMul *= 1 + .2 * m;
  else if (u.id === 'haste') P.cdMul = Math.max(.35, P.cdMul * (1 - .12 * m));
  else if (u.id === 'ward') P.armMul = Math.max(.45, P.armMul * (1 - .08 * m));
  else if (u.id === 'dash') P.dashMul = Math.max(.4, P.dashMul * (1 - .2 * m));
  else if (u.id === 'crit') P.crit = Math.min(.7, P.crit + .08 * m);
  else if (u.id === 'master') P.mast = Math.min(6, P.mast + (m > 1 ? 2 : 1));
  const info = upInfo(P, u.id, m); text(P.x, P.y - 22, info.name + '!', info.col); sfx('stairs');
  burst(P.x, P.y, info.col, 16, 100);
}
function applyUpgrade(i) {
  const o = G.offer, u = o.opts[i]; applyUp(o.P, u.id, u.m); G.offer = null; G.state = 'play';
}""",
     """function applyUp(P, id, m) {
  if (id === 'vit') P.up.hp += Math.round(25 * m);
  else if (id === 'swift') P.up.spd *= 1 + .1 * m;
  else if (id === 'power') P.up.dmg *= 1 + .2 * m;
  else if (id === 'haste') P.up.cd *= 1 - .12 * m;
  else if (id === 'ward') P.up.arm *= 1 - .08 * m;
  else if (id === 'dash') P.up.dash *= 1 - .2 * m;
  else if (id === 'crit') P.up.crit += .08 * m;
  else if (id === 'master') P.mast = Math.min(6, P.mast + (m > 1 ? 2 : 1));
  recalc(P);
  if (id === 'vit') P.hp = Math.min(P.max, P.hp + Math.round(25 * m));
  const info = upInfo(P, id, m); text(P.x, P.y - 22, info.name + '!', info.col); sfx('stairs');
  burst(P.x, P.y, info.col, 16, 100);
}
function applyUpgrade(i) {
  const o = G.offer;
  if (o.kind === 'gear') { if (i === 0) equip(o.P, o.item); else { text(o.P.x, o.P.y - 20, 'Left behind', '#98a0b3'); } }
  else { const u = o.opts[i]; applyUp(o.P, u.id, u.m); }
  closeOffer();
}""")

edit(L, """  G.offer = { P, opts: rollOffer(it.big) }; G.state = 'offer';""",
     """  queueOffer({ kind: 'up', P, opts: rollOffer(it.big) });
  if (it.big) dropGear(it.x, it.y, 18);""")

run()
