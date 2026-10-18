from patch import edit, run

L = 'part_logic.js'

# --- four abilities nobody was ever told about ---------------------------
# Every delver has a special on a nine second cooldown with its own bar in
# the HUD, and the game never says what it does. The name flashes over your
# head the moment you use it, which is a label on an event, not something
# you can read beforehand. The menu card describes the ordinary attack and
# stops there.
#
# They are not small. Shield Slam sweeps arrows out of the air -- a defence
# against the one thing that reaches you from the dark -- and nothing
# anywhere mentioned it. Entangle roots a room for three seconds. Shadow
# Step is seven tiles of invulnerable movement and a ring of daggers.
#
# Written from what the code does, not from the names.
edit(L, """const SPECIALS = { bulwark: 'Shield Slam', ember: 'Fire Nova', sable: 'Shadow Step', thistle: 'Entangle' };""",
     """const SPECIALS = { bulwark: 'Shield Slam', ember: 'Fire Nova', sable: 'Shadow Step', thistle: 'Entangle' };
const SPECIAL_DESC = {
  bulwark: 'a shield for a moment, everything near you hurled back, and arrows already in the air swept out of it',
  ember: 'a burst all around you, and ten bolts thrown outward through whatever is left',
  sable: 'slip forward untouchable, and leave a ring of daggers where you were',
  thistle: 'roots everything near you to the floor for a few seconds'
};
const specialLine = c => SPECIALS[c.key] + ' \\u2014 ' + SPECIAL_DESC[c.key] + '.';""")

# on the card, where the delver is chosen
edit(L, """    b.innerHTML = '<canvas class="gl" width="96" height="96"></canvas><span class="nm">' + c.name + '</span><span class="bl">' + c.blurb + '</span>' +""",
     """    b.innerHTML = '<canvas class="gl" width="96" height="96"></canvas><span class="nm">' + c.name + '</span><span class="bl">' + c.blurb + '</span>' +
      '<span class="bl sp">Special: ' + specialLine(c) + '</span>' +""")

# and on the pause sheet, where it is remembered
edit(L, """    const bits = [];
    if (boons.length) bits.push('Boons: ' + boons.join(', '));
    if (pacts.length) bits.push('Pacts: ' + pacts.join(', '));
    if (bits.length) extras.push(who + bits.join('  \\u00b7  '));""",
     """    const bits = ['Special: ' + specialLine(P.cls)];
    if (boons.length) bits.push('Boons: ' + boons.join(', '));
    if (pacts.length) bits.push('Pacts: ' + pacts.join(', '));
    extras.push(who + bits.join('  \\u00b7  '));""")

run()
