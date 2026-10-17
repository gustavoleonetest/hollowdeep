from patch import edit, run

L = 'part_logic.js'

# --- dropping gear ---------------------------------------------------------
edit(L, """/* ---------- chests and upgrades ---------- */""",
     """function dropGear(x, y, bonus) {
  const it = rollItem(null, rollRarity(bonus || 0));
  G.items.push({ kind: 'gear', x, y, t: 0, item: it });
  G.drops++;
  burstDir(x, y, -Math.PI / 2, it.col, 12, 210, 1.1, 'spark', .8);
  sfx('coin');
  return it;
}

/* ---------- chests and upgrades ---------- */""")

# --- who drops what --------------------------------------------------------
edit(L, """  if (e.type === 'thief' && e.loot > 0) {""",
     """  if (e.boss) { dropGear(e.x - 34, e.y + 8, 32); dropGear(e.x + 34, e.y + 8, 32); }
  else if (e.elite) dropGear(e.x, e.y, 14);
  else if (e.type !== 'thief' && e.type !== 'reaper' && Math.random() < .022) dropGear(e.x, e.y, 0);
  if (e.type === 'thief' && e.loot > 0) {""")

# --- picking things up -----------------------------------------------------
edit(L, """    if (it.kind === 'chest') { if (d < 26) { G.items.splice(i, 1); openChest(P, it); return; } continue; }""",
     """    if (it.kind === 'chest') { if (d < 26) { G.items.splice(i, 1); openChest(P, it); return; } continue; }
    if (it.kind === 'gear') {
      if (d < 21) {
        G.items.splice(i, 1);
        const cur = P.gear[it.item.slot];
        if (!cur) equip(P, it.item);
        else queueOffer({ kind: 'gear', P, item: it.item, cur });
        return;
      }
      continue;
    }""")

edit(L, """      if (it.kind === 'gold') { G.gold += 10; G.score += 10; text(P.x, P.y - 16, '+10', '#f0a23c'); sfx('coin'); burst(P.x, P.y - 6, '#ffe08a', 4, 90, .5, 'spark'); }
      else if (it.kind === 'gem') { G.gold += 50; G.score += 60; text(P.x, P.y - 16, '+50', '#8fd3ff'); sfx('coin'); burst(P.x, P.y - 6, '#8fd3ff', 10, 120, .7, 'spark'); }
      else if (it.kind === 'key') { G.keys++; text(P.x, P.y - 16, 'Key', '#f0a23c'); sfx('door'); }
      else if (it.kind === 'food') { if (P.hp >= P.max) continue; P.hp = Math.min(P.max, P.hp + 35); text(P.x, P.y - 16, '+35 HP', '#9bd16a'); sfx('coin'); P.drink = .75; burst(P.x, P.y, '#9bd16a', 12, 70, 1.3, 'ember'); }""",
     """      const gmul = 1 + (P.g ? P.g.gold : 0);
      if (it.kind === 'gold') { const v = Math.round((it.v || 10) * gmul); G.gold += v; G.score += v; text(P.x, P.y - 16, '+' + v, '#f0a23c'); sfx('coin'); burst(P.x, P.y - 6, '#ffe08a', 4, 90, .5, 'spark'); }
      else if (it.kind === 'gem') { const v = Math.round(50 * gmul); G.gold += v; G.score += 60; text(P.x, P.y - 16, '+' + v, '#8fd3ff'); sfx('coin'); burst(P.x, P.y - 6, '#8fd3ff', 10, 120, .7, 'spark'); }
      else if (it.kind === 'key') { G.keys++; text(P.x, P.y - 16, 'Key', '#f0a23c'); sfx('door'); announceOnce('key', 4, 'A key is found', '#f0a23c'); }
      else if (it.kind === 'bomb') { G.bombs++; text(P.x, P.y - 16, 'Potion', '#b98cff'); sfx('coin'); burst(P.x, P.y, '#b98cff', 14, 110, 1, 'spark'); }
      else if (it.kind === 'food') { if (P.hp >= P.max - .5) continue; const h = 36 + G.level * 3; P.hp = Math.min(P.max, P.hp + h); text(P.x, P.y - 16, '+' + h + ' HP', '#9bd16a'); sfx('coin'); P.drink = .75; burst(P.x, P.y, '#9bd16a', 12, 70, 1.3, 'ember'); }""")

