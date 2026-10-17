from patch import edit, run

L = 'part_logic.js'
H = 'part_head.html'

# --- what survives a death -------------------------------------------------
edit(L, """/* ---------- the announcer ----------""",
     """/* ---------- what you carry out of the dark ----------
   A run always ends. Echoes are what is left of it, and they buy the small
   advantages that make the next descent reach further. */
const META_KEY = 'hollowdeep-meta';
const META = { best: 0, echoes: 0, perks: {}, runs: 0, deepest: 1, reduceMotion: false, voice: true, music: true };
function loadMeta() {
  try {
    const raw = JSON.parse(localStorage.getItem(META_KEY) || '{}');
    if (raw && typeof raw === 'object') for (const k in META) if (raw[k] !== undefined) META[k] = raw[k];
    if (!META.perks || typeof META.perks !== 'object') META.perks = {};
    const old = parseInt(localStorage.getItem('hollowdeep-best') || '0', 10);
    if (old > META.best) META.best = old;
  } catch (e) {}
}
function saveMeta() { try { localStorage.setItem(META_KEY, JSON.stringify(META)); } catch (e) {} }
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

/* ---------- the announcer ----------""")

# --- perks shape the delver you start with --------------------------------
edit(L, """      xp: 0, plvl: 1, buys: {} };
    recalc(P); P.hp = P.max; return P;
  });""",
     """      xp: 0, plvl: 1, buys: {} };
    P.up.hp += perkLv('vigour') * 12;
    P.up.crit += perkLv('edge') * .04;
    P.perkDrain = -perkLv('slow') * .08;
    P.perkGold = perkLv('purse') * .12;
    if (perkLv('relic')) P.gear.trinket = rollItem('trinket', RARITY.magic);
    recalc(P); P.hp = P.max; return P;
  });""")

edit(L, """  G.bombs = 1; G.drops = 0;""", """  G.bombs = 1 + perkLv('flask'); G.drops = 0; G.kills = 0; G.runT = 0; G.earned = 0;""")

edit(L, """      const gmul = 1 + (P.g ? P.g.gold : 0);""",
     """      const gmul = 1 + (P.g ? P.g.gold : 0) + (P.perkGold || 0);""")

# --- tally the run ---------------------------------------------------------
edit(L, """  G.score += Math.round(base * comboMult());
  gainXp(Math.max(1, Math.round(base * (.5 + G.level * .05))));""",
     """  G.score += Math.round(base * comboMult());
  G.kills = (G.kills || 0) + 1;
  if (e.elite) G.elites = (G.elites || 0) + 1;
  if (e.boss) G.bosses = (G.bosses || 0) + 1;
  gainXp(Math.max(1, Math.round(base * (.5 + G.level * .05))));""")

edit(L, """function update(dt) {
  if (G.state !== 'play') return;""",
     """function update(dt) {
  if (G.state !== 'play') return;
  G.runT = (G.runT || 0) + dt;""")

edit(L, """function die() {
  G.state = 'dead'; G.best = Math.max(G.best, G.score);
  try { localStorage.setItem('hollowdeep-best', String(G.best)); } catch (e) {}
}""",
     """function die() {
  G.state = 'dead'; G.best = Math.max(G.best, G.score);
  G.earned = Math.max(1, Math.round(G.gold * .25 + G.score / 40 + (G.level - 1) * 8));
  META.echoes += G.earned; META.best = G.best; META.runs = (META.runs || 0) + 1;
  META.deepest = Math.max(META.deepest || 1, G.level);
  saveMeta();
  announce('Swallowed by the deep', '#d9534f');
}""")

edit(L, """try { G.best = parseInt(localStorage.getItem('hollowdeep-best') || '0', 10) || 0; } catch (e) { G.best = 0; }""",
     """loadMeta(); G.best = META.best || 0;
voiceOn = META.voice !== false; musicOn = META.music !== false;""")

# --- the summary -----------------------------------------------------------
edit(L, """if (G.state === 'dead' && !overShown) { overShown = true; $('oLvl').textContent = G.level; $('oScore').textContent = G.score; $('oChain').textContent = G.comboBest; $('oBest').textContent = G.best; $('over').hidden = false; $('hud').hidden = true; $('again').focus({ preventScroll: true }); }""",
     """if (G.state === 'dead' && !overShown) { overShown = true; showOver(); }""")

