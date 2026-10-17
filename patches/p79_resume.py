from patch import edit, run

L = 'part_logic.js'

# --- a descent lived or died with the browser tab -------------------------
# Twenty minutes down, and a reload, a crash or a phone call took the lot.
# Nothing was written anywhere: META held the best score and the echoes, and
# the run itself existed only in memory. Every other kind of loss in this
# game is earned; that one was not.
#
# The checkpoint is written the moment a floor begins. What comes back is the
# top of the floor you had reached, with the delver you had made: gear,
# levels, boons, pacts, gold, keys, flasks. The floor itself is generated
# fresh, and that is the honest cost -- you keep what you earned, not where
# you were standing.
#
# Dying clears it, so death still means what it meant.

# the delver build is pulled out of startGame so a resumed run can rebuild
# the same shape before laying the saved progress back over it
edit(L, """function startGame(list) {
  if (!Array.isArray(list)) list = [list];
  G.clsKeys = list; G.clsKey = list[0]; G.co = list.length > 1;
  G.players = list.map((k, i) => {
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
  });""",
     """function makeDelver(k, i) {
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
  G.players = list.map((k, i) => makeDelver(k, i));""")

# --- the store -----------------------------------------------------------
edit(L, """function saveMeta() { try { localStorage.setItem(META_KEY, JSON.stringify(META)); } catch (e) {} }""",
     """function saveMeta() { try { localStorage.setItem(META_KEY, JSON.stringify(META)); } catch (e) {} }
/* ---------- the run you left behind ---------- */
const RUN_KEY = 'hollowdeep-run';
let pendingRun = null;
function saveRun() {
  if (!G.players || !G.players.length) return;
  try {
    localStorage.setItem(RUN_KEY, JSON.stringify({
      v: 1, cls: G.clsKeys, level: G.level, score: G.score, gold: G.gold, keys: G.keys,
      bombs: G.bombs, kills: G.kills, drops: G.drops, runT: G.runT, comboBest: G.comboBest, won: !!G.won,
      ps: G.players.map(P => ({
        hp: P.hp, down: !!P.down, up: P.up, gear: P.gear, xp: P.xp, plvl: P.plvl,
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
    keys: metaNum(raw.keys, 0, 0), bombs: metaNum(raw.bombs, 0, 0), kills: metaNum(raw.kills, 0, 0),
    drops: metaNum(raw.drops, 0, 0), runT: Math.max(0, num(raw.runT, 0)),
    comboBest: metaNum(raw.comboBest, 0, 0), won: !!raw.won, ps: []
  };
  for (const p of ps) {
    if (!p || typeof p !== 'object') { clearRun(); return null; }
    const up = p.up && typeof p.up === 'object' ? p.up : {};
    const g = p.gear && typeof p.gear === 'object' ? p.gear : {};
    for (const slot of SLOTS) if (!gearOk(g[slot] === undefined ? null : g[slot])) { clearRun(); return null; }
    out.ps.push({
      hp: num(p.hp, 1), down: !!p.down,
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
    P.down = s.down && r.cls.length > 1;
    P.hp = P.down ? 0 : Math.max(1, Math.min(P.max, s.hp));
  });
  G.player = G.players[0];
  G.gold = r.gold; G.keys = r.keys; G.bombs = r.bombs; G.kills = r.kills; G.drops = r.drops;
  G.runT = r.runT; G.comboBest = r.comboBest; G.score = r.score; G.won = r.won;
  G.combo = 0; G.comboT = 0; G.earned = 0; G.zones = []; G.timers = []; G.bolts = [];
  G.voice = null; G.flash = 0; G.offer = null; G.offerQ = []; G.wares = []; G.winPending = false;
  G.level = r.level; genLevel(); G.state = 'play'; G.paused = false;
  /* written again at once, so a second reload still finds the run */
  saveRun();
}""")

# --- where it is written and wiped ---------------------------------------
# A floor is the checkpoint. Note that startGame itself must NOT write: boot
# calls it once to have something behind the menu, and "Change delver" calls
# it again -- either would quietly destroy the very run being offered.
edit(L, """  sfx('stairs'); genLevel();
}""",
     """  sfx('stairs'); genLevel(); saveRun();
}""")

edit(L, """  G.state = 'dead'; bankRun();""",
     """  G.state = 'dead'; bankRun(); clearRun();""")

edit(L, """function begin(list) { initAudio(); startGame(list); $('menu').hidden = true; $('over').hidden = true; $('hud').hidden = false; cam.x = G.player.x - W / Z / 2; cam.y = G.player.y - H / Z / 2; }""",
     """function begin(list) { initAudio(); startGame(list); saveRun(); $('menu').hidden = true; $('over').hidden = true; $('hud').hidden = false; cam.x = G.player.x - W / Z / 2; cam.y = G.player.y - H / Z / 2; }""")

# --- and offered ---------------------------------------------------------
edit(L, """function showMenu() { syncOpts(); setMode(mode); $('menu').hidden = false; $('over').hidden = true; $('barrow').hidden = true; $('hud').hidden = true; G.state = 'menu'; $('best').textContent = G.best; $('echoes').textContent = META.echoes; const f = document.querySelector('#cards .card'); if (f) f.focus({ preventScroll: true }); }""",
     """function refreshResume() {
  const row = $('resumeRow'); if (!row) return;
  row.hidden = !pendingRun;
  if (pendingRun) $('resume').textContent = 'Carry on from depth ' + pendingRun.level;
}
function showMenu() { syncOpts(); setMode(mode); $('menu').hidden = false; $('over').hidden = true; $('barrow').hidden = true; $('hud').hidden = true; G.state = 'menu'; $('best').textContent = G.best; $('echoes').textContent = META.echoes; refreshResume(); const f = pendingRun ? $('resume') : document.querySelector('#cards .card'); if (f) f.focus({ preventScroll: true }); }""")

edit(L, """$('barrowBtn').addEventListener('click', () => showBarrow(true));""",
     """$('resume').addEventListener('click', () => {
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
$('barrowBtn').addEventListener('click', () => showBarrow(true));""")

edit(L, """loadMeta(); G.best = META.best || 0;""",
     """loadMeta(); G.best = META.best || 0;
pendingRun = loadRun();""")

run()
