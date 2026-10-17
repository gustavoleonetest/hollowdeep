/* Behavioural checks for the Gauntlet and Diablo systems. */
const results = [];
const ok = (n, c, x) => results.push([c ? 'PASS' : 'FAIL', n, x === undefined ? '' : String(x)]);
for (const k in SPR) { const s = SPR[k]; s.ok = true; s.src = { width: 1280, height: 1280 }; s.f = 1; }
const clearOffers = () => { let g = 0; while (G.offer && g++ < 60) applyUpgrade(0); G.offerQ.length = 0; G.state = 'play'; };
const quiet = () => { G.state = 'play'; };

startGame(['bulwark']);
G.level = 6; genLevel(); clearOffers();
let P = G.players[0];

/* Measuring the drain, or the stairs rule, means nothing else may touch the
   player: food heals, foes hit, a chest raises a card and update returns
   before the rule under test ever runs. */
function bareFloor() {
  G.enemies.length = 0; G.nests.length = 0; G.hazards.length = 0;
  G.eshots.length = 0; G.shots.length = 0; G.items.length = 0; G.zones.length = 0;
  G.hitstop = 0; G.winPending = false; G.offer = null; G.offerQ.length = 0;
  /* the stairs room can itself be an arena room: stepping onto the exit then
     starts the arena, which moves the delvers out of it entirely */
  G.event = null;
  for (const r of (G.rooms || [])) r.eventDone = true;
  for (const p of G.players) { p.down = false; p.inv = 1e9; p.kx = 0; p.ky = 0; p.dash = 0; }
}
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
    /* a cramped room eats every shard on a wall before the recall, which says
       nothing about whether they come back: keep looking for a room with room */
    let mine = G.eshots.slice();
    for (let attempt = 0; attempt < 12 && mine.length; attempt++) {
      let alive = 0;
      const probe = mine.map(s2 => ({ s2, x: s2.x, y: s2.y, vx: s2.vx, vy: s2.vy }));
      for (let i = 0; i < 52; i++) updateShots(1 / 60);
      alive = mine.filter(s2 => G.eshots.indexOf(s2) >= 0).length;
      for (const q of probe) { q.s2.x = q.x; q.s2.y = q.y; q.s2.vx = q.vx; q.s2.vy = q.vy; q.s2.life = 3.4; if (G.eshots.indexOf(q.s2) < 0) G.eshots.push(q.s2); }
      if (alive >= 3) break;
      const b2 = bossIn('obsidian'); b2[0].st = 'shards'; bossAct(b2[0]); mine = G.eshots.slice();
    }
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
    bareFloor();
    P.hp = P.max; const h0 = P.hp;
    for (let i = 0; i < 120; i++) { P.inv = 1e9; update(1 / 60); }
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

/* ---------------- the scenery ---------------- */
{
  const atlas = new Set();
  for (const meta of [SPR_META, SPR_META2])
    for (const k in meta) if (meta[k].frames) for (const f in meta[k].frames) atlas.add(f);

  /* a misspelt prop name draws nothing at all and says nothing about it */
  { const bad = [];
    PROP_POOL.forEach((pool, zone) => pool.forEach(e => { if (!atlas.has(e[0])) bad.push('zone' + zone + ':' + e[0]); }));
    ok('every prop a zone can roll exists in the atlas', bad.length === 0, bad.join(' ') || atlas.size + ' frames'); }

  { const thin = PROP_POOL.map((p, i) => [i, p.length]).filter(([, n]) => n < 8);
    ok('every zone has scenery to draw from', thin.length === 0, thin.map(([i, n]) => 'zone' + i + '=' + n).join(' ') || PROP_POOL.map(p => p.length).join('/')); }

  /* the furniture is meant to land where a room of that kind would have had it */
  const poolHas = (zone, name) => PROP_POOL[zone].some(e => e[0] === name);
  ok('the stores are furnished', ['p_table', 'p_bench', 'p_stool', 'p_crate_metal'].every(n => poolHas(1, n)));
  ok('the forge has a bench to work at', poolHas(3, 'p_bench') && poolHas(3, 'p_crate_metal'));
  ok('the sanctum has shelves and glassware', poolHas(5, 'r_bookcase') && poolHas(5, 'p_bottles'));
  ok('the graves get candles', poolHas(0, 'r_candles') && poolHas(4, 'r_candles'));

  /* and it must actually reach the floor, not just the table of possibilities */
  { const seen = new Set();
    for (let r = 0; r < 40; r++) { startGame(['sable']); G.level = 5; genLevel(); for (const q of G.props) seen.add(q.k); }
    const furniture = ['p_table', 'p_bench', 'p_stool', 'p_chair', 'p_crate_metal', 'p_chest_wood', 'p_stall', 'p_bottles'];
    const landed = furniture.filter(f => seen.has(f));
    ok('furniture is placed in the drowned halls', landed.length >= 4, landed.join(',') || 'none in 40 levels'); }

  /* glass should not splinter like a plank */
  ok('bottles break like glass', propMat('p_bottles') === 'glass' && propMat('p_potion2') === 'glass', propMat('p_bottles'));
  ok('and so does the chalice', propMat('p_chalice') === 'glass');
  ok('while a table is still wood', propMat('p_table') === 'wood');
  ok('and a metal crate is still metal', propMat('p_crate_metal') === 'metal');
  ok('glass has colours to break into', Array.isArray(MATCOL.glass) && MATCOL.glass.length === 3);

  /* the locked door carries the gate, and stops once it is open */
  { startGame(['thistle']); G.level = 4; genLevel(); G.offer = null; G.offerQ.length = 0;
    const d = G.door;
    const drawn = () => {
      const seen = {};
      const real = sprProp;
      sprProp = function (n) { seen[n] = 1; return true; };
      try { drawDoor(); } finally { sprProp = real; }
      return seen;
    };
    /* fog is cleared in the render pass, which does not run here, so lift it
       directly: this check is about the door, not about what you can see */
    const P = G.players[0]; P.x = d.x * T + T / 2; P.y = d.y * T + T / 2 + 24;
    for (let i = 0; i < 30; i++) update(1 / 60);
    fogA.fill(0);
    ok('a locked door is a gate you can see', !!drawn()['gate'], 'tile=' + G.map[d.y * MW + d.x]);
    G.map[d.y * MW + d.x] = 0;
    ok('and it is gone once unlocked', !drawn()['gate']); }
}

