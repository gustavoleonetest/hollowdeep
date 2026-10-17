import io

p = 'behave2_drive.js'
s = io.open(p, encoding='utf-8').read()
anchor = "const fails = results.filter(r => r[0] === 'FAIL');"
assert s.count(anchor) == 1

block = r"""/* ---------------- the scenery ---------------- */
{
  const atlas = new Set();
  for (const meta of [SPR_META, SPR_META2])
    for (const k in meta) if (meta[k].frames) for (const f in meta[k].frames) atlas.add(f);

  /* a misspelt prop name draws nothing at all and says nothing about it */
  { const bad = [];
    PROP_POOL.forEach((pool, zone) => pool.forEach(e => { if (!atlas.has(e[0])) bad.push('zone' + zone + ':' + e[0]); }));
    ok('every prop a zone can roll exists in the atlas', bad.length === 0, bad.join(' ') || atlas.size + ' frames'); }

  { const thin = PROP_POOL.map((p, i) => [i, p.length]).filter(([, n]) => n < 8);
    ok('every zone has scenery to draw from', thin.length === 0, thin.map(([i, n]) => 'zone' + i + '=' + n).join(' ') || PROP_POOL.map(p => p.length).join('/')); }

  /* the furniture is meant to land where a room of that kind would have had it */
  const poolHas = (zone, name) => PROP_POOL[zone].some(e => e[0] === name);
  ok('the stores are furnished', ['p_table', 'p_bench', 'p_stool', 'p_crate_metal'].every(n => poolHas(1, n)));
  ok('the forge has a bench to work at', poolHas(3, 'p_bench') && poolHas(3, 'p_crate_metal'));
  ok('the sanctum has shelves and glassware', poolHas(5, 'r_bookcase') && poolHas(5, 'p_bottles'));
  ok('the graves get candles', poolHas(0, 'r_candles') && poolHas(4, 'r_candles'));

  /* and it must actually reach the floor, not just the table of possibilities */
  { const seen = new Set();
    for (let r = 0; r < 40; r++) { startGame(['sable']); G.level = 5; genLevel(); for (const q of G.props) seen.add(q.k); }
    const furniture = ['p_table', 'p_bench', 'p_stool', 'p_chair', 'p_crate_metal', 'p_chest_wood', 'p_stall', 'p_bottles'];
    const landed = furniture.filter(f => seen.has(f));
    ok('furniture is placed in the drowned halls', landed.length >= 4, landed.join(',') || 'none in 40 levels'); }

  /* glass should not splinter like a plank */
  ok('bottles break like glass', propMat('p_bottles') === 'glass' && propMat('p_potion2') === 'glass', propMat('p_bottles'));
  ok('and so does the chalice', propMat('p_chalice') === 'glass');
  ok('while a table is still wood', propMat('p_table') === 'wood');
  ok('and a metal crate is still metal', propMat('p_crate_metal') === 'metal');
  ok('glass has colours to break into', Array.isArray(MATCOL.glass) && MATCOL.glass.length === 3);

  /* the locked door carries the gate, and stops once it is open */
  { startGame(['thistle']); G.level = 4; genLevel(); G.offer = null; G.offerQ.length = 0;
    const d = G.door;
    const drawn = () => {
      const seen = {};
      const real = sprProp;
      sprProp = function (n) { seen[n] = 1; return true; };
      try { drawDoor(); } finally { sprProp = real; }
      return seen;
    };
    /* stand next to it so fog is not what decides the answer */
    const P = G.players[0]; P.x = d.x * T + T / 2; P.y = d.y * T + T / 2 + 24;
    for (let i = 0; i < 30; i++) update(1 / 60);
    ok('a locked door is a gate you can see', !!drawn()['gate'], 'tile=' + G.map[d.y * MW + d.x]);
    G.map[d.y * MW + d.x] = 0;
    ok('and it is gone once unlocked', !drawn()['gate']); }
}

"""

io.open(p, 'w', encoding='utf-8', newline='').write(s.replace(anchor, block + anchor))
print('scenery tests inserted')
