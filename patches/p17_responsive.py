from patch import edit, run

H = 'part_head.html'
L = 'part_logic.js'

# --- the HUD row now carries more, so let it wrap instead of clipping -----
edit(H, """#hud{position:absolute; top:10px; left:10px; right:10px; display:flex; justify-content:space-between; align-items:flex-start; gap:10px; pointer-events:none}""",
     """#hud{position:absolute; top:10px; left:10px; right:10px; display:flex; flex-wrap:wrap; justify-content:space-between; align-items:flex-start; gap:8px 10px; pointer-events:none}""")

edit(H, """.stats{display:flex; gap:14px; font-size:13px; font-variant-numeric:tabular-nums}""",
     """.stats{display:flex; flex-wrap:wrap; gap:4px 14px; font-size:13px; font-variant-numeric:tabular-nums; min-width:0}
@media (max-width:520px){.stats{gap:3px 10px; font-size:12px}.hp{width:min(200px,54vw)}}""")

# --- keep the narrator clear of the minimap at every width ----------------
edit(L, """  if (G.voice) {
    const v = G.voice, a = clamp(v.t / .55, 0, 1), vy = H - (B ? 96 : 56);""",
     """  if (G.voice) {
    const v = G.voice, a = clamp(v.t / .55, 0, 1);
    const miniTop = H - 10 - Math.min(156, W * .3) * .73;
    const vy = Math.min(H - (B ? 96 : 56), miniTop - 16);""")

run()