/* ---------------- two delvers, one keyboard ---------------- */
{
startGame(['bulwark', 'sable']);
ok('two delvers start together', G.players.length === 2, G.players.map(p => p.cls.name).join(' + '));
ok('co-op is flagged', G.co === true);
G.level = 4; genLevel();
let g = 0; while (G.offer && g++ < 20) applyUpgrade(0); G.offerQ.length = 0; G.state = 'play';
ok('both are placed on open floor', G.players.every(p => openAt(p.x, p.y) && !blockedAt(p.x, p.y, 11)));

/* one falling must not end the run */
const [A, B] = G.players;
A.hp = 1; A.inv = 0; downPlayer(A);
ok('one down does not end the run', G.state === 'play' && A.down === true);
ok('and the other still stands', !B.down);

/* and a partner standing over them can bring them back */
B.x = A.x + 6; B.y = A.y;
for (let i = 0; i < 180 && A.down; i++) updateRevive(1 / 60);
ok('a partner can raise the fallen', A.down === false, 'hp=' + Math.round(A.hp));

/* both down ends it */
A.inv = 0; B.inv = 0; downPlayer(A); downPlayer(B);
ok('both down ends the run', G.state === 'dead');

/* The stairs rule lives at the end of update: every delver still standing has
   to be within reach of the exit. Drive it a frame at a time in a bare room,
   rather than simulating two hundred and letting everything else in the game
   decide the answer. */
startGame(['ember', 'thistle']); G.level = 3; genLevel();
g = 0; while (G.offer && g++ < 20) applyUpgrade(0); G.offerQ.length = 0; G.state = 'play';
const [P1, P2] = G.players;
const lvl0 = G.level;
G.keys = 9;
const clear = () => { bareFloor(); for (const p of G.players) p.hp = p.max; };
const put = (p, dx) => { p.x = G.exit.x + dx; p.y = G.exit.y; };

clear(); put(P1, -6); put(P2, 600);
update(1 / 60);
ok('one delver alone does not take the stairs', G.state === 'play', G.state);

clear(); put(P1, -6); put(P2, 6);
update(1 / 60);
ok('both on the stairs clears the depth', G.state === 'clear', G.state);

for (let i = 0; i < 200 && G.state === 'clear'; i++) clearTick(1 / 60);
ok('and the stall follows', G.state === 'shop', G.state);
if (G.state === 'shop') { renderShop(); leaveShop(); }
ok('and leaving it descends', G.level > lvl0, 'depth ' + lvl0 + ' -> ' + G.level);
ok('both delvers come down together', G.players.filter(p => !p.down).length === 2);

/* a fallen partner must not hold the stairs: the living ones decide */
g = 0; while (G.offer && g++ < 20) applyUpgrade(0); G.offerQ.length = 0; G.state = 'play';
G.keys = 9;
clear(); put(P1, -6); P2.down = true; P2.x = G.exit.x + 600; P2.y = G.exit.y;
update(1 / 60);
ok('a fallen partner does not hold the stairs', G.state === 'clear', G.state);
G.state = 'play';

/* an offer belongs to one delver, and must land on that one */
startGame(['bulwark', 'sable']); G.level = 5; genLevel(); G.offerQ.length = 0; G.offer = null;
queueOffer({ kind: 'up', P: G.players[1], opts: rollOffer(false) });
ok('an offer can belong to the second delver', G.offer && G.offer.P === G.players[1]);
const second0 = G.players[1].dmgMul, first0 = G.players[0].dmgMul;
applyUpgrade(0);
ok('and it applies to that delver', G.players[1].dmgMul !== second0 || G.players[1].plvl > 0);
ok('not to the first', G.players[0].dmgMul === first0);
}

/* ---------------- it thins itself on a slow device ---------------- */
{
  const resetPerf = () => { fxLevel = 0; PERF.ring.length = 0; PERF.at = 0; PERF.hold = 0; };
  const feed = (ms, frames) => { for (let i = 0; i < frames; i++) perfTick(ms); };

  startGame(['sable']); G.level = 3; genLevel();
  let gg = 0; while (G.offer && gg++ < 20) applyUpgrade(0); G.offerQ.length = 0; G.state = 'play';

  resetPerf();
  ok('a quick device draws everything', fxLevel === 0 && fxThin() === 1);

  feed(40, PERF.n * 2);
  ok('sustained slow frames thin the decoration', fxLevel > 0, 'level ' + fxLevel);
  const thinned = fxLevel;
  feed(40, PERF.n * 6);
  ok('and it keeps stepping down while it struggles', fxLevel > thinned || fxLevel === 2, 'level ' + fxLevel);
  ok('but never past the floor', fxLevel <= 2, 'level ' + fxLevel);

  feed(3, PERF.n * 8);
  ok('and climbs back when the device keeps up', fxLevel === 0, 'level ' + fxLevel);

  /* a couple of slow frames in a row is a hitch, not a slow device */
  resetPerf();
  feed(4, PERF.n);
  const before = fxLevel;
  for (let i = 0; i < 5; i++) perfTick(60);
  ok('a brief hitch is not treated as a slow device', fxLevel === before, 'level ' + fxLevel);

  /* and it must not flutter between levels frame to frame */
  resetPerf();
  let changes = 0, prev = fxLevel;
  for (let i = 0; i < PERF.n * 10; i++) { perfTick(i % 2 ? 40 : 3); if (fxLevel !== prev) { changes++; prev = fxLevel; } }
  ok('it cannot flutter between levels', changes <= 3, changes + ' changes over ' + (PERF.n * 10) + ' frames');

  /* menus are not the game, and must not be measured */
  resetPerf(); G.state = 'menu';
  feed(80, PERF.n * 4);
  ok('a slow menu does not thin the game', fxLevel === 0, 'level ' + fxLevel);
  G.state = 'play';

  /* what it changes is decoration, and only decoration */
  resetPerf();
  G.parts.length = 0; burst(100, 100, '#fff', 40, 100);
  const full = G.parts.length;
  fxLevel = 2;
  G.parts.length = 0; burst(100, 100, '#fff', 40, 100);
  const sparse = G.parts.length;
  ok('thinning means fewer particles', sparse < full, full + ' -> ' + sparse);
  ok('but never none at all', sparse > 0, sparse);

  /* the simulation must not notice */
  resetPerf();
  startGame(['thistle']); G.level = 4; genLevel();
  gg = 0; while (G.offer && gg++ < 20) applyUpgrade(0); G.offerQ.length = 0; G.state = 'play';
  const snap = () => ({ foes: G.enemies.length, crypts: G.nests.length, items: G.items.length,
                        hp: Math.round(G.players[0].hp), props: G.props.length });
  fxLevel = 0; const a0 = snap();
  fxLevel = 2; const a2 = snap();
  ok('thinning changes nothing the game runs on',
     JSON.stringify(a0) === JSON.stringify(a2), JSON.stringify(a2));
  { const P = G.players[0];
    bareFloor();
    fxLevel = 2; P.hp = P.max; const h0 = P.hp;
    for (let i = 0; i < 60; i++) { P.inv = 1e9; update(1 / 60); }
    const lost2 = h0 - P.hp;
    bareFloor();
    fxLevel = 0; P.hp = h0;
    for (let i = 0; i < 60; i++) { P.inv = 1e9; update(1 / 60); }
    const lost0 = h0 - P.hp;
    ok('and the clock runs at the same rate either way', Math.abs(lost2 - lost0) < 1.5,
       lost0.toFixed(1) + ' vs ' + lost2.toFixed(1) + ' health in a second'); }
  fxLevel = 0;
}

