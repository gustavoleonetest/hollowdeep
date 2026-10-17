import io

p = 'behave2_drive.js'
s = io.open(p, encoding='utf-8').read()
anchor = "const fails = results.filter(r => r[0] === 'FAIL');"
assert s.count(anchor) == 1, 'anchor not unique'
assert 'a browser that will not let you save' not in s, 'already inserted'

block = r"""/* ---------------- a browser that will not let you save ---------------- */
{
  /* Private browsing in Safari throws on setItem. Some setups throw on even
     touching window.localStorage. An artifact gets opened by strangers on
     whatever browser they have, so the game has to come up either way --
     and, since it cannot keep anything, it has to say so rather than let
     someone earn a Barrow full of echoes that quietly evaporates. */
  const real = globalThis.localStorage;
  const mem = () => { const m = new Map(); return {
    getItem: k => (m.has(String(k)) ? m.get(String(k)) : null),
    setItem: (k, v) => { m.set(String(k), String(v)); },
    removeItem: k => { m.delete(String(k)); }, clear: () => m.clear() }; };

  const hostile = {
    'one that throws on every call': {
      getItem() { throw new Error('denied'); },
      setItem() { throw new Error('denied'); },
      removeItem() { throw new Error('denied'); },
    },
    'one that reads but refuses to write': (() => { const s = mem(); return {
      getItem: s.getItem, removeItem: s.removeItem,
      setItem() { throw new Error('quota'); } }; })(),
    'one that is not there at all': undefined,
    'one that is there but is not a store': {},
  };

  const broke = [];
  for (const [name, fake] of Object.entries(hostile)) {
    try {
      globalThis.localStorage = fake;
      /* everything the game does with storage, in the order boot does it */
      loadMeta();
      saveMeta();
      clearRun();
      startGame(['thistle']);
      saveRun();
      loadRun();
      G.offer = null; G.offerQ.length = 0; G.state = 'play';
      nextLevel();
      for (let i = 0; i < 120; i++) update(1 / 60);
      teach('crypt');
      die();
    } catch (e) {
      broke.push(name + ': ' + (e && e.message));
    } finally {
      globalThis.localStorage = real;
    }
  }
  ok('the game comes up on a browser that denies it storage', broke.length === 0,
     broke.join(' | ') || Object.keys(hostile).length + ' kinds of refusal survived');

  /* and it must notice, rather than pretend everything is fine */
  {
    const seen = {};
    for (const [name, fake] of Object.entries(hostile)) {
      globalThis.localStorage = fake;
      seen[name] = storageWorks(true);
      globalThis.localStorage = real;
    }
    const fooled = Object.keys(seen).filter(k => seen[k] !== false);
    ok('and knows it cannot save', fooled.length === 0,
       fooled.join(', ') || 'all four refusals detected');
    ok('while a working store is not wrongly condemned', storageWorks(true) === true);
  }

  /* the notice is only for the menu, and only when there is something to say */
  {
    globalThis.localStorage = hostile['one that throws on every call'];
    storageWorks(true); showMenu();
    const shownWhenBroken = !$('noSave').hidden;
    globalThis.localStorage = real;
    storageWorks(true); showMenu();
    const shownWhenFine = !$('noSave').hidden;
    ok('the warning shows when nothing can be kept', shownWhenBroken);
    ok('and stays out of the way when it can', !shownWhenFine);
  }

  /* a run started on such a browser still plays to the end */
  {
    globalThis.localStorage = hostile['one that reads but refuses to write'];
    storageWorks(true);
    let err = null;
    try {
      startGame(['ember']); G.offer = null; G.offerQ.length = 0; G.state = 'play';
      for (let d = 0; d < 3; d++) { G.offer = null; G.offerQ.length = 0; nextLevel(); }
      for (let i = 0; i < 600; i++) update(1 / 60);
      die();
    } catch (e) { err = e; }
    globalThis.localStorage = real; storageWorks(true);
    ok('and a whole run plays out on one, start to finish', err === null,
       err ? String(err.message) : 'three floors and a death');
  }
}

"""

io.open(p, 'w', encoding='utf-8', newline='').write(s.replace(anchor, block + anchor))
print('storage tests inserted')
