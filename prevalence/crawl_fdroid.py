"""Gesture-prevalence crawl of issue trackers outside GitHub.

Population: every app in the F-Droid catalogue (index-v2.json) whose issue
tracker or source code is on gitlab.com, framagit.org (GitLab) or codeberg.org
(Forgejo). For each project, up to --per-project issues carrying a bug label,
most recently updated first. Nothing in the selection looks at issue content,
and the crawl takes every eligible project, so there is no stopping rule to
bias the result.

  python crawl_fdroid.py --index fdroid_index_v2.json

Output: raw_fdroid_issues.jsonl (same record format as the GitHub crawls).
"""
import argparse
import json
import random
import re
import sys
import time
import urllib.parse
from pathlib import Path

import requests

HERE = Path(__file__).resolve().parent
RAW = HERE / "raw_fdroid_issues.jsonl"
PROG = HERE / ".progress_fdroid.json"
UA = {"User-Agent": "carbon-prevalence-fdroid (research crawl)"}
GITLAB_LABELS = ["bug", "Bug", "type::bug", "type: bug", "Type: Bug", "kind::bug", "crash", "Crash", "defect"]
FORGEJO_LABELS = ["bug", "Bug", "Kind/Bug", "kind/bug", "type: bug", "Type: Bug", "crash", "Crash", "defect"]
HOSTS = {"gitlab.com": "gitlab", "framagit.org": "gitlab", "codeberg.org": "forgejo"}


def get(url, params=None, tries=5):
    for a in range(tries):
        try:
            r = requests.get(url, params=params, headers=UA, timeout=40)
        except requests.RequestException as e:
            print(f"  [net] {e}", file=sys.stderr, flush=True); time.sleep(5 * (a + 1)); continue
        if r.status_code == 200:
            return r
        if r.status_code in (403, 429):
            wait = int(r.headers.get("Retry-After", "60")) + 2
            print(f"  [rate-limit] {url[:60]} sleep {wait}s", file=sys.stderr, flush=True); time.sleep(wait); continue
        if r.status_code in (404, 410, 401):
            return None
        time.sleep(2 ** a)
    return None


def projects(index_path, seed):
    pk = json.load(open(index_path))["packages"]
    out = []
    for app, p in pk.items():
        m = p.get("metadata", {})
        for url in (m.get("issueTracker") or "", m.get("sourceCode") or ""):
            u = urllib.parse.urlparse(url)
            host = u.netloc.lower()
            if host not in HOSTS:
                continue
            path = re.sub(r"(/-)?/issues.*$", "", u.path).strip("/").removesuffix(".git")
            if path.count("/") >= 1:
                out.append((app, host, path)); break
    uniq = list({(h, p): (a, h, p) for a, h, p in out}.values())
    random.Random(seed).shuffle(uniq)
    return uniq


def gitlab_issues(host, path, n):
    pid = urllib.parse.quote(path, safe="")
    got = {}
    for label in GITLAB_LABELS:
        if len(got) >= n:
            break
        r = get(f"https://{host}/api/v4/projects/{pid}/issues",
                {"labels": label, "state": "all", "per_page": 100, "order_by": "updated_at", "sort": "desc"})
        time.sleep(0.4)
        if r is None:
            continue
        for it in r.json():
            got.setdefault(it["iid"], {"number": it["iid"], "url": it["web_url"], "title": it.get("title") or "",
                                       "body": it.get("description") or "", "labels": it.get("labels", []),
                                       "state": it.get("state", ""), "created_at": it.get("created_at")})
            if len(got) >= n:
                break
    return list(got.values())[:n]


def forgejo_issues(host, path, n):
    got = {}
    for label in FORGEJO_LABELS:
        if len(got) >= n:
            break
        r = get(f"https://{host}/api/v1/repos/{path}/issues",
                {"type": "issues", "state": "all", "labels": label, "limit": 50, "sort": "recentupdate"})
        time.sleep(0.6)
        if r is None:
            continue
        for it in r.json():
            if label.lower() not in {l["name"].lower() for l in it.get("labels", [])}:
                continue          # some servers ignore an unknown label filter
            got.setdefault(it["number"], {"number": it["number"], "url": it["html_url"], "title": it.get("title") or "",
                                          "body": it.get("body") or "", "labels": [l["name"] for l in it.get("labels", [])],
                                          "state": it.get("state", ""), "created_at": it.get("created_at")})
            if len(got) >= n:
                break
    return list(got.values())[:n]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--index", required=True)
    ap.add_argument("--per-project", type=int, default=15)
    ap.add_argument("--seed", type=int, default=20261007)
    args = ap.parse_args()
    done = set(json.loads(PROG.read_text())["done"]) if PROG.exists() else set()
    projs = projects(args.index, args.seed)
    print(f"[start] {len(projs)} projects on GitLab/Framagit/Codeberg; {len(done)} done", flush=True)
    total = sum(1 for _ in RAW.open()) if RAW.exists() else 0
    with RAW.open("a") as f:
        for i, (app, host, path) in enumerate(projs, 1):
            key = f"{host}/{path}"
            if key in done:
                continue
            fetch = gitlab_issues if HOSTS[host] == "gitlab" else forgejo_issues
            try:
                issues = fetch(host, path, args.per_project)
            except Exception as e:
                print(f"  {key} ERR {e}", file=sys.stderr, flush=True); issues = []
            owner, repo = path.split("/", 1)
            for it in issues:
                f.write(json.dumps({"source": f"fdroid-{host}", "app_id": app, "owner": owner, "repo": repo,
                                    "issue_number": it["number"], "url": it["url"], "title": it["title"],
                                    "body": it["body"][:20000], "labels": it["labels"], "state": it["state"],
                                    "created_at": it["created_at"]}) + "\n")
            f.flush(); total += len(issues); done.add(key)
            PROG.write_text(json.dumps({"done": sorted(done)}))
            if issues:
                print(f"[{i:4d}/{len(projs)}] {key:<55s} +{len(issues):2d} (total {total})", flush=True)
    print(f"[done] {total} issues from {len(done)} projects", flush=True)


if __name__ == "__main__":
    main()
