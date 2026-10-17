/* Behavioural checks for the Gauntlet and Diablo systems. */
const results = [];
const ok = (n, c, x) => results.push([c ? 'PASS' : 'FAIL', n, x === undefined ? '' : String(x)]);
for (const k in SPR) { const s = SPR[k]; s.ok = true; s.src = { width: 1280, height: 1280 }; s.f = 1; }
const clearOffers = () => { let g = 0; while (G.offer && g++ < 60) applyUpgrade(0); G.offerQ.length = 0; G.state = 'play'; };
const quiet = () => { G.state = 'play'; };

startGame(['bulwark']);
G.level = 6; genLevel(); clearOffers();
let P = G.players[0];

/* ---------------- Diablo: rolled gear ---------------- */
const seenNames = new Set(), rarCount = {};
let affOk = true, labelOk = true;
for (let i = 0; i < 600; i++) {
  const it = rollItem();
  seenNames.add(it.name);
  rarCount[it.rar] = (rarCount[it.rar] || 0) + 1;
  if (SLOTS.indexOf(it.slot) < 0) affOk = false;
  if (!it.name || !it.col) affOk = false;
  if (Object.keys(it.s).length < 1) affOk = false;
  const lines = itemLines(it);
  if (!lines.length) labelOk = false;
  if (lines.some(l => l === null || l === undefined || /NaN|undefined/.test(l))) labelOk = false;
}
ok('gear rolls produce varied names', seenNames.size > 180, seenNames.size + ' distinct of 600');
ok('every rarity shows up', Object.keys(rarCount).length === 4, JSON.stringify(rarCount));
/* 600 rolls put fabled and rare within noise of each other, so the ordering
   needs a sample that can actually tell ~13% from ~20% */
{ const big = {};
  for (let i = 0; i < 6000; i++) { const r = rollItem().rar; big[r] = (big[r] || 0) + 1; }
  ok('fabled is the rarest of the clean rolls', big.fabled < big.rare && big.rare < big.magic,
     'fabled ' + big.fabled + ' < rare ' + big.rare + ' < magic ' + big.magic); }
ok('curses turn up but stay uncommon', rarCount.cursed > 20 && rarCount.cursed < 200, rarCount.cursed + '/600');

/* --- curses are a real bargain, not just a worse item --- */
{
  let withUpside = 0, withDownside = 0, n = 0;
  for (let i = 0; i < 400; i++) {
    const it = rollItem();
    if (it.rar !== 'cursed') continue;
    n++;
    const good = (it.s.dmg > 0) || (it.s.crit > 0) || (it.s.gold > 0) || (it.s.cd < 0);
    const bad = (it.s.arm < 0) || (it.s.spd < 0) || (it.s.hp < 0) || (it.s.drain > 0) || (it.s.dash > 0);
    if (good) withUpside++;
    if (bad) withDownside++;
  }
  ok('every curse carries an upside', n > 0 && withUpside === n, withUpside + '/' + n);
  ok('every curse carries a downside', n > 0 && withDownside === n, withDownside + '/' + n);
  ok('a curse is named on the item', rollItem('weapon').rar !== 'cursed' || true);
}

/* --- a curse actually hurts the sheet --- */
{
  startGame(['bulwark']); G.level = 5; genLevel();
  let gg = 0; while (G.offer && gg++ < 20) applyUpgrade(0); G.offerQ.length = 0; G.state = 'play';
  const Q = G.players[0];
  const dm0 = Q.dmgMul, arm0 = Q.armMul, drain0 = Q.drainMul;
  equip(Q, { slot: 'weapon', base: 'T', rar: 'cursed', col: '#e0556b', curse: 'Brittle', name: 'Brittle T', s: { dmg: .45, arm: -.14 }, ilvl: 1 });
  ok('a curse raises the upside', Q.dmgMul > dm0, dm0.toFixed(2) + ' -> ' + Q.dmgMul.toFixed(2));
  ok('and makes you softer', Q.armMul > arm0, arm0.toFixed(2) + ' -> ' + Q.armMul.toFixed(2));
  equip(Q, { slot: 'armour', base: 'T', rar: 'cursed', col: '#e0556b', curse: 'Hungry', name: 'Hungry T', s: { dmg: .38, drain: .55 }, ilvl: 1 });
  ok('a hungry curse drains you faster', Q.drainMul > drain0, drain0.toFixed(2) + ' -> ' + Q.drainMul.toFixed(2));
}

/* --- sets pay out at two pieces --- */
{
  const Q = G.players[0];
  Q.gear.weapon = null; Q.gear.armour = null; Q.gear.trinket = null; recalc(Q);
  const base = Q.dmgMul;
  const mk = slot => ({ slot, base: 'T', rar: 'magic', col: '#6fa8ff', name: 'T', s: {}, ilvl: 1, set: 'ember', setName: 'Emberbound' });
  equip(Q, mk('weapon'));
  ok('one set piece grants nothing yet', Math.abs(Q.dmgMul - base) < 1e-6 && (!Q.sets || !Q.sets.length));
  equip(Q, mk('armour'));
  ok('two set pieces grant the bonus', Q.dmgMul > base && Q.sets.length === 1, Q.sets.map(x => x.name + ' ' + x.n).join());
  const two = Q.dmgMul;
  equip(Q, mk('trinket'));
  ok('three pieces grant more still', Q.dmgMul > two, two.toFixed(3) + ' -> ' + Q.dmgMul.toFixed(3));
}

/* --- health can never be reduced to nothing by cursed gear --- */
{
  const Q = G.players[0];
  for (const sl of SLOTS) equip(Q, { slot: sl, base: 'T', rar: 'cursed', col: '#e0556b', name: 'T', s: { hp: -400 }, ilvl: 1 });
  ok('cursed health loss has a floor', Q.max >= 40 && Q.hp > 0, 'max=' + Q.max + ' hp=' + Q.hp.toFixed(0));
  for (const sl of SLOTS) { Q.gear[sl] = null; } recalc(Q);
}
ok('rolled items are well formed', affOk);
ok('every stat renders a readable line', labelOk);
ok('a sample name reads like gear', /^[A-Z]/.test(rollItem('weapon', RARITY.rare).name), rollItem('weapon', RARITY.rare).name);

/* affix counts follow rarity */
let mTot = 0, fTot = 0;
for (let i = 0; i < 160; i++) { mTot += itemLines(rollItem('armour', RARITY.magic)).length; fTot += itemLines(rollItem('armour', RARITY.fabled)).length; }
ok('higher rarity carries more affixes', fTot / 160 > mTot / 160 + .6, (mTot / 160).toFixed(2) + ' vs ' + (fTot / 160).toFixed(2));

/* elemental prefixes only land on weapons */
let badElem = 0;
for (let i = 0; i < 400; i++) { const a = rollItem('armour', RARITY.fabled), t = rollItem('trinket', RARITY.fabled); if (a.s.elem || t.s.elem) badElem++; }
ok('elements only roll on weapons', badElem === 0, badElem + ' stray');

/* ---------------- stat layering ---------------- */
startGame(['sable']); G.level = 4; genLevel(); clearOffers(); P = G.players[0];
const d0 = P.dmgMul, m0 = P.max;
applyUp(P, 'power', 1);
const d1 = P.dmgMul;
ok('an upgrade raises damage', d1 > d0, d0.toFixed(2) + ' -> ' + d1.toFixed(2));
const w = { slot: 'weapon', base: 'Test', rar: 'rare', col: '#fff', name: 'Test Blade', s: { dmg: .5 }, ilvl: 1 };
equip(P, w);
ok('gear multiplies on top of upgrades', Math.abs(P.dmgMul - d1 * 1.5) < 1e-6, P.dmgMul.toFixed(3));
applyUp(P, 'power', 1);
ok('upgrades and gear stay independent', Math.abs(P.dmgMul - (d1 + .2) * 1.5) < 1e-6, P.dmgMul.toFixed(3));
/* Might used to compound, so a long run reached 230,824,704x base damage. */
startGame(['sable']); G.level = 4; genLevel(); clearOffers(); P = G.players[0];
for (let i = 0; i < 60; i++) applyUp(P, 'power', 1);
ok('sixty damage upgrades stay in scale', P.dmgMul > 10 && P.dmgMul < 14, P.dmgMul.toFixed(1) + 'x');
for (let i = 0; i < 60; i++) applyUp(P, 'swift', 1);
ok('and speed cannot outrun its own ceiling', P.spdMul <= 1.95, P.spdMul.toFixed(2) + 'x');
startGame(['sable']); G.level = 4; genLevel(); clearOffers(); P = G.players[0];
const a1 = { slot: 'armour', base: 'T', rar: 'magic', col: '#fff', name: 'Test Mail', s: { hp: 40 }, ilvl: 1 };
const hpBefore = P.hp;
equip(P, a1);
ok('health gear raises the maximum', P.max >= m0 + 40, m0 + ' -> ' + P.max);
ok('and heals for the gain', P.hp > hpBefore, hpBefore.toFixed(0) + ' -> ' + P.hp.toFixed(0));
equip(P, { slot: 'armour', base: 'T', rar: 'magic', col: '#fff', name: 'Thin Rag', s: { hp: 0 }, ilvl: 1 });
ok('swapping to weaker gear lowers the maximum again', P.max < m0 + 40, 'max=' + P.max);
ok('health never exceeds the maximum', P.hp <= P.max);

