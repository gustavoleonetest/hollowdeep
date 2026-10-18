import io

p = 'smoke_stubs.js'
s = io.open(p, encoding='utf-8').read()

# getImageData handed back a correctly-shaped array of zeros whatever had
# been drawn. Nothing calls it today, but the next person to reach for a
# pixel assertion would get a plausible answer that means nothing -- the
# same shape of trap as the no-op classList and the string textContent.
# Refusing is the honest answer: this stub does not rasterise, so pixels
# have to be measured in a browser.
old = """    getImageData: (x, y, w, h) => ({ width: w, height: h, data: new Uint8ClampedArray(w * h * 4) }),"""
new = """    getImageData() {
      throw new Error('the test stub does not rasterise: it would hand back ' +
        'zeros whatever was drawn, so a pixel check here would pass on nothing. ' +
        'Measure pixels in a browser instead.');
    },"""
assert s.count(old) == 1, 'getImageData anchor not unique'
s = s.replace(old, new)

# querySelector cannot do the job either, and should say which job.
old2 = """    querySelector: () => el('q'), querySelectorAll: () => [],"""
new2 = """    /* A stand-in, not a match. This stub builds a tree from createElement and
       appendChild, but the UI also fills rows with `innerHTML = '<span
       class="nm">...'`, which is a string here and never becomes children.
       So a real matcher would return null and renderShop would throw on it.
       The stand-in keeps that code running, and is marked so that nothing
       mistakes writing into it for writing into the page. */
    querySelector: () => { const q = el('q'); q.__standIn = true; return q; },
    querySelectorAll: () => [],"""
assert s.count(old2) == 1, 'querySelector anchor not unique'
s = s.replace(old2, new2)

# the document-level pair, same story
old3 = """  querySelectorAll: () => [],
  querySelector: () => el('q'),"""
new3 = """  querySelectorAll: () => [],
  querySelector: () => { const q = el('q'); q.__standIn = true; return q; },"""
assert s.count(old3) == 1, 'document querySelector anchor not unique'
s = s.replace(old3, new3)

io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('stub now refuses what it cannot do')
