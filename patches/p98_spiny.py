from patch import edit, run

L = 'part_logic.js'

# --- an elite modifier that was only ever a word -------------------------
# Six modifiers an elite can roll, and the game floats their names over its
# head so you know what you are facing. Five of them do something. `spiny`
# appears exactly once in the whole file: in the table that names it. A
# player fights something labelled Spiny and nothing spiny happens.
#
# It is the mirror of the delver's own thorns, so the shape was already
# there: it pricks whoever comes close enough to strike it.
#
# Two things it must NOT do. It must not go through hurtPlayer, because
# that grants half a second of invulnerability -- which would mean a Spiny
# elite protected you from its own attacks and the modifier was a gift. And
# it must count towards what the creatures took from you on the death
# screen, which is the sort of thing the reaper already taught me to
# remember.
edit(L, """  if (src) {
    applyElem(e, src, dmg);""",
     """  if (src) {
    applyElem(e, src, dmg);
    /* Spiny: it pricks whoever is close enough to have struck it. Its own
       cooldown rather than the delver's invulnerability, so being pricked
       never becomes a shield against the thing doing the pricking. */
    if (e.eaff && e.eaff.indexOf('spiny') >= 0 && src.cls && !src.down &&
        (!e.spineT || clock - e.spineT > .45) &&
        Math.hypot(src.x - e.x, src.y - e.y) < e.r + (src.r || 11) + 26) {
      e.spineT = clock;
      const back = Math.max(1, Math.round(e.dmg * .35)), was = src.hp;
      src.hp -= back; toll('foes', was, src);
      src.hurt = Math.max(src.hurt, .18);
      text(src.x, src.y - 16, '-' + back, '#9bd16a');
      burst(src.x, src.y, '#9bd16a', 6, 90, .8, 'spark');
      if (src.hp <= 0) downPlayer(src);
    }""")

run()
