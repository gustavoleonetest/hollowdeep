from patch import edit, run

L = 'part_logic.js'

# The same line is shown on the item being offered and on the one already
# worn, so "this WOULD make a pair" read as a prediction on a card
# describing something the delver has had on for three floors. Neutral
# wording is true of both: it describes the piece, not the act of taking it.
#
# Anchored on the plain words only. The surrounding source holds an escape
# sequence for the dash, and every layer between here and the file -- the
# tool's own JSON, a shell heredoc -- gets a chance to unescape it and turn
# a match into a near-miss. Not including it sidesteps the whole question.
edit(L, "this would complete all three'", "all three together'")
edit(L, "this would make a pair'", "a pair with what else you wear'")

run()
