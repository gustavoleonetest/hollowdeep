import io

p = 'behave2_drive.js'
s = io.open(p, encoding='utf-8').read()
anchor = "const fails = results.filter(r => r[0] === 'FAIL');"
assert s.count(anchor) == 1

block = r"""/* ---------------- told apart by more than colour ---------------- */
{
  /* Simulate each dichromacy in LMS, then measure CIE76 distance in Lab.
     Roughly: under about 12 is hard to tell at a glance in a dim moving
     scene, under 6 is the same colour. These numbers are a guard against a
     palette change quietly making two things identical, not a precise model
     of anyone's sight. */
  const toLin = c => { c /= 255; return c <= .04045 ? c / 12.92 : Math.pow((c + .055) / 1.055, 2.4); };
  const toSrgb = c => { c = Math.max(0, Math.min(1, c)); return (c <= .0031308 ? 12.92 * c : 1.055 * Math.pow(c, 1 / 2.4) - .055) * 255; };
  const hexRgb = h => { h = h.replace('#', ''); return [0, 2, 4].map(i => parseInt(h.slice(i, i + 2), 16)); };
  const mul = (m, v) => m.map(r => r[0] * v[0] + r[1] * v[1] + r[2] * v[2]);
  const RGB2LMS = [[.31399022, .63951294, .04649755], [.15537241, .75789446, .08670142], [.01775239, .10944209, .87256922]];
  const LMS2RGB = [[5.47221206, -4.6419601, .16963708], [-1.1252419, 2.29317094, -.1678952], [.02980165, -.19318073, 1.16364789]];
  const SIMM = {
    deuteranopia: [[1, 0, 0], [.9513092, 0, .04866992], [0, 0, 1]],
    protanopia: [[0, 1.05118294, -.05116099], [0, 1, 0], [0, 0, 1]],
    tritanopia: [[1, 0, 0], [0, 1, 0], [-.86744736, 1.86727089, 0]],
  };
  const sim = (hex, kind) => {
    const lin = hexRgb(hex).map(toLin);
    if (kind === 'normal') return lin.map(toSrgb);
    return mul(LMS2RGB, mul(SIMM[kind], mul(RGB2LMS, lin))).map(toSrgb);
  };
  const lab = rgb => {
    const lin = rgb.map(c => toLin(Math.max(0, Math.min(255, c))));
    const [x, y, z] = mul([[.4124, .3576, .1805], [.2126, .7152, .0722], [.0193, .1192, .9505]], lin);
    const f = t => t > .008856 ? Math.cbrt(t) : 7.787 * t + 16 / 116;
    const fx = f(x / .95047), fy = f(y), fz = f(z / 1.08883);
    return [116 * fy - 16, 500 * (fx - fy), 200 * (fy - fz)];
  };
  const dE = (a, b) => { const p = lab(a), q = lab(b); return Math.hypot(p[0] - q[0], p[1] - q[1], p[2] - q[2]); };
  const worstPair = (cols) => {
    const ks = Object.keys(cols);
    let out = { d: 1e9, a: '', b: '', kind: '' };
    for (const kind of ['normal', 'deuteranopia', 'protanopia', 'tritanopia']) {
      const S = {}; for (const k of ks) S[k] = sim(cols[k], kind);
      for (let i = 0; i < ks.length; i++) for (let j = i + 1; j < ks.length; j++) {
        const d = dE(S[ks[i]], S[ks[j]]);
        if (d < out.d) out = { d, a: ks[i], b: ks[j], kind };
      }
    }
    return out;
  };

  /* The minimap is the one surface that names nothing, so its markers are the
     ones that must not rely on colour. */
  { const w = worstPair({ exit: C.cyan, crypt: C.blood, chest: C.amber, floor: '#3a4359', door: '#a8743d' });
    ok('the minimap markers cannot be told apart by colour alone',
       w.d < 12, w.a + '/' + w.b + ' dE ' + w.d.toFixed(1) + ' under ' + w.kind + ' — hence the shapes'); }

  /* so each one draws a different shape */
  { const calls = [];
    const real = {};
    for (const k of ['arc', 'moveTo', 'lineTo', 'fillRect', 'strokeRect', 'stroke', 'fill', 'beginPath', 'clearRect']) {
      real[k] = mctx[k];
      mctx[k] = function (...a) { calls.push(k); return real[k] && real[k].apply(mctx, a); };
    }
    startGame(['sable']); G.level = 5; genLevel();
    let gg = 0; while (G.offer && gg++ < 20) applyUpgrade(0); G.offerQ.length = 0; G.state = 'play';
    G.seen.fill(1); fogA.fill(0);
    const P = G.players[0];
    G.nests.length = 0; G.items.length = 0;
    G.nests.push({ x: P.x + 60, y: P.y, r: 15, hp: 50, max: 100, t: 0, flash: 0 });
    G.items.push({ kind: 'chest', x: P.x - 60, y: P.y, t: 0 });
    calls.length = 0;
    drawMini();
    for (const k in real) mctx[k] = real[k];
    ok('the way out is drawn as a ring', calls.includes('arc'));
    ok('a crypt is drawn as a cross', calls.filter(c => c === 'lineTo').length >= 2, calls.filter(c => c === 'lineTo').length + ' strokes');
    ok('and you are outlined so you are findable', calls.includes('strokeRect')); }

  /* everything else names itself, so colour there is the second channel */
  ok('an elite says what it is in words', EAFF.every(a => typeof a.name === 'string' && a.name.length > 2));
  ok('and no two elites share one colour', new Set(EAFF.map(a => a.col)).size === EAFF.length,
     EAFF.map(a => a.col).join(' '));
  ok('an omen names itself too', OMENS.every(o => typeof o.name === 'string' && o.name.length > 2));
  ok('and no two omens share one colour', new Set(OMENS.map(o => o.col)).size === OMENS.length);

  /* the altars are the one place a shape is not available, so their three
     colours have to hold up on their own */
  { const w = worstPair(SHRINE_COL);
    ok('the three kinds of altar stay apart for every kind of sight', w.d > 20,
       w.a + '/' + w.b + ' dE ' + w.d.toFixed(1) + ' under ' + w.kind); }

  /* and loot rarity, which is read off a beam of light */
  { const w = worstPair({ magic: RARITY.magic.col, rare: RARITY.rare.col, fabled: RARITY.fabled.col, cursed: '#e0556b' });
    ok('loot rarities stay apart too', w.d > 15, w.a + '/' + w.b + ' dE ' + w.d.toFixed(1) + ' under ' + w.kind); }
}

"""

io.open(p, 'w', encoding='utf-8', newline='').write(s.replace(anchor, block + anchor))
print('colour-vision guards inserted')
