from patch import edit, run

L = 'part_logic.js'

# --- the last overlay reading through -------------------------------------
# An overlay here dims the stage rather than covering it, which is the look
# the game wants, but it means anything still showing underneath reads
# straight through the sheet. That has now bitten three times: the HUD
# through the pause sheet, the menu through the Barrow, and this one.
#
# The menu, the death screen and the stall all take the HUD away while they
# are up. The loot screen never did -- and it is the one you see most, once
# per chest and once per piece of gear, so on a phone the health bar sat on
# top of the card you were choosing from.
edit(L, """  $('loot').hidden = false;""",
     """  $('hud').hidden = true;
  $('loot').hidden = false;""")

# it comes back when there is a floor to look at again. Not between two
# offers in a row, since the next one is about to cover the stage anyway.
edit(L, """  applyUpgrade(i); $('loot').hidden = true; lootShown = false;""",
     """  applyUpgrade(i); $('loot').hidden = true; lootShown = false;
  if (G.state === 'play') $('hud').hidden = false;""")

edit(L, """  if (G.state === 'offer' && !lootShown) { lootShown = true; showLoot(); } else if (G.state !== 'offer' && lootShown) { lootShown = false; $('loot').hidden = true; }""",
     """  if (G.state === 'offer' && !lootShown) { lootShown = true; showLoot(); }
  else if (G.state !== 'offer' && lootShown) {
    lootShown = false; $('loot').hidden = true;
    if (G.state === 'play') $('hud').hidden = false;
  }""")

run()
