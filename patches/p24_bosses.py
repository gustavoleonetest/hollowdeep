from patch import edit, run

L = 'part_logic.js'

# --- three archetypes, each with its own grammar of attacks ---------------
edit(L, """const zoneOf = L => ZONES[Math.floor((L - 1) / 3) % ZONES.length];""",
     """const zoneOf = L => ZONES[Math.floor((L - 1) / 3) % ZONES.length];
/* The Count presses you, the Choir keeps its distance and raises the dead,
   the Maw never stops moving. Each zone draws one of the three. */
const BOSSES = {
  count: { spr: 'boss_vampire', sc: 1.2, fy: 18, bar: -88, r: 22, hpm: 1, spdm: 1, dmgm: 1, glow: '#b06a8a',
    acts: { 1: ['slam', 'burst'], 2: ['slam', 'burst', 'summon', 'burst'], 3: ['charge', 'burst', 'slam', 'summon', 'burst', 'charge'] } },
  caller: { spr: 'foe_skeleton', sc: 1.95, fy: 14, bar: -78, r: 20, hpm: .86, spdm: 1.14, dmgm: .9, glow: '#9a6bd6',
    acts: { 1: ['volley', 'raise'], 2: ['volley', 'blink', 'raise', 'volley'], 3: ['blink', 'volley', 'raise', 'volley', 'blink'] } },
  maw: { spr: 'foe_orc', sc: 1.95, fy: 16, bar: -80, r: 24, hpm: 1.24, spdm: .9, dmgm: 1.2, glow: '#e0702f',
    acts: { 1: ['quake', 'charge'], 2: ['charge', 'quake', 'rampage'], 3: ['rampage', 'quake', 'charge', 'rampage'] } }
};
const BOSS_KIND = ['count', 'caller', 'maw'];
const bossKindOf = L => BOSS_KIND[zoneOf(L).id % 3];
const BOSS_DUR = { slam: .9, burst: .6, summon: .7, charge: 1.42, volley: 1, blink: .5, raise: .8, quake: 1, rampage: 2.1 };""")

# --- zone names now match the thing that lives there ----------------------
edit(L, """  { id: 1, name: 'The Drowned Halls', dec: 1, tint: 'rgba(40,120,160,.17)', amb: '#5fc4e8', boss: 'The Drowned Count', bcol: '#4fa3b8' },
  { id: 2, name: 'Mossroot Caverns', dec: 2, tint: 'rgba(70,130,50,.16)', amb: '#9bd16a', boss: 'The Mossroot Count', bcol: '#7aa05a' },""",
     """  { id: 1, name: 'The Drowned Halls', dec: 1, tint: 'rgba(40,120,160,.17)', amb: '#5fc4e8', boss: 'The Drowned Choir', bcol: '#4fa3b8' },
  { id: 2, name: 'Mossroot Caverns', dec: 2, tint: 'rgba(70,130,50,.16)', amb: '#9bd16a', boss: 'The Mossroot Maw', bcol: '#7aa05a' },""")

edit(L, """  { id: 4, name: 'The Bone Gardens', dec: 4, tint: 'rgba(150,140,110,.13)', amb: '#e8dfc0', boss: 'The Pale Count', bcol: '#d8d2bd' },
  { id: 5, name: 'The Obsidian Reach', dec: 5, tint: 'rgba(92,58,150,.18)', amb: '#b98cff', boss: 'The Obsidian Count', bcol: '#8a6bd6' }""",
     """  { id: 4, name: 'The Bone Gardens', dec: 4, tint: 'rgba(150,140,110,.13)', amb: '#e8dfc0', boss: 'The Pale Chorister', bcol: '#d8d2bd' },
  { id: 5, name: 'The Obsidian Reach', dec: 5, tint: 'rgba(92,58,150,.18)', amb: '#b98cff', boss: 'The Obsidian Maw', bcol: '#8a6bd6' }""")

