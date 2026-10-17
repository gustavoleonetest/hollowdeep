import io

p = 'behave2_drive.js'
s = io.open(p, encoding='utf-8').read()

# The first cut of these checks read `want` AFTER the descent loop, so the
# loop's own effects had already overwritten what the test set: nextLevel
# heals to full, which made "the health you had" compare 187 to 187, and
# genLevel clears the key, which made "the key you held" compare 0 to 0.
# Both would have passed had resume handed out a free refill.
old = """  G.gold = 321; G.keys = 1; G.bombs = 3; G.kills = 77; G.score = 4210;
  let guard = 0;
  while (G.level < 4 && guard++ < 12) { G.offer = null; G.offerQ.length = 0; nextLevel(); }

  const want = {
    level: G.level, gold: G.gold, keys: G.keys, bombs: G.bombs, kills: G.kills, score: G.score,
    plvl: P0.plvl, dmg: P0.up.dmg, max: P0.max, hp: P0.hp,
    weapon: P0.gear.weapon.name, pacts: P0.pacts.length, boons: Object.keys(P0.boons).length
  };
"""
new = """  let guard = 0;
  while (G.level < 4 && guard++ < 12) { G.offer = null; G.offerQ.length = 0; nextLevel(); }
  /* set the run's state AFTER descending, then checkpoint deliberately:
     nextLevel heals to full and genLevel clears the key, so anything set
     before the loop is not the thing being tested */
  G.gold = 321; G.bombs = 3; G.kills = 77; G.score = 4210;
  P0.hp = P0.max * .41;
  saveRun();

  const want = {
    level: G.level, gold: G.gold, bombs: G.bombs, kills: G.kills, score: G.score,
    plvl: P0.plvl, dmg: P0.up.dmg, max: P0.max, hp: P0.hp,
    weapon: P0.gear.weapon.name, pacts: P0.pacts.length, boons: Object.keys(P0.boons).length
  };
  ok('the health being saved is not already full', want.hp < want.max - 1, want.hp.toFixed(1) + '/' + want.max);
"""
assert s.count(old) == 1, 'setup anchor not unique'
s = s.replace(old, new)

old2 = """  ok('holding the gold, the key and the flasks',
     G.gold === want.gold && G.keys === want.keys && G.bombs === want.bombs,
     G.gold + 'g ' + G.keys + 'k ' + G.bombs + 'f');"""
new2 = """  ok('holding the gold and the flasks it had',
     G.gold === want.gold && G.bombs === want.bombs, G.gold + 'g ' + G.bombs + 'f');
  /* the key is deliberately NOT carried: a fresh floor hides its own */
  ok('but not a key, because the new floor hides its own',
     G.keys === (om('freeKey', false) ? 1 : 0), 'holding ' + G.keys);"""
assert s.count(old2) == 1, 'gold anchor not unique'
s = s.replace(old2, new2)

old3 = """  ok('and the health is what you had, not a free refill', Math.abs(R.hp - want.hp) < 1e-6,
     R.hp.toFixed(1) + ' vs ' + want.hp.toFixed(1));"""
new3 = """  ok('and the health is what you had, not a free refill', Math.abs(R.hp - want.hp) < 1e-6,
     R.hp.toFixed(1) + ' vs ' + want.hp.toFixed(1));
  ok('which is not simply full health', R.hp < R.max - 1, R.hp.toFixed(1) + '/' + R.max);"""
assert s.count(old3) == 1, 'health anchor not unique'
s = s.replace(old3, new3)

io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('resume tests sharpened')
