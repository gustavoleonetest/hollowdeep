import io

p = 'smoke_stubs.js'
s = io.open(p, encoding='utf-8').read()

# addEventListener threw every handler away, so a test could "click" a
# button and watch nothing happen whatever the button was wired to -- which
# is how a check that a card does NOT pick an upgrade passed without ever
# clicking anything. Same family as the no-op classList and the string
# textContent. Keep the handlers and let a test fire them.
old = """    addEventListener() {}, removeEventListener() {}, appendChild(c) { this.children.push(c); return c; },"""
new = """    _on: null,
    addEventListener(type, fn) {
      if (typeof fn !== 'function') return;
      (this._on || (this._on = {}))[type] = (this._on[type] || []).concat(fn);
    },
    removeEventListener(type, fn) {
      if (this._on && this._on[type]) this._on[type] = this._on[type].filter(f => f !== fn);
    },
    /* what a test uses to actually press the thing */
    dispatch(type, ev) {
      const fns = (this._on && this._on[type]) || [];
      for (const f of fns) f(ev || { type, preventDefault() {}, stopPropagation() {} });
      return fns.length;
    },
    appendChild(c) { this.children.push(c); return c; },"""
assert s.count(old) == 1, 'listener anchor not unique'
s = s.replace(old, new)

io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('stub keeps its handlers now')
