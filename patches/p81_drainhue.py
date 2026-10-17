from patch import edit, run

H = 'part_head.html'

# The first band was pale hatching over the red bar, and that was a mistake
# I only found by measuring it. A pale stripe over red differs from the red
# almost entirely in hue, so under tritanopia it collapsed: dE 3.8 against
# the low-health bar, which is to say invisible, at exactly the moment the
# drain matters most. Amber-vs-bone fared worse still, dE 2.2.
#
# Hatching DARK instead makes the difference a drop in luminance, which no
# dichromacy takes away. Worst case across normal, protan, deutan and tritan
# over both bar colours goes from 3.8 to 29.3. It also reads better: the bar
# looks eaten into rather than highlighted, which is what a drain does.
edit(H, """.fill.drain{position:absolute; top:0; width:0; transition:none; pointer-events:none;
  background:repeating-linear-gradient(135deg, rgba(235,228,210,.42) 0 2px, rgba(235,228,210,0) 2px 5px)}
.fill.drain.worse{background:repeating-linear-gradient(135deg, rgba(255,164,60,.62) 0 2px, rgba(255,164,60,0) 2px 5px)}""",
     """.fill.drain{position:absolute; top:0; width:0; transition:none; pointer-events:none;
  background:repeating-linear-gradient(135deg, rgba(8,10,14,.62) 0 2px, rgba(8,10,14,0) 2px 5px)}
.fill.drain.worse{background:repeating-linear-gradient(135deg, rgba(120,62,10,.62) 0 2px, rgba(120,62,10,0) 2px 5px)}""")

run()
