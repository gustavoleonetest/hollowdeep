from patch import edit, run

L = 'part_logic.js'
H = 'part_head.html'

# --- when the browser will not let the game save --------------------------
# Every storage call in here is already wrapped, so a browser that refuses
# does not crash the game. That is the smaller half of the problem. The
# larger half is that it refuses SILENTLY: someone in a private window can
# play for an hour, bank a few hundred echoes, buy half the Barrow, close
# the tab and find none of it ever existed. And now that a run can be
# carried on, they would simply never be offered it, with no hint why.
#
# Losing the progress is the browser's call and not ours to override. Saying
# nothing about it is ours. So: one probe at boot, and a line in the menu.
edit(L, """function saveMeta() { try { localStorage.setItem(META_KEY, JSON.stringify(META)); } catch (e) {} }""",
     """function saveMeta() { try { localStorage.setItem(META_KEY, JSON.stringify(META)); } catch (e) {} }
/* Write something, read it back, take it away again. Nothing short of the
   round trip will do: a private window hands you a store that reads fine and
   throws only when you try to keep something, and some setups throw on the
   mere mention of localStorage. Asked once and remembered, since this cannot
   change while the page is open -- `recheck` is for the tests. */
let storageOk = null;
function storageWorks(recheck) {
  if (storageOk !== null && !recheck) return storageOk;
  storageOk = false;
  try {
    const k = 'hollowdeep-probe', v = String(Date.now());
    localStorage.setItem(k, v);
    const back = localStorage.getItem(k);
    localStorage.removeItem(k);
    storageOk = back === v;
  } catch (e) { storageOk = false; }
  return storageOk;
}""")

# the menu says it, once, where it will be read
edit(L, """function showMenu() { syncOpts(); setMode(mode);""",
     """function showMenu() {
  /* said in the menu only: nobody needs this over the top of a fight */
  { const n = $('noSave'); if (n) n.hidden = storageWorks(); }
  syncOpts(); setMode(mode);""")

edit(L, """loadMeta(); G.best = META.best || 0;
pendingRun = loadRun();""",
     """storageWorks();
loadMeta(); G.best = META.best || 0;
pendingRun = loadRun();""")

# --- markup --------------------------------------------------------------
edit(H, """      <div class="row" id="resumeRow" hidden>""",
     """      <p class="sub nosave" id="noSave" hidden>This browser will not let the game keep anything. You can play, but echoes, the Barrow and carrying on where you left off will all be gone when you close the tab.</p>
      <div class="row" id="resumeRow" hidden>""")

edit(H, """.phoneonly{display:none}""",
     """.phoneonly{display:none}
.nosave{color:#f0a23c; border-left:3px solid #f0a23c; padding-left:10px}""")

# and on a phone it belongs with the title, above everything it affects
edit(H, """  #menu .sheet h2{order:1}
  #menu .sheet #resumeRow{order:2}""",
     """  #menu .sheet h2{order:1}
  #menu .sheet #noSave{order:2}
  #menu .sheet #resumeRow{order:3}""")

edit(H, """  #menu .sheet #modes{order:3}
  #menu .sheet #miniHint{order:4; display:block}
  #menu .sheet #pickHint{order:5}
  #menu .sheet #cards{order:6}
  #menu .sheet #opts{order:7}
  #menu .sheet .sub{order:8}""",
     """  #menu .sheet #modes{order:4}
  #menu .sheet #miniHint{order:5; display:block}
  #menu .sheet #pickHint{order:6}
  #menu .sheet #cards{order:7}
  #menu .sheet #opts{order:8}
  #menu .sheet .sub{order:9}""")

run()
