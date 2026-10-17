from patch import edit, run

L = 'part_logic.js'

# --- poison ticks alongside burn, and chill wears off ----------------------
edit(L, """    if (e.burn > 0 && !e.dead) {
      e.burn -= dt; e.burnT -= dt;""",
     """    if (e.chill > 0) {
      e.chill -= dt;
      if (Math.random() < .25) G.parts.push({ x: e.x + rnd(-7, 7), y: e.y + rnd(-8, 4), vx: 0, vy: -.18, life: .45, max: .45, col: '#bfe6ff', s: 1.8 });
    }
    if (e.pois > 0 && !e.dead) {
      e.pois -= dt; e.poisT -= dt;
      if (Math.random() < .4) G.parts.push({ x: e.x + rnd(-7, 7), y: e.y + rnd(-8, 3), vx: rnd(-.1, .1), vy: -.3, life: .5, max: .5, col: '#9bd16a', s: 2 });
      if (e.poisT <= 0) {
        e.poisT = .5; e.hp -= e.poisDmg; text(e.x + rnd(-7, 7), e.y - e.r - 2, String(Math.round(e.poisDmg)), '#9bd16a', 11);
        if (e.hp <= 0) { finishFoe(e); continue; }
      }
    }
    if (e.burn > 0 && !e.dead) {
      e.burn -= dt; e.burnT -= dt;""")

# --- the thief robs you and runs; Death cannot be fought, only outrun ------
edit(L, """    if (e.root > 0) { e.root -= dt; tx = 0; ty = 0;""",
     """    if (e.type === 'thief') {
      if (e.loot > 0) {
        e.flee -= dt;
        const ax2 = (e.x - P.x) / (Math.hypot(e.x - P.x, e.y - P.y) || 1), ay2 = (e.y - P.y) / (Math.hypot(e.x - P.x, e.y - P.y) || 1);
        tx = ax2 * e.spd * 1.4; ty = ay2 * e.spd * 1.4;
        if (Math.random() < .3) G.parts.push({ x: e.x, y: e.y, vx: 0, vy: -.3, life: .4, max: .4, col: '#f0a23c', s: 2 });
        if (e.flee <= 0) {
          burst(e.x, e.y, '#3a4152', 14, 90, 1.3, 'smoke'); burst(e.x, e.y, '#c9a24a', 8, 110, .8, 'spark');
          announceOnce('robbed', 3, 'The thief escaped with your gold', '#c9a24a');
          e.hp = 0; e.gone = 1; continue;
        }
      } else if (e.alert) { tx *= 1.15; ty *= 1.15; }
    }
    if (e.type === 'reaper') {
      e.alert = true;
      for (const p of alive) {
        if (Math.hypot(p.x - e.x, p.y - e.y) >= e.r + p.r + 6) continue;
        const bite = (22 + G.level * 2) * dt;
        p.hp -= bite; e.fed = (e.fed || 0) + bite; p.hurt = Math.max(p.hurt, .12);
        if (Math.random() < .5) G.parts.push({ x: p.x + rnd(-8, 8), y: p.y + rnd(-8, 4), vx: (e.x - p.x) * .02, vy: (e.y - p.y) * .02, life: .45, max: .45, col: '#dfe4ef', s: 2.4 });
        announceOnce('death', 6, p.cls.name + ' is being devoured', '#dfe4ef');
        if (p.hp <= 0) downPlayer(p);
      }
      if ((e.fed || 0) > 70 + G.level * 12) {
        burst(e.x, e.y, '#dfe4ef', 26, 150, 1.4, 'smoke'); burst(e.x, e.y, '#ffffff', 14, 190, .9, 'spark');
        announceOnce('deathgone', 4, 'Death departs, sated', '#dfe4ef');
        e.hp = 0; e.gone = 1; continue;
      }
    }
    if (e.chill > 0) { tx *= .5; ty *= .5; }
    if (e.root > 0) { e.root -= dt; tx = 0; ty = 0;""")

# --- contact: the thief takes gold instead of blood ------------------------
edit(L, """    for (const p of alive) { const dd = Math.hypot(p.x - e.x, p.y - e.y); if (dd < e.r + p.r + 7 && e.atk <= -.25) e.atk = .3; if (dd < e.r + p.r) hurtPlayer(p, e.dmg, Math.atan2(p.y - e.y, p.x - e.x)); }""",
     """    for (const p of alive) {
      const dd = Math.hypot(p.x - e.x, p.y - e.y);
      if (dd < e.r + p.r + 7 && e.atk <= -.25 && e.dmg > 0) e.atk = .3;
      if (dd >= e.r + p.r) continue;
      if (e.type === 'thief') {
        if (e.loot <= 0 && G.gold > 0) {
          e.loot = Math.max(20, Math.round(G.gold * .4)); e.loot = Math.min(e.loot, G.gold); G.gold -= e.loot;
          e.flee = 9; e.alert = true; sfx('coin'); G.shake = Math.max(G.shake, .25);
          text(p.x, p.y - 22, '-' + e.loot + ' gold', '#c9a24a', 15);
          announce(p.cls.name + ' has been robbed!', '#c9a24a');
          burst(e.x, e.y, '#f0a23c', 14, 130, .9, 'spark');
        }
        continue;
      }
      if (e.dmg > 0) hurtPlayer(p, e.dmg, Math.atan2(p.y - e.y, p.x - e.x), e);
    }""")

