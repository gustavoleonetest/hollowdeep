from patch import edit, run
L = 'part_logic.js'
# rollRarity's bonus is a slice of 100, so 1 was no bonus at all
edit(L, """  rar = rar || rollRarity(om('rich', false) ? 1 : 0);""",
     """  rar = rar || rollRarity(om('rich', false) ? 17 : 0);""")
run()
