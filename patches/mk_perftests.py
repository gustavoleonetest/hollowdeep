import io

p = 'behave2_drive.js'
s = io.open(p, encoding='utf-8').read()
anchor = "const fails = results.filter(r => r[0] === 'FAIL');"
assert s.count(anchor) == 1

block = r"""/* ---------------- it thins itself on a slow device ---------------- */
{
  const resetPerf = () => { fxLevel = 0; PERF.ring.length = 0; PERF.at = 0; PERF.hold = 0; };
  const feed = (ms, frames) => { for (let i = 0; i < frames; i++) perfTick(ms); };

  startGame(['sable']); G.level = 3; genLevel();
  let gg = 0; while (G.offer && gg++ < 20) applyUpgrade(0); G.offerQ.length = 0; G.state = 'play';

  resetPerf();
  ok('a quick device draws everything', fxLevel === 0 && fxThin() === 1);

  feed(40, PERF.n * 2);
  ok('sustained slow frames thin the decoration', fxLevel > 0, 'level ' + fxLevel);
  const thinned = fxLevel;
  feed(40, PERF.n * 6);
  ok('and it keeps stepping down while it struggles', fxLevel > thinned || fxLevel === 2, 'level ' + fxLevel);
  ok('but never past the floor', fxLevel <= 2, 'level ' + fxLevel);

  feed(3, PERF.n * 8);
  ok('and climbs back when the device keeps up', fxLevel === 0, 'level ' + fxLevel);

  /* a couple of slow frames in a row is a hitch, not a slow device */
  resetPerf();
  feed(4, PERF.n);
  const before = fxLevel;
  for (let i = 0; i < 5; i++) perfTick(60);
  ok('a brief hitch is not treated as a slow device', fxLevel === before, 'level ' + fxLevel);

  /* and it must not flutter between levels frame to frame */
  resetPerf();
  let changes = 0, prev = fxLevel;
  for (let i = 0; i < PERF.n * 10; i++) { perfTick(i % 2 ? 40 : 3); if (fxLevel !== prev) { changes++; prev = fxLevel; } }
  ok('it cannot flutter between levels', changes <= 3, changes + ' changes over ' + (PERF.n * 10) + ' frames');

  /* menus are not the game, and must not be measured */
  resetPerf(); G.state = 'menu';
  feed(80, PERF.n * 4);
  ok('a slow menu does not thin the game', fxLevel === 0, 'level ' + fxLevel);
  G.state = 'play';

  /* what it changes is decoration, and only decoration */
  resetPerf();
  G.parts.length = 0; burst(100, 100, '#fff', 40, 100);
  const full = G.parts.length;
  fxLevel = 2;
  G.parts.length = 0; burst(100, 100, '#fff', 40, 100);
  const sparse = G.parts.length;
  ok('thinning means fewer particles', sparse < full, full + ' -> ' + sparse);
  ok('but never none at all', sparse > 0, sparse);

  /* the simulation must not notice */
  resetPerf();
  startGame(['thistle']); G.level = 4; genLevel();
  gg = 0; while (G.offer && gg++ < 20) applyUpgrade(0); G.offerQ.length = 0; G.state = 'play';
  const snap = () => ({ foes: G.enemies.length, crypts: G.nests.length, items: G.items.length,
                        hp: Math.round(G.players[0].hp), props: G.props.length });
  fxLevel = 0; const a0 = snap();
  fxLevel = 2; const a2 = snap();
  ok('thinning changes nothing the game runs on',
     JSON.stringify(a0) === JSON.stringify(a2), JSON.stringify(a2));
  { const P = G.players[0];
    fxLevel = 2; const h0 = P.hp;
    for (let i = 0; i < 60; i++) update(1 / 60);
    const lost2 = h0 - P.hp;
    fxLevel = 0; P.hp = h0;
    for (let i = 0; i < 60; i++) update(1 / 60);
    const lost0 = h0 - P.hp;
    ok('and the clock runs at the same rate either way', Math.abs(lost2 - lost0) < 1.5,
       lost0.toFixed(1) + ' vs ' + lost2.toFixed(1) + ' health in a second'); }
  fxLevel = 0;
}

"""

io.open(p, 'w', encoding='utf-8', newline='').write(s.replace(anchor, block + anchor))
print('adaptive-quality tests inserted')
