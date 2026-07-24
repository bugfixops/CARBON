"""Natural, app-agnostic Android bug crawl with a LENIENT 6-complex-category
classifier. Resumes from the existing raw_random_bugs.jsonl, crawls more repos
(no gesture terms in the discovery query), and regenerates the CSV.

Usage:
  python crawl_lenient.py --dryrun           # re-classify existing raw only
  python crawl_lenient.py --target 4000 --min-per 3 --max-repos 1200
"""
from __future__ import annotations
import argparse, json, os, re, sys, time
from collections import Counter, OrderedDict
from pathlib import Path
import requests
from dotenv import load_dotenv

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
load_dotenv(ROOT / ".env"); load_dotenv(ROOT / "BugCrawler" / ".env")
GH = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
H = {"Authorization": f"token {GH}", "Accept": "application/vnd.github+json",
     "X-GitHub-Api-Version": "2022-11-28", "User-Agent": "carbon-prevalence"}

RAW = HERE / "raw_random_bugs.jsonl"
CSV = HERE / "random_gesture_bugs.csv"
PROG = HERE / ".random_progress.json"

BUG_LABELS = ["bug", "Bug", "crash", "Crash", "defect", "Defect", "type: bug",
              "type:bug", "Type: Bug", "kind/bug", "bug-report", "confirmed bug",
              "Issue-Bug", "t:bug", "C-bug"]

COMPLEX = ["pinch_zoom", "quick_tap", "drag_and_drop", "swipe_region", "picker_scroll", "multi_touch"]
SIMPLE = ["scroll", "swipe", "orientation", "long_press", "double_tap"]

# LENIENT patterns (complex first; priority decides ties).
PATTERNS = [
    ("pinch_zoom",   re.compile(r"\b(pinch|pinch[- ]?to[- ]?zoom|zoom\s*(in|out)|two[- ]?finger\s*zoom)\b", re.I)),
    ("quick_tap",    re.compile(r"\b(tap(p?ing|ped)?\s+(twice|repeatedly|rapidly|multiple\s+times|fast|several\s+times|in\s+quick)|rapid(ly)?\s+tap|quick(ly)?\s+tap|spam(ming)?\s+(tap|click|the\s+button)|tap(p?ing|ped)?\s+too\s+(fast|quick)|click(ing|ed)?\s+(rapidly|too\s+fast)|consecutive\s+tap|in\s+rapid\s+succession|double[- ]?tap\s+(fast|quick))\b", re.I)),
    ("drag_and_drop",re.compile(r"\b(drag\s*(and|&)\s*drop(?!\s+(files|image|video|\w+\s+here|the\s+whole))|drag(ged|ging)?\s+(it|the|a|an|to|from|into)|reorder\w*\s+\w*\s*drag)\b", re.I)),
    ("swipe_region", re.compile(r"\b(edge[- ]?swipe|swipe\s+from\s+(the\s+)?(edge|left|right|screen)|seek\s*bar|seekbar|drag\s+(the\s+)?(slider|handle|seek|thumb|progress)|scrub(bing|bed)?|swipe\s+(at|on|over|across)\s+(a\s+)?(specific|exact|certain|particular))\b", re.I)),
    ("picker_scroll",re.compile(r"\b(number\s*picker|numberpicker|date\s*picker|time\s*picker|datepicker|timepicker|scroll\s*wheel|wheel\s*picker|picker\s+(wheel|dial|scroll|spinner)|scroll.*picker|spin(ner)?\s+(wheel|to\s+select))\b", re.I)),
    ("multi_touch",  re.compile(r"\b(multi[- ]?touch|multitouch|two[- ]?finger|three[- ]?finger|two\s+fingers|three\s+fingers|rotate\s+(the\s+)?(map|image|photo|view|canvas)|rotate\s*gesture|rotation\s*gesture|twist\s+gesture|two\s+pointer)\b", re.I)),
    ("scroll",       re.compile(r"\b(scroll(ed|ing)?|pull[- ]?to[- ]?refresh)\b", re.I)),
    ("swipe",        re.compile(r"\b(swipe|fling|swip(ed|ing))\b", re.I)),
    ("orientation",  re.compile(r"\b(rotat(e|ing)|landscape|portrait|screen\s*rotation|orientation\s*(change|lock))\b", re.I)),
    ("long_press",   re.compile(r"\b(long[- ]?(press|click|tap)|press\s+and\s+hold|hold\s+(down|your\s+finger)|tap\s+and\s+hold)\b", re.I)),
    ("double_tap",   re.compile(r"\b(double[- ]?tap|double[- ]?click|tap(ped|ping)?\s+twice)\b", re.I)),
]
PRIORITY = COMPLEX + SIMPLE


def classify(title, body):
    text = (title or "") + "\n" + (body or "")
    matched = [cat for cat, pat in PATTERNS if pat.search(text)]
    if not matched:
        return "none", "none", []
    primary = min(matched, key=lambda c: PRIORITY.index(c))
    tier = "complex" if primary in COMPLEX else "simple"
    return primary, tier, matched


def gh(url, params=None, tries=4):
    for a in range(tries):
        r = requests.get(url, headers=H, params=params, timeout=30)
        if r.status_code == 200:
            return r
        if r.status_code in (403, 429):
            reset = int(r.headers.get("X-RateLimit-Reset", time.time() + 60))
            wait = max(5, reset - int(time.time()) + 3)
            print(f"  [rate-limit] sleep {wait}s", file=sys.stderr); time.sleep(wait); continue
        if r.status_code in (404, 410, 451):
            return None
        time.sleep(2 ** a)
    return None


