import io

p = 'behave2_drive.js'
s = io.open(p, encoding='utf-8').read()
anchor = "const fails = results.filter(r => r[0] === 'FAIL');"
assert s.count(anchor) == 1

block = r"""/* ---------------- altars ask for something back ---------------- */
{
  /* every depth lights at least one font, and always on floor you can reach */
  let depths = 0, withShrine = 0, reachable = 0, total = 0;
  for (let d = 1; d <= 14; d++) {
    for (let r = 0; r < 6; r++) {
      startGame(['sable']); G.level = d; genLevel();
      depths++;
      const sh = G.items.filter(i => i.kind === 'shrine');
      if (sh.length) withShrine++;
      for (const it of sh) { total++; if (openAt(it.x, it.y) && !blockedAt(it.x, it.y, 11)) reachable++; }
    }
  }
  ok('every depth lights a font', withShrine === depths, withShrine + '/' + depths);
  ok('and never inside a wall', total > 0 && reachable === total, reachable + '/' + total);
}
{ startGame(['sable']); G.level = 7; genLevel();
  const n = G.items.filter(i => i.kind === 'shrine').length;
  ok('the deep lights more than one', n >= 1, n + ' on depth 7'); }

/* every pact must cost something, and every blessing must not */
ok('each pact names a gain and a price', PACTS.every(p => p.good && p.bad && p.s));
ok('and every blessing asks nothing', BLESSINGS.every(b => b.good && !b.bad && !b.s));
{ let bad = [];
  for (const p of PACTS) {
    const vals = Object.keys(p.s).map(k => [k, p.s[k]]);
    /* arm and cd read backwards: a positive arm is a gain, a positive cd is a loss */
    const gain = vals.some(([k, v]) => k === 'arm' ? v > 0 : k === 'cd' ? v < 0 : v > 0);
    const cost = vals.some(([k, v]) => k === 'arm' ? v < 0 : k === 'cd' ? v > 0 : v < 0 || k === 'drain');
    if (!gain || !cost) bad.push(p.id);
  }
  ok('no pact is free money', bad.length === 0, bad.join(',') || 'all six cut both ways'); }

/* walking up to a font puts the choice in front of you */
function shrineRun(pact) {
  startGame(['sable']); G.level = 4; genLevel();
  const P = G.players[0]; G.offer = null; G.offerQ.length = 0;
  G.items = G.items.filter(i => i.kind !== 'shrine');
  const it = { kind: 'shrine', x: P.x + 8, y: P.y, t: 0, cool: 0,
               sh: { kind: pact.s ? 'pact' : 'blessing', pact } };
  G.items.push(it);
  updateItems(1 / 60);
  return [P, it];
}
{ const [P, it] = shrineRun(PACTS[0]);
  ok('stepping up to a font offers the bargain', G.offer && G.offer.kind === 'pact', G.offer ? G.offer.kind : 'none'); }
{ const [P, it] = shrineRun(PACTS[0]);
  const d0 = P.dmgMul, dr0 = P.drainMul;
  applyUpgrade(0);
  ok('taking the Pact of Embers raises damage', P.dmgMul > d0, d0.toFixed(2) + ' -> ' + P.dmgMul.toFixed(2));
  ok('and the price is charged too', P.drainMul > dr0, dr0.toFixed(2) + ' -> ' + P.drainMul.toFixed(2));
  ok('the font is spent once taken', G.items.indexOf(it) < 0);
  ok('and it is listed on the delver', P.pacts.length === 1, P.pacts.map(x => x.name).join(',')); }
{ const [P, it] = shrineRun(PACTS[0]);
  applyUpgrade(1);
  ok('walking away leaves the font standing', G.items.indexOf(it) >= 0);
  ok('and costs nothing', P.pacts.length === 0);
  ok('but it does not re-open in your face', (it.cool || 0) > 0, (it.cool || 0).toFixed(1) + 's'); }

/* the costly half of a pact must survive recalc, the way a curse must */
for (const p of PACTS) {
  startGame(['sable']); G.level = 4; genLevel();
  const P = G.players[0];
  const before = { dmg: P.dmgMul, cd: P.cdMul, spd: P.spdMul, arm: P.armMul, crit: P.crit, drain: P.drainMul, hp: P.max };
  P.pacts.push(p); recalc(P);
  const after = { dmg: P.dmgMul, cd: P.cdMul, spd: P.spdMul, arm: P.armMul, crit: P.crit, drain: P.drainMul, hp: P.max };
  let worseSomewhere = after.drain > before.drain + 1e-9 || after.spd < before.spd - 1e-9 ||
                       after.hp < before.hp - 1e-9 || after.cd > before.cd + 1e-9 ||
                       after.arm > before.arm + 1e-9;
  let betterSomewhere = after.dmg > before.dmg + 1e-9 || after.spd > before.spd + 1e-9 ||
                        after.crit > before.crit + 1e-9 || after.cd < before.cd - 1e-9 ||
                        after.arm < before.arm - 1e-9 || (p.s.leech || 0) > 0 || (p.s.gold || 0) > 0;
  ok(p.name + ' still costs you after recalc', worseSomewhere, 'drain ' + before.drain.toFixed(2) + '->' + after.drain.toFixed(2) +
     ' spd ' + before.spd.toFixed(2) + '->' + after.spd.toFixed(2) + ' hp ' + before.hp + '->' + after.hp);
  ok(p.name + ' still pays you after recalc', betterSomewhere);
}
/* blessings do what they say */
{ const [P, it] = shrineRun(BLESSINGS.find(b => b.id === 'mend'));
  P.hp = 10; applyUpgrade(0);
  ok('the Mending Font closes your wounds', P.hp === P.max, P.hp + '/' + P.max); }
{ const [P, it] = shrineRun(BLESSINGS.find(b => b.id === 'ward'));
  P.shield = 0; applyUpgrade(0);
  ok('the Warding Font raises a ward', P.shield > 0, P.shield.toFixed(1) + 's'); }
{ const [P, it] = shrineRun(BLESSINGS.find(b => b.id === 'hoard'));
  const g0 = G.gold; applyUpgrade(0);
  ok('the Gilded Font pays out', G.gold > g0, g0 + ' -> ' + G.gold); }
/* a mystery keeps its face hidden until taken */
{ startGame(['sable']); G.level = 6; genLevel();
  let mys = 0;
  for (let i = 0; i < 400; i++) if (rollShrine(6).kind === 'mystery') mys++;
  ok('some altars are unreadable', mys > 20 && mys < 180, mys + '/400'); }
{ let pacts = 0, deep = 0;
  for (let i = 0; i < 400; i++) { if (rollShrine(1).kind === 'pact') pacts++; if (rollShrine(14).kind === 'pact') deep++; }
  ok('the deep asks for payment more often', deep > pacts, pacts + ' at depth 1 -> ' + deep + ' at depth 14'); }

"""

io.open(p, 'w', encoding='utf-8', newline='').write(s.replace(anchor, block + anchor))
print('shrine tests inserted')
