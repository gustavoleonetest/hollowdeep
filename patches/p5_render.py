from patch import edit, run

L = 'part_logic.js'
H = 'part_head.html'

# --- spike rendering --------------------------------------------------------
edit(L, """function drawProp(p) {
  if (!sprOk('props')) return;""",
     """function drawHazard(h) {
  const warn = h.warn, up = h.up;
  ctx.save(); ctx.translate(h.x, h.y);
  ctx.fillStyle = 'rgba(6,8,14,.5)'; ctx.beginPath(); ctx.ellipse(0, 2, h.r, h.r * .5, 0, 0, TAU); ctx.fill();
  ctx.strokeStyle = warn ? 'rgba(255,120,80,' + (.4 + .45 * Math.sin(clock * 24)) + ')' : 'rgba(141,147,168,.3)';
  ctx.lineWidth = warn ? 2 : 1.3; ctx.beginPath(); ctx.ellipse(0, 2, h.r - 1.5, (h.r - 1.5) * .5, 0, 0, TAU); ctx.stroke();
  ctx.fillStyle = 'rgba(141,147,168,.18)';
  for (let i = 0; i < 4; i++) { const a = i / 4 * TAU + .4; ctx.beginPath(); ctx.ellipse(Math.cos(a) * 6.5, Math.sin(a) * 3.2 + 2, 2.6, 1.4, 0, 0, TAU); ctx.fill(); }
  if (up > .02) {
    if (up > .5) glow(0, 0, 26, '#d5d9e6', .12);
    for (let i = 0; i < 4; i++) {
      const a = i / 4 * TAU + .4, px = Math.cos(a) * 6.5, py = Math.sin(a) * 3.2 + 2, hh = 15 * up;
      ctx.fillStyle = '#6e7788'; ctx.beginPath(); ctx.moveTo(px - 2.8, py); ctx.lineTo(px, py - hh); ctx.lineTo(px + 2.8, py); ctx.fill();
      ctx.fillStyle = '#d5d9e6'; ctx.beginPath(); ctx.moveTo(px - .9, py); ctx.lineTo(px, py - hh); ctx.lineTo(px + 1, py); ctx.fill();
    }
  }
  ctx.restore();
}
function drawProp(p) {
  if (!sprOk('props')) return;""")

# --- the bloat borrows the puglin rig, scaled up and gone green -------------
edit(L, """  hound: { key: 'foe_zombie', fy: 8, bar: -42, sc: 1.3 }, warden: { key: 'boss_vampire', fy: 18, bar: -88, sc: 1.2 }
};""", """  hound: { key: 'foe_zombie', fy: 8, bar: -42, sc: 1.3 }, warden: { key: 'boss_vampire', fy: 18, bar: -88, sc: 1.2 },
  bloat: { key: 'foe_puglin', fy: 9, bar: -50, sc: 1.8 }
};""")

edit(L, """  if (useSpr) drawFoeSpr(e, mv); else ({ gloam: drawGloam, wisp: drawWisp, bonewalker: drawBone, brute: drawBrute, hound: drawHound, warden: drawWarden })[e.type](e, mv);
  if (e.hp < e.max && !e.boss) { const w = e.r * 2 + 6, top = useSpr ? e.y + SF.bar : e.type === 'brute' ? e.y - 30 : e.y - e.r - 14; ctx.fillStyle = '#0a0c11'; ctx.fillRect(e.x - w / 2, top, w, 3); ctx.fillStyle = C.blood; ctx.fillRect(e.x - w / 2, top, w * e.hp / e.max, 3); }""",
     """  if (useSpr) drawFoeSpr(e, mv); else ({ gloam: drawGloam, wisp: drawWisp, bonewalker: drawBone, brute: drawBrute, hound: drawHound, bloat: drawGloam, warden: drawWarden })[e.type](e, mv);
  if (e.hp < e.max && !e.boss) { const w = e.r * 2 + 6, hb = e.elite ? 4 : 3, top = useSpr ? e.y + (SF ? SF.bar : -40) : e.type === 'brute' ? e.y - 30 : e.y - e.r - 14; ctx.fillStyle = '#0a0c11'; ctx.fillRect(e.x - w / 2, top, w, hb); ctx.fillStyle = e.elite ? '#ffd24a' : C.blood; ctx.fillRect(e.x - w / 2, top, w * e.hp / e.max, hb); }""")

