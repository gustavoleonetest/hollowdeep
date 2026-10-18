from patch import edit, run

L = 'part_logic.js'

# --- the one mark you most need was underneath all the others ------------
# The exit was drawn first and everything else on top of it, so a crypt
# standing beside the stairs, or a loaf dropped on them, painted over the
# way out. On an ordinary floor that is a near miss; on a Horde floor,
# measured at thirty-two crypts and fifteen loaves, it is a real one.
#
# Drawing it last costs nothing and means the destination is never hidden
# by the things you pass on the way to it. A shade larger too, because it
# is not one mark among several -- it is where you are going.
edit(L, """  markRing(G.exit.x, G.exit.y, C.cyan);
  for (const n of G.nests) markCross(n.x, n.y, C.blood);
  for (const i of G.items) {
    if (i.kind === 'chest') markDiamond(i.x, i.y, C.amber);
    else if (i.kind === 'key') markTri(i.x, i.y, C.amber);
    else if (i.kind === 'food') markBar(i.x, i.y, C.leaf);
    else if (i.kind === 'shrine') markDisc(i.x, i.y, shrineCol(i.sh));
  }""",
     """  for (const n of G.nests) markCross(n.x, n.y, C.blood);
  for (const i of G.items) {
    if (i.kind === 'chest') markDiamond(i.x, i.y, C.amber);
    else if (i.kind === 'key') markTri(i.x, i.y, C.amber);
    else if (i.kind === 'food') markBar(i.x, i.y, C.leaf);
    else if (i.kind === 'shrine') markDisc(i.x, i.y, shrineCol(i.sh));
  }
  /* last, and over the top of everything: the way down is not one mark
     among several, it is where the whole floor is going */
  markRing(G.exit.x, G.exit.y, C.cyan);""")

edit(L, """  const markRing = (x, y, c) => {
    if (!seenAt(x, y)) return;
    mctx.strokeStyle = c; mctx.lineWidth = 1.5;
    mctx.beginPath(); mctx.arc(px(x), px(y), 2.6, 0, TAU); mctx.stroke();
    mctx.fillStyle = c; mctx.fillRect(px(x) - .5, px(y) - .5, 1, 1);
  };""",
     """  const markRing = (x, y, c) => {
    if (!seenAt(x, y)) return;
    mctx.strokeStyle = c; mctx.lineWidth = 1.5;
    mctx.beginPath(); mctx.arc(px(x), px(y), 3.4, 0, TAU); mctx.stroke();
    mctx.fillStyle = c; mctx.fillRect(px(x) - 1, px(y) - 1, 2, 2);
  };""")

run()
