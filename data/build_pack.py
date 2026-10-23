#!/usr/bin/env python3
"""Build the single Northeast Florida pack: validation-jax.html

This replaces the three separate pages (old jax pack, Laredo pack, supply-scan page).
Source of truth: nefl-supply-scan.json + nefl-review-counts.csv + nefl-keyword-demand.csv.
Run: python3 build_pack.py
"""
import json, os, csv, html, statistics as st

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

D = json.load(open(os.path.join(HERE, "nefl-supply-scan.json")))
OPS = list(csv.DictReader(open(os.path.join(HERE, "nefl-supply-scan.csv"))))
REVIEWS = list(csv.DictReader(open(os.path.join(HERE, "nefl-review-counts.csv"))))
KW = list(csv.DictReader(open(os.path.join(HERE, "nefl-keyword-demand.csv"))))


def esc(s):
    return html.escape(str(s)) if s is not None else ""


def phone_link(p):
    if not p:
        return "—"
    digits = "".join(c for c in p if c.isdigit())
    return f'<a href="tel:+1{digits}">{esc(p)}</a>'


def rev_summary(svc):
    key = {"marine salvage / recovery": "marine salvage"}.get(svc, svc)
    rs = [r for r in REVIEWS if r["service"] == key]
    rc = sorted(int(r["review_count"]) for r in rs if r["review_count"])
    if not rc:
        return None
    return {"n": len(rs), "median": int(st.median(rc)), "lo": rc[0], "hi": rc[-1]}


def dedupe(svc, regions=("core", "fringe")):
    rows = [r for r in OPS if r["service"] == svc and r["region"] in regions]
    by = {}
    for r in rows:
        k = r["operator"].lower()
        e = by.setdefault(k, {"name": r["operator"], "phone": r["phone"],
                              "rating": r["rating"], "website": r["website"], "metros": []})
        if r["metro"] not in e["metros"]:
            e["metros"].append(r["metro"])
        if r["website"] == "yes":
            e["website"] = "yes"
        if r["phone"] and not e["phone"]:
            e["phone"] = r["phone"]
    items = list(by.values())
    items.sort(key=lambda x: (-float(x["rating"] or 0), x["name"].lower()))
    return items


def op_table(svc):
    out = []
    for it in dedupe(svc):
        web = ('<span class="pill p-yes">yes</span>' if it["website"] == "yes"
               else '<span class="pill p-no">no</span>')
        metros = ", ".join(esc(m.replace(" FL", "")) for m in it["metros"])
        out.append(f'      <tr><td>{esc(it["name"])}</td><td class="phone">{phone_link(it["phone"])}</td>'
                   f'<td>{esc(it["rating"] or "—")}</td><td>{web}</td><td class="thin">{metros}</td></tr>')
    return "\n".join(out)


GAPS = [
    ("well pump repair", "Well pump repair", "Supply gap, but geographic",
     "20 paid listings · median 132 reviews",
     "The metro has established incumbents — 928 reviews at the top of the pack. What it does not have is coverage at the edges: Orange Park returns 2 listings, Macclenny's local options rate 3.0–3.2, and 6 of 20 paid listings have no website at all. Several two-truck shops advertise 24-hour service.",
     "If a fringe customer's well dies at 6pm, the choice is a phone that rings out or a drive from the city. That is an intake problem at the edge of a metro, not a visibility problem."),
    ("boat detailing", "Boat detailing", "Thinnest bench of the four",
     "11 paid listings · median 17 reviews",
     "Half the local-pack results are car detailers with a boat line. The boat-only operators are single-operator mobile businesses — median 17 reviews against 132 in well pump. The beaches compete on polish at 5.0; the river metros barely have a boat specialist.",
     "Mobile by nature, no shop, no inventory. The constraint is one person's calendar, which is exactly what an intake layer relieves."),
    ("hurricane shutter installation", "Hurricane shutter installation", "Bimodal, consultative",
     "12 paid listings · median 78 reviews",
     "One specialist serves the whole core metro. Everything else in the pack is a blinds store or a window installer, and Orange Park returns two results. Review depth is bimodal: a 1,000-review incumbent beside entrants with 2–12.",
     "High ticket, insurance-adjacent, and sold by appointment. The sellable unit is a booked measure, not a callback."),
    ("marine salvage / recovery", "Marine salvage &amp; recovery", "Real gap, storm-gated",
     "10 paid listings · median 12 reviews",
     "No dedicated marine salvage operator appears in any metro scanned — only dive shops, tow services and boat yards. The category is effectively unbuilt locally, which is also why there is no proof anyone pays for it.",
     "After a named storm the scarce resource is a crew with a barge, not a phone number that ranks. Weakest of the four because it is seasonal and you would be brokering availability you do not control."),
]