# --- a boss takes its shape from its archetype ----------------------------
edit(L, """  if (elite && G.state === 'play') sfx('elite');
  if (eaff.indexOf('fast') >= 0) E.spd *= 1.55;""",
     """  if (type === 'warden') {
    E.kind = bossKindOf(G.level);
    const B = BOSSES[E.kind] || BOSSES.count;
    E.hp = E.max = Math.round(hp * B.hpm);
    E.spd *= B.spdm; E.dmg = Math.round(E.dmg * B.dmgm); E.r = B.r; E.n = 0;
  }
  if (elite && G.state === 'play') sfx('elite');
  if (eaff.indexOf('fast') >= 0) E.spd *= 1.55;""")

# --- the state machine now covers moving and charging actions ------------
edit(L, """    if (e.boss && e.alert) {
      e.ph = e.hp < e.max * .26 ? 3 : e.hp < e.max * .5 ? 2 : 1;
      if (e.st === 'charge') {
        e.stt += dt;
        if (e.stt < .68) { tx = 0; ty = 0; e.ca = e.face; }
        else if (e.stt < 1.42) { tx = Math.cos(e.ca) * e.spd * 5.4; ty = Math.sin(e.ca) * e.spd * 5.4; if (Math.random() < .7) burst(e.x, e.y, '#ff5a46', 2, 80, .6, 'spark'); }
        else bossAct(e);
      }
      else if (e.st !== 'chase') { e.stt += dt; tx = 0; ty = 0; if (e.stt >= ({ slam: .9, burst: .6, summon: .7 }[e.st] || .6)) bossAct(e); }
      else {
        if (e.ph >= 2) { const m2 = e.ph >= 3 ? 1.5 : 1.3; tx *= m2; ty *= m2; }
        if (e.cd <= 0 && seen) { const pool = e.ph >= 3 ? ['charge', 'burst', 'slam', 'summon', 'burst', 'charge'] : e.ph === 2 ? ['slam', 'burst', 'summon', 'burst'] : ['slam', 'burst']; e.st = pool[e.n++ % pool.length]; e.stt = 0; sfx('bone'); }
      }
    }""",
     """    if (e.boss && e.alert) {
      e.ph = e.hp < e.max * .26 ? 3 : e.hp < e.max * .5 ? 2 : 1;
      const BK = BOSSES[e.kind] || BOSSES.count;
      if (e.st === 'charge' || e.st === 'rampage') {
        e.stt += dt;
        const rush = e.st === 'rampage', seg = rush ? .7 : 1.42, wind = rush ? .26 : .68;
        const ph = e.stt % seg;
        if (ph < wind) { tx = 0; ty = 0; e.ca = e.face; }
        else { const sp = e.spd * (rush ? 6.2 : 5.4); tx = Math.cos(e.ca) * sp; ty = Math.sin(e.ca) * sp; if (Math.random() < .7) burst(e.x, e.y, '#ff5a46', 2, 80, .6, 'spark'); }
        if (e.stt >= BOSS_DUR[e.st]) bossAct(e);
      }
      else if (e.st !== 'chase') { e.stt += dt; tx = 0; ty = 0; if (e.stt >= (BOSS_DUR[e.st] || .6)) bossAct(e); }
      else {
        if (e.ph >= 2) { const m2 = e.ph >= 3 ? 1.5 : 1.3; tx *= m2; ty *= m2; }
        if (e.cd <= 0 && seen) { const pool = BK.acts[e.ph] || BK.acts[1]; e.st = pool[e.n++ % pool.length]; e.stt = 0; sfx('bone'); }
      }
    }""")