# --- "Elf shot the food!" --------------------------------------------------
edit(L, """    if (dead) G.shots.splice(i, 1);
  }
  for (let i = G.eshots.length - 1; i >= 0; i--) {""",
     """    for (let fi = G.items.length - 1; fi >= 0; fi--) {
      const it = G.items[fi];
      if (it.kind !== 'food' || Math.hypot(it.x - s.x, it.y - s.y) > 13 + s.r) continue;
      G.items.splice(fi, 1);
      burst(it.x, it.y, '#d9534f', 16, 140, 1); burst(it.x, it.y, '#9bd16a', 7, 100, .8, 'spark');
      announceOnce('shotfood', 2.2, (s.own ? s.own.cls.name : 'Someone') + ' shot the food!', '#d9534f');
      sfx('hurt'); break;
    }
    if (dead) G.shots.splice(i, 1);
  }
  for (let i = G.eshots.length - 1; i >= 0; i--) {""")

# --- more food, because the drain never stops; plus potions ----------------
edit(L, """    if (Math.random() < .5) { const p = roomPoint(r); G.items.push({ kind: 'food', x: p.x, y: p.y, t: 0 }); }""",
     """    for (let f = Math.random() < .72 ? 1 : 0, extra = Math.random() < .3 ? 1 : 0; f + extra > 0; f ? f-- : extra--) { const p = roomPoint(r); G.items.push({ kind: 'food', x: p.x, y: p.y, t: 0 }); }""")

# --- thief, Death and potions join the level build -------------------------
edit(L, """  makeProps(); makeHazards();
  G.flowT = 0;""",
     """  makeProps(); makeHazards();
  const mid = () => G.rooms[rint(1, Math.max(1, G.rooms.length - 2))];
  for (let b = (G.level === 1 ? 1 : 0) + (Math.random() < .55 ? 1 : 0); b > 0; b--) { const p = roomPoint(mid()); G.items.push({ kind: 'bomb', x: p.x, y: p.y, t: Math.random() * 6 }); }
  if (G.level >= 3 && Math.random() < .5) { const p = roomPoint(mid()); spawnFoe('thief', p.x, p.y, false); }
  if (G.level >= 6 && Math.random() < .38) {
    const p = roomPoint(mid()); spawnFoe('reaper', p.x, p.y, false);
    G.enemies[G.enemies.length - 1].alert = true;
  }
  G.bolts = []; G.voice = null; G.flash = 0; G.offer = null; G.offerQ = [];
  G.flowT = 0;""")

# --- the new monsters borrow rigs that already read right -------------------
edit(L, """  bloat: { key: 'foe_puglin', fy: 9, bar: -50, sc: 1.8 }
};""",
     """  bloat: { key: 'foe_puglin', fy: 9, bar: -50, sc: 1.8 },
  thief: { key: 'npc_keeper', fy: 8, bar: -44, sc: 1.3 },
  reaper: { key: 'foe_ghost', fy: 10, bar: -64, sc: 2.2 }
};""")

edit(L, """  if (useSpr) drawFoeSpr(e, mv); else ({ gloam: drawGloam, wisp: drawWisp, bonewalker: drawBone, brute: drawBrute, hound: drawHound, bloat: drawGloam, warden: drawWarden })[e.type](e, mv);""",
     """  if (useSpr) drawFoeSpr(e, mv); else ({ gloam: drawGloam, wisp: drawWisp, bonewalker: drawBone, brute: drawBrute, hound: drawHound, bloat: drawGloam, thief: drawGloam, reaper: drawWisp, warden: drawWarden })[e.type](e, mv);""")

# --- a fresh run clears carried potions and gear ---------------------------
edit(L, """  G.player = G.players[0]; G.gold = 0; G.keys = 0; G.combo = 0; G.comboT = 0; G.comboBest = 0;""",
     """  G.player = G.players[0]; G.gold = 0; G.keys = 0; G.combo = 0; G.comboT = 0; G.comboBest = 0;
  G.bombs = 1; G.drops = 0; G.bolts = []; G.voice = null; G.flash = 0; G.offer = null; G.offerQ = [];""")

run()
