from patch import edit, run

L = 'part_logic.js'

# The tint argument was being passed as null, so the altar rendered in its own
# pale stone and swallowed the colour the ring was trying to signal.
edit(L, """  if (!sprProp('altar', it.x, it.y + 11, 1.6, null, .75)) {
    ctx.fillStyle = '#4a4740'; ctx.fillRect(it.x - 14, it.y - 12, 28, 24);
    ctx.fillStyle = hexA(col, .75); ctx.fillRect(it.x - 11, it.y - 17, 22, 6);
  }""",
     """  if (!sprProp('altar', it.x, it.y + 11, 1.38, col, .44 + pu * .16)) {
    ctx.fillStyle = '#4a4740'; ctx.fillRect(it.x - 14, it.y - 12, 28, 24);
    ctx.fillStyle = hexA(col, .75); ctx.fillRect(it.x - 11, it.y - 17, 22, 6);
  }""")

run()
