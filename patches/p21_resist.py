from patch import edit, run

L = 'part_logic.js'

# --- what each monster fears and what it shrugs off -----------------------
edit(L, """/* ---------- elite modifiers, after Diablo's champion packs ---------- */""",
     """/* ---------- elemental affinities ----------
   Every monster fears one element and shrugs off another, so the weapon you
   carry is a decision rather than a number. */
const ELEM_COL = { fire: '#ff8a3a', cold: '#8fd3ff', shock: '#c9b6ff', poison: '#9bd16a' };
const ELEM_NAME = { fire: 'fire', cold: 'cold', shock: 'lightning', poison: 'poison' };
const AFFIN = {
  gloam: { weak: 'fire', res: 'shock' },
  wisp: { weak: 'shock', res: 'cold' },
  bonewalker: { weak: 'fire', res: 'poison' },
  brute: { weak: 'poison', res: 'fire' },
  hound: { weak: 'cold', res: 'fire' },
  bloat: { weak: 'fire', res: 'poison' },
  thief: { weak: 'shock', res: null },
  reaper: { weak: null, res: 'all' },
  warden: { weak: null, res: 'cold' }
};
function elemMul(e, elem) {
  const a = AFFIN[e.type]; if (!a || !elem) return 1;
  if (a.res === 'all' || a.res === elem) return .25;
  if (a.weak === elem) return 1.9;
  return 1;
}

/* ---------- elite modifiers, after Diablo's champion packs ---------- */""")

# --- elements now land a real chunk, scaled by affinity -------------------
edit(L, """function applyElem(e, P, dmg) {
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
}""",
     """function applyElem(e, P, dmg) {
  const g = P && P.g; if (!g || !g.elem) return;
  const el = g.elem, m = elemMul(e, el), col = ELEM_COL[el] || '#ebe4d2';
  const ed = Math.max(1, dmg * g.elemDmg * m);
  const direct = Math.round(ed * .45);
  if (direct > 0) { e.hp -= direct; text(e.x + rnd(-9, 9), e.y - e.r - 11, String(direct), col, m > 1 ? 15 : 11); }
  if (!e.wkT || clock - e.wkT > 1.3) {
    e.wkT = clock;
    if (m > 1) { text(e.x, e.y - e.r - 22, 'Weak to ' + ELEM_NAME[el], col, 13); burst(e.x, e.y, col, 8, 130, .8, 'spark'); }
    else if (m < 1) text(e.x, e.y - e.r - 22, 'Resists ' + ELEM_NAME[el], '#98a0b3', 11);
  }
  if (el === 'fire') { e.burn = Math.max(e.burn || 0, 2.4 * m); e.burnDmg = Math.max(e.burnDmg || 0, Math.max(1, ed * .4)); }
  else if (el === 'cold') { e.chill = Math.max(e.chill || 0, 2 * m); burst(e.x, e.y, '#8fd3ff', 4, 80, .7, 'spark'); }
  else if (el === 'poison') { e.pois = Math.max(e.pois || 0, 3.4 * m); e.poisDmg = Math.max(e.poisDmg || 0, Math.max(1, ed * .28)); }
  else if (el === 'shock') {
    let n = 0, reach = m > 1 ? 150 : 115;
    for (const o of G.enemies.slice()) {
      if (n >= (m > 1 ? 3 : 2) || o === e || o.dead || o.hp <= 0) continue;
      if (Math.hypot(o.x - e.x, o.y - e.y) > reach) continue;
      n++; G.bolts.push({ x1: e.x, y1: e.y, x2: o.x, y2: o.y, t: 0 });
      hurtFoe(o, ed, Math.atan2(o.y - e.y, o.x - e.x), false, false, null);
    }
  }
}""")

# --- say so on the item card, so the choice is informed -------------------
edit(L, """  elem: v => ({ fire: 'Burns what it strikes', cold: 'Chills what it strikes', shock: 'Arcs to nearby foes', poison: 'Poisons what it strikes' })[v],""",
     """  elem: v => ({ fire: 'Fire damage: burns, and skeletons fear it', cold: 'Cold damage: chills, and hounds fear it', shock: 'Lightning damage: arcs, and wisps fear it', poison: 'Poison damage: rots, and brutes fear it' })[v],""")

run()
