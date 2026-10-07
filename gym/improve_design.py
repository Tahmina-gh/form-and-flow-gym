"""
FORM & FLOW - design upgrade #1: trust strip, icons, checkmarks, card lift.

HOW TO USE
  1. Save this file in the project ROOT - the "gym" folder, next to manage.py.
  2. In the VS Code terminal (Ctrl + `), make sure you're in that folder, then run:
         py improve_design.py
  Safe to run twice - anything already applied is skipped and reported.
"""
import pathlib

EDITS = []
def edit(file, old, new):
    EDITS.append((file, old, new))

H = "core/templates/core/home.html"
C = "static/css/style.css"

# ---------------------------------------------------------------- home.html
# 1. "Why Form & Flow" trust strip, right after the marquee
edit(H,
'''<section id="paths">''',
'''<section style="padding:64px 0 24px;">
  <div class="wrap">
    <div class="why-grid">
      <div class="why-card">
        <div class="why-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" width="26" height="26"><circle cx="12" cy="9" r="5"/><path d="M8.5 13.5L7 21l5-2.5L17 21l-1.5-7.5"/></svg></div>
        <h3>Certified Coaches</h3>
        <p>Every trainer is certified and coaches your form, not just your reps.</p>
      </div>
      <div class="why-card">
        <div class="why-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" width="26" height="26"><circle cx="9" cy="8" r="3"/><path d="M3 20c0-3.3 2.7-6 6-6s6 2.7 6 6"/><circle cx="17.5" cy="9" r="2.2"/><path d="M15.3 20c0-2.6 1-4.6 2.5-5.7"/></svg></div>
        <h3>Small Class Sizes</h3>
        <p>Capped classes so you always get personal attention.</p>
      </div>
      <div class="why-card">
        <div class="why-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" width="26" height="26"><rect x="3" y="9" width="18" height="4"/><rect x="5" y="13" width="14" height="8"/><path d="M12 9v12"/><path d="M12 9c-1.4-3-5-4-5-1.3C7 9.2 9 9 12 9zM12 9c1.4-3 5-4 5-1.3C17 9.2 15 9 12 9z"/></svg></div>
        <h3>Free First Visit</h3>
        <p>Try a class or the studio on us before you commit to anything.</p>
      </div>
      <div class="why-card">
        <div class="why-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" width="26" height="26"><path d="M20 11A8 8 0 1 0 18.5 16"/><path d="M20 5v6h-6"/></svg></div>
        <h3>Flexible Membership</h3>
        <p>Pause or cancel anytime — no lock-in contracts.</p>
      </div>
    </div>
  </div>
</section>

<section id="paths">''')

# 2. Real icons instead of plain colour circles on the 3 path cards
edit(H,
'<div class="path-card"><div class="path-icon"></div><h3>Build Strength</h3>',
'''<div class="path-card"><div class="path-icon"><svg viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="9" width="3" height="6" rx="1"/><rect x="19" y="9" width="3" height="6" rx="1"/><rect x="6" y="7" width="2.5" height="10" rx="1"/><rect x="15.5" y="7" width="2.5" height="10" rx="1"/><line x1="8.5" y1="12" x2="15.5" y2="12"/></svg></div><h3>Build Strength</h3>''')

edit(H,
'<div class="path-card"><div class="path-icon" style="background:var(--terracotta)"></div><h3>Move &amp; Mobility</h3>',
'''<div class="path-card"><div class="path-icon" style="background:var(--terracotta)"><svg viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="4" r="2"/><path d="M12 6v7M12 13l-5 5M12 13l5 5M9 9l3-1 3 1"/></svg></div><h3>Move &amp; Mobility</h3>''')

edit(H,
'<div class="path-card"><div class="path-icon" style="background:#B7A48C"></div><h3>Reset &amp; Recover</h3>',
'''<div class="path-card"><div class="path-icon" style="background:#B7A48C"><svg viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M5 19c8 0 14-6 14-14-8 0-14 6-14 14z"/><path d="M5 19c0-5 3-9 7-11"/></svg></div><h3>Reset &amp; Recover</h3>''')

