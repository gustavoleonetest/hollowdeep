/* Headless balance sweep.
   A scripted player that fights, feeds, loots and descends, so we can ask where
   the difficulty curve actually breaks instead of guessing. */

/* cosmetics cost most of the frame and change nothing about balance */
burst = () => {}; burstDir = () => {}; coinSpray = () => {}; text = () => {};
sfx = () => {}; announce = () => {}; announceOnce = () => {};

const SKILL = { cautious: { flee: .45, food: .72, bomb: .3, kite: 1 }, brave: { flee: .22, food: .5, bomb: .16, kite: 0 } };

let aiF = null, aiGoalI = -1, aiAt = -1;
function aiStep(P, gx, gy) {
  const gi = Math.floor(gy / T) * MW + Math.floor(gx / T);
  if (gi < 0 || gi >= MW * MH) return null;
  if (!aiF || aiGoalI !== gi || clock - aiAt > .45) {
    aiGoalI = gi; aiAt = clock;
    aiF = new Int16Array(MW * MH).fill(-1);
    if (G.map[gi] === 1) return null;
    aiF[gi] = 0; const q = [gi];
    for (let h = 0; h < q.length; h++) {
      const c = q[h], cx = c % MW, cy = (c / MW) | 0, d = aiF[c];
      if (d > 140) continue;
      for (const dd of DIRS) {
        const nx = cx + dd[0], ny = cy + dd[1];
        if (nx < 0 || ny < 0 || nx >= MW || ny >= MH) continue;
        const ni = ny * MW + nx;
        if (aiF[ni] >= 0 || G.map[ni] === 1) continue;
        aiF[ni] = d + 1; q.push(ni);
      }
    }
  }
  const px = Math.floor(P.x / T), py = Math.floor(P.y / T), pi = py * MW + px;
  if (pi < 0 || pi >= MW * MH || aiF[pi] < 0) return null;
  let best = aiF[pi], bx = null;
  for (const dd of DIRS) {
    const nx = px + dd[0], ny = py + dd[1];
    if (nx < 0 || ny < 0 || nx >= MW || ny >= MH) continue;
    const v = aiF[ny * MW + nx];
    if (v >= 0 && v < best) { best = v; bx = [nx, ny]; }
  }
  if (!bx) return { x: gx - P.x, y: gy - P.y };
  return { x: (bx[0] + .5) * T - P.x, y: (bx[1] + .5) * T - P.y };
}

