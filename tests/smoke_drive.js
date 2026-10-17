/* Drives the loaded game: plays every class through many depths with sprites on
   and off, forcing elites, bloats, crits, hazards and the boss to actually run. */
const report = [];
const seen = new Set();
const origErr = console.error;

function step(n, label) {
  for (let i = 0; i < n; i++) {
    try {
      readInput();
      update(1 / 60);
      if (G.state === 'clear') clearTick(1 / 60);
      if (G.state === 'offer') { const o = G.offer; const n = o && o.kind === 'gear' ? 2 : o && o.kind === 'pact' ? 2 : (o && o.opts ? o.opts.length : 3); applyUpgrade(Math.floor(Math.random() * n)); }
      if (G.state === 'shop') { renderShop(); leaveShop(); }
      if (G.state === 'dead') { G.state = 'play'; for (const P of G.players) { P.down = false; P.hp = P.max; } }
      if (W && H && G.map) { updateHud(); render(); }
    } catch (e) {
      const key = label + '|' + (e && e.message);
      if (!seen.has(key)) { seen.add(key); report.push(label + ': ' + (e && e.stack || e)); }
      throw e;
    }
  }
}

function spritesOn(on) {
  for (const k in SPR) { const s = SPR[k]; s.ok = on; s.src = on ? { width: 1280, height: 1280 } : null; s.f = 1; }
}

let nFrames = 0;
for (const mode of ['sprites', 'procedural']) {
  spritesOn(mode === 'sprites');
  for (const cls of ['bulwark', 'ember', 'sable', 'thistle']) {
    startGame([cls]);
    /* 15 and 18 carry the last two wardens, 21 the Heart, 22 the wrap past it */
    for (const depth of [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,18,21,22]) {
      G.level = depth;
      genLevel();
      // make the level busy and exercise every new system
      const r = G.rooms[1] || G.rooms[0];
      for (let i = 0; i < 6; i++) { const p = roomPoint(r); spawnFoe(pickFoe(), p.x, p.y, i % 2 === 0); }
      for (let i = 0; i < 3; i++) { const p = roomPoint(r); spawnFoe('bloat', p.x, p.y, i === 0); }
      { const p = roomPoint(r); spawnFoe('warden', p.x, p.y); }
      for (const e of G.enemies) { e.alert = true; e.burn = 1.2; e.burnDmg = 3; }
      // crit every hit for a while so the crit paths all run
      const P = G.players[0];
      P.crit = 1; P.mast = 3;
      INS[0].mx = 1; INS[0].my = .3; INS[0].fire = true; INS[0].dash = depth % 3 === 0; INS[0].sp = depth % 4 === 0;
      step(70, mode + '/' + cls + '/depth' + depth);
      nFrames += 70;
      P.crit = 0;
      // drive the warden through all three phases and every attack it owns,
      // plus every act any other archetype could throw, so one depth still
      // exercises the whole repertoire
      const B = G.enemies.find(e => e.boss);
      if (B) {
        const own = BOSSES[B.kind] || BOSSES.count;
        const mine = [].concat(own.acts[1] || [], own.acts[2] || [], own.acts[3] || []);
        const every = [...new Set(mine.concat(Object.keys(BOSS_DUR)))];
        for (const frac of [.9, .4, .2]) {
          B.hp = B.max * frac; B.alert = true;
          for (const st of every) {
            B.st = st; B.stt = 0; B.ca = 1;
            B.immune = false; B.wardT = undefined; B.wardAdds = null;
            step(18, mode + '/boss/' + st); nFrames += 18;
          }
        }
        B.immune = false; B.wardT = undefined; B.wardAdds = null;
      }
      // force every spike through a full cycle while someone stands on it
      for (const h of G.hazards) { h.ph = h.cyc * .75; const Q = G.players[0]; Q.x = h.x; Q.y = h.y; Q.inv = 0; }
      step(40, mode + '/spikes/depth' + depth); nFrames += 40;
      // walk everyone onto the stairs to run the clear + shop path
      for (const Q of G.players) { Q.down = false; Q.hp = Q.max; Q.x = G.exit.x; Q.y = G.exit.y; }
      step(30, mode + '/exit/depth' + depth); nFrames += 30;
    }
  }
}

/* co-op, the menu and the death screen */
spritesOn(true);
startGame(['bulwark', 'ember']);
INS[1].mx = -1; INS[1].fire = true; INS[1].sp = true;
for (const e of G.enemies) e.alert = true;
step(120, 'coop'); nFrames += 120;
G.players[1].down = true; G.players[1].hp = 0;
step(60, 'coop-down'); nFrames += 60;
for (const P of G.players) { P.hp = 0; P.down = true; }
die();
step(20, 'dead'); nFrames += 20;
showMenu(); buildMenu(); onSprReady(); drawVendor();
G.state = 'menu';
step(20, 'menu'); nFrames += 20;

console.log('nFrames stepped:', nFrames);
console.log('draw calls:', __drawCalls());
console.log('best chain reached:', G.comboBest);
console.log(report.length ? 'ERRORS:\n' + report.join('\n') : 'NO RUNTIME ERRORS');
