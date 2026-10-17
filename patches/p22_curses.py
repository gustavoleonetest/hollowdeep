from patch import edit, run

L = 'part_logic.js'

# --- curses and sets ------------------------------------------------------
edit(L, """const BASE_STAT = { weapon: 'dmg', armour: 'arm', trinket: 'crit' };""",
     """/* A curse is a bargain: more of one thing, less of another. They are the only
   items that can make a run worse, which is what makes choosing one interesting. */
const CURSE = [
  { id: 'brittle', name: 'Brittle', s: { dmg: .45, arm: -.14 } },
  { id: 'leaden', name: 'Leaden', s: { dmg: .55, spd: -.16 } },
  { id: 'hungry', name: 'Hungry', s: { dmg: .38, drain: .55 } },
  { id: 'frail', name: 'Frail', s: { crit: .22, hp: -32 } },
  { id: 'reckless', name: 'Reckless', s: { cd: -.3, arm: -.1 } },
  { id: 'greedy', name: 'Greedy', s: { gold: .8, hp: -24 } },
  { id: 'bound', name: 'Bound', s: { dmg: .6, dash: .5 } }
];
const SETS = [
  { id: 'barrow', name: "The Barrow King's", s2: { hp: 38, arm: .06 } },
  { id: 'ember', name: 'Emberbound', s2: { dmg: .17, crit: .05 } },
  { id: 'quick', name: 'The Quickened', s2: { spd: .11, cd: -.1 } }
];
const BASE_STAT = { weapon: 'dmg', armour: 'arm', trinket: 'crit' };""")

# --- roll them ------------------------------------------------------------
edit(L, """  const base = BASES[slot][rint(0, BASES[slot].length - 1)];
  const name = (pre.length ? pre[0].name + ' ' : '') + base + (suf.length ? ' ' + suf[0].name : '');
  return { slot, base, rar: rar.k, col: rar.col, name, s, ilvl: G.level };""",
     """  const base = BASES[slot][rint(0, BASES[slot].length - 1)];
  if (Math.random() < .16) {
    const c = CURSE[rint(0, CURSE.length - 1)];
    for (const k in c.s) s[k] = +(((s[k] || 0) + c.s[k]).toFixed(3));
    if (s.hp) s.hp = Math.round(s.hp);
    return { slot, base, rar: 'cursed', col: '#e0556b', curse: c.name, name: c.name + ' ' + base + (suf.length ? ' ' + suf[0].name : ''), s, ilvl: G.level };
  }
  let set = null;
  if (Math.random() < .22) set = SETS[rint(0, SETS.length - 1)];
  const name = (pre.length ? pre[0].name + ' ' : '') + base + (suf.length ? ' ' + suf[0].name : '');
  return { slot, base, rar: rar.k, col: rar.col, name, s, ilvl: G.level, set: set ? set.id : null, setName: set ? set.name : null };""")

