from patch import edit, run

L = 'part_logic.js'

# --- six named bosses that were three ------------------------------------
# zoneOf cycles through six zones, each naming its own boss, but bossKindOf
# folded them onto three behaviours: the Cinder Count fought exactly like
# Count Hollow. Each zone now has a boss of its own.
edit(L, """  maw: { spr: 'foe_orc', sc: 1.95, fy: 16, bar: -80, r: 24, hpm: 1.24, spdm: .9, dmgm: 1.2, glow: '#e0702f',
    acts: { 1: ['quake', 'charge'], 2: ['charge', 'quake', 'rampage'], 3: ['rampage', 'quake', 'charge', 'rampage'] } }
};
const BOSS_KIND = ['count', 'caller', 'maw'];
const bossKindOf = L => BOSS_KIND[zoneOf(L).id % 3];
const BOSS_DUR = { slam: .9, burst: .6, summon: .7, charge: 1.42, volley: 1, blink: .5, raise: .8, quake: 1, rampage: 2.1 };""",
     """  maw: { spr: 'foe_orc', sc: 1.95, fy: 16, bar: -80, r: 24, hpm: 1.24, spdm: .9, dmgm: 1.2, glow: '#e0702f',
    acts: { 1: ['quake', 'charge'], 2: ['charge', 'quake', 'rampage'], 3: ['rampage', 'quake', 'charge', 'rampage'] } },
  /* fights the floor rather than you: marks the ground and sets it alight */
  pyre: { spr: 'foe_imp', sc: 2.05, fy: 14, bar: -76, r: 21, hpm: .94, spdm: 1.06, dmgm: 1, glow: '#ff7a3a',
    acts: { 1: ['pillars', 'charge'], 2: ['pillars', 'comet', 'charge'], 3: ['comet', 'pillars', 'charge', 'pillars'] } },
  /* will not be touched while its choir still stands */
  chorister: { spr: 'foe_ghost', sc: 2, fy: 12, bar: -76, r: 20, hpm: .82, spdm: 1.1, dmgm: .95, glow: '#e8dfc0',
    acts: { 1: ['wail', 'volley'], 2: ['ward', 'wail', 'volley', 'raise'], 3: ['wail', 'ward', 'volley', 'wail', 'raise'] } },
  /* throws the room at you and takes it back */
  obsidian: { spr: 'foe_zombie', sc: 2.1, fy: 16, bar: -82, r: 23, hpm: 1.16, spdm: .95, dmgm: 1.1, glow: '#b98cff',
    acts: { 1: ['shards', 'quake'], 2: ['shards', 'rampage', 'quake'], 3: ['shards', 'quake', 'rampage', 'shards'] } }
};
const BOSS_KIND = ['count', 'caller', 'maw', 'pyre', 'chorister', 'obsidian'];
const bossKindOf = L => BOSS_KIND[zoneOf(L).id % BOSS_KIND.length];
const BOSS_DUR = { slam: .9, burst: .6, summon: .7, charge: 1.42, volley: 1, blink: .5, raise: .8, quake: 1, rampage: 2.1,
  pillars: .95, comet: .8, wail: 1.15, ward: .9, shards: 1 };""")

# --- an fx may outlive the fixed eight tenths, for a fair telegraph -------
edit(L, """  for (const f of G.fxs) f.t += dt; G.fxs = G.fxs.filter(f => f.t < .8);""",
     """  for (const f of G.fxs) f.t += dt; G.fxs = G.fxs.filter(f => f.t < (f.dur || .8));""")

# --- a ring on the floor that fills before it goes off --------------------
edit(L, """  for (const f of G.fxs) { if (f.kind === 'shock') drawShock(f); else if (f.kind === 'crit') drawCrit(f); else if (f.kind === 'hit')""",
     """  for (const f of G.fxs) { if (f.kind === 'warn') drawWarn(f); else if (f.kind === 'shock') drawShock(f); else if (f.kind === 'crit') drawCrit(f); else if (f.kind === 'hit')""")

