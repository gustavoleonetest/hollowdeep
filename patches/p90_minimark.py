from patch import edit, run

L = 'part_logic.js'

# --- the map remembered the wrong things ---------------------------------
# The minimap marks the way out, the crypts and the chests. It does not mark
# the key, which is the thing that actually gates the floor -- "take the key,
# unlock the door, find the stairs" is the whole instruction -- and it does
# not mark food, which is the only cure for the seventy per cent of a run's
# health that the drain takes.
#
# Both are already-discovered things. The markers are gated on seen ground,
# so nothing hidden is revealed: this only stops you forgetting where the
# loaf was while you were busy being chased away from it. Which is a thing
# that happens constantly, because being chased away from it is the game.
edit(L, """const C = { floorA: '#1a1f2c', floorB: '#1d2333', speck: '#262d40', wall: '#2c3447', wallHi: '#3b455d', face: '#11141c', void: '#0a0c11', door: '#7a4e2a', amber: '#f0a23c', blood: '#d9534f', bone: '#ebe4d2', cyan: '#8fd3ff' };""",
     """const C = { floorA: '#1a1f2c', floorB: '#1d2333', speck: '#262d40', wall: '#2c3447', wallHi: '#3b455d', face: '#11141c', void: '#0a0c11', door: '#7a4e2a', amber: '#f0a23c', blood: '#d9534f', bone: '#ebe4d2', cyan: '#8fd3ff', leaf: '#9bd16a' };""")

edit(L, """  /* a diamond: something to open */""",
     """  /* a triangle: the way through, if you can reach it */
  const markTri = (x, y, c) => {
    if (!seenAt(x, y)) return;
    const a = px(x), b = px(y), r = 3;
    mctx.fillStyle = c;
    mctx.beginPath(); mctx.moveTo(a, b - r); mctx.lineTo(a + r, b + r - .5); mctx.lineTo(a - r, b + r - .5);
    mctx.closePath(); mctx.fill();
  };
  /* a bar: something to eat, which is the only clock that matters */
  const markBar = (x, y, c) => {
    if (!seenAt(x, y)) return;
    mctx.fillStyle = c;
    mctx.fillRect(px(x) - 3, px(y) - 1.5, 6, 3);
  };
  /* a diamond: something to open */""")

edit(L, """  for (const i of G.items) if (i.kind === 'chest') markDiamond(i.x, i.y, C.amber);""",
     """  for (const i of G.items) {
    if (i.kind === 'chest') markDiamond(i.x, i.y, C.amber);
    else if (i.kind === 'key') markTri(i.x, i.y, C.amber);
    else if (i.kind === 'food') markBar(i.x, i.y, C.leaf);
  }""")

run()
