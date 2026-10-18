import io

p = 'behave2_drive.js'
s = io.open(p, encoding='utf-8').read()
anchor = "const fails = results.filter(r => r[0] === 'FAIL');"
assert s.count(anchor) == 1, 'anchor not unique'
assert 'the stall between floors' not in s, 'already inserted'

block = r"""/* ---------------- the stall between floors ---------------- */
{
  /* Ten upgrades with compounding prices, four caps and a five-state
     machine, and the only thing anyone had ever checked was that the stall
     turns up and does not throw while rendering. */
  const shopOpen = (level, gold) => {
    startGame(['sable']); G.level = level; genLevel();
    G.offer = null; G.offerQ.length = 0; G.wares = [];
    G.state = 'shop'; G.gold = gold;
    return G.players[0];
  };
  const item = id => SHOP.find(s => s.id === id);

  /* 1. the price compounds with each one you take, and with the depth */
  {
    const P = shopOpen(5, 99999), it = item('power');
    const first = shopPrice(P, it);
    shopBuy(P, 'power');
    const second = shopPrice(P, it);
    ok('a second Might costs more than the first', second > first, first + 'g -> ' + second + 'g');
    ok('and by exactly the stated growth', second === Math.round((it.base + it.per * 5) * it.grow),
       second + ' vs ' + Math.round((it.base + it.per * 5) * it.grow));
    const shallow = shopPrice(P, item('ward'));
    G.level = 15;
    ok('and everything costs more the deeper you are', shopPrice(P, item('ward')) > shallow,
       shallow + 'g at depth 5 -> ' + shopPrice(P, item('ward')) + 'g at 15');
  }

  /* 2. you pay what it says, and never go into debt */
  {
    const P = shopOpen(6, 400), it = item('swift');
    const price = shopPrice(P, it), before = G.gold;
    ok('buying deducts exactly the price shown', shopBuy(P, 'swift') && G.gold === before - price,
       before + ' - ' + price + ' = ' + G.gold);
    G.gold = 1;
    const broke = shopBuy(P, 'power');
    ok('and what you cannot afford you cannot buy', broke === false && G.gold === 1, 'gold ' + G.gold);
    ok('the stall calls that being poor', shopState(P, item('power')) === 'poor', shopState(P, item('power')));
  }

  /* 3. the caps hold */
  {
    const P = shopOpen(4, 9999999), it = item('dash');
    let bought = 0;
    while (shopBuy(P, 'dash')) if (++bought > 50) break;
    ok('a capped upgrade stops at its cap', bought === it.max, bought + ' of ' + it.max);
    ok('and says so rather than going quiet', shopState(P, it) === 'max', shopState(P, it));
  }

  /* 4. healing is not sold to someone who does not need it */
  {
    const P = shopOpen(5, 9999); P.hp = P.max;
    ok('no draught for a delver at full health', shopState(P, item('draught')) === 'full',
       shopState(P, item('draught')));
    P.hp = P.max * .4;
    ok('but one for a delver who is hurt', shopState(P, item('draught')) === 'ok',
       shopState(P, item('draught')));
    const before = P.hp;
    shopBuy(P, 'draught');
    ok('and it restores half of them', Math.abs(P.hp - Math.min(P.max, before + P.max * .5)) < 1e-9,
       before.toFixed(1) + ' -> ' + P.hp.toFixed(1));
  }

  /* 5. a downed delver buys nothing */
  {
    const P = shopOpen(5, 99999); P.down = true;
    const states = SHOP.map(it => shopState(P, it));
    ok('a fallen delver is sold nothing at all', states.every(s => s === 'down'),
       [...new Set(states)].join(','));
    ok('and cannot be made to buy', shopBuy(P, 'power') === false);
    P.down = false;
  }

  /* 6. two delvers, one purse */
  {
    startGame(['bulwark', 'ember']); G.level = 6; genLevel();
    G.offer = null; G.offerQ.length = 0; G.wares = []; G.state = 'shop'; G.gold = 100000;
    const [A, B] = G.players;
    shopBuy(A, 'power'); shopBuy(A, 'power');
    ok('what one delver buys does not raise the price for the other',
       shopPrice(B, item('power')) < shopPrice(A, item('power')),
       'A pays ' + shopPrice(A, item('power')) + ', B pays ' + shopPrice(B, item('power')));
    const purse = G.gold, cost = shopPrice(B, item('power'));
    shopBuy(B, 'power');
    ok('but they spend from the same purse', G.gold === purse - cost, purse + ' -> ' + G.gold);

    /* the elixir is the one thing worth buying at full health */
    A.hp = A.max; B.hp = 0; B.down = true;
    ok('an elixir is sold at full health when a friend is down',
       shopState(A, item('elixir')) === 'ok', shopState(A, item('elixir')));
    shopBuy(A, 'elixir');
    ok('and raises them', !B.down && B.hp > 0, B.down ? 'still down' : 'up with ' + Math.round(B.hp));
    A.hp = A.max; B.hp = B.max; B.down = false;
    ok('with nobody down it is not sold to the healthy',
       shopState(A, item('elixir')) === 'full', shopState(A, item('elixir')));
  }

  /* 7. the upgrades actually do something */
  {
    const P = shopOpen(5, 9999999);
    const before = { max: P.max, dmg: P.up.dmg, spd: P.up.spd, crit: P.up.crit };
    shopBuy(P, 'vit'); shopBuy(P, 'power'); shopBuy(P, 'swift'); shopBuy(P, 'crit');
    ok('Vitality raises the health it promises', P.max >= before.max + 25, before.max + ' -> ' + P.max);
    ok('Might, Fleet Feet and Keen Edge all land',
       P.up.dmg > before.dmg && P.up.spd > before.spd && P.up.crit > before.crit,
       'dmg ' + P.up.dmg.toFixed(2) + ' spd ' + P.up.spd.toFixed(2) + ' crit ' + P.up.crit.toFixed(3));
  }

  /* 8. leaving the stall takes you down, and only from the stall */
  {
    const P = shopOpen(7, 0);
    const was = G.level;
    leaveShop();
    ok('leaving the stall is how you descend', G.level === was + 1 && G.state === 'play',
       'depth ' + G.level + ', ' + G.state);
    const after = G.level;
    leaveShop();
    ok('and calling it again from the floor does nothing', G.level === after, 'depth ' + G.level);
  }

  /* 9. the gear stall */
  {
    const P = shopOpen(8, 100000);
    rollWares();
    ok('the stall lays out three things', G.wares.length === 3, String(G.wares.length));
    ok('one of each kind', new Set(G.wares.map(w => w.slot)).size === 3,
       G.wares.map(w => w.slot).join(','));
    ok('each with a price', G.wares.every(w => w.price > 0), G.wares.map(w => w.price).join(','));
    const w = G.wares[0], purse = G.gold;
    ok('and a bought one is paid for and marked sold',
       buyWare(P, 0) && G.wares[0].sold && G.gold === purse - w.price,
       purse + ' -> ' + G.gold + ', sold ' + G.wares[0].sold);
    ok('and cannot be bought twice', buyWare(P, 0) === false);
  }

  /* 10. what the stall would cost against what a run actually earns -- a cap
         nobody can reach is a cap that is not really there */
  {
    const P = shopOpen(10, 0);
    let full = 0;
    for (const it of SHOP) {
      const cap = it.id === 'master' ? 6 : (it.max || 1);
      for (let n = 0; n < cap; n++) full += Math.round((it.base + it.per * 10) * Math.pow(it.grow, n));
    }
    ok('maxing every upgrade at depth ten is priced out of reach, by design',
       full > 20000, full + ' gold for the lot');
  }
}

"""

io.open(p, 'w', encoding='utf-8', newline='').write(s.replace(anchor, block + anchor))
print('shop tests inserted')
