from patch import edit, run

L = 'part_logic.js'
H = 'part_head.html'

# --- the thing that actually kills you was the thing you could not see -----
# Across fifty-six simulated runs, seventy per cent of all the health lost
# was the drain, not a monster. The dungeon is the enemy; the foes are
# weather. And the drain is not a constant: it climbs with depth, the famine
# omen multiplies it, a pact can raise it by half, a cursed trinket adds to
# it and the Barrow's Slow Blood perk takes some away.
#
# All of that was invisible. The bar went down, and nothing told you how
# fast, or that the bargain you just took had changed the rate.
#
# So: a shaded band at the leading edge of the health bar, showing the next
# ten seconds of drain. It is not a prediction of your death -- food and
# fights make a mockery of that -- it is the rate, drawn to scale, which is
# the one honest thing a bar can say. It grows when you take Embers. It
# turns amber when the rate is worse than the depth alone would give.

# one function, so the bar cannot drift from what the floor actually takes
edit(L, """  /* the dungeon itself is draining you; food is the only clock that matters */
  const dl = (.8 + Math.min(G.level, 8) * .2 + Math.max(0, G.level - 8) * .07) * om('drain', 1);
  P.hp -= dl * (G.co ? .85 : 1) * (P.drainMul || 1) * dt;""",
     """  /* the dungeon itself is draining you; food is the only clock that matters */
  P.hp -= drainRate(P) * dt;""")

edit(L, """const om = (k, dflt) => (G.omen && G.omen[k] !== undefined) ? G.omen[k] : dflt;""",
     """const om = (k, dflt) => (G.omen && G.omen[k] !== undefined) ? G.omen[k] : dflt;
/* The drain, in one place, because the health bar draws this number and the
   floor takes it: two copies would be two answers.
   drainPlain is what the depth alone asks. Everything past it -- the omen,
   the pacts, a curse, the Barrow's slow blood, the mercy of having company
   -- is the part worth showing a player, because it is the part they chose
   or were dealt. */
function drainPlain() { return .8 + Math.min(G.level, 8) * .2 + Math.max(0, G.level - 8) * .07; }
function drainRate(P) { return drainPlain() * om('drain', 1) * (G.co ? .85 : 1) * ((P && P.drainMul) || 1); }
/* how far the band on the bar looks ahead */
const DRAIN_AHEAD = 10;""")

# --- and on the bar ------------------------------------------------------
edit(L, """const mkHud = s => ({ box: $('hp' + s), hp: $('hpFill' + s), txt: $('hpTxt' + s), dash: $('dashFill' + s), sp: $('spFill' + s), name: $('clsName' + s), xp: $('xpFill' + s), lv: $('lv' + s), gear: $('gear' + s) });""",
     """const mkHud = s => ({ box: $('hp' + s), hp: $('hpFill' + s), txt: $('hpTxt' + s), dash: $('dashFill' + s), sp: $('spFill' + s), name: $('clsName' + s), xp: $('xpFill' + s), lv: $('lv' + s), gear: $('gear' + s), drain: $('drainFill' + s) });""")

edit(L, """  h.hp.style.width = (P.hp / P.max * 100) + '%'; h.txt.textContent = P.down ? 'DOWN' : Math.ceil(P.hp) + ' / ' + P.max;
  h.hp.style.background = P.hp / P.max < .34 ? '#ff2f28' : '';""",
     """  h.hp.style.width = (P.hp / P.max * 100) + '%'; h.txt.textContent = P.down ? 'DOWN' : Math.ceil(P.hp) + ' / ' + P.max;
  h.hp.style.background = P.hp / P.max < .34 ? '#ff2f28' : '';
  /* the next ten seconds of drain, drawn to scale at the leading edge */
  if (h.drain) {
    const rate = drainRate(P), cost = Math.min(P.hp, rate * DRAIN_AHEAD);
    const lo = Math.max(0, (P.hp - cost) / P.max), hi = Math.max(lo, P.hp / P.max);
    h.drain.hidden = P.down || P.hp <= 0;
    h.drain.style.left = (lo * 100) + '%';
    h.drain.style.width = ((hi - lo) * 100) + '%';
    /* amber when something you took made it worse than the depth alone */
    h.drain.classList.toggle('worse', rate > drainPlain() * 1.02);
    h.drain.title = 'The deep takes ' + rate.toFixed(1) + ' health a second here';
  }""")

# --- and say so, once, when the lesson lands -----------------------------
edit(L, """  ['drain', 'Your health drains the whole way down. Food is the only thing that gives it back.'],""",
     """  ['drain', 'Your health drains the whole way down \\u2014 the shaded part of your bar is the next ten seconds of it. Food is the only thing that gives it back.'],""")

# --- markup --------------------------------------------------------------
edit(H, """        <div class="track"><div class="fill" id="hpFill"></div></div>""",
     """        <div class="track"><div class="fill" id="hpFill"></div><div class="fill drain" id="drainFill" hidden></div></div>""")

edit(H, """        <div class="track"><div class="fill" id="hpFill2"></div></div>""",
     """        <div class="track"><div class="fill" id="hpFill2"></div><div class="fill drain" id="drainFill2" hidden></div></div>""")

edit(H, """.track{height:8px; background:#0a0c11; border:1px solid var(--line)}""",
     """.track{height:8px; background:#0a0c11; border:1px solid var(--line); position:relative}
/* the share of the bar the deep is about to take: hatched, so it reads as
   spoken for rather than as health you still have */
.fill.drain{position:absolute; top:0; width:0; transition:none; pointer-events:none;
  background:repeating-linear-gradient(135deg, rgba(235,228,210,.42) 0 2px, rgba(235,228,210,0) 2px 5px)}
.fill.drain.worse{background:repeating-linear-gradient(135deg, rgba(255,164,60,.62) 0 2px, rgba(255,164,60,0) 2px 5px)}""")

run()