REJECTS = [
    ("Septic tank pumping", "7–11 per metro", "4.3–5.0", "Served everywhere in the ring. 508-listing scan found no invisible operator."),
    ("Dock / marine construction", "7–10 per metro", "4.9–5.0", "Premium trade, websites near-universal, relationships already established."),
    ("Porta potty rental", "6–7 per metro", "5.0 median", "Dense, but many are unrated no-website city-name shells — SEO churn, not capacity. Real operators own the result."),
    ("Generator repair", "5–7 per metro", "4.6–4.9", "Mostly electricians and dealers, not repair specialists. Storm-season demand is real but seasonal."),
    ("Land clearing", "5–8 per metro", "5.0", "Developer-led, long sales cycles. Not a call-driven business."),
    ("Mobile mechanic", "7 per metro", "4.8", "24-hour flags everywhere, several no-website operators — density high enough that this is service quality, not supply."),
]

# --- who to call first, per gap: fringe/edge operators with no website, or the specialists
def first_calls(svc, limit=6, prefer_nosite=True):
    items = [i for i in dedupe(svc) if i["phone"]]
    if prefer_nosite:
        items.sort(key=lambda x: (x["website"] == "yes", -float(x["rating"] or 0)))
    return items[:limit]


CALL_BLOCKS = []
for svc, label, _, _, _, _ in GAPS:
    picks = first_calls(svc)
    if not picks:
        continue
    lis = "".join(
        f'<li><b>{esc(p["name"])}</b> — {phone_link(p["phone"])} — '
        f'{esc(p["rating"] or "unrated")} · {"site" if p["website"]=="yes" else "no site"} · '
        f'<span class="thin">{esc(", ".join(p["metros"]))}</span></li>'
        for p in picks)
    CALL_BLOCKS.append(f'<h3 style="font-size:1rem;margin:0 0 6px">{label}</h3><ul class="calls">{lis}</ul>')

gap_sections = []
for svc, label, tag, stat, line, so_what in GAPS:
    rs = rev_summary(svc)
    n = len(dedupe(svc))
    gap_sections.append(f"""
<section>
  <div class="sechead"><h2>{label} <span class="tag-inline">{tag}</span></h2><span class="note">{stat}</span></div>
  <div class="panel" style="margin-bottom:14px">
    <p style="margin:0 0 10px">{line}</p>
    <p style="margin:0;font-size:.9rem;color:var(--ink2)"><b>So what:</b> {so_what}</p>
  </div>
  <div class="tablewrap"><table>
    <thead><tr><th>Operator</th><th>Phone</th><th>Rating</th><th>Web</th><th>Seen in</th></tr></thead>
    <tbody>
{op_table(svc)}
    </tbody>
  </table></div>
  <p class="thin">{n} unique operators across core + fringe metros, deduped by name.</p>
</section>""")

# --- supply map table (one row per service)
VERDICT = {k: v["verdict"] for k, v in D["assessment"].items()}
SERVICES = ["well pump repair", "boat detailing", "hurricane shutter installation",
            "marine salvage / recovery", "septic tank pumping", "dock / marine construction",
            "porta potty rental", "generator repair", "land clearing", "mobile mechanic"]
ORDER = {s: i for i, s in enumerate(SERVICES)}