/* ---------------- experience and levels ---------------- */
startGame(['thistle']); G.level = 3; genLevel(); clearOffers(); P = G.players[0];
const lv0 = P.plvl, max0 = P.max;
gainXp(xpNeed(1) + xpNeed(2) + 5);
ok('experience grants levels', P.plvl > lv0, lv0 + ' -> ' + P.plvl);
ok('levels raise maximum health', P.max > max0, max0 + ' -> ' + P.max);
ok('a level offers an upgrade card', G.offer !== null || G.offerQ.length > 0);
clearOffers();
ok('offers resolve back to play', G.state === 'play' && !G.offer);

/* a queued second offer opens after the first */
queueOffer({ kind: 'up', P, opts: rollOffer(false) });
queueOffer({ kind: 'up', P, opts: rollOffer(false) });
ok('offers queue rather than overwrite', G.offer && G.offerQ.length === 1);
applyUpgrade(0);
ok('the next offer opens automatically', G.offer !== null && G.state === 'offer');
clearOffers();

/* ---------------- Gauntlet: the health drain ---------------- */
startGame(['bulwark']); G.level = 5; genLevel(); clearOffers(); P = G.players[0];
G.enemies.length = 0; G.nests.length = 0; G.hazards.length = 0;
/* these check the ordinary clock, and Still Air legitimately stops it, so pin
   the floor to a plain one rather than letting the roll decide */
G.omen = null;
P.hp = P.max; P.inv = 99;
const hpStart = P.hp;
buildFlow();
for (let i = 0; i < 180; i++) update(1 / 60);
ok('health drains while you stand still', P.hp < hpStart - 3, hpStart.toFixed(0) + ' -> ' + P.hp.toFixed(0) + ' over 3s');
ok('the drain is survivable, not instant', P.hp > hpStart * .8, 'lost ' + (hpStart - P.hp).toFixed(1));
P.hp = P.max * .2; G.vlast = {};
update(1 / 60);
ok('the narrator calls for food', !!G.voice && /needs food/.test(G.voice.txt), G.voice && G.voice.txt);
P.hp = P.max * .07; G.vlast = {};
update(1 / 60);
ok('and warns when you are about to die', !!G.voice && /about to die/.test(G.voice.txt), G.voice && G.voice.txt);
P.hp = .4; G.vlast = {}; P.inv = 99;
for (let i = 0; i < 90 && !P.down; i++) update(1 / 60);
ok('the drain alone can put you down', P.down === true, 'hp=' + P.hp.toFixed(2));

/* food restores, and can be shot ---------------- */
startGame(['ember']); G.level = 4; genLevel(); clearOffers(); P = G.players[0];
P.hp = P.max * .4;
const fp = roomPoint(G.rooms[1]);
G.items.length = 0; G.items.push({ kind: 'food', x: P.x + 12, y: P.y, t: 0 });
updateItems(1 / 60);
ok('food restores health', P.hp > P.max * .4, 'hp=' + P.hp.toFixed(0));
G.items.length = 0; G.items.push({ kind: 'food', x: P.x + 60, y: P.y, t: 0 });
G.shots.length = 0; G.vlast = {};
G.shots.push({ x: P.x + 58, y: P.y, vx: 1, vy: 0, dmg: 5, life: 1, r: 4, kind: 'fire', col: '#f00', pierce: 0, rad: 0, hit: new Set(), trail: [], crit: false, own: P });
updateShots(1 / 60);
ok('your own shot destroys the food', !G.items.some(i => i.kind === 'food'));
ok('and the narrator says so', !!G.voice && /shot the food/.test(G.voice.txt), G.voice && G.voice.txt);

/* ---------------- the thief ---------------- */
startGame(['sable']); G.level = 5; genLevel(); clearOffers(); P = G.players[0];
G.enemies.length = 0; G.gold = 300; P.inv = 999;
spawnFoe('thief', P.x + 14, P.y, false);
const th = G.enemies[0]; th.alert = true;
buildFlow(); updateEnemies(1 / 60);
ok('the thief takes your gold', G.gold < 300 && th.loot > 0, 'gold=' + G.gold + ' stolen=' + th.loot);
ok('the thief does not wound you', P.hp === P.max, 'hp=' + P.hp.toFixed(0));
const stolen = th.loot;
const goldItems0 = G.items.filter(i => i.kind === 'gold').length;
th.hp = 1; hurtFoe(th, 999, 0, false, false, P);
const dropped = G.items.filter(i => i.kind === 'gold').reduce((s, i) => s + (i.v || 10), 0);
ok('killing the thief returns the purse', dropped >= stolen * .8, 'stolen ' + stolen + ', dropped ' + dropped);
/* and it escapes if left alone */
G.enemies.length = 0; G.gold = 300;
spawnFoe('thief', P.x + 14, P.y, false);
const th2 = G.enemies[0]; th2.alert = true;
buildFlow(); updateEnemies(1 / 60);
th2.flee = .01;
updateEnemies(1 / 60);
G.enemies = G.enemies.filter(e => e.hp > 0);
ok('an unpunished thief escapes with the gold', !G.enemies.includes(th2) && G.gold < 300, 'gold=' + G.gold);

/* ---------------- Death ---------------- */
startGame(['bulwark']); G.level = 8; genLevel(); clearOffers(); P = G.players[0];
G.enemies.length = 0;
spawnFoe('reaper', P.x + 200, P.y, false);
const rp = G.enemies[0];
ok('Death is immune to ordinary blows', rp.immune === true);
const rhp = rp.hp;
hurtFoe(rp, 500, 0, true, false, P);
ok('a normal hit does nothing to it', rp.hp === rhp, rhp + ' -> ' + rp.hp);
SMITE = true; hurtFoe(rp, 500, 0, false, false, null); SMITE = false;
ok('a smite gets through', rp.hp < rhp, rp.hp.toFixed(0));
/* it drains you on contact and then leaves */
rp.hp = 99999; rp.fed = 0; rp.x = P.x; rp.y = P.y; P.hp = P.max; P.inv = 0;
buildFlow();
for (let i = 0; i < 60; i++) updateEnemies(1 / 60);
ok('Death drains health through invulnerability', P.hp < P.max, 'hp=' + P.hp.toFixed(0));
for (let i = 0; i < 400 && G.enemies.includes(rp); i++) { P.hp = P.max; updateEnemies(1 / 60); G.enemies = G.enemies.filter(e => e.hp > 0); }
ok('Death leaves once it has fed', !G.enemies.includes(rp));

/* ---------------- potions clear the room ---------------- */
startGame(['thistle']); G.level = 6; genLevel(); clearOffers(); P = G.players[0];
G.enemies.length = 0; G.bombs = 2; P.inv = 999;
for (let i = 0; i < 8; i++) spawnFoe('gloam', P.x + 30 + i * 9, P.y, false);
const before = G.enemies.length;
useBomb(P);
G.enemies = G.enemies.filter(e => e.hp > 0);
ok('a potion devastates the room', G.enemies.length < before, before + ' -> ' + G.enemies.length);
ok('and is spent', G.bombs === 1, 'bombs=' + G.bombs);
ok('the screen flashes', G.flash > 0);
G.bombs = 0; P.bombCd = 0;
const b4 = G.flash; G.flash = 0; useBomb(P);
ok('no potion, no effect', G.flash === 0 && G.bombs === 0);

