from patch import edit, run

L = 'part_logic.js'

# raise the fallen the same way the Hearth Elixir does
edit(L, """    else if (p.id === 'mend') { P.hp = P.max; for (const q of G.players) if (q.down) revive(q); }""",
     """    else if (p.id === 'mend') { P.hp = P.max; for (const D of G.players) if (D.down) { D.down = false; D.hp = D.max * .5; D.rev = 0; D.inv = 1; } }""")

run()
