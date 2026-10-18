import io

p = 'behave2_drive.js'
s = io.open(p, encoding='utf-8').read()
anchor = "const fails = results.filter(r => r[0] === 'FAIL');"
assert s.count(anchor) == 1, 'anchor not unique'
assert 'what an element is worth' not in s, 'already inserted'

block = r"""/* ---------------- what an element is worth ---------------- */
{
  const weapon = (elem, share) => ({
    slot: 'weapon', base: 'Hollowblade', rar: 'magic', col: '#6fa8ff',
    name: 'Test blade', s: { dmg: .1, elem: elem, elemDmg: share }, ilvl: 4,
    set: null, setName: null
  });
  const lines = it => itemLines(it);
  const elemLine = it => lines(it).find(l => /damage: \+/.test(l)) || '';
  const foeLine = it => lines(it).find(l => /fear it|shrug it off/.test(l)) || '';

  /* 1. the magnitude is on the card at all, and is the item's own */
  {
    const a = weapon('fire', .3), b = weapon('fire', .6);
    ok('an element says how much of every hit it adds', /\+30% of every hit/.test(elemLine(a)), elemLine(a));
    ok('and two weapons of the same element read differently',
       elemLine(a) !== elemLine(b) && /\+60%/.test(elemLine(b)), elemLine(b));
    ok('it keeps the element’s own word for what it does', /it burns/.test(elemLine(a)), elemLine(a));
    ok('and lightning is called lightning, not shock',
       /^Lightning damage/.test(elemLine(weapon('shock', .45))), elemLine(weapon('shock', .45)));
  }

  /* 2. who fears it and who shrugs is read off AFFIN, not written by hand:
        recompute both lists here and insist the card agrees */
  {
    const wrong = [];
    for (const el of ['fire', 'cold', 'shock', 'poison']) {
      const line = foeLine(weapon(el, .4));
      for (const t in AFFIN) {
        const a = AFFIN[t], nm = FOE_NAME[t];
        const named = line.indexOf(nm) >= 0;
        const shouldFear = a.weak === el, shouldResist = a.res === el || a.res === 'all';
        if ((shouldFear || shouldResist) && !named) wrong.push(el + ' never mentions ' + nm);
        if (!shouldFear && !shouldResist && named) wrong.push(el + ' wrongly mentions ' + nm);
      }
    }
    ok('every foe that cares about an element is named, and no other',
       wrong.length === 0, wrong.slice(0, 3).join('; ') || 'four elements against nine foes');
  }

  /* 3. the two findings that prompted this */
  {
    ok('fire names all three that fear it, not just the skeletons',
       /gloam/.test(foeLine(weapon('fire', .4))) &&
       /bonewalkers/.test(foeLine(weapon('fire', .4))) &&
       /bloats/.test(foeLine(weapon('fire', .4))), foeLine(weapon('fire', .4)));
    ok('and cold admits the warden shrugs it off',
       /wardens[^;]*shrug it off|shrug it off/.test(foeLine(weapon('cold', .4))) &&
       /wardens/.test(foeLine(weapon('cold', .4))), foeLine(weapon('cold', .4)));
    ok('the reaper, which resists everything, is named by every element',
       ['fire', 'cold', 'shock', 'poison'].every(el => /the reaper/.test(foeLine(weapon(el, .4)))),
       foeLine(weapon('poison', .4)));
  }

  /* 4. the card's claim and the dungeon's arithmetic have to agree: a foe
        the card says fears it must actually take more, and one the card
        says shrugs it off must actually take less */
  {
    const bad = [];
    for (const el of ['fire', 'cold', 'shock', 'poison']) {
      const line = foeLine(weapon(el, .4));
      for (const t in AFFIN) {
        const nm = FOE_NAME[t], m = elemMul({ type: t }, el);
        if (!line.indexOf) continue;
        const beforeSemi = line.split(';')[0], afterSemi = line.split(';')[1] || '';
        const saidFears = beforeSemi.indexOf(nm) >= 0 && /fear it/.test(beforeSemi);
        const saidShrugs = afterSemi.indexOf(nm) >= 0;
        if (saidFears && !(m > 1)) bad.push(nm + ' said to fear ' + el + ' but takes x' + m);
        if (saidShrugs && !(m < 1)) bad.push(nm + ' said to shrug off ' + el + ' but takes x' + m);
      }
    }
    ok('what the card claims is what the arithmetic does', bad.length === 0,
       bad.slice(0, 3).join('; ') || 'checked every foe against every element');
    ok('and the swing is the eightfold one worth knowing about',
       Math.abs(elemMul({ type: 'bonewalker' }, 'fire') / elemMul({ type: 'brute' }, 'fire') - 7.6) < .01,
       'x' + elemMul({ type: 'bonewalker' }, 'fire') + ' vs x' + elemMul({ type: 'brute' }, 'fire'));
  }

  /* 5. a weapon with no element says nothing about one */
  {
    const plain = { slot: 'weapon', base: 'Hollowblade', rar: 'magic', col: '#6fa8ff',
                    name: 'Plain', s: { dmg: .2 }, ilvl: 3, set: null, setName: null };
    ok('a plain weapon mentions no element', elemLine(plain) === '' && foeLine(plain) === '',
       lines(plain).join(' | '));
  }

  /* 6. every foe the dungeon can spawn has a name to be called by */
  {
    const unnamed = Object.keys(AFFIN).filter(t => !FOE_NAME[t]);
    ok('every foe with an affinity has a name', unnamed.length === 0, unnamed.join(','));
  }
}

"""

io.open(p, 'w', encoding='utf-8', newline='').write(s.replace(anchor, block + anchor))
print('element tests inserted')
