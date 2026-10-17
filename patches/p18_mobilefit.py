from patch import edit, run

L = 'part_logic.js'

# --- know whether the touch controls are on screen, so text can dodge them -
edit(L, """  Z = clamp(Math.min(W / 740, H / 500), .66, 1.6);""",
     """  Z = clamp(Math.min(W / 740, H / 500), .66, 1.6);
  try { btnsOn = getComputedStyle($('dashBtn')).display !== 'none'; } catch (e) { btnsOn = false; }""")

edit(L, """let spTouch = false, dashTouch = false, bombTouch = false, clock = 0;""",
     """let spTouch = false, dashTouch = false, bombTouch = false, btnsOn = false, clock = 0;""")

edit(L, """    const miniTop = H - 10 - Math.min(156, W * .3) * .73;
    const vy = Math.min(H - (B ? 96 : 56), miniTop - 16);""",
     """    const stack = Math.min(156, W * .3) * .73;
    const miniTop = H - 10 - stack, btnTop = H - (stack + 22 + 64);
    const vy = Math.min(H - (B ? 96 : 56), (btnsOn ? Math.min(miniTop, btnTop) : miniTop) - 16);""")

# --- the depth banner drops below the HUD when it wraps on a phone --------
edit(L, """  if (G.banner && (G.state === 'play' || G.state === 'clear')) { ctx.globalAlpha = clamp(G.banner.t, 0, 1); ctx.fillStyle = C.bone; ctx.font = '400 54px "Pirata One",Georgia,serif'; ctx.textAlign = 'center'; ctx.fillText(G.banner.txt, W / 2, H * .3); if (G.banner.sub) { ctx.fillStyle = zn.amb; ctx.font = '600 13px "Spline Sans Mono",monospace'; ctx.fillText(G.banner.sub.toUpperCase(), W / 2, H * .3 + 28); } ctx.globalAlpha = 1; }""",
     """  if (G.banner && (G.state === 'play' || G.state === 'clear')) {
    const by = H * (W < 560 ? .44 : .3), bs = W < 560 ? 40 : 54;
    ctx.globalAlpha = clamp(G.banner.t, 0, 1); ctx.fillStyle = C.bone; ctx.font = '400 ' + bs + 'px "Pirata One",Georgia,serif'; ctx.textAlign = 'center'; ctx.fillText(G.banner.txt, W / 2, by);
    if (G.banner.sub) { ctx.fillStyle = zn.amb; ctx.font = '600 ' + (W < 560 ? 11 : 13) + 'px "Spline Sans Mono",monospace'; ctx.fillText(G.banner.sub.toUpperCase(), W / 2, by + 24); }
    ctx.globalAlpha = 1;
  }""")

run()
