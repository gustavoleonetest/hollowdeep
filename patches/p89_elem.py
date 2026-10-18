from patch import edit, run

L = 'part_logic.js'

# --- an eightfold swing the player was never shown ------------------------
# A weapon can roll an element, and the element matters more than almost
# anything else on the item: 1.9x against a foe that fears it, 0.25x against
# one that shrugs it off. Best case to worst is nearly eight to one.
#
# What the card said was "Fire damage: burns, and skeletons fear it". No
# magnitude at all -- elemDmg was explicitly labelled as null and left out
# of the list of stats worth printing -- so two elemental weapons rolling
# anywhere from +30% to +60% looked identical. And the flavour named one foe
# per element off the top of someone's head: fire is in fact feared by three
# of the nine, and nothing anywhere mentioned who RESISTS an element, which
# is the half that costs you. Cold is shrugged off by the warden, which is
# the boss of most floors, and the game never said so.
#
# Both halves now come out of AFFIN itself, so the card cannot drift from
# what the dungeon actually does.

edit(L, """const AFFIN = {""",
     """/* The dungeon had no vocabulary for its own inhabitants: they are keys in a
   table and nothing ever had to name one out loud. */
const FOE_NAME = {
  gloam: 'gloam', wisp: 'wisps', bonewalker: 'bonewalkers', brute: 'brutes',
  hound: 'hounds', bloat: 'bloats', thief: 'thieves', reaper: 'the reaper',
  warden: 'wardens'
};
const ELEM_VERB = { fire: 'it burns', cold: 'it chills', shock: 'it arcs to others', poison: 'it rots' };
const AFFIN = {""")

edit(L, """function elemMul(e, elem) {""",
     """/* Who fears an element and who shrugs it off, read off the same table the
   damage is read off, so the two cannot disagree. */
function elemFoes(elem) {
  const weak = [], res = [];
  for (const t in AFFIN) {
    const a = AFFIN[t], nm = FOE_NAME[t] || t;
    if (a.weak === elem) weak.push(nm);
    else if (a.res === elem || a.res === 'all') res.push(nm);
  }
  return { weak, res };
}
const nameList = a => a.length < 2 ? (a[0] || '') : a.slice(0, -1).join(', ') + ' and ' + a[a.length - 1];
function elemMul(e, elem) {""")

# the generic stat loop no longer owns the element: it needs the whole item
edit(L, """  elem: v => ({ fire: 'Fire damage: burns, and skeletons fear it', cold: 'Cold damage: chills, and hounds fear it', shock: 'Lightning damage: arcs, and wisps fear it', poison: 'Poison damage: rots, and brutes fear it' })[v],
  elemDmg: () => null
};""",
     """};""")

edit(L, """  for (const k of ['dmg', 'arm', 'hp', 'crit', 'spd', 'cd', 'dash', 'sp', 'leech', 'thorns', 'gold', 'drain', 'elem']) {""",
     """  for (const k of ['dmg', 'arm', 'hp', 'crit', 'spd', 'cd', 'dash', 'sp', 'leech', 'thorns', 'gold', 'drain']) {""")

edit(L, """  if (it.setName) {""",
     """  if (it.s.elem) {
    const el = it.s.elem, nm = ELEM_NAME[el] || el;
    const share = Math.round((it.s.elemDmg || .4) * 100);
    out.push(nm.charAt(0).toUpperCase() + nm.slice(1) + ' damage: +' + share +
             '% of every hit, and ' + (ELEM_VERB[el] || 'it bites'));
    const f = elemFoes(el), bits = [];
    if (f.weak.length) bits.push(nameList(f.weak) + ' fear it');
    if (f.res.length) bits.push(nameList(f.res) + ' shrug it off');
    if (bits.length) {
      const line = bits.join('; ');
      out.push(line.charAt(0).toUpperCase() + line.slice(1));
    }
  }
  if (it.setName) {""")

run()
