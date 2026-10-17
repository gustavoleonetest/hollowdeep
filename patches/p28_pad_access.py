from patch import edit, run

L = 'part_logic.js'
H = 'part_head.html'

# --- gamepads: this is a twin-stick game, it should play like one ---------
edit(L, """function readInput() {""",
     """const PAD_DZ = .24;
function padAt(i) {
  try {
    if (!navigator.getGamepads) return null;
    const ps = navigator.getGamepads(); if (!ps) return null;
    let n = 0;
    for (let k = 0; k < ps.length; k++) { const p = ps[k]; if (!p || !p.connected) continue; if (n++ === i) return p; }
  } catch (e) {}
  return null;
}
function readPad(I, pad) {
  const ax = pad.axes[0] || 0, ay = pad.axes[1] || 0, rx = pad.axes[2] || 0, ry = pad.axes[3] || 0;
  const b = pad.buttons || [], bt = i => !!(b[i] && (b[i].pressed || b[i].value > .5));
  const lm = Math.hypot(ax, ay), rm = Math.hypot(rx, ry);
  let used = false, aimed = false;
  if (lm > PAD_DZ) { I.mx = ax; I.my = ay; used = true; }
  if (rm > PAD_DZ) { I.aim = Math.atan2(ry, rx); I.fire = true; used = true; aimed = true; }
  if (bt(7) || bt(0)) { I.fire = true; used = true; }
  if (bt(5) || bt(1)) { I.dash = true; used = true; }
  if (bt(4) || bt(2)) { I.sp = true; used = true; }
  if (bt(3) || bt(6)) { I.bomb = true; used = true; }
  if (used) { padSeen = true; initAudio(); }
  return { used, aimed };
}
let padSeen = false;
function readInput() {""")

edit(L, """  if (P2) {
    let x = 0, y = 0;""",
     """  const pd1 = padAt(0);
  if (pd1) { const r = readPad(a, pd1); if (r.used && !r.aimed) a.aim = assistAim(P1, (a.mx || a.my) ? Math.atan2(a.my, a.mx) : P1.face); }
  if (P2) {
    let x = 0, y = 0;""")

edit(L, """    b.bomb = !!(keys.AltRight || keys.Numpad3 || keys.Comma);""",
     """    b.bomb = !!(keys.AltRight || keys.Numpad3 || keys.Comma);
    const pd2 = padAt(1);
    if (pd2) { const r = readPad(b, pd2); if (r.used && !r.aimed) b.aim = assistAim(P2, (b.mx || b.my) ? Math.atan2(b.my, b.mx) : P2.face); }""")

# --- reduced motion --------------------------------------------------------
edit(L, """let spTouch = false, dashTouch = false, bombTouch = false, btnsOn = false, clock = 0;""",
     """let spTouch = false, dashTouch = false, bombTouch = false, btnsOn = false, clock = 0, reduceMotion = false;""")

edit(L, """loadMeta(); G.best = META.best || 0;
voiceOn = META.voice !== false; musicOn = META.music !== false;""",
     """loadMeta(); G.best = META.best || 0;
voiceOn = META.voice !== false; musicOn = META.music !== false;
if (META.reduceMotion === undefined || META.reduceMotion === null) {
  try { META.reduceMotion = !!(window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches); } catch (e) { META.reduceMotion = false; }
}
reduceMotion = !!META.reduceMotion;""")

edit(L, """  const sh = G.shake > 0 ? G.shake * 14 : 0,""",
     """  const sh = (G.shake > 0 && !reduceMotion) ? G.shake * 14 : 0,""")

edit(L, """  if (G.state === 'menu') { P.x += Math.cos(clock * .12) * 220; P.y += Math.sin(clock * .17) * 130; }""",
     """  if (G.state === 'menu' && !reduceMotion) { P.x += Math.cos(clock * .12) * 220; P.y += Math.sin(clock * .17) * 130; }""")

edit(L, """  if (G.flash > 0) { ctx.fillStyle = 'rgba(232,222,255,' + Math.min(.72, G.flash) + ')'; ctx.fillRect(0, 0, W, H); }""",
     """  if (G.flash > 0) { ctx.fillStyle = 'rgba(232,222,255,' + Math.min(.72, G.flash) * (reduceMotion ? .3 : 1) + ')'; ctx.fillRect(0, 0, W, H); }""")