edit(L, """function drawShock(f) {""",
     """function drawWarn(f) {
  /* fills up as the moment approaches, so standing in it is a choice */
  const q = clamp(f.t / (f.dur || .9), 0, 1), r = Math.max(2, f.r || 40), c = f.c || '255,140,60';
  ctx.save();
  ctx.globalAlpha = .18 + q * .28;
  const g = ctx.createRadialGradient(f.x, f.y, 1, f.x, f.y, r);
  g.addColorStop(0, 'rgba(' + c + ',' + (.12 + q * .3) + ')');
  g.addColorStop(.75, 'rgba(' + c + ',' + (.06 + q * .16) + ')');
  g.addColorStop(1, 'rgba(' + c + ',0)');
  ctx.fillStyle = g; ctx.beginPath(); ctx.ellipse(f.x, f.y, r, r * .62, 0, 0, TAU); ctx.fill();
  ctx.globalAlpha = .45 + q * .5; ctx.strokeStyle = 'rgba(' + c + ',.95)'; ctx.lineWidth = 1.6 + q * 1.6;
  ctx.beginPath(); ctx.ellipse(f.x, f.y, r, r * .62, 0, 0, TAU); ctx.stroke();
  /* the inner ring closes on the outer one as the timer runs out */
  ctx.globalAlpha = .5 + q * .45; ctx.lineWidth = 1.4;
  ctx.beginPath(); ctx.ellipse(f.x, f.y, r * q, r * q * .62, 0, 0, TAU); ctx.stroke();
  ctx.restore(); ctx.globalAlpha = 1;
}
function drawShock(f) {""")

# --- a comet bends after you ---------------------------------------------
edit(L, """    const s = G.eshots[i]; s.x += s.vx * k; s.y += s.vy * k; s.life -= dt;""",
     """    const s = G.eshots[i];
    if (s.seek) {
      let b = null, bd2 = 1e9;
      for (const P of G.players) { if (P.down) continue; const d2 = Math.hypot(P.x - s.x, P.y - s.y); if (d2 < bd2) { bd2 = d2; b = P; } }
      if (b) {
        const cur = Math.atan2(s.vy, s.vx), want = Math.atan2(b.y - s.y, b.x - s.x), sp = Math.hypot(s.vx, s.vy);
        let da = want - cur; da = Math.atan2(Math.sin(da), Math.cos(da));
        const na = cur + clamp(da, -s.seek, s.seek) * k;
        s.vx = Math.cos(na) * sp; s.vy = Math.sin(na) * sp;
      }
    }
    s.x += s.vx * k; s.y += s.vy * k; s.life -= dt;""")

