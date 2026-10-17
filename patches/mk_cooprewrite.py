import io

p = 'behave2_drive.js'
s = io.open(p, encoding='utf-8').read()

start = s.index('/* ---------------- two delvers, one keyboard ---------------- */')
# the block ends at the next top-level comment heading
end = s.index('/* ---------------- it thins itself on a slow device ---------------- */')

block = r"""/* ---------------- two delvers, one keyboard ---------------- */
{
startGame(['bulwark', 'sable']);
ok('two delvers start together', G.players.length === 2, G.players.map(p => p.cls.name).join(' + '));
ok('co-op is flagged', G.co === true);
G.level = 4; genLevel();
let g = 0; while (G.offer && g++ < 20) applyUpgrade(0); G.offerQ.length = 0; G.state = 'play';
ok('both are placed on open floor', G.players.every(p => openAt(p.x, p.y) && !blockedAt(p.x, p.y, 11)));

/* one falling must not end the run */
const [A, B] = G.players;
A.hp = 1; A.inv = 0; downPlayer(A);
ok('one down does not end the run', G.state === 'play' && A.down === true);
ok('and the other still stands', !B.down);

/* and a partner standing over them can bring them back */
B.x = A.x + 6; B.y = A.y;
for (let i = 0; i < 180 && A.down; i++) updateRevive(1 / 60);
ok('a partner can raise the fallen', A.down === false, 'hp=' + Math.round(A.hp));

/* both down ends it */
A.inv = 0; B.inv = 0; downPlayer(A); downPlayer(B);
ok('both down ends the run', G.state === 'dead');

/* The stairs rule lives at the end of update: every delver still standing has
   to be within reach of the exit. Drive it a frame at a time in a bare room,
   rather than simulating two hundred and letting everything else in the game
   decide the answer. */
startGame(['ember', 'thistle']); G.level = 3; genLevel();
g = 0; while (G.offer && g++ < 20) applyUpgrade(0); G.offerQ.length = 0; G.state = 'play';
const [P1, P2] = G.players;
const lvl0 = G.level;
G.keys = 9;
const clear = () => {
  G.enemies.length = 0; G.nests.length = 0; G.hazards.length = 0; G.eshots.length = 0;
  G.hitstop = 0; G.winPending = false; G.offerQ.length = 0; G.offer = null;
  for (const p of G.players) { p.down = false; p.hp = p.max; p.inv = 1e9; p.kx = 0; p.ky = 0; p.dash = 0; }
};
const put = (p, dx) => { p.x = G.exit.x + dx; p.y = G.exit.y; };

clear(); put(P1, -6); put(P2, 600);
update(1 / 60);
ok('one delver alone does not take the stairs', G.state === 'play', G.state);

clear(); put(P1, -6); put(P2, 6);
update(1 / 60);
ok('both on the stairs clears the depth', G.state === 'clear', G.state);

for (let i = 0; i < 200 && G.state === 'clear'; i++) clearTick(1 / 60);
ok('and the stall follows', G.state === 'shop', G.state);
if (G.state === 'shop') { renderShop(); leaveShop(); }
ok('and leaving it descends', G.level > lvl0, 'depth ' + lvl0 + ' -> ' + G.level);
ok('both delvers come down together', G.players.filter(p => !p.down).length === 2);

/* a fallen partner must not hold the stairs: the living ones decide */
g = 0; while (G.offer && g++ < 20) applyUpgrade(0); G.offerQ.length = 0; G.state = 'play';
G.keys = 9;
clear(); put(P1, -6); P2.down = true; P2.x = G.exit.x + 600; P2.y = G.exit.y;
update(1 / 60);
ok('a fallen partner does not hold the stairs', G.state === 'clear', G.state);
G.state = 'play';

/* an offer belongs to one delver, and must land on that one */
startGame(['bulwark', 'sable']); G.level = 5; genLevel(); G.offerQ.length = 0; G.offer = null;
queueOffer({ kind: 'up', P: G.players[1], opts: rollOffer(false) });
ok('an offer can belong to the second delver', G.offer && G.offer.P === G.players[1]);
const second0 = G.players[1].dmgMul, first0 = G.players[0].dmgMul;
applyUpgrade(0);
ok('and it applies to that delver', G.players[1].dmgMul !== second0 || G.players[1].plvl > 0);
ok('not to the first', G.players[0].dmgMul === first0);
}

"""

io.open(p, 'w', encoding='utf-8', newline='').write(s[:start] + block + s[end:])
print('co-op block rewritten')