map_rows = []
for svc in SERVICES:
    cells = [m for m in D["markets"] if m["service"] == svc and m["region"] in ("core", "fringe")]
    if not cells:
        continue
    ops = [m["operators"] for m in cells]
    meds = [m["median_rating"] for m in cells if m["median_rating"] is not None]
    rs = rev_summary(svc)
    rev = f'{rs["median"]}' if rs else "not pulled"
    v = VERDICT.get(svc, "")
    cls = "p-yes" if v.startswith(("gap", "thin")) else "p-no"
    map_rows.append(f'      <tr><td><b>{esc(svc.title())}</b></td><td>{len(cells)}</td>'
                    f'<td>{min(ops)}–{max(ops)}</td>'
                    f'<td>{round(min(meds),1) if meds else "—"}–{round(max(meds),1) if meds else "—"}</td>'
                    f'<td>{rev}</td><td><span class="pill {cls}">{esc(v)}</span></td></tr>')

# --- paid data tables
rev_rows = []
for svc, label in [("well pump repair", "Well pump repair"), ("boat detailing", "Boat detailing"),
                   ("hurricane shutter installation", "Hurricane shutters"), ("marine salvage", "Marine salvage")]:
    s = rev_summary(svc)
    if not s:
        continue
    noweb = sum(1 for r in REVIEWS if r["service"] == svc and r["website"] == "no")
    rev_rows.append(f'      <tr><td><b>{label}</b></td><td>{s["n"]}</td><td><b>{s["median"]}</b></td>'
                    f'<td>{s["lo"]}–{s["hi"]}</td><td>{noweb}</td></tr>')

JAX_TERMS = {"well pump repair jacksonville fl", "boat detailing jacksonville", "hurricane shutters jacksonville",
             "marine salvage jacksonville fl", "well drilling jacksonville fl", "storm shutters jacksonville fl"}
kw_rows = []
for r in KW:
    if r["keyword"] not in JAX_TERMS:
        continue
    vol = int(r["volume_monthly_national"] or 0)
    cpc = float(r["cpc_usd"] or 0)
    kw_rows.append((vol, f'      <tr><td>{esc(r["keyword"])}</td><td>{vol}</td><td>${cpc:.2f}</td></tr>'))
kw_rows.sort(key=lambda t: -t[0])
kw_html = "\n".join(h for _, h in kw_rows)

total_ops = len(OPS)
total_cells = len(D["markets"])

