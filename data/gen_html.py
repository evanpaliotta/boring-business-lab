#!/usr/bin/env python3
"""Generate validation-nefl-services.html from nefl-supply-scan.json.

Single self-contained page, no build step, no external assets. Same visual system as
validation-jax.html so the pack reads as one family.
"""
import json, os, html, statistics as st

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

with open(os.path.join(HERE, "nefl-supply-scan.json")) as f:
    D = json.load(f)

OPS = []
import csv
with open(os.path.join(HERE, "nefl-supply-scan.csv")) as f:
    OPS = list(csv.DictReader(f))

GAP_ORDER = ["well pump repair", "boat detailing", "hurricane shutter installation", "marine salvage / recovery"]

# Paid data (added 23 Oct, ~$0.014 of treg credit): review depth per operator and local
# keyword demand. Optional - the page still builds without them.
REVIEWS, KW = [], []
_rp = os.path.join(HERE, "nefl-review-counts.csv")
if os.path.exists(_rp):
    with open(_rp) as f:
        REVIEWS = list(csv.DictReader(f))
_kp = os.path.join(HERE, "nefl-keyword-demand.csv")
if os.path.exists(_kp):
    with open(_kp) as f:
        KW = list(csv.DictReader(f))


def review_summary(svc):
    rs = [r for r in REVIEWS if r["service"] == svc]
    rc = sorted(int(r["review_count"]) for r in rs if r["review_count"])
    if not rc:
        return None
    return {"n": len(rs), "median": int(st.median(rc)), "lo": rc[0], "hi": rc[-1]}


def kw_for(terms):
    out = []
    for r in KW:
        if r["keyword"] in terms:
            out.append(r)
    return out

SAT_ORDER = ["septic tank pumping", "dock / marine construction", "porta potty rental",
             "generator repair", "land clearing", "mobile mechanic"]

GAP_META = {
 "well pump repair": dict(
   title="Well pump repair", tag="Deepest gap",
   stat="180 listings · 29 cells",
   line="Orange Park returns 2 listings. Macclenny's local options rate 3.0–3.2. Across the core and fringe, a large share of the operators that do exist have no website at all — and several advertise 24-hour service, which in a two-truck shop means a phone nobody is watching.",
   sell="Answer + triage + dispatch. Emergency-shaped, low ticket, high repeat.",
   revread="Established incumbents exist in the metro — 928 reviews at the top. The gap is geographic (Orange Park, Macclenny, Callahan), not metro-wide, and 6 of 20 listings have no website.",
   why="Rural and semi-rural customers have no alternative but a phone call, and the well either works or the house is dry."),
 "boat detailing": dict(
   title="Boat detailing", tag="Clearest sellable gap",
   stat="160 listings · 26 cells",
   line="The beaches are saturated — every operator on the coast is 5.0-rated and competing on polish. The river metros and Amelia/Yulee are not: what shows up there is mostly car detailers with a boat line, plus a couple of genuinely boat-only mobile operators.",
   sell="Mobile, no shop, no inventory. Owner-operated, so a scheduling/intake layer is the constraint, not demand.",
   revread="Thinnest bench of the four by a wide margin — median 17 reviews. Half the local-pack results are car detailers; the boat-only specialists are single-operator mobile businesses.",
   why="Boats are where the money is and the work is mobile by nature — the operator drives to the lift, not the other way round."),
 "hurricane shutter installation": dict(
   title="Hurricane shutter installation", tag="Thinnest specialist bench",
   stat="147 listings · 25 cells",
   line="Exactly one true shutter specialist serves the whole core metro. Everything else in the local pack is a blinds store or a window installer. Orange Park returns two results total. This is a consultative, quote-then-schedule sale.",
   sell="Qualified appointment setting — book the measure/quote, not the callback.",
   revread="Bimodal: a 1,000-review incumbent next to entrants with 2–12 reviews. The spread is the opening, not the median.",
   why="High ticket, insurance-adjacent, and the buyer is a homeowner who fills a form or calls once and then waits."),
 "marine salvage / recovery": dict(
   title="Marine salvage &amp; recovery", tag="Real gap, storm-gated",
   stat="14 listings · 2 cells",
   line="No dedicated marine salvage operator appears in any metro scanned — only dive shops, tow services and boat yards. The availability gap is genuine. The catch is that it only matters during a named storm.",
   sell="Surge brokering: who can actually mobilise this week.",
   revread="Most players sit at 2–12 reviews and the category is effectively unbuilt locally — which is also why there is no proof that anyone pays for it.",
   why="After a storm the scarce resource is a crew with a barge, not a phone number that ranks."),
}