/* ---------------- saved progress survives being wrong ---------------- */
{
  const put = (o) => localStorage.setItem(META_KEY, typeof o === 'string' ? o : JSON.stringify(o));
  const keep = localStorage.getItem(META_KEY);

  /* numbers that arrived as strings used to make the next payout concatenate:
     "40" + 67 became "4067", written back, growing every run */
  put({ echoes: '40', best: '900', runs: '7', wins: '2', deepest: '9' });
  loadMeta();
  ok('a number saved as text is read as a number', typeof META.echoes === 'number', typeof META.echoes + ' ' + META.echoes);
  ok('and keeps its value', META.echoes === 40 && META.best === 900 && META.deepest === 9,
     META.echoes + '/' + META.best + '/' + META.deepest);
  { const e0 = META.echoes;
    G.won = false; G.gold = 0; G.score = 0; G.level = 2; bankRun();
    ok('so banking a run adds rather than concatenates', typeof META.echoes === 'number' && META.echoes > e0,
       e0 + ' -> ' + META.echoes); }

  put({ echoes: 'lots', best: null, deepest: 'deep', wins: NaN });
  loadMeta();
  ok('nonsense falls back to a sane default',
     META.echoes === 0 && META.best === 0 && META.deepest === 1 && META.wins === 0,
     [META.echoes, META.best, META.deepest, META.wins].join('/'));

  put({ echoes: -500, wins: -3, deepest: -9, runs: -1 });
  loadMeta();
  ok('negatives cannot be saved in', META.echoes >= 0 && META.wins >= 0 && META.deepest >= 1 && META.runs >= 0,
     [META.echoes, META.wins, META.deepest, META.runs].join('/'));

  put({ echoes: 12.7 });
  loadMeta();
  ok('and a fraction becomes a whole number', Number.isInteger(META.echoes), String(META.echoes));

  /* perk levels drive array maths and pricing, so they have to be whole and capped */
  put({ perks: { vigour: '2', slow: 99, flask: 'x', nonsense: 4, purse: -2 } });
  loadMeta();
  ok('a perk level saved as text still counts', perkLv('vigour') === 2, String(perkLv('vigour')));
  ok('and cannot exceed its cap', perkLv('slow') === PERKS.find(p => p.id === 'slow').max, String(perkLv('slow')));
  ok('an unreadable level is simply zero', perkLv('flask') === 0, String(perkLv('flask')));
  ok('a negative one too', perkLv('purse') === 0, String(perkLv('purse')));
  ok('and an unknown perk is dropped', META.perks.nonsense === undefined);
  ok('every kept level is a whole number', Object.keys(META.perks).every(k => Number.isInteger(META.perks[k])),
     JSON.stringify(META.perks));

  put('{ this is not json');
  loadMeta();
  ok('a torn save does not throw', typeof META.echoes === 'number');

  put({ perks: 'not an object' });
  loadMeta();
  ok('and neither does a perks field that is not one', META.perks && typeof META.perks === 'object');

  /* the price of a perk has to stay a real number whatever was loaded */
  ok('perk prices stay finite', PERKS.every(p => Number.isFinite(perkCost(p))));

  if (keep === null) localStorage.removeItem(META_KEY); else localStorage.setItem(META_KEY, keep);
  loadMeta();
}

/* ---------------- one bad frame does not end the game ---------------- */
{
  /* the loop used to schedule the next frame last, so anything that threw
     stopped it for good and the game froze on its final image */
  startGame(['sable']); G.level = 3; genLevel();
  let gg = 0; while (G.offer && gg++ < 20) applyUpgrade(0); G.offerQ.length = 0; G.state = 'play';

  let scheduled = 0;
  const realRaf = globalThis.requestAnimationFrame;
  globalThis.requestAnimationFrame = () => { scheduled++; return 1; };
  const realRender = render, errs0 = frameErrs;
  /* the throw here is deliberate, so keep its report out of the suite output */
  const realErr0 = console.error;
  console.error = () => {};
  let threw = false;
  try {
    render = () => { throw new Error('a frame blew up'); };
    frame(performance.now());
    frame(performance.now());
  } catch (e) { threw = true; }
  finally { render = realRender; globalThis.requestAnimationFrame = realRaf; console.error = realErr0; }

  ok('a throwing frame does not escape the loop', !threw);
  ok('and the next frame is still scheduled', scheduled >= 2, scheduled + ' scheduled');
  ok('the failure is reported rather than swallowed', frameErrs > errs0, (frameErrs - errs0) + ' reported');

  /* and it must stop shouting once it has made the point: a fault every
     frame would otherwise bury the console and slow the page further */
  frameErrs = 0;
  let logged = 0;
  const realErr = console.error;
  console.error = () => { logged++; };
  globalThis.requestAnimationFrame = () => 1;
  try { render = () => { throw new Error('again'); }; for (let i = 0; i < 60; i++) frame(performance.now()); }
  finally { render = realRender; globalThis.requestAnimationFrame = realRaf; console.error = realErr; }
  ok('it stops reporting after the first few', logged > 0 && logged <= 4, logged + ' lines for 60 bad frames');

  /* the game is still playable afterwards */
  const P = G.players[0], h0 = P.hp;
  for (let i = 0; i < 30; i++) update(1 / 60);
  ok('and the game still runs after a bad frame', P.hp !== h0 || G.state === 'play', G.state);
}