# --- the new attacks themselves ------------------------------------------
edit(L, """  } else if (st === 'burst') {""",
     """  } else if (st === 'volley') {
    const n = e.ph >= 3 ? 5 : 3, a0 = e.face || 0;
    for (let i = 0; i < n; i++) {
      const a = a0 + (i - (n - 1) / 2) * .17;
      G.eshots.push({ x: e.x, y: e.y, vx: Math.cos(a) * 4.3, vy: Math.sin(a) * 4.3, life: 2.6, r: 6, dmg: Math.round(e.dmg * .62), own: e });
    }
    burstDir(e.x, e.y, a0, '#d8d2bd', 10, 200, .9, 'spark', .3); sfx('bone');
  } else if (st === 'blink') {
    burst(e.x, e.y, '#9a6bd6', 22, 150, 1.3, 'smoke');
    const alive2 = G.players.filter(p => !p.down), tgt = alive2.length ? alive2[rint(0, alive2.length - 1)] : null;
    if (tgt) for (let k = 0; k < 24; k++) {
      const a = rnd(0, TAU), d = rnd(95, 165), nx = tgt.x + Math.cos(a) * d, ny = tgt.y + Math.sin(a) * d;
      if (!blockedAt(nx, ny, e.r) && openAt(nx, ny)) { e.x = nx; e.y = ny; break; }
    }
    burst(e.x, e.y, '#9a6bd6', 22, 150, 1.3, 'smoke');
    G.fxs.push({ kind: 'shock', x: e.x, y: e.y, t: 0, r: 95, c1: '226,196,255', c2: '154,107,214' });
    sfx('dash');
  } else if (st === 'raise') {
    for (let i = 0, made = 0; i < 16 && made < (e.ph >= 2 ? 4 : 3) && G.enemies.length < 38; i++) {
      const a = rnd(0, TAU), d = rnd(44, 76), x = e.x + Math.cos(a) * d, y = e.y + Math.sin(a) * d;
      if (blockedAt(x, y, 11) || !openAt(x, y)) continue;
      spawnFoe('bonewalker', x, y, false);
      const n2 = G.enemies[G.enemies.length - 1]; n2.alert = true; made++;
      burst(x, y, '#d8d2bd', 12, 110, 1.1, 'spark'); burst(x, y, '#3a4152', 5, 50, 1.3, 'smoke');
    }
    G.fxs.push({ kind: 'shock', x: e.x, y: e.y, t: 0, r: 110, c1: '240,236,214', c2: '150,146,128' }); sfx('bone');
  } else if (st === 'quake') {
    const R = 155, dm = Math.round(e.dmg * 1.1);
    G.fxs.push({ kind: 'shock', x: e.x, y: e.y, t: 0, r: R, c1: '255,230,200', c2: '206,150,90' },
                { kind: 'shock', x: e.x, y: e.y, t: -.16, r: R * 1.45, c1: '255,240,210', c2: '180,120,70' });
    G.shake = Math.max(G.shake, .55); sfx('boom'); G.hitstop = Math.max(G.hitstop, .06);
    burst(e.x, e.y, '#3a4152', 16, 140, 1.5, 'smoke'); burst(e.x, e.y, '#d9b48a', 18, 190, 1, 'sq');
    for (const p of G.players) {
      if (p.down) continue; const d = Math.hypot(p.x - e.x, p.y - e.y);
      if (d >= R * 1.45) continue;
      const ang = Math.atan2(p.y - e.y, p.x - e.x);
      hurtPlayer(p, d < R ? dm : Math.round(dm * .6), ang, e);
      moveEnt(p, Math.cos(ang) * 14, Math.sin(ang) * 14);
    }
    for (const pr of G.props.slice()) if (Math.hypot(pr.x - e.x, pr.y - e.y) < R) hurtProp(pr, 60, Math.atan2(pr.y - e.y, pr.x - e.x));
  } else if (st === 'burst') {""")

