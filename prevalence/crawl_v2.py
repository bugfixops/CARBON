"""Gesture-prevalence crawl, version 2: a larger sample under a fixed protocol.

Differences from crawl_gesture_prevalence.py (v1, kept unchanged with its data):
  * Fixed stopping rule: the crawl stops at --target issues. It never looks at
    what it has found (v1 kept crawling until every complex category had a
    minimum count, which can bias the estimate upwards).
  * Disjoint from v1: repositories already sampled in v1 are skipped.
  * Wider, still gesture-neutral discovery: GitHub's `android` topics, Kotlin
    or Java, sliced by stars and by last push, queried in a seeded random
    order. No app, gesture or UI terms appear in any query.
  * Per repository: up to --per-repo bug-labelled issues (v1's label list),
    most recently updated first.
  * --prs: also up to --per-repo merged pull requests whose title mentions a
    fix ("patches"), stored separately. They are a different population (fixes
    that were made), reported apart from the issues.

Classification is a separate step (classify.py), so v1 and v2 go through the
same classifier.

  GITHUB_TOKEN=... python crawl_v2.py --target 10000 --prs
"""
import argparse
import itertools
import json
import os
import random
import sys
import time
from collections import OrderedDict
from pathlib import Path

import requests

HERE = Path(__file__).resolve().parent
V1_RAW = HERE / "raw_random_bugs.jsonl"
RAW = HERE / "raw_v2_issues.jsonl"
RAW_PR = HERE / "raw_v2_prs.jsonl"
PROG = HERE / ".progress_v2.json"
TOKEN = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
H = {"Authorization": f"token {TOKEN}", "Accept": "application/vnd.github+json",
     "X-GitHub-Api-Version": "2022-11-28", "User-Agent": "carbon-prevalence-v2"}

BUG_LABELS = ["bug", "Bug", "crash", "Crash", "defect", "Defect", "type: bug",
              "type:bug", "Type: Bug", "kind/bug", "bug-report", "confirmed bug",
              "Issue-Bug", "t:bug", "C-bug"]          # same list as v1

TOPICS = ["android", "android-app", "android-application"]
LANGS = ["Kotlin", "Java"]
STARS = ["5..9", "10..19", "20..49", "50..99", "100..499", ">=500"]
PUSHED = ["2024-01-01..2026-12-31", "2021-01-01..2023-12-31"]


def gh(url, params=None, tries=6):
    for attempt in range(tries):
        try:
            r = requests.get(url, headers=H, params=params, timeout=40)
        except requests.RequestException as e:
            print(f"  [net] {e}", file=sys.stderr, flush=True); time.sleep(10 * (attempt + 1)); continue
        if r.status_code == 200:
            return r
        if r.status_code in (403, 429):
            retry = r.headers.get("Retry-After")
            if retry:
                wait = int(retry) + 2
            else:
                reset = int(r.headers.get("X-RateLimit-Reset", time.time() + 60))
                wait = max(5, reset - int(time.time()) + 3)
            print(f"  [rate-limit] sleep {wait}s", file=sys.stderr, flush=True); time.sleep(min(wait, 3700)); continue
        if r.status_code in (404, 410, 422, 451):
            return None
        time.sleep(2 ** attempt)
    return None


def queries(seed):
    qs = [f"topic:{t} language:{l} stars:{s} pushed:{p} archived:false"
          for t, l, s, p in itertools.product(TOPICS, LANGS, STARS, PUSHED)]
    random.Random(seed).shuffle(qs)
    return qs


def discover(seed, skip):
    seen = set(skip)
    for q in queries(seed):
        for page in range(1, 11):          # the search API returns at most 1,000 results per query
            r = gh("https://api.github.com/search/repositories",
                   {"q": q, "sort": "updated", "order": "desc", "per_page": 100, "page": page})
            time.sleep(2.2)                # search API: 30 requests per minute
            items = r.json().get("items", []) if r is not None else []
            if not items:
                break
            for it in items:
                full = it["full_name"]
                if full in seen or not it.get("has_issues", True):
                    continue
                seen.add(full)
                yield full, q, it.get("stargazers_count")


