from patch import edit, run

L = 'part_logic.js'
H = 'part_head.html'

# --- a phone has no room for a control hint it has already read ----------
# The bar sits outside the stage, so the playing class has to live on body
# for the hint to be reclaimable. On a 375 wide screen the hint plus the HUD
# were taking about a third of the height while playing.
edit(L, """  { const st = $('stage'), on = !$('hud').hidden;
    if (st && st.classList && st.dataset.play !== (on ? '1' : '0')) { st.dataset.play = on ? '1' : '0'; st.classList.toggle('playing', on); } }""",
     """  { const st = $('stage'), on = !$('hud').hidden;
    if (st && st.classList && st.dataset.play !== (on ? '1' : '0')) {
      st.dataset.play = on ? '1' : '0';
      st.classList.toggle('playing', on);
      if (document.body && document.body.classList) document.body.classList.toggle('playing', on);
    } }""")

edit(H, """.touchhelp{display:none}
@media (pointer:coarse){.kbdhelp{display:none}.touchhelp{display:block}}""",
     """.touchhelp{display:none}
@media (pointer:coarse){
  .kbdhelp{display:none}
  .touchhelp{display:block}
  /* once you are playing you have read it, and the screen is small */
  body.playing .touchhelp{display:none}
  body.playing .bar{padding-bottom:2px}
}""")

run()
