from patch import edit, run

L = 'part_logic.js'
H = 'part_head.html'

edit(L, """bombs: 0, bolts: [], voice: null, flash: 0, offerQ: [], drops: 0 };""",
     """bombs: 0, bolts: [], voice: null, flash: 0, offerQ: [], drops: 0, wares: [] };""")

# --- the peddler lays out three pieces each visit -------------------------
edit(L, """function enterShop() {
  G.state = 'clear'; G.clearT = 0; G.clearE = 0; sfx('stairs');""",
     """const RAR_PRICE = { magic: 1, rare: 1.9, fabled: 3.4, cursed: .62 };
function warePrice(it) { return Math.round((70 + it.ilvl * 20) * (RAR_PRICE[it.rar] || 1)); }
function rollWares() {
  G.wares = [];
  const slots = ['weapon', 'armour', 'trinket'];
  for (let i = 0; i < 3; i++) {
    const it = rollItem(slots[i], rollRarity(G.level * .6));
    it.price = warePrice(it); it.sold = false;
    G.wares.push(it);
  }
}
function buyWare(P, i) {
  const it = G.wares[i];
  if (!it || it.sold || P.down || G.state !== 'shop' || G.gold < it.price) return false;
  G.gold -= it.price; it.sold = true;
  equip(P, it);
  return true;
}
function enterShop() {
  G.state = 'clear'; G.clearT = 0; G.clearE = 0; sfx('stairs'); rollWares();""")

edit(L, """  G.bombs = 1; G.drops = 0; G.bolts = []; G.voice = null; G.flash = 0; G.offer = null; G.offerQ = [];""",
     """  G.bombs = 1; G.drops = 0; G.bolts = []; G.voice = null; G.flash = 0; G.offer = null; G.offerQ = []; G.wares = [];""")

# --- render them above the blessings --------------------------------------
edit(L, """  const wrap = $('shopRows'); wrap.innerHTML = '';
  for (const it of SHOP) {""",
     """  const ww = $('shopWares'); ww.innerHTML = '';
  for (let i = 0; i < G.wares.length; i++) {
    const it = G.wares[i];
    const row = document.createElement('div'); row.className = 'srow'; row.style.setProperty('--c', it.col);
    const info = document.createElement('div');
    const nm = document.createElement('span'); nm.className = 'nm'; nm.textContent = it.name; info.appendChild(nm);
    const tag = document.createElement('span'); tag.className = 'itemrar'; tag.style.color = it.col;
    tag.textContent = (it.rar === 'cursed' ? 'Cursed' : (RARITY[it.rar] || {}).name || it.rar) + ' \\u00b7 ' + it.slot; info.appendChild(tag);
    const bl = document.createElement('span'); bl.className = 'bl'; bl.textContent = itemLines(it).join(' \\u00b7 '); info.appendChild(bl);
    row.appendChild(info);
    const bw = document.createElement('div'); bw.className = 'sbuy';
    for (const P of G.players) {
      const b = document.createElement('button'); b.type = 'button'; b.className = 'btn buy';
      const cur = P.gear[it.slot];
      const can = !it.sold && !P.down && G.gold >= it.price;
      b.textContent = (G.co ? 'P' + (P.idx + 1) + ' \\u00b7 ' : 'Buy \\u00b7 ') + (it.sold ? 'Sold' : it.price + 'g');
      b.disabled = !can;
      if (cur && !it.sold) b.title = 'Replaces ' + cur.name;
      else if (!it.sold && G.gold < it.price) b.title = 'Not enough gold';
      b.addEventListener('click', () => { if (buyWare(P, i)) { sfx('gear'); renderShop(); } });
      bw.appendChild(b);
    }
    row.appendChild(bw); ww.appendChild(row);
  }
  const wrap = $('shopRows'); wrap.innerHTML = '';
  for (const it of SHOP) {""")

# --- markup and styling ---------------------------------------------------
edit(H, """      <div class="srows" id="shopRows"></div>""",
     """      <h3 class="shsec">Wares</h3>
      <div class="srows" id="shopWares"></div>
      <h3 class="shsec">Blessings</h3>
      <div class="srows" id="shopRows"></div>""")

edit(H, """.itemrar{font-size:10px; letter-spacing:.1em; text-transform:uppercase; opacity:.85}""",
     """.itemrar{font-size:10px; letter-spacing:.1em; text-transform:uppercase; opacity:.85}
.shsec{margin:4px 0 -4px; font:400 22px/1 var(--display); color:var(--dim); letter-spacing:.04em}""")

run()
