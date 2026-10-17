/* What does the meta-progression actually cost, and what does a run pay? */
let total = 0;
const rows = [];
for (const p of PERKS) {
  META.perks = {};
  let sum = 0;
  for (let lv = 0; lv < p.max; lv++) { META.perks[p.id] = lv; sum += perkCost(p); }
  rows.push([p.name, p.max, sum]);
  total += sum;
}
META.perks = {};
console.log('PERK COSTS (echoes to take each to its cap)');
for (const [n, mx, c] of rows) console.log('   ' + n.padEnd(14) + ' x' + mx + '  ' + String(c).padStart(5));
console.log('   ' + 'EVERYTHING'.padEnd(14) + '      ' + String(total).padStart(5));

console.log('\nSHOP PRICES at a few depths (first purchase)');
for (const d of [1, 5, 10, 15]) {
  G.level = d;
  const P = { buys: {}, cls: CLASSES.sable };
  const line = SHOP.map(it => it.id + ' ' + shopPrice(P, it)).join('  ');
  console.log('   depth ' + String(d).padStart(2) + ': ' + line);
}

console.log('\nWHAT A RUN PAYS (echoes = gold/4 + score/40 + (depth-1)*8, doubled on a win)');
for (const [depth, gold, score] of [[3, 150, 600], [6, 400, 2000], [10, 900, 6000], [15, 1800, 14000], [21, 3000, 30000]]) {
  G.level = depth; G.gold = gold; G.score = score; G.won = false;
  const plain = runEchoes();
  G.won = true; const won = runEchoes();
  console.log('   reaching depth ' + String(depth).padStart(2) + ' with ' + String(gold).padStart(4) + ' gold: ' +
    String(plain).padStart(4) + ' echoes' + (depth === 21 ? '   (' + won + ' if the Heart falls)' : ''));
}
G.won = false;
