from patch import edit, run

L = 'part_logic.js'
H = 'part_head.html'

# --- something to beat ----------------------------------------------------
# The depth curve went flat from seventeen on: once a run survived that far it
# simply kept going, because nothing was waiting at the bottom. Twenty-one is
# one full turn of the six zones plus a last descent, and about one simulated
# run in twenty got there.
edit(L, """const BOSS_KIND = ['count', 'caller', 'maw', 'pyre', 'chorister', 'obsidian'];""",
     """/* it remembers every warden you put down on the way here */
BOSSES.heart = { spr: 'boss_vampire', sc: 1.62, fy: 22, bar: -104, r: 30, hpm: 2.3, spdm: .88, dmgm: 1.25, glow: '#ff3b5c',
  acts: { 1: ['slam', 'wail', 'volley', 'burst'],
          2: ['pillars', 'shards', 'raise', 'burst', 'wail'],
          3: ['ward', 'rampage', 'pillars', 'shards', 'wail', 'comet'] } };
const FINAL_DEPTH = 21;
const isFinalLvl = L => L === FINAL_DEPTH;
const HEART_NAME = 'The Hollow Heart';
const BOSS_KIND = ['count', 'caller', 'maw', 'pyre', 'chorister', 'obsidian'];""")

# --- the last depth puts the Heart in the key room ------------------------
edit(L, """  if (isBossLvl(G.level)) {
    spawnFoe('warden', keyRoom.cx * T + T / 2, keyRoom.cy * T + T / 2);
    const b = G.enemies[G.enemies.length - 1]; b.name = G.zone.boss; b.col = G.zone.bcol;""",
     """  if (isBossLvl(G.level)) {
    spawnFoe('warden', keyRoom.cx * T + T / 2, keyRoom.cy * T + T / 2);
    const b = G.enemies[G.enemies.length - 1];
    if (isFinalLvl(G.level)) {
      /* the door is not the obstacle down here, the Heart is */
      b.kind = 'heart'; b.name = HEART_NAME; b.col = '#ff3b5c';
      const K = BOSSES.heart;
      b.r = K.r; b.max = Math.round(b.max * 2.3); b.hp = b.max;
      b.dmg = Math.round(b.dmg * 1.25); b.spd *= .88;
      G.keys = Math.max(G.keys, 1);
    } else { b.name = G.zone.boss; b.col = G.zone.bcol; }""")

# --- the banner says where you are, and what is down here -----------------
edit(L, """  G.banner = { txt: 'Depth ' + G.level, sub: G.zone.name""",
     """  G.banner = { txt: isFinalLvl(G.level) ? 'Depth ' + G.level : 'Depth ' + G.level, sub: isFinalLvl(G.level) ? 'The Hollow \\u00b7 ' + HEART_NAME + ' waits' : G.zone.name""")

# --- killing it is the end of the descent, not another key ----------------
edit(L, """  if (e.boss) {
    G.items.push({ kind: 'key', x: e.x, y: e.y, t: 0 }); G.items.push({ kind: 'chest', x: e.x + 28, y: e.y, t: 0, big: true });""",
     """  if (e.boss && e.kind === 'heart') {
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
    G.items.push({ kind: 'key', x: e.x, y: e.y, t: 0 }); G.items.push({ kind: 'chest', x: e.x + 28, y: e.y, t: 0, big: true });""")

