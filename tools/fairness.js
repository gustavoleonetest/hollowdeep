/* Of every hit the player takes, how much came from something on screen? */
const tally = { total: 0, bySource: {}, unseenSource: 0, noSource: 0, samples: [] };
const realHurt = hurtPlayer;
hurtPlayer = function (P, dmg, ang, src) {
  const before = P.hp;
  const r = realHurt.apply(this, arguments);
  if (P.hp < before) {
    tally.total++;
    const kind = src ? (src.boss ? 'boss' : src.type || 'foe') : 'unattributed';
    tally.bySource[kind] = (tally.bySource[kind] || 0) + 1;
    if (!src) tally.noSource++;
    else {
      const f = fogAt(src.x, src.y);
      if (f >= .4) { tally.unseenSource++; if (tally.samples.length < 5) tally.samples.push(kind + ' fog=' + f.toFixed(2) + ' dist=' + Math.round(Math.hypot(src.x - P.x, src.y - P.y))); }
    }
  }
  return r;
};

for (let depth = 2; depth <= 16; depth += 2) {
  startGame(['thistle']); G.level = depth; genLevel();
  let g = 0; while (G.offer && g++ < 30) applyUpgrade(0);
  G.offerQ.length = 0; G.state = 'play';
  const P = G.players[0];
  for (let i = 0; i < 1500; i++) {
    P.hp = P.max;                      /* never die, so the sample keeps going */
    INS[0].mx = Math.cos(i / 40); INS[0].my = Math.sin(i / 37); INS[0].fire = true;
    readInput(); update(1 / 60);
    updateFog();
    if (G.state !== 'play') G.state = 'play';
  }
}
hurtPlayer = realHurt;
console.log('hits taken: ' + tally.total);
console.log('by source  : ' + JSON.stringify(tally.bySource));
console.log('from something in fog: ' + tally.unseenSource + '  (' + (tally.unseenSource / Math.max(1, tally.total) * 100).toFixed(1) + '%)');
console.log('with no source at all: ' + tally.noSource + '  (' + (tally.noSource / Math.max(1, tally.total) * 100).toFixed(1) + '%)  <- traps, shots, boss ground effects');
if (tally.samples.length) console.log('examples of unseen sources: ' + tally.samples.join(' | '));