def esc(s):
    return html.escape(str(s)) if s is not None else ""


def pct_webless(rows):
    if not rows:
        return 0
    return round(100.0 * sum(1 for r in rows if r["website"] == "no") / len(rows))


def op_table(service):
    rows = [r for r in OPS if r["service"] == service and r["region"] in ("core", "fringe")]
    by = {}
    for r in rows:
        k = r["operator"].lower()
        e = by.setdefault(k, {"name": r["operator"], "phone": r["phone"],
                              "rating": r["rating"], "website": r["website"],
                              "metros": []})
        if r["metro"] not in e["metros"]:
            e["metros"].append(r["metro"])
        if r["website"] == "yes":
            e["website"] = "yes"
        if r["phone"] and not e["phone"]:
            e["phone"] = r["phone"]
    items = list(by.values())

    def key(x):
        try:
            r = float(x["rating"])
        except (TypeError, ValueError):
            r = -1
        return (-r, x["name"].lower())

    items.sort(key=key)
    out = []
    for it in items:
        web = ('<span class="pill p-yes">yes</span>' if it["website"] == "yes"
               else '<span class="pill p-no">no</span>')
        rating = it["rating"] if it["rating"] else "—"
        phone = (f'<a href="tel:+1{esc("".join(c for c in it["phone"] if c.isdigit()))}">{esc(it["phone"])}</a>'
                 if it["phone"] else "—")
        metros = ", ".join(esc(m.replace(" FL", "").replace(" GA", "").replace(" NC", "").replace(" SC", ""))
                          for m in it["metros"])
        out.append(f'      <tr><td>{esc(it["name"])}</td><td class="phone">{phone}</td>'
                   f'<td>{esc(rating)}</td><td>{web}</td><td class="thin">{metros}</td></tr>')
    return "\n".join(out), len(items)


def market_table(service):
    rows = [m for m in D["markets"] if m["service"] == service]
    order = {"core": 0, "fringe": 1, "out": 2}
    rows.sort(key=lambda m: (order[m["region"]], m["metro"]))
    out = []
    for m in rows:
        b = m.get("basis", "")
        out.append(f'      <tr><td><b>{esc(m["metro"])}</b></td>'
                   f'<td><span class="pill p-yes">{esc(m["region"])}</span></td>'
                   f'<td>{m["operators"]}</td><td>{m["median_rating"] if m["median_rating"] is not None else "—"}</td>'
                   f'<td>{m["no_website"] if m["no_website"] is not None else "—"}</td>'
                   f'<td class="thin">{esc(m.get("note","")[:90])}</td></tr>')
    return "\n".join(out)


