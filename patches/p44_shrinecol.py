from patch import edit, run

L = 'part_logic.js'

# Nine different hues told the player nothing and one of them (a grey Pact of
# Stone) vanished against the floor. Three colours by KIND is learnable at a
# glance: gold gives, crimson wants paying, violet will not say.
edit(L, """const isPact = (p) => PACTS.indexOf(p) >= 0;
const shrineCol = (sh) => sh.kind === 'mystery' ? '#b98cff' : sh.pact.col;""",
     """const isPact = (p) => PACTS.indexOf(p) >= 0;
const SHRINE_COL = { blessing: '#f0a23c', pact: '#e0556b', mystery: '#b98cff' };
const shrineCol = (sh) => SHRINE_COL[sh.kind] || '#f0a23c';""")

run()
