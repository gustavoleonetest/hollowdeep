import io

p = 'behave2_drive.js'
s = io.open(p, encoding='utf-8').read()
anchor = "const fails = results.filter(r => r[0] === 'FAIL');"
assert s.count(anchor) == 1, 'anchor not unique'
assert 'every modifier an elite can wear' not in s, 'already inserted'

block = r"""/* ---------------- every modifier an elite can wear ----------------
   An elite rolls one or two of six modifiers and the game floats their
   names over its head, so each name is a promise to the player about what
   this fight will be. `spiny` appeared exactly once in the whole file --
   in the table that named it -- so for one fight in six the promise was a
   word and nothing else.

   Each is driven here and checked for doing the thing its name says. The
   list comes from EAFF, so a modifier added later with nothing behind it
   fails this rather than shipping as a label. */
{
  const arena = () => {
    startGame(['bulwark']); G.level = 6; genLevel();
    G.offer = null; G.offerQ.length = 0; G.state = 'play';
    G.enemies.length = 0; G.eshots.length = 0; G.shots.length = 0; G.items.length = 0;
    const P = G.players[0]; P.hp = P.max; P.inv = 0; P.chill = 0; P.down = false;
    return P;
  };
  const elite = (P, aff, dx) => {
    spawnFoe('gloam', P.x + (dx === undefined ? 24 : dx), P.y, true);
    const e = G.enemies[G.enemies.length - 1];
    e.eaff = [aff];
    if (aff === 'warded') { e.wardMax = e.max * .45; e.ward = e.wardMax; }
    if (aff === 'fast') e.spd *= 1.55;
    return e;
  };

  const PROBES = {
    fast: P => {
      const plain = (spawnFoe('gloam', P.x + 300, P.y, true), G.enemies[G.enemies.length - 1]).spd;
      const quick = elite(P, 'fast', 300).spd;
      return quick > plain * 1.4;
    },
    warded: P => {
      const e = elite(P, 'warded');
      const hp = e.hp, ward = e.ward;
      hurtFoe(e, 10, 0, false, false, P);
      return e.ward < ward && e.hp === hp;          /* the ward took it, not the foe */
    },
    vamp: P => {
      const e = elite(P, 'vamp');
      e.hp = e.max * .5;
      const before = e.hp;
      P.inv = 0; hurtPlayer(P, 20, 0, e);
      return e.hp > before;                          /* it drank */
    },
    frozen: P => {
      const e = elite(P, 'frozen');
      P.chill = 0; P.inv = 0; hurtPlayer(P, 20, 0, e);
      return P.chill > 0;                            /* you are slowed */
    },
    fiery: P => {
      const e = elite(P, 'fiery', 30);
      P.hp = P.max; P.inv = 0;
      const before = P.hp;
      hurtFoe(e, e.max * 10 + 9999, 0, false, false, P);
      return P.hp < before;                          /* it went off on you */
    },
    spiny: P => {
      const e = elite(P, 'spiny', 24);
      P.hp = P.max; P.inv = 0;
      const before = P.hp;
      hurtFoe(e, 5, 0, false, false, P);
      return P.hp < before;                          /* it pricked you back */
    },
  };

  /* the list cannot fall behind the table */
  {
    const unprobed = EAFF.map(a => a.id).filter(id => !PROBES[id]);
    const extra = Object.keys(PROBES).filter(id => !EAFF.some(a => a.id === id));
    ok('every elite modifier is probed here', unprobed.length === 0,
       unprobed.join(',') || EAFF.length + ' modifiers');
    ok('and nothing is probed that no elite can roll', extra.length === 0, extra.join(','));
  }

  /* each does what its name says */
  {
    const dead = [];
    for (const id in PROBES) {
      let did = false;
      try { did = PROBES[id](arena()); } catch (e) { dead.push(id + ' threw: ' + e.message); continue; }
      if (!did) dead.push(id);
    }
    ok('every elite modifier actually does something', dead.length === 0,
       dead.join('; ') || Object.keys(PROBES).length + ' modifiers, all live');
  }

  /* and the one that was only ever a word, in detail */
  {
    const P = arena();
    const e = elite(P, 'spiny', 24);
    P.hp = P.max; P.inv = 0;
    const start = P.hp;
    hurtFoe(e, 5, 0, false, false, P);
    const pricked = start - P.hp;
    ok('Spiny pricks whoever strikes it close to', pricked > 0, 'took ' + pricked.toFixed(0));
    ok('and does not hand out invulnerability while doing it', P.inv <= 0,
       'inv ' + P.inv + ' — a Spiny elite must not shield you from itself');

    /* it has its own cooldown, so a fast weapon is not shredded */
    const afterOne = P.hp;
    hurtFoe(e, 5, 0, false, false, P);
    ok('and it cannot prick again at once', P.hp === afterOne, 'hp ' + P.hp.toFixed(1));

    /* from across the room, spines do not reach */
    const far = arena();
    const e2 = elite(far, 'spiny', 400);
    far.hp = far.max; far.inv = 0;
    const was = far.hp;
    hurtFoe(e2, 5, 0, false, false, far);
    ok('but not someone shooting it from across the room', far.hp === was, 'hp ' + far.hp.toFixed(1));

    /* and what it takes is counted as a creature taking it */
    const t = arena();
    const e3 = elite(t, 'spiny', 24);
    t.hp = t.max; t.inv = 0; G.tollFoes = 0; G.tollDeep = 0;
    hurtFoe(e3, 5, 0, false, false, t);
    ok('and the death screen counts it among the creatures', G.tollFoes > 0,
       'creatures took ' + G.tollFoes.toFixed(1));
  }
}

"""

io.open(p, 'w', encoding='utf-8', newline='').write(s.replace(anchor, block + anchor))
print('elite modifier probes inserted')
