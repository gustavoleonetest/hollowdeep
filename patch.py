"""Apply exact-anchor patches to part_logic.js / part_head.html.

Each edit is (file, old, new). Every `old` must appear exactly once or the run
aborts without writing anything, so a bad anchor can never half-apply.
"""
import io
import sys

EDITS = []


def edit(path, old, new, count=1):
    EDITS.append((path, old, new, count))


def run():
    bufs = {}
    for path, old, new, count in EDITS:
        if path not in bufs:
            bufs[path] = io.open(path, encoding='utf-8').read()
        s = bufs[path]
        got = s.count(old)
        if got != count:
            print('FAIL %s: expected %d occurrence(s), found %d for:\n---\n%s\n---'
                  % (path, count, got, old[:400]))
            sys.exit(1)
        bufs[path] = s.replace(old, new)
    for path, s in bufs.items():
        io.open(path, 'w', encoding='utf-8', newline='').write(s)
        print('wrote %s (%d bytes)' % (path, len(s)))
    print('applied %d edit(s)' % len(EDITS))
