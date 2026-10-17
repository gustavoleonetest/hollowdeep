from patch import edit, run

L = 'part_logic.js'

# A font has to pull you across a room, and at a glance it was reading as one
# more lit prop. A ring burnt into the floor carries much further than a
# vertical beam does in a top down view.
edit(L, """  const mys = sh.kind === 'mystery', want = sh.kind === 'pact';
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
  }""",
     """  const mys = sh.kind === 'mystery', want = sh.kind === 'pact';
  /* a ring burnt into the floor: this is what you see from across a hall */
  ctx.save();
  ctx.globalAlpha = .5 + pu * .3;
  ctx.strokeStyle = hexA(col, .8); ctx.lineWidth = 2.4;
  ctx.beginPath(); ctx.ellipse(it.x, it.y + 11, 34, 15, 0, 0, TAU); ctx.stroke();
  ctx.globalAlpha = .22 + pu * .16;
  ctx.strokeStyle = hexA(col, .6); ctx.lineWidth = 1.3;
  ctx.beginPath(); ctx.ellipse(it.x, it.y + 11, 44 + pu * 5, 20 + pu * 2, 0, 0, TAU); ctx.stroke();
  const fg = ctx.createRadialGradient(it.x, it.y + 11, 1, it.x, it.y + 11, Math.max(2, 40));
  fg.addColorStop(0, hexA(col, .3 + pu * .12)); fg.addColorStop(1, hexA(col, 0));
  ctx.fillStyle = fg; ctx.globalAlpha = 1;
  ctx.beginPath(); ctx.ellipse(it.x, it.y + 11, 42, 19, 0, 0, TAU); ctx.fill();
  ctx.restore();
  /* and a column of light above it, so it reads once you are close */
  const h = 96;
  const g = ctx.createLinearGradient(it.x, it.y - h, it.x, it.y + 8);
  g.addColorStop(0, hexA(col, 0)); g.addColorStop(.6, hexA(col, .16 + pu * .12)); g.addColorStop(1, hexA(col, .44 + pu * .16));
  ctx.fillStyle = g; ctx.fillRect(it.x - 17, it.y - h, 34, h + 8);
  glow(it.x, it.y - 4, 52 + pu * 12, col, .42 + pu * .2);
  shadow(it.x, it.y + 11, 15, 6, .36);
  if (!sprProp('altar', it.x, it.y + 11, 1.6, null, .75)) {
    ctx.fillStyle = '#4a4740'; ctx.fillRect(it.x - 14, it.y - 12, 28, 24);
    ctx.fillStyle = hexA(col, .75); ctx.fillRect(it.x - 11, it.y - 17, 22, 6);
  }""")

run()