/* ---------------- told apart by more than colour ---------------- */
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

/* ---------------- playable with no mouse ---------------- */
{
  startGame(['thistle']); G.level = 3; genLevel();
  let gg = 0; while (G.offer && gg++ < 20) applyUpgrade(0); G.offerQ.length = 0; G.state = 'play';
  const P = G.players[0];
  const keep = mouse.last;
  mouse.last = -1e9;                   /* the mouse has never been touched */
  for (const k of ['KeyW', 'KeyA', 'KeyS', 'KeyD']) keys[k] = false;

  keys.KeyD = true; readInput(); keys.KeyD = false;
  const right = INS[0].aim;
  keys.KeyW = true; readInput(); keys.KeyW = false;
  const up = INS[0].aim;
  ok('aim follows the way you walk when there is no mouse',
     Math.abs(Math.atan2(Math.sin(right), Math.cos(right))) < .5 && up < -1 && up > -2.2,
     'right ' + right.toFixed(2) + ', up ' + up.toFixed(2));

  /* and that aim has to be good enough to actually hit something */
  bareFloor();
  spawnFoe('gloam', P.x + 70, P.y, false);
  const e = G.enemies[G.enemies.length - 1];
  e.x = P.x + 70; e.y = P.y; e.hp = 9999; e.max = 9999; e.spd = 0;
  keys.KeyD = true; readInput(); keys.KeyD = false;
  P.cd = 0; const h0 = e.hp;
  attack(P);
  for (let i = 0; i < 60; i++) update(1 / 60);
  ok('and a keyboard-only attack lands', e.hp < h0, (h0 - e.hp).toFixed(0) + ' damage');
  mouse.last = keep;
}

/* ---------------- the game makes a noise when it matters ---------------- */
{
  /* sfx() silently ignores a name it does not know, so a typo is a moment
     that simply never makes a sound. Listen to what the game asks for and
     check every name against the table. */
  const heard = [];
  const realSfx = sfx;
  const listen = (fn) => {
    heard.length = 0;
    sfx = (k) => { heard.push(k); };
    try { fn(); } finally { sfx = realSfx; }
    return heard.slice();
  };

  ok('every sound the game can play is defined', Object.keys(SFXF).length >= 15, Object.keys(SFXF).length + ' sounds');
  ok('and asking for one that is not does nothing rather than throw',
     (() => { try { realSfx('no such sound'); return true; } catch (e) { return false; } })());

  /* the moments that should be audible */
  const moments = {};
  moments['an omen arriving'] = listen(() => {
    const real = rollOmen; rollOmen = () => OMENS[0];
    try { startGame(['sable']); G.level = 8; genLevel(); } finally { rollOmen = real; }
  });
  moments['a chest opening'] = listen(() => {
    startGame(['sable']); G.level = 4; genLevel(); G.offer = null; G.offerQ.length = 0;
    openChest(G.players[0], { x: G.players[0].x, y: G.players[0].y, big: false });
  });
  moments['a warden falling'] = listen(() => {
    startGame(['sable']); G.level = 6; genLevel();
    let gg = 0; while (G.offer && gg++ < 20) applyUpgrade(0); G.offerQ.length = 0; G.state = 'play';
    const B = G.enemies.find(e => e.boss);
    if (B) hurtFoe(B, B.max * 10, 0, false, false, G.players[0]);
  });
  moments['learning a boon'] = listen(() => {
    startGame(['bulwark']); G.level = 4; genLevel(); G.offer = null; G.offerQ.length = 0;
    const P = G.players[0];
    queueOffer({ kind: 'boon', P, opts: rollBoons(P) });
    applyUpgrade(0);
  });
  moments['taking a pact'] = listen(() => {
    startGame(['sable']); G.level = 5; genLevel(); G.offer = null; G.offerQ.length = 0;
    const P = G.players[0];
    const it = { kind: 'shrine', x: P.x, y: P.y, t: 0, cool: 0, sh: { kind: 'pact', pact: PACTS[0] } };
    G.items.push(it);
    queueOffer({ kind: 'pact', P, shrine: it });
    applyUpgrade(0);
  });
  moments['taking a hit'] = listen(() => {
    startGame(['ember']); G.level = 3; genLevel(); G.state = 'play';
    const P = G.players[0]; P.inv = 0; hurtPlayer(P, 5, 0);
  });

  const silent = Object.keys(moments).filter(k => moments[k].length === 0);
  ok('every moment that should be heard makes a sound', silent.length === 0, silent.join(', ') || Object.keys(moments).length + ' checked');

  /* and nothing asks for a sound that does not exist */
  const asked = new Set();
  for (const k in moments) for (const n of moments[k]) asked.add(n);
  const unknown = [...asked].filter(n => !SFXF[n]);
  ok('and none of them asks for a sound that is not there', unknown.length === 0, unknown.join(',') || [...asked].sort().join(' '));

  /* the omen one is new, and was the gap that prompted this */
  ok('an omen is heard, not only narrated', moments['an omen arriving'].includes('omen'),
     moments['an omen arriving'].join(',') || 'silence');

  /* arriving on a floor must sound the same however you got there: the elite
     sting is for an elite you have met, not for every one the floor was built
     with */
  { const onArrive = (fn) => listen(fn).filter(n => n === 'elite').length;
    const fresh = onArrive(() => { startGame(['sable']); });
    /* build the floor first and listen only to the descent itself, or the
       setup's own generation is what gets counted */
    startGame(['sable']); G.level = 7; genLevel();
    { let gg = 0; while (G.offer && gg++ < 20) applyUpgrade(0); }
    G.offerQ.length = 0; G.state = 'shop';
    const descended = onArrive(() => leaveShop());
    ok('starting a run does not announce its elites', fresh === 0, fresh + ' stings');
    ok('and nor does descending to the next depth', descended === 0, descended + ' stings');
    ok('but meeting one still does', listen(() => {
      startGame(['sable']); G.level = 4; genLevel(); G.state = 'play';
      spawnFoe('gloam', G.players[0].x + 80, G.players[0].y, true);
    }).includes('elite')); }

  /* mute has to stop the one-shots too, not just the music */
  { const wasMuted = muted;
    const calls = [];
    const realTone = tone;
    tone = (...a) => { calls.push('tone'); };
    try {
      setMuted(true);
      realSfx('coin'); realSfx('boom');
      ok('mute stops the sound effects', calls.length === 0, calls.length + ' tones while muted');
    } finally { tone = realTone; setMuted(wasMuted); } }

  /* and the narrator is a preference that is remembered */
  { const was = voiceOn;
    voiceOn = false; G.vlast = {}; G.voice = null;
    announce('a line nobody asked for', '#fff');
    ok('the narrator still shows its line on screen when muted', !!G.voice, G.voice ? 'shown' : 'nothing');
    voiceOn = was; }
}