HTML = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow">
<meta name="color-scheme" content="light">
<title>Northeast Florida Pack — Boring Business Lab</title>
<style>
:root{{
  --ink:#141715;--ink2:#2c332e;--muted:#6a756d;--paper:#f3f0e7;--card:#fffdf7;
  --line:#d9d7c9;--acid:#c9f06b;--clay:#b8562f;--moss:#1d4a3f;--sand:#e9e5d6;
  --red:#8d3f32;--amber:#a3852a;--sea:#1c5a6b;
  --shadow:0 18px 44px rgba(20,35,28,.07);
  --mono:ui-monospace,SFMono-Regular,Menlo,monospace;
}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--paper);color:var(--ink);font:16px/1.6 -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;-webkit-font-smoothing:antialiased}}
a{{color:var(--moss);text-underline-offset:3px}}
h1,h2,h3,h4{{font-family:Georgia,serif;font-weight:500;letter-spacing:-.02em;margin:0}}
.wrap{{max-width:1100px;margin:0 auto;padding:0 26px}}
.bar{{position:sticky;top:0;z-index:40;background:rgba(243,240,231,.9);backdrop-filter:blur(14px);border-bottom:1px solid var(--line)}}
.bar .wrap{{display:flex;align-items:center;gap:14px;height:58px;font-size:.85rem;flex-wrap:wrap}}
.bar a.home{{font-weight:700;color:var(--ink);text-decoration:none}}
.bar .sep{{color:var(--line)}}.bar .spacer{{flex:1}}
.bar .btn{{border:1px solid var(--line);background:transparent;color:var(--ink);border-radius:7px;padding:6px 11px;font-size:.78rem;font-weight:650;text-decoration:none}}
header.hero{{padding:54px 0 24px;position:relative;overflow:hidden}}
header.hero .wave{{position:absolute;right:-80px;top:10px;width:340px;height:340px;border:1px solid var(--line);border-radius:50%;box-shadow:0 0 0 30px rgba(28,90,107,.04),0 0 0 64px rgba(28,90,107,.03);pointer-events:none}}
.kicker{{font-family:var(--mono);font-size:.72rem;letter-spacing:.16em;text-transform:uppercase;color:var(--sea);font-weight:600}}
h1{{font-size:clamp(2.2rem,5vw,3.8rem);line-height:1.02;margin:14px 0 18px;max-width:24ch}}
h1 em{{font-style:normal;color:var(--moss);border-bottom:5px solid var(--acid)}}
p.lede{{max-width:64ch;font-size:1.08rem;color:var(--ink2);margin:0}}
.rule{{border:0;border-top:1px solid var(--line);margin:30px 0}}
section{{padding:6px 0 26px}}
.sechead{{display:flex;justify-content:space-between;align-items:baseline;gap:16px;border-bottom:1px solid var(--line);padding-bottom:10px;margin-bottom:18px;flex-wrap:wrap}}
h2{{font-size:clamp(1.4rem,2.6vw,1.95rem)}}
.tag-inline{{font-family:var(--mono);font-size:.62rem;letter-spacing:.1em;text-transform:uppercase;color:var(--clay);vertical-align:middle;margin-left:6px}}
.sechead .note{{font-family:var(--mono);font-size:.7rem;text-transform:uppercase;letter-spacing:.1em;color:var(--muted)}}
.panel{{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:20px 23px;box-shadow:var(--shadow)}}
.grid3{{display:grid;grid-template-columns:repeat(3,1fr);gap:13px}}
.grid2{{display:grid;grid-template-columns:1fr 1fr;gap:14px}}
.verdict{{border-radius:13px;padding:17px 19px;border:1px solid var(--line);background:var(--card);border-top-width:4px}}
.v-sea{{border-top-color:var(--sea)}}.v-go{{border-top-color:var(--moss)}}
.v-test{{border-top-color:var(--amber)}}.v-kill{{border-top-color:var(--red)}}
.verdict .tag{{font-family:var(--mono);font-size:.65rem;letter-spacing:.1em;text-transform:uppercase;color:var(--muted);font-weight:700}}
.verdict h3{{font-size:1.02rem;margin:5px 0 7px}}
.verdict p{{margin:.35em 0;font-size:.88rem;color:var(--ink2)}}
.verdict .stat{{font-family:var(--mono);font-size:.75rem;color:var(--muted);margin-top:8px}}
table{{width:100%;border-collapse:collapse;background:var(--card)}}
.tablewrap{{border:1px solid var(--line);border-radius:13px;overflow:hidden;box-shadow:var(--shadow);margin-bottom:16px;overflow-x:auto}}
th,td{{text-align:left;padding:10px 12px;border-bottom:1px solid var(--line);font-size:.86rem;vertical-align:top}}
th{{font-size:.67rem;text-transform:uppercase;letter-spacing:.08em;color:var(--muted);background:#eef1e9;white-space:nowrap}}
tr:last-child td{{border-bottom:0}}
td.phone a{{font-family:var(--mono);font-size:.81rem;white-space:nowrap;text-decoration:none;background:#eaf0e2;padding:3px 7px;border-radius:5px;border:1px solid #d3ddc6}}
.pill{{display:inline-block;font-size:.64rem;font-family:var(--mono);text-transform:uppercase;letter-spacing:.06em;padding:2px 6px;border-radius:4px;border:1px solid}}
.p-yes{{color:var(--moss);border-color:#a9c3b6;background:#e6efe6}}
.p-no{{color:var(--red);border-color:#e0b7ab;background:#fbeae0}}
.thin{{color:var(--muted);font-size:.8rem}}
.caveat{{background:#fffbe8;border:1px solid #e6dca8;border-radius:12px;padding:16px 19px;font-size:.87rem;color:#5a4f27}}
.caveat p{{margin:.4em 0}}
.kill{{background:#fdf0e8;border:1px solid #eccdb9;border-radius:12px;padding:16px 19px;color:#5b3a2c;font-size:.9rem}}
.kill strong{{color:#8c3b1c}}
.kill + .kill{{margin-top:10px}}
.pivot{{background:#e6efe6;border:1px solid #a9c3b6;border-radius:13px;padding:18px 21px}}
.pivot h3{{color:var(--moss)}}
ul.calls{{margin:0 0 16px;padding-left:18px}}
ul.calls li{{font-size:.88rem;margin-bottom:5px}}
code{{font-family:var(--mono);font-size:.82rem;background:#e8ecd9;padding:1px 5px;border-radius:4px}}
footer{{border-top:1px solid var(--line);margin-top:26px;padding:22px 0 60px;font-size:.78rem;color:var(--muted)}}
@media(max-width:820px){{.grid3,.grid2{{grid-template-columns:1fr}}.wrap{{padding:0 16px}}header.hero{{padding:34px 0 16px}}}}
@media print{{.bar{{display:none}}body{{background:#fff}}.panel,.verdict,.tablewrap{{box-shadow:none;break-inside:avoid}}}}
</style>
</head>
<body>

<div class="bar"><div class="wrap">
  <a class="home" href="./">Boring Business Lab</a><span class="sep">/</span><span>Northeast Florida pack</span>
  <span class="spacer"></span>
  <a class="btn" href="./">← Pipeline</a>
</div></div>

<div class="wrap">
<header class="hero">
  <div class="wave"></div>
  <div class="kicker">10 trades · {total_cells} city × service cells · {total_ops} operator listings · $0.0135 spent</div>
  <h1>The goal is local. <em>The model isn't decided</em>.</h1>
  <p class="lede">The point of this lab is to help boring businesses in Northeast Florida. How, exactly, is still open — so this pack does not pitch a business. It maps which local trades are actually short of something, and what each one is short of. Four are thin. Six are served. One paid pull then corrected the free scan on the two things that decide everything: review depth and search demand.</p>
</header>

<section>
  <div class="sechead"><h2>What this lab is for now</h2><span class="note">read this before the tables</span></div>
  <div class="panel">
    <p style="margin:0 0 12px"><b>Goal:</b> help boring, capital-light service businesses in Northeast Florida — the ones with a truck, a phone and no ops layer. <b>Mechanism: undecided.</b> Three candidates survive the data, and they are not the same business:</p>
    <ol class="steps">
      <li><b>After-hours intake &amp; dispatch.</b> One local number that answers when the owner is elbow-deep, qualifies the job, quotes a range, routes to whoever can actually serve today. Fits the fringe well-pump and marine trades. Revenue: per dispatched job.</li>
      <li><b>Appointment setting for consultative trades.</b> Book the measure or quote, not the callback. Fits hurricane shutters. Revenue: per booked appointment.</li>
      <li><b>Availability brokering.</b> Know who is free this week and place the work — the Laredo lesson without the Laredo market. Fits boat detailing's one-person calendars and post-storm marine work. Revenue: per placement.</li>
    </ol>
    <p style="margin:12px 0 0"><b>What picks between them:</b> one week of calls, not more research. Any mechanism needs the same first evidence — an operator saying, in their own words, that they lost a bookable job and what it cost. The kill criteria at the bottom of this page are written to produce that answer or end the thread.</p>
  </div>
</section>

<hr class="rule">

<section>
  <div class="sechead"><h2>Ten trades, one table</h2><span class="note">free scan: {total_ops} listings · paid review pull on the four gaps</span></div>
  <div class="tablewrap"><table>
    <thead><tr><th>Trade</th><th>Core + fringe cells</th><th>Operators / cell</th><th>Median rating range</th><th>Median reviews</th><th>Verdict</th></tr></thead>
    <tbody>
{"".join(map_rows)}
    </tbody>
  </table></div>
  <p class="thin">Operators-per-cell is the min–max across core and fringe metros, not a total. Review depth is only measured for the four gap trades; the six rejections were not worth the extra $0.006.</p>
</section>

<hr class="rule">

<section>
  <div class="sechead"><h2>The paid data, and what it corrected</h2><span class="note">23 Oct · review counts + keyword volume · $0.0135</span></div>
  <div class="verdict v-kill" style="margin-bottom:14px">
    <div class="tag">Two corrections to the free scan</div>
    <h3>Review depth isn't the gap, and there is no search volume to arbitrage.</h3>
    <p><b>One:</b> well-pump operators in this metro are established — median <b>132</b> reviews — so "nobody can be found" was wrong there. The gap is geographic, at the edges of the metro. Boat detailing is the genuinely thin bench at <b>17</b>. <b>Two:</b> every Jacksonville-specific search term in all four trades sits at <b>10–90 searches a month</b>. A lead-volume product would have almost no leads to sell. That rules out the lead-site model for the whole metro and leaves relationship work.</p>
    <div class="stat">$0.0075 keyword pull + $0.0060 places pull</div>
  </div>
  <div class="grid2">
    <div class="tablewrap"><table>
      <thead><tr><th>Trade</th><th>Listings</th><th>Median reviews</th><th>Range</th><th>No site</th></tr></thead>
      <tbody>
{"".join(rev_rows)}
      </tbody>
    </table></div>
    <div class="tablewrap"><table>
      <thead><tr><th>Search term</th><th>Vol / mo (US)</th><th>CPC</th></tr></thead>
      <tbody>
{kw_html}
      </tbody>
    </table></div>
  </div>
  <p class="thin">Reviews: Google Places via serper, 7 calls, $0.001 each. Volume: Serpstat via treg, national monthly volume for geo-tagged phrases — there is no geo parameter, so treat these as an upper bound for the metro, not a local measurement. CPC is the commercial signal: $6.27 for "well pump repair jacksonville" says one click is worth buying; 70 a month says there are almost none. One keyword, <code>boat detailing jacksonville fl</code> at $62.91, is a single-term outlier and is excluded here.</p>
</section>

<hr class="rule">

<section>
  <div class="sechead"><h2>Who to call first, per gap</h2><span class="note">no-website and low-review operators first — they have the most to gain</span></div>
  <div class="grid2">
    <div class="panel">
      {"".join(CALL_BLOCKS[:2])}
    </div>
    <div class="panel">
      {"".join(CALL_BLOCKS[2:])}
    </div>
  </div>
  <p class="thin" style="margin-top:12px">Never open with "I can get you more leads." In a market this small that reads as spam and the call ends in ten seconds. Open with capacity and after-hours handling; price comes last, and only if the first answers sound open.</p>
</section>

<hr class="rule">
{"".join(gap_sections)}

<hr class="rule">

<section>
  <div class="sechead"><h2>What was rejected, and why</h2><span class="note">so it doesn't get re-litigated</span></div>
  <div class="tablewrap"><table>
    <thead><tr><th>Trade</th><th>Operators / metro</th><th>Median rating</th><th>Read</th></tr></thead>
    <tbody>
{"".join(f'      <tr><td><b>{esc(n)}</b></td><td>{esc(o)}</td><td>{esc(m)}</td><td class="thin">{esc(r)}</td></tr>' for n, o, m, r in REJECTS)}
    </tbody>
  </table></div>
</section>

<section>
  <div class="sechead"><h2>Kill criteria</h2><span class="note">one week of calls decides this</span></div>
  <div class="kill"><p><b>Well pump, fringe intake.</b> Kill if the edge operators say failures already reach a live person, or that their work comes entirely from builder and plumber relationships. <b>Keep</b> if two or more describe the same miss — call came in, nobody answered, customer rang the next name — and one names what a booked job is worth.</p></div>
  <div class="kill"><p><b>Boat detailing.</b> Kill if the mobile operators say the season is already full and they want no more. <b>Keep</b> if they lose work to whoever answers first, or want the off-season filled and will pay per booked detail.</p></div>
  <div class="kill"><p><b>Hurricane shutters.</b> Kill if the specialist says the measure calendar is booked through the season anyway. <b>Keep</b> if quote requests sit unanswered in the pre-storm rush — that is appointment setting, priced per booked measure.</p></div>
  <div class="kill"><p><b>Marine salvage.</b> Kill unless an operator confirms missed mobilisations they cannot cover. Seasonal, insurer-adjacent, and you would be brokering availability you do not control — the weakest of the four.</p></div>
</section>

<section>
  <div class="sechead"><h2>What would change these verdicts</h2><span class="note">the honest open list</span></div>
  <div class="pivot">
    <h3>Four things this pack does not know</h3>
    <ul class="calls" style="margin-bottom:0">
      <li><b>Whether the search volume is really that low.</b> Serpstat has no geo parameter. A local-pack impression pull or Google Ads geo report would settle it.</li>
      <li><b>Whether the fringe operators want the work.</b> Two listings in Orange Park could mean thin supply or no demand. Only the phone distinguishes them.</li>
      <li><b>What a booked job is worth</b> in each trade. That number sets the ceiling for any per-job fee, and no listing data contains it.</li>
      <li><b>Whether boat detailing's low review count means young businesses or bad operators.</b> Review depth alone cannot tell those apart.</li>
    </ul>
  </div>
</section>

<section>
  <div class="sechead"><h2>Method &amp; limits</h2><span class="note">what this is and is not</span></div>
  <div class="caveat">
    <p><b>Source:</b> Google Maps local list view via browser (free), {total_cells} queries across 10 services and 30 metros, 22–23 Oct 2026; plus a paid pull of {len(REVIEWS)} listings with review counts (Google Places, 7 calls) and 20 keywords (Serpstat). Total spend $0.0135.</p>
    <p><b>Regions.</b> "Core" is Duval, Jacksonville Beach, St Johns, Clay and Nassau. "Fringe" is the drivable NE Florida ring — Callahan, Yulee, Macclenny, Middleburg, Green Cove Springs, St Augustine, Amelia. Comparison metros outside the region (Gainesville, Ocala, Tallahassee, Brunswick, Waycross, Douglas, Valdosta, the Carolinas) were scanned only to test whether a finding was local or generic, and are not prospects.</p>
    <p><b>Review counts are partial.</b> Only the 53 listings in the paid pull carry them. The 508-listing grid does not, so the ten-trade table says "not pulled" rather than implying zero.</p>
    <p><b>Duplicates and drift.</b> The same operator appears across metros and sometimes under two numbers; gap tables dedupe by name, market counts do not. Repeated local-pack calls returned different counts and medians — treat every number as a snapshot that orients a call.</p>
    <p><b>This is not a market study.</b> No revenue, no lead volume, no capacity, no pricing. All of that requires the phone.</p>
    <p style="margin:0"><b>Raw data:</b> <code>data/nefl-supply-scan.csv</code> ({total_ops} listings) · <code>data/nefl-supply-markets.csv</code> ({total_cells} cells) · <code>data/nefl-review-counts.csv</code> · <code>data/nefl-keyword-demand.csv</code> · <code>data/nefl-supply-scan.json</code> · rebuild with <code>data/build_pack.py</code>.</p>
  </div>
</section>

<footer>Boring Business Lab · Northeast Florida pack · {total_ops} listings, {total_cells} cells, $0.0135 of data · the goal is local, the model is still open.</footer>
</div>
</body>
</html>
"""

path = os.path.join(ROOT, "validation-jax.html")
open(path, "w").write(HTML)
print("wrote", path, len(HTML), "chars")
print("gap sections:", len(gap_sections), "call blocks:", len(CALL_BLOCKS), "map rows:", len(map_rows))
