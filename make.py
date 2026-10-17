"""Build and test Hollowdeep.

Run from this directory:

    python make.py build     # hollowdeep.html + hollowdeep-publish.html
    python make.py test      # syntax, map generation, smoke, both behaviour suites
    python make.py sim       # headless balance sweep (slow: several minutes)
    python make.py all       # build + test

Everything under build/ is generated and is not committed. The sources are
part_head.html (markup and CSS), part_data.txt (base64 sprite atlases, never
hand-edited) and part_logic.js (all the game code).
"""
import io
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BUILD = os.path.join(HERE, 'build')
PARTS = ['part_head.html', 'part_data.txt', 'part_logic.js']
DRIVERS = [
    ('smoke', 'smoke_drive.js'),
    ('behave', 'behave_drive.js'),
    ('behave2', 'behave2_drive.js'),
    ('sim', 'sim_drive.js'),
]


def read(path):
    return io.open(os.path.join(HERE, path), encoding='utf-8').read()


def write_build(name, text):
    os.makedirs(BUILD, exist_ok=True)
    p = os.path.join(BUILD, name)
    io.open(p, 'w', encoding='utf-8', newline='').write(text)
    return p


def build():
    """Concatenate the parts, then strip the document skeleton for publishing.

    The artifact platform wraps the payload in its own doctype/head/body, so
    what gets published must have that skeleton removed. The assertions below
    are the contract: if any of them trips, do not publish the result.
    """
    full = ''.join(read(p) for p in PARTS)
    out = write_build('hollowdeep.html', full)

    marker = '</style></head><body>' + chr(10)
    tail = chr(10) * 2 + '</body></html>'
    body = full[full.index(marker) + len(marker):-len(tail)] + chr(10)
    assert body.startswith('<title>Hollowdeep</title>'), 'payload must start at the title'
    low = body.lower()
    assert '<!doctype' not in low and '<html' not in low and '<body' not in low, 'skeleton not stripped'
    assert body.count('<script src') == 0, 'no external scripts may be referenced'
    # a literal · in the markup means a JS escape leaked into HTML text
    assert body[:body.index('<script>')].count(chr(92) + 'u00') == 0, 'escaped char leaked into markup'
    pub = write_build('hollowdeep-publish.html', body)

    print('built %s (%.2f MB)' % (os.path.relpath(out, HERE), os.path.getsize(out) / 1048576))
    print('built %s (%.2f MB)  <- this is what gets published' % (os.path.relpath(pub, HERE), os.path.getsize(pub) / 1048576))
    return pub


def atlas_frames():
    """The real frame names, read from the sprite data.

    The stub used to carry a hand-typed copy of these and had drifted 24 frames
    behind, so anything newly drawn rendered nothing under test while passing.
    """
    import json
    import re
    d = read('part_data.txt')
    out = {}
    for var, atlas in (('SPR_META', 'props'), ('SPR_META2', 'props2')):
        m = re.search(var + r'\s*=\s*(\{.*?\});', d, re.S)
        out[atlas] = sorted(json.loads(m.group(1))[atlas]['frames'].keys())
    return out


def bundle():
    """Stub out the DOM, append the game, then a driver: one file node can run."""
    import json
    logic = read('part_logic.js')
    game = logic[:logic.rindex('</script>')]
    write_build('check.js', game)
    stubs = read(os.path.join('tests', 'smoke_stubs.js'))
    fr = atlas_frames()
    stubs = stubs.replace('__PROP_NAMES__', json.dumps(fr['props']))
    stubs = stubs.replace('__PROP2_NAMES__', json.dumps(fr['props2']))
    assert '__PROP' not in stubs, 'a frame-list placeholder was left unfilled'
    for name, driver in DRIVERS:
        write_build(name + '.js', stubs + chr(10) + game + chr(10) + read(os.path.join('tests', driver)))


def node(script, env=None, show=1):
    e = dict(os.environ)
    if env:
        e.update(env)
    r = subprocess.run(['node', os.path.join(BUILD, script)], capture_output=True, text=True, env=e, cwd=HERE)
    out = (r.stdout or '') + (r.stderr or '')
    lines = [l for l in out.strip().splitlines() if l.strip()]
    for l in lines[-show:]:
        print('   ' + l)
    return r.returncode, out


def test():
    bundle()
    ok = True

    print('syntax')
    r = subprocess.run(['node', '--check', os.path.join(BUILD, 'check.js')], capture_output=True, text=True)
    print('   ' + ('OK' if r.returncode == 0 else (r.stderr or '').strip()))
    ok &= r.returncode == 0

    print('map generation (2160 levels)')
    r = subprocess.run([sys.executable, os.path.join('tests', 'gentest.py')],
                       capture_output=True, text=True, cwd=HERE)
    out = (r.stdout or '') + (r.stderr or '')
    for l in [l for l in out.strip().splitlines() if l.strip()][-3:]:
        print('   ' + l)
    ok &= 'ALL INVARIANTS HELD' in out

    print('smoke (every class, every depth, every boss attack)')
    code, out = node('smoke.js')
    ok &= 'NO RUNTIME ERRORS' in out

    for name in ('behave', 'behave2'):
        print(name)
        code, out = node(name + '.js', show=1)
        ok &= 'FAILURES' not in out

    print('\n' + ('ALL GREEN' if ok else 'SOMETHING FAILED'))
    return 0 if ok else 1


def sim():
    bundle()
    print('balance sweep — this takes several minutes')
    env = {'SIM_N': os.environ.get('SIM_N', '6'), 'SIM_CAP': os.environ.get('SIM_CAP', '600')}
    code, out = node('sim.js', env=env, show=200)
    return code


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'all'
    if cmd == 'build':
        build(); sys.exit(0)
    if cmd == 'test':
        sys.exit(test())
    if cmd == 'sim':
        sys.exit(sim())
    if cmd == 'all':
        build(); sys.exit(test())
    print(__doc__)
    sys.exit(2)
