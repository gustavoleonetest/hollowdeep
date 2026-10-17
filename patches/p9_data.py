from patch import edit, run

L = 'part_logic.js'

# --- two Gauntlet monsters: the thief who robs you, and Death itself --------
edit(L, """  bloat: { hp: 44, spd: .82, r: 13, dmg: 13, col: '#8fbf5a', gold: .85 },""",
     """  bloat: { hp: 44, spd: .82, r: 13, dmg: 13, col: '#8fbf5a', gold: .85 },
  thief: { hp: 46, spd: 2.5, r: 10, dmg: 0, col: '#c9a24a', gold: 0 },
  reaper: { hp: 99999, spd: .62, r: 15, dmg: 0, col: '#dfe4ef', gold: 0 },""")

# --- run state for gear, levels, bombs, the announcer ----------------------
edit(L, """clsKey: 'bulwark', clsKeys: ['bulwark'], players: [], keys: 0, gold: 0, co: false, hazards: [], combo: 0, comboT: 0, comboBest: 0 };""",
     """clsKey: 'bulwark', clsKeys: ['bulwark'], players: [], keys: 0, gold: 0, co: false, hazards: [], combo: 0, comboT: 0, comboBest: 0,
  bombs: 0, bolts: [], voice: null, flash: 0, offerQ: [], drops: 0 };""")