# 3. Nicer star rating on testimonials
edit(H,
'<div class="name">{{ t.name }} · {{ t.rating }}★</div>',
'<div class="name">{{ t.name }} <span class="stars">{{ t.rating }}.0 ★</span></div>')

# ------------------------------------------------------------------ style.css
# 1. Trust strip layout
edit(C,
'.eyebrow{color:var(--sage-dark); font-size:12.5px; font-weight:600; letter-spacing:2px; margin-bottom:16px;}',
'''.eyebrow{color:var(--sage-dark); font-size:12.5px; font-weight:600; letter-spacing:2px; margin-bottom:16px;}
.why-grid{display:grid; gap:24px; grid-template-columns:repeat(2,1fr); text-align:center;}
@media(min-width:780px){.why-grid{grid-template-columns:repeat(4,1fr);}}
.why-icon{width:56px; height:56px; margin:0 auto 14px; border-radius:50%; background:var(--beige); display:flex; align-items:center; justify-content:center; color:var(--terracotta-dark);}
.why-card h3{font-size:16.5px; margin-bottom:6px;}
.why-card p{font-size:13.5px; color:var(--brown-soft); line-height:1.5;}''')

# 2. Icons inside the path cards + gentle hover lift
edit(C,
'.path-icon{width:52px; height:52px; border-radius:50%; background:var(--sage); margin-bottom:20px;}',
'.path-icon{width:52px; height:52px; border-radius:50%; background:var(--sage); margin-bottom:20px; display:flex; align-items:center; justify-content:center;}\n.path-icon svg{width:26px; height:26px;}')

# 3. Checkmarks on membership plan lists (replaces the plain border-top list)
edit(C,
'''.plan ul li{padding:6px 0; border-top:1px solid rgba(0,0,0,.08);}
.plan.featured ul li{border-top:1px solid rgba(255,255,255,.14);}
.plan ul li:first-child{border-top:none;}''',
'''.plan ul li{padding:7px 0 7px 26px; border-top:1px solid rgba(0,0,0,.08); position:relative;}
.plan ul li::before{content:''; position:absolute; left:0; top:12px; width:14px; height:14px; background:var(--sage-dark); -webkit-mask:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='white' stroke-width='3' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpolyline points='20 6 9 17 4 12'/%3E%3C/svg%3E") center/contain no-repeat; mask:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='white' stroke-width='3' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpolyline points='20 6 9 17 4 12'/%3E%3C/svg%3E") center/contain no-repeat;}
.plan.featured ul li{border-top:1px solid rgba(255,255,255,.14);}
.plan.featured ul li::before{background:var(--terracotta);}
.plan ul li:first-child{border-top:none;}''')

# 4. Subtle hover lift on plan / facility / testimonial cards, and styled star rating
edit(C,
'.plan{background:var(--beige); border-radius:var(--radius); padding:32px 28px; position:relative; box-shadow:var(--shadow-sm); border-top:3px solid transparent;}',
'.plan{background:var(--beige); border-radius:var(--radius); padding:32px 28px; position:relative; box-shadow:var(--shadow-sm); border-top:3px solid transparent; transition:transform .18s ease, box-shadow .18s ease;}\n.plan:hover{transform:translateY(-4px); box-shadow:var(--shadow);}')

edit(C,
'.facility-card{border-radius:var(--radius); height:220px; padding:22px; display:flex; align-items:flex-end; color:#fff; position:relative; overflow:hidden; box-shadow:var(--shadow-sm); background:var(--beige-2);}',
'.facility-card{border-radius:var(--radius); height:220px; padding:22px; display:flex; align-items:flex-end; color:#fff; position:relative; overflow:hidden; box-shadow:var(--shadow-sm); background:var(--beige-2); transition:transform .18s ease, box-shadow .18s ease;}\n.facility-card:hover{transform:translateY(-4px); box-shadow:var(--shadow);}')

edit(C,
'.testi{background:#fff; border-radius:var(--radius); padding:26px; box-shadow:var(--shadow-sm); position:relative; overflow:hidden;}',
'.testi{background:#fff; border-radius:var(--radius); padding:26px; box-shadow:var(--shadow-sm); position:relative; overflow:hidden; transition:transform .18s ease;}\n.testi:hover{transform:translateY(-4px);}\n.stars{color:var(--terracotta-dark); font-weight:600;}')

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