# --- enemy shots remember who fired them ----------------------------------
edit(L, """        if (e.cd <= 0 && d < 380) { e.cd = 2.2; const a = Math.atan2(dy, dx); G.eshots.push({ x: e.x, y: e.y, vx: Math.cos(a) * 3.2, vy: Math.sin(a) * 3.2, life: 2.6, r: 5, dmg: e.dmg }); sfx('bone'); }""",
     """        if (e.cd <= 0 && d < 380) { e.cd = 2.2; const a = Math.atan2(dy, dx); G.eshots.push({ x: e.x, y: e.y, vx: Math.cos(a) * 3.2, vy: Math.sin(a) * 3.2, life: 2.6, r: 5, dmg: e.dmg, own: e }); sfx('bone'); }""")

edit(L, """    for (let i = 0; i < n; i++) { const a = o + i / n * TAU; G.eshots.push({ x: e.x, y: e.y, vx: Math.cos(a) * 2.6, vy: Math.sin(a) * 2.6, life: 2.4, r: 6, dmg: Math.round(e.dmg * .5) }); }""",
     """    for (let i = 0; i < n; i++) { const a = o + i / n * TAU; G.eshots.push({ x: e.x, y: e.y, vx: Math.cos(a) * 2.6, vy: Math.sin(a) * 2.6, life: 2.4, r: 6, dmg: Math.round(e.dmg * .5), own: e }); }""")

edit(L, """    if (!dead) for (const P of G.players) if (!P.down && Math.hypot(P.x - s.x, P.y - s.y) < P.r + s.r) { hurtPlayer(P, s.dmg, Math.atan2(s.vy, s.vx) + Math.PI); dead = true; break; }""",
     """    if (!dead) for (const P of G.players) if (!P.down && Math.hypot(P.x - s.x, P.y - s.y) < P.r + s.r) { hurtPlayer(P, s.dmg, Math.atan2(s.vy, s.vx) + Math.PI, s.own); dead = true; break; }""")

# --- each archetype gets its own rig --------------------------------------
edit(L, """  thief: { key: 'npc_keeper', fy: 8, bar: -44, sc: 1.3 },
  reaper: { key: 'foe_ghost', fy: 10, bar: -64, sc: 2.2 }
};""",
     """  thief: { key: 'npc_keeper', fy: 8, bar: -44, sc: 1.3 },
  reaper: { key: 'foe_ghost', fy: 10, bar: -64, sc: 2.2 },
  warden_caller: { key: 'foe_skeleton', fy: 14, bar: -78, sc: 1.95 },
  warden_maw: { key: 'foe_orc', fy: 16, bar: -80, sc: 1.95 }
};""")

edit(L, """function foeDef(type) {
  if (type === 'gloam' && sprOk('foe_puglin')) return SPRFOE.gloam_pug;
  if (type === 'hound' && G.zone.id >= 1 && sprOk('foe_imp')) return SPRFOE.hound_imp;
  return SPRFOE[type];
}""",
     """function foeDef(type, kind) {
  if (type === 'warden') return SPRFOE[kind === 'caller' ? 'warden_caller' : kind === 'maw' ? 'warden_maw' : 'warden'];
  if (type === 'gloam' && sprOk('foe_puglin')) return SPRFOE.gloam_pug;
  if (type === 'hound' && G.zone.id >= 1 && sprOk('foe_imp')) return SPRFOE.hound_imp;
  return SPRFOE[type];
}""")

edit(L, """  const SF = foeDef(e.type), useSpr = SF && sprOk(SF.key);""",
     """  const SF = foeDef(e.type, e.kind), useSpr = SF && sprOk(SF.key);""")

edit(L, """  const S = foeDef(e.type), x = e.x, y = e.y, ghost = e.type === 'wisp', boss = e.boss;""",
     """  const S = foeDef(e.type, e.kind), x = e.x, y = e.y, ghost = e.type === 'wisp', boss = e.boss;""")

edit(L, """  G.dying.push({ type: e.type, x: e.x, y: e.y, r: e.r, col: e.col, face: e.face || 0, t: 0, walk: e.walk || 0 });""",
     """  G.dying.push({ type: e.type, kind: e.kind, x: e.x, y: e.y, r: e.r, col: e.col, face: e.face || 0, t: 0, walk: e.walk || 0 });""")