edit(L, """function burst(x, y, col, n, sp, life, kind) {
  for (let i = 0; i < n; i++) {""",
     """function burst(x, y, col, n, sp, life, kind) {
  if (reduceMotion) n = Math.max(1, Math.round(n * .4));
  for (let i = 0; i < n; i++) {""")

edit(L, """function burstDir(x, y, ang, col, n, sp, life, kind, spread) {
  for (let i = 0; i < n; i++) {""",
     """function burstDir(x, y, ang, col, n, sp, life, kind, spread) {
  if (reduceMotion) n = Math.max(1, Math.round(n * .4));
  for (let i = 0; i < n; i++) {""")

edit(L, """  if (G.parts.length > 1400) G.parts.splice(0, G.parts.length - 1400);""",
     """  const cap = reduceMotion ? 450 : 1400;
  if (G.parts.length > cap) G.parts.splice(0, G.parts.length - cap);""")

# --- rarity also reads without colour -------------------------------------
edit(L, """    sp.style.color = it ? it.col : '#454c5e';
    sp.style.borderColor = it ? it.col : '#2d3548';""",
     """    sp.style.color = it ? it.col : '#454c5e';
    sp.style.borderColor = it ? it.col : '#2d3548';
    sp.style.borderStyle = it ? ({ magic: 'solid', rare: 'dashed', fabled: 'double', cursed: 'dotted' }[it.rar] || 'solid') : 'solid';
    sp.style.borderWidth = it && it.rar === 'fabled' ? '3px' : '1px';""")

# --- options the player can actually reach ---------------------------------
edit(L, """$('barrowBtn').addEventListener('click', () => showBarrow(true));""",
     """function syncOpts() {
  $('optMotion').textContent = 'Reduce motion: ' + (reduceMotion ? 'on' : 'off');
  $('optVoice').textContent = 'Narrator: ' + (voiceOn ? 'on' : 'off');
  $('optMusic').textContent = 'Music: ' + (musicOn ? 'on' : 'off');
}
$('optMotion').addEventListener('click', () => { reduceMotion = !reduceMotion; META.reduceMotion = reduceMotion; saveMeta(); syncOpts(); });
$('optVoice').addEventListener('click', () => { voiceOn = !voiceOn; META.voice = voiceOn; saveMeta(); syncOpts(); if (!voiceOn && typeof speechSynthesis !== 'undefined') { try { speechSynthesis.cancel(); } catch (e) {} } });
$('optMusic').addEventListener('click', () => { musicOn = !musicOn; META.music = musicOn; saveMeta(); syncOpts(); setMix(G.state === 'play'); });
$('barrowBtn').addEventListener('click', () => showBarrow(true));""")

edit(L, """function showMenu() { setMode(mode); $('menu').hidden = false;""",
     """function showMenu() { syncOpts(); setMode(mode); $('menu').hidden = false;""")

edit(L, """  if (e.code === 'KeyV') { voiceOn = !voiceOn; announce('Narrator ' + (voiceOn ? 'on' : 'off'), '#8fd3ff', !voiceOn); }""",
     """  if (e.code === 'KeyV') { voiceOn = !voiceOn; META.voice = voiceOn; saveMeta(); announce('Narrator ' + (voiceOn ? 'on' : 'off'), '#8fd3ff', !voiceOn); }""")

edit(L, """  if (e.code === 'KeyN') { musicOn = !musicOn; setMix(G.state === 'play'); announce('Music ' + (musicOn ? 'on' : 'off'), '#8fd3ff', true); }""",
     """  if (e.code === 'KeyN') { musicOn = !musicOn; META.music = musicOn; saveMeta(); setMix(G.state === 'play'); announce('Music ' + (musicOn ? 'on' : 'off'), '#8fd3ff', true); }""")

# --- markup ---------------------------------------------------------------
edit(H, """      <p class="sub" id="pickHint" aria-live="polite"></p>""",
     """      <div class="row" id="opts">
        <button class="btn alt" id="optMotion" type="button">Reduce motion: off</button>
        <button class="btn alt" id="optVoice" type="button">Narrator: on</button>
        <button class="btn alt" id="optMusic" type="button">Music: on</button>
      </div>
      <p class="sub" id="pickHint" aria-live="polite"></p>""")

run()
