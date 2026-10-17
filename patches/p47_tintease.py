from patch import edit, run
L = 'part_logic.js'
# a flat colour block loses the carving; enough tint to read, not to erase
edit(L, """sprProp('altar', it.x, it.y + 11, 1.38, col, .44 + pu * .16)""",
     """sprProp('altar', it.x, it.y + 11, 1.38, col, .3 + pu * .14)""")
run()