gap_sections = []
for svc in GAP_ORDER:
    meta = GAP_META[svc]
    a = D["assessment"][svc]
    tbl, n = op_table(svc)
    rs = review_summary(svc)
    if rs:
        rev_line = (f'<p class="thin" style="margin:10px 0 0"><b>Review depth (paid Places pull):</b> '
                    f'{rs["n"]} listings, median <b>{rs["median"]}</b> reviews, range {rs["lo"]}–{rs["hi"]}. '
                    f'{meta.get("revread","")}</p>')
    else:
        rev_line = ""
    gap_sections.append(f"""
<section>
  <div class="sechead"><h2>{meta['title']} <span class="tag-inline">{meta['tag']}</span></h2>
    <span class="note">{meta['stat']}</span></div>
  <div class="panel" style="margin-bottom:14px">
    <p style="margin:0 0 10px">{meta['line']}</p>
    <p style="margin:0;font-size:.88rem;color:var(--ink2)"><b>What is sellable here:</b> {meta['sell']}</p>
    {rev_line}
  </div>
  <div class="tablewrap"><table>
    <thead><tr><th>Operator (deduped)</th><th>Phone</th><th>Rating</th><th>Web</th><th>Seen in</th></tr></thead>
    <tbody>
{tbl}
    </tbody>
  </table></div>
  <p class="thin">{n} unique operators across core + fringe metros. Rating and website presence as displayed by Google Maps on 22–23 Oct 2026.</p>
</section>""")

# ---- paid-data section (review counts + local keyword demand) ----
rev_rows = []
for svc, label in [("well pump repair", "Well pump repair"), ("boat detailing", "Boat detailing"),
                   ("hurricane shutter installation", "Hurricane shutters"), ("marine salvage", "Marine salvage")]:
    s = review_summary(svc)
    if not s:
        continue
    cell = [m for m in D["markets"] if m["service"] == svc and m["region"] == "core"]
    noweb = sum(int(r["review_count"] is not None and (r["website"] == "no")) for r in REVIEWS if r["service"] == svc)
    rev_rows.append(f'      <tr><td><b>{label}</b></td><td>{s["n"]}</td>'
                    f'<td><b>{s["median"]}</b></td><td>{s["lo"]}–{s["hi"]}</td><td>{noweb}</td></tr>')

JAX_KW = ["well pump repair jacksonville fl", "well pump repair jacksonville", "well pump service jacksonville fl",
          "well drilling jacksonville fl", "boat detailing jacksonville fl", "boat detailing jacksonville",
          "mobile boat detailing jacksonville", "hurricane shutters jacksonville fl",
          "hurricane shutters jacksonville", "hurricane shutter installation jacksonville",
          "storm shutters jacksonville fl", "marine salvage jacksonville fl", "boat salvage jacksonville",
          "sunken boat removal jacksonville", "boat recovery jacksonville fl"]
kw_rows = []
for r in KW:
    if r["keyword"] not in JAX_KW:
        continue
    vol = int(r["volume_monthly_national"] or 0)
    cpc = float(r["cpc_usd"] or 0)
    flag = ' <span class="pill p-no">outlier</span>' if cpc > 20 else ""
    kw_rows.append(f'      <tr><td>{esc(r["keyword"])}</td><td>{vol}</td>'
                   f'<td>${cpc:.2f}{flag}</td>'
                   f'<td>{"yes" if r["has_local_pack"] == "True" else "no"}</td></tr>')
kw_rows.sort(key=lambda s: int(s.split("<td>")[2].split("</td>")[0]))

