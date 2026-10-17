from patch import edit, run

L = 'part_logic.js'

# --- the data -------------------------------------------------------------
edit(L, """/* ---------- fonts ----------""",
     """/* ---------- omens ----------
   Fifteen depths that each ask the same three things of you is fifteen of the
   same depth. An omen changes what the floor wants: more of them, fewer but
   blind, no food, no clock at all. Every field below is a plain multiplier
   read either at generation or in the loop, so an omen can never put a depth
   into a state the ordinary rules cannot reach. */
const OMENS = [
  { id: 'horde', name: 'The Horde', col: '#ff8a3a',
    line: 'The door is already open. Nothing here means you to reach it.',
    foes: 1.9, nests: 1.4, gold: 1.25, freeKey: true },
  { id: 'famine', name: 'Famine', col: '#c98b5a',
    line: 'Nothing grows this deep, and nothing has been left behind.',
    food: 0, drain: 1.4, gold: 2 },
  { id: 'dark', name: 'Pitch Dark', col: '#6f7fa8',
    line: 'Your torch gutters. What lives here never needed one.',
    light: .52, foes: .7, rich: true },
  { id: 'still', name: 'Still Air', col: '#7fd1c7',
    line: 'The deep is holding its breath. It is not hungry, only crowded.',
    drain: 0, foes: 1.8, food: 0 },
  { id: 'gilded', name: 'The Gilded Seam', col: '#f0a23c',
    line: 'Gold in the walls, and something fat has been feeding on the miners.',
    gold: 2.6, chests: 2, elite: true, foes: .75 },
  { id: 'warren', name: 'The Warren', col: '#9a6bd6',
    line: 'The crypts here have had time. Far too much of it.',
    nests: 2.4, foes: .55, gold: 1.3 }
];
function rollOmen(depth) {
  /* the first depths stay plain so the ordinary rules are learned first, and
     a boss floor already has its own shape */
  if (depth < 3 || isBossLvl(depth)) return null;
  if (Math.random() > Math.min(.46, .22 + depth * .022)) return null;
  return OMENS[rint(0, OMENS.length - 1)];
}
const om = (k, dflt) => (G.omen && G.omen[k] !== undefined) ? G.omen[k] : dflt;

/* ---------- fonts ----------""")

# --- chosen as the depth is built -----------------------------------------
edit(L, """  G.keys = 0;
  G.players.forEach((P, i) => {""",
     """  G.omen = rollOmen(G.level);
  G.keys = om('freeKey', false) ? 1 : 0;
  G.players.forEach((P, i) => {""")

# --- how many of them, and how many crypts --------------------------------
edit(L, """    const nn = r.quiet ? 0 : Math.min(3, rint(1, 1 + Math.floor(G.level / 2)) + (r.w * r.h > 60 ? 1 : 0) + (r.kind === 'arena' ? 1 : 0));
    for (let k = 0; k < nn; k++) { const p = roomPoint(r); G.nests.push({ x: p.x, y: p.y, r: 15, hp: 70 + G.level * 14, max: 70 + G.level * 14, t: rnd(.5, 2.5), flash: 0 }); }
    for (let k = rint(1, 3) + (r.kind === 'arena' ? 2 : 0); k > 0; k--) { const p = roomPoint(r); spawnFoe(pickFoe(), p.x, p.y); }""",
     """    const nn0 = r.quiet ? 0 : Math.min(3, rint(1, 1 + Math.floor(G.level / 2)) + (r.w * r.h > 60 ? 1 : 0) + (r.kind === 'arena' ? 1 : 0));
    const nn = Math.min(5, Math.round(nn0 * om('nests', 1)));
    for (let k = 0; k < nn; k++) { const p = roomPoint(r); G.nests.push({ x: p.x, y: p.y, r: 15, hp: 70 + G.level * 14, max: 70 + G.level * 14, t: rnd(.5, 2.5), flash: 0 }); }
    const fn = Math.max(0, Math.round((rint(1, 3) + (r.kind === 'arena' ? 2 : 0)) * om('foes', 1)));
    for (let k = 0; k < fn; k++) { const p = roomPoint(r); spawnFoe(pickFoe(), p.x, p.y, om('elite', false) ? true : undefined); }""")

