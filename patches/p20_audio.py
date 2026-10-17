from patch import edit, run

L = 'part_logic.js'

OLD = """/* ---------- audio ---------- */
let AC = null, muted = false;
function initAudio() {
  if (!AC) { try { AC = new (window.AudioContext || window.webkitAudioContext)(); } catch (e) { AC = null; } }
  if (AC && AC.state === 'suspended') AC.resume();
}
const SFX = { shoot: [520, .05, 'square', .03], hit: [180, .07, 'sawtooth', .04], coin: [880, .08, 'triangle', .05], hurt: [110, .18, 'sawtooth', .08], dash: [300, .1, 'sine', .04], boom: [70, .25, 'sawtooth', .07], bone: [400, .06, 'square', .03], door: [140, .2, 'triangle', .07], stairs: [330, .4, 'triangle', .07], swing: [240, .09, 'sawtooth', .04] };
function sfx(k) {
  if (muted || !AC || !SFX[k]) return;
  const p = SFX[k], t = AC.currentTime, o = AC.createOscillator(), g = AC.createGain();
  o.type = p[2]; o.frequency.setValueAtTime(p[0], t);
  o.frequency.exponentialRampToValueAtTime(Math.max(40, p[0] * .5), t + p[1]);
  g.gain.setValueAtTime(p[3], t); g.gain.exponentialRampToValueAtTime(.0001, t + p[1]);
  o.connect(g); g.connect(AC.destination); o.start(t); o.stop(t + p[1] + .02);
}"""

