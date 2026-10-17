from patch import edit, run

L = 'part_logic.js'

# btnsOn records whether the touch buttons are showing, and decides where the
# narrator's line sits and what the pause overlay tells you to press. It was
# only ever recomputed by resize(). Since the buttons are now gated on the
# stage's playing class, starting a run changes their visibility without
# changing any element's size.
#
# It does in fact keep up, because the observer fires anyway, but nothing in
# the code says so and it took a live check to find out. Recompute it where
# the class actually changes, so it is true by construction rather than by a
# side effect nobody wrote down.
edit(L, """      st.dataset.play = on ? '1' : '0';
      st.classList.toggle('playing', on);
      if (document.body && document.body.classList) document.body.classList.toggle('playing', on);
    } }""",
     """      st.dataset.play = on ? '1' : '0';
      st.classList.toggle('playing', on);
      if (document.body && document.body.classList) document.body.classList.toggle('playing', on);
      try { btnsOn = getComputedStyle($('dashBtn')).display !== 'none'; } catch (e) {}
    } }""")

run()
