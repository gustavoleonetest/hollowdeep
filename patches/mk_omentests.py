import io

p = 'behave2_drive.js'
s = io.open(p, encoding='utf-8').read()
anchor = "const fails = results.filter(r => r[0] === 'FAIL');"
assert s.count(anchor) == 1

block = r"""/* ---------------- omens change what a depth asks ---------------- */
/* force one on, build the depth, and measure it against a plain one */
function underOmen(id, depth, fn) {
  const o = id ? OMENS.find(x => x.id === id) : null;
  const real = rollOmen;
  rollOmen = () => o;
  try { startGame(['sable']); G.level = depth; genLevel(); return fn(G.players[0]); }
  finally { rollOmen = real; }
}
function avgOver(id, depth, n, fn) {
  let t = 0;
  for (let i = 0; i < n; i++) t += underOmen(id, depth, fn);
  return t / n;
}
const foeCount = () => G.enemies.length;
const nestCount = () => G.nests.length;
const kindCount = (k) => G.items.filter(i => i.kind === k).length;

ok('the first depths stay plain', [1, 2].every(d => rollOmen(d) === null));
ok('and a boss floor keeps its own shape', [3, 6, 9, 12].every(d => rollOmen(d) === null));
{ let n = 0; for (let i = 0; i < 600; i++) if (rollOmen(7)) n++;
  ok('an omen is a sometimes thing, not every depth', n > 60 && n < 420, n + '/600'); }
ok('every omen names itself and says why', OMENS.every(o => o.id && o.name && o.line && o.col));

{ const plain = avgOver(null, 8, 14, foeCount), horde = avgOver('horde', 8, 14, foeCount);
  ok('The Horde fills the floor', horde > plain * 1.3, plain.toFixed(1) + ' -> ' + horde.toFixed(1) + ' foes'); }
{ const held = underOmen('horde', 8, () => G.keys), keyItems = underOmen('horde', 8, () => kindCount('key'));
  ok('and hands you the door instead of hiding a key', held >= 1 && keyItems === 0, 'keys held ' + held + ', keys lying about ' + keyItems); }
{ const food = avgOver('famine', 8, 10, () => kindCount('food'));
  ok('Famine leaves nothing to eat', food === 0, food + ' food'); }
{ const plain = avgOver(null, 8, 14, () => kindCount('gold')), rich = avgOver('famine', 8, 14, () => kindCount('gold'));
  ok('but pays better for it', rich > plain * 1.4, plain.toFixed(1) + ' -> ' + rich.toFixed(1) + ' gold'); }
{ const plain = avgOver(null, 8, 14, foeCount), dark = avgOver('dark', 8, 14, foeCount);
  ok('Pitch Dark is emptier than a plain floor', dark < plain, plain.toFixed(1) + ' -> ' + dark.toFixed(1) + ' foes'); }
{ const plain = avgOver(null, 8, 14, nestCount), warren = avgOver('warren', 8, 14, nestCount);
  ok('The Warren is thick with crypts', warren > plain * 1.5, plain.toFixed(1) + ' -> ' + warren.toFixed(1) + ' crypts'); }
{ const plain = avgOver(null, 8, 14, foeCount), still = avgOver('still', 8, 14, foeCount);
  ok('Still Air is crowded instead', still > plain * 1.3, plain.toFixed(1) + ' -> ' + still.toFixed(1) + ' foes'); }
{ const plain = avgOver(null, 8, 12, () => kindCount('chest')), gild = avgOver('gilded', 8, 12, () => kindCount('chest'));
  ok('The Gilded Seam puts out more chests', gild > plain, plain.toFixed(1) + ' -> ' + gild.toFixed(1) + ' chests'); }
{ const elites = underOmen('gilded', 8, () => G.enemies.filter(e => e.elite).length),
      all = underOmen('gilded', 8, () => G.enemies.length);
  ok('and every foe on it is an elite', all > 0 && elites === all, elites + '/' + all); }

/* the clock: the one thing an omen must never break */
{ const rate = (id) => underOmen(id, 8, (P) => {
    P.hp = P.max; const h0 = P.hp;
    for (let i = 0; i < 120; i++) { P.inv = 999; update(1 / 60); }
    return h0 - P.hp;
  });
  const plain = rate(null), famine = rate('famine'), still = rate('still');
  ok('Famine winds the clock on', famine > plain, plain.toFixed(1) + ' -> ' + famine.toFixed(1) + ' health in 2s');
  ok('and Still Air stops it entirely', still < plain * .5, plain.toFixed(1) + ' -> ' + still.toFixed(1) + ' health in 2s'); }

/* whatever an omen does, the depth must still be finishable */
{ let broken = [];
  for (const o of OMENS) {
    for (let r = 0; r < 8; r++) {
      underOmen(o.id, 9, () => {
        const key = G.items.find(i => i.kind === 'key');
        if (!key && G.keys < 1) { broken.push(o.id + ':nokey'); return; }
        if (!G.exit) { broken.push(o.id + ':noexit'); return; }
        if (key) {
          const tx = Math.floor(key.x / T), ty = Math.floor(key.y / T);
          if (!openAt(key.x, key.y)) broken.push(o.id + ':keyburied');
        }
      });
    }
  }
  ok('every omen still leaves a finishable depth', broken.length === 0, broken.slice(0, 4).join(' ') || 'all six'); }
{ let bad = [];
  for (const o of OMENS) underOmen(o.id, 9, () => {
    if (G.enemies.length > 220) bad.push(o.id + ':' + G.enemies.length);
    if (G.nests.length > 60) bad.push(o.id + ':nests' + G.nests.length);
  });
  ok('and none of them floods the floor', bad.length === 0, bad.join(' ') || 'within bounds'); }
{ const banner = underOmen('horde', 8, () => G.banner && G.banner.sub);
  ok('the banner names the omen on arrival', /Horde/.test(banner || ''), banner || 'none'); }

"""

io.open(p, 'w', encoding='utf-8', newline='').write(s.replace(anchor, block + anchor))
print('omen tests inserted')
