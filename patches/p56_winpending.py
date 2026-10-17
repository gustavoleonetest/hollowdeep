from patch import edit, run

L = 'part_logic.js'

# Killing the Heart hands over enough experience to level you, so the state
# was 'offer' when the victory timer fired and the screen never came. Hold the
# win until the card is answered rather than snatching the choice away.
edit(L, """  G.timers.push({ t: 2.6, fn: () => { if (G.state === 'play') G.state = 'won'; } });""",
     """  G.timers.push({ t: 2.6, fn: () => { G.winPending = true; } });""")

edit(L, """function update(dt) {
  if (G.state !== 'play') return;""",
     """function update(dt) {
  if (G.winPending && G.state === 'play') { G.winPending = false; G.state = 'won'; return; }
  if (G.state !== 'play') return;""")

edit(L, """  G.level = 1; G.score = 0; G.won = false; genLevel(); G.state = 'play'; G.paused = false;""",
     """  G.level = 1; G.score = 0; G.won = false; G.winPending = false; genLevel(); G.state = 'play'; G.paused = false;""")

# going deeper after the win clears it, or the screen would come straight back
edit(L, """  G.state = 'play'; overShown = false;
  announce('Deeper, then', '#ffd24a');""",
     """  G.state = 'play'; overShown = false; G.winPending = false;
  announce('Deeper, then', '#ffd24a');""")

run()
