# Hollowdeep

A single-file HTML5 canvas dungeon crawler, published as a claude.ai artifact:
<https://claude.ai/artifact/3Wc6rtgjWbNjm8Lh8tsyJT> (currently version 26).

Descend through a procedurally generated dungeon. Your health drains the whole
way down, so food is the clock. Smash the crypts, take the key, unlock the
door, find the stairs. Something waits at the bottom.

## Working on it

Everything runs from this directory.

```bash
python make.py build   # build/hollowdeep-publish.html is what gets published
python make.py test    # syntax, 2160 map generations, smoke run, 276 checks
python make.py sim     # headless balance sweep (several minutes)
python make.py all     # build then test
```

`build/` is generated and ignored. `python make.py build` reproduces the
published artifact byte for byte.

## The three sources

| file | what it is |
| --- | --- |
| `part_head.html` | markup, CSS, HUD and every overlay |
| `part_data.txt` | base64 WebP sprite atlases (Kenney / Quaternius, CC0) — never hand-edited |
| `part_logic.js` | all the game code |

The build is just those three concatenated, then the document skeleton
stripped: the artifact platform wraps the payload in its own
`<!doctype>/<head>/<body>`, so publishing a payload that still has one
produces a broken page. `make.py build` asserts the skeleton is gone and
refuses to produce a payload that would break — do not publish around those
assertions.

## Editing

Changes go through `patch.py`, which applies exact-anchor edits and is atomic:
if any anchor does not match exactly once, nothing is written at all. That
means a failed patch never leaves the file half-edited.

```python
from patch import edit, run
edit('part_logic.js', "old text that appears exactly once", "new text")
run()
```

Two things that have bitten repeatedly:

- **Write patch scripts to a file and run them**, rather than piping a heredoc
  through bash. This shell collapses `\\` in heredocs, so `'\\u00b7'` silently
  becomes a literal `·` and `'\\n'` becomes a real newline inside a JS string
  literal. Build escapes with `chr(92)` when it matters.
- `·` (one backslash) is for HTML text; `\\u00b7` is only for inside a JS
  string literal. The build asserts that no escape leaks into the markup.

`patches/` holds the one-shot scripts for every change already applied. They
cannot be re-run — their anchors are gone — but they record what each change
did and why.

## Tests

| suite | covers |
| --- | --- |
| `tests/gentest.py` | 2160 map generations: the stairs room is sealed behind exactly one door, every other room is reachable without it, nothing spawns in a wall |
| `tests/smoke_drive.js` | every class across 18 depths with sprites on and off, driving every boss attack, ~26k frames, asserting no runtime errors |
| `tests/behave_drive.js` | 43 checks: generation invariants, boss phases and attacks |
| `tests/behave2_drive.js` | 233 checks: loot and affixes, boons, altars and pacts, omens, the six bosses, the finale |
| `tests/sim_drive.js` | headless balance sweep — plays whole runs with a scripted delver and reports depth reached, what kills you, per-depth attrition and build variety |

A few checks are statistical by nature. Where that caused flakiness the test
was rewritten to assert the thing itself rather than wait on a dice roll — for
example the bosses walk their attack list in order and only swing with line of
sight, so the suite drives each attack directly instead of watching a fight and
hoping. Keep that habit: a test that fails one run in forty is worse than no
test, because it trains you to ignore it.

Two gotchas when writing tests against the engine:

- `blockedAt` only sees wall tiles, not props. A barrel will stop a charge, so
  arena-style tests clear `G.props` first.
- Timers (`G.timers`) tick in `updateFx`, projectiles move in `updateShots`.
  A test that runs one and then the other does not advance time consistently —
  anything on a delay needs both ticked together each frame.

## How a run is shaped

- **Four delvers** — Bulwark, Ember, Sable, Thistle — with different reach,
  speed and attack shape.
- **Boons**: every other level offers one of four per class that change how the
  attack works rather than how big it is (Cyclone strikes behind you, Seeking
  Flame curves, Fan of Knives triples the throw).
- **Altars**: six pacts that cost something real, three blessings that cost
  nothing, and mystery fonts that do not say which. Colour tells you which kind
  — gold gives, crimson wants paying, violet will not say.
- **Omens**: roughly a third of non-boss depths from 3 on carry a condition
  that changes what the floor asks (The Horde, Famine, Pitch Dark, Still Air,
  The Gilded Seam, The Warren).
- **Six zones, six bosses**, one per zone, with distinct attack pools.
- **The Hollow Heart at depth 21** ends the run in victory. You may climb out
  with it or keep going deeper.
- **The Barrow** banks echoes between runs for permanent perks.

## Balance

Numbers come from `make.py sim`, not from guessing. It found the two worst
defects so far: damage upgrades were compounding to 230,824,704x base, and
Hunter's Mark was raising the damage *number* without raising the damage. Any
tuning change should be measured the same way, and the simulator understates
melee — its scripted delver stalls far more often with the Bulwark than with
the ranged classes, so its Bulwark figures measure the driver, not the class.
