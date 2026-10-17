from patch import edit, run

L = 'part_logic.js'

# --- attachments that break the four shared rigs apart --------------------
#     Recolouring alone makes a crowd noisier; a changed outline does not.
edit(L, """function drawFoeSpr(e, mv) {""",
     """function foeAdorn(e, S, x, y) {
  const r = e.r, f = e.face || 0, ca = Math.cos(f), sa = Math.sin(f);
  const by = y + S.fy - r * 1.8;
  ctx.save();
  if (e.type === 'bloat') {
    /* a swollen sac and horns: never mistake it for the gloam it shares a rig with */
    const sw = e.fuse > 0 ? 1 + (1 - e.fuse / .6) * .55 : 1;
    ctx.fillStyle = e.fuse > 0 ? 'rgba(226,255,176,.9)' : 'rgba(126,191,74,.85)';
    for (const o of [[-.82, .1, .46], [.82, .16, .42], [0, -.52, .4]]) {
      ctx.beginPath(); ctx.ellipse(x + o[0] * r * sw, by + o[1] * r * sw, o[2] * r * sw, o[2] * r * .86 * sw, 0, 0, TAU); ctx.fill();
    }
    ctx.fillStyle = '#4e7128';
    for (const sg of [-1, 1]) { ctx.beginPath(); ctx.moveTo(x + sg * r * .42, by - r * .55); ctx.lineTo(x + sg * r * .78, by - r * 1.4); ctx.lineTo(x + sg * r * .12, by - r * .68); ctx.fill(); }
  } else if (e.type === 'reaper') {
    /* a scythe and a torn hood, so Death never reads as a wisp */
    const sg = ca >= 0 ? 1 : -1, hx = x + sg * r * 1.25, hy = y + S.fy - r * .4;
    ctx.strokeStyle = 'rgba(60,64,78,.95)'; ctx.lineWidth = 2.6; ctx.lineCap = 'round';
    ctx.beginPath(); ctx.moveTo(hx, hy); ctx.lineTo(hx - sg * r * .18, hy - r * 3.1); ctx.stroke();
    ctx.strokeStyle = 'rgba(226,232,245,.95)'; ctx.lineWidth = 3.4;
    ctx.beginPath(); ctx.arc(hx - sg * r * .18, hy - r * 3.05, r * 1.05, sg > 0 ? -1.9 : -1.25, sg > 0 ? -.05 : .8, sg < 0);
    ctx.stroke(); ctx.lineCap = 'butt';
    ctx.fillStyle = 'rgba(214,222,240,.75)';
    for (const s2 of [-1, 1]) { ctx.beginPath(); ctx.moveTo(x + s2 * r * .5, by - r * .3); ctx.lineTo(x + s2 * r * .78, by - r * 1.35); ctx.lineTo(x + s2 * r * .06, by - r * .5); ctx.fill(); }
  } else if (e.type === 'thief') {
    /* the swag sack rides on its back, and swells once it has your gold */
    const bx = x - ca * r * 1.05, byy = y + S.fy - r * 1.5, s2 = e.loot > 0 ? 1.25 : .9;
    ctx.fillStyle = e.loot > 0 ? 'rgba(220,168,66,.95)' : 'rgba(120,98,62,.9)';
    ctx.beginPath(); ctx.ellipse(bx, byy, r * .52 * s2, r * .6 * s2, 0, 0, TAU); ctx.fill();
    ctx.strokeStyle = 'rgba(60,46,26,.9)'; ctx.lineWidth = 1.6;
    ctx.beginPath(); ctx.moveTo(bx - r * .3, byy - r * .5); ctx.lineTo(bx + r * .3, byy - r * .5); ctx.stroke();
  } else if (e.boss && e.kind === 'caller') {
    /* a back banner, the classic elite silhouette tell */
    const w = r * .72, h = r * 3.3, bxx = x - ca * r * .5, byy = y + S.fy - r * 2;
    ctx.fillStyle = 'rgba(70,58,98,.92)';
    ctx.beginPath(); ctx.moveTo(bxx - w, byy); ctx.lineTo(bxx + w, byy); ctx.lineTo(bxx + w, byy - h);
    ctx.lineTo(bxx, byy - h * .88); ctx.lineTo(bxx - w, byy - h); ctx.fill();
    ctx.fillStyle = 'rgba(190,160,255,.8)';
    ctx.beginPath(); ctx.arc(bxx, byy - h * .62, r * .26, 0, TAU); ctx.fill();
    ctx.strokeStyle = 'rgba(40,34,56,.95)'; ctx.lineWidth = 2;
    ctx.beginPath(); ctx.moveTo(bxx, byy + r * .4); ctx.lineTo(bxx, byy - h); ctx.stroke();
  } else if (e.boss && e.kind === 'maw') {
    /* shoulder spines */
    ctx.fillStyle = 'rgba(206,110,52,.95)';
    for (const sg of [-1, 1]) for (let i = 0; i < 3; i++) {
      const px = x + sg * (r * .75 + i * r * .24), py = by + r * .18 - i * r * .1;
      ctx.beginPath(); ctx.moveTo(px - r * .16, py); ctx.lineTo(px + sg * r * .1, py - r * (.9 - i * .18)); ctx.lineTo(px + r * .16, py); ctx.fill();
    }
  } else if (e.boss) {
    /* a high collar for the Count */
    ctx.fillStyle = 'rgba(120,52,74,.92)';
    for (const sg of [-1, 1]) {
      ctx.beginPath(); ctx.moveTo(x + sg * r * .36, by + r * .1);
      ctx.quadraticCurveTo(x + sg * r * 1.25, by - r * .5, x + sg * r * .85, by - r * 1.5);
      ctx.quadraticCurveTo(x + sg * r * .4, by - r * .7, x + sg * r * .2, by + r * .1); ctx.fill();
    }
  }
  ctx.restore();
}
function drawFoeSpr(e, mv) {""")

