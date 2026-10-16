# Gesture prevalence study

How often do Android bug reports need a gesture, and how often a complex one
that ReBL, AdbGPT and ReActDroid cannot perform? (Paper, Section 2.2.)

## From the crawl to the 2,597 reports

| Step | Script | Output | Reports |
|---|---|---|---:|
| 1. Crawl bug-labelled GitHub issues of open-source Android projects | `crawl_v2.py` | `raw_v2_issues.jsonl` | 10,000 from 1,362 projects |
| 2. Draw a random sample with a fixed seed (20261007) | `make_sample.py` | `raw_sample3500.jsonl` | 3,500 from 1,066 projects |
| 3. Second rubric: can the bug be reproduced through the app's GUI? | `llm_scope.py` | `labels_sample3500_scope.jsonl` | gui 2,590, not_gui 884, unclear 26 |
| 4. Two authors check 100 random `not_gui` labels | [`../audit/prevalence-labels/`](../audit/prevalence-labels/) | `verified_scope.csv` | 7 become gui |
| 5. Keep the GUI-reproducible reports | `count_gestures.py` | | **2,597** |

- **Crawl.** The queries name no app, gesture or action. They combine three
  topic tags (`android`, `android-app`, `android-application`), Java or Kotlin,
  six star ranges and two last-push ranges, skip archived projects and run in
  a seeded random order. The crawl takes at most 15 bug-labelled issues per
  project, open or closed, and stops at 10,000. It skips the 325 projects of an
  earlier pilot crawl (`pilot_repos.txt`), whose reports are not used.
- **Sample.** The draw uses only the file order, never the report text.
- **GUI filter.** It removes 903 reports. The 877 `not_gui` ones need
  something other than the app's UI: build or dependency errors, library bugs
  that only code can trigger, server, CI or documentation problems, and
  feature requests or questions. The 26 `unclear` ones do not say enough to
  decide. When in doubt, the rubric answers `gui`.

## Labels

Every one of the 3,500 reports has four LLM labels and a keyword-scan label.

| Rubric | Question | Script | Labels | Model |
|---|---|---|---|---|
| First | Which action must the reporter perform to trigger the bug? With a quote. | `llm_label.py` | `labels_sample3500_all.jsonl` (`llm_label`) | Gemini 2.5 Flash, temperature 0 |
| Second | Can the bug be reproduced through the app's GUI? | `llm_scope.py` | `labels_sample3500_scope.jsonl` | Gemini 2.5 Flash, temperature 0 |
| Third | Which gesture does any step need, including setup? | `llm_label_loose.py` | `labels_sample3500_loose.jsonl` | Gemini 2.5 Flash, temperature 0 |
| Fourth | Six further gestures: fling, shake, drawing, edge swipe, one-finger zoom, two-finger rotate | `llm_label_extended.py` | `labels_sample3500_extended.jsonl` | Gemini 3.8 Flash, temperature 0 |
| Keyword scan | Fixed regular expressions | `keyword_scan.py` | `labels_sample3500_all.jsonl` (`kw_primary`) | – |

The four rubrics cost US$15.10 in total (3.516, 3.962, 4.000 and 3.626).

Two authors checked 508 items independently (Cohen's κ = 0.915): every gesture
or rotation label of the first rubric (308), 100 random `none` labels of the
first rubric and 100 random `not_gui` labels of the second. Their verdicts are
in `verified_labels.csv` and `verified_scope.csv` and replace the labels they
checked. The third and fourth rubrics were not checked. The ratings and the
check page are in [`../audit/prevalence-labels/`](../audit/prevalence-labels/)
([README](../audit/README.md)).

## Counts over the 2,597 reports

`count_gestures.py` prints the table under two definitions of "needs a
gesture". Each report counts once, as complex when any of its labels is a
complex gesture.

| Definition | Need a gesture | Complex | Common | Complex share of gesture reports |
|---|---:|---:|---:|---:|
| 1. The first rubric's trigger label, checked by the authors | 228 (8.8%) | 91 | 137 | 39.9% (33.8–46.4) |
| 2. Any rubric, the keyword scan or a gesture word | 723 (27.8%) | 262 | 461 | 36.2% (32.8–39.8) |

Definition 2 adds the reports that only the third or fourth rubric, the
keyword scan or the word search (`WORDS` in `count_gestures.py`, outside code
blocks and log lines) flags. None of these was checked, and the third rubric is
deliberately inclusive, so definition 2 is an upper bound. Intervals are 95%
Wilson intervals.

`estimate_sample.py` prints the first rubric's counts over all 3,500 reports
and over the 2,597, and writes the lists the authors checked.

## Reproduce

```
GITHUB_TOKEN=... python crawl_v2.py --target 10000   # GitHub's results change over time
python make_sample.py                                 # rewrites raw_sample3500.jsonl, byte for byte
python llm_label.py --input raw_sample3500.jsonl --select all --out labels_sample3500_all.jsonl
python llm_scope.py
python llm_label_loose.py
python llm_label_extended.py
python estimate_sample.py                             # rewrites the check lists in ../audit/prevalence-labels/
(cd ../audit/prevalence-labels && python agreement.py ratings_rater1.csv ratings_rater2.csv --resolved recheck_final.csv)
python count_gestures.py
```

The labelling scripts need Vertex AI credentials and `GCP_PROJECT_ID` in the
repository's `.env`. They skip reports already in their output files.
