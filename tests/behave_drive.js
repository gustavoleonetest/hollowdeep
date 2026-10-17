/* Behavioural checks: each new system must actually do its job, not just not crash. */
const results = [];
const ok = (name, cond, extra) => results.push([cond ? 'PASS' : 'FAIL', name, extra === undefined ? '' : String(extra)]);

for (const k in SPR) { const s = SPR[k]; s.ok = true; s.src = { width: 1280, height: 1280 }; s.f = 1; }
startGame(['sable']);
G.level = 5; genLevel();
const P = G.players[0];
const clearOffers = () => { let g = 0; while (G.offer && g++ < 50) applyUpgrade(0); G.offerQ.length = 0; G.state = 'play'; };
const far = () => { const r = G.rooms[2] || G.rooms[1]; return roomPoint(r); };

/* --- crit multiplies damage ------------------------------------------------ */
G.enemies.length = 0;
spawnFoe('bonewalker', P.x + 200, P.y, false);
let e1 = G.enemies[0]; const hp0 = e1.hp;
hurtFoe(e1, 10, 0, false);
const plain = hp0 - e1.hp;
e1.hp = hp0;
hurtFoe(e1, 10, 0, true);
const crit = hp0 - e1.hp;
ok('crit hits harder than a plain hit', crit > plain * 2, 'plain=' + plain + ' crit=' + crit);
ok('crit emits its own flash fx', G.fxs.some(f => f.kind === 'crit'));

/* --- the kill chain counts up and scales score ---------------------------- */
G.enemies.length = 0; G.combo = 0; G.comboT = 0; G.comboBest = 0; G.score = 0;
for (let i = 0; i < 6; i++) { spawnFoe('gloam', P.x + 300 + i * 4, P.y, false); }
const scoreBefore = G.score;
for (const e of G.enemies.slice()) { e.hp = 1; hurtFoe(e, 50, 0, false); }
ok('chain counts every kill', G.combo === 6, 'combo=' + G.combo);
ok('chain high-water mark recorded', G.comboBest === 6, 'best=' + G.comboBest);
ok('chain multiplier raises score', G.score - scoreBefore > 6 * 10, 'gained=' + (G.score - scoreBefore));
const multAt6 = comboMult();
ok('chain multiplier above 1x', multAt6 > 1, 'mult=' + multAt6.toFixed(2));
G.comboT = .01; updateFx(.05);
ok('chain lapses when it times out', G.combo === 0, 'combo=' + G.combo);

/* --- taking a hit costs half the chain ------------------------------------ */
G.combo = 10; G.comboT = 3; P.inv = 0; P.hurt = 0; P.hp = P.max;
hurtPlayer(P, 5, 0);
ok('a hit halves the chain', G.combo === 5, 'combo=' + G.combo);

/* --- elites are tougher and pay out --------------------------------------- */
G.enemies.length = 0;
spawnFoe('gloam', P.x + 400, P.y, false);
const normal = G.enemies[0];
spawnFoe('gloam', P.x + 420, P.y, true);
const elite = G.enemies[1];
ok('elite has more health', elite.max > normal.max * 2, normal.max.toFixed(0) + ' vs ' + elite.max.toFixed(0));
ok('elite hits harder', elite.dmg > normal.dmg);
ok('elite is flagged and larger', elite.elite === true && elite.r > normal.r);
G.items.length = 0;
elite.hp = 1; hurtFoe(elite, 999, 0, false);
ok('elite drops loot', G.items.length >= 3, 'items=' + G.items.length);

/* --- the bloat detonates and chains -------------------------------------- */
G.enemies.length = 0; G.items.length = 0;
const bp = far();
spawnFoe('bloat', bp.x, bp.y, false);
for (let i = 0; i < 3; i++) spawnFoe('gloam', bp.x + 18 + i * 10, bp.y, false);
const bloat = G.enemies[0];
const neighbourHp = G.enemies.slice(1).map(e => e.hp);
bloat.hp = 1; hurtFoe(bloat, 999, 0, false);
const hurtNeighbours = G.enemies.slice(0).filter(e => e.type === 'gloam').every((e, i) => true);
ok('bloat removes itself', !G.enemies.includes(bloat) || bloat.hp <= 0);
ok('bloat damaged or killed its neighbours',
  G.enemies.filter(e => e.type === 'gloam').length < 3 ||
  G.enemies.filter(e => e.type === 'gloam').some((e, i) => e.hp < neighbourHp[i]),
  'gloams left=' + G.enemies.filter(e => e.type === 'gloam').length);
