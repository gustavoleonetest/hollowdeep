from patch import edit, run

L = 'part_logic.js'

edit(L, """bombs: 0, bolts: [], voice: null, flash: 0, offerQ: [], drops: 0, wares: [], event: null };""",
     """bombs: 0, bolts: [], voice: null, flash: 0, offerQ: [], drops: 0, wares: [], event: null, zones: [], timers: [] };""")

# --- lingering fire pools, and a way to schedule a delayed effect ---------
edit(L, """/* ---------- the arena ----------""",
     """/* a patch of ground that keeps hurting things that stand in it */
function addZone(x, y, r, dmg, life, own) { G.zones.push({ x, y, r, dmg, life, max: life, tick: 0, own }); }
function updateZones(dt) {
  for (let i = G.zones.length - 1; i >= 0; i--) {
    const z = G.zones[i];
    z.life -= dt; z.tick -= dt;
    if (Math.random() < .6 && !reduceMotion) G.parts.push({ x: z.x + rnd(-z.r, z.r), y: z.y + rnd(-z.r * .6, z.r * .6), vx: rnd(-.1, .1), vy: -.5, life: .5, max: .5, col: Math.random() < .5 ? '#ff8a3a' : '#ffd08a', s: 2, k: 'ember' });
    if (z.tick <= 0) {
      z.tick = .35;
      for (const e of G.enemies.slice()) if (e.hp > 0 && !e.dead && Math.hypot(e.x - z.x, e.y - z.y) < z.r + e.r) hurtFoe(e, z.dmg, Math.atan2(e.y - z.y, e.x - z.x), false, true, z.own);
    }
    if (z.life <= 0) G.zones.splice(i, 1);
  }
}
function drawZones() {
  for (const z of G.zones) {
    const q = clamp(z.life / z.max, 0, 1), pu = .6 + .4 * Math.sin(clock * 7 + z.x * .05);
    const g = ctx.createRadialGradient(z.x, z.y, 0, z.x, z.y, z.r);
    g.addColorStop(0, 'rgba(255,190,90,' + .34 * q * pu + ')');
    g.addColorStop(.6, 'rgba(255,110,50,' + .22 * q + ')');
    g.addColorStop(1, 'rgba(255,80,30,0)');
    ctx.fillStyle = g; ctx.beginPath(); ctx.ellipse(z.x, z.y, z.r, z.r * .62, 0, 0, TAU); ctx.fill();
  }
}

/* ---------- the arena ----------""")

edit(L, """  updateRevive(dt); updateEnemies(dt); updateNests(dt); updateShots(dt); updateItems(dt); updateHazards(dt); updateFx(dt);""",
     """  updateRevive(dt); updateEnemies(dt); updateNests(dt); updateShots(dt); updateItems(dt); updateHazards(dt); updateZones(dt); updateFx(dt);""")

edit(L, """  G.bolts = []; G.voice = null; G.flash = 0; G.offer = null; G.offerQ = [];
  G.flowT = 0;""",
     """  G.bolts = []; G.voice = null; G.flash = 0; G.offer = null; G.offerQ = []; G.zones = []; G.timers = [];
  G.flowT = 0;""")

edit(L, """  G.bombs = 1 + perkLv('flask'); G.drops = 0; G.kills = 0; G.runT = 0; G.earned = 0;""",
     """  G.bombs = 1 + perkLv('flask'); G.drops = 0; G.kills = 0; G.runT = 0; G.earned = 0; G.zones = []; G.timers = [];""")

edit(L, """  for (const b of G.bolts) b.t += dt; if (G.bolts.length) G.bolts = G.bolts.filter(b => b.t < .22);""",
     """  for (let i = G.timers.length - 1; i >= 0; i--) { const q = G.timers[i]; q.t -= dt; if (q.t <= 0) { G.timers.splice(i, 1); try { q.fn(); } catch (e) {} } }
  for (const b of G.bolts) b.t += dt; if (G.bolts.length) G.bolts = G.bolts.filter(b => b.t < .22);""")

edit(L, """  drawShots(); drawBolts(); drawFx(); drawFog();""",
     """  drawZones(); drawShots(); drawBolts(); drawFx(); drawFog();""")

