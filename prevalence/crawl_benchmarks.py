"""Bug-report texts of published Android bug-reproduction benchmarks.

Collects the reports into raw_benchmarks.jsonl so the gesture classifier can
run over them. Nothing here classifies anything.

Sources (one record per bug report, deduplicated by URL within a source):
  benchmark-andror2                SageSELab/AndroR2: reports/ (saved GitHub issue pages)
                                   and metadata/. The saved page supplies the text; the
                                   GitHub API is used only where the page is missing or is
                                   not the issue.
  benchmark-recdroid               AndroidTestBugReport/ReCDroid: "Evaluation Result/
                                   evaluationDataSet.xlsx" (ICSE'19, 51 bugs) and the
                                   journal-new-data sheet (same 51 + journal extension).
                                   Text fetched from each issue's tracker.
  benchmark-themis                 the-themis-benchmarks/home README, the N bugs the README
                                   says Themis contains (52). Text from the GitHub API.
  benchmark-rebl                   results/ReBL_Full_Dataset and results/ReBL_Failed_Dataset
                                   (local bug_report.txt), deduplicated by case.
  benchmark-reactdroid-motivation  baselines/ReActDroid/motivation/data.xlsx, sheet 1
                                   (local text; no fetching).

Extra fields beyond the requested schema:
  text_origin    where title/body came from (saved-page, github-api, google-code-archive,
                 gitlab-api, local-file, local-sheet)
  canonical_url  the issue's current URL when the tracker reported one (renamed or
                 transferred repositories), else the benchmark's URL
  note           only on records that needed a judgement call

GitHub token: `git credential fill` for github.com (never printed or written).
Requests are spaced ~0.5 s apart and pause when the shared core limit runs low.

  python crawl_benchmarks.py --repos /tmp/bench-repos [--cache /tmp/gh-cache.json]
"""
import argparse
import ast
import json
import re
import subprocess
import sys
import time
import zipfile
import xml.etree.ElementTree as ET
from collections import Counter, OrderedDict, defaultdict
from datetime import datetime, timedelta, timezone
from html.parser import HTMLParser
from pathlib import Path

import requests

HERE = Path(__file__).resolve().parent
CARBON = HERE.parent
OUT = HERE / "raw_benchmarks.jsonl"
BODY_MAX = 20000
UA = "carbon-benchmark-reports"
LOW_WATER = 300  # pause when fewer core requests than this remain (shared token)

GH_ISSUE = re.compile(r"https?://(?:www\.)?github\.com/([^/\s]+)/([^/\s]+)/(issues|pull)/(\d+)", re.I)
GOOGLE_CODE = re.compile(r"https?://code\.google\.com/(?:archive/)?p/([^/\s]+)/issues/(?:detail\?id=)?(\d+)", re.I)
GITLAB = re.compile(r"https?://gitlab\.com/(.+?)/(?:-/)?issues/(\d+)", re.I)
BITBUCKET = re.compile(r"https?://bitbucket\.org/([^/\s]+)/([^/\s]+)/issues/(\d+)", re.I)


def norm_url(url):
    """Comparable key for an issue URL (GitHub issue and pull numbers share one space)."""
    u = (url or "").strip()
    m = GH_ISSUE.match(u)
    if m:
        return f"https://github.com/{m[1]}/{m[2]}/issues/{m[4]}".lower()
    m = GOOGLE_CODE.match(u)
    if m:
        return f"https://code.google.com/archive/p/{m[1]}/issues/{m[2]}".lower()
    m = GITLAB.match(u)
    if m:
        return f"https://gitlab.com/{m[1]}/issues/{m[2]}".lower()
    m = BITBUCKET.match(u)
    if m:
        return f"https://bitbucket.org/{m[1]}/{m[2]}/issues/{m[3]}".lower()
    return u.lower().replace("http://", "https://").rstrip("/")


def make_record(source, owner, repo, number, url, title, body, labels, state, created_at,
                benchmark_id, text_origin, canonical_url=None, note=None):
    rec = OrderedDict(
        source=source, owner=owner, repo=repo,
        issue_number=int(number) if number is not None else None, url=url,
        title=(title or "").strip(), body=(body or "")[:BODY_MAX],
        labels=list(labels or []), state=state, created_at=created_at,
        benchmark_id=benchmark_id, text_origin=text_origin,
        canonical_url=canonical_url or url)
    if note:
        rec["note"] = note
    return rec


