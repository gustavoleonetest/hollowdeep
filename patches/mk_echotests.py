import io

p = 'behave2_drive.js'
s = io.open(p, encoding='utf-8').read()
anchor = "const fails = results.filter(r => r[0] === 'FAIL');"
assert s.count(anchor) == 1, 'anchor not unique'
assert 'where the echoes came from' not in s, 'already inserted'

block = r"""/* ---------------- where the echoes came from ----------------
   Echoes buy the Barrow, and the Barrow is the only thing that carries
   from one descent to the next. The death screen printed the number and
   said nothing about where it came from, so the loop meant to pull a
   player back was never described to them. */
{
  const at = (gold, score, level, won) => {
    startGame(['sable']); G.state = 'play';
    G.gold = gold; G.score = score; G.level = level; G.won = !!won;
    return echoParts();
  };

  /* 1. the explanation is the arithmetic, not a second copy of it */
  {
    const bad = [];
    for (const g of [0, 37, 440, 5000]) {
      for (const sc of [0, 311, 4210, 90000]) {
        for (const lv of [1, 7, 21]) {
          for (const won of [false, true]) {
            const p = at(g, sc, lv, won);
            /* the old formula, written out, must still be what is paid */
            const orig = Math.max(1, Math.round(g * .25 + sc / 40 + (lv - 1) * 8)) * (won ? 2 : 1);
            if (p.total !== orig) bad.push(g + '/' + sc + '/d' + lv + (won ? '/won' : '') +
              ': ' + p.total + ' vs ' + orig);
          }
        }
      }
    }
    ok('naming the parts did not change what a run pays', bad.length === 0,
       bad.slice(0, 2).join('; ') || '48 combinations');
  }

  /* 2. and the parts add up, because a player will add them */
  {
    const bad = [];
    for (const g of [0, 37, 440, 5000, 9]) {
      for (const sc of [0, 311, 4210, 7, 90000]) {
        for (const lv of [1, 2, 7, 21]) {
          const p = at(g, sc, lv, false);
          if (p.gold + p.score + p.depth !== p.base) {
            bad.push(g + '/' + sc + '/d' + lv + ': ' + p.gold + '+' + p.score + '+' + p.depth +
              ' = ' + (p.gold + p.score + p.depth) + ', not ' + p.base);
          }
          if (p.gold < 0 || p.score < 0 || p.depth < 0) bad.push('negative at ' + g + '/' + sc + '/d' + lv);
        }
      }
    }
    ok('the parts sum to the total, in every case tried', bad.length === 0,
       bad.slice(0, 2).join('; ') || '100 combinations');
  }

  /* 3. each part moves with the thing it is named after */
  {
    const base = at(100, 1000, 5, false);
    ok('more gold is more echoes from gold', at(900, 1000, 5, false).gold > base.gold,
       base.gold + ' -> ' + at(900, 1000, 5, false).gold);
    ok('a better score is more from the score', at(100, 9000, 5, false).score > base.score,
       base.score + ' -> ' + at(100, 9000, 5, false).score);
    ok('and going deeper is more from the depth', at(100, 1000, 15, false).depth > base.depth,
       base.depth + ' -> ' + at(100, 1000, 15, false).depth);
    ok('a first-floor death earns nothing from depth', at(100, 1000, 1, false).depth === 0,
       String(at(100, 1000, 1, false).depth));
  }

  /* 4. carrying the Heart out doubles it, and says so */
  {
    const lost = at(400, 4000, 21, false), won = at(400, 4000, 21, true);
    ok('carrying the Heart out doubles the lot', won.total === lost.total * 2,
       lost.total + ' -> ' + won.total);
    ok('and only then is it called doubled', won.doubled === true && lost.doubled === false);
  }

  /* 5. the screen actually says it */
  {
    startGame(['ember']); G.level = 9; genLevel();
    G.offer = null; G.offerQ.length = 0; G.state = 'play';
    G.gold = 612; G.score = 8840;
    die(); showOver();
    const line = $('oEchHow').textContent, p = echoParts();
    ok('the death screen explains where the echoes came from', line.length > 40, line.slice(0, 90));
    ok('with the three numbers it actually used',
       line.indexOf(String(p.gold)) >= 0 && line.indexOf(String(p.score)) >= 0 &&
       line.indexOf(String(p.depth)) >= 0,
       'gold ' + p.gold + ', score ' + p.score + ', depth ' + p.depth);
    ok('and says what they are for', /Barrow/.test(line), line.slice(-60));
    ok('without claiming a doubling that did not happen', !/doubled/.test(line), line.slice(-60));
  }

  /* 6. and on a won run it does claim it */
  {
    startGame(['ember']); G.level = FINAL_DEPTH; genLevel();
    G.offer = null; G.offerQ.length = 0; G.state = 'play';
    G.gold = 400; G.score = 9000; G.won = true;
    G.state = 'won'; showOver();
    ok('a run that carried the Heart out is told the lot was doubled',
       /doubled/.test($('oEchHow').textContent), $('oEchHow').textContent.slice(-70));
  }
}

"""

io.open(p, 'w', encoding='utf-8', newline='').write(s.replace(anchor, block + anchor))
print('echo breakdown tests inserted')