function aiTick(sk) {
  const P = G.players[0], I = INS[0];
  I.mx = I.my = 0; I.fire = false; I.dash = false; I.sp = false; I.bomb = false;
  if (P.down) return;
  const hpf = P.hp / P.max;
  const near = [];
  for (const e of G.enemies) if (e.hp > 0) { const d = Math.hypot(e.x - P.x, e.y - P.y); if (d < 190) near.push(d); }
  const crowd = near.length, closest = near.length ? Math.min(...near) : 1e9;

  /* what are we going for */
  let goal = null, shoot = null, bd = 1e9, goalKind = 'walk';
  const pick = (o, w, kind) => { const d = Math.hypot(o.x - P.x, o.y - P.y) * w; if (d < bd) { bd = d; goal = o; goalKind = kind; } };

  /* crypts are the objective, not the monsters they pour out; once the key is
     in hand and the spawners are down, leave rather than farm forever */
  const boss = G.enemies.find(e => e.boss && e.hp > 0);
  /* floor is done: leave, rather than wander it forever */
  const keyOut = G.items.some(i => i.kind === 'key');
  const cleared = G.nests.length === 0 && !boss && (G.keys > 0 || !keyOut);
  if (cleared && hpf > .5) { goal = G.exit; goalKind = 'walk'; }
  if (!goal && hpf < sk.food) for (const it of G.items) if (it.kind === 'food') pick(it, .5, 'item');
  if (!goal) for (const it of G.items) if (it.kind === 'key') pick(it, .5, 'item');
  if (!goal) for (const it of G.items) if (it.kind === 'chest' || it.kind === 'gear' || it.kind === 'bomb') pick(it, .75, 'item');
  if (!goal) for (const n of G.nests) if (n.hp > 0) pick(n, .8, 'fight');
  if (!goal && boss) { goal = boss; goalKind = 'fight'; }
  if (!goal && G.keys > 0) { goal = G.exit; goalKind = 'walk'; }
  if (!goal) for (const e of G.enemies) if (e.hp > 0 && !e.immune && Math.hypot(e.x - P.x, e.y - P.y) < 320) pick(e, 1, 'fight');
  if (!goal) for (const it of G.items) if (it.kind === 'gold' || it.kind === 'gem') pick(it, 1, 'item');
  if (!goal) { goal = G.exit; goalKind = 'walk'; }

  /* aim at whatever is actually threatening us */
  bd = 1e9;
  for (const e of G.enemies) if (e.hp > 0 && !e.immune) { const d = Math.hypot(e.x - P.x, e.y - P.y); if (d < bd) { bd = d; shoot = e; } }
  for (const n of G.nests) if (n.hp > 0) { const d = Math.hypot(n.x - P.x, n.y - P.y); if (d < bd) { bd = d; shoot = n; } }
  if (shoot) {
    I.aim = Math.atan2(shoot.y - P.y, shoot.x - P.x);
    const rng = P.cls.atk === 'melee' ? (P.cls.range + 6) : 330;
    I.fire = bd < rng;
  }

  /* panic buttons */
  if (hpf < sk.bomb && crowd >= 5 && G.bombs > 0) I.bomb = true;
  if (P.spCd <= 0 && (crowd >= 3 || (shoot && shoot.boss))) I.sp = true;

  /* retreat when badly hurt and something is on us */
  const fleeing = hpf < (boss ? sk.flee * .6 : sk.flee) && closest < 90;
  let v = null;
  if (fleeing) {
    let ax = 0, ay = 0;
    for (const e of G.enemies) if (e.hp > 0) { const dx = P.x - e.x, dy = P.y - e.y, d = Math.hypot(dx, dy) || 1; if (d < 150) { ax += dx / d; ay += dy / d; } }
    v = { x: ax, y: ay };
    if (P.dashCd <= 0) I.dash = true;
  } else if (sk.kite && P.cls.atk !== 'melee' && closest < 70) {
    const e = G.enemies.find(q => q.hp > 0 && Math.hypot(q.x - P.x, q.y - P.y) < 70);
    if (e) v = { x: P.x - e.x, y: P.y - e.y };
  }
  if (!v && goal) {
    const want = Math.hypot(goal.x - P.x, goal.y - P.y);
    /* you walk onto loot and stairs; you stop short only of things you are hitting */
    /* a melee delver that walks right onto a foe oscillates and wedges, so
       hold at the outer edge of its own reach instead */
    const stopAt = goalKind === 'fight'
      ? (P.cls.atk === 'melee' ? Math.max(20, (P.cls.range || 62) * .72) : 150) : 0;
    if (want > stopAt) v = aiStep(P, goal.x, goal.y) || { x: goal.x - P.x, y: goal.y - P.y };
  }
  if (v) { const L = Math.hypot(v.x, v.y) || 1; I.mx = v.x / L; I.my = v.y / L; }

  /* a real player never stands grinding against a corner; shake loose */
  const a = P._ai || (P._ai = { lx: P.x, ly: P.y, stuck: 0, jig: 0, jx: 0, jy: 0 });
  const movedPx = Math.hypot(P.x - a.lx, P.y - a.ly);
  a.lx = P.x; a.ly = P.y;
  if (movedPx < .3 && (I.mx || I.my)) a.stuck += 1 / 60; else a.stuck = 0;
  if (a.stuck > .5 && a.jig <= 0) { a.jig = .55; const an = Math.random() * TAU; a.jx = Math.cos(an); a.jy = Math.sin(an); a.stuck = 0; }
  if (a.jig > 0) { a.jig -= 1 / 60; I.mx = a.jx; I.my = a.jy; if (P.dashCd <= 0 && Math.random() < .04) I.dash = true; }
}

