from patch import edit, run

L = 'part_logic.js'
DOT = chr(92) + 'u00b7'   # the JS escape as it appears in the source

# Every boss depth announced "a count", whichever boss was actually waiting,
# and the shop said the same on the way down.
edit(L,
     "isBossLvl(G.level) ? ' " + DOT + " a count guards the key' : G.omen ? ' " + DOT + " ' + G.omen.name : ''",
     "isBossLvl(G.level) ? ' " + DOT + " ' + G.zone.boss + ' guards the key' : G.omen ? ' " + DOT + " ' + G.omen.name : ''")

edit(L,
     "(isBossLvl(nxt) ? ', where a count guards the key.' : '.')",
     "(isBossLvl(nxt) ? ', where ' + ZONES[Math.floor((nxt - 1) / 3) % ZONES.length].boss + ' guards the key.' : '.')")

run()
