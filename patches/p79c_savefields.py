from patch import edit, run

L = 'part_logic.js'

# Two of the things being saved could never come back, because the floor
# itself decides them a moment later: genLevel hands out the key (none,
# unless the gilded omen is up) and picks up anyone who had fallen, at half
# health. Storing them made the save look as though it carried more than it
# does. A save format is a promise; it should not contain fields that are
# quietly overruled.
edit(L, """      v: 1, cls: G.clsKeys, level: G.level, score: G.score, gold: G.gold, keys: G.keys,
      bombs: G.bombs, kills: G.kills, drops: G.drops, runT: G.runT, comboBest: G.comboBest, won: !!G.won,
      ps: G.players.map(P => ({
        hp: P.hp, down: !!P.down, up: P.up, gear: P.gear, xp: P.xp, plvl: P.plvl,
        buys: P.buys, boons: P.boons, pacts: (P.pacts || []).map(p => p.id)
      }))""",
     """      v: 1, cls: G.clsKeys, level: G.level, score: G.score, gold: G.gold,
      bombs: G.bombs, kills: G.kills, drops: G.drops, runT: G.runT, comboBest: G.comboBest, won: !!G.won,
      /* no key and no fallen: the floor that is about to be built hands out
         its own key and sets anyone down back on their feet */
      ps: G.players.map(P => ({
        hp: P.hp, up: P.up, gear: P.gear, xp: P.xp, plvl: P.plvl,
        buys: P.buys, boons: P.boons, pacts: (P.pacts || []).map(p => p.id)
      }))""")

edit(L, """    cls: cls.slice(), level: lvl, score: metaNum(raw.score, 0, 0), gold: metaNum(raw.gold, 0, 0),
    keys: metaNum(raw.keys, 0, 0), bombs: metaNum(raw.bombs, 0, 0), kills: metaNum(raw.kills, 0, 0),""",
     """    cls: cls.slice(), level: lvl, score: metaNum(raw.score, 0, 0), gold: metaNum(raw.gold, 0, 0),
    bombs: metaNum(raw.bombs, 0, 0), kills: metaNum(raw.kills, 0, 0),""")

edit(L, """      hp: num(p.hp, 1), down: !!p.down,
      up: {""",
     """      hp: num(p.hp, 1),
      up: {""")

edit(L, """    recalc(P);
    P.down = s.down && r.cls.length > 1;
    P.hp = P.down ? 0 : Math.max(1, Math.min(P.max, s.hp));
  });""",
     """    recalc(P);
    P.hp = Math.max(1, Math.min(P.max, s.hp));
  });""")

edit(L, """  G.gold = r.gold; G.keys = r.keys; G.bombs = r.bombs; G.kills = r.kills; G.drops = r.drops;""",
     """  G.gold = r.gold; G.bombs = r.bombs; G.kills = r.kills; G.drops = r.drops;""")

run()
