from patch import edit, run

L = 'part_logic.js'

# --- looking away should not cost you the run ----------------------------
# There was no visibility handling at all. Browsers do not stop a background
# tab outright, they slow it: measured here the loop kept going at about a
# twentieth of speed, so the drain kept draining and the foes kept acting
# while nobody was watching. Switching tabs, or taking a call on a phone,
# quietly cost health and could end a run in a fight the player never saw.
#
# Pausing on the way out is the easy half. The hard half is that pause was
# bound to P and nothing else, so a touch player auto-paused by switching
# apps would have had no way back in at all.
edit(L, """addEventListener('blur', () => { for (const k in keys) keys[k] = false; mouse.down = false; });""",
     """addEventListener('blur', () => { for (const k in keys) keys[k] = false; mouse.down = false; });
/* hold the run while the page is out of sight, and leave it held: dropping
   someone straight back into a fight they walked away from is worse */
function pauseForHidden() {
  if (typeof document === 'undefined') return;
  if (document.hidden && G.state === 'play' && !G.paused) {
    G.paused = true;
    for (const k in keys) keys[k] = false;
    mouse.down = false; spTouch = dashTouch = bombTouch = false;
    touch.move = null; touch.aim = null;
  }
}
addEventListener('visibilitychange', pauseForHidden);
addEventListener('pagehide', pauseForHidden);
/* P is no use on a phone, so anything that counts as "I am back" resumes */
function resumeFromPause() {
  if (G.state !== 'play' || !G.paused) return false;
  G.paused = false;
  return true;
}""")

# a tap or click anywhere is the way back for a touch player, and must not
# also swing the weapon on the way through
edit(L, """cv.addEventListener('mousedown', () => { mouse.down = true; mouse.last = performance.now(); initAudio(); });""",
     """cv.addEventListener('mousedown', () => { if (resumeFromPause()) return; mouse.down = true; mouse.last = performance.now(); initAudio(); });""")

edit(L, """cv.addEventListener('pointerdown', e => {
  if (e.pointerType === 'mouse') return; initAudio();""",
     """cv.addEventListener('pointerdown', e => {
  if (e.pointerType === 'mouse') return;
  if (resumeFromPause()) return;
  initAudio();""")

# --- and say how to get back in ------------------------------------------
edit(L, """  if (G.paused) { ctx.fillStyle = 'rgba(6,8,12,.6)'; ctx.fillRect(0, 0, W, H); ctx.fillStyle = C.bone; ctx.font = '400 54px "Pirata One",Georgia,serif'; ctx.textAlign = 'center'; ctx.fillText('Paused', W / 2, H / 2); }""",
     """  if (G.paused) {
    ctx.fillStyle = 'rgba(6,8,12,.6)'; ctx.fillRect(0, 0, W, H);
    ctx.fillStyle = C.bone; ctx.font = '400 54px "Pirata One",Georgia,serif'; ctx.textAlign = 'center';
    ctx.fillText('Paused', W / 2, H / 2 - 14);
    ctx.fillStyle = '#98a0b3'; ctx.font = '400 15px "Spline Sans Mono",monospace';
    ctx.fillText(btnsOn ? 'Tap to carry on' : 'Press P, or click, to carry on', W / 2, H / 2 + 26);
    ctx.textAlign = 'left';
  }""")

run()
