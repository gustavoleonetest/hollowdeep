from patch import edit, run

L = 'part_logic.js'

# --- one bad frame should not end the game -------------------------------
# requestAnimationFrame(frame) was the last statement in the loop, so
# anything that threw anywhere in a frame stopped the loop for good: the
# game froze on the last drawn image with no way back but a reload. This
# project has already had one such crash, a radial gradient handed a
# negative radius, which killed every frame after it.
#
# Scheduling the next frame first means a throw costs one frame instead of
# the run. The error is still reported for the first few, so a real fault is
# visible while developing rather than silently swallowed for ever.
edit(L, """function frame(now) {
  const dt = Math.min(.05, (now - last) / 1000); last = now; clock += dt;
  const _t0 = performance.now();""",
     """let frameErrs = 0;
function frameError(e) {
  if (frameErrs++ < 3 && typeof console !== 'undefined' && console.error) {
    console.error('Hollowdeep: a frame failed and was skipped', e);
    if (frameErrs === 3) console.error('Hollowdeep: further frame errors will not be reported');
  }
}
function frame(now) {
  /* before anything that could throw, so a bad frame costs a frame */
  requestAnimationFrame(frame);
  const _t0 = performance.now();
  try {
  const dt = Math.min(.05, (now - last) / 1000); last = now; clock += dt;""")

edit(L, """  perfTick(performance.now() - _t0);
  requestAnimationFrame(frame);
}""",
     """  } catch (e) { frameError(e); }
  perfTick(performance.now() - _t0);
}""")

run()
