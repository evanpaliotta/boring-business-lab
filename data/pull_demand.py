#!/usr/bin/env python3
"""Pull the demand leg (keyword volume/CPC) + review counts (Places ratingCount) for the
four gap trades, and merge them into the scan dataset.

Costs: serpstat keyword volume ~$0.0005/keyword returned, serper places $0.001/call.
Every call is saved raw next to this script so nothing has to be re-bought.
"""
import json, os, subprocess, csv, statistics as st

HERE = os.path.dirname(os.path.abspath(__file__))

PLACES_QUERIES = [
    ("well pump repair", "Jacksonville, FL", "core", "well pump repair in Jacksonville, FL", None),
    ("well pump repair", "Orange Park, FL", "core", "well pump repair in Orange Park, FL", None),
    ("boat detailing", "Jacksonville, FL", "core", "boat detailing in Jacksonville, FL", None),
    ("boat detailing", "Fleming Island, FL", "core", "boat detailing in Fleming Island, FL", None),
    ("hurricane shutter installation", "Jacksonville, FL", "core", "hurricane shutter installation in Jacksonville, FL", None),
    ("hurricane shutter installation", "Orange Park, FL", "core", "hurricane shutter installation in Orange Park, FL", None),
    ("marine salvage", "Jacksonville, FL", "core", "marine salvage in Jacksonville, FL", None),
]


def first_object(text):
    i = text.index("{")
    d, _ = json.JSONDecoder().raw_decode(text[i:])
    return d


def call_places(q, slug):
    path = os.path.join(HERE, f"raw_places_{slug}.json")
    if os.path.exists(path):
        return json.load(open(path)), 0.0
    body = json.dumps({"q": q, "gl": "us", "hl": "en"})
    out = subprocess.run(["treg", "call", "serper.google.serp.places", "--data", body],
                         capture_output=True, text=True).stdout
    d = first_object(out)
    json.dump(d, open(path, "w"), indent=1)
    return d, 0.001


# 1. Places: review counts per operator
rows, spend = [], 0.0
for svc, metro, region, q, _ in PLACES_QUERIES:
    slug = (svc + "_" + metro).lower().replace(" ", "-").replace(",", "").replace(".", "")
    d, c = call_places(q, slug)
    spend += c
    for p in d.get("places", []):
        rows.append({
            "service": svc, "metro": metro, "region": region,
            "position": p.get("position"),
            "operator": p.get("title", ""),
            "phone": p.get("phoneNumber", ""),
            "rating": p.get("rating"),
            "review_count": p.get("ratingCount"),
            "website": "yes" if p.get("website") else "no",
            "category": p.get("category", ""),
            "address": p.get("address", ""),
        })

with open(os.path.join(HERE, "nefl-review-counts.csv"), "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    w.writeheader()
    w.writerows(rows)

# 2. Keywords
kw = []
raw = open(os.path.join(HERE, "kw_raw.txt")).read()
for r in first_object(raw)["result"]["data"]:
    kw.append({"keyword": r["keyword"],
               "volume_monthly_national": r.get("region_queries_count"),
               "cpc_usd": round(float(r.get("cost") or 0), 2),
               "competition": r.get("concurrency"),
               "difficulty": r.get("difficulty"),
               "found_results": r.get("found_results"),
               "has_local_pack": "local_pack" in (r.get("types") or [])})
kw.sort(key=lambda r: -(r["volume_monthly_national"] or 0))
with open(os.path.join(HERE, "nefl-keyword-demand.csv"), "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(kw[0].keys()))
    w.writeheader()
    w.writerows(kw)

# 3. Summary per service
def per_service(svc):
    rs = [r for r in rows if r["service"] == svc]
    rc = [r["review_count"] for r in rs if r["review_count"]]
    rt = [r["rating"] for r in rs if r["rating"]]
    return {
        "cells": len(set(r["metro"] for r in rs)),
        "listings": len(rs),
        "median_reviews": int(st.median(rc)) if rc else None,
        "min_reviews": min(rc) if rc else None,
        "max_reviews": max(rc) if rc else None,
        "median_rating": round(st.median(rt), 2) if rt else None,
        "no_website": sum(1 for r in rs if r["website"] == "no"),
    }

print(f"places spend: ${spend:.4f}  (new calls only; cached raw reused)")
print(f"review rows: {len(rows)}   keyword rows: {len(kw)}\n")
print(f"{'service':32s} {'cells':>5s} {'listings':>8s} {'med rev':>8s} {'range':>12s} {'med rtg':>8s} {'noweb':>6s}")
for svc in ["well pump repair", "boat detailing", "hurricane shutter installation", "marine salvage"]:
    s = per_service(svc)
    print(f"{svc:32s} {s['cells']:5d} {s['listings']:8d} {str(s['median_reviews']):>8s} "
          f"{str(s['min_reviews'])+'-'+str(s['max_reviews']):>12s} {str(s['median_rating']):>8s} {s['no_website']:6d}")

print("\nkeyword demand (national monthly, serpstat):")
for r in kw[:20]:
    print(f"  {r['keyword']:44s} vol={str(r['volume_monthly_national']):>5s} cpc=${r['cpc_usd']:>5.2f} "
          f"local_pack={'Y' if r['has_local_pack'] else '-'}")