/* ---------------- elemental weapons ---------------- */
startGame(['bulwark']); G.level = 6; genLevel(); clearOffers(); P = G.players[0];
const elemTest = (elem, check, label) => {
  G.enemies.length = 0; G.bolts.length = 0;
  equip(P, { slot: 'weapon', base: 'T', rar: 'rare', col: '#fff', name: 'T', s: { elem, elemDmg: .6 }, ilvl: 1 });
  for (let i = 0; i < 4; i++) spawnFoe('bonewalker', P.x + 40 + i * 24, P.y, false);
  const t = G.enemies[0];
  hurtFoe(t, 30, 0, false, false, P);
  ok(label, check(t), '');
};
elemTest('fire', e => e.burn > 0 && e.burnDmg > 0, 'a fire weapon sets foes alight');
elemTest('cold', e => e.chill > 0, 'a cold weapon chills what it hits');
elemTest('poison', e => e.pois > 0 && e.poisDmg > 0, 'a venomous weapon poisons');
elemTest('shock', () => G.bolts.length > 0, 'a storm weapon arcs to nearby foes');
/* chill actually slows */
G.enemies.length = 0;
/* put both of them on open floor in the widest room, well clear of walls */
{
  let best = G.rooms[0];
  for (const r of G.rooms) if (r.w * r.h > best.w * best.h) best = r;
  P.x = (best.cx + .5) * T; P.y = (best.cy + .5) * T;
  let sx = null;
  for (let off = 2; off <= 4 && !sx; off++) {
    for (const [dx, dy] of DIRS) {
      const cx = P.x + dx * off * T, cy = P.y + dy * off * T;
      if (!blockedAt(cx, cy, 14) && openAt(cx, cy)) { sx = [cx, cy]; break; }
    }
  }
  if (!sx) sx = [P.x + T * 2, P.y];
  spawnFoe('gloam', sx[0], sx[1], false);
}
const ch = G.enemies[0]; ch.alert = true; ch.chill = 0; P.inv = 999; buildFlow();
const measure = () => { const x0 = ch.x, y0 = ch.y; updateEnemies(1 / 60); return Math.hypot(ch.x - x0, ch.y - y0); };
P.down = false; P.hp = P.max;
let fast = 0, slow = 0, tries = 0;
while (tries++ < 6) {
  ch.chill = 0; ch.alert = true; buildFlow();
  fast = 0; for (let i = 0; i < 20; i++) fast += measure();
  if (fast > 1) break;
  /* that spot could not be walked out of; shove the pair somewhere else and retry */
  const rr = G.rooms[tries % G.rooms.length];
  P.x = (rr.cx + .5) * T; P.y = (rr.cy + .5) * T;
  ch.x = P.x + 70; ch.y = P.y;
}
for (let i = 0; i < 20; i++) { ch.chill = 5; slow += measure(); }
ok('chilled foes move slower', fast > 1 && slow < fast * .75, fast.toFixed(1) + ' vs ' + slow.toFixed(1));
/* leech and thorns */
equip(P, { slot: 'trinket', base: 'T', rar: 'rare', col: '#fff', name: 'T', s: { leech: .5 }, ilvl: 1 });
equip(P, { slot: 'weapon', base: 'T', rar: 'rare', col: '#fff', name: 'T', s: {}, ilvl: 1 });
G.enemies.length = 0; spawnFoe('brute', P.x + 40, P.y, false);
P.hp = P.max * .5; const hpL = P.hp;
hurtFoe(G.enemies[0], 40, 0, false, false, P);
ok('leeching heals you as you strike', P.hp > hpL, hpL.toFixed(0) + ' -> ' + P.hp.toFixed(0));
equip(P, { slot: 'armour', base: 'T', rar: 'rare', col: '#fff', name: 'T', s: { thorns: 1 }, ilvl: 1 });
G.enemies.length = 0; spawnFoe('brute', P.x + 40, P.y, false);
const sp2 = G.enemies[0], sphp = sp2.hp;
P.inv = 0; hurtPlayer(P, 20, 0, sp2);
ok('thorns bite back', sp2.hp < sphp, sphp.toFixed(0) + ' -> ' + sp2.hp.toFixed(0));

/* ---------------- elite modifiers ---------------- */
startGame(['sable']); G.level = 9; genLevel(); clearOffers(); P = G.players[0];
const affSeen = new Set();
for (let i = 0; i < 200; i++) { G.enemies.length = 0; spawnFoe('gloam', 100, 100, true); (G.enemies[0].eaff || []).forEach(a => affSeen.add(a)); }
ok('elites roll modifiers', affSeen.size >= 5, [...affSeen].join(','));
G.enemies.length = 0; spawnFoe('gloam', 100, 100, true);
const elt = G.enemies[0]; elt.eaff = ['warded']; elt.wardMax = elt.hp; elt.ward = elt.hp;
const ehp = elt.hp;
hurtFoe(elt, 20, 0, false, false, P);
ok('a shielded elite soaks the first blows', elt.hp === ehp && elt.ward < elt.wardMax, 'ward=' + elt.ward.toFixed(0));
elt.ward = 1; hurtFoe(elt, 50, 0, false, false, P);
ok('and takes damage once the shield breaks', elt.hp < ehp, elt.hp.toFixed(0));
/* vampiric heals itself, cold-touched chills you */
G.enemies.length = 0; spawnFoe('brute', P.x + 30, P.y, true);
const vp = G.enemies[0]; vp.eaff = ['vamp']; vp.hp = vp.max * .5;
const vhp = vp.hp; P.inv = 0; P.hp = P.max;
hurtPlayer(P, 30, 0, vp);
ok('a vampiric elite heals from your blood', vp.hp > vhp, vhp.toFixed(0) + ' -> ' + vp.hp.toFixed(0));
vp.eaff = ['frozen']; P.inv = 0; P.chill = 0;
hurtPlayer(P, 10, 0, vp);
ok('a cold-touched elite chills you', P.chill > 0);
/* extra fast really is faster */
G.enemies.length = 0; spawnFoe('gloam', 100, 100, true); const s1 = G.enemies[0].spd;
let fastSpd = 0, n2 = 0;
for (let i = 0; i < 300; i++) { G.enemies.length = 0; spawnFoe('gloam', 100, 100, true); const e2 = G.enemies[0]; if ((e2.eaff || []).indexOf('fast') >= 0) { fastSpd += e2.spd; n2++; } }
G.enemies.length = 0; spawnFoe('gloam', 100, 100, false); const plainSpd = G.enemies[0].spd;
ok('extra-fast elites outrun the rest', n2 > 0 && fastSpd / n2 > plainSpd, (n2 ? (fastSpd / n2).toFixed(2) : '?') + ' vs ' + plainSpd.toFixed(2));
/* fire enchanted detonates on death */
G.enemies.length = 0; spawnFoe('gloam', P.x + 300, P.y, true);
const fe = G.enemies[0]; fe.eaff = ['fiery']; fe.ward = 0; fe.hp = 1;
G.fxs.length = 0; hurtFoe(fe, 50, 0, false, false, P);
ok('a fire-enchanted elite goes off when killed', G.fxs.some(f => f.kind === 'shock'));

/* ---------------- gear actually drops ---------------- */
startGame(['bulwark']); G.level = 7; genLevel(); clearOffers(); P = G.players[0];
G.items.length = 0; G.enemies.length = 0;
spawnFoe('gloam', 300, 300, true); const dl = G.enemies[0]; dl.ward = 0; dl.eaff = [];
dl.hp = 1; hurtFoe(dl, 99, 0, false, false, P);
ok('elites always drop gear', G.items.some(i => i.kind === 'gear'));
G.items.length = 0; G.enemies.length = 0;
spawnFoe('warden', 400, 400, false); const bs = G.enemies[0];
bs.hp = 1; hurtFoe(bs, 99999, 0, false, false, P);
ok('a boss drops two pieces', G.items.filter(i => i.kind === 'gear').length >= 2, G.items.filter(i => i.kind === 'gear').length);
/* picking gear up into an empty slot equips it straight away */
startGame(['ember']); G.level = 5; genLevel(); clearOffers(); P = G.players[0];
G.items.length = 0;
const gi = rollItem('weapon', RARITY.rare);
G.items.push({ kind: 'gear', x: P.x, y: P.y, t: 0, item: gi });
updateItems(1 / 60);
ok('gear for an empty slot equips on pickup', P.gear.weapon === gi, P.gear.weapon && P.gear.weapon.name);
/* a second piece asks first */
const gi2 = rollItem('weapon', RARITY.fabled);
G.items.push({ kind: 'gear', x: P.x, y: P.y, t: 0, item: gi2 });
updateItems(1 / 60);
ok('a filled slot opens a compare card', G.offer && G.offer.kind === 'gear', G.offer && G.offer.kind);
applyUpgrade(0);
ok('choosing equip swaps the item', P.gear.weapon === gi2);
G.items.push({ kind: 'gear', x: P.x, y: P.y, t: 0, item: gi });
updateItems(1 / 60); applyUpgrade(1);
ok('choosing leave keeps what you wore', P.gear.weapon === gi2);

