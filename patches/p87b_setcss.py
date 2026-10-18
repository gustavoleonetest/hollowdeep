from patch import edit, run
H = 'part_head.html'
edit(H, """.sheet .nosave{color:#f0a23c; border-left:3px solid #f0a23c; padding-left:10px}""",
     """.sheet .nosave{color:#f0a23c; border-left:3px solid #f0a23c; padding-left:10px}
/* losing a set is the one thing a stat-by-stat comparison cannot show you:
   the new item can be better on every line and still be a downgrade */
.setwarn{display:block; margin-top:6px; color:#f0a23c; font-size:12px}""")
run()
