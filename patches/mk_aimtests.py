import io

p = 'behave2_drive.js'
s = io.open(p, encoding='utf-8').read()
anchor = "const fails = results.filter(r => r[0] === 'FAIL');"
assert s.count(anchor) == 1, 'anchor not unique'
assert 'playing without a mouse' not in s, 'already inserted'

block = r"""/* ---------------- playing without a mouse ----------------
   Three of the four delvers are ranged and the controls said "mouse aim",
   which reads to anyone without one as "this is not for you". It is: four
   seconds after the mouse last moved, P1 falls back to the same assisted
   aim that P2 -- who has never had a mouse -- uses for everything.

   That is an accessibility feature the game kept to itself, so it had
   better work. */
{
  const arena = (cls) => {
    startGame([cls]); G.level = 4; genLevel();
    G.offer = null; G.offerQ.length = 0; G.state = 'play';
    G.enemies.length = 0; G.shots.length = 0; G.items.length = 0;
    const P = G.players[0];
    P.hp = P.max; P.cd = 0; P.inv = 0; P.face = 0; P.aim = 0;
    const tx = Math.floor(P.x / T), ty = Math.floor(P.y / T);
    for (let y = ty - 5; y <= ty + 5; y++) for (let x = tx - 7; x <= tx + 7; x++)
      if (x > 0 && y > 0 && x < MW - 1 && y < MH - 1) G.map[y * MW + x] = 0;
    G.mapVer++;
    return P;
  };
  const foe = (P, dx, dy) => {
    spawnFoe('gloam', P.x + dx, P.y + (dy || 0), false);
    const e = G.enemies[G.enemies.length - 1]; e.hp = e.max = 9999; return e;
  };
  const deg = r => r * 180 / Math.PI;

  /* 1. facing roughly at something is enough */
  {
    const P = arena('thistle');
    const e = foe(P, 120, 40);                       /* about 18 degrees off */
    const straight = 0;
    const aimed = assistAim(P, straight);
    const want = Math.atan2(e.y - P.y, e.x - P.x);
    ok('facing roughly at a foe puts the shot on it', Math.abs(aimed - want) < 1e-9,
       deg(aimed).toFixed(1) + ' vs the foe at ' + deg(want).toFixed(1));
    ok('and it is a correction, not the direction you were facing',
       Math.abs(aimed - straight) > .1, deg(aimed - straight).toFixed(1) + ' degrees of help');
  }

  /* 2. but it is help, not a homing beacon */
  {
    const P = arena('thistle');
    foe(P, 40, 400);                                  /* far off to the side */
    ok('something behind you is not swung round to', assistAim(P, 0) === 0,
       deg(assistAim(P, 0)).toFixed(1));
    const Q = arena('thistle');
    foe(Q, 600, 0);                                   /* dead ahead but distant */
    ok('and something too far away is left alone', assistAim(Q, 0) === 0,
       deg(assistAim(Q, 0)).toFixed(1));
  }

  /* 3. it does not shoot through walls */
  {
    const P = arena('thistle');
    const e = foe(P, 120, 0);
    const wall = Math.floor((P.x + 60) / T) + Math.floor(P.y / T) * MW;
    G.map[wall] = 1; G.mapVer++;
    ok('and nothing is aimed at through a wall', assistAim(P, 0) === 0,
       'aim ' + deg(assistAim(P, 0)).toFixed(1));
    G.map[wall] = 0; G.mapVer++;
    ok('though the same foe is found once the wall is gone',
       assistAim(P, 0) !== 0 || e.y !== P.y);
  }

  /* 4. the crypts count too, since breaking them is half the floor */
  {
    const P = arena('ember');
    G.nests.length = 0;
    G.nests.push({ x: P.x + 100, y: P.y + 30, hp: 10, max: 10, r: 12, t: 0, flash: 0 });
    ok('a crypt is something worth aiming at', assistAim(P, 0) !== 0,
       deg(assistAim(P, 0)).toFixed(1));
    G.nests.length = 0;
  }

  /* 5. THE POINT: a delver who never touches a mouse can actually hit
        something, through the real input path */
  {
    const P = arena('thistle');
    const e = foe(P, 150, 45);
    /* the mouse has not moved in a long time, which is what readInput tests */
    mouse.last = -100000;
    keys.KeyD = true;                                 /* walking right */
    readInput();
    keys.KeyD = false;
    const hp = e.hp;
    P.aim = INS[0].aim; P.cd = 0; attack(P);
    for (let i = 0; i < 40; i++) update(1 / 60);
    ok('a delver who never touches a mouse still hits what they face',
       e.hp < hp, 'took ' + (hp - e.hp).toFixed(0));
  }

  /* 6. and the second delver, who has never had a mouse at all */
  {
    startGame(['bulwark', 'thistle']); G.level = 4; genLevel();
    G.offer = null; G.offerQ.length = 0; G.state = 'play';
    G.enemies.length = 0; G.shots.length = 0;
    const P2 = G.players[1];
    const tx = Math.floor(P2.x / T), ty = Math.floor(P2.y / T);
    for (let y = ty - 5; y <= ty + 5; y++) for (let x = tx - 7; x <= tx + 7; x++)
      if (x > 0 && y > 0 && x < MW - 1 && y < MH - 1) G.map[y * MW + x] = 0;
    G.mapVer++;
    spawnFoe('gloam', P2.x + 140, P2.y + 40, false);
    const e = G.enemies[G.enemies.length - 1]; e.hp = e.max = 9999;
    keys.ArrowRight = true;
    readInput();
    keys.ArrowRight = false;
    const want = Math.atan2(e.y - P2.y, e.x - P2.x);
    ok('the second delver is aimed for, always', Math.abs(INS[1].aim - want) < 1e-9,
       deg(INS[1].aim).toFixed(1) + ' vs ' + deg(want).toFixed(1));
  }

  /* 7. and the help is mentioned, which was the whole problem */
  {
    G.paused = false; pauseShown = false;
    startGame(['thistle']); G.level = 2; genLevel();
    G.offer = null; G.offerQ.length = 0; G.state = 'play';
    const was = btnsOn; btnsOn = false;
    G.paused = true; frame(0);
    ok('and the pause sheet says a mouse is not needed',
       /No mouse needed/i.test($('pauseKeys').textContent), $('pauseKeys').textContent.slice(-60));
    btnsOn = was; G.paused = false; frame(0);
  }
}

"""

io.open(p, 'w', encoding='utf-8', newline='').write(s.replace(anchor, block + anchor))
print('keyboard aim tests inserted')