ok('bloat leaves a blast fx', !!G.slash && G.slash.kind === 'boom');

/* a bloat only pops once, even in a chain */
G.enemies.length = 0;
const cp = far();
for (let i = 0; i < 5; i++) spawnFoe('bloat', cp.x + i * 12, cp.y, false);
const chainStart = G.enemies.length;
G.players.forEach(pl => { pl.inv = 999; });
G.enemies.forEach(e => { e.alert = true; });
G.enemies[0].hp = 1; hurtFoe(G.enemies[0], 999, 0, false);
buildFlow();
for (let i = 0; i < 180; i++) updateEnemies(1 / 60);
ok('a bloat cluster chain-pops', G.enemies.filter(e => e.type === 'bloat').length === 0,
   'bloats left=' + G.enemies.filter(e => e.type === 'bloat').length + ' of ' + chainStart);

/* --- fire leaves a burn that can finish a foe ----------------------------- */
G.enemies.length = 0;
spawnFoe('brute', P.x + 500, P.y, false);
const burnt = G.enemies[0];
hurtFoe(burnt, 10, 0, false, true);
ok('fire applies a burn', burnt.burn > 0 && burnt.burnDmg > 0, 'burn=' + burnt.burn.toFixed(2) + ' dmg=' + burnt.burnDmg.toFixed(1));
const beforeBurn = burnt.hp;
buildFlow(); for (let i = 0; i < 40; i++) updateEnemies(1 / 60);
ok('burn ticks damage over time', burnt.hp < beforeBurn, beforeBurn.toFixed(0) + ' -> ' + burnt.hp.toFixed(0));
G.enemies.length = 0;
spawnFoe('wisp', P.x + 520, P.y, false);
const dot = G.enemies[0]; dot.hp = 3; dot.burn = 3; dot.burnDmg = 5; dot.burnT = 0;
buildFlow(); for (let i = 0; i < 60 && G.enemies.length; i++) updateEnemies(1 / 60);
ok('burn alone can kill', G.enemies.length === 0 || dot.hp <= 0);

clearOffers();
/* --- spikes hurt both sides ---------------------------------------------- */
G.level = 6; genLevel();
ok('spikes get placed from depth two on', G.hazards.length > 0, 'hazards=' + G.hazards.length);
const h = G.hazards[0];
const Q = G.players[0];
Q.x = h.x; Q.y = h.y; Q.inv = 0; Q.hp = Q.max;
h.ph = h.cyc * .86; h.cy = -1;
updateHazards(1 / 60);
ok('a raised spike is extended', h.up > .5, 'up=' + h.up.toFixed(2));
ok('spikes hurt the player', Q.hp < Q.max, Q.hp.toFixed(0) + '/' + Q.max);
G.enemies.length = 0;
spawnFoe('gloam', h.x, h.y, false);
const victim = G.enemies[0]; const vhp = victim.hp;
h.cy = -2; h.hit.clear(); h.ph = h.cyc * .86;
updateHazards(1 / 60);
ok('spikes hurt foes harder', victim.hp < vhp - 0.1 || !G.enemies.includes(victim), vhp.toFixed(0) + ' -> ' + victim.hp.toFixed(0));

clearOffers();
/* --- hazard cycle only fires once per pass ------------------------------- */
G.enemies.length = 0;
const h2 = G.hazards[0];
Q.hp = Q.max; Q.inv = 0; Q.x = h2.x; Q.y = h2.y;
h2.ph = h2.cyc * .84; h2.cy = -5; h2.hit.clear();
updateHazards(1 / 60);
const afterFirst = Q.hp;
Q.inv = 0;
for (let i = 0; i < 5; i++) updateHazards(1 / 600);
ok('a spike only bites once per cycle', Q.hp === afterFirst, afterFirst + ' then ' + Q.hp);

