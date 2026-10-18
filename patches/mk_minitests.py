import io

p = 'behave2_drive.js'
s = io.open(p, encoding='utf-8').read()
anchor = "const fails = results.filter(r => r[0] === 'FAIL');"
assert s.count(anchor) == 1, 'anchor not unique'
assert 'what the map remembers for you' not in s, 'already inserted'

block = r"""/* ---------------- what the map remembers for you ---------------- */
{
  /* The stub cannot rasterise and says so, so the way to find out what the
     map drew is to listen to it drawing. Recording the calls also settles
     the question that matters for telling the marks apart: a ring, a cross,
     a diamond, a triangle and a bar are different SHAPES, so the map does
     not lean on colour to say which is which. */
  const listen = fn => {
    const shapes = [];
    const real = {};
    for (const k of ['beginPath', 'moveTo', 'lineTo', 'arc', 'closePath', 'fill', 'stroke', 'fillRect']) real[k] = mctx[k];
    let pending = null;
    mctx.beginPath = () => { pending = { pts: [], arc: false }; };
    mctx.moveTo = (x, y) => { if (pending) pending.pts.push([x, y]); };
    mctx.lineTo = (x, y) => { if (pending) pending.pts.push([x, y]); };
    mctx.arc = (x, y, r) => { if (pending) { pending.arc = true; pending.at = [x, y]; } };
    mctx.closePath = () => {};
    mctx.fill = () => {
      if (pending) shapes.push({ form: pending.arc ? 'disc' : 'poly', pts: pending.pts.length,
                                 at: pending.pts[0] || pending.at, col: mctx.fillStyle });
      pending = null;
    };
    mctx.stroke = () => {
      if (pending) shapes.push({ form: pending.arc ? 'ring' : 'lines', pts: pending.pts.length, col: mctx.strokeStyle });
      pending = null;
    };
    mctx.fillRect = (x, y, w, h) => shapes.push({ form: 'rect', x, y, w, h, col: mctx.fillStyle });
    try { fn(); } finally { for (const k in real) mctx[k] = real[k]; }
    return shapes;
  };
  /* the map floor is drawn as 3x3 tiles and the delver as a 4x4 square, so
     a 6x3 bar is unambiguous */
  const bars = sh => sh.filter(s => s.form === 'rect' && s.w === 6 && s.h === 3);
  const tris = sh => sh.filter(s => s.form === 'poly' && s.pts === 3);
  const diamonds = sh => sh.filter(s => s.form === 'poly' && s.pts === 4);

  startGame(['sable']); G.level = 4; genLevel();
  G.offer = null; G.offerQ.length = 0; G.state = 'play';
  const P = G.players[0];
  const seeAll = () => G.seen.fill(1);
  const seeNone = () => G.seen.fill(0);

  /* a key and a loaf, both on ground the delver has walked */
  G.items.length = 0;
  G.items.push({ kind: 'key', x: P.x + 60, y: P.y, t: 0 });
  G.items.push({ kind: 'food', x: P.x, y: P.y + 60, t: 0 });
  seeAll();
  {
    const sh = listen(drawMini);
    ok('the key the floor is locked behind is on the map', tris(sh).length === 1,
       tris(sh).length + ' triangles');
    ok('and so is the food', bars(sh).length === 1, bars(sh).length + ' bars');
  }

  /* nothing unseen is given away */
  {
    seeNone();
    const sh = listen(drawMini);
    ok('but nothing on ground you have not walked', tris(sh).length === 0 && bars(sh).length === 0,
       tris(sh).length + ' triangles, ' + bars(sh).length + ' bars');
    seeAll();
  }

  /* and what has been taken is no longer there */
  {
    G.items.length = 0;
    const sh = listen(drawMini);
    ok('a key already taken leaves no mark', tris(sh).length === 0, String(tris(sh).length));
    ok('nor does food already eaten', bars(sh).length === 0, String(bars(sh).length));
  }

  /* the five marks have five different shapes, so none of them needs its
     colour read to be told from the others */
  {
    G.items.length = 0;
    G.items.push({ kind: 'key', x: P.x + 40, y: P.y, t: 0 });
    G.items.push({ kind: 'food', x: P.x, y: P.y + 40, t: 0 });
    G.items.push({ kind: 'chest', x: P.x - 40, y: P.y, t: 0, big: false });
    G.nests.length = 0;
    G.nests.push({ x: P.x, y: P.y - 40, hp: 10, max: 10, r: 12, t: 0, flash: 0 });
    seeAll();
    const sh = listen(drawMini);
    const forms = {
      exit: sh.filter(s => s.form === 'ring').length,
      crypt: sh.filter(s => s.form === 'lines' && s.pts === 4).length,
      chest: diamonds(sh).length,
      key: tris(sh).length,
      food: bars(sh).length,
    };
    ok('every kind of thing on the map has its own shape',
       forms.exit >= 1 && forms.crypt >= 1 && forms.chest === 1 && forms.key === 1 && forms.food === 1,
       JSON.stringify(forms));
    const counts = [forms.chest, forms.key, forms.food];
    ok('and one of each is drawn once, not twice', counts.every(n => n === 1), counts.join(','));
  }

  /* several loaves all get marked: this is a memory, not a hint */
  {
    G.items.length = 0;
    for (let i = 0; i < 4; i++) G.items.push({ kind: 'food', x: P.x + i * 30, y: P.y, t: 0 });
    seeAll();
    ok('four loaves make four marks', bars(listen(drawMini)).length === 4,
       String(bars(listen(drawMini)).length));
    G.items.length = 0;
  }

  /* and it survives being asked to draw a floor it knows nothing about */
  {
    G.items.length = 0; G.nests.length = 0; seeNone();
    let err = null;
    try { listen(drawMini); } catch (e) { err = e; }
    ok('an unexplored floor draws without complaint', err === null, err ? String(err.message) : 'drew');
  }
}

"""

io.open(p, 'w', encoding='utf-8', newline='').write(s.replace(anchor, block + anchor))
print('minimap tests inserted')