# --- Bulwark: cyclone, burning wake, shield bash, riposte ----------------
edit(L, """  const dm = c.dmg * P.dmgMul, rg = (c.range || 0) + 9 * P.mast, arc = Math.min(3.6, (c.arc || 0) + .18 * P.mast);
  const a = P.aim, cr = Math.random() < P.crit;
  if (c.atk === 'melee') {
    sfx('swing'); G.slash = { x: P.x, y: P.y, a, life: .16, kind: 'arc', rad: rg };
    const inArc = (o, rr) => {
      const d = Math.hypot(o.x - P.x, o.y - P.y); if (d > rg + rr) return false;
      let da = Math.atan2(o.y - P.y, o.x - P.x) - a; da = Math.atan2(Math.sin(da), Math.cos(da));
      return Math.abs(da) < arc / 2 || d < rr + P.r + 4;
    };
    for (const e of G.enemies.slice()) if (e.hp > 0 && inArc(e, e.r)) hurtFoe(e, dm, a, cr, false, P);""",
     """  const dm = c.dmg * P.dmgMul, rg = (c.range || 0) + 9 * P.mast + (bn(P, 'cyclone') ? 10 : 0);
  const arc = bn(P, 'cyclone') ? TAU : Math.min(3.6, (c.arc || 0) + .18 * P.mast);
  const a = P.aim;
  let cr = Math.random() < P.crit;
  if (P.nextCrit) { cr = true; P.nextCrit = false; }
  if (c.atk === 'melee') {
    sfx('swing'); G.slash = { x: P.x, y: P.y, a, life: .16, kind: 'arc', rad: rg, full: bn(P, 'cyclone') };
    const inArc = (o, rr) => {
      const d = Math.hypot(o.x - P.x, o.y - P.y); if (d > rg + rr) return false;
      if (arc >= TAU) return true;
      let da = Math.atan2(o.y - P.y, o.x - P.x) - a; da = Math.atan2(Math.sin(da), Math.cos(da));
      return Math.abs(da) < arc / 2 || d < rr + P.r + 4;
    };
    for (const e of G.enemies.slice()) {
      if (e.hp <= 0 || !inArc(e, e.r)) continue;
      const ang2 = Math.atan2(e.y - P.y, e.x - P.x);
      hurtFoe(e, dm, ang2, cr, bn(P, 'wake'), P);
      if (bn(P, 'bash') && !e.dead) { e.kx += Math.cos(ang2) * (e.boss ? 1.2 : 7); e.ky += Math.sin(ang2) * (e.boss ? 1.2 : 7); e.root = Math.max(e.root || 0, e.boss ? .25 : .9); }
    }""")

edit(L, """  P.hp -= d; P.inv = .55; P.hurt = .25; G.shake = Math.max(G.shake, .3);
  if (G.combo > 0) { G.combo = Math.floor(G.combo * .5); if (G.combo <= 0) G.comboT = 0; }""",
     """  P.hp -= d; P.inv = .55; P.hurt = .25; G.shake = Math.max(G.shake, .3);
  if (bn(P, 'riposte')) { P.cd = 0; P.nextCrit = true; burst(P.x, P.y, '#fff1b8', 10, 150, .8, 'spark'); }
  if (G.combo > 0) { G.combo = Math.floor(G.combo * .5); if (G.combo <= 0) G.comboT = 0; }""")

# --- extra projectiles on a volley --------------------------------------
edit(L, """  G.shots.push(mk(a + (c.atk === 'dagger' ? rnd(-.07, .07) : 0)));
  if (c.atk === 'dagger') for (let k = 1; k <= Math.min(3, P.mast); k++) G.shots.push(mk(a + (k % 2 ? 1 : -1) * .2 * Math.ceil(k / 2)));""",
     """  G.shots.push(mk(a + (c.atk === 'dagger' ? rnd(-.07, .07) : 0)));
  if (c.atk === 'dagger') for (let k = 1; k <= Math.min(3, P.mast); k++) G.shots.push(mk(a + (k % 2 ? 1 : -1) * .2 * Math.ceil(k / 2)));
  if (c.atk === 'dagger' && bn(P, 'fan')) { G.shots.push(mk(a - .23)); G.shots.push(mk(a + .23)); }
  if (c.atk === 'arrow' && bn(P, 'volley')) { G.shots.push(mk(a - .17)); G.shots.push(mk(a + .17)); }""")

