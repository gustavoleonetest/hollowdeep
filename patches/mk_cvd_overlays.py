import io

p = 'tools/colour-vision.py'
s = io.open(p, encoding='utf-8').read()

anchor = """print('Closest pair in each set, per kind of vision (CIE76 dE):\\n')"""
assert s.count(anchor) == 1, 'anchor not unique'
assert 'OVERLAYS' not in s, 'already extended'

# The sets above are opaque colours standing side by side. The drain band is
# a different problem: a translucent hatch laid OVER something, where the
# thing underneath changes (the health bar turns bright red below a third).
# It needs its own check, because the first version of that band passed every
# instinct I had and collapsed to dE 3.8 under tritanopia.
block = '''
# ---------------------------------------------------------------------------
# Translucent things laid over other things.
#
# A hatch over a bar is not a colour standing next to a colour: it is a
# composite, and what it sits on changes (the health bar turns bright red
# below a third). The first drain band was pale hatching, which differs from
# red almost only in hue -- it measured dE 3.8 under tritanopia against the
# low-health bar, invisible exactly when the drain matters most. Hatching
# dark makes it a luminance difference, which no dichromacy removes.
OVERLAYS = {
    'drain band on the health bar': {
        'under': {'healthy bar': '#d9534f', 'low-health bar': '#ff2f28'},
        'layers': {
            'the band': ('#080a0e', 0.62),
            'the band when something made it worse': ('#783e0a', 0.62),
        },
        # the band has to be visible against the bar, and its two states have
        # to be tellable apart from each other
        'against': 'under+each other',
    },
}


def composite(hexcol, alpha, base_hex):
    fg, bg = hex_rgb(hexcol), hex_rgb(base_hex)
    return tuple(f * alpha + b * (1 - alpha) for f, b in zip(fg, bg))


def sim_rgb(rgb, kind):
    """simulate() takes a hex string; composites are already rgb triples"""
    return simulate('#%02x%02x%02x' % tuple(int(round(max(0, min(255, c)))) for c in rgb), kind)


print('Translucent overlays, composited onto what they sit on (CIE76 dE):\\n')
for name, spec in OVERLAYS.items():
    print(name)
    for kind in ('normal', 'deuteranopia', 'protanopia', 'tritanopia'):
        worst = None
        for base_name, base in spec['under'].items():
            comps = {k: composite(c, a, base) for k, (c, a) in spec['layers'].items()}
            shown = {k: sim_rgb(v, kind) for k, v in comps.items()}
            bar = sim_rgb(hex_rgb(base), kind)
            for k, v in shown.items():
                d = dE(v, bar)
                if worst is None or d < worst[0]:
                    worst = (d, k + ' vs ' + base_name)
            for a, b in itertools.combinations(shown, 2):
                d = dE(shown[a], shown[b])
                if d < worst[0]:
                    worst = (d, 'its two states, on the ' + base_name)
        flag = '   <-- too close' if worst[0] < 12 else ''
        print('   %-13s worst %-44s dE %5.1f%s' % (kind, worst[1], worst[0], flag))
        if worst[0] < 12:
            problems.append((name, kind, worst[1], 'the bar', round(worst[0], 1)))
    print()

'''

s = s.replace(anchor, block.lstrip('\n') + anchor)

# the overlay section runs first and appends to `problems`, so that list has
# to exist before it rather than after
s = s.replace("print('Translucent overlays", "problems = []\nprint('Translucent overlays", 1)
s = s.replace("print('Closest pair in each set, per kind of vision (CIE76 dE):\\n')\nproblems = []\n",
              "print('Closest pair in each set, per kind of vision (CIE76 dE):\\n')\n")

io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('colour-vision tool now checks composited overlays too')