# --- the announcer. Gauntlet's narrator is half of why it is remembered ----
edit(L, """/* ---------- world helpers ---------- */""",
     """/* ---------- the announcer ----------
   Gauntlet's narrator is half of what people remember, so the callouts are
   spoken where the browser allows it and always shown on screen. */
let voiceOn = true;
function speak(txt) {
  if (!voiceOn || muted || typeof speechSynthesis === 'undefined') return;
  try {
    const u = new SpeechSynthesisUtterance(txt);
    u.rate = .95; u.pitch = .55; u.volume = .85;
    speechSynthesis.cancel(); speechSynthesis.speak(u);
  } catch (e) {}
}
function announce(txt, col, quiet) {
  G.voice = { txt, col: col || '#ebe4d2', t: 2.9 };
  if (!quiet) speak(txt);
}
/* one line per subject at a time, so the narrator does not stutter */
function announceOnce(key, gap, txt, col) {
  G.vlast = G.vlast || {};
  if (G.vlast[key] && clock - G.vlast[key] < gap) return;
  G.vlast[key] = clock; announce(txt, col);
}

/* ---------- gear: rolled drops in the Diablo mould ----------
   A drop is a base type plus up to three affixes; the affixes supply the name
   and every stat, so "Savage Gravefang of the Wolf" reads as what it does. */
const SLOTS = ['weapon', 'armour', 'trinket'];
const RARITY = {
  magic: { k: 'magic', name: 'Magic', col: '#6fa8ff', aff: 1 },
  rare: { k: 'rare', name: 'Rare', col: '#ffd24a', aff: 2 },
  fabled: { k: 'fabled', name: 'Fabled', col: '#e08a3c', aff: 3 }
};
const BASES = {
  weapon: ['Hollowblade', 'Crypt Cleaver', 'Gravefang', 'Ashen Rod', 'Pale Talon', 'Widow Spike'],
  armour: ['Shroud', 'Bone Plate', 'Gravemail', 'Hide Wrap', 'Dust Vestment', 'Barrow Coat'],
  trinket: ['Signet', 'Charm', 'Sigil', 'Idol', 'Knucklebone', 'Lantern Tooth']
};
/* s: dmg/spd are multipliers, arm is damage shaved off, hp is flat,
   cd and dash are cooldown scalers (negative is faster) */
const PREFIX = [
  { id: 'savage', name: 'Savage', s: { dmg: .16 } },
  { id: 'brutal', name: 'Brutal', s: { dmg: .27, cd: .07 } },
  { id: 'keen', name: 'Keen', s: { crit: .06 } },
  { id: 'swift', name: 'Swift', s: { cd: -.09 } },
  { id: 'hardy', name: 'Hardy', s: { hp: 22 } },
  { id: 'warded', name: 'Warded', s: { arm: .07 } },
  { id: 'fleet', name: 'Fleet', s: { spd: .07 } },
  { id: 'grim', name: 'Grim', s: { dmg: .11, crit: .03 } },
  { id: 'ember', name: 'Ember', w: 'weapon', s: { elem: 'fire', elemDmg: .5 } },
  { id: 'rime', name: 'Rime', w: 'weapon', s: { elem: 'cold', elemDmg: .35 } },
  { id: 'storm', name: 'Storm', w: 'weapon', s: { elem: 'shock', elemDmg: .45 } },
  { id: 'fetid', name: 'Fetid', w: 'weapon', s: { elem: 'poison', elemDmg: .4 } }
];
const SUFFIX = [
  { id: 'wolf', name: 'of the Wolf', s: { spd: .08 } },
  { id: 'bear', name: 'of the Bear', s: { hp: 28 } },
  { id: 'owl', name: 'of the Owl', s: { sp: 1.4 } },
  { id: 'viper', name: 'of the Viper', s: { cd: -.11 } },
  { id: 'leech', name: 'of Leeching', s: { leech: .05 } },
  { id: 'thorns', name: 'of Thorns', s: { thorns: .4 } },
  { id: 'fortune', name: 'of Fortune', s: { gold: .3 } },
  { id: 'ruin', name: 'of Ruin', s: { dmg: .2 } },
  { id: 'fox', name: 'of the Fox', s: { dash: -.18 } },
  { id: 'warding', name: 'of Warding', s: { arm: .08 } }
];
const BASE_STAT = { weapon: 'dmg', armour: 'arm', trinket: 'crit' };
function rollRarity(bonus) {
  const r = Math.random() * 100 - (bonus || 0) - G.level * 1.1;
  return r < 9 ? RARITY.fabled : r < 33 ? RARITY.rare : RARITY.magic;
}
function rollItem(slot, rar) {
  slot = slot || SLOTS[rint(0, 2)];
  rar = rar || rollRarity(0);
  const s = {}, lv = 1 + G.level * .06;
  /* the base type carries the slot's core stat */
  if (slot === 'weapon') s.dmg = +(rnd(.10, .20) * lv).toFixed(3);
  else if (slot === 'armour') { s.arm = +(rnd(.05, .10) * lv).toFixed(3); s.hp = Math.round(rnd(8, 18) * lv); }
  else s.crit = +(rnd(.02, .045) * lv).toFixed(3);
  const fits = a => !a.w || a.w === slot;
  const pre = [], suf = [];
  const pool = { p: PREFIX.filter(fits).slice(), s: SUFFIX.filter(fits).slice() };
  for (let i = 0; i < rar.aff; i++) {
    const wantPre = pre.length === 0 || (suf.length > 0 && Math.random() < .5);
    const from = wantPre && pool.p.length ? pool.p : pool.s.length ? pool.s : pool.p;
    if (!from.length) break;
    const a = from.splice(rint(0, from.length - 1), 1)[0];
    (from === pool.p ? pre : suf).push(a);
    for (const k in a.s) {
      const v = a.s[k];
      if (typeof v !== 'number') s[k] = v;
      else s[k] = +((s[k] || 0) + v * rnd(.85, 1.2) * (k === 'hp' ? lv : 1)).toFixed(3);
    }
    if (s.hp) s.hp = Math.round(s.hp);
  }
  const base = BASES[slot][rint(0, BASES[slot].length - 1)];
  const name = (pre.length ? pre[0].name + ' ' : '') + base + (suf.length ? ' ' + suf[0].name : '');
  return { slot, base, rar: rar.k, col: rar.col, name, s, ilvl: G.level };
}
/* a short, readable stat line for the compare card */
const STAT_LABEL = {
  dmg: v => '+' + Math.round(v * 100) + '% damage',
  arm: v => '-' + Math.round(v * 100) + '% damage taken',
  hp: v => '+' + Math.round(v) + ' max health',
  crit: v => '+' + Math.round(v * 100) + '% critical chance',
  spd: v => '+' + Math.round(v * 100) + '% move speed',
  cd: v => (v < 0 ? 'Attacks ' + Math.round(-v * 100) + '% faster' : 'Attacks ' + Math.round(v * 100) + '% slower'),
  dash: v => 'Dash recharges ' + Math.round(-v * 100) + '% faster',
  sp: v => 'Special recharges ' + v.toFixed(1) + 's sooner',
  leech: v => 'Heal ' + Math.round(v * 100) + '% of damage dealt',
  thorns: v => 'Return ' + Math.round(v * 100) + '% of melee damage',
  gold: v => '+' + Math.round(v * 100) + '% gold',
  elem: v => ({ fire: 'Burns what it strikes', cold: 'Chills what it strikes', shock: 'Arcs to nearby foes', poison: 'Poisons what it strikes' })[v],
  elemDmg: () => null
};
function itemLines(it) {
  const out = [];
  for (const k of ['dmg', 'arm', 'hp', 'crit', 'spd', 'cd', 'dash', 'sp', 'leech', 'thorns', 'gold', 'elem']) {
    if (it.s[k] === undefined || it.s[k] === 0) continue;
    const t = STAT_LABEL[k] && STAT_LABEL[k](it.s[k]); if (t) out.push(t);
  }
  return out;
}

/* ---------- elite modifiers, after Diablo's champion packs ---------- */
const EAFF = [
  { id: 'fast', name: 'Extra Fast', col: '#8fd3ff' },
  { id: 'fiery', name: 'Fire Enchanted', col: '#ff6a3d' },
  { id: 'frozen', name: 'Cold Touched', col: '#8fd3ff' },
  { id: 'vamp', name: 'Vampiric', col: '#d9534f' },
  { id: 'spiny', name: 'Spiny', col: '#9bd16a' },
  { id: 'warded', name: 'Shielded', col: '#ffd24a' }
];

/* ---------- world helpers ---------- */""")

run()
