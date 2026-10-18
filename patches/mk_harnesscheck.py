import io

p = 'behave2_drive.js'
s = io.open(p, encoding='utf-8').read()
anchor = "const fails = results.filter(r => r[0] === 'FAIL');"
assert s.count(anchor) == 1, 'anchor not unique'
assert 'can the harness tell doing from not-doing' not in s, 'already inserted'

block = r"""/* ---------------- can the harness tell doing from not-doing ----------------
   Three times running, the thing that nearly voided a check was this file's
   own scaffolding rather than the game: a classList whose toggle did
   nothing and whose contains always said no, a textContent that was a plain
   string while the UI builds its rows out of child spans, and a chain
   report read at a moment when the number had already been reset. Each one
   made a check pass no matter what the code did, which is worse than having
   no check, because it reads as evidence.

   So: for every facility the suite leans on, prove it can distinguish the
   code having acted from the code having done nothing. A stub that cannot
   fail cannot test. */
{
  const node = () => document.createElement('div');

  /* classes */
  {
    const e = node();
    const blind = e.classList.contains('x');
    e.classList.add('x');
    const sees = e.classList.contains('x');
    e.classList.toggle('x', false);
    ok('[harness] a class that is set can be seen, and one that is not cannot',
       !blind && sees && !e.classList.contains('x'));
  }

  /* text, composed from children as a real node does */
  {
    const row = node(), a = node(), b = node();
    a.textContent = 'left'; b.textContent = 'right';
    row.appendChild(a); row.appendChild(b);
    ok('[harness] text reads through to the children', row.textContent === 'leftright', row.textContent);
    const stale = row.textContent;
    b.textContent = 'changed';
    ok('[harness] and follows them when they change', row.textContent !== stale, row.textContent);
    row.textContent = 'flat';
    ok('[harness] setting it replaces them, as a browser does',
       row.textContent === 'flat' && row.children.length === 0, row.textContent + ', ' + row.children.length);
  }

  /* emptying a list before refilling it */
  {
    const wrap = node();
    wrap.appendChild(node()); wrap.appendChild(node());
    const had = wrap.children.length;
    wrap.innerHTML = '';
    ok('[harness] clearing by innerHTML really empties it',
       had === 2 && wrap.children.length === 0, had + ' -> ' + wrap.children.length);
  }

  /* hidden, which every overlay check in here turns on */
  {
    const e = node(); e.hidden = true;
    const on = e.hidden; e.hidden = false;
    ok('[harness] hidden is a property that holds what it is given', on === true && e.hidden === false);
  }

  /* storage, which the saved-run checks live on */
  {
    const k = 'hollowdeep-harness-probe';
    localStorage.setItem(k, 'kept');
    const back = localStorage.getItem(k);
    localStorage.removeItem(k);
    ok('[harness] storage keeps what it is given and gives it back',
       back === 'kept' && localStorage.getItem(k) === null, String(back));
  }

  /* pixels: the stub does not rasterise, and must say so rather than hand
     back a plausible array of zeros */
  {
    let refused = false, message = '';
    try { ctx.getImageData(0, 0, 4, 4); } catch (e) { refused = true; message = String(e.message || ''); }
    ok('[harness] it refuses to pretend it can read pixels', refused, message.slice(0, 60) || 'it answered');
    ok('[harness] and says where to measure them instead', /browser/i.test(message), message.slice(0, 80));
  }

  /* selectors: it cannot match into content built from an innerHTML string,
     so what comes back is a marked stand-in and nothing may be asserted
     through it */
  {
    const row = node();
    row.innerHTML = '<span class="nm"></span>';
    const found = row.querySelector('.nm');
    ok('[harness] a selector result is a marked stand-in, not a match',
       !!found && found.__standIn === true, found ? 'marked ' + !!found.__standIn : 'null');
    ok('[harness] so writing through one reaches nothing on the row',
       (found.textContent = 'written', row.children.length === 0),
       'row children ' + row.children.length);
  }
}

"""

io.open(p, 'w', encoding='utf-8', newline='').write(s.replace(anchor, block + anchor))
print('harness self-check inserted')
