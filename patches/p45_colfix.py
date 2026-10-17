from patch import edit, run
L = 'part_logic.js'
edit(L, """    const p = sh.pact, col = p.col;""",
     """    const p = sh.pact, col = shrineCol(sh);""")
run()