# --------------------------------------------------------------------------- GitHub
def github_token():
    out = subprocess.run(["git", "-C", str(CARBON), "credential", "fill"],
                         input="protocol=https\nhost=github.com\n\n",
                         capture_output=True, text=True, timeout=60).stdout
    for line in out.splitlines():
        if line.startswith("password="):
            return line.split("=", 1)[1].strip()
    sys.exit("no GitHub token from `git credential fill`")


class GitHub:
    def __init__(self, cache_path=None):
        self.s = requests.Session()
        self.s.headers.update({"Authorization": f"token {github_token()}",
                               "Accept": "application/vnd.github+json",
                               "X-GitHub-Api-Version": "2022-11-28", "User-Agent": UA})
        self.cache_path = Path(cache_path) if cache_path else None
        self.cache = {}
        if self.cache_path and self.cache_path.exists():
            self.cache = json.loads(self.cache_path.read_text())
        self.calls = 0

    def remaining(self):
        r = self.s.get("https://api.github.com/rate_limit", timeout=30)  # not counted
        return r.json()["resources"]["core"]["remaining"]

    def _wait_reset(self, headers, why):
        retry = headers.get("Retry-After")
        if retry:
            wait = int(retry) + 2
        else:
            reset = int(headers.get("X-RateLimit-Reset", time.time() + 60))
            wait = max(5, reset - int(time.time()) + 3)
        print(f"  [rate-limit: {why}] sleeping {wait}s", file=sys.stderr, flush=True)
        time.sleep(min(wait, 3700))

    def _get(self, url, tries=6):
        for attempt in range(tries):
            time.sleep(0.5)
            try:
                r = self.s.get(url, timeout=40)
            except requests.RequestException as e:
                print(f"  [net] {type(e).__name__}; retrying", file=sys.stderr, flush=True)
                time.sleep(5 * (attempt + 1))
                continue
            self.calls += 1
            rem = r.headers.get("X-RateLimit-Remaining")
            if r.status_code == 200:
                if rem is not None and int(rem) < LOW_WATER:
                    self._wait_reset(r.headers, f"{rem} left")
                return 200, r.json()
            if r.status_code in (403, 429) and (r.headers.get("Retry-After") or rem == "0"):
                self._wait_reset(r.headers, f"HTTP {r.status_code}")
                continue
            if r.status_code >= 500:
                time.sleep(5 * (attempt + 1))
                continue
            return r.status_code, None
        return -1, None

    def issue(self, owner, repo, number):
        key = f"{owner}/{repo}#{number}".lower()
        if key not in self.cache:
            status, data = self._get(f"https://api.github.com/repos/{owner}/{repo}/issues/{number}")
            if status == -1:
                return {"status": status, "data": None}
            if data is not None:  # keep only what the records need
                data = {k: data.get(k) for k in ("title", "body", "state", "created_at", "html_url")} | {
                    "labels": [l.get("name") for l in data.get("labels") or []],
                    "is_pull": bool(data.get("pull_request"))}
            self.cache[key] = {"status": status, "data": data}
            if self.cache_path:
                self.cache_path.write_text(json.dumps(self.cache))
        return self.cache[key]


def from_github(gh, source, owner, repo, number, url, benchmark_id, note=None):
    """Record from the GitHub API, or (None, reason)."""
    got = gh.issue(owner, repo, number)
    if got["status"] != 200:
        return None, f"GitHub API HTTP {got['status']}"
    d = got["data"]
    if d.get("is_pull"):
        note = (note + "; " if note else "") + "the benchmark's link is a pull request, not an issue"
    return make_record(source, owner, repo, number, url, d["title"], d["body"], d["labels"],
                       d["state"], d["created_at"], benchmark_id, "github-api",
                       canonical_url=d["html_url"], note=note), None


# ------------------------------------------------------------- other public trackers
_PLAIN = requests.Session()
_PLAIN.headers["User-Agent"] = UA
_OTHER_CACHE = {}


