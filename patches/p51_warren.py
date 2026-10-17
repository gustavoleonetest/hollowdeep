from patch import edit, run

L = 'part_logic.js'

# The per room cap of five swallowed most of the Warren's multiplier, so the
# floor named for its crypts had only about half again as many.
edit(L, """    const nn = Math.min(5, Math.round(nn0 * om('nests', 1)));""",
     """    const nn = Math.min(om('nestCap', 5), Math.round(nn0 * om('nests', 1)));""")

edit(L, """    nests: 2.4, foes: .55, gold: 1.3 }""",
     """    nests: 2.4, nestCap: 8, foes: .55, gold: 1.3 }""")

run()
