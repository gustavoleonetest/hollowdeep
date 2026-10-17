import io

p = 'behave2_drive.js'
s = io.open(p, encoding='utf-8').read()
anchor = "const fails = results.filter(r => r[0] === 'FAIL');"
assert s.count(anchor) == 1

block = r"""/* ---------------- things move ---------------- */
{
  /* record every atlas frame the renderer asks for */
  function framesDrawn(fn) {
    const seen = {};
    const real = sprProp;
    sprProp = function (name) { seen[name] = (seen[name] || 0) + 1; return true; };
    try { fn(); } finally { sprProp = real; }
    return seen;
  }

  /* gold turns, using the eight frame sequence that sat unused in the atlas */
  { startGame(['thistle']); G.level = 3; genLevel(); G.offer = null; G.offerQ.length = 0;
    const it = { kind: 'gold', x: 100, y: 100, t: 0, v: 10 };
    const seen = framesDrawn(() => {
      for (let i = 0; i < 240; i++) { clock = i / 60; drawItem(it); }
    });
    const coins = Object.keys(seen).filter(k => /^coin_\d$/.test(k)).sort();
    ok('gold is drawn as a turning coin', coins.length === 8, coins.length + ' of 8 frames');
    ok('and not as the hand-drawn fallback', !seen['p_coin_pile']); }

  /* a scattered hoard must not turn in lockstep, or it reads as one object */
  { const a = { kind: 'gold', x: 100, y: 100, t: 0, v: 10 };
    const b = { kind: 'gold', x: 140, y: 100, t: 2.7, v: 10 };
    let differed = 0;
    for (let i = 0; i < 60; i++) {
      clock = i / 20;
      const fa = Object.keys(framesDrawn(() => drawItem(a)))[0];
      const fb = Object.keys(framesDrawn(() => drawItem(b)))[0];
      if (fa !== fb) differed++;
    }
    ok('two coins do not turn in step', differed > 30, differed + '/60 frames apart'); }

  /* a crypt half down looks half down: the atlas carries a broken state */
  { startGame(['sable']); G.level = 4; genLevel(); G.offer = null; G.offerQ.length = 0;
    const whole = framesDrawn(() => drawNest({ x: 90, y: 90, r: 15, hp: 95, max: 100, t: 0, flash: 0 }));
    const broke = framesDrawn(() => drawNest({ x: 90, y: 90, r: 15, hp: 15, max: 100, t: 0, flash: 0 }));
    ok('a whole crypt uses the whole sprite', !!whole['crypt'] && !whole['crypt_b']);
    ok('and a broken one shows it', !!broke['crypt_b'] && !broke['crypt'], Object.keys(broke).join(',')); }

  /* opening a chest hops it, and the hop lands */
  { const ys = [];
    const realT = ctx.translate;
    ctx.translate = function (x, y) { ys.push(y); };
    try {
      for (let i = 0; i <= 24; i++) { const f = { kind: 'chest', x: 0, y: 0, t: i / 30, big: true }; drawChestFx(f); }
    } finally { ctx.translate = realT; }
    const lift = ys.map(y => -y);           // translate(y - hop): more negative y is higher
    const peak = Math.max(...lift), first = lift[0], last = lift[lift.length - 1];
    ok('opening a chest lifts it off the floor', peak > first + 4, 'peak ' + peak.toFixed(1) + ' from ' + first.toFixed(1));
    ok('and it comes back down', last < peak - 4, 'settled at ' + last.toFixed(1)); }
}

"""

io.open(p, 'w', encoding='utf-8', newline='').write(s.replace(anchor, block + anchor))
print('animation tests inserted')
