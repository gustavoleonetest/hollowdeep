from patch import edit, run

L = 'part_logic.js'
H = 'part_head.html'

# A goal nobody is told about is not a goal. Say what is at the bottom, and
# keep a count of how often it has been put down.
edit(H, """Keep a potion for when the floor turns against you. Best run: <span class="big" id="best">0</span></p>""",
     """Keep a potion for when the floor turns against you. <b>The Hollow Heart waits at depth 21</b> — put it down and the deep is yours. Best run: <span class="big" id="best">0</span><span id="menuWins"></span></p>""")

edit(L, """loadMeta(); G.best = META.best || 0;""",
     """loadMeta(); G.best = META.best || 0;
{ /* a trophy line, once there is something to show */
  const w = META.wins || 0, el = $('menuWins');
  if (el && w > 0) el.textContent = '  \\u00b7  Heart taken ' + w + (w === 1 ? ' time' : ' times');
}""")

run()
