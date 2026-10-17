import io

p = 'behave2_drive.js'
s = io.open(p, encoding='utf-8').read()
anchor = "const fails = results.filter(r => r[0] === 'FAIL');"
assert s.count(anchor) == 1

block = r"""/* ---------------- saved progress survives being wrong ---------------- */
{
  const put = (o) => localStorage.setItem(META_KEY, typeof o === 'string' ? o : JSON.stringify(o));
  const keep = localStorage.getItem(META_KEY);

  /* numbers that arrived as strings used to make the next payout concatenate:
     "40" + 67 became "4067", written back, growing every run */
  put({ echoes: '40', best: '900', runs: '7', wins: '2', deepest: '9' });
  loadMeta();
  ok('a number saved as text is read as a number', typeof META.echoes === 'number', typeof META.echoes + ' ' + META.echoes);
  ok('and keeps its value', META.echoes === 40 && META.best === 900 && META.deepest === 9,
     META.echoes + '/' + META.best + '/' + META.deepest);
  { const e0 = META.echoes;
    G.won = false; G.gold = 0; G.score = 0; G.level = 2; bankRun();
    ok('so banking a run adds rather than concatenates', typeof META.echoes === 'number' && META.echoes > e0,
       e0 + ' -> ' + META.echoes); }

  put({ echoes: 'lots', best: null, deepest: 'deep', wins: NaN });
  loadMeta();
  ok('nonsense falls back to a sane default',
     META.echoes === 0 && META.best === 0 && META.deepest === 1 && META.wins === 0,
     [META.echoes, META.best, META.deepest, META.wins].join('/'));

  put({ echoes: -500, wins: -3, deepest: -9, runs: -1 });
  loadMeta();
  ok('negatives cannot be saved in', META.echoes >= 0 && META.wins >= 0 && META.deepest >= 1 && META.runs >= 0,
     [META.echoes, META.wins, META.deepest, META.runs].join('/'));

  put({ echoes: 12.7 });
  loadMeta();
  ok('and a fraction becomes a whole number', Number.isInteger(META.echoes), String(META.echoes));

  /* perk levels drive array maths and pricing, so they have to be whole and capped */
  put({ perks: { vigour: '2', slow: 99, flask: 'x', nonsense: 4, purse: -2 } });
  loadMeta();
  ok('a perk level saved as text still counts', perkLv('vigour') === 2, String(perkLv('vigour')));
  ok('and cannot exceed its cap', perkLv('slow') === PERKS.find(p => p.id === 'slow').max, String(perkLv('slow')));
  ok('an unreadable level is simply zero', perkLv('flask') === 0, String(perkLv('flask')));
  ok('a negative one too', perkLv('purse') === 0, String(perkLv('purse')));
  ok('and an unknown perk is dropped', META.perks.nonsense === undefined);
  ok('every kept level is a whole number', Object.keys(META.perks).every(k => Number.isInteger(META.perks[k])),
     JSON.stringify(META.perks));

  put('{ this is not json');
  loadMeta();
  ok('a torn save does not throw', typeof META.echoes === 'number');

  put({ perks: 'not an object' });
  loadMeta();
  ok('and neither does a perks field that is not one', META.perks && typeof META.perks === 'object');

  /* the price of a perk has to stay a real number whatever was loaded */
  ok('perk prices stay finite', PERKS.every(p => Number.isFinite(perkCost(p))));

  if (keep === null) localStorage.removeItem(META_KEY); else localStorage.setItem(META_KEY, keep);
  loadMeta();
}

"""

io.open(p, 'w', encoding='utf-8', newline='').write(s.replace(anchor, block + anchor))
print('save-robustness tests inserted')