edit(L, """  if (e.elite && e.eaff && e.eaff.length) {
    const nm = e.eaff.map(id => { const a = EAFF.find(z => z.id === id); return a ? a.name : null; }).filter(Boolean).join(' \\u00b7 ');""",
     """  foeAdorn(e, S, x, y);
  if (e.elite && e.eaff && e.eaff.length) {
    const nm = e.eaff.map(id => { const a = EAFF.find(z => z.id === id); return a ? a.name : null; }).filter(Boolean).join(' \\u00b7 ');""")

# --- idle sway, a real flinch, and shape on every boss wind-up ------------
edit(L, """  if (e.type === 'bloat' && e.fuse > 0) { const f = 1 - e.fuse / .6; sx *= 1 + f * .42; sy *= 1 + f * .42; }""",
     """  if (e.type === 'bloat' && e.fuse > 0) { const f = 1 - e.fuse / .6; sx *= 1 + f * .42; sy *= 1 + f * .42; }
  /* idle sway, so a waiting monster is not a frozen one */
  if (mv <= .12 && !ghost && e.atk <= 0) { rot += Math.sin(e.t * 1.5 + e.x * .013) * .035; oy += Math.sin(e.t * 2.1 + e.y * .011) * .5; }
  /* flinch away from the blow, not just squash */
  if (e.fl > 0) { const q = e.fl / .2 * (boss ? .3 : 1); ox -= Math.cos(e.fa || 0) * 3.4 * q; oy -= Math.sin(e.fa || 0) * 2.6 * q; }
  /* bosses telegraph with posture as well as light */
  if (boss && e.st && e.st !== 'chase') {
    const dur = BOSS_DUR[e.st] || .6, p = Math.min(1, e.stt / dur);
    if (e.st === 'slam') { sy *= 1 - p * .12; sx *= 1 + p * .1; oy += p * r6(e) * .2; }
    else if (e.st === 'volley') { rot -= .16 * p; ox -= Math.cos(e.face || 0) * 4 * p; }
    else if (e.st === 'raise') { sy *= 1 + p * .14; sx *= 1 - p * .05; oy -= p * 4; }
    else if (e.st === 'blink') { const q = Math.min(1, p * 1.6); sx *= 1 - q * .55; sy *= 1 + q * .35; }
    else if (e.st === 'quake') { sy *= 1 + p * .1; sx *= 1 - p * .06; }
    else if (e.st === 'charge' || e.st === 'rampage') {
      const seg = e.st === 'rampage' ? .7 : 1.42, w = e.st === 'rampage' ? .26 : .68, q = Math.min(1, (e.stt % seg) / w);
      if ((e.stt % seg) < w) { ox -= Math.cos(e.ca != null ? e.ca : 0) * 6 * q; sx *= 1 - q * .08; sy *= 1 + q * .1; }
      else { sx *= 1.1; sy *= .94; }
    }
  }""")

edit(L, """function foeAdorn(e, S, x, y) {""",
     """const r6 = e => e.r;
function foeAdorn(e, S, x, y) {""")

run()
