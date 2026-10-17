from patch import edit, run

H = 'part_head.html'

# `.nosave` lost to `.sheet .sub`, which is more specific, so the warning was
# rendering in the same dim grey as the blurb around it -- present, but not
# reading as a warning at all. Found by asking the browser for the computed
# colour rather than trusting that the rule I wrote was the rule that won.
edit(H, """.nosave{color:#f0a23c; border-left:3px solid #f0a23c; padding-left:10px}""",
     """.sheet .nosave{color:#f0a23c; border-left:3px solid #f0a23c; padding-left:10px}""")

run()
