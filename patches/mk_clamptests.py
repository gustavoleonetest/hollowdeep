import io

p = 'behave2_drive.js'
s = io.open(p, encoding='utf-8').read()
anchor = "const fails = results.filter(r => r[0] === 'FAIL');"
assert s.count(anchor) == 1, 'anchor not unique'
assert 'nothing runs away with itself' not in s, 'already inserted'

block = r"""/* ---------------- nothing runs away with itself ----------------
   This game once shipped a damage multiplier of two hundred and thirty
   million, from an upgrade that multiplied where it should have added. The
   clamps in recalc are the scar tissue from that, and scar tissue is worth
   a test: a bound nobody checks is a bound that quietly stops holding. */
{
  const everything = () => {
    startGame(['bulwark']); G.level = 21; genLevel();
    G.offer = null; G.offerQ.length = 0; G.state = 'play';
    G.enemies.length = 0; G.items.length = 0; G.omen = null;
    const P = G.players[0];
    /* the most extravagant thing the dungeon can actually hand someone:
       three fabled pieces, every pact, and a full set on top */
    for (const slot of SLOTS) {
      P.gear[slot] = { slot, base: 'Greed', rar: 'fabled', col: '#e08a3c', name: 'Absurd ' + slot,
        s: { dmg: .9, arm: .9, hp: 400, crit: .9, spd: .9, cd: -.9, dash: -.9,
             leech: .9, thorns: .9, gold: .9, sp: 9, drain: -.9 },
        ilvl: 21, set: 'quick', setName: 'The Quickened' };
    }
    P.pacts.length = 0;
    for (const q of PACTS) P.pacts.push(q);
    /* and every shop upgrade bought to its cap */
    for (const it of SHOP) {
      const cap = it.id === 'master' ? 6 : (it.max || 1);
      for (let n = 0; n < cap; n++) { P.buys = P.buys || {}; P.buys[it.id] = n + 1; if (it.id !== 'draught' && it.id !== 'elixir') applyUp(P, it.id, 1); }
    }
    recalc(P);
    return P;
  };

  const P = everything();
  const bounds = [
    ['move speed', P.spdMul, .4, 1.95],
    ['armour', P.armMul, .32, 2.2],
    ['dash', P.dashMul, .35, 2.4],
    ['attack speed', P.cdMul, .3, Infinity],
    ['critical chance', P.crit, 0, .75],
    ['the drain', P.drainMul, .3, Infinity],
  ];
  const escaped = bounds.filter(([, v, lo, hi]) => !(v >= lo - 1e-9 && v <= hi + 1e-9));
  ok('no multiplier escapes its clamp, however much is piled on',
     escaped.length === 0,
     escaped.map(([n, v]) => n + ' = ' + v).join('; ') ||
       bounds.map(([n, v]) => n + ' ' + (+v).toFixed(2)).join(', '));

  ok('every one of them is still a number', bounds.every(([, v]) => Number.isFinite(v)),
     bounds.map(([n, v]) => n + ' ' + v).join(', '));

  /* damage is deliberately not clamped -- it is the one that is supposed to
     grow -- so the guard is that it stays somewhere a human could reach */
  ok('damage grows without running away', Number.isFinite(P.dmgMul) && P.dmgMul > 1 && P.dmgMul < 500,
     'x' + P.dmgMul.toFixed(1));
  ok('and health stays a sane whole number',
     Number.isFinite(P.max) && P.max > 0 && P.max === Math.round(P.max) && P.max < 100000,
     String(P.max));

  /* and the delver is still playable with all of it on */
  {
    let err = null;
    try { for (let i = 0; i < 300; i++) update(1 / 60); } catch (e) { err = e; }
    ok('and a delver wearing the lot survives five seconds of play',
       err === null && Number.isFinite(G.players[0].hp),
       err ? String(err.message) : 'hp ' + Math.round(G.players[0].hp));
  }

  /* the specific shape of the old bug: an upgrade bought many times must
     add, not compound */
  {
    startGame(['ember']); G.level = 3; genLevel();
    G.offer = null; G.offerQ.length = 0; G.state = 'play';
    const Q = G.players[0], first = Q.up.dmg;
    applyUp(Q, 'power', 1); recalc(Q); const one = Q.up.dmg;
    for (let i = 0; i < 5; i++) { applyUp(Q, 'power', 1); }
    recalc(Q);
    const six = Q.up.dmg;
    const step = one - first;
    ok('buying Might six times adds six steps rather than compounding',
       Math.abs((six - first) - 6 * step) < 1e-9,
       'one step ' + step.toFixed(3) + ', six gave ' + (six - first).toFixed(3));
  }
}

"""

io.open(p, 'w', encoding='utf-8', newline='').write(s.replace(anchor, block + anchor))
print('clamp tests inserted')
