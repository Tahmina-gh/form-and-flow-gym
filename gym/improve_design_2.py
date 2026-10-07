"""
FORM & FLOW - design upgrade #2: editorial pull-quote, facility captions,
more breathing room on larger screens, trust line under pricing.

Save this in the project ROOT (the "gym" folder, next to manage.py) and run:
    py improve_design_2.py
Safe to run twice - anything already applied is skipped and reported.
"""
import pathlib

EDITS = []
def edit(file, old, new):
    EDITS.append((file, old, new))

H = "core/templates/core/home.html"
C = "static/css/style.css"

# ---------------------------------------------------------------- home.html
# 1. Editorial pull-quote, inserted right before the "paths" section
edit(H,
'<section id="paths">',
'''<section class="pull-quote">
  <div class="wrap">
    <p>This isn't a gym you survive. It's a studio you <em>return to</em>.</p>
  </div>
</section>

<section id="paths">''')

# 2. One-line captions on each facility photo
edit(H, '<span>Studio</span></div>',
'<span>Studio<span class="caption">Open-plan, light-filled, built for group and private sessions alike.</span></span></div>')
edit(H, '<span>Strength Area</span></div>',
'<span>Strength Area<span class="caption">Free weights and platforms, spaced so you\'re never waiting.</span></span></div>')
edit(H, '<span>Recovery Area</span></div>',
'<span>Recovery Area<span class="caption">Stretch, breathe, and let your nervous system catch up.</span></span></div>')
edit(H, '<span>Changing Rooms</span></div>',
'<span>Changing Rooms<span class="caption">Quiet and unhurried, stocked with everything you forgot.</span></span></div>')
edit(H, '<span>Relaxation Zone</span></div>',
'<span>Relaxation Zone<span class="caption">Sit with a tea before or after — no one\'s rushing you out.</span></span></div>')

# 3. Trust line under the membership plans
edit(H,
'''    </div>
  </div>
</section>

<section id="facility">''',
'''    </div>
    <p class="plan-note">No lock-in contracts · Pause anytime · Cancel in one click</p>
  </div>
</section>

<section id="facility">''')

# ------------------------------------------------------------------ style.css
# 1. Pull-quote styling
edit(C,
'section{padding:88px 0;}',
'''section{padding:88px 0;}
.pull-quote{padding:40px 0; text-align:center;}
.pull-quote p{font-family:'Fraunces',serif; font-style:italic; font-size:clamp(24px,3.4vw,34px); color:var(--brown); max-width:18ch; margin:0 auto; line-height:1.3;}
.pull-quote p em{color:var(--terracotta-dark); font-style:italic;}
.plan-note{text-align:center; margin-top:28px; font-size:13px; color:var(--brown-soft); letter-spacing:.3px;}
@media(min-width:1024px){
  section{padding:120px 0;}
  .section-head{margin-bottom:60px;}
}''')

# 2. Caption text under each facility label
edit(C,
'.facility-card span{position:relative; font-family:\'Fraunces\',serif; font-size:22px; text-shadow:0 2px 10px rgba(0,0,0,.45);}',
'''.facility-card span{position:relative; font-family:'Fraunces',serif; font-size:22px; text-shadow:0 2px 10px rgba(0,0,0,.45);}
.facility-card .caption{display:block; font-family:'Inter',sans-serif; font-style:normal; font-size:12.5px; font-weight:400; color:rgba(255,255,255,.82); margin-top:4px; text-shadow:0 1px 6px rgba(0,0,0,.4);}''')

# ------------------------------------------------------------------- runner
def main():
    ok = skipped = missing = 0
    for file, old, new in EDITS:
        path = pathlib.Path(file)
        if not path.exists():
            print("MISSING  %s  (run this from the project root - the 'gym' folder)" % file)
            missing += 1
            continue
        text = path.read_text(encoding="utf-8")
        if new in text:
            print("SKIP     %s  (already applied): %s" % (file, old.strip().splitlines()[0][:50]))
            skipped += 1
            continue
        if old not in text:
            print("NOT FOUND %s: %s" % (file, old.strip().splitlines()[0][:50]))
            missing += 1
            continue
        path.write_text(text.replace(old, new, 1), encoding="utf-8")
        print("OK       %s: %s" % (file, old.strip().splitlines()[0][:50]))
        ok += 1
    print("\nDone. %d applied, %d already applied, %d problems." % (ok, skipped, missing))

if __name__ == "__main__":
    main()