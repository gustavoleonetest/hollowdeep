from patch import edit, run
L = 'part_logic.js'
# visibilitychange is fired at the document. It does reach a window listener
# by bubbling, but listening where it is actually dispatched is one less
# thing to depend on, and it is what every reference does.
edit(L, """addEventListener('visibilitychange', pauseForHidden);
addEventListener('pagehide', pauseForHidden);""",
     """if (typeof document !== 'undefined' && document.addEventListener) document.addEventListener('visibilitychange', pauseForHidden);
addEventListener('visibilitychange', pauseForHidden);
addEventListener('pagehide', pauseForHidden);
addEventListener('blur', pauseForHidden);""")
run()
