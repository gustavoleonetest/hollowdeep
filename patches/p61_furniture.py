from patch import edit, run

L = 'part_logic.js'

# --- the locked door gets the gate that was sitting in the atlas ----------
# It was baked as hand-drawn planks into the tile canvas, which meant it took
# no light and could not react. Drawn as an entity it is lit like everything
# else, and can lean on its hinges when you try it without the key.
edit(L, """  drawTiles(); drawDecals(); drawArena(); drawExit(); for (const t of G.torches) drawTorch(t);""",
     """  drawTiles(); drawDecals(); drawArena(); drawExit(); drawDoor(); for (const t of G.torches) drawTorch(t);""")

edit(L, """function drawExit() {""",
     """function drawDoor() {
  const d = G.door;
  if (!d || !G.map || G.map[d.y * MW + d.x] !== 2) return;
  const x = d.x * T + T / 2, y = d.y * T + T / 2;
  if (fogAt(x, y) > .85) return;
  const p = (Math.sin(clock * 2.2) + 1) / 2;
  /* it strains when you are near without the key, and settles when you hold one */
  const near = G.players.some(q => !q.down && Math.hypot(q.x - x, q.y - y) < 70);
  const held = G.keys > 0;
  const rattle = (near && !held) ? Math.sin(clock * 24) * 1.1 : 0;
  shadow(x, y + 13, 14, 5, .4);
  glow(x, y, 34, held ? '#f0a23c' : '#8d93a8', (held ? .34 : .16) + p * .1);
  if (!sprProp('gate', x + rattle, y + 13, 1.45)) return;
  /* the lock reads gold once a key is in hand, so the door tells you itself */
  ctx.save();
  ctx.globalAlpha = .75 + p * .25;
  ctx.fillStyle = held ? '#ffd24a' : '#6e7d97';
  ctx.beginPath(); ctx.arc(x, y - 1, 3.4, 0, TAU); ctx.fill();
  ctx.fillStyle = held ? '#fff6d8' : '#3a4152';
  ctx.fillRect(x - .9, y - 1, 1.8, 4);
  ctx.restore(); ctx.globalAlpha = 1;
  if (held && Math.random() < .12) G.parts.push({ x: x + rnd(-10, 10), y: y + rnd(-10, 6), vx: 0, vy: -.4, life: .5, max: .5, col: '#ffd24a', s: 2, k: 'ember' });
}
function drawExit() {""")

# the baked planks would show through the gate, so leave the tile plain
edit(L, """function bakeDoor(b, px, py) {
  b.fillStyle = '#6e4626'; b.fillRect(px + 2, py + 1, T - 4, T - 2);""",
     """function bakeDoor(b, px, py) {
  /* only the frame is baked now: drawDoor puts the gate itself on top, lit */
  b.fillStyle = '#241a12'; b.fillRect(px, py, T, T);
  b.fillStyle = '#3a2a1c'; b.fillRect(px + 1, py + 1, T - 2, T - 2);
  if (sprOk('props')) return;
  b.fillStyle = '#6e4626'; b.fillRect(px + 2, py + 1, T - 4, T - 2);""")

# --- glass breaks like glass, not like a plank ---------------------------
edit(L, """const MATCOL = { stone: ['#8d93a8', '#5b6275', '#d5d9e6'], clay: ['#a8643a', '#7a4426', '#d9a070'], metal: ['#9aa3b2', '#5d6574', '#eef2f8'], wood: ['#8a5a2e', '#5e3c1c', '#c9a062'], bone: ['#e8e0c8', '#b8ae92', '#ffffff'] };""",
     """const MATCOL = { stone: ['#8d93a8', '#5b6275', '#d5d9e6'], clay: ['#a8643a', '#7a4426', '#d9a070'], metal: ['#9aa3b2', '#5d6574', '#eef2f8'], wood: ['#8a5a2e', '#5e3c1c', '#c9a062'], bone: ['#e8e0c8', '#b8ae92', '#ffffff'], glass: ['#9fd4e8', '#5d8ea8', '#ffffff'] };""")

edit(L, """  if (/skull/.test(k)) return 'bone';
  return 'wood';""",
     """  if (/skull/.test(k)) return 'bone';
  if (/(bottles|potion2|chalice)/.test(k)) return 'glass';
  return 'wood';""")

# --- furniture, placed where a room of that kind would have had it -------
# The Drowned Halls are the stores: tables, benches, crates, a stall.
edit(L, """['rts_logs', 0, 1.4, 1], ['p_bookcase', 12, 1.0, 1]],""",
     """['rts_logs', 0, 1.4, 1], ['p_bookcase', 12, 1.0, 1],
   ['p_table', 12, 1.0, 2], ['p_bench', 10, 1.1, 2], ['p_stool', 5, 1.2, 2], ['p_chair', 6, 1.15, 1],
   ['p_crate_metal', 9, 1.2, 2], ['p_chest_wood', 9, 1.2, 1], ['p_stall', 12, 1.0, 1], ['p_bottles', 0, 1.4, 1]],""")

# The Cinder Vaults are a forge: a bench to work at, bottles, a metal crate.
edit(L, """['p_sword', 0, 1.5, 1], ['p_shield', 0, 1.4, 1]],""",
     """['p_sword', 0, 1.5, 1], ['p_shield', 0, 1.4, 1],
   ['p_bench', 10, 1.1, 2], ['p_stool', 5, 1.2, 1], ['p_crate_metal', 9, 1.2, 2], ['p_bottles', 0, 1.4, 1]],""")

# The Crypts and the Bone Gardens: candles and a vase on a grave.
edit(L, """['p_candlestick', 5, 1.2, 2, 70], ['p_bookstand', 6, 1.2, 1], ['p_coin_pile', 0, 1.4, 1]],""",
     """['p_candlestick', 5, 1.2, 2, 70], ['p_bookstand', 6, 1.2, 1], ['p_coin_pile', 0, 1.4, 1],
   ['r_candles', 0, 1.7, 2, 56], ['p_vase', 6, 1.3, 2]],""")

edit(L, """['r_column_round', 9, 1.1, 2], ['p_pouch', 0, 1.4, 1]],""",
     """['r_column_round', 9, 1.1, 2], ['p_pouch', 0, 1.4, 1],
   ['r_candles', 0, 1.7, 2, 56], ['p_vase', 6, 1.3, 1]],""")

# The Obsidian Reach is a sanctum: shelves, a table, glassware, broken pots.
edit(L, """['p_chalice', 0, 1.5, 1], ['r_pot2', 7, 1.3, 2], ['trap', 0, 1.2, 1]]""",
     """['p_chalice', 0, 1.5, 1], ['r_pot2', 7, 1.3, 2], ['trap', 0, 1.2, 1],
   ['r_bookcase', 12, 1.0, 2], ['p_table', 12, 1.0, 1], ['p_potion2', 0, 1.4, 1], ['p_bottles', 0, 1.4, 1],
   ['r_pot2_broken', 0, 1.3, 1], ['p_vase', 6, 1.3, 1]]""")

run()
