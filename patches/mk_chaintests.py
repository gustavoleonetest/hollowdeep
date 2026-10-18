import io

p = 'behave2_drive.js'
s = io.open(p, encoding='utf-8').read()
anchor = "const fails = results.filter(r => r[0] === 'FAIL');"
assert s.count(anchor) == 1, 'anchor not unique'
assert 'the chain nobody was testing' not in s, 'already inserted'

block = r"""/* ---------------- the chain nobody was testing ---------------- */
{
  /* The smoke run prints "best chain reached: 0", which looked like a dead
     mechanic. It is not -- it is the report that is wrong, since it reads
     G.comboBest at the very end and startGame has reset it by then. The
     mechanic itself had no coverage at all, so here it is: kills within
     3.2 seconds of each other build a chain, the chain multiplies score,
     being hit halves it, and a warden does not count towards it. */
  const quiet = () => { G.enemies.length = 0; G.eshots.length = 0; G.shots.length = 0;
                        G.hazards.length = 0; G.items.length = 0; };
  const slay = (type, elite) => {
    const P = G.players[0];
    spawnFoe(type || 'gloam', P.x + 40, P.y, !!elite);
    const e = G.enemies[G.enemies.length - 1];
    hurtFoe(e, e.max * 10 + 9999, 0, false, false, P);
    return e;
  };

  startGame(['sable']); G.level = 4; genLevel();
  G.offer = null; G.offerQ.length = 0; G.state = 'play'; quiet();
  G.combo = 0; G.comboT = 0; G.comboBest = 0;

  /* 1. it builds */
  for (let i = 0; i < 6; i++) slay('gloam');
  ok('killing in quick succession builds a chain', G.combo === 6, 'chain ' + G.combo);
  ok('and the run remembers the longest one', G.comboBest === 6, 'best ' + G.comboBest);

  /* 2. it is worth something: the same foe, chained and unchained */
  {
    G.combo = 0; G.comboT = 0;
    let before = G.score; slay('gloam'); const plain = G.score - before;
    G.combo = 30; G.comboT = 3.2;             /* past the cap on purpose */
    before = G.score; slay('gloam'); const chained = G.score - before;
    ok('a chained kill scores more than a lone one', chained > plain,
       plain + ' -> ' + chained);
    ok('and the multiplier stops at two and a half', Math.abs(comboMult() - 2.6) < 1e-9,
       'x' + comboMult().toFixed(2) + ' at a chain of ' + G.combo);
    ok('which is what the kill was actually paid', Math.abs(chained / plain - 2.6) < .02,
       (chained / plain).toFixed(3) + 'x');
  }

  /* 3. it lapses if you stop */
  {
    G.combo = 9; G.comboT = 3.2; quiet();
    for (let i = 0; i < 180; i++) { update(1 / 60); quiet(); }   /* three seconds */
    const stillUp = G.combo;
    for (let i = 0; i < 30; i++) { update(1 / 60); quiet(); }    /* past 3.2 */
    ok('a chain outlives a short pause', stillUp === 9, 'chain ' + stillUp + ' after 3.0s');
    ok('and lapses once you stop killing', G.combo === 0, 'chain ' + G.combo + ' after 3.5s');
  }

  /* 4. being hit costs you half of it */
  {
    const P = G.players[0];
    G.combo = 10; G.comboT = 3.2; P.inv = 0; P.hp = P.max;
    hurtPlayer(P, 6, 0);
    ok('taking a hit halves the chain', G.combo === 5, 'chain ' + G.combo);
    G.combo = 1; G.comboT = 3.2; P.inv = 0;
    hurtPlayer(P, 6, 0);
    ok('and a chain of one is lost outright', G.combo === 0 && G.comboT === 0,
       'chain ' + G.combo + ', timer ' + G.comboT);
  }

  /* 5. a warden is not a link in it */
  {
    G.combo = 4; G.comboT = 3.2; quiet();
    const P = G.players[0];
    spawnFoe('gloam', P.x + 40, P.y); const b = G.enemies[G.enemies.length - 1];
    b.boss = true; b.kind = 'count';
    const was = G.combo;
    hurtFoe(b, b.max * 10 + 9999, 0, false, false, P);
    ok('killing a warden does not add to the chain', G.combo === was, was + ' -> ' + G.combo);
  }

  /* 6. the HUD shows it only once there is one */
  {
    G.combo = 1; updateHud();
    const hiddenAtOne = hud.comboBox.hidden;
    G.combo = 2; G.comboT = 3.2; updateHud();
    const shownAtTwo = !hud.comboBox.hidden, label = hud.combo.textContent;
    ok('a chain of one is not worth announcing', hiddenAtOne);
    ok('a chain of two is', shownAtTwo && /^2×/.test(label), label);
  }

  /* 7. the longest chain is a line on the death screen, so it has to survive
        the whole descent rather than being reset by each new floor */
  {
    G.combo = 0; G.comboT = 0; G.comboBest = 0; quiet();
    for (let i = 0; i < 7; i++) slay('gloam');
    const peak = G.comboBest;
    G.offer = null; G.offerQ.length = 0; nextLevel();
    ok('the longest chain survives taking the stairs', G.comboBest === peak && peak === 7,
       'best ' + G.comboBest + ' after reaching depth ' + G.level);
    ok('even though the chain itself does not', G.combo === 0, 'chain ' + G.combo);
  }
}

"""

io.open(p, 'w', encoding='utf-8', newline='').write(s.replace(anchor, block + anchor))
print('chain tests inserted')