edit(L, """  const S = foeDef(d.type); if (!S || !sprOk(S.key)) return drawDyingOld(d);""",
     """  const S = foeDef(d.type, d.kind); if (!S || !sprOk(S.key)) return drawDyingOld(d);""")

# --- telegraphs for the new attacks ---------------------------------------
edit(L, """    if (e.st === 'charge' && e.stt < .72) {
      const p = Math.min(1, e.stt / .68); ctx.save(); ctx.translate(x, y); ctx.rotate(e.ca != null ? e.ca : (e.face || 0));
      ctx.strokeStyle = 'rgba(255,90,70,' + (.18 + p * .5) + ')'; ctx.lineWidth = 7 + p * 11; ctx.setLineDash([15, 10]);
      ctx.beginPath(); ctx.moveTo(24, 0); ctx.lineTo(310, 0); ctx.stroke(); ctx.setLineDash([]); ctx.restore();
    }""",
     """    if ((e.st === 'charge' || e.st === 'rampage') && (e.stt % (e.st === 'rampage' ? .7 : 1.42)) < (e.st === 'rampage' ? .3 : .72)) {
      const w = e.st === 'rampage' ? .26 : .68, p = Math.min(1, (e.stt % (e.st === 'rampage' ? .7 : 1.42)) / w);
      ctx.save(); ctx.translate(x, y); ctx.rotate(e.ca != null ? e.ca : (e.face || 0));
      ctx.strokeStyle = 'rgba(255,90,70,' + (.18 + p * .5) + ')'; ctx.lineWidth = 7 + p * 11; ctx.setLineDash([15, 10]);
      ctx.beginPath(); ctx.moveTo(24, 0); ctx.lineTo(310, 0); ctx.stroke(); ctx.setLineDash([]); ctx.restore();
    }
    if (e.st === 'quake') {
      const p = Math.min(1, e.stt / BOSS_DUR.quake), R = 155 * 1.45;
      ctx.fillStyle = 'rgba(214,160,100,' + (.06 + p * .14) + ')'; ctx.beginPath(); ctx.arc(x, y, R, 0, TAU); ctx.fill();
      ctx.strokeStyle = 'rgba(255,220,170,' + (.3 + p * .55) + ')'; ctx.lineWidth = 2 + p * 3; ctx.beginPath(); ctx.arc(x, y, R * p, 0, TAU); ctx.stroke();
      ctx.strokeStyle = 'rgba(255,200,140,.35)'; ctx.lineWidth = 2; ctx.beginPath(); ctx.arc(x, y, 155, 0, TAU); ctx.stroke();
    }
    if (e.st === 'volley') {
      const p = Math.min(1, e.stt / BOSS_DUR.volley); ctx.save(); ctx.translate(x, y); ctx.rotate(e.face || 0);
      ctx.strokeStyle = 'rgba(232,228,210,' + (.2 + p * .5) + ')'; ctx.lineWidth = 1.5 + p * 2; ctx.setLineDash([9, 7]);
      for (const a of [-.17, 0, .17]) { ctx.save(); ctx.rotate(a); ctx.beginPath(); ctx.moveTo(20, 0); ctx.lineTo(250, 0); ctx.stroke(); ctx.restore(); }
      ctx.setLineDash([]); ctx.restore();
    }
    if (e.st === 'raise') glow(x, y, 110, '#d8d2bd', .25 + Math.sin(e.t * 22) * .12);""")

edit(L, """    glow(x, y, 54, e.ph >= 2 ? '#ff4a3a' : e.col, e.ph >= 2 ? .22 + Math.sin(e.t * 6) * .06 : .16);""",
     """    glow(x, y, 54, e.ph >= 2 ? '#ff4a3a' : ((BOSSES[e.kind] || BOSSES.count).glow || e.col), e.ph >= 2 ? .22 + Math.sin(e.t * 6) * .06 : .18);""")

run()