# --- what is left lying about ---------------------------------------------
edit(L, """    for (let k = rint(2, 4); k > 0; k--) { const p = roomPoint(r); G.items.push({ kind: 'gold', x: p.x, y: p.y, t: Math.random() * 6 }); }
    for (let f = Math.random() < .72 ? 1 : 0, extra = Math.random() < .3 ? 1 : 0; f + extra > 0; f ? f-- : extra--) { const p = roomPoint(r); G.items.push({ kind: 'food', x: p.x, y: p.y, t: 0 }); }""",
     """    const gn = Math.max(0, Math.round(rint(2, 4) * om('gold', 1)));
    for (let k = 0; k < gn; k++) { const p = roomPoint(r); G.items.push({ kind: 'gold', x: p.x, y: p.y, t: Math.random() * 6 }); }
    const fdn = Math.round((Math.random() < .72 ? 1 : 0) + (Math.random() < .3 ? 1 : 0)) * om('food', 1);
    for (let f = 0; f < fdn; f++) { const p = roomPoint(r); G.items.push({ kind: 'food', x: p.x, y: p.y, t: 0 }); }""")

edit(L, """  for (let k = 0; k < (rooms.length > 8 ? 2 : 1); k++) { const p = roomPoint(mids[rint(0, mids.length - 1)]); G.items.push({ kind: 'chest', x: p.x, y: p.y, t: Math.random() * 6 }); }""",
     """  for (let k = 0; k < (rooms.length > 8 ? 2 : 1) + om('chests', 0); k++) { const p = roomPoint(mids[rint(0, mids.length - 1)]); G.items.push({ kind: 'chest', x: p.x, y: p.y, t: Math.random() * 6 }); }""")

# --- a depth that hands you the door needs no key lying in it -------------
edit(L, """  } else G.items.push({ kind: 'key', x: kp.x, y: kp.y, t: 0 });""",
     """  } else if (!om('freeKey', false)) G.items.push({ kind: 'key', x: kp.x, y: kp.y, t: 0 });""")

# --- the clock, which some omens wind on and one stops entirely ----------
edit(L, """  const dl = .8 + Math.min(G.level, 8) * .2 + Math.max(0, G.level - 8) * .07;
  P.hp -= dl * (G.co ? .85 : 1) * (P.drainMul || 1) * dt;""",
     """  const dl = (.8 + Math.min(G.level, 8) * .2 + Math.max(0, G.level - 8) * .07) * om('drain', 1);
  P.hp -= dl * (G.co ? .85 : 1) * (P.drainMul || 1) * dt;""")

# --- and the light you read the room by -----------------------------------
edit(L, """  for (const P of G.players) hole(P.x, P.y, P.down ? 90 : 300, 1);""",
     """  const lr = om('light', 1);
  for (const P of G.players) hole(P.x, P.y, (P.down ? 90 : 300) * lr, 1);""")

# --- richer rolls where the dark hides better things ----------------------
edit(L, """function rollItem(slot, rar, noCurse) {
  slot = slot || SLOTS[rint(0, 2)];
  rar = rar || rollRarity(0);""",
     """function rollItem(slot, rar, noCurse) {
  slot = slot || SLOTS[rint(0, 2)];
  rar = rar || rollRarity(om('rich', false) ? 1 : 0);""")

# --- told on arrival, and kept in front of you ----------------------------
edit(L, """  G.flowT = 0; G.banner = { txt: 'Depth ' + G.level, sub: G.zone.name + (isBossLvl(G.level) ? ' \\u00b7 a count guards the key' : ''), t: 2.8 }; G.mapVer = (G.mapVer || 0) + 1;""",
     """  G.flowT = 0;
  G.banner = { txt: 'Depth ' + G.level, sub: G.zone.name + (isBossLvl(G.level) ? ' \\u00b7 a count guards the key' : G.omen ? ' \\u00b7 ' + G.omen.name : ''), t: 2.8, omen: !!G.omen };
  if (G.omen) announceOnce('omen' + G.level, 6, G.omen.name + '. ' + G.omen.line, G.omen.col);
  G.mapVer = (G.mapVer || 0) + 1;""")

run()