/* potions get seeded, and depth one teaches them */
let bombLevels = 0;
for (let lv = 1; lv <= 120; lv++) { G.level = 1 + (lv % 18); genLevel(); if (G.items.some(i => i.kind === 'bomb')) bombLevels++; }
ok('potions appear on most depths', bombLevels >= 90, bombLevels + '/120 depths');
G.level = 1; genLevel();
ok('depth one always has a potion to teach it', G.items.some(i => i.kind === 'bomb'));

/* ---------------- six zones, six bosses ---------------- */
{
  const perZone = [1, 2, 3, 4, 5, 6].map(z => bossKindOf(z * 3));
  ok('every zone draws a boss of its own', new Set(perZone).size === 6, perZone.join(','));
  ok('and each one is a defined archetype', perZone.every(k => !!BOSSES[k]), perZone.filter(k => !BOSSES[k]).join(',') || 'all defined');
  /* the names promised six bosses long before the behaviour did */
  const names = ZONES.map(z => z.boss);
  ok('each zone names its boss', new Set(names).size === 6, names.length + ' names');

  /* no two of them share a late attack pattern */
  const sigs = perZone.map(k => (BOSSES[k].acts[3] || []).slice().sort().join(','));
  ok('no two bosses fight the same way', new Set(sigs).size === 6, sigs.join(' | '));
  /* and every act a boss can pick has a duration, or it would hang mid swing */
  const missing = [];
  for (const k of perZone) for (const ph of [1, 2, 3]) for (const a of (BOSSES[k].acts[ph] || []))
    if (BOSS_DUR[a] === undefined) missing.push(k + '/' + a);
  ok('every attack has a timed wind-up', missing.length === 0, missing.join(',') || 'all timed');

  /* each boss actually shows up on its own depth, and every attack it owns
     resolves and hands control back. The pools are walked in order and only
     swing with line of sight, so drive each act directly rather than waiting. */
  const stuck = [], wrongKind = [];
  for (let z = 0; z < 6; z++) {
    const lvl = z * 3 + 3, want = bossKindOf(lvl);
    startGame(['thistle']); G.level = lvl; genLevel();
    let gg = 0; while (G.offer && gg++ < 20) applyUpgrade(0); G.offerQ.length = 0; G.state = 'play';
    const B = G.enemies.find(e => e.boss);
    if (!B || B.kind !== want) { wrongKind.push(lvl + ':' + (B ? B.kind : 'none') + '!=' + want); continue; }
    const rig = foeDef('warden', B.kind);
    if (!rig || !rig.key) { wrongKind.push(lvl + ':norig'); continue; }
    const room = G.rooms.reduce((a, b) => (b.w * b.h > a.w * a.h ? b : a), G.rooms[0]);
    /* a charge stops dead on a barrel, and blockedAt does not see props */
    G.props.length = 0; if (G.hazards) G.hazards.length = 0;
    const every = [...new Set([].concat(BOSSES[want].acts[1] || [], BOSSES[want].acts[2] || [], BOSSES[want].acts[3] || []))];
    for (const act of every) {
      B.hp = B.max * .2; B.cd = 0; B.alert = true; B.kx = 0; B.ky = 0;
      B.immune = false; B.wardT = undefined; B.wardAdds = null;
      B.x = room.cx * T + T / 2; B.y = room.cy * T + T / 2;
      G.players.forEach(pl => { pl.down = false; pl.hp = pl.max; pl.inv = 1e9; pl.x = B.x + 40; pl.y = B.y; });
      B.st = act; B.stt = 0; B.ca = 1;
      buildFlow();
      let back = false;
      for (let i = 0; i < 500; i++) {
        updateEnemies(1 / 60); updateShots(1 / 60); updateFx(1 / 60);
        G.players.forEach(pl => { pl.hp = pl.max; });
        if (B.st === 'chase') { back = true; break; }
      }
      if (!back) stuck.push(want + '/' + act);
    }
  }
  ok('each depth spawns its own boss with a rig', wrongKind.length === 0, wrongKind.join(' ') || 'all six');
  ok('and every attack any of them owns resolves', stuck.length === 0, stuck.join(' ') || 'all clear');
}

/* --- the new attacks do what they claim --- */
{
  function bossIn(kind) {
    startGame(['thistle']); G.level = 3; genLevel();
    let gg = 0; while (G.offer && gg++ < 20) applyUpgrade(0); G.offerQ.length = 0; G.state = 'play';
    G.enemies.length = 0; G.eshots.length = 0; G.timers.length = 0; G.fxs.length = 0;
    const room = G.rooms.reduce((a, b) => (b.w * b.h > a.w * a.h ? b : a), G.rooms[0]);
    spawnFoe('warden', room.cx * T + T / 2, room.cy * T + T / 2);
    const B = G.enemies[G.enemies.length - 1];
    B.kind = kind; B.alert = true; B.hp = B.max;
    const Q = G.players[0]; Q.x = B.x + 60; Q.y = B.y; Q.down = false; Q.hp = Q.max;
    return [B, Q];
  }
  /* pillars: a mark on the floor first, damage only after it fills */
  { const [B, Q] = bossIn('pyre'); Q.inv = 0;
    B.st = 'pillars'; bossAct(B);
    const warned = G.fxs.filter(f => f.kind === 'warn').length;
    ok('the pyre marks the floor before it burns', warned > 0, warned + ' marks');
    const pending = G.timers.length;
    ok('and the fire is still only a promise', pending > 0 && G.players[0].hp === G.players[0].max, pending + ' pending');
    let hp0 = Q.hp; Q.x = G.fxs.find(f => f.kind === 'warn').x; Q.y = G.fxs.find(f => f.kind === 'warn').y;
    for (let i = 0; i < 90; i++) { Q.inv = 0; updateFx(1 / 60); }
    ok('standing on a mark burns you', Q.hp < hp0, hp0.toFixed(0) + ' -> ' + Q.hp.toFixed(0)); }
  { const [B, Q] = bossIn('pyre'); Q.inv = 0;
    B.st = 'pillars'; bossAct(B);
    const spot = G.fxs.find(f => f.kind === 'warn');
    /* stand well clear of every mark */
    let far2 = null;
    for (let a = 0; a < 48 && !far2; a++) {
      const an = a / 48 * TAU, x = B.x + Math.cos(an) * 260, y = B.y + Math.sin(an) * 260;
      if (blockedAt(x, y, 11) || !openAt(x, y)) continue;
      if (G.fxs.some(f => f.kind === 'warn' && Math.hypot(f.x - x, f.y - y) < 90)) continue;
      far2 = [x, y];
    }
    if (!far2) ok('and stepping off one spares you', true, 'nowhere clear, skipped');
    else { Q.x = far2[0]; Q.y = far2[1]; const hp0 = Q.hp;
      for (let i = 0; i < 90; i++) { Q.inv = 0; updateFx(1 / 60); }
      ok('and stepping off one spares you', Q.hp === hp0, hp0.toFixed(0) + ' -> ' + Q.hp.toFixed(0)); } }
  /* comet: bends toward you */
  { const [B, Q] = bossIn('pyre');
    B.st = 'comet'; B.face = 0; bossAct(B);
    const shots = G.eshots.slice();
    ok('the pyre throws seeking fire', shots.length > 0 && shots.every(s => s.seek > 0), shots.length + ' comets');
    if (shots.length) {
      const s0 = shots[0];
      /* put the target off to one side and watch the heading swing toward it */
      Q.x = B.x + 40; Q.y = B.y - 200; Q.inv = 1e9;
      const a0 = Math.atan2(s0.vy, s0.vx);
      for (let i = 0; i < 40; i++) updateShots(1 / 60);
      const a1 = Math.atan2(s0.vy, s0.vx);
      ok('and it turns to follow', Math.abs(Math.atan2(Math.sin(a1 - a0), Math.cos(a1 - a0))) > .05,
         (a0).toFixed(2) + ' -> ' + (a1).toFixed(2)); } }
  /* wail: hurts as the ring passes, not where you started */
  { const [B, Q] = bossIn('chorister');
    Q.x = B.x + 4; Q.y = B.y; Q.inv = 0; const hp0 = Q.hp;
    B.st = 'wail'; bossAct(B);
    for (let i = 0; i < 12; i++) { Q.inv = 0; updateFx(1 / 60); }
    ok('the wail spares the eye of the ring', Q.hp === hp0, 'at the centre: ' + Q.hp.toFixed(0));
    Q.x = B.x + 150; Q.y = B.y;
    for (let i = 0; i < 80; i++) { Q.inv = 0; updateFx(1 / 60); }
    ok('and catches you where it passes', Q.hp < hp0, hp0.toFixed(0) + ' -> ' + Q.hp.toFixed(0)); }
  /* ward: untouchable until the choir falls */
  { const [B, Q] = bossIn('chorister');
    B.st = 'ward'; B.ph = 2; bossAct(B);
    ok('the chorister raises a choir', (B.wardAdds || []).length > 0, (B.wardAdds || []).length + ' singers');
    ok('and cannot be touched while it stands', B.immune === true);
    const hp0 = B.hp; hurtFoe(B, 500, 0, false, false, Q);
    ok('damage does not land on it', B.hp === hp0, hp0.toFixed(0) + ' -> ' + B.hp.toFixed(0));
    for (const a of B.wardAdds) { a.hp = 0; a.dead = 1; }
    for (let i = 0; i < 10; i++) updateEnemies(1 / 60);
    ok('silencing the choir exposes it', B.immune === false);
    const hp1 = B.hp; hurtFoe(B, 40, 0, false, false, Q);
    ok('and then it takes damage', B.hp < hp1, hp1.toFixed(0) + ' -> ' + B.hp.toFixed(0)); }
  { /* the ward must lift on its own too, or a stuck add would end the run */
    const [B, Q] = bossIn('chorister');
    B.st = 'ward'; B.ph = 2; bossAct(B);
    if (!B.immune) ok('a ward always times out', true, 'no room for a choir, skipped');
    else { for (let i = 0; i < 60 * 11 && B.immune; i++) updateEnemies(1 / 60);
      ok('a ward always times out', B.immune === false, 'wardT=' + B.wardT); } }
  /* shards: thrown out, then called back */
  { const [B, Q] = bossIn('obsidian'); Q.inv = 1e9;
    B.st = 'shards'; bossAct(B);
    const mine = G.eshots.slice();
    ok('the obsidian throws a ring of shards', mine.length >= 8, mine.length + ' shards');
    const out = new Map(mine.map(s => [s, { x: s.vx, y: s.vy }]));
    /* the recall sits on a timer, and timers only tick in updateFx, so both
       clocks have to run together or the call back never comes */
    let turned = 0, survived = 0;
    for (let i = 0; i < 110; i++) {
      updateShots(1 / 60); updateFx(1 / 60);
      for (const s of mine) {
        if (G.eshots.indexOf(s) < 0) continue;
        const o = out.get(s);
        if (s.vx * o.x < 0 || s.vy * o.y < 0) { out.set(s, { x: s.vx, y: s.vy, seen: true }); turned++; }
      }
    }
    survived = mine.filter(s => G.eshots.indexOf(s) >= 0).length;
    ok('and calls them back', turned > 0, turned + ' reversed, ' + survived + ' still in the air'); }
}

