from patch import edit, run

H = 'part_head.html'

# A phone turned on its side, or any short window, loses about a quarter of
# its height to the control reference while playing. Coarse pointers already
# drop their hint once the run starts; do the same wherever vertical room is
# scarce, whatever is pointing at it. It is still there on the menu, which is
# where someone reads it.
edit(H, """
.touchhelp{display:none}
@media (pointer:coarse){""",
     """
@media (max-height:560px){ body.playing .bar p{display:none} body.playing .bar{padding-bottom:2px} }
.touchhelp{display:none}
@media (pointer:coarse){""")

run()
