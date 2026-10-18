import io

p = 'behave2_drive.js'
s = io.open(p, encoding='utf-8').read()
anchor = "const fails = results.filter(r => r[0] === 'FAIL');"
assert s.count(anchor) == 1, 'anchor not unique'
assert 'a set you can actually see' not in s, 'already inserted'

block = r"""/* ---------------- a set you can actually see ---------------- */
{
  const piece = (slot, setId, stats) => ({
    slot, base: 'Test', rar: 'magic', col: '#6fa8ff', name: 'Test ' + slot,
    s: stats || {}, ilvl: 1, set: setId || null,
    setName: setId ? (SETS.find(x => x.id === setId) || {}).name : null
  });

  startGame(['bulwark']); G.level = 4; genLevel();
  G.offer = null; G.offerQ.length = 0; G.state = 'play';
  const P = G.players[0];
  const bare = () => { P.gear.weapon = P.gear.armour = P.gear.trinket = null; recalc(P); };

  /* 1. the bonus is real, and doubles at three */
  {
    bare(); const alone = { max: P.max, spd: P.spdMul };
    P.gear.weapon = piece('weapon', 'quick'); recalc(P);
    ok('one piece of a set grants nothing', Math.abs(P.spdMul - alone.spd) < 1e-9,
       P.spdMul.toFixed(4) + ' vs ' + alone.spd.toFixed(4));
    P.gear.armour = piece('armour', 'quick'); recalc(P);
    const pair = P.spdMul;
    ok('two pieces grant the bonus', pair > alone.spd, alone.spd.toFixed(3) + ' -> ' + pair.toFixed(3));
    P.gear.trinket = piece('trinket', 'quick'); recalc(P);
    ok('and three grant it twice over',
       Math.abs((P.spdMul - alone.spd) - 2 * (pair - alone.spd)) < 1e-6,
       '+' + (pair - alone.spd).toFixed(4) + ' -> +' + (P.spdMul - alone.spd).toFixed(4));
  }

  /* 2. and the delver now knows which set it is, not just that there is one */
  {
    ok('a live set is recorded with its id', P.sets.length === 1 && P.sets[0].id === 'quick',
       JSON.stringify(P.sets));
    ok('and how many pieces are up', P.sets[0].n === 3, String(P.sets[0].n));
    ok('setLive agrees', setLive(P, 'quick') === true && setLive(P, 'ember') === false);
  }

  /* 3. counting excludes the slot being filled, because equipping replaces */
  {
    bare();
    P.gear.weapon = piece('weapon', 'quick');
    P.gear.armour = piece('armour', 'quick');
    recalc(P);
    ok('two other slots hold the set when asking about a third',
       setWorn(P, 'quick', 'trinket') === 2, String(setWorn(P, 'quick', 'trinket')));
    ok('but only one when asking about a slot the set is already in',
       setWorn(P, 'quick', 'armour') === 1, String(setWorn(P, 'quick', 'armour')));
  }

  /* 4. the item line speaks to whoever is reading it */
  {
    bare();
    const lone = piece('weapon', 'quick');
    const noOne = itemLines(lone).find(l => /^Set:/.test(l));
    const toBare = itemLines(lone, P).find(l => /^Set:/.test(l));
    ok('with nobody asking it states the plain rule', /2 pieces grant more/.test(noOne || ''), noOne);
    ok('to a delver wearing none of it, it says so', /no other piece/.test(toBare || ''), toBare);

    P.gear.armour = piece('armour', 'quick'); recalc(P);
    const toOne = itemLines(lone, P).find(l => /^Set:/.test(l));
    ok('to one wearing a piece, it offers the pair', /would make a pair/.test(toOne || ''), toOne);

    P.gear.trinket = piece('trinket', 'quick'); recalc(P);
    const toTwo = itemLines(lone, P).find(l => /^Set:/.test(l));
    ok('and to one wearing two, it offers the lot', /complete all three/.test(toTwo || ''), toTwo);
  }

  /* 5. THE POINT OF ALL THIS: being warned before you break one */
  {
    bare();
    P.gear.weapon = piece('weapon', 'quick', { dmg: .10 });
    P.gear.armour = piece('armour', 'quick');
    recalc(P);
    ok('the set is up before the offer', setLive(P, 'quick'), JSON.stringify(P.sets));

    /* a better weapon that belongs to no set: strictly better on its lines,
       and taking it drops the pair */
    const tempting = piece('weapon', null, { dmg: .40 });
    G.offer = { kind: 'gear', P, item: tempting, cur: P.gear.weapon };
    G.state = 'offer';
    showLoot();
    const cards = [...$('lootCards').children].map(c => c.textContent);
    const warned = cards.some(t => /breaks The Quickened/.test(t));
    ok('taking a better item that breaks a set says so', warned,
       cards.join(' | ').slice(0, 150));

    /* and a replacement from the same set must NOT raise the warning */
    const sameSet = piece('weapon', 'quick', { dmg: .40 });
    G.offer = { kind: 'gear', P, item: sameSet, cur: P.gear.weapon };
    showLoot();
    const quiet = [...$('lootCards').children].map(c => c.textContent)
      .some(t => /breaks The Quickened/.test(t));
    ok('but swapping one set piece for another does not', !quiet);

    /* nor does a slot that is not holding the set up */
    P.gear.trinket = piece('trinket', 'ember');
    recalc(P);
    G.offer = { kind: 'gear', P, item: piece('trinket', null, { crit: .2 }), cur: P.gear.trinket };
    showLoot();
    const alsoQuiet = [...$('lootCards').children].map(c => c.textContent)
      .some(t => /breaks/.test(t));
    ok('and nor does dropping a piece of a set that was never up', !alsoQuiet);
    G.offer = null; G.state = 'play';
  }

  /* 6. the sheet line says what you have on */
  {
    bare();
    ok('with no set, the sheet says nothing about one', !/Wearing/.test(sheetLine(P)), sheetLine(P));
    P.gear.weapon = piece('weapon', 'quick');
    P.gear.armour = piece('armour', 'quick');
    recalc(P);
    ok('with a pair it names it', /Wearing The Quickened/.test(sheetLine(P)), sheetLine(P));
    P.gear.trinket = piece('trinket', 'quick'); recalc(P);
    ok('and with all three it says so', /The Quickened in full/.test(sheetLine(P)), sheetLine(P));
    bare();
  }
}

"""

io.open(p, 'w', encoding='utf-8', newline='').write(s.replace(anchor, block + anchor))
print('set tests inserted')