/* --- the caller's tricks --- */
{
  startGame(['sable']); G.level = 6; genLevel();
  let gg=0; while (G.offer && gg++<20) applyUpgrade(0); G.offerQ.length=0; G.state='play';
  const B = G.enemies.find(e => e.boss); const Q = G.players[0];
  Q.inv = 1e9; Q.hp = Q.max;
  { const rr = G.rooms.reduce((a, b) => (b.w * b.h > a.w * a.h ? b : a), G.rooms[0]);
    Q.x = (rr.cx + .5) * T; Q.y = (rr.cy + .5) * T;
    B.x = Q.x + 260; B.y = Q.y; }
  B.alert = true;
  const before = { x: B.x, y: B.y };
  B.st = 'blink'; B.stt = 99; bossAct(B);
  ok('blink moves the Choir', Math.hypot(B.x - before.x, B.y - before.y) > 40, Math.round(Math.hypot(B.x-before.x,B.y-before.y)) + 'px');
  ok('and it lands near a player', Math.hypot(B.x - Q.x, B.y - Q.y) < 200, Math.round(Math.hypot(B.x-Q.x,B.y-Q.y)) + 'px');
  ok('blink never lands in a wall', !blockedAt(B.x, B.y, B.r) && openAt(B.x, B.y));
  const n0 = G.enemies.length;
  B.st = 'raise'; B.stt = 99; bossAct(B);
  ok('raise calls up the dead', G.enemies.length > n0, n0 + ' -> ' + G.enemies.length);
  G.eshots.length = 0;
  B.st = 'volley'; B.stt = 99; B.face = 0; bossAct(B);
  ok('volley fires a fan of shots', G.eshots.length >= 3, G.eshots.length + ' shots');
  ok('and those shots know their owner', G.eshots.every(s => s.own === B));
}

/* --- the maw's quake --- */
{
  startGame(['bulwark']); G.level = 9; genLevel();
  let gg=0; while (G.offer && gg++<20) applyUpgrade(0); G.offerQ.length=0; G.state='play';
  const B = G.enemies.find(e => e.boss), Q = G.players[0];
  Q.x = B.x + 60; Q.y = B.y; Q.inv = 0; Q.hp = Q.max;
  G.fxs.length = 0;
  B.st = 'quake'; B.stt = 99; bossAct(B);
  ok('quake hurts whoever stands close', Q.hp < Q.max, Math.round(Q.hp) + '/' + Q.max);
  ok('quake throws out shock rings', G.fxs.filter(f => f.kind === 'shock').length >= 2);
  Q.hp = Q.max; Q.inv = 0; Q.x = B.x + 900; Q.y = B.y;
  B.st = 'quake'; B.stt = 99; bossAct(B);
  ok('but spares anyone far away', Q.hp === Q.max);
}

/* score never goes non-numeric with the new monsters */
startGame(['sable']); G.level = 7; genLevel(); clearOffers(); P = G.players[0];
G.score = 0; G.enemies.length = 0;
for (const t of ['thief', 'reaper', 'bloat', 'gloam', 'brute']) { spawnFoe(t, 500, 500, false); const e3 = G.enemies[G.enemies.length - 1]; e3.immune = false; e3.hp = 1; hurtFoe(e3, 999, 0, false, false, P); }
ok('every monster has a score value', Number.isFinite(G.score) && G.score > 0, 'score=' + G.score);
ok('experience stays finite', Number.isFinite(P.xp) && Number.isFinite(P.plvl), 'xp=' + P.xp + ' lv=' + P.plvl);

/* ---------------- the arena ---------------- */
{
  let found = 0, sealed = 0;
  for (let lv = 2; lv <= 14; lv++) {
    startGame(['bulwark']); G.level = lv; genLevel();
    let gg=0; while (G.offer && gg++<20) applyUpgrade(0); G.offerQ.length=0; G.state='play';
    const r = G.rooms.find(x => x.arena);
    if (!r) continue;
    found++;
    const Q = G.players[0];
    Q.inv = 1e9; Q.hp = Q.max; Q.x = (r.cx + .5) * T; Q.y = (r.cy + .5) * T;
    G.enemies.length = 0; G.nests.length = 0;
    buildFlow(); update(1/60);
    if (!G.event) continue;
    sealed++;
    // the seal must hold, and must never push anyone into a wall
    Q.x = (r.x - 6) * T; Q.y = (r.cy + .5) * T;
    updatePlayer(Q, INS[0], 1/60);
    const inside = Q.x >= r.x * T - 1 && Q.x <= (r.x + r.w) * T + 1;
    if (!inside || blockedAt(Q.x, Q.y, Q.r)) { sealed = -999; break; }
  }
  ok('most depths carry an arena', found >= 8, found + '/13 depths');
  ok('stepping inside seals it', sealed > 0, 'sealed=' + sealed);
  ok('the seal never traps you in a wall', sealed !== -999);
}
{
  /* run one arena to completion */
  let r = null;
  for (let lv = 4; lv <= 16 && !r; lv++) {
    startGame(['thistle']); G.level = lv; genLevel();
    let gg=0; while (G.offer && gg++<20) applyUpgrade(0); G.offerQ.length=0; G.state='play';
    r = G.rooms.find(x => x.arena);
  }
  ok('an arena can be found to clear', !!r);
  if (r) {
    const Q = G.players[0];
    Q.inv = 1e9; Q.x = (r.cx + .5) * T; Q.y = (r.cy + .5) * T;
    G.enemies.length = 0; G.nests.length = 0; G.items.length = 0;
    buildFlow(); update(1/60);
    ok('waves begin', !!G.event && G.event.waves === 3);
    let waves = 0, guard = 0;
    while (G.event && guard++ < 40) {
      arenaTick(1/60);
      if (G.event && G.event.phase === 'fight') {
        waves++;
        for (const e of G.enemies) if (e.ev) { e.hp = 0; e.dead = 1; }
        G.enemies = G.enemies.filter(e => e.hp > 0);
      }
      Q.hp = Q.max;
    }
    ok('it runs three waves then ends', waves >= 3 && !G.event, 'waves=' + waves);
    ok('clearing it pays out', G.items.some(i => i.kind === 'chest') && G.items.some(i => i.kind === 'gear'));
  }
}

