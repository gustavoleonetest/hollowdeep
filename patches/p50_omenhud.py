from patch import edit, run

H = 'part_head.html'
L = 'part_logic.js'

# The banner fades after under three seconds, and an omen governs the whole
# floor, so it has to stay somewhere the player can glance at.
edit(H, """      <span id="comboBox" hidden>Chain <b id="combo">0</b></span>""",
     """      <span id="comboBox" hidden>Chain <b id="combo">0</b></span>
      <span id="omenBox" hidden><b id="omenName"></b></span>""")

edit(L, """const hud1 = mkHud(''), hud2 = mkHud('2'), hud = { lvl: $('lvl'), gold: $('gold'), keys: $('keys'), combo: $('combo'), comboBox: $('comboBox'), bombs: $('bombs'), bombBox: $('bombBox') };""",
     """const hud1 = mkHud(''), hud2 = mkHud('2'), hud = { lvl: $('lvl'), gold: $('gold'), keys: $('keys'), combo: $('combo'), comboBox: $('comboBox'), bombs: $('bombs'), bombBox: $('bombBox'), omenBox: $('omenBox'), omenName: $('omenName') };""")

edit(L, """  hud.lvl.textContent = G.level; hud.gold.textContent = G.gold; hud.keys.textContent = G.keys;""",
     """  hud.lvl.textContent = G.level; hud.gold.textContent = G.gold; hud.keys.textContent = G.keys;
  if (hud.omenBox) {
    hud.omenBox.hidden = !G.omen;
    if (G.omen) { hud.omenName.textContent = G.omen.name; hud.omenBox.style.color = G.omen.col; }
  }""")

run()
