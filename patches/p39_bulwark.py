from patch import edit, run

L = 'part_logic.js'

# The simulated bulwark stalled in 71% of runs against 36% for the ranged
# delvers, so its depth figures measured the driver, not the class. Reach and
# footspeed stay (a melee delver must close, and the drain is a clock), but the
# drain resistance was a guess the data cannot support and it is invisible to
# the player on top of that.
edit(L, """armor: 0.72, drain: -.15""", """armor: 0.72""")

run()
