from patch import edit, run

L = 'part_logic.js'

# --- saved progress has to survive being wrong ---------------------------
# loadMeta caught bad JSON but copied whatever the keys held. A save where
# echoes was the string "40" turned the next payout into "4067": string
# concatenation, written straight back, growing every run. The Barrow then
# shows nonsense and nothing can be bought, with no way out but clearing
# site data. Coerce on the way in instead of trusting it.
edit(L, """function loadMeta() {
  try {
    const raw = JSON.parse(localStorage.getItem(META_KEY) || '{}');
    if (raw && typeof raw === 'object') for (const k in META) if (raw[k] !== undefined) META[k] = raw[k];
    if (!META.perks || typeof META.perks !== 'object') META.perks = {};
    const old = parseInt(localStorage.getItem('hollowdeep-best') || '0', 10);
    if (old > META.best) META.best = old;
  } catch (e) {}
}""",
     """/* a whole number at least `lo`, or the fallback if it is anything else */
function metaNum(v, dflt, lo) {
  const n = typeof v === 'number' ? v : parseFloat(v);
  return Number.isFinite(n) ? Math.max(lo, Math.floor(n)) : dflt;
}
function loadMeta() {
  try {
    const raw = JSON.parse(localStorage.getItem(META_KEY) || '{}');
    if (raw && typeof raw === 'object') {
      META.best = metaNum(raw.best, 0, 0);
      META.echoes = metaNum(raw.echoes, 0, 0);
      META.runs = metaNum(raw.runs, 0, 0);
      META.wins = metaNum(raw.wins, 0, 0);
      META.deepest = metaNum(raw.deepest, 1, 1);
      /* only a real boolean counts: anything else leaves the default, and
         null still means "has not been chosen yet" for reduced motion */
      for (const k of ['voice', 'music']) if (typeof raw[k] === 'boolean') META[k] = raw[k];
      if (typeof raw.reduceMotion === 'boolean' || raw.reduceMotion === null) META.reduceMotion = raw.reduceMotion;
      META.perks = {};
      if (raw.perks && typeof raw.perks === 'object') {
        for (const p of PERKS) {
          const lv = metaNum(raw.perks[p.id], 0, 0);
          if (lv > 0) META.perks[p.id] = Math.min(p.max, lv);
        }
      }
    }
    const old = parseInt(localStorage.getItem('hollowdeep-best') || '0', 10);
    if (Number.isFinite(old) && old > META.best) META.best = old;
  } catch (e) {}
}""")

run()