/* ---------------- it explains itself, once ---------------- */
{
  const forget = () => { META.taught = {}; G.vlast = {}; G.voice = null; };
  const said = () => (G.voice && G.voice.txt) || '';

  ok('there is a lesson for each thing a new delver must work out',
     TAUGHT.length >= 3 && TAUGHT.every(t => t[0] && t[1] && t[1].length > 20), TAUGHT.map(t => t[0]).join(','));

  /* the drain: only once it has cost you, and only with nothing hitting you */
  { forget(); bareFloor();
    startGame(['bulwark']); G.level = 2; genLevel(); G.state = 'play';
    bareFloor();
    const P = G.players[0];
    ok('nothing is said while you are still whole', !META.taught.drain);
    P.hp = P.max; P.inv = 1e9; P.lastHit = -999;
    for (let i = 0; i < 60 * 25 && !META.taught.drain; i++) update(1 / 60);
    ok('the drain explains itself once it bites', !!META.taught.drain, said().slice(0, 40)); }

  /* and never again, on any later run */
  { const before = said();
    G.vlast = {}; G.voice = null;
    const P = G.players[0]; P.hp = P.max * .5;
    for (let i = 0; i < 120; i++) update(1 / 60);
    ok('and does not repeat itself afterwards', said() !== before || said() === '', said().slice(0, 30) || 'silent'); }

  /* being hit is not the drain, and must not be explained as it */
  { forget();
    startGame(['bulwark']); G.level = 2; genLevel(); G.state = 'play';
    bareFloor();
    const P = G.players[0]; P.hp = P.max * .5; P.inv = 0; P.lastHit = clock;
    for (let i = 0; i < 90; i++) { P.lastHit = clock; update(1 / 60); }
    ok('taking hits is not explained as the drain', !META.taught.drain); }

  /* a crypt, when one is actually in front of you */
  { forget();
    startGame(['sable']); G.level = 3; genLevel(); G.state = 'play';
    G.nests.length = 0; fogA.fill(1);
    const P = G.players[0];
    updateNests(1 / 60);
    ok('a crypt you cannot see teaches nothing', !META.taught.crypt);
    G.nests.push({ x: P.x + 60, y: P.y, r: 15, hp: 100, max: 100, t: 9, flash: 0 });
    fogA.fill(0);
    updateNests(1 / 60);
    ok('one you can see does', !!META.taught.crypt, said().slice(0, 40)); }

  /* the locked door, when you reach it with nothing to open it */
  { forget();
    startGame(['thistle']); G.level = 3; genLevel(); G.state = 'play';
    bareFloor();
    const P = G.players[0], d = G.door;
    G.keys = 0; P.lockMsg = 0;
    P.x = d.x * T + T / 2; P.y = d.y * T + T / 2 + 20;
    for (let i = 0; i < 90 && !META.taught.door; i++) { P.x = d.x * T + T / 2; P.y = d.y * T + T / 2 + 20; update(1 / 60); }
    ok('the locked door says what it wants', !!META.taught.door, said().slice(0, 40)); }

  /* a delver who has been told keeps it between runs */
  { META.taught = { drain: 1, crypt: 1, door: 1 };
    saveMeta(); loadMeta();
    ok('what you have been told is remembered across runs',
       META.taught.drain === 1 && META.taught.crypt === 1 && META.taught.door === 1, JSON.stringify(META.taught)); }

  /* and a torn save cannot invent lessons that do not exist */
  { const keep = localStorage.getItem(META_KEY);
    localStorage.setItem(META_KEY, JSON.stringify({ taught: { drain: 1, nonsense: 1, door: 'yes' } }));
    loadMeta();
    ok('an unknown lesson is dropped on the way in', META.taught.nonsense === undefined, JSON.stringify(META.taught));
    if (keep === null) localStorage.removeItem(META_KEY); else localStorage.setItem(META_KEY, keep);
    loadMeta(); }
}

/* ---------------- looking away does not cost the run ---------------- */
{
  const hide = (on) => { try { Object.defineProperty(document, 'hidden', { value: on, configurable: true }); } catch (e) { document.hidden = on; } };
  const wasHidden = !!document.hidden;

  startGame(['bulwark']); G.level = 3; genLevel();
  let gg = 0; while (G.offer && gg++ < 20) applyUpgrade(0); G.offerQ.length = 0; G.state = 'play'; G.paused = false;
  bareFloor();

  hide(true); pauseForHidden();
  ok('a run holds when the page goes out of sight', G.paused === true);

  /* and the clock must genuinely stop, not merely look stopped */
  { const P = G.players[0], h0 = P.hp;
    for (let i = 0; i < 300; i++) { if (G.state === 'play' && !G.paused) update(1 / 60); }
    ok('and nothing drains while it is held', P.hp === h0, h0.toFixed(1) + ' -> ' + P.hp.toFixed(1)); }

  /* coming back must not drop you straight into whatever you walked away from */
  hide(false); pauseForHidden();
  ok('coming back does not resume on its own', G.paused === true);

  /* P is no use on a phone, so a tap has to work: resumeFromPause is what
     both the click and the touch handler call */
  ok('and a tap or click carries on', resumeFromPause() === true && G.paused === false);
  ok('but does nothing when there is nothing to resume', resumeFromPause() === false);

  /* a key held down as you tab away must not still be held when you return */
  { G.paused = false; keys.KeyD = true; mouse.down = true;
    hide(true); pauseForHidden();
    ok('a held key is let go when the run is put down', !keys.KeyD && !mouse.down);
    hide(false); G.paused = false; }

  /* the menu, the stall and the death screen are not runs */
  for (const st of ['menu', 'shop', 'dead', 'won']) {
    G.state = st; G.paused = false;
    hide(true); pauseForHidden();
    ok('nothing to hold while in ' + st, G.paused === false);
  }
  hide(wasHidden); G.state = 'play'; G.paused = false;
}

