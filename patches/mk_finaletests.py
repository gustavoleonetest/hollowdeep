import io

p = 'behave2_drive.js'
s = io.open(p, encoding='utf-8').read()
anchor = "const fails = results.filter(r => r[0] === 'FAIL');"
assert s.count(anchor) == 1

block = r"""/* ---------------- something to beat ---------------- */
{
  const atDepth = (d) => {
    startGame(['thistle']); G.level = d; genLevel();
    let g = 0; while (G.offer && g++ < 20) applyUpgrade(0); G.offerQ.length = 0; G.state = 'play';
    return G.enemies.find(e => e.boss);
  };
  ok('the descent has a bottom', typeof FINAL_DEPTH === 'number' && FINAL_DEPTH > 0, 'depth ' + FINAL_DEPTH);
  ok('and it lands on a boss depth', isBossLvl(FINAL_DEPTH), String(FINAL_DEPTH));
  ok('every depth above it is ordinary', [3, 6, 9, 12, 15, 18].every(d => !isFinalLvl(d)));

  const H = atDepth(FINAL_DEPTH);
  ok('the last depth puts the Heart in the way', !!H && H.kind === 'heart', H && H.kind);
  ok('and names it', !!H && H.name === HEART_NAME, H && H.name);
  const W = atDepth(18);
  ok('while eighteen still holds its own warden', !!W && W.kind !== 'heart', W && W.kind);
  ok('the Heart is the harder of the two', !!H && !!W && H.max > W.max * 1.5, (W ? W.max : 0) + ' -> ' + (H ? H.max : 0) + ' health');
  ok('and hits harder', !!H && !!W && H.dmg > W.dmg, (W ? W.dmg : 0) + ' -> ' + (H ? H.dmg : 0));

  /* every attack it can throw must be one the engine knows how to time */
  const hacts = [...new Set([].concat(BOSSES.heart.acts[1], BOSSES.heart.acts[2], BOSSES.heart.acts[3]))];
  ok('the Heart only throws attacks the engine times', hacts.every(a => BOSS_DUR[a] !== undefined),
     hacts.filter(a => BOSS_DUR[a] === undefined).join(',') || hacts.length + ' attacks');
  ok('and it remembers more of them than any warden', hacts.length > Math.max(...BOSS_KIND.map(k =>
     new Set([].concat(BOSSES[k].acts[1], BOSSES[k].acts[2], BOSSES[k].acts[3])).size)),
     hacts.length + ' attacks');

  /* the door is not a second wall down there */
  { atDepth(FINAL_DEPTH);
    ok('you hold the key on the last depth', G.keys >= 1, 'keys=' + G.keys); }

  /* every one of its attacks resolves, driven directly */
  { const B = atDepth(FINAL_DEPTH);
    const room = G.rooms.reduce((a, b) => (b.w * b.h > a.w * a.h ? b : a), G.rooms[0]);
    const stuck = [];
    for (const act of hacts) {
      B.hp = B.max * .2; B.cd = 0; B.alert = true; B.kx = 0; B.ky = 0;
      B.immune = false; B.wardT = undefined; B.wardAdds = null;
      B.x = room.cx * T + T / 2; B.y = room.cy * T + T / 2;
      G.players.forEach(pl => { pl.down = false; pl.hp = pl.max; pl.inv = 1e9; pl.x = B.x + 40; pl.y = B.y; });
      B.st = act; B.stt = 0; B.ca = 1;
      buildFlow();
      let back = false;
      for (let i = 0; i < 500; i++) {
        updateEnemies(1 / 60); updateShots(1 / 60); updateFx(1 / 60);
        G.players.forEach(pl => { pl.hp = pl.max; });
        if (B.st === 'chase') { back = true; break; }
      }
      if (!back) stuck.push(act);
    }
    ok('and every one of them resolves', stuck.length === 0, stuck.join(',') || 'all clear'); }

  /* putting it down wins the run */
  { const wins0 = META.wins || 0;
    const B = atDepth(FINAL_DEPTH);
    G.won = false;
    hurtFoe(B, B.max * 10, 0, false, false, G.players[0]);
    for (let i = 0; i < 6; i++) updateEnemies(1 / 60);
    ok('putting the Heart down wins the run', G.won === true);
    ok('and the win is remembered', (META.wins || 0) === wins0 + 1, wins0 + ' -> ' + (META.wins || 0));
    ok('it drops no key, because there is nowhere left to unlock', !G.items.some(i => i.kind === 'key'));
    ok('but it does pay out', G.items.filter(i => i.kind === 'chest').length >= 3,
       G.items.filter(i => i.kind === 'chest').length + ' chests');
    /* the victory screen is its own state, so the player chooses what next */
    for (let i = 0; i < 60 * 4; i++) updateFx(1 / 60);
    ok('and the run stops for a victory screen', G.state === 'won', G.state); }

  /* an ordinary boss still just drops a key */
  { const B = atDepth(18); G.won = false;
    hurtFoe(B, B.max * 10, 0, false, false, G.players[0]);
    for (let i = 0; i < 6; i++) updateEnemies(1 / 60);
    ok('an ordinary warden still only drops a key', G.items.some(i => i.kind === 'key') && G.won === false); }

  /* a won run banks more, and only once */
  { startGame(['sable']); G.level = 12; G.score = 1000; G.gold = 400;
    G.won = false; const e0 = META.echoes; die(); const plain = META.echoes - e0;
    startGame(['sable']); G.level = 12; G.score = 1000; G.gold = 400;
    G.won = true; const e1 = META.echoes; die(); const won = META.echoes - e1;
    ok('a won run is worth more echoes', won > plain, plain + ' -> ' + won);
    const e2 = META.echoes; die(); die();
    ok('and a run can only be banked once', META.echoes === e2, 'held at ' + META.echoes); }
}

"""

io.open(p, 'w', encoding='utf-8', newline='').write(s.replace(anchor, block + anchor))
print('finale tests inserted')
