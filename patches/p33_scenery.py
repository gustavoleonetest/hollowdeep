from patch import edit, run

L = 'part_logic.js'

# --- rooms were placing 17 of 99 available prop sprites; dress them ------
edit(L, """    for (let n = rint(2, 4), tries = 0; n > 0 && tries < 18; tries++) {""",
     """    /* props that belong against a wall, hung along the room's north edge */
    const WALLY = ['banner', 'cross', 'p_shelf', 'p_bookcase', 'p_weaponstand', 'p_dummy', 'r_bricks', 'spear', 'p_bed', 'p_cabinet'];
    for (let n = rint(1, 3), tries = 0; n > 0 && tries < 14 && r.w > 6; tries++) {
      const tx = rint(r.x + 1, r.x + r.w - 2), ty = r.y;
      const x = tx * T + T / 2 + rnd(-4, 4), y = ty * T + T / 2 + 5;
      if (!openAt(x, y)) continue;
      if (avoid.some(a => Math.hypot(x - a[0], y - a[1]) < a[2]) || G.props.some(p => Math.hypot(x - p.x, y - p.y) < 30)) continue;
      const k = WALLY[rint(0, WALLY.length - 1)];
      const hp = Math.round(30 * (1 + (G.level - 1) * .04));
      G.props.push({ k, x, y, sr: 0, sc: 1.2, lit: 0, ph: Math.random() * 6, hp, max: hp, fl: 0, wob: 0, wall: 1 }); n--;
    }
    /* clusters read as somebody lived here; scattered singles read as noise */
    for (let n = rint(3, 6), tries = 0; n > 0 && tries < 26; tries++) {""")

edit(L, """      G.props.push({ k: def[0], x, y, sr: def[1], sc: def[2], lit: def[4] || 0, ph: Math.random() * 6, hp, max: hp, fl: 0, wob: 0 }); n--;
    }
  });""",
     """      G.props.push({ k: def[0], x, y, sr: def[1], sc: def[2], lit: def[4] || 0, ph: Math.random() * 6, hp, max: hp, fl: 0, wob: 0 }); n--;
      /* a second or third of the same kind beside it, so it looks placed */
      if (Math.random() < .45) for (let c = rint(1, 2); c > 0; c--) {
        const cx2 = x + rnd(-34, 34), cy2 = y + rnd(-26, 26);
        if (!openAt(cx2, cy2)) continue;
        if (avoid.some(a => Math.hypot(cx2 - a[0], cy2 - a[1]) < a[2]) || G.props.some(p => Math.hypot(cx2 - p.x, cy2 - p.y) < 22)) continue;
        G.props.push({ k: def[0], x: cx2, y: cy2, sr: def[1], sc: def[2] * rnd(.86, 1.02), lit: def[4] || 0, ph: Math.random() * 6, hp, max: hp, fl: 0, wob: 0 });
      }
    }
  });""")

# --- the floor of each zone does something ------------------------------
edit(L, """function updateFx(dt) {
  const k = 60 * dt;""",
     """/* a slow drift of whatever this zone is made of, seeded around the camera */
function zoneMotes(dt) {
  if (reduceMotion || G.state === 'menu' || !G.map) return;
  const z = (G.zone || ZONES[0]).dec;
  G.moteT = (G.moteT || 0) - dt;
  if (G.moteT > 0) return;
  G.moteT = .12;
  const vx = cam.x, vy = cam.y, vw = W / Z, vh = H / Z;
  for (let i = 0; i < 2; i++) {
    const x = vx + Math.random() * vw, y = vy + Math.random() * vh;
    if (!G.map || solid(Math.floor(x / T), Math.floor(y / T))) continue;
    if (fogAt(x, y) > .75) continue;
    if (z === 1) G.parts.push({ x, y, vx: rnd(-.05, .05), vy: -.08, life: rnd(1.4, 2.4), max: 2.4, col: '#7fc6e8', s: 1.6, k: 'drip' });
    else if (z === 2) G.parts.push({ x, y, vx: rnd(-.14, .14), vy: -.22, life: rnd(1.6, 3), max: 3, col: '#a8d98a', s: 1.8, k: 'ember' });
    else if (z === 3) G.parts.push({ x, y: y + 8, vx: rnd(-.1, .1), vy: -.5, life: rnd(1.2, 2.2), max: 2.2, col: Math.random() < .5 ? '#ff8a3a' : '#ffd08a', s: 1.7, k: 'ember' });
    else if (z === 4) G.parts.push({ x, y, vx: rnd(-.1, .1), vy: -.12, life: rnd(1.8, 3), max: 3, col: '#e8dfc0', s: 1.5, k: 'drip' });
    else if (z === 5) G.parts.push({ x, y, vx: rnd(-.08, .08), vy: -.3, life: rnd(1.4, 2.6), max: 2.6, col: '#b98cff', s: 1.7, k: 'ember' });
    else G.parts.push({ x, y, vx: rnd(-.06, .06), vy: -.1, life: rnd(1.4, 2.4), max: 2.4, col: '#8a93ab', s: 1.3, k: 'drip' });
  }
}
function updateFx(dt) {
  const k = 60 * dt;
  zoneMotes(dt);""")

