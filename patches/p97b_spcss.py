from patch import edit, run
H = 'part_head.html'
# the special is the one line on the card that is about what you can DO,
# so it reads a shade brighter than the flavour above it
edit(H, """.subhead{color:var(--bone); letter-spacing:.04em; text-transform:uppercase; font-size:13px; margin-top:4px}""",
     """.subhead{color:var(--bone); letter-spacing:.04em; text-transform:uppercase; font-size:13px; margin-top:4px}
.card .bl.sp{color:#c6cddd}""")
run()
