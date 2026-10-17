import io

p = 'behave2_drive.js'
s = io.open(p, encoding='utf-8').read()
anchor = "const fails = results.filter(r => r[0] === 'FAIL');"
assert s.count(anchor) == 1

block = r"""/* ---------------- the game makes a noise when it matters ---------------- */
{
  /* sfx() silently ignores a name it does not know, so a typo is a moment
     that simply never makes a sound. Listen to what the game asks for and
     check every name against the table. */
  const heard = [];
  const realSfx = sfx;
  const listen = (fn) => {
    heard.length = 0;
    sfx = (k) => { heard.push(k); };
    try { fn(); } finally { sfx = realSfx; }
    return heard.slice();
  };

  ok('every sound the game can play is defined', Object.keys(SFXF).length >= 15, Object.keys(SFXF).length + ' sounds');
  ok('and asking for one that is not does nothing rather than throw',
     (() => { try { realSfx('no such sound'); return true; } catch (e) { return false; } })());

  /* the moments that should be audible */
  const moments = {};
  moments['an omen arriving'] = listen(() => {
    const real = rollOmen; rollOmen = () => OMENS[0];
    try { startGame(['sable']); G.level = 8; genLevel(); } finally { rollOmen = real; }
  });
  moments['a chest opening'] = listen(() => {
    startGame(['sable']); G.level = 4; genLevel(); G.offer = null; G.offerQ.length = 0;
    openChest(G.players[0], { x: G.players[0].x, y: G.players[0].y, big: false });
  });
  moments['a warden falling'] = listen(() => {
    startGame(['sable']); G.level = 6; genLevel();
    let gg = 0; while (G.offer && gg++ < 20) applyUpgrade(0); G.offerQ.length = 0; G.state = 'play';
    const B = G.enemies.find(e => e.boss);
    if (B) hurtFoe(B, B.max * 10, 0, false, false, G.players[0]);
  });
  moments['learning a boon'] = listen(() => {
    startGame(['bulwark']); G.level = 4; genLevel(); G.offer = null; G.offerQ.length = 0;
    const P = G.players[0];
    queueOffer({ kind: 'boon', P, opts: rollBoons(P) });
    applyUpgrade(0);
  });
  moments['taking a pact'] = listen(() => {
    startGame(['sable']); G.level = 5; genLevel(); G.offer = null; G.offerQ.length = 0;
    const P = G.players[0];
    const it = { kind: 'shrine', x: P.x, y: P.y, t: 0, cool: 0, sh: { kind: 'pact', pact: PACTS[0] } };
    G.items.push(it);
    queueOffer({ kind: 'pact', P, shrine: it });
    applyUpgrade(0);
  });
  moments['taking a hit'] = listen(() => {
    startGame(['ember']); G.level = 3; genLevel(); G.state = 'play';
    const P = G.players[0]; P.inv = 0; hurtPlayer(P, 5, 0);
  });

  const silent = Object.keys(moments).filter(k => moments[k].length === 0);
  ok('every moment that should be heard makes a sound', silent.length === 0, silent.join(', ') || Object.keys(moments).length + ' checked');

  /* and nothing asks for a sound that does not exist */
  const asked = new Set();
  for (const k in moments) for (const n of moments[k]) asked.add(n);
  const unknown = [...asked].filter(n => !SFXF[n]);
  ok('and none of them asks for a sound that is not there', unknown.length === 0, unknown.join(',') || [...asked].sort().join(' '));

  /* the omen one is new, and was the gap that prompted this */
  ok('an omen is heard, not only narrated', moments['an omen arriving'].includes('omen'),
     moments['an omen arriving'].join(',') || 'silence');

  /* mute has to stop the one-shots too, not just the music */
  { const wasMuted = muted;
    const calls = [];
    const realTone = tone;
    tone = (...a) => { calls.push('tone'); };
    try {
      setMuted(true);
      realSfx('coin'); realSfx('boom');
      ok('mute stops the sound effects', calls.length === 0, calls.length + ' tones while muted');
    } finally { tone = realTone; setMuted(wasMuted); } }

  /* and the narrator is a preference that is remembered */
  { const was = voiceOn;
    voiceOn = false; G.vlast = {}; G.voice = null;
    announce('a line nobody asked for', '#fff');
    ok('the narrator still shows its line on screen when muted', !!G.voice, G.voice ? 'shown' : 'nothing');
    voiceOn = was; }
}

"""

io.open(p, 'w', encoding='utf-8', newline='').write(s.replace(anchor, block + anchor))
print('audio tests inserted')
