# Gesture prevalence: the paper's 3,500-report sample

The paper's prevalence numbers (Section 2.2, Table 1). They come from one
random sample of bug reports, every report labelled.

## Design

1. **Sample** (`make_sample.py` → `raw_sample3500.jsonl`): 3,500 reports drawn
   with a fixed seed (20261007) from the 10,000 bug-labelled GitHub issues of
   the v2 crawl (`raw_v2_issues.jsonl`, 1,362 open-source Android projects,
   gesture-neutral queries, fixed target; see [RESULTS_v2.md](RESULTS_v2.md)).
   The draw uses only the file order. The sample covers 1,066 projects;
   2,636 of its issues are closed.
2. **Labels** (`labels_sample3500_all.jsonl`): every report labelled by
   `llm_label.py`'s rubric (Gemini 2.5 Flash, temperature 0): the action the
   reporter must perform to *trigger* the bug, with a supporting quote.
   Reproduce with
   `python llm_label.py --input raw_sample3500.jsonl --select all --out labels_sample3500_all.jsonl`.
   The 3,500 labels cost US$3.52.
3. **Counts** (`estimate_sample.py`): a report *needs a gesture* when its
   trigger is a common gesture (scroll, swipe, long press, double tap) or a
   complex or precision gesture. An orientation change is a device action and
   is counted separately. Intervals are 95% Wilson intervals. No weights: every
   report is labelled.
4. **Author check:** two authors checked 508 items independently in
   `check/check_labels.html` (offline): the 308 gesture or orientation labels,
   100 random `none` labels and 100 random `not_gui` labels. Their exports are
   `check/ratings_rater1.csv` and `check/ratings_rater2.csv`. They then settled
   every disagreement, and every item both had changed to `quick_tap`, together
   (`check/recheck.html`); `check/recheck_final.csv` holds both raters' answers
   and the settled label. In `check/`,
   `python agreement.py ratings_rater1.csv ratings_rater2.csv --resolved recheck_final.csv`
   reports Cohen's kappa and writes `verified_labels.csv` and `verified_scope.csv`,
   which `estimate_sample.py` uses in place of the LLM's labels.

## Results (after the authors' check)

| Action that triggers the bug | Reports | Share of sample | Share of gesture reports |
|---|---:|---:|---:|
| **Complex or precision gesture** | **95** | 2.7% (2.2–3.3) | **40.1% (34.1–46.4)** |
| &nbsp;&nbsp;Drag-and-drop | 29 | 0.8% | 12.2% |
| &nbsp;&nbsp;Timing-sensitive tap | 19 | 0.5% | 8.0% |
| &nbsp;&nbsp;Region/coordinate swipe | 34 | 1.0% | 14.3% |
| &nbsp;&nbsp;Pinch-to-zoom | 6 | 0.2% | 2.5% |
| &nbsp;&nbsp;Picker scroll | 4 | 0.1% | 1.7% |
| &nbsp;&nbsp;Other multi-finger | 3 | 0.1% | 1.3% |
| **Common gesture** | **142** | 4.1% (3.5–4.8) | 59.9% (53.6–65.9) |
| &nbsp;&nbsp;Scroll | 73 | 2.1% | 30.8% |
| &nbsp;&nbsp;Swipe | 31 | 0.9% | 13.1% |
| &nbsp;&nbsp;Long press | 34 | 1.0% | 14.3% |
| &nbsp;&nbsp;Double tap | 4 | 0.1% | 1.7% |
| **Any gesture** | **237** | **6.8% (6.0–7.7)** | 100% |
| Orientation change (device action) | 62 | 1.8% | |
| Tap, text, navigation only | 3100 | 88.6% | |
| Unclear from the report | 101 | 2.9% | |
| Total | 3,500 | 100% | |

- **6.8% of reports need a gesture, and 40.1% of those (95 of 237) need a
  complex or precision gesture** that ReBL, AdbGPT and ReActDroid cannot
  express. Over the whole sample that is 2.7% of reports.
- CARBON's five gestures that execute as named (`pinch`, `drag_and_drop`,
  `swipe_region`, `quick_tap`, `picker_scroll`) cover 92 of the 95; the other
  three need another multi-finger gesture (a four-finger tap, a two-finger swipe).