# --- elite aura, bloat swell, boss charge telegraph -------------------------
edit(L, """  if (boss) {
    if (e.st === 'slam') {
      const p = Math.min(1, e.stt / .9);
      ctx.fillStyle = 'rgba(255,70,50,' + (.08 + p * .12) + ')'; ctx.beginPath(); ctx.arc(x, y, 120, 0, TAU); ctx.fill();
      ctx.strokeStyle = 'rgba(255,90,70,' + (.4 + p * .5) + ')'; ctx.lineWidth = 2; ctx.beginPath(); ctx.arc(x, y, 120, 0, TAU); ctx.stroke();
      ctx.fillStyle = 'rgba(255,90,70,' + (.16 + p * .25) + ')'; ctx.beginPath(); ctx.arc(x, y, 120 * p, 0, TAU); ctx.fill();
    }
    if (e.st === 'burst') glow(x, y, 60 + Math.sin(e.t * 30) * 6, '#ff5a46', .45);
    if (e.st === 'summon') glow(x, y, 70, '#9a6bd6', .5);
    glow(x, y, 54, e.ph === 2 ? '#ff4a3a' : e.col, e.ph === 2 ? .22 + Math.sin(e.t * 6) * .06 : .16);
  }
  const bob = ghost ? Math.sin(e.t * 3) * 2.5 - 5 : 0;
  shadow(x, y + S.fy + 1, e.r * (boss ? 1.15 : .95), e.r * .42, ghost ? .2 : .4);""",
     """  if (boss) {
    if (e.st === 'slam') {
      const p = Math.min(1, e.stt / .9);
      ctx.fillStyle = 'rgba(255,70,50,' + (.08 + p * .12) + ')'; ctx.beginPath(); ctx.arc(x, y, 120, 0, TAU); ctx.fill();
      ctx.strokeStyle = 'rgba(255,90,70,' + (.4 + p * .5) + ')'; ctx.lineWidth = 2; ctx.beginPath(); ctx.arc(x, y, 120, 0, TAU); ctx.stroke();
      ctx.fillStyle = 'rgba(255,90,70,' + (.16 + p * .25) + ')'; ctx.beginPath(); ctx.arc(x, y, 120 * p, 0, TAU); ctx.fill();
    }
    if (e.st === 'charge' && e.stt < .72) {
      const p = Math.min(1, e.stt / .68); ctx.save(); ctx.translate(x, y); ctx.rotate(e.ca != null ? e.ca : (e.face || 0));
      ctx.strokeStyle = 'rgba(255,90,70,' + (.18 + p * .5) + ')'; ctx.lineWidth = 7 + p * 11; ctx.setLineDash([15, 10]);
      ctx.beginPath(); ctx.moveTo(24, 0); ctx.lineTo(310, 0); ctx.stroke(); ctx.setLineDash([]); ctx.restore();
    }
    if (e.st === 'burst') glow(x, y, 60 + Math.sin(e.t * 30) * 6, '#ff5a46', .45);
    if (e.st === 'summon') glow(x, y, 70, '#9a6bd6', .5);
    glow(x, y, 54, e.ph >= 2 ? '#ff4a3a' : e.col, e.ph >= 2 ? .22 + Math.sin(e.t * 6) * .06 : .16);
  }
  if (e.type === 'bloat') {
    const f = e.fuse > 0 ? 1 - e.fuse / .6 : 0, pu = .5 + .5 * Math.sin(clock * (e.fuse > 0 ? 26 : 4));
    glow(x, y - 4, 40 + f * 36, e.fuse > 0 ? '#eaffc4' : '#8fbf5a', .2 + pu * (e.fuse > 0 ? .5 : .1));
  }
  if (e.elite) {
    const pu = .5 + .5 * Math.sin(clock * 3.2 + e.t);
    glow(x, y - 4, e.r * 3.4, '#ffd24a', .13 + pu * .08);
    ctx.save(); ctx.strokeStyle = 'rgba(255,210,74,' + (.3 + pu * .3) + ')'; ctx.lineWidth = 1.6;
    ctx.beginPath(); ctx.ellipse(x, y + S.fy, e.r * 1.5, e.r * .62, 0, 0, TAU); ctx.stroke();
    ctx.globalAlpha = .35; ctx.beginPath(); ctx.ellipse(x, y + S.fy, e.r * 1.5 * (1 + pu * .2), e.r * .62 * (1 + pu * .2), 0, 0, TAU); ctx.stroke(); ctx.restore();
  }
  const bob = ghost ? Math.sin(e.t * 3) * 2.5 - 5 : 0;
  shadow(x, y + S.fy + 1, e.r * (boss ? 1.15 : .95), e.r * .42, ghost ? .2 : .4);""")

