from patch import edit, run

L = 'part_logic.js'

edit(L, """bombs: 0, bolts: [], voice: null, flash: 0, offerQ: [], drops: 0, wares: [] };""",
     """bombs: 0, bolts: [], voice: null, flash: 0, offerQ: [], drops: 0, wares: [], event: null };""")

# --- the arena: walk in and the way out closes behind you -----------------
edit(L, """/* ---------- floor hazards ----------""",
     """/* ---------- the arena ----------
   One marked hall per depth. Step inside and it seals until the waves are done,
   which turns a room you would have walked through into a fight you chose. */
function startArena(r) {
  r.eventDone = true;
  G.event = { room: r, wave: 0, waves: 3, t: 0, phase: 'spawn' };
  G.banner = { txt: 'The gate falls', sub: 'Hold the arena', t: 2.4 };
  announce('Hold the arena!', '#ff8a3a');
  sfx('door'); G.shake = Math.max(G.shake, .45);
  G.fxs.push({ kind: 'shock', x: (r.cx + .5) * T, y: (r.cy + .5) * T, t: 0, r: 220, c1: '255,220,170', c2: '255,138,58' });
}
function finishArena() {
  const r = G.event.room, cx = (r.cx + .5) * T, cy = (r.cy + .5) * T;
  G.event = null;
  G.banner = { txt: 'The arena yields', sub: 'Take your due', t: 2.6 };
  announce('The arena yields!', '#ffd24a');
  G.items.push({ kind: 'chest', big: true, x: cx, y: cy, t: 0 });
  dropGear(cx - 46, cy + 10, 26);
  for (const P of G.players) if (!P.down) P.hp = Math.min(P.max, P.hp + P.max * .35);
  G.fxs.push({ kind: 'shock', x: cx, y: cy, t: 0, r: 210, c1: '255,245,210', c2: '240,190,70' });
  G.shake = Math.max(G.shake, .4); sfx('boom'); coinSpray(cx, cy, 22);
  G.score += 150 * G.level;
}
function arenaTick(dt) {
  const E = G.event; if (!E) return;
  E.t += dt;
  const left = G.enemies.reduce((n, e) => n + (e.ev && e.hp > 0 ? 1 : 0), 0);
  E.left = left;
  if (E.phase === 'spawn') {
    const want = Math.round(4 + G.level * .45 + E.wave * 2);
    let made = 0;
    for (let i = 0; i < 90 && made < want && G.enemies.length < 44; i++) {
      const p = roomPoint(E.room);
      if (!openAt(p.x, p.y) || blockedAt(p.x, p.y, 12)) continue;
      if (G.players.some(q => !q.down && Math.hypot(q.x - p.x, q.y - p.y) < 70)) continue;
      spawnFoe(pickFoe(), p.x, p.y, E.wave === E.waves - 1 && made === 0);
      const e = G.enemies[G.enemies.length - 1]; e.ev = true; e.alert = true; made++;
      burst(p.x, p.y, '#ff8a3a', 9, 100, .9, 'spark');
    }
    if (!made) { finishArena(); return; }
    E.phase = 'fight'; E.t = 0;
    G.banner = { txt: 'Wave ' + (E.wave + 1) + ' of ' + E.waves, sub: null, t: 1.5 };
    sfx('bone');
  } else if (E.phase === 'fight' && left === 0) {
    E.wave++;
    if (E.wave >= E.waves) { finishArena(); return; }
    E.phase = 'spawn'; E.t = 0; sfx('stairs');
  }
}
function arenaHold(P) {
  const E = G.event; if (!E) return;
  const r = E.room;
  const nx = clamp(P.x, r.x * T + P.r + 2, (r.x + r.w) * T - P.r - 2);
  const ny = clamp(P.y, r.y * T + P.r + 2, (r.y + r.h) * T - P.r - 2);
  if (nx === P.x && ny === P.y) return;
  if (blockedAt(nx, ny, P.r)) return;   /* never shove anyone into a wall */
  P.x = nx; P.y = ny;
  if (!P.sealMsg || clock - P.sealMsg > 1.6) { P.sealMsg = clock; text(P.x, P.y - 20, 'Sealed in', '#ff8a3a'); }
}

/* ---------- floor hazards ----------""")