# --- on-hit boons, ambush, ricochet, barbs -------------------------------
edit(L, """    if (!dead) for (const e of G.enemies) {
      if (e.hp > 0 && !s.hit.has(e) && Math.hypot(e.x - s.x, e.y - s.y) < e.r + s.r) {
        s.hit.add(e); hurtFoe(e, s.dmg, Math.atan2(s.vy, s.vx), s.crit, s.kind === 'fire', s.own);
        if (s.kind === 'fire') { explode(s); dead = true; break; }
        if (s.pierce-- <= 0) { dead = true; break; }
      }
    }""",
     """    if (!dead) for (const e of G.enemies) {
      if (e.hp > 0 && !s.hit.has(e) && Math.hypot(e.x - s.x, e.y - s.y) < e.r + s.r) {
        const O = s.own, unaware = !e.alert;
        s.hit.add(e);
        hurtFoe(e, s.dmg, Math.atan2(s.vy, s.vx), s.crit || (bn(O, 'ambush') && unaware), s.kind === 'fire' || bn(O, 'wake'), O);
        if (!e.dead) {
          if (s.kind === 'dagger' && bn(O, 'venom')) { e.pois = Math.max(e.pois || 0, 2.8); e.poisDmg = Math.max(e.poisDmg || 0, Math.max(1, s.dmg * .3)); }
          if (s.kind === 'arrow' && bn(O, 'frost')) { e.chill = Math.max(e.chill || 0, 1.9); burst(e.x, e.y, '#8fd3ff', 3, 70, .6, 'spark'); }
          if (bn(O, 'mark')) e.mark = 4;
        }
        if (s.kind === 'fire') { explode(s); dead = true; break; }
        if (s.kind === 'arrow' && bn(O, 'barbs')) s.dmg *= 1.35;
        /* a ricochet leaps on instead of stopping */
        if (s.kind === 'dagger' && bn(O, 'ric') && (s.bounce || 0) < 2) {
          let b = null, bd2 = 1e9;
          for (const o2 of G.enemies) {
            if (o2.hp <= 0 || o2.dead || s.hit.has(o2)) continue;
            const d2 = Math.hypot(o2.x - s.x, o2.y - s.y);
            if (d2 < bd2 && d2 < 190) { bd2 = d2; b = o2; }
          }
          if (b) {
            s.bounce = (s.bounce || 0) + 1; s.life = Math.max(s.life, .5);
            const sp = Math.hypot(s.vx, s.vy) || 9, an2 = Math.atan2(b.y - s.y, b.x - s.x);
            s.vx = Math.cos(an2) * sp; s.vy = Math.sin(an2) * sp;
            G.bolts.push({ x1: e.x, y1: e.y, x2: b.x, y2: b.y, t: .1 });
            break;
          }
        }
        if (s.pierce-- <= 0) { dead = true; break; }
      }
    }""")

# --- Ember: seeking, splinter, pyre, kindling ----------------------------
edit(L, """    const s = G.shots[i]; s.x += s.vx * k; s.y += s.vy * k; s.life -= dt;""",
     """    const s = G.shots[i];
    if (s.kind === 'fire' && bn(s.own, 'seek')) {
      let b = null, bd2 = 1e9;
      for (const e of G.enemies) { if (e.hp <= 0 || e.dead || s.hit.has(e)) continue; const d2 = Math.hypot(e.x - s.x, e.y - s.y); if (d2 < bd2 && d2 < 230) { bd2 = d2; b = e; } }
      if (b) {
        const cur = Math.atan2(s.vy, s.vx), want = Math.atan2(b.y - s.y, b.x - s.x), sp = Math.hypot(s.vx, s.vy);
        let da = want - cur; da = Math.atan2(Math.sin(da), Math.cos(da));
        const na = cur + clamp(da, -.09, .09) * k;
        s.vx = Math.cos(na) * sp; s.vy = Math.sin(na) * sp;
      }
    }
    s.x += s.vx * k; s.y += s.vy * k; s.life -= dt;""")