edit(L, """  if (e.fl > 0) { const q = e.fl / .2 * (boss ? .35 : 1); sx *= 1 + .18 * q; sy *= 1 - .14 * q; rot += Math.cos(e.fa || 0) * .28 * q; }""",
     """  if (e.fl > 0) { const q = e.fl / .2 * (boss ? .35 : 1); sx *= 1 + .18 * q; sy *= 1 - .14 * q; rot += Math.cos(e.fa || 0) * .28 * q; }
  if (e.type === 'bloat' && e.fuse > 0) { const f = 1 - e.fuse / .6; sx *= 1 + f * .42; sy *= 1 + f * .42; }""")

edit(L, """  ctx.save(); ctx.translate(x + ox, y + S.fy + bob + oy); ctx.rotate(rot); ctx.scale(sx, sy); ctx.globalAlpha = fade * (ghost ? .92 : 1);
  sprChar(S.key, 0, 0, e.face || 0, kk, kc, S.sc, e.flash > 0 ? '#ffffff' : null, .85);""",
     """  let tint = null, ta = .85;
  if (e.flash > 0) tint = '#ffffff';
  else if (e.type === 'bloat') { tint = e.fuse > 0 ? '#eaffc4' : '#7fbf4a'; ta = e.fuse > 0 ? .72 : .5; }
  else if (e.elite) { tint = '#ffd98a'; ta = .3; }
  ctx.save(); ctx.translate(x + ox, y + S.fy + bob + oy); ctx.rotate(rot); ctx.scale(sx, sy); ctx.globalAlpha = fade * (ghost ? .92 : 1);
  sprChar(S.key, 0, 0, e.face || 0, kk, kc, S.sc, tint, ta);""")

# --- the warden's phase tint covers phase three too -------------------------
edit(L, """  const col = e.flash > 0 ? '#ffffff' : e.col, dk = mix(e.col, -.5), lt = mix(e.col, .35), x = e.x, y = e.y, ph = e.walk * .5, f = e.face || 0, p2 = e.ph === 2, t = e.t;""",
     """  const col = e.flash > 0 ? '#ffffff' : e.col, dk = mix(e.col, -.5), lt = mix(e.col, .35), x = e.x, y = e.y, ph = e.walk * .5, f = e.face || 0, p2 = e.ph >= 2, t = e.t;""")

edit(L, """ctx.fillStyle = B.ph === 2 ? '#ff4a3a' : C.blood;""", """ctx.fillStyle = B.ph >= 3 ? '#ff2a18' : B.ph >= 2 ? '#ff4a3a' : C.blood;""")

