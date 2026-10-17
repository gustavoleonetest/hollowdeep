from patch import edit, run

L = 'part_logic.js'

# --- 1. Might and Swiftness compounded, so a long run left the dungeon behind.
#        Measured over 48 simulated runs: damage reached 230,824,704x base.
#        Enemy health grows linearly with depth, so these grow linearly too.
edit(L, """  else if (id === 'swift') P.up.spd *= 1 + .1 * m;
  else if (id === 'power') P.up.dmg *= 1 + .2 * m;""",
     """  else if (id === 'swift') P.up.spd += .07 * m;
  else if (id === 'power') P.up.dmg += .2 * m;""")

# --- speed had a floor but no ceiling, and past ~2x you outrun your own aim
edit(L, """  P.spdMul = Math.max(.4, P.up.spd * g.spd);""",
     """  P.spdMul = clamp(P.up.spd * g.spd, .4, 1.95);""")

# --- 2. The drain was 68% of all health lost and 75% of deaths. It is meant to
#        be the clock, not the whole threat, so the deep slope eases off while
#        the early pressure stays exactly as it was.
edit(L, """  P.hp -= (.8 + G.level * .2) * (G.co ? .85 : 1) * (P.drainMul || 1) * dt;""",
     """  const dl = .8 + Math.min(G.level, 8) * .2 + Math.max(0, G.level - 8) * .07;
  P.hp -= dl * (G.co ? .85 : 1) * (P.drainMul || 1) * dt;""")

# --- 3. Bulwark reached median depth 3 where Sable reached 12. He was the
#        slowest delver in a game whose dominant threat is a clock, and the only
#        one who has to close the distance to deal any damage at all.
edit(L, """hp: 170, spd: 2.0, col: '#e7b04a', atk: 'melee', dmg: 18, cd: 0.4, range: 62, arc: 2.0, armor: 0.72""",
     """hp: 170, spd: 2.2, col: '#e7b04a', atk: 'melee', dmg: 18, cd: 0.4, range: 72, arc: 2.0, armor: 0.72, drain: -.15""")

# --- the class may now carry its own drain modifier
edit(L, """  P.drainMul = Math.max(.3, 1 + g.drain + (P.perkDrain || 0));""",
     """  P.drainMul = Math.max(.3, 1 + g.drain + (P.cls.drain || 0) + (P.perkDrain || 0));""")

run()
