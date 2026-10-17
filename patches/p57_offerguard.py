from patch import edit, run

L = 'part_logic.js'

# A delver who has learned three of its four boons is offered one card, not
# three. chooseUp guards the index, but applyUpgrade is the thing that
# actually mutates and it took whatever it was handed.
edit(L, """function applyUpgrade(i) {
  const o = G.offer;""",
     """function applyUpgrade(i) {
  const o = G.offer;
  if (!o) return;
  if ((o.kind === 'boon' || !o.kind || o.kind === 'up') && !o.opts[i]) return;""")

# and the hint should name the cards that are actually there
edit(L, """    $('lootHint').textContent = 'Click a card or press 1, 2 or 3. This one changes how your attack works.';""",
     """    $('lootHint').textContent = (o.opts.length > 1
      ? 'Click a card or press 1' + (o.opts.length > 2 ? ', 2 or 3' : ' or 2') + '.'
      : 'Click the card or press 1.') + ' This one changes how your attack works.';""")

run()