PAID_SECTION = f"""
<hr class="rule">

<section>
  <div class="sechead"><h2>The paid data, and what it changed</h2><span class="note">pulled 23 Oct · review counts + keyword volume · $0.014 spent</span></div>
  <div class="verdict v-kill" style="margin-bottom:14px">
    <div class="tag">Correction to the free scan</div>
    <h3>Review depth is not the gap — and local search demand is too thin to arbitrage.</h3>
    <p>Two findings, both against the earlier read. <b>One:</b> Jacksonville's well-pump operators are established, not invisible — median <b>132</b> reviews. <b>Two:</b> every Jacksonville-specific search term in all four trades sits between <b>10 and 70 searches a month</b>. There is no volume here to sell as leads. What exists is a relationship-and-availability gap, which is a phone business, not a search-arbitrage business.</p>
    <div class="stat">Spend: $0.0075 keyword pull + $0.0060 places pull = $0.0135</div>
  </div>
  <div class="tablewrap"><table>
    <thead><tr><th>Trade</th><th>Listings pulled</th><th>Median reviews</th><th>Range</th><th>No website</th></tr></thead>
    <tbody>
{"".join(rev_rows)}
    </tbody>
  </table></div>
  <p class="thin">Source: Google Places via serper ($0.001/call), 7 queries across Jacksonville and Orange Park. Median review count is the discriminator the free list view could not show: 17 (boat detailing) is thin, 132 (well pump) is an established trade.</p>

  <div class="tablewrap"><table>
    <thead><tr><th>Jacksonville search term</th><th>Volume / mo (US)</th><th>CPC</th><th>Local pack</th></tr></thead>
    <tbody>
{"".join(kw_rows)}
    </tbody>
  </table></div>
  <p class="thin">Source: Serpstat via treg, national monthly volume (no geo parameter exists — these are US-wide volumes for geo-tagged phrases, so treat them as an upper bound for the metro, not a local measurement). CPC is the commercial signal: $6.27 for "well pump repair jacksonville" and $4.17 for shutters says the clicks are worth buying; 70 searches a month says there are not many of them.</p>
</section>
"""


sat_rows = []
for svc in SAT_ORDER:
    a = D["assessment"][svc]
    cells = [m for m in D["markets"] if m["service"] == svc and m["region"] in ("core", "fringe")]
    if not cells:
        continue
    ops = [m["operators"] for m in cells]
    meds = [m["median_rating"] for m in cells if m["median_rating"] is not None]
    sat_rows.append(f'      <tr><td><b>{esc(svc.title())}</b></td><td>{min(ops)}–{max(ops)}</td>'
                    f'<td>{round(min(meds),1) if meds else "—"}–{round(max(meds),1) if meds else "—"}</td>'
                    f'<td>{esc(a["verdict"])}</td><td class="thin">{esc(a["why"][:150])}</td></tr>')

total_ops = len(OPS)
total_cells = len(D["markets"])

