from patch import edit, run
L = 'part_logic.js'
# Lavender was a worse choice than the duplicate it replaced: it collapses
# into Cold Touched under deuteranopia. The five other modifiers already cap
# this set at 11.4 between themselves, so the most a sixth can do is reach
# that ceiling, which a pale speed-white does.
edit(L, """  { id: 'fast', name: 'Extra Fast', col: '#c9b6ff' },""",
     """  { id: 'fast', name: 'Extra Fast', col: '#eaf4ff' },""")
run()