# --- banking a run, won or lost, happens in one place ---------------------
edit(L, """function die() {
  G.state = 'dead'; G.best = Math.max(G.best, G.score);
  G.earned = Math.max(1, Math.round(G.gold * .25 + G.score / 40 + (G.level - 1) * 8));
  META.echoes += G.earned; META.best = G.best; META.runs = (META.runs || 0) + 1;
  META.deepest = Math.max(META.deepest || 1, G.level);
  saveMeta();
  announce('Swallowed by the deep', '#d9534f');
}""",
     """function bankRun() {
  G.best = Math.max(G.best, G.score);
  G.earned = Math.max(1, Math.round(G.gold * .25 + G.score / 40 + (G.level - 1) * 8)) * (G.won ? 2 : 1);
  META.echoes += G.earned; META.best = G.best; META.runs = (META.runs || 0) + 1;
  META.deepest = Math.max(META.deepest || 1, G.level);
  saveMeta();
}
function die() {
  if (G.state === 'dead') return;
  G.state = 'dead'; bankRun();
  announce(G.won ? 'You carried the Heart out of the dark' : 'Swallowed by the deep', G.won ? '#ffd24a' : '#d9534f');
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
  G.timers.push({ t: 2.6, fn: () => { if (G.state === 'play') G.state = 'won'; } });
}""")

# --- the overlay has to be able to say something else ---------------------
edit(H, """      <h2>Swallowed by the deep.</h2>""",
     """      <h2 id="oTitle">Swallowed by the deep.</h2>""")

edit(H, """        <button class="btn" id="again" type="button">Descend again</button>""",
     """        <button class="btn" id="deeper" type="button" hidden>Go deeper</button>
        <button class="btn" id="again" type="button">Descend again</button>""")

edit(L, """function showOver() {
  const P = G.players[0];
  $('oLine').textContent = 'You reached depth ' + G.level + ' of ' + (G.zone ? G.zone.name : 'the dark') + '.';""",
     """function showOver() {
  const P = G.players[0];
  const won = G.state === 'won';
  $('oTitle').textContent = won ? 'The Hollow is still.' : G.won ? 'You carried it out of the dark.' : 'Swallowed by the deep.';
  $('oLine').textContent = won
    ? 'You put down ' + HEART_NAME + ' at depth ' + G.level + '. Climb out with it, or see what lies below.'
    : 'You reached depth ' + G.level + ' of ' + (G.zone ? G.zone.name : 'the dark') + '.';
  $('deeper').hidden = !won;""")

edit(L, """  $('over').hidden = false; $('hud').hidden = true; $('again').focus({ preventScroll: true });""",
     """  $('over').hidden = false; $('hud').hidden = true;
  (G.state === 'won' ? $('deeper') : $('again')).focus({ preventScroll: true });""")

edit(L, """$('again').addEventListener('click', () => begin(G.clsKeys));""",
     """$('again').addEventListener('click', () => { if (G.state === 'won') { G.state = 'dead'; bankRun(); } begin(G.clsKeys); });
$('deeper').addEventListener('click', () => {
  $('over').hidden = true; $('hud').hidden = false;
  G.state = 'play'; overShown = false;
  announce('Deeper, then', '#ffd24a');
});""")

# --- the run summary, and a trophy that persists --------------------------
edit(L, """    ['Time below', mmss(G.runT || 0)]
  ];""",
     """    ['Time below', mmss(G.runT || 0)]
  ];
  if (G.won) rows.unshift([HEART_NAME, 'put down at depth ' + FINAL_DEPTH + '  \\u00b7  ' + (META.wins || 1) + (META.wins === 1 ? ' time' : ' times') + ' in all']);""")

edit(L, """const META = { best: 0, echoes: 0, perks: {}, runs: 0, deepest: 1, reduceMotion: false, voice: true, music: true };""",
     """const META = { best: 0, echoes: 0, perks: {}, runs: 0, deepest: 1, wins: 0, reduceMotion: false, voice: true, music: true };""")

edit(L, """  G.level = 1; G.score = 0; genLevel(); G.state = 'play'; G.paused = false;""",
     """  G.level = 1; G.score = 0; G.won = false; genLevel(); G.state = 'play'; G.paused = false;""")

# --- the overlay only ever appeared for a death --------------------------
edit(L, """  if (G.state === 'dead' && !overShown) { overShown = true; showOver(); }
  if (G.state !== 'dead') overShown = false;""",
     """  if ((G.state === 'dead' || G.state === 'won') && !overShown) { overShown = true; showOver(); }
  if (G.state !== 'dead' && G.state !== 'won') overShown = false;""")

run()
