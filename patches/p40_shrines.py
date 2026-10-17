from patch import edit, run

L = 'part_logic.js'

# --- the data -------------------------------------------------------------
edit(L, """/* ---------- boons ----------""",
     """/* ---------- fonts ----------
   A pact is the one bargain in the dungeon that costs you something. Every
   figure below goes through the same stat machinery the affixes use, so the
   clamps in recalc hold them exactly as they hold a cursed trinket. */
const PACTS = [
  { id: 'embers', name: 'Pact of Embers', col: '#ff6a4d',
    good: 'Your blows land far harder.', bad: 'The deep drinks you half again as fast.',
    s: { dmg: .4, drain: .5 } },
  { id: 'stone', name: 'Pact of Stone', col: '#98a0b3',
    good: 'You take a quarter less harm.', bad: 'You move as though waist deep.',
    s: { arm: .25, spd: -.16 } },
  { id: 'hare', name: 'Pact of the Hare', col: '#8fd3ff',
    good: 'You move and strike markedly faster.', bad: 'You are a good deal easier to kill.',
    s: { spd: .2, cd: -.16, hp: -42 } },
  { id: 'greed', name: 'Pact of Greed', col: '#f0a23c',
    good: 'The dead give up far more gold.', bad: 'Riches make you careless of your own skin.',
    s: { gold: 1, arm: -.22 } },
  { id: 'blood', name: 'Pact of Blood', col: '#d9534f',
    good: 'What you wound, feeds you.', bad: 'The drain never once relents.',
    s: { leech: .07, drain: .35 } },
  { id: 'edge', name: 'Pact of the Edge', col: '#fff1b8',
    good: 'Your strikes bite critically far more often.', bad: 'But they come slow and heavy.',
    s: { crit: .24, cd: .22 } }
];
/* fonts that ask nothing, so a lit altar is not always a trap */
const BLESSINGS = [
  { id: 'mend', name: 'Mending Font', col: '#7fd1c7', good: 'Your wounds close, and the fallen rise.' },
  { id: 'ward', name: 'Warding Font', col: '#9bd16a', good: 'A ward that soaks what comes next.' },
  { id: 'hoard', name: 'Gilded Font', col: '#f0a23c', good: 'A scattering of gold for the taking.' }
];
function rollShrine(depth) {
  const r = Math.random();
  /* the deeper you are, the likelier the altar wants something back */
  const pactChance = Math.min(.62, .3 + depth * .03);
  if (r < .17) return { kind: 'mystery', pact: Math.random() < pactChance + .1 ? PACTS[rint(0, PACTS.length - 1)] : BLESSINGS[rint(0, BLESSINGS.length - 1)] };
  if (r < .17 + pactChance) return { kind: 'pact', pact: PACTS[rint(0, PACTS.length - 1)] };
  return { kind: 'blessing', pact: BLESSINGS[rint(0, BLESSINGS.length - 1)] };
}
const isPact = (p) => PACTS.indexOf(p) >= 0;
const shrineCol = (sh) => sh.kind === 'mystery' ? '#b98cff' : sh.pact.col;

/* ---------- boons ----------""")

# --- the player carries them ----------------------------------------------
edit(L, """      xp: 0, plvl: 1, buys: {}, boons: {} };""",
     """      xp: 0, plvl: 1, buys: {}, boons: {}, pacts: [] };""")

# --- pact stats ride the same pipeline as gear ----------------------------
edit(L, """  P.sets = [];
  for (const id in setN) {""",
     """  for (const p of (P.pacts || [])) for (const k in p.s) addStat(g, k, p.s[k]);
  P.sets = [];
  for (const id in setN) {""")

# --- an altar or two per depth --------------------------------------------
edit(L, """  const bc = openAt((last.x + 1.5) * T, (last.y + 1.5) * T) ? { x: (last.x + 1.5) * T, y: (last.y + 1.5) * T } : roomPoint(last);""",
     """  if (mids.length) {
    for (let k = 0; k < (G.level >= 5 && mids.length > 3 ? 2 : 1); k++) {
      const p = roomPoint(mids[rint(0, mids.length - 1)]);
      const sh = rollShrine(G.level);
      G.items.push({ kind: 'shrine', x: p.x, y: p.y, t: Math.random() * 6, sh, cool: 0 });
    }
  }
  const bc = openAt((last.x + 1.5) * T, (last.y + 1.5) * T) ? { x: (last.x + 1.5) * T, y: (last.y + 1.5) * T } : roomPoint(last);""")

