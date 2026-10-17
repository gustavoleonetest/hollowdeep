from patch import edit, run

L = 'part_logic.js'

# --- timers for the new effects -------------------------------------------
edit(L, """  if (G.slash) { G.slash.life -= dt; if (G.slash.life <= 0) G.slash = null; }""",
     """  for (const b of G.bolts) b.t += dt; if (G.bolts.length) G.bolts = G.bolts.filter(b => b.t < .22);
  if (G.flash > 0) G.flash = Math.max(0, G.flash - dt * 1.9);
  if (G.voice) { G.voice.t -= dt; if (G.voice.t <= 0) G.voice = null; }
  for (const P of G.players) if (P.bombCd > 0) P.bombCd -= dt;
  if (G.slash) { G.slash.life -= dt; if (G.slash.life <= 0) G.slash = null; }""")

# --- gear on the floor gets a Diablo light column -------------------------
edit(L, """function drawItem(it) {
  if (!sprOk('props') || it.kind === 'gem' || it.kind === 'gold') return drawItemOld(it);
  const b = Math.sin(it.t * 4) * 2;
  if (it.kind === 'food') { glow(it.x, it.y, 18, '#ff6a6a', .35); shadow(it.x, it.y + 9, 6, 2.2, .3); sprProp('potion', it.x, it.y + 10 + b, 1.9); }""",
     """const hexA = (h, a) => { const n = parseInt(h.slice(1), 16); return 'rgba(' + (n >> 16) + ',' + ((n >> 8) & 255) + ',' + (n & 255) + ',' + a + ')'; };
function drawGear(it) {
  const o = it.item, b = Math.sin(it.t * 3) * 1.8, pu = .5 + .5 * Math.sin(clock * 2.6 + it.t);
  const g = ctx.createLinearGradient(it.x, it.y - 92, it.x, it.y + 8);
  g.addColorStop(0, hexA(o.col, 0)); g.addColorStop(.72, hexA(o.col, .16 + pu * .1)); g.addColorStop(1, hexA(o.col, .42 + pu * .14));
  ctx.fillStyle = g; ctx.fillRect(it.x - 8, it.y - 92, 16, 100);
  glow(it.x, it.y, 32, o.col, .4 + pu * .18); shadow(it.x, it.y + 9, 8, 3, .32);
  const sp = o.slot === 'weapon' ? 'sword' : o.slot === 'armour' ? 'shield' : 'p_pouch';
  if (!sprProp(sp, it.x, it.y + 11 + b, 1.5)) {
    ctx.fillStyle = o.col; ctx.beginPath(); ctx.moveTo(it.x, it.y - 7 + b); ctx.lineTo(it.x + 6, it.y + b); ctx.lineTo(it.x, it.y + 7 + b); ctx.lineTo(it.x - 6, it.y + b); ctx.fill();
  }
  for (let i = 0; i < 3; i++) { const a = clock * 1.6 + i * 2.1; ctx.fillStyle = hexA(o.col, .8); ctx.fillRect(it.x + Math.cos(a) * 13, it.y - 12 + Math.sin(a) * 5 - Math.abs(Math.sin(clock * 2.4 + i)) * 8, 2, 2); }
}
function drawItem(it) {
  if (it.kind === 'gear') return drawGear(it);
  if (!sprOk('props') || it.kind === 'gem' || it.kind === 'gold' || it.kind === 'food') return drawItemOld(it);
  const b = Math.sin(it.t * 4) * 2;
  if (it.kind === 'bomb') {
    const pu = .5 + .5 * Math.sin(clock * 3);
    glow(it.x, it.y, 30, '#b98cff', .4 + pu * .2); shadow(it.x, it.y + 9, 7, 2.4, .3);
    sprProp('potion', it.x, it.y + 10 + b, 1.9, '#b98cff', .55);
  }""")

