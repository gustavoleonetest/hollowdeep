from patch import edit, run

H = 'part_head.html'
L = 'part_logic.js'

# --- HUD markup: level, experience, worn gear, potions ---------------------
edit(H, """      <div class="panel hp" id="hp">
        <div class="nm"><span id="clsName">Bulwark</span><span id="hpTxt">0 / 0</span></div>
        <div class="track"><div class="fill" id="hpFill"></div></div>
        <div class="track" title="Dash"><div class="fill dash" id="dashFill"></div></div>
        <div class="track" title="Special (E)"><div class="fill sp" id="spFill"></div></div>
      </div>
      <div class="panel hp" id="hp2" hidden>
        <div class="nm"><span id="clsName2">Ember</span><span id="hpTxt2">0 / 0</span></div>
        <div class="track"><div class="fill" id="hpFill2"></div></div>
        <div class="track" title="Dash"><div class="fill dash" id="dashFill2"></div></div>
        <div class="track" title="Special (Right Ctrl)"><div class="fill sp" id="spFill2"></div></div>
      </div>""",
     """      <div class="panel hp" id="hp">
        <div class="nm"><span id="clsName">Bulwark</span><span class="lv" id="lv">LV 1</span><span class="tx" id="hpTxt">0 / 0</span></div>
        <div class="track"><div class="fill" id="hpFill"></div></div>
        <div class="track xpt" title="Experience"><div class="fill xp" id="xpFill"></div></div>
        <div class="track" title="Dash"><div class="fill dash" id="dashFill"></div></div>
        <div class="track" title="Special (E)"><div class="fill sp" id="spFill"></div></div>
        <div class="gear" id="gear"><span data-s="weapon">W</span><span data-s="armour">A</span><span data-s="trinket">T</span></div>
      </div>
      <div class="panel hp" id="hp2" hidden>
        <div class="nm"><span id="clsName2">Ember</span><span class="lv" id="lv2">LV 1</span><span class="tx" id="hpTxt2">0 / 0</span></div>
        <div class="track"><div class="fill" id="hpFill2"></div></div>
        <div class="track xpt" title="Experience"><div class="fill xp" id="xpFill2"></div></div>
        <div class="track" title="Dash"><div class="fill dash" id="dashFill2"></div></div>
        <div class="track" title="Special (Right Ctrl)"><div class="fill sp" id="spFill2"></div></div>
        <div class="gear" id="gear2"><span data-s="weapon">W</span><span data-s="armour">A</span><span data-s="trinket">T</span></div>
      </div>""")

edit(H, """      <span id="comboBox" hidden>Chain <b id="combo">0</b></span>""",
     """      <span id="bombBox">Potions <b id="bombs">0</b></span>
      <span id="comboBox" hidden>Chain <b id="combo">0</b></span>""")

edit(H, """  <button id="spBtn" type="button">SPECIAL</button>""",
     """  <button id="spBtn" type="button">SPECIAL</button>
  <button id="bombBtn" type="button">POTION</button>""")

edit(H, """      <p class="sub">Click a card or press 1, 2 or 3.</p>""",
     """      <p class="sub" id="lootHint">Click a card or press 1, 2 or 3.</p>""")

# --- styles for the new HUD pieces -----------------------------------------
edit(H, """.hp .nm{display:flex; justify-content:space-between; font-size:12px; letter-spacing:.06em; text-transform:uppercase}""",
     """.hp .nm{display:flex; align-items:baseline; gap:8px; font-size:12px; letter-spacing:.06em; text-transform:uppercase}
.hp .nm .tx{margin-left:auto}
.hp .lv{color:var(--torch); font-size:10px; letter-spacing:.1em}
.track.xpt{height:4px}
.fill.xp{background:#c9a24a; transition:none}
.gear{display:flex; gap:4px}
.gear span{flex:none; width:19px; height:19px; display:grid; place-items:center; border:1px solid var(--line); border-radius:3px; color:#454c5e; font:600 10px var(--mono)}
.itemstats{display:grid; gap:2px; font-size:12px; color:var(--dim)}
.itemrar{font-size:10px; letter-spacing:.1em; text-transform:uppercase; opacity:.85}""")

