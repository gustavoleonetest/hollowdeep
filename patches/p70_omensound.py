from patch import edit, run

L = 'part_logic.js'

# --- an omen arrived in silence ------------------------------------------
# Every other moment of that weight makes a noise: a pact and a boon ring the
# level chime, a warden falls with a boom, the door gives with a thud. An
# omen governs the whole floor and had only the narrator, which is a toggle
# and is missing entirely in browsers without speech synthesis. So on a good
# many machines a floor-wide change announced itself with nothing at all.
#
# Low, slow and hollow, so it does not read as an impact: a pedal note with a
# flattened fifth over it and a long filtered breath underneath.
edit(L, """  door: t => { tone(t, 92, .35, 'sine', .13, null, 50); nz(t, .18, .06, 'lowpass', 520); },""",
     """  door: t => { tone(t, 92, .35, 'sine', .13, null, 50); nz(t, .18, .06, 'lowpass', 520); },
  omen: t => {
    tone(t, 70, 1.5, 'sine', .11, null, 58);
    tone(t + .06, 99, 1.35, 'triangle', .05, null, 92);
    tone(t + .12, 140, 1.1, 'sine', .035, null, 132);
    nz(t, 1.3, .045, 'lowpass', 420);
    nz(t + .1, .5, .02, 'bandpass', 1300, .8);
  },""")

edit(L, """  if (G.omen) announceOnce('omen' + G.level, 6, G.omen.name + '. ' + G.omen.line, G.omen.col);""",
     """  if (G.omen) { sfx('omen'); announceOnce('omen' + G.level, 6, G.omen.name + '. ' + G.omen.line, G.omen.col); }""")

run()