# --- lightning arcs --------------------------------------------------------
edit(L, """function drawShots() {""",
     """function drawBolts() {
  for (const b of G.bolts) {
    const a = Math.max(0, 1 - b.t / .22); if (a <= 0) continue;
    const n = 5, dx = (b.x2 - b.x1) / n, dy = (b.y2 - b.y1) / n;
    for (const [w, col] of [[5 * a + 1.5, 'rgba(120,180,255,' + a * .45 + ')'], [2 * a + .7, 'rgba(235,245,255,' + a + ')']]) {
      ctx.strokeStyle = col; ctx.lineWidth = w; ctx.beginPath(); ctx.moveTo(b.x1, b.y1);
      for (let i = 1; i < n; i++) ctx.lineTo(b.x1 + dx * i + rnd(-7, 7), b.y1 + dy * i + rnd(-7, 7));
      ctx.lineTo(b.x2, b.y2); ctx.stroke();
    }
  }
}
function drawShots() {""")

edit(L, """  drawShots(); drawFx(); drawFog();""", """  drawShots(); drawBolts(); drawFx(); drawFog();""")

# --- elites wear their modifiers; chill and wards read at a glance ---------
edit(L, """  let tint = null, ta = .85;
  if (e.flash > 0) tint = '#ffffff';
  else if (e.type === 'bloat') { tint = e.fuse > 0 ? '#eaffc4' : '#7fbf4a'; ta = e.fuse > 0 ? .72 : .5; }
  else if (e.elite) { tint = '#ffd98a'; ta = .3; }""",
     """  let tint = null, ta = .85;
  if (e.flash > 0) tint = '#ffffff';
  else if (e.type === 'reaper') { tint = '#eef2ff'; ta = .55; }
  else if (e.type === 'thief') { tint = '#e8c877'; ta = .45; }
  else if (e.type === 'bloat') { tint = e.fuse > 0 ? '#eaffc4' : '#7fbf4a'; ta = e.fuse > 0 ? .72 : .5; }
  else if (e.chill > 0) { tint = '#9fd8ff'; ta = .5; }
  else if (e.elite) { tint = '#ffd98a'; ta = .3; }""")

edit(L, """  if (e.type === 'bloat') {
    const f = e.fuse > 0 ? 1 - e.fuse / .6 : 0, pu = .5 + .5 * Math.sin(clock * (e.fuse > 0 ? 26 : 4));
    glow(x, y - 4, 40 + f * 36, e.fuse > 0 ? '#eaffc4' : '#8fbf5a', .2 + pu * (e.fuse > 0 ? .5 : .1));
  }""",
     """  if (e.type === 'bloat') {
    const f = e.fuse > 0 ? 1 - e.fuse / .6 : 0, pu = .5 + .5 * Math.sin(clock * (e.fuse > 0 ? 26 : 4));
    glow(x, y - 4, 40 + f * 36, e.fuse > 0 ? '#eaffc4' : '#8fbf5a', .2 + pu * (e.fuse > 0 ? .5 : .1));
  }
  if (e.type === 'reaper') {
    const pu = .5 + .5 * Math.sin(clock * 1.6);
    glow(x, y - 10, 90 + pu * 16, '#dfe4ef', .22 + pu * .12);
    ctx.save(); ctx.globalAlpha = .5; ctx.strokeStyle = 'rgba(223,228,239,' + (.3 + pu * .3) + ')'; ctx.lineWidth = 1.4;
    for (let i = 0; i < 2; i++) { ctx.beginPath(); ctx.ellipse(x, y + S.fy, 24 + i * 11 + pu * 4, (24 + i * 11) * .4, 0, 0, TAU); ctx.stroke(); }
    ctx.restore();
  }
  if (e.type === 'thief' && e.loot > 0) {
    glow(x, y - 6, 34, '#f0a23c', .3 + .2 * Math.sin(clock * 7));
    ctx.fillStyle = '#f0a23c'; ctx.font = '600 10px "Spline Sans Mono",monospace'; ctx.textAlign = 'center';
    ctx.lineWidth = 3; ctx.strokeStyle = 'rgba(8,10,14,.8)';
    ctx.strokeText(e.loot + 'g', x, y + S.bar - 6); ctx.fillText(e.loot + 'g', x, y + S.bar - 6);
  }
  if (e.ward > 0) {
    const q = e.ward / e.wardMax, pu = .5 + .5 * Math.sin(clock * 4);
    ctx.save(); ctx.strokeStyle = 'rgba(255,210,74,' + (.3 + pu * .25 + (e.wardFl > 0 ? .4 : 0)) + ')'; ctx.lineWidth = 2;
    ctx.beginPath(); ctx.arc(x, y, e.r * 1.9 * (.8 + q * .3), 0, TAU); ctx.stroke(); ctx.restore();
    if (e.wardFl > 0) e.wardFl -= 1 / 60;
  }
  if (e.elite && e.eaff && e.eaff.length) {
    const nm = e.eaff.map(id => { const a = EAFF.find(z => z.id === id); return a ? a.name : null; }).filter(Boolean).join(' \\u00b7 ');
    ctx.fillStyle = '#ffd24a'; ctx.font = '600 9px "Spline Sans Mono",monospace'; ctx.textAlign = 'center';
    ctx.lineWidth = 3; ctx.strokeStyle = 'rgba(8,10,14,.85)';
    ctx.strokeText(nm, x, y + S.bar - 7); ctx.fillText(nm, x, y + S.bar - 7);
  }""")

