from patch import edit, run

H = 'part_head.html'

# --- on a phone, the game opened on a wall of text ------------------------
# Measured at 375x812: the menu sheet is 1718px tall and the first delver
# card sits at y=802, which is to say just off the bottom of the screen. The
# overlay does scroll, so nothing was unreachable, but a new player opening
# this on a phone saw six lines of prose and no visible way to begin. That
# was true before this session (first card at y=706) and the resume row I
# added made it 96px worse, which is what sent me looking.
#
# The fix is order, not deletion: the explanation is worth keeping, it just
# should not stand between someone and the thing they came to tap. Under the
# project's existing 520px breakpoint the cards come up to meet them, and one
# line of what-to-do goes above, so nothing essential is below the fold.

edit(H, """      <p class="sub" id="pickHint" aria-live="polite"></p>""",
     """      <p class="sub phoneonly" id="miniHint">Smash the crypts, take the key, find the stairs. <b>Your health drains the whole way down.</b></p>
      <p class="sub" id="pickHint" aria-live="polite"></p>""")

edit(H, """@media (max-width:520px){.bar h1{font-size:26px}.sheet h2{font-size:30px}}""",
     """@media (max-width:520px){.bar h1{font-size:26px}.sheet h2{font-size:30px}}
.phoneonly{display:none}
/* On a narrow screen the delvers come up to meet you: title, the run you
   left, how many of you there are, then the cards. The blurb keeps every
   word it had and waits below, where it is still there for anyone who
   wants it. Nothing changes on a wider screen. */
@media (max-width:520px){
  #menu .sheet h2{order:1}
  #menu .sheet #resumeRow{order:2}
  #menu .sheet #modes{order:3}
  #menu .sheet #miniHint{order:4; display:block}
  #menu .sheet #pickHint{order:5}
  #menu .sheet #cards{order:6}
  #menu .sheet #opts{order:7}
  #menu .sheet .sub{order:8}
}""")

run()
