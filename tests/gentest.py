"""Pull the generator out of the patched logic and exercise it in node."""
import io
import subprocess

s = io.open('part_logic.js', encoding='utf-8').read()

start = s.index('const ROOM_KINDS =')
end = s.index('function genLevel()')
gen = s[start:end]
assert 'function makeMap' in gen

harness = r"""
const T = 32, MW = 52, MH = 38, TAU = Math.PI * 2;
const DIRS = [[1, 0], [-1, 0], [0, 1], [0, -1]];
const rnd = (a, b) => a + Math.random() * (b - a);
const rint = (a, b) => Math.floor(rnd(a, b + 1));
const clamp = (v, a, b) => Math.max(a, Math.min(b, v));
const G = { level: 1 };

/*__GEN__*/

let fails = 0, attemptsTotal = 0, roomCounts = [], kinds = {}, runs = 0;
for (let lvl = 1; lvl <= 18; lvl++) {
  G.level = lvl;
  for (let trial = 0; trial < 120; trial++) {
    let res = null, a = 0;
    for (; a < 300 && !res; a++) res = makeMap();
    attemptsTotal += a; runs++;
    if (!res) { fails++; continue; }
    const { m, rooms, door } = res;
    const last = rooms[rooms.length - 1];
    if (!door) throw new Error('no door at level ' + lvl);
    if (rooms.length < 6) throw new Error('too few rooms: ' + rooms.length);
    roomCounts.push(rooms.length);
    for (const r of rooms) {
      kinds[r.kind] = (kinds[r.kind] || 0) + 1;
      if (m[r.cy * MW + r.cx] !== 0) throw new Error('room centre is not floor, kind=' + r.kind);
    }
    // the door tile must be the only way into the stairs room
    const flood = pass => {
      const s0 = rooms[0].cy * MW + rooms[0].cx, seen = new Set([s0]), q = [s0];
      for (let h = 0; h < q.length; h++) {
        const c = q[h], cx = c % MW, cy = (c / MW) | 0;
        for (const [dx, dy] of DIRS) {
          const x = cx + dx, y = cy + dy; if (x < 0 || y < 0 || x >= MW || y >= MH) continue;
          const i = y * MW + x, t = m[i]; if (seen.has(i) || t === 1 || (t === 2 && !pass)) continue;
          seen.add(i); q.push(i);
        }
      }
      return seen;
    };
    const sealed = flood(false), open = flood(true);
    const id = r => r.cy * MW + r.cx;
    if (sealed.has(id(last))) throw new Error('stairs room reachable without the key');
    if (!open.has(id(last))) throw new Error('stairs room unreachable even with the key');
    for (let i = 0; i < rooms.length - 1; i++)
      if (!sealed.has(id(rooms[i]))) throw new Error('room ' + i + ' (' + rooms[i].kind + ') is walled off');
    // every floor tile in the open flood should be one connected blob
    let floors = 0;
    for (let i = 0; i < m.length; i++) if (m[i] === 0) floors++;
    if (floors < 300) throw new Error('suspiciously small map: ' + floors + ' floor tiles');
  }
}
const avg = a => (a.reduce((s, v) => s + v, 0) / a.length).toFixed(1);
console.log('runs', runs, 'failed', fails, 'avg attempts/level', (attemptsTotal / runs).toFixed(2));
console.log('avg rooms', avg(roomCounts), 'min', Math.min(...roomCounts), 'max', Math.max(...roomCounts));
console.log('room kinds', JSON.stringify(kinds));
console.log(fails === 0 ? 'ALL INVARIANTS HELD' : 'SOME LEVELS FAILED TO GENERATE');
"""

import os
out = os.path.join('build', 'gentest.js')
os.makedirs('build', exist_ok=True)
io.open(out, 'w', encoding='utf-8', newline='').write(harness.replace('/*__GEN__*/', gen))
r = subprocess.run(['node', out], capture_output=True, text=True)
print(r.stdout or '', r.stderr or '')
