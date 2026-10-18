import io

p = 'behave2_drive.js'
s = io.open(p, encoding='utf-8').read()
anchor = "const fails = results.filter(r => r[0] === 'FAIL');"
assert s.count(anchor) == 1, 'anchor not unique'
assert 'the ability nobody was told about' not in s, 'already inserted'

block = r"""/* ---------------- the ability nobody was told about ---------------- */
{
  /* 1. every delver has one described, and none is left out */
  {
    const keys = Object.keys(CLASSES);
    const missing = keys.filter(k => !SPECIALS[k] || !SPECIAL_DESC[k]);
    ok('every delver’s special is named and described', missing.length === 0, missing.join(','));
    const extra = Object.keys(SPECIAL_DESC).filter(k => !CLASSES[k]);
    ok('and nothing is described that no delver has', extra.length === 0, extra.join(','));
    ok('each description is its own, not copied about',
       new Set(keys.map(k => SPECIAL_DESC[k])).size === keys.length,
       String(new Set(keys.map(k => SPECIAL_DESC[k])).size));
  }

  /* 2. the descriptions have to match what the code actually does, which is
        the whole point: the names alone were already on screen. Drive each
        special and check the thing its line claims. */
  {
    const setup = (cls) => {
      startGame([cls]); G.level = 5; genLevel();
      G.offer = null; G.offerQ.length = 0; G.state = 'play';
      G.enemies.length = 0; G.eshots.length = 0; G.shots.length = 0; G.items.length = 0;
      const P = G.players[0]; P.spCd = 0; P.hp = P.max; P.aim = 0;
      return P;
    };

    /* Bulwark: "arrows already in the air swept out of it" */
    {
      const P = setup('bulwark');
      for (let i = 0; i < 6; i++) G.eshots.push({ x: P.x + 20 + i * 5, y: P.y, vx: 0, vy: 0, r: 4, dmg: 5, life: 3, col: '#fff', kind: 'arrow' });
      const far = { x: P.x + 400, y: P.y, vx: 0, vy: 0, r: 4, dmg: 5, life: 3, col: '#fff', kind: 'arrow' };
      G.eshots.push(far);
      const before = G.eshots.length;
      special(P);
      ok('Shield Slam really does sweep arrows out of the air',
         G.eshots.length < before && G.eshots.indexOf(far) >= 0,
         before + ' shots -> ' + G.eshots.length + ', the distant one kept: ' + (G.eshots.indexOf(far) >= 0));
      ok('and shields the delver, as it says', P.shield > 0, 'shield ' + P.shield);
    }

    /* Thistle: "roots everything near you to the floor" */
    {
      const P = setup('thistle');
      spawnFoe('gloam', P.x + 40, P.y, false);
      spawnFoe('gloam', P.x + 400, P.y, false);
      const near = G.enemies[0], far = G.enemies[1];
      special(P);
      ok('Entangle really does root what is near', (near.root || 0) > 1,
         'rooted for ' + (near.root || 0));
      ok('and leaves what is far alone', !(far.root > 0), 'far root ' + (far.root || 0));
    }

    /* Sable: "slip forward untouchable" */
    {
      const P = setup('sable');
      const x0 = P.x, y0 = P.y;
      special(P);
      const moved = Math.hypot(P.x - x0, P.y - y0);
      ok('Shadow Step really does move the delver', moved > 20, moved.toFixed(0) + ' away');
      ok('and really is untouchable for a moment', P.inv > .5, 'invulnerable ' + P.inv.toFixed(2) + 's');
      ok('and really leaves daggers behind', G.shots.length >= 10, G.shots.length + ' thrown');
    }

    /* Ember: "a burst all around you, and ten bolts thrown outward" */
    {
      const P = setup('ember');
      spawnFoe('gloam', P.x + 30, P.y, false);
      const e = G.enemies[0], hp = e.hp;
      special(P);
      ok('Fire Nova really does burst around the delver', e.hp < hp, hp.toFixed(0) + ' -> ' + e.hp.toFixed(0));
      ok('and really throws its bolts', G.shots.length >= 10, G.shots.length + ' bolts');
    }
  }

  /* 3. it is on the card where the delver is chosen, and on the sheet */
  {
    buildMenu();
    const cards = [...$('cards').children];
    ok('the menu builds a card for every delver', cards.length === Object.keys(CLASSES).length,
       String(cards.length));
    const html = cards.map(c => c.innerHTML).join(' ');
    const named = Object.keys(CLASSES).filter(k => html.indexOf(SPECIALS[k]) >= 0);
    ok('and every card names its special', named.length === Object.keys(CLASSES).length,
       named.join(',') || 'none');

    startGame(['bulwark']); G.level = 2; genLevel();
    G.offer = null; G.offerQ.length = 0; G.state = 'play';
    G.paused = false; pauseShown = false; G.paused = true; frame(0);
    ok('and the pause sheet says it too', /Shield Slam/.test($('pauseExtra').textContent),
       $('pauseExtra').textContent.slice(0, 90));
    ok('which is shown rather than hidden, now that there is always something on it',
       $('pauseExtra').hidden === false);
    G.paused = false; frame(0);
  }
}

"""

io.open(p, 'w', encoding='utf-8', newline='').write(s.replace(anchor, block + anchor))
print('special tests inserted')