# --- crit starburst ---------------------------------------------------------
edit(L, """function drawShock(f) {""", """function drawCrit(f) {
  if (f.t > .3) return;
  const q = f.t / .3, al = 1 - q;
  ctx.save(); ctx.translate(f.x, f.y); ctx.rotate((f.a || 0) + q * .5);
  ctx.strokeStyle = 'rgba(255,241,184,' + al + ')'; ctx.lineWidth = 2.4 * al + .6;
  for (let i = 0; i < 4; i++) {
    const a = i / 4 * TAU + .4, r0 = 7 + q * 11, r1 = 21 + q * 31;
    ctx.beginPath(); ctx.moveTo(Math.cos(a) * r0, Math.sin(a) * r0); ctx.lineTo(Math.cos(a) * r1, Math.sin(a) * r1); ctx.stroke();
  }
  ctx.globalAlpha = al * .8; ctx.fillStyle = '#fff6d8'; ctx.beginPath(); ctx.arc(0, 0, 5 * (1 - q), 0, TAU); ctx.fill();
  ctx.restore(); ctx.globalAlpha = 1;
}
function drawShock(f) {""")

edit(L, """  for (const f of G.fxs) { if (f.kind === 'shock') drawShock(f); else if (f.kind === 'hit') {""",
     """  for (const f of G.fxs) { if (f.kind === 'shock') drawShock(f); else if (f.kind === 'crit') drawCrit(f); else if (f.kind === 'hit') {""")

# --- fog at twice the tile resolution, so its edge stops looking blocky -----
edit(L, """const fogCv = document.createElement('canvas'), fctx = fogCv.getContext('2d'); fogCv.width = MW; fogCv.height = MH;
const fogImg = fctx.createImageData(MW, MH); let fogA = new Float32Array(MW * MH).fill(1), fogRooms = null, fogT = 0;
const fogOn = () => G.state !== 'menu';
const fogAt = (x, y) => { if (!fogOn()) return 0; const tx = Math.floor(x / T), ty = Math.floor(y / T); return (tx < 0 || ty < 0 || tx >= MW || ty >= MH) ? 1 : fogA[ty * MW + tx]; };
function updateFog() {
  const now = performance.now(), dt = Math.min(.1, (now - fogT) / 1000); fogT = now;
  if (fogRooms !== G.rooms) { fogRooms = G.rooms; fogA.fill(1); }
  const ps = G.players.filter(p => !p.down); const src = ps.length ? ps : G.players, k = Math.min(1, dt * 9), d = fogImg.data;
  for (let y = 0; y < MH; y++) for (let x = 0; x < MW; x++) {
    let vis = 0; for (const p of src) { const dd = Math.hypot(x + .5 - p.x / T, y + .5 - p.y / T); const q = clamp((8.4 - dd) / 2.4, 0, 1); if (q > vis) vis = q; }
    const i = y * MW + x, tgt = G.seen[i] ? .62 * (1 - vis) : 1 - vis;
    fogA[i] += (tgt - fogA[i]) * k; const a = fogA[i];
    d[i * 4] = 5; d[i * 4 + 1] = 7; d[i * 4 + 2] = 11; d[i * 4 + 3] = Math.round(clamp(a, 0, 1) * 255);
  }
  fctx.putImageData(fogImg, 0, 0);
}""", """const FS = 2, FW = MW * FS, FH = MH * FS, FTS = T / FS;
const fogCv = document.createElement('canvas'), fctx = fogCv.getContext('2d'); fogCv.width = FW; fogCv.height = FH;
const fogImg = fctx.createImageData(FW, FH); let fogA = new Float32Array(FW * FH).fill(1), fogRooms = null, fogT = 0;
const fogOn = () => G.state !== 'menu';
const fogAt = (x, y) => { if (!fogOn()) return 0; const fx = Math.floor(x / FTS), fy = Math.floor(y / FTS); return (fx < 0 || fy < 0 || fx >= FW || fy >= FH) ? 1 : fogA[fy * FW + fx]; };
function updateFog() {
  const now = performance.now(), dt = Math.min(.1, (now - fogT) / 1000); fogT = now;
  if (fogRooms !== G.rooms) { fogRooms = G.rooms; fogA.fill(1); }
  const ps = G.players.filter(p => !p.down); const src = ps.length ? ps : G.players, k = Math.min(1, dt * 9), d = fogImg.data;
  for (let y = 0; y < FH; y++) for (let x = 0; x < FW; x++) {
    let vis = 0; for (const p of src) { const dd = Math.hypot((x + .5) / FS - p.x / T, (y + .5) / FS - p.y / T); const q = clamp((8.4 - dd) / 2.4, 0, 1); if (q > vis) vis = q; }
    const i = y * FW + x, tgt = G.seen[((y / FS) | 0) * MW + ((x / FS) | 0)] ? .62 * (1 - vis) : 1 - vis;
    fogA[i] += (tgt - fogA[i]) * k; const a = fogA[i];
    d[i * 4] = 5; d[i * 4 + 1] = 7; d[i * 4 + 2] = 11; d[i * 4 + 3] = Math.round(clamp(a, 0, 1) * 255);
  }
  fctx.putImageData(fogImg, 0, 0);
}""")