# --- marks that stay on the floor ---------------------------------------
edit(L, """function explode(s) {""",
     """function scorch(x, y, r, col, kind) {
  G.decals.push({ x, y, r, col, k: kind || 'scorch', rot: rnd(0, TAU) });
  if (G.decals.length > 110) G.decals.shift();
}
function explode(s) {""")

edit(L, """  G.slash = { x: s.x, y: s.y, a: 0, life: .22, kind: 'boom', rad: s.rad };""",
     """  G.slash = { x: s.x, y: s.y, a: 0, life: .22, kind: 'boom', rad: s.rad };
  scorch(s.x, s.y, Math.max(14, s.rad * .55), '#2a1c14', 'scorch');""")

edit(L, """  else if (el === 'cold') { e.chill = Math.max(e.chill || 0, 2 * m); burst(e.x, e.y, '#8fd3ff', 4, 80, .7, 'spark'); }""",
     """  else if (el === 'cold') { e.chill = Math.max(e.chill || 0, 2 * m); burst(e.x, e.y, '#8fd3ff', 4, 80, .7, 'spark'); if (Math.random() < .3) scorch(e.x, e.y, 12 + Math.random() * 8, '#7fc0e8', 'frost'); }""")

edit(L, """  else if (el === 'poison') { e.pois = Math.max(e.pois || 0, 3.4 * m); e.poisDmg = Math.max(e.poisDmg || 0, Math.max(1, ed * .28)); }""",
     """  else if (el === 'poison') { e.pois = Math.max(e.pois || 0, 3.4 * m); e.poisDmg = Math.max(e.poisDmg || 0, Math.max(1, ed * .28)); if (Math.random() < .3) scorch(e.x, e.y, 11 + Math.random() * 7, '#7aa84e', 'frost'); }""")

edit(L, """    G.shake = Math.max(G.shake, .55); sfx('boom'); G.hitstop = Math.max(G.hitstop, .06);""",
     """    G.shake = Math.max(G.shake, .55); sfx('boom'); G.hitstop = Math.max(G.hitstop, .06);
    for (let i = 0; i < 7; i++) scorch(e.x + rnd(-110, 110), e.y + rnd(-90, 90), rnd(10, 22), '#3a2a1e', 'crack');""")

# --- draw the new decal kinds -------------------------------------------
edit(L, """    if (d.k === 'bonewalker') { ctx.fillStyle = '#cfc8b2'; for (let i = 0; i < 5; i++) ctx.fillRect(-9 + i * 4, ((i * 7) % 5) - 3, 3, 1.6); }""",
     """    if (d.k === 'scorch') {
      ctx.globalAlpha = .34; const g2 = ctx.createRadialGradient(0, 0, 0, 0, 0, d.r);
      g2.addColorStop(0, d.col); g2.addColorStop(.65, d.col); g2.addColorStop(1, 'rgba(0,0,0,0)');
      ctx.fillStyle = g2; ctx.beginPath(); ctx.ellipse(0, 0, d.r, d.r * .62, 0, 0, TAU); ctx.fill();
    } else if (d.k === 'frost') {
      ctx.globalAlpha = .26; ctx.strokeStyle = d.col; ctx.lineWidth = 1.2;
      for (let i = 0; i < 5; i++) { const a = i / 5 * TAU; ctx.beginPath(); ctx.moveTo(0, 0); ctx.lineTo(Math.cos(a) * d.r, Math.sin(a) * d.r * .6); ctx.stroke(); }
    } else if (d.k === 'crack') {
      ctx.globalAlpha = .3; ctx.strokeStyle = d.col; ctx.lineWidth = 1.6;
      ctx.beginPath(); let px = -d.r, py = 0; ctx.moveTo(px, py);
      for (let i = 0; i < 4; i++) { px += d.r * .5; py += (i % 2 ? 1 : -1) * d.r * .22; ctx.lineTo(px, py); } ctx.stroke();
    } else if (d.k === 'bonewalker') { ctx.fillStyle = '#cfc8b2'; for (let i = 0; i < 5; i++) ctx.fillRect(-9 + i * 4, ((i * 7) % 5) - 3, 3, 1.6); }""")

run()
