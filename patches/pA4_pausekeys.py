from patch import edit, run

L = 'part_logic.js'

# The bar has handed the reference over, so the pause sheet has to actually
# hold it: the keys the bar no longer lists, the gamepad, and the second
# delver's own five, which only matter when there is a second delver.
edit(L, """  $('pauseKeys').textContent = btnsOn
    ? 'Left half of the screen moves you \\u00b7 right half aims and attacks \\u00b7 the buttons are dash, special and potion.'
    : 'WASD move \\u00b7 mouse aim \\u00b7 click or Space attack \\u00b7 Shift dash \\u00b7 E special \\u00b7 F potion \\u00b7 P pause. '
      + 'No mouse needed: face a foe and the shot finds it.';""",
     """  {
    const bits = [];
    if (btnsOn) {
      bits.push('Left half of the screen moves you, right half aims and attacks');
      bits.push('the buttons are dash, special and potion');
    } else {
      bits.push('WASD move, mouse aim, click or Space attack');
      bits.push('Shift dash, E special, F potion, P pause');
      bits.push('no mouse needed: face a foe and the shot finds it');
    }
    bits.push('M mute, V narrator, N music');
    bits.push('a gamepad works too: sticks move and aim, triggers fight');
    if (G.co) bits.push('the second delver: arrows move, Enter attacks, Right Shift dashes, Right Ctrl is the special, Right Alt the potion');
    $('pauseKeys').textContent = bits.join('  \\u00b7  ') + '.';
  }""")

run()
