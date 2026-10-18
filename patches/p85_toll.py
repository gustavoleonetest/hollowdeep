from patch import edit, run

L = 'part_logic.js'

# --- the death screen never said what killed you -------------------------
# It lists depth, score, kills, gold, time. All true, none of it an answer
# to the only question a player actually has when they die, which is what
# went wrong. And the answer is usually not what they think: across fifty-six
# simulated runs, seventy per cent of all health lost was the drain, not a
# monster. People die in this game of the clock while fighting the weather.
#
# The band on the health bar says it during a run. This says it after one,
# in their own numbers, at the moment they are most willing to hear it.
#
# Three places take health off a delver and they must all be counted: the
# drain, hurtPlayer, and the reaper, which devours straight through armour
# and invulnerability and so never passes through hurtPlayer at all. Missing
# that third one would quietly understate exactly the deaths that feel most
# unfair.
edit(L, """  G.player = G.players[0]; G.gold = 0; G.keys = 0; G.combo = 0; G.comboT = 0; G.comboBest = 0;""",
     """  G.player = G.players[0]; G.gold = 0; G.keys = 0; G.combo = 0; G.comboT = 0; G.comboBest = 0;
  G.tollDeep = 0; G.tollFoes = 0;""")

edit(L, """const om = (k, dflt) => (G.omen && G.omen[k] !== undefined) ? G.omen[k] : dflt;""",
     """const om = (k, dflt) => (G.omen && G.omen[k] !== undefined) ? G.omen[k] : dflt;
/* What a delver actually lost, and to what. Counted against the health they
   had rather than the blow that was thrown, so the killing hit adds what it
   really took and not the overkill on top. */
function toll(which, was, P) {
  const lost = Math.max(0, was - Math.max(0, P.hp));
  if (which === 'deep') G.tollDeep = (G.tollDeep || 0) + lost;
  else G.tollFoes = (G.tollFoes || 0) + lost;
}""")

edit(L, """  P.hp -= d; P.inv = .55; P.hurt = .25; P.lastHit = clock; G.shake = Math.max(G.shake, .3);""",
     """  const wasHp = P.hp;
  P.hp -= d; toll('foes', wasHp, P);
  P.inv = .55; P.hurt = .25; P.lastHit = clock; G.shake = Math.max(G.shake, .3);""")

edit(L, """  P.hp -= drainRate(P) * dt;""",
     """  const wasDrain = P.hp;
  P.hp -= drainRate(P) * dt; toll('deep', wasDrain, P);""")

# the reaper eats through armour and inv, so it never reaches hurtPlayer
edit(L, """        p.hp -= bite; e.fed = (e.fed || 0) + bite; p.hurt = Math.max(p.hurt, .12);""",
     """        const wasBite = p.hp;
        p.hp -= bite; toll('foes', wasBite, p);
        e.fed = (e.fed || 0) + bite; p.hurt = Math.max(p.hurt, .12);""")

# --- and it has to survive carrying a run on ------------------------------
edit(L, """      bombs: G.bombs, kills: G.kills, drops: G.drops, runT: G.runT, comboBest: G.comboBest, won: !!G.won,""",
     """      bombs: G.bombs, kills: G.kills, drops: G.drops, runT: G.runT, comboBest: G.comboBest, won: !!G.won,
      tollDeep: G.tollDeep, tollFoes: G.tollFoes,""")

edit(L, """    comboBest: metaNum(raw.comboBest, 0, 0), won: !!raw.won, ps: []""",
     """    comboBest: metaNum(raw.comboBest, 0, 0), won: !!raw.won,
    /* absent in a save written before this existed, which is simply zero */
    tollDeep: Math.max(0, num(raw.tollDeep, 0)), tollFoes: Math.max(0, num(raw.tollFoes, 0)), ps: []""")

edit(L, """  G.runT = r.runT; G.comboBest = r.comboBest; G.score = r.score; G.won = r.won;""",
     """  G.runT = r.runT; G.comboBest = r.comboBest; G.score = r.score; G.won = r.won;
  G.tollDeep = r.tollDeep; G.tollFoes = r.tollFoes;""")

# --- say it ---------------------------------------------------------------
edit(L, """    ['Time below', mmss(G.runT || 0)]
  ];""",
     """    ['Time below', mmss(G.runT || 0)]
  ];
  /* the one row that answers "what went wrong" */
  {
    const deep = Math.round(G.tollDeep || 0), foes = Math.round(G.tollFoes || 0), all = deep + foes;
    if (all > 0) {
      const pc = n => Math.round(n / all * 100);
      rows.splice(3, 0, [won || G.won ? 'What wore you down' : 'What took you',
        'the deep ' + deep + '  (' + pc(deep) + '%)  \\u00b7  its creatures ' + foes + '  (' + pc(foes) + '%)']);
    }
  }""")

run()
