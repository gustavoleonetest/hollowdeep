from patch import edit, run

L = 'part_logic.js'

# --- kills must pay experience, and the new monsters need score values.
#     Without them the table lookup is undefined and the score goes NaN. ----
edit(L, """  const base = { gloam: 10, wisp: 8, bonewalker: 15, brute: 40, hound: 14, bloat: 22, warden: 500 }[e.type] * (e.elite ? 3 : 1);
  if (!e.boss) { G.combo++; G.comboT = 3.2; if (G.combo > G.comboBest) G.comboBest = G.combo; }
  G.score += Math.round(base * comboMult());""",
     """  const base = ({ gloam: 10, wisp: 8, bonewalker: 15, brute: 40, hound: 14, bloat: 22, thief: 45, reaper: 120, warden: 500 }[e.type] || 10) * (e.elite ? 3 : 1);
  if (!e.boss) { G.combo++; G.comboT = 3.2; if (G.combo > G.comboBest) G.comboBest = G.combo; }
  G.score += Math.round(base * comboMult());
  gainXp(Math.max(1, Math.round(base * (.5 + G.level * .05))));""")

# --- recalc already heals for the max-health gain; don't heal twice -------
edit(L, """  recalc(P);
  if (id === 'vit') P.hp = Math.min(P.max, P.hp + Math.round(25 * m));
  const info = upInfo(P, id, m);""",
     """  recalc(P);
  const info = upInfo(P, id, m);""")

run()