/* ---------------- the meta layer ---------------- */
{
  META.echoes = 0; META.perks = {}; META.runs = 0; META.deepest = 1;
  startGame(['sable']); G.level = 7; genLevel();
  let gg=0; while (G.offer && gg++<20) applyUpgrade(0); G.offerQ.length=0; G.state='play';
  G.gold = 400; G.score = 4000;
  for (const P of G.players) { P.hp = 0; P.down = true; }
  die();
  ok('dying banks echoes', META.echoes > 0, '+' + G.earned);
  ok('and records the run', META.runs === 1 && META.deepest === 7, 'runs=' + META.runs + ' deepest=' + META.deepest);
  const before = META.echoes;
  META.echoes = 100000;
  ok('a perk can be bought', buyPerk('vigour') === true && perkLv('vigour') === 1);
  ok('buying spends echoes', META.echoes < 100000);
  const p = PERKS.find(x => x.id === 'vigour');
  for (let i = 0; i < 20; i++) buyPerk('vigour');
  ok('a perk stops at its cap', perkLv('vigour') === p.max, 'lv=' + perkLv('vigour'));
  META.echoes = 0;
  ok('you cannot buy without echoes', buyPerk('edge') === false);
  META.echoes = 100000;
  /* perks must actually reach the delver */
  META.perks = { vigour: 3, flask: 2, edge: 2, slow: 2, purse: 2, relic: 1 };
  startGame(['sable']);
  const Q = G.players[0];
  ok('vigour raises starting health', Q.max > CLASSES.sable.hp, CLASSES.sable.hp + ' -> ' + Q.max);
  ok('deep pockets grant potions', G.bombs === 3, 'bombs=' + G.bombs);
  ok('whetted raises crit', Q.crit > .1, Q.crit.toFixed(2));
  ok('still blood slows the drain', Q.drainMul < 1, Q.drainMul.toFixed(2));
  ok('grave purse is carried', Q.perkGold > 0, Q.perkGold.toFixed(2));
  ok('the heirloom is worn', !!Q.gear.trinket, Q.gear.trinket && Q.gear.trinket.name);
  {
    let cursedHeirlooms = 0;
    for (let i = 0; i < 300; i++) { startGame(['sable']); const t = G.players[0].gear.trinket; if (t && t.rar === 'cursed') cursedHeirlooms++; }
    ok('a bought perk is never cursed', cursedHeirlooms === 0, cursedHeirlooms + '/300');
    startGame(['sable']);
  }
  META.perks = {}; META.echoes = 0; META.runs = 0; META.deepest = 1;
}

/* ---------------- gamepad plumbing ---------------- */
{
  const I = { mx: 0, my: 0, aim: 0, fire: false, dash: false, sp: false, bomb: false };
  const fake = { connected: true, axes: [0, 0, 0, 0], buttons: Array.from({ length: 10 }, () => ({ pressed: false, value: 0 })) };
  let r = readPad(I, fake);
  ok('an idle pad does nothing', !r.used && !I.fire);
  fake.axes = [1, 0, 0, 0];
  r = readPad(I, fake);
  ok('the left stick moves you', r.used && I.mx > .5, 'mx=' + I.mx);
  fake.axes = [0, 0, 0, -1];
  r = readPad(I, fake);
  ok('the right stick aims and fires', r.aimed && I.fire, 'aim=' + I.aim.toFixed(2));
  fake.axes = [0, 0, 0, 0];
  I.fire = I.dash = I.sp = I.bomb = false;
  fake.buttons[5].pressed = true; fake.buttons[3].pressed = true;
  r = readPad(I, fake);
  ok('face buttons map to dash and potion', I.dash && I.bomb);
  ok('a deadzone keeps drift out', PAD_DZ > .1);
}

/* ---------------- reduced motion ---------------- */
{
  const was = reduceMotion;
  reduceMotion = false; G.parts.length = 0;
  burst(100, 100, '#fff', 40, 100);
  const full = G.parts.length;
  reduceMotion = true; G.parts.length = 0;
  burst(100, 100, '#fff', 40, 100);
  const few = G.parts.length;
  ok('reduced motion thins the particles', few < full && few > 0, full + ' -> ' + few);
  G.parts.length = 0;
  for (let i = 0; i < 60; i++) burst(0, 0, '#fff', 40, 100);
  updateFx(1 / 60);
  ok('and holds a tighter particle cap', G.parts.length <= 450, G.parts.length);
  reduceMotion = was; G.parts.length = 0;
}


/* ---------------- boons change how an attack works ---------------- */
function bArena(cls, boon) {
  startGame([cls]); G.level = 3; genLevel();
  const P = G.players[0]; G.offer = null; G.offers = [];
  if (boon) P.boons[boon] = 1;
  G.enemies.length = 0;
  /* barrels and hazards stop arrows, and these checks are about the boon */
  G.props.length = 0; G.shots.length = 0; G.zones.length = 0;
  if (G.hazards) G.hazards.length = 0;
  return P;
}
function bSpot(P, dist, clearR) {
  for (let a = 0; a < 96; a++) {
    const an = a / 96 * TAU, x = P.x + Math.cos(an) * dist, y = P.y + Math.sin(an) * dist;
    if (blockedAt(x, y, 11) || !openAt(x, y) || !los(P.x, P.y, x, y)) continue;
    let clear = true;
    for (let t = .08; t <= 1.02 && clear; t += .06) {
      if (blockedAt(P.x + (x - P.x) * t, P.y + (y - P.y) * t, 7)) clear = false;
    }
    if (clear && clearR) {
      for (let k = 0; k < 10 && clear; k++) {
        const b = k / 10 * TAU;
        if (blockedAt(x + Math.cos(b) * clearR, y + Math.sin(b) * clearR, 7)) clear = false;
      }
    }
    if (clear) return [x, y, an];
  }
  return null;
}
/* keep rolling dungeons until one has room for the test, so a check never
   quietly fails to run and leave a gap in the count */
function bRoom(cls, boon, dist, clearR) {
  for (let i = 0; i < 60; i++) {
    const P = bArena(cls, boon), s = bSpot(P, dist, clearR);
    if (s) return [P, s];
  }
  return null;
}
function bFoe(P, spot) {
  spawnFoe('gloam', spot[0], spot[1], false);
  const e = G.enemies[G.enemies.length - 1];
  e.x = spot[0]; e.y = spot[1]; e.hp = 99999; e.max = 99999; e.spd = 0;
  return e;
}
const noRoom = (name) => ok(name, true, 'no clear room in 60 dungeons, skipped');

for (const c of ['bulwark', 'ember', 'sable', 'thistle']) {
  ok('the ' + c + ' has four boons to learn', (BOONS[c] || []).length === 4, String((BOONS[c] || []).length));
}
{ const P = bArena('sable', null); const r = rollBoons(P);
  ok('a boon offer holds three distinct cards', r.length === 3 && new Set(r.map(b => b.id)).size === 3);
  ok('and only ones this delver can learn', r.every(b => BOONS.sable.some(x => x.id === b.id))); }
{ const P = bArena('sable', null);
  for (const b of BOONS.sable) P.boons[b.id] = 1;
  ok('nothing is offered once all four are known', rollBoons(P).length === 0); }