# --- the narrator on screen, and the potion flash --------------------------
edit(L, """  if (G.paused) { ctx.fillStyle = 'rgba(6,8,12,.6)'; ctx.fillRect(0, 0, W, H);""",
     """  if (G.flash > 0) { ctx.fillStyle = 'rgba(232,222,255,' + Math.min(.72, G.flash) + ')'; ctx.fillRect(0, 0, W, H); }
  if (G.voice) {
    const v = G.voice, a = clamp(v.t / .55, 0, 1), vy = H - (B ? 96 : 56);
    ctx.globalAlpha = a; ctx.textAlign = 'center';
    ctx.font = '400 ' + (W < 560 ? 21 : 27) + 'px "Pirata One",Georgia,serif';
    ctx.lineWidth = 5; ctx.strokeStyle = 'rgba(6,8,12,.9)'; ctx.strokeText(v.txt, W / 2, vy);
    ctx.fillStyle = v.col; ctx.fillText(v.txt, W / 2, vy);
    ctx.globalAlpha = 1;
  }
  if (G.paused) { ctx.fillStyle = 'rgba(6,8,12,.6)'; ctx.fillRect(0, 0, W, H);""")

# --- the chill on the player reads too ------------------------------------
edit(L, """  if (hurtV > 0) { const g = ctx.createRadialGradient(W / 2, H / 2, Math.min(W, H) * .3, W / 2, H / 2, Math.max(W, H) * .7); g.addColorStop(0, 'rgba(217,83,79,0)'); g.addColorStop(1, 'rgba(217,83,79,' + hurtV * 1.6 + ')'); ctx.fillStyle = g; ctx.fillRect(0, 0, W, H); }""",
     """  if (hurtV > 0) { const g = ctx.createRadialGradient(W / 2, H / 2, Math.min(W, H) * .3, W / 2, H / 2, Math.max(W, H) * .7); g.addColorStop(0, 'rgba(217,83,79,0)'); g.addColorStop(1, 'rgba(217,83,79,' + hurtV * 1.6 + ')'); ctx.fillStyle = g; ctx.fillRect(0, 0, W, H); }
  const chillV = Math.max(0, ...G.players.map(p => p.chill || 0));
  if (chillV > 0) { const g = ctx.createRadialGradient(W / 2, H / 2, Math.min(W, H) * .25, W / 2, H / 2, Math.max(W, H) * .72); g.addColorStop(0, 'rgba(143,211,255,0)'); g.addColorStop(1, 'rgba(143,211,255,' + Math.min(.4, chillV * .22) + ')'); ctx.fillStyle = g; ctx.fillRect(0, 0, W, H); }""")

# --- input: the potion key -------------------------------------------------
edit(L, """  a.aim = aim; a.fire = fire; a.sp = !!(keys.KeyE || keys.KeyQ || spTouch); a.dash = !!(keys.ShiftLeft || keys.KeyK || (!co && keys.ShiftRight) || dashTouch);""",
     """  a.aim = aim; a.fire = fire; a.sp = !!(keys.KeyE || keys.KeyQ || spTouch); a.dash = !!(keys.ShiftLeft || keys.KeyK || (!co && keys.ShiftRight) || dashTouch);
  a.bomb = !!(keys.KeyF || keys.KeyR || bombTouch);""")

