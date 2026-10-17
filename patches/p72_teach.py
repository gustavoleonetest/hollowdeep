from patch import edit, run

L = 'part_logic.js'

# --- the game explained itself only in the paragraph nobody reads ---------
# The narrator remarks on things ("A key is found", "The thief escaped with
# your gold") but never tells you how the floor works. Everything a new
# player needs is in the menu blurb, which is a wall of text above a row of
# delver portraits: people click the portrait.
#
# Three lessons, each said once ever and then never again, at the moment the
# thing is actually in front of you. Remembered across runs, so this costs a
# returning player nothing.
edit(L, """const META = { best: 0, echoes: 0, perks: {}, runs: 0, deepest: 1, wins: 0, reduceMotion: false, voice: true, music: true };""",
     """const META = { best: 0, echoes: 0, perks: {}, runs: 0, deepest: 1, wins: 0, taught: {}, reduceMotion: false, voice: true, music: true };
const TAUGHT = [
  ['drain', 'Your health drains the whole way down. Food is the only thing that gives it back.'],
  ['crypt', 'A crypt. It keeps sending them up until you break it.'],
  ['door', 'The way down is locked. The key is somewhere on this floor.'],
];
function teach(id) {
  if (!META.taught || META.taught[id]) return;
  const row = TAUGHT.find(t => t[0] === id); if (!row) return;
  META.taught[id] = 1; saveMeta();
  announce(row[1], '#8fd3ff');
}""")

# keep it across runs, and do not trust what comes back off the disk
edit(L, """      META.perks = {};
      if (raw.perks && typeof raw.perks === 'object') {""",
     """      META.taught = {};
      if (raw.taught && typeof raw.taught === 'object') {
        for (const t of TAUGHT) if (raw.taught[t[0]]) META.taught[t[0]] = 1;
      }
      META.perks = {};
      if (raw.perks && typeof raw.perks === 'object') {""")

# --- the drain: said the first time it takes a bite with nothing near you -
edit(L, """  const dl = (.8 + Math.min(G.level, 8) * .2 + Math.max(0, G.level - 8) * .07) * om('drain', 1);
  P.hp -= dl * (G.co ? .85 : 1) * (P.drainMul || 1) * dt;""",
     """  const dl = (.8 + Math.min(G.level, 8) * .2 + Math.max(0, G.level - 8) * .07) * om('drain', 1);
  P.hp -= dl * (G.co ? .85 : 1) * (P.drainMul || 1) * dt;
  /* only once it has actually cost something, and only when nothing is
     hitting you, so the lesson is unmistakably about the drain */
  if (P.hp < P.max * .9 && !G.enemies.some(e => e.hp > 0 && !e.dead && Math.hypot(e.x - P.x, e.y - P.y) < 220)) teach('drain');""")

# --- a crypt: the first one you can actually see -------------------------
edit(L, """function updateNests(dt) {
  const alive = G.players.filter(p => !p.down);""",
     """function updateNests(dt) {
  const alive = G.players.filter(p => !p.down);
  if (alive.length) for (const n of G.nests) {
    if (n.hp > 0 && fogAt(n.x, n.y) < .4 &&
        alive.some(p => Math.hypot(p.x - n.x, p.y - n.y) < 260)) { teach('crypt'); break; }
  }""")

# --- the door: the first time you reach it with nothing to open it --------
edit(L, """      if (G.keys > 0) { G.keys--; G.map[ty * MW + tx] = 0; G.mapVer++; sfx('door'); G.shake = .15; burst((tx + .5) * T, (ty + .5) * T, '#a8743d', 16, 100); text(P.x, P.y - 18, 'Unlocked', '#f0a23c'); }""",
     """      if (G.keys > 0) { G.keys--; G.map[ty * MW + tx] = 0; G.mapVer++; sfx('door'); G.shake = .15; burst((tx + .5) * T, (ty + .5) * T, '#a8743d', 16, 100); text(P.x, P.y - 18, 'Unlocked', '#f0a23c'); }
      else teach('door');""")

run()