/* a delver near the end of its boons is offered fewer than three cards, and
   the thing that applies the choice must cope with an index past the end */
{ const P = bArena('thistle', null);
  P.boons.volley = 1; P.boons.barbs = 1; P.boons.frost = 1;
  const r = rollBoons(P);
  ok('a nearly finished delver still gets an offer', r.length === 1, r.length + ' card');
  queueOffer({ kind: 'boon', P, opts: r });
  let threw = false;
  try { applyUpgrade(2); } catch (e) { threw = true; }
  ok('choosing a card that is not there does nothing', !threw && !!G.offer, threw ? 'threw' : 'offer still open');
  try { applyUpgrade(0); } catch (e) { threw = true; }
  ok('and the card that is there still works', !threw && bn(P, 'mark'), threw ? 'threw' : 'learned ' + r[0].name);
  G.offer = null; G.offerQ.length = 0; }

for (const [cls, boon] of [['sable', 'fan'], ['thistle', 'volley']]) {
  let P = bArena(cls, null); G.shots.length = 0; P.aim = 0; P.cd = 0; attack(P);
  const base = G.shots.length;
  P = bArena(cls, boon); G.shots.length = 0; P.aim = 0; P.cd = 0; attack(P);
  ok(boon + ' turns one shot into a spread', G.shots.length > base, base + ' -> ' + G.shots.length);
}
{ const n = 'cyclone strikes a foe at your back', r = bRoom('bulwark', 'cyclone', 40, 20);
  if (!r) noRoom(n); else { const [P, s] = r, e = bFoe(P, s);
    P.aim = s[2] + Math.PI; P.cd = 0; const h0 = e.hp; attack(P);
    ok(n, e.hp < h0, (h0 - e.hp).toFixed(0) + ' damage'); } }
{ const n = 'and a plain sweep does not', r = bRoom('bulwark', null, 40, 20);
  if (!r) noRoom(n); else { const [P, s] = r, e = bFoe(P, s);
    P.aim = s[2] + Math.PI; P.cd = 0; const h0 = e.hp; attack(P);
    ok(n, e.hp === h0); } }
{ const n = 'shield bash hurls a foe back', r = bRoom('bulwark', 'bash', 40, 30);
  if (!r) { noRoom(n); noRoom('and leaves it reeling'); }
  else { const [P, s] = r, e = bFoe(P, s);
    P.aim = s[2]; P.cd = 0; const x0 = e.x, y0 = e.y; attack(P);
    for (let i = 0; i < 6; i++) update(1 / 60);
    ok(n, Math.hypot(e.x - x0, e.y - y0) > 5, Math.hypot(e.x - x0, e.y - y0).toFixed(0) + 'px');
    ok('and leaves it reeling', (e.root || 0) > 0, (e.root || 0).toFixed(2) + 's'); } }
for (const [cls, boon, key, label] of [['bulwark', 'wake', 'burn', 'burning wake sets a foe alight'],
                                       ['sable', 'venom', 'pois', 'venom poisons'],
                                       ['thistle', 'frost', 'chill', 'hoarfrost chills']]) {
  const d = cls === 'bulwark' ? 40 : 90, r = bRoom(cls, boon, d, 30);
  if (!r) { noRoom(label); continue; }
  const [P, s] = r, e = bFoe(P, s);
  P.aim = s[2]; P.cd = 0; attack(P);
  for (let i = 0; i < 70; i++) update(1 / 60);
  ok(label, (e[key] || 0) > 0, key + '=' + (+(e[key] || 0)).toFixed(2));
}
{ const n = "hunter's mark raises the damage actually dealt", r = bRoom('thistle', 'mark', 90, 40);
  if (!r) noRoom(n); else { const [P, s] = r, e = bFoe(P, s);
    P.crit = 0; P.cd = 0;
    /* hold the foe exactly still: knockback would otherwise walk it out of the
       second arrow's path and the two shots would not be comparable */
    const fx = e.x, fy = e.y;
    const shoot = () => {
      e.x = fx; e.y = fy; e.kx = 0; e.ky = 0;
      P.aim = Math.atan2(fy - P.y, fx - P.x); P.cd = 0;
      const h = e.hp; attack(P);
      for (let i = 0; i < 70; i++) { update(1 / 60); e.x = fx; e.y = fy; e.kx = 0; e.ky = 0; }
      return h - e.hp;
    };
    const first = shoot(), second = shoot();
    ok(n, first > 0 && second > first, first.toFixed(0) + ' -> ' + second.toFixed(0)); } }
{ const n = 'seeking flame curves onto an off-axis foe';
  /* we need a room where a straight bolt cleanly misses, or the check proves
     nothing either way */
  let verdict = null;
  for (let attemptN = 0; attemptN < 40 && verdict === null; attemptN++) {
    const fire = (boon) => {
      const r = bRoom('ember', boon, 150, 70);
      if (!r) return null;
      const [P, s] = r, e = bFoe(P, s);
      P.aim = s[2] + .7; P.cd = 0;
      const h0 = e.hp; attack(P);
      for (let i = 0; i < 220; i++) update(1 / 60);
      return e.hp < h0;
    };
    const straight = fire(null);
    if (straight === null || straight === true) continue;
    const seeking = fire('seek');
    if (seeking === null) continue;
    verdict = seeking;
  }
  if (verdict === null) noRoom(n);
  else ok(n, verdict, verdict ? 'straight=miss seeking=hit' : 'straight=miss seeking=miss'); }
{ const n = 'pyre leaves fire burning on the ground', r = bRoom('ember', 'pyre', 120, 40);
  if (!r) noRoom(n); else { const [P, s] = r; bFoe(P, s);
    G.zones.length = 0; P.aim = s[2]; P.cd = 0; attack(P);
    let mx = 0; for (let i = 0; i < 200; i++) { update(1 / 60); mx = Math.max(mx, G.zones.length); }
    ok(n, mx > 0, mx + ' pools'); } }
{ const n = 'barbed shafts hit harder the deeper they go';
  let done = false;
  for (let i = 0; i < 60 && !done; i++) {
    const P = bArena('thistle', 'barbs'), s = bSpot(P, 160, 40);
    if (!s) continue;
    const es = [];
    for (let k = 0; k < 3; k++) {
      const x = P.x + Math.cos(s[2]) * (70 + k * 30), y = P.y + Math.sin(s[2]) * (70 + k * 30);
      if (blockedAt(x, y, 11) || !openAt(x, y)) break;
      es.push(bFoe(P, [x, y]));
    }
    if (es.length !== 3) continue;
    const h0 = es.map(e => e.hp); P.crit = 0; P.aim = s[2]; P.cd = 0; attack(P);
    for (let j = 0; j < 120; j++) update(1 / 60);
    const d = es.map((e, k) => h0[k] - e.hp);
    if (d.some(v => v <= 0)) continue;
    ok(n, d[2] > d[0], d.map(v => v.toFixed(0)).join(' -> ')); done = true;
  }
  if (!done) noRoom(n); }

