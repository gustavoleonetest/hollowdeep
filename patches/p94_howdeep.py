from patch import edit, run

L = 'part_logic.js'
H = 'part_head.html'

# --- the game never said how far down it went ----------------------------
# Six zones, six wardens and the Heart at twenty-one, and a player who dies
# at depth six every time has no way of knowing any of it is there. The
# menu mentions the Heart once, in a paragraph above a row of portraits
# that people click straight past. The Barrow knows the deepest reach and
# says it as a bare number, which tells you nothing about what it is a
# number OUT OF.
#
# So: the whole descent laid out, with the names filled in only as far as
# you have actually been. Nothing new is stored for this -- the zones and
# the boss floors are a function of depth, and getting past a warden is the
# only way to the floor below it, so one number already knows all of it.
edit(L, """function renderBarrow() {
  $('barrowSub').textContent = 'You have ' + META.echoes + ' echoes. ' + (META.runs || 0) + ' descent' + (META.runs === 1 ? '' : 's') + ', deepest reach ' + (META.deepest || 1) + '.';""",
     """/* Each zone holds three depths and its warden stands on the last of them,
   so zone i runs from 3i+1 to 3i+3. You cannot reach 3i+4 without having
   put that warden down, which is what makes one number enough. */
function renderDeep() {
  const wrap = $('deepRows'); if (!wrap) return;
  wrap.innerHTML = '';
  const deepest = META.deepest || 1, wins = META.wins || 0;
  const row = (col, name, blurb, right, dim) => {
    const r = document.createElement('div'); r.className = 'srow'; r.style.setProperty('--c', col);
    if (dim) r.style.opacity = '.55';
    const info = document.createElement('div');
    const nm = document.createElement('span'); nm.className = 'nm'; nm.textContent = name; info.appendChild(nm);
    const bl = document.createElement('span'); bl.className = 'bl'; bl.textContent = blurb; info.appendChild(bl);
    r.appendChild(info);
    const bw = document.createElement('div'); bw.className = 'sbuy';
    const s = document.createElement('span'); s.className = 'bl'; s.textContent = right; bw.appendChild(s);
    r.appendChild(bw); wrap.appendChild(r);
  };
  for (let i = 0; i < ZONES.length; i++) {
    const z = ZONES[i], first = 3 * i + 1, last = 3 * i + 3;
    const seen = deepest >= first, felled = deepest >= last + 1;
    row(seen ? z.amb : '#454c5e',
        'Depths ' + first + '\\u2013' + last + (seen ? '  \\u00b7  ' + z.name : ''),
        seen ? z.boss + ' guards the key at depth ' + last + '.' : 'You have not been this deep.',
        felled ? 'Felled' : seen ? 'Still standing' : '\\u2014',
        !seen);
  }
  const won = wins > 0;
  row(won ? '#ffd24a' : '#454c5e',
      'Depth ' + FINAL_DEPTH + '  \\u00b7  The Hollow',
      won ? HEART_NAME + ' has been put down.'
          : deepest >= FINAL_DEPTH ? HEART_NAME + ' is still beating.'
          : HEART_NAME + ' waits at the bottom.',
      won ? 'Taken ' + wins + (wins === 1 ? ' time' : ' times') : '\\u2014',
      !won);
}
function renderBarrow() {
  $('barrowSub').textContent = 'You have ' + META.echoes + ' echoes. ' + (META.runs || 0) + ' descent' + (META.runs === 1 ? '' : 's') + ', deepest reach ' + (META.deepest || 1) + ' of ' + FINAL_DEPTH + '.';
  renderDeep();""")

edit(H, """      <div class="srows" id="barrowRows"></div>
      <div class="row"><button class="btn" id="barrowBack" type="button">Back</button></div>""",
     """      <div class="srows" id="barrowRows"></div>
      <p class="sub subhead">How deep it goes</p>
      <div class="srows" id="deepRows"></div>
      <div class="row"><button class="btn" id="barrowBack" type="button">Back</button></div>""")

edit(H, """.phoneonly{display:none}""",
     """.phoneonly{display:none}
.subhead{color:var(--bone); letter-spacing:.04em; text-transform:uppercase; font-size:13px; margin-top:4px}""")

run()
