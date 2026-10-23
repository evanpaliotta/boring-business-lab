#!/usr/bin/env python3
"""Merge the paid pulls (review counts + keyword demand) into nefl-supply-scan.json.

Run after build_scan.py and pull_demand.py:
    python3 build_scan.py && python3 pull_demand.py && python3 merge_paid.py && python3 build_pack.py
"""
import json, os, csv, statistics as st

HERE = os.path.dirname(os.path.abspath(__file__))

D = json.load(open(os.path.join(HERE, "nefl-supply-scan.json")))
rev = list(csv.DictReader(open(os.path.join(HERE, "nefl-review-counts.csv"))))
kw = list(csv.DictReader(open(os.path.join(HERE, "nefl-keyword-demand.csv"))))

for r in rev:
    r["review_count"] = int(r["review_count"]) if r["review_count"] else None
    r["rating"] = float(r["rating"]) if r["rating"] else None
    r["position"] = int(r["position"])
for k in kw:
    k["volume_monthly_national"] = int(k["volume_monthly_national"] or 0)
    k["cpc_usd"] = float(k["cpc_usd"])
    k["has_local_pack"] = k["has_local_pack"] == "True"

depth = {}
for s in {r["service"] for r in rev}:
    rc = [r["review_count"] for r in rev if r["service"] == s and r["review_count"]]
    depth[s] = {"listings": len([r for r in rev if r["service"] == s]),
                "median_reviews": int(st.median(rc)), "min": min(rc), "max": max(rc)}

D["paid_pull"] = {
    "date": "2026-10-23",
    "cost_usd": 0.0135,
    "what": "review counts (Google Places via serper, 7 calls) + keyword volume/CPC (Serpstat, 20 terms)",
    "review_depth": depth,
    "corrects": [
        "Well pump has established incumbents (median 132 reviews); the gap is geographic, not metro-wide.",
        "Boat detailing has the thinnest bench (median 17 reviews).",
        "Jacksonville-specific search demand is 10-70/mo in all four trades, so a lead-volume product has no supply of leads.",
        "CPC is high where volume is low ($6.27 well pump repair jacksonville, $4.17 shutters) - commercial value per click, not volume.",
    ],
    "review_rows": rev,
    "keyword_rows": kw,
}
json.dump(D, open(os.path.join(HERE, "nefl-supply-scan.json"), "w"), indent=1)
print("merged paid pull:", json.dumps(depth))
