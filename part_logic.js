'use strict';
/* Hollowdeep: game logic. Original characters, monsters and levels. */
const T = 32, MW = 52, MH = 38, TAU = Math.PI * 2;
const DIRS = [[1, 0], [-1, 0], [0, 1], [0, -1]];
const rnd = (a, b) => a + Math.random() * (b - a);
const rint = (a, b) => Math.floor(rnd(a, b + 1));
const clamp = (v, a, b) => Math.max(a, Math.min(b, v));

const CLASSES = {
  bulwark: { key: 'bulwark', name: 'Bulwark', blurb: 'Plated knight. Wide sword sweep hits everything in front. Soaks damage.', hp: 170, spd: 2.2, col: '#e7b04a', atk: 'melee', dmg: 18, cd: 0.4, range: 72, arc: 2.0, armor: 0.72, m: [1, .55, .6] },
  ember: { key: 'ember', name: 'Ember', blurb: 'Fire mage. Slow bolts burst on impact and burn crowds.', hp: 90, spd: 2.25, col: '#ff6a4d', atk: 'fire', dmg: 22, cd: 0.52, shot: 6.5, rad: 54, armor: 1, m: [.5, .65, .75] },
  sable: { key: 'sable', name: 'Sable', blurb: 'Quick rogue. Rapid thrown daggers, fastest on her feet.', hp: 100, spd: 3.1, col: '#7fd1c7', atk: 'dagger', dmg: 7, cd: 0.13, shot: 10, armor: 1, m: [.55, 1, 1] },
  thistle: { key: 'thistle', name: 'Thistle', blurb: 'Ranger. Long piercing arrows that pass through several foes.', hp: 115, spd: 2.6, col: '#9bd16a', atk: 'arrow', dmg: 13, cd: 0.33, shot: 12, armor: 1, m: [.62, .8, .65] }
};
const FOES = {
  gloam: { hp: 26, spd: .95, r: 11, dmg: 9, col: '#9a6bd6', gold: .45 },
  wisp: { hp: 12, spd: 1.9, r: 8, dmg: 5, col: '#6fd3ff', gold: .3 },
  bonewalker: { hp: 34, spd: .9, r: 11, dmg: 7, col: '#d8d2bd', gold: .7 },
  brute: { hp: 110, spd: .75, r: 15, dmg: 20, col: '#c2563f', gold: 1.5 },
  hound: { hp: 30, spd: 1.0, r: 10, dmg: 11, col: '#b9893f', gold: .5 },
  bloat: { hp: 44, spd: .82, r: 13, dmg: 13, col: '#8fbf5a', gold: .85 },
  thief: { hp: 46, spd: 2.5, r: 10, dmg: 0, col: '#c9a24a', gold: 0 },
  reaper: { hp: 99999, spd: .62, r: 15, dmg: 0, col: '#dfe4ef', gold: 0 },
  warden: { hp: 380, spd: .7, r: 22, dmg: 16, col: '#8d93a8', gold: 0 }
};
const ZONES = [
  { id: 0, name: 'The Crypts', dec: 0, tint: null, amb: '#f0a23c', boss: 'Count Hollow', bcol: '#8d93a8' },
  { id: 1, name: 'The Drowned Halls', dec: 1, tint: 'rgba(40,120,160,.17)', amb: '#5fc4e8', boss: 'The Drowned Choir', bcol: '#4fa3b8' },
  { id: 2, name: 'Mossroot Caverns', dec: 2, tint: 'rgba(70,130,50,.16)', amb: '#9bd16a', boss: 'The Mossroot Maw', bcol: '#7aa05a' },
  { id: 3, name: 'The Cinder Vaults', dec: 3, tint: 'rgba(190,70,20,.17)', amb: '#ff7a3a', boss: 'The Cinder Count', bcol: '#c2563f' },
  { id: 4, name: 'The Bone Gardens', dec: 4, tint: 'rgba(150,140,110,.13)', amb: '#e8dfc0', boss: 'The Pale Chorister', bcol: '#d8d2bd' },
  { id: 5, name: 'The Obsidian Reach', dec: 5, tint: 'rgba(92,58,150,.18)', amb: '#b98cff', boss: 'The Obsidian Maw', bcol: '#8a6bd6' }
];
const zoneOf = L => ZONES[Math.floor((L - 1) / 3) % ZONES.length];
/* The Count presses you, the Choir keeps its distance and raises the dead,
   the Maw never stops moving. Each zone draws one of the three. */
const BOSSES = {
  count: { spr: 'boss_vampire', sc: 1.2, fy: 18, bar: -88, r: 22, hpm: 1, spdm: 1, dmgm: 1, glow: '#b06a8a',
    acts: { 1: ['slam', 'burst'], 2: ['slam', 'burst', 'summon', 'burst'], 3: ['charge', 'burst', 'slam', 'summon', 'burst', 'charge'] } },
  caller: { spr: 'foe_skeleton', sc: 1.95, fy: 14, bar: -78, r: 20, hpm: .86, spdm: 1.14, dmgm: .9, glow: '#9a6bd6',
    acts: { 1: ['volley', 'raise'], 2: ['volley', 'blink', 'raise', 'volley'], 3: ['blink', 'volley', 'raise', 'volley', 'blink'] } },
  maw: { spr: 'foe_orc', sc: 1.95, fy: 16, bar: -80, r: 24, hpm: 1.24, spdm: .9, dmgm: 1.2, glow: '#e0702f',
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
/* it remembers every warden you put down on the way here */
BOSSES.heart = { spr: 'boss_vampire', sc: 1.62, fy: 22, bar: -104, r: 30, hpm: 2.3, spdm: .88, dmgm: 1.25, glow: '#ff3b5c',
  acts: { 1: ['slam', 'wail', 'volley', 'burst'],
          2: ['pillars', 'shards', 'raise', 'burst', 'wail'],
          3: ['ward', 'rampage', 'pillars', 'shards', 'wail', 'comet'] } };
const FINAL_DEPTH = 21;
const isFinalLvl = L => L === FINAL_DEPTH;
const HEART_NAME = 'The Hollow Heart';
const BOSS_KIND = ['count', 'caller', 'maw', 'pyre', 'chorister', 'obsidian'];
const bossKindOf = L => BOSS_KIND[zoneOf(L).id % BOSS_KIND.length];
const BOSS_DUR = { slam: .9, burst: .6, summon: .7, charge: 1.42, volley: 1, blink: .5, raise: .8, quake: 1, rampage: 2.1,
  pillars: .95, comet: .8, wail: 1.15, ward: .9, shards: 1 };
const isBossLvl = L => L % 3 === 0;

const G = { state: 'menu', paused: false, level: 1, map: null, seen: null, rooms: [], player: null, enemies: [], nests: [], shots: [], eshots: [], items: [], parts: [], texts: [], torches: [], decals: [], dying: [], fxs: [], mapVer: 0, props: [], hitstop: 0, zone: ZONES[0], exit: null, door: null, flow: null, flowT: 0, shake: 0, score: 0, best: 0, banner: null, slash: null, clsKey: 'bulwark', clsKeys: ['bulwark'], players: [], keys: 0, gold: 0, co: false, hazards: [], combo: 0, comboT: 0, comboBest: 0,
  bombs: 0, bolts: [], voice: null, flash: 0, offerQ: [], drops: 0, wares: [], event: null, zones: [], timers: [] };
const INS = [{ mx: 0, my: 0, aim: 0, fire: false, dash: false, sp: false }, { mx: 0, my: 0, aim: 0, fire: false, dash: false, sp: false }];
const SEPX = 430, SEPY = 250;

/* ---------- audio ----------
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
  omen: t => {
    tone(t, 70, 1.5, 'sine', .11, null, 58);
    tone(t + .06, 99, 1.35, 'triangle', .05, null, 92);
    tone(t + .12, 140, 1.1, 'sine', .035, null, 132);
    nz(t, 1.3, .045, 'lowpass', 420);
    nz(t + .1, .5, .02, 'bandpass', 1300, .8);
  },
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
}

/* ---------- what you carry out of the dark ----------
   A run always ends. Echoes are what is left of it, and they buy the small
   advantages that make the next descent reach further. */
const META_KEY = 'hollowdeep-meta';
const META = { best: 0, echoes: 0, perks: {}, runs: 0, deepest: 1, wins: 0, taught: {}, reduceMotion: false, voice: true, music: true };
const TAUGHT = [
  ['drain', 'Your health drains the whole way down \u2014 the shaded part of your bar is the next ten seconds of it. Food is the only thing that gives it back.'],
  ['crypt', 'A crypt. It keeps sending them up until you break it.'],
  ['door', 'The way down is locked. The key is somewhere on this floor.'],
];
function teach(id) {
  if (!META.taught || META.taught[id]) return;
  const row = TAUGHT.find(t => t[0] === id); if (!row) return;
  META.taught[id] = 1; saveMeta();
  announce(row[1], '#8fd3ff');
}
/* a whole number at least `lo`, or the fallback if it is anything else */
function metaNum(v, dflt, lo) {
  const n = typeof v === 'number' ? v : parseFloat(v);
  return Number.isFinite(n) ? Math.max(lo, Math.floor(n)) : dflt;
}
function loadMeta() {
  try {
    const raw = JSON.parse(localStorage.getItem(META_KEY) || '{}');
    if (raw && typeof raw === 'object') {
      META.best = metaNum(raw.best, 0, 0);
      META.echoes = metaNum(raw.echoes, 0, 0);
      META.runs = metaNum(raw.runs, 0, 0);
      META.wins = metaNum(raw.wins, 0, 0);
      META.deepest = metaNum(raw.deepest, 1, 1);
      /* only a real boolean counts: anything else leaves the default, and
         null still means "has not been chosen yet" for reduced motion */
      for (const k of ['voice', 'music']) if (typeof raw[k] === 'boolean') META[k] = raw[k];
      if (typeof raw.reduceMotion === 'boolean' || raw.reduceMotion === null) META.reduceMotion = raw.reduceMotion;
      META.taught = {};
      if (raw.taught && typeof raw.taught === 'object') {
        for (const t of TAUGHT) if (raw.taught[t[0]]) META.taught[t[0]] = 1;
      }
      META.perks = {};
      if (raw.perks && typeof raw.perks === 'object') {
        for (const p of PERKS) {
          const lv = metaNum(raw.perks[p.id], 0, 0);
          if (lv > 0) META.perks[p.id] = Math.min(p.max, lv);
        }
      }
    }
    const old = parseInt(localStorage.getItem('hollowdeep-best') || '0', 10);
    if (Number.isFinite(old) && old > META.best) META.best = old;
  } catch (e) {}
}
function saveMeta() { try { localStorage.setItem(META_KEY, JSON.stringify(META)); } catch (e) {} }
/* Write something, read it back, take it away again. Nothing short of the
   round trip will do: a private window hands you a store that reads fine and
   throws only when you try to keep something, and some setups throw on the
   mere mention of localStorage. Asked once and remembered, since this cannot
   change while the page is open -- `recheck` is for the tests. */
let storageOk = null;
function storageWorks(recheck) {
  if (storageOk !== null && !recheck) return storageOk;
  storageOk = false;
  try {
    const k = 'hollowdeep-probe', v = String(Date.now());
    localStorage.setItem(k, v);
    const back = localStorage.getItem(k);
    localStorage.removeItem(k);
    storageOk = back === v;
  } catch (e) { storageOk = false; }
  return storageOk;
}
/* ---------- the run you left behind ---------- */
const RUN_KEY = 'hollowdeep-run';
let pendingRun = null;
function saveRun() {
  if (!G.players || !G.players.length) return;
  try {
    localStorage.setItem(RUN_KEY, JSON.stringify({
      v: 1, cls: G.clsKeys, level: G.level, score: G.score, gold: G.gold,
      bombs: G.bombs, kills: G.kills, drops: G.drops, runT: G.runT, comboBest: G.comboBest, won: !!G.won,
      tollDeep: G.tollDeep, tollFoes: G.tollFoes,
      /* no key and no fallen: the floor that is about to be built hands out
         its own key and sets anyone down back on their feet */
      ps: G.players.map(P => ({
        hp: P.hp, up: P.up, gear: P.gear, xp: P.xp, plvl: P.plvl,
        buys: P.buys, boons: P.boons, pacts: (P.pacts || []).map(p => p.id)
      }))
    }));
  } catch (e) {}
}
function clearRun() { pendingRun = null; try { localStorage.removeItem(RUN_KEY); } catch (e) {} }
/* Nothing off the disk is trusted. A half-written save, one from an older
   build, or one somebody has edited by hand must come back as "no run" --
   never as a delver carrying a damage multiplier of NaN. Anything that does
   not survive the checks is thrown away rather than offered. */
function loadRun() {
  let raw = null;
  try { raw = JSON.parse(localStorage.getItem(RUN_KEY) || 'null'); } catch (e) { raw = null; }
  if (!raw || typeof raw !== 'object' || raw.v !== 1) { clearRun(); return null; }
  const cls = Array.isArray(raw.cls) ? raw.cls : [];
  const ps = Array.isArray(raw.ps) ? raw.ps : [];
  if (!cls.length || cls.length > 2 || cls.some(k => !CLASSES[k]) || ps.length !== cls.length) { clearRun(); return null; }
  const num = (v, d) => (typeof v === 'number' && Number.isFinite(v) ? v : d);
  const gearOk = g => g === null || (!!g && typeof g === 'object' && typeof g.slot === 'string' && !!g.s && typeof g.s === 'object');
  const lvl = metaNum(raw.level, 1, 1);
  if (lvl > 99) { clearRun(); return null; }
  const out = {
    cls: cls.slice(), level: lvl, score: metaNum(raw.score, 0, 0), gold: metaNum(raw.gold, 0, 0),
    bombs: metaNum(raw.bombs, 0, 0), kills: metaNum(raw.kills, 0, 0),
    drops: metaNum(raw.drops, 0, 0), runT: Math.max(0, num(raw.runT, 0)),
    comboBest: metaNum(raw.comboBest, 0, 0), won: !!raw.won,
    /* absent in a save written before this existed, which is simply zero */
    tollDeep: Math.max(0, num(raw.tollDeep, 0)), tollFoes: Math.max(0, num(raw.tollFoes, 0)), ps: []
  };
  for (const p of ps) {
    if (!p || typeof p !== 'object') { clearRun(); return null; }
    const up = p.up && typeof p.up === 'object' ? p.up : {};
    const g = p.gear && typeof p.gear === 'object' ? p.gear : {};
    for (const slot of SLOTS) if (!gearOk(g[slot] === undefined ? null : g[slot])) { clearRun(); return null; }
    out.ps.push({
      hp: num(p.hp, 1),
      up: { dmg: num(up.dmg, 1), spd: num(up.spd, 1), cd: num(up.cd, 1), arm: num(up.arm, 1),
            dash: num(up.dash, 1), crit: num(up.crit, .1), hp: num(up.hp, 0) },
      gear: { weapon: g.weapon || null, armour: g.armour || null, trinket: g.trinket || null },
      xp: Math.max(0, num(p.xp, 0)), plvl: metaNum(p.plvl, 1, 1),
      buys: p.buys && typeof p.buys === 'object' ? p.buys : {},
      boons: p.boons && typeof p.boons === 'object' ? p.boons : {},
      pacts: (Array.isArray(p.pacts) ? p.pacts : []).map(id => PACTS.find(q => q.id === id)).filter(Boolean)
    });
  }
  return out;
}
/* rebuild the delver the Barrow would give you now, then lay the saved run
   back over it: the perks are re-derived, everything earned is restored */
function resumeRun(r) {
  G.clsKeys = r.cls.slice(); G.clsKey = r.cls[0]; G.co = r.cls.length > 1;
  G.players = r.cls.map((k, i) => makeDelver(k, i));
  G.players.forEach((P, i) => {
    const s = r.ps[i];
    P.up = s.up; P.gear = s.gear; P.xp = s.xp; P.plvl = s.plvl;
    P.buys = s.buys; P.boons = s.boons; P.pacts = s.pacts;
    recalc(P);
    P.hp = Math.max(1, Math.min(P.max, s.hp));
  });
  G.player = G.players[0];
  G.gold = r.gold; G.bombs = r.bombs; G.kills = r.kills; G.drops = r.drops;
  G.runT = r.runT; G.comboBest = r.comboBest; G.score = r.score; G.won = r.won;
  G.tollDeep = r.tollDeep; G.tollFoes = r.tollFoes; G.gaveUp = false;
  G.combo = 0; G.comboT = 0; G.earned = 0; G.zones = []; G.timers = []; G.bolts = [];
  G.voice = null; G.flash = 0; G.offer = null; G.offerQ = []; G.wares = []; G.winPending = false;
  G.level = r.level; genLevel(); G.state = 'play'; G.paused = false;
  /* written again at once, so a second reload still finds the run */
  saveRun();
}
const PERKS = [
  { id: 'vigour', name: 'Deep Vigour', desc: '+12 starting max health.', cost: 40, grow: 1.6, max: 5, col: '#d9534f' },
  { id: 'slow', name: 'Still Blood', desc: 'Your health drains 8% slower.', cost: 55, grow: 1.7, max: 4, col: '#8fd3ff' },
  { id: 'flask', name: 'Deep Pockets', desc: 'Begin each run with another potion.', cost: 60, grow: 1.8, max: 3, col: '#b98cff' },
  { id: 'purse', name: 'Grave Purse', desc: '+12% gold found.', cost: 50, grow: 1.7, max: 4, col: '#f0a23c' },
  { id: 'edge', name: 'Whetted', desc: '+4% critical chance.', cost: 70, grow: 1.8, max: 4, col: '#ffd24a' },
  { id: 'relic', name: 'Heirloom', desc: 'Begin each run wearing a magic trinket.', cost: 90, grow: 2.4, max: 2, col: '#6fa8ff' }
];
const perkLv = id => (META.perks && META.perks[id]) || 0;
const perkCost = p => Math.round(p.cost * Math.pow(p.grow, perkLv(p.id)));
function buyPerk(id) {
  const p = PERKS.find(x => x.id === id); if (!p) return false;
  if (perkLv(id) >= p.max || META.echoes < perkCost(p)) return false;
  META.echoes -= perkCost(p); META.perks[id] = perkLv(id) + 1; saveMeta();
  return true;
}

/* ---------- the announcer ----------
   Gauntlet's narrator is half of what people remember, so the callouts are
   spoken where the browser allows it and always shown on screen. */
let voiceOn = true;
function speak(txt) {
  if (!voiceOn || muted || typeof speechSynthesis === 'undefined') return;
  try {
    const u = new SpeechSynthesisUtterance(txt);
    u.rate = .95; u.pitch = .55; u.volume = .85;
    speechSynthesis.cancel(); speechSynthesis.speak(u);
  } catch (e) {}
}
function announce(txt, col, quiet) {
  G.voice = { txt, col: col || '#ebe4d2', t: 2.9 };
  if (!quiet) speak(txt);
}
/* one line per subject at a time, so the narrator does not stutter */
function announceOnce(key, gap, txt, col) {
  G.vlast = G.vlast || {};
  if (G.vlast[key] && clock - G.vlast[key] < gap) return;
  G.vlast[key] = clock; announce(txt, col);
}

/* ---------- gear: rolled drops in the Diablo mould ----------
   A drop is a base type plus up to three affixes; the affixes supply the name
   and every stat, so "Savage Gravefang of the Wolf" reads as what it does. */
const SLOTS = ['weapon', 'armour', 'trinket'];
const RARITY = {
  magic: { k: 'magic', name: 'Magic', col: '#6fa8ff', aff: 1 },
  rare: { k: 'rare', name: 'Rare', col: '#ffd24a', aff: 2 },
  fabled: { k: 'fabled', name: 'Fabled', col: '#e08a3c', aff: 3 }
};
const BASES = {
  weapon: ['Hollowblade', 'Crypt Cleaver', 'Gravefang', 'Ashen Rod', 'Pale Talon', 'Widow Spike'],
  armour: ['Shroud', 'Bone Plate', 'Gravemail', 'Hide Wrap', 'Dust Vestment', 'Barrow Coat'],
  trinket: ['Signet', 'Charm', 'Sigil', 'Idol', 'Knucklebone', 'Lantern Tooth']
};
/* s: dmg/spd are multipliers, arm is damage shaved off, hp is flat,
   cd and dash are cooldown scalers (negative is faster) */
const PREFIX = [
  { id: 'savage', name: 'Savage', s: { dmg: .16 } },
  { id: 'brutal', name: 'Brutal', s: { dmg: .27, cd: .07 } },
  { id: 'keen', name: 'Keen', s: { crit: .06 } },
  { id: 'swift', name: 'Swift', s: { cd: -.09 } },
  { id: 'hardy', name: 'Hardy', s: { hp: 22 } },
  { id: 'warded', name: 'Warded', s: { arm: .07 } },
  { id: 'fleet', name: 'Fleet', s: { spd: .07 } },
  { id: 'grim', name: 'Grim', s: { dmg: .11, crit: .03 } },
  { id: 'ember', name: 'Ember', w: 'weapon', s: { elem: 'fire', elemDmg: .5 } },
  { id: 'rime', name: 'Rime', w: 'weapon', s: { elem: 'cold', elemDmg: .35 } },
  { id: 'storm', name: 'Storm', w: 'weapon', s: { elem: 'shock', elemDmg: .45 } },
  { id: 'fetid', name: 'Fetid', w: 'weapon', s: { elem: 'poison', elemDmg: .4 } }
];
const SUFFIX = [
  { id: 'wolf', name: 'of the Wolf', s: { spd: .08 } },
  { id: 'bear', name: 'of the Bear', s: { hp: 28 } },
  { id: 'owl', name: 'of the Owl', s: { sp: 1.4 } },
  { id: 'viper', name: 'of the Viper', s: { cd: -.11 } },
  { id: 'leech', name: 'of Leeching', s: { leech: .05 } },
  { id: 'thorns', name: 'of Thorns', s: { thorns: .4 } },
  { id: 'fortune', name: 'of Fortune', s: { gold: .3 } },
  { id: 'ruin', name: 'of Ruin', s: { dmg: .2 } },
  { id: 'fox', name: 'of the Fox', s: { dash: -.18 } },
  { id: 'warding', name: 'of Warding', s: { arm: .08 } }
];
/* A curse is a bargain: more of one thing, less of another. They are the only
   items that can make a run worse, which is what makes choosing one interesting. */
const CURSE = [
  { id: 'brittle', name: 'Brittle', s: { dmg: .45, arm: -.14 } },
  { id: 'leaden', name: 'Leaden', s: { dmg: .55, spd: -.16 } },
  { id: 'hungry', name: 'Hungry', s: { dmg: .38, drain: .55 } },
  { id: 'frail', name: 'Frail', s: { crit: .22, hp: -32 } },
  { id: 'reckless', name: 'Reckless', s: { cd: -.3, arm: -.1 } },
  { id: 'greedy', name: 'Greedy', s: { gold: .8, hp: -24 } },
  { id: 'bound', name: 'Bound', s: { dmg: .6, dash: .5 } }
];
const SETS = [
  { id: 'barrow', name: "The Barrow King's", s2: { hp: 38, arm: .06 } },
  { id: 'ember', name: 'Emberbound', s2: { dmg: .17, crit: .05 } },
  { id: 'quick', name: 'The Quickened', s2: { spd: .11, cd: -.1 } }
];
const BASE_STAT = { weapon: 'dmg', armour: 'arm', trinket: 'crit' };
/* How many pieces of a set a delver has on. `exceptSlot` leaves one slot
   out, because equipping something REPLACES what is in that slot rather
   than adding to it -- counting the worn piece as well would promise a
   pair that taking the new item would actually break. */
function setWorn(P, id, exceptSlot) {
  let n = 0;
  if (!id || !P || !P.gear) return 0;
  for (const slot of SLOTS) {
    if (slot === exceptSlot) continue;
    const g = P.gear[slot];
    if (g && g.set === id) n++;
  }
  return n;
}
const setLive = (P, id) => !!id && (P.sets || []).some(s => s.id === id);
function rollRarity(bonus) {
  const r = Math.random() * 100 - (bonus || 0) - G.level * 1.1;
  return r < 9 ? RARITY.fabled : r < 33 ? RARITY.rare : RARITY.magic;
}
function rollItem(slot, rar, noCurse) {
  slot = slot || SLOTS[rint(0, 2)];
  rar = rar || rollRarity(om('rich', false) ? 17 : 0);
  const s = {}, lv = 1 + G.level * .06;
  /* the base type carries the slot's core stat */
  if (slot === 'weapon') s.dmg = +(rnd(.10, .20) * lv).toFixed(3);
  else if (slot === 'armour') { s.arm = +(rnd(.05, .10) * lv).toFixed(3); s.hp = Math.round(rnd(8, 18) * lv); }
  else s.crit = +(rnd(.02, .045) * lv).toFixed(3);
  const fits = a => !a.w || a.w === slot;
  const pre = [], suf = [];
  const pool = { p: PREFIX.filter(fits).slice(), s: SUFFIX.filter(fits).slice() };
  for (let i = 0; i < rar.aff; i++) {
    const wantPre = pre.length === 0 || (suf.length > 0 && Math.random() < .5);
    const from = wantPre && pool.p.length ? pool.p : pool.s.length ? pool.s : pool.p;
    if (!from.length) break;
    const a = from.splice(rint(0, from.length - 1), 1)[0];
    (from === pool.p ? pre : suf).push(a);
    for (const k in a.s) {
      const v = a.s[k];
      if (typeof v !== 'number') s[k] = v;
      else s[k] = +((s[k] || 0) + v * rnd(.85, 1.2) * (k === 'hp' ? lv : 1)).toFixed(3);
    }
    if (s.hp) s.hp = Math.round(s.hp);
  }
  const base = BASES[slot][rint(0, BASES[slot].length - 1)];
  if (!noCurse && Math.random() < .16) {
    const c = CURSE[rint(0, CURSE.length - 1)];
    for (const k in c.s) {
      const v = c.s[k], cur = s[k] || 0;
      /* negatives, and extra drain or dash cooldown, are the price: they must bite */
      if (v < 0) s[k] = +(Math.min(cur + v, v).toFixed(3));
      else if (k === 'drain' || k === 'dash') s[k] = +(Math.max(cur + v, v).toFixed(3));
      else s[k] = +((cur + v).toFixed(3));
    }
    if (s.hp) s.hp = Math.round(s.hp);
    return { slot, base, rar: 'cursed', col: '#e0556b', curse: c.name, name: c.name + ' ' + base + (suf.length ? ' ' + suf[0].name : ''), s, ilvl: G.level };
  }
  let set = null;
  if (Math.random() < .22) set = SETS[rint(0, SETS.length - 1)];
  const name = (pre.length ? pre[0].name + ' ' : '') + base + (suf.length ? ' ' + suf[0].name : '');
  return { slot, base, rar: rar.k, col: rar.col, name, s, ilvl: G.level, set: set ? set.id : null, setName: set ? set.name : null };
}
/* a short, readable stat line for the compare card */
const STAT_LABEL = {
  dmg: v => '+' + Math.round(v * 100) + '% damage',
  arm: v => '-' + Math.round(v * 100) + '% damage taken',
  hp: v => '+' + Math.round(v) + ' max health',
  crit: v => '+' + Math.round(v * 100) + '% critical chance',
  spd: v => '+' + Math.round(v * 100) + '% move speed',
  cd: v => (v < 0 ? 'Attacks ' + Math.round(-v * 100) + '% faster' : 'Attacks ' + Math.round(v * 100) + '% slower'),
  dash: v => 'Dash recharges ' + Math.round(-v * 100) + '% faster',
  sp: v => 'Special recharges ' + v.toFixed(1) + 's sooner',
  leech: v => 'Heal ' + Math.round(v * 100) + '% of damage dealt',
  thorns: v => 'Return ' + Math.round(v * 100) + '% of melee damage',
  gold: v => '+' + Math.round(v * 100) + '% gold',
  drain: v => v > 0 ? 'Your health drains ' + Math.round(v * 100) + '% faster' : 'Your health drains ' + Math.round(-v * 100) + '% slower',
};
function itemLines(it, P) {
  const out = [];
  for (const k of ['dmg', 'arm', 'hp', 'crit', 'spd', 'cd', 'dash', 'sp', 'leech', 'thorns', 'gold', 'drain']) {
    if (it.s[k] === undefined || it.s[k] === 0) continue;
    const t = STAT_LABEL[k] && STAT_LABEL[k](it.s[k]); if (t) out.push(t);
  }
  if (it.s.elem) {
    const el = it.s.elem, nm = ELEM_NAME[el] || el;
    const share = Math.round((it.s.elemDmg || .4) * 100);
    out.push(nm.charAt(0).toUpperCase() + nm.slice(1) + ' damage: +' + share +
             '% of every hit, and ' + (ELEM_VERB[el] || 'it bites'));
    const f = elemFoes(el), bits = [];
    if (f.weak.length) bits.push(nameList(f.weak) + ' fear it');
    if (f.res.length) bits.push(nameList(f.res) + ' shrug it off');
    if (bits.length) {
      const line = bits.join('; ');
      out.push(line.charAt(0).toUpperCase() + line.slice(1));
    }
  }
  if (it.setName) {
    /* with a delver to ask, say what taking this would actually do */
    if (P) {
      const would = setWorn(P, it.set, it.slot) + 1;
      out.push('Set: ' + it.setName + (would >= 3 ? ' \u2014 all three together'
        : would === 2 ? ' \u2014 a pair with what else you wear'
        : ' \u2014 no other piece of it yet'));
    } else out.push('Set: ' + it.setName + ' (2 pieces grant more)');
  }
  return out;
}

/* ---------- omens ----------
   Fifteen depths that each ask the same three things of you is fifteen of the
   same depth. An omen changes what the floor wants: more of them, fewer but
   blind, no food, no clock at all. Every field below is a plain multiplier
   read either at generation or in the loop, so an omen can never put a depth
   into a state the ordinary rules cannot reach. */
const OMENS = [
  { id: 'horde', name: 'The Horde', col: '#e0553a',
    line: 'The door is already open. Nothing here means you to reach it.',
    foes: 1.9, nests: 1.4, gold: 1.25, freeKey: true },
  { id: 'famine', name: 'Famine', col: '#c98b5a',
    line: 'Nothing grows this deep, and nothing has been left behind.',
    food: 0, drain: 1.4, gold: 2 },
  { id: 'dark', name: 'Pitch Dark', col: '#6f7fa8',
    line: 'Your torch gutters. What lives here never needed one.',
    light: .52, foes: .7, rich: true },
  { id: 'still', name: 'Still Air', col: '#7fd1c7',
    line: 'The deep is holding its breath. It is not hungry, only crowded.',
    drain: 0, foes: 2.1, nests: 0, food: 0 },
  { id: 'gilded', name: 'The Gilded Seam', col: '#f0a23c',
    line: 'Gold in the walls, and something fat has been feeding on the miners.',
    gold: 2.6, chests: 2, elite: true, foes: .75 },
  { id: 'warren', name: 'The Warren', col: '#9a6bd6',
    line: 'The crypts here have had time. Far too much of it.',
    nests: 2.4, nestCap: 8, foes: .55, gold: 1.3 }
];
function rollOmen(depth) {
  /* the first depths stay plain so the ordinary rules are learned first, and
     a boss floor already has its own shape */
  if (depth < 3 || isBossLvl(depth)) return null;
  if (Math.random() > Math.min(.46, .22 + depth * .022)) return null;
  return OMENS[rint(0, OMENS.length - 1)];
}
const om = (k, dflt) => (G.omen && G.omen[k] !== undefined) ? G.omen[k] : dflt;
/* What a delver actually lost, and to what. Counted against the health they
   had rather than the blow that was thrown, so the killing hit adds what it
   really took and not the overkill on top. */
function toll(which, was, P) {
  const lost = Math.max(0, was - Math.max(0, P.hp));
  if (which === 'deep') G.tollDeep = (G.tollDeep || 0) + lost;
  else G.tollFoes = (G.tollFoes || 0) + lost;
}
/* The drain, in one place, because the health bar draws this number and the
   floor takes it: two copies would be two answers.
   drainPlain is what the depth alone asks. Everything past it -- the omen,
   the pacts, a curse, the Barrow's slow blood, the mercy of having company
   -- is the part worth showing a player, because it is the part they chose
   or were dealt. */
function drainPlain() { return .8 + Math.min(G.level, 8) * .2 + Math.max(0, G.level - 8) * .07; }
function drainRate(P) { return drainPlain() * om('drain', 1) * (G.co ? .85 : 1) * ((P && P.drainMul) || 1); }
/* how far the band on the bar looks ahead */
const DRAIN_AHEAD = 10;

/* ---------- fonts ----------
   A pact is the one bargain in the dungeon that costs you something. Every
   figure below goes through the same stat machinery the affixes use, so the
   clamps in recalc hold them exactly as they hold a cursed trinket. */
const PACTS = [
  { id: 'embers', name: 'Pact of Embers',
    good: 'Your blows land far harder.', bad: 'The deep drinks you half again as fast.',
    s: { dmg: .4, drain: .5 } },
  { id: 'stone', name: 'Pact of Stone',
    good: 'You take a quarter less harm.', bad: 'You move as though waist deep.',
    s: { arm: .25, spd: -.16 } },
  { id: 'hare', name: 'Pact of the Hare',
    good: 'You move and strike markedly faster.', bad: 'You are a good deal easier to kill.',
    s: { spd: .2, cd: -.16, hp: -42 } },
  { id: 'greed', name: 'Pact of Greed',
    good: 'The dead give up far more gold.', bad: 'Riches make you careless of your own skin.',
    s: { gold: 1, arm: -.22 } },
  { id: 'blood', name: 'Pact of Blood',
    good: 'What you wound, feeds you.', bad: 'The drain never once relents.',
    s: { leech: .07, drain: .35 } },
  { id: 'edge', name: 'Pact of the Edge',
    good: 'Your strikes bite critically far more often.', bad: 'But they come slow and heavy.',
    s: { crit: .24, cd: .22 } }
];
/* fonts that ask nothing, so a lit altar is not always a trap */
const BLESSINGS = [
  { id: 'mend', name: 'Mending Font', good: 'Your wounds close, and the fallen rise.' },
  { id: 'ward', name: 'Warding Font', good: 'A ward that soaks what comes next.' },
  { id: 'hoard', name: 'Gilded Font', good: 'A scattering of gold for the taking.' }
];
function rollShrine(depth) {
  const r = Math.random();
  /* the deeper you are, the likelier the altar wants something back */
  const pactChance = Math.min(.62, .3 + depth * .03);
  if (r < .17) return { kind: 'mystery', pact: Math.random() < pactChance + .1 ? PACTS[rint(0, PACTS.length - 1)] : BLESSINGS[rint(0, BLESSINGS.length - 1)] };
  if (r < .17 + pactChance) return { kind: 'pact', pact: PACTS[rint(0, PACTS.length - 1)] };
  return { kind: 'blessing', pact: BLESSINGS[rint(0, BLESSINGS.length - 1)] };
}
const isPact = (p) => PACTS.indexOf(p) >= 0;
const SHRINE_COL = { blessing: '#f0a23c', pact: '#e0556b', mystery: '#b98cff' };
const shrineCol = (sh) => SHRINE_COL[sh.kind] || '#f0a23c';

/* ---------- boons ----------
   An upgrade makes the same swing bigger. A boon makes it a different swing.
   Four per delver, offered in place of a stat card every other level. */
const BOONS = {
  bulwark: [
    { id: 'cyclone', name: 'Cyclone', desc: 'Your sweep comes all the way round, striking everything about you.' },
    { id: 'wake', name: 'Burning Wake', desc: 'Whatever your sword touches catches fire.' },
    { id: 'bash', name: 'Shield Bash', desc: 'Your blows hurl foes back and leave them reeling.' },
    { id: 'riposte', name: 'Riposte', desc: 'Being struck readies your weapon at once, and the answer lands true.' }
  ],
  ember: [
    { id: 'split', name: 'Splinter', desc: 'Each burst throws three smaller bolts outward.' },
    { id: 'seek', name: 'Seeking Flame', desc: 'Your bolts bend toward whatever is nearest.' },
    { id: 'pyre', name: 'Pyre', desc: 'Your bursts leave a fire burning on the ground.' },
    { id: 'kindle', name: 'Kindling', desc: 'A foe that dies burning goes off like a bomb.' }
  ],
  sable: [
    { id: 'fan', name: 'Fan of Knives', desc: 'Every throw becomes a spread of three.' },
    { id: 'ric', name: 'Ricochet', desc: 'Your daggers leap on to a second and third mark.' },
    { id: 'venom', name: 'Venom', desc: 'Your blades carry poison.' },
    { id: 'ambush', name: 'Ambush', desc: 'The first strike on an unwary foe always lands critically.' }
  ],
  thistle: [
    { id: 'volley', name: 'Volley', desc: 'Each draw looses three arrows in a fan.' },
    { id: 'barbs', name: 'Barbed Shafts', desc: 'An arrow hits harder with every foe it passes through.' },
    { id: 'frost', name: 'Hoarfrost', desc: 'Your arrows chill what they strike.' },
    { id: 'mark', name: "Hunter's Mark", desc: 'Foes you hit take more from every source for a while.' }
  ]
};
const bn = (P, id) => !!(P && P.boons && P.boons[id]);
function boonsLeft(P) { return (BOONS[P.cls.key] || []).filter(b => !bn(P, b.id)); }
function rollBoons(P) {
  const pool = boonsLeft(P).slice(), out = [];
  while (out.length < 3 && pool.length) out.push(pool.splice(rint(0, pool.length - 1), 1)[0]);
  return out;
}

/* ---------- elemental affinities ----------
   Every monster fears one element and shrugs off another, so the weapon you
   carry is a decision rather than a number. */
const ELEM_COL = { fire: '#ff8a3a', cold: '#8fd3ff', shock: '#c9b6ff', poison: '#9bd16a' };
const ELEM_NAME = { fire: 'fire', cold: 'cold', shock: 'lightning', poison: 'poison' };
/* The dungeon had no vocabulary for its own inhabitants: they are keys in a
   table and nothing ever had to name one out loud. */
const FOE_NAME = {
  gloam: 'gloam', wisp: 'wisps', bonewalker: 'bonewalkers', brute: 'brutes',
  hound: 'hounds', bloat: 'bloats', thief: 'thieves', reaper: 'the reaper',
  warden: 'wardens'
};
const ELEM_VERB = { fire: 'it burns', cold: 'it chills', shock: 'it arcs to others', poison: 'it rots' };
const AFFIN = {
  gloam: { weak: 'fire', res: 'shock' },
  wisp: { weak: 'shock', res: 'cold' },
  bonewalker: { weak: 'fire', res: 'poison' },
  brute: { weak: 'poison', res: 'fire' },
  hound: { weak: 'cold', res: 'fire' },
  bloat: { weak: 'fire', res: 'poison' },
  thief: { weak: 'shock', res: null },
  reaper: { weak: null, res: 'all' },
  warden: { weak: null, res: 'cold' }
};
/* Who fears an element and who shrugs it off, read off the same table the
   damage is read off, so the two cannot disagree. */
function elemFoes(elem) {
  const weak = [], res = [];
  for (const t in AFFIN) {
    const a = AFFIN[t], nm = FOE_NAME[t] || t;
    if (a.weak === elem) weak.push(nm);
    else if (a.res === elem || a.res === 'all') res.push(nm);
  }
  return { weak, res };
}
const nameList = a => a.length < 2 ? (a[0] || '') : a.slice(0, -1).join(', ') + ' and ' + a[a.length - 1];
function elemMul(e, elem) {
  const a = AFFIN[e.type]; if (!a || !elem) return 1;
  if (a.res === 'all' || a.res === elem) return .25;
  if (a.weak === elem) return 1.9;
  return 1;
}

/* ---------- elite modifiers, after Diablo's champion packs ---------- */
const EAFF = [
  { id: 'fast', name: 'Extra Fast', col: '#eaf4ff' },
  { id: 'fiery', name: 'Fire Enchanted', col: '#ff6a3d' },
  { id: 'frozen', name: 'Cold Touched', col: '#8fd3ff' },
  { id: 'vamp', name: 'Vampiric', col: '#d9534f' },
  { id: 'spiny', name: 'Spiny', col: '#9bd16a' },
  { id: 'warded', name: 'Shielded', col: '#ffd24a' }
];

/* ---------- world helpers ---------- */
function solid(tx, ty) {
  if (tx < 0 || ty < 0 || tx >= MW || ty >= MH) return true;
  const t = G.map[ty * MW + tx]; return t === 1 || t === 2;
}
function blockedAt(x, y, r) {
  const a = Math.floor((x - r) / T), b = Math.floor((x + r) / T), c = Math.floor((y - r) / T), d = Math.floor((y + r) / T);
  return solid(a, c) || solid(b, c) || solid(a, d) || solid(b, d);
}
function propHit(e, nx, ny) {
  for (const p of G.props) {
    if (!p.sr) continue; const nd = Math.hypot(nx - p.x, ny - p.y);
    if (nd < e.r + p.sr && nd < Math.hypot(e.x - p.x, e.y - p.y)) return true;
  }
  return false;
}
function moveEnt(e, dx, dy) {
  let hit = false;
  if (!blockedAt(e.x + dx, e.y, e.r) && !propHit(e, e.x + dx, e.y)) e.x += dx; else hit = true;
  if (!blockedAt(e.x, e.y + dy, e.r) && !propHit(e, e.x, e.y + dy)) e.y += dy; else hit = true;
  return hit;
}
function los(ax, ay, bx, by) {
  const n = Math.ceil(Math.hypot(bx - ax, by - ay) / 10);
  for (let i = 1; i < n; i++) {
    const t = i / n;
    if (solid(Math.floor((ax + (bx - ax) * t) / T), Math.floor((ay + (by - ay) * t) / T))) return false;
  }
  return true;
}
const openAt = (x, y) => {
  const tx = Math.floor(x / T), ty = Math.floor(y / T);
  if (tx < 0 || ty < 0 || tx >= MW || ty >= MH) return false;
  return !!(G.reach && G.reach[ty * MW + tx]);
};
/* flood from the start room, treating the locked door as passable, so nothing
   is ever placed inside a pillar or in a pocket walled off by one */
function buildReach() {
  const r = new Uint8Array(MW * MH), s = G.rooms[0], q = [s.cy * MW + s.cx];
  r[q[0]] = 1;
  for (let h = 0; h < q.length; h++) {
    const c = q[h], cx = c % MW, cy = (c / MW) | 0;
    for (const [dx, dy] of DIRS) {
      const x = cx + dx, y = cy + dy; if (x < 0 || y < 0 || x >= MW || y >= MH) continue;
      const i = y * MW + x; if (r[i] || G.map[i] === 1) continue;
      r[i] = 1; q.push(i);
    }
  }
  G.reach = r;
}
function clearPoint(rooms, want) {
  for (let i = 0; i < 60; i++) {
    const r = rooms[rint(0, rooms.length - 1)], p = roomPoint(r);
    if (openAt(p.x, p.y) && !blockedAt(p.x, p.y, want)) return p;
  }
  for (let i = 0; i < 60; i++) {
    const r = rooms[rint(0, rooms.length - 1)], p = roomPoint(r);
    if (openAt(p.x, p.y) && !blockedAt(p.x, p.y, 11)) return p;
  }
  return roomPoint(rooms[rint(0, rooms.length - 1)]);
}
function roomPoint(r) {
  for (let i = 0; i < 40; i++) {
    const x = (r.x + 1 + Math.random() * (r.w - 2)) * T, y = (r.y + 1 + Math.random() * (r.h - 2)) * T;
    if (openAt(x, y)) return { x, y };
  }
  return { x: (r.cx + .5) * T, y: (r.cy + .5) * T };
}

/* ---------- level generation ----------
   Rooms are placed, shaped, then wired with a minimum spanning tree plus a few
   loop edges, so a depth is a branching dungeon with dead ends rather than a
   left-to-right ribbon. The stairs sit in the leaf room furthest from the start,
   walled off behind the one locked door. */
const ROOM_KINDS = ['hall', 'hall', 'hall', 'pillars', 'pillars', 'arena', 'cells', 'cross'];
function shapeRoom(m, r) {
  for (let j = r.y; j < r.y + r.h; j++) for (let i = r.x; i < r.x + r.w; i++) m[j * MW + i] = 0;
  if (r.kind === 'cross' && r.w >= 9 && r.h >= 7) {
    const cw = Math.max(2, r.w >> 2), ch = Math.max(2, r.h >> 2);
    for (let j = 0; j < ch; j++) for (let i = 0; i < cw; i++) {
      m[(r.y + j) * MW + r.x + i] = 1; m[(r.y + j) * MW + r.x + r.w - 1 - i] = 1;
      m[(r.y + r.h - 1 - j) * MW + r.x + i] = 1; m[(r.y + r.h - 1 - j) * MW + r.x + r.w - 1 - i] = 1;
    }
  } else if (r.kind === 'arena' || r.kind === 'vault') {
    const c = r.kind === 'vault' ? 1 : 2;
    for (let j = 0; j < c; j++) for (let i = 0; i < c - j; i++) {
      m[(r.y + j) * MW + r.x + i] = 1; m[(r.y + j) * MW + r.x + r.w - 1 - i] = 1;
      m[(r.y + r.h - 1 - j) * MW + r.x + i] = 1; m[(r.y + r.h - 1 - j) * MW + r.x + r.w - 1 - i] = 1;
    }
  }
}
function makeMap() {
  const m = new Uint8Array(MW * MH).fill(1), rooms = [];
  const want = 8 + Math.min(G.level, 5);
  for (let tries = 0; rooms.length < want && tries < 800; tries++) {
    const big = Math.random() < .24;
    const w = big ? rint(11, 15) : rint(6, 10), h = big ? rint(8, 12) : rint(5, 9);
    const x = rint(2, MW - w - 3), y = rint(2, MH - h - 3);
    if (rooms.some(r => x < r.x + r.w + 2 && x + w + 2 > r.x && y < r.y + r.h + 2 && y + h + 2 > r.y)) continue;
    rooms.push({ x, y, w, h, cx: x + (w >> 1), cy: y + (h >> 1), big });
  }
  const n = rooms.length;
  if (n < 6) return null;
  /* wire a spanning tree by nearest unconnected room */
  const inT = new Array(n).fill(false), deg = new Array(n).fill(0), adj = rooms.map(() => []);
  const span = (a, b) => Math.abs(rooms[a].cx - rooms[b].cx) + Math.abs(rooms[a].cy - rooms[b].cy);
  inT[0] = true;
  for (let it = 1; it < n; it++) {
    let ba = -1, bb = -1, bd = 1e9;
    for (let a = 0; a < n; a++) { if (!inT[a]) continue; for (let b = 0; b < n; b++) { if (inT[b]) continue; const d = span(a, b); if (d < bd) { bd = d; ba = a; bb = b; } } }
    if (bb < 0) return null;
    inT[bb] = true; deg[ba]++; deg[bb]++; adj[ba].push(bb); adj[bb].push(ba);
  }
  /* the stairs go in the leaf room deepest from the start */
  const depth = new Array(n).fill(-1), q = [0]; depth[0] = 0;
  for (let h = 0; h < q.length; h++) for (const b of adj[q[h]]) if (depth[b] < 0) { depth[b] = depth[q[h]] + 1; q.push(b); }
  let xi = -1;
  for (let i = 1; i < n; i++) if (depth[i] > 0 && deg[i] === 1 && (xi < 0 || depth[i] > depth[xi])) xi = i;
  if (xi < 0) return null;
  rooms.forEach((r, i) => { r.kind = i === 0 ? 'hall' : i === xi ? 'vault' : r.big && Math.random() < .55 ? 'arena' : ROOM_KINDS[rint(0, ROOM_KINDS.length - 1)]; });
  for (const r of rooms) shapeRoom(m, r);
  /* corridors: random leg order, sometimes two tiles wide */
  const corr = new Set();
  const carve = (a, b, wide) => {
    const path = []; let x = a.cx, y = a.cy;
    const legX = () => { while (x !== b.cx) { x += Math.sign(b.cx - x); path.push([x, y]); } };
    const legY = () => { while (y !== b.cy) { y += Math.sign(b.cy - y); path.push([x, y]); } };
    if (Math.random() < .5) { legX(); legY(); } else { legY(); legX(); }
    for (const [px, py] of path) {
      m[py * MW + px] = 0; corr.add(py * MW + px);
      if (wide) for (const [dx, dy] of [[1, 0], [0, 1]]) {
        const nx = px + dx, ny = py + dy;
        if (nx > 0 && ny > 0 && nx < MW - 1 && ny < MH - 1) { m[ny * MW + nx] = 0; corr.add(ny * MW + nx); }
      }
    }
    return path;
  };
  const done = new Set();
  for (let a = 0; a < n; a++) for (const b of adj[a]) {
    const key = Math.min(a, b) + ':' + Math.max(a, b); if (done.has(key)) continue; done.add(key);
    if (a === xi || b === xi) continue;
    carve(rooms[a], rooms[b], Math.random() < .26);
  }
  /* a few loop edges so the map is not a pure tree (never into the stairs room) */
  const cand = [];
  for (let a = 0; a < n; a++) for (let b = a + 1; b < n; b++) {
    if (a === xi || b === xi || adj[a].includes(b)) continue;
    if (span(a, b) < 24) cand.push([a, b]);
  }
  for (let k = 0, lim = rint(1, 3); k < lim && cand.length; k++) {
    const e = cand.splice(rint(0, cand.length - 1), 1)[0]; carve(rooms[e[0]], rooms[e[1]], Math.random() < .2);
  }
  /* seal the stairs room, then punch one locked door on its only corridor */
  const last = rooms[xi];
  for (let x = last.x - 1; x <= last.x + last.w; x++) for (let y = last.y - 1; y <= last.y + last.h; y++)
    if ((x === last.x - 1 || x === last.x + last.w || y === last.y - 1 || y === last.y + last.h) && x >= 0 && y >= 0 && x < MW && y < MH) m[y * MW + x] = 1;
  const lastPath = carve(rooms[adj[xi][0]], last, false);
  let door = null;
  for (const [x, y] of lastPath) {
    const ring = x >= last.x - 1 && x <= last.x + last.w && y >= last.y - 1 && y <= last.y + last.h;
    const inside = x >= last.x && x < last.x + last.w && y >= last.y && y < last.y + last.h;
    if (ring && !inside) { m[y * MW + x] = 2; door = { x, y }; break; }
  }
  /* interior cover: pillars you can fight around, never blocking a corridor */
  rooms.forEach((r, i) => {
    if (i === 0 || i === xi || r.w < 6 || r.h < 5) return;
    const dens = r.kind === 'pillars' ? .50 : r.kind === 'cells' ? .34 : r.kind === 'arena' ? .20 : .11;
    const put = [];
    const free = (x, y) => {
      if (x < r.x + 1 || y < r.y + 1 || x >= r.x + r.w - 1 || y >= r.y + r.h - 1) return false;
      if (Math.abs(x - r.cx) <= 1 && Math.abs(y - r.cy) <= 1) return false;
      if (m[y * MW + x] !== 0) return false;
      for (let j = -1; j <= 1; j++) for (let i2 = -1; i2 <= 1; i2++) if (corr.has((y + j) * MW + (x + i2))) return false;
      return true;
    };
    for (let k = Math.round(r.w * r.h * dens / 9), t = 0; k > 0 && t < 48; t++) {
      const x = rint(r.x + 1, r.x + r.w - 2), y = rint(r.y + 1, r.y + r.h - 2);
      if (!free(x, y) || put.some(p => Math.abs(p[0] - x) < 3 && Math.abs(p[1] - y) < 3)) continue;
      m[y * MW + x] = 1; put.push([x, y]);
      if (r.kind === 'pillars' && Math.random() < .45) { const ax = x + (Math.random() < .5 ? 1 : -1); if (free(ax, y)) m[y * MW + ax] = 1; }
      k--;
    }
  });
  /* every room must be reachable without the key; the stairs only with it */
  const reach = pass => {
    const s = rooms[0].cy * MW + rooms[0].cx, seen = new Set([s]), qq = [s];
    for (let h = 0; h < qq.length; h++) {
      const c = qq[h], cx = c % MW, cy = (c / MW) | 0;
      for (const [dx, dy] of DIRS) {
        const x = cx + dx, y = cy + dy; if (x < 0 || y < 0 || x >= MW || y >= MH) continue;
        const i = y * MW + x, t = m[i]; if (seen.has(i) || t === 1 || (t === 2 && !pass)) continue;
        seen.add(i); qq.push(i);
      }
    }
    return seen;
  };
  const sealed = reach(false), open = reach(true), id = r => r.cy * MW + r.cx;
  const ok = !!door && !sealed.has(id(last)) && open.has(id(last)) && rooms.every((r, i) => i === xi || sealed.has(id(r)));
  if (!ok) return null;
  /* keep the stairs room last so the rest of the level build can index it */
  if (xi !== n - 1) { const t = rooms[n - 1]; rooms[n - 1] = rooms[xi]; rooms[xi] = t; }
  return { m, rooms, door };
}
function genLevel() {
  let res = null;
  for (let a = 0; a < 300 && !res; a++) res = makeMap();
  const { m, rooms } = res, last = rooms[rooms.length - 1]; G.door = res.door;
  G.map = m; G.seen = new Uint8Array(MW * MH); G.rooms = rooms; buildReach();
  G.enemies = []; G.nests = []; G.shots = []; G.eshots = []; G.items = []; G.parts = []; G.texts = []; G.torches = []; G.slash = null; G.decals = []; G.dying = []; G.fxs = []; G.props = []; G.hazards = []; G.combo = 0; G.comboT = 0;
  const start = rooms[0];
  G.exit = { x: last.cx * T + T / 2, y: last.cy * T + T / 2, r: 20 };
  G.omen = rollOmen(G.level);
  G.keys = om('freeKey', false) ? 1 : 0;
  G.players.forEach((P, i) => {
    P.x = start.cx * T + T / 2 + (G.players.length > 1 ? (i ? 14 : -14) : 0); P.y = start.cy * T + T / 2;
    if (P.down || P.hp <= 0) { P.down = false; P.hp = P.max * .5; } P.rev = 0; P.inv = 1;
  });
  rooms.forEach((r, i) => {
    for (let k = 0; k < 2; k++) {
      const tx = r.x + 1 + Math.floor(Math.random() * (r.w - 2)), ty = r.y - 1;
      if (k === 0 || r.w > 8) G.torches.push({ x: (r.x + (k ? r.w - 2 : 1)) * T + T / 2, y: ty * T + T / 2, ph: Math.random() * 6 });
    }
    if (i === 0) return;
    const gn = Math.max(0, Math.round(rint(2, 4) * om('gold', 1)));
    for (let k = 0; k < gn; k++) { const p = roomPoint(r); G.items.push({ kind: 'gold', x: p.x, y: p.y, t: Math.random() * 6 }); }
    const fdn = Math.round((Math.random() < .72 ? 1 : 0) + (Math.random() < .3 ? 1 : 0)) * om('food', 1);
    for (let f = 0; f < fdn; f++) { const p = roomPoint(r); G.items.push({ kind: 'food', x: p.x, y: p.y, t: 0 }); }
    if (Math.random() < .25) { const p = roomPoint(r); G.items.push({ kind: 'gem', x: p.x, y: p.y, t: 0 }); }
    if (i === rooms.length - 1) return;
    if (r.kind !== 'arena' && Math.random() < .12) r.quiet = true;
    const nn0 = r.quiet ? 0 : Math.min(3, rint(1, 1 + Math.floor(G.level / 2)) + (r.w * r.h > 60 ? 1 : 0) + (r.kind === 'arena' ? 1 : 0));
    const nn = Math.min(om('nestCap', 5), Math.round(nn0 * om('nests', 1)));
    for (let k = 0; k < nn; k++) { const p = roomPoint(r); G.nests.push({ x: p.x, y: p.y, r: 15, hp: 70 + G.level * 14, max: 70 + G.level * 14, t: rnd(.5, 2.5), flash: 0 }); }
    const fn = Math.max(0, Math.round((rint(1, 3) + (r.kind === 'arena' ? 2 : 0)) * om('foes', 1)));
    for (let k = 0; k < fn; k++) { const p = roomPoint(r); spawnFoe(pickFoe(), p.x, p.y, om('elite', false) ? true : undefined); }
    if (r.kind === 'arena' && G.level >= 3 && Math.random() < .7) { const p = roomPoint(r); spawnFoe(pickFoe(), p.x, p.y, true); }
    if (r.kind === 'cells') for (let k = rint(1, 2); k > 0; k--) { const p = roomPoint(r); G.items.push({ kind: 'gold', x: p.x, y: p.y, t: Math.random() * 6 }); }
  });
  const mids = rooms.slice(1, -1);
  for (let k = 0; k < (rooms.length > 8 ? 2 : 1) + om('chests', 0); k++) { const p = roomPoint(mids[rint(0, mids.length - 1)]); G.items.push({ kind: 'chest', x: p.x, y: p.y, t: Math.random() * 6 }); }
  if (mids.length) {
    for (let k = 0; k < (G.level >= 5 && mids.length > 3 ? 2 : 1); k++) {
      const p = clearPoint(mids, 20);
      const sh = rollShrine(G.level);
      G.items.push({ kind: 'shrine', x: p.x, y: p.y, t: Math.random() * 6, sh, cool: 0 });
    }
  }
  const bc = openAt((last.x + 1.5) * T, (last.y + 1.5) * T) ? { x: (last.x + 1.5) * T, y: (last.y + 1.5) * T } : roomPoint(last);
  G.items.push({ kind: 'chest', big: true, x: bc.x, y: bc.y, t: 0 });
  const keyRoom = rooms[rint(1, Math.max(1, rooms.length - 2))], kp = roomPoint(keyRoom);
  G.zone = zoneOf(G.level); G.hitstop = 0; tuneAmbience();
  if (isBossLvl(G.level)) {
    spawnFoe('warden', keyRoom.cx * T + T / 2, keyRoom.cy * T + T / 2);
    const b = G.enemies[G.enemies.length - 1];
    if (isFinalLvl(G.level)) {
      /* the door is not the obstacle down here, the Heart is */
      b.kind = 'heart'; b.name = HEART_NAME; b.col = '#ff3b5c';
      const K = BOSSES.heart;
      b.r = K.r; b.max = Math.round(b.max * 2.3); b.hp = b.max;
      b.dmg = Math.round(b.dmg * 1.25); b.spd *= .88;
      G.keys = Math.max(G.keys, 1);
    } else { b.name = G.zone.boss; b.col = G.zone.bcol; }
  } else if (!om('freeKey', false)) G.items.push({ kind: 'key', x: kp.x, y: kp.y, t: 0 });
  makeProps(); makeHazards();
  G.event = null;
  if (G.level >= 2) {
    const cands = G.rooms.filter((r, i) => i > 0 && i < G.rooms.length - 1 && r.w >= 8 && r.h >= 6);
    if (cands.length) {
      cands.sort((a, b) => (b.kind === 'arena') - (a.kind === 'arena') || b.w * b.h - a.w * a.h);
      cands[0].arena = true;
    }
  }
  const mid = () => G.rooms[rint(1, Math.max(1, G.rooms.length - 2))];
  for (let b = (G.level === 1 ? 1 : 0) + (Math.random() < .85 ? 1 : 0) + (Math.random() < .2 ? 1 : 0); b > 0; b--) { const p = roomPoint(mid()); G.items.push({ kind: 'bomb', x: p.x, y: p.y, t: Math.random() * 6 }); }
  if (G.level >= 3 && Math.random() < .5) { const p = roomPoint(mid()); spawnFoe('thief', p.x, p.y, false); }
  if (G.level >= 6 && Math.random() < .38) {
    const p = roomPoint(mid()); spawnFoe('reaper', p.x, p.y, false);
    G.enemies[G.enemies.length - 1].alert = true;
  }
  G.bolts = []; G.voice = null; G.flash = 0; G.offer = null; G.offerQ = []; G.zones = []; G.timers = [];
  G.flowT = 0;
  G.banner = { txt: isFinalLvl(G.level) ? 'Depth ' + G.level : 'Depth ' + G.level, sub: isFinalLvl(G.level) ? 'The Hollow \u00b7 ' + HEART_NAME + ' waits' : G.zone.name + (isBossLvl(G.level) ? ' \u00b7 ' + G.zone.boss + ' guards the key' : G.omen ? ' \u00b7 ' + G.omen.name : ''), t: 2.8, omen: !!G.omen };
  if (G.omen) { sfx('omen'); announceOnce('omen' + G.level, 6, G.omen.name + '. ' + G.omen.line, G.omen.col); }
  G.mapVer = (G.mapVer || 0) + 1;
}
// [sprite, solid radius, scale, weight, lit radius]
const PROP_POOL = [
  [['grave_round', 8, 1.5, 3], ['grave_cross', 8, 1.5, 2], ['grave_broken', 0, 1.5, 2], ['grave_bevel', 7, 1.5, 2], ['coffin', 0, 1.3, 1], ['urn', 5, 1.6, 2], ['candles', 0, 1.7, 2, 56], ['cross', 7, 1.3, 1], ['altar', 14, 1.1, 1],
   ['r_column_round', 9, 1.1, 2], ['r_column_square', 9, 1.1, 1], ['r_statue_fox', 10, 1.15, 1], ['r_statue_stag', 10, 1.15, 1], ['r_skull', 0, 1.8, 2], ['r_bricks', 0, 1.3, 2], ['r_pot1', 7, 1.3, 2], ['r_pot1_broken', 0, 1.3, 1], ['p_candlestick', 5, 1.2, 2, 70], ['p_bookstand', 6, 1.2, 1], ['p_coin_pile', 0, 1.4, 1],
   ['r_candles', 0, 1.7, 2, 56], ['p_vase', 6, 1.3, 2]],
  [['barrel', 9, 1.5, 3], ['pot', 8, 1.5, 3], ['rocks', 12, 1.1, 2], ['rocks_tall', 12, 1.1, 2], ['urn', 5, 1.6, 2], ['lantern', 4, 1.7, 2, 78], ['grave_broken', 0, 1.5, 1],
   ['r_barrel', 9, 1.2, 2], ['r_crate', 9, 1.2, 2], ['p_bucket', 5, 1.3, 2], ['p_barrel_apples', 9, 1.15, 1], ['r_cart', 12, 1.0, 1], ['p_rope', 0, 1.5, 1], ['p_chain', 0, 1.3, 1], ['p_cage', 9, 1.15, 1], ['rts_logs', 0, 1.4, 1], ['p_bookcase', 12, 1.0, 1],
   ['p_table', 12, 1.0, 2], ['p_bench', 10, 1.1, 2], ['p_stool', 5, 1.2, 2], ['p_chair', 6, 1.15, 1],
   ['p_crate_metal', 9, 1.2, 2], ['p_chest_wood', 9, 1.2, 1], ['p_stall', 12, 1.0, 1], ['p_bottles', 0, 1.4, 1]],
  [['trunk', 8, 1.5, 3], ['pumpkin', 0, 1.7, 2], ['rocks', 12, 1.1, 2], ['rocks_tall', 12, 1.1, 2], ['grave_broken', 0, 1.5, 1], ['pot', 8, 1.5, 1], ['lantern', 4, 1.7, 2, 78],
   ['rts_pine', 8, 1.15, 2], ['rts_rock', 10, 1.15, 2], ['rts_rocks', 12, 1.0, 2], ['r_beartrap', 0, 1.4, 1], ['p_bucket', 5, 1.3, 1], ['rts_logs', 0, 1.4, 2], ['r_pot3', 7, 1.3, 1], ['p_pickaxe', 0, 1.4, 1], ['rts_gold1', 10, 1.15, 1]],
  [['brazier', 8, 1.6, 3, 120], ['column', 9, 1.4, 2], ['pillar', 5, 1.5, 2], ['candles', 0, 1.7, 2, 56], ['trap', 0, 1.2, 2], ['altar', 14, 1.1, 1], ['urn', 5, 1.6, 1],
   ['p_cauldron', 10, 1.15, 2], ['p_anvil', 8, 1.25, 2], ['p_weaponstand', 10, 1.0, 2], ['p_dummy', 9, 1.0, 1], ['p_workbench', 12, 1.0, 1], ['rts_gold2', 12, 1.0, 2], ['p_candlestick', 5, 1.2, 1, 70], ['r_column_square', 9, 1.1, 1], ['p_sword', 0, 1.5, 1], ['p_shield', 0, 1.4, 1],
   ['p_bench', 10, 1.1, 2], ['p_stool', 5, 1.2, 1], ['p_crate_metal', 9, 1.2, 2], ['p_bottles', 0, 1.4, 1]],
  [['grave_round', 8, 1.5, 3], ['grave_cross', 8, 1.5, 3], ['grave_broken', 0, 1.5, 2], ['grave_bevel', 7, 1.5, 2], ['coffin', 0, 1.3, 2], ['cross', 7, 1.3, 2], ['r_skull', 0, 1.8, 3], ['candles', 0, 1.7, 2, 56],
   ['urn', 5, 1.6, 2], ['altar', 14, 1.1, 1], ['r_statue_stag', 10, 1.15, 1], ['r_bricks', 0, 1.3, 2], ['p_bookstand', 6, 1.2, 1], ['rocks', 12, 1.1, 1], ['r_column_round', 9, 1.1, 2], ['p_pouch', 0, 1.4, 1],
   ['r_candles', 0, 1.7, 2, 56], ['p_vase', 6, 1.3, 1]],
  [['r_column_square', 9, 1.1, 3], ['pillar', 5, 1.5, 2], ['brazier', 8, 1.6, 2, 120], ['p_cauldron', 10, 1.15, 2], ['altar', 14, 1.1, 2], ['r_skull', 0, 1.8, 2], ['p_candlestick', 5, 1.2, 2, 70],
   ['p_bookcase', 12, 1.0, 1], ['p_books', 0, 1.3, 1], ['p_scroll', 0, 1.4, 1], ['r_statue_fox', 10, 1.15, 1], ['rts_gold2', 12, 1.0, 1], ['p_chalice', 0, 1.5, 1], ['r_pot2', 7, 1.3, 2], ['trap', 0, 1.2, 1],
   ['r_bookcase', 12, 1.0, 2], ['p_table', 12, 1.0, 1], ['p_potion2', 0, 1.4, 1], ['p_bottles', 0, 1.4, 1],
   ['r_pot2_broken', 0, 1.3, 1], ['p_vase', 6, 1.3, 1]]
];
function makeProps() {
  const pool = PROP_POOL[G.zone.id], tw = pool.reduce((s, p) => s + p[3], 0), avoid = [];
  for (const i of G.items) avoid.push([i.x, i.y, 40]); for (const n of G.nests) avoid.push([n.x, n.y, 46]); for (const e of G.enemies) avoid.push([e.x, e.y, e.boss ? 80 : 30]);
  for (const P of G.players) avoid.push([P.x, P.y, 70]); avoid.push([G.exit.x, G.exit.y, 60]);
  G.rooms.forEach((r, ri) => {
    if (r.w < 5 || r.h < 4) return;
    /* props that belong against a wall, hung along the room's north edge */
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
    for (let n = rint(3, 6), tries = 0; n > 0 && tries < 26; tries++) {
      const tx = rint(r.x + 1, r.x + r.w - 2), ty = rint(r.y + 1, r.y + r.h - 2), x = tx * T + T / 2 + rnd(-6, 6), y = ty * T + T / 2 + rnd(-6, 6);
      if (!openAt(x, y)) continue;
      if (avoid.some(a => Math.hypot(x - a[0], y - a[1]) < a[2]) || G.props.some(p => Math.hypot(x - p.x, y - p.y) < 40)) continue;
      let w = Math.random() * tw, def = pool[0]; for (const p of pool) { if ((w -= p[3]) <= 0) { def = p; break; } }
      const hp = Math.round((def[1] >= 12 ? 90 : def[1] >= 8 ? 45 : def[1] > 0 ? 30 : 18) * (1 + (G.level - 1) * .04));
      G.props.push({ k: def[0], x, y, sr: def[1], sc: def[2], lit: def[4] || 0, ph: Math.random() * 6, hp, max: hp, fl: 0, wob: 0 }); n--;
      /* a second or third of the same kind beside it, so it looks placed */
      if (Math.random() < .45) for (let c = rint(1, 2); c > 0; c--) {
        const cx2 = x + rnd(-34, 34), cy2 = y + rnd(-26, 26);
        if (!openAt(cx2, cy2)) continue;
        if (avoid.some(a => Math.hypot(cx2 - a[0], cy2 - a[1]) < a[2]) || G.props.some(p => Math.hypot(cx2 - p.x, cy2 - p.y) < 22)) continue;
        G.props.push({ k: def[0], x: cx2, y: cy2, sr: def[1], sc: def[2] * rnd(.86, 1.02), lit: def[4] || 0, ph: Math.random() * 6, hp, max: hp, fl: 0, wob: 0 });
      }
    }
  });
}
/* a patch of ground that keeps hurting things that stand in it */
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

/* ---------- the arena ----------
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

/* ---------- floor hazards ----------
   Spikes run on a slow cycle with a visible warning beat. They hurt foes harder
   than they hurt you, so a corridor trap is a tool as much as a threat. */
function makeHazards() {
  G.hazards = [];
  if (G.level < 2 || !G.rooms.length) return;
  const want = Math.min(11, 2 + Math.floor(G.level * .9)), avoid = [[G.exit.x, G.exit.y, 72]];
  for (const P of G.players) avoid.push([P.x, P.y, 96]);
  for (const i of G.items) avoid.push([i.x, i.y, 36]);
  for (const n of G.nests) avoid.push([n.x, n.y, 40]);
  for (let k = want, t = 0; k > 0 && t < 320; t++) {
    const r = G.rooms[rint(1, G.rooms.length - 1)];
    if (r.w < 5 || r.h < 4) continue;
    const tx = rint(r.x + 1, r.x + r.w - 2), ty = rint(r.y + 1, r.y + r.h - 2);
    if (G.map[ty * MW + tx] !== 0) continue;
    const x = tx * T + T / 2, y = ty * T + T / 2;
    if (!openAt(x, y)) continue;
    if (avoid.some(a => Math.hypot(x - a[0], y - a[1]) < a[2])) continue;
    if (G.props.some(p => Math.hypot(x - p.x, y - p.y) < 28)) continue;
    if (G.hazards.some(h => Math.hypot(x - h.x, y - h.y) < 44)) continue;
    G.hazards.push({ x, y, r: 15, ph: Math.random() * 4, cyc: rnd(2.5, 3.6), dmg: Math.round(8 + G.level * 1.6), hit: new Set(), cy: -1, up: 0, warn: false });
    k--;
  }
}
function updateHazards(dt) {
  for (const h of G.hazards) {
    h.ph += dt;
    const cy = Math.floor(h.ph / h.cyc);
    if (cy !== h.cy) { h.cy = cy; h.hit.clear(); }
    const t = (h.ph % h.cyc) / h.cyc;
    h.warn = t >= .66 && t < .8;
    h.up = t < .8 ? 0 : t < .94 ? Math.min(1, (t - .8) / .05) : Math.max(0, 1 - (t - .94) / .06);
    if (h.warn && Math.random() < .22) G.parts.push({ x: h.x + rnd(-11, 11), y: h.y + rnd(-6, 6), vx: 0, vy: -.3, life: .4, max: .4, col: '#8d93a8', s: 2 });
    if (h.up <= .5) continue;
    if (h.up > .5 && h.rang !== h.cy) { h.rang = h.cy; sfx('bone'); }
    for (const P of G.players) if (!P.down && !h.hit.has(P) && Math.hypot(P.x - h.x, P.y - h.y) < h.r + P.r) { h.hit.add(P); hurtPlayer(P, h.dmg, Math.atan2(P.y - h.y, P.x - h.x)); }
    for (const e of G.enemies.slice()) if (!e.dead && e.hp > 0 && !h.hit.has(e) && Math.hypot(e.x - h.x, e.y - h.y) < h.r + e.r) { h.hit.add(e); hurtFoe(e, h.dmg * 2.4, Math.atan2(e.y - h.y, e.x - h.x)); }
  }
}

/* ---------- breakable props ---------- */
const MATCOL = { stone: ['#8d93a8', '#5b6275', '#d5d9e6'], clay: ['#a8643a', '#7a4426', '#d9a070'], metal: ['#9aa3b2', '#5d6574', '#eef2f8'], wood: ['#8a5a2e', '#5e3c1c', '#c9a062'], bone: ['#e8e0c8', '#b8ae92', '#ffffff'], glass: ['#9fd4e8', '#5d8ea8', '#ffffff'] };
function propMat(k) {
  if (/^(grave|r_column|r_statue|altar|column|pillar|rocks|rts_rock|rts_gold|r_bricks|cross|coffin)/.test(k)) return 'stone';
  if (/^(pot|urn|r_pot|p_vase)/.test(k)) return 'clay';
  if (/(anvil|cauldron|chain|cage|brazier|trap|beartrap|sword|pickaxe|crate_metal|candlestick|lantern)/.test(k)) return 'metal';
  if (/skull/.test(k)) return 'bone';
  if (/(bottles|potion2|chalice)/.test(k)) return 'glass';
  return 'wood';
}
function hurtProp(p, dmg, ang) {
  p.hp -= dmg; p.fl = .1; p.wob = p.hp / p.max < .4 ? .26 : .18; sfx('hit'); const cols = MATCOL[propMat(p.k)];
  burstDir(p.x, p.y - 4, ang, cols[0], 3, 110, .8, 'sq', .9); burstDir(p.x, p.y - 4, ang, cols[2], 2, 140, .6, 'spark', .8);
  if (p.hp <= 0) destroyProp(p);
}
function destroyProp(p) {
  const i = G.props.indexOf(p); if (i < 0) return; G.props.splice(i, 1);
  const m = propMat(p.k), cols = MATCOL[m], big = p.sr >= 10;
  for (let n = 0; n < (big ? 20 : 12); n++) burst(p.x, p.y - 2, cols[n % 2], 1, big ? 150 : 110, 1.1, 'sq');
  burst(p.x, p.y, '#3a4152', big ? 8 : 4, 40, 1.4, 'smoke'); if (m === 'stone' || m === 'metal') burst(p.x, p.y - 4, cols[2], 6, 160, .7, 'spark');
  G.shake = Math.max(G.shake, big ? .14 : .06); sfx(big ? 'door' : 'bone'); G.score += big ? 8 : 3;
  const roll = Math.random();
  if (roll < (big ? .7 : .4)) for (let k = 0; k < (big ? 2 : 1); k++) G.items.push({ kind: 'gold', x: p.x + rnd(-8, 8), y: p.y + rnd(-6, 6), t: 0 });
  else if (roll < (big ? .78 : .46)) G.items.push({ kind: 'food', x: p.x, y: p.y, t: 0 });
  if (Math.random() < .025) G.items.push({ kind: 'gem', x: p.x, y: p.y, t: 0 });
}
function pickFoe() {
  const r = Math.random(), L = G.level;
  if (L >= 3 && r < .09) return 'brute';
  if (L >= 2 && r < .2) return 'hound';
  if (L >= 2 && r < .3) return 'bloat';
  if (L >= 2 && r < .48) return 'bonewalker';
  return r < .74 ? 'gloam' : 'wisp';
}
function spawnFoe(type, x, y, elite) {
  const d = FOES[type], s = 1 + (G.level - 1) * .18;
  if (elite == null) elite = type !== 'warden' && G.level >= 2 && Math.random() < Math.min(.17, .025 + G.level * .013);
  const hp = d.hp * s * (elite ? 2.7 : 1);
  const eaff = [];
  if (elite) {
    const pool = EAFF.slice();
    for (let i = 0, n = G.level >= 7 ? 2 : 1; i < n && pool.length; i++) eaff.push(pool.splice(rint(0, pool.length - 1), 1)[0].id);
  }
  const E = { type, x, y, r: d.r * (elite ? 1.22 : 1), hp, max: hp, spd: d.spd * (1 + (G.level - 1) * .03) * (elite ? .93 : 1), dmg: Math.round((d.dmg + G.level) * (elite ? 1.45 : 1)), col: d.col, elite: !!elite, eaff, t: rnd(0, 6), cd: rnd(1, 2), kx: 0, ky: 0, flash: 0, alert: false, st: 'chase', stt: 0, n: 0, ph: 1, boss: type === 'warden', age: 0, fl: 0, fa: 0, atk: -1, burn: 0, burnDmg: 0, burnT: 0, pois: 0, poisDmg: 0, poisT: 0, chill: 0, dead: 0, fuse: 0, loot: 0, immune: type === 'reaper' };
  if (type === 'warden') {
    E.kind = bossKindOf(G.level);
    const B = BOSSES[E.kind] || BOSSES.count;
    E.hp = E.max = Math.round(hp * B.hpm);
    E.spd *= B.spdm; E.dmg = Math.round(E.dmg * B.dmgm); E.r = B.r; E.n = 0;
  }
  if (elite && G.state === 'play') sfx('elite');
  if (eaff.indexOf('fast') >= 0) E.spd *= 1.55;
  if (eaff.indexOf('warded') >= 0) { E.wardMax = hp * .45; E.ward = E.wardMax; }
  G.enemies.push(E);
}

/* ---------- effects ---------- */
function burst(x, y, col, n, sp, life, kind) {
  if (reduceMotion) n = Math.max(1, Math.round(n * .4));
  if (fxLevel) n = Math.max(1, Math.round(n * fxThin()));
  for (let i = 0; i < n; i++) {
    const a = rnd(0, TAU), v = rnd(.3, 1) * (sp || 80) / 60;
    G.parts.push({ x, y, vx: Math.cos(a) * v, vy: Math.sin(a) * v, life: rnd(.25, .6) * (life || 1), max: .6 * (life || 1), col, s: rnd(1.5, 3.5), k: kind || 'sq' });
  }
}
function burstDir(x, y, ang, col, n, sp, life, kind, spread) {
  if (reduceMotion) n = Math.max(1, Math.round(n * .4));
  for (let i = 0; i < n; i++) { const a = ang + rnd(-spread, spread), v = rnd(.4, 1) * sp / 60; G.parts.push({ x, y, vx: Math.cos(a) * v, vy: Math.sin(a) * v, life: rnd(.25, .5) * (life || 1), max: .5 * (life || 1), col, s: rnd(1.5, 3), k: kind || 'spark' }); }
}
function coinSpray(x, y, n) {
  for (let i = 0; i < n; i++) { const a = rnd(0, TAU), v = rnd(.6, 2.4); G.parts.push({ x, y, vx: Math.cos(a) * v, vy: Math.sin(a) * v * .7, z: 4, vz: rnd(3.2, 6), life: rnd(.9, 1.4), max: 1.4, col: '#f0a23c', s: 3, k: 'coin', sp: rnd(0, 6) }); }
}
function text(x, y, txt, col, sz) { G.texts.push({ x, y, txt, col: col || '#ebe4d2', life: .9, sz: sz || 13 }); }

/* ---------- character sheet ---------- */
function addStat(g, k, v) {
  if (!v) return;
  if (k === 'dmg') g.dmg *= 1 + v;
  else if (k === 'cd') g.cd *= 1 + v;
  else if (k === 'crit') g.crit += v;
  else if (k === 'spd') g.spd *= 1 + v;
  else if (k === 'hp') g.hp += v;
  else if (k === 'arm') g.arm *= 1 - v;
  else if (k === 'leech') g.leech += v;
  else if (k === 'thorns') g.thorns += v;
  else if (k === 'gold') g.gold += v;
  else if (k === 'sp') g.sp += v;
  else if (k === 'dash') g.dash *= 1 + v;
  else if (k === 'drain') g.drain += v;
}
function recalc(P) {
  const g = { dmg: 1, cd: 1, crit: 0, spd: 1, hp: 0, arm: 1, leech: 0, thorns: 0, gold: 0, sp: 0, dash: 1, drain: 0, elem: null, elemDmg: 0 };
  const setN = {};
  for (const slot of SLOTS) {
    const it = P.gear[slot]; if (!it) continue;
    for (const k in it.s) if (k !== 'elem' && k !== 'elemDmg') addStat(g, k, it.s[k]);
    if (it.s.elem && slot === 'weapon') { g.elem = it.s.elem; g.elemDmg = it.s.elemDmg || .4; }
    if (it.set) setN[it.set] = (setN[it.set] || 0) + 1;
  }
  for (const p of (P.pacts || [])) for (const k in p.s) addStat(g, k, p.s[k]);
  P.sets = [];
  for (const id in setN) {
    if (setN[id] < 2) continue;
    const S = SETS.find(x => x.id === id); if (!S) continue;
    const mult = setN[id] >= 3 ? 2 : 1;
    P.sets.push({ id, name: S.name, n: setN[id] });
    for (const k in S.s2) addStat(g, k, S.s2[k] * mult);
  }
  P.g = g;
  P.dmgMul = P.up.dmg * g.dmg;
  P.cdMul = Math.max(.3, P.up.cd * g.cd);
  P.spdMul = clamp(P.up.spd * g.spd, .4, 1.95);
  P.armMul = clamp(P.up.arm * g.arm, .32, 2.2);
  P.dashMul = clamp(P.up.dash * g.dash, .35, 2.4);
  P.crit = Math.min(.75, P.up.crit + g.crit);
  P.drainMul = Math.max(.3, 1 + g.drain + (P.cls.drain || 0) + (P.perkDrain || 0));
  const nm = Math.max(40, Math.round(P.cls.hp + P.up.hp + g.hp)), d = nm - P.max;
  P.max = nm; if (d > 0) P.hp += d;
  P.hp = Math.min(P.hp, P.max);
}
function equip(P, it) {
  const old = P.gear[it.slot];
  P.gear[it.slot] = it; recalc(P);
  text(P.x, P.y - 26, it.name, it.col, 13); sfx('gear');
  burst(P.x, P.y, it.col, 18, 120, 1, 'spark');
  G.fxs.push({ kind: 'shock', x: P.x, y: P.y, t: 0, r: 80, c1: '255,250,230', c2: '200,200,255' });
  return old;
}
const xpNeed = l => Math.round(36 + l * 30 + l * l * 7);
function gainXp(amt) {
  for (const P of G.players) {
    if (P.down) continue;
    P.xp += amt;
    let guard = 0;
    while (P.xp >= xpNeed(P.plvl) && guard++ < 20) {
      P.xp -= xpNeed(P.plvl); P.plvl++;
      P.up.hp += 7; recalc(P); P.hp = Math.min(P.max, P.hp + P.max * .35);
      announceOnce('lvl' + P.idx, .6, P.cls.name + ' reaches level ' + P.plvl, P.cls.col); sfx('level');
      G.fxs.push({ kind: 'shock', x: P.x, y: P.y, t: 0, r: 130, c1: '255,245,210', c2: '240,190,70' });
      burst(P.x, P.y, '#ffd24a', 26, 180, 1.2, 'spark'); sfx('stairs');
      const bo = P.plvl % 2 === 0 ? rollBoons(P) : [];
      if (bo.length) queueOffer({ kind: 'boon', P, opts: bo });
      else queueOffer({ kind: 'up', P, opts: rollOffer(false) });
    }
  }
}
/* one card at a time, the rest wait their turn */
function queueOffer(o) { G.offerQ.push(o); nextOffer(); }
function nextOffer() {
  if (G.offer || !G.offerQ.length || (G.state !== 'play' && G.state !== 'offer')) return;
  G.offer = G.offerQ.shift(); G.state = 'offer';
}
function closeOffer() {
  G.offer = null;
  if (G.offerQ.length) { G.offer = G.offerQ.shift(); G.state = 'offer'; }
  else G.state = 'play';
}

/* ---------- combat ---------- */
function makeDelver(k, i) {
  const c = CLASSES[k];
  const P = { idx: i, x: 0, y: 0, r: 11, cls: c, hp: c.hp, max: c.hp, cd: 0, inv: 0, dash: 0, dashCd: 0, face: 0, aim: 0, hurt: 0, dx: 0, dy: 0, down: false, rev: 0,
    dmgMul: 1, spdMul: 1, cdMul: 1, armMul: 1, dashMul: 1, crit: .1, mast: 0, spCd: 3, shield: 0, cast: 0, chill: 0,
    up: { dmg: 1, spd: 1, cd: 1, arm: 1, dash: 1, crit: .1, hp: 0 },
    gear: { weapon: null, armour: null, trinket: null },
    xp: 0, plvl: 1, buys: {}, boons: {}, pacts: [] };
  P.up.hp += perkLv('vigour') * 12;
  P.up.crit += perkLv('edge') * .04;
  P.perkDrain = -perkLv('slow') * .08;
  P.perkGold = perkLv('purse') * .12;
  if (perkLv('relic')) P.gear.trinket = rollItem('trinket', RARITY.magic, true);
  recalc(P); P.hp = P.max; return P;
}
function startGame(list) {
  if (!Array.isArray(list)) list = [list];
  G.clsKeys = list; G.clsKey = list[0]; G.co = list.length > 1;
  G.players = list.map((k, i) => makeDelver(k, i));
  G.player = G.players[0]; G.gold = 0; G.keys = 0; G.combo = 0; G.comboT = 0; G.comboBest = 0;
  G.tollDeep = 0; G.tollFoes = 0;
  G.bombs = 1 + perkLv('flask'); G.drops = 0; G.kills = 0; G.runT = 0; G.earned = 0; G.zones = []; G.timers = []; G.bolts = []; G.voice = null; G.flash = 0; G.offer = null; G.offerQ = []; G.wares = [];
  G.level = 1; G.score = 0; G.won = false; G.winPending = false; G.gaveUp = false; genLevel(); G.state = 'play'; G.paused = false;
}
function nextLevel() {
  G.level++; G.score += 150 * (G.level - 1);
  for (const P of G.players) if (!P.down && P.hp > 0) P.hp = Math.min(P.max, P.hp + P.max * .3);
  sfx('stairs'); genLevel(); saveRun();
}
function updateRevive(dt) {
  for (const D of G.players) {
    if (!D.down) continue;
    const helper = G.players.some(p => p !== D && !p.down && Math.hypot(p.x - D.x, p.y - D.y) < 42);
    D.rev = helper ? D.rev + dt : Math.max(0, D.rev - dt * 2);
    if (D.rev >= 1.5) { D.down = false; D.rev = 0; D.hp = D.max * .4; D.inv = 1.5; D.rise = .75; G.fxs.push({ kind: 'shock', x: D.x, y: D.y, t: 0, r: 80, c1: '220,255,200', c2: '155,209,106' }); text(D.x, D.y - 18, 'Revived', '#9bd16a'); burst(D.x, D.y, '#9bd16a', 16, 100); sfx('coin'); }
  }
}
function runEchoes() {
  return Math.max(1, Math.round(G.gold * .25 + G.score / 40 + (G.level - 1) * 8)) * (G.won ? 2 : 1);
}
function bankRun() {
  G.best = Math.max(G.best, G.score);
  G.earned = runEchoes();
  META.echoes += G.earned; META.best = G.best; META.runs = (META.runs || 0) + 1;
  META.deepest = Math.max(META.deepest || 1, G.level);
  saveMeta();
}
function die() {
  if (G.state === 'dead') return;
  G.state = 'dead'; bankRun(); clearRun();
  announce(G.won ? 'You carried the Heart out of the dark' : G.gaveUp ? 'You turned back' : 'Swallowed by the deep', G.gaveUp ? '#98a0b3' : G.won ? '#ffd24a' : '#d9534f');
}
/* the Heart is down: the run is won, but it is the player's call whether to
   climb out with it or keep going into whatever is below twenty-one */
function winRun() {
  if (G.won) return;
  G.won = true; G.score += 5000;
  META.wins = (META.wins || 0) + 1;
  META.best = Math.max(META.best || 0, G.score);
  saveMeta();
  announce('The Hollow Heart is still. You have beaten the deep.', '#ffd24a');
  G.timers.push({ t: 2.6, fn: () => { G.winPending = true; } });
}
function downPlayer(P) {
  if (P.down) return;
  P.hp = 0; P.down = true; P.rev = 0; burst(P.x, P.y, P.cls.col, 18, 120); text(P.x, P.y - 22, 'Down!', '#d9534f');
  announceOnce('down' + P.idx, 1.5, P.cls.name + ' has fallen', '#d9534f');
  if (G.players.every(p => p.down)) die();
}
function hurtPlayer(P, dmg, ang, src) {
  if (P.down || P.inv > 0 || G.state !== 'play') return;
  const d = Math.max(1, Math.round(dmg * P.cls.armor * P.armMul * (P.shield > 0 ? .3 : 1)));
  const wasHp = P.hp;
  P.hp -= d; toll('foes', wasHp, P);
  P.inv = .55; P.hurt = .25; P.lastHit = clock; G.shake = Math.max(G.shake, .3);
  if (bn(P, 'riposte')) { P.cd = 0; P.nextCrit = true; burst(P.x, P.y, '#fff1b8', 10, 150, .8, 'spark'); }
  if (G.combo > 0) { G.combo = Math.floor(G.combo * .5); if (G.combo <= 0) G.comboT = 0; }
  moveEnt(P, Math.cos(ang) * -6, Math.sin(ang) * -6);
  text(P.x, P.y - 16, '-' + d, '#d9534f'); sfx('hurt'); burst(P.x, P.y, '#d9534f', 6, 70);
  if (src && src.hp > 0 && !src.dead) {
    if (P.g && P.g.thorns > 0) hurtFoe(src, d * P.g.thorns, ang + Math.PI, false, false, null);
    if (src.eaff) {
      if (src.eaff.indexOf('vamp') >= 0) { src.hp = Math.min(src.max, src.hp + d * .6); burst(src.x, src.y, '#d9534f', 5, 80, .7, 'spark'); }
      if (src.eaff.indexOf('frozen') >= 0) { P.chill = 1.8; burst(P.x, P.y, '#8fd3ff', 8, 90, .8, 'spark'); }
    }
  }
  if (P.hp <= 0) downPlayer(P);
}
const comboMult = () => 1 + Math.min(1.6, G.combo * .055);
/* Death shrugs off ordinary blows; only a special or a potion counts */
let SMITE = false;
function applyElem(e, P, dmg) {
  const g = P && P.g; if (!g || !g.elem) return;
  const el = g.elem, m = elemMul(e, el), col = ELEM_COL[el] || '#ebe4d2';
  const ed = Math.max(1, dmg * g.elemDmg * m);
  const direct = Math.round(ed * .45);
  if (direct > 0) { e.hp -= direct; text(e.x + rnd(-9, 9), e.y - e.r - 11, String(direct), col, m > 1 ? 15 : 11); }
  if (!e.wkT || clock - e.wkT > 1.3) {
    e.wkT = clock;
    if (m > 1) { text(e.x, e.y - e.r - 22, 'Weak to ' + ELEM_NAME[el], col, 13); burst(e.x, e.y, col, 8, 130, .8, 'spark'); }
    else if (m < 1) text(e.x, e.y - e.r - 22, 'Resists ' + ELEM_NAME[el], '#98a0b3', 11);
  }
  if (el === 'fire') { e.burn = Math.max(e.burn || 0, 2.4 * m); e.burnDmg = Math.max(e.burnDmg || 0, Math.max(1, ed * .4)); }
  else if (el === 'cold') { e.chill = Math.max(e.chill || 0, 2 * m); burst(e.x, e.y, '#8fd3ff', 4, 80, .7, 'spark'); if (Math.random() < .3) scorch(e.x, e.y, 12 + Math.random() * 8, '#7fc0e8', 'frost'); }
  else if (el === 'poison') { e.pois = Math.max(e.pois || 0, 3.4 * m); e.poisDmg = Math.max(e.poisDmg || 0, Math.max(1, ed * .28)); if (Math.random() < .3) scorch(e.x, e.y, 11 + Math.random() * 7, '#7aa84e', 'frost'); }
  else if (el === 'shock') {
    let n = 0, reach = m > 1 ? 150 : 115;
    for (const o of G.enemies.slice()) {
      if (n >= (m > 1 ? 3 : 2) || o === e || o.dead || o.hp <= 0) continue;
      if (Math.hypot(o.x - e.x, o.y - e.y) > reach) continue;
      n++; G.bolts.push({ x1: e.x, y1: e.y, x2: o.x, y2: o.y, t: 0 });
      hurtFoe(o, ed, Math.atan2(o.y - e.y, o.x - e.x), false, false, null);
    }
  }
}
function hurtFoe(e, dmg, ang, crit, burn, src) {
  if (e.dead) return;
  if (e.immune && !SMITE) {
    if (!e.immT || clock - e.immT > .9) { e.immT = clock; text(e.x, e.y - e.r - 6, 'Immune', '#cfd4e0', 12); }
    burst(e.x, e.y, '#cfd4e0', 3, 70, .6, 'spark'); return;
  }
  if (e.eaff && e.eaff.indexOf('warded') >= 0 && e.ward > 0) {
    e.ward -= dmg; e.wardFl = .18;
    burst(e.x, e.y, '#ffd24a', 4, 90, .6, 'spark'); text(e.x, e.y - e.r - 4, 'Blocked', '#ffd24a', 12); sfx('ward');
    if (e.ward > 0) return;
    dmg = -e.ward; e.ward = 0;
  }
  if (crit) dmg *= 2.25;
  if (e.mark > 0) dmg *= 1.25;
  dmg = Math.round(dmg); e.hp -= dmg; e.flash = .1; e.alert = true; e.fl = crit ? .3 : .2; e.fa = ang;
  const kb = (e.boss ? .2 : 1) * (crit ? 1.5 : 1); e.kx += Math.cos(ang) * 2.2 * kb; e.ky += Math.sin(ang) * 2.2 * kb;
  if (burn) { e.burn = Math.max(e.burn || 0, 2.4); e.burnDmg = Math.max(e.burnDmg || 0, Math.max(2, dmg * .16)); if (bn(src, 'kindle')) e.kindled = 1; }
  text(e.x, e.y - e.r - 4, crit ? dmg + '!' : String(dmg), crit ? '#fff1b8' : dmg >= 40 ? '#ffd24a' : '#ebe4d2', crit ? Math.min(31, 17 + dmg * .12) : Math.min(24, 12 + dmg * .1));
  sfx('hit'); G.hitstop = Math.max(G.hitstop, crit ? .05 : e.boss || e.type === 'brute' ? .035 : .02); burst(e.x, e.y, e.col, 3, 60, .7); burst(e.x, e.y, '#fff3d0', 4, 120, .5, 'spark');
  burstDir(e.x, e.y, ang, '#fff3d0', 5, 230, .9, 'spark', .7); burstDir(e.x, e.y, ang, e.col, 4, 150, 1, 'sq', .9); G.fxs.push({ kind: 'hit', x: e.x, y: e.y, t: 0 });
  if (crit) { G.fxs.push({ kind: 'crit', x: e.x, y: e.y - 4, t: 0, a: ang }); burstDir(e.x, e.y, ang, '#fff1b8', 10, 330, 1.1, 'spark', .45); G.shake = Math.max(G.shake, .16); sfx('crit'); e.imp = .07; }
  if (e.hp <= 0) e.imp = Math.max(e.imp || 0, .09);
  if (dmg >= 40 || e.boss || e.type === 'brute') G.shake = Math.max(G.shake, .08);
  if (src) {
    applyElem(e, src, dmg);
    /* Spiny: it pricks whoever is close enough to have struck it. Its own
       cooldown rather than the delver's invulnerability, so being pricked
       never becomes a shield against the thing doing the pricking. */
    if (e.eaff && e.eaff.indexOf('spiny') >= 0 && src.cls && !src.down &&
        (!e.spineT || clock - e.spineT > .45) &&
        Math.hypot(src.x - e.x, src.y - e.y) < e.r + (src.r || 11) + 26) {
      e.spineT = clock;
      const back = Math.max(1, Math.round(e.dmg * .35)), was = src.hp;
      src.hp -= back; toll('foes', was, src);
      src.hurt = Math.max(src.hurt, .18);
      text(src.x, src.y - 16, '-' + back, '#9bd16a');
      burst(src.x, src.y, '#9bd16a', 6, 90, .8, 'spark');
      if (src.hp <= 0) downPlayer(src);
    }
    if (src.g && src.g.leech > 0 && !src.down && src.hp < src.max) {
      src.hp = Math.min(src.max, src.hp + dmg * src.g.leech);
      if (Math.random() < .4) G.parts.push({ x: e.x, y: e.y, vx: (src.x - e.x) * .02, vy: (src.y - e.y) * .02, life: .4, max: .4, col: '#d9534f', s: 2.2 });
    }
  }
  if (e.hp <= 0) finishFoe(e, ang);
}
function finishFoe(e) {
  if (e.dead) return; e.dead = 1;
  if (e.type === 'bloat') bloatPop(e); else killFoe(e);
}
/* a bloat going off hurts whatever is nearby, foes included, so a tight pack can chain */
function bloatPop(e) {
  const R = 74, dm = e.dmg * 1.8;
  G.shake = Math.max(G.shake, .34); sfx('boom'); G.hitstop = Math.max(G.hitstop, .05);
  G.slash = { x: e.x, y: e.y, a: 0, life: .22, kind: 'boom', rad: R };
  G.fxs.push({ kind: 'shock', x: e.x, y: e.y, t: 0, r: R + 24, c1: '234,255,196', c2: '143,191,90' });
  burst(e.x, e.y, '#8fbf5a', 24, 175, 1.2); burst(e.x, e.y, '#d8f0a0', 12, 240, .8, 'spark'); burst(e.x, e.y, '#3a4152', 8, 55, 1.5, 'smoke');
  for (const P of G.players) if (!P.down && Math.hypot(P.x - e.x, P.y - e.y) < R + P.r) hurtPlayer(P, dm, Math.atan2(P.y - e.y, P.x - e.x));
  for (const n of G.nests) if (n.hp > 0 && Math.hypot(n.x - e.x, n.y - e.y) < R + n.r) hurtNest(n, dm);
  for (const p of G.props.slice()) if (Math.hypot(p.x - e.x, p.y - e.y) < R + 8) hurtProp(p, dm, Math.atan2(p.y - e.y, p.x - e.x));
  e.hp = 0; killFoe(e);
  for (const o of G.enemies.slice()) {
    if (o === e || o.dead || o.hp <= 0) continue;
    if (Math.hypot(o.x - e.x, o.y - e.y) >= R + o.r) continue;
    if (o.type === 'bloat' && o.fuse <= 0) { o.fuse = .22; o.alert = true; sfx('bone'); }
    else hurtFoe(o, dm * 1.15, Math.atan2(o.y - e.y, o.x - e.x));
  }
}
function killFoe(e) {
  const base = ({ gloam: 10, wisp: 8, bonewalker: 15, brute: 40, hound: 14, bloat: 22, thief: 45, reaper: 120, warden: 500 }[e.type] || 10) * (e.elite ? 3 : 1);
  if (!e.boss) { G.combo++; G.comboT = 3.2; if (G.combo > G.comboBest) G.comboBest = G.combo; }
  G.score += Math.round(base * comboMult());
  G.kills = (G.kills || 0) + 1;
  if (e.elite) G.elites = (G.elites || 0) + 1;
  if (e.boss) G.bosses = (G.bosses || 0) + 1;
  gainXp(Math.max(1, Math.round(base * (.5 + G.level * .05))));
  if (G.combo >= 5 && G.combo % 5 === 0) { text(e.x, e.y - 42, G.combo + ' chain', '#ffd24a', 16); sfx('coin'); }
  G.hitstop = Math.max(G.hitstop, e.boss ? .14 : e.type === 'brute' ? .07 : .04);
  burst(e.x, e.y, e.col, 14, 110);
  G.dying.push({ type: e.type, kind: e.kind, x: e.x, y: e.y, r: e.r, col: e.col, face: e.face || 0, t: 0, walk: e.walk || 0 });
  G.decals.push({ x: e.x, y: e.y, r: e.r, col: e.col, k: e.type, rot: rnd(0, TAU) }); if (G.decals.length > 90) G.decals.shift();
  if (e.type === 'bonewalker') burst(e.x, e.y, '#ebe4d2', 10, 130, 1, 'spark');
  else if (e.type === 'gloam') burst(e.x, e.y, e.col, 8, 50, 1.2, 'drip');
  else if (e.type === 'wisp') burst(e.x, e.y, '#8fd3ff', 12, 70, 1.4, 'ember');
  else if (e.type === 'brute') { burst(e.x, e.y, '#ff6a4d', 14, 120, 1.2, 'ember'); G.shake = Math.max(G.shake, .2); }
  burst(e.x, e.y, '#3a4152', 5, 40, 1.4, 'smoke');
  if (e.boss && e.kind === 'heart') {
    for (let i = 0; i < 3; i++) G.items.push({ kind: 'chest', x: e.x + (i - 1) * 46, y: e.y + 10, t: 0, big: true });
    for (let i = 0; i < 14; i++) G.items.push({ kind: 'gold', x: e.x + rnd(-60, 60), y: e.y + rnd(-50, 50), t: 0 });
    G.shake = 1; coinSpray(e.x, e.y, 60); sfx('boom');
    G.fxs.push({ kind: 'shock', x: e.x, y: e.y, t: 0, r: 220, c1: '255,240,220', c2: '255,59,92' },
               { kind: 'shock', x: e.x, y: e.y, t: -.2, r: 340, c1: '255,255,255', c2: '255,120,140' },
               { kind: 'shock', x: e.x, y: e.y, t: -.42, r: 460, c1: '255,240,220', c2: '255,59,92' });
    burst(e.x, e.y, '#fff3d0', 60, 300, 1.4, 'spark'); burst(e.x, e.y, '#ff3b5c', 40, 220, 1.6, 'ember');
    text(e.x, e.y - 44, 'The Hollow is still', '#ffd24a', 22);
    G.enemies.forEach(o => { if (o !== e && o.hp > 0) o.hp = 0; });
    winRun();
  } else if (e.boss) {
    G.items.push({ kind: 'key', x: e.x, y: e.y, t: 0 }); G.items.push({ kind: 'chest', x: e.x + 28, y: e.y, t: 0, big: true });
    for (let i = 0; i < 6; i++) G.items.push({ kind: 'gold', x: e.x + rnd(-34, 34), y: e.y + rnd(-34, 34), t: 0 });
    G.shake = .6; coinSpray(e.x, e.y, 26); G.fxs.push({ kind: 'shock', x: e.x, y: e.y, t: 0, r: 150, c2: '240,162,60' }, { kind: 'shock', x: e.x, y: e.y, t: -.18, r: 240, c1: '255,240,200', c2: '255,120,60' }); sfx('boom'); text(e.x, e.y - 36, 'Warden fallen', '#f0a23c', 18); burst(e.x, e.y, '#fff3d0', 30, 220, 1, 'spark'); burst(e.x, e.y, e.col, 24, 160, 1.4, 'ember');
    G.enemies.forEach(o => { if (o !== e && o.hp > 0 && o.type === 'gloam') { o.hp = 0; } });
  }
  if (e.eaff && e.eaff.indexOf('fiery') >= 0) {
    const R = 92, dm = e.dmg * 1.5;
    G.fxs.push({ kind: 'shock', x: e.x, y: e.y, t: 0, r: R + 20, c1: '255,240,200', c2: '255,106,60' });
    G.slash = { x: e.x, y: e.y, a: 0, life: .22, kind: 'boom', rad: R };
    burst(e.x, e.y, '#ff6a3d', 22, 180, 1.2, 'ember'); G.shake = Math.max(G.shake, .3); sfx('boom');
    for (const p of G.players) if (!p.down && Math.hypot(p.x - e.x, p.y - e.y) < R + p.r) hurtPlayer(p, dm, Math.atan2(p.y - e.y, p.x - e.x));
  }
  if (e.boss) { dropGear(e.x - 34, e.y + 8, 32); dropGear(e.x + 34, e.y + 8, 32); }
  else if (e.elite) dropGear(e.x, e.y, 14);
  else if (e.type !== 'thief' && e.type !== 'reaper' && Math.random() < .022) dropGear(e.x, e.y, 0);
  if (e.kindled && e.burn > 0) {
    const R = 76, dm2 = Math.max(8, (e.burnDmg || 4) * 7);
    G.fxs.push({ kind: 'shock', x: e.x, y: e.y, t: 0, r: R + 18, c1: '255,240,200', c2: '255,120,50' });
    G.slash = { x: e.x, y: e.y, a: 0, life: .22, kind: 'boom', rad: R };
    burst(e.x, e.y, '#ff8a3a', 20, 170, 1.2, 'ember'); G.shake = Math.max(G.shake, .24); sfx('boom');
    for (const o of G.enemies.slice()) if (o !== e && !o.dead && o.hp > 0 && Math.hypot(o.x - e.x, o.y - e.y) < R + o.r) hurtFoe(o, dm2, Math.atan2(o.y - e.y, o.x - e.x), false, true, null);
  }
  if (e.type === 'thief' && e.loot > 0) {
    coinSpray(e.x, e.y, 14); announceOnce('recovered', 2, 'The thief drops its purse', '#f0a23c');
    for (let i = 0; i < Math.min(8, 1 + Math.round(e.loot / 25)); i++) G.items.push({ kind: 'gold', x: e.x + rnd(-20, 20), y: e.y + rnd(-16, 16), t: 0, v: Math.round(e.loot / Math.min(8, 1 + Math.round(e.loot / 25))) });
  }
  if (e.elite) {
    coinSpray(e.x, e.y, 10); G.shake = Math.max(G.shake, .26); sfx('boom');
    G.fxs.push({ kind: 'shock', x: e.x, y: e.y, t: 0, r: 110, c1: '255,245,205', c2: '240,190,70' });
    for (let i = 0; i < 3; i++) G.items.push({ kind: 'gold', x: e.x + rnd(-20, 20), y: e.y + rnd(-16, 16), t: 0 });
    G.items.push(Math.random() < .45 ? { kind: 'chest', x: e.x, y: e.y, t: 0 } : { kind: 'gem', x: e.x, y: e.y, t: 0 });
    text(e.x, e.y - 30, 'Elite slain', '#ffd24a', 15);
  }
  if (Math.random() < FOES[e.type].gold) G.items.push({ kind: 'gold', x: e.x, y: e.y, t: 0 });
  if (Math.random() < .07) G.items.push({ kind: 'food', x: e.x, y: e.y, t: 0 });
  if (e.type === 'brute' && Math.random() < .35) G.items.push({ kind: 'chest', x: e.x, y: e.y, t: 0 });
}
function hurtNest(n, dmg) {
  if (n.hp <= 0) return;
  n.hp -= dmg; n.flash = .1; sfx('hit'); burst(n.x, n.y, '#c2563f', 3, 60, .7); text(n.x, n.y - 20, String(Math.round(dmg)));
  if (n.hp <= 0) {
    G.score += 100; G.shake = Math.max(G.shake, .35); sfx('boom'); burst(n.x, n.y, '#c2563f', 26, 160, 1.2);
    for (let i = 0; i < 3; i++) G.items.push({ kind: 'gold', x: n.x + rnd(-14, 14), y: n.y + rnd(-14, 14), t: 0 });
  }
}
function scorch(x, y, r, col, kind) {
  G.decals.push({ x, y, r, col, k: kind || 'scorch', rot: rnd(0, TAU) });
  if (G.decals.length > 110) G.decals.shift();
}
function explode(s) {
  G.shake = Math.max(G.shake, .18); sfx('boom'); burst(s.x, s.y, '#ff6a4d', 18, 150); burst(s.x, s.y, '#f0a23c', 10, 90); burst(s.x, s.y, '#3a4152', 6, 50, 1.4, 'smoke'); burst(s.x, s.y, '#fff3d0', 8, 160, .6, 'spark');
  G.slash = { x: s.x, y: s.y, a: 0, life: .22, kind: 'boom', rad: s.rad };
  scorch(s.x, s.y, Math.max(14, s.rad * .55), '#2a1c14', 'scorch');
  if (bn(s.own, 'pyre')) addZone(s.x, s.y, Math.max(26, s.rad * .72), Math.max(2, s.dmg * .16), 4, s.own);
  if (bn(s.own, 'split') && !s.isSplit) {
    for (let i = 0; i < 3; i++) {
      const an = rnd(0, TAU);
      G.shots.push({ x: s.x, y: s.y, vx: Math.cos(an) * 5.5, vy: Math.sin(an) * 5.5, dmg: s.dmg * .45, life: .5, r: 5, kind: 'fire', col: '#ff8a3a', pierce: 0, rad: Math.max(22, (s.rad || 40) * .55), hit: new Set(), trail: [], crit: false, own: s.own, isSplit: 1 });
    }
  }
  for (const e of G.enemies.slice()) if (e.hp > 0 && Math.hypot(e.x - s.x, e.y - s.y) < s.rad + e.r) hurtFoe(e, s.dmg * .7, Math.atan2(e.y - s.y, e.x - s.x), s.crit, true, s.own);
  for (const n of G.nests) if (n.hp > 0 && Math.hypot(n.x - s.x, n.y - s.y) < s.rad + n.r) hurtNest(n, s.dmg * .7);
  for (const p of G.props.slice()) if (Math.hypot(p.x - s.x, p.y - s.y) < s.rad + 8) hurtProp(p, s.dmg * .7, Math.atan2(p.y - s.y, p.x - s.x));
}
function useBomb(P) {
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
const SP_CD = 9;
const SPECIALS = { bulwark: 'Shield Slam', ember: 'Fire Nova', sable: 'Shadow Step', thistle: 'Entangle' };
const SPECIAL_DESC = {
  bulwark: 'a shield for a moment, everything near you hurled back, and arrows already in the air swept out of it',
  ember: 'a burst all around you, and ten bolts thrown outward through whatever is left',
  sable: 'slip forward untouchable, and leave a ring of daggers where you were',
  thistle: 'roots everything near you to the floor for a few seconds'
};
const specialLine = c => SPECIALS[c.key] + ' \u2014 ' + SPECIAL_DESC[c.key] + '.';
function special(P) {
  if (P.down || P.spCd > 0 || G.state !== 'play') return;
  const c = P.cls, dm = c.dmg * P.dmgMul, a = P.aim, cr = Math.random() < P.crit;
  P.spMax = Math.max(2.5, SP_CD - (P.g ? P.g.sp : 0)); P.spCd = P.spMax; P.swing = P.swm = .34; P.cast = .4; P.cd = Math.max(P.cd, .25);
  const ring = (r, c1, c2, d) => G.fxs.push({ kind: 'shock', x: P.x, y: P.y, t: d || 0, r, c1, c2 });
  const near = (R, fn) => { for (const e of G.enemies.slice()) if (e.hp > 0 && Math.hypot(e.x - P.x, e.y - P.y) < R + e.r) fn(e, Math.atan2(e.y - P.y, e.x - P.x)); for (const n of G.nests.slice()) if (n.hp > 0 && Math.hypot(n.x - P.x, n.y - P.y) < R + n.r) hurtNest(n, dm * 1.5); for (const p of G.props.slice()) if (Math.hypot(p.x - P.x, p.y - P.y) < R + 8) hurtProp(p, dm * 2, Math.atan2(p.y - P.y, p.x - P.x)); };
  text(P.x, P.y - 30, SPECIALS[c.key], c.col, 14);
  SMITE = true;
  if (c.key === 'bulwark') {
    P.shield = 2.5; G.shake = Math.max(G.shake, .35); sfx('boom'); ring(120, '255,240,200', '231,176,74'); ring(70, '255,255,255', '231,176,74', -.08);
    near(115, (e, ang) => { hurtFoe(e, dm * 1.9, ang, cr, false, P); e.kx += Math.cos(ang) * (e.boss ? 1 : 9); e.ky += Math.sin(ang) * (e.boss ? 1 : 9); });
    G.eshots = G.eshots.filter(s => Math.hypot(s.x - P.x, s.y - P.y) > 120);
    burst(P.x, P.y, '#e7b04a', 22, 190, 1, 'spark'); burst(P.x, P.y, '#9aa3b8', 10, 120, 1.2, 'smoke');
  } else if (c.key === 'ember') {
    G.shake = Math.max(G.shake, .3); sfx('boom'); ring(140, '255,240,200', '255,106,77'); ring(90, '255,200,120', '255,80,40', -.1);
    explode({ x: P.x, y: P.y, rad: 125, dmg: dm * 3, crit: cr, own: P });
    for (let i = 0; i < 10; i++) { const ang = i / 10 * TAU; G.shots.push({ x: P.x + Math.cos(ang) * 14, y: P.y + Math.sin(ang) * 14, vx: Math.cos(ang) * 5, vy: Math.sin(ang) * 5, dmg: dm * .9, life: .9, r: 7, kind: 'fire', col: c.col, pierce: 0, rad: 44, hit: new Set(), trail: [], crit: cr, own: P }); }
  } else if (c.key === 'sable') {
    burst(P.x, P.y, '#1a2a30', 18, 90, 1, 'smoke'); burst(P.x, P.y, c.col, 12, 150, .7, 'spark');
    for (let i = 0; i < 9; i++) moveEnt(P, Math.cos(a) * 17, Math.sin(a) * 17);
    P.inv = Math.max(P.inv, .7); sfx('dash'); ring(70, '200,255,250', '127,209,199'); burst(P.x, P.y, '#1a2a30', 14, 90, 1, 'smoke'); burst(P.x, P.y, c.col, 14, 170, .8, 'spark');
    for (let i = 0; i < 10; i++) { const ang = i / 10 * TAU; G.shots.push({ x: P.x, y: P.y, vx: Math.cos(ang) * 9, vy: Math.sin(ang) * 9, dmg: dm * 2, life: .5, r: 4, kind: 'dagger', col: c.col, pierce: 0, rad: 0, hit: new Set(), trail: [], crit: cr, own: P }); }
  } else {
    sfx('door'); ring(150, '230,255,200', '155,209,106'); ring(100, '200,255,160', '90,160,60', -.12);
    near(145, (e, ang) => { hurtFoe(e, dm * 1.3, ang, cr, false, P); e.root = e.boss ? 1.2 : 3.2; });
    for (let i = 0; i < 26; i++) { const ang = rnd(0, TAU), d = rnd(20, 140); G.parts.push({ x: P.x + Math.cos(ang) * d, y: P.y + Math.sin(ang) * d, vx: 0, vy: -rnd(.2, .8), life: rnd(.5, 1.2), max: 1.2, col: '#5fa03c', s: 3, k: 'ember' }); }
    burst(P.x, P.y, '#9bd16a', 18, 150, 1, 'spark');
  }
  SMITE = false;
}
function attack(P) {
  const c = P.cls; if (P.down || P.cd > 0) return; P.cd = c.cd * P.cdMul; P.swm = Math.max(.17, Math.min(.34, c.cd * P.cdMul * 1.15)); P.swing = P.swm;
  const dm = c.dmg * P.dmgMul, rg = (c.range || 0) + 9 * P.mast + (bn(P, 'cyclone') ? 10 : 0);
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
    }
    for (const n of G.nests) if (n.hp > 0 && inArc(n, n.r)) hurtNest(n, dm);
    for (const p of G.props.slice()) if (inArc(p, Math.max(p.sr, 9))) hurtProp(p, dm, a);
    return;
  }
  sfx('shoot');
  const mk = ang => ({ x: P.x + Math.cos(a) * 12, y: P.y + Math.sin(a) * 12, vx: Math.cos(ang) * c.shot, vy: Math.sin(ang) * c.shot, dmg: dm, life: c.atk === 'arrow' ? 1.3 : c.atk === 'fire' ? 1.5 : .8, r: c.atk === 'fire' ? 7 : 4, kind: c.atk, col: c.col, pierce: c.atk === 'arrow' ? 2 + P.mast : 0, rad: (c.rad || 0) + 9 * P.mast, hit: new Set(), trail: [], crit: cr, own: P });
  G.shots.push(mk(a + (c.atk === 'dagger' ? rnd(-.07, .07) : 0)));
  if (c.atk === 'dagger') for (let k = 1; k <= Math.min(3, P.mast); k++) G.shots.push(mk(a + (k % 2 ? 1 : -1) * .2 * Math.ceil(k / 2)));
  if (c.atk === 'dagger' && bn(P, 'fan')) { G.shots.push(mk(a - .23)); G.shots.push(mk(a + .23)); }
  if (c.atk === 'arrow' && bn(P, 'volley')) { G.shots.push(mk(a - .17)); G.shots.push(mk(a + .17)); }
}

function dropGear(x, y, bonus) {
  const it = rollItem(null, rollRarity(bonus || 0));
  G.items.push({ kind: 'gear', x, y, t: 0, item: it });
  G.drops++;
  burstDir(x, y, -Math.PI / 2, it.col, 12, 210, 1.1, 'spark', .8);
  sfx('gear');
  return it;
}

/* ---------- chests and upgrades ---------- */
const UP_IDS = ['vit', 'swift', 'power', 'haste', 'ward', 'dash', 'crit', 'master'];
function upInfo(P, id, m) {
  const r = v => Math.round(v * m);
  const mast = { melee: ['Whetstone', 'Sword reaches further and sweeps wider.'], fire: ['Wildfire', 'Fire bursts grow larger.'], dagger: ['Twin Blades', 'Throw an extra dagger each volley.'], arrow: ['Barbed Heads', 'Arrows pierce one more foe.'] }[P.cls.atk];
  const t = {
    vit: ['Vitality', '+' + r(25) + ' max health and heal that much.', '#d9534f'],
    swift: ['Fleet Feet', '+' + r(10) + '% move speed.', '#8fd3ff'],
    power: ['Might', '+' + r(20) + '% damage.', '#f0a23c'],
    haste: ['Quick Hands', 'Attack ' + r(12) + '% faster.', '#9bd16a'],
    ward: ['Iron Skin', 'Take ' + r(8) + '% less damage.', '#98a0b3'],
    dash: ['Light Step', 'Dash recharges ' + r(20) + '% faster.', '#8fd3ff'],
    crit: ['Keen Edge', '+' + r(8) + '% chance to strike critically for double damage.', '#ffd24a'],
    master: [mast[0], mast[1] + (m > 1 ? ' Rare: two levels at once.' : ''), P.cls.col]
  }[id];
  return { name: t[0], desc: t[1], col: t[2] };
}
function rollOffer(big) {
  const pool = UP_IDS.slice(), out = [], rare = (big ? .5 : .15) + G.level * .02;
  while (out.length < 3) { const id = pool.splice(Math.floor(Math.random() * pool.length), 1)[0]; out.push({ id, m: Math.random() < rare ? 1.6 : 1 }); }
  return out;
}
function openChest(P, it) {
  sfx('door'); G.shake = Math.max(G.shake, it.big ? .3 : .18); G.hitstop = Math.max(G.hitstop, .04); burst(it.x, it.y, '#f0a23c', 22, 130); coinSpray(it.x, it.y, it.big ? 20 : 11); burstDir(it.x, it.y, -Math.PI / 2, '#fff3d0', 14, 260, 1.1, 'spark', .9); G.fxs.push({ kind: 'chest', x: it.x, y: it.y, t: 0, big: !!it.big });
  G.gold += it.big ? 60 : 25; G.score += it.big ? 60 : 25; text(it.x, it.y - 14, '+' + (it.big ? 60 : 25), '#f0a23c');
  queueOffer({ kind: 'up', P, opts: rollOffer(it.big) });
  if (it.big) dropGear(it.x, it.y, 18);
}
function applyUp(P, id, m) {
  if (id === 'vit') P.up.hp += Math.round(25 * m);
  else if (id === 'swift') P.up.spd += .07 * m;
  else if (id === 'power') P.up.dmg += .2 * m;
  else if (id === 'haste') P.up.cd *= 1 - .12 * m;
  else if (id === 'ward') P.up.arm *= 1 - .08 * m;
  else if (id === 'dash') P.up.dash *= 1 - .2 * m;
  else if (id === 'crit') P.up.crit += .08 * m;
  else if (id === 'master') P.mast = Math.min(6, P.mast + (m > 1 ? 2 : 1));
  recalc(P);
  const info = upInfo(P, id, m); text(P.x, P.y - 22, info.name + '!', info.col); sfx('stairs');
  burst(P.x, P.y, info.col, 16, 100);
}
function applyUpgrade(i) {
  const o = G.offer;
  if (!o) return;
  if ((o.kind === 'boon' || !o.kind || o.kind === 'up') && !o.opts[i]) return;
  if (o.kind === 'gear') { if (i === 0) equip(o.P, o.item); else { text(o.P.x, o.P.y - 20, 'Left behind', '#98a0b3'); } }
  else if (o.kind === 'boon') {
    const b = o.opts[i], P = o.P;
    P.boons[b.id] = 1;
    text(P.x, P.y - 24, b.name + '!', P.cls.col, 15); sfx('level');
    announceOnce('boon' + P.idx, .5, P.cls.name + ' learns ' + b.name, P.cls.col);
    G.fxs.push({ kind: 'shock', x: P.x, y: P.y, t: 0, r: 140, c1: '255,250,225', c2: '200,180,255' });
    burst(P.x, P.y, P.cls.col, 28, 190, 1.3, 'spark');
  }
  else if (o.kind === 'pact') {
    const P = o.P, it = o.shrine, sh = it.sh;
    if (i !== 0) { it.cool = 2.5; text(P.x, P.y - 20, 'Left unlit', '#98a0b3'); closeOffer(); return; }
    const idx = G.items.indexOf(it); if (idx >= 0) G.items.splice(idx, 1);
    const p = sh.pact, col = shrineCol(sh);
    if (p.s) { P.pacts.push(p); recalc(P); }
    else if (p.id === 'mend') { P.hp = P.max; for (const D of G.players) if (D.down) { D.down = false; D.hp = D.max * .5; D.rev = 0; D.inv = 1; } }
    else if (p.id === 'ward') P.shield = Math.max(P.shield, 9);
    else if (p.id === 'hoard') { G.gold += 60 + G.level * 22; coinSpray(P.x, P.y, 18); }
    text(P.x, P.y - 24, p.name + '!', col, 15); sfx('level');
    announceOnce('pact' + P.idx, .5, P.cls.name + ' takes the ' + p.name, col);
    G.fxs.push({ kind: 'shock', x: P.x, y: P.y, t: 0, r: 160, c1: '255,250,225', c2: '200,180,255' });
    burst(P.x, P.y, col, 30, 200, 1.4, 'spark');
    G.shake = Math.max(G.shake, .3);
  }
  else { const u = o.opts[i]; applyUp(o.P, u.id, u.m); }
  closeOffer();
}
/* ---------- the stall between depths ---------- */
const SHOP = [
  { id: 'draught', name: 'Healing Draught', desc: 'Restore half of your health.', col: '#d9534f', base: 28, per: 8, grow: 1.2 },
  { id: 'elixir', name: 'Hearth Elixir', desc: 'Restore all health and raise any fallen friend.', col: '#ff8a7a', base: 70, per: 14, grow: 1.25 },
  { id: 'vit', name: 'Vitality', desc: '+25 max health and heal that much.', col: '#d9534f', base: 60, per: 12, grow: 1.45, max: 6 },
  { id: 'power', name: 'Might', desc: '+20% damage.', col: '#f0a23c', base: 90, per: 18, grow: 1.5, max: 6 },
  { id: 'swift', name: 'Fleet Feet', desc: '+10% move speed.', col: '#8fd3ff', base: 70, per: 14, grow: 1.5, max: 6 },
  { id: 'haste', name: 'Quick Hands', desc: 'Attack 12% faster.', col: '#9bd16a', base: 80, per: 16, grow: 1.5, max: 6 },
  { id: 'ward', name: 'Iron Skin', desc: 'Take 8% less damage.', col: '#98a0b3', base: 80, per: 16, grow: 1.5, max: 6 },
  { id: 'dash', name: 'Light Step', desc: 'Dash recharges 20% faster.', col: '#8fd3ff', base: 55, per: 12, grow: 1.45, max: 4 },
  { id: 'crit', name: 'Keen Edge', desc: '+8% chance to strike critically for double damage.', col: '#ffd24a', base: 75, per: 15, grow: 1.5, max: 6 },
  { id: 'master', name: null, desc: null, col: null, base: 140, per: 25, grow: 1.6, max: 6 }
];
function shopInfo(P, it) {
  if (it.id === 'master') { const u = upInfo(P, 'master', 1); return { name: u.name, desc: u.desc, col: P.cls.col }; }
  return { name: it.name, desc: it.desc, col: it.col };
}
function shopBuys(P, id) { return (P.buys && P.buys[id]) || 0; }
function shopPrice(P, it) { return Math.round((it.base + it.per * G.level) * Math.pow(it.grow, shopBuys(P, it.id))); }
function shopState(P, it) {
  if (P.down) return 'down';
  if (it.id === 'master' ? P.mast >= 6 : it.max && shopBuys(P, it.id) >= it.max) return 'max';
  if ((it.id === 'draught' || it.id === 'elixir') && P.hp >= P.max - .5 && !(it.id === 'elixir' && G.players.some(p => p.down))) return 'full';
  return G.gold < shopPrice(P, it) ? 'poor' : 'ok';
}
function shopBuy(P, id) {
  const it = SHOP.find(s => s.id === id); if (!it || G.state !== 'shop' || shopState(P, it) !== 'ok') return false;
  G.gold -= shopPrice(P, it); P.buys = P.buys || {}; P.buys[id] = shopBuys(P, id) + 1;
  if (id === 'draught') P.hp = Math.min(P.max, P.hp + P.max * .5);
  else if (id === 'elixir') { P.hp = P.max; for (const D of G.players) if (D.down) { D.down = false; D.hp = D.max * .5; D.rev = 0; D.inv = 1; } }
  else applyUp(P, id, 1);
  return true;
}
const RAR_PRICE = { magic: 1, rare: 1.9, fabled: 3.4, cursed: .62 };
function warePrice(it) { return Math.round((70 + it.ilvl * 20) * (RAR_PRICE[it.rar] || 1)); }
function rollWares() {
  G.wares = [];
  const slots = ['weapon', 'armour', 'trinket'];
  for (let i = 0; i < 3; i++) {
    const it = rollItem(slots[i], rollRarity(G.level * .6));
    it.price = warePrice(it); it.sold = false;
    G.wares.push(it);
  }
}
function buyWare(P, i) {
  const it = G.wares[i];
  if (!it || it.sold || P.down || G.state !== 'shop' || G.gold < it.price) return false;
  G.gold -= it.price; it.sold = true;
  equip(P, it);
  return true;
}
function enterShop() {
  G.state = 'clear'; G.clearT = 0; G.clearE = 0; sfx('stairs'); rollWares();
  for (const P of G.players) { P.cheer = 1.5; P.swing = 0; }
  G.fxs.push({ kind: 'shock', x: G.exit.x, y: G.exit.y, t: 0, r: 170, c2: '240,162,60' });
  G.banner = { txt: 'Depth cleared', sub: 'The stall awaits', t: 1.8 };
}
function clearTick(dt) {
  G.clearT += dt; G.clearE -= dt; updateFx(dt);
  if (G.clearE <= 0) { G.clearE = .09; coinSpray(G.exit.x, G.exit.y, 2); const P = G.players[rint(0, G.players.length - 1)]; burst(P.x, P.y - 10, P.cls.col, 4, 110, 1, 'spark'); }
  for (const P of G.players) P.cheer = Math.max(0, (P.cheer || 0) - dt);
  if (G.clearT >= 1.5) G.state = 'shop';
}
function leaveShop() { if (G.state !== 'shop') return; nextLevel(); G.state = 'play'; }

/* ---------- updates ---------- */
function updatePlayer(P, I, dt) {
  if (P.down) return;
  const k = 60 * dt;
  let mx = I.mx, my = I.my; const len = Math.hypot(mx, my);
  if (len > 1) { mx /= len; my /= len; }
  if (len > .1) P.face = Math.atan2(my, mx);
  P.spCd -= dt; P.shield = Math.max(0, P.shield - dt); P.cast = Math.max(0, P.cast - dt); if (I.sp) special(P);
  P.aim = I.aim; P.cd -= dt; P.inv -= dt; P.dashCd -= dt; P.hurt = Math.max(0, P.hurt - dt);
  P.chill = Math.max(0, P.chill - dt);
  if (I.bomb) useBomb(P);
  /* the dungeon itself is draining you; food is the only clock that matters */
  const wasDrain = P.hp;
  P.hp -= drainRate(P) * dt; toll('deep', wasDrain, P);
  /* only once it has actually cost something, and only when nothing is
     hitting you, so the lesson is unmistakably about the drain */
  if (P.hp < P.max * .92 && clock - (P.lastHit || 0) > 3.5) teach('drain');
  const frac = P.hp / P.max;
  if (frac < .12) announceOnce('dying' + P.idx, 9, P.cls.name + ' is about to die!', '#d9534f');
  else if (frac < .34) announceOnce('food' + P.idx, 11, P.cls.name + ' needs food, badly!', '#ffd24a');
  if (P.hp <= 0) { downPlayer(P); return; }
  if (I.dash && P.dashCd <= 0 && len > .1) { P.dash = .16; P.dashCd = 1.3 * P.dashMul; P.dx = mx; P.dy = my; P.inv = Math.max(P.inv, .2); sfx('dash'); burst(P.x, P.y, P.cls.col, 8, 60); }
  let vx, vy;
  const chl = P.chill > 0 ? .62 : 1;
  if (P.dash > 0) { P.dash -= dt; vx = P.dx * (P.cls.spd * P.spdMul) * 3.3; vy = P.dy * (P.cls.spd * P.spdMul) * 3.3; if (Math.random() < .6) G.parts.push({ x: P.x, y: P.y, vx: 0, vy: 0, life: .25, max: .25, col: P.cls.col, s: 6 }); }
  else { vx = mx * (P.cls.spd * P.spdMul) * chl; vy = my * (P.cls.spd * P.spdMul) * chl; }
  const ox = P.x, oy = P.y; moveEnt(P, vx * k, vy * k);
  P.walk = (P.walk || 0) + Math.hypot(vx, vy) * k * .09; P.swing = Math.max(0, (P.swing || 0) - dt); P.drink = Math.max(0, (P.drink || 0) - dt); P.rise = Math.max(0, (P.rise || 0) - dt);
  for (const o of G.players) {
    if (o === P || o.down) continue;
    const far = Math.abs(o.x - P.x) > SEPX || Math.abs(o.y - P.y) > SEPY;
    if (far && Math.hypot(P.x - o.x, P.y - o.y) > Math.hypot(ox - o.x, oy - o.y)) { P.x = ox; P.y = oy; break; }
  }
  if (P.dash <= 0 && (vx || vy)) {
    for (const [ox, oy] of DIRS) {
      const tx = Math.floor((P.x + ox * (P.r + 3)) / T), ty = Math.floor((P.y + oy * (P.r + 3)) / T);
      if (tx >= 0 && ty >= 0 && tx < MW && ty < MH && G.map[ty * MW + tx] === 2) {
        if (G.keys > 0) { G.keys--; G.map[ty * MW + tx] = 0; G.mapVer++; sfx('door'); G.shake = .15; burst((tx + .5) * T, (ty + .5) * T, '#a8743d', 16, 100); text(P.x, P.y - 18, 'Unlocked', '#f0a23c'); }
        else if (!P.lockMsg || P.lockMsg < performance.now() - 1500) { P.lockMsg = performance.now(); teach('door'); text(P.x, P.y - 18, 'Locked. Find a key.', '#98a0b3'); }
      }
    }
  }
  if (I.fire) attack(P);
  arenaHold(P);
  // reveal map
  const px = Math.floor(P.x / T), py = Math.floor(P.y / T);
  for (let j = -8; j <= 8; j++) for (let i = -8; i <= 8; i++) {
    const x = px + i, y = py + j;
    if (x >= 0 && y >= 0 && x < MW && y < MH && i * i + j * j <= 62) G.seen[y * MW + x] = 1;
  }
}
function buildFlow() {
  const f = G.flow || (G.flow = new Int16Array(MW * MH)); f.fill(-1); const q = [];
  for (const P of G.players) {
    if (P.down) continue; const s = Math.floor(P.y / T) * MW + Math.floor(P.x / T);
    if (f[s] < 0) { f[s] = 0; q.push(s); }
  }
  for (let h = 0; h < q.length; h++) {
    const c = q[h], cx = c % MW, cy = (c / MW) | 0, d = f[c]; if (d > 70) continue;
    for (const [dx, dy] of DIRS) {
      const nx = cx + dx, ny = cy + dy; if (solid(nx, ny)) continue;
      const ni = ny * MW + nx; if (f[ni] >= 0) continue; f[ni] = d + 1; q.push(ni);
    }
  }
}
function bossAct(e) {
  const st = e.st; e.st = 'chase'; e.stt = 0; e.cd = e.ph >= 3 ? 1.1 : e.ph === 2 ? 1.6 : 2.4;
  if (st === 'charge') {
    G.fxs.push({ kind: 'shock', x: e.x, y: e.y, t: 0, r: 90, c1: '255,230,200', c2: '255,90,70' });
    G.shake = Math.max(G.shake, .3); sfx('boom'); burst(e.x, e.y, '#3a4152', 8, 100, 1.3, 'smoke'); burst(e.x, e.y, '#fff3d0', 8, 170, .7, 'spark');
    for (const p of G.players) if (!p.down && Math.hypot(p.x - e.x, p.y - e.y) < 90 + p.r) hurtPlayer(p, Math.round(e.dmg * .7), Math.atan2(p.y - e.y, p.x - e.x));
  } else if (st === 'slam') {
    const R = 120; G.fxs.push({ kind: 'shock', x: e.x, y: e.y, t: 0, r: R }); G.shake = Math.max(G.shake, .4); sfx('boom'); G.hitstop = Math.max(G.hitstop, .05);
    for (const p of G.players) if (!p.down && Math.hypot(p.x - e.x, p.y - e.y) < R + p.r) hurtPlayer(p, e.dmg, Math.atan2(p.y - e.y, p.x - e.x));
    burst(e.x, e.y, '#3a4152', 10, 120, 1.4, 'smoke'); burst(e.x, e.y, '#fff3d0', 12, 200, .7, 'spark');
  } else if (st === 'volley') {
    const n = e.ph >= 3 ? 5 : 3, a0 = e.face || 0;
    for (let i = 0; i < n; i++) {
      const a = a0 + (i - (n - 1) / 2) * .17;
      G.eshots.push({ x: e.x, y: e.y, vx: Math.cos(a) * 4.3, vy: Math.sin(a) * 4.3, life: 2.6, r: 6, dmg: Math.round(e.dmg * .62), own: e });
    }
    burstDir(e.x, e.y, a0, '#d8d2bd', 10, 200, .9, 'spark', .3); sfx('bone');
  } else if (st === 'blink') {
    burst(e.x, e.y, '#9a6bd6', 22, 150, 1.3, 'smoke');
    const alive2 = G.players.filter(p => !p.down), tgt = alive2.length ? alive2[rint(0, alive2.length - 1)] : null;
    if (tgt) {
      let landed = false;
      for (let k = 0; k < 40 && !landed; k++) {
        const a = rnd(0, TAU), d = rnd(80, 175), nx = tgt.x + Math.cos(a) * d, ny = tgt.y + Math.sin(a) * d;
        if (!blockedAt(nx, ny, e.r) && openAt(nx, ny)) { e.x = nx; e.y = ny; landed = true; }
      }
      /* nothing on the ring: walk the line in from the target and take what opens */
      if (!landed) {
        const base = Math.atan2(e.y - tgt.y, e.x - tgt.x);
        for (let s = 0; s < 12 && !landed; s++) {
          const a = base + (s % 2 ? 1 : -1) * Math.ceil(s / 2) * .5;
          for (let d = 170; d >= 60 && !landed; d -= 14) {
            const nx = tgt.x + Math.cos(a) * d, ny = tgt.y + Math.sin(a) * d;
            if (!blockedAt(nx, ny, e.r) && openAt(nx, ny)) { e.x = nx; e.y = ny; landed = true; }
          }
        }
      }
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
    for (let i = 0; i < 7; i++) scorch(e.x + rnd(-110, 110), e.y + rnd(-90, 90), rnd(10, 22), '#3a2a1e', 'crack');
    burst(e.x, e.y, '#3a4152', 16, 140, 1.5, 'smoke'); burst(e.x, e.y, '#d9b48a', 18, 190, 1, 'sq');
    for (const p of G.players) {
      if (p.down) continue; const d = Math.hypot(p.x - e.x, p.y - e.y);
      if (d >= R * 1.45) continue;
      const ang = Math.atan2(p.y - e.y, p.x - e.x);
      hurtPlayer(p, d < R ? dm : Math.round(dm * .6), ang, e);
      moveEnt(p, Math.cos(ang) * 14, Math.sin(ang) * 14);
    }
    for (const pr of G.props.slice()) if (Math.hypot(pr.x - e.x, pr.y - e.y) < R) hurtProp(pr, 60, Math.atan2(pr.y - e.y, pr.x - e.x));
  } else if (st === 'burst') {
    const n = e.ph === 2 ? 16 : 10, o = rnd(0, TAU);
    for (let i = 0; i < n; i++) { const a = o + i / n * TAU; G.eshots.push({ x: e.x, y: e.y, vx: Math.cos(a) * 2.6, vy: Math.sin(a) * 2.6, life: 2.4, r: 6, dmg: Math.round(e.dmg * .5), own: e }); }
    sfx('bone');
  } else if (st === 'pillars') {
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
  } else if (st === 'summon') {
    for (let i = 0; i < 3 && G.enemies.length < 38; i++) {
      const a = rnd(0, TAU), x = e.x + Math.cos(a) * 52, y = e.y + Math.sin(a) * 52;
      if (!blockedAt(x, y, 11) && openAt(x, y)) { spawnFoe('gloam', x, y, false); G.enemies[G.enemies.length - 1].alert = true; burst(x, y, '#9a6bd6', 8, 60); }
    }
  }
}
function updateEnemies(dt) {
  const k = 60 * dt, f = G.flow, alive = G.players.filter(p => !p.down);
  if (!alive.length) return;
  for (const e of G.enemies) {
    e.t += dt; e.flash = Math.max(0, e.flash - dt); e.cd -= dt; e.age += dt; e.fl = Math.max(0, e.fl - dt); e.atk = Math.max(-1, e.atk - dt);
    if (e.imp > 0) e.imp -= dt;
    if (e.mark > 0) {
      e.mark -= dt;
      if (Math.random() < .2) G.parts.push({ x: e.x + rnd(-8, 8), y: e.y - e.r - rnd(2, 10), vx: 0, vy: -.2, life: .4, max: .4, col: '#9bd16a', s: 1.6 });
    }
    if (e.chill > 0) {
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
      e.burn -= dt; e.burnT -= dt;
      if (Math.random() < .5) G.parts.push({ x: e.x + rnd(-7, 7), y: e.y + rnd(-9, 3), vx: rnd(-.15, .15), vy: -.5, life: .42, max: .42, col: Math.random() < .5 ? '#ffb347' : '#ff7a3a', s: 2, k: 'ember' });
      if (e.burnT <= 0) {
        e.burnT = .4; e.hp -= e.burnDmg; text(e.x + rnd(-7, 7), e.y - e.r - 2, String(Math.round(e.burnDmg)), '#ff9a4a', 11);
        if (e.hp <= 0) { finishFoe(e); continue; }
      }
    }
    let P = alive[0], bd = 1e9;
    for (const p of alive) { const dd = Math.hypot(p.x - e.x, p.y - e.y); if (dd < bd) { bd = dd; P = p; } }
    const dx = P.x - e.x, dy = P.y - e.y, d = Math.hypot(dx, dy) || 1;
    e.face = Math.atan2(dy, dx);
    const seen = d < 440 && los(e.x, e.y, P.x, P.y);
    if (seen || d < 140) e.alert = true;
    let tx = 0, ty = 0;
    if (e.alert) {
      let ax = dx / d, ay = dy / d;
      if (!seen) {
        const ex = Math.floor(e.x / T), ey = Math.floor(e.y / T); let best = f[ey * MW + ex], bx = null;
        if (best >= 0) for (const [ox, oy] of DIRS) {
          const nx = ex + ox, ny = ey + oy; if (nx < 0 || ny < 0 || nx >= MW || ny >= MH) continue;
          const v = f[ny * MW + nx]; if (v >= 0 && v < best) { best = v; bx = [nx, ny]; }
        }
        if (bx) { const cx = bx[0] * T + T / 2 - e.x, cy = bx[1] * T + T / 2 - e.y, cl = Math.hypot(cx, cy) || 1; ax = cx / cl; ay = cy / cl; }
      }
      if (e.type === 'wisp') { const w = Math.sin(e.t * 5) * .8; const nx = -ay, ny = ax; ax += nx * w; ay += ny * w; }
      if (e.type === 'bonewalker' && seen) {
        if (d < 170) { ax = -ax; ay = -ay; } else if (d < 260) { ax = 0; ay = 0; }
        if (e.cd <= 0 && d < 380) { e.cd = 2.2; const a = Math.atan2(dy, dx); G.eshots.push({ x: e.x, y: e.y, vx: Math.cos(a) * 3.2, vy: Math.sin(a) * 3.2, life: 2.6, r: 5, dmg: e.dmg, own: e }); sfx('bone'); }
      }
      tx = ax * e.spd; ty = ay * e.spd;
    }
    if (e.type === 'hound' && e.alert) {
      if (e.st === 'wind') { e.stt += dt; tx = 0; ty = 0; if (e.stt >= .45) { e.st = 'lunge'; e.stt = 0; e.la = e.face; sfx('dash'); } }
      else if (e.st === 'lunge') { e.stt += dt; e.face = e.la; tx = Math.cos(e.la) * e.spd * 4.6; ty = Math.sin(e.la) * e.spd * 4.6; if (e.stt >= .32) { e.st = 'chase'; e.cd = 1.6 + Math.random(); } }
      else if (e.cd <= 0 && seen && d < 250 && d > 60) { e.st = 'wind'; e.stt = 0; }
    }
    if (e.type === 'bloat' && e.alert) {
      if (e.fuse > 0) {
        e.fuse -= dt; tx = 0; ty = 0;
        if (Math.random() < .7) G.parts.push({ x: e.x + rnd(-9, 9), y: e.y + rnd(-11, 4), vx: 0, vy: -.6, life: .3, max: .3, col: '#d8f0a0', s: 2, k: 'ember' });
        if (e.fuse <= 0) { finishFoe(e); continue; }
      } else if (bd < 48 && seen) { e.fuse = .6; sfx('bone'); G.fxs.push({ kind: 'shock', x: e.x, y: e.y, t: .18, r: 62, c1: '234,255,196', c2: '143,191,90' }); }
    }
    if (e.boss && e.alert) {
      e.ph = e.hp < e.max * .26 ? 3 : e.hp < e.max * .5 ? 2 : 1;
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
    }
    for (const o of G.enemies) {
      if (o === e) continue; const ox = e.x - o.x, oy = e.y - o.y, od = Math.hypot(ox, oy);
      if (od > 0 && od < e.r + o.r) { tx += ox / od * .4; ty += oy / od * .4; }
    }
    if (e.type === 'thief') {
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
        const wasBite = p.hp;
        p.hp -= bite; toll('foes', wasBite, p);
        e.fed = (e.fed || 0) + bite; p.hurt = Math.max(p.hurt, .12);
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
    if (e.root > 0) { e.root -= dt; tx = 0; ty = 0; if (Math.random() < .15) G.parts.push({ x: e.x + rnd(-8, 8), y: e.y + rnd(-6, 8), vx: 0, vy: -.3, life: .5, max: .5, col: '#5fa03c', s: 2.5 }); }
    moveEnt(e, (tx + e.kx) * k, (ty + e.ky) * k); e.walk = (e.walk || 0) + Math.hypot(tx, ty) * k * .35; e.kx *= .85; e.ky *= .85;
    for (const p of alive) {
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
    }
  }
  G.enemies = G.enemies.filter(e => e.hp > 0);
}
function updateNests(dt) {
  const alive = G.players.filter(p => !p.down);
  if (alive.length) for (const n of G.nests) {
    if (n.hp > 0 && fogAt(n.x, n.y) < .4 &&
        alive.some(p => Math.hypot(p.x - n.x, p.y - n.y) < 260)) { teach('crypt'); break; }
  }
  for (const n of G.nests) {
    n.flash = Math.max(0, n.flash - dt); if (n.hp <= 0) continue; n.t -= dt;
    const d = alive.reduce((m, p) => Math.min(m, Math.hypot(p.x - n.x, p.y - n.y)), 1e9);
    if (n.t <= 0 && d < 520 && G.enemies.length < 38) {
      n.t = rnd(2.4, 3.6) / (1 + .05 * G.level);
      for (let i = 0; i < 8; i++) {
        const a = rnd(0, TAU), x = n.x + Math.cos(a) * 30, y = n.y + Math.sin(a) * 30;
        if (!blockedAt(x, y, 11) && openAt(x, y)) { spawnFoe(pickFoe(), x, y); burst(x, y, '#c2563f', 6, 60); break; }
      }
    }
  }
  G.nests = G.nests.filter(n => n.hp > 0);
}
function updateShots(dt) {
  const k = 60 * dt;
  for (let i = G.shots.length - 1; i >= 0; i--) {
    const s = G.shots[i];
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
    s.x += s.vx * k; s.y += s.vy * k; s.life -= dt; if (s.trail) { s.trail.push({ x: s.x, y: s.y }); if (s.trail.length > 16) s.trail.shift(); } let dead = s.life <= 0;
    if (s.kind === 'fire' && Math.random() < .7) G.parts.push({ x: s.x, y: s.y, vx: rnd(-.3, .3), vy: rnd(-.3, .3), life: .3, max: .3, col: '#f0a23c', s: 3 });
    if (s.kind === 'fire' && Math.random() < .35) G.parts.push({ x: s.x, y: s.y, vx: rnd(-.2, .2), vy: -.4, life: .5, max: .5, col: '#ffb347', s: 1, k: 'ember' });
    else if (s.kind === 'arrow' && Math.random() < .45) G.parts.push({ x: s.x, y: s.y, vx: rnd(-.3, .3), vy: rnd(-.3, .3), life: .35, max: .35, col: '#bfe88a', s: 1.6 });
    else if (s.kind === 'dagger' && Math.random() < .3) G.parts.push({ x: s.x, y: s.y, vx: rnd(-.2, .2), vy: rnd(-.2, .2), life: .25, max: .25, col: '#9fe6dc', s: 1.5 });
    if (!dead && blockedAt(s.x, s.y, 2)) { dead = true; if (s.kind === 'fire') explode(s); else burst(s.x, s.y, s.col, 4, 40); }
    if (!dead) for (const e of G.enemies) {
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
    }
    if (!dead) for (const n of G.nests) {
      if (n.hp > 0 && Math.hypot(n.x - s.x, n.y - s.y) < n.r + s.r) { hurtNest(n, s.dmg); if (s.kind === 'fire') explode(s); dead = true; break; }
    }
    if (!dead) for (const p of G.props.slice()) {
      if (s.hit.has(p) || Math.hypot(p.x - s.x, p.y - s.y) > Math.max(p.sr, 9) + s.r) continue;
      s.hit.add(p); hurtProp(p, s.dmg, Math.atan2(s.vy, s.vx));
      if (s.kind === 'fire') { explode(s); dead = true; break; }
      if (s.pierce-- <= 0) { dead = true; break; }
    }
    for (let fi = G.items.length - 1; fi >= 0; fi--) {
      const it = G.items[fi];
      if (it.kind !== 'food' || Math.hypot(it.x - s.x, it.y - s.y) > 13 + s.r) continue;
      G.items.splice(fi, 1);
      burst(it.x, it.y, '#d9534f', 16, 140, 1); burst(it.x, it.y, '#9bd16a', 7, 100, .8, 'spark');
      announceOnce('shotfood', 2.2, (s.own ? s.own.cls.name : 'Someone') + ' shot the food!', '#d9534f');
      sfx('hurt'); break;
    }
    if (dead) G.shots.splice(i, 1);
  }
  for (let i = G.eshots.length - 1; i >= 0; i--) {
    const s = G.eshots[i];
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
    s.x += s.vx * k; s.y += s.vy * k; s.life -= dt;
    let dead = s.life <= 0 || blockedAt(s.x, s.y, 2);
    if (!dead) for (const P of G.players) if (!P.down && Math.hypot(P.x - s.x, P.y - s.y) < P.r + s.r) { hurtPlayer(P, s.dmg, Math.atan2(s.vy, s.vx) + Math.PI, s.own); dead = true; break; }
    if (dead) G.eshots.splice(i, 1);
  }
}
function updateItems(dt) {
  const alive = G.players.filter(p => !p.down); if (!alive.length) return;
  for (let i = G.items.length - 1; i >= 0; i--) {
    const it = G.items[i]; it.t += dt;
    let P = alive[0], d = 1e9;
    for (const p of alive) { const dd = Math.hypot(p.x - it.x, p.y - it.y); if (dd < d) { d = dd; P = p; } }
    if (it.kind === 'chest') { if (d < 26) { G.items.splice(i, 1); openChest(P, it); return; } continue; }
    if (it.kind === 'shrine') {
      /* refusing leaves the font standing, so brushing past one costs nothing */
      it.cool = Math.max(0, (it.cool || 0) - dt);
      if (d < 30 && it.cool <= 0 && !G.offer && !G.offerQ.length) { queueOffer({ kind: 'pact', P, shrine: it }); return; }
      continue;
    }
    if (it.kind === 'gear') {
      if (d < 21) {
        G.items.splice(i, 1);
        const cur = P.gear[it.item.slot];
        if (!cur) equip(P, it.item);
        else queueOffer({ kind: 'gear', P, item: it.item, cur });
        return;
      }
      continue;
    }
    const dx = P.x - it.x, dy = P.y - it.y;
    if (it.kind === 'gold' && d < 80 && d > 1) { it.x += dx / d * 2.6; it.y += dy / d * 2.6; if (Math.random() < .5) G.parts.push({ x: it.x, y: it.y, vx: 0, vy: 0, life: .2, max: .2, col: '#f0a23c', s: 2.2 }); }
    if (d < 18) {
      const gmul = 1 + (P.g ? P.g.gold : 0) + (P.perkGold || 0);
      if (it.kind === 'gold') { const v = Math.round((it.v || 10) * gmul); G.gold += v; G.score += v; text(P.x, P.y - 16, '+' + v, '#f0a23c'); sfx('coin'); burst(P.x, P.y - 6, '#ffe08a', 4, 90, .5, 'spark'); }
      else if (it.kind === 'gem') { const v = Math.round(50 * gmul); G.gold += v; G.score += 60; text(P.x, P.y - 16, '+' + v, '#8fd3ff'); sfx('coin'); burst(P.x, P.y - 6, '#8fd3ff', 10, 120, .7, 'spark'); }
      else if (it.kind === 'key') { G.keys++; text(P.x, P.y - 16, 'Key', '#f0a23c'); sfx('door'); announceOnce('key', 4, 'A key is found', '#f0a23c'); }
      else if (it.kind === 'bomb') { G.bombs++; text(P.x, P.y - 16, 'Potion', '#b98cff'); sfx('coin'); burst(P.x, P.y, '#b98cff', 14, 110, 1, 'spark'); }
      else if (it.kind === 'food') { if (P.hp >= P.max - .5) continue; const h = 36 + G.level * 3; P.hp = Math.min(P.max, P.hp + h); text(P.x, P.y - 16, '+' + h + ' HP', '#9bd16a'); sfx('coin'); P.drink = .75; burst(P.x, P.y, '#9bd16a', 12, 70, 1.3, 'ember'); }
      G.items.splice(i, 1);
    }
  }
}
/* a slow drift of whatever this zone is made of, seeded around the camera */
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
  zoneMotes(dt);
  if (G.comboT > 0) { G.comboT -= dt; if (G.comboT <= 0) G.combo = 0; }
  for (const p of G.props) { if (p.fl > 0) p.fl -= dt; if (p.wob > 0) p.wob -= dt; }
  for (const d of G.dying) d.t += dt; G.dying = G.dying.filter(d => d.t < .5);
  for (const f of G.fxs) f.t += dt; G.fxs = G.fxs.filter(f => f.t < (f.dur || .8));
  for (let i = G.parts.length - 1; i >= 0; i--) { const p = G.parts[i]; p.x += p.vx * k; p.y += p.vy * k; p.vx *= .94; p.vy *= .94; if (p.k === 'ember') p.vy -= .02 * k; else if (p.k === 'drip') p.vy += .06 * k; else if (p.k === 'coin') { p.vx *= .985 / .94; p.vy *= .985 / .94; p.z += p.vz * k; p.vz -= .36 * k; if (p.z < 0) { p.z = 0; p.vz = -p.vz * .45; if (p.vz < .7) p.vz = 0; } } p.life -= dt; if (p.life <= 0) G.parts.splice(i, 1); }
  const cap = Math.round((reduceMotion ? 450 : 1400) * fxThin());
  if (G.parts.length > cap) G.parts.splice(0, G.parts.length - cap);
  for (let i = G.texts.length - 1; i >= 0; i--) { const t = G.texts[i]; t.y -= 24 * dt; t.life -= dt; if (t.life <= 0) G.texts.splice(i, 1); }
  for (let i = G.timers.length - 1; i >= 0; i--) { const q = G.timers[i]; q.t -= dt; if (q.t <= 0) { G.timers.splice(i, 1); try { q.fn(); } catch (e) {} } }
  for (const b of G.bolts) b.t += dt; if (G.bolts.length) G.bolts = G.bolts.filter(b => b.t < .22);
  if (G.flash > 0) G.flash = Math.max(0, G.flash - dt * 1.9);
  if (G.voice) { G.voice.t -= dt; if (G.voice.t <= 0) G.voice = null; }
  for (const P of G.players) if (P.bombCd > 0) P.bombCd -= dt;
  if (G.slash) { G.slash.life -= dt; if (G.slash.life <= 0) G.slash = null; }
  if (G.banner) { G.banner.t -= dt; if (G.banner.t <= 0) G.banner = null; }
  G.shake = Math.max(0, G.shake - dt);
}
function update(dt) {
  if (G.winPending && G.state === 'play') { G.winPending = false; G.state = 'won'; return; }
  if (G.state !== 'play') return;
  G.runT = (G.runT || 0) + dt;
  if (G.hitstop > 0) { G.hitstop -= dt; updateFx(dt * .3); return; }
  G.flowT -= dt; if (G.flowT <= 0) { buildFlow(); G.flowT = .3; }
  G.players.forEach((P, i) => updatePlayer(P, INS[i], dt));
  if (G.state !== 'play') return;
  if (!G.event) {
    for (const P of G.players) {
      if (P.down) continue;
      const tx = Math.floor(P.x / T), ty = Math.floor(P.y / T);
      const r = G.rooms.find(r2 => r2.arena && !r2.eventDone && tx > r2.x && tx < r2.x + r2.w - 1 && ty > r2.y && ty < r2.y + r2.h - 1);
      if (r) { startArena(r); break; }
    }
  } else arenaTick(dt);
  updateRevive(dt); updateEnemies(dt); updateNests(dt); updateShots(dt); updateItems(dt); updateHazards(dt); updateZones(dt); updateFx(dt);
  const alive = G.players.filter(p => !p.down), onExit = alive.filter(p => Math.hypot(p.x - G.exit.x, p.y - G.exit.y) < G.exit.r + p.r + 10);
  if (alive.length && onExit.length === alive.length) enterShop();
  else if (onExit.length && (G.exitMsg = (G.exitMsg || 0) - dt) < 0) { G.exitMsg = 1.5; text(G.exit.x, G.exit.y - 30, 'Wait for your partner', '#8fd3ff'); }
}
'use strict';
/* Hollowdeep: procedural art. Everything is drawn in code; nothing is copied from any other game. */
const _mc = {};
function mix(hex, t) {
  const key = hex + t; if (_mc[key]) return _mc[key];
  if (hex.length === 4) hex = '#' + hex[1] + hex[1] + hex[2] + hex[2] + hex[3] + hex[3];
  const n = parseInt(hex.slice(1), 16), f = t < 0 ? 0 : 255, a = Math.abs(t), q = v => Math.round(v + (f - v) * a);
  return (_mc[key] = 'rgb(' + q(n >> 16) + ',' + q((n >> 8) & 255) + ',' + q(n & 255) + ')');
}
const hash = (x, y, s) => { let h = (x * 374761393 + y * 668265263 + (s || 0) * 2147483647) >>> 0; h = ((h ^ (h >> 13)) * 1274126177) >>> 0; return (h ^ (h >> 16)) >>> 0; };
const hr = (x, y, s) => hash(x, y, s) / 4294967296;
/* An entity's shadow leaning away from the nearest flame does more for depth
   than any amount of extra detail on the sprite. */
function shadowL(x, y, rx, ry, a, LT) {
  if (!LT) return shadow(x, y, rx, ry, a);
  const o = 3 + LT.a * 6;
  shadow(x - LT.dx * o, y - LT.dy * o * .45, rx * (1 + LT.a * .12), ry, a);
}
function shadow(x, y, rx, ry, a) {
  rx = Math.max(.5, rx || 0); ry = Math.max(.25, ry || 0);
  a = a || .35; ctx.save(); ctx.translate(x, y); ctx.scale(1, ry / rx);
  const g = ctx.createRadialGradient(0, 0, 0, 0, 0, rx); g.addColorStop(0, 'rgba(0,0,0,' + a + ')'); g.addColorStop(.65, 'rgba(0,0,0,' + a * .6 + ')'); g.addColorStop(1, 'rgba(0,0,0,0)');
  ctx.fillStyle = g; ctx.beginPath(); ctx.arc(0, 0, rx, 0, TAU); ctx.fill(); ctx.restore();
}

/* ---------- baked map (floors, walls, doors) ---------- */
let baked = null, bakedVer = -1, bakedBS = 0;
const wallAt = (tx, ty) => tx < 0 || ty < 0 || tx >= MW || ty >= MH || G.map[ty * MW + tx] === 1;
function bakeDoor(b, px, py) {
  /* only the frame is baked now: drawDoor puts the gate itself on top, lit */
  b.fillStyle = '#241a12'; b.fillRect(px, py, T, T);
  b.fillStyle = '#3a2a1c'; b.fillRect(px + 1, py + 1, T - 2, T - 2);
  if (sprOk('props')) return;
  b.fillStyle = '#6e4626'; b.fillRect(px + 2, py + 1, T - 4, T - 2);
  for (let i = 0; i < 4; i++) { b.fillStyle = i % 2 ? '#7a4e2a' : '#69421f'; b.fillRect(px + 3 + i * 7, py + 2, 6, T - 4); b.fillStyle = 'rgba(0,0,0,.25)'; b.fillRect(px + 8 + i * 7, py + 2, 1, T - 4); }
  b.fillStyle = '#3a3f4f'; b.fillRect(px + 2, py + 6, T - 4, 3); b.fillRect(px + 2, py + T - 10, T - 4, 3);
  b.fillStyle = '#f0a23c'; b.beginPath(); b.arc(px + T / 2, py + T / 2, 5, 0, TAU); b.fill();
  b.fillStyle = '#3b2b12'; b.beginPath(); b.arc(px + T / 2, py + T / 2 - 1.5, 1.5, 0, TAU); b.fill(); b.fillRect(px + T / 2 - 1, py + T / 2 - 1, 2, 4);
}
function bakeWall(b, tx, ty, px, py) {
  let near = false;
  for (let j = -1; j <= 1 && !near; j++) for (let i = -1; i <= 1; i++) { const x = tx + i, y = ty + j; if (x >= 0 && y >= 0 && x < MW && y < MH && G.map[y * MW + x] !== 1) { near = true; break; } }
  if (!near) { b.fillStyle = '#0a0c11'; b.fillRect(px, py, T, T); return; }
  const faceH = (ty + 1 < MH && G.map[(ty + 1) * MW + tx] !== 1) ? 11 : 0, topH = T - faceH;
  const wt = wallTex(tx, ty);
  if (wt) wallFill(b, wt, tx, ty, px, py); else for (let row = 0; row < 3; row++) {
    const y0 = py + row * (topH / 3), h = topH / 3, off = (row + tx + ty) % 2 ? 0 : 8;
    for (let k = -1; k < 3; k++) {
      const bx = px + off + k * 16, r = hr(tx * 7 + k, ty * 5 + row, 5);
      b.fillStyle = 'rgb(' + ((40 + r * 12) | 0) + ',' + ((48 + r * 12) | 0) + ',' + ((66 + r * 14) | 0) + ')';
      const x0 = Math.max(bx, px), x1 = Math.min(bx + 16, px + T); if (x1 > x0) b.fillRect(x0, y0, x1 - x0 - 1, h - 1);
    }
  }
  if (!wallAt(tx, ty - 1)) { b.fillStyle = '#4a5775'; b.fillRect(px, py, T, 2); }
  if (!wallAt(tx - 1, ty)) { b.fillStyle = 'rgba(255,255,255,.08)'; b.fillRect(px, py, 1, topH); }
  if (!wallAt(tx + 1, ty)) { b.fillStyle = 'rgba(0,0,0,.3)'; b.fillRect(px + T - 2, py, 2, topH); }
  if (faceH) {
    if (wt) { const iw = wt.img.width / 3, ih = wt.img.height / 3; b.drawImage(wt.img, (tx % 3) * iw, (ty % 3) * ih + (T - faceH) / T * ih, iw, faceH / T * ih, px, py + topH, T, faceH); b.fillStyle = 'rgba(6,9,18,.6)'; } else b.fillStyle = '#141824';
    b.fillRect(px, py + topH, T, faceH);
    b.fillStyle = 'rgba(255,255,255,.07)'; b.fillRect(px, py + topH, T, 1);
    b.fillStyle = '#0d1018'; for (let k = 0; k < 2; k++) b.fillRect(px + 4 + k * 16 + ((hr(tx, ty, 8) * 6) | 0), py + topH + 3, 10, 1);
    b.fillStyle = 'rgba(0,0,0,.35)'; b.fillRect(px, py + T - 3, T, 3);
  }
}
function bakeDecor(b, tx, ty) {
  const t = G.map[ty * MW + tx], px = tx * T, py = ty * T, Zn = G.zone || ZONES[0], zn = Zn.dec != null ? Zn.dec : Zn.id;
  if (Zn.tint) { b.fillStyle = Zn.tint; b.fillRect(px, py, T, T); }
  if (t === 1) {
    if (!wallAt(tx, ty + 1)) {
      if (zn === 2 && hr(tx, ty, 71) < .45) { b.strokeStyle = 'rgba(86,150,60,.7)'; b.lineWidth = 1.6; for (let i = 0; i < 3; i++) { const vx = px + 4 + hr(tx, ty, 72 + i) * 24, len = 6 + hr(tx, ty, 75 + i) * 14, y0 = py + T - 14; b.beginPath(); b.moveTo(vx, y0); b.quadraticCurveTo(vx + 2, y0 + len * .5, vx - 1, y0 + len); b.stroke(); } }
      if (zn === 1 && hr(tx, ty, 81) < .35) { b.fillStyle = 'rgba(90,190,230,.35)'; b.fillRect(px + 6 + hr(tx, ty, 82) * 16, py + T - 12, 2, 8 + hr(tx, ty, 83) * 10); }
      if (zn === 3 && hr(tx, ty, 84) < .25) { b.fillStyle = 'rgba(255,120,50,.55)'; b.fillRect(px + 5 + hr(tx, ty, 85) * 20, py + T - 10, 6, 1.5); }
      if (zn === 5 && hr(tx, ty, 86) < .3) { b.fillStyle = 'rgba(185,140,255,.5)'; for (let i = 0; i < 2; i++) { const gx = px + 7 + hr(tx, ty, 87 + i) * 18, gy = py + T - 13; b.beginPath(); b.moveTo(gx - 2, gy); b.lineTo(gx, gy + 7 + hr(tx, ty, 89 + i) * 5); b.lineTo(gx + 2, gy); b.fill(); } }
    }
    return;
  }
  if (t !== 0) return;
  const r5 = hr(tx, ty, 90), r6 = hr(tx, ty, 91), cx = px + 6 + hr(tx, ty, 92) * 20, cy = py + 8 + hr(tx, ty, 93) * 18;
  if (zn === 1 && r5 < .13) {
    b.fillStyle = 'rgba(48,130,170,.38)'; b.beginPath(); b.ellipse(cx, cy, 8 + r6 * 10, 4 + r6 * 5, 0, 0, TAU); b.fill();
    b.strokeStyle = 'rgba(190,235,255,.28)'; b.lineWidth = 1; b.beginPath(); b.ellipse(cx, cy, 6 + r6 * 8, 3 + r6 * 4, 0, 3.6, 5.6); b.stroke();
  } else if (zn === 2 && r5 < .2) {
    b.fillStyle = 'rgba(78,140,52,.32)';
    for (let i = 0; i < 4; i++) { b.beginPath(); b.arc(cx + (hr(tx, ty, 94 + i) - .5) * 14, cy + (hr(tx, ty, 98 + i) - .5) * 10, 3 + hr(tx, ty, 102 + i) * 5, 0, TAU); b.fill(); }
    if (r6 < .3) { b.fillStyle = '#e8d9a8'; b.fillRect(cx + 3, cy - 2, 1.6, 5); b.fillStyle = '#c4553f'; b.beginPath(); b.ellipse(cx + 3.8, cy - 2.5, 3.2, 2, 0, 0, TAU); b.fill(); }
  } else if (zn === 3 && r5 < .17) {
    let x = cx - 8, y = cy - 6; const pts = [[x, y]];
    for (let i = 0; i < 4; i++) { x += 4 + hr(tx, ty, 110 + i) * 5; y += (hr(tx, ty, 114 + i) - .4) * 8; pts.push([x, y]); }
    for (const [w, col] of [[4, 'rgba(255,110,40,.22)'], [1.4, '#ff8a3a']]) { b.strokeStyle = col; b.lineWidth = w; b.beginPath(); pts.forEach((p, i) => i ? b.lineTo(p[0], p[1]) : b.moveTo(p[0], p[1])); b.stroke(); }
  } else if (zn === 4 && r5 < .22) {
    b.fillStyle = 'rgba(226,218,190,.38)';
    for (let i = 0; i < 3; i++) { const sx2 = cx + (hr(tx, ty, 130 + i) - .5) * 17, sy2 = cy + (hr(tx, ty, 134 + i) - .5) * 12; b.fillRect(sx2, sy2, 5 + hr(tx, ty, 138 + i) * 6, 1.7); }
    if (r6 < .4) { b.beginPath(); b.arc(cx + 4, cy + 3, 2.6, 0, TAU); b.fill(); b.fillStyle = '#12151c'; b.fillRect(cx + 2.8, cy + 2.2, 1.1, 1.4); b.fillRect(cx + 4.8, cy + 2.2, 1.1, 1.4); }
  } else if (zn === 5 && r5 < .2) {
    for (let i = 0; i < 3; i++) {
      const gx = cx + (hr(tx, ty, 140 + i) - .5) * 15, gy = cy + (hr(tx, ty, 144 + i) - .5) * 11, gh = 4 + hr(tx, ty, 148 + i) * 7;
      b.fillStyle = 'rgba(150,110,220,.42)'; b.beginPath(); b.moveTo(gx - 2.3, gy + 1); b.lineTo(gx, gy - gh); b.lineTo(gx + 2.3, gy + 1); b.fill();
      b.fillStyle = 'rgba(214,190,255,.5)'; b.beginPath(); b.moveTo(gx - .7, gy + 1); b.lineTo(gx, gy - gh); b.lineTo(gx + .8, gy + 1); b.fill();
    }
  }
  if (r6 > .978) {
    b.fillStyle = '#cfc8b2'; b.fillRect(cx - 7, cy + 2, 9, 1.8); b.fillRect(cx - 3, cy - 2, 1.8, 7); b.fillRect(cx + 2, cy + 4, 7, 1.6);
    b.beginPath(); b.arc(cx + 4, cy - 1, 3.4, 0, TAU); b.fill(); b.fillStyle = '#12151c'; b.fillRect(cx + 2.4, cy - 2, 1.2, 1.6); b.fillRect(cx + 4.6, cy - 2, 1.2, 1.6);
  } else if (r6 < .022) {
    for (let i = 0; i < 4; i++) { b.fillStyle = i % 2 ? '#3a4152' : '#2f3647'; b.beginPath(); b.moveTo(cx + i * 4 - 6, cy + 3); b.lineTo(cx + i * 4 - 4, cy - 2 - i % 2 * 2); b.lineTo(cx + i * 4 - 1, cy + 3); b.fill(); }
  }
  if (wallAt(tx, ty - 1) && wallAt(tx - 1, ty) && hr(tx, ty, 120) < .7) {
    b.strokeStyle = 'rgba(220,225,235,.22)'; b.lineWidth = 1; b.beginPath();
    for (let i = 1; i <= 3; i++) { b.moveTo(px, py); b.lineTo(px + 16, py + i * 5); b.moveTo(px, py); b.lineTo(px + i * 5, py + 16); }
    b.moveTo(px + 6, py + 2); b.quadraticCurveTo(px + 6, py + 6, px + 2, py + 6); b.moveTo(px + 11, py + 3); b.quadraticCurveTo(px + 11, py + 11, px + 3, py + 11); b.stroke();
  }
}
function bakeTile(b, tx, ty) { bakeTile0(b, tx, ty); bakeDecor(b, tx, ty); }
const FGRADE = ['#a4aecb', '#8fc0d2', '#adc48e', '#d49c80', '#cfc7a8', '#a99ad0'], WGRADE = ['#7d88a8', '#6898b2', '#88a068', '#b07a60', '#a89f84', '#8276b0'];
function floorTex(tx, ty) { const h = hr(tx >> 2, ty >> 2, 33), k = h < .5 ? 'fl_std' : h < .72 ? 'fl_sq' : h < .9 ? 'fl_big' : 'fl_dia'; return texOk(k) ? TEXI[k] : null; }
function gradeTex(b, px, py, col, dark) { b.globalCompositeOperation = 'multiply'; b.fillStyle = col; b.fillRect(px, py, T, T); b.globalCompositeOperation = 'source-over'; b.fillStyle = 'rgba(8,12,24,' + dark + ')'; b.fillRect(px, py, T, T); }
function wallTex(tx, ty) { const h = hr((tx / 3) | 0, (ty / 3) | 0, 44), k = h < .78 ? 'wl_std' : 'wl_brk'; return texOk(k) ? TEXI[k] : null; }
function wallFill(b, t, tx, ty, px, py) { const im = t.img, w = im.width / 3, h = im.height / 3; b.drawImage(im, (tx % 3) * w, (ty % 3) * h, w, h, px, py, T, T); gradeTex(b, px, py, WGRADE[(G.zone || ZONES[0]).id], .7); }
function bakeTile0(b, tx, ty) {
  const t = G.map[ty * MW + tx], px = tx * T, py = ty * T;
  if (t === 1) return bakeWall(b, tx, ty, px, py);
  const r1 = hr(tx, ty, 1), r2 = hr(tx, ty, 2), r3 = hr(tx, ty, 3), r4 = hr(tx, ty, 4);
  const fv = floorTex(tx, ty);
  if (fv) { b.drawImage(fv.img, (tx & 3) * 64, (ty & 3) * 64, 64, 64, px, py, T, T); gradeTex(b, px, py, FGRADE[(G.zone || ZONES[0]).id], .3); }
  else {
    b.fillStyle = ['#1b2030', '#1d2333', '#1a1f2e', '#1f2536'][(r1 * 4) | 0]; b.fillRect(px, py, T, T);
    b.fillStyle = 'rgba(0,0,0,.35)'; b.fillRect(px + T - 1, py, 1, T); b.fillRect(px, py + T - 1, T, 1);
    b.fillStyle = 'rgba(255,255,255,.045)'; b.fillRect(px, py, T - 1, 1); b.fillRect(px, py, 1, T - 1);
  }
  if (!fv && r2 < .4) { const sx = px + 8 + ((r3 * 16) | 0); b.fillStyle = 'rgba(0,0,0,.28)'; b.fillRect(sx, py, 1, T); b.fillStyle = 'rgba(255,255,255,.03)'; b.fillRect(sx + 1, py, 1, T); }
  if (r4 < .14) {
    b.strokeStyle = 'rgba(0,0,0,.4)'; b.lineWidth = 1; b.beginPath(); let cx = px + 4 + r1 * 24, cy = py + 2; b.moveTo(cx, cy);
    for (let i = 0; i < 4; i++) { cx += (hr(tx, ty, 10 + i) - .5) * 12; cy += 7; b.lineTo(cx, cy); } b.stroke();
  }
  if (r3 > .93) { b.fillStyle = 'rgba(70,115,62,.2)'; for (let i = 0; i < 3; i++) { b.beginPath(); b.arc(px + hr(tx, ty, 20 + i) * T, py + hr(tx, ty, 30 + i) * T, 3 + hr(tx, ty, 40 + i) * 5, 0, TAU); b.fill(); } }
  if (r1 > .94) { b.fillStyle = 'rgba(130,138,160,.25)'; for (let i = 0; i < 3; i++) b.fillRect(px + 4 + hr(tx, ty, 50 + i) * 22, py + 4 + hr(tx, ty, 60 + i) * 22, 3, 2); }
  if (wallAt(tx, ty - 1)) {
    b.fillStyle = 'rgba(0,0,0,.42)'; b.fillRect(px, py, T, 6);
    b.fillStyle = 'rgba(0,0,0,.24)'; b.fillRect(px, py + 6, T, 6);
    b.fillStyle = 'rgba(0,0,0,.11)'; b.fillRect(px, py + 12, T, 6);
  }
  if (wallAt(tx - 1, ty)) { b.fillStyle = 'rgba(0,0,0,.22)'; b.fillRect(px, py, 5, T); }
  if (t === 2) bakeDoor(b, px, py);
}
function drawTiles() {
  const bs = DPR * Z > 1.25 ? 2 : 1;
  if (!baked || bakedVer !== G.mapVer || bakedBS !== bs) {
    if (!baked) baked = document.createElement('canvas');
    baked.width = MW * T * bs; baked.height = MH * T * bs;
    const b = baked.getContext('2d'); b.setTransform(bs, 0, 0, bs, 0, 0);
    for (let ty = 0; ty < MH; ty++) for (let tx = 0; tx < MW; tx++) bakeTile(b, tx, ty);
    bakedVer = G.mapVer; bakedBS = bs;
  }
  const sx = Math.max(0, cam.x), sy = Math.max(0, cam.y), sw = Math.min(MW * T - sx, W / Z + 2), sh = Math.min(MH * T - sy, H / Z + 2);
  if (sw > 0 && sh > 0) ctx.drawImage(baked, sx * bs, sy * bs, sw * bs, sh * bs, sx, sy, sw, sh);
}
function drawArena() {
  const E = G.event; if (!E) return;
  const r = E.room, x0 = r.x * T, y0 = r.y * T, w = r.w * T, h = r.h * T, pu = .5 + .5 * Math.sin(clock * 4);
  ctx.save();
  ctx.strokeStyle = 'rgba(255,170,100,' + (.08 + pu * .07) + ')'; ctx.lineWidth = 12; ctx.strokeRect(x0, y0, w, h);
  ctx.strokeStyle = 'rgba(255,138,58,' + (.4 + pu * .3) + ')'; ctx.lineWidth = 2.5;
  ctx.setLineDash([16, 11]); ctx.lineDashOffset = -clock * 30; ctx.strokeRect(x0, y0, w, h);
  ctx.setLineDash([]); ctx.restore();
}
function drawDecals() {
  for (const d of G.decals) {
    ctx.save(); ctx.translate(d.x, d.y); ctx.rotate(d.rot); ctx.globalAlpha = .3;
    if (d.k === 'scorch') {
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
    } else if (d.k === 'bonewalker') { ctx.fillStyle = '#cfc8b2'; for (let i = 0; i < 5; i++) ctx.fillRect(-9 + i * 4, ((i * 7) % 5) - 3, 3, 1.6); }
    else { ctx.fillStyle = mix(d.col, -.5); ctx.beginPath(); ctx.ellipse(0, 0, d.r, d.r * .65, 0, 0, TAU); ctx.fill(); ctx.beginPath(); ctx.arc(d.r * .9, 2, 2.4, 0, TAU); ctx.arc(-d.r * .7, -d.r * .5, 1.8, 0, TAU); ctx.fill(); }
    ctx.restore();
  }
  ctx.globalAlpha = 1;
}

/* ---------- props ---------- */
function drawTorch(t) {
  const f = Math.sin(clock * 9 + t.ph), g = Math.sin(clock * 13 + t.ph * 2);
  glow(t.x, t.y + 6, 80 + f * 6, '#f0a23c', .22);
  ctx.fillStyle = '#2b2118'; ctx.fillRect(t.x - 3, t.y + 1, 6, 10); ctx.fillStyle = '#4a3a28'; ctx.fillRect(t.x - 4, t.y - 1, 8, 3);
  ctx.fillStyle = '#d9731f'; ctx.beginPath(); ctx.moveTo(t.x - 4, t.y - 1); ctx.quadraticCurveTo(t.x - 5 + g, t.y - 9, t.x + g * 1.5, t.y - 14 - f * 2); ctx.quadraticCurveTo(t.x + 5, t.y - 8, t.x + 4, t.y - 1); ctx.fill();
  ctx.fillStyle = '#ffc45a'; ctx.beginPath(); ctx.moveTo(t.x - 2, t.y - 1); ctx.quadraticCurveTo(t.x - 3, t.y - 6, t.x + g * .8, t.y - 10); ctx.quadraticCurveTo(t.x + 3, t.y - 6, t.x + 2, t.y - 1); ctx.fill();
  ctx.fillStyle = '#fff1b8'; ctx.beginPath(); ctx.ellipse(t.x, t.y - 3, 1.4, 3, 0, 0, TAU); ctx.fill();
}
function drawExitOld() {
  const e = G.exit, p = (Math.sin(clock * 3) + 1) / 2;
  glow(e.x, e.y, 70, C.cyan, .3 + p * .15);
  ctx.save(); ctx.translate(e.x, e.y);
  for (let i = 0; i < 6; i++) { const s = 1 - i * .13; ctx.fillStyle = i % 2 ? '#1c2233' : '#252d42'; ctx.beginPath(); ctx.ellipse(0, i * 1.2, 22 * s, 17 * s, 0, 0, TAU); ctx.fill(); }
  ctx.strokeStyle = C.cyan; ctx.lineWidth = 2; ctx.globalAlpha = .6 + p * .3;
  for (let i = 0; i < 3; i++) { ctx.beginPath(); ctx.ellipse(0, 3, 7 + i * 5 + p * 1.5, 5 + i * 4 + p, clock * (.8 - i * .2), 0, TAU * .72); ctx.stroke(); }
  ctx.globalAlpha = 1; ctx.fillStyle = '#05070a'; ctx.beginPath(); ctx.ellipse(0, 4, 4, 3, 0, 0, TAU); ctx.fill(); ctx.restore();
  for (let i = 0; i < 4; i++) { const k = (clock * 8 + i * 5) % 12, a = clock * 1.3 + i * 1.57; ctx.fillStyle = 'rgba(143,211,255,' + (1 - k / 12) * .8 + ')'; ctx.fillRect(e.x + Math.cos(a) * 10, e.y - k * 1.6 - 2, 2, 2); }
}
function chestBody(big) {
  shadow(0, 10, 14, 4.5, .4);
  ctx.fillStyle = big ? '#4f3870' : '#6b4424'; ctx.fillRect(-12, -6, 24, 15);
  ctx.fillStyle = big ? '#654a8c' : '#80532c'; for (let i = 0; i < 3; i++) ctx.fillRect(-12, -5 + i * 5, 24, 1);
  ctx.fillStyle = '#2b2f3c'; ctx.fillRect(-12, -6, 3, 15); ctx.fillRect(9, -6, 3, 15);
  ctx.fillStyle = '#f0a23c'; ctx.fillRect(-12, 7, 24, 2);
}
function chestLid(big) {
  ctx.fillStyle = big ? '#654a8c' : '#80532c'; ctx.beginPath(); ctx.moveTo(-12, 0); ctx.lineTo(-12, -4); ctx.quadraticCurveTo(0, -12, 12, -4); ctx.lineTo(12, 0); ctx.fill();
  ctx.fillStyle = 'rgba(255,255,255,.14)'; ctx.beginPath(); ctx.moveTo(-10, -3); ctx.quadraticCurveTo(0, -9.5, 10, -3); ctx.lineTo(10, -4.5); ctx.quadraticCurveTo(0, -11, -10, -4.5); ctx.fill();
  ctx.fillStyle = '#2b2f3c'; ctx.fillRect(-12, -4, 3, 4); ctx.fillRect(9, -4, 3, 4);
  ctx.fillStyle = '#f0a23c'; ctx.fillRect(-2.5, -2.5, 5, 5); ctx.fillStyle = '#3b2b12'; ctx.fillRect(-.7, -1, 1.4, 2.6);
  if (big) { ctx.fillStyle = '#8fd3ff'; ctx.beginPath(); ctx.arc(-7, -3.5, 1.5, 0, TAU); ctx.fill(); ctx.fillStyle = '#d9534f'; ctx.beginPath(); ctx.arc(7, -3.5, 1.5, 0, TAU); ctx.fill(); }
}
function drawChestFx(f) {
  const t = f.t / .8, al = 1 - t, s = f.big ? 1.25 : 1;
  ctx.save(); ctx.translate(f.x, f.y); ctx.scale(s, s); ctx.globalAlpha = Math.min(1, al * 1.6);
  chestBody(f.big);
  ctx.save(); ctx.translate(0, -6); ctx.rotate(-Math.min(1, t * 3) * 1.1); chestLid(f.big); ctx.restore();
  const g = ctx.createLinearGradient(0, -6, 0, -50); g.addColorStop(0, 'rgba(255,225,140,' + al * .8 + ')'); g.addColorStop(1, 'rgba(255,225,140,0)');
  ctx.fillStyle = g; ctx.beginPath(); ctx.moveTo(-9, -6); ctx.lineTo(9, -6); ctx.lineTo(16, -50); ctx.lineTo(-16, -50); ctx.fill();
  ctx.restore();
}
function drawItemOld(it) {
  const b = Math.sin(it.t * 4) * 2;
  if (it.kind === 'gold') {
    const sx = Math.abs(Math.cos(it.t * 3)) * 4.5 + .8;
    glow(it.x, it.y, 14, C.amber, .45); shadow(it.x, it.y + 7, 4, 1.5, .3);
    ctx.fillStyle = '#c98414'; ctx.beginPath(); ctx.ellipse(it.x, it.y + b, sx + .8, 5.8, 0, 0, TAU); ctx.fill();
    ctx.fillStyle = '#ffc94d'; ctx.beginPath(); ctx.ellipse(it.x, it.y + b, sx, 5, 0, 0, TAU); ctx.fill();
    ctx.fillStyle = '#fff0b0'; ctx.fillRect(it.x - sx * .4, it.y + b - 3, Math.max(1, sx * .3), 3);
  } else if (it.kind === 'gem') {
    glow(it.x, it.y, 20, C.cyan, .5); const x = it.x, y = it.y + b;
    ctx.fillStyle = '#4fa8d8'; ctx.beginPath(); ctx.moveTo(x, y - 8); ctx.lineTo(x + 6.5, y - 1); ctx.lineTo(x, y + 8); ctx.lineTo(x - 6.5, y - 1); ctx.fill();
    ctx.fillStyle = '#a9e4ff'; ctx.beginPath(); ctx.moveTo(x, y - 8); ctx.lineTo(x + 6.5, y - 1); ctx.lineTo(x, y - 1); ctx.fill();
    ctx.fillStyle = 'rgba(255,255,255,.7)'; ctx.fillRect(x - 3, y - 4, 2, 2);
  } else if (it.kind === 'food') {
    const x = it.x, y = it.y + b; shadow(x, it.y + 8, 5, 2, .3);
    ctx.fillStyle = '#a8322d'; ctx.beginPath(); ctx.arc(x - 2, y, 6, 0, TAU); ctx.arc(x + 2.5, y, 6, 0, TAU); ctx.fill();
    ctx.fillStyle = '#d9534f'; ctx.beginPath(); ctx.arc(x - 2, y - .5, 5, 0, TAU); ctx.arc(x + 2.5, y - .5, 5, 0, TAU); ctx.fill();
    ctx.fillStyle = 'rgba(255,255,255,.4)'; ctx.fillRect(x - 5, y - 4, 2, 3);
    ctx.fillStyle = '#5a3a1e'; ctx.fillRect(x - .5, y - 9, 1.6, 4); ctx.fillStyle = '#6fae48'; ctx.beginPath(); ctx.ellipse(x + 3, y - 8, 3.5, 1.8, -.4, 0, TAU); ctx.fill();
  } else if (it.kind === 'chest') {
    const s = it.big ? 1.25 : 1;
    glow(it.x, it.y, 36 * s, C.amber, .4 + Math.sin(it.t * 3) * .1);
    ctx.save(); ctx.translate(it.x, it.y); ctx.scale(s, s); chestBody(it.big); ctx.translate(0, -6); chestLid(it.big); ctx.restore();
    ctx.fillStyle = 'rgba(255,230,150,.9)';
    for (let i = 0; i < 3; i++) { const a = clock * 2 + i * 2.1; ctx.fillRect(it.x + Math.cos(a) * 15 * s, it.y - 10 + Math.sin(a) * 6 - Math.abs(Math.sin(clock * 3 + i)) * 6, 2, 2); }
  } else {
    glow(it.x, it.y, 24, C.amber, .6); const x = it.x, y = it.y + b; shadow(x, it.y + 8, 7, 2, .3);
    ctx.strokeStyle = '#f0a23c'; ctx.fillStyle = '#f0a23c'; ctx.lineWidth = 3; ctx.beginPath(); ctx.arc(x - 5, y, 4, 0, TAU); ctx.stroke();
    ctx.fillRect(x - 1, y - 1.5, 13, 3); ctx.fillRect(x + 7, y, 3, 5); ctx.fillRect(x + 11, y, 2, 4);
    ctx.fillStyle = '#fff1b8'; ctx.fillRect(x - 7, y - 5, 2, 1.5); ctx.fillStyle = 'rgba(255,255,255,' + (.4 + .4 * Math.sin(clock * 6)) + ')'; ctx.fillRect(x + 2, y - 5, 2, 2);
  }
}
function drawNestOld(n) {
  const p = (Math.sin(clock * 4 + n.x) + 1) / 2, fl = n.flash > 0, x = n.x, y = n.y;
  shadow(x, y + 13, 20, 7, .45); glow(x, y, 46, '#c2563f', .22 + p * .2);
  ctx.fillStyle = fl ? '#fff' : '#2a2030'; ctx.fillRect(x - 17, y - 2, 34, 15);
  ctx.fillStyle = fl ? '#fff' : '#3a2a44'; ctx.fillRect(x - 17, y - 8, 34, 7);
  ctx.fillStyle = 'rgba(255,255,255,.08)'; ctx.fillRect(x - 17, y - 8, 34, 1);
  ctx.fillStyle = '#c2563f'; ctx.globalAlpha = .6 + p * .4;
  for (let i = 0; i < 3; i++) { ctx.fillRect(x - 11 + i * 9, y + 2, 3, 7); ctx.fillRect(x - 12 + i * 9, y + 5, 5, 2); }
  ctx.globalAlpha = 1;
  ctx.fillStyle = fl ? '#fff' : '#d8d2bd'; ctx.beginPath(); ctx.arc(x, y - 14, 9, 0, TAU); ctx.fill(); ctx.fillRect(x - 5, y - 10, 10, 6);
  ctx.fillStyle = '#0a0c11'; ctx.beginPath(); ctx.arc(x - 3.5, y - 15, 2.4, 0, TAU); ctx.arc(x + 3.5, y - 15, 2.4, 0, TAU); ctx.fill(); ctx.fillRect(x - 1, y - 11, 2, 2);
  ctx.fillStyle = 'rgba(255,110,80,' + (.5 + p * .5) + ')'; ctx.fillRect(x - 4, y - 16, 2, 2); ctx.fillRect(x + 2, y - 16, 2, 2);
  const w = 34; ctx.fillStyle = '#0a0c11'; ctx.fillRect(x - w / 2, y - 31, w, 4); ctx.fillStyle = C.blood; ctx.fillRect(x - w / 2, y - 31, w * n.hp / n.max, 4);
}

/* ---------- characters ---------- */
function feet(x, y, ang, phase, amp, side, col, rx, ry) {
  const c = Math.cos(ang), s = Math.sin(ang);
  for (const sg of [1, -1]) {
    const sw = Math.sin(phase + (sg > 0 ? 0 : Math.PI)) * amp;
    ctx.fillStyle = col; ctx.beginPath(); ctx.ellipse(x + c * sw - s * side * sg, y + s * sw + c * side * sg + 5, rx, ry, ang, 0, TAU); ctx.fill();
  }
}
const CLASS_ART = {
  bulwark(P, a, sw, ph, mv, h) {
    const ca = Math.cos(a), sa = Math.sin(a), steel = h ? '#fff' : '#8e9bb0', steelD = h ? '#fff' : '#5f6c82', gold = h ? '#fff' : '#e7b04a';
    ctx.save(); ctx.translate(sa * 11 + ca * 2, -ca * 11 + sa * 2 + 2); ctx.rotate(a);
    ctx.fillStyle = steelD; ctx.beginPath(); ctx.ellipse(0, 0, 4, 10.5, 0, 0, TAU); ctx.fill();
    ctx.fillStyle = gold; ctx.beginPath(); ctx.ellipse(0, 0, 2.6, 8.5, 0, 0, TAU); ctx.fill();
    ctx.fillStyle = steel; ctx.beginPath(); ctx.arc(0, 0, 2.6, 0, TAU); ctx.fill(); ctx.restore();
    ctx.fillStyle = steelD; ctx.beginPath(); ctx.ellipse(0, 3, 10, 8.5, 0, 0, TAU); ctx.fill();
    ctx.fillStyle = steel; ctx.beginPath(); ctx.ellipse(0, 1.5, 8.5, 7, 0, 0, TAU); ctx.fill();
    ctx.fillStyle = gold; ctx.fillRect(-8, 5, 16, 2); ctx.fillRect(-1, -4, 2, 9);
    for (const sg of [1, -1]) { ctx.fillStyle = steelD; ctx.beginPath(); ctx.arc(sg * 9.5, 0, 4.2, 0, TAU); ctx.fill(); ctx.fillStyle = gold; ctx.beginPath(); ctx.arc(sg * 9.5, 0, 1.6, 0, TAU); ctx.fill(); }
    const wa = sw > 0 ? a - 1.2 + (1 - sw) * 2.4 : a + .15;
    ctx.save(); ctx.translate(-sa * 9, ca * 9 + 2); ctx.rotate(wa);
    ctx.fillStyle = '#7a5a34'; ctx.fillRect(-3, -1.5, 6, 3); ctx.fillStyle = gold; ctx.fillRect(3, -4, 2.5, 8);
    ctx.fillStyle = '#d6dde8'; ctx.beginPath(); ctx.moveTo(5.5, -2); ctx.lineTo(24, -1.2); ctx.lineTo(28, 0); ctx.lineTo(24, 1.2); ctx.lineTo(5.5, 2); ctx.fill();
    ctx.fillStyle = 'rgba(255,255,255,.7)'; ctx.fillRect(6, -.5, 17, 1); ctx.restore();
    ctx.save(); ctx.translate(ca * 1.5, -8 + sa * 1.5);
    ctx.fillStyle = h ? '#fff' : '#c2423a'; ctx.beginPath(); ctx.ellipse(-ca * 5, -3 - sa * 4, 3.2, 5.5, 0, 0, TAU); ctx.fill();
    ctx.fillStyle = steelD; ctx.beginPath(); ctx.arc(0, 0, 7.5, 0, TAU); ctx.fill(); ctx.fillStyle = steel; ctx.beginPath(); ctx.arc(-1, -1, 6, 0, TAU); ctx.fill();
    ctx.rotate(a); ctx.fillStyle = '#10131a'; ctx.fillRect(2.2, -3.5, 3.4, 7); ctx.restore();
  },
  ember(P, a, sw, ph, mv, h) {
    const ca = Math.cos(a), sa = Math.sin(a), robe = h ? '#fff' : '#b3402c', robeD = h ? '#fff' : '#7f2b1f', gold = h ? '#fff' : '#f0a23c';
    ctx.fillStyle = robeD; ctx.beginPath(); ctx.moveTo(-11, 12); ctx.lineTo(11, 12); ctx.lineTo(7, -3); ctx.lineTo(-7, -3); ctx.fill();
    ctx.fillStyle = robe; ctx.beginPath(); ctx.moveTo(-9, 12); ctx.lineTo(9, 12); ctx.lineTo(5.5, -3); ctx.lineTo(-5.5, -3); ctx.fill();
    ctx.fillStyle = gold; ctx.fillRect(-9, 10.5, 18, 1.6); ctx.fillRect(-6.5, 2, 13, 2);
    ctx.fillStyle = robeD; for (const sg of [1, -1]) { ctx.beginPath(); ctx.arc(sg * 7.5, 0, 3.6, 0, TAU); ctx.fill(); }
    ctx.save(); ctx.translate(-sa * 8 + ca * 2, ca * 8 + sa * 2 + 1); ctx.rotate(a);
    ctx.fillStyle = '#6b4a2a'; ctx.fillRect(-6, -1.2, 28, 2.4); ctx.fillStyle = gold; ctx.fillRect(18, -2.5, 2, 5);
    const pulse = 1 + (sw > 0 ? sw * .8 : 0) + Math.sin(clock * 8) * .1;
    glow(26, 0, 14 * pulse, '#ff8a6b', .8); ctx.fillStyle = '#ff6a3d'; ctx.beginPath(); ctx.arc(26, 0, 4.2 * pulse, 0, TAU); ctx.fill();
    ctx.fillStyle = '#fff1c8'; ctx.beginPath(); ctx.arc(26, 0, 2 * pulse, 0, TAU); ctx.fill(); ctx.restore();
    ctx.save(); ctx.translate(ca * 1.2, -8 + sa * 1.2);
    ctx.fillStyle = robeD; ctx.beginPath(); ctx.arc(0, 0, 7.8, 0, TAU); ctx.fill(); ctx.beginPath(); ctx.moveTo(-6, -3); ctx.lineTo(0, -15); ctx.lineTo(6, -3); ctx.fill();
    ctx.fillStyle = '#140808'; ctx.beginPath(); ctx.ellipse(ca * 2, sa * 1.6, 5, 4.4, 0, 0, TAU); ctx.fill();
    ctx.fillStyle = '#ffb347'; ctx.fillRect(ca * 2 - 3, sa * 1.6 - 1, 2, 2); ctx.fillRect(ca * 2 + 1, sa * 1.6 - 1, 2, 2); ctx.restore();
  },
  sable(P, a, sw, ph, mv, h) {
    const ca = Math.cos(a), sa = Math.sin(a), f = P.face || 0, cl = h ? '#fff' : '#1f4a49', body = h ? '#fff' : '#2f6e6a', sc = h ? '#fff' : '#7fd1c7';
    const tl = 8 + 8 * mv, tx = -Math.cos(f) * tl, ty = -Math.sin(f) * tl + 4 + Math.sin(ph * 1.3) * 1.5 * mv;
    ctx.fillStyle = cl; ctx.beginPath(); ctx.moveTo(-8, 0); ctx.quadraticCurveTo(tx - 4, ty - 2, tx, ty + 5); ctx.quadraticCurveTo(tx + 5, ty, 8, 0); ctx.closePath(); ctx.fill();
    ctx.fillStyle = body; ctx.beginPath(); ctx.ellipse(0, 3, 8.2, 7.6, 0, 0, TAU); ctx.fill();
    ctx.fillStyle = '#12302f'; ctx.fillRect(-8, 6, 16, 2); ctx.fillStyle = '#c9a24a'; ctx.fillRect(-1.5, 5.7, 3, 2.6);
    for (const sg of [1, -1]) {
      ctx.save(); ctx.translate(-sa * sg * 8.5 + ca * (4 + sw * 7), ca * sg * 8.5 + sa * (4 + sw * 7) + 2); ctx.rotate(a + sg * .22);
      ctx.fillStyle = '#e6f3f1'; ctx.beginPath(); ctx.moveTo(1, -1.4); ctx.lineTo(11, 0); ctx.lineTo(1, 1.4); ctx.fill();
      ctx.fillStyle = '#3b2b1a'; ctx.fillRect(-3, -1.2, 4, 2.4); ctx.fillStyle = '#c9a24a'; ctx.fillRect(1, -2.5, 1.4, 5); ctx.restore();
    }
    ctx.fillStyle = sc; ctx.beginPath(); ctx.ellipse(0, -2.5, 6, 2.6, 0, 0, TAU); ctx.fill();
    ctx.beginPath(); ctx.moveTo(-3, -2); ctx.lineTo(-7 - Math.sin(ph * 2) * 2 * mv, 5); ctx.lineTo(-1, 0); ctx.fill();
    ctx.save(); ctx.translate(ca * 1.2, -8 + sa * 1.2);
    ctx.fillStyle = cl; ctx.beginPath(); ctx.arc(0, 0, 7.2, 0, TAU); ctx.fill(); ctx.beginPath(); ctx.moveTo(-5.5, -3); ctx.lineTo(-1, -12.5); ctx.lineTo(5.5, -3); ctx.fill();
    ctx.fillStyle = '#0b1b1b'; ctx.beginPath(); ctx.ellipse(ca * 1.8, sa * 1.4, 4.6, 4, 0, 0, TAU); ctx.fill();
    ctx.fillStyle = '#e6f3f1'; ctx.fillRect(ca * 1.8 - 2.8, sa * 1.4 - .8, 1.8, 1.6); ctx.fillRect(ca * 1.8 + 1, sa * 1.4 - .8, 1.8, 1.6); ctx.restore();
  },
  thistle(P, a, sw, ph, mv, h) {
    const ca = Math.cos(a), sa = Math.sin(a), tun = h ? '#fff' : '#5b8a3c', cl = h ? '#fff' : '#4a3a26', cap = h ? '#fff' : '#3f6b2a', skin = h ? '#fff' : '#e3c4a0';
    ctx.save(); ctx.translate(-ca * 7, -sa * 5 + 1); ctx.rotate(.3); ctx.fillStyle = '#5a3a1e'; ctx.fillRect(-2.5, -8, 5, 13);
    ctx.fillStyle = '#9bd16a'; ctx.fillRect(-2, -11, 1.2, 4); ctx.fillRect(0, -12, 1.2, 5); ctx.fillRect(1.6, -10.5, 1.2, 4); ctx.restore();
    ctx.fillStyle = cl; ctx.beginPath(); ctx.ellipse(0, 4, 9.5, 8, 0, 0, TAU); ctx.fill();
    ctx.fillStyle = tun; ctx.beginPath(); ctx.ellipse(0, 2.6, 8, 7, 0, 0, TAU); ctx.fill();
    ctx.fillStyle = '#4a3220'; ctx.fillRect(-8, 5, 16, 2); ctx.fillStyle = '#c9a24a'; ctx.fillRect(-1.5, 4.8, 3, 3.4);
    ctx.save(); ctx.translate(ca * 3 - sa * 4, sa * 3 + ca * 4 + 1); ctx.rotate(a);
    const pull = sw > 0 ? 1 - sw * .4 : 0, sx = pull ? 2 - 5 * pull : 1;
    ctx.strokeStyle = '#7a5a34'; ctx.lineWidth = 3; ctx.beginPath(); ctx.arc(2, 0, 14, -1.15, 1.15); ctx.stroke();
    ctx.strokeStyle = '#e9e3cf'; ctx.lineWidth = 1; ctx.beginPath(); ctx.moveTo(2 + Math.cos(-1.15) * 14, Math.sin(-1.15) * 14); ctx.lineTo(sx, 0); ctx.lineTo(2 + Math.cos(1.15) * 14, Math.sin(1.15) * 14); ctx.stroke();
    ctx.strokeStyle = '#b89a6a'; ctx.lineWidth = 1.6; ctx.beginPath(); ctx.moveTo(sx, 0); ctx.lineTo(18, 0); ctx.stroke();
    ctx.fillStyle = '#d6dccb'; ctx.beginPath(); ctx.moveTo(18, 0); ctx.lineTo(14.5, -2); ctx.lineTo(14.5, 2); ctx.fill(); ctx.restore();
    ctx.save(); ctx.translate(ca * 1.2, -8 + sa * 1.2);
    ctx.fillStyle = skin; ctx.beginPath(); ctx.arc(0, 0, 6.4, 0, TAU); ctx.fill();
    ctx.fillStyle = cap; ctx.beginPath(); ctx.arc(0, -1.5, 6.9, Math.PI, TAU); ctx.fill(); ctx.fillRect(-7, -2, 14, 2);
    ctx.strokeStyle = '#d6dccb'; ctx.lineWidth = 1.5; ctx.beginPath(); ctx.moveTo(4, -5); ctx.quadraticCurveTo(10, -9, 12, -3); ctx.stroke();
    ctx.fillStyle = '#2a1a10'; ctx.fillRect(ca * 2 - 2.8, sa * 1.4 + .4, 1.6, 1.8); ctx.fillRect(ca * 2 + 1.2, sa * 1.4 + .4, 1.6, 1.8); ctx.restore();
  }
};
function drawPlayerOld(P) {
  const c = P.cls, x = P.x, y = P.y;
  if (P.down) {
    shadow(x, y + 7, 12, 5); ctx.fillStyle = '#4a5166'; ctx.beginPath(); ctx.ellipse(x, y + 2, 11, 7, 0, 0, TAU); ctx.fill();
    ctx.fillStyle = mix(c.col, -.4); ctx.beginPath(); ctx.arc(x - 5, y - 1, 4, 0, TAU); ctx.fill();
    ctx.strokeStyle = c.col; ctx.lineWidth = 2; ctx.beginPath(); ctx.arc(x, y, 17, -Math.PI / 2, -Math.PI / 2 + TAU * P.rev / 1.5); ctx.stroke();
    ctx.fillStyle = C.bone; ctx.font = '600 10px "Spline Sans Mono",monospace'; ctx.textAlign = 'center'; ctx.fillText('REVIVE', x, y - 22);
    return;
  }
  const mv = Math.min(1, Math.hypot(x - (P.lx ?? x), y - (P.ly ?? y)) * 1.4); P.lx = x; P.ly = y;
  const ph = P.walk || 0, bob = Math.abs(Math.sin(ph)) * 1.6 * mv, sw = P.swing > 0 ? P.swing / (P.swm || .18) : 0;
  if (P.inv > 0 && P.dash <= 0 && Math.floor(clock * 20) % 2) ctx.globalAlpha = .45;
  shadow(x, y + 10, 12, 5); glow(x, y, 32, c.col, .2);
  feet(x, y, P.face || 0, ph, 4.5 * mv, 4, '#241d19', 3.4, 2.4);
  ctx.save(); ctx.translate(x, y - 3 - bob);
  CLASS_ART[c.key](P, P.aim, sw, ph, mv, P.hurt > 0);
  ctx.restore(); ctx.globalAlpha = 1;
  if (G.co) { ctx.fillStyle = c.col; ctx.font = '600 10px "Spline Sans Mono",monospace'; ctx.textAlign = 'center'; ctx.fillText('P' + (P.idx + 1), x, y - 26); }
}

/* ---------- monsters ---------- */
function drawGloam(e) {
  const w = Math.sin(e.walk * .8) * .1 + (e.flash > 0 ? .08 : 0), r = e.r, col = e.flash > 0 ? '#ffffff' : e.col;
  shadow(e.x, e.y + r * .8, r, r * .4, .35);
  ctx.save(); ctx.translate(e.x, e.y + 2); ctx.scale(1 + w, 1 - w);
  const g = ctx.createRadialGradient(-3, -6, 1, 0, -1, r + 5); g.addColorStop(0, mix(col, .5)); g.addColorStop(.6, col); g.addColorStop(1, mix(col, -.45));
  ctx.fillStyle = g; ctx.beginPath(); ctx.moveTo(-r, 4); ctx.bezierCurveTo(-r - 2, -r, r + 2, -r, r, 4); ctx.bezierCurveTo(r - 2, r * .9, -r + 2, r * .9, -r, 4); ctx.fill();
  ctx.fillStyle = mix(col, -.2); ctx.beginPath(); ctx.arc(-r + 1, 7, 2.5, 0, TAU); ctx.arc(r - 2, 8, 2, 0, TAU); ctx.fill();
  ctx.fillStyle = 'rgba(255,255,255,.35)'; ctx.beginPath(); ctx.ellipse(-4, -6, 3.5, 2, -.5, 0, TAU); ctx.fill();
  const lx = Math.cos(e.face || 0) * 1.5, ly = Math.sin(e.face || 0);
  ctx.fillStyle = '#fff'; ctx.beginPath(); ctx.arc(-4, -1, 3.2, 0, TAU); ctx.arc(4, -1, 3.2, 0, TAU); ctx.fill();
  ctx.fillStyle = '#1a1020'; ctx.beginPath(); ctx.arc(-4 + lx, -1 + ly, 1.6, 0, TAU); ctx.arc(4 + lx, -1 + ly, 1.6, 0, TAU); ctx.fill();
  ctx.strokeStyle = '#1a1020'; ctx.lineWidth = 1.2; ctx.beginPath(); ctx.arc(0, 4, 3, .15, Math.PI - .15); ctx.stroke();
  ctx.restore();
}
function drawWisp(e) {
  const col = e.flash > 0 ? '#ffffff' : e.col, t = e.t, y = e.y + Math.sin(t * 5) * 2 - 4;
  shadow(e.x, e.y + 8, 6, 2.5, .25); glow(e.x, y, 26, e.col, .55);
  ctx.fillStyle = col; ctx.beginPath(); ctx.moveTo(e.x - 7, y); ctx.bezierCurveTo(e.x - 7, y - 11, e.x + 7, y - 11, e.x + 7, y);
  for (let i = 0; i < 4; i++) { const ex = e.x + 7 - (i + 1) * 3.5; ctx.quadraticCurveTo(ex + 1.75, y + 8 + Math.sin(t * 8 + i * 2) * 3, ex, y + 2 + Math.sin(t * 8 + i)); }
  ctx.fill();
  ctx.fillStyle = 'rgba(255,255,255,.55)'; ctx.beginPath(); ctx.ellipse(e.x, y - 3, 3, 4, 0, 0, TAU); ctx.fill();
  ctx.fillStyle = '#10212b'; ctx.beginPath(); ctx.ellipse(e.x - 2.5, y - 2, 1.3, 2, 0, 0, TAU); ctx.ellipse(e.x + 2.5, y - 2, 1.3, 2, 0, 0, TAU); ctx.fill();
}
function drawBone(e, mv) {
  const col = e.flash > 0 ? '#ffffff' : '#d8d2bd', dk = e.flash > 0 ? '#ffffff' : '#a59f8a', ph = e.walk, x = e.x, y = e.y, f = e.face || 0;
  shadow(x, y + 10, 9, 3.5, .35);
  ctx.strokeStyle = dk; ctx.lineWidth = 2.5; ctx.lineCap = 'round';
  for (const sg of [1, -1]) { const s = Math.sin(ph + (sg > 0 ? 0 : Math.PI)) * 4 * mv; ctx.beginPath(); ctx.moveTo(x + sg * 3, y + 4); ctx.lineTo(x + sg * 3, y + 11 + s * .6); ctx.stroke(); }
  ctx.fillStyle = col; ctx.fillRect(x - 6, y - 4, 12, 10); ctx.fillStyle = '#2a2a33'; for (let i = 0; i < 3; i++) ctx.fillRect(x - 5, y - 2 + i * 3, 10, 1.2);
  ctx.fillStyle = dk; ctx.fillRect(x - 1, y - 4, 2, 10);
  ctx.strokeStyle = col; ctx.lineWidth = 2.2;
  for (const sg of [1, -1]) { const s = Math.sin(ph + (sg > 0 ? Math.PI : 0)) * 3 * mv; ctx.beginPath(); ctx.moveTo(x + sg * 6, y - 2); ctx.lineTo(x + sg * 10, y + 3 + s); ctx.stroke(); }
  ctx.fillStyle = col; ctx.beginPath(); ctx.arc(x, y - 9, 6.5, 0, TAU); ctx.fill(); ctx.fillRect(x - 3.5, y - 6, 7, 4);
  ctx.fillStyle = '#14141b'; ctx.beginPath(); ctx.arc(x - 2.6 + Math.cos(f), y - 9.5 + Math.sin(f) * .8, 2, 0, TAU); ctx.arc(x + 2.6 + Math.cos(f), y - 9.5 + Math.sin(f) * .8, 2, 0, TAU); ctx.fill();
  ctx.fillRect(x - 2, y - 5, 1, 2); ctx.fillRect(x + 1, y - 5, 1, 2);
  const rs = e.cd < .5 ? 1 : 0; ctx.save(); ctx.translate(x + 10, y + 2 - rs * 3); ctx.rotate(-.6 + Math.sin(ph) * .15 * mv - rs * .5);
  ctx.fillStyle = '#ebe4d2'; ctx.fillRect(-1, -7, 2, 14); ctx.beginPath(); ctx.arc(-1.5, -7, 2, 0, TAU); ctx.arc(1.5, -7, 2, 0, TAU); ctx.arc(-1.5, 7, 2, 0, TAU); ctx.arc(1.5, 7, 2, 0, TAU); ctx.fill(); ctx.restore();
  ctx.lineCap = 'butt';
}
function drawBrute(e, mv) {
  const col = e.flash > 0 ? '#ffffff' : e.col, dk = mix(e.col, -.4), lt = mix(e.col, .3), x = e.x, y = e.y, ph = e.walk * .7, f = e.face || 0;
  shadow(x, y + 13, 15, 6, .4);
  for (const sg of [1, -1]) { const s = Math.sin(ph + (sg > 0 ? 0 : Math.PI)) * 3.5 * mv; ctx.fillStyle = dk; ctx.beginPath(); ctx.ellipse(x + sg * 6, y + 11 + s * .5, 5, 4, 0, 0, TAU); ctx.fill(); }
  ctx.save(); ctx.translate(x + 13, y - 2); ctx.rotate(-.5 + Math.sin(ph) * .35 * mv);
  ctx.fillStyle = '#6b4a2a'; ctx.fillRect(-2.5, -2, 5, 18); ctx.fillStyle = '#7a5a34'; ctx.beginPath(); ctx.ellipse(0, 18, 6, 7, 0, 0, TAU); ctx.fill();
  ctx.fillStyle = '#c9ccd6'; ctx.fillRect(-1, 15, 2, 2); ctx.fillRect(3, 18, 2, 2); ctx.restore();
  const g = ctx.createRadialGradient(-4, -8, 2, 0, 0, 20); g.addColorStop(0, e.flash > 0 ? '#fff' : lt); g.addColorStop(1, e.flash > 0 ? '#fff' : dk);
  ctx.save(); ctx.translate(x, y); ctx.fillStyle = g; ctx.beginPath(); ctx.ellipse(0, 0, 14, 13, 0, 0, TAU); ctx.fill(); ctx.restore();
  ctx.fillStyle = dk; ctx.beginPath(); ctx.ellipse(x - 12, y - 3, 6, 5, 0, 0, TAU); ctx.fill();
  ctx.fillStyle = '#4a3322'; ctx.fillRect(x - 11, y + 2, 22, 4); ctx.fillStyle = '#c9a24a'; ctx.fillRect(x - 2, y + 1.5, 4, 5);
  ctx.fillStyle = col; ctx.beginPath(); ctx.arc(x, y - 11, 8, 0, TAU); ctx.fill();
  ctx.fillStyle = '#ebe4d2'; ctx.beginPath(); ctx.moveTo(x - 5, y - 6); ctx.lineTo(x - 7, y - 2); ctx.lineTo(x - 3, y - 5); ctx.moveTo(x + 5, y - 6); ctx.lineTo(x + 7, y - 2); ctx.lineTo(x + 3, y - 5); ctx.fill();
  ctx.beginPath(); ctx.moveTo(x - 7, y - 16); ctx.lineTo(x - 11, y - 25); ctx.lineTo(x - 3, y - 18); ctx.moveTo(x + 7, y - 16); ctx.lineTo(x + 11, y - 25); ctx.lineTo(x + 3, y - 18); ctx.fill();
  ctx.fillStyle = '#ffd24a'; ctx.fillRect(x - 5, y - 13, 3.5, 2.5); ctx.fillRect(x + 1.5, y - 13, 3.5, 2.5);
  ctx.fillStyle = '#2a0f0a'; ctx.fillRect(x - 4 + Math.cos(f), y - 12.8, 1.4, 2); ctx.fillRect(x + 2.5 + Math.cos(f), y - 12.8, 1.4, 2);
}
function drawHound(e, mv) {
  const col = e.flash > 0 ? '#ffffff' : e.col, dk = mix(e.col, -.45), lt = mix(e.col, .3), f = e.face || 0, ph = e.walk * .9, wind = e.st === 'wind', lunge = e.st === 'lunge';
  if (wind) {
    const p = Math.min(1, e.stt / .45); ctx.save(); ctx.translate(e.x, e.y); ctx.rotate(f);
    ctx.strokeStyle = 'rgba(255,90,70,' + (.25 + p * .5) + ')'; ctx.lineWidth = 2 + p * 4; ctx.setLineDash([8, 6]); ctx.beginPath(); ctx.moveTo(14, 0); ctx.lineTo(150, 0); ctx.stroke(); ctx.setLineDash([]); ctx.restore();
  }
  shadow(e.x, e.y + 7, 15, 5, .35);
  ctx.save(); ctx.translate(e.x, e.y); ctx.rotate(f); ctx.scale(lunge ? 1.25 : wind ? .9 : 1, lunge ? .85 : wind ? 1.1 : 1);
  for (const [lx, s] of [[7, 0], [7, 1], [-7, 1], [-7, 0]]) { const sw = Math.sin(ph + s * Math.PI) * 4 * (lunge ? 1.6 : mv); ctx.fillStyle = dk; ctx.beginPath(); ctx.ellipse(lx + sw, s ? 5.5 : -5.5, 3.4, 2.3, 0, 0, TAU); ctx.fill(); }
  ctx.strokeStyle = dk; ctx.lineWidth = 3; ctx.lineCap = 'round'; ctx.beginPath(); ctx.moveTo(-11, 0); ctx.quadraticCurveTo(-18, Math.sin(ph) * 4, -20, Math.sin(ph) * 6 - 3); ctx.stroke();
  const g = ctx.createRadialGradient(-2, -3, 1, 0, 0, 14); g.addColorStop(0, e.flash > 0 ? '#fff' : lt); g.addColorStop(1, e.flash > 0 ? '#fff' : dk);
  ctx.fillStyle = g; ctx.beginPath(); ctx.ellipse(0, 0, 13, 7.5, 0, 0, TAU); ctx.fill();
  ctx.fillStyle = dk; for (let i = 0; i < 4; i++) { ctx.beginPath(); ctx.moveTo(-8 + i * 5, -6.5); ctx.lineTo(-6 + i * 5, -10); ctx.lineTo(-4 + i * 5, -6.5); ctx.fill(); }
  ctx.fillStyle = col; ctx.beginPath(); ctx.ellipse(13, 0, 7, 5.5, 0, 0, TAU); ctx.fill();
  ctx.fillStyle = dk; ctx.beginPath(); ctx.moveTo(10, -4); ctx.lineTo(8, -9); ctx.lineTo(14, -5); ctx.moveTo(10, 4); ctx.lineTo(8, 9); ctx.lineTo(14, 5); ctx.fill();
  ctx.fillStyle = '#ebe4d2'; ctx.fillRect(17.5, -1.8, 3, 1.1); ctx.fillRect(17.5, .7, 3, 1.1);
  ctx.fillStyle = wind ? '#ff5a46' : '#ffd24a'; ctx.fillRect(13, -3.6, 2.6, 1.8); ctx.fillRect(13, 1.8, 2.6, 1.8);
  ctx.restore();
}
function drawWarden(e, mv) {
  const col = e.flash > 0 ? '#ffffff' : e.col, dk = mix(e.col, -.5), lt = mix(e.col, .35), x = e.x, y = e.y, ph = e.walk * .5, f = e.face || 0, p2 = e.ph >= 2, t = e.t;
  if (e.st === 'slam') {
    const p = Math.min(1, e.stt / .9);
    ctx.fillStyle = 'rgba(255,70,50,' + (.08 + p * .12) + ')'; ctx.beginPath(); ctx.arc(x, y, 120, 0, TAU); ctx.fill();
    ctx.strokeStyle = 'rgba(255,90,70,' + (.4 + p * .5) + ')'; ctx.lineWidth = 2; ctx.beginPath(); ctx.arc(x, y, 120, 0, TAU); ctx.stroke();
    ctx.fillStyle = 'rgba(255,90,70,' + (.16 + p * .25) + ')'; ctx.beginPath(); ctx.arc(x, y, 120 * p, 0, TAU); ctx.fill();
  }
  if (e.st === 'burst') glow(x, y, 60 + Math.sin(t * 30) * 6, '#ff5a46', .45);
  if (e.st === 'summon') glow(x, y, 70, '#9a6bd6', .5);
  if (p2) glow(x, y, 54, '#ff4a3a', .18 + Math.sin(t * 6) * .06);
  shadow(x, y + 20, 26, 10, .5);
  for (const sg of [1, -1]) { const s = Math.sin(ph + (sg > 0 ? 0 : Math.PI)) * 5 * mv; ctx.fillStyle = dk; ctx.beginPath(); ctx.ellipse(x + sg * 9, y + 18 + s * .5, 7, 5, 0, 0, TAU); ctx.fill(); }
  ctx.fillStyle = mix(e.col, -.65); ctx.beginPath(); ctx.moveTo(x - 16, y - 6); ctx.lineTo(x + 16, y - 6); ctx.lineTo(x + 20 + Math.sin(t * 3) * 2, y + 22); ctx.lineTo(x - 20 + Math.sin(t * 3 + 1) * 2, y + 22); ctx.fill();
  const wa = -.7 + (e.st === 'slam' ? -Math.min(1, e.stt / .9) * 1.2 : Math.sin(ph) * .12 * mv);
  ctx.save(); ctx.translate(x + 24, y); ctx.rotate(wa);
  ctx.fillStyle = '#5a4630'; ctx.fillRect(-2.5, -4, 5, 14); ctx.fillStyle = '#c9a24a'; ctx.fillRect(-7, -6, 14, 3);
  ctx.fillStyle = '#c9ccd6'; ctx.beginPath(); ctx.moveTo(-4, -6); ctx.lineTo(-3, -42); ctx.lineTo(0, -50); ctx.lineTo(3, -42); ctx.lineTo(4, -6); ctx.fill();
  ctx.fillStyle = 'rgba(255,255,255,.5)'; ctx.fillRect(-.6, -44, 1.2, 36); ctx.restore();
  const g = ctx.createRadialGradient(x - 6, y - 10, 3, x, y, 26); g.addColorStop(0, e.flash > 0 ? '#fff' : lt); g.addColorStop(1, e.flash > 0 ? '#fff' : dk);
  ctx.fillStyle = g; ctx.beginPath(); ctx.ellipse(x, y, 20, 17, 0, 0, TAU); ctx.fill();
  ctx.fillStyle = col; ctx.beginPath(); ctx.ellipse(x - 19, y - 4, 9, 7, -.3, 0, TAU); ctx.ellipse(x + 17, y - 4, 9, 7, .3, 0, TAU); ctx.fill();
  ctx.fillStyle = dk; for (const sx of [-19, 17]) { ctx.beginPath(); ctx.moveTo(x + sx - 4, y - 9); ctx.lineTo(x + sx, y - 17); ctx.lineTo(x + sx + 4, y - 9); ctx.fill(); }
  ctx.strokeStyle = 'rgba(0,0,0,.35)'; ctx.lineWidth = 1.5; ctx.beginPath(); ctx.moveTo(x - 12, y + 4); ctx.lineTo(x + 12, y + 4); ctx.moveTo(x, y - 12); ctx.lineTo(x, y + 12); ctx.stroke();
  ctx.fillStyle = '#c9a24a'; ctx.beginPath(); ctx.arc(x, y + 4, 3.5, 0, TAU); ctx.fill();
  ctx.fillStyle = col; ctx.beginPath(); ctx.arc(x, y - 17, 11, 0, TAU); ctx.fill();
  ctx.fillStyle = dk; ctx.beginPath(); ctx.moveTo(x - 10, y - 21); ctx.lineTo(x - 17, y - 34); ctx.lineTo(x - 4, y - 26); ctx.moveTo(x + 10, y - 21); ctx.lineTo(x + 17, y - 34); ctx.lineTo(x + 4, y - 26); ctx.fill();
  ctx.fillStyle = '#0a0c11'; ctx.fillRect(x - 8, y - 19, 16, 4);
  ctx.fillStyle = p2 ? '#ff4a3a' : '#ffd24a'; ctx.fillRect(x - 6.5 + Math.cos(f) * 1.2, y - 18.5, 4, 3); ctx.fillRect(x + 2.5 + Math.cos(f) * 1.2, y - 18.5, 4, 3);
}
function drawCrit(f) {
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
function drawWarn(f) {
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
function drawShock(f) {
  if (f.t < 0) return;
  const c1 = f.c1 || '255,230,200', c2 = f.c2 || '255,90,60';
  const p = Math.min(1, f.t / .35), al = Math.max(0, 1 - f.t / .8), R = Math.max(1, (f.r || 80) * (.3 + .7 * p));
  ctx.strokeStyle = 'rgba(' + c1 + ',' + al + ')'; ctx.lineWidth = 6 * al + 1; ctx.beginPath(); ctx.arc(f.x, f.y, R, 0, TAU); ctx.stroke();
  ctx.strokeStyle = 'rgba(' + c2 + ',' + al * .6 + ')'; ctx.lineWidth = 14 * al; ctx.beginPath(); ctx.arc(f.x, f.y, R * .94, 0, TAU); ctx.stroke();
}
function drawFoe(e) {
  const mv = Math.min(1, Math.hypot(e.x - (e.lx ?? e.x), e.y - (e.ly ?? e.y)) * 1.6); e.lx = e.x; e.ly = e.y;
  const SF = foeDef(e.type, e.kind), useSpr = SF && sprOk(SF.key);
  if (useSpr) drawFoeSpr(e, mv); else ({ gloam: drawGloam, wisp: drawWisp, bonewalker: drawBone, brute: drawBrute, hound: drawHound, bloat: drawGloam, thief: drawGloam, reaper: drawWisp, warden: drawWarden })[e.type](e, mv);
  if (e.hp < e.max && !e.boss) { const w = e.r * 2 + 6, hb = e.elite ? 4 : 3, top = useSpr ? e.y + (SF ? SF.bar : -40) : e.type === 'brute' ? e.y - 30 : e.y - e.r - 14; ctx.fillStyle = '#0a0c11'; ctx.fillRect(e.x - w / 2, top, w, hb); ctx.fillStyle = e.elite ? '#ffd24a' : C.blood; ctx.fillRect(e.x - w / 2, top, w * e.hp / e.max, hb); }
}
function drawDyingOld(d) {
  const p = d.t / .5, a = 1 - p;
  ctx.save(); ctx.translate(d.x, d.y);
  ctx.strokeStyle = 'rgba(255,255,255,' + a * .8 + ')'; ctx.lineWidth = 2 * a + .5; ctx.beginPath(); ctx.arc(0, 0, d.r * (1 + p * 2.2), 0, TAU); ctx.stroke();
  ctx.globalAlpha = a; ctx.scale(1 + p * .25, 1 - p * .9); ctx.translate(0, d.r * p * .9);
  ctx.fillStyle = p < .25 ? '#fff' : d.col; ctx.beginPath(); ctx.ellipse(0, 0, d.r, d.r * 1.1, 0, 0, TAU); ctx.fill();
  ctx.restore();
}

/* ---------- projectiles and effects ---------- */
function trailLine(tr, col, w) {
  if (tr.length < 4) return; ctx.strokeStyle = col; ctx.lineWidth = w; ctx.beginPath(); ctx.moveTo(tr[0], tr[1]);
  for (let i = 2; i < tr.length; i += 2) ctx.lineTo(tr[i], tr[i + 1]); ctx.stroke();
}
function drawBolts() {
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
function drawShots() {
  for (const s of G.shots) {
    const a = Math.atan2(s.vy, s.vx), tr = s.trail;
    if (s.kind === 'fire') {
      for (let i = 0; i < tr.length; i += 2) { const q = i / tr.length; ctx.fillStyle = 'rgba(255,' + ((120 + q * 80) | 0) + ',60,' + q * .5 + ')'; ctx.beginPath(); ctx.arc(tr[i], tr[i + 1], 2 + q * 4, 0, TAU); ctx.fill(); }
      glow(s.x, s.y, 26, '#ff7a4a', .75); const j = Math.random() * 1.5;
      ctx.fillStyle = '#ff6a2b'; ctx.beginPath(); ctx.arc(s.x, s.y, 6.5 + j, 0, TAU); ctx.fill();
      ctx.fillStyle = '#ffb347'; ctx.beginPath(); ctx.arc(s.x, s.y, 4.5, 0, TAU); ctx.fill();
      ctx.fillStyle = '#fff3c8'; ctx.beginPath(); ctx.arc(s.x, s.y, 2.4, 0, TAU); ctx.fill();
    } else if (s.kind === 'arrow') {
      trailLine(tr, 'rgba(155,209,106,.35)', 2);
      ctx.save(); ctx.translate(s.x, s.y); ctx.rotate(a);
      ctx.strokeStyle = '#b89a6a'; ctx.lineWidth = 1.8; ctx.beginPath(); ctx.moveTo(-12, 0); ctx.lineTo(6, 0); ctx.stroke();
      ctx.fillStyle = '#d6dccb'; ctx.beginPath(); ctx.moveTo(11, 0); ctx.lineTo(5, -2.8); ctx.lineTo(5, 2.8); ctx.fill();
      ctx.fillStyle = '#9bd16a'; ctx.beginPath(); ctx.moveTo(-12, 0); ctx.lineTo(-15, -3); ctx.lineTo(-9, 0); ctx.lineTo(-15, 3); ctx.fill(); ctx.restore();
      glow(s.x, s.y, 12, s.col, .35);
    } else {
      trailLine(tr, 'rgba(127,209,199,.4)', 2);
      ctx.save(); ctx.translate(s.x, s.y); ctx.rotate(s.life * 50);
      ctx.fillStyle = '#e6f3f1'; ctx.beginPath(); ctx.moveTo(7, 0); ctx.lineTo(-2, -2.6); ctx.lineTo(-2, 2.6); ctx.fill();
      ctx.fillStyle = '#3b2b1a'; ctx.fillRect(-5, -1, 3, 2); ctx.restore();
    }
  }
  for (const s of G.eshots) {
    glow(s.x, s.y, 12, '#d8d2bd', .4); ctx.save(); ctx.translate(s.x, s.y); ctx.rotate(s.life * 14);
    ctx.fillStyle = '#ebe4d2'; ctx.fillRect(-1, -5, 2, 10); ctx.beginPath(); ctx.arc(-1.4, -5, 1.7, 0, TAU); ctx.arc(1.4, -5, 1.7, 0, TAU); ctx.arc(-1.4, 5, 1.7, 0, TAU); ctx.arc(1.4, 5, 1.7, 0, TAU); ctx.fill(); ctx.restore();
  }
}
function drawFx() {
  for (const p of G.parts) {
    const al = clamp(p.life / p.max, 0, 1);
    if (p.k === 'spark') { ctx.strokeStyle = p.col; ctx.globalAlpha = al; ctx.lineWidth = 1.5; ctx.beginPath(); ctx.moveTo(p.x, p.y); ctx.lineTo(p.x - p.vx * 3, p.y - p.vy * 3); ctx.stroke(); }
    else if (p.k === 'smoke') { ctx.globalAlpha = al * .35; ctx.fillStyle = p.col; ctx.beginPath(); ctx.arc(p.x, p.y, p.s * (2.5 + (1 - al) * 4), 0, TAU); ctx.fill(); }
    else if (p.k === 'ember') { glow(p.x, p.y, 7, p.col, al); }
    else if (p.k === 'coin') { const w = Math.abs(Math.cos(p.sp + p.life * 14)); ctx.globalAlpha = Math.min(1, p.life * 2.5); ctx.fillStyle = 'rgba(0,0,0,.25)'; ctx.beginPath(); ctx.ellipse(p.x, p.y + 1, 3, 1.4, 0, 0, TAU); ctx.fill(); ctx.fillStyle = '#f0a23c'; ctx.beginPath(); ctx.ellipse(p.x, p.y - p.z, 3.2 * w + .6, 3.2, 0, 0, TAU); ctx.fill(); ctx.fillStyle = '#ffe08a'; ctx.fillRect(p.x - .6, p.y - p.z - 1.5, 1.2, 1.4); }
    else if (p.k === 'drip') { ctx.globalAlpha = al; ctx.fillStyle = p.col; ctx.beginPath(); ctx.arc(p.x, p.y, p.s * .9, 0, TAU); ctx.fill(); }
    else { ctx.globalAlpha = al; ctx.fillStyle = p.col; ctx.fillRect(p.x - p.s / 2, p.y - p.s / 2, p.s, p.s); }
  }
  ctx.globalAlpha = 1;
  const s = G.slash;
  if (s && s.kind === 'arc' && s.full) {
    const t = 1 - s.life / .16, R = Math.max(1, s.rad * .95), al = clamp(1 - t * .8, 0, 1), sweep = Math.min(1, t * 1.8) * TAU;
    ctx.fillStyle = 'rgba(255,238,190,' + al * .5 + ')';
    ctx.beginPath(); ctx.arc(s.x, s.y, R, s.a, s.a + sweep); ctx.arc(s.x, s.y, R * .45, s.a + sweep, s.a, true); ctx.closePath(); ctx.fill();
    ctx.strokeStyle = 'rgba(255,255,255,' + al + ')'; ctx.lineWidth = 2.4; ctx.beginPath(); ctx.arc(s.x, s.y, R, s.a, s.a + sweep); ctx.stroke();
  } else if (s && s.kind === 'arc') {
    const t = 1 - s.life / .16, h = s.a - 1.15 + 2.3 * Math.min(1, t * 1.6), tail = Math.max(s.a - 1.15, h - 1.3), R = Math.max(1, s.rad * .95), al = clamp(1 - t * .8, 0, 1);
    ctx.fillStyle = 'rgba(255,238,190,' + al * .75 + ')'; ctx.beginPath(); ctx.arc(s.x, s.y, R, tail, h); ctx.arc(s.x, s.y, R * .55, h, tail, true); ctx.closePath(); ctx.fill();
    ctx.strokeStyle = 'rgba(255,255,255,' + al + ')'; ctx.lineWidth = 2; ctx.beginPath(); ctx.arc(s.x, s.y, R, tail, h); ctx.stroke();
  } else if (s && s.kind === 'boom') {
    const t = clamp(1 - s.life / .22, 0, 1), R = Math.max(1, (s.rad || 60) * (.35 + .8 * t)), al = clamp(1 - t, 0, 1);
    const g = ctx.createRadialGradient(s.x, s.y, 0, s.x, s.y, R); g.addColorStop(0, 'rgba(255,240,200,' + al + ')'); g.addColorStop(.5, 'rgba(255,140,60,' + al * .6 + ')'); g.addColorStop(1, 'rgba(255,80,30,0)');
    ctx.fillStyle = g; ctx.beginPath(); ctx.arc(s.x, s.y, R, 0, TAU); ctx.fill();
    ctx.strokeStyle = 'rgba(255,200,120,' + al + ')'; ctx.lineWidth = 3 * al + 1; ctx.beginPath(); ctx.arc(s.x, s.y, R, 0, TAU); ctx.stroke();
  }
  for (const f of G.fxs) { if (f.kind === 'warn') drawWarn(f); else if (f.kind === 'shock') drawShock(f); else if (f.kind === 'crit') drawCrit(f); else if (f.kind === 'hit') { if (f.t < .2) { const q = f.t / .2; ctx.strokeStyle = 'rgba(255,243,208,' + (1 - q) + ')'; ctx.lineWidth = 2 * (1 - q) + .5; ctx.beginPath(); ctx.arc(f.x, f.y, 6 + q * 16, 0, TAU); ctx.stroke(); } } else drawChestFx(f); }
}


/* ================= sprite engine: renders of Kenney CC0 3D models (see sprites.js) ================= */
const SPR = {}, SK = 1 / 3;
let _pxu = 96;
function sprOk(k) { const s = SPR[k]; return !!(s && s.ok); }
const TEXI = {}, texOk = k => !!(TEXI[k] && TEXI[k].ok);
function loadSprites() {
  if (typeof SPR_META === 'undefined' || typeof Image === 'undefined') return;
  const MS = Object.assign({}, SPR_META, typeof SPR_META2 !== 'undefined' ? SPR_META2 : {}), SS = Object.assign({}, SPR_SRC, typeof SPR_SRC2 !== 'undefined' ? SPR_SRC2 : {});
  for (const k in MS) {
    const s = { m: MS[k], img: new Image(), ok: false, src: null, f: 1 };
    s.img.onload = () => { s.ok = true; s.src = s.img; s.f = 1; sprScale(s); if (typeof onSprReady === 'function') onSprReady(); };
    s.img.src = SS[k]; SPR[k] = s;
  }
  if (typeof TEX_SRC !== 'undefined') for (const k in TEX_SRC) { const t = { img: new Image(), ok: false }; t.img.onload = () => { t.ok = true; G.mapVer = (G.mapVer || 0) + 1; }; t.img.src = TEX_SRC[k]; TEXI[k] = t; }
}
function sprScale(s) {
  if (!s.ok) return;
  let f = 1; const d = 96 / _pxu; while (d * f > 1.45 && f > .25) f *= .5;
  if (Math.abs(f - s.f) < 1e-6) return;
  let cur = s.img, cf = 1;
  while (cf > f + 1e-6) {
    const nf = cf * .5, c = document.createElement('canvas'); c.width = Math.round(s.img.width * nf); c.height = Math.round(s.img.height * nf);
    const g = c.getContext('2d'); g.imageSmoothingQuality = 'high'; g.drawImage(cur, 0, 0, c.width, c.height); cur = c; cf = nf;
  }
  s.src = cur; s.f = cf;
}
function setSprDensity(pxu) { _pxu = pxu; for (const k in SPR) sprScale(SPR[k]); }
const dirIdx = a => (((Math.round((Math.PI / 2 - a) / (Math.PI / 4)) % 8) + 8) % 8);
const _tc = document.createElement('canvas'), _tx = _tc.getContext('2d');
const _rc = document.createElement('canvas'), _rx = _rc.getContext('2d');
const fitCv = (c, g, w, h) => { if (c.width !== w || c.height !== h) { c.width = w; c.height = h; } else g.clearRect(0, 0, w, h); };
function sprBlit(s, sx, sy, sw, sh, dx, dy, dw, dh, tint, ta) {
  const f = s.f;
  if (tint && ta > 0) {
    const w = Math.max(1, Math.round(sw * f)), h = Math.max(1, Math.round(sh * f)); fitCv(_tc, _tx, w, h);
    _tx.drawImage(s.src, sx * f, sy * f, sw * f, sh * f, 0, 0, w, h); _tx.globalCompositeOperation = 'source-atop'; _tx.globalAlpha = ta; _tx.fillStyle = tint; _tx.fillRect(0, 0, w, h); _tx.globalAlpha = 1; _tx.globalCompositeOperation = 'source-over';
    ctx.drawImage(_tc, 0, 0, w, h, dx, dy, dw, dh);
  } else ctx.drawImage(s.src, sx * f, sy * f, sw * f, sh * f, dx, dy, dw, dh);
}
/* flat silhouette of a frame, in one colour */
function sprSil(s, sx, sy, sw, sh, dx, dy, dw, dh, col, a) {
  const f = s.f, w = Math.max(1, Math.round(sw * f)), h = Math.max(1, Math.round(sh * f));
  fitCv(_rc, _rx, w, h);
  _rx.globalCompositeOperation = 'source-over';
  _rx.drawImage(s.src, sx * f, sy * f, sw * f, sh * f, 0, 0, w, h);
  _rx.globalCompositeOperation = 'source-in'; _rx.fillStyle = col; _rx.fillRect(0, 0, w, h);
  _rx.globalCompositeOperation = 'source-over';
  const pa = ctx.globalAlpha; ctx.globalAlpha = pa * clamp(a, 0, 1);
  ctx.drawImage(_rc, 0, 0, w, h, dx, dy, dw, dh);
  ctx.globalAlpha = pa;
}
/* Which way the nearest real light falls, and how hard. Valve's TF2 work found
   a rim read separates a figure from the background better than an outline. */
function lightAt(x, y) {
  let bd = 1e9, bx = 0, by = -1, col = null;
  const test = (lx, ly, c) => { const d = Math.hypot(lx - x, ly - y); if (d > 300 || d >= bd) return; bd = d; bx = lx - x; by = ly - y; col = c; };
  for (const t of G.torches) test(t.x, t.y + 10, '#ffcf8a');
  for (const p of G.props) if (p.lit) test(p.x, p.y - 4, '#ffb55a');
  for (const n of G.nests) if (n.hp > 0) test(n.x, n.y, '#ff7a5a');
  if (G.exit) test(G.exit.x, G.exit.y, '#9fdcff');
  const len = Math.hypot(bx, by) || 1, near = col ? clamp(1 - bd / 300, 0, 1) : 0;
  return { dx: bx / len, dy: by / len, col: col || ((G.zone || ZONES[0]).amb), a: .2 + near * .55 };
}
function entLight(e) {
  if (!e._lt || clock - e._lt > .12) { e._lt = clock; e._lr = lightAt(e.x, e.y); }
  return e._lr;
}
// draw one frame of an animated character; (x, fy) is where its feet land
function sprChar(key, x, fy, ang, kind, col, sc, tint, ta, rim) {
  const s = SPR[key]; if (!s || !s.ok) return false;
  const m = s.m, sz = m.sz; if (m[kind] == null) return false;
  const d = (kind === 'die' || kind === 'pick') ? 0 : dirIdx(ang), row = m[kind] + d, ay = kind === 'die' && m.dieAy ? m.dieAy : m.ay, k = SK * (sc || 1);
  const dx0 = x - m.ax * k, dy0 = fy - ay * k, dsz = sz * k;
  if (rim && rim.a > 0 && !reduceMotion) sprSil(s, col * sz, row * sz, sz, sz, dx0 + rim.dx, dy0 + rim.dy, dsz, dsz, rim.col, rim.a);
  sprBlit(s, col * sz, row * sz, sz, sz, dx0, dy0, dsz, dsz, tint, ta); return true;
}
function sprProp(name, x, fy, sc, tint, ta) {
  let s = SPR.props2; if (!(s && s.ok && s.m.frames[name])) s = SPR.props; if (!s || !s.ok) return false; const f = s.m.frames[name]; if (!f) return false; const k = SK * (sc || 1);
  sprBlit(s, f.x, f.y, f.w, f.h, x - f.ax * k, fy - f.ay * k, f.w * k, f.h * k, tint, ta); return true;
}
loadSprites();

/* ---------- heroes ---------- */
function weaponOverlay(P, x, y, sw) {
  const c = P.cls, a = P.aim, ca = Math.cos(a), sa = Math.sin(a), hx = x + ca * 10, hy = y + sa * 8 + 2, hurt = P.hurt > 0;
  ctx.save(); ctx.lineCap = 'round';
  if (c.atk === 'melee') {
    const wa = sw > 0 ? a - 1.2 + (1 - sw) * 2.4 : a + .3, sx = x + Math.cos(a + 1.5) * 9, sy = y + Math.sin(a + 1.5) * 7 + 3;
    ctx.fillStyle = '#6e7d97'; ctx.beginPath(); ctx.arc(sx, sy, 6, 0, TAU); ctx.fill(); ctx.fillStyle = '#e7b04a'; ctx.beginPath(); ctx.arc(sx, sy, 3.2, 0, TAU); ctx.fill(); ctx.fillStyle = '#c9d2e0'; ctx.beginPath(); ctx.arc(sx, sy, 1.4, 0, TAU); ctx.fill();
    const bx = hx, by = hy, ex = bx + Math.cos(wa) * 17, ey = by + Math.sin(wa) * 15;
    ctx.strokeStyle = '#eef3fa'; ctx.lineWidth = 2.6; ctx.beginPath(); ctx.moveTo(bx, by); ctx.lineTo(ex, ey); ctx.stroke();
    ctx.strokeStyle = '#e7b04a'; ctx.lineWidth = 2.4; ctx.beginPath(); ctx.moveTo(bx + Math.cos(wa + 1.57) * 4, by + Math.sin(wa + 1.57) * 4); ctx.lineTo(bx - Math.cos(wa + 1.57) * 4, by - Math.sin(wa + 1.57) * 4); ctx.stroke();
  } else if (c.atk === 'fire') {
    const tx = hx + ca * 14, ty = hy + sa * 12, pul = .5 + .5 * Math.sin(clock * 8) + (sw > 0 ? 1 : 0);
    ctx.strokeStyle = '#7a5a34'; ctx.lineWidth = 2.4; ctx.beginPath(); ctx.moveTo(hx - ca * 7, hy - sa * 6); ctx.lineTo(tx, ty); ctx.stroke();
    glow(tx, ty, 14 + pul * 6, '#ff8a3a', .55); ctx.fillStyle = '#ffd08a'; ctx.beginPath(); ctx.arc(tx, ty, 3.2, 0, TAU); ctx.fill(); ctx.fillStyle = '#fff6df'; ctx.beginPath(); ctx.arc(tx - .6, ty - .6, 1.4, 0, TAU); ctx.fill();
  } else if (c.atk === 'dagger') {
    const ext = sw > 0 ? 5 : 0;
    for (const sd of [-1, 1]) {
      const px = x + Math.cos(a + sd * 1.15) * 9, py = y + Math.sin(a + sd * 1.15) * 7 + 3;
      ctx.strokeStyle = '#dfe6f2'; ctx.lineWidth = 2.2; ctx.beginPath(); ctx.moveTo(px, py); ctx.lineTo(px + ca * (8 + ext), py + sa * (7 + ext)); ctx.stroke();
      ctx.strokeStyle = '#6a4a2a'; ctx.lineWidth = 2.6; ctx.beginPath(); ctx.moveTo(px, py); ctx.lineTo(px - ca * 3, py - sa * 3); ctx.stroke();
    }
  } else if (c.atk === 'arrow') {
    const bx = hx + ca * 2, by = hy + sa * 2, r = 10;
    ctx.strokeStyle = '#9a6a34'; ctx.lineWidth = 2.6; ctx.beginPath(); ctx.arc(bx - ca * 5, by - sa * 5, r, a - 1.05, a + 1.05); ctx.stroke();
    const e1x = bx - ca * 5 + Math.cos(a - 1.05) * r, e1y = by - sa * 5 + Math.sin(a - 1.05) * r, e2x = bx - ca * 5 + Math.cos(a + 1.05) * r, e2y = by - sa * 5 + Math.sin(a + 1.05) * r;
    const pull = sw > 0 ? 0 : 3.5; ctx.strokeStyle = '#efe9d6'; ctx.lineWidth = 1; ctx.beginPath(); ctx.moveTo(e1x, e1y); ctx.lineTo(bx - ca * (5 + pull), by - sa * (5 + pull)); ctx.lineTo(e2x, e2y); ctx.stroke();
    if (sw <= 0) { ctx.strokeStyle = '#e9e1c8'; ctx.lineWidth = 1.6; ctx.beginPath(); ctx.moveTo(bx - ca * (5 + pull), by - sa * (5 + pull)); ctx.lineTo(bx + ca * 9, by + sa * 9); ctx.stroke(); }
  }
  ctx.restore();
}
function drawPlayer(P) {
  const c = P.cls, x = P.x, y = P.y, key = 'hero_' + c.key;
  if (!sprOk(key)) return drawPlayerOld(P);
  const M = SPR[key].m, hsc = M.idle != null ? 1.8 : 1.3;
  if (P.down) {
    const pu = .5 + .5 * Math.sin(clock * 3);
    shadow(x, y + 9, 12, 5); glow(x, y + 4, 26 + pu * 6, '#d9534f', .1 + pu * .1); ctx.globalAlpha = .85; sprChar(key, x, y + 10, 0, 'die', 3, 1.3, '#2a3040', .35); ctx.globalAlpha = 1;
    ctx.strokeStyle = c.col; ctx.lineWidth = 2; ctx.beginPath(); ctx.arc(x, y, 17, -Math.PI / 2, -Math.PI / 2 + TAU * P.rev / 1.5); ctx.stroke();
    ctx.fillStyle = C.bone; ctx.font = '600 10px "Spline Sans Mono",monospace'; ctx.textAlign = 'center'; ctx.fillText('REVIVE', x, y - 22);
    return;
  }
  const mv = Math.min(1, Math.hypot(x - (P.lx ?? x), y - (P.ly ?? y)) * 1.4); P.lx = x; P.ly = y;
  const cheer = P.cheer > 0, sw = P.swing > 0 ? P.swing / (P.swm || .18) : 0, up = !cheer && Math.sin(P.aim) < -.35;
  const ph = (P.walk || 0) / .09 / 90 * TAU, bob = Math.abs(Math.sin(ph)) * 1.4 * mv;
  let rot = Math.sin(ph) * .05 * mv, sx = 1, sy = 1, ox = 0, oy = 0, lift = 0, spin = 0;
  if (mv < .12 && sw <= 0 && !cheer) { const br = Math.sin(clock * 2.4 + P.idx * 1.7); sy *= 1 + br * .02; sx *= 1 - br * .01; }
  const ca = Math.cos(P.aim), sa = Math.sin(P.aim);
  if (sw > 0) { const q = Math.sin((1 - sw) * Math.PI), k = c.atk === 'melee' || c.atk === 'dagger' ? 5 * q : c.atk === 'fire' ? -3.5 * sw : -2.5 * sw; ox += ca * k; oy += sa * k * .7; if (k > 0) { sx *= 1 + .05 * q; sy *= 1 - .04 * q; } }
  if (P.hurt > 0) { const q = P.hurt / .25; sx *= 1 + .12 * q; sy *= 1 - .1 * q; }
  const dr = P.drink > 0 ? 1 - P.drink / .75 : -1;
  if (dr >= 0) { const s = Math.sin(dr * Math.PI); lift += s * 3; sy *= 1 + s * .05; }
  if (P.rise > 0) { const q = P.rise / .75; rot -= q * 1.2; sy *= 1 - q * .3; sx *= 1 + q * .1; }
  if (cheer) lift += Math.abs(Math.sin(clock * 10 + P.idx * 2)) * 7;
  const dashing = P.dash > 0, dq = dashing ? clamp(1 - P.dash / .16, 0, 1) : 0, rolling = dashing && M.roll != null;
  if (dashing && !rolling) { spin = dq * TAU * (Math.cos(P.face || 0) >= 0 ? 1 : -1); sy *= .92; }
  const gh = P.gh || (P.gh = []);
  if (dashing && !(gh.length && clock - gh[gh.length - 1].t < .025)) gh.push({ x, y, a: P.face || 0, t: clock });
  while (gh.length && clock - gh[0].t > .25) gh.shift();
  for (const g of gh) { ctx.globalAlpha = (1 - (clock - g.t) / .25) * .4; sprChar(key, g.x, g.y + 10, g.a, 'walk', 1, hsc, c.col, .75); }
  ctx.globalAlpha = 1;
  const blink = P.inv > 0 && P.dash <= 0 && !(P.rise > 0) && !cheer && Math.floor(clock * 20) % 2, A = blink ? .45 : 1;
  ctx.globalAlpha = A; shadowL(x, y + 10, 12 - lift * .5, 5 - lift * .2, .4, entLight(P)); glow(x, y, 32, c.col, .16);
  ctx.strokeStyle = c.col; ctx.globalAlpha = A * .55; ctx.lineWidth = 1.5; ctx.beginPath(); ctx.ellipse(x, y + 10, 11, 4.6, 0, 0, TAU); ctx.stroke(); ctx.globalAlpha = A;
  const aim0 = P.aim, swO = cheer ? .5 + .5 * Math.sin(clock * 16) : sw; if (cheer) P.aim = Math.PI / 2;
  const wx = x + ox, wy = y + oy - bob - lift;
  if (up && !spin && !rolling) weaponOverlay(P, wx, wy, swO);
  const atkFrame = cheer ? Math.floor(clock * 9) % 6 : Math.min(5, Math.floor((1 - sw) * 6));
  let kind = 'walk', col = mv > .12 ? Math.floor(((P.walk || 0) / .09) / 15) % 6 : 0, fang = P.aim;
  if (sw > 0 || cheer) { kind = 'atk'; col = atkFrame; }
  else if (mv <= .12 && M.idle != null) { kind = 'idle'; col = Math.floor(clock * 5 + P.idx * 2) % 4; }
  if (P.hurt > 0 && M.hit != null) { kind = 'hit'; col = P.hurt > .12 ? 0 : 1; }
  if (dr >= 0 && M.pick != null) { kind = 'pick'; col = Math.min(3, Math.floor(dr * 4)); }
  if (rolling) { kind = 'roll'; col = Math.min(5, Math.floor(dq * 6)); fang = P.face || 0; }
  const PLT = entLight(P);
  ctx.save(); ctx.translate(x + ox, y + 10 - bob - lift + oy); ctx.rotate(rot);
  if (spin) { ctx.translate(0, -14); ctx.rotate(spin); ctx.translate(0, 14); }
  ctx.scale(sx, sy);
  sprChar(key, 0, 0, fang, kind, col, hsc, P.hurt > 0 ? '#ff2a2a' : null, .5, { dx: PLT.dx * 2.6, dy: PLT.dy * 2.6 - .8, col: PLT.col, a: PLT.a });
  ctx.restore();
  if (!up && !spin && !rolling) weaponOverlay(P, wx, wy, swO);
  if (sw > .6 && (c.atk === 'fire' || c.atk === 'arrow' || c.atk === 'dagger')) glow(x + ca * 22, y + sa * 16, 22, c.col, .7 * (sw - .6) / .4);
  P.aim = aim0; ctx.globalAlpha = 1;
  if (dr >= 0) { const s = Math.sin(dr * Math.PI); glow(x, y, 34, '#9bd16a', .35 * s); ctx.globalAlpha = s; sprProp('potion', x, y - 24 - dr * 8, 1.7); ctx.globalAlpha = 1; }
  if (P.rise > 0) { const q = P.rise / .75; glow(x, y, 50 * (2 - q), '#9bd16a', .5 * q); }
  if (G.co) { ctx.fillStyle = c.col; ctx.font = '600 10px "Spline Sans Mono",monospace'; ctx.textAlign = 'center'; ctx.fillText('P' + (P.idx + 1), x, y - 40 - lift); }
}

/* ---------- monsters ---------- */
const SPRFOE = {
  gloam_pug: { key: 'foe_puglin', fy: 8, bar: -36, sc: 1.2 }, hound_imp: { key: 'foe_imp', fy: 8, bar: -46, sc: 1.25 },
  wisp: { key: 'foe_ghost', fy: 8, bar: -41, sc: 1.3 }, bonewalker: { key: 'foe_skeleton', fy: 9, bar: -40, sc: 1.3 }, brute: { key: 'foe_orc', fy: 12, bar: -49, sc: 1.2 },
  hound: { key: 'foe_zombie', fy: 8, bar: -42, sc: 1.3 }, warden: { key: 'boss_vampire', fy: 18, bar: -88, sc: 1.2 },
  bloat: { key: 'foe_puglin', fy: 9, bar: -50, sc: 1.8 },
  thief: { key: 'npc_keeper', fy: 8, bar: -44, sc: 1.3 },
  reaper: { key: 'foe_ghost', fy: 10, bar: -64, sc: 2.2 },
  warden_caller: { key: 'foe_skeleton', fy: 14, bar: -78, sc: 1.95 },
  warden_maw: { key: 'foe_orc', fy: 16, bar: -80, sc: 1.95 }
};
function foeDef(type, kind) {
  if (type === 'warden') return SPRFOE[kind === 'caller' ? 'warden_caller' : kind === 'maw' ? 'warden_maw' : 'warden'];
  if (type === 'gloam' && sprOk('foe_puglin')) return SPRFOE.gloam_pug;
  if (type === 'hound' && G.zone.id >= 1 && sprOk('foe_imp')) return SPRFOE.hound_imp;
  return SPRFOE[type];
}
const r6 = e => e.r;
function foeAdorn(e, S, x, y) {
  const r = e.r, f = e.face || 0, ca = Math.cos(f), sa = Math.sin(f);
  const by = y + S.fy - r * 1.8;
  ctx.save();
  if (e.type === 'bloat') {
    /* a swollen sac and horns: never mistake it for the gloam it shares a rig with */
    const sw = e.fuse > 0 ? 1 + (1 - e.fuse / .6) * .55 : 1;
    ctx.fillStyle = e.fuse > 0 ? 'rgba(226,255,176,.9)' : 'rgba(126,191,74,.85)';
    for (const o of [[-.82, .1, .46], [.82, .16, .42], [0, -.52, .4]]) {
      ctx.beginPath(); ctx.ellipse(x + o[0] * r * sw, by + o[1] * r * sw, o[2] * r * sw, o[2] * r * .86 * sw, 0, 0, TAU); ctx.fill();
    }
    ctx.fillStyle = '#4e7128';
    for (const sg of [-1, 1]) { ctx.beginPath(); ctx.moveTo(x + sg * r * .42, by - r * .55); ctx.lineTo(x + sg * r * .78, by - r * 1.4); ctx.lineTo(x + sg * r * .12, by - r * .68); ctx.fill(); }
  } else if (e.type === 'reaper') {
    /* a scythe and a torn hood, so Death never reads as a wisp */
    const sg = ca >= 0 ? 1 : -1, hx = x + sg * r * 1.25, hy = y + S.fy - r * .4;
    ctx.strokeStyle = 'rgba(60,64,78,.95)'; ctx.lineWidth = 2.6; ctx.lineCap = 'round';
    ctx.beginPath(); ctx.moveTo(hx, hy); ctx.lineTo(hx - sg * r * .18, hy - r * 3.1); ctx.stroke();
    ctx.strokeStyle = 'rgba(226,232,245,.95)'; ctx.lineWidth = 3.4;
    ctx.beginPath(); ctx.arc(hx - sg * r * .18, hy - r * 3.05, r * 1.05, sg > 0 ? -1.9 : -1.25, sg > 0 ? -.05 : .8, sg < 0);
    ctx.stroke(); ctx.lineCap = 'butt';
    ctx.fillStyle = 'rgba(214,222,240,.75)';
    for (const s2 of [-1, 1]) { ctx.beginPath(); ctx.moveTo(x + s2 * r * .5, by - r * .3); ctx.lineTo(x + s2 * r * .78, by - r * 1.35); ctx.lineTo(x + s2 * r * .06, by - r * .5); ctx.fill(); }
  } else if (e.type === 'thief') {
    /* the swag sack rides on its back, and swells once it has your gold */
    const bx = x - ca * r * 1.05, byy = y + S.fy - r * 1.5, s2 = e.loot > 0 ? 1.25 : .9;
    ctx.fillStyle = e.loot > 0 ? 'rgba(220,168,66,.95)' : 'rgba(120,98,62,.9)';
    ctx.beginPath(); ctx.ellipse(bx, byy, r * .52 * s2, r * .6 * s2, 0, 0, TAU); ctx.fill();
    ctx.strokeStyle = 'rgba(60,46,26,.9)'; ctx.lineWidth = 1.6;
    ctx.beginPath(); ctx.moveTo(bx - r * .3, byy - r * .5); ctx.lineTo(bx + r * .3, byy - r * .5); ctx.stroke();
  } else if (e.boss && e.kind === 'caller') {
    /* a back banner, the classic elite silhouette tell */
    const w = r * .72, h = r * 3.3, bxx = x - ca * r * .5, byy = y + S.fy - r * 2;
    ctx.fillStyle = 'rgba(70,58,98,.92)';
    ctx.beginPath(); ctx.moveTo(bxx - w, byy); ctx.lineTo(bxx + w, byy); ctx.lineTo(bxx + w, byy - h);
    ctx.lineTo(bxx, byy - h * .88); ctx.lineTo(bxx - w, byy - h); ctx.fill();
    ctx.fillStyle = 'rgba(190,160,255,.8)';
    ctx.beginPath(); ctx.arc(bxx, byy - h * .62, r * .26, 0, TAU); ctx.fill();
    ctx.strokeStyle = 'rgba(40,34,56,.95)'; ctx.lineWidth = 2;
    ctx.beginPath(); ctx.moveTo(bxx, byy + r * .4); ctx.lineTo(bxx, byy - h); ctx.stroke();
  } else if (e.boss && e.kind === 'maw') {
    /* shoulder spines */
    ctx.fillStyle = 'rgba(206,110,52,.95)';
    for (const sg of [-1, 1]) for (let i = 0; i < 3; i++) {
      const px = x + sg * (r * .75 + i * r * .24), py = by + r * .18 - i * r * .1;
      ctx.beginPath(); ctx.moveTo(px - r * .16, py); ctx.lineTo(px + sg * r * .1, py - r * (.9 - i * .18)); ctx.lineTo(px + r * .16, py); ctx.fill();
    }
  } else if (e.boss) {
    /* a high collar for the Count */
    ctx.fillStyle = 'rgba(120,52,74,.92)';
    for (const sg of [-1, 1]) {
      ctx.beginPath(); ctx.moveTo(x + sg * r * .36, by + r * .1);
      ctx.quadraticCurveTo(x + sg * r * 1.25, by - r * .5, x + sg * r * .85, by - r * 1.5);
      ctx.quadraticCurveTo(x + sg * r * .4, by - r * .7, x + sg * r * .2, by + r * .1); ctx.fill();
    }
  }
  ctx.restore();
}
function drawFoeSpr(e, mv) {
  const S = foeDef(e.type, e.kind), x = e.x, y = e.y, ghost = e.type === 'wisp', boss = e.boss;
  if (e.type === 'hound' && e.st === 'wind') {
    const p = Math.min(1, e.stt / .45); ctx.save(); ctx.translate(x, y); ctx.rotate(e.face || 0);
    ctx.strokeStyle = 'rgba(255,90,70,' + (.25 + p * .5) + ')'; ctx.lineWidth = 2 + p * 4; ctx.setLineDash([8, 6]); ctx.beginPath(); ctx.moveTo(14, 0); ctx.lineTo(150, 0); ctx.stroke(); ctx.setLineDash([]); ctx.restore();
  }
  if (boss) {
    if (e.st === 'slam') {
      const p = Math.min(1, e.stt / .9);
      ctx.fillStyle = 'rgba(255,70,50,' + (.08 + p * .12) + ')'; ctx.beginPath(); ctx.arc(x, y, 120, 0, TAU); ctx.fill();
      ctx.strokeStyle = 'rgba(255,90,70,' + (.4 + p * .5) + ')'; ctx.lineWidth = 2; ctx.beginPath(); ctx.arc(x, y, 120, 0, TAU); ctx.stroke();
      ctx.fillStyle = 'rgba(255,90,70,' + (.16 + p * .25) + ')'; ctx.beginPath(); ctx.arc(x, y, 120 * p, 0, TAU); ctx.fill();
    }
    if ((e.st === 'charge' || e.st === 'rampage') && (e.stt % (e.st === 'rampage' ? .7 : 1.42)) < (e.st === 'rampage' ? .3 : .72)) {
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
    if (e.st === 'raise') glow(x, y, 110, '#d8d2bd', .25 + Math.sin(e.t * 22) * .12);
    if (e.st === 'burst') glow(x, y, 60 + Math.sin(e.t * 30) * 6, '#ff5a46', .45);
    if (e.st === 'summon') glow(x, y, 70, '#9a6bd6', .5);
    glow(x, y, 54, e.ph >= 2 ? '#ff4a3a' : ((BOSSES[e.kind] || BOSSES.count).glow || e.col), e.ph >= 2 ? .22 + Math.sin(e.t * 6) * .06 : .18);
  }
  if (e.type === 'bloat') {
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
  foeAdorn(e, S, x, y);
  if (e.elite && e.eaff && e.eaff.length) {
    const nm = e.eaff.map(id => { const a = EAFF.find(z => z.id === id); return a ? a.name : null; }).filter(Boolean).join(' \u00b7 ');
    ctx.fillStyle = '#ffd24a'; ctx.font = '600 9px "Spline Sans Mono",monospace'; ctx.textAlign = 'center';
    ctx.lineWidth = 3; ctx.strokeStyle = 'rgba(8,10,14,.85)';
    ctx.strokeText(nm, x, y + S.bar - 7); ctx.fillText(nm, x, y + S.bar - 7);
  }
  if (e.elite) {
    const pu = .5 + .5 * Math.sin(clock * 3.2 + e.t);
    glow(x, y - 4, e.r * 3.4, '#ffd24a', .13 + pu * .08);
    ctx.save(); ctx.strokeStyle = 'rgba(255,210,74,' + (.3 + pu * .3) + ')'; ctx.lineWidth = 1.6;
    ctx.beginPath(); ctx.ellipse(x, y + S.fy, e.r * 1.5, e.r * .62, 0, 0, TAU); ctx.stroke();
    ctx.globalAlpha = .35; ctx.beginPath(); ctx.ellipse(x, y + S.fy, e.r * 1.5 * (1 + pu * .2), e.r * .62 * (1 + pu * .2), 0, 0, TAU); ctx.stroke(); ctx.restore();
  }
  const bob = ghost ? Math.sin(e.t * 3) * 2.5 - 5 : 0;
  shadowL(x, y + S.fy + 1, e.r * (boss ? 1.15 : .95), e.r * .42, ghost ? .2 : .4, entLight(e));
  if (ghost) glow(x, y - 3, 32, e.col, .38);
  const col = (ghost || mv > .12) ? Math.floor((e.walk / .35) / (ghost ? 11 : boss ? 17 : 14)) % 6 : 0;
  let sx = 1, sy = 1;
  if (e.type === 'hound') { if (e.st === 'wind') { sy = .9; sx = 1.06; } else if (e.st === 'lunge') { sx = .94; sy = 1.1; } }
  if (boss && e.st === 'slam') { const p = Math.min(1, e.stt / .9); sy = 1 + p * .08; sx = 1 - p * .04; }
  let kk = 'walk', kc = col;
  if (SPR[S.key].m.atk != null && !boss) {
    if (e.type === 'hound' && e.st === 'wind') { kk = 'atk'; kc = 0; } else if (e.type === 'hound' && e.st === 'lunge') { kk = 'atk'; kc = 2; }
    else if (e.atk > 0) { kk = 'atk'; kc = Math.min(3, Math.floor((1 - e.atk / .3) * 4)); }
  }
  let rot = 0, ox = 0, oy = 0, fade = 1; const ph = (e.walk / .35) / 84 * TAU, fa = e.face || 0;
  if (mv > .12 && !ghost) { rot += Math.sin(ph) * .06; oy -= Math.abs(Math.sin(ph)) * 1.6; }
  else if (e.st === 'chase' || !e.st) { const br = Math.sin(e.t * 2.3 + x * .01); sy *= 1 + br * .03; sx *= 1 - br * .015; }
  if (e.fl > 0) { const q = e.fl / .2 * (boss ? .35 : 1); sx *= 1 + .18 * q; sy *= 1 - .14 * q; rot += Math.cos(e.fa || 0) * .28 * q; }
  if (e.type === 'bloat' && e.fuse > 0) { const f = 1 - e.fuse / .6; sx *= 1 + f * .42; sy *= 1 + f * .42; }
  /* idle sway, so a waiting monster is not a frozen one */
  if (mv <= .12 && !ghost && e.atk <= 0) { rot += Math.sin(e.t * 1.5 + e.x * .013) * .035; oy += Math.sin(e.t * 2.1 + e.y * .011) * .5; }
  /* flinch away from the blow, not just squash */
  if (e.fl > 0) { const q = e.fl / .2 * (boss ? .3 : 1); ox -= Math.cos(e.fa || 0) * 3.4 * q; oy -= Math.sin(e.fa || 0) * 2.6 * q; }
  /* bosses telegraph with posture as well as light */
  if (boss && e.st && e.st !== 'chase') {
    const dur = BOSS_DUR[e.st] || .6, p = Math.min(1, e.stt / dur);
    if (e.st === 'slam') { sy *= 1 - p * .12; sx *= 1 + p * .1; oy += p * r6(e) * .2; }
    else if (e.st === 'volley') { rot -= .16 * p; ox -= Math.cos(e.face || 0) * 4 * p; }
    else if (e.st === 'raise') { sy *= 1 + p * .14; sx *= 1 - p * .05; oy -= p * 4; }
    else if (e.st === 'blink') { const q = Math.min(1, p * 1.6); sx *= 1 - q * .55; sy *= 1 + q * .35; }
    else if (e.st === 'quake') { sy *= 1 + p * .1; sx *= 1 - p * .06; }
    else if (e.st === 'charge' || e.st === 'rampage') {
      const seg = e.st === 'rampage' ? .7 : 1.42, w = e.st === 'rampage' ? .26 : .68, q = Math.min(1, (e.stt % seg) / w);
      if ((e.stt % seg) < w) { ox -= Math.cos(e.ca != null ? e.ca : 0) * 6 * q; sx *= 1 - q * .08; sy *= 1 + q * .1; }
      else { sx *= 1.1; sy *= .94; }
    }
  }
  if (e.atk > 0 && !boss && SPR[S.key].m.atk == null) { const t = 1 - e.atk / .3; if (t < .4) { const w = t / .4; ox -= Math.cos(fa) * 4 * w; oy -= Math.sin(fa) * 3 * w; sy *= 1 + .05 * w; } else { const s2 = Math.sin((t - .4) / .6 * Math.PI); ox += Math.cos(fa) * 9 * s2; oy += Math.sin(fa) * 7 * s2; sx *= 1 + .08 * s2; sy *= 1 - .06 * s2; } }
  if (e.age < .45) {
    const p = e.age / .45, c1 = 1.70158, eo = 1 + (c1 + 1) * Math.pow(p - 1, 3) + c1 * Math.pow(p - 1, 2);
    sx *= Math.max(.05, eo); sy *= Math.max(.05, eo); fade = Math.min(1, p * 2.2);
    ctx.globalAlpha = (1 - p) * .7; ctx.strokeStyle = e.col; ctx.lineWidth = 2; ctx.beginPath(); ctx.ellipse(x, y + S.fy, e.r * (.6 + p * 1.8), e.r * (.6 + p * 1.8) * .45, 0, 0, TAU); ctx.stroke(); ctx.globalAlpha = 1;
  }
  let tint = null, ta = .85;
  if (e.imp > 0) { tint = '#ffffff'; ta = 1; }
  else if (e.flash > 0) tint = '#ffffff';
  else if (e.type === 'reaper') { tint = '#eef2ff'; ta = .55; }
  else if (e.type === 'thief') { tint = '#e8c877'; ta = .45; }
  else if (e.type === 'bloat') { tint = e.fuse > 0 ? '#eaffc4' : '#7fbf4a'; ta = e.fuse > 0 ? .72 : .5; }
  else if (e.chill > 0) { tint = '#9fd8ff'; ta = .5; }
  else if (e.type === 'gloam') { tint = '#9a6bd6'; ta = .5; }   /* or it reads as a small bloat */
  else if (e.type === 'hound') { tint = '#c4622a'; ta = .55; }  /* warm, against the cool floors */
  else if (e.elite) { tint = '#ffd98a'; ta = .3; }
  const LT = entLight(e), rimS = 2.9 + (boss ? 1.8 : 0);
  const rim = { dx: LT.dx * rimS, dy: LT.dy * rimS - .8, col: LT.col, a: LT.a * (ghost ? .5 : 1) };
  ctx.save(); ctx.translate(x + ox, y + S.fy + bob + oy); ctx.rotate(rot); ctx.scale(sx, sy); ctx.globalAlpha = fade * (ghost ? .92 : 1);
  sprChar(S.key, 0, 0, e.face || 0, kk, kc, S.sc, tint, ta, rim);
  if (boss) { ctx.globalCompositeOperation = 'lighter'; ctx.globalAlpha = .22; sprChar(S.key, 0, 0, e.face || 0, 'walk', col, S.sc); ctx.globalCompositeOperation = 'source-over'; }
  ctx.restore();
}
function drawDying(d) {
  const S = foeDef(d.type, d.kind); if (!S || !sprOk(S.key)) return drawDyingOld(d);
  const p = d.t / .5, a = 1 - p;
  ctx.save(); ctx.translate(d.x, d.y);
  ctx.strokeStyle = 'rgba(255,255,255,' + a * .8 + ')'; ctx.lineWidth = 2 * a + .5; ctx.beginPath(); ctx.arc(0, 0, d.r * (1 + p * 2.2), 0, TAU); ctx.stroke(); ctx.restore();
  shadow(d.x, d.y + S.fy + 1, d.r, d.r * .4, .3 * a);
  const pop = 1 + Math.sin(Math.min(1, p * 2.5) * Math.PI) * .12; ctx.save(); ctx.translate(d.x, d.y + S.fy); ctx.scale(pop, 2 - pop); ctx.translate(-d.x, -(d.y + S.fy)); ctx.globalAlpha = p < .55 ? 1 : Math.max(0, (1 - p) / .45); sprChar(S.key, d.x, d.y + S.fy, 0, 'die', Math.min(3, Math.floor(p * 4)), S.sc, p < .2 ? '#ffffff' : null, .8); ctx.globalAlpha = 1; ctx.restore();
}

/* ---------- items, crypts, stairs, decor ---------- */
const hexA = (h, a) => { const n = parseInt(h.slice(1), 16); return 'rgba(' + (n >> 16) + ',' + ((n >> 8) & 255) + ',' + (n & 255) + ',' + a + ')'; };
function drawShrine(it) {
  const sh = it.sh, col = shrineCol(sh), pu = .5 + .5 * Math.sin(clock * 1.7 + it.t);
  const mys = sh.kind === 'mystery', want = sh.kind === 'pact';
  /* a ring burnt into the floor: this is what you see from across a hall */
  ctx.save();
  ctx.globalAlpha = .5 + pu * .3;
  ctx.strokeStyle = hexA(col, .8); ctx.lineWidth = 2.4;
  ctx.beginPath(); ctx.ellipse(it.x, it.y + 11, 34, 15, 0, 0, TAU); ctx.stroke();
  ctx.globalAlpha = .22 + pu * .16;
  ctx.strokeStyle = hexA(col, .6); ctx.lineWidth = 1.3;
  ctx.beginPath(); ctx.ellipse(it.x, it.y + 11, 44 + pu * 5, 20 + pu * 2, 0, 0, TAU); ctx.stroke();
  const fg = ctx.createRadialGradient(it.x, it.y + 11, 1, it.x, it.y + 11, Math.max(2, 40));
  fg.addColorStop(0, hexA(col, .3 + pu * .12)); fg.addColorStop(1, hexA(col, 0));
  ctx.fillStyle = fg; ctx.globalAlpha = 1;
  ctx.beginPath(); ctx.ellipse(it.x, it.y + 11, 42, 19, 0, 0, TAU); ctx.fill();
  ctx.restore();
  /* and a column of light above it, so it reads once you are close */
  const h = 96;
  const g = ctx.createLinearGradient(it.x, it.y - h, it.x, it.y + 8);
  g.addColorStop(0, hexA(col, 0)); g.addColorStop(.6, hexA(col, .16 + pu * .12)); g.addColorStop(1, hexA(col, .44 + pu * .16));
  ctx.fillStyle = g; ctx.fillRect(it.x - 17, it.y - h, 34, h + 8);
  glow(it.x, it.y - 4, 52 + pu * 12, col, .42 + pu * .2);
  shadow(it.x, it.y + 11, 15, 6, .36);
  if (!sprProp('altar', it.x, it.y + 11, 1.38, col, .3 + pu * .14)) {
    ctx.fillStyle = '#4a4740'; ctx.fillRect(it.x - 14, it.y - 12, 28, 24);
    ctx.fillStyle = hexA(col, .75); ctx.fillRect(it.x - 11, it.y - 17, 22, 6);
  }
  /* motes rise from a gift, and circle a bargain like flies */
  const n = mys ? 5 : 4;
  for (let i = 0; i < n; i++) {
    const a = clock * (want ? -1.5 : .9) + i * (TAU / n);
    const rr = want ? 13 + Math.abs(Math.sin(clock * 1.9 + i)) * 7 : 11;
    const ry = want ? Math.sin(a) * rr * .4 : -(((clock * 26 + i * 37) % 54));
    ctx.fillStyle = hexA(col, want ? .9 : .5 + pu * .4);
    ctx.fillRect(it.x + Math.cos(a) * rr, it.y - 8 + ry, 2, mys ? 3 : 2);
  }
  if (mys) {
    ctx.fillStyle = hexA(col, .55 + pu * .35); ctx.font = 'bold 15px ui-monospace, monospace';
    ctx.textAlign = 'center'; ctx.fillText('?', it.x, it.y - 30 - pu * 3); ctx.textAlign = 'left';
  }
}
function drawGear(it) {
  const o = it.item, b = Math.sin(it.t * 3) * 1.8, cursed = o.rar === 'cursed';
  const rank = cursed ? 1 : o.rar === 'fabled' ? 3 : o.rar === 'rare' ? 2 : 1;
  /* each rarity's beam behaves differently, so the tier reads without colour */
  const pu = cursed ? .5 + .5 * Math.sin(clock * 5.5 + it.t)
    : rank >= 3 ? .62 + .38 * Math.sin(clock * 2.2 + it.t)
    : rank === 2 ? .5 + .5 * Math.sin(clock * 1.5 + it.t) : .55;
  const h = 70 + rank * 22, wdt = 6 + rank * 2.5;
  const g = ctx.createLinearGradient(it.x, it.y - h, it.x, it.y + 8);
  g.addColorStop(0, hexA(o.col, 0));
  g.addColorStop(.7, hexA(o.col, (cursed ? .1 : .14) + pu * .1));
  g.addColorStop(1, hexA(o.col, (cursed ? .3 : .4) + pu * .14));
  ctx.fillStyle = g; ctx.fillRect(it.x - wdt, it.y - h, wdt * 2, h + 8);
  if (rank >= 3) {
    /* a slow turning shaft for the best things */
    ctx.save(); ctx.translate(it.x, it.y); ctx.globalAlpha = .16 + pu * .12;
    for (let i = 0; i < 3; i++) {
      const a = clock * .5 + i * (TAU / 3), w2 = Math.abs(Math.cos(a)) * wdt * 1.5 + 1;
      ctx.fillStyle = hexA(o.col, .55); ctx.fillRect(-w2, -h, w2 * 2, h);
    }
    ctx.restore(); ctx.globalAlpha = 1;
  }
  if (cursed) { ctx.globalAlpha = .22 + pu * .2; ctx.fillStyle = '#1a0a10'; ctx.beginPath(); ctx.ellipse(it.x, it.y + 4, 24, 11, 0, 0, TAU); ctx.fill(); ctx.globalAlpha = 1; }
  glow(it.x, it.y, 28 + rank * 7, o.col, (cursed ? .3 : .38) + pu * .18); shadow(it.x, it.y + 9, 8, 3, .32);
  const sp = o.slot === 'weapon' ? 'sword' : o.slot === 'armour' ? 'shield' : 'p_pouch';
  if (!sprProp(sp, it.x, it.y + 11 + b, 1.5)) {
    ctx.fillStyle = o.col; ctx.beginPath(); ctx.moveTo(it.x, it.y - 7 + b); ctx.lineTo(it.x + 6, it.y + b); ctx.lineTo(it.x, it.y + 7 + b); ctx.lineTo(it.x - 6, it.y + b); ctx.fill();
  }
  /* motes fall inward on good loot, scatter outward on cursed */
  const n = 2 + rank;
  for (let i = 0; i < n; i++) {
    const a = clock * (cursed ? -2.4 : 1.6) + i * (TAU / n);
    const rr = cursed ? 9 + Math.abs(Math.sin(clock * 2 + i)) * 13 : 15 - Math.abs(Math.sin(clock * 1.7 + i)) * 9;
    ctx.fillStyle = hexA(o.col, .85);
    ctx.fillRect(it.x + Math.cos(a) * rr, it.y - 12 + Math.sin(a) * rr * .45 - (cursed ? 0 : Math.abs(Math.sin(clock * 2.4 + i)) * 7), 2, 2);
  }
}
function drawItem(it) {
  if (it.kind === 'gear') return drawGear(it);
  if (it.kind === 'shrine') return drawShrine(it);
  if (!sprOk('props') || it.kind === 'gem' || it.kind === 'food') return drawItemOld(it);
  const b = Math.sin(it.t * 4) * 2;
  if (it.kind === 'gold') {
    /* it.t seeds the phase so a scattered hoard does not turn in lockstep */
    const fr = Math.floor((clock * 9 + it.t * 5) % 8);
    const lift = Math.abs(Math.sin(clock * 2.4 + it.t)) * 2.5;
    glow(it.x, it.y, 18, C.amber, .4 + Math.sin(clock * 3 + it.t) * .12);
    shadow(it.x, it.y + 8, 5 - lift * .4, 2, .3);
    if (!sprProp('coin_' + fr, it.x, it.y + 9 - lift, 1.05)) return drawItemOld(it);
    return;
  }
  if (it.kind === 'bomb') {
    const pu = .5 + .5 * Math.sin(clock * 3);
    glow(it.x, it.y, 30, '#b98cff', .4 + pu * .2); shadow(it.x, it.y + 9, 7, 2.4, .3);
    sprProp('potion', it.x, it.y + 10 + b, 1.9, '#b98cff', .55);
  }
  else if (it.kind === 'chest') {
    const s0 = it.big ? 2.25 : 1.7, pu = Math.sin(clock * 2.1 + it.t);
    /* breathing on the vertical only: it reads as something straining at the
       lid rather than the whole box pulsing */
    const sy = s0 * (1 + pu * .028), sx = s0 * (1 - pu * .018);
    glow(it.x, it.y, 40 * (it.big ? 1.2 : 1), C.amber, .4 + pu * .12);
    shadow(it.x, it.y + 9, 14 * (it.big ? 1.3 : 1), 5, .4);
    ctx.save(); ctx.translate(it.x, it.y + 10); ctx.scale(sx / s0, sy / s0); ctx.translate(-it.x, -(it.y + 10));
    sprProp('chest', it.x, it.y + 10, s0);
    ctx.restore();
    /* a glint that travels across the lid, so a chest catches the eye from
       across a room the way a lit altar does */
    const gt = (clock * .55 + it.t * .3) % 3.4;
    if (gt < .5) {
      const q = gt / .5, w = 13 * (it.big ? 1.3 : 1);
      ctx.save(); ctx.globalAlpha = Math.sin(q * Math.PI) * .75;
      ctx.fillStyle = '#fff6d8';
      ctx.fillRect(it.x - w + q * w * 2, it.y - 6 - (it.big ? 3 : 0), 2.5, 7);
      ctx.restore(); ctx.globalAlpha = 1;
    }
    ctx.fillStyle = 'rgba(255,230,150,.9)';
    for (let i = 0; i < 3; i++) { const a = clock * 2 + i * 2.1; ctx.fillRect(it.x + Math.cos(a) * 15 * s0 / 1.7, it.y - 10 + Math.sin(a) * 6 - Math.abs(Math.sin(clock * 3 + i)) * 6, 2, 2); }
  } else {
    glow(it.x, it.y, 26, C.amber, .6); shadow(it.x, it.y + 9, 8, 2.4, .3); sprProp('key', it.x, it.y + 11 + b, 1.5);
    ctx.fillStyle = 'rgba(255,255,255,' + (.4 + .4 * Math.sin(clock * 6)) + ')'; ctx.fillRect(it.x + 4, it.y - 7 + b, 2, 2);
  }
}
function drawChestFx(f) {
  const t = f.t / .8, al = 1 - t, s = f.big ? 1.25 : 1;
  const open = Math.min(1, t * 2.6), crack = Math.min(1, t * 7);
  /* a short hop, then squash on the landing: the lid coming up on its own
     reads as a door opening, the hop reads as something giving way */
  const hopT = Math.min(1, t * 3.2);
  const hop = Math.sin(hopT * Math.PI) * 9;
  const land = hopT >= 1 ? Math.max(0, 1 - (t * 3.2 - 1) * 3.4) : 0;
  const sq = 1 + land * .18, st = 1 - land * .14;
  ctx.save(); ctx.translate(f.x, f.y - hop); ctx.scale(s * sq, s * st); ctx.globalAlpha = Math.min(1, al * 1.6);
  /* light escapes the seam before the lid is up */
  if (crack < 1) { ctx.globalAlpha = Math.min(1, al * 1.6) * crack; ctx.fillStyle = 'rgba(255,245,205,.95)'; ctx.fillRect(-10, -8, 20, 3 + crack * 3); ctx.globalAlpha = Math.min(1, al * 1.6); }
  if (!sprProp('chest_open', 0, 10 / s * 1, 1.7)) { chestBody(f.big); ctx.save(); ctx.translate(0, -6); ctx.rotate(-open * 1.45); chestLid(f.big); ctx.restore(); }
  const gh = 46 + open * 26;
  const g = ctx.createLinearGradient(0, -6, 0, -gh); g.addColorStop(0, 'rgba(255,230,155,' + al * .9 + ')'); g.addColorStop(.55, 'rgba(255,225,140,' + al * .4 + ')'); g.addColorStop(1, 'rgba(255,225,140,0)');
  ctx.fillStyle = g; ctx.beginPath(); ctx.moveTo(-9, -6); ctx.lineTo(9, -6); ctx.lineTo(14 + open * 8, -gh); ctx.lineTo(-14 - open * 8, -gh); ctx.fill();
  /* a flare on the moment it gives */
  if (t < .3) { const q = 1 - t / .3; ctx.globalAlpha = q * .8; glow(0, -8, 38 * (1 + (1 - q)), '#fff3cc', .9); ctx.globalAlpha = 1; }
  ctx.restore();
}
function drawNest(n) {
  if (!sprOk('props')) return drawNestOld(n);
  const p = (Math.sin(clock * 4 + n.x) + 1) / 2, fl = n.flash > 0, x = n.x, y = n.y;
  shadow(x, y + 14, 22, 7, .45); glow(x, y, 50, '#c2563f', .22 + p * .2);
  /* the atlas carries a second, broken crypt: show it once the thing is
     half down, so progress is visible without reading the bar */
  const hurt = n.hp / n.max < .5;
  const shake = hurt ? Math.sin(clock * 11 + n.x) * (fl ? 1.6 : .7) : 0;
  sprProp(hurt ? 'crypt_b' : 'crypt', x + shake, y + 15, .95, fl ? '#ffffff' : null, .8);
  glow(x, y + 5, 12, '#ff5a3a', (hurt ? .6 : .45) + p * .3);
  if (hurt && Math.random() < .25) G.parts.push({ x: x + rnd(-12, 12), y: y + rnd(-6, 8), vx: rnd(-.2, .2), vy: -.5, life: .45, max: .45, col: '#ff8a3a', s: 2, k: 'ember' });
  const w = 34; ctx.fillStyle = '#0a0c11'; ctx.fillRect(x - w / 2, y - 34, w, 4); ctx.fillStyle = C.blood; ctx.fillRect(x - w / 2, y - 34, w * n.hp / n.max, 4);
}
function drawDoor() {
  const d = G.door;
  if (!d || !G.map || G.map[d.y * MW + d.x] !== 2) return;
  const x = d.x * T + T / 2, y = d.y * T + T / 2;
  if (fogAt(x, y) > .85) return;
  const p = (Math.sin(clock * 2.2) + 1) / 2;
  /* it strains when you are near without the key, and settles when you hold one */
  const near = G.players.some(q => !q.down && Math.hypot(q.x - x, q.y - y) < 70);
  const held = G.keys > 0;
  const rattle = (near && !held) ? Math.sin(clock * 24) * 1.1 : 0;
  shadow(x, y + 13, 14, 5, .4);
  glow(x, y, 34, held ? '#f0a23c' : '#8d93a8', (held ? .34 : .16) + p * .1);
  if (!sprProp('gate', x + rattle, y + 13, 1.45)) return;
  /* the lock reads gold once a key is in hand, so the door tells you itself */
  ctx.save();
  ctx.globalAlpha = .75 + p * .25;
  ctx.fillStyle = held ? '#ffd24a' : '#6e7d97';
  ctx.beginPath(); ctx.arc(x, y - 1, 3.4, 0, TAU); ctx.fill();
  ctx.fillStyle = held ? '#fff6d8' : '#3a4152';
  ctx.fillRect(x - .9, y - 1, 1.8, 4);
  ctx.restore(); ctx.globalAlpha = 1;
  if (held && Math.random() < .12) G.parts.push({ x: x + rnd(-10, 10), y: y + rnd(-10, 6), vx: 0, vy: -.4, life: .5, max: .5, col: '#ffd24a', s: 2, k: 'ember' });
}
function drawExit() {
  if (!sprOk('props')) return drawExitOld();
  const e = G.exit, p = (Math.sin(clock * 3) + 1) / 2;
  glow(e.x, e.y, 76, C.cyan, .3 + p * .15);
  sprProp('stairs', e.x, e.y + 16, 1.2);
  ctx.save(); ctx.translate(e.x, e.y); ctx.strokeStyle = C.cyan; ctx.lineWidth = 2; ctx.globalAlpha = .45 + p * .3;
  for (let i = 0; i < 2; i++) { ctx.beginPath(); ctx.ellipse(0, 3, 9 + i * 6 + p * 1.5, 6 + i * 4 + p, clock * (.8 - i * .3), 0, TAU * .72); ctx.stroke(); }
  ctx.restore();
  for (let i = 0; i < 4; i++) { const k = (clock * 8 + i * 5) % 12, a = clock * 1.3 + i * 1.57; ctx.fillStyle = 'rgba(143,211,255,' + (1 - k / 12) * .8 + ')'; ctx.fillRect(e.x + Math.cos(a) * 10, e.y - k * 1.6 - 2, 2, 2); }
}
function drawHazard(h) {
  const warn = h.warn, up = h.up;
  ctx.save(); ctx.translate(h.x, h.y);
  ctx.fillStyle = 'rgba(6,8,14,.62)'; ctx.beginPath(); ctx.ellipse(0, 2, h.r, h.r * .5, 0, 0, TAU); ctx.fill();
  ctx.strokeStyle = warn ? 'rgba(255,120,80,' + (.45 + .45 * Math.sin(clock * 24)) + ')' : 'rgba(176,184,206,.6)';
  ctx.lineWidth = warn ? 2.2 : 1.6; ctx.beginPath(); ctx.ellipse(0, 2, h.r - 1.5, (h.r - 1.5) * .5, 0, 0, TAU); ctx.stroke();
  ctx.strokeStyle = 'rgba(10,13,20,.5)'; ctx.lineWidth = 1; ctx.beginPath(); ctx.ellipse(0, 2, h.r - 4, (h.r - 4) * .5, 0, 0, TAU); ctx.stroke();
  ctx.fillStyle = warn ? 'rgba(255,150,110,.5)' : 'rgba(176,184,206,.34)';
  for (let i = 0; i < 4; i++) { const a = i / 4 * TAU + .4; ctx.beginPath(); ctx.ellipse(Math.cos(a) * 6.5, Math.sin(a) * 3.2 + 2, 2.8, 1.5, 0, 0, TAU); ctx.fill(); }
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
  if (!sprOk('props')) return;
  shadow(p.x, p.y + 5, 11 * p.sc / 1.5, 4, .3);
  if (p.lit) glow(p.x, p.y - 4, p.lit * .55, '#f0a23c', .22 + Math.sin(clock * 9 + p.ph) * .04);
  const dmg = 1 - Math.max(0, p.hp) / p.max;
  const wob = p.wob > 0 ? Math.sin(p.wob * 60) * (1.6 + dmg * 2.2) * (p.wob / .18) : 0;
  /* a prop near breaking leans and shivers, so you can tell one more hit will do */
  const lean = dmg > .5 ? Math.sin(clock * 3 + p.ph) * dmg * .05 : 0;
  if (lean) { ctx.save(); ctx.translate(p.x, p.y + 8); ctx.rotate(lean); ctx.translate(-p.x, -(p.y + 8)); }
  sprProp(p.k, p.x + wob, p.y + 8, p.sc * (1 - dmg * .05), p.fl > 0 ? '#ffffff' : null, .6);
  if (lean) ctx.restore();
  if (dmg > .28) {
    /* cracks that spread with the damage */
    ctx.save(); ctx.globalAlpha = Math.min(.75, dmg * .9); ctx.strokeStyle = 'rgba(16,12,10,.95)'; ctx.lineWidth = 1.2;
    const n = dmg > .66 ? 3 : 2;
    for (let i = 0; i < n; i++) {
      const sx2 = p.x + (hr(i, 1, 9) - .5) * 13 * p.sc, sy2 = p.y + 2 - hr(i, 2, 9) * 11 * p.sc;
      ctx.beginPath(); ctx.moveTo(sx2, sy2);
      let cx2 = sx2, cy2 = sy2;
      for (let j = 0; j < 3; j++) { cx2 += (hr(i, j + 3, 9) - .5) * 7; cy2 += 3.4 * p.sc; ctx.lineTo(cx2, cy2); }
      ctx.stroke();
    }
    ctx.restore();
  }
  if (p.hp < p.max) { ctx.fillStyle = '#0a0c11'; ctx.fillRect(p.x - 9, p.y + 12, 18, 3); ctx.fillStyle = dmg > .66 ? '#e0734a' : '#d9b44a'; ctx.fillRect(p.x - 9, p.y + 12, 18 * Math.max(0, p.hp) / p.max, 3); }
  if (p.k === 'brazier') {
    const f = Math.sin(clock * 9 + p.ph), g = Math.sin(clock * 13 + p.ph * 2), x = p.x, y = p.y - 1;
    ctx.fillStyle = '#d9731f'; ctx.beginPath(); ctx.moveTo(x - 5, y); ctx.quadraticCurveTo(x - 6 + g, y - 9, x + g * 1.5, y - 15 - f * 2); ctx.quadraticCurveTo(x + 6, y - 8, x + 5, y); ctx.fill();
    ctx.fillStyle = '#ffc45a'; ctx.beginPath(); ctx.moveTo(x - 3, y); ctx.quadraticCurveTo(x - 3.5, y - 6, x + g * .8, y - 11); ctx.quadraticCurveTo(x + 3.5, y - 6, x + 3, y); ctx.fill();
  } else if (p.k === 'candles' || p.k === 'lantern') {
    const f = Math.sin(clock * 11 + p.ph); ctx.fillStyle = '#ffd98a'; ctx.beginPath(); ctx.ellipse(p.x, p.y - (p.k === 'lantern' ? 9 : 3), 1.6, 2.8 + f * .5, 0, 0, TAU); ctx.fill();
  }
}
'use strict';
/* Hollowdeep: rendering, input, UI. */
const $ = id => document.getElementById(id);
const stage = $('stage'), cv = $('cv'), ctx = cv.getContext('2d');
const lightCv = document.createElement('canvas'), lctx = lightCv.getContext('2d');
const mini = $('mini'), mctx = mini.getContext('2d');
let W = 0, H = 0, DPR = 1, Z = 1;
const cam = { x: 0, y: 0 }, keys = {}, mouse = { x: 0, y: 0, down: false, last: -1e9 }, touch = { move: null, aim: null };
let spTouch = false, dashTouch = false, bombTouch = false, btnsOn = false, clock = 0, reduceMotion = false;
/* 0 = draw everything, 1 = thinned, 2 = sparse. Raised only by sustained slow
   frames and lowered again by sustained quick ones, with a wide gap between
   the two so it cannot flutter between levels. */
let fxLevel = 0;
const PERF = { ring: [], at: 0, hold: 0, n: 90 };
function perfTick(ms) {
  if (G.state !== 'play') return;          /* menus and overlays are not the game */
  const p = PERF;
  p.ring[p.at++ % p.n] = ms;
  if (p.ring.length < p.n) return;
  p.hold -= 1;
  if (p.hold > 0) return;
  const s = p.ring.slice().sort((a, b) => a - b), med = s[s.length >> 1];
  /* 22ms is about 45fps: slower than that and the drop is worth more than
     the particles. 11ms leaves room to climb back without immediately
     falling over again. */
  if (med > 22 && fxLevel < 2) { fxLevel++; p.hold = p.n * 3; }
  else if (med < 11 && fxLevel > 0) { fxLevel--; p.hold = p.n * 3; }
}
const fxThin = () => fxLevel === 0 ? 1 : fxLevel === 1 ? .5 : .25;
const C = { floorA: '#1a1f2c', floorB: '#1d2333', speck: '#262d40', wall: '#2c3447', wallHi: '#3b455d', face: '#11141c', void: '#0a0c11', door: '#7a4e2a', amber: '#f0a23c', blood: '#d9534f', bone: '#ebe4d2', cyan: '#8fd3ff', leaf: '#9bd16a' };

function resize() {
  DPR = Math.min(window.devicePixelRatio || 1, 2); W = stage.clientWidth; H = stage.clientHeight;
  if (!W || !H) return;
  cv.width = lightCv.width = Math.round(W * DPR); cv.height = lightCv.height = Math.round(H * DPR);
  Z = clamp(Math.min(W / 740, H / 500), .66, 1.6);
  try { btnsOn = getComputedStyle($('dashBtn')).display !== 'none'; } catch (e) { btnsOn = false; }
  if (typeof setSprDensity === 'function') setSprDensity(32 * Z * DPR);
}
new ResizeObserver(resize).observe(stage); resize();

/* ---------- input ---------- */
addEventListener('keydown', e => {
  keys[e.code] = true; initAudio();
  if (['Space', 'ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight', 'Slash'].includes(e.code)) e.preventDefault();
  if (e.code === 'KeyP' && G.state === 'play') G.paused = !G.paused;
  if (e.code === 'KeyM') setMuted(!muted);
  if (e.code === 'KeyN') { musicOn = !musicOn; META.music = musicOn; saveMeta(); setMix(G.state === 'play'); announce('Music ' + (musicOn ? 'on' : 'off'), '#8fd3ff', true); }
  if (e.code === 'KeyV') { voiceOn = !voiceOn; META.voice = voiceOn; saveMeta(); announce('Narrator ' + (voiceOn ? 'on' : 'off'), '#8fd3ff', !voiceOn); }
  if (G.state === 'offer' && /^Digit[123]$/.test(e.code)) chooseUp(+e.code.slice(5) - 1);
});
addEventListener('keyup', e => { keys[e.code] = false; });
addEventListener('blur', () => { for (const k in keys) keys[k] = false; mouse.down = false; });
/* hold the run while the page is out of sight, and leave it held: dropping
   someone straight back into a fight they walked away from is worse */
function pauseForHidden() {
  if (typeof document === 'undefined') return;
  if (document.hidden && G.state === 'play' && !G.paused) {
    G.paused = true;
    for (const k in keys) keys[k] = false;
    mouse.down = false; spTouch = dashTouch = bombTouch = false;
    touch.move = null; touch.aim = null;
  }
}
if (typeof document !== 'undefined' && document.addEventListener) document.addEventListener('visibilitychange', pauseForHidden);
addEventListener('visibilitychange', pauseForHidden);
addEventListener('pagehide', pauseForHidden);
addEventListener('blur', pauseForHidden);
/* P is no use on a phone, so anything that counts as "I am back" resumes */
function resumeFromPause() {
  if (G.state !== 'play' || !G.paused) return false;
  G.paused = false;
  return true;
}
cv.addEventListener('mousemove', e => { const r = cv.getBoundingClientRect(); mouse.x = e.clientX - r.left; mouse.y = e.clientY - r.top; mouse.last = performance.now(); });
cv.addEventListener('mousedown', () => { if (resumeFromPause()) return; mouse.down = true; mouse.last = performance.now(); initAudio(); });
addEventListener('mouseup', () => { mouse.down = false; });
cv.addEventListener('pointerdown', e => {
  if (e.pointerType === 'mouse') return;
  if (resumeFromPause()) return;
  initAudio();
  try { cv.setPointerCapture(e.pointerId); } catch (x) {}
  const r = cv.getBoundingClientRect(), x = e.clientX - r.left, y = e.clientY - r.top, s = { id: e.pointerId, ox: x, oy: y, x, y };
  if (x < W / 2) touch.move = s; else touch.aim = s;
});
cv.addEventListener('pointermove', e => {
  for (const k of ['move', 'aim']) { const s = touch[k]; if (s && s.id === e.pointerId) { const r = cv.getBoundingClientRect(); s.x = e.clientX - r.left; s.y = e.clientY - r.top; } }
});
const endTouch = e => { for (const k of ['move', 'aim']) if (touch[k] && touch[k].id === e.pointerId) touch[k] = null; };
cv.addEventListener('pointerup', endTouch); cv.addEventListener('pointercancel', endTouch);
$('dashBtn').addEventListener('pointerdown', e => { e.stopPropagation(); dashTouch = true; initAudio(); });
$('dashBtn').addEventListener('pointerup', () => { dashTouch = false; });
$('spBtn').addEventListener('pointerdown', e => { e.stopPropagation(); spTouch = true; initAudio(); });
$('spBtn').addEventListener('pointerup', () => { spTouch = false; });
$('bombBtn').addEventListener('pointerdown', e => { e.stopPropagation(); bombTouch = true; initAudio(); });
$('bombBtn').addEventListener('pointerup', () => { bombTouch = false; });

function assistAim(P, base) {
  let best = base, bd = 1e9;
  const test = o => {
    const dx = o.x - P.x, dy = o.y - P.y, d = Math.hypot(dx, dy); if (d > 320 || d < 1 || d >= bd) return;
    let da = Math.atan2(dy, dx) - base; da = Math.atan2(Math.sin(da), Math.cos(da));
    if (Math.abs(da) < .5 && los(P.x, P.y, o.x, o.y)) { bd = d; best = Math.atan2(dy, dx); }
  };
  G.enemies.forEach(test); G.nests.forEach(test); return best;
}
const PAD_DZ = .24;
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
function readInput() {
  const co = G.co, P1 = G.players[0], P2 = G.players[1], a = INS[0], b = INS[1];
  let mx = 0, my = 0;
  if (keys.KeyA || (!co && keys.ArrowLeft)) mx--; if (keys.KeyD || (!co && keys.ArrowRight)) mx++;
  if (keys.KeyW || (!co && keys.ArrowUp)) my--; if (keys.KeyS || (!co && keys.ArrowDown)) my++;
  if (!co && touch.move) {
    const dx = touch.move.x - touch.move.ox, dy = touch.move.y - touch.move.oy, d = Math.hypot(dx, dy);
    if (d > 8) { const m = Math.min(d, 50) / 50; mx = dx / d * m; my = dy / d * m; }
  }
  a.mx = mx; a.my = my;
  let aim, fire = !!(keys.Space || keys.KeyJ || (!co && mouse.down));
  if (!co && touch.aim && Math.hypot(touch.aim.x - touch.aim.ox, touch.aim.y - touch.aim.oy) > 10) {
    aim = Math.atan2(touch.aim.y - touch.aim.oy, touch.aim.x - touch.aim.ox); fire = true;
  } else if (!co && performance.now() - mouse.last < 4000) {
    aim = Math.atan2(cam.y + mouse.y / Z - P1.y, cam.x + mouse.x / Z - P1.x);
  } else aim = assistAim(P1, (mx || my) ? Math.atan2(my, mx) : P1.face);
  a.aim = aim; a.fire = fire; a.sp = !!(keys.KeyE || keys.KeyQ || spTouch); a.dash = !!(keys.ShiftLeft || keys.KeyK || (!co && keys.ShiftRight) || dashTouch);
  a.bomb = !!(keys.KeyF || keys.KeyR || bombTouch);
  const pd1 = padAt(0);
  if (pd1) { const r = readPad(a, pd1); if (r.used && !r.aimed) a.aim = assistAim(P1, (a.mx || a.my) ? Math.atan2(a.my, a.mx) : P1.face); }
  if (P2) {
    let x = 0, y = 0;
    if (keys.ArrowLeft) x--; if (keys.ArrowRight) x++; if (keys.ArrowUp) y--; if (keys.ArrowDown) y++;
    b.mx = x; b.my = y; b.aim = assistAim(P2, (x || y) ? Math.atan2(y, x) : P2.face);
    b.fire = !!(keys.Enter || keys.NumpadEnter || keys.Numpad0); b.dash = !!(keys.ShiftRight || keys.Slash || keys.Numpad1); b.sp = !!(keys.ControlRight || keys.Period || keys.Numpad2);
    b.bomb = !!(keys.AltRight || keys.Numpad3 || keys.Comma);
    const pd2 = padAt(1);
    if (pd2) { const r = readPad(b, pd2); if (r.used && !r.aimed) b.aim = assistAim(P2, (b.mx || b.my) ? Math.atan2(b.my, b.mx) : P2.face); }
  }
}

/* ---------- drawing ---------- */
function glow(x, y, r, col, a) {
  r = r > 0 ? r : 0; if (!(r > 0) || !isFinite(x) || !isFinite(y)) return;
  const g = ctx.createRadialGradient(x, y, 0, x, y, r); g.addColorStop(0, col); g.addColorStop(1, 'rgba(0,0,0,0)');
  ctx.globalAlpha = clamp(a, 0, 1); ctx.fillStyle = g; ctx.beginPath(); ctx.arc(x, y, r, 0, TAU); ctx.fill(); ctx.globalAlpha = 1;
}
function drawLighting() {
  const k = DPR * Z;
  lctx.setTransform(1, 0, 0, 1, 0, 0); lctx.globalCompositeOperation = 'source-over'; lctx.clearRect(0, 0, lightCv.width, lightCv.height);
  lctx.fillStyle = 'rgba(5,7,11,.93)'; lctx.fillRect(0, 0, lightCv.width, lightCv.height);
  lctx.globalCompositeOperation = 'destination-out';
  const hole = (wx, wy, r, a) => {
    const x = (wx - cam.x) * k, y = (wy - cam.y) * k, rr = r * k;
    if (x < -rr || y < -rr || x > lightCv.width + rr || y > lightCv.height + rr) return;
    const g = lctx.createRadialGradient(x, y, rr * .08, x, y, rr); g.addColorStop(0, 'rgba(0,0,0,' + a + ')'); g.addColorStop(.6, 'rgba(0,0,0,' + a * .55 + ')'); g.addColorStop(1, 'rgba(0,0,0,0)');
    lctx.fillStyle = g; lctx.beginPath(); lctx.arc(x, y, rr, 0, TAU); lctx.fill();
  };
  const lr = om('light', 1);
  for (const P of G.players) hole(P.x, P.y, (P.down ? 90 : 300) * lr, 1);
  const fz = (x, y) => fogAt(x, y) > .85;
  for (const t of G.torches) if (!fz(t.x, t.y)) hole(t.x, t.y + 14, 170 + Math.sin(clock * 8 + t.ph) * 6 + Math.sin(clock * 19 + t.ph * 3) * 3 + Math.sin(clock * 33 + t.ph) * 1.5, .9);
  for (const s of G.shots) hole(s.x, s.y, s.kind === 'fire' ? 130 : 70, .8);
  for (const s of G.eshots) hole(s.x, s.y, 56, .6);
  for (const n of G.nests) if (!fz(n.x, n.y)) hole(n.x, n.y, 80, .6);
  for (const pr of G.props) if (pr.lit && !fz(pr.x, pr.y)) hole(pr.x, pr.y, pr.lit, .7);
  for (const hz of G.hazards) if ((hz.warn || hz.up > .1) && !fz(hz.x, hz.y)) hole(hz.x, hz.y, 60, .45);
  for (const i of G.items) if ((i.kind === 'gear' || i.kind === 'bomb') && !fz(i.x, i.y)) hole(i.x, i.y, i.kind === 'gear' ? 96 : 72, .7);
  for (const b of G.bolts) if (b.t < .22) { hole(b.x1, b.y1, 100, .8); hole(b.x2, b.y2, 84, .7); }
  for (const e of G.enemies) if (e.type === 'bloat' && e.fuse > 0) hole(e.x, e.y, 120, .8);
  for (const e of G.enemies) { if (fz(e.x, e.y)) continue; if (e.type === 'wisp') hole(e.x, e.y, 90, .6); else if (e.boss) hole(e.x, e.y, e.st !== 'chase' ? 190 : 130, .7); }
  if (!fz(G.exit.x, G.exit.y)) hole(G.exit.x, G.exit.y, 110, .8);
  for (const i of G.items) if ((i.kind === 'key' || i.kind === 'chest') && !fz(i.x, i.y)) hole(i.x, i.y, 70, .7);
  if (G.slash && G.slash.kind === 'boom') hole(G.slash.x, G.slash.y, 160, 1);
  ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.drawImage(lightCv, 0, 0);
  const zn = zoneOf(G.level), vx0 = cam.x - 200, vy0 = cam.y - 200, vx1 = cam.x + W / Z + 200, vy1 = cam.y + H / Z + 200;
  ctx.setTransform(k, 0, 0, k, -cam.x * k, -cam.y * k); ctx.globalCompositeOperation = 'lighter';
  const tint = (x, y, r, col, a) => { if (x > vx0 && x < vx1 && y > vy0 && y < vy1) glow(x, y, r, col, a); };
  for (const t of G.torches) if (!fz(t.x, t.y)) tint(t.x, t.y + 8, 140 + Math.sin(clock * 11 + t.ph) * 8, zn.amb, .17);
  for (const P of G.players) if (!P.down) tint(P.x, P.y, 110, P.cls.col, .09);
  for (const s of G.shots) { const ec = s.own && s.own.g && s.own.g.elem ? ELEM_COL[s.own.g.elem] : s.col; tint(s.x, s.y, s.kind === 'fire' ? 120 : 74, ec, .34); }
  for (const s of G.eshots) tint(s.x, s.y, 48, '#ffd9a8', .3);
  for (const b of G.bolts) { const a = Math.max(0, 1 - b.t / .22); if (a > 0) { tint(b.x1, b.y1, 96, '#c9b6ff', .5 * a); tint(b.x2, b.y2, 80, '#c9b6ff', .4 * a); } }
  for (const e of G.enemies) {
    if (fz(e.x, e.y)) continue;
    if (e.type === 'wisp') tint(e.x, e.y, 90, e.col, .3);
    else if (e.type === 'reaper') tint(e.x, e.y - 6, 120, '#dfe4ef', .26);
    else if (e.type === 'bloat' && e.fuse > 0) tint(e.x, e.y, 90 + (1 - e.fuse / .6) * 50, '#d8f0a0', .45);
    else if (e.type === 'thief' && e.loot > 0) tint(e.x, e.y, 70, '#f0a23c', .28);
    else if (e.boss && e.st !== 'chase') tint(e.x, e.y, 130, (BOSSES[e.kind] || BOSSES.count).glow, .26);
    if (e.burn > 0) tint(e.x, e.y, 54, '#ff8a3a', .22);
    else if (e.chill > 0) tint(e.x, e.y, 48, '#8fd3ff', .18);
    else if (e.pois > 0) tint(e.x, e.y, 48, '#9bd16a', .18);
  }
  for (const i of G.items) {
    if (fz(i.x, i.y)) continue;
    if (i.kind === 'gear') tint(i.x, i.y - 10, 86, i.item.col, .4 + Math.sin(clock * 2.6 + i.t) * .1);
    else if (i.kind === 'bomb') tint(i.x, i.y, 66, '#b98cff', .34);
    else if (i.kind === 'key' || i.kind === 'chest') tint(i.x, i.y, 70, '#f0a23c', .3);
  }
  for (const h of G.hazards) if (h.up > .1 && !fz(h.x, h.y)) tint(h.x, h.y, 60, '#cfd6e6', .16 * h.up);
  if (G.event) { const r = G.event.room, pu = .5 + .5 * Math.sin(clock * 4); tint((r.cx + .5) * T, (r.cy + .5) * T, Math.max(r.w, r.h) * T * .6, '#ff8a3a', .07 + pu * .04); }
  for (const pr of G.props) if (pr.lit && !fz(pr.x, pr.y)) tint(pr.x, pr.y - 4, pr.lit * .8, '#ffb55a', .16);
  for (const f of G.fxs) if (f.kind === 'chest') tint(f.x, f.y, 150, '#ffd98a', .5 * Math.max(0, 1 - f.t / .8));
  if (!fz(G.exit.x, G.exit.y)) tint(G.exit.x, G.exit.y, 100, C.cyan, .2);
  ctx.globalCompositeOperation = 'source-over';
}

/* ---------- fog of war ---------- */
const FS = 2, FW = MW * FS, FH = MH * FS, FTS = T / FS;
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
}
function drawFog() {
  if (!fogOn()) return; updateFog();
  ctx.imageSmoothingEnabled = true; ctx.drawImage(fogCv, 0, 0, MW * T, MH * T);
}
function drawMini() {
  const w = mini.width, h = mini.height, s = 3; mctx.clearRect(0, 0, w, h);
  for (let y = 0; y < MH; y++) for (let x = 0; x < MW; x++) {
    if (!G.seen[y * MW + x]) continue; const t = G.map[y * MW + x];
    mctx.globalAlpha = fogA[(y * FS) * FW + x * FS] < .3 ? 1 : .5; mctx.fillStyle = t === 0 ? '#3a4359' : t === 2 ? '#a8743d' : '#1c2130'; mctx.fillRect(x * s, y * s, s, s); mctx.globalAlpha = 1;
  }
  const seenAt = (x, y) => !!G.seen[Math.floor(y / T) * MW + Math.floor(x / T)];
  const px = v => v / T * s;
  /* a ring: the way out */
  const markRing = (x, y, c) => {
    if (!seenAt(x, y)) return;
    mctx.strokeStyle = c; mctx.lineWidth = 1.5;
    mctx.beginPath(); mctx.arc(px(x), px(y), 2.6, 0, TAU); mctx.stroke();
    mctx.fillStyle = c; mctx.fillRect(px(x) - .5, px(y) - .5, 1, 1);
  };
  /* a cross: something to break */
  const markCross = (x, y, c) => {
    if (!seenAt(x, y)) return;
    const a = px(x), b = px(y), r = 2.4;
    mctx.strokeStyle = c; mctx.lineWidth = 1.4;
    mctx.beginPath();
    mctx.moveTo(a - r, b - r); mctx.lineTo(a + r, b + r);
    mctx.moveTo(a + r, b - r); mctx.lineTo(a - r, b + r);
    mctx.stroke();
  };
  /* a triangle: the way through, if you can reach it */
  const markTri = (x, y, c) => {
    if (!seenAt(x, y)) return;
    const a = px(x), b = px(y), r = 3;
    mctx.fillStyle = c;
    mctx.beginPath(); mctx.moveTo(a, b - r); mctx.lineTo(a + r, b + r - .5); mctx.lineTo(a - r, b + r - .5);
    mctx.closePath(); mctx.fill();
  };
  /* a bar: something to eat, which is the only clock that matters */
  const markBar = (x, y, c) => {
    if (!seenAt(x, y)) return;
    mctx.fillStyle = c;
    mctx.fillRect(px(x) - 3, px(y) - 1.5, 6, 3);
  };
  /* a diamond: something to open */
  const markDiamond = (x, y, c) => {
    if (!seenAt(x, y)) return;
    const a = px(x), b = px(y), r = 3;
    mctx.fillStyle = c;
    mctx.beginPath(); mctx.moveTo(a, b - r); mctx.lineTo(a + r, b); mctx.lineTo(a, b + r); mctx.lineTo(a - r, b); mctx.fill();
  };
  markRing(G.exit.x, G.exit.y, C.cyan);
  for (const n of G.nests) markCross(n.x, n.y, C.blood);
  for (const i of G.items) {
    if (i.kind === 'chest') markDiamond(i.x, i.y, C.amber);
    else if (i.kind === 'key') markTri(i.x, i.y, C.amber);
    else if (i.kind === 'food') markBar(i.x, i.y, C.leaf);
  }
  for (const P of G.players) { mctx.strokeStyle = 'rgba(235,228,210,.3)'; mctx.lineWidth = 1; mctx.beginPath(); mctx.arc(px(P.x), px(P.y), 7.5 * s, 0, TAU); mctx.stroke(); }
  /* and you are a square with a pale edge, so you are findable whatever
     delver you took and however you see colour */
  for (const P of G.players) {
    const a = px(P.x), b = px(P.y);
    mctx.fillStyle = P.down ? '#4a5166' : P.cls.col;
    mctx.fillRect(a - 2, b - 2, 4, 4);
    mctx.strokeStyle = P.down ? 'rgba(235,228,210,.5)' : '#ebe4d2';
    mctx.lineWidth = 1; mctx.strokeRect(a - 2.5, b - 2.5, 5, 5);
  }
}
function drawScreenFx() {
  const hurtV = Math.max(...G.players.map(p => p.hurt));
  ctx.setTransform(DPR, 0, 0, DPR, 0, 0);
  const zn = zoneOf(G.level); ctx.fillStyle = zn.amb;
  for (let i = 0; i < 34; i++) {
    const sp = 4 + (i % 5) * 3, x = (((i * 137.5 + clock * sp - cam.x * (.25 + (i % 3) * .1)) % W) + W) % W, y = (((i * 71.3 - clock * (3 + i % 4 * 2) - cam.y * (.25 + (i % 3) * .1)) % H) + H) % H;
    ctx.globalAlpha = .05 + .1 * (.5 + .5 * Math.sin(clock * 1.3 + i)); ctx.beginPath(); ctx.arc(x, y, .8 + (i % 3) * .5, 0, TAU); ctx.fill();
  }
  ctx.globalAlpha = 1;
  const vg = ctx.createRadialGradient(W / 2, H / 2, Math.min(W, H) * .4, W / 2, H / 2, Math.max(W, H) * .76);
  vg.addColorStop(0, 'rgba(3,5,9,0)'); vg.addColorStop(.6, 'rgba(3,5,9,.2)'); vg.addColorStop(1, 'rgba(3,5,9,.62)');
  ctx.fillStyle = vg; ctx.fillRect(0, 0, W, H);
  for (const t of G.texts) { const pop = 1 + Math.max(0, t.life - .72) * 2.4; ctx.globalAlpha = clamp(t.life / .5, 0, 1); ctx.fillStyle = t.col; ctx.font = '600 ' + Math.round((t.sz || 13) * pop) + 'px "Spline Sans Mono",monospace'; ctx.textAlign = 'center'; ctx.lineWidth = 3; ctx.strokeStyle = 'rgba(8,10,14,.8)'; const tx = (t.x - cam.x) * Z, ty = (t.y - cam.y) * Z; ctx.strokeText(t.txt, tx, ty); ctx.fillText(t.txt, tx, ty); }
  ctx.globalAlpha = 1;
  if (G.event && G.state === 'play') {
    const E = G.event, txt = 'Wave ' + Math.min(E.waves, E.wave + 1) + ' of ' + E.waves + (E.left ? '  \u00b7  ' + E.left + ' left' : '');
    ctx.font = '600 13px "Spline Sans Mono",monospace'; ctx.textAlign = 'center';
    const ty = H * (W < 560 ? .2 : .14);
    ctx.lineWidth = 4; ctx.strokeStyle = 'rgba(6,8,12,.85)'; ctx.strokeText(txt, W / 2, ty);
    ctx.fillStyle = '#ff8a3a'; ctx.fillText(txt, W / 2, ty);
  }
  const B = G.state === 'play' ? G.enemies.find(e => e.boss && e.alert && e.hp > 0) : null;
  if (B) {
    const bw = clamp(W - 360, 160, 440), bx = (W - bw) / 2, by = H - 46;
    ctx.fillStyle = 'rgba(12,14,19,.78)'; ctx.fillRect(bx - 6, by - 24, bw + 12, 38); ctx.strokeStyle = '#2d3548'; ctx.lineWidth = 1; ctx.strokeRect(bx - 5.5, by - 23.5, bw + 11, 37);
    ctx.fillStyle = C.bone; ctx.font = '400 18px "Pirata One",Georgia,serif'; ctx.textAlign = 'center'; ctx.fillText(B.name || 'The Warden', W / 2, by - 8);
    ctx.fillStyle = '#0a0c11'; ctx.fillRect(bx, by, bw, 8); ctx.fillStyle = B.ph >= 3 ? '#ff2a18' : B.ph >= 2 ? '#ff4a3a' : C.blood; ctx.fillRect(bx, by, bw * Math.max(0, B.hp) / B.max, 8); ctx.fillStyle = 'rgba(255,255,255,.5)'; ctx.fillRect(bx + bw / 2 - .5, by - 1, 1, 10);
  }
  if (hurtV > 0) { const g = ctx.createRadialGradient(W / 2, H / 2, Math.min(W, H) * .3, W / 2, H / 2, Math.max(W, H) * .7); g.addColorStop(0, 'rgba(217,83,79,0)'); g.addColorStop(1, 'rgba(217,83,79,' + hurtV * 1.6 + ')'); ctx.fillStyle = g; ctx.fillRect(0, 0, W, H); }
  const chillV = Math.max(0, ...G.players.map(p => p.chill || 0));
  if (chillV > 0) { const g = ctx.createRadialGradient(W / 2, H / 2, Math.min(W, H) * .25, W / 2, H / 2, Math.max(W, H) * .72); g.addColorStop(0, 'rgba(143,211,255,0)'); g.addColorStop(1, 'rgba(143,211,255,' + Math.min(.4, chillV * .22) + ')'); ctx.fillStyle = g; ctx.fillRect(0, 0, W, H); }
  if (G.banner && (G.state === 'play' || G.state === 'clear')) {
    const by = H * (W < 560 ? .44 : .3), bs = W < 560 ? 40 : 54;
    ctx.globalAlpha = clamp(G.banner.t, 0, 1); ctx.fillStyle = C.bone; ctx.font = '400 ' + bs + 'px "Pirata One",Georgia,serif'; ctx.textAlign = 'center'; ctx.fillText(G.banner.txt, W / 2, by);
    if (G.banner.sub) { ctx.fillStyle = zn.amb; ctx.font = '600 ' + (W < 560 ? 11 : 13) + 'px "Spline Sans Mono",monospace'; ctx.fillText(G.banner.sub.toUpperCase(), W / 2, by + 24); }
    ctx.globalAlpha = 1;
  }
  if (G.flash > 0) { ctx.fillStyle = 'rgba(232,222,255,' + Math.min(.72, G.flash) * (reduceMotion ? .3 : 1) + ')'; ctx.fillRect(0, 0, W, H); }
  if (G.voice) {
    const v = G.voice, a = clamp(v.t / .55, 0, 1);
    const stack = Math.min(156, W * .3) * .73;
    const miniTop = H - 10 - stack, btnTop = H - (stack + 22 + 64);
    const vy = Math.min(H - (B ? 96 : 56), (btnsOn ? Math.min(miniTop, btnTop) : miniTop) - 16);
    ctx.globalAlpha = a; ctx.textAlign = 'center';
    ctx.font = '400 ' + (W < 560 ? 21 : 27) + 'px "Pirata One",Georgia,serif';
    ctx.lineWidth = 5; ctx.strokeStyle = 'rgba(6,8,12,.9)'; ctx.strokeText(v.txt, W / 2, vy);
    ctx.fillStyle = v.col; ctx.fillText(v.txt, W / 2, vy);
    ctx.globalAlpha = 1;
  }
  /* the pause sheet is an overlay now, and dims the stage itself */
  for (const k of ['move', 'aim']) { const s = touch[k]; if (!s) continue; ctx.strokeStyle = 'rgba(235,228,210,.35)'; ctx.lineWidth = 2; ctx.beginPath(); ctx.arc(s.ox, s.oy, 50, 0, TAU); ctx.stroke(); ctx.fillStyle = 'rgba(235,228,210,.35)'; ctx.beginPath(); ctx.arc(s.ox + clamp(s.x - s.ox, -50, 50), s.oy + clamp(s.y - s.oy, -50, 50), 18, 0, TAU); ctx.fill(); }
}
function render() {
  const al = G.players.filter(p => !p.down), src = al.length ? al : G.players, P = { x: src.reduce((s, p) => s + p.x, 0) / src.length, y: src.reduce((s, p) => s + p.y, 0) / src.length };
  ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.fillStyle = '#05070a'; ctx.fillRect(0, 0, cv.width, cv.height);
  if (G.state === 'menu' && !reduceMotion) { P.x += Math.cos(clock * .12) * 220; P.y += Math.sin(clock * .17) * 130; }
  const vw = W / Z, vh = H / Z, mw = MW * T, mh = MH * T;
  const tx = clamp(P.x - vw / 2, 0, Math.max(0, mw - vw)), ty = clamp(P.y - vh / 2, 0, Math.max(0, mh - vh));
  if (cam.r !== G.rooms) { cam.r = G.rooms; cam.x = tx; cam.y = ty; }
  if (mw < vw) cam.x = (mw - vw) / 2; else cam.x += (tx - cam.x) * .14;
  if (mh < vh) cam.y = (mh - vh) / 2; else cam.y += (ty - cam.y) * .14;
  const sh = (G.shake > 0 && !reduceMotion) ? G.shake * 14 : 0, ox = (Math.random() - .5) * sh, oy = (Math.random() - .5) * sh, k = DPR * Z;
  ctx.setTransform(k, 0, 0, k, (-cam.x + ox) * k, (-cam.y + oy) * k);
  drawTiles(); drawDecals(); drawArena(); drawExit(); drawDoor(); for (const t of G.torches) drawTorch(t);
  for (const i of G.items) drawItem(i);
  const ents = [];
  for (const n of G.nests) ents.push([n.y, n, drawNest]);
  for (const e of G.enemies) if (fogAt(e.x, e.y) < .4) ents.push([e.y, e, drawFoe]);
  for (const d of G.dying) if (fogAt(d.x, d.y) < .4) ents.push([d.y, d, drawDying]);
  for (const p of G.players) ents.push([p.y, p, drawPlayer]);
  for (const pr of G.props) ents.push([pr.y, pr, drawProp]);
  for (const hz of G.hazards) ents.push([hz.y, hz, drawHazard]);
  ents.sort((a, b) => a[0] - b[0]); for (const [, o, fn] of ents) fn(o);
  drawZones(); drawShots(); drawBolts(); drawFx(); drawFog();
  drawLighting(); ctx.setTransform(k, 0, 0, k, (-cam.x + ox) * k, (-cam.y + oy) * k);
  drawScreenFx(); drawMini();
}

/* ---------- UI ---------- */
const mkHud = s => ({ box: $('hp' + s), hp: $('hpFill' + s), txt: $('hpTxt' + s), dash: $('dashFill' + s), sp: $('spFill' + s), name: $('clsName' + s), xp: $('xpFill' + s), lv: $('lv' + s), gear: $('gear' + s), drain: $('drainFill' + s) });
const hud1 = mkHud(''), hud2 = mkHud('2'), hud = { lvl: $('lvl'), gold: $('gold'), keys: $('keys'), combo: $('combo'), comboBox: $('comboBox'), bombs: $('bombs'), bombBox: $('bombBox'), omenBox: $('omenBox'), omenName: $('omenName') };
const SLOT_GLYPH = { weapon: 'W', armour: 'A', trinket: 'T' };
function setHp(h, P) {
  h.hp.style.width = (P.hp / P.max * 100) + '%'; h.txt.textContent = P.down ? 'DOWN' : Math.ceil(P.hp) + ' / ' + P.max;
  h.hp.style.background = P.hp / P.max < .34 ? '#ff2f28' : '';
  /* the next ten seconds of drain, drawn to scale at the leading edge */
  if (h.drain) {
    const rate = drainRate(P), cost = Math.min(P.hp, rate * DRAIN_AHEAD);
    const lo = Math.max(0, (P.hp - cost) / P.max), hi = Math.max(lo, P.hp / P.max);
    h.drain.hidden = P.down || P.hp <= 0 || cost <= 0;
    h.drain.style.left = (lo * 100) + '%';
    h.drain.style.width = ((hi - lo) * 100) + '%';
    /* amber when something you took made it worse than the depth alone */
    h.drain.classList.toggle('worse', rate > drainPlain() * 1.02);
    h.drain.title = 'The deep takes ' + rate.toFixed(1) + ' health a second here';
  }
  h.xp.style.width = clamp(P.xp / xpNeed(P.plvl), 0, 1) * 100 + '%';
  h.lv.textContent = 'LV ' + P.plvl;
  for (const sp of h.gear.children) {
    const it = P.gear[sp.dataset.s];
    sp.textContent = SLOT_GLYPH[sp.dataset.s];
    sp.style.color = it ? it.col : '#454c5e';
    sp.style.borderColor = it ? it.col : '#2d3548';
    sp.style.borderStyle = it ? ({ magic: 'solid', rare: 'dashed', fabled: 'double', cursed: 'dotted' }[it.rar] || 'solid') : 'solid';
    sp.style.borderWidth = it && it.rar === 'fabled' ? '3px' : '1px';
    /* underlined means this piece is holding up a set that is live: a
       typographic mark, so it does not lean on colour */
    sp.style.textDecoration = it && setLive(P, it.set) ? 'underline' : 'none';
    sp.title = it ? it.name + ' \u2014 ' + itemLines(it, P).join(', ') : 'No ' + sp.dataset.s;
  }
  h.dash.style.width = (100 - clamp(P.dashCd / (1.3 * P.dashMul), 0, 1) * 100) + '%';
  h.sp.style.width = (100 - clamp(P.spCd / (P.spMax || SP_CD), 0, 1) * 100) + '%'; h.sp.style.background = P.spCd <= 0 ? P.cls.col : '';
  h.name.textContent = (G.co ? 'P' + (P.idx + 1) + ' ' : '') + P.cls.name; h.name.style.color = P.cls.col;
}
function updateHud() {
  setHp(hud1, G.players[0]); hud2.box.hidden = !G.players[1]; if (G.players[1]) setHp(hud2, G.players[1]);
  hud.lvl.textContent = G.level; hud.gold.textContent = G.gold; hud.keys.textContent = G.keys;
  if (hud.omenBox) {
    hud.omenBox.hidden = !G.omen;
    if (G.omen) { hud.omenName.textContent = G.omen.name; hud.omenBox.style.color = G.omen.col; }
  }
  hud.bombs.textContent = G.bombs; hud.bombBox.hidden = false;
  $('bombBtn').style.opacity = G.bombs > 0 ? '1' : '.35';
  hud.comboBox.hidden = G.combo < 2;
  if (G.combo >= 2) { hud.combo.textContent = G.combo + '\u00d7' + comboMult().toFixed(1); hud.combo.style.color = G.combo >= 15 ? '#fff1b8' : G.combo >= 8 ? '#ffd24a' : ''; }
}
let mode = 1, picks = [];
function setMode(m) {
  mode = m; picks = [];
  document.querySelectorAll('#modes .btn').forEach(b => b.classList.toggle('on', +b.dataset.m === m));
  $('pickHint').textContent = m === 2 ? 'Player 1 (WASD, Space, Left Shift): choose your delver.' : '';
}
function portrait(c, b) {
  try {
    const P = { x: 33, y: 40, r: 11, cls: c, face: .5, aim: 1.2, hp: 1, max: 1, down: false, inv: 0, dash: 0, hurt: 0, walk: 0, swing: 0, idx: 0, rev: 0 }, co = G.co; G.co = false;
    ctx.save(); ctx.setTransform(3, 0, 0, 3, 0, 0); ctx.clearRect(0, 0, 70, 70); drawPlayer(P); ctx.restore(); G.co = co;
    ctx.save(); ctx.setTransform(1, 0, 0, 1, 0, 0);
    const pc = b.querySelector('canvas.gl'); if (pc) pc.getContext('2d').drawImage(cv, 0, 0, 200, 200, 0, 0, 96, 96);
    ctx.clearRect(0, 0, 200, 200); ctx.restore();
  } catch (e) {}
}
function onSprReady() { document.querySelectorAll('#cards .card').forEach(b => { if (b._cls) portrait(b._cls, b); }); }
function drawVendor() {
  try {
    const pc = $('vendor'); if (!pc || !pc.getContext) return;
    ctx.save(); ctx.setTransform(2.2, 0, 0, 2.2, 0, 0); ctx.clearRect(0, 0, 100, 100); sprChar('npc_keeper', 32, 46, Math.PI / 2, 'walk', 0, 1); ctx.restore();
    ctx.save(); ctx.setTransform(1, 0, 0, 1, 0, 0); const g = pc.getContext('2d'); g.clearRect(0, 0, pc.width, pc.height); g.drawImage(cv, 0, 0, 140, 140, 0, 0, pc.width, pc.height); ctx.clearRect(0, 0, 140, 140); ctx.restore();
  } catch (e) {}
}
let shopShown = false;
function showShop() {
  shopShown = true; const nxt = G.level + 1;
  $('shopSub').textContent = 'A hooded peddler waits at the foot of the stairs. Spend your gold before you descend to depth ' + nxt + (isBossLvl(nxt) ? ', where ' + ZONES[Math.floor((nxt - 1) / 3) % ZONES.length].boss + ' guards the key.' : '.');
  $('descend').textContent = 'Descend to depth ' + nxt; $('hud').hidden = true; $('shop').hidden = false; drawVendor(); renderShop();
}
function renderShop() {
  $('shopGold').textContent = G.gold;
  const pct = x => Math.round((x - 1) * 100), hl = $('shopHeroes'); hl.innerHTML = '';
  for (const P of G.players) {
    const d = document.createElement('div'); d.className = 'heroline'; d.style.color = P.cls.col;
    d.textContent = (G.co ? 'P' + (P.idx + 1) + ' ' : '') + P.cls.name + ' \u00b7 level ' + P.plvl + (P.down ? ' \u00b7 down' : ' \u00b7 ' + Math.ceil(P.hp) + ' / ' + P.max + ' health') + ' \u00b7 damage +' + pct(P.dmgMul) + '% \u00b7 speed +' + pct(P.spdMul) + '%';
    hl.appendChild(d);
    if ((P.pacts || []).length) {
      const pl = document.createElement('div'); pl.className = 'heroline'; pl.style.color = '#e0556b';
      pl.textContent = 'Pacts: ' + P.pacts.map(p => p.name).join(' \u00b7 ');
      hl.appendChild(pl);
    }
    const learned = (BOONS[P.cls.key] || []).filter(b => bn(P, b.id));
    if (learned.length) {
      const bl = document.createElement('div'); bl.className = 'heroline'; bl.style.color = P.cls.col;
      bl.textContent = 'Boons: ' + learned.map(b => b.name).join(' \u00b7 ');
      hl.appendChild(bl);
    }
    const worn = SLOTS.map(s => P.gear[s]).filter(Boolean);
    if (worn.length) {
      const g = document.createElement('div'); g.className = 'heroline';
      worn.forEach((it, i) => { const sp = document.createElement('span'); sp.style.color = it.col; sp.textContent = (i ? ' \u00b7 ' : '') + it.name; g.appendChild(sp); });
      hl.appendChild(g);
    }
  }
  const ww = $('shopWares'); ww.innerHTML = '';
  for (let i = 0; i < G.wares.length; i++) {
    const it = G.wares[i];
    const row = document.createElement('div'); row.className = 'srow'; row.style.setProperty('--c', it.col);
    const info = document.createElement('div');
    const nm = document.createElement('span'); nm.className = 'nm'; nm.textContent = it.name; info.appendChild(nm);
    const tag = document.createElement('span'); tag.className = 'itemrar'; tag.style.color = it.col;
    tag.textContent = (it.rar === 'cursed' ? 'Cursed' : (RARITY[it.rar] || {}).name || it.rar) + ' \u00b7 ' + it.slot; info.appendChild(tag);
    const bl = document.createElement('span'); bl.className = 'bl'; bl.textContent = itemLines(it).join(' \u00b7 '); info.appendChild(bl);
    row.appendChild(info);
    const bw = document.createElement('div'); bw.className = 'sbuy';
    for (const P of G.players) {
      const b = document.createElement('button'); b.type = 'button'; b.className = 'btn buy';
      const cur = P.gear[it.slot];
      const can = !it.sold && !P.down && G.gold >= it.price;
      b.textContent = (G.co ? 'P' + (P.idx + 1) + ' \u00b7 ' : 'Buy \u00b7 ') + (it.sold ? 'Sold' : it.price + 'g');
      b.disabled = !can;
      if (cur && !it.sold) b.title = 'Replaces ' + cur.name;
      else if (!it.sold && G.gold < it.price) b.title = 'Not enough gold';
      b.addEventListener('click', () => { if (buyWare(P, i)) { sfx('gear'); renderShop(); } });
      bw.appendChild(b);
    }
    row.appendChild(bw); ww.appendChild(row);
  }
  const wrap = $('shopRows'); wrap.innerHTML = '';
  for (const it of SHOP) {
    const info = it.id === 'master' && G.co ? { name: 'Weapon Mastery', desc: 'Your own weapon gets better: wider, bigger, extra daggers or piercing arrows.', col: '#e7b04a' } : shopInfo(G.players[0], it);
    const row = document.createElement('div'); row.className = 'srow'; row.style.setProperty('--c', info.col);
    row.innerHTML = '<div class="sinfo"><span class="nm"></span><span class="bl"></span></div><div class="sbuy"></div>';
    row.querySelector('.nm').textContent = info.name; row.querySelector('.bl').textContent = info.desc;
    const bw = row.querySelector('.sbuy');
    for (const P of G.players) {
      const st = shopState(P, it), pr = shopPrice(P, it), b = document.createElement('button'); b.type = 'button'; b.className = 'btn buy';
      const lab = st === 'max' ? 'Maxed' : st === 'full' ? 'Full' : st === 'down' ? 'Down' : pr + 'g';
      b.textContent = (G.co ? 'P' + (P.idx + 1) + ' \u00b7 ' : 'Buy \u00b7 ') + lab; b.disabled = st !== 'ok';
      if (st === 'poor') b.title = 'Not enough gold';
      b.addEventListener('click', () => { if (shopBuy(P, it.id)) { sfx('coin'); renderShop(); } }); bw.appendChild(b);
    }
    wrap.appendChild(row);
  }
}
$('descend').addEventListener('click', () => { leaveShop(); });
function buildMenu() {
  const wrap = $('cards'); wrap.innerHTML = '';
  for (const c of Object.values(CLASSES)) {
    const b = document.createElement('button'); b.type = 'button'; b.className = 'card'; b.style.setProperty('--c', c.col);
    const lab = ['Health', 'Speed', 'Power'];
    b.innerHTML = '<canvas class="gl" width="96" height="96"></canvas><span class="nm">' + c.name + '</span><span class="bl">' + c.blurb + '</span>' +
      '<span class="bl sp">Special: ' + specialLine(c) + '</span>' +
      c.m.map((v, i) => '<span class="meter"><span>' + lab[i] + '</span><i style="--v:' + Math.round(v * 100) + '%;--c:' + c.col + '"></i></span>').join('');
    b._cls = c; portrait(c, b); b.addEventListener('click', () => pick(c.key)); wrap.appendChild(b);
  }
  document.querySelectorAll('#modes .btn').forEach(b => b.addEventListener('click', () => setMode(+b.dataset.m)));
}
function pick(key) {
  if (mode === 1) return begin([key]);
  picks.push(key);
  if (picks.length < 2) { $('pickHint').textContent = 'Player 2 (arrows, Enter, Right Shift): choose your delver.'; return; }
  const p = picks; picks = []; begin(p);
}
function refreshResume() {
  const row = $('resumeRow'); if (!row) return;
  row.hidden = !pendingRun;
  if (pendingRun) $('resume').textContent = 'Carry on from depth ' + pendingRun.level;
}
function showMenu() {
  /* said in the menu only: nobody needs this over the top of a fight */
  { const n = $('noSave'); if (n) n.hidden = storageWorks(); }
  syncOpts(); setMode(mode); $('menu').hidden = false; $('over').hidden = true; $('barrow').hidden = true; $('hud').hidden = true; G.state = 'menu'; $('best').textContent = G.best; $('echoes').textContent = META.echoes; refreshResume(); const f = pendingRun ? $('resume') : document.querySelector('#cards .card'); if (f) f.focus({ preventScroll: true }); }
function begin(list) { initAudio(); startGame(list); saveRun(); $('menu').hidden = true; $('over').hidden = true; $('hud').hidden = false; cam.x = G.player.x - W / Z / 2; cam.y = G.player.y - H / Z / 2; }
$('again').addEventListener('click', () => { if (G.state === 'won') { G.state = 'dead'; bankRun(); } begin(G.clsKeys); });
$('deeper').addEventListener('click', () => {
  $('over').hidden = true; $('hud').hidden = false;
  G.state = 'play'; overShown = false; G.winPending = false;
  announce('Deeper, then', '#ffd24a');
});
function syncOpts() {
  $('optMotion').textContent = 'Reduce motion: ' + (reduceMotion ? 'on' : 'off');
  $('optVoice').textContent = 'Narrator: ' + (voiceOn ? 'on' : 'off');
  $('optMusic').textContent = 'Music: ' + (musicOn ? 'on' : 'off');
}
$('optMotion').addEventListener('click', () => { reduceMotion = !reduceMotion; META.reduceMotion = reduceMotion; saveMeta(); syncOpts(); });
$('optVoice').addEventListener('click', () => { voiceOn = !voiceOn; META.voice = voiceOn; saveMeta(); syncOpts(); if (!voiceOn && typeof speechSynthesis !== 'undefined') { try { speechSynthesis.cancel(); } catch (e) {} } });
$('optMusic').addEventListener('click', () => { musicOn = !musicOn; META.music = musicOn; saveMeta(); syncOpts(); setMix(G.state === 'play'); });
let giveUpArmed = false;
$('giveUp').addEventListener('click', e => {
  if (e && e.stopPropagation) e.stopPropagation();
  if (!giveUpArmed) { giveUpArmed = true; $('giveUp').textContent = 'Really give up?'; return; }
  giveUpArmed = false;
  G.gaveUp = true; G.paused = false; pauseShown = false; $('paused').hidden = true;
  die();
});
$('paused').addEventListener('click', () => { resumeFromPause(); });
$('resume').addEventListener('click', () => {
  if (!pendingRun) return;
  initAudio(); const at = pendingRun.level; resumeRun(pendingRun); pendingRun = null;
  $('menu').hidden = true; $('over').hidden = true; $('hud').hidden = false;
  cam.x = G.player.x - W / Z / 2; cam.y = G.player.y - H / Z / 2;
  announce('Back into the dark, at depth ' + at, '#8fd3ff');
});
/* and a way to be rid of it, so an old run cannot sit there for ever */
$('abandon').addEventListener('click', () => {
  clearRun(); refreshResume();
  const f = document.querySelector('#cards .card'); if (f) f.focus({ preventScroll: true });
});
$('barrowBtn').addEventListener('click', () => showBarrow(true));
$('barrowBack').addEventListener('click', () => showBarrow(false));
$('oBarrow').addEventListener('click', () => { $('over').hidden = true; showMenu(); showBarrow(true); });
$('change').addEventListener('click', () => { startGame(G.clsKeys); showMenu(); });

const mmss = s => Math.floor(s / 60) + ':' + String(Math.floor(s % 60)).padStart(2, '0');
function showOver() {
  const P = G.players[0];
  const won = G.state === 'won';
  $('oTitle').textContent = won ? 'The Hollow is still.' : G.won ? 'You carried it out of the dark.'
    : G.gaveUp ? 'You turned back.' : 'Swallowed by the deep.';
  $('oLine').textContent = won
    ? 'You put down ' + HEART_NAME + ' at depth ' + G.level + '. Climb out with it, or see what lies below.'
    : (G.gaveUp ? 'You left the dark at depth ' : 'You reached depth ') + G.level +
      ' of ' + (G.zone ? G.zone.name : 'the dark') + '.';
  $('deeper').hidden = !won;
  const rows = [
    ['Score', G.score + (G.score >= G.best ? '  \u00b7  a new best' : '  \u00b7  best ' + G.best)],
    ['Depth reached', String(G.level)],
    ['Longest chain', String(G.comboBest || 0)],
    ['Delver level', G.players.map(p => p.cls.name + ' ' + p.plvl).join(', ')],
    ['Monsters slain', (G.kills || 0) + (G.elites ? '  \u00b7  ' + G.elites + ' elite' : '') + (G.bosses ? '  \u00b7  ' + G.bosses + (G.bosses === 1 ? ' warden' : ' wardens') : '')],
    ['Gold carried', String(G.gold)],
    ['Time below', mmss(G.runT || 0)]
  ];
  /* the one row that answers "what went wrong" */
  {
    const deep = Math.round(G.tollDeep || 0), foes = Math.round(G.tollFoes || 0), all = deep + foes;
    if (all > 0) {
      const pc = n => Math.round(n / all * 100);
      rows.splice(3, 0, [won || G.won ? 'What wore you down' : 'What took you',
        'the deep ' + deep + '  (' + pc(deep) + '%)  \u00b7  its creatures ' + foes + '  (' + pc(foes) + '%)']);
    }
  }
  if (G.won) rows.unshift([HEART_NAME, 'put down at depth ' + FINAL_DEPTH + '  \u00b7  ' + (META.wins || 1) + (META.wins === 1 ? ' time' : ' times') + ' in all']);
  const allPacts = [];
  for (const p of G.players) for (const q of (p.pacts || [])) allPacts.push(q.name);
  if (allPacts.length) rows.push(['Pacts taken', allPacts.join(', ')]);
  const allBoons = [];
  for (const p of G.players) for (const b of (BOONS[p.cls.key] || [])) if (bn(p, b.id)) allBoons.push(b.name);
  if (allBoons.length) rows.push(['Boons learned', allBoons.join(', ')]);
  const worn = [];
  for (const p of G.players) for (const s of SLOTS) if (p.gear[s]) worn.push(p.gear[s]);
  const wrap = $('oStats'); wrap.innerHTML = '';
  for (const [k, v] of rows) {
    const r = document.createElement('div'); r.className = 'orow';
    const a = document.createElement('span'); a.textContent = k;
    const b = document.createElement('b'); b.textContent = v;
    r.appendChild(a); r.appendChild(b); wrap.appendChild(r);
  }
  if (worn.length) {
    const r = document.createElement('div'); r.className = 'orow';
    const a = document.createElement('span'); a.textContent = 'Carried out';
    const b = document.createElement('b');
    worn.forEach((it, i) => { const sp = document.createElement('span'); sp.style.color = it.col; sp.textContent = (i ? ' \u00b7 ' : '') + it.name; b.appendChild(sp); });
    r.appendChild(a); r.appendChild(b); wrap.appendChild(r);
  }
  $('oEchLbl').textContent = won ? 'Echoes waiting above' : 'Echoes earned';
  $('oEch').textContent = '+' + (won ? runEchoes() : (G.earned || 0));
  $('oEchTot').textContent = String(META.echoes);
  $('over').hidden = false; $('hud').hidden = true;
  (G.state === 'won' ? $('deeper') : $('again')).focus({ preventScroll: true });
}
/* ---------- the Barrow: spend what the last run left ---------- */
/* Each zone holds three depths and its warden stands on the last of them,
   so zone i runs from 3i+1 to 3i+3. You cannot reach 3i+4 without having
   put that warden down, which is what makes one number enough. */
function renderDeep() {
  const wrap = $('deepRows'); if (!wrap) return;
  wrap.innerHTML = '';
  const deepest = META.deepest || 1, wins = META.wins || 0;
  const row = (col, name, blurb, right, dim) => {
    const r = document.createElement('div'); r.className = 'srow'; r.style.setProperty('--c', col);
    if (dim) r.style.opacity = '.55';
    const info = document.createElement('div');
    const nm = document.createElement('span'); nm.className = 'nm'; nm.textContent = name; info.appendChild(nm);
    const bl = document.createElement('span'); bl.className = 'bl'; bl.textContent = blurb; info.appendChild(bl);
    r.appendChild(info);
    const bw = document.createElement('div'); bw.className = 'sbuy';
    const s = document.createElement('span'); s.className = 'bl'; s.textContent = right; bw.appendChild(s);
    r.appendChild(bw); wrap.appendChild(r);
  };
  for (let i = 0; i < ZONES.length; i++) {
    const z = ZONES[i], first = 3 * i + 1, last = 3 * i + 3;
    const seen = deepest >= first, felled = deepest >= last + 1;
    row(seen ? z.amb : '#454c5e',
        'Depths ' + first + '\u2013' + last + (seen ? '  \u00b7  ' + z.name : ''),
        seen ? z.boss + ' guards the key at depth ' + last + '.' : 'You have not been this deep.',
        felled ? 'Felled' : seen ? 'Still standing' : '\u2014',
        !seen);
  }
  const won = wins > 0;
  row(won ? '#ffd24a' : '#454c5e',
      'Depth ' + FINAL_DEPTH + '  \u00b7  The Hollow',
      won ? HEART_NAME + ' has been put down.'
          : deepest >= FINAL_DEPTH ? HEART_NAME + ' is still beating.'
          : HEART_NAME + ' waits at the bottom.',
      won ? 'Taken ' + wins + (wins === 1 ? ' time' : ' times') : '\u2014',
      !won);
}
function renderBarrow() {
  $('barrowSub').textContent = 'You have ' + META.echoes + ' echoes. ' + (META.runs || 0) + ' descent' + (META.runs === 1 ? '' : 's') + ', deepest reach ' + (META.deepest || 1) + ' of ' + FINAL_DEPTH + '.';
  renderDeep();
  const wrap = $('barrowRows'); wrap.innerHTML = '';
  for (const p of PERKS) {
    const lv = perkLv(p.id), maxed = lv >= p.max, cost = perkCost(p);
    const row = document.createElement('div'); row.className = 'srow'; row.style.setProperty('--c', p.col);
    const info = document.createElement('div');
    const nm = document.createElement('span'); nm.className = 'nm'; nm.textContent = p.name; info.appendChild(nm);
    const bl = document.createElement('span'); bl.className = 'bl'; bl.textContent = p.desc + '  (' + lv + ' of ' + p.max + ')'; info.appendChild(bl);
    row.appendChild(info);
    const bw = document.createElement('div'); bw.className = 'sbuy';
    const b = document.createElement('button'); b.type = 'button'; b.className = 'btn buy';
    b.textContent = maxed ? 'Maxed' : cost + ' echoes';
    b.disabled = maxed || META.echoes < cost;
    if (!maxed && META.echoes < cost) b.title = 'Not enough echoes';
    b.addEventListener('click', () => { if (buyPerk(p.id)) { sfx('coin'); renderBarrow(); } });
    bw.appendChild(b); row.appendChild(bw); wrap.appendChild(row);
  }
}
function showBarrow(on) {
  $('barrow').hidden = !on;
  /* the menu is behind it and shows through, so it waits outside */
  $('menu').hidden = !!on;
  if (on) { renderBarrow(); $('barrowBack').focus({ preventScroll: true }); }
  else { $('barrow').scrollTop = 0; }
}
let lootShown = false, pauseShown = false;
/* What you are carrying, and what it has made of you. */
function showPaused() {
  const wrap = $('pauseGear'); wrap.innerHTML = '';
  const sheets = [], extras = [];
  for (const P of G.players) {
    const who = G.co ? 'P' + (P.idx + 1) + ' \u00b7 ' : '';
    sheets.push(who + sheetLine(P));
    for (const slot of SLOTS) {
      wrap.appendChild(gearCard(who + slot, P.gear[slot], -1, '', P, null));
    }
    const boons = (BOONS[P.cls.key] || []).filter(b => bn(P, b.id)).map(b => b.name);
    const pacts = (P.pacts || []).map(q => q.name);
    const bits = ['Special: ' + specialLine(P.cls)];
    if (boons.length) bits.push('Boons: ' + boons.join(', '));
    if (pacts.length) bits.push('Pacts: ' + pacts.join(', '));
    extras.push(who + bits.join('  \u00b7  '));
  }
  $('pauseS').textContent = sheets.join('   |   ');
  $('pauseExtra').textContent = extras.join('   |   ');
  $('pauseExtra').hidden = extras.length === 0;
  $('pauseKeys').textContent = btnsOn
    ? 'Left half of the screen moves you \u00b7 right half aims and attacks \u00b7 the buttons are dash, special and potion.'
    : 'WASD move \u00b7 mouse aim \u00b7 click or Space attack \u00b7 Shift dash \u00b7 E special \u00b7 F potion \u00b7 P pause.';
  giveUpArmed = false; $('giveUp').textContent = 'Give up this descent';
  $('pauseHint').textContent = btnsOn ? 'Tap anywhere to carry on.' : 'Press P, or click, to carry on.';
  $('hud').hidden = true;
  $('paused').hidden = false;
}
function sheetLine(P) {
  const pct = x => Math.round((x - 1) * 100);
  let line = P.cls.name + ' \u00b7 level ' + P.plvl + ' \u00b7 ' + P.max + ' max health, damage +' + pct(P.dmgMul) + '%, speed +' + pct(P.spdMul) + '%, attacks ' + pct(1 / P.cdMul) + '% faster.';
  if (P.sets && P.sets.length) {
    line += ' Wearing ' + P.sets.map(s => s.name + (s.n >= 3 ? ' in full' : '')).join(' and ') + '.';
  }
  return line;
}
function gearCard(label, item, idx, hint, who, breaks) {
  const b = document.createElement('button'); b.type = 'button'; b.className = 'card';
  b.style.setProperty('--c', item ? item.col : '#3a4152');
  const r = document.createElement('span'); r.className = 'itemrar'; r.style.color = item ? item.col : '#98a0b3';
  r.textContent = label; b.appendChild(r);
  const n = document.createElement('span'); n.className = 'nm'; n.textContent = item ? item.name : 'Nothing worn'; b.appendChild(n);
  const s = document.createElement('span'); s.className = 'itemstats';
  if (item) for (const line of itemLines(item, who)) { const d = document.createElement('span'); d.textContent = line; s.appendChild(d); }
  else { const d = document.createElement('span'); d.textContent = 'That slot is empty.'; s.appendChild(d); }
  b.appendChild(s);
  if (breaks) {
    const w = document.createElement('span'); w.className = 'setwarn';
    w.textContent = 'Taking this breaks ' + breaks;
    b.appendChild(w);
  }
  const h = document.createElement('span'); h.className = 'rare'; h.textContent = hint; b.appendChild(h);
  /* idx below zero means this card is being shown, not offered */
  if (idx >= 0) b.addEventListener('click', () => chooseUp(idx));
  else b.tabIndex = -1;
  return b;
}
function showLoot() {
  const o = G.offer, P = o.P, wrap = $('lootCards'); wrap.innerHTML = '';
  if (o.kind === 'gear') {
    $('lootT').textContent = (G.co ? 'P' + (P.idx + 1) + ' finds ' : 'You find ') + o.item.name;
    $('lootS').textContent = sheetLine(P);
    $('lootHint').textContent = 'Press 1 to equip, 2 to leave it.';
    /* the set the worn piece is holding up, if swapping it would drop the
       count back under two */
    let breaks = null;
    if (o.cur && o.cur.set && setLive(P, o.cur.set) && setWorn(P, o.cur.set, o.cur.slot) + (o.item.set === o.cur.set ? 1 : 0) < 2) {
      const S = SETS.find(x => x.id === o.cur.set);
      breaks = S ? S.name : null;
    }
    wrap.appendChild(gearCard('New \u00b7 ' + (RARITY[o.item.rar] || {}).name, o.item, 0, '1 \u00b7 Equip', P, breaks));
    wrap.appendChild(gearCard('Worn \u00b7 ' + o.item.slot, o.cur, 1, '2 \u00b7 Keep this', P, null));
  } else if (o.kind === 'pact') {
    const sh = o.shrine.sh, p = sh.pact, mys = sh.kind === 'mystery', col = shrineCol(sh);
    $('lootT').textContent = (G.co ? 'P' + (P.idx + 1) + ': ' : '') + (mys ? 'An altar you cannot read' : isPact(p) ? 'The altar wants something back' : 'A font burns clean');
    $('lootS').textContent = sheetLine(P);
    $('lootHint').textContent = 'Press 1 to take it, 2 to walk away. Walking away leaves the font standing.';
    const take = document.createElement('button'); take.type = 'button'; take.className = 'card'; take.style.setProperty('--c', col);
    const r1 = document.createElement('span'); r1.className = 'itemrar'; r1.style.color = col;
    r1.textContent = mys ? 'Unknown' : isPact(p) ? 'Pact' : 'Blessing'; take.appendChild(r1);
    const n1 = document.createElement('span'); n1.className = 'nm'; n1.textContent = '1 \u00b7 ' + (mys ? 'Drink anyway' : p.name); take.appendChild(n1);
    if (mys) {
      const d1 = document.createElement('span'); d1.className = 'bl';
      d1.textContent = 'The carving has worn away. It may bless you, or it may want paying.';
      take.appendChild(d1);
    } else {
      const d1 = document.createElement('span'); d1.className = 'bl'; d1.textContent = p.good; take.appendChild(d1);
      if (p.bad) { const d2 = document.createElement('span'); d2.className = 'bl'; d2.style.color = '#e0556b'; d2.textContent = p.bad; take.appendChild(d2); }
    }
    take.addEventListener('click', () => chooseUp(0)); wrap.appendChild(take);
    const skip = document.createElement('button'); skip.type = 'button'; skip.className = 'card'; skip.style.setProperty('--c', '#98a0b3');
    const r2 = document.createElement('span'); r2.className = 'itemrar'; r2.style.color = '#98a0b3'; r2.textContent = 'Leave'; skip.appendChild(r2);
    const n2 = document.createElement('span'); n2.className = 'nm'; n2.textContent = '2 \u00b7 Walk away'; skip.appendChild(n2);
    const d3 = document.createElement('span'); d3.className = 'bl'; d3.textContent = 'The font stays lit. You may come back to it.'; skip.appendChild(d3);
    skip.addEventListener('click', () => chooseUp(1)); wrap.appendChild(skip);
  } else if (o.kind === 'boon') {
    $('lootT').textContent = (G.co ? 'P' + (P.idx + 1) + ': ' : '') + 'A new way to fight';
    $('lootS').textContent = sheetLine(P);
    $('lootHint').textContent = (o.opts.length > 1
      ? 'Click a card or press 1' + (o.opts.length > 2 ? ', 2 or 3' : ' or 2') + '.'
      : 'Click the card or press 1.') + ' This one changes how your attack works.';
    o.opts.forEach((b, i) => {
      const btn = document.createElement('button'); btn.type = 'button'; btn.className = 'card'; btn.style.setProperty('--c', P.cls.col);
      const r = document.createElement('span'); r.className = 'itemrar'; r.style.color = P.cls.col; r.textContent = 'Boon'; btn.appendChild(r);
      const n = document.createElement('span'); n.className = 'nm'; n.textContent = (i + 1) + '. ' + b.name; btn.appendChild(n);
      const d = document.createElement('span'); d.className = 'bl'; d.textContent = b.desc; btn.appendChild(d);
      btn.addEventListener('click', () => chooseUp(i)); wrap.appendChild(btn);
    });
  } else {
    $('lootT').textContent = G.co ? 'P' + (P.idx + 1) + ' opens a chest' : 'Chest opened';
    $('lootS').textContent = sheetLine(P);
    $('lootHint').textContent = 'Click a card or press 1, 2 or 3.';
    o.opts.forEach((u, i) => {
      const info = upInfo(P, u.id, u.m), b = document.createElement('button'); b.type = 'button'; b.className = 'card'; b.style.setProperty('--c', info.col);
      const n = document.createElement('span'); n.className = 'nm'; n.textContent = (i + 1) + '. ' + info.name; b.appendChild(n);
      const d = document.createElement('span'); d.className = 'bl'; d.textContent = info.desc; b.appendChild(d);
      if (u.m > 1) { const r = document.createElement('span'); r.className = 'rare'; r.textContent = 'Rare'; b.appendChild(r); }
      b.addEventListener('click', () => chooseUp(i)); wrap.appendChild(b);
    });
  }
  $('hud').hidden = true;
  $('loot').hidden = false;
}
function chooseUp(i) {
  const o = G.offer;
  if (G.state !== 'offer' || !o) return;
  if (o.kind === 'pact') { if (i !== 0 && i !== 1) return; }
  else if (o.kind === 'gear' ? (i !== 0 && i !== 1) : !o.opts[i]) return;
  if (o.kind === 'boon' && !o.opts[i]) return;
  applyUpgrade(i); $('loot').hidden = true; lootShown = false;
  if (G.state === 'play') $('hud').hidden = false;
}

/* ---------- loop ---------- */
let last = performance.now(), overShown = false, wasPlaying = false;
let frameErrs = 0;
function frameError(e) {
  if (frameErrs++ < 3 && typeof console !== 'undefined' && console.error) {
    console.error('Hollowdeep: a frame failed and was skipped', e);
    if (frameErrs === 3) console.error('Hollowdeep: further frame errors will not be reported');
  }
}
function frame(now) {
  /* before anything that could throw, so a bad frame costs a frame */
  requestAnimationFrame(frame);
  const _t0 = performance.now();
  try {
  const dt = Math.min(.05, (now - last) / 1000); last = now; clock += dt;
  musicTick();
  const playing = G.state === 'play' || G.state === 'offer' || G.state === 'clear';
  if (playing !== wasPlaying) { wasPlaying = playing; setMix(playing); }
  if (G.state === 'play' && !G.paused) { readInput(); update(dt); }
  else if (G.state === 'clear' && !G.paused) clearTick(dt);
  else if (G.state === 'menu') { for (const t of G.torches) t.ph += 0; }
  if ((G.state === 'dead' || G.state === 'won') && !overShown) { overShown = true; showOver(); }
  if (G.state !== 'dead' && G.state !== 'won') overShown = false;
  if (G.state === 'shop' && !shopShown) showShop(); else if (G.state !== 'shop' && shopShown) { shopShown = false; $('shop').hidden = true; if (G.state === 'play') $('hud').hidden = false; }
  /* the touch buttons and the minimap belong to play, and the HUD already
     knows when that is */
  { const st = $('stage'), on = !$('hud').hidden;
    if (st && st.classList && st.dataset.play !== (on ? '1' : '0')) {
      st.dataset.play = on ? '1' : '0';
      st.classList.toggle('playing', on);
      if (document.body && document.body.classList) document.body.classList.toggle('playing', on);
      try { btnsOn = getComputedStyle($('dashBtn')).display !== 'none'; } catch (e) {}
    } }
  if (G.state === 'offer' && !lootShown) { lootShown = true; showLoot(); }
  else if (G.state !== 'offer' && lootShown) {
    lootShown = false; $('loot').hidden = true;
    if (G.state === 'play') $('hud').hidden = false;
  }
  const wantPause = G.paused && G.state === 'play';
  if (wantPause && !pauseShown) { pauseShown = true; showPaused(); }
  else if (!wantPause && pauseShown) {
    pauseShown = false; $('paused').hidden = true;
    if (G.state === 'play') $('hud').hidden = false;
  }
  if (W && H && G.map) { if (G.state === 'play' || G.state === 'offer' || G.state === 'shop' || G.state === 'clear') updateHud(); render(); }
  } catch (e) { frameError(e); }
  perfTick(performance.now() - _t0);
}
storageWorks();
loadMeta(); G.best = META.best || 0;
pendingRun = loadRun();
{ /* a trophy line, once there is something to show */
  const w = META.wins || 0, el = $('menuWins');
  if (el && w > 0) el.textContent = '  \u00b7  Heart taken ' + w + (w === 1 ? ' time' : ' times');
}
voiceOn = META.voice !== false; musicOn = META.music !== false;
if (META.reduceMotion === undefined || META.reduceMotion === null) {
  try { META.reduceMotion = !!(window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches); } catch (e) { META.reduceMotion = false; }
}
reduceMotion = !!META.reduceMotion;
buildMenu(); startGame('bulwark'); showMenu();
requestAnimationFrame(frame);
</script>

</body></html>