HTML = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow">
<meta name="color-scheme" content="light">
<title>NE Florida Supply Scan — Boring Business Lab</title>
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
h1{{font-size:clamp(2.2rem,5vw,3.8rem);line-height:1.02;margin:14px 0 18px;max-width:22ch}}
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
.verdict{{border-radius:13px;padding:17px 19px;border:1px solid var(--line);background:var(--card);border-top-width:4px}}
.v-sea{{border-top-color:var(--sea)}}.v-go{{border-top-color:var(--moss)}}
.v-test{{border-top-color:var(--amber)}}.v-kill{{border-top-color:var(--red)}}
.verdict .tag{{font-family:var(--mono);font-size:.65rem;letter-spacing:.1em;text-transform:uppercase;color:var(--muted);font-weight:700}}
.verdict h3{{font-size:1.02rem;margin:5px 0 7px}}
.verdict p{{margin:.35em 0;font-size:.87rem;color:var(--ink2)}}
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
code{{font-family:var(--mono);font-size:.82rem;background:#e8ecd9;padding:1px 5px;border-radius:4px}}
footer{{border-top:1px solid var(--line);margin-top:26px;padding:22px 0 60px;font-size:.78rem;color:var(--muted)}}
@media(max-width:820px){{.grid3{{grid-template-columns:1fr}}.wrap{{padding:0 16px}}header.hero{{padding:34px 0 16px}}}}
@media print{{.bar{{display:none}}body{{background:#fff}}.panel,.verdict,.tablewrap{{box-shadow:none;break-inside:avoid}}}}
</style>
</head>
<body>

<div class="bar"><div class="wrap">
  <a class="home" href="./">Boring Business Lab</a><span class="sep">/</span><span>Supply scan</span>
  <span class="spacer"></span>
  <a class="btn" href="./">← Pipeline</a>
  <a class="btn" href="validation-jax.html">North Florida pack</a>
  <a class="btn" href="validation.html">Laredo pack</a>
</div></div>

<div class="wrap">
<header class="hero">
  <div class="wave"></div>
  <div class="kicker">10 services · {total_cells} city × service cells · {total_ops} operator listings</div>
  <h1>Supply, measured. <em>Not demand</em>.</h1>
  <p class="lede">Same method as the Laredo pack, pointed at your own region and at ten trades instead of four. The question this answers: <b>where is a local service so thin that a person with a phone can be useful?</b> Four trades qualify. Six do not, and the six matter as much as the four — they are the ones that would have wasted a month.</p>
</header>

<section>
  <div class="sechead"><h2>What the scan found</h2><span class="note">captured 22–23 Oct 2026 · Google Maps list view · $0</span></div>
  <div class="grid3">
    <div class="verdict v-go"><div class="tag">Thin supply</div><h3>4 of 10 trades</h3><p>Well pump repair, boat detailing, hurricane shutters and marine salvage all show fewer operators than the surrounding metros support — and the ones present often have no website.</p><div class="stat">see the gap tables below</div></div>
    <div class="verdict v-kill"><div class="tag">Already served</div><h3>6 of 10 trades</h3><p>Septic, dock building, porta potty, generators, land clearing and mobile mechanics have 5–11 competitors per metro at 4.3–5.0. Any lead product there competes with people who already rank.</p><div class="stat">documented so you don't revisit</div></div>
    <div class="verdict v-test"><div class="tag">Now measured</div><h3>Review depth, not review gaps</h3><p>The paid pull closed the blind spot: median <b>17</b> reviews for boat detailing operators, <b>132</b> for well pump. Thin review depth is a real signal in two trades, and an illusion in the other two.</p><div class="stat">also: 10–70 Jacksonville searches / month</div></div>
  </div>
</section>

<hr class="rule">

<section>
  <div class="sechead"><h2>Where supply is thin</h2><span class="note">ranked by how sellable the gap is</span></div>
  <div class="tablewrap"><table>
    <thead><tr><th>Service</th><th>Core + fringe cells</th><th>Verdict</th><th>Why it reads as a gap</th></tr></thead>
    <tbody>
      <tr><td><b>Well pump repair</b></td><td>12</td><td><span class="pill p-yes">gap</span></td><td class="thin">Orange Park: 2 listings. Macclenny: 3.0–3.2 ratings. Many core/fringe operators have no site. 24-hour flags on two-truck shops.</td></tr>
      <tr><td><b>Boat detailing</b></td><td>12</td><td><span class="pill p-yes">gap</span></td><td class="thin">Beaches saturated at 5.0; river metros (Fleming Island, Orange Park, Middleburg) show car detailers with a boat line instead of boat specialists.</td></tr>
      <tr><td><b>Hurricane shutters</b></td><td>12</td><td><span class="pill p-yes">gap</span></td><td class="thin">One true specialist for the whole core metro. Orange Park: 2 results. Everything else is blinds stores.</td></tr>
      <tr><td><b>Marine salvage</b></td><td>2</td><td><span class="pill p-yes">thin</span></td><td class="thin">No dedicated salvage operator in any metro scanned. Genuine, but storm-gated — a burst business.</td></tr>
    </tbody>
  </table></div>
  <p class="thin">"Gap" here is a supply statement, not a demand statement. It does not say anyone wants to pay for intake — that is the phone call, and it is still unmade.</p>
</section>

{PAID_SECTION}

<hr class="rule">
{"".join(gap_sections)}

<hr class="rule">

<section>
  <div class="sechead"><h2>Where supply is already there</h2><span class="note">the six that would have wasted a month</span></div>
  <div class="tablewrap"><table>
    <thead><tr><th>Service</th><th>Operators per metro</th><th>Median rating</th><th>Verdict</th><th>Read</th></tr></thead>
    <tbody>
{"".join(sat_rows)}
    </tbody>
  </table></div>
  <p class="thin">Porta potty is the interesting rejection: listing density is high but a large share are unrated, no-website, city-name shells — SEO churn rather than real capacity. The established operators (Floaters, Premier, Fortis, Maxline, Carefree) already own the search result.</p>
</section>

<hr class="rule">

<section>
  <div class="sechead"><h2>Kill criteria</h2><span class="note">decide before dialling — one per gap</span></div>
  <div class="kill"><p><b>Well pump repair.</b> Kill if the operators say the pump failure calls already reach a live person after hours, or if the ones with no website tell you they get all their work from a builder/plumber relationship and want no more. <b>Keep</b> if two or more describe the same failure (call came in, nobody answered, customer called the next name) and one names what a booked job is worth.</p></div>
  <div class="kill"><p><b>Boat detailing.</b> Kill if the mobile operators say their calendar is full in season and empty off-season with no interest in filling it. <b>Keep</b> if they describe losing jobs to whoever answers first, or want the off-season filled and will pay per booked detail.</p></div>
  <div class="kill"><p><b>Hurricane shutters.</b> Kill if the one specialist says the measure/quote calendar is booked through the season anyway. <b>Keep</b> if they say quote requests sit unanswered during the pre-storm rush — that is appointment setting, priced per booked measure.</p></div>
  <div class="kill"><p><b>Marine salvage.</b> Kill unless an operator confirms the surge creates missed mobilisations they cannot cover. This is the weakest of the four: seasonal, insurer-adjacent, and you would be brokering availability you do not control.</p></div>
</section>

<section>
  <div class="sechead"><h2>Method &amp; limits</h2><span class="note">what this is and is not</span></div>
  <div class="caveat">
    <p><b>Source:</b> Google Maps local list view via browser, {total_cells} queries across 10 services and 30 metros, captured 22–23 Oct 2026. Names, phones, ratings and website presence as displayed. Zero data-provider spend.</p>
    <p><b>Review counts were added on 23 Oct.</b> The first pass used the free list view, which does not expose review depth; a paid Places pull (7 queries, $0.006) and a keyword pull (20 terms, $0.0075) now back the review and demand tables. Every raw response is saved as <code>data/raw_places_*.json</code> and <code>data/kw_raw.txt</code> so nothing has to be re-bought.</p>
    <p><b>Regions matter.</b> "Core" is Duval, Jacksonville Beach, St Johns, Clay and Nassau — your backyard. "Fringe" is the drivable NE Florida ring. "Out" cells (Gainesville, Ocala, Tallahassee, Brunswick, Waynesville/Waycross, the Carolinas) exist as comparison only and are <b>not</b> prospects.</p>
    <p><b>Duplicates.</b> The same operator appears across metros and occasionally under two phone numbers. Gap tables are deduped by name; market counts are not.</p>
    <p><b>Samples drift.</b> Repeated local-pack calls for the same query returned different counts and medians. Treat every number as a snapshot that orients a phone call, not a measurement.</p>
    <p style="margin:0"><b>Raw data:</b> <code>data/nefl-supply-scan.csv</code> (one row per operator listing), <code>data/nefl-supply-markets.csv</code> (market aggregates), <code>data/nefl-supply-scan.json</code> (both + verdicts), rebuildable with <code>data/build_scan.py</code>.</p>
  </div>
</section>

<footer>Boring Business Lab · NE Florida supply scan · {total_ops} operator listings across {total_cells} city × service cells · no idea scored, nothing bought, nothing built.</footer>
</div>
</body>
</html>
"""

path = os.path.join(ROOT, "validation-nefl-services.html")
with open(path, "w") as f:
    f.write(HTML)
print("wrote", path, len(HTML), "chars")
print("gap sections:", len(gap_sections), "saturated rows:", len(sat_rows))
