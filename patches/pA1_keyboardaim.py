from patch import edit, run

L = 'part_logic.js'
H = 'part_head.html'

# --- the game aims for you, and never mentioned it -----------------------
# Three of the four delvers are ranged, and the controls say "mouse aim".
# Somebody without a mouse, or who would rather not use one, reads that as
# "this is not for you".
#
# It is, and it has been all along: four seconds after the mouse last
# moved, P1 falls back to assistAim, and P2 -- who has never had a mouse --
# uses nothing else. It takes whatever you are facing, looks for a foe or a
# crypt within 320, inside 29 degrees and in line of sight, and puts the
# shot on it.
#
# That is a real accessibility feature that the game kept to itself.
edit(H, """ gamepad: sticks move and aim, triggers fight""",
     """ no mouse needed: face a foe and the shot finds it · gamepad: sticks move and aim, triggers fight""")

edit(L, """    : 'WASD move \\u00b7 mouse aim \\u00b7 click or Space attack \\u00b7 Shift dash \\u00b7 E special \\u00b7 F potion \\u00b7 P pause.';""",
     """    : 'WASD move \\u00b7 mouse aim \\u00b7 click or Space attack \\u00b7 Shift dash \\u00b7 E special \\u00b7 F potion \\u00b7 P pause. '
      + 'No mouse needed: face a foe and the shot finds it.';""")

run()
