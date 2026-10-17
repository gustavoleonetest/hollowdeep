from patch import edit, run

L = 'part_logic.js'

# --- the same arrival sounded different depending on how you got there ----
# spawnFoe guards its elite sting with G.state === 'play', which reads as
# "not while the floor is being built". startGame honours that by generating
# before it flips to play, so depth one is quiet. leaveShop flips first and
# then generates, so every depth after the first announced all of its elites
# the instant you arrived, before you had seen any of them. Generate first,
# the way starting a run already does.
edit(L, """function leaveShop() { if (G.state !== 'shop') return; G.state = 'play'; nextLevel(); }""",
     """function leaveShop() { if (G.state !== 'shop') return; nextLevel(); G.state = 'play'; }""")

run()
