import io

p = 'behave2_drive.js'
s = io.open(p, encoding='utf-8').read()
anchor = "const fails = results.filter(r => r[0] === 'FAIL');"
assert s.count(anchor) == 1, 'anchor not unique'
assert 'who you have become' not in s, 'already inserted'

block = r"""/* ---------------- who you have become ---------------- */
{
  const piece = (slot, name, stats, setId) => ({
    slot, base: 'Thing', rar: 'rare', col: '#ffd24a', name,
    s: stats || {}, ilvl: 5, set: setId || null,
    setName: setId ? (SETS.find(x => x.id === setId) || {}).name : null
  });
  const text = () => $('pauseGear').textContent + ' ' + $('pauseS').textContent + ' ' + $('pauseExtra').textContent;

  startGame(['ember']); G.level = 6; genLevel();
  G.offer = null; G.offerQ.length = 0; G.state = 'play';
  const P = G.players[0];
  P.gear.weapon = piece('weapon', 'Rime Hollowblade', { dmg: .2, elem: 'cold', elemDmg: .4 });
  P.gear.armour = piece('armour', 'Swift Gravemail', { arm: .1, hp: 30 }, 'quick');
  P.gear.trinket = null;
  P.boons = { pyre: 1 };
  P.pacts = [PACTS.find(q => q.id === 'embers')];
  recalc(P); P.hp = P.max;

  /* 1. pausing puts it on screen, by whichever route the pause came */
  {
    G.paused = false; pauseShown = false; $('paused').hidden = true;
    G.paused = true;
    frame(0);                         /* one turn of the real loop */
    ok('pausing shows the sheet', $('paused').hidden === false, 'hidden ' + $('paused').hidden);
    ok('and it names what is worn',
       /Rime Hollowblade/.test(text()) && /Swift Gravemail/.test(text()), text().slice(0, 120));
    ok('an empty slot says so rather than being left out',
       /Nothing worn|That slot is empty/.test(text()), text().slice(0, 160));
  }

  /* 2. everything a tooltip used to hide is on it */
  {
    const t = text();
    ok('the stats of each piece are there', /\+20% damage/.test(t), t.slice(0, 160));
    ok('so is the element, with its magnitude', /Cold damage: \+40%/.test(t), t.slice(0, 200));
    ok('so is the set', /The Quickened/.test(t), t.slice(0, 200));
    ok('and the boons and pacts', /Pyre/.test(t) && /Pact of Embers/.test(t), $('pauseExtra').textContent);
    ok('with the delver’s own line above it', /Ember/.test($('pauseS').textContent),
       $('pauseS').textContent.slice(0, 120));
  }

  /* 3. a card on the sheet is a thing to read, not a thing to pick: the
        offer screen reuses this card and its click equips something */
  {
    const cards = $('pauseGear').children;
    ok('three slots are shown', cards.length === 3, String(cards.length));
    const chosen = [];
    const real = applyUpgrade;
    applyUpgrade = i => chosen.push(i);
    try { for (const c of cards) if (c.listeners) c.listeners.forEach(f => f()); } catch (e) {}
    applyUpgrade = real;
    ok('and clicking one picks nothing', chosen.length === 0, chosen.join(','));
  }

  /* 4. unpausing takes it away again */
  {
    G.paused = false;
    frame(0);
    ok('carrying on hides it', $('paused').hidden === true, 'hidden ' + $('paused').hidden);
  }

  /* 5. THE TRAP: the sheet covers the canvas, and tapping the canvas was
        the only way back in for a touch player. The overlay has to resume. */
  {
    G.paused = true; frame(0);
    ok('the sheet is up', $('paused').hidden === false);
    const resumed = resumeFromPause();
    ok('and the overlay itself can let you back in', resumed === true && G.paused === false,
       'resumed ' + resumed + ', paused ' + G.paused);
    frame(0);
    ok('after which it is gone', $('paused').hidden === true);
  }

  /* 6. it is only ever up during play, never over a menu or a death */
  {
    const wrong = [];
    for (const st of ['menu', 'dead', 'won', 'offer', 'shop']) {
      G.state = st; G.paused = true; frame(0);
      if (!$('paused').hidden) wrong.push(st);
      G.paused = false; frame(0);
    }
    G.state = 'play';
    ok('and never over anything that is not play', wrong.length === 0, wrong.join(','));
  }

  /* 7. two delvers each get their own */
  {
    startGame(['bulwark', 'sable']); G.level = 3; genLevel();
    G.offer = null; G.offerQ.length = 0; G.state = 'play';
    G.players[0].gear.weapon = piece('weapon', 'Ones Blade', { dmg: .1 });
    G.players[1].gear.weapon = piece('weapon', 'Twos Dagger', { dmg: .1 });
    recalc(G.players[0]); recalc(G.players[1]);
    G.paused = false; pauseShown = false; G.paused = true; frame(0);
    ok('in co-op both delvers are laid out', $('pauseGear').children.length === 6,
       String($('pauseGear').children.length));
    const t = text();
    ok('each named so you can tell whose is whose', /P1/.test(t) && /P2/.test(t), t.slice(0, 100));
    ok('and both blades are on it', /Ones Blade/.test(t) && /Twos Dagger/.test(t), t.slice(0, 160));
    G.paused = false; frame(0);
  }
}

"""

io.open(p, 'w', encoding='utf-8', newline='').write(s.replace(anchor, block + anchor))
print('pause sheet tests inserted')
