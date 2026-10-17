from patch import edit, run

L = 'part_logic.js'

# --- gold spins, using art that was already in the atlas -------------------
# coin_0..coin_7 is a pre-rendered turn of a coin, and nothing ever drew it:
# drawItem sent gold straight to the hand-drawn fallback. Gold is the thing a
# player sees most, so this is the biggest change for the least work.
edit(L, """  if (!sprOk('props') || it.kind === 'gem' || it.kind === 'gold' || it.kind === 'food') return drawItemOld(it);
  const b = Math.sin(it.t * 4) * 2;""",
     """  if (!sprOk('props') || it.kind === 'gem' || it.kind === 'food') return drawItemOld(it);
  const b = Math.sin(it.t * 4) * 2;
  if (it.kind === 'gold') {
    /* it.t seeds the phase so a scattered hoard does not turn in lockstep */
    const fr = Math.floor((clock * 9 + it.t * 5) % 8);
    const lift = Math.abs(Math.sin(clock * 2.4 + it.t)) * 2.5;
    glow(it.x, it.y, 18, C.amber, .4 + Math.sin(clock * 3 + it.t) * .12);
    shadow(it.x, it.y + 8, 5 - lift * .4, 2, .3);
    if (!sprProp('coin_' + fr, it.x, it.y + 9 - lift, 1.05)) return drawItemOld(it);
    return;
  }""")

# --- a closed chest should look like it is holding something --------------
edit(L, """  else if (it.kind === 'chest') {
    const s = it.big ? 2.25 : 1.7;
    glow(it.x, it.y, 40 * (it.big ? 1.2 : 1), C.amber, .4 + Math.sin(it.t * 3) * .1); shadow(it.x, it.y + 9, 14 * (it.big ? 1.3 : 1), 5, .4);
    sprProp('chest', it.x, it.y + 10, s);
    ctx.fillStyle = 'rgba(255,230,150,.9)'; for (let i = 0; i < 3; i++) { const a = clock * 2 + i * 2.1; ctx.fillRect(it.x + Math.cos(a) * 15 * s / 1.7, it.y - 10 + Math.sin(a) * 6 - Math.abs(Math.sin(clock * 3 + i)) * 6, 2, 2); }
  }""",
     """  else if (it.kind === 'chest') {
    const s0 = it.big ? 2.25 : 1.7, pu = Math.sin(clock * 2.1 + it.t);
    /* breathing on the vertical only: it reads as something straining at the
       lid rather than the whole box pulsing */
    const sy = s0 * (1 + pu * .028), sx = s0 * (1 - pu * .018);
    glow(it.x, it.y, 40 * (it.big ? 1.2 : 1), C.amber, .4 + pu * .12);
    shadow(it.x, it.y + 9, 14 * (it.big ? 1.3 : 1), 5, .4);
    ctx.save(); ctx.translate(it.x, it.y + 10); ctx.scale(sx / s0, sy / s0); ctx.translate(-it.x, -(it.y + 10));
    sprProp('chest', it.x, it.y + 10, s0);
    ctx.restore();
    /* a glint that travels across the lid, so a chest catches the eye from
       across a room the way a lit altar does */
    const gt = (clock * .55 + it.t * .3) % 3.4;
    if (gt < .5) {
      const q = gt / .5, w = 13 * (it.big ? 1.3 : 1);
      ctx.save(); ctx.globalAlpha = Math.sin(q * Math.PI) * .75;
      ctx.fillStyle = '#fff6d8';
      ctx.fillRect(it.x - w + q * w * 2, it.y - 6 - (it.big ? 3 : 0), 2.5, 7);
      ctx.restore(); ctx.globalAlpha = 1;
    }
    ctx.fillStyle = 'rgba(255,230,150,.9)';
    for (let i = 0; i < 3; i++) { const a = clock * 2 + i * 2.1; ctx.fillRect(it.x + Math.cos(a) * 15 * s0 / 1.7, it.y - 10 + Math.sin(a) * 6 - Math.abs(Math.sin(clock * 3 + i)) * 6, 2, 2); }
  }""")

# --- opening it gets a hop and a landing ----------------------------------
edit(L, """function drawChestFx(f) {
  const t = f.t / .8, al = 1 - t, s = f.big ? 1.25 : 1;
  const open = Math.min(1, t * 2.6), crack = Math.min(1, t * 7);
  ctx.save(); ctx.translate(f.x, f.y); ctx.scale(s, s); ctx.globalAlpha = Math.min(1, al * 1.6);""",
     """function drawChestFx(f) {
  const t = f.t / .8, al = 1 - t, s = f.big ? 1.25 : 1;
  const open = Math.min(1, t * 2.6), crack = Math.min(1, t * 7);
  /* a short hop, then squash on the landing: the lid coming up on its own
     reads as a door opening, the hop reads as something giving way */
  const hopT = Math.min(1, t * 3.2);
  const hop = Math.sin(hopT * Math.PI) * 9;
  const land = hopT >= 1 ? Math.max(0, 1 - (t * 3.2 - 1) * 3.4) : 0;
  const sq = 1 + land * .18, st = 1 - land * .14;
  ctx.save(); ctx.translate(f.x, f.y - hop); ctx.scale(s * sq, s * st); ctx.globalAlpha = Math.min(1, al * 1.6);""")

# --- a crypt that has taken a beating should look like it ------------------
edit(L, """  sprProp('crypt', x, y + 15, .95, fl ? '#ffffff' : null, .8);
  glow(x, y + 5, 12, '#ff5a3a', .45 + p * .3);""",
     """  /* the atlas carries a second, broken crypt: show it once the thing is
     half down, so progress is visible without reading the bar */
  const hurt = n.hp / n.max < .5;
  const shake = hurt ? Math.sin(clock * 11 + n.x) * (fl ? 1.6 : .7) : 0;
  sprProp(hurt ? 'crypt_b' : 'crypt', x + shake, y + 15, .95, fl ? '#ffffff' : null, .8);
  glow(x, y + 5, 12, '#ff5a3a', (hurt ? .6 : .45) + p * .3);
  if (hurt && Math.random() < .25) G.parts.push({ x: x + rnd(-12, 12), y: y + rnd(-6, 8), vx: rnd(-.2, .2), vy: -.5, life: .45, max: .45, col: '#ff8a3a', s: 2, k: 'ember' });""")

run()