edit(L, """  G.slash = { x: s.x, y: s.y, a: 0, life: .22, kind: 'boom', rad: s.rad };
  scorch(s.x, s.y, Math.max(14, s.rad * .55), '#2a1c14', 'scorch');""",
     """  G.slash = { x: s.x, y: s.y, a: 0, life: .22, kind: 'boom', rad: s.rad };
  scorch(s.x, s.y, Math.max(14, s.rad * .55), '#2a1c14', 'scorch');
  if (bn(s.own, 'pyre')) addZone(s.x, s.y, Math.max(26, s.rad * .72), Math.max(2, s.dmg * .16), 4, s.own);
  if (bn(s.own, 'split') && !s.isSplit) {
    for (let i = 0; i < 3; i++) {
      const an = rnd(0, TAU);
      G.shots.push({ x: s.x, y: s.y, vx: Math.cos(an) * 5.5, vy: Math.sin(an) * 5.5, dmg: s.dmg * .45, life: .5, r: 5, kind: 'fire', col: '#ff8a3a', pierce: 0, rad: Math.max(22, (s.rad || 40) * .55), hit: new Set(), trail: [], crit: false, own: s.own, isSplit: 1 });
    }
  }""")

edit(L, """  if (burn) { e.burn = Math.max(e.burn || 0, 2.4); e.burnDmg = Math.max(e.burnDmg || 0, Math.max(2, dmg * .16)); }""",
     """  if (burn) { e.burn = Math.max(e.burn || 0, 2.4); e.burnDmg = Math.max(e.burnDmg || 0, Math.max(2, dmg * .16)); if (bn(src, 'kindle')) e.kindled = 1; }
  if (e.mark > 0) dmg = Math.round(dmg * 1.25);""")

edit(L, """    if (e.chill > 0) {
      e.chill -= dt;""",
     """    if (e.mark > 0) {
      e.mark -= dt;
      if (Math.random() < .2) G.parts.push({ x: e.x + rnd(-8, 8), y: e.y - e.r - rnd(2, 10), vx: 0, vy: -.2, life: .4, max: .4, col: '#9bd16a', s: 1.6 });
    }
    if (e.chill > 0) {
      e.chill -= dt;""")

edit(L, """  if (e.type === 'thief' && e.loot > 0) {
    coinSpray(e.x, e.y, 14); announceOnce('recovered', 2, 'The thief drops its purse', '#f0a23c');""",
     """  if (e.kindled && e.burn > 0) {
    const R = 76, dm2 = Math.max(8, (e.burnDmg || 4) * 7);
    G.fxs.push({ kind: 'shock', x: e.x, y: e.y, t: 0, r: R + 18, c1: '255,240,200', c2: '255,120,50' });
    G.slash = { x: e.x, y: e.y, a: 0, life: .22, kind: 'boom', rad: R };
    burst(e.x, e.y, '#ff8a3a', 20, 170, 1.2, 'ember'); G.shake = Math.max(G.shake, .24); sfx('boom');
    for (const o of G.enemies.slice()) if (o !== e && !o.dead && o.hp > 0 && Math.hypot(o.x - e.x, o.y - e.y) < R + o.r) hurtFoe(o, dm2, Math.atan2(o.y - e.y, o.x - e.x), false, true, null);
  }
  if (e.type === 'thief' && e.loot > 0) {
    coinSpray(e.x, e.y, 14); announceOnce('recovered', 2, 'The thief drops its purse', '#f0a23c');""")

# --- the cyclone draws as a full ring ------------------------------------
edit(L, """  if (s && s.kind === 'arc') {
    const t = 1 - s.life / .16, h = s.a - 1.15 + 2.3 * Math.min(1, t * 1.6), tail = Math.max(s.a - 1.15, h - 1.3), R = Math.max(1, s.rad * .95), al = clamp(1 - t * .8, 0, 1);""",
     """  if (s && s.kind === 'arc' && s.full) {
    const t = 1 - s.life / .16, R = Math.max(1, s.rad * .95), al = clamp(1 - t * .8, 0, 1), sweep = Math.min(1, t * 1.8) * TAU;
    ctx.fillStyle = 'rgba(255,238,190,' + al * .5 + ')';
    ctx.beginPath(); ctx.arc(s.x, s.y, R, s.a, s.a + sweep); ctx.arc(s.x, s.y, R * .45, s.a + sweep, s.a, true); ctx.closePath(); ctx.fill();
    ctx.strokeStyle = 'rgba(255,255,255,' + al + ')'; ctx.lineWidth = 2.4; ctx.beginPath(); ctx.arc(s.x, s.y, R, s.a, s.a + sweep); ctx.stroke();
  } else if (s && s.kind === 'arc') {
    const t = 1 - s.life / .16, h = s.a - 1.15 + 2.3 * Math.min(1, t * 1.6), tail = Math.max(s.a - 1.15, h - 1.3), R = Math.max(1, s.rad * .95), al = clamp(1 - t * .8, 0, 1);""")

run()