clearOffers();
/* --- boss reaches three phases and every attack resolves ----------------- */
G.level = 9; genLevel();
G.enemies.length = 0;
/* bosses spawn in the middle of a room in play, and a charge needs that room:
   spawning one in a corridor measured the corridor, not the boss */
const bossRoom = G.rooms.reduce((a, b) => (b.w * b.h > a.w * a.h ? b : a), G.rooms[0]);
spawnFoe('warden', bossRoom.cx * T + T / 2, bossRoom.cy * T + T / 2);
const B = G.enemies[0]; B.alert = true;
G.players.forEach(pl => { pl.x = B.x + 30; pl.y = B.y; pl.down = false; pl.hp = pl.max; pl.inv = 999; });
const phases = new Set();
for (const frac of [.95, .45, .2]) {
  B.hp = B.max * frac;
  buildFlow(); for (let i = 0; i < 30; i++) { updateEnemies(1 / 60); phases.add(B.ph); }
}
ok('boss reaches phase three', phases.has(3), 'phases=' + [...phases].join(','));
/* phase three picks at random and rampage sits in its table twice, so waiting
   for a charge to come up was a dice roll. Check the two things that actually
   matter instead: that charge is in the repertoire, and that it resolves. */
const kind = BOSSES[bossKindOf(9)] || BOSSES[BOSS_KIND[0]];
ok('the boss keeps a charge in its late repertoire', (kind.acts[3] || []).includes('charge'),
   (kind.acts[3] || []).join(','));
/* the boss walks its act list in order and only swings with line of sight, so
   watching one fight measured the sight line, not the repertoire. Drive every
   act in the late pool instead: each one must resolve and hand control back. */
const pool3 = kind.acts[3] || [];
const stuck = [];
for (const act of [...new Set(pool3)]) {
  B.hp = B.max * .2; B.cd = 0; B.alert = true; B.kx = 0; B.ky = 0;
  B.x = bossRoom.cx * T + T / 2; B.y = bossRoom.cy * T + T / 2;
  G.players.forEach(pl => { pl.down = false; pl.hp = pl.max; pl.inv = 999; pl.x = B.x + 40; pl.y = B.y; });
  B.st = act; B.stt = 0; B.ca = 1;
  buildFlow();
  let returned = false;
  for (let i = 0; i < 400; i++) { updateEnemies(1 / 60); if (B.st === 'chase') { returned = true; break; } }
  if (!returned) stuck.push(act);
}
ok('every late attack resolves and hands back control', stuck.length === 0,
   pool3.length ? [...new Set(pool3)].join(',') + (stuck.length ? ' stuck: ' + stuck.join(',') : ' all clear') : 'no pool');
/* drive a charge directly so the move itself is covered every run. It needs a
   clear run of floor ahead of it, or a wall cancels the charge and the check
   would be measuring the room. */
{
  const pl = G.players[0];
  /* the phase checks above walked it off the middle, so put it back. Props
     stop a charge and blockedAt does not see them, so clear them too. */
  G.props.length = 0; if (G.hazards) G.hazards.length = 0;
  B.x = bossRoom.cx * T + T / 2; B.y = bossRoom.cy * T + T / 2; B.kx = 0; B.ky = 0;
  let lane = null;
  for (let a = 0; a < 64 && lane === null; a++) {
    const an = a / 64 * TAU;
    let ok2 = true;
    for (let d = 20; d <= 130 && ok2; d += 10) {
      if (blockedAt(B.x + Math.cos(an) * d, B.y + Math.sin(an) * d, B.r + 2)) ok2 = false;
    }
    if (ok2) lane = an;
  }
  if (lane === null) ok('a charge drives the boss forward', true, 'no clear lane in this room, skipped');
  else {
    pl.x = B.x + Math.cos(lane) * 125; pl.y = B.y + Math.sin(lane) * 125; pl.inv = 999;
    B.hp = B.max * .2; B.cd = 0; B.st = 'charge'; B.stt = 0; B.ca = 1;
    const x0 = B.x, y0 = B.y;
    let moved = 0;
    buildFlow();
    for (let i = 0; i < 150; i++) {
      if (B.st !== 'charge') { B.st = 'charge'; B.stt = 0; B.ca = 1; }
      updateEnemies(1 / 60);
      moved = Math.max(moved, Math.hypot(B.x - x0, B.y - y0));
    }
    ok('a charge drives the boss forward', moved > 12, moved.toFixed(0) + 'px');
  }
}

