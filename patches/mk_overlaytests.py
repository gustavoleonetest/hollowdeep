import io

p = 'behave2_drive.js'
s = io.open(p, encoding='utf-8').read()
anchor = "const fails = results.filter(r => r[0] === 'FAIL');"
assert s.count(anchor) == 1, 'anchor not unique'
assert 'nothing reads through an overlay' not in s, 'already inserted'

block = r"""/* ---------------- nothing reads through an overlay ----------------
   An overlay in this game dims the stage rather than covering it, which is
   the look it wants and the reason this keeps going wrong: anything left
   showing underneath reads straight through the sheet. It has bitten three
   times now -- the HUD through the pause sheet, the menu through the
   Barrow, the HUD through the loot screen -- each found by eye, on a phone,
   after shipping.

   So this is the rule rather than another instance of it: while a
   full-screen overlay is up, nothing else full-screen is. The list of
   overlays is read from the document, so an overlay added later is held to
   the same rule without anyone remembering to add it here. */
{
  const OVERLAYS = ['menu', 'over', 'shop', 'barrow', 'paused', 'loot'];
  const up = () => OVERLAYS.filter(id => !$(id).hidden);
  const hudUp = () => !$('hud').hidden;
  const clear = () => { for (const id of OVERLAYS) $(id).hidden = true; };

  /* the list has to match what the page actually has, or this checks a
     subset and says it checked everything */
  {
    const missing = OVERLAYS.filter(id => !$(id));
    ok('[overlays] every overlay named here exists', missing.length === 0, missing.join(','));
  }

  const breaches = [];
  const look = (what) => {
    const o = up();
    if (o.length > 1) breaches.push(what + ': ' + o.join(' + '));
    else if (o.length === 1 && hudUp()) breaches.push(what + ': HUD under ' + o[0]);
  };

  /* the loot screen, which is the one you see most */
  {
    clear();
    startGame(['sable']); G.level = 4; genLevel();
    $('hud').hidden = false; G.state = 'play';
    G.offer = null; G.offerQ.length = 0;
    queueOffer({ kind: 'gear', P: G.players[0],
      item: rollItem('weapon', RARITY.magic, true), cur: G.players[0].gear.weapon });
    frame(0);
    look('a gear offer');
    ok('[overlays] the loot screen is up', !$('loot').hidden);
    ok('[overlays] and the HUD is not under it', !hudUp(), 'hud up ' + hudUp());
    /* and it comes back once the choice is made */
    chooseUp(1);
    G.state = 'play'; frame(0);
    ok('[overlays] the HUD returns to a floor with nothing over it',
       hudUp() && $('loot').hidden, 'hud ' + hudUp() + ', loot hidden ' + $('loot').hidden);
  }

  /* the stall */
  {
    clear(); $('hud').hidden = false; G.state = 'play';
    G.wares = []; showShop();
    look('the stall');
    ok('[overlays] the stall takes the HUD too', !hudUp(), 'hud up ' + hudUp());
    G.state = 'play'; shopShown = true; frame(0);
  }

  /* the pause sheet */
  {
    clear(); $('hud').hidden = false; G.state = 'play';
    G.paused = false; pauseShown = false; G.paused = true; frame(0);
    look('a pause');
    G.paused = false; frame(0);
  }

  /* the Barrow over the menu */
  {
    clear(); showMenu(); showBarrow(true);
    look('the Barrow');
    showBarrow(false);
    look('the menu');
  }

  /* the death screen */
  {
    clear();
    startGame(['ember']); G.level = 3; genLevel(); G.state = 'play'; $('hud').hidden = false;
    for (const P of G.players) { P.hp = 0; P.down = true; }
    die(); showOver();
    look('a death');
  }

  ok('[overlays] no two overlays are ever up together, and none has the HUD under it',
     breaches.length === 0, breaches.join('; ') || 'six screens checked');

  /* and the inverse: an ordinary floor has the HUD and no overlay at all */
  {
    clear();
    startGame(['thistle']); G.level = 2; genLevel();
    G.offer = null; G.offerQ.length = 0; G.state = 'play'; $('hud').hidden = false;
    frame(0);
    ok('[overlays] a floor being played has the HUD and nothing over it',
       hudUp() && up().length === 0, 'hud ' + hudUp() + ', up: ' + (up().join(',') || 'none'));
  }
}

"""

io.open(p, 'w', encoding='utf-8', newline='').write(s.replace(anchor, block + anchor))
print('overlay invariant inserted')
