from patch import edit, run

L = 'part_logic.js'

# A font is a landmark with a column of light over it, so unlike a coin it
# wants standing room. Nothing is ever unreachable without this, it simply
# looks wrong half sunk into a wall.
edit(L, """function roomPoint(r) {""",
     """function clearPoint(rooms, want) {
  for (let i = 0; i < 60; i++) {
    const r = rooms[rint(0, rooms.length - 1)], p = roomPoint(r);
    if (openAt(p.x, p.y) && !blockedAt(p.x, p.y, want)) return p;
  }
  for (let i = 0; i < 60; i++) {
    const r = rooms[rint(0, rooms.length - 1)], p = roomPoint(r);
    if (openAt(p.x, p.y) && !blockedAt(p.x, p.y, 11)) return p;
  }
  return roomPoint(rooms[rint(0, rooms.length - 1)]);
}
function roomPoint(r) {""")

edit(L, """      const p = roomPoint(mids[rint(0, mids.length - 1)]);
      const sh = rollShrine(G.level);""",
     """      const p = clearPoint(mids, 20);
      const sh = rollShrine(G.level);""")

run()