edit(L, """let lootShown = false;""",
     """const mmss = s => Math.floor(s / 60) + ':' + String(Math.floor(s % 60)).padStart(2, '0');
function showOver() {
  const P = G.players[0];
  $('oLine').textContent = 'You reached depth ' + G.level + ' of ' + (G.zone ? G.zone.name : 'the dark') + '.';
  const rows = [
    ['Score', G.score + (G.score >= G.best ? '  \\u00b7  a new best' : '  \\u00b7  best ' + G.best)],
    ['Depth reached', String(G.level)],
    ['Longest chain', String(G.comboBest || 0)],
    ['Delver level', G.players.map(p => p.cls.name + ' ' + p.plvl).join(', ')],
    ['Monsters slain', (G.kills || 0) + (G.elites ? '  \\u00b7  ' + G.elites + ' elite' : '') + (G.bosses ? '  \\u00b7  ' + G.bosses + ' count' : '')],
    ['Gold carried', String(G.gold)],
    ['Time below', mmss(G.runT || 0)]
  ];
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
    worn.forEach((it, i) => { const sp = document.createElement('span'); sp.style.color = it.col; sp.textContent = (i ? ' \\u00b7 ' : '') + it.name; b.appendChild(sp); });
    r.appendChild(a); r.appendChild(b); wrap.appendChild(r);
  }
  $('oEch').textContent = '+' + (G.earned || 0);
  $('oEchTot').textContent = String(META.echoes);
  $('over').hidden = false; $('hud').hidden = true; $('again').focus({ preventScroll: true });
}
/* ---------- the Barrow: spend what the last run left ---------- */
function renderBarrow() {
  $('barrowSub').textContent = 'You have ' + META.echoes + ' echoes. ' + (META.runs || 0) + ' descent' + (META.runs === 1 ? '' : 's') + ', deepest reach ' + (META.deepest || 1) + '.';
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
function showBarrow(on) { $('barrow').hidden = !on; if (on) { renderBarrow(); $('barrowBack').focus({ preventScroll: true }); } }
let lootShown = false;""")

edit(L, """$('again').addEventListener('click', () => begin(G.clsKeys));""",
     """$('again').addEventListener('click', () => begin(G.clsKeys));
$('barrowBtn').addEventListener('click', () => showBarrow(true));
$('barrowBack').addEventListener('click', () => showBarrow(false));
$('oBarrow').addEventListener('click', () => { $('over').hidden = true; showMenu(); showBarrow(true); });""")

edit(L, """function showMenu() { setMode(mode); $('menu').hidden = false; $('over').hidden = true; $('hud').hidden = true; G.state = 'menu'; $('best').textContent = G.best;""",
     """function showMenu() { setMode(mode); $('menu').hidden = false; $('over').hidden = true; $('barrow').hidden = true; $('hud').hidden = true; G.state = 'menu'; $('best').textContent = G.best; $('echoes').textContent = META.echoes;""")

# --- markup ---------------------------------------------------------------
edit(H, """      <p class="sub">You reached depth <span class="big" id="oLvl">1</span> with a score of <span class="big" id="oScore">0</span>, on a best chain of <span class="big" id="oChain">0</span>. Best run: <span class="big" id="oBest">0</span></p>
      <div class="row">
        <button class="btn" id="again" type="button">Descend again</button>
        <button class="btn alt" id="change" type="button">Change delver</button>
      </div>""",
     """      <p class="sub" id="oLine"></p>
      <div class="srows" id="oStats"></div>
      <p class="sub">Echoes earned <b class="big" id="oEch">+0</b> \\u00b7 you now hold <b class="big" id="oEchTot">0</b></p>
      <div class="row">
        <button class="btn" id="again" type="button">Descend again</button>
        <button class="btn alt" id="oBarrow" type="button">The Barrow</button>
        <button class="btn alt" id="change" type="button">Change delver</button>
      </div>""")

edit(H, """      <div class="row" id="modes">
        <button class="btn on" type="button" data-m="1">One delver</button>
        <button class="btn alt" type="button" data-m="2">Two delvers, one keyboard</button>
      </div>""",
     """      <div class="row" id="modes">
        <button class="btn on" type="button" data-m="1">One delver</button>
        <button class="btn alt" type="button" data-m="2">Two delvers, one keyboard</button>
        <button class="btn alt" id="barrowBtn" type="button">The Barrow \\u00b7 <span id="echoes">0</span></button>
      </div>""")

edit(H, """  <div class="overlay" id="loot" hidden>""",
     """  <div class="overlay" id="barrow" hidden>
    <div class="sheet">
      <h2>The Barrow</h2>
      <p class="sub" id="barrowSub"></p>
      <div class="srows" id="barrowRows"></div>
      <div class="row"><button class="btn" id="barrowBack" type="button">Back</button></div>
    </div>
  </div>
  <div class="overlay" id="loot" hidden>""")

edit(H, """.shsec{margin:4px 0 -4px; font:400 22px/1 var(--display); color:var(--dim); letter-spacing:.04em}""",
     """.shsec{margin:4px 0 -4px; font:400 22px/1 var(--display); color:var(--dim); letter-spacing:.04em}
.orow{display:flex; gap:12px; justify-content:space-between; align-items:baseline; padding:7px 12px; background:var(--stone); border:1px solid var(--line); font-size:13px; color:var(--dim); min-width:0}
.orow b{color:var(--bone); font-weight:600; text-align:right; min-width:0}""")

run()