def discover_repos(max_repos):
    seen = set()
    queries = [
        "topic:android language:Kotlin stars:>=20 pushed:>=2023-01-01",
        "topic:android language:Java stars:>=20 pushed:>=2023-01-01",
        "topic:android-application stars:>=10 pushed:>=2022-01-01",
        "topic:android language:Kotlin stars:5..20 pushed:>=2023-06-01",
        "topic:android language:Java stars:5..20 pushed:>=2023-06-01",
        "topic:mobile-app language:Kotlin stars:>=10 pushed:>=2023-01-01",
    ]
    for q in queries:
        for page in range(1, 11):
            if len(seen) >= max_repos:
                return
            r = gh("https://api.github.com/search/repositories",
                   {"q": q, "sort": "updated", "order": "desc", "per_page": 100, "page": page})
            time.sleep(2.2)
            if r is None:
                break
            items = r.json().get("items", [])
            if not items:
                break
            for it in items:
                full = it["full_name"]
                if full in seen or not it.get("has_issues", True):
                    continue
                seen.add(full)
                yield tuple(full.split("/", 1))
                if len(seen) >= max_repos:
                    return


def fetch_bugs(owner, repo, per_repo):
    out = OrderedDict()
    for label in BUG_LABELS:
        if len(out) >= per_repo:
            break
        r = gh(f"https://api.github.com/repos/{owner}/{repo}/issues",
               {"state": "all", "labels": label, "per_page": 100, "sort": "updated", "direction": "desc"})
        time.sleep(0.15)
        if r is None:
            continue
        data = r.json()
        if not isinstance(data, list):
            continue
        for it in data:
            if it.get("pull_request"):
                continue
            n = it.get("number")
            if n and n not in out:
                out[n] = it
            if len(out) >= per_repo:
                break
    return list(out.values())[:per_repo]


def complex_counts():
    c = Counter()
    if not RAW.exists():
        return c
    for line in RAW.open():
        try:
            b = json.loads(line)
        except Exception:
            continue
        primary, tier, _ = classify(b.get("title",""), b.get("body",""))
        if tier == "complex":
            c[primary] += 1
    return c


def write_csv():
    import csv as _csv
    bugs = [json.loads(l) for l in RAW.open()]
    tier_c = Counter(); prim_c = Counter()
    with CSV.open("w", newline="") as f:
        w = _csv.writer(f)
        w.writerow(["repo", "issue_number", "primary_gesture", "tier", "matched_raw", "url", "state"])
        for b in bugs:
            primary, tier, matched = classify(b.get("title",""), b.get("body",""))
            tier_c[tier] += 1; prim_c[primary] += 1
            w.writerow([f"{b['owner']}/{b['repo']}", b["issue_number"], primary, tier,
                        "|".join(matched), b["url"], b.get("state", "")])
    n = len(bugs)
    print(f"\n==== RESULTS ====  TOTAL bugs: {n}")
    for t in ("complex", "simple", "none"):
        print(f"  {t:8s}: {tier_c.get(t,0):4d} ({100*tier_c.get(t,0)/max(n,1):.1f}%)")
    action = tier_c['complex'] + tier_c['simple']
    print(f"  action-related: {action} ({100*action/max(n,1):.1f}%); complex/action = {100*tier_c['complex']/max(action,1):.1f}%")
    print("--- complex categories ---")
    for k in COMPLEX:
        print(f"  {k:16s}: {prim_c.get(k,0)}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dryrun", action="store_true")
    ap.add_argument("--target", type=int, default=4000)
    ap.add_argument("--min-per", type=int, default=3)
    ap.add_argument("--per-repo", type=int, default=15)
    ap.add_argument("--max-repos", type=int, default=1500)
    args = ap.parse_args()

    if args.dryrun:
        write_csv(); return
    if not GH:
        print("ERROR: no GitHub token", file=sys.stderr); sys.exit(2)

    done = set(); seen_urls = set()
    if PROG.exists():
        done = set(map(tuple, json.loads(PROG.read_text()).get("done", [])))
    if RAW.exists():
        for line in RAW.open():
            try: seen_urls.add(json.loads(line)["url"])
            except Exception: pass
    total = len(seen_urls)
    print(f"[start] resume {total} bugs, {len(done)} repos done; target {args.target}, min-per {args.min_per}")
    rawf = RAW.open("a")
    for owner, repo in discover_repos(args.max_repos):
        if (owner, repo) in done:
            continue
        cc = complex_counts()
        if total >= args.target and all(cc.get(c,0) >= args.min_per for c in COMPLEX):
            print(f"[stop] target {total} reached and every complex category >= {args.min_per}: {dict(cc)}")
            break
        try:
            issues = fetch_bugs(owner, repo, args.per_repo)
        except Exception as e:
            print(f"  {owner}/{repo} ERR {e}", file=sys.stderr); done.add((owner,repo)); continue
        wrote = 0
        for it in issues:
            url = it["html_url"]
            if url in seen_urls:
                continue
            rec = {"owner": owner, "repo": repo, "issue_number": it["number"], "url": url,
                   "title": it.get("title","") or "", "body": (it.get("body") or "")[:20000],
                   "labels": [l["name"] for l in it.get("labels", [])],
                   "state": it.get("state",""), "created_at": it.get("created_at")}
            rawf.write(json.dumps(rec) + "\n"); seen_urls.add(url); wrote += 1; total += 1
        rawf.flush(); done.add((owner,repo))
        PROG.write_text(json.dumps({"done": [list(d) for d in done]}))
        if wrote:
            cc = complex_counts()
            print(f"[{len(done):4d}] {owner}/{repo:<32s} +{wrote:3d} (total {total}) complex={dict(cc)}")
    rawf.close(); write_csv()


if __name__ == "__main__":
    main()