# --- stepping up to one puts the choice in front of you -------------------
edit(L, """    if (it.kind === 'chest') { if (d < 26) { G.items.splice(i, 1); openChest(P, it); return; } continue; }""",
     """    if (it.kind === 'chest') { if (d < 26) { G.items.splice(i, 1); openChest(P, it); return; } continue; }
    if (it.kind === 'shrine') {
      /* refusing leaves the font standing, so brushing past one costs nothing */
      it.cool = Math.max(0, (it.cool || 0) - dt);
      if (d < 30 && it.cool <= 0 && !G.offer && !G.offerQ.length) { queueOffer({ kind: 'pact', P, shrine: it }); return; }
      continue;
    }""")

# --- taking it ------------------------------------------------------------
edit(L, """  else { const u = o.opts[i]; applyUp(o.P, u.id, u.m); }
  closeOffer();""",
     """  else if (o.kind === 'pact') {
    const P = o.P, it = o.shrine, sh = it.sh;
    if (i !== 0) { it.cool = 2.5; text(P.x, P.y - 20, 'Left unlit', '#98a0b3'); closeOffer(); return; }
    const idx = G.items.indexOf(it); if (idx >= 0) G.items.splice(idx, 1);
    const p = sh.pact, col = p.col;
    if (p.s) { P.pacts.push(p); recalc(P); }
    else if (p.id === 'mend') { P.hp = P.max; for (const q of G.players) if (q.down) revive(q); }
    else if (p.id === 'ward') P.shield = Math.max(P.shield, 9);
    else if (p.id === 'hoard') { G.gold += 60 + G.level * 22; coinSpray(P.x, P.y, 18); }
    text(P.x, P.y - 24, p.name + '!', col, 15); sfx('level');
    announceOnce('pact' + P.idx, .5, P.cls.name + ' takes the ' + p.name, col);
    G.fxs.push({ kind: 'shock', x: P.x, y: P.y, t: 0, r: 160, c1: '255,250,225', c2: '200,180,255' });
    burst(P.x, P.y, col, 30, 200, 1.4, 'spark');
    G.shake = Math.max(G.shake, .3);
  }
  else { const u = o.opts[i]; applyUp(o.P, u.id, u.m); }
  closeOffer();""")

# --- the card -------------------------------------------------------------
edit(L, """  } else if (o.kind === 'boon') {""",
     """  } else if (o.kind === 'pact') {
    const sh = o.shrine.sh, p = sh.pact, mys = sh.kind === 'mystery', col = shrineCol(sh);
    $('lootT').textContent = (G.co ? 'P' + (P.idx + 1) + ': ' : '') + (mys ? 'An altar you cannot read' : isPact(p) ? 'The altar wants something back' : 'A font burns clean');
    $('lootS').textContent = sheetLine(P);
    $('lootHint').textContent = 'Press 1 to take it, 2 to walk away. Walking away leaves the font standing.';
    const take = document.createElement('button'); take.type = 'button'; take.className = 'card'; take.style.setProperty('--c', col);
    const r1 = document.createElement('span'); r1.className = 'itemrar'; r1.style.color = col;
    r1.textContent = mys ? 'Unknown' : isPact(p) ? 'Pact' : 'Blessing'; take.appendChild(r1);
    const n1 = document.createElement('span'); n1.className = 'nm'; n1.textContent = '1 \\u00b7 ' + (mys ? 'Drink anyway' : p.name); take.appendChild(n1);
    if (mys) {
      const d1 = document.createElement('span'); d1.className = 'bl';
      d1.textContent = 'The carving has worn away. It may bless you, or it may want paying.';
      take.appendChild(d1);
    } else {
      const d1 = document.createElement('span'); d1.className = 'bl'; d1.textContent = p.good; take.appendChild(d1);
      if (p.bad) { const d2 = document.createElement('span'); d2.className = 'bl'; d2.style.color = '#e0556b'; d2.textContent = p.bad; take.appendChild(d2); }
    }
    take.addEventListener('click', () => chooseUp(0)); wrap.appendChild(take);
    const skip = document.createElement('button'); skip.type = 'button'; skip.className = 'card'; skip.style.setProperty('--c', '#98a0b3');
    const r2 = document.createElement('span'); r2.className = 'itemrar'; r2.style.color = '#98a0b3'; r2.textContent = 'Leave'; skip.appendChild(r2);
    const n2 = document.createElement('span'); n2.className = 'nm'; n2.textContent = '2 \\u00b7 Walk away'; skip.appendChild(n2);
    const d3 = document.createElement('span'); d3.className = 'bl'; d3.textContent = 'The font stays lit. You may come back to it.'; skip.appendChild(d3);
    skip.addEventListener('click', () => chooseUp(1)); wrap.appendChild(skip);
  } else if (o.kind === 'boon') {""")

