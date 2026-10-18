from patch import edit, run

L = 'part_logic.js'
H = 'part_head.html'

# --- two things the pause sheet was the right place for ------------------
# First, the controls. They are printed above the stage, and on a short
# screen the game hides that line the moment you start playing -- which is
# every phone. So the one place a phone player could read what the buttons
# do was the place they could not be while playing.
#
# Second, a way out. A roguelike gets bad starts, and the only exits from
# one were to die on purpose or close the tab. Dying on purpose takes
# minutes of standing still, now that the drain is the thing that kills
# you. Giving up ends the run properly: the echoes are banked exactly as a
# death banks them, so the descent still counts for something.

edit(H, """      <p class="sub" id="pauseExtra" hidden></p>
      <p class="sub" id="pauseHint">Press P, or click, to carry on.</p>""",
     """      <p class="sub" id="pauseExtra" hidden></p>
      <p class="sub" id="pauseKeys"></p>
      <div class="row">
        <button class="btn alt" id="giveUp" type="button">Give up this descent</button>
      </div>
      <p class="sub" id="pauseHint">Press P, or click, to carry on.</p>""")

edit(L, """  $('pauseHint').textContent = btnsOn ? 'Tap anywhere to carry on.' : 'Press P, or click, to carry on.';""",
     """  $('pauseKeys').textContent = btnsOn
    ? 'Left half of the screen moves you \\u00b7 right half aims and attacks \\u00b7 the buttons are dash, special and potion.'
    : 'WASD move \\u00b7 mouse aim \\u00b7 click or Space attack \\u00b7 Shift dash \\u00b7 E special \\u00b7 F potion \\u00b7 P pause.';
  giveUpArmed = false; $('giveUp').textContent = 'Give up this descent';
  $('pauseHint').textContent = btnsOn ? 'Tap anywhere to carry on.' : 'Press P, or click, to carry on.';""")

# the overlay resumes on a click, so this button has to keep its own click
# to itself or giving up would simply carry on
edit(L, """$('paused').addEventListener('click', () => { resumeFromPause(); });""",
     """let giveUpArmed = false;
$('giveUp').addEventListener('click', e => {
  if (e && e.stopPropagation) e.stopPropagation();
  if (!giveUpArmed) { giveUpArmed = true; $('giveUp').textContent = 'Really give up?'; return; }
  giveUpArmed = false;
  G.gaveUp = true; G.paused = false; pauseShown = false; $('paused').hidden = true;
  die();
});
$('paused').addEventListener('click', () => { resumeFromPause(); });""")

# a run that was put down is not a run that was taken
edit(L, """  G.level = 1; G.score = 0; G.won = false; G.winPending = false; genLevel(); G.state = 'play'; G.paused = false;""",
     """  G.level = 1; G.score = 0; G.won = false; G.winPending = false; G.gaveUp = false; genLevel(); G.state = 'play'; G.paused = false;""")

edit(L, """  G.tollDeep = r.tollDeep; G.tollFoes = r.tollFoes;""",
     """  G.tollDeep = r.tollDeep; G.tollFoes = r.tollFoes; G.gaveUp = false;""")

edit(L, """  announce(G.won ? 'You carried the Heart out of the dark' : 'Swallowed by the deep', G.won ? '#ffd24a' : '#d9534f');""",
     """  announce(G.won ? 'You carried the Heart out of the dark' : G.gaveUp ? 'You turned back' : 'Swallowed by the deep', G.gaveUp ? '#98a0b3' : G.won ? '#ffd24a' : '#d9534f');""")

edit(L, """  $('oTitle').textContent = won ? 'The Hollow is still.' : G.won ? 'You carried it out of the dark.' : 'Swallowed by the deep.';
  $('oLine').textContent = won
    ? 'You put down ' + HEART_NAME + ' at depth ' + G.level + '. Climb out with it, or see what lies below.'
    : 'You reached depth ' + G.level + ' of ' + (G.zone ? G.zone.name : 'the dark') + '.';""",
     """  $('oTitle').textContent = won ? 'The Hollow is still.' : G.won ? 'You carried it out of the dark.'
    : G.gaveUp ? 'You turned back.' : 'Swallowed by the deep.';
  $('oLine').textContent = won
    ? 'You put down ' + HEART_NAME + ' at depth ' + G.level + '. Climb out with it, or see what lies below.'
    : (G.gaveUp ? 'You left the dark at depth ' : 'You reached depth ') + G.level +
      ' of ' + (G.zone ? G.zone.name : 'the dark') + '.';""")

run()
