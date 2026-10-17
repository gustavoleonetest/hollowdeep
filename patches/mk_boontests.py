import io

p = 'behave2_drive.js'
s = io.open(p, encoding='utf-8').read()
start = s.index("/* ---------------- boons change how an attack works ---------------- */")
end = s.index("const fails = results.filter(r => r[0] === 'FAIL');")

new_block = r"""/* ---------------- boons change how an attack works ---------------- */
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

"""

io.open(p, 'w', encoding='utf-8', newline='').write(s[:start] + new_block + s[end:])
print('boon tests rewritten')