def from_other_tracker(source, url, owner, repo, benchmark_id):
    """Google Code archive / GitLab / Bitbucket issues (no GitHub quota). (rec|None, reason)."""
    key = norm_url(url)
    if key not in _OTHER_CACHE:
        time.sleep(0.3)
        m = GOOGLE_CODE.match(url)
        g = GITLAB.match(url)
        b = BITBUCKET.match(url)
        try:
            if m:
                r = _PLAIN.get("https://storage.googleapis.com/google-code-archive/v2/code.google.com/"
                               f"{m[1]}/issues/issue-{m[2]}.json", timeout=40)
                if r.status_code != 200:
                    _OTHER_CACHE[key] = (None, f"Google Code archive HTTP {r.status_code}")
                else:
                    d = json.loads(r.content.decode("utf-8"))
                    first = (d.get("comments") or [{}])[0]
                    ts = first.get("timestamp")
                    created = (datetime.fromtimestamp(int(ts), timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
                               if ts else None)
                    _OTHER_CACHE[key] = (dict(title=d.get("summary"), body=first.get("content") or "",
                                              labels=d.get("labels") or [], state=d.get("status"),
                                              created_at=created, origin="google-code-archive",
                                              canonical=url, number=m[2]), None)
            elif g:
                proj = requests.utils.quote(g[1], safe="")
                r = _PLAIN.get(f"https://gitlab.com/api/v4/projects/{proj}/issues/{g[2]}", timeout=40)
                if r.status_code != 200:
                    _OTHER_CACHE[key] = (None, f"GitLab API HTTP {r.status_code}")
                else:
                    d = r.json()
                    _OTHER_CACHE[key] = (dict(title=d.get("title"), body=d.get("description") or "",
                                              labels=d.get("labels") or [], state=d.get("state"),
                                              created_at=d.get("created_at"), origin="gitlab-api",
                                              canonical=url, number=g[2]), None)
            elif b:
                r = _PLAIN.get(f"https://api.bitbucket.org/2.0/repositories/{b[1]}/{b[2]}/issues/{b[3]}",
                               timeout=40)
                if r.status_code != 200:
                    _OTHER_CACHE[key] = (None, f"Bitbucket issues API HTTP {r.status_code}"
                                               + (" (issue API deprecated)" if r.status_code == 410 else ""))
                else:
                    d = r.json()
                    _OTHER_CACHE[key] = (dict(title=d.get("title"), body=(d.get("content") or {}).get("raw") or "",
                                              labels=[x for x in (d.get("kind"), d.get("component")) if x],
                                              state=d.get("state"), created_at=d.get("created_on"),
                                              origin="bitbucket-api", canonical=url, number=b[3]), None)
            else:
                _OTHER_CACHE[key] = (None, "unrecognised tracker URL")
        except (requests.RequestException, ValueError) as e:
            _OTHER_CACHE[key] = (None, f"{type(e).__name__} fetching tracker")
    d, why = _OTHER_CACHE[key]
    if d is None:
        return None, why
    return make_record(source, owner, repo, d["number"], url, d["title"], d["body"], d["labels"],
                       d["state"], d["created_at"], benchmark_id, d["origin"],
                       canonical_url=d["canonical"]), None


def fetch_any(gh, source, url, benchmark_id, note=None):
    m = GH_ISSUE.match(url)
    if m:
        return from_github(gh, source, m[1], m[2], m[4], url, benchmark_id, note)
    for rx in (GOOGLE_CODE, GITLAB, BITBUCKET):
        mm = rx.match(url)
        if mm:
            if rx is GOOGLE_CODE:
                owner = repo = mm[1]
            elif rx is GITLAB:
                owner, _, repo = mm[1].rpartition("/")
            else:
                owner, repo = mm[1], mm[2]
            return from_other_tracker(source, url, owner, repo, benchmark_id)
    return None, "unrecognised URL"


# -------------------------------------------------------------------------- xlsx
_NS = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
       "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
       "pr": "http://schemas.openxmlformats.org/package/2006/relationships"}


def _col(ref):
    n = 0
    for ch in re.match(r"[A-Z]+", ref).group(0):
        n = n * 26 + ord(ch) - 64
    return n - 1


