from patch import edit, run

L = 'part_logic.js'
H = 'part_head.html'

# --- the touch controls were on before there was anything to control ------
# dashBtn, spBtn, bombBtn and the minimap are siblings of the HUD, not
# children, so hiding the HUD left them sitting over the menu, the stall and
# the death screen. They now follow a class on the stage, which in turn
# follows the HUD, so there is one source of truth rather than six call sites.
edit(H, """@media (pointer:coarse){#spBtn{display:block}}""",
     """@media (pointer:coarse){#stage.playing #spBtn{display:block}}""")
edit(H, """@media (pointer:coarse){#bombBtn{display:block}}""",
     """@media (pointer:coarse){#stage.playing #bombBtn{display:block}}""")
edit(H, """@media (pointer:coarse){#dashBtn{display:block}}""",
     """@media (pointer:coarse){#stage.playing #dashBtn{display:block}}""")
edit(H, """#mini{position:absolute;""",
     """#stage:not(.playing) #mini{display:none}
#mini{position:absolute;""")

# --- a phone was being told to press WASD --------------------------------
edit(H, """  <p><kbd>WASD</kbd> move""",
     """  <p class="touchhelp">Left half of the screen moves you · right half aims and attacks · the buttons are dash, special and potion</p>
  <p class="kbdhelp"><kbd>WASD</kbd> move""")

edit(H, """.overlay{position:absolute; inset:0;""",
     """.touchhelp{display:none}
@media (pointer:coarse){.kbdhelp{display:none}.touchhelp{display:block}}
.overlay{position:absolute; inset:0;""")

# --- keep the stage class in step with the HUD ---------------------------
edit(L, """  if (G.state === 'shop' && !shopShown) showShop(); else if (G.state !== 'shop' && shopShown) { shopShown = false; $('shop').hidden = true; if (G.state === 'play') $('hud').hidden = false; }""",
     """  if (G.state === 'shop' && !shopShown) showShop(); else if (G.state !== 'shop' && shopShown) { shopShown = false; $('shop').hidden = true; if (G.state === 'play') $('hud').hidden = false; }
  /* the touch buttons and the minimap belong to play, and the HUD already
     knows when that is */
  { const st = $('stage'), on = !$('hud').hidden;
    if (st && st.classList && st.dataset.play !== (on ? '1' : '0')) { st.dataset.play = on ? '1' : '0'; st.classList.toggle('playing', on); } }""")

run()
