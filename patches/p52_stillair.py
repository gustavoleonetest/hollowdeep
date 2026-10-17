from patch import edit, run

L = 'part_logic.js'

# Stopping the clock removes the only thing stopping you camping, and crypts
# feed forever, so a Still Air floor could be farmed without limit. It gets a
# garrison instead of spawners: no clock, no reinforcements, a finite fight.
edit(L, """    drain: 0, foes: 1.8, food: 0 },""",
     """    drain: 0, foes: 2.1, nests: 0, food: 0 },""")

run()
