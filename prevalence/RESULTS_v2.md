# Gesture prevalence, extended study (v2)

How often do Android bug reports need a gesture beyond tap and text input,
and in particular a complex or precision gesture (pinch-to-zoom, drag-and-drop,
region/coordinate swipe, timing-sensitive tap, picker scroll, multi-finger)
that current LLM-driven reproduction tools cannot express?

The original study (v1: `raw_random_bugs.jsonl`, `random_gesture_bugs.csv`,
`crawl_gesture_prevalence.py`) is kept unchanged. This extension adds four
sources and a corrected classification.

## Sources (none selected for gestures)

| Source | File | Reports | Collection |
|---|---|---:|---|
| GitHub issues, original sample (v1) | `raw_random_bugs.jsonl` | 3,629 | 325 projects via `topic:android`; at most 15 bug-labelled issues each |
| GitHub issues, new sample (v2) | `raw_v2_issues.jsonl` | 10,000 | `crawl_v2.py`: 1,362 further projects (4,727 examined); the same neutral queries sliced by language, stars and recent push, in a seeded random order; **fixed stopping rule** |
| GitHub fix pull requests | `raw_v2_prs.jsonl` | 6,941 | `crawl_v2.py --prs`: merged PRs titled "fix", from 934 of the v2 projects |
| F-Droid apps outside GitHub | `raw_fdroid_issues.jsonl` | 1,595 | `crawl_fdroid.py`: every F-Droid app whose tracker is on GitLab, Framagit or Codeberg (661; 188 have bug-labelled issues) |
| Published benchmarks | `raw_benchmarks.jsonl` | 12,120 | `crawl_benchmarks.py`: ReActDroid's 11,821 crash reports (its motivational study), AndroR2 (91), ReCDroid (62), Themis (51), ReBL (95) |

**Note on v1:** `crawl_gesture_prevalence.py` kept crawling until every complex
category had a minimum count. That is a data-dependent stopping rule, which can
bias the estimate upward. v2 uses a fixed target instead.

## Classification

1. **Keyword scan:** v1's regular expressions, unchanged (`classify.py` reuses them).
   Each report gets one tier (complex, simple or none) by a fixed priority.
2. **LLM relabelling:** `llm_label.py`, Gemini 2.5 Flash, temperature 0, with the
   written rubric in the script. Per source, it labels every keyword-flagged report
   and a random 400 of the unflagged ones; the benchmarks are labelled in full.
   4,552 labels cost US$4.47.
3. **Author check (pending):** every LLM-positive report is listed in
   `to_verify.csv` (318). Fill in `verified_label` and save as
   `verified_labels.csv` (columns `url`, `verified_label`). `estimate.py` then
   uses those labels in place of the LLM's.
4. **Estimate:** `estimate.py`, a stratified two-phase estimate per source (keyword
   tier as stratum), with a 95% CI that includes a finite-population correction.

## Results (LLM-corrected, before the author check)

| Source | Reports | Keyword estimate | Corrected estimate (95% CI) | Beyond tap/text: keyword → corrected | Labelled |
|---|---:|---:|---:|---:|---:|
| GitHub issues (v1 sample) | 3,629 | 43 (1.18%) | 117 (3.22%; 2.06–4.39%) | 9.1% → 9.7% | 730 |
| GitHub issues (v2 sample) | 10,000 | 85 (0.85%) | 354 (3.54%; 2.02–5.06%) | 7.6% → 8.9% | 1,155 |
| GitHub fix PRs (v2 repos) | 6,941 | 60 (0.86%) | 66 (0.94%; 0.49–1.40%) | 4.6% → 4.3% | 718 |
| F-Droid apps, GitLab/Codeberg | 1,595 | 8 (0.50%) | 30 (1.89%; 0.95–2.83%) | 7.4% → 7.6% | 518 |
| ReActDroid crash reports | 11,821 | 86 (0.73%) | 256 (2.17%; 1.07–3.27%) | 6.2% → 6.9% | 1,132 |
| AndroR2 benchmark | 91 | 0 (0.00%) | 3 (3.30%; 3.30–3.30%) | 22.0% → 25.3% | 91 |
| ReCDroid benchmark | 62 | 2 (3.23%) | 2 (3.23%; 3.23–3.23%) | 21.0% → 24.2% | 62 |
| Themis benchmark | 51 | 0 (0.00%) | 1 (1.96%; 1.96–1.96%) | 5.9% → 7.8% | 51 |
| ReBL benchmark | 95 | 3 (3.16%) | 5 (5.26%; 5.26–5.26%) | 20.0% → 22.1% | 95 |

- The keyword scan alone finds 0.5-1.2% everywhere. After correction, 1.9-3.5% of
  issue reports need a complex or precision gesture; pooled over the four issue
  sources (27,045 reports), about 2.8%.
- The share needing any action beyond tap and text input hardly changes
  (e.g. 9.1% to 9.7%): the scan mainly misses complex gestures that a report
  describes without naming them.
- The LLM labels are noisy too (e.g. "rapid state changes through the presenter"
  labelled quick_tap). That is why the author check is required before these
  numbers are used.

## Reproduce

```
GITHUB_TOKEN=... python crawl_v2.py --target 10000 --prs
python crawl_fdroid.py --index index-v2.json        # https://f-droid.org/repo/index-v2.json
python crawl_benchmarks.py
python classify.py raw_random_bugs.jsonl raw_v2_issues.jsonl raw_v2_prs.jsonl raw_fdroid_issues.jsonl raw_benchmarks.jsonl
python llm_label.py ...                             # commands in llm_label.py's docstring
python estimate.py
```

Google Play was not crawled: its terms do not allow automated scraping, and
store reviews are not bug reports with reproduction steps.
