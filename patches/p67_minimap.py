from patch import edit, run

L = 'part_logic.js'

# --- the minimap was telling you things in colour alone -------------------
# Everywhere else the game names what it is showing: elite modifiers, omens
# and delvers all carry text, so colour only reinforces. The minimap has no
# text at all, and drew four different things as near enough the same small
# square. Measured as CIE76 distance after simulating each dichromacy, the
# closest pair was indistinguishable even to ordinary sight: a chest and the
# Bulwark's own marker at dE 11.4, falling to 4.1 under protanopia, and the
# crypts matching the doors at 4.3 under deuteranopia.
#
# Shape carries it now, with colour as the second channel: a ring for the way
# out, a cross for a crypt, a diamond for a chest, and a square with a pale
# outline for yourself.
edit(L, """  const mark = (x, y, c, r) => { if (!G.seen[Math.floor(y / T) * MW + Math.floor(x / T)]) return; mctx.fillStyle = c; mctx.fillRect(x / T * s - r / 2, y / T * s - r / 2, r, r); };
  mark(G.exit.x, G.exit.y, C.cyan, 4); for (const n of G.nests) mark(n.x, n.y, C.blood, 3); for (const i of G.items) if (i.kind === 'chest') mark(i.x, i.y, C.amber, 3);
  for (const P of G.players) { mctx.strokeStyle = 'rgba(235,228,210,.3)'; mctx.lineWidth = 1; mctx.beginPath(); mctx.arc(P.x / T * s, P.y / T * s, 7.5 * s, 0, TAU); mctx.stroke(); }
  for (const P of G.players) { mctx.fillStyle = P.down ? '#4a5166' : P.cls.col; mctx.fillRect(P.x / T * s - 2, P.y / T * s - 2, 4, 4); }""",
     """  const seenAt = (x, y) => !!G.seen[Math.floor(y / T) * MW + Math.floor(x / T)];
  const px = v => v / T * s;
  /* a ring: the way out */
  const markRing = (x, y, c) => {
    if (!seenAt(x, y)) return;
    mctx.strokeStyle = c; mctx.lineWidth = 1.5;
    mctx.beginPath(); mctx.arc(px(x), px(y), 2.6, 0, TAU); mctx.stroke();
    mctx.fillStyle = c; mctx.fillRect(px(x) - .5, px(y) - .5, 1, 1);
  };
  /* a cross: something to break */
  const markCross = (x, y, c) => {
    if (!seenAt(x, y)) return;
    const a = px(x), b = px(y), r = 2.4;
    mctx.strokeStyle = c; mctx.lineWidth = 1.4;
    mctx.beginPath();
    mctx.moveTo(a - r, b - r); mctx.lineTo(a + r, b + r);
    mctx.moveTo(a + r, b - r); mctx.lineTo(a - r, b + r);
    mctx.stroke();
  };
  /* a diamond: something to open */
  const markDiamond = (x, y, c) => {
    if (!seenAt(x, y)) return;
    const a = px(x), b = px(y), r = 3;
    mctx.fillStyle = c;
    mctx.beginPath(); mctx.moveTo(a, b - r); mctx.lineTo(a + r, b); mctx.lineTo(a, b + r); mctx.lineTo(a - r, b); mctx.fill();
  };
  markRing(G.exit.x, G.exit.y, C.cyan);
  for (const n of G.nests) markCross(n.x, n.y, C.blood);
  for (const i of G.items) if (i.kind === 'chest') markDiamond(i.x, i.y, C.amber);
  for (const P of G.players) { mctx.strokeStyle = 'rgba(235,228,210,.3)'; mctx.lineWidth = 1; mctx.beginPath(); mctx.arc(px(P.x), px(P.y), 7.5 * s, 0, TAU); mctx.stroke(); }
  /* and you are a square with a pale edge, so you are findable whatever
     delver you took and however you see colour */
  for (const P of G.players) {
    const a = px(P.x), b = px(P.y);
    mctx.fillStyle = P.down ? '#4a5166' : P.cls.col;
    mctx.fillRect(a - 2, b - 2, 4, 4);
    mctx.strokeStyle = P.down ? 'rgba(235,228,210,.5)' : '#ebe4d2';
    mctx.lineWidth = 1; mctx.strokeRect(a - 2.5, b - 2.5, 5, 5);
  }""")

run()
