import io

p = 'smoke_stubs.js'
s = io.open(p, encoding='utf-8').read()

old = """    classList: { add() {}, remove() {}, toggle() {}, contains: () => false },"""
new = """    /* a real one: a no-op classList makes every test that asks about a
       class pass whatever the code does, which is worse than no test */
    classList: (() => {
      const set = new Set();
      return {
        add: (...c) => c.forEach(x => set.add(x)),
        remove: (...c) => c.forEach(x => set.delete(x)),
        toggle: (c, on) => { const want = on === undefined ? !set.has(c) : !!on; if (want) set.add(c); else set.delete(c); return want; },
        contains: c => set.has(c),
        get length() { return set.size; },
        toString: () => [...set].join(' '),
      };
    })(),"""
assert s.count(old) == 1, 'classList anchor not unique'
io.open(p, 'w', encoding='utf-8', newline='').write(s.replace(old, new))
print('stub classList is now real')
