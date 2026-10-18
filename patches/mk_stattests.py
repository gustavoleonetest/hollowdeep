import io

p = 'behave2_drive.js'
s = io.open(p, encoding='utf-8').read()
anchor = "const fails = results.filter(r => r[0] === 'FAIL');"
assert s.count(anchor) == 1, 'anchor not unique'
assert 'every number an item promises' not in s, 'already inserted'

block = r"""/* ---------------- every number an item promises ----------------
   An item advertises a stat by having a line in STAT_LABEL. Nothing
   connected that list to the code that makes the stat do something, so a
   stat could be added, printed on the card, and never wired up -- a promise
   in writing that the dungeon does not keep. Worse than a missing feature,
   because the player is told otherwise.

   The list below is checked against STAT_LABEL itself, so a new label with
   no probe behind it fails here rather than shipping as a lie. */
{
  const bare = () => {
    startGame(['sable']); G.level = 5; genLevel();
    G.offer = null; G.offerQ.length = 0; G.state = 'play';
    G.enemies.length = 0; G.nests.length = 0; G.items.length = 0; G.hazards.length = 0;
    G.omen = null;
    const P = G.players[0];
    P.gear.weapon = P.gear.armour = P.gear.trinket = null;
    P.pacts.length = 0; P.perkGold = 0; P.perkDrain = 0;
    recalc(P); P.hp = P.max; P.inv = 0;
    return P;
  };
  const wear = (P, stat, v) => {
    P.gear.trinket = { slot: 'trinket', base: 'Sigil', rar: 'magic', col: '#6fa8ff',
                       name: 'Probe', s: { [stat]: v }, ilvl: 1, set: null, setName: null };
    recalc(P); P.hp = P.max; P.inv = 0;
    return P;
  };

  /* each probe: set the stat high, measure one observable, say which way it
     should move. Measured through the game's own code, never by reading the
     stat back out of the bag it was just put into. */
  const PROBES = {
    dmg:    { v: .5,  want: 'up',   m: P => P.dmgMul },
    cd:     { v: -.4, want: 'down', m: P => P.cdMul },
    crit:   { v: .3,  want: 'up',   m: P => P.crit },
    spd:    { v: .3,  want: 'up',   m: P => P.spdMul },
    hp:     { v: 60,  want: 'up',   m: P => P.max },
    dash:   { v: -.4, want: 'down', m: P => P.dashMul },
    drain:  { v: .6,  want: 'up',   m: P => drainRate(P) },
    arm:    { v: .5,  want: 'down', m: P => {
      P.hp = P.max; P.inv = 0; const before = P.hp;
      hurtPlayer(P, 60, 0);
      return before - P.hp;                       /* health actually lost */
    } },
    leech:  { v: .5,  want: 'up',   m: P => {
      P.hp = P.max * .5;
      spawnFoe('gloam', P.x + 40, P.y);
      const e = G.enemies[G.enemies.length - 1], before = P.hp;
      hurtFoe(e, 30, 0, false, false, P);
      const gained = P.hp - before;
      G.enemies.length = 0;
      return gained;                              /* health drawn back */
    } },
    thorns: { v: .8,  want: 'up',   m: P => {
      spawnFoe('brute', P.x + 30, P.y);
      const e = G.enemies[G.enemies.length - 1], before = e.hp;
      P.hp = P.max; P.inv = 0;
      hurtPlayer(P, 40, 0, e);
      const dealt = before - e.hp;
      G.enemies.length = 0;
      return dealt;                               /* damage returned */
    } },
    gold:   { v: 1,   want: 'up',   m: P => {
      G.gold = 0; G.items.length = 0;
      G.items.push({ kind: 'gold', x: P.x, y: P.y, t: 0, v: 100 });
      update(1 / 60);
      const got = G.gold;
      G.items.length = 0;
      return got;                                 /* coin actually banked */
    } },
    sp:     { v: 3,   want: 'down', m: P => {
      P.spCd = 0; G.state = 'play'; special(P);
      return P.spMax;                             /* seconds until the next */
    } },
  };

  /* (a) the list cannot fall behind what an item may advertise */
  {
    const labelled = Object.keys(STAT_LABEL);
    const unprobed = labelled.filter(k => !PROBES[k]);
    const extra = Object.keys(PROBES).filter(k => !STAT_LABEL[k]);
    ok('every stat an item can advertise is probed here', unprobed.length === 0,
       unprobed.join(',') || labelled.length + ' stats');
    ok('and nothing is probed that no item can advertise', extra.length === 0, extra.join(','));
  }

  /* (b) each one actually does something, in the right direction */
  {
    const dead = [], backwards = [];
    for (const k in PROBES) {
      const pr = PROBES[k];
      const without = pr.m(bare());
      const withIt = pr.m(wear(bare(), k, pr.v));
      const moved = Math.abs(withIt - without) > 1e-6;
      if (!moved) { dead.push(k + ' (' + without + ')'); continue; }
      const right = pr.want === 'up' ? withIt > without : withIt < without;
      if (!right) backwards.push(k + ': ' + without.toFixed(3) + ' -> ' + withIt.toFixed(3));
    }
    ok('every advertised stat changes something', dead.length === 0,
       dead.join('; ') || Object.keys(PROBES).length + ' stats, all live');
    ok('and changes it the way the card says', backwards.length === 0,
       backwards.join('; ') || 'all in the promised direction');
  }

  /* (c) the two that are easiest to get backwards, stated outright */
  {
    const plain = bare(), before = plain.cdMul;
    const fast = wear(bare(), 'cd', -.4);
    ok('"attacks faster" means a shorter wait, not a longer one', fast.cdMul < before,
       before.toFixed(3) + ' -> ' + fast.cdMul.toFixed(3));
    const soft = wear(bare(), 'arm', .5);
    soft.hp = soft.max; soft.inv = 0; const hadS = soft.hp; hurtPlayer(soft, 60, 0);
    const tough = hadS - soft.hp;
    const naked = bare(); naked.hp = naked.max; naked.inv = 0;
    const hadN = naked.hp; hurtPlayer(naked, 60, 0);
    const soft2 = hadN - naked.hp;
    ok('"less damage taken" means less of it arrives', tough < soft2,
       soft2.toFixed(1) + ' without -> ' + tough.toFixed(1) + ' with');
  }
}

"""

io.open(p, 'w', encoding='utf-8', newline='').write(s.replace(anchor, block + anchor))
print('stat probes inserted')