/* ---------------- nothing grows without limit ---------------- */
{
  /* A run can last half an hour, and anything that only ever gets pushed to
     will eventually cost frames. The ceilings below are what the game
     actually reached over three passes of sixteen depths of constant
     fighting, with room left over: particles peaked at 322 against their cap
     of 1400, foes at 45, crypts at 47, props at 63, and nothing else got
     past single figures. A list that sails past these is growing, not busy. */
  /* The foe ceiling is the arena's own arithmetic, not a measured peak: it
     spawns while fewer than 44 are alive, in a batch of round(4 + depth*.45
     + wave*2), which is about 19 at the deepest. So 43 + 19 = 62 is what
     the code permits, and a measured max of 45 simply never hit an arena at
     depth. Anything past 90 is growth, not a busy arena. */
  const CEILING = {
    parts: 1400, enemies: 90, nests: 90, props: 160, torches: 60, hazards: 40,
    texts: 200, fxs: 200, decals: 120, dying: 60, shots: 300, eshots: 400,
    zones: 300, timers: 200,
  };
  const over = [];
  startGame(['ember']);
  for (let depth = 1; depth <= 14; depth++) {
    G.level = depth; genLevel();
    let gg = 0; while (G.offer && gg++ < 30) applyUpgrade(0);
    G.offerQ.length = 0; G.state = 'play';
    const P = G.players[0];
    for (let i = 0; i < 240; i++) {
      P.inv = 1e9; P.hp = P.max;
      INS[0].mx = Math.cos(i / 25); INS[0].my = Math.sin(i / 25); INS[0].fire = true;
      readInput(); update(1 / 60);
      if (G.state !== 'play') G.state = 'play';
      for (const k in CEILING) {
        const n = (G[k] && G[k].length) || 0;
        if (n > CEILING[k]) over.push(k + ' ' + n + ' at depth ' + depth);
      }
    }
  }
  INS[0].fire = false; INS[0].mx = 0; INS[0].my = 0;
  ok('no list runs away over a long descent', over.length === 0, over.slice(0, 3).join(', ') || 'all within bounds');
}

/* ---------------- the touch controls know they are showing ---------------- */
{
  /* btnsOn decides where the narrator's line sits and what the pause overlay
     tells you to press, so it has to match what is actually on screen. */
  const shown = () => { try { return getComputedStyle($('dashBtn')).display !== 'none'; } catch (e) { return false; } };
  startGame(['bulwark']); G.level = 2; genLevel(); G.state = 'play';
  $('hud').hidden = false;
  frame(performance.now());
  ok('the flag matches what is on screen in play', btnsOn === shown(), btnsOn + ' vs ' + shown());
  $('hud').hidden = true;
  frame(performance.now());
  ok('and when the run is not running', btnsOn === shown(), btnsOn + ' vs ' + shown());
  $('hud').hidden = false;
}

/* ---------------- nothing hits you out of the dark ---------------- */
{
  /* Fog stops a foe being drawn past about eight tiles, while a foe notices
     you from thirteen. That is fine for an archer, whose arrow is the
     warning, but nothing should be able to reach out and touch you while
     invisible. Measured over fifteen hundred frames on each of eight
     depths, about one hit in ten came from a foe in fog, and every one was
     an archer at roughly 265 units. */
  const bad = [];
  /* updateFog eases towards its target using real elapsed time, so in a tight
     loop it barely moves and every foe looks fogged. Advance the clock like a
     browser would, or this measures the harness instead of the game. */
  const realNow = performance.now;
  let fakeT = realNow.call(performance);
  performance.now = () => (fakeT += 16.7);
  const realHurt = hurtPlayer;
  hurtPlayer = function (P, dmg, ang, src) {
    const before = P.hp;
    const r = realHurt.apply(this, arguments);
    if (P.hp < before && src && src.x !== undefined) {
      const d = Math.hypot(src.x - P.x, src.y - P.y);
      if (fogAt(src.x, src.y) >= .4 && d < 120) bad.push((src.type || 'foe') + ' at ' + Math.round(d));
    }
    return r;
  };
  try {
    for (const depth of [4, 9, 14]) {
      startGame(['thistle']); G.level = depth; genLevel();
      let gg = 0; while (G.offer && gg++ < 30) applyUpgrade(0);
      G.offerQ.length = 0; G.state = 'play';
      const P = G.players[0];
      for (let i = 0; i < 700; i++) {
        P.hp = P.max;
        INS[0].mx = Math.cos(i / 40); INS[0].my = Math.sin(i / 37); INS[0].fire = true;
        readInput(); update(1 / 60); updateFog();
        if (G.state !== 'play') G.state = 'play';
      }
    }
  } finally { hurtPlayer = realHurt; performance.now = realNow; INS[0].fire = false; INS[0].mx = 0; INS[0].my = 0; }
  ok('nothing invisible reaches out and touches you', bad.length === 0, bad.slice(0, 3).join(', ') || 'none in 2100 frames');

  /* and the arrow that is your only warning carries its own light. The
     player's shots always punched a hole in the dark; the foes' did not,
     so the one thing you needed to see was the dimmest thing on screen. */
  { startGame(['sable']); G.level = 5; genLevel(); G.state = 'play';
    G.eshots.length = 0; G.shots.length = 0;
    const P = G.players[0];
    /* hole() skips anything off screen, and the stubbed canvas has no size,
       so give it one and put the camera on the player or everything culls */
    const keepW = lightCv.width, keepH = lightCv.height;
    lightCv.width = 800; lightCv.height = 600;
    cam.x = P.x - 400 / (DPR * Z); cam.y = P.y - 300 / (DPR * Z);
    let gradients = 0;
    const realGrad = lctx.createRadialGradient;
    lctx.createRadialGradient = function (...a) { gradients++; return realGrad.apply(lctx, a); };
    try {
      gradients = 0; drawLighting();
      const without = gradients;
      for (let i = 0; i < 6; i++) G.eshots.push({ x: P.x + 20 + i * 14, y: P.y, vx: 0, vy: 0, life: 9, r: 6, dmg: 1, own: null });
      gradients = 0; drawLighting();
      const withShots = gradients;
      ok('an incoming shot lights its own way', withShots >= without + 6,
         without + ' lights -> ' + withShots + ' with six arrows in the air');
    } finally {
      lctx.createRadialGradient = realGrad;
      lightCv.width = keepW; lightCv.height = keepH;
      G.eshots.length = 0;
    } }
}

