from patch import edit, run

L = 'part_logic.js'

# --- boons change how an ability works, where upgrades only change its size --
edit(L, """/* ---------- elemental affinities ----------""",
     """/* ---------- boons ----------
   An upgrade makes the same swing bigger. A boon makes it a different swing.
   Four per delver, offered in place of a stat card every other level. */
const BOONS = {
  bulwark: [
    { id: 'cyclone', name: 'Cyclone', desc: 'Your sweep comes all the way round, striking everything about you.' },
    { id: 'wake', name: 'Burning Wake', desc: 'Whatever your sword touches catches fire.' },
    { id: 'bash', name: 'Shield Bash', desc: 'Your blows hurl foes back and leave them reeling.' },
    { id: 'riposte', name: 'Riposte', desc: 'Being struck readies your weapon at once, and the answer lands true.' }
  ],
  ember: [
    { id: 'split', name: 'Splinter', desc: 'Each burst throws three smaller bolts outward.' },
    { id: 'seek', name: 'Seeking Flame', desc: 'Your bolts bend toward whatever is nearest.' },
    { id: 'pyre', name: 'Pyre', desc: 'Your bursts leave a fire burning on the ground.' },
    { id: 'kindle', name: 'Kindling', desc: 'A foe that dies burning goes off like a bomb.' }
  ],
  sable: [
    { id: 'fan', name: 'Fan of Knives', desc: 'Every throw becomes a spread of three.' },
    { id: 'ric', name: 'Ricochet', desc: 'Your daggers leap on to a second and third mark.' },
    { id: 'venom', name: 'Venom', desc: 'Your blades carry poison.' },
    { id: 'ambush', name: 'Ambush', desc: 'The first strike on an unwary foe always lands critically.' }
  ],
  thistle: [
    { id: 'volley', name: 'Volley', desc: 'Each draw looses three arrows in a fan.' },
    { id: 'barbs', name: 'Barbed Shafts', desc: 'An arrow hits harder with every foe it passes through.' },
    { id: 'frost', name: 'Hoarfrost', desc: 'Your arrows chill what they strike.' },
    { id: 'mark', name: "Hunter's Mark", desc: 'Foes you hit take more from every source for a while.' }
  ]
};
const bn = (P, id) => !!(P && P.boons && P.boons[id]);
function boonsLeft(P) { return (BOONS[P.cls.key] || []).filter(b => !bn(P, b.id)); }
function rollBoons(P) {
  const pool = boonsLeft(P).slice(), out = [];
  while (out.length < 3 && pool.length) out.push(pool.splice(rint(0, pool.length - 1), 1)[0]);
  return out;
}

/* ---------- elemental affinities ----------""")

# --- the player carries them ----------------------------------------------
edit(L, """      xp: 0, plvl: 1, buys: {} };""",
     """      xp: 0, plvl: 1, buys: {}, boons: {} };""")

# --- every other level offers a boon instead of a stat --------------------
edit(L, """      queueOffer({ kind: 'up', P, opts: rollOffer(false) });""",
     """      const bo = P.plvl % 2 === 0 ? rollBoons(P) : [];
      if (bo.length) queueOffer({ kind: 'boon', P, opts: bo });
      else queueOffer({ kind: 'up', P, opts: rollOffer(false) });""")

edit(L, """function applyUpgrade(i) {
  const o = G.offer;
  if (o.kind === 'gear') { if (i === 0) equip(o.P, o.item); else { text(o.P.x, o.P.y - 20, 'Left behind', '#98a0b3'); } }
  else { const u = o.opts[i]; applyUp(o.P, u.id, u.m); }
  closeOffer();
}""",
     """function applyUpgrade(i) {
  const o = G.offer;
  if (o.kind === 'gear') { if (i === 0) equip(o.P, o.item); else { text(o.P.x, o.P.y - 20, 'Left behind', '#98a0b3'); } }
  else if (o.kind === 'boon') {
    const b = o.opts[i], P = o.P;
    P.boons[b.id] = 1;
    text(P.x, P.y - 24, b.name + '!', P.cls.col, 15); sfx('level');
    announceOnce('boon' + P.idx, .5, P.cls.name + ' learns ' + b.name, P.cls.col);
    G.fxs.push({ kind: 'shock', x: P.x, y: P.y, t: 0, r: 140, c1: '255,250,225', c2: '200,180,255' });
    burst(P.x, P.y, P.cls.col, 28, 190, 1.3, 'spark');
  }
  else { const u = o.opts[i]; applyUp(o.P, u.id, u.m); }
  closeOffer();
}""")

# --- the card ---------------------------------------------------------------
edit(L, """  } else {
    $('lootT').textContent = G.co ? 'P' + (P.idx + 1) + ' opens a chest' : 'Chest opened';""",
     """  } else if (o.kind === 'boon') {
    $('lootT').textContent = (G.co ? 'P' + (P.idx + 1) + ': ' : '') + 'A new way to fight';
    $('lootS').textContent = sheetLine(P);
    $('lootHint').textContent = 'Click a card or press 1, 2 or 3. This one changes how your attack works.';
    o.opts.forEach((b, i) => {
      const btn = document.createElement('button'); btn.type = 'button'; btn.className = 'card'; btn.style.setProperty('--c', P.cls.col);
      const r = document.createElement('span'); r.className = 'itemrar'; r.style.color = P.cls.col; r.textContent = 'Boon'; btn.appendChild(r);
      const n = document.createElement('span'); n.className = 'nm'; n.textContent = (i + 1) + '. ' + b.name; btn.appendChild(n);
      const d = document.createElement('span'); d.className = 'bl'; d.textContent = b.desc; btn.appendChild(d);
      btn.addEventListener('click', () => chooseUp(i)); wrap.appendChild(btn);
    });
  } else {
    $('lootT').textContent = G.co ? 'P' + (P.idx + 1) + ' opens a chest' : 'Chest opened';""")

edit(L, """  if (o.kind === 'gear' ? (i !== 0 && i !== 1) : !o.opts[i]) return;""",
     """  if (o.kind === 'gear' ? (i !== 0 && i !== 1) : !o.opts[i]) return;
  if (o.kind === 'boon' && !o.opts[i]) return;""")

# --- show what each delver has learned ------------------------------------
edit(L, """    const worn = SLOTS.map(s => P.gear[s]).filter(Boolean);""",
     """    const learned = (BOONS[P.cls.key] || []).filter(b => bn(P, b.id));
    if (learned.length) {
      const bl = document.createElement('div'); bl.className = 'heroline'; bl.style.color = P.cls.col;
      bl.textContent = 'Boons: ' + learned.map(b => b.name).join(' \\u00b7 ');
      hl.appendChild(bl);
    }
    const worn = SLOTS.map(s => P.gear[s]).filter(Boolean);""")

edit(L, """    ['Time below', mmss(G.runT || 0)]
  ];""",
     """    ['Time below', mmss(G.runT || 0)]
  ];
  const allBoons = [];
  for (const p of G.players) for (const b of (BOONS[p.cls.key] || [])) if (bn(p, b.id)) allBoons.push(b.name);
  if (allBoons.length) rows.push(['Boons learned', allBoons.join(', ')]);""")

run()
