from patch import edit, run

L = 'part_logic.js'
H = 'part_head.html'

# --- the progression loop was never explained ----------------------------
# Echoes buy the Barrow, and the Barrow is the only thing that carries from
# one descent to the next. The death screen prints the number you earned
# and nothing about where it came from, so the loop that is supposed to
# pull a player back in -- score well, go deep, come back stronger -- is
# invisible. A chain is worth something, gold is worth something, and
# reaching a new depth is worth a great deal; none of that was ever said.
#
# One function for the number and its parts, so the explanation cannot
# drift from the arithmetic, and the parts are made to sum to the total
# rather than being rounded separately into a sum that does not add up.
edit(L, """function runEchoes() {
  return Math.max(1, Math.round(G.gold * .25 + G.score / 40 + (G.level - 1) * 8)) * (G.won ? 2 : 1);
}""",
     """function echoParts() {
  const g = G.gold * .25, s = G.score / 40, d = Math.max(0, G.level - 1) * 8;
  const base = Math.max(1, Math.round(g + s + d));
  const p = { gold: Math.round(g), score: Math.round(s), depth: Math.round(d) };
  /* three numbers rounded on their own will not always add up to a total
     rounded once, and a player reading the line will try to add them, so
     the largest part carries the difference */
  const drift = base - (p.gold + p.score + p.depth);
  if (drift) {
    const big = p.depth >= p.gold && p.depth >= p.score ? 'depth' : p.gold >= p.score ? 'gold' : 'score';
    p[big] = Math.max(0, p[big] + drift);
  }
  p.base = base; p.doubled = !!G.won; p.total = base * (G.won ? 2 : 1);
  return p;
}
function runEchoes() { return echoParts().total; }""")

edit(L, """  $('oEchTot').textContent = String(META.echoes);""",
     """  $('oEchTot').textContent = String(META.echoes);
  {
    /* where the number came from, so the loop that is meant to bring
       someone back has at least been described to them once */
    const p = echoParts(), el = $('oEchHow');
    if (el) {
      el.textContent = 'The gold you carried gave ' + p.gold + ', your score ' + p.score +
        ' and the depth you reached ' + p.depth +
        (p.doubled ? ', and carrying ' + HEART_NAME + ' out doubled the lot.' : '.') +
        ' Spend them in the Barrow, and the next delver starts stronger.';
    }
  }""")

edit(H, """      <p class="sub"><span id="oEchLbl">Echoes earned</span> <b class="big" id="oEch">+0</b> · you now hold <b class="big" id="oEchTot">0</b></p>""",
     """      <p class="sub"><span id="oEchLbl">Echoes earned</span> <b class="big" id="oEch">+0</b> · you now hold <b class="big" id="oEchTot">0</b></p>
      <p class="sub" id="oEchHow"></p>""")

run()
