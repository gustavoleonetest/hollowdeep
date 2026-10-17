import io

p = 'behave2_drive.js'
s = io.open(p, encoding='utf-8').read()
anchor = "const fails = results.filter(r => r[0] === 'FAIL');"
assert s.count(anchor) == 1, 'anchor not unique'
assert 'the run you left behind' not in s, 'already inserted'

block = r"""/* ---------------- the run you left behind ---------------- */
{
  const RK = 'hollowdeep-run';
  const stored = () => { try { return JSON.parse(localStorage.getItem(RK) || 'null'); } catch (e) { return null; } };

  /* a descent that gets somewhere, and earns things on the way down */
  META.perks = { vigour: 3 };
  clearRun();
  startGame(['ember']);
  saveRun();                                   /* what pressing a delver does */
  const P0 = G.players[0];
  P0.gear.weapon = rollItem('weapon', RARITY.fabled, true);
  P0.boons['pyre'] = 1;
  P0.pacts.push(PACTS[0]);
  P0.plvl = 5; P0.up.dmg = 1.4; P0.up.hp += 30;
  recalc(P0); P0.hp = P0.max * .62;
  G.gold = 321; G.keys = 1; G.bombs = 3; G.kills = 77; G.score = 4210;
  let guard = 0;
  while (G.level < 4 && guard++ < 12) { G.offer = null; G.offerQ.length = 0; nextLevel(); }

  const want = {
    level: G.level, gold: G.gold, keys: G.keys, bombs: G.bombs, kills: G.kills, score: G.score,
    plvl: P0.plvl, dmg: P0.up.dmg, max: P0.max, hp: P0.hp,
    weapon: P0.gear.weapon.name, pacts: P0.pacts.length, boons: Object.keys(P0.boons).length
  };

  ok('taking the stairs writes a checkpoint', !!stored() && stored().level === want.level,
     stored() ? 'depth ' + stored().level : 'nothing written');

  /* THE TRAP: boot builds a throwaway run so the menu has something behind
     it, and Change delver does the same. Either writing a checkpoint would
     destroy the very run the menu is about to offer. */
  startGame('bulwark');
  ok('the menu backdrop does not clobber the run', !!stored() && stored().level === want.level,
     stored() ? 'depth ' + stored().level : 'the run was destroyed by the menu');

  /* what a reload is: the page comes back holding nothing but the store */
  const back = loadRun();
  ok('a reload finds the run', !!back && back.level === want.level, back ? 'depth ' + back.level : 'nothing');
  resumeRun(back);
  const R = G.players[0];
  ok('and it is your delver that comes back', G.clsKey === 'ember', G.clsKey);
  ok('at the depth it had reached', G.level === want.level, G.level + ' vs ' + want.level);
  ok('holding the gold, the key and the flasks',
     G.gold === want.gold && G.keys === want.keys && G.bombs === want.bombs,
     G.gold + 'g ' + G.keys + 'k ' + G.bombs + 'f');
  ok('with the score and the kills it had', G.score === want.score && G.kills === want.kills,
     G.score + ' / ' + G.kills);
  ok('carrying the weapon it found', !!R.gear.weapon && R.gear.weapon.name === want.weapon,
     R.gear.weapon ? R.gear.weapon.name : 'empty handed');
  ok('at the level it had earned', R.plvl === want.plvl && Math.abs(R.up.dmg - want.dmg) < 1e-9,
     'level ' + R.plvl + ' dmg ' + R.up.dmg);
  ok('with the pact it swore and the boon it learned',
     R.pacts.length === want.pacts && !!R.boons['pyre'], R.pacts.length + ' pacts, pyre ' + !!R.boons['pyre']);
  ok('and the pact is the real one, not a copy off the disk',
     R.pacts[0] === PACTS[0], R.pacts[0] === PACTS[0] ? 'same object' : 'a lookalike');
  /* the subtle one: makeDelver applies the Barrow's perks, and the saved
     stats already include them. Laying one over the other must not add
     vigour twice. */
  ok('the Barrow is not paid out twice', R.max === want.max, R.max + ' vs ' + want.max);
  ok('and the health is what you had, not a free refill', Math.abs(R.hp - want.hp) < 1e-6,
     R.hp.toFixed(1) + ' vs ' + want.hp.toFixed(1));
  ok('a second reload still finds it', !!stored() && stored().level === want.level,
     stored() ? 'depth ' + stored().level : 'nothing left to come back to');

  /* death is still death */
  die();
  ok('dying clears the checkpoint', stored() === null, stored() ? 'the run survived its own death' : 'gone');
  ok('and there is nothing to offer afterwards', loadRun() === null);

  /* nothing off the disk is trusted */
  const refuse = [
    ['gibberish', 'not json at all {{{'],
    ['a save from another build', JSON.stringify({ v: 99, cls: ['ember'], level: 4, ps: [{}] })],
    ['a delver that does not exist', JSON.stringify({ v: 1, cls: ['sorcerer'], level: 4, ps: [{}] })],
    ['a depth beyond the deep', JSON.stringify({ v: 1, cls: ['ember'], level: 50000, ps: [{}] })],
    ['gear that is not gear', JSON.stringify({ v: 1, cls: ['ember'], level: 4, ps: [{ gear: { weapon: 'a sword' } }] })],
    ['two delvers listed and one saved', JSON.stringify({ v: 1, cls: ['ember', 'sable'], level: 4, ps: [{}] })],
    ['no delver at all', JSON.stringify({ v: 1, cls: [], level: 4, ps: [] })],
  ];
  const kept = [];
  for (const [name, raw] of refuse) {
    localStorage.setItem(RK, raw);
    if (loadRun() !== null || stored() !== null) kept.push(name);
  }
  ok('a save that makes no sense is refused, and thrown away with it',
     kept.length === 0, kept.join('; ') || refuse.length + ' kinds refused');

  /* but a save that is merely sloppy is coerced rather than discarded: this
     is the shape that once grew "4067" echoes out of a string and a number */
  localStorage.setItem(RK, JSON.stringify({
    v: 1, cls: ['ember'], level: '4', score: '12', gold: null, keys: undefined,
    runT: 'ages', ps: [{ hp: 'lots', plvl: '3', up: { dmg: 'huge', crit: {} }, pacts: ['embers', 'no such pact'] }]
  }));
  const sloppy = loadRun();
  const nums = sloppy ? [sloppy.level, sloppy.score, sloppy.gold, sloppy.keys, sloppy.runT,
                         sloppy.ps[0].hp, sloppy.ps[0].plvl, sloppy.ps[0].up.dmg, sloppy.ps[0].up.crit] : [NaN];
  ok('a sloppy save is coerced, not discarded', !!sloppy && sloppy.level === 4, sloppy ? 'depth ' + sloppy.level : 'thrown away');
  ok('and every number that comes back is a number', nums.every(n => typeof n === 'number' && Number.isFinite(n)),
     nums.join(','));
  ok('while a pact nobody has heard of is dropped', !!sloppy && sloppy.ps[0].pacts.length === 1,
     sloppy ? sloppy.ps[0].pacts.length + ' pacts' : '-');
  /* and it must actually run, not just parse */
  if (sloppy) {
    resumeRun(sloppy);
    const S = G.players[0];
    ok('a run rebuilt from it is playable', G.state === 'play' && S.hp > 0 && Number.isFinite(S.max) && S.max > 0,
       'hp ' + S.hp + '/' + S.max);
    let err = null;
    try { for (let i = 0; i < 180; i++) update(1 / 60); } catch (e) { err = e; }
    ok('and survives three seconds of play', err === null && Number.isFinite(G.players[0].hp),
       err ? String(err && err.message) : 'no throw');
  }

  clearRun(); META.perks = {};
}

"""

io.open(p, 'w', encoding='utf-8', newline='').write(s.replace(anchor, block + anchor))
print('resume tests inserted')