edit(H, """@media (pointer:coarse){#spBtn{display:block}}""",
     """@media (pointer:coarse){#spBtn{display:block}}
#bombBtn{display:none; position:absolute; right:10px; bottom:calc(min(156px,30vw)*.73 + 94px); width:64px; height:64px; border-radius:50%; border:1px solid #b98cff; background:rgba(12,14,19,.7); color:#b98cff; font:600 11px var(--mono); letter-spacing:.08em}
@media (pointer:coarse){#bombBtn{display:block}}""")

# --- controls and the pitch -------------------------------------------------
edit(H, """  <p><kbd>WASD</kbd> move · <kbd>mouse</kbd> aim · <kbd>click</kbd>/<kbd>Space</kbd> attack · <kbd>Shift</kbd> dash · <kbd>E</kbd> special · <kbd>P</kbd> pause · <kbd>M</kbd> mute · Co-op P2: <kbd>arrows</kbd>, <kbd>Enter</kbd> attack, <kbd>Right Shift</kbd> dash, <kbd>Right Ctrl</kbd> special</p>""",
     """  <p><kbd>WASD</kbd> move · <kbd>mouse</kbd> aim · <kbd>click</kbd>/<kbd>Space</kbd> attack · <kbd>Shift</kbd> dash · <kbd>E</kbd> special · <kbd>F</kbd> potion · <kbd>P</kbd> pause · <kbd>M</kbd> mute · <kbd>V</kbd> narrator · Co-op P2: <kbd>arrows</kbd>, <kbd>Enter</kbd> attack, <kbd>Right Shift</kbd> dash, <kbd>Right Ctrl</kbd> special, <kbd>Right Alt</kbd> potion</p>""")

edit(H, """      <p class="sub">Smash the crypts that spawn monsters, grab the key, unlock the sealed door and find the stairs. Chests let you pick an upgrade. Kill without pause to build a chain and score more. Mind the spike plates — and lure the horde across them. Every depth is a new dungeon. Best run: <span class="big" id="best">0</span></p>""",
     """      <p class="sub">Smash the crypts, take the key, unlock the door, find the stairs. <b>Your health drains the whole way down</b>, so food is the only clock that matters. Monsters drop rolled gear — weapons, armour and trinkets with their own affixes — and kills earn levels. Keep a potion for when the floor turns against you. Best run: <span class="big" id="best">0</span></p>""")

