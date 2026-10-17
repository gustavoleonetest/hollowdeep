from patch import edit, run

L = 'part_logic.js'
H = 'part_head.html'

# --- rooms now contain pillars, so anything we drop in one has to land on a
#     floor tile the player can actually walk to -----------------------------
edit(L, """function roomPoint(r) { return { x: (r.x + 1 + Math.random() * (r.w - 2)) * T, y: (r.y + 1 + Math.random() * (r.h - 2)) * T }; }""",
     """const openAt = (x, y) => {
  const tx = Math.floor(x / T), ty = Math.floor(y / T);
  if (tx < 0 || ty < 0 || tx >= MW || ty >= MH) return false;
  return !!(G.reach && G.reach[ty * MW + tx]);
};
/* flood from the start room, treating the locked door as passable, so nothing
   is ever placed inside a pillar or in a pocket walled off by one */
function buildReach() {
  const r = new Uint8Array(MW * MH), s = G.rooms[0], q = [s.cy * MW + s.cx];
  r[q[0]] = 1;
  for (let h = 0; h < q.length; h++) {
    const c = q[h], cx = c % MW, cy = (c / MW) | 0;
    for (const [dx, dy] of DIRS) {
      const x = cx + dx, y = cy + dy; if (x < 0 || y < 0 || x >= MW || y >= MH) continue;
      const i = y * MW + x; if (r[i] || G.map[i] === 1) continue;
      r[i] = 1; q.push(i);
    }
  }
  G.reach = r;
}
function roomPoint(r) {
  for (let i = 0; i < 40; i++) {
    const x = (r.x + 1 + Math.random() * (r.w - 2)) * T, y = (r.y + 1 + Math.random() * (r.h - 2)) * T;
    if (openAt(x, y)) return { x, y };
  }
  return { x: (r.cx + .5) * T, y: (r.cy + .5) * T };
}""")

edit(L, """  G.map = m; G.seen = new Uint8Array(MW * MH); G.rooms = rooms;""",
     """  G.map = m; G.seen = new Uint8Array(MW * MH); G.rooms = rooms; buildReach();""")

edit(L, """  G.items.push({ kind: 'chest', big: true, x: (last.x + 1.5) * T, y: (last.y + 1.5) * T, t: 0 });""",
     """  const bc = openAt((last.x + 1.5) * T, (last.y + 1.5) * T) ? { x: (last.x + 1.5) * T, y: (last.y + 1.5) * T } : roomPoint(last);
  G.items.push({ kind: 'chest', big: true, x: bc.x, y: bc.y, t: 0 });""")

edit(L, """      if (avoid.some(a => Math.hypot(x - a[0], y - a[1]) < a[2]) || G.props.some(p => Math.hypot(x - p.x, y - p.y) < 40)) continue;""",
     """      if (!openAt(x, y)) continue;
      if (avoid.some(a => Math.hypot(x - a[0], y - a[1]) < a[2]) || G.props.some(p => Math.hypot(x - p.x, y - p.y) < 40)) continue;""")

edit(L, """    if (G.map[ty * MW + tx] !== 0) continue;
    const x = tx * T + T / 2, y = ty * T + T / 2;
    if (avoid.some(a => Math.hypot(x - a[0], y - a[1]) < a[2])) continue;""",
     """    if (G.map[ty * MW + tx] !== 0) continue;
    const x = tx * T + T / 2, y = ty * T + T / 2;
    if (!openAt(x, y)) continue;
    if (avoid.some(a => Math.hypot(x - a[0], y - a[1]) < a[2])) continue;""")

# --- the nests also spawn foes around themselves ----------------------------
edit(L, """        const a = rnd(0, TAU), x = n.x + Math.cos(a) * 30, y = n.y + Math.sin(a) * 30;
        if (!blockedAt(x, y, 11)) { spawnFoe(pickFoe(), x, y); burst(x, y, '#c2563f', 6, 60); break; }""",
     """        const a = rnd(0, TAU), x = n.x + Math.cos(a) * 30, y = n.y + Math.sin(a) * 30;
        if (!blockedAt(x, y, 11) && openAt(x, y)) { spawnFoe(pickFoe(), x, y); burst(x, y, '#c2563f', 6, 60); break; }""")

# --- and so does the warden ------------------------------------------------
edit(L, """      if (!blockedAt(x, y, 11)) { spawnFoe('gloam', x, y); G.enemies[G.enemies.length - 1].alert = true; burst(x, y, '#9a6bd6', 8, 60); }""",
     """      if (!blockedAt(x, y, 11) && openAt(x, y)) { spawnFoe('gloam', x, y, false); G.enemies[G.enemies.length - 1].alert = true; burst(x, y, '#9a6bd6', 8, 60); }""")

# --- tell the player what is new -------------------------------------------
edit(H, """  <p><kbd>WASD</kbd> move · <kbd>mouse</kbd> aim · <kbd>click</kbd>/<kbd>Space</kbd> attack · <kbd>Shift</kbd> dash · <kbd>E</kbd> special · <kbd>P</kbd> pause · <kbd>M</kbd> mute · Co-op P2: <kbd>arrows</kbd>, <kbd>Enter</kbd> attack, <kbd>Right Shift</kbd> dash, <kbd>Right Ctrl</kbd> special</p>""",
     """  <p><kbd>WASD</kbd> move · <kbd>mouse</kbd> aim · <kbd>click</kbd>/<kbd>Space</kbd> attack · <kbd>Shift</kbd> dash · <kbd>E</kbd> special · <kbd>P</kbd> pause · <kbd>M</kbd> mute · Co-op P2: <kbd>arrows</kbd>, <kbd>Enter</kbd> attack, <kbd>Right Shift</kbd> dash, <kbd>Right Ctrl</kbd> special</p>""")

edit(H, """      <p class="sub">Smash the crypts that spawn monsters, grab the key, unlock the sealed door and find the stairs. Chests let you pick an upgrade. Every depth is a new dungeon. Best run: <span class="big" id="best">0</span></p>""",
     """      <p class="sub">Smash the crypts that spawn monsters, grab the key, unlock the sealed door and find the stairs. Chests let you pick an upgrade. Kill without pause to build a chain and score more. Mind the spike plates — and lure the horde across them. Every depth is a new dungeon. Best run: <span class="big" id="best">0</span></p>""")

edit(H, """      <p class="sub">You reached depth <span class="big" id="oLvl">1</span> with a score of <span class="big" id="oScore">0</span>. Best run: <span class="big" id="oBest">0</span></p>""",
     """      <p class="sub">You reached depth <span class="big" id="oLvl">1</span> with a score of <span class="big" id="oScore">0</span>, on a best chain of <span class="big" id="oChain">0</span>. Best run: <span class="big" id="oBest">0</span></p>""")

edit(L, """if (G.state === 'dead' && !overShown) { overShown = true; $('oLvl').textContent = G.level; $('oScore').textContent = G.score; $('oBest').textContent = G.best;""",
     """if (G.state === 'dead' && !overShown) { overShown = true; $('oLvl').textContent = G.level; $('oScore').textContent = G.score; $('oChain').textContent = G.comboBest; $('oBest').textContent = G.best;""")

edit(L, """  G.player = G.players[0]; G.gold = 0; G.keys = 0;""",
     """  G.player = G.players[0]; G.gold = 0; G.keys = 0; G.combo = 0; G.comboT = 0; G.comboBest = 0;""")

run()