/* --- choices --- */
const UP_W = { vit: 1.0, power: 1.3, haste: 1.12, crit: 1.05, ward: .95, swift: .72, dash: .4, master: 1.2 };
function scoreItem(it) {
  const s = it.s || {};
  return (s.dmg || 0) * 100 + (s.crit || 0) * 190 + (s.arm || 0) * 150 + (s.hp || 0) * .75 + (s.spd || 0) * 60
    - (s.cd || 0) * 115 + (s.leech || 0) * 220 + (s.thorns || 0) * 18 + (s.gold || 0) * 12
    - (s.drain || 0) * 130 - (s.dash || 0) * 18 + (s.elem ? 28 : 0);
}
function aiOffer() {
  const o = G.offer; if (!o) return;
  if (o.kind === 'gear') {
    const cur = o.cur ? scoreItem(o.cur) : -1e9;
    applyUpgrade(scoreItem(o.item) > cur ? 0 : 1);
  } else if (o.kind === 'pact') {
    const sh = o.shrine.sh;
    /* take anything free; weigh a bargain by how much health is already going */
    const free = !isPact(sh.pact) && sh.kind !== 'mystery';
    const P = G.players[0], hpf = P.hp / P.max;
    const take = free || (sh.kind === 'mystery' ? Math.random() < .5 : hpf > .45 && Math.random() < .6);
    applyUpgrade(take ? 0 : 1);
  } else if (o.kind === 'boon') {
    applyUpgrade(Math.floor(Math.random() * o.opts.length));
  } else {
    let bi = 0, bs = -1e9;
    o.opts.forEach((u, i) => { const s = (UP_W[u.id] || .5) * u.m; if (s > bs) { bs = s; bi = i; } });
    applyUpgrade(bi);
  }
}
function aiShop() {
  const P = G.players[0];
  for (let guard = 0; guard < 40; guard++) {
    let did = false;
    if (P.hp < P.max * .7) { const d = SHOP.find(s => s.id === 'draught'); if (d && shopState(P, d) === 'ok') { shopBuy(P, 'draught'); did = true; } }
    if (!did) {
      /* best wares piece if it clearly beats what we wear */
      let wi = -1, wb = 0;
      G.wares.forEach((w, i) => { if (w.sold || G.gold < w.price) return; const cur = P.gear[w.slot] ? scoreItem(P.gear[w.slot]) : 0; const gain = scoreItem(w) - cur; if (gain > wb) { wb = gain; wi = i; } });
      if (wi >= 0 && wb > 25) { buyWare(P, wi); did = true; }
    }
    if (!did) {
      let bid = null, bs = -1e9;
      for (const it of SHOP) {
        if (it.id === 'draught' || it.id === 'elixir') continue;
        if (shopState(P, it) !== 'ok') continue;
        const s = (UP_W[it.id] || .5) / Math.max(1, shopPrice(P, it) / 100);
        if (s > bs) { bs = s; bid = it.id; }
      }
      if (bid) { shopBuy(P, bid); did = true; }
    }
    if (!did) break;
  }
}

