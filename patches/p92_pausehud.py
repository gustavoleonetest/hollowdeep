from patch import edit, run
L = 'part_logic.js'

# The overlay dims the stage rather than hiding it, so the HUD panel shows
# through the sheet. On a desktop they sit apart and it reads fine; on a
# phone the health bar lands on top of the heading. The sheet already says
# what the HUD says -- it opens with the delver's health -- so while it is
# up the HUD has nothing left to tell anyone.
edit(L, """  $('pauseHint').textContent = btnsOn ? 'Tap anywhere to carry on.' : 'Press P, or click, to carry on.';
  $('paused').hidden = false;""",
     """  $('pauseHint').textContent = btnsOn ? 'Tap anywhere to carry on.' : 'Press P, or click, to carry on.';
  $('hud').hidden = true;
  $('paused').hidden = false;""")

# and give it back on the way out, but only to a run that is still going:
# a pause that ends because the delver died has already had the HUD taken
# away by the screen that replaced it
edit(L, """  else if (!wantPause && pauseShown) { pauseShown = false; $('paused').hidden = true; }""",
     """  else if (!wantPause && pauseShown) {
    pauseShown = false; $('paused').hidden = true;
    if (G.state === 'play') $('hud').hidden = false;
  }""")
run()
