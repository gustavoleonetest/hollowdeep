from patch import edit, run

L = 'part_logic.js'

# A bloat caught in a blast lights its own fuse instead of just taking damage,
# so a cluster pops in sequence rather than needing to be softened up first.
# It also keeps the chain on the game loop instead of the call stack.
edit(L, """  e.hp = 0; killFoe(e);
  for (const o of G.enemies.slice()) if (o !== e && !o.dead && o.hp > 0 && Math.hypot(o.x - e.x, o.y - e.y) < R + o.r) hurtFoe(o, dm * 1.15, Math.atan2(o.y - e.y, o.x - e.x));
}""", """  e.hp = 0; killFoe(e);
  for (const o of G.enemies.slice()) {
    if (o === e || o.dead || o.hp <= 0) continue;
    if (Math.hypot(o.x - e.x, o.y - e.y) >= R + o.r) continue;
    if (o.type === 'bloat' && o.fuse <= 0) { o.fuse = .22; o.alert = true; sfx('bone'); }
    else hurtFoe(o, dm * 1.15, Math.atan2(o.y - e.y, o.x - e.x));
  }
}""")

run()
