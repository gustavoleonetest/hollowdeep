import io

p = 'behave2_drive.js'
s = io.open(p, encoding='utf-8').read()
anchor = "const fails = results.filter(r => r[0] === 'FAIL');"
assert s.count(anchor) == 1, 'anchor not unique'
assert 'how far down it goes' not in s, 'already inserted'

block = r"""/* ---------------- how far down it goes ---------------- */
{
  const at = (deepest, wins) => {
    META.deepest = deepest; META.wins = wins || 0;
    renderBarrow();
    return [...$('deepRows').children].map(r => r.textContent);
  };
  const named = rows => rows.filter(t => ZONES.some(z => t.indexOf(z.name) >= 0)).length;

  /* 1. the whole descent is laid out, however little of it you have seen */
  {
    const rows = at(1, 0);
    ok('every zone has a row, plus the Hollow', rows.length === ZONES.length + 1, String(rows.length));
    ok('and the depths are all there even when the names are not',
       rows.filter(t => /Depths? \d/.test(t)).length === ZONES.length + 1,
       rows.filter(t => /Depths? \d/.test(t)).length + ' rows carry a depth');
  }

  /* 2. names appear only as far as you have been */
  {
    ok('a first descent names only the zone it started in', named(at(1, 0)) === 1, String(named(at(1, 0))));
    ok('reaching the fourth depth names the second zone', named(at(4, 0)) === 2, String(named(at(4, 0))));
    ok('and the deepest reach names them all', named(at(FINAL_DEPTH, 0)) === ZONES.length,
       String(named(at(FINAL_DEPTH, 0))));
    ok('while the unreached ones say so rather than lying',
       at(1, 0).filter(t => /not been this deep/.test(t)).length === ZONES.length - 1,
       String(at(1, 0).filter(t => /not been this deep/.test(t)).length));
  }

  /* 3. a warden counts as felled only once you are past it. You cannot
        reach the floor below a boss floor without taking its key, so the
        deepest reach alone settles this. */
  {
    const atBoss = at(3, 0), past = at(4, 0);
    ok('standing on a warden’s floor is not the same as beating it',
       /Still standing/.test(atBoss[0]) && !/Felled/.test(atBoss[0]), atBoss[0].slice(0, 80));
    ok('but the floor below it is', /Felled/.test(past[0]), past[0].slice(0, 80));
    const deep = at(10, 0);
    ok('three wardens are felled by the tenth depth',
       deep.filter(t => /Felled/.test(t)).length === 3,
       deep.filter(t => /Felled/.test(t)).length + ' felled at depth 10');
  }

  /* 4. the Heart is its own row, and only the wins settle it */
  {
    const never = at(6, 0), there = at(FINAL_DEPTH, 0), done = at(FINAL_DEPTH, 2);
    const last = r => r[r.length - 1];
    ok('the Hollow is named from the start, since the menu names it too',
       /The Hollow/.test(last(never)), last(never).slice(0, 60));
    ok('and waits at the bottom for someone who has never been',
       /waits at the bottom/.test(last(never)), last(never));
    ok('is still beating for someone who got there and failed',
       /still beating/.test(last(there)), last(there));
    ok('and is put down only once it actually has been',
       /has been put down/.test(last(done)) && /Taken 2 times/.test(last(done)), last(done));
  }

  /* 5. the number is given something to be a number out of */
  {
    META.deepest = 7; META.wins = 0; renderBarrow();
    ok('the deepest reach says what it is out of',
       new RegExp('deepest reach 7 of ' + FINAL_DEPTH).test($('barrowSub').textContent),
       $('barrowSub').textContent);
  }

  /* 6. and a save that has never been written does not break it */
  {
    const keep = META.deepest;
    META.deepest = undefined; META.wins = undefined;
    let err = null;
    try { renderBarrow(); } catch (e) { err = e; }
    ok('a Barrow with nothing recorded in it still draws', err === null,
       err ? String(err.message) : 'drew ' + $('deepRows').children.length + ' rows');
    META.deepest = keep; META.wins = 0;
  }
}

"""

io.open(p, 'w', encoding='utf-8', newline='').write(s.replace(anchor, block + anchor))
print('how-deep tests inserted')
