import io

# --- the wall of text above the game -------------------------------------
# Three hundred and eight characters of controls, wrapping to three lines,
# 52 of the 86 pixels the bar takes off the top of a 768-high screen. It is
# the first thing anyone sees, and most of it -- the mute key, the narrator
# key, the music key, the gamepad, the second delver's five keys -- is
# reference material nobody needs before they have started.
#
# The pause sheet carries the controls now, and has room. So the bar keeps
# the verbs you need to begin and pause hands over the rest. Nothing is
# lost; it moves to where there is space to read it.
#
# Done by slicing between two markers rather than matching the line, since
# it is full of punctuation that every layer between here and the file gets
# a chance to mangle.

H = 'part_head.html'
s = io.open(H, encoding='utf-8').read()

start = s.index('<p class="kbdhelp">')
end = s.index('</p>', start) + len('</p>')
old = s[start:end]
assert 'Co-op P2' in old, 'not the line I meant'

new = ('<p class="kbdhelp"><kbd>WASD</kbd> move · <kbd>mouse</kbd> aim, or just face them · '
       '<kbd>click</kbd>/<kbd>Space</kbd> attack · <kbd>Shift</kbd> dash · '
       '<kbd>E</kbd> special · <kbd>F</kbd> potion · <kbd>P</kbd> pause, '
       'which lists the rest</p>')

io.open(H, 'w', encoding='utf-8', newline='').write(s[:start] + new + s[end:])
print('bar trimmed: %d chars -> %d' % (len(old), len(new)))
