from patch import edit, run

H = 'part_head.html'

# The offer sits above the delver cards, because if you left a run going it
# is almost certainly what you came back for. Hidden outright when there is
# nothing to carry on, so a first-time player never sees it.
edit(H, """      <div class="row" id="modes">""",
     """      <div class="row" id="resumeRow" hidden>
        <button class="btn" id="resume" type="button">Carry on</button>
        <button class="btn alt" id="abandon" type="button">Leave it down there</button>
      </div>
      <div class="row" id="modes">""")

run()
