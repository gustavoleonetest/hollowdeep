from patch import edit, run

L = 'part_logic.js'
H = 'part_head.html'

# --- you could never look at what you were carrying ----------------------
# Gear is the spine of a run: three slots, rolled affixes, sets, curses,
# elements. Once equipped, the only way to read any of it was to hover the
# W / A / T glyphs in the corner for a tooltip. A phone has no hover, so a
# touch player could equip a thing and then never see it again -- not its
# name, not its stats, not whether their set was up.
#
# Pause is where that belongs. It already stops the world; it may as well
# say who you have become.

# a card on the pause sheet is not a choice, so it must not act like one
edit(L, """  b.addEventListener('click', () => chooseUp(idx));
  return b;""",
     """  /* idx below zero means this card is being shown, not offered */
  if (idx >= 0) b.addEventListener('click', () => chooseUp(idx));
  else b.tabIndex = -1;
  return b;""")

edit(L, """let lootShown = false;""",
     """let lootShown = false, pauseShown = false;
/* What you are carrying, and what it has made of you. */
function showPaused() {
  const wrap = $('pauseGear'); wrap.innerHTML = '';
  const sheets = [], extras = [];
  for (const P of G.players) {
    const who = G.co ? 'P' + (P.idx + 1) + ' \\u00b7 ' : '';
    sheets.push(who + sheetLine(P));
    for (const slot of SLOTS) {
      wrap.appendChild(gearCard(who + slot, P.gear[slot], -1, '', P, null));
    }
    const boons = (BOONS[P.cls.key] || []).filter(b => bn(P, b.id)).map(b => b.name);
    const pacts = (P.pacts || []).map(q => q.name);
    const bits = [];
    if (boons.length) bits.push('Boons: ' + boons.join(', '));
    if (pacts.length) bits.push('Pacts: ' + pacts.join(', '));
    if (bits.length) extras.push(who + bits.join('  \\u00b7  '));
  }
  $('pauseS').textContent = sheets.join('   |   ');
  $('pauseExtra').textContent = extras.join('   |   ');
  $('pauseExtra').hidden = extras.length === 0;
  $('pauseHint').textContent = btnsOn ? 'Tap anywhere to carry on.' : 'Press P, or click, to carry on.';
  $('paused').hidden = false;
}""")

# shown and hidden by the same hand that shows the loot screen, so it does
# not matter which of the several ways into a pause was taken
edit(L, """  if (G.state === 'offer' && !lootShown) { lootShown = true; showLoot(); } else if (G.state !== 'offer' && lootShown) { lootShown = false; $('loot').hidden = true; }""",
     """  if (G.state === 'offer' && !lootShown) { lootShown = true; showLoot(); } else if (G.state !== 'offer' && lootShown) { lootShown = false; $('loot').hidden = true; }
  const wantPause = G.paused && G.state === 'play';
  if (wantPause && !pauseShown) { pauseShown = true; showPaused(); }
  else if (!wantPause && pauseShown) { pauseShown = false; $('paused').hidden = true; }""")

# the overlay sits over the canvas, so the canvas no longer hears the tap
# that was the only way back in for a touch player
edit(L, """$('resume').addEventListener('click', () => {""",
     """$('paused').addEventListener('click', () => { resumeFromPause(); });
$('resume').addEventListener('click', () => {""")

# and the canvas no longer has to say it
edit(L, """  if (G.paused) {
    ctx.fillStyle = 'rgba(6,8,12,.6)'; ctx.fillRect(0, 0, W, H);
    ctx.fillStyle = C.bone; ctx.font = '400 54px "Pirata One",Georgia,serif'; ctx.textAlign = 'center';
    ctx.fillText('Paused', W / 2, H / 2 - 14);
    ctx.fillStyle = '#98a0b3'; ctx.font = '400 15px "Spline Sans Mono",monospace';
    ctx.fillText(btnsOn ? 'Tap to carry on' : 'Press P, or click, to carry on', W / 2, H / 2 + 26);
    ctx.textAlign = 'left';
  }""",
     """  /* the pause sheet is an overlay now, and dims the stage itself */""")

# --- markup --------------------------------------------------------------
edit(H, """  <div class="overlay" id="loot" hidden>""",
     """  <div class="overlay" id="paused" hidden>
    <div class="sheet">
      <h2>Paused</h2>
      <p class="sub" id="pauseS"></p>
      <div class="cards" id="pauseGear"></div>
      <p class="sub" id="pauseExtra" hidden></p>
      <p class="sub" id="pauseHint">Press P, or click, to carry on.</p>
    </div>
  </div>
  <div class="overlay" id="loot" hidden>""")

run()
