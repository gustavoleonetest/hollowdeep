from patch import edit, run
L = 'part_logic.js'

# The Barrow is shown over the menu, and the overlay dims rather than
# hides, so the blurb and the delver cards read through it. That was
# survivable while the Barrow was short; adding the descent to it made it a
# wall of text over a wall of text. The menu is not doing anything while
# the Barrow is up, so it steps out and comes back on the way out.
edit(L, """function showBarrow(on) { $('barrow').hidden = !on; if (on) { renderBarrow(); $('barrowBack').focus({ preventScroll: true }); } }""",
     """function showBarrow(on) {
  $('barrow').hidden = !on;
  /* the menu is behind it and shows through, so it waits outside */
  $('menu').hidden = !!on;
  if (on) { renderBarrow(); $('barrowBack').focus({ preventScroll: true }); }
  else { $('barrow').scrollTop = 0; }
}""")
run()