# --- mark one hall per depth, and reset the event --------------------------
edit(L, """  makeProps(); makeHazards();
  const mid = () => G.rooms[rint(1, Math.max(1, G.rooms.length - 2))];""",
     """  makeProps(); makeHazards();
  G.event = null;
  if (G.level >= 2) {
    const cands = G.rooms.filter((r, i) => i > 0 && i < G.rooms.length - 1 && r.kind === 'arena' && r.w >= 9 && r.h >= 7);
    if (cands.length) { cands.sort((a, b) => b.w * b.h - a.w * a.h); cands[0].arena = true; }
  }
  const mid = () => G.rooms[rint(1, Math.max(1, G.rooms.length - 2))];""")

# --- drive it from the step -----------------------------------------------
edit(L, """  updateRevive(dt); updateEnemies(dt); updateNests(dt); updateShots(dt); updateItems(dt); updateHazards(dt); updateFx(dt);""",
     """  if (!G.event) {
    for (const P of G.players) {
      if (P.down) continue;
      const tx = Math.floor(P.x / T), ty = Math.floor(P.y / T);
      const r = G.rooms.find(r2 => r2.arena && !r2.eventDone && tx > r2.x && tx < r2.x + r2.w - 1 && ty > r2.y && ty < r2.y + r2.h - 1);
      if (r) { startArena(r); break; }
    }
  } else arenaTick(dt);
  updateRevive(dt); updateEnemies(dt); updateNests(dt); updateShots(dt); updateItems(dt); updateHazards(dt); updateFx(dt);""")

edit(L, """  if (I.fire) attack(P);
  // reveal map""",
     """  if (I.fire) attack(P);
  arenaHold(P);
  // reveal map""")

# --- show the seal and the count ------------------------------------------
edit(L, """function drawDecals() {""",
     """function drawArena() {
  const E = G.event; if (!E) return;
  const r = E.room, x0 = r.x * T, y0 = r.y * T, w = r.w * T, h = r.h * T, pu = .5 + .5 * Math.sin(clock * 4);
  ctx.save();
  ctx.strokeStyle = 'rgba(255,170,100,' + (.08 + pu * .07) + ')'; ctx.lineWidth = 12; ctx.strokeRect(x0, y0, w, h);
  ctx.strokeStyle = 'rgba(255,138,58,' + (.4 + pu * .3) + ')'; ctx.lineWidth = 2.5;
  ctx.setLineDash([16, 11]); ctx.lineDashOffset = -clock * 30; ctx.strokeRect(x0, y0, w, h);
  ctx.setLineDash([]); ctx.restore();
}
function drawDecals() {""")

edit(L, """  drawTiles(); drawDecals(); drawExit(); for (const t of G.torches) drawTorch(t);""",
     """  drawTiles(); drawDecals(); drawArena(); drawExit(); for (const t of G.torches) drawTorch(t);""")

edit(L, """  const B = G.state === 'play' ? G.enemies.find(e => e.boss && e.alert && e.hp > 0) : null;""",
     """  if (G.event && G.state === 'play') {
    const E = G.event, txt = 'Wave ' + Math.min(E.waves, E.wave + 1) + ' of ' + E.waves + (E.left ? '  \\u00b7  ' + E.left + ' left' : '');
    ctx.font = '600 13px "Spline Sans Mono",monospace'; ctx.textAlign = 'center';
    const ty = H * (W < 560 ? .2 : .14);
    ctx.lineWidth = 4; ctx.strokeStyle = 'rgba(6,8,12,.85)'; ctx.strokeText(txt, W / 2, ty);
    ctx.fillStyle = '#ff8a3a'; ctx.fillText(txt, W / 2, ty);
  }
  const B = G.state === 'play' ? G.enemies.find(e => e.boss && e.alert && e.hp > 0) : null;""")

run()
