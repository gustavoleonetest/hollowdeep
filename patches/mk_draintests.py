import io

p = 'behave2_drive.js'
s = io.open(p, encoding='utf-8').read()
anchor = "const fails = results.filter(r => r[0] === 'FAIL');"
assert s.count(anchor) == 1, 'anchor not unique'
assert 'what the deep is taking' not in s, 'already inserted'

block = r"""/* ---------------- what the deep is taking ---------------- */
{
  /* seventy per cent of all health lost in a run is this, so the bar has to
     be telling the truth about it */
  const quiet = () => { G.enemies.length = 0; G.nests.length = 0; G.eshots.length = 0;
                        G.shots.length = 0; G.hazards.length = 0; G.items.length = 0; };

  /* 1. the number on the bar is the number the floor takes */
  startGame(['sable']); G.level = 6; genLevel();
  G.offer = null; G.offerQ.length = 0; G.state = 'play'; quiet();
  {
    const P = G.players[0]; P.hp = P.max; P.inv = 999;
    const rate = drainRate(P);
    const before = P.hp;
    for (let i = 0; i < 120; i++) { update(1 / 60); quiet(); }
    const lost = before - P.hp, want = rate * 2;
    ok('the bar draws the same drain the floor takes', Math.abs(lost - want) < .05,
       'lost ' + lost.toFixed(3) + ' vs ' + want.toFixed(3));
  }

  /* 2. pulling it into a function must not have changed the game: this is
        the original expression, written out, and it has to still match */
  {
    const orig = (lv, omen, co, mul) =>
      (.8 + Math.min(lv, 8) * .2 + Math.max(0, lv - 8) * .07) * omen * (co ? .85 : 1) * mul;
    const bad = [];
    for (const lv of [1, 4, 8, 9, 15, 21, 30]) {
      for (const mul of [1, .5, 1.5, 2.2]) {
        G.level = lv; G.omen = null; G.co = false;
        if (Math.abs(drainRate({ drainMul: mul }) - orig(lv, 1, false, mul)) > 1e-9) bad.push('d' + lv + 'x' + mul);
        G.co = true;
        if (Math.abs(drainRate({ drainMul: mul }) - orig(lv, 1, true, mul)) > 1e-9) bad.push('co d' + lv + 'x' + mul);
      }
    }
    G.co = false;
    const famine = OMENS.find(o => o.drain !== undefined);
    if (famine) {
      G.level = 6; G.omen = famine;
      if (Math.abs(drainRate({ drainMul: 1 }) - orig(6, famine.drain, false, 1)) > 1e-9) bad.push('famine');
    }
    G.omen = null;
    ok('the drain itself is unchanged by being given a name', bad.length === 0,
       bad.join(',') || '28 depths and multipliers, plus the famine');
  }

  /* 3. the band on the bar, drawn to scale */
  const pct = v => parseFloat(String(v).replace('%', ''));
  startGame(['ember']); G.level = 5; genLevel();
  G.offer = null; G.offerQ.length = 0; G.state = 'play'; quiet();
  {
    const P = G.players[0]; P.hp = P.max; P.drainMul = 1; recalc(P); P.hp = P.max;
    setHp(hud1, P);
    const lo = pct(hud1.drain.style.left), w = pct(hud1.drain.style.width);
    const wantW = Math.min(P.hp, drainRate(P) * DRAIN_AHEAD) / P.max * 100;
    ok('the band ends where your health ends', Math.abs(lo + w - P.hp / P.max * 100) < .01,
       (lo + w).toFixed(2) + '% vs ' + (P.hp / P.max * 100).toFixed(2) + '%');
    ok('and is as wide as ten seconds of drain', Math.abs(w - wantW) < .01,
       w.toFixed(2) + '% vs ' + wantW.toFixed(2) + '%');
    ok('which is a share of the bar you can actually see', w > 3 && w < 60, w.toFixed(1) + '%');
    ok('at the depth alone it is not marked as worse', !hud1.drain.classList.contains('worse'),
       hud1.drain.classList.toString() || 'plain');

    /* a pact that drinks you faster has to show */
    const narrow = w;
    P.pacts.push(PACTS.find(q => q.id === 'embers')); recalc(P); P.hp = P.max;
    setHp(hud1, P);
    const wide = pct(hud1.drain.style.width);
    ok('swearing the Pact of Embers widens the band', wide > narrow * 1.3,
       narrow.toFixed(1) + '% -> ' + wide.toFixed(1) + '%');
    ok('and turns it amber, because you chose that', hud1.drain.classList.contains('worse'),
       hud1.drain.classList.toString() || 'still plain');

    /* and the Barrow's slow blood pulls the other way */
    P.pacts.length = 0; P.perkDrain = -.24; recalc(P); P.hp = P.max;
    setHp(hud1, P);
    const slow = pct(hud1.drain.style.width);
    ok('slow blood narrows it again', slow < narrow * .9, narrow.toFixed(1) + '% -> ' + slow.toFixed(1) + '%');
    ok('and it is not marked as worse', !hud1.drain.classList.contains('worse'),
       hud1.drain.classList.toString() || 'plain');
    P.perkDrain = 0; recalc(P);
  }

  /* 4. it must never run off either end of the bar */
  {
    const P = G.players[0]; const bad = [];
    for (const hp of [P.max, P.max * .5, 12, 3, 1, .2]) {
      P.hp = hp; setHp(hud1, P);
      const lo = pct(hud1.drain.style.left), w = pct(hud1.drain.style.width);
      if (lo < -0.001 || w < -0.001 || lo + w > 100.001) bad.push('at ' + hp.toFixed(1) + ': ' + lo.toFixed(1) + '+' + w.toFixed(1));
    }
    ok('the band never runs off the bar, however little is left', bad.length === 0,
       bad.join('; ') || 'six levels of health checked');
    P.hp = P.max;
  }

  /* 5. nothing to draw for someone who is already down */
  {
    const P = G.players[0]; P.down = true; P.hp = 0; setHp(hud1, P);
    ok('and nothing is drawn for a delver who is down', hud1.drain.hidden === true,
       hud1.drain.hidden ? 'hidden' : 'still drawn');
    P.down = false; P.hp = P.max; setHp(hud1, P);
    ok('but it comes back when they do', hud1.drain.hidden === false);
  }

  /* 6. the stub's own classList has to be real, or checks 3 and 5 prove
        nothing at all: this is that check, checked */
  {
    const probe = document.createElement('div');
    probe.classList.toggle('x', true);
    const on = probe.classList.contains('x');
    probe.classList.toggle('x', false);
    ok('the harness can actually see a class being set', on && !probe.classList.contains('x'),
       'set ' + on + ', cleared ' + !probe.classList.contains('x'));
  }
}

"""

io.open(p, 'w', encoding='utf-8', newline='').write(s.replace(anchor, block + anchor))
print('drain tests inserted')