/* --- one run --- */
function playRun(cls, skillName, capSec) {
  const sk = SKILL[skillName];
  startGame([cls]);
  const P = G.players[0];
  const rec = { cls, skill: skillName, depth: 1, t: 0, drain: 0, dmg: 0, kills: 0, gold: 0, plvl: 1, cause: 'timeout', deepest: 1, boons: [], pacts: [] };
  let guard = 0, stuck = 0, lastDepth = 1, lastDepthT = 0;
  const dt = 1 / 60;
  while (guard++ < capSec * 60) {
    if (G.state === 'dead') { rec.cause = rec.drain > rec.dmg ? 'drain' : 'damage'; break; }
    if (G.level > 26) { rec.cause = 'survived'; break; }
    if (G.state === 'offer') { aiOffer(); continue; }
    if (G.state === 'clear') { clearTick(dt); rec.t += dt; continue; }
    if (G.state === 'shop') { aiShop(); leaveShop(); continue; }
    if (G.state !== 'play') break;
    const before = P.hp;
    aiTick(sk);
    const dr = P.down ? 0 : (.8 + G.level * .2) * (P.drainMul || 1) * dt;
    update(dt);
    rec.t += dt;
    const lost = before - P.hp;
    if (lost > 0) { const d = Math.min(lost, dr); rec.drain += d; rec.dmg += lost - d; }
    if (G.level !== lastDepth) { lastDepth = G.level; lastDepthT = rec.t; stuck = 0; }
    else if (rec.t - lastDepthT > (isBossLvl(G.level) ? 260 : 170)) {
      rec.cause = 'stalled';
      const keyItem = G.items.some(i => i.kind === 'key');
      rec.why = 'd' + G.level + ' keys=' + G.keys + ' keyItem=' + (keyItem ? 'y' : 'n') + ' crypts=' + G.nests.length +
        ' foes=' + G.enemies.length + ' exitDist=' + Math.round(Math.hypot(P.x - G.exit.x, P.y - G.exit.y));
      break;
    }
    rec.deepest = Math.max(rec.deepest, G.level);
  }
  rec.depth = G.level; rec.kills = G.kills || 0; rec.gold = G.gold; rec.plvl = P.plvl;
  rec.hpEnd = Math.max(0, P.hp); rec.maxHp = P.max; rec.dmgMul = +P.dmgMul.toFixed(2);
  rec.gear = SLOTS.map(s => P.gear[s]).filter(Boolean).length;
  rec.boons = (BOONS[P.cls.key] || []).filter(b => bn(P, b.id)).map(b => b.id);
  rec.pacts = (P.pacts || []).map(p => p.id);
  return rec;
}

/* --- sweep --- */
const CLASSES_L = ['bulwark', 'ember', 'sable', 'thistle'];
const N = +(process.env.SIM_N || 12), CAP = +(process.env.SIM_CAP || 420);
const runs = [];
const t0 = Date.now();
for (const sk of ['cautious', 'brave']) for (const c of CLASSES_L) for (let i = 0; i < N; i++) runs.push(playRun(c, sk, CAP));
const secs = ((Date.now() - t0) / 1000).toFixed(1);

const pct = (a, p) => { const v = a.slice().sort((x, y) => x - y); return v.length ? v[Math.min(v.length - 1, Math.floor(v.length * p))] : 0; };
const avg = a => a.length ? a.reduce((x, y) => x + y, 0) / a.length : 0;
console.log('runs ' + runs.length + ' in ' + secs + 's');
console.log('\n-- how deep by class --');
for (const c of CLASSES_L) {
  const r = runs.filter(x => x.cls === c), d = r.map(x => x.deepest);
  console.log(c.padEnd(9) + ' median ' + String(pct(d, .5)).padStart(3) + '   mean ' + avg(d).toFixed(1).padStart(5) + '   p90 ' + String(pct(d, .9)).padStart(3) + '   best ' + String(Math.max(...d)).padStart(3));
}
console.log('\n-- how deep by caution --');
for (const s of ['cautious', 'brave']) {
  const r = runs.filter(x => x.skill === s), d = r.map(x => x.deepest);
  console.log(s.padEnd(9) + ' median ' + String(pct(d, .5)).padStart(3) + '   mean ' + avg(d).toFixed(1).padStart(5));
}
console.log('\n-- what kills you --');
const causes = {};
for (const r of runs) causes[r.cause] = (causes[r.cause] || 0) + 1;
for (const k in causes) console.log(k.padEnd(9) + ' ' + causes[k] + '  (' + (causes[k] / runs.length * 100).toFixed(0) + '%)');
const st = runs.filter(r => r.cause === 'stalled');
if (st.length) console.log('stall reasons: ' + st.slice(0, 5).map(r => r.why).join(' | '));
const died = runs.filter(r => r.cause === 'drain' || r.cause === 'damage');
if (died.length) console.log('of deaths: drain ' + (died.filter(r => r.cause === 'drain').length / died.length * 100).toFixed(0) + '%  damage ' + (died.filter(r => r.cause === 'damage').length / died.length * 100).toFixed(0) + '%');

