from patch import edit, run

L = 'part_logic.js'

# Hunter's Mark raised the number shown but not the damage dealt: the multiply
# landed three lines after e.hp had already been reduced.
edit(L, """  if (crit) dmg *= 2.25;
  dmg = Math.round(dmg); e.hp -= dmg;""",
     """  if (crit) dmg *= 2.25;
  if (e.mark > 0) dmg *= 1.25;
  dmg = Math.round(dmg); e.hp -= dmg;""")

edit(L, """  if (e.mark > 0) dmg = Math.round(dmg * 1.25);
  text(e.x, e.y - e.r - 4,""",
     """  text(e.x, e.y - e.r - 4,""")

run()