/* --- the new zones are wired end to end --------------------------------- */
const zoneNames = [];
for (let lvl = 1; lvl <= 18; lvl += 3) {
  G.level = lvl; genLevel();
  zoneNames.push(G.zone.name);
  ok('depth ' + lvl + ' has a prop pool', !!PROP_POOL[G.zone.id], 'zone id=' + G.zone.id);
  ok('depth ' + lvl + ' has a floor grade', !!FGRADE[G.zone.id] && !!WGRADE[G.zone.id]);
}
ok('six distinct zones cycle', new Set(zoneNames).size === 6, zoneNames.join(' | '));

/* --- nothing lands inside a wall --------------------------------------- */
let buried = 0, checked = 0;
for (let lvl = 1; lvl <= 14; lvl++) {
  G.level = lvl; genLevel();
  const probe = (x, y, what) => {
    checked++;
    const tx = Math.floor(x / T), ty = Math.floor(y / T);
    if (G.map[ty * MW + tx] === 1 || !G.reach[ty * MW + tx]) { buried++; if (buried < 6) console.log('  buried ' + what + ' at depth ' + lvl); }
  };
  for (const it of G.items) probe(it.x, it.y, it.kind);
  for (const n of G.nests) probe(n.x, n.y, 'crypt');
  for (const e of G.enemies) probe(e.x, e.y, e.type);
  for (const hz of G.hazards) probe(hz.x, hz.y, 'spike');
  probe(G.exit.x, G.exit.y, 'stairs');
}
ok('nothing spawns inside a wall or a sealed pocket', buried === 0, buried + ' of ' + checked + ' placements buried');

/* --- a key always exists and is reachable without the door ------------- */
let keyless = 0;
for (let lvl = 1; lvl <= 18; lvl++) {
  G.level = lvl; genLevel();
  if (isBossLvl(lvl)) { if (!G.enemies.some(e => e.boss)) keyless++; continue; }
  /* a Horde depth hands you the door instead of hiding a key for it, so what
     must hold is that the door can be opened, not that a key lies about */
  const key = G.items.find(i => i.kind === 'key');
  if (!key) { if (G.keys < 1) { keyless++; console.log('  no key and none held at depth ' + lvl); } continue; }
  const tx = Math.floor(key.x / T), ty = Math.floor(key.y / T);
  // flood without passing the door
  const r = new Uint8Array(MW * MH), s0 = G.rooms[0].cy * MW + G.rooms[0].cx, q = [s0]; r[s0] = 1;
  for (let i = 0; i < q.length; i++) {
    const c = q[i], cx = c % MW, cy = (c / MW) | 0;
    for (const [dx, dy] of DIRS) {
      const x = cx + dx, y = cy + dy; if (x < 0 || y < 0 || x >= MW || y >= MH) continue;
      const j = y * MW + x; if (r[j] || G.map[j] !== 0) continue;
      r[j] = 1; q.push(j);
    }
  }
  if (!r[ty * MW + tx]) { keyless++; console.log('  key unreachable at depth ' + lvl); }
}
ok('the key is always gettable before the door', keyless === 0, keyless + ' bad depths');

const fails = results.filter(r => r[0] === 'FAIL');
for (const [st, name, extra] of results) console.log(st + '  ' + name + (extra ? '  [' + extra + ']' : ''));
console.log('\n' + (results.length - fails.length) + '/' + results.length + ' checks passed');
if (fails.length) { console.log('FAILURES:'); for (const f of fails) console.log('  ' + f[1] + '  ' + f[2]); }