def first_sheet(path):
    """Rows of the workbook's first sheet: list of {col: {'v': value, 'f': formula, 'link': url}}."""
    z = zipfile.ZipFile(path)
    shared = []
    if "xl/sharedStrings.xml" in z.namelist():
        for si in ET.fromstring(z.read("xl/sharedStrings.xml")).findall("m:si", _NS):
            shared.append("".join(t.text or "" for t in si.iter(f"{{{_NS['m']}}}t")))
    wb = ET.fromstring(z.read("xl/workbook.xml"))
    rels = {r.get("Id"): r.get("Target") for r in
            ET.fromstring(z.read("xl/_rels/workbook.xml.rels")).findall("pr:Relationship", _NS)}
    sheet = wb.find("m:sheets", _NS).findall("m:sheet", _NS)[0]
    target = rels[sheet.get(f"{{{_NS['r']}}}id")].lstrip("/")
    target = target if target.startswith("xl/") else "xl/" + target
    root = ET.fromstring(z.read(target))
    links = {}
    relpath = target.replace("worksheets/", "worksheets/_rels/") + ".rels"
    if relpath in z.namelist() and root.find("m:hyperlinks", _NS) is not None:
        srel = {r.get("Id"): r.get("Target") for r in
                ET.fromstring(z.read(relpath)).findall("pr:Relationship", _NS)}
        for h in root.find("m:hyperlinks", _NS).findall("m:hyperlink", _NS):
            links[h.get("ref")] = srel.get(h.get(f"{{{_NS['r']}}}id"))
    rows = []
    for row in root.iter(f"{{{_NS['m']}}}row"):
        cells = {}
        for c in row.findall("m:c", _NS):
            t, f, v = c.get("t"), c.find("m:f", _NS), c.find("m:v", _NS)
            if t == "s" and v is not None:
                val = shared[int(v.text)]
            elif t == "inlineStr":
                val = "".join(x.text or "" for x in c.iter(f"{{{_NS['m']}}}t"))
            else:
                val = v.text if v is not None else None
            cells[_col(c.get("r"))] = {"v": val, "f": f.text if f is not None else None,
                                       "link": links.get(c.get("r"))}
        rows.append(cells)
    return rows


def cell(row, i, key="v"):
    return (row.get(i) or {}).get(key)


# ------------------------------------------------------------- saved GitHub pages
_VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param",
         "source", "track", "wbr"}
_BLOCK = {"p", "div", "ul", "ol", "li", "pre", "h1", "h2", "h3", "h4", "h5", "h6", "blockquote",
          "table", "thead", "tbody", "tr", "details", "summary", "dl", "dt", "dd", "hr"}


