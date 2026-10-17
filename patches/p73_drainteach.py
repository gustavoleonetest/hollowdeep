from patch import edit, run

L = 'part_logic.js'

# Keying the drain lesson off "no foe within 220" meant it rarely fired:
# depth one puts foes near the start, so a new player's first floor read as
# combat and the one thing they most need telling went unsaid. What actually
# separates the drain from a fight is that nothing has hit you.
edit(L, """  if (P.hp < P.max * .9 && !G.enemies.some(e => e.hp > 0 && !e.dead && Math.hypot(e.x - P.x, e.y - P.y) < 220)) teach('drain');""",
     """  if (P.hp < P.max * .92 && clock - (P.lastHit || 0) > 3.5) teach('drain');""")

edit(L, """  P.hp -= d; P.inv = .55; P.hurt = .25; G.shake = Math.max(G.shake, .3);""",
     """  P.hp -= d; P.inv = .55; P.hurt = .25; P.lastHit = clock; G.shake = Math.max(G.shake, .3);""")

run()