- A keyword scan for gesture terms (v1's `classify()`) flags only 17 of the
  95; 59 contain none of its keywords.
- The broader four-source study ([RESULTS_v2.md](RESULTS_v2.md), 27,045
  issue reports) gives a consistent share: 44% of the reports that need a
  gesture need a complex or precision gesture (orientation excluded, as here).
  That study rests on the LLM's labels alone; its author check was not made.

## The authors' check

| List | Items | Agreed in the first round | Cohen's kappa |
|---|---:|---:|---:|
| Gesture or orientation labels (`to_verify_sample.csv`) | 308 | 280 | 0.894 |
| Random `none` labels (`to_verify_sample_none100.csv`) | 100 | 91 | 0.827 |
| Random `not_gui` labels (`to_verify_scope_notgui100.csv`) | 100 | 99 | 0.918 |
| **All** | **508** | **470** | **0.915** |

- The 78 items settled together are the 38 disagreements and the 40 items both
  raters had changed to `quick_tap` although the LLM had not.
- `quick_tap` means a tap whose timing matters: rapid repeated taps, a tap during
  an animation or transition, a tap before a timeout or a dialog closes. In 48 of
  the 78, the settled label was `quick_tap` for a report that needs only ordinary
  taps. By the rubric an ordinary tap is `none`, so those 48 are `none` (the 40
  from the random `none` list) or keep the LLM's label (the 8 from the main
  list); `recheck_final.csv` notes each one.
- Among the 100 random `none` labels the check found no missed gesture (95 stay
  `none`, 5 become `unclear`), so the counts need no weighting.

## Before the check: the LLM's labels

| Action that triggers the bug | Reports | Share of sample | Share of gesture reports |
|---|---:|---:|---:|
| **Complex or precision gesture** | **101** | 2.9% (2.4–3.5) | **41.7% (35.7–48.0)** |
| &nbsp;&nbsp;Drag-and-drop | 30 | 0.9% | 12.4% |
| &nbsp;&nbsp;Timing-sensitive tap | 27 | 0.8% | 11.2% |
| &nbsp;&nbsp;Region/coordinate swipe | 30 | 0.9% | 12.4% |
| &nbsp;&nbsp;Pinch-to-zoom | 7 | 0.2% | 2.9% |
| &nbsp;&nbsp;Picker scroll | 4 | 0.1% | 1.7% |
| &nbsp;&nbsp;Other multi-finger | 3 | 0.1% | 1.2% |
| **Common gesture** | **141** | 4.0% (3.4–4.7) | 58.3% (52.0–64.3) |
| &nbsp;&nbsp;Scroll | 78 | 2.2% | 32.2% |
| &nbsp;&nbsp;Swipe | 26 | 0.7% | 10.7% |
| &nbsp;&nbsp;Long press | 34 | 1.0% | 14.0% |
| &nbsp;&nbsp;Double tap | 3 | 0.1% | 1.2% |
| **Any gesture** | **242** | **6.9% (6.1–7.8)** | 100% |
| Orientation change (device action) | 66 | 1.9% | |
| Tap, text, navigation only | 3102 | 88.6% | |
| Unclear from the report | 90 | 2.6% | |
| Total | 3,500 | 100% | |

With the LLM's labels alone, 6.9% of reports need a gesture and 41.7% of those
(101 of 242) a complex or precision gesture; CARBON's gestures cover 98 of the
101, and the keyword scan flags 17 of them (65 contain none of its keywords).

## Over the GUI-reproducible reports (second labelling pass)

Scope labels: 3,500 (gui 2,597, not_gui 877, unclear 26); checked by the authors: 100
Gesture reports by scope label: {'gui': 228, 'not_gui': 9}

| | Reports | Share |
|---|---:|---:|
| GUI-reproducible reports | 2,597 | 74.2% (72.7–75.6) of the sample |
| Need a gesture | 228 | **8.8% (7.8–9.9)** of GUI-reproducible reports |
| Need a complex or precision gesture | 91 | 39.9% (33.8–46.4) of those; 3.5% (2.9–4.3) of GUI-reproducible reports |
| Need a gesture or an orientation change | 289 | 11.1% (10.0–12.4) of GUI-reproducible reports |

`llm_scope.py` labels whether each report can be reproduced through an app's
GUI at all (same model and settings; rubric in the script; US$3.96). Build and
dependency errors, library-API bugs that need code, server or CI problems,
documentation, and feature requests or questions are `not_gui`; when in doubt
the rubric answers `gui`. A gesture report counts here only if its scope label
is also `gui` (9 of the 237 are not). The complex share is the same as over
the whole sample (40%). The authors checked 100 random `not_gui` labels
(`to_verify_scope_notgui100.csv`), since those labels shrink the base. With the
LLM's scope and trigger labels alone, the base was 2,590 reports and the share
97 of 232 (42%).
