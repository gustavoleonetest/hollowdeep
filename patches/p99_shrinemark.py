from patch import edit, run

L = 'part_logic.js'

# --- the map did not mark the one thing you are invited to come back to --
# A shrine is the sharpest decision on a floor: a pact that costs you
# something, a blessing that does not, or an altar you cannot read. And the
# game deliberately lets you walk away from one -- "refusing leaves the
# font standing, so brushing past one costs nothing" -- which is an
# invitation to return once you have seen what the floor holds.
#
# It then gave you no way to find it again. The map knew where it was and
# said nothing.
#
# A disc, which is the one simple shape the map was not already using: the
# exit is a stroked ring, the crypt an X, the chest a diamond, the key a
# triangle, the food a bar, the delver a square. In the shrine's own colour,
# the same one it is drawn with in the world, so nothing is given away that
# standing in front of it would not have told you.
edit(L, """  /* a bar: something to eat, which is the only clock that matters */""",
     """  /* a disc: an altar, and you are allowed to come back to it */
  const markDisc = (x, y, c) => {
    if (!seenAt(x, y)) return;
    mctx.fillStyle = c;
    mctx.beginPath(); mctx.arc(px(x), px(y), 2.6, 0, TAU); mctx.fill();
  };
  /* a bar: something to eat, which is the only clock that matters */""")

edit(L, """    if (i.kind === 'chest') markDiamond(i.x, i.y, C.amber);
    else if (i.kind === 'key') markTri(i.x, i.y, C.amber);
    else if (i.kind === 'food') markBar(i.x, i.y, C.leaf);""",
     """    if (i.kind === 'chest') markDiamond(i.x, i.y, C.amber);
    else if (i.kind === 'key') markTri(i.x, i.y, C.amber);
    else if (i.kind === 'food') markBar(i.x, i.y, C.leaf);
    else if (i.kind === 'shrine') markDisc(i.x, i.y, shrineCol(i.sh));""")

run()