# --- one place that knows how a stat folds into the sheet -----------------
edit(L, """function recalc(P) {
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
}""",
     """function addStat(g, k, v) {
  if (!v) return;
  if (k === 'dmg') g.dmg *= 1 + v;
  else if (k === 'cd') g.cd *= 1 + v;
  else if (k === 'crit') g.crit += v;
  else if (k === 'spd') g.spd *= 1 + v;
  else if (k === 'hp') g.hp += v;
  else if (k === 'arm') g.arm *= 1 - v;
  else if (k === 'leech') g.leech += v;
  else if (k === 'thorns') g.thorns += v;
  else if (k === 'gold') g.gold += v;
  else if (k === 'sp') g.sp += v;
  else if (k === 'dash') g.dash *= 1 + v;
  else if (k === 'drain') g.drain += v;
}
function recalc(P) {
  const g = { dmg: 1, cd: 1, crit: 0, spd: 1, hp: 0, arm: 1, leech: 0, thorns: 0, gold: 0, sp: 0, dash: 1, drain: 0, elem: null, elemDmg: 0 };
  const setN = {};
  for (const slot of SLOTS) {
    const it = P.gear[slot]; if (!it) continue;
    for (const k in it.s) if (k !== 'elem' && k !== 'elemDmg') addStat(g, k, it.s[k]);
    if (it.s.elem && slot === 'weapon') { g.elem = it.s.elem; g.elemDmg = it.s.elemDmg || .4; }
    if (it.set) setN[it.set] = (setN[it.set] || 0) + 1;
  }
  P.sets = [];
  for (const id in setN) {
    if (setN[id] < 2) continue;
    const S = SETS.find(x => x.id === id); if (!S) continue;
    const mult = setN[id] >= 3 ? 2 : 1;
    P.sets.push({ name: S.name, n: setN[id] });
    for (const k in S.s2) addStat(g, k, S.s2[k] * mult);
  }
  P.g = g;
  P.dmgMul = P.up.dmg * g.dmg;
  P.cdMul = Math.max(.3, P.up.cd * g.cd);
  P.spdMul = Math.max(.4, P.up.spd * g.spd);
  P.armMul = clamp(P.up.arm * g.arm, .32, 2.2);
  P.dashMul = clamp(P.up.dash * g.dash, .35, 2.4);
  P.crit = Math.min(.75, P.up.crit + g.crit);
  P.drainMul = Math.max(.3, 1 + g.drain + (P.perkDrain || 0));
  const nm = Math.max(40, Math.round(P.cls.hp + P.up.hp + g.hp)), d = nm - P.max;
  P.max = nm; if (d > 0) P.hp += d;
  P.hp = Math.min(P.hp, P.max);
}""")

# --- the drain and the special cooldown now listen to gear ----------------
edit(L, """  P.hp -= (.8 + G.level * .2) * (G.co ? .85 : 1) * dt;""",
     """  P.hp -= (.8 + G.level * .2) * (G.co ? .85 : 1) * (P.drainMul || 1) * dt;""")

edit(L, """  const c = P.cls, dm = c.dmg * P.dmgMul, a = P.aim, cr = Math.random() < P.crit; P.spCd = SP_CD;""",
     """  const c = P.cls, dm = c.dmg * P.dmgMul, a = P.aim, cr = Math.random() < P.crit;
  P.spMax = Math.max(2.5, SP_CD - (P.g ? P.g.sp : 0)); P.spCd = P.spMax;""")

edit(L, """  h.sp.style.width = (100 - clamp(P.spCd / SP_CD, 0, 1) * 100) + '%';""",
     """  h.sp.style.width = (100 - clamp(P.spCd / (P.spMax || SP_CD), 0, 1) * 100) + '%';""")

# --- and the card explains the bargain ------------------------------------
edit(L, """  gold: v => '+' + Math.round(v * 100) + '% gold',""",
     """  gold: v => '+' + Math.round(v * 100) + '% gold',
  drain: v => v > 0 ? 'Your health drains ' + Math.round(v * 100) + '% faster' : 'Your health drains ' + Math.round(-v * 100) + '% slower',""")

edit(L, """function itemLines(it) {
  const out = [];
  for (const k of ['dmg', 'arm', 'hp', 'crit', 'spd', 'cd', 'dash', 'sp', 'leech', 'thorns', 'gold', 'elem']) {
    if (it.s[k] === undefined || it.s[k] === 0) continue;
    const t = STAT_LABEL[k] && STAT_LABEL[k](it.s[k]); if (t) out.push(t);
  }
  return out;
}""",
     """function itemLines(it) {
  const out = [];
  for (const k of ['dmg', 'arm', 'hp', 'crit', 'spd', 'cd', 'dash', 'sp', 'leech', 'thorns', 'gold', 'drain', 'elem']) {
    if (it.s[k] === undefined || it.s[k] === 0) continue;
    const t = STAT_LABEL[k] && STAT_LABEL[k](it.s[k]); if (t) out.push(t);
  }
  if (it.setName) out.push('Set: ' + it.setName + ' (2 pieces grant more)');
  return out;
}""")

run()