edit(L, """    b.fire = !!(keys.Enter || keys.NumpadEnter || keys.Numpad0); b.dash = !!(keys.ShiftRight || keys.Slash || keys.Numpad1); b.sp = !!(keys.ControlRight || keys.Period || keys.Numpad2);""",
     """    b.fire = !!(keys.Enter || keys.NumpadEnter || keys.Numpad0); b.dash = !!(keys.ShiftRight || keys.Slash || keys.Numpad1); b.sp = !!(keys.ControlRight || keys.Period || keys.Numpad2);
    b.bomb = !!(keys.AltRight || keys.Numpad3 || keys.Comma);""")

edit(L, """let spTouch = false, dashTouch = false, clock = 0;""",
     """let spTouch = false, dashTouch = false, bombTouch = false, clock = 0;""")

edit(L, """$('spBtn').addEventListener('pointerdown', e => { e.stopPropagation(); spTouch = true; initAudio(); });
$('spBtn').addEventListener('pointerup', () => { spTouch = false; });""",
     """$('spBtn').addEventListener('pointerdown', e => { e.stopPropagation(); spTouch = true; initAudio(); });
$('spBtn').addEventListener('pointerup', () => { spTouch = false; });
$('bombBtn').addEventListener('pointerdown', e => { e.stopPropagation(); bombTouch = true; initAudio(); });
$('bombBtn').addEventListener('pointerup', () => { bombTouch = false; });""")

edit(L, """  if (e.code === 'KeyM') muted = !muted;""",
     """  if (e.code === 'KeyM') { muted = !muted; if (muted && typeof speechSynthesis !== 'undefined') try { speechSynthesis.cancel(); } catch (x) {} }
  if (e.code === 'KeyV') { voiceOn = !voiceOn; announce('Narrator ' + (voiceOn ? 'on' : 'off'), '#8fd3ff', !voiceOn); }""")

# --- the HUD gains a level, an experience bar, worn gear and potions -------
edit(L, """const mkHud = s => ({ box: $('hp' + s), hp: $('hpFill' + s), txt: $('hpTxt' + s), dash: $('dashFill' + s), sp: $('spFill' + s), name: $('clsName' + s) });""",
     """const mkHud = s => ({ box: $('hp' + s), hp: $('hpFill' + s), txt: $('hpTxt' + s), dash: $('dashFill' + s), sp: $('spFill' + s), name: $('clsName' + s), xp: $('xpFill' + s), lv: $('lv' + s), gear: $('gear' + s) });""")

edit(L, """function setHp(h, P) {
  h.hp.style.width = (P.hp / P.max * 100) + '%'; h.txt.textContent = P.down ? 'DOWN' : Math.ceil(P.hp) + ' / ' + P.max;""",
     """const SLOT_GLYPH = { weapon: 'W', armour: 'A', trinket: 'T' };
function setHp(h, P) {
  h.hp.style.width = (P.hp / P.max * 100) + '%'; h.txt.textContent = P.down ? 'DOWN' : Math.ceil(P.hp) + ' / ' + P.max;
  h.hp.style.background = P.hp / P.max < .34 ? '#ff2f28' : '';
  h.xp.style.width = clamp(P.xp / xpNeed(P.plvl), 0, 1) * 100 + '%';
  h.lv.textContent = 'LV ' + P.plvl;
  for (const sp of h.gear.children) {
    const it = P.gear[sp.dataset.s];
    sp.textContent = SLOT_GLYPH[sp.dataset.s];
    sp.style.color = it ? it.col : '#454c5e';
    sp.style.borderColor = it ? it.col : '#2d3548';
    sp.title = it ? it.name + ' \\u2014 ' + itemLines(it).join(', ') : 'No ' + sp.dataset.s;
  }""")

edit(L, """  hud.comboBox.hidden = G.combo < 2;""",
     """  hud.bombs.textContent = G.bombs; hud.bombBox.hidden = false;
  $('bombBtn').style.opacity = G.bombs > 0 ? '1' : '.35';
  hud.comboBox.hidden = G.combo < 2;""")

edit(L, """const hud1 = mkHud(''), hud2 = mkHud('2'), hud = { lvl: $('lvl'), gold: $('gold'), keys: $('keys'), combo: $('combo'), comboBox: $('comboBox') };""",
     """const hud1 = mkHud(''), hud2 = mkHud('2'), hud = { lvl: $('lvl'), gold: $('gold'), keys: $('keys'), combo: $('combo'), comboBox: $('comboBox'), bombs: $('bombs'), bombBox: $('bombBox') };""")

run()