edit(L, """    mctx.globalAlpha = fogA[y * MW + x] < .3 ? 1 : .5;""",
     """    mctx.globalAlpha = fogA[(y * FS) * FW + x * FS] < .3 ? 1 : .5;""")

# --- a vignette to pull the eye in from the edges ---------------------------
edit(L, """    ctx.globalAlpha = .05 + .1 * (.5 + .5 * Math.sin(clock * 1.3 + i)); ctx.beginPath(); ctx.arc(x, y, .8 + (i % 3) * .5, 0, TAU); ctx.fill();
  }
  ctx.globalAlpha = 1;""",
     """    ctx.globalAlpha = .05 + .1 * (.5 + .5 * Math.sin(clock * 1.3 + i)); ctx.beginPath(); ctx.arc(x, y, .8 + (i % 3) * .5, 0, TAU); ctx.fill();
  }
  ctx.globalAlpha = 1;
  const vg = ctx.createRadialGradient(W / 2, H / 2, Math.min(W, H) * .4, W / 2, H / 2, Math.max(W, H) * .76);
  vg.addColorStop(0, 'rgba(3,5,9,0)'); vg.addColorStop(.6, 'rgba(3,5,9,.2)'); vg.addColorStop(1, 'rgba(3,5,9,.62)');
  ctx.fillStyle = vg; ctx.fillRect(0, 0, W, H);""")

# --- hazards sort in with everything else that stands on the floor ----------
edit(L, """  for (const pr of G.props) ents.push([pr.y, pr, drawProp]);""",
     """  for (const pr of G.props) ents.push([pr.y, pr, drawProp]);
  for (const hz of G.hazards) ents.push([hz.y, hz, drawHazard]);""")

# --- spikes read as light sources when they are out ------------------------
edit(L, """  for (const pr of G.props) if (pr.lit && !fz(pr.x, pr.y)) hole(pr.x, pr.y, pr.lit, .7);""",
     """  for (const pr of G.props) if (pr.lit && !fz(pr.x, pr.y)) hole(pr.x, pr.y, pr.lit, .7);
  for (const hz of G.hazards) if ((hz.warn || hz.up > .1) && !fz(hz.x, hz.y)) hole(hz.x, hz.y, 60, .45);""")

# --- the chain counter on the HUD ------------------------------------------
edit(H, """      <span>Keys <b id="keys">0</b></span>""",
     """      <span>Keys <b id="keys">0</b></span>
      <span id="comboBox" hidden>Chain <b id="combo">0</b></span>""")

edit(L, """const hud1 = mkHud(''), hud2 = mkHud('2'), hud = { lvl: $('lvl'), gold: $('gold'), keys: $('keys') };""",
     """const hud1 = mkHud(''), hud2 = mkHud('2'), hud = { lvl: $('lvl'), gold: $('gold'), keys: $('keys'), combo: $('combo'), comboBox: $('comboBox') };""")

edit(L, """  hud.lvl.textContent = G.level; hud.gold.textContent = G.gold; hud.keys.textContent = G.keys;""",
     """  hud.lvl.textContent = G.level; hud.gold.textContent = G.gold; hud.keys.textContent = G.keys;
  hud.comboBox.hidden = G.combo < 2;
  if (G.combo >= 2) { hud.combo.textContent = G.combo + '\\u00d7' + comboMult().toFixed(1); hud.combo.style.color = G.combo >= 15 ? '#fff1b8' : G.combo >= 8 ? '#ffd24a' : ''; }""")

run()