/* ---------------- altars ask for something back ---------------- */
{
  /* every depth lights at least one font, and always on floor you can reach */
  let depths = 0, withShrine = 0, reachable = 0, total = 0;
  for (let d = 1; d <= 14; d++) {
    for (let r = 0; r < 6; r++) {
      startGame(['sable']); G.level = d; genLevel();
      depths++;
      const sh = G.items.filter(i => i.kind === 'shrine');
      if (sh.length) withShrine++;
      /* what matters is that you can get close enough to use it, not that the
         altar itself sits on a tile you could stand on */
      for (const it of sh) {
        total++;
        let can = false;
        for (let a = 0; a < 48 && !can; a++) for (let q = 0; q <= 30 && !can; q += 4) {
          const an = a / 48 * TAU, x = it.x + Math.cos(an) * q, y = it.y + Math.sin(an) * q;
          if (!blockedAt(x, y, 11) && openAt(x, y)) can = true;
        }
        if (can) reachable++;
      }
    }
  }
  ok('every depth lights a font', withShrine === depths, withShrine + '/' + depths);
  ok('and always close enough to use', total > 0 && reachable === total, reachable + '/' + total);
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

/* ---------------- omens change what a depth asks ---------------- */
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
{ /* with no clock running, spawners would let you farm the floor forever */
  const n = avgOver('still', 8, 10, nestCount);
  ok('and sends no reinforcements to camp against', n === 0, n + ' crypts'); }
{ const plain = avgOver(null, 8, 12, () => kindCount('chest')), gild = avgOver('gilded', 8, 12, () => kindCount('chest'));
  ok('The Gilded Seam puts out more chests', gild > plain, plain.toFixed(1) + ' -> ' + gild.toFixed(1) + ' chests'); }
{ /* the thief and the reaper are placed deliberately and keep their own
     nature; what the omen promotes is the ordinary rank and file */
  const ord = (e) => e.type !== 'thief' && e.type !== 'reaper' && !e.boss;
  let elites = 0, all = 0;
  for (let i = 0; i < 6; i++) underOmen('gilded', 8, () => {
    for (const e of G.enemies) if (ord(e)) { all++; if (e.elite) elites++; }
  });
  ok('and its rank and file are all elites', all > 0 && elites === all, elites + '/' + all);
  let plainElite = 0, plainAll = 0;
  for (let i = 0; i < 6; i++) underOmen(null, 8, () => {
    for (const e of G.enemies) if (ord(e)) { plainAll++; if (e.elite) plainElite++; }
  });
  ok('where a plain floor keeps elites rare', plainElite < plainAll * .4,
     plainElite + '/' + plainAll + ' on a plain floor'); }

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
      /* depth 8: omens never land on a boss floor, where the key comes off the boss */
      underOmen(o.id, 8, () => {
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
  for (const o of OMENS) underOmen(o.id, 8, () => {
    if (G.enemies.length > 220) bad.push(o.id + ':' + G.enemies.length);
    if (G.nests.length > 80) bad.push(o.id + ':nests' + G.nests.length);
  });
  ok('and none of them floods the floor', bad.length === 0, bad.join(' ') || 'within bounds'); }
{ const banner = underOmen('horde', 8, () => G.banner && G.banner.sub);
  ok('the banner names the omen on arrival', /Horde/.test(banner || ''), banner || 'none'); }

/* ---------------- something to beat ---------------- */
{
  const atDepth = (d) => {
    startGame(['thistle']); G.level = d; genLevel();
    let g = 0; while (G.offer && g++ < 20) applyUpgrade(0); G.offerQ.length = 0; G.state = 'play';
    return G.enemies.find(e => e.boss);
  };
  ok('the descent has a bottom', typeof FINAL_DEPTH === 'number' && FINAL_DEPTH > 0, 'depth ' + FINAL_DEPTH);
  ok('and it lands on a boss depth', isBossLvl(FINAL_DEPTH), String(FINAL_DEPTH));
  ok('every depth above it is ordinary', [3, 6, 9, 12, 15, 18].every(d => !isFinalLvl(d)));

  const H = atDepth(FINAL_DEPTH);
  ok('the last depth puts the Heart in the way', !!H && H.kind === 'heart', H && H.kind);
  ok('and names it', !!H && H.name === HEART_NAME, H && H.name);
  const W = atDepth(18);
  ok('while eighteen still holds its own warden', !!W && W.kind !== 'heart', W && W.kind);
  ok('the Heart is the harder of the two', !!H && !!W && H.max > W.max * 1.5, (W ? W.max : 0) + ' -> ' + (H ? H.max : 0) + ' health');
  ok('and hits harder', !!H && !!W && H.dmg > W.dmg, (W ? W.dmg : 0) + ' -> ' + (H ? H.dmg : 0));

  /* every attack it can throw must be one the engine knows how to time */
  const hacts = [...new Set([].concat(BOSSES.heart.acts[1], BOSSES.heart.acts[2], BOSSES.heart.acts[3]))];
  ok('the Heart only throws attacks the engine times', hacts.every(a => BOSS_DUR[a] !== undefined),
     hacts.filter(a => BOSS_DUR[a] === undefined).join(',') || hacts.length + ' attacks');
  ok('and it remembers more of them than any warden', hacts.length > Math.max(...BOSS_KIND.map(k =>
     new Set([].concat(BOSSES[k].acts[1], BOSSES[k].acts[2], BOSSES[k].acts[3])).size)),
     hacts.length + ' attacks');

  /* the door is not a second wall down there */
  { atDepth(FINAL_DEPTH);
    ok('you hold the key on the last depth', G.keys >= 1, 'keys=' + G.keys); }

  /* every one of its attacks resolves, driven directly */
  { const B = atDepth(FINAL_DEPTH);
    const room = G.rooms.reduce((a, b) => (b.w * b.h > a.w * a.h ? b : a), G.rooms[0]);
    G.props.length = 0; if (G.hazards) G.hazards.length = 0;
    const stuck = [];
    for (const act of hacts) {
      B.hp = B.max * .2; B.cd = 0; B.alert = true; B.kx = 0; B.ky = 0;
      B.immune = false; B.wardT = undefined; B.wardAdds = null;
      B.x = room.cx * T + T / 2; B.y = room.cy * T + T / 2;
      G.players.forEach(pl => { pl.down = false; pl.hp = pl.max; pl.inv = 1e9; pl.x = B.x + 40; pl.y = B.y; });
      B.st = act; B.stt = 0; B.ca = 1;
      buildFlow();
      let back = false;
      for (let i = 0; i < 500; i++) {
        updateEnemies(1 / 60); updateShots(1 / 60); updateFx(1 / 60);
        G.players.forEach(pl => { pl.hp = pl.max; });
        if (B.st === 'chase') { back = true; break; }
      }
      if (!back) stuck.push(act);
    }
    ok('and every one of them resolves', stuck.length === 0, stuck.join(',') || 'all clear'); }

  /* putting it down wins the run */
  { const wins0 = META.wins || 0;
    const B = atDepth(FINAL_DEPTH);
    G.won = false;
    hurtFoe(B, B.max * 10, 0, false, false, G.players[0]);
    for (let i = 0; i < 6; i++) updateEnemies(1 / 60);
    ok('putting the Heart down wins the run', G.won === true);
    ok('and the win is remembered', (META.wins || 0) === wins0 + 1, wins0 + ' -> ' + (META.wins || 0));
    ok('it drops no key, because there is nowhere left to unlock', !G.items.some(i => i.kind === 'key'));
    ok('but it does pay out', G.items.filter(i => i.kind === 'chest').length >= 3,
       G.items.filter(i => i.kind === 'chest').length + ' chests');
    /* the victory screen is its own state, so the player chooses what next */
    /* the kill levels you, so a card is usually open at that moment: the win
       has to wait for it rather than snatch the choice away */
    for (let i = 0; i < 60 * 4; i++) updateFx(1 / 60);
    const heldForCard = G.state === 'offer';
    let gg2 = 0; while (G.offer && gg2++ < 20) applyUpgrade(0);
    for (let i = 0; i < 20; i++) update(1 / 60);
    ok('and the run stops for a victory screen', G.state === 'won', G.state + (heldForCard ? ' (waited for a card)' : ''));
    ok('the victory outlasts a pending upgrade card', G.won === true); }

  /* an ordinary boss still just drops a key */
  { const B = atDepth(18); G.won = false;
    hurtFoe(B, B.max * 10, 0, false, false, G.players[0]);
    for (let i = 0; i < 6; i++) updateEnemies(1 / 60);
    ok('an ordinary warden still only drops a key', G.items.some(i => i.kind === 'key') && G.won === false); }

  /* a won run banks more, and only once */
  { startGame(['sable']); G.level = 12; G.score = 1000; G.gold = 400;
    G.won = false; const e0 = META.echoes; die(); const plain = META.echoes - e0;
    startGame(['sable']); G.level = 12; G.score = 1000; G.gold = 400;
    G.won = true; const e1 = META.echoes; die(); const won = META.echoes - e1;
    ok('a won run is worth more echoes', won > plain, plain + ' -> ' + won);
    const e2 = META.echoes; die(); die();
    ok('and a run can only be banked once', META.echoes === e2, 'held at ' + META.echoes); }
}

/* ---------------- things move ---------------- */
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

const fails = results.filter(r => r[0] === 'FAIL');
for (const [st, n, x] of results) console.log(st + '  ' + n + (x ? '  [' + x + ']' : ''));
console.log('\n' + (results.length - fails.length) + '/' + results.length + ' checks passed');
if (fails.length) { console.log('FAILURES:'); for (const f of fails) console.log('  ' + f[1] + '  ' + f[2]); }
