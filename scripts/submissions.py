#!/usr/bin/env python3
"""List RentHumanoid form submissions from Netlify, or export them to CSV.

Needs NETLIFY_AUTH_TOKEN in the environment or in .env (never committed).
  python3 scripts/submissions.py                 # print all forms
  python3 scripts/submissions.py rental-request --csv requests.csv
"""
import csv, json, os, sys, urllib.request

SITE = "2b509499-449d-4a94-8f78-b69316a371c4"  # renthumanoid on Netlify
SKIP = {"ip", "user_agent", "referrer"}

def token():
    if os.environ.get("NETLIFY_AUTH_TOKEN"):
        return os.environ["NETLIFY_AUTH_TOKEN"]
    env = os.path.join(os.path.dirname(__file__), "..", ".env")
    for line in open(env):
        if line.startswith("NETLIFY_AUTH_TOKEN="):
            return line.split("=", 1)[1].strip().strip('"\'')
    sys.exit("NETLIFY_AUTH_TOKEN not set")

def get(path):
    req = urllib.request.Request("https://api.netlify.com/api/v1" + path, headers={"Authorization": "Bearer " + token()})
    return json.load(urllib.request.urlopen(req))

def main():
    args = sys.argv[1:]
    out = args[args.index("--csv") + 1] if "--csv" in args else None
    only = next((a for a in args if not a.startswith("--") and a != out), None)
    for form in get(f"/sites/{SITE}/forms"):
        if only and form["name"] != only:
            continue
        subs = get(f"/forms/{form['id']}/submissions?per_page=100")
        print(f"== {form['name']} ({len(subs)})")
        rows = [{"submitted": s["created_at"][:16].replace("T", " "), **{k: v for k, v in s["data"].items() if k not in SKIP}} for s in subs]
        for r in rows:
            print("  " + " | ".join(f"{k}={v}" for k, v in r.items() if v))
        if out:
            keys = list(dict.fromkeys(k for r in rows for k in r))
            with open(out, "w", newline="") as f:
                w = csv.DictWriter(f, fieldnames=keys); w.writeheader(); w.writerows(rows)
            print(f"wrote {out}")

main()
