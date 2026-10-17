"""How far apart are the game's colour-coded sets, to eyes that see differently?

Viénot/Brettel-style LMS simulation for the three dichromacies, then CIE76
distance in Lab. Rough rule of thumb: dE under about 12 is hard to tell apart
at a glance in a dim, moving scene; under 6 is effectively the same colour.
"""
import itertools
import math

SETS = {
    'loot rarity': {
        'magic': '#6fa8ff', 'rare': '#ffd24a', 'fabled': '#e08a3c', 'cursed': '#e0556b',
    },
    'altars': {
        'blessing': '#f0a23c', 'pact': '#e0556b', 'mystery': '#b98cff',
    },
    'delvers': {
        'bulwark': '#e7b04a', 'ember': '#ff6a4d', 'sable': '#7fd1c7', 'thistle': '#9bd16a',
    },
    'omens': {
        'horde': '#e0553a', 'famine': '#c98b5a', 'dark': '#6f7fa8',
        'still': '#7fd1c7', 'gilded': '#f0a23c', 'warren': '#9a6bd6',
    },
}


def srgb_to_lin(c):
    c /= 255.0
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def lin_to_srgb(c):
    c = max(0.0, min(1.0, c))
    return 12.92 * c if c <= 0.0031308 else 1.055 * (c ** (1 / 2.4)) - 0.055


def hex_rgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


RGB2LMS = ((0.31399022, 0.63951294, 0.04649755),
           (0.15537241, 0.75789446, 0.08670142),
           (0.01775239, 0.10944209, 0.87256922))
LMS2RGB = ((5.47221206, -4.6419601, 0.16963708),
           (-1.1252419, 2.29317094, -0.1678952),
           (0.02980165, -0.19318073, 1.16364789))

SIM = {
    'deuteranopia': ((1.0, 0.0, 0.0), (0.9513092, 0.0, 0.04866992), (0.0, 0.0, 1.0)),
    'protanopia': ((0.0, 1.05118294, -0.05116099), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0)),
    'tritanopia': ((1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (-0.86744736, 1.86727089, 0.0)),
}


def mul(m, v):
    return tuple(sum(m[i][j] * v[j] for j in range(3)) for i in range(3))


def simulate(hexcol, kind):
    lin = [srgb_to_lin(c) for c in hex_rgb(hexcol)]
    if kind == 'normal':
        out = lin
    else:
        lms = mul(RGB2LMS, lin)
        out = mul(LMS2RGB, mul(SIM[kind], lms))
    return tuple(lin_to_srgb(c) * 255 for c in out)


def lab(rgb):
    x, y, z = 0.0, 0.0, 0.0
    lin = [srgb_to_lin(max(0.0, min(255.0, c))) for c in rgb]
    M = ((0.4124, 0.3576, 0.1805), (0.2126, 0.7152, 0.0722), (0.0193, 0.1192, 0.9505))
    x, y, z = mul(M, lin)
    wx, wy, wz = 0.95047, 1.0, 1.08883
    def f(t):
        return t ** (1 / 3) if t > 0.008856 else 7.787 * t + 16 / 116
    fx, fy, fz = f(x / wx), f(y / wy), f(z / wz)
    return (116 * fy - 16, 500 * (fx - fy), 200 * (fy - fz))


def dE(a, b):
    return math.sqrt(sum((p - q) ** 2 for p, q in zip(lab(a), lab(b))))


print('Closest pair in each set, per kind of vision (CIE76 dE):\n')
problems = []
for name, cols in SETS.items():
    print(name)
    for kind in ('normal', 'deuteranopia', 'protanopia', 'tritanopia'):
        sim = {k: simulate(v, kind) for k, v in cols.items()}
        pairs = sorted(((dE(sim[a], sim[b]), a, b) for a, b in itertools.combinations(cols, 2)))
        d, a, b = pairs[0]
        flag = '   <-- too close' if d < 12 else ''
        print('   %-13s worst pair %-10s %-10s dE %5.1f%s' % (kind, a, b, d, flag))
        if d < 12:
            problems.append((name, kind, a, b, round(d, 1)))
    print()

print('SETS THAT COLLAPSE:' if problems else 'every set stays distinguishable')
for p in problems:
    print('   %s under %s: %s vs %s (dE %.1f)' % p)