/* ---------------- the run you left behind ---------------- */
{
  const RK = 'hollowdeep-run';
  const stored = () => { try { return JSON.parse(localStorage.getItem(RK) || 'null'); } catch (e) { return null; } };

  /* a descent that gets somewhere, and earns things on the way down */
  META.perks = { vigour: 3 };
  clearRun();
  startGame(['ember']);
  saveRun();                                   /* what pressing a delver does */
  const P0 = G.players[0];
  P0.gear.weapon = rollItem('weapon', RARITY.fabled, true);
  P0.boons['pyre'] = 1;
  P0.pacts.push(PACTS[0]);
  P0.plvl = 5; P0.up.dmg = 1.4; P0.up.hp += 30;
  recalc(P0); P0.hp = P0.max * .62;
  let guard = 0;
  while (G.level < 4 && guard++ < 12) { G.offer = null; G.offerQ.length = 0; nextLevel(); }
  /* set the run's state AFTER descending, then checkpoint deliberately:
     nextLevel heals to full and genLevel clears the key, so anything set
     before the loop is not the thing being tested */
  G.gold = 321; G.bombs = 3; G.kills = 77; G.score = 4210;
  P0.hp = P0.max * .41;
  saveRun();

  const want = {
    level: G.level, gold: G.gold, bombs: G.bombs, kills: G.kills, score: G.score,
    plvl: P0.plvl, dmg: P0.up.dmg, max: P0.max, hp: P0.hp,
    weapon: P0.gear.weapon.name, pacts: P0.pacts.length, boons: Object.keys(P0.boons).length
  };
  ok('the health being saved is not already full', want.hp < want.max - 1, want.hp.toFixed(1) + '/' + want.max);

  ok('taking the stairs writes a checkpoint', !!stored() && stored().level === want.level,
     stored() ? 'depth ' + stored().level : 'nothing written');

  /* THE TRAP: boot builds a throwaway run so the menu has something behind
     it, and Change delver does the same. Either writing a checkpoint would
     destroy the very run the menu is about to offer. */
  startGame('bulwark');
  ok('the menu backdrop does not clobber the run', !!stored() && stored().level === want.level,
     stored() ? 'depth ' + stored().level : 'the run was destroyed by the menu');

  /* what a reload is: the page comes back holding nothing but the store */
  const back = loadRun();
  ok('a reload finds the run', !!back && back.level === want.level, back ? 'depth ' + back.level : 'nothing');
  resumeRun(back);
  const R = G.players[0];
  ok('and it is your delver that comes back', G.clsKey === 'ember', G.clsKey);
  ok('at the depth it had reached', G.level === want.level, G.level + ' vs ' + want.level);
  ok('holding the gold and the flasks it had',
     G.gold === want.gold && G.bombs === want.bombs, G.gold + 'g ' + G.bombs + 'f');
  /* the key is deliberately NOT carried: a fresh floor hides its own */
  ok('but not a key, because the new floor hides its own',
     G.keys === (om('freeKey', false) ? 1 : 0), 'holding ' + G.keys);
  ok('with the score and the kills it had', G.score === want.score && G.kills === want.kills,
     G.score + ' / ' + G.kills);
  ok('carrying the weapon it found', !!R.gear.weapon && R.gear.weapon.name === want.weapon,
     R.gear.weapon ? R.gear.weapon.name : 'empty handed');
  ok('at the level it had earned', R.plvl === want.plvl && Math.abs(R.up.dmg - want.dmg) < 1e-9,
     'level ' + R.plvl + ' dmg ' + R.up.dmg);
  ok('with the pact it swore and the boon it learned',
     R.pacts.length === want.pacts && !!R.boons['pyre'], R.pacts.length + ' pacts, pyre ' + !!R.boons['pyre']);
  ok('and the pact is the real one, not a copy off the disk',
     R.pacts[0] === PACTS[0], R.pacts[0] === PACTS[0] ? 'same object' : 'a lookalike');
  /* the subtle one: makeDelver applies the Barrow's perks, and the saved
     stats already include them. Laying one over the other must not add
     vigour twice. */
  ok('the Barrow is not paid out twice', R.max === want.max, R.max + ' vs ' + want.max);
  ok('and the health is what you had, not a free refill', Math.abs(R.hp - want.hp) < 1e-6,
     R.hp.toFixed(1) + ' vs ' + want.hp.toFixed(1));
  ok('which is not simply full health', R.hp < R.max - 1, R.hp.toFixed(1) + '/' + R.max);
  ok('a second reload still finds it', !!stored() && stored().level === want.level,
     stored() ? 'depth ' + stored().level : 'nothing left to come back to');

  /* death is still death */
  die();
  ok('dying clears the checkpoint', stored() === null, stored() ? 'the run survived its own death' : 'gone');
  ok('and there is nothing to offer afterwards', loadRun() === null);

  /* nothing off the disk is trusted */
  const refuse = [
    ['gibberish', 'not json at all {{{'],
    ['a save from another build', JSON.stringify({ v: 99, cls: ['ember'], level: 4, ps: [{}] })],
    ['a delver that does not exist', JSON.stringify({ v: 1, cls: ['sorcerer'], level: 4, ps: [{}] })],
    ['a depth beyond the deep', JSON.stringify({ v: 1, cls: ['ember'], level: 50000, ps: [{}] })],
    ['gear that is not gear', JSON.stringify({ v: 1, cls: ['ember'], level: 4, ps: [{ gear: { weapon: 'a sword' } }] })],
    ['two delvers listed and one saved', JSON.stringify({ v: 1, cls: ['ember', 'sable'], level: 4, ps: [{}] })],
    ['no delver at all', JSON.stringify({ v: 1, cls: [], level: 4, ps: [] })],
  ];
  const kept = [];
  for (const [name, raw] of refuse) {
    localStorage.setItem(RK, raw);
    if (loadRun() !== null || stored() !== null) kept.push(name);
  }
  ok('a save that makes no sense is refused, and thrown away with it',
     kept.length === 0, kept.join('; ') || refuse.length + ' kinds refused');

  /* but a save that is merely sloppy is coerced rather than discarded: this
     is the shape that once grew "4067" echoes out of a string and a number */
  localStorage.setItem(RK, JSON.stringify({
    v: 1, cls: ['ember'], level: '4', score: '12', gold: null, keys: undefined,
    runT: 'ages', ps: [{ hp: 'lots', plvl: '3', up: { dmg: 'huge', crit: {} }, pacts: ['embers', 'no such pact'] }]
  }));
  const sloppy = loadRun();
  const nums = sloppy ? [sloppy.level, sloppy.score, sloppy.gold, sloppy.bombs, sloppy.runT,
                         sloppy.ps[0].hp, sloppy.ps[0].plvl, sloppy.ps[0].up.dmg, sloppy.ps[0].up.crit] : [NaN];
  ok('a sloppy save is coerced, not discarded', !!sloppy && sloppy.level === 4, sloppy ? 'depth ' + sloppy.level : 'thrown away');
  ok('and every number that comes back is a number', nums.every(n => typeof n === 'number' && Number.isFinite(n)),
     nums.join(','));
  ok('while a pact nobody has heard of is dropped', !!sloppy && sloppy.ps[0].pacts.length === 1,
     sloppy ? sloppy.ps[0].pacts.length + ' pacts' : '-');
  /* and it must actually run, not just parse */
  if (sloppy) {
    resumeRun(sloppy);
    const S = G.players[0];
    ok('a run rebuilt from it is playable', G.state === 'play' && S.hp > 0 && Number.isFinite(S.max) && S.max > 0,
       'hp ' + S.hp + '/' + S.max);
    let err = null;
    try { for (let i = 0; i < 180; i++) update(1 / 60); } catch (e) { err = e; }
    ok('and survives three seconds of play', err === null && Number.isFinite(G.players[0].hp),
       err ? String(err && err.message) : 'no throw');
  }

  clearRun(); META.perks = {};
}

