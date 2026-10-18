import io

p = 'behave2_drive.js'
s = io.open(p, encoding='utf-8').read()
anchor = "const fails = results.filter(r => r[0] === 'FAIL');"
assert s.count(anchor) == 1, 'anchor not unique'
assert 'every boon a delver can learn' not in s, 'already inserted'

block = r"""/* ---------------- every boon a delver can learn ----------------
   Sixteen boons, four per delver, offered every few floors and chosen on
   purpose. `spiny` was a table entry with nothing behind it; these are the
   biggest table left where the same thing could hide, and reading the code
   only shows that each id is mentioned somewhere, not that choosing it
   changes anything.

   So each is driven twice -- once without, once with -- and the difference
   has to be the thing the boon's own description claims. The list comes
   from BOONS, so a seventeenth cannot slip in unprobed. */
{
  const arena = (cls) => {
    startGame([cls]); G.level = 5; genLevel();
    G.offer = null; G.offerQ.length = 0; G.state = 'play';
    G.enemies.length = 0; G.shots.length = 0; G.eshots.length = 0;
    G.items.length = 0; G.zones.length = 0; G.hazards.length = 0;
    const P = G.players[0];
    P.hp = P.max; P.inv = 0; P.cd = 0; P.boons = {}; P.aim = 0; P.down = false;
    return P;
  };
  const foeAt = (P, dx, dy, alert) => {
    spawnFoe('gloam', P.x + dx, P.y + (dy || 0), false);
    const e = G.enemies[G.enemies.length - 1];
    e.hp = e.max = 9999; e.alert = alert === undefined ? true : alert;
    return e;
  };
  const steps = n => { for (let i = 0; i < (n || 12); i++) update(1 / 60); };

  /* Each probe returns a number; with the boon it must differ from without,
     in the direction the boon promises. */
  const PROBES = {
    /* --- Bulwark, who swings --- */
    cyclone: ['bulwark', P => { const e = foeAt(P, -34); P.aim = 0; P.cd = 0; attack(P); return 9999 - e.hp; }, 'up'],
    wake:    ['bulwark', P => { const e = foeAt(P, 30); P.cd = 0; attack(P); return e.burn || 0; }, 'up'],
    bash:    ['bulwark', P => { const e = foeAt(P, 30); P.cd = 0; attack(P); return e.root || 0; }, 'up'],
    riposte: ['bulwark', P => { const e = foeAt(P, 30); P.cd = 5; P.inv = 0; hurtPlayer(P, 8, 0, e); return 5 - P.cd; }, 'up'],

    /* --- Ember, who throws fire --- */
    split:   ['ember', P => { foeAt(P, 70); P.cd = 0; attack(P); steps(30); return G.shots.length; }, 'up'],
    seek:    ['ember', P => { P.aim = 0; foeAt(P, 90, -70); P.cd = 0; attack(P);
                              const s0 = G.shots[0]; const vy0 = s0 ? s0.vy : 0; steps(8);
                              const s1 = G.shots[0]; return s1 ? Math.abs(s1.vy - vy0) : 0; }, 'up'],
    pyre:    ['ember', P => { foeAt(P, 70); P.cd = 0; attack(P); steps(30); return G.zones.length; }, 'up'],
    kindle:  ['ember', P => { const e = foeAt(P, 40); e.hp = e.max = 4; P.cd = 0; attack(P); steps(20);
                              return (G.enemies[0] && G.enemies[0].kindled) || (e.kindled ? 1 : 0); }, 'up'],

    /* --- Sable, who throws daggers --- */
    fan:     ['sable', P => { P.cd = 0; attack(P); return G.shots.length; }, 'up'],
    ric:     ['sable', P => { foeAt(P, 60); foeAt(P, 60, 40); P.cd = 0; attack(P); steps(30);
                              return G.shots.reduce((n, s) => n + (s.bounce || 0), 0); }, 'up'],
    venom:   ['sable', P => { const e = foeAt(P, 60); P.cd = 0; attack(P); steps(30); return e.pois || 0; }, 'up'],
    ambush:  ['sable', P => { const e = foeAt(P, 60, 0, false); e.alert = false; P.cd = 0; attack(P);
                              const hp = e.hp; steps(30); return hp - e.hp; }, 'up'],

    /* --- Thistle, who looses arrows --- */
    volley:  ['thistle', P => { P.cd = 0; attack(P); return G.shots.length; }, 'up'],
    barbs:   ['thistle', P => { P.cd = 0; attack(P); return G.shots.length ? G.shots[0].dmg : 0; }, 'up'],
    frost:   ['thistle', P => { const e = foeAt(P, 60); P.cd = 0; attack(P); steps(30); return e.chill || 0; }, 'up'],
    mark:    ['thistle', P => { const e = foeAt(P, 60); P.cd = 0; attack(P); steps(30); return e.mark || 0; }, 'up'],
  };

  /* the list cannot fall behind the table */
  {
    const all = [];
    for (const k in BOONS) for (const b of BOONS[k]) all.push(b.id);
    const unprobed = all.filter(id => !PROBES[id]);
    const extra = Object.keys(PROBES).filter(id => all.indexOf(id) < 0);
    ok('every boon a delver can learn is probed here', unprobed.length === 0,
       unprobed.join(',') || all.length + ' boons');
    ok('and nothing is probed that no delver can learn', extra.length === 0, extra.join(','));
  }

  /* each one changes what it says it changes */
  {
    const dead = [], backwards = [];
    for (const id in PROBES) {
      const [cls, run, want] = PROBES[id];
      let without, with_;
      try {
        const A = arena(cls); without = run(A);
        const B = arena(cls); B.boons[id] = 1; with_ = run(B);
      } catch (e) { dead.push(id + ' threw: ' + e.message); continue; }
      if (Math.abs(with_ - without) < 1e-9) { dead.push(id + ' (both ' + without + ')'); continue; }
      const right = want === 'up' ? with_ > without : with_ < without;
      if (!right) backwards.push(id + ': ' + without + ' -> ' + with_);
    }
    ok('every boon changes something when it is learned', dead.length === 0,
       dead.join('; ') || Object.keys(PROBES).length + ' boons, all live');
    ok('and changes it the way its description promises', backwards.length === 0,
       backwards.join('; ') || 'all in the promised direction');
  }

  /* the one that is easiest to be wrong about: a full circle really is one */
  {
    const A = arena('bulwark'); const behindA = foeAt(A, -34); A.cd = 0; A.aim = 0; attack(A);
    const B = arena('bulwark'); B.boons.cyclone = 1;
    const behindB = foeAt(B, -34); B.cd = 0; B.aim = 0; attack(B);
    ok('without Cyclone a sweep does not reach behind you', behindA.hp === 9999,
       'took ' + (9999 - behindA.hp));
    ok('and with it, it does', behindB.hp < 9999, 'took ' + (9999 - behindB.hp));
  }
}

"""

io.open(p, 'w', encoding='utf-8', newline='').write(s.replace(anchor, block + anchor))
print('boon probes inserted')
