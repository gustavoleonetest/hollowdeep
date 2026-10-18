import io

p = 'behave2_drive.js'
s = io.open(p, encoding='utf-8').read()
anchor = "const fails = results.filter(r => r[0] === 'FAIL');"
assert s.count(anchor) == 1, 'anchor not unique'
assert 'a way out of a bad descent' not in s, 'already inserted'

block = r"""/* ---------------- a way out of a bad descent ---------------- */
{
  const openPause = () => {
    G.paused = false; pauseShown = false; $('paused').hidden = true;
    G.state = 'play'; G.paused = true; frame(0);
  };

  /* 1. the controls are on it, which is the only place a phone can read
        them: the bar above the stage hides itself the moment you play */
  {
    startGame(['thistle']); G.level = 3; genLevel();
    G.offer = null; G.offerQ.length = 0; openPause();
    const was = btnsOn;
    ok('the controls are on the sheet', $('pauseKeys').textContent.length > 20,
       $('pauseKeys').textContent.slice(0, 70));
    /* and they are the right ones for how the game is being played */
    btnsOn = true; showPaused();
    const touch = $('pauseKeys').textContent;
    btnsOn = false; showPaused();
    const keys = $('pauseKeys').textContent;
    btnsOn = was;
    ok('a phone is told about halves of the screen', /Left half/.test(touch), touch.slice(0, 60));
    ok('and a keyboard about keys', /WASD/.test(keys) && !/Left half/.test(keys), keys.slice(0, 60));
  }

  /* 2. THE TRAP: the overlay resumes on any click, so the button that ends
        a run would otherwise simply carry on instead */
  {
    startGame(['sable']); G.level = 4; genLevel();
    G.offer = null; G.offerQ.length = 0; openPause();
    let stopped = false;
    $('giveUp').dispatch('click', { type: 'click', stopPropagation: () => { stopped = true; }, preventDefault() {} });
    ok('the give-up button keeps its click to itself', stopped,
       stopped ? 'propagation stopped' : 'the click would have resumed the game');
    ok('and the run is still going after one press', G.state === 'play' && G.paused === true,
       G.state + ', paused ' + G.paused);
  }

  /* 3. it asks once before it does it */
  {
    ok('one press only arms it', /Really/.test($('giveUp').textContent), $('giveUp').textContent);
    const press = () => $('giveUp').dispatch('click', { type: 'click', stopPropagation() {}, preventDefault() {} });
    press();
    ok('the second press ends the run', G.state === 'dead', G.state);
    ok('and it is recorded as turning back, not as being killed', G.gaveUp === true);
  }

  /* 4. what you earned on the way down still counts */
  {
    META.echoes = 0; META.runs = 0;
    startGame(['ember']); G.level = 7; genLevel();
    G.offer = null; G.offerQ.length = 0; G.state = 'play';
    G.gold = 400; G.score = 3000; G.kills = 120;
    saveRun();
    openPause();
    const press = () => $('giveUp').dispatch('click', { type: 'click', stopPropagation() {}, preventDefault() {} });
    press(); press();
    ok('giving up banks the echoes the descent earned', META.echoes > 0, '+' + META.echoes);
    ok('and counts as a descent taken', META.runs === 1, String(META.runs));
    ok('and the depth reached is remembered', META.deepest >= 7, String(META.deepest));
    ok('while the saved run is cleared, as any ending clears it',
       localStorage.getItem('hollowdeep-run') === null, 'still there');
  }

  /* 5. and the summary says what actually happened */
  {
    showOver();
    ok('the screen does not claim the deep took you', /turned back/i.test($('oTitle').textContent),
       $('oTitle').textContent);
    ok('and says where you left off', /left the dark at depth 7/.test($('oLine').textContent),
       $('oLine').textContent);
  }

  /* 6. a real death still reads as a death */
  {
    startGame(['bulwark']); G.level = 5; genLevel();
    G.offer = null; G.offerQ.length = 0; G.state = 'play';
    for (const P of G.players) { P.hp = 0; P.down = true; }
    die(); showOver();
    ok('a delver who actually died is not said to have turned back',
       /Swallowed/.test($('oTitle').textContent) && G.gaveUp === false, $('oTitle').textContent);
  }

  /* 7. and a fresh descent starts without the mark on it */
  {
    G.gaveUp = true;
    startGame(['sable']);
    ok('a new descent is not born given up on', G.gaveUp === false);
  }
}

"""

io.open(p, 'w', encoding='utf-8', newline='').write(s.replace(anchor, block + anchor))
print('give-up tests inserted')
