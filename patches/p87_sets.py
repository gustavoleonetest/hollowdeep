from patch import edit, run

L = 'part_logic.js'

# --- a promise made on the item and never kept where it mattered ---------
# Gear rolls into three sets, two pieces grant a bonus and three grant it
# twice over. All of that works: recalc counts the pieces and folds the
# bonus in. It even records what is active, on P.sets -- which is written
# and then read by absolutely nothing.
#
# So the item card says "2 pieces grant more", the bonus quietly happens,
# and the player is never told it did. Worse, at the one moment the set is
# supposed to matter -- a better item turning up for a slot a set piece is
# in -- nothing warns that taking it breaks the set. That is precisely the
# decision the system exists to create, and it was being made blind.

# recalc already knows; let it say which set, not just its name
edit(L, """    P.sets.push({ name: S.name, n: setN[id] });""",
     """    P.sets.push({ id, name: S.name, n: setN[id] });""")

edit(L, """const BASE_STAT = { weapon: 'dmg', armour: 'arm', trinket: 'crit' };""",
     """const BASE_STAT = { weapon: 'dmg', armour: 'arm', trinket: 'crit' };
/* How many pieces of a set a delver has on. `exceptSlot` leaves one slot
   out, because equipping something REPLACES what is in that slot rather
   than adding to it -- counting the worn piece as well would promise a
   pair that taking the new item would actually break. */
function setWorn(P, id, exceptSlot) {
  let n = 0;
  if (!id || !P || !P.gear) return 0;
  for (const slot of SLOTS) {
    if (slot === exceptSlot) continue;
    const g = P.gear[slot];
    if (g && g.set === id) n++;
  }
  return n;
}
const setLive = (P, id) => !!id && (P.sets || []).some(s => s.id === id);""")

# --- the line on the item, which now knows who is reading it -------------
edit(L, """function itemLines(it) {""",
     """function itemLines(it, P) {""")

edit(L, """  if (it.setName) out.push('Set: ' + it.setName + ' (2 pieces grant more)');
  return out;""",
     """  if (it.setName) {
    /* with a delver to ask, say what taking this would actually do */
    if (P) {
      const would = setWorn(P, it.set, it.slot) + 1;
      out.push('Set: ' + it.setName + (would >= 3 ? ' \\u2014 this would complete all three'
        : would === 2 ? ' \\u2014 this would make a pair'
        : ' \\u2014 no other piece of it yet'));
    } else out.push('Set: ' + it.setName + ' (2 pieces grant more)');
  }
  return out;""")

# --- and the warning that was missing entirely ---------------------------
# Losing a set is the one thing a straight stat comparison cannot show you:
# the new item can be better in every line and still be a downgrade.
edit(L, """  const s = document.createElement('span'); s.className = 'itemstats';
  if (item) for (const line of itemLines(item)) { const d = document.createElement('span'); d.textContent = line; s.appendChild(d); }""",
     """  const s = document.createElement('span'); s.className = 'itemstats';
  if (item) for (const line of itemLines(item, who)) { const d = document.createElement('span'); d.textContent = line; s.appendChild(d); }""")

edit(L, """function gearCard(label, item, idx, hint) {""",
     """function gearCard(label, item, idx, hint, who, breaks) {""")

edit(L, """  const h = document.createElement('span'); h.className = 'rare'; h.textContent = hint; b.appendChild(h);""",
     """  if (breaks) {
    const w = document.createElement('span'); w.className = 'setwarn';
    w.textContent = 'Taking this breaks ' + breaks;
    b.appendChild(w);
  }
  const h = document.createElement('span'); h.className = 'rare'; h.textContent = hint; b.appendChild(h);""")

edit(L, """    wrap.appendChild(gearCard('New \\u00b7 ' + (RARITY[o.item.rar] || {}).name, o.item, 0, '1 \\u00b7 Equip'));
    wrap.appendChild(gearCard('Worn \\u00b7 ' + o.item.slot, o.cur, 1, '2 \\u00b7 Keep this'));""",
     """    /* the set the worn piece is holding up, if swapping it would drop the
       count back under two */
    let breaks = null;
    if (o.cur && o.cur.set && setLive(P, o.cur.set) && setWorn(P, o.cur.set, o.cur.slot) + (o.item.set === o.cur.set ? 1 : 0) < 2) {
      const S = SETS.find(x => x.id === o.cur.set);
      breaks = S ? S.name : null;
    }
    wrap.appendChild(gearCard('New \\u00b7 ' + (RARITY[o.item.rar] || {}).name, o.item, 0, '1 \\u00b7 Equip', P, breaks));
    wrap.appendChild(gearCard('Worn \\u00b7 ' + o.item.slot, o.cur, 1, '2 \\u00b7 Keep this', P, null));""")

# --- what you are already wearing, on the sheet line ---------------------
edit(L, """  return P.cls.name + ' \\u00b7 level ' + P.plvl + ' \\u00b7 ' + P.max + ' max health, damage +' + pct(P.dmgMul) + '%, speed +' + pct(P.spdMul) + '%, attacks ' + pct(1 / P.cdMul) + '% faster.';""",
     """  let line = P.cls.name + ' \\u00b7 level ' + P.plvl + ' \\u00b7 ' + P.max + ' max health, damage +' + pct(P.dmgMul) + '%, speed +' + pct(P.spdMul) + '%, attacks ' + pct(1 / P.cdMul) + '% faster.';
  if (P.sets && P.sets.length) {
    line += ' Wearing ' + P.sets.map(s => s.name + (s.n >= 3 ? ' in full' : '')).join(' and ') + '.';
  }
  return line;""")

# --- and a mark in the HUD, so a live set is visible at a glance ---------
edit(L, """    sp.title = it ? it.name + ' \\u2014 ' + itemLines(it).join(', ') : 'No ' + sp.dataset.s;""",
     """    /* underlined means this piece is holding up a set that is live: a
       typographic mark, so it does not lean on colour */
    sp.style.textDecoration = it && setLive(P, it.set) ? 'underline' : 'none';
    sp.title = it ? it.name + ' \\u2014 ' + itemLines(it, P).join(', ') : 'No ' + sp.dataset.s;""")

run()
