from patch import edit, run

L = 'part_logic.js'

# --- the thing about to hit you should be the thing you can see ----------
# Measured over fifteen hundred frames on each of eight depths: about one
# hit in ten comes from a foe the player cannot see, and every one of them
# was an archer at roughly 265 units, which is just past where fog stops
# drawing a foe at all. That is fine in itself, archers are meant to outrange
# your sight, so long as the arrow is readable. It was not.
#
# The player's own shots punch a hole in the dark and tint it. Enemy shots
# only tinted, so the one warning you get was the dimmest thing on screen.
# They now carry their own light: smaller and softer than yours, since an
# arrow should not light the room, but enough to read as incoming.
edit(L, """  for (const s of G.shots) hole(s.x, s.y, s.kind === 'fire' ? 130 : 70, .8);""",
     """  for (const s of G.shots) hole(s.x, s.y, s.kind === 'fire' ? 130 : 70, .8);
  for (const s of G.eshots) hole(s.x, s.y, 56, .6);""")

edit(L, """  for (const s of G.eshots) tint(s.x, s.y, 42, '#ebe4d2', .2);""",
     """  for (const s of G.eshots) tint(s.x, s.y, 48, '#ffd9a8', .3);""")

run()