# --- the chest card and the gear compare share one overlay ------------------
edit(L, """function showLoot() {
  const o = G.offer, P = o.P, pct = x => Math.round((x - 1) * 100);
  $('lootT').textContent = G.co ? 'P' + (P.idx + 1) + ' opens a chest' : 'Chest opened';
  $('lootS').textContent = P.cls.name + ': ' + P.max + ' max health, speed +' + pct(P.spdMul) + '%, damage +' + pct(P.dmgMul) + '%, attacks ' + pct(1 / P.cdMul) + '% faster.';
  const wrap = $('lootCards'); wrap.innerHTML = '';
  o.opts.forEach((u, i) => {
    const info = upInfo(P, u.id, u.m), b = document.createElement('button'); b.type = 'button'; b.className = 'card'; b.style.setProperty('--c', info.col);
    b.innerHTML = '<span class="nm">' + (i + 1) + '. ' + info.name + '</span><span class="bl">' + info.desc + '</span>' + (u.rare || u.m > 1 ? '<span class="rare">Rare</span>' : '');
    b.addEventListener('click', () => chooseUp(i)); wrap.appendChild(b);
  });
  $('loot').hidden = false;
}
function chooseUp(i) { if (G.state !== 'offer' || !G.offer || !G.offer.opts[i]) return; applyUpgrade(i); $('loot').hidden = true; lootShown = false; }""",
     """function sheetLine(P) {
  const pct = x => Math.round((x - 1) * 100);
  return P.cls.name + ' \\u00b7 level ' + P.plvl + ' \\u00b7 ' + P.max + ' max health, damage +' + pct(P.dmgMul) + '%, speed +' + pct(P.spdMul) + '%, attacks ' + pct(1 / P.cdMul) + '% faster.';
}
function gearCard(label, item, idx, hint) {
  const b = document.createElement('button'); b.type = 'button'; b.className = 'card';
  b.style.setProperty('--c', item ? item.col : '#3a4152');
  const r = document.createElement('span'); r.className = 'itemrar'; r.style.color = item ? item.col : '#98a0b3';
  r.textContent = label; b.appendChild(r);
  const n = document.createElement('span'); n.className = 'nm'; n.textContent = item ? item.name : 'Nothing worn'; b.appendChild(n);
  const s = document.createElement('span'); s.className = 'itemstats';
  if (item) for (const line of itemLines(item)) { const d = document.createElement('span'); d.textContent = line; s.appendChild(d); }
  else { const d = document.createElement('span'); d.textContent = 'That slot is empty.'; s.appendChild(d); }
  b.appendChild(s);
  const h = document.createElement('span'); h.className = 'rare'; h.textContent = hint; b.appendChild(h);
  b.addEventListener('click', () => chooseUp(idx));
  return b;
}
function showLoot() {
  const o = G.offer, P = o.P, wrap = $('lootCards'); wrap.innerHTML = '';
  if (o.kind === 'gear') {
    $('lootT').textContent = (G.co ? 'P' + (P.idx + 1) + ' finds ' : 'You find ') + o.item.name;
    $('lootS').textContent = sheetLine(P);
    $('lootHint').textContent = 'Press 1 to equip, 2 to leave it.';
    wrap.appendChild(gearCard('New \\u00b7 ' + (RARITY[o.item.rar] || {}).name, o.item, 0, '1 \\u00b7 Equip'));
    wrap.appendChild(gearCard('Worn \\u00b7 ' + o.item.slot, o.cur, 1, '2 \\u00b7 Keep this'));
  } else {
    $('lootT').textContent = G.co ? 'P' + (P.idx + 1) + ' opens a chest' : 'Chest opened';
    $('lootS').textContent = sheetLine(P);
    $('lootHint').textContent = 'Click a card or press 1, 2 or 3.';
    o.opts.forEach((u, i) => {
      const info = upInfo(P, u.id, u.m), b = document.createElement('button'); b.type = 'button'; b.className = 'card'; b.style.setProperty('--c', info.col);
      const n = document.createElement('span'); n.className = 'nm'; n.textContent = (i + 1) + '. ' + info.name; b.appendChild(n);
      const d = document.createElement('span'); d.className = 'bl'; d.textContent = info.desc; b.appendChild(d);
      if (u.m > 1) { const r = document.createElement('span'); r.className = 'rare'; r.textContent = 'Rare'; b.appendChild(r); }
      b.addEventListener('click', () => chooseUp(i)); wrap.appendChild(b);
    });
  }
  $('loot').hidden = false;
}
function chooseUp(i) {
  const o = G.offer;
  if (G.state !== 'offer' || !o) return;
  if (o.kind === 'gear' ? (i !== 0 && i !== 1) : !o.opts[i]) return;
  applyUpgrade(i); $('loot').hidden = true; lootShown = false;
}""")

# --- the stall lists what each delver is wearing ---------------------------
edit(L, """  for (const P of G.players) { const d = document.createElement('div'); d.className = 'heroline'; d.style.color = P.cls.col; d.textContent = (G.co ? 'P' + (P.idx + 1) + ' ' : '') + P.cls.name + (P.down ? ': down' : ': ' + Math.ceil(P.hp) + ' / ' + P.max + ' health') + ' \\u00b7 damage +' + pct(P.dmgMul) + '% \\u00b7 speed +' + pct(P.spdMul) + '%'; hl.appendChild(d); }""",
     """  for (const P of G.players) {
    const d = document.createElement('div'); d.className = 'heroline'; d.style.color = P.cls.col;
    d.textContent = (G.co ? 'P' + (P.idx + 1) + ' ' : '') + P.cls.name + ' \\u00b7 level ' + P.plvl + (P.down ? ' \\u00b7 down' : ' \\u00b7 ' + Math.ceil(P.hp) + ' / ' + P.max + ' health') + ' \\u00b7 damage +' + pct(P.dmgMul) + '% \\u00b7 speed +' + pct(P.spdMul) + '%';
    hl.appendChild(d);
    const worn = SLOTS.map(s => P.gear[s]).filter(Boolean);
    if (worn.length) {
      const g = document.createElement('div'); g.className = 'heroline';
      worn.forEach((it, i) => { const sp = document.createElement('span'); sp.style.color = it.col; sp.textContent = (i ? ' \\u00b7 ' : '') + it.name; g.appendChild(sp); });
      hl.appendChild(g);
    }
  }""")

run()
