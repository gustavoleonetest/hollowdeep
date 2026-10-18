import io

p = 'smoke_stubs.js'
s = io.open(p, encoding='utf-8').read()

old = """    children: [], innerHTML: '', textContent: '', value: '', title: '',"""
new = """    children: [], value: '', title: '', _text: '', _html: '',"""
assert s.count(old) == 1, 'element literal anchor not unique'
s = s.replace(old, new)

old2 = """    getContext: () => ctx2d(),
  };
  return e;
}"""
new2 = """    getContext: () => ctx2d(),
  };
  /* A real node's textContent is everything underneath it, and the UI here
     builds its rows out of child spans -- so a plain string property made
     every test that read a built-up row see '' and pass regardless. Setting
     it replaces the children, as it does in a browser. */
  Object.defineProperty(e, 'textContent', {
    enumerable: true, configurable: true,
    get() { return this._text + this.children.map(c => c.textContent).join(''); },
    set(v) { this._text = v == null ? '' : String(v); this.children.length = 0; },
  });
  /* and `innerHTML = ''` is how this codebase empties a list before
     refilling it: leaving the children in place made rows accumulate */
  Object.defineProperty(e, 'innerHTML', {
    enumerable: true, configurable: true,
    get() { return this._html; },
    set(v) {
      this._html = v == null ? '' : String(v);
      if (this._html === '') { this.children.length = 0; this._text = ''; }
    },
  });
  return e;
}"""
assert s.count(old2) == 1, 'el() tail anchor not unique'
s = s.replace(old2, new2)

io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('stub text nodes now behave like a DOM')