console.log('\n-- survival by depth (share of runs reaching it) --');
const maxD = Math.max(...runs.map(r => r.deepest));
for (let d = 1; d <= Math.min(maxD, 24); d++) {
  const n = runs.filter(r => r.deepest >= d).length, share = n / runs.length;
  if (share < .02 && d > 3) break;
  console.log('depth ' + String(d).padStart(2) + '  ' + String(n).padStart(3) + '/' + runs.length + '  ' + '#'.repeat(Math.round(share * 40)) + ' ' + (share * 100).toFixed(0) + '%');
}
console.log('\n-- per-depth attrition (of those who got there, how many got one deeper) --');
for (let d = 1; d <= Math.min(maxD, 20); d++) {
  const at = runs.filter(r => r.deepest >= d).length, on = runs.filter(r => r.deepest >= d + 1).length;
  if (at < 4) break;
  console.log('depth ' + String(d).padStart(2) + '  ' + (on / at * 100).toFixed(0) + '% went deeper   (' + at + ' -> ' + on + ')');
}
console.log('\n-- averages at the end --');
console.log('time alive ' + (avg(runs.map(r => r.t)) / 60).toFixed(1) + ' min   level ' + avg(runs.map(r => r.plvl)).toFixed(1) +
  '   kills ' + avg(runs.map(r => r.kills)).toFixed(0) + '   gear worn ' + avg(runs.map(r => r.gear)).toFixed(1) +
  '   damage mult ' + avg(runs.map(r => r.dmgMul)).toFixed(2));
console.log('drain share of all HP lost ' + (avg(runs.map(r => r.drain)) / Math.max(.001, avg(runs.map(r => r.drain)) + avg(runs.map(r => r.dmg))) * 100).toFixed(0) + '%');

console.log('\n-- how each run ended, by class --');
for (const cls of CLASSES_L) {
  const r = runs.filter(x => x.cls === cls), c = {};
  for (const x of r) c[x.cause] = (c[x.cause] || 0) + 1;
  const parts = ['stalled','timeout','drain','damage','survived'].filter(k => c[k]).map(k => k + ' ' + c[k]);
  console.log(cls.padEnd(9) + ' ' + parts.join('  ') + '   | reached depth ' + avg(r.map(x => x.deepest)).toFixed(1) +
    '  killed ' + avg(r.map(x => x.kills)).toFixed(0) + '  lived ' + (avg(r.map(x => x.t)) / 60).toFixed(1) + 'min');
}
console.log('\n-- build variety: boons actually learned --');
const btot = {};
for (const r of runs) for (const b of r.boons) btot[b] = (btot[b] || 0) + 1;
for (const cls of CLASSES_L) {
  const r = runs.filter(x => x.cls === cls);
  const names = (BOONS[cls] || []).map(b => b.id + ' ' + r.filter(x => x.boons.includes(b.id)).length);
  console.log(cls.padEnd(9) + ' avg ' + avg(r.map(x => x.boons.length)).toFixed(1) + ' learned   ' + names.join('  '));
}
console.log('runs that learned none: ' + runs.filter(r => !r.boons.length).length + '/' + runs.length);
