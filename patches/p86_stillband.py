from patch import edit, run

L = 'part_logic.js'

# On a Still Air floor the deep is not draining you at all, so there is
# nothing for the band to say. It was still being drawn, at zero width.
# Harmless to look at, but "shown and empty" and "nothing to show" are
# different states and the bar should be in the second one.
edit(L, """    h.drain.hidden = P.down || P.hp <= 0;""",
     """    h.drain.hidden = P.down || P.hp <= 0 || cost <= 0;""")

run()