class IssuePage(HTMLParser):
    """Title, first comment (the report), state, labels and creation time of a saved issue page."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []
        self.title = self._title = None
        self.body = self._body = None
        self._pre = 0
        self._lists = []  # per open <ol>/<ul> in the body: item counter, or None for bullets
        self.state = self.created_at = self.og_url = None
        self.labels = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        cls = (a.get("class") or "").split()
        if tag == "meta" and a.get("property") == "og:url":
            self.og_url = a.get("content")
        if tag == "relative-time" and self.created_at is None and a.get("datetime"):
            self.created_at = a["datetime"]
        if self.state is None and "State" in cls and (a.get("title") or "").startswith("Status:"):
            self.state = a["title"].split(":", 1)[1].strip().lower()
        if tag == "a" and "IssueLabel" in cls and "width-fit" in cls and a.get("data-name"):
            if a["data-name"] not in self.labels:
                self.labels.append(a["data-name"])
        if self._body is not None:
            if tag == "pre":
                self._pre += 1
            if tag in ("ol", "ul"):
                self._lists.append(int(a.get("start") or 1) - 1 if tag == "ol" else None)
            if tag == "br":
                self._body.append("\n")
            elif tag == "li":
                if self._lists and self._lists[-1] is not None:
                    self._lists[-1] += 1
                    self._body.append(f"\n{self._lists[-1]}. ")
                else:
                    self._body.append("\n- ")
            elif tag == "input" and a.get("type") == "checkbox":
                self._body.append("[x] " if "checked" in a else "[ ] ")
            elif tag in _BLOCK:
                self._body.append("\n")
        role = None
        if self.title is None and self._title is None and "js-issue-title" in cls:
            role, self._title = "title", []
        elif self.body is None and self._body is None and "js-comment-body" in cls:
            role, self._body = "body", []
        if tag not in _VOID:
            self.stack.append((tag, role))

    def handle_endtag(self, tag):
        if tag in _VOID:
            return
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][0] == tag:
                popped = self.stack[i:]
                del self.stack[i:]
                break
        else:
            return
        for t, role in reversed(popped):
            if self._body is not None:
                if t == "pre":
                    self._pre = max(0, self._pre - 1)
                if t in ("ol", "ul") and self._lists:
                    self._lists.pop()
                if t in _BLOCK:
                    self._body.append("\n")
            if role == "title":
                self.title = " ".join("".join(self._title).split())
                self._title = None
            elif role == "body":
                self.body = _clean_text("".join(self._body))
                self._body = None

    def handle_data(self, data):
        if self._title is not None:
            self._title.append(data)
        if self._body is not None:
            self._body.append(data if self._pre else re.sub(r"\s+", " ", data))


def _clean_text(text):
    lines = [ln.rstrip() for ln in text.replace("\r", "").split("\n")]
    lines = [ln[1:] if ln.startswith(" ") and not ln.startswith("  ") else ln for ln in lines]
    out = re.sub(r"\n{3,}", "\n\n", "\n".join(lines)).strip()
    return "" if out == "No description provided." else out


def parse_issue_page(path):
    p = IssuePage()
    p.feed(path.read_text(encoding="utf-8", errors="replace"))
    p.close()
    return p


# -------------------------------------------------------------------------- sources
def src_andror2(repos, gh, problems):
    source = "benchmark-andror2"
    root = repos / "AndroR2"
    readme = {m[1]: m[2] for m in re.finditer(r"^\|\s*(\d+)\s*\|\s*\[Link\]\((\S+?)\)",
                                               (root / "README.md").read_text(encoding="utf-8"), re.M)}
    meta = {}
    for p in sorted((root / "metadata").glob("*.json")):
        txt = p.read_text(encoding="utf-8")
        try:
            meta[p.stem] = json.loads(txt)
        except json.JSONDecodeError:
            meta[p.stem] = ast.literal_eval(txt)  # the files are Python dict literals
    reports = {p.name.split(".")[0]: p for p in (root / "reports").iterdir()
               if p.suffix.lower() in (".htm", ".html")}
    recs = []
    for bid in sorted(set(meta) | set(reports), key=int):
        page = parse_issue_page(reports[bid]) if bid in reports else None
        url = (meta.get(bid) or {}).get("github_issue") or readme.get(bid)
        if not url and page and page.og_url and GH_ISSUE.match(page.og_url):
            url = page.og_url  # report without metadata or README row: the page's own URL
        m = GH_ISSUE.match(url or "")
        if not m:
            problems.append(f"andror2 {bid}: no issue URL; skipped")
            continue
        owner, repo, num = m[1], m[2], m[4]
        url = f"https://github.com/{owner}/{repo}/issues/{num}"
        page_ok = (page is not None and page.title and page.body is not None and page.og_url
                   and norm_url(page.og_url) == norm_url(url))
        if page_ok:
            recs.append(make_record(source, owner, repo, num, url, page.title, page.body, page.labels,
                                    page.state, page.created_at, bid, "saved-page",
                                    canonical_url=page.og_url))
            continue
        why = ("no saved report page" if page is None else
               f"saved page is not this issue ({page.og_url or 'no og:url'})")
        rec, err = from_github(gh, source, owner, repo, num, url, bid, note=f"{why}; text from GitHub API")
        if rec:
            recs.append(rec)
            problems.append(f"andror2 {bid}: {why}; fetched from the API")
        else:
            problems.append(f"andror2 {bid}: {why}; API failed ({err}); skipped")
    return recs


def src_recdroid(repos, gh, problems):
    source = "benchmark-recdroid"
    root = repos / "ReCDroid" / "Evaluation Result"
    entries = OrderedDict()
    for sheet in (root / "evaluationDataSet.xlsx", root / "journal-new-data" / "evaluationDataSet (1).xlsx"):
        extension = False
        for row in first_sheet(sheet)[1:]:
            a, b = (cell(row, 0) or "").strip(), (cell(row, 1) or "").strip()
            if a.lower().startswith("journal extension"):
                extension = True
                continue
            if not b.lower().startswith("http"):
                continue
            key = norm_url(b)
            if key not in entries:
                entries[key] = {"url": b, "id": a, "subset": "journal-extension" if extension else "icse2019"}
    local = {norm_url(url): (case, text) for case, text, url in rebl_cases()}
    recs = []
    for e in entries.values():
        rec, err = fetch_any(gh, source, e["url"], e["id"])
        if rec is None and norm_url(e["url"]) in local:
            # Gone from its tracker, but ReBL's benchmark ships a copy of the same report.
            case, text = local[norm_url(e["url"])]
            m = GH_ISSUE.match(e["url"])
            rec = make_record(source, m[1] if m else None, m[2] if m else None, m[4] if m else None,
                              e["url"], text["title"], text["body"], [], None, None, e["id"],
                              "rebl-local-copy",
                              note=f"{err}; text from ReBL's local copy (results/.../{case}/bug_report.txt)")
            problems.append(f"recdroid {e['id']} {e['url']}: {err}; used ReBL's local copy ({case})")
        if rec is None:
            problems.append(f"recdroid {e['id']} {e['url']}: {err}; skipped")
            continue
        rec["recdroid_subset"] = e["subset"]
        recs.append(rec)
    return recs


def src_themis(repos, gh, problems):
    source = "benchmark-themis"
    text = (repos / "themis" / "README.md").read_text(encoding="utf-8")
    n_bugs = int(re.search(r"Themis now contains \*?(\d+)\*? reproducible crash bugs", text)[1])
    section = text.split("### List of crash bugs", 1)[1].split("\n## ", 1)[0]
    rows = re.findall(r"^\s*(\d+)\s*\|\s*\*\[([^\]]+)\]\([^)]*\)\*\s*\|\s*(.*?)\s*\|", section, re.M)
    listed = [r for r in rows if 1 <= int(r[0]) <= n_bugs]
    extra = [r for r in rows if int(r[0]) > n_bugs]
    if extra:
        problems.append(f"themis: README says {n_bugs} bugs; its table also lists rows "
                        f"{extra[0][0]}-{extra[-1][0]} ({len(extra)} later additions), not collected")
    by_url = OrderedDict()
    for idx, app, cell_txt in listed:
        links = re.findall(r"\[#(\d+)\]\((https?://github\.com/[^)\s]+)\)", cell_txt)
        if not links:
            problems.append(f"themis row {idx}: no GitHub link; skipped")
            continue
        num, url = links[0]
        bid = f"{app}-#{num}"
        note = None
        ref = re.search(r"\(Ref:\s*\[#(\d+)\]\((https?://github\.com/[^)\s]+)\)\)", cell_txt)
        if "/pull/" in url and ref and GH_ISSUE.match(ref[2]).group(1, 2) == GH_ISSUE.match(url).group(1, 2):
            note = (f"Themis links fix PR {url}; the bug is described in referenced issue #{ref[1]}, "
                    "which is used here")
            url = ref[2]
        key = norm_url(url)
        if key in by_url:
            by_url[key]["ids"].append(bid)
        else:
            by_url[key] = {"url": url, "ids": [bid], "note": note}
    recs = []
    for e in by_url.values():
        note = e["note"]
        if len(e["ids"]) > 1:
            note = (note + "; " if note else "") + f"one report for Themis bugs {', '.join(e['ids'])}"
        rec, err = fetch_any(gh, source, e["url"], ",".join(e["ids"]))
        if rec is None:
            problems.append(f"themis {e['ids']} {e['url']}: {err}; skipped")
            continue
        if note:
            rec["note"] = note
        recs.append(rec)
    return recs


# ReBL cases whose report comes from a tracker other than github.com/<owner>/<repo>
# (folder name keeps ReBL's naming). Matched to ReCDroid's evaluation list; the local
# title is checked against the tracker's title below.
REBL_NON_GITHUB = {
    "opensudoku-android_OpenSudoku_173": "https://code.google.com/archive/p/opensudoku-android/issues/173",
    "helloworld1_AnyMemo_18": "https://code.google.com/archive/p/anymemo/issues/18",
    "banderlabs_notepad_23": "https://code.google.com/archive/p/banderlabs/issues/23",
    "fdroid_fdroidclient_1821": "https://gitlab.com/fdroid/fdroidclient/issues/1821",
}


def _parse_rebl(text):
    lines = text.replace("\r\n", "\n").split("\n")
    if lines and lines[0].strip() == "Bug Report Title:":
        try:
            k = next(i for i, ln in enumerate(lines) if ln.strip() == "Bug Report Issue:")
        except StopIteration:
            k = 2
        return {"title": " ".join(" ".join(lines[1:k]).split()),
                "body": "\n".join(lines[k + 1:]).strip("\n"), "url": None}
    url = next((m[1] for ln in lines for m in [re.match(r"Issue:\s*(\S+)", ln.strip())] if m), None)
    body = text.split("--- Full Issue Body ---", 1)[1].strip("\n") if "--- Full Issue Body ---" in text else text
    return {"title": lines[0].strip(), "body": body, "url": url}


def _title_key(t):
    return re.sub(r"[^a-z0-9]+", " ", (t or "").lower()).strip()


def rebl_cases():
    """(case, {title, body}, url) per ReBL case, Full and Failed sets merged by case folder.

    The report text comes from ReBL_Full_Dataset when the case is there (the Failed copies
    wrap the same report in CARBON's own analysis notes); the URL from a file's "Issue:"
    line, else from the folder name <owner>_<repo>_<number> (or REBL_NON_GITHUB)."""
    cases = OrderedDict()
    for ds in ("ReBL_Full_Dataset", "ReBL_Failed_Dataset"):
        for cat in ("crash", "non_crash"):
            folder = CARBON / "results" / ds / cat
            for d in sorted(folder.iterdir()) if folder.is_dir() else []:
                f = d / "bug_report.txt"
                if f.is_file():
                    cases.setdefault(d.name, {})[ds] = _parse_rebl(f.read_text(encoding="utf-8", errors="replace"))
    out = []
    for case, got in cases.items():
        text = got.get("ReBL_Full_Dataset") or got["ReBL_Failed_Dataset"]
        url = next((g["url"] for g in got.values() if g.get("url")), None)
        m = re.match(r"^([^_]+)_(.+)_(\d+)$", case)
        if not url:
            url = REBL_NON_GITHUB.get(case) or (f"https://github.com/{m[1]}/{m[2]}/issues/{m[3]}" if m else None)
        out.append((case, text, url))
    return out


def src_rebl(gh, problems):
    source = "benchmark-rebl"
    recs, seen = [], set()
    for case, text, url in rebl_cases():
        m = re.match(r"^([^_]+)_(.+)_(\d+)$", case)
        owner, repo, num = (m[1], m[2], m[3]) if m else (None, None, None)
        if not url:
            problems.append(f"rebl {case}: no URL; skipped")
            continue
        key = norm_url(url)
        if key in seen:
            problems.append(f"rebl {case}: duplicate URL {url}; dropped")
            continue
        seen.add(key)
        # Tracker metadata (and a check that the URL is this report): title must match.
        tracker, err = fetch_any(gh, source, url, case)
        note = None
        if tracker is None:
            problems.append(f"rebl {case}: could not check {url} ({err}); kept local text")
            note = f"URL not verified ({err})"
        elif _title_key(tracker["title"]) != _title_key(text["title"]):
            problems.append(f"rebl {case}: local title {text['title']!r} != tracker title "
                            f"{tracker['title']!r} at {url}")
            note = f"tracker title differs: {tracker['title']!r}"
        gm = GH_ISSUE.match(url)
        if gm:
            owner, repo, num = gm[1], gm[2], gm[4]
        rec = make_record(
            source, owner, repo, num, url, text["title"], text["body"],
            tracker["labels"] if tracker else [], tracker["state"] if tracker else None,
            tracker["created_at"] if tracker else None, case, "local-file",
            canonical_url=tracker["canonical_url"] if tracker else url, note=note)
        # Most local files append the issue's comments after the report ("Comments:" then
        # "Comment#1:"). Kept, as the file has it; this offset lets a consumer cut them.
        cm = re.search(r"(?m)^Comments:\s*\n(?=Comment#1:)", rec["body"])
        rec["comments_offset"] = cm.start() if cm else None
        recs.append(rec)
    return recs


def src_reactdroid(problems):
    source = "benchmark-reactdroid-motivation"
    path = CARBON / "baselines" / "ReActDroid" / "motivation" / "data.xlsx"
    rows = first_sheet(path)
    head = {(cell(rows[0], i) or "").strip(): i for i in rows[0]}
    need = ["_id", "title", "body", "created_at", "issue_page"]
    missing = [c for c in need if c not in head]
    if missing:
        problems.append(f"reactdroid: sheet lacks columns {missing}; skipped")
        return []
    recs, seen, dups, bad = [], set(), 0, 0
    for row in rows[1:]:
        if not row:
            continue
        ip = head["issue_page"]
        f = cell(row, ip, "f") or ""
        mm = re.search(r'HYPERLINK\(\s*"([^"]+)"', f)
        url = mm[1] if mm else (cell(row, ip, "link") or "")
        m = GH_ISSUE.match(url)
        if not m:
            bad += 1
            continue
        key = norm_url(url)
        if key in seen:
            dups += 1
            continue
        seen.add(key)
        created = cell(row, head["created_at"])
        if created and re.fullmatch(r"\d+(\.\d+)?", created):  # Excel serial date
            created = (datetime(1899, 12, 30) + timedelta(days=float(created))).strftime("%Y-%m-%d")
        recs.append(make_record(source, m[1], m[2], m[4], url, cell(row, head["title"]),
                                cell(row, head["body"]), [], None, created,
                                cell(row, head["_id"]), "local-sheet"))
    if bad:
        problems.append(f"reactdroid: {bad} rows without a parseable GitHub issue URL; skipped")
    if dups:
        problems.append(f"reactdroid: {dups} rows repeat an earlier URL; dropped")
    return recs


# ---------------------------------------------------------------------------- main
def ensure_repos(repos):
    repos.mkdir(parents=True, exist_ok=True)
    for name, url in (("AndroR2", "https://github.com/SageSELab/AndroR2.git"),
                      ("themis", "https://github.com/the-themis-benchmarks/home.git")):
        if not (repos / name).exists():
            subprocess.run(["git", "clone", "-q", "--depth", "1", url, str(repos / name)], check=True)
    rc = repos / "ReCDroid"
    if not rc.exists():  # only the evaluation sheets; the repo also holds large APKs and videos
        subprocess.run(["git", "clone", "-q", "--depth", "1", "--filter=blob:none", "--no-checkout",
                        "https://github.com/AndroidTestBugReport/ReCDroid.git", str(rc)], check=True)
        subprocess.run(["git", "-C", str(rc), "sparse-checkout", "set", "--no-cone",
                        "/Evaluation Result/*.xlsx", "/Evaluation Result/journal-new-data/*.xlsx"], check=True)
        subprocess.run(["git", "-C", str(rc), "checkout", "-q"], check=True)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--repos", required=True, help="folder for (or with) the AndroR2, ReCDroid, themis clones")
    ap.add_argument("--cache", help="JSON cache of GitHub API answers (re-runs cost no requests)")
    ap.add_argument("--out", default=str(OUT))
    args = ap.parse_args()
    repos = Path(args.repos)
    ensure_repos(repos)
    gh = GitHub(args.cache)
    print(f"GitHub core requests remaining at start: {gh.remaining()}", flush=True)

    problems, out = [], []
    for name, fn in (("andror2", lambda: src_andror2(repos, gh, problems)),
                     ("recdroid", lambda: src_recdroid(repos, gh, problems)),
                     ("themis", lambda: src_themis(repos, gh, problems)),
                     ("rebl", lambda: src_rebl(gh, problems)),
                     ("reactdroid", lambda: src_reactdroid(problems))):
        recs = fn()
        print(f"{name}: {len(recs)} records ({dict(Counter(r['text_origin'] for r in recs))})", flush=True)
        out.extend(recs)

    with open(args.out, "w", encoding="utf-8") as fh:
        for r in out:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")

    # Cross-source duplicates, matching renamed/transferred repositories via the API's URLs.
    alias = {}
    for k, v in gh.cache.items():
        if v.get("data") and v["data"].get("html_url"):
            m = GH_ISSUE.match(v["data"]["html_url"])
            req = k.split("#")[0]
            if m:
                alias[req] = f"{m[1]}/{m[2]}".lower()

    def xkey(r):
        k = norm_url(r["canonical_url"] or r["url"])
        m = GH_ISSUE.match(k)
        if m:
            k = f"https://github.com/{alias.get(f'{m[1]}/{m[2]}'.lower(), f'{m[1]}/{m[2]}'.lower())}/issues/{m[4]}"
        return k

    where = defaultdict(set)
    for r in out:
        where[xkey(r)].add(r["source"])
    shared = {k: s for k, s in where.items() if len(s) > 1}
    pairs = Counter(" & ".join(sorted(s)) for s in shared.values())
    print(f"\nwrote {len(out)} records to {args.out}")
    print(f"cross-source duplicates: {len(shared)} reports appear in 2+ sources "
          f"({sum(len(s) for s in shared.values())} records)")
    for p, n in pairs.most_common():
        print(f"  {n:4d}  {p}")
    print(f"\nGitHub API calls this run: {gh.calls}; remaining now: {gh.remaining()}")
    print(f"\nproblems ({len(problems)}):")
    for p in problems:
        print("  -", p)


if __name__ == "__main__":
    main()