NEW = """/* ---------- audio ----------
   Everything is synthesised: a drone that retunes per zone, a sparse score that
   quickens when you are hurt or a boss is awake, and layered one-shots. */
let AC = null, muted = false, musicOn = true;
let masterG = null, sfxG = null, musG = null, ambG = null, noiseBuf = null, amb = null;
const ZONE_ROOT = [55, 49, 58.27, 61.74, 51.91, 46.25];
function initAudio() {
  if (!AC) {
    try { AC = new (window.AudioContext || window.webkitAudioContext)(); } catch (e) { AC = null; return; }
    try {
      masterG = AC.createGain(); masterG.gain.value = muted ? 0 : .9; masterG.connect(AC.destination);
      sfxG = AC.createGain(); sfxG.gain.value = .9; sfxG.connect(masterG);
      musG = AC.createGain(); musG.gain.value = 0; musG.connect(masterG);
      ambG = AC.createGain(); ambG.gain.value = 0; ambG.connect(masterG);
      const n = Math.floor(AC.sampleRate * 2);
      noiseBuf = AC.createBuffer(1, n, AC.sampleRate);
      const d = noiseBuf.getChannelData(0);
      for (let i = 0; i < n; i++) d[i] = Math.random() * 2 - 1;
      startAmbience();
    } catch (e) {}
  }
  if (AC && AC.state === 'suspended') { try { AC.resume(); } catch (e) {} }
}
function startAmbience() {
  if (!AC || amb) return;
  amb = { oscs: [], filt: AC.createBiquadFilter() };
  amb.filt.type = 'lowpass'; amb.filt.frequency.value = 300; amb.filt.Q.value = 1.6; amb.filt.connect(ambG);
  for (let i = 0; i < 3; i++) {
    const o = AC.createOscillator(), g = AC.createGain();
    o.type = i === 2 ? 'triangle' : 'sawtooth'; g.gain.value = i === 2 ? .05 : .075;
    o.frequency.value = 55 * [1, 1.5, 2.005][i];
    o.connect(g); g.connect(amb.filt); o.start();
    amb.oscs.push(o);
  }
  const ns = AC.createBufferSource(); ns.buffer = noiseBuf; ns.loop = true;
  const nf = AC.createBiquadFilter(); nf.type = 'lowpass'; nf.frequency.value = 420;
  const ng = AC.createGain(); ng.gain.value = .05;
  ns.connect(nf); nf.connect(ng); ng.connect(ambG); ns.start();
  const lfo = AC.createOscillator(), lg = AC.createGain();
  lfo.frequency.value = .07; lg.gain.value = .035; lfo.connect(lg); lg.connect(ng.gain); lfo.start();
  amb.wind = nf;
  tuneAmbience();
}
function tuneAmbience() {
  if (!amb || !AC) return;
  const z = ((G.zone || ZONES[0]).id) % ZONE_ROOT.length, r = ZONE_ROOT[z], t = AC.currentTime, rat = [1, 1.5, 2.005];
  try {
    amb.oscs.forEach((o, i) => o.frequency.setTargetAtTime(r * rat[i], t, 1.2));
    amb.filt.frequency.setTargetAtTime(250 + z * 26, t, 1.5);
    amb.wind.frequency.setTargetAtTime(340 + z * 40, t, 1.5);
  } catch (e) {}
}
function setMix(playing) {
  if (!AC || !ambG) return;
  try {
    ambG.gain.setTargetAtTime(playing ? .5 : .12, AC.currentTime, .5);
    musG.gain.setTargetAtTime(playing && musicOn ? .5 : 0, AC.currentTime, .6);
  } catch (e) {}
}
function setMuted(m) {
  muted = m;
  if (AC && masterG) { try { masterG.gain.setTargetAtTime(m ? 0 : .9, AC.currentTime, .05); } catch (e) {} }
  if (m && typeof speechSynthesis !== 'undefined') { try { speechSynthesis.cancel(); } catch (e) {} }
}
/* --- one-shot voices --- */
function tone(t, f, dur, type, gain, dest, f2) {
  const o = AC.createOscillator(), g = AC.createGain();
  o.type = type; o.frequency.setValueAtTime(f, t);
  if (f2) o.frequency.exponentialRampToValueAtTime(Math.max(20, f2), t + dur);
  g.gain.setValueAtTime(.0001, t); g.gain.linearRampToValueAtTime(gain, t + .006);
  g.gain.exponentialRampToValueAtTime(.0001, t + dur);
  o.connect(g); g.connect(dest || sfxG); o.start(t); o.stop(t + dur + .03);
}
function nz(t, dur, gain, type, f, q, dest) {
  const s = AC.createBufferSource(); s.buffer = noiseBuf; s.loop = true;
  const bf = AC.createBiquadFilter(); bf.type = type || 'bandpass'; bf.frequency.setValueAtTime(f, t); if (q) bf.Q.value = q;
  const g = AC.createGain(); g.gain.setValueAtTime(gain, t); g.gain.exponentialRampToValueAtTime(.0001, t + dur);
  s.connect(bf); bf.connect(g); g.connect(dest || sfxG); s.start(t); s.stop(t + dur + .03);
}
const SFXF = {
  shoot: t => { tone(t, 620, .07, 'square', .045, null, 250); nz(t, .05, .025, 'highpass', 1800); },
  hit: t => { nz(t, .07, .1, 'bandpass', 900, 1.2); tone(t, 185, .09, 'triangle', .06, null, 90); },
  crit: t => { tone(t, 1250, .12, 'triangle', .08, null, 720); nz(t, .11, .08, 'highpass', 2400); tone(t + .03, 1870, .1, 'sine', .045); },
  swing: t => { nz(t, .13, .06, 'bandpass', 760, .7); },
  coin: t => { tone(t, 1180, .07, 'triangle', .06); tone(t + .05, 1560, .1, 'triangle', .05); },
  gear: t => { tone(t, 880, .16, 'sine', .055); tone(t + .07, 1320, .18, 'sine', .045); tone(t + .14, 1760, .24, 'triangle', .04); nz(t, .2, .02, 'highpass', 3200); },
  hurt: t => { tone(t, 225, .22, 'sawtooth', .1, null, 70); nz(t, .16, .08, 'lowpass', 700); },
  dash: t => { nz(t, .18, .055, 'bandpass', 1400, .6); tone(t, 400, .14, 'sine', .035, null, 900); },
  boom: t => { tone(t, 125, .5, 'sine', .17, null, 32); nz(t, .4, .14, 'lowpass', 900); nz(t, .12, .07, 'highpass', 2200); },
  bone: t => { nz(t, .05, .08, 'bandpass', 2200, 3); tone(t, 430, .05, 'square', .035, null, 300); },
  door: t => { tone(t, 92, .35, 'sine', .13, null, 50); nz(t, .18, .06, 'lowpass', 520); },
  stairs: t => { [0, 4, 7, 12].forEach((s, i) => tone(t + i * .07, 330 * Math.pow(2, s / 12), .3, 'triangle', .055)); },
  level: t => { [0, 4, 7, 12, 16].forEach((s, i) => tone(t + i * .08, 392 * Math.pow(2, s / 12), .45, 'triangle', .06)); nz(t, .5, .025, 'highpass', 3000); },
  elite: t => { tone(t, 150, .7, 'sawtooth', .09, null, 110); tone(t + .02, 159, .7, 'sawtooth', .07, null, 117); nz(t, .5, .06, 'lowpass', 600); },
  ward: t => { tone(t, 700, .14, 'sine', .05, null, 1100); nz(t, .1, .04, 'bandpass', 1600, 2); }
};
const sfxLast = {};
function sfx(k) {
  if (muted || !AC || !SFXF[k]) return;
  const now = AC.currentTime;
  if (sfxLast[k] && now - sfxLast[k] < .028) return;
  sfxLast[k] = now;
  try { SFXF[k](now + .002); } catch (e) {}
}
/* --- the score: scheduled a little ahead of the clock --- */
let musT = 0, musStep = 0;
const PENTA = [0, 3, 5, 7, 10];
function musicTick() {
  if (!AC || !musG || muted || !musicOn) return;
  if (G.state === 'menu') { musT = 0; return; }
  const alive = G.players.filter(p => !p.down);
  const lowHp = alive.length ? Math.min(...alive.map(p => p.hp / p.max)) : 1;
  const boss = G.enemies.some(e => e.boss && e.alert && e.hp > 0);
  const intensity = boss ? 2 : lowHp < .3 ? 1.5 : 1;
  const bpm = 58 + Math.min(34, G.level * 2.1) + (intensity - 1) * 26;
  const beat = 60 / bpm / 2;
  const now = AC.currentTime;
  if (!musT || musT < now - 1) musT = now + .06;
  let guard = 0;
  while (musT < now + .35 && guard++ < 32) { scheduleBeat(musT, musStep++, intensity, lowHp); musT += beat; }
}
function scheduleBeat(t, step, intensity, lowHp) {
  const z = ((G.zone || ZONES[0]).id) % ZONE_ROOT.length, root = ZONE_ROOT[z] * 2, s = step % 16;
  try {
    if (s === 0 || s === 6 || s === 10) tone(t, root, .5, 'triangle', .14, musG);
    if (s === 0) tone(t, root * 1.5, 1.7, 'sine', .06, musG);
    if (intensity >= 2 && (s === 4 || s === 12)) { tone(t, root * .5, .34, 'square', .07, musG); nz(t, .14, .05, 'lowpass', 400, 0, musG); }
    if (lowHp < .3 && (s % 4 === 0)) tone(t, root * 2, .1, 'sine', .07, musG);
    if ((s === 3 || s === 11 || s === 14) && Math.random() < .45 + intensity * .12) {
      const f = root * 4 * Math.pow(2, PENTA[rint(0, 4)] / 12);
      tone(t, f, .9, 'triangle', .042, musG);
    }
    if (s === 8 && Math.random() < .3) tone(t, root * 3 * Math.pow(2, PENTA[rint(0, 4)] / 12), 1.4, 'sine', .03, musG);
  } catch (e) {}
}"""

