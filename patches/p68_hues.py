from patch import edit, run
L = 'part_logic.js'
# The Horde and The Gilded Seam were 2.0 apart under deuteranopia: the same
# colour. The omen name is written in the HUD, so this was never the only
# clue, but two of six rendering identically is sloppy.
edit(L, """  { id: 'horde', name: 'The Horde', col: '#ff8a3a',""",
     """  { id: 'horde', name: 'The Horde', col: '#e0553a',""")
# Extra Fast and Cold Touched shared one hex exactly
edit(L, """  { id: 'fast', name: 'Extra Fast', col: '#8fd3ff' },""",
     """  { id: 'fast', name: 'Extra Fast', col: '#c9b6ff' },""")
run()