def fetch_bugs(full, per_repo):
    out = OrderedDict()
    # Ask only for the bug labels this repository has (one request instead of
    # up to 15); the sample definition is unchanged.
    r = gh(f"https://api.github.com/repos/{full}/labels", {"per_page": 100})
    have = {l["name"].lower() for l in r.json()} if r is not None and isinstance(r.json(), list) else None
    labels = [l for l in BUG_LABELS if have is None or l.lower() in have]
    labels = list(OrderedDict((l.lower(), l) for l in labels).values())   # labels match case-insensitively
    for label in labels:
        if len(out) >= per_repo:
            break
        r = gh(f"https://api.github.com/repos/{full}/issues",
               {"state": "all", "labels": label, "per_page": 100, "sort": "updated", "direction": "desc"})
        if r is None:
            continue
        data = r.json()
        if not isinstance(data, list):
            continue
        for it in data:
            if it.get("pull_request"):
                continue
            if it.get("number") not in out:
                out[it["number"]] = it
            if len(out) >= per_repo:
                break
    return list(out.values())[:per_repo]


def fetch_fix_prs(full, per_repo):
    r = gh("https://api.github.com/search/issues",
           {"q": f"repo:{full} is:pr is:merged fix in:title", "sort": "updated", "order": "desc",
            "per_page": per_repo})
    time.sleep(2.2)
    return r.json().get("items", [])[:per_repo] if r is not None else []


def rec(full, q, stars, it, kind):
    owner, repo = full.split("/", 1)
    return {"source": f"github-{kind}", "owner": owner, "repo": repo, "issue_number": it["number"],
            "url": it["html_url"], "title": it.get("title") or "", "body": (it.get("body") or "")[:20000],
            "labels": [l["name"] for l in it.get("labels", [])], "state": it.get("state", ""),
            "created_at": it.get("created_at"), "repo_query": q, "repo_stars": stars}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--target", type=int, default=10000, help="issues to collect (fixed stopping rule)")
    ap.add_argument("--per-repo", type=int, default=15)
    ap.add_argument("--prs", action="store_true", help="also collect merged fix PRs")
    ap.add_argument("--seed", type=int, default=20261007)
    args = ap.parse_args()
    if not TOKEN:
        sys.exit("set GITHUB_TOKEN")

    v1_repos = {f"{json.loads(l)['owner']}/{json.loads(l)['repo']}" for l in V1_RAW.open()}
    prog = json.loads(PROG.read_text()) if PROG.exists() else {"done": []}
    done = set(prog["done"])
    seen = set()
    total = 0
    if RAW.exists():
        for l in RAW.open():
            seen.add(json.loads(l)["url"]); total += 1
    print(f"[start] v1 repos skipped: {len(v1_repos)}; resume {total} issues, {len(done)} repos done; "
          f"target {args.target}", flush=True)
    with RAW.open("a") as fi, RAW_PR.open("a") as fp:
        for full, q, stars in discover(args.seed, v1_repos):
            if total >= args.target:
                break
            if full in done:
                continue
            issues = fetch_bugs(full, args.per_repo)
            n = 0
            for it in issues:
                if it["html_url"] in seen or total >= args.target:
                    continue
                fi.write(json.dumps(rec(full, q, stars, it, "issue")) + "\n"); seen.add(it["html_url"])
                total += 1; n += 1
            fi.flush()
            m = 0
            if args.prs and issues:      # same repositories as the issue sample
                for it in fetch_fix_prs(full, args.per_repo):
                    fp.write(json.dumps(rec(full, q, stars, it, "fix-pr")) + "\n"); m += 1
                fp.flush()
            done.add(full)
            PROG.write_text(json.dumps({"done": sorted(done)}))
            if n:
                print(f"[{len(done):5d}] {full:<45s} +{n:2d} issues +{m:2d} PRs  (total {total})", flush=True)
    print(f"[done] {total} issues", flush=True)


if __name__ == "__main__":
    main()
