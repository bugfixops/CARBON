# Audits

Every audit reported in the paper is in this folder.

| Folder | What was audited | Result |
|---|---|---|
| [`prevalence-labels/`](prevalence-labels/) | The LLM's labels in the prevalence study (paper, Section 2.2), checked independently by two authors | 508 items, Cohen's κ = 0.915 |
| [`reproduction-claims/gesture-benchmark/`](reproduction-claims/gesture-benchmark/) | The 100-bug gesture benchmark: every success claim of CARBON, its three ablations and ReBL, and every run of AdbGPT and ReActDroid (Section 4.5) | CARBON 88, ReBL 34, AdbGPT 2, ReActDroid 4 |
| [`reproduction-claims/rebl-benchmark/`](reproduction-claims/rebl-benchmark/) | CARBON on ReBL's benchmark, 95 bugs (Section 5.3.2) | 91 claimed, 90 pass |
| [`reproduction-claims/rebl-nine-failures/`](reproduction-claims/rebl-nine-failures/) | CARBON's separate run on the nine bugs that ReBL documents as its failures | 7 claimed, 7 pass |

## Prevalence labels

Two authors judged the same 508 items independently. The files call them
Rater 1 and Rater 2.

| List | Items | Agreed in the first round | Cohen's κ |
|---|---:|---:|---:|
| All gesture and rotation labels of the main rubric (`to_verify_sample.csv`) | 308 | 280 | 0.894 |
| 100 random `none` labels of the main rubric (`to_verify_sample_none100.csv`) | 100 | 91 | 0.827 |
| 100 random `not_gui` labels of the scope rubric (`to_verify_scope_notgui100.csv`) | 100 | 99 | 0.918 |
| **All** | **508** | **470** | **0.915** |

- `to_verify_*.csv`: the items both raters judged, written by
  [`prevalence/estimate_sample.py`](../prevalence/estimate_sample.py).
- `check_labels.html`: the offline page both raters used, built by `make_check_page.py`.
- `ratings_rater1.csv`, `ratings_rater2.csv`: their independent first-round verdicts.
- `recheck.html` and `recheck_final.csv`: the 78 items the raters then settled
  together, built by `make_recheck_page.py`. These are the 38 disagreements and
  40 items that both raters had changed to `quick_tap` although the LLM had not.
- `agreement.py`: computes κ and writes the settled labels to
  `prevalence/verified_labels.csv` and `prevalence/verified_scope.csv`, which the
  prevalence counts use.

To reproduce κ:

```
cd audit/prevalence-labels
python agreement.py ratings_rater1.csv ratings_rater2.csv --resolved recheck_final.csv
```

## Success claims

A success claim counts only if all six criteria hold (paper, Section 4.5):

1. the tool reported success;
2. at least one action reached the device;
3. the run lasted more than 10 s;
4. the log ends cleanly, with no harness or tool error;
5. the evidence that the bug type calls for is present. For a crash bug, this
   is a fatal exception or ANR in the app's own process that matches the report,
   or the reported failure on the screen. For a non-crash bug, it is the reported
   incorrect state in the view hierarchy, a screenshot or a recording;
6. nothing in the tool's own reasoning contradicts the claim.

AdbGPT reports no success of its own, and ReActDroid reports none on non-crash
bugs. Every run of these two tools was therefore audited with three checks: an
action reached the device, the reported trigger was performed, and the reported
behavior is visible.

- `gesture-benchmark/`: one sheet per tool or variant, one row per bug. Its
  [README](reproduction-claims/gesture-benchmark/README.md) explains the columns.
- `rebl-benchmark/carbon_rebl_benchmark_audit.csv`: one row per bug.
  - `claimed` is CARBON's last verdict in its log, and `audited` is `pass` or `fail`.
  - `note`, `evidence` and `log` point into
    [`results/carbon-test-rebl-full-gemini-2.5-pro/`](../results/carbon-test-rebl-full-gemini-2.5-pro/).
  - The rows are taken from that folder's `RESULTS.md` table.
- `rebl-nine-failures/carbon_rebl_nine_failures_audit.csv`: the same columns, plus
  `what_decided_it`. The rows are taken from
  [`results/carbon-test-rebl-failed-gemini-2.5-pro/RESULTS.md`](../results/carbon-test-rebl-failed-gemini-2.5-pro/RESULTS.md).
  All nine bugs are also in the ReBL-benchmark sheet. The two are separate runs,
  and AnkiDroid #6432 has a different verdict in each.

## Not covered by these audits

- CARBON's two re-runs
  ([`results/carbon-retest-1-gemini-2.5-pro/`](../results/carbon-retest-1-gemini-2.5-pro/),
  [`results/carbon-retest-2-gemini-2.5-pro/`](../results/carbon-retest-2-gemini-2.5-pro/)):
  their 84 and 81 count CARBON's own success claims, as the paper states.
- CARBON with GPT-4o ([`results/carbon-test-gpt-4o/`](../results/carbon-test-gpt-4o/)):
  its 81 are CARBON's own verdicts. They were corrected by hand where a review
  overturned a claim, and there is no audit sheet.
- The prevalence counts in the paper's Table 2 also use labels from the other
  rubrics and a word search. The authors' check covers the main rubric's labels
  and 100 of the scope rubric's labels.
