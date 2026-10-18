import io

p = 'behave2_drive.js'
s = io.open(p, encoding='utf-8').read()
anchor = "const fails = results.filter(r => r[0] === 'FAIL');"
assert s.count(anchor) == 1, 'anchor not unique'
assert 'what actually took you' not in s, 'already inserted'

block = r"""/* ---------------- what actually took you ---------------- */
{
  const quiet = () => { G.enemies.length = 0; G.nests.length = 0; G.eshots.length = 0;
                        G.shots.length = 0; G.hazards.length = 0; G.items.length = 0; };

  /* 1. the drain's toll is the drain, to the number */
  startGame(['bulwark']); G.level = 6; genLevel();
  G.offer = null; G.offerQ.length = 0; G.state = 'play'; quiet();
  {
    const P = G.players[0]; P.hp = P.max; P.inv = 999;
    G.tollDeep = 0; G.tollFoes = 0;
    const rate = drainRate(P);
    for (let i = 0; i < 120; i++) { update(1 / 60); quiet(); }
    ok('the deep’s toll is what the deep took', Math.abs(G.tollDeep - rate * 2) < .05,
       G.tollDeep.toFixed(2) + ' vs ' + (rate * 2).toFixed(2));
    ok('and nothing is blamed on the creatures', G.tollFoes === 0, String(G.tollFoes));
  }

  /* 2. a blow is counted after armour, not before */
  {
    const P = G.players[0]; P.hp = P.max; P.inv = 0;
    G.tollDeep = 0; G.tollFoes = 0;
    const before = P.hp;
    hurtPlayer(P, 40, 0);
    const actuallyLost = before - P.hp;
    ok('a blow is counted as it landed, not as it was thrown',
       Math.abs(G.tollFoes - actuallyLost) < 1e-9 && actuallyLost < 40,
       'thrown 40, landed ' + actuallyLost.toFixed(1) + ', counted ' + G.tollFoes.toFixed(1));
  }

  /* 3. the reaper eats through armour and invulnerability, so it never goes
        near hurtPlayer: the obvious place to instrument would have missed it */
  {
    startGame(['ember']); G.level = 8; genLevel();
    G.offer = null; G.offerQ.length = 0; G.state = 'play'; quiet();
    const P = G.players[0]; P.hp = P.max; P.inv = 999;
    G.tollDeep = 0; G.tollFoes = 0;
    spawnFoe('reaper', P.x, P.y);
    const before = P.hp;
    for (let i = 0; i < 30; i++) { update(1 / 60); G.items.length = 0; }
    const lost = before - P.hp;
    ok('being devoured counts, though it never touches hurtPlayer',
       G.tollFoes > 0 && lost > 0, 'lost ' + lost.toFixed(1) + ', of which creatures ' + G.tollFoes.toFixed(1));
    ok('and the drain is not blamed for the reaper’s share',
       G.tollDeep < lost, 'deep ' + G.tollDeep.toFixed(1) + ' of ' + lost.toFixed(1));
    ok('the two together are the whole of what was lost',
       Math.abs((G.tollDeep + G.tollFoes) - lost) < .05,
       (G.tollDeep + G.tollFoes).toFixed(2) + ' vs ' + lost.toFixed(2));
  }

  /* 4. the killing blow adds what it took, not what it threw */
  {
    startGame(['sable']); G.level = 3; genLevel();
    G.offer = null; G.offerQ.length = 0; G.state = 'play'; quiet();
    const P = G.players[0];
    P.hp = 5; P.inv = 0; G.tollDeep = 0; G.tollFoes = 0;
    hurtPlayer(P, 9999, 0);
    ok('an overkill is counted as the health it actually took', G.tollFoes <= 5 + 1e-9,
       'had 5, counted ' + G.tollFoes.toFixed(2));
    ok('and never as a negative share of the run', G.tollFoes >= 0 && G.tollDeep >= 0);
  }

  /* 5. it survives carrying a run on, and an older save simply has none */
  {
    startGame(['thistle']); G.level = 2; genLevel();
    G.offer = null; G.offerQ.length = 0; G.state = 'play'; quiet();
    G.tollDeep = 123.5; G.tollFoes = 44.25;
    saveRun();
    const back = loadRun();
    ok('the tally is kept when a run is carried on',
       !!back && Math.abs(back.tollDeep - 123.5) < 1e-9 && Math.abs(back.tollFoes - 44.25) < 1e-9,
       back ? back.tollDeep + ' / ' + back.tollFoes : 'nothing');
    resumeRun(back);
    ok('and is still there once it is', Math.abs(G.tollDeep - 123.5) < 1e-9,
       G.tollDeep + ' / ' + G.tollFoes);

    /* a save written before this existed has no such fields at all */
    const old = JSON.parse(localStorage.getItem('hollowdeep-run'));
    delete old.tollDeep; delete old.tollFoes;
    localStorage.setItem('hollowdeep-run', JSON.stringify(old));
    const older = loadRun();
    ok('a save from before this existed loads with an empty tally',
       !!older && older.tollDeep === 0 && older.tollFoes === 0,
       older ? older.tollDeep + ' / ' + older.tollFoes : 'refused outright');
    clearRun();
  }

  /* 6. a new run starts from nothing */
  {
    G.tollDeep = 500; G.tollFoes = 500;
    startGame(['bulwark']);
    ok('a new descent starts the tally again', G.tollDeep === 0 && G.tollFoes === 0,
       G.tollDeep + ' / ' + G.tollFoes);
  }

  /* 7. and it reaches the death screen */
  {
    startGame(['ember']); G.level = 5; genLevel();
    G.offer = null; G.offerQ.length = 0; G.state = 'play'; quiet();
    G.tollDeep = 300; G.tollFoes = 100;
    die(); showOver();
    const rows = [...$('oStats').children].map(r => r.textContent);
    const line = rows.find(t => /took you|wore you down/.test(t));
    ok('the death screen says what took you', !!line, line || rows.join(' | ').slice(0, 120));
    ok('and gets the share right', !!line && /75%/.test(line) && /25%/.test(line), line || '-');
    /* nothing to say when nothing was lost */
    startGame(['ember']); G.tollDeep = 0; G.tollFoes = 0; G.state = 'dead'; showOver();
    const none = [...$('oStats').children].map(r => r.textContent)
      .some(t => /took you|wore you down/.test(t));
    ok('and keeps quiet when a run cost nothing', !none);
  }
}

"""

io.open(p, 'w', encoding='utf-8', newline='').write(s.replace(anchor, block + anchor))
print('toll tests inserted')
