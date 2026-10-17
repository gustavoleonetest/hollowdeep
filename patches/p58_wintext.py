from patch import edit, run

L = 'part_logic.js'
H = 'part_head.html'
DOT = chr(92) + 'u00b7'

# The victory screen is shown before the run is banked, so it read
# "Echoes earned +0". Say what is waiting instead, from the same sum that
# bankRun will actually pay.
edit(L, """function bankRun() {
  G.best = Math.max(G.best, G.score);
  G.earned = Math.max(1, Math.round(G.gold * .25 + G.score / 40 + (G.level - 1) * 8)) * (G.won ? 2 : 1);""",
     """function runEchoes() {
  return Math.max(1, Math.round(G.gold * .25 + G.score / 40 + (G.level - 1) * 8)) * (G.won ? 2 : 1);
}
function bankRun() {
  G.best = Math.max(G.best, G.score);
  G.earned = runEchoes();""")

edit(H, """      <p class="sub">Echoes earned <b class="big" id="oEch">+0</b> · you now hold <b class="big" id="oEchTot">0</b></p>""",
     """      <p class="sub"><span id="oEchLbl">Echoes earned</span> <b class="big" id="oEch">+0</b> · you now hold <b class="big" id="oEchTot">0</b></p>""")

edit(L, """  $('oEch').textContent = '+' + (G.earned || 0);
  $('oEchTot').textContent = String(META.echoes);""",
     """  $('oEchLbl').textContent = won ? 'Echoes waiting above' : 'Echoes earned';
  $('oEch').textContent = '+' + (won ? runEchoes() : (G.earned || 0));
  $('oEchTot').textContent = String(META.echoes);""")

# "1 count" was written when every boss was a count
edit(L, """(G.bosses ? '  """ + DOT + """  ' + G.bosses + ' count' : '')""",
     """(G.bosses ? '  """ + DOT + """  ' + G.bosses + (G.bosses === 1 ? ' warden' : ' wardens') : '')""")

run()
