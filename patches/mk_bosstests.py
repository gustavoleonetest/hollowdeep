import io

p = 'behave2_drive.js'
s = io.open(p, encoding='utf-8').read()

start = s.index("/* ---------------- three distinct bosses ---------------- */")
end = s.index("/* --- the caller's tricks --- */")

block = r"""/* ---------------- six zones, six bosses ---------------- */
{
  const perZone = [1, 2, 3, 4, 5, 6].map(z => bossKindOf(z * 3));
  ok('every zone draws a boss of its own', new Set(perZone).size === 6, perZone.join(','));
  ok('and each one is a defined archetype', perZone.every(k => !!BOSSES[k]), perZone.filter(k => !BOSSES[k]).join(',') || 'all defined');
  /* the names promised six bosses long before the behaviour did */
  const names = ZONES.map(z => z.boss);
  ok('each zone names its boss', new Set(names).size === 6, names.length + ' names');

  /* no two of them share a late attack pattern */
  const sigs = perZone.map(k => (BOSSES[k].acts[3] || []).slice().sort().join(','));
  ok('no two bosses fight the same way', new Set(sigs).size === 6, sigs.join(' | '));
  /* and every act a boss can pick has a duration, or it would hang mid swing */
  const missing = [];
  for (const k of perZone) for (const ph of [1, 2, 3]) for (const a of (BOSSES[k].acts[ph] || []))
    if (BOSS_DUR[a] === undefined) missing.push(k + '/' + a);
  ok('every attack has a timed wind-up', missing.length === 0, missing.join(',') || 'all timed');

  /* each boss actually shows up on its own depth, and every attack it owns
     resolves and hands control back. The pools are walked in order and only
     swing with line of sight, so drive each act directly rather than waiting. */
  const stuck = [], wrongKind = [];
  for (let z = 0; z < 6; z++) {
    const lvl = z * 3 + 3, want = bossKindOf(lvl);
    startGame(['thistle']); G.level = lvl; genLevel();
    let gg = 0; while (G.offer && gg++ < 20) applyUpgrade(0); G.offerQ.length = 0; G.state = 'play';
    const B = G.enemies.find(e => e.boss);
    if (!B || B.kind !== want) { wrongKind.push(lvl + ':' + (B ? B.kind : 'none') + '!=' + want); continue; }
    const rig = foeDef('warden', B.kind);
    if (!rig || !rig.key) { wrongKind.push(lvl + ':norig'); continue; }
    const room = G.rooms.reduce((a, b) => (b.w * b.h > a.w * a.h ? b : a), G.rooms[0]);
    const every = [...new Set([].concat(BOSSES[want].acts[1] || [], BOSSES[want].acts[2] || [], BOSSES[want].acts[3] || []))];
    for (const act of every) {
      B.hp = B.max * .2; B.cd = 0; B.alert = true; B.kx = 0; B.ky = 0;
      B.immune = false; B.wardT = undefined; B.wardAdds = null;
      B.x = room.cx * T + T / 2; B.y = room.cy * T + T / 2;
      G.players.forEach(pl => { pl.down = false; pl.hp = pl.max; pl.inv = 1e9; pl.x = B.x + 40; pl.y = B.y; });
      B.st = act; B.stt = 0; B.ca = 1;
      buildFlow();
      let back = false;
      for (let i = 0; i < 500; i++) {
        updateEnemies(1 / 60); updateShots(1 / 60); updateFx(1 / 60);
        G.players.forEach(pl => { pl.hp = pl.max; });
        if (B.st === 'chase') { back = true; break; }
      }
      if (!back) stuck.push(want + '/' + act);
    }
  }
  ok('each depth spawns its own boss with a rig', wrongKind.length === 0, wrongKind.join(' ') || 'all six');
  ok('and every attack any of them owns resolves', stuck.length === 0, stuck.join(' ') || 'all clear');
}

/* --- the new attacks do what they claim --- */
{
  function bossIn(kind) {
    startGame(['thistle']); G.level = 3; genLevel();
    let gg = 0; while (G.offer && gg++ < 20) applyUpgrade(0); G.offerQ.length = 0; G.state = 'play';
    G.enemies.length = 0; G.eshots.length = 0; G.timers.length = 0; G.fxs.length = 0;
    const room = G.rooms.reduce((a, b) => (b.w * b.h > a.w * a.h ? b : a), G.rooms[0]);
    spawnFoe('warden', room.cx * T + T / 2, room.cy * T + T / 2);
    const B = G.enemies[G.enemies.length - 1];
    B.kind = kind; B.alert = true; B.hp = B.max;
    const Q = G.players[0]; Q.x = B.x + 60; Q.y = B.y; Q.down = false; Q.hp = Q.max;
    return [B, Q];
  }
  /* pillars: a mark on the floor first, damage only after it fills */
  { const [B, Q] = bossIn('pyre'); Q.inv = 0;
    B.st = 'pillars'; bossAct(B);
    const warned = G.fxs.filter(f => f.kind === 'warn').length;
    ok('the pyre marks the floor before it burns', warned > 0, warned + ' marks');
    const pending = G.timers.length;
    ok('and the fire is still only a promise', pending > 0 && G.players[0].hp === G.players[0].max, pending + ' pending');
    let hp0 = Q.hp; Q.x = G.fxs.find(f => f.kind === 'warn').x; Q.y = G.fxs.find(f => f.kind === 'warn').y;
    for (let i = 0; i < 90; i++) { Q.inv = 0; updateFx(1 / 60); }
    ok('standing on a mark burns you', Q.hp < hp0, hp0.toFixed(0) + ' -> ' + Q.hp.toFixed(0)); }
  { const [B, Q] = bossIn('pyre'); Q.inv = 0;
    B.st = 'pillars'; bossAct(B);
    const spot = G.fxs.find(f => f.kind === 'warn');
    /* stand well clear of every mark */
    let far2 = null;
    for (let a = 0; a < 48 && !far2; a++) {
      const an = a / 48 * TAU, x = B.x + Math.cos(an) * 260, y = B.y + Math.sin(an) * 260;
      if (blockedAt(x, y, 11) || !openAt(x, y)) continue;
      if (G.fxs.some(f => f.kind === 'warn' && Math.hypot(f.x - x, f.y - y) < 90)) continue;
      far2 = [x, y];
    }
    if (!far2) ok('and stepping off one spares you', true, 'nowhere clear, skipped');
    else { Q.x = far2[0]; Q.y = far2[1]; const hp0 = Q.hp;
      for (let i = 0; i < 90; i++) { Q.inv = 0; updateFx(1 / 60); }
      ok('and stepping off one spares you', Q.hp === hp0, hp0.toFixed(0) + ' -> ' + Q.hp.toFixed(0)); } }
  /* comet: bends toward you */
  { const [B, Q] = bossIn('pyre');
    B.st = 'comet'; B.face = 0; bossAct(B);
    const shots = G.eshots.slice();
    ok('the pyre throws seeking fire', shots.length > 0 && shots.every(s => s.seek > 0), shots.length + ' comets');
    if (shots.length) {
      const s0 = shots[0];
      /* put the target off to one side and watch the heading swing toward it */
      Q.x = B.x + 40; Q.y = B.y - 200; Q.inv = 1e9;
      const a0 = Math.atan2(s0.vy, s0.vx);
      for (let i = 0; i < 40; i++) updateShots(1 / 60);
      const a1 = Math.atan2(s0.vy, s0.vx);
      ok('and it turns to follow', Math.abs(Math.atan2(Math.sin(a1 - a0), Math.cos(a1 - a0))) > .05,
         (a0).toFixed(2) + ' -> ' + (a1).toFixed(2)); } }
  /* wail: hurts as the ring passes, not where you started */
  { const [B, Q] = bossIn('chorister');
    Q.x = B.x + 4; Q.y = B.y; Q.inv = 0; const hp0 = Q.hp;
    B.st = 'wail'; bossAct(B);
    for (let i = 0; i < 12; i++) { Q.inv = 0; updateFx(1 / 60); }
    ok('the wail spares the eye of the ring', Q.hp === hp0, 'at the centre: ' + Q.hp.toFixed(0));
    Q.x = B.x + 150; Q.y = B.y;
    for (let i = 0; i < 80; i++) { Q.inv = 0; updateFx(1 / 60); }
    ok('and catches you where it passes', Q.hp < hp0, hp0.toFixed(0) + ' -> ' + Q.hp.toFixed(0)); }
  /* ward: untouchable until the choir falls */
  { const [B, Q] = bossIn('chorister');
    B.st = 'ward'; B.ph = 2; bossAct(B);
    ok('the chorister raises a choir', (B.wardAdds || []).length > 0, (B.wardAdds || []).length + ' singers');
    ok('and cannot be touched while it stands', B.immune === true);
    const hp0 = B.hp; hurtFoe(B, 500, 0, false, false, Q);
    ok('damage does not land on it', B.hp === hp0, hp0.toFixed(0) + ' -> ' + B.hp.toFixed(0));
    for (const a of B.wardAdds) { a.hp = 0; a.dead = 1; }
    for (let i = 0; i < 10; i++) updateEnemies(1 / 60);
    ok('silencing the choir exposes it', B.immune === false);
    const hp1 = B.hp; hurtFoe(B, 40, 0, false, false, Q);
    ok('and then it takes damage', B.hp < hp1, hp1.toFixed(0) + ' -> ' + B.hp.toFixed(0)); }
  { /* the ward must lift on its own too, or a stuck add would end the run */
    const [B, Q] = bossIn('chorister');
    B.st = 'ward'; B.ph = 2; bossAct(B);
    if (!B.immune) ok('a ward always times out', true, 'no room for a choir, skipped');
    else { for (let i = 0; i < 60 * 11 && B.immune; i++) updateEnemies(1 / 60);
      ok('a ward always times out', B.immune === false, 'wardT=' + B.wardT); } }
  /* shards: thrown out, then called back */
  { const [B, Q] = bossIn('obsidian'); Q.inv = 1e9;
    B.st = 'shards'; bossAct(B);
    const mine = G.eshots.slice();
    ok('the obsidian throws a ring of shards', mine.length >= 8, mine.length + ' shards');
    const s0 = mine[0], out = { x: s0.vx, y: s0.vy };
    for (let i = 0; i < 70; i++) updateShots(1 / 60);
    for (let i = 0; i < 12; i++) updateFx(1 / 60);
    const alive2 = mine.filter(s => G.eshots.indexOf(s) >= 0);
    const turned = alive2.filter(s => s.vx * out.x < 0 || s.vy * out.y < 0).length;
    ok('and calls them back', alive2.length === 0 || turned > 0, turned + ' of ' + alive2.length + ' reversed'); }
}

"""

io.open(p, 'w', encoding='utf-8', newline='').write(s[:start] + block + s[end:])
print('boss tests rewritten')