edit(L, """  if (o.kind === 'gear' ? (i !== 0 && i !== 1) : !o.opts[i]) return;
  if (o.kind === 'boon' && !o.opts[i]) return;""",
     """  if (o.kind === 'pact') { if (i !== 0 && i !== 1) return; }
  else if (o.kind === 'gear' ? (i !== 0 && i !== 1) : !o.opts[i]) return;
  if (o.kind === 'boon' && !o.opts[i]) return;""")

# --- an altar you can use reads differently from one that is scenery ------
edit(L, """function drawItem(it) {
  if (it.kind === 'gear') return drawGear(it);""",
     """function drawItem(it) {
  if (it.kind === 'gear') return drawGear(it);
  if (it.kind === 'shrine') return drawShrine(it);""")

edit(L, """function drawGear(it) {""",
     """function drawShrine(it) {
  const sh = it.sh, col = shrineCol(sh), pu = .5 + .5 * Math.sin(clock * 1.7 + it.t);
  const mys = sh.kind === 'mystery', want = sh.kind === 'pact';
  /* a column of light so a live altar is never mistaken for the scenery */
  const h = 78;
  const g = ctx.createLinearGradient(it.x, it.y - h, it.x, it.y + 8);
  g.addColorStop(0, hexA(col, 0)); g.addColorStop(.7, hexA(col, .1 + pu * .09)); g.addColorStop(1, hexA(col, .3 + pu * .12));
  ctx.fillStyle = g; ctx.fillRect(it.x - 15, it.y - h, 30, h + 8);
  glow(it.x, it.y - 2, 40 + pu * 10, col, .34 + pu * .18);
  shadow(it.x, it.y + 10, 13, 5, .34);
  if (!sprProp('altar', it.x, it.y + 10, 1.25, null, .7)) {
    ctx.fillStyle = '#4a4740'; ctx.fillRect(it.x - 12, it.y - 10, 24, 20);
    ctx.fillStyle = hexA(col, .7); ctx.fillRect(it.x - 9, it.y - 14, 18, 5);
  }
  /* motes rise from a gift, and circle a bargain like flies */
  const n = mys ? 5 : 4;
  for (let i = 0; i < n; i++) {
    const a = clock * (want ? -1.5 : .9) + i * (TAU / n);
    const rr = want ? 13 + Math.abs(Math.sin(clock * 1.9 + i)) * 7 : 11;
    const ry = want ? Math.sin(a) * rr * .4 : -(((clock * 26 + i * 37) % 54));
    ctx.fillStyle = hexA(col, want ? .9 : .5 + pu * .4);
    ctx.fillRect(it.x + Math.cos(a) * rr, it.y - 8 + ry, 2, mys ? 3 : 2);
  }
  if (mys) {
    ctx.fillStyle = hexA(col, .55 + pu * .35); ctx.font = 'bold 15px ui-monospace, monospace';
    ctx.textAlign = 'center'; ctx.fillText('?', it.x, it.y - 30 - pu * 3); ctx.textAlign = 'left';
  }
}
function drawGear(it) {""")

# --- what you are carrying shows up where everything else does ------------
edit(L, """    const learned = (BOONS[P.cls.key] || []).filter(b => bn(P, b.id));""",
     """    if ((P.pacts || []).length) {
      const pl = document.createElement('div'); pl.className = 'heroline'; pl.style.color = '#e0556b';
      pl.textContent = 'Pacts: ' + P.pacts.map(p => p.name).join(' \\u00b7 ');
      hl.appendChild(pl);
    }
    const learned = (BOONS[P.cls.key] || []).filter(b => bn(P, b.id));""")

edit(L, """  const allBoons = [];""",
     """  const allPacts = [];
  for (const p of G.players) for (const q of (p.pacts || [])) allPacts.push(q.name);
  if (allPacts.length) rows.push(['Pacts taken', allPacts.join(', ')]);
  const allBoons = [];""")

run()