edit(L, OLD, NEW)

# --- hooks: retune on a new depth, run the scheduler, follow the game state ---
edit(L, """  G.zone = zoneOf(G.level); G.hitstop = 0;""",
     """  G.zone = zoneOf(G.level); G.hitstop = 0; tuneAmbience();""")

edit(L, """  const dt = Math.min(.05, (now - last) / 1000); last = now; clock += dt;""",
     """  const dt = Math.min(.05, (now - last) / 1000); last = now; clock += dt;
  musicTick();
  const playing = G.state === 'play' || G.state === 'offer' || G.state === 'clear';
  if (playing !== wasPlaying) { wasPlaying = playing; setMix(playing); }""")

edit(L, """let last = performance.now(), overShown = false;""",
     """let last = performance.now(), overShown = false, wasPlaying = false;""")

edit(L, """  if (e.code === 'KeyM') { muted = !muted; if (muted && typeof speechSynthesis !== 'undefined') try { speechSynthesis.cancel(); } catch (x) {} }""",
     """  if (e.code === 'KeyM') setMuted(!muted);
  if (e.code === 'KeyN') { musicOn = !musicOn; setMix(G.state === 'play'); announce('Music ' + (musicOn ? 'on' : 'off'), '#8fd3ff', true); }""")

# --- the new voices get used where they belong ------------------------------
edit(L, """  if (crit) { G.fxs.push({ kind: 'crit', x: e.x, y: e.y - 4, t: 0, a: ang }); burstDir(e.x, e.y, ang, '#fff1b8', 10, 330, 1.1, 'spark', .45); G.shake = Math.max(G.shake, .16); }""",
     """  if (crit) { G.fxs.push({ kind: 'crit', x: e.x, y: e.y - 4, t: 0, a: ang }); burstDir(e.x, e.y, ang, '#fff1b8', 10, 330, 1.1, 'spark', .45); G.shake = Math.max(G.shake, .16); sfx('crit'); }""")

edit(L, """    e.ward -= dmg; e.wardFl = .18;
    burst(e.x, e.y, '#ffd24a', 4, 90, .6, 'spark'); text(e.x, e.y - e.r - 4, 'Blocked', '#ffd24a', 12); sfx('hit');""",
     """    e.ward -= dmg; e.wardFl = .18;
    burst(e.x, e.y, '#ffd24a', 4, 90, .6, 'spark'); text(e.x, e.y - e.r - 4, 'Blocked', '#ffd24a', 12); sfx('ward');""")

edit(L, """      announceOnce('lvl' + P.idx, .6, P.cls.name + ' reaches level ' + P.plvl, P.cls.col);""",
     """      announceOnce('lvl' + P.idx, .6, P.cls.name + ' reaches level ' + P.plvl, P.cls.col); sfx('level');""")

edit(L, """  text(P.x, P.y - 26, it.name, it.col, 13); sfx('stairs');""",
     """  text(P.x, P.y - 26, it.name, it.col, 13); sfx('gear');""")

edit(L, """  G.drops++;
  burstDir(x, y, -Math.PI / 2, it.col, 12, 210, 1.1, 'spark', .8);
  sfx('coin');""",
     """  G.drops++;
  burstDir(x, y, -Math.PI / 2, it.col, 12, 210, 1.1, 'spark', .8);
  sfx('gear');""")

edit(L, """  if (eaff.indexOf('fast') >= 0) E.spd *= 1.55;""",
     """  if (elite && G.state === 'play') sfx('elite');
  if (eaff.indexOf('fast') >= 0) E.spd *= 1.55;""")

run()