# --- a thief that dies gives the gold back ---------------------------------
edit(L, """  if (e.elite) {
    coinSpray(e.x, e.y, 10);""",
     """  if (e.type === 'thief' && e.loot > 0) {
    coinSpray(e.x, e.y, 14); announceOnce('recovered', 2, 'The thief drops its purse', '#f0a23c');
    for (let i = 0; i < Math.min(8, 1 + Math.round(e.loot / 25)); i++) G.items.push({ kind: 'gold', x: e.x + rnd(-20, 20), y: e.y + rnd(-16, 16), t: 0, v: Math.round(e.loot / Math.min(8, 1 + Math.round(e.loot / 25))) });
  }
  if (e.elite) {
    coinSpray(e.x, e.y, 10);""")

# --- Gauntlet's clock: health bleeds away, so food is the real timer -------
edit(L, """  P.aim = I.aim; P.cd -= dt; P.inv -= dt; P.dashCd -= dt; P.hurt = Math.max(0, P.hurt - dt);""",
     """  P.aim = I.aim; P.cd -= dt; P.inv -= dt; P.dashCd -= dt; P.hurt = Math.max(0, P.hurt - dt);
  P.chill = Math.max(0, P.chill - dt);
  if (I.bomb) useBomb(P);
  /* the dungeon itself is draining you; food is the only clock that matters */
  P.hp -= (.8 + G.level * .2) * (G.co ? .85 : 1) * dt;
  const frac = P.hp / P.max;
  if (frac < .12) announceOnce('dying' + P.idx, 9, P.cls.name + ' is about to die!', '#d9534f');
  else if (frac < .34) announceOnce('food' + P.idx, 11, P.cls.name + ' needs food, badly!', '#ffd24a');
  if (P.hp <= 0) { downPlayer(P); return; }""")

edit(L, """  if (P.dash > 0) { P.dash -= dt; vx = P.dx * (P.cls.spd * P.spdMul) * 3.3; vy = P.dy * (P.cls.spd * P.spdMul) * 3.3;""",
     """  const chl = P.chill > 0 ? .62 : 1;
  if (P.dash > 0) { P.dash -= dt; vx = P.dx * (P.cls.spd * P.spdMul) * 3.3; vy = P.dy * (P.cls.spd * P.spdMul) * 3.3;""")

edit(L, """  else { vx = mx * (P.cls.spd * P.spdMul); vy = my * (P.cls.spd * P.spdMul); }""",
     """  else { vx = mx * (P.cls.spd * P.spdMul) * chl; vy = my * (P.cls.spd * P.spdMul) * chl; }""")

# --- potions are Gauntlet's panic button -----------------------------------
edit(L, """const SP_CD = 9;""",
     """function useBomb(P) {
  if (G.bombs <= 0 || G.state !== 'play' || P.down || (P.bombCd || 0) > 0) return;
  G.bombs--; P.bombCd = .6;
  SMITE = true;
  const R = 470, dm = 80 + G.level * 24;
  for (const e of G.enemies.slice()) {
    const d = Math.hypot(e.x - P.x, e.y - P.y); if (d > R) continue;
    hurtFoe(e, dm, Math.atan2(e.y - P.y, e.x - P.x) , true, false, null);
  }
  for (const n of G.nests.slice()) if (Math.hypot(n.x - P.x, n.y - P.y) < R) hurtNest(n, dm * 1.4);
  SMITE = false;
  G.shake = .75; G.flash = .5; sfx('boom'); G.hitstop = Math.max(G.hitstop, .09);
  G.fxs.push({ kind: 'shock', x: P.x, y: P.y, t: 0, r: 300, c1: '240,220,255', c2: '185,140,255' },
              { kind: 'shock', x: P.x, y: P.y, t: -.14, r: 470, c1: '255,255,255', c2: '150,110,220' });
  burst(P.x, P.y, '#b98cff', 36, 240, 1.3, 'spark'); burst(P.x, P.y, '#e8d8ff', 20, 160, 1.5, 'smoke');
  announce(P.cls.name + ' unleashes a potion!', '#b98cff');
}
const SP_CD = 9;""")

run()