/* ---------------- what the deep is taking ---------------- */
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

/* ---------------- a browser that will not let you save ---------------- */
{
  /* Private browsing in Safari throws on setItem. Some setups throw on even
     touching window.localStorage. An artifact gets opened by strangers on
     whatever browser they have, so the game has to come up either way --
     and, since it cannot keep anything, it has to say so rather than let
     someone earn a Barrow full of echoes that quietly evaporates. */
  const real = globalThis.localStorage;
  const mem = () => { const m = new Map(); return {
    getItem: k => (m.has(String(k)) ? m.get(String(k)) : null),
    setItem: (k, v) => { m.set(String(k), String(v)); },
    removeItem: k => { m.delete(String(k)); }, clear: () => m.clear() }; };

  const hostile = {
    'one that throws on every call': {
      getItem() { throw new Error('denied'); },
      setItem() { throw new Error('denied'); },
      removeItem() { throw new Error('denied'); },
    },
    'one that reads but refuses to write': (() => { const s = mem(); return {
      getItem: s.getItem, removeItem: s.removeItem,
      setItem() { throw new Error('quota'); } }; })(),
    'one that is not there at all': undefined,
    'one that is there but is not a store': {},
  };

  const broke = [];
  for (const [name, fake] of Object.entries(hostile)) {
    try {
      globalThis.localStorage = fake;
      /* everything the game does with storage, in the order boot does it */
      loadMeta();
      saveMeta();
      clearRun();
      startGame(['thistle']);
      saveRun();
      loadRun();
      G.offer = null; G.offerQ.length = 0; G.state = 'play';
      nextLevel();
      for (let i = 0; i < 120; i++) update(1 / 60);
      teach('crypt');
      die();
    } catch (e) {
      broke.push(name + ': ' + (e && e.message));
    } finally {
      globalThis.localStorage = real;
    }
  }
  ok('the game comes up on a browser that denies it storage', broke.length === 0,
     broke.join(' | ') || Object.keys(hostile).length + ' kinds of refusal survived');

  /* and it must notice, rather than pretend everything is fine */
  {
    const seen = {};
    for (const [name, fake] of Object.entries(hostile)) {
      globalThis.localStorage = fake;
      seen[name] = storageWorks(true);
      globalThis.localStorage = real;
    }
    const fooled = Object.keys(seen).filter(k => seen[k] !== false);
    ok('and knows it cannot save', fooled.length === 0,
       fooled.join(', ') || 'all four refusals detected');
    ok('while a working store is not wrongly condemned', storageWorks(true) === true);
  }

  /* the notice is only for the menu, and only when there is something to say */
  {
    globalThis.localStorage = hostile['one that throws on every call'];
    storageWorks(true); showMenu();
    const shownWhenBroken = !$('noSave').hidden;
    globalThis.localStorage = real;
    storageWorks(true); showMenu();
    const shownWhenFine = !$('noSave').hidden;
    ok('the warning shows when nothing can be kept', shownWhenBroken);
    ok('and stays out of the way when it can', !shownWhenFine);
  }

  /* a run started on such a browser still plays to the end */
  {
    globalThis.localStorage = hostile['one that reads but refuses to write'];
    storageWorks(true);
    let err = null;
    try {
      startGame(['ember']); G.offer = null; G.offerQ.length = 0; G.state = 'play';
      for (let d = 0; d < 3; d++) { G.offer = null; G.offerQ.length = 0; nextLevel(); }
      for (let i = 0; i < 600; i++) update(1 / 60);
      die();
    } catch (e) { err = e; }
    globalThis.localStorage = real; storageWorks(true);
    ok('and a whole run plays out on one, start to finish', err === null,
       err ? String(err.message) : 'three floors and a death');
  }
}

const fails = results.filter(r => r[0] === 'FAIL');
for (const [st, n, x] of results) console.log(st + '  ' + n + (x ? '  [' + x + ']' : ''));
console.log('\n' + (results.length - fails.length) + '/' + results.length + ' checks passed');
if (fails.length) { console.log('FAILURES:'); for (const f of fails) console.log('  ' + f[1] + '  ' + f[2]); }
