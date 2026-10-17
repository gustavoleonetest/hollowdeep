from patch import edit, run

L = 'part_logic.js'

# The new layouts carry more rooms than the old ribbon did, which quietly raised
# the crypt count per depth. Leave some rooms without one: it holds the old
# pressure and gives a run somewhere to breathe between fights.
edit(L, """    const nn = Math.min(3, rint(1, 1 + Math.floor(G.level / 2)) + (r.w * r.h > 60 ? 1 : 0) + (r.kind === 'arena' ? 1 : 0));
    for (let k = 0; k < nn; k++) { const p = roomPoint(r); G.nests.push({ x: p.x, y: p.y, r: 15, hp: 70 + G.level * 14, max: 70 + G.level * 14, t: rnd(.5, 2.5), flash: 0 }); }
    for (let k = rint(1, 3) + (r.kind === 'arena' ? 2 : 0); k > 0; k--) { const p = roomPoint(r); spawnFoe(pickFoe(), p.x, p.y); }
    if (r.kind === 'arena' && G.level >= 2) { const p = roomPoint(r); spawnFoe(pickFoe(), p.x, p.y, true); }""",
     """    if (r.kind !== 'arena' && Math.random() < .3) r.quiet = true;
    const nn = r.quiet ? 0 : Math.min(3, rint(1, 1 + Math.floor(G.level / 2)) + (r.w * r.h > 60 ? 1 : 0) + (r.kind === 'arena' ? 1 : 0));
    for (let k = 0; k < nn; k++) { const p = roomPoint(r); G.nests.push({ x: p.x, y: p.y, r: 15, hp: 70 + G.level * 14, max: 70 + G.level * 14, t: rnd(.5, 2.5), flash: 0 }); }
    for (let k = rint(1, 3) + (r.kind === 'arena' ? 2 : 0); k > 0; k--) { const p = roomPoint(r); spawnFoe(pickFoe(), p.x, p.y); }
    if (r.kind === 'arena' && G.level >= 3 && Math.random() < .7) { const p = roomPoint(r); spawnFoe(pickFoe(), p.x, p.y, true); }""")

# A trap you cannot see until it fires is not a trap, it is a tax. Keep the
# plate legible while it is down so the warning beat is a reminder, not a reveal.
edit(L, """  ctx.fillStyle = 'rgba(6,8,14,.5)'; ctx.beginPath(); ctx.ellipse(0, 2, h.r, h.r * .5, 0, 0, TAU); ctx.fill();
  ctx.strokeStyle = warn ? 'rgba(255,120,80,' + (.4 + .45 * Math.sin(clock * 24)) + ')' : 'rgba(141,147,168,.3)';
  ctx.lineWidth = warn ? 2 : 1.3; ctx.beginPath(); ctx.ellipse(0, 2, h.r - 1.5, (h.r - 1.5) * .5, 0, 0, TAU); ctx.stroke();
  ctx.fillStyle = 'rgba(141,147,168,.18)';
  for (let i = 0; i < 4; i++) { const a = i / 4 * TAU + .4; ctx.beginPath(); ctx.ellipse(Math.cos(a) * 6.5, Math.sin(a) * 3.2 + 2, 2.6, 1.4, 0, 0, TAU); ctx.fill(); }""",
     """  ctx.fillStyle = 'rgba(6,8,14,.62)'; ctx.beginPath(); ctx.ellipse(0, 2, h.r, h.r * .5, 0, 0, TAU); ctx.fill();
  ctx.strokeStyle = warn ? 'rgba(255,120,80,' + (.45 + .45 * Math.sin(clock * 24)) + ')' : 'rgba(176,184,206,.6)';
  ctx.lineWidth = warn ? 2.2 : 1.6; ctx.beginPath(); ctx.ellipse(0, 2, h.r - 1.5, (h.r - 1.5) * .5, 0, 0, TAU); ctx.stroke();
  ctx.strokeStyle = 'rgba(10,13,20,.5)'; ctx.lineWidth = 1; ctx.beginPath(); ctx.ellipse(0, 2, h.r - 4, (h.r - 4) * .5, 0, 0, TAU); ctx.stroke();
  ctx.fillStyle = warn ? 'rgba(255,150,110,.5)' : 'rgba(176,184,206,.34)';
  for (let i = 0; i < 4; i++) { const a = i / 4 * TAU + .4; ctx.beginPath(); ctx.ellipse(Math.cos(a) * 6.5, Math.sin(a) * 3.2 + 2, 2.8, 1.5, 0, 0, TAU); ctx.fill(); }""")

run()