# --- the new acts ---------------------------------------------------------
edit(L, """  } else if (st === 'summon') {""",
     """  } else if (st === 'pillars') {
    /* marks the floor under and around you, then sets every mark alight */
    const spots = [], alive3 = G.players.filter(p => !p.down);
    for (const p of alive3) spots.push([p.x, p.y]);
    for (let i = 0; i < (e.ph >= 2 ? 5 : 3); i++) {
      const a = rnd(0, TAU), d = rnd(50, 170);
      spots.push([e.x + Math.cos(a) * d, e.y + Math.sin(a) * d]);
    }
    const R = 46, dm = Math.round(e.dmg * .85), wait = .85;
    for (const [sx, sy] of spots) {
      if (blockedAt(sx, sy, 10)) continue;
      G.fxs.push({ kind: 'warn', x: sx, y: sy, t: 0, r: R, dur: wait, c: '255,140,60' });
      G.timers.push({ t: wait, fn: () => {
        G.fxs.push({ kind: 'shock', x: sx, y: sy, t: 0, r: R * 1.5, c1: '255,236,190', c2: '255,110,50' });
        burst(sx, sy, '#ff8a3a', 14, 190, 1.1, 'ember'); burst(sx, sy, '#3a4152', 5, 70, 1.3, 'smoke');
        scorch(sx, sy, rnd(14, 22), '#2a1810', 'crack'); sfx('boom');
        for (const p of G.players) if (!p.down && Math.hypot(p.x - sx, p.y - sy) < R + p.r) hurtPlayer(p, dm, Math.atan2(p.y - sy, p.x - sx), e);
        for (const q of G.enemies.slice()) if (!q.dead && q.hp > 0 && !q.boss && Math.hypot(q.x - sx, q.y - sy) < R + q.r) hurtFoe(q, dm, 0, false, true, null);
      } });
    }
    G.shake = Math.max(G.shake, .2); sfx('bone');
  } else if (st === 'comet') {
    const alive3 = G.players.filter(p => !p.down);
    const tgt = alive3.length ? alive3[rint(0, alive3.length - 1)] : null;
    const n = e.ph >= 3 ? 3 : 2, base = tgt ? Math.atan2(tgt.y - e.y, tgt.x - e.x) : (e.face || 0);
    for (let i = 0; i < n; i++) {
      const a = base + (i - (n - 1) / 2) * .5;
      G.eshots.push({ x: e.x, y: e.y, vx: Math.cos(a) * 2.2, vy: Math.sin(a) * 2.2, life: 4.2, r: 8,
                      dmg: Math.round(e.dmg * .7), own: e, seek: .026, col: '#ff8a3a' });
    }
    burst(e.x, e.y, '#ff8a3a', 12, 150, 1, 'ember'); sfx('bone');
  } else if (st === 'wail') {
    /* a ring that travels outward: it hurts as it passes over you, so the
       answer is to move with it rather than away from it */
    const dm = Math.round(e.dmg * .75), ox = e.x, oy = e.y;
    G.fxs.push({ kind: 'shock', x: ox, y: oy, t: 0, r: 230, c1: '245,240,220', c2: '200,190,160' });
    G.shake = Math.max(G.shake, .3); sfx('bone');
    for (let step = 0; step < 7; step++) {
      const inner = 24 + step * 30;
      G.timers.push({ t: .07 + step * .075, fn: () => {
        for (let i = 0; i < 5; i++) {
          const a = rnd(0, TAU);
          G.parts.push({ x: ox + Math.cos(a) * inner, y: oy + Math.sin(a) * inner * .7, vx: 0, vy: -.3, life: .35, max: .35, col: '#efe8cf', s: 2, k: 'spark' });
        }
        for (const p of G.players) {
          if (p.down || p.inv > 0) continue;
          const d = Math.hypot(p.x - ox, p.y - oy);
          if (d >= inner - 16 && d < inner + 18) hurtPlayer(p, dm, Math.atan2(p.y - oy, p.x - ox), e);
        }
      } });
    }
  } else if (st === 'ward') {
    /* it cannot be touched while its choir stands, so the answer is the adds */
    const made = [];
    for (let i = 0, tries = 0; tries < 20 && made.length < (e.ph >= 3 ? 4 : 3) && G.enemies.length < 38; tries++) {
      const a = rnd(0, TAU), d = rnd(58, 96), x = e.x + Math.cos(a) * d, y = e.y + Math.sin(a) * d;
      if (blockedAt(x, y, 11) || !openAt(x, y)) continue;
      spawnFoe('wisp', x, y, false);
      const n2 = G.enemies[G.enemies.length - 1]; n2.alert = true; made.push(n2);
      burst(x, y, '#e8dfc0', 12, 120, 1.1, 'spark');
    }
    if (made.length) {
      e.immune = true; e.wardAdds = made; e.wardT = 9;
      announceOnce('ward' + e.kind, 5, (e.name || 'The boss') + ' will not be touched', '#e8dfc0');
      G.fxs.push({ kind: 'shock', x: e.x, y: e.y, t: 0, r: 130, c1: '245,240,220', c2: '190,180,150' });
    }
    sfx('bone');
  } else if (st === 'shards') {
    /* thrown out, then called back: the gap between is the only safe moment */
    const n = e.ph >= 3 ? 14 : 10, o = rnd(0, TAU), mine = [];
    for (let i = 0; i < n; i++) {
      const a = o + i / n * TAU;
      const s2 = { x: e.x, y: e.y, vx: Math.cos(a) * 3.1, vy: Math.sin(a) * 3.1, life: 3.4, r: 7,
                   dmg: Math.round(e.dmg * .55), own: e, col: '#b98cff' };
      G.eshots.push(s2); mine.push(s2);
    }
    sfx('bone'); burst(e.x, e.y, '#b98cff', 14, 160, 1, 'spark');
    G.timers.push({ t: .85, fn: () => {
      let any = false;
      for (const s2 of mine) {
        if (G.eshots.indexOf(s2) < 0) continue;
        s2.vx = -s2.vx; s2.vy = -s2.vy; s2.life = Math.max(s2.life, 1.6); any = true;
        burst(s2.x, s2.y, '#b98cff', 2, 50, .6, 'spark');
      }
      if (any) sfx('dash');
    } });
  } else if (st === 'summon') {""")

# --- the ward has to lift, or the fight cannot end ------------------------
edit(L, """      e.ph = e.hp < e.max * .26 ? 3 : e.hp < e.max * .5 ? 2 : 1;
      const BK = BOSSES[e.kind] || BOSSES.count;""",
     """      e.ph = e.hp < e.max * .26 ? 3 : e.hp < e.max * .5 ? 2 : 1;
      if (e.wardT !== undefined) {
        e.wardT -= dt;
        const choirDown = !e.wardAdds || !e.wardAdds.some(a => a && !a.dead && a.hp > 0);
        if (choirDown || e.wardT <= 0) {
          e.immune = false; e.wardT = undefined; e.wardAdds = null;
          G.fxs.push({ kind: 'shock', x: e.x, y: e.y, t: 0, r: 140, c1: '255,250,225', c2: '200,190,160' });
          text(e.x, e.y - e.r - 10, 'Exposed', '#ffd24a', 15); sfx('ward');
          announceOnce('wardoff' + e.kind, 5, 'The choir is silenced', '#ffd24a');
        }
      }
      const BK = BOSSES[e.kind] || BOSSES.count;""")

run()
