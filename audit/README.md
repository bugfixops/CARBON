# Audits

Every audit reported in the paper is in this folder.

| Folder | What was audited | Result |
|---|---|---|
| [`prevalence-labels/single-author/`](prevalence-labels/single-author/) | The LLM's labels in the prevalence study (paper, Section 2.2): one author's audit of all four rubrics: the first three on 100 random reports, the fourth on the same 100 and the 21 reports it labels | Cohen's κ = 0.69, 0.68, 0.59 and 0.74 |
| [`reproduction-claims/gesture-benchmark/`](reproduction-claims/gesture-benchmark/) | The 100-bug gesture benchmark: every success claim of CARBON, its three ablations and ReBL, and every run of AdbGPT and ReActDroid (Section 4.5) | CARBON 88, ReBL 34, AdbGPT 2, ReActDroid 4 |
| [`reproduction-claims/rebl-benchmark/`](reproduction-claims/rebl-benchmark/) | CARBON on ReBL's benchmark, 95 bugs (Section 5.3.2) | 91 claimed, 90 pass |
| [`reproduction-claims/rebl-nine-failures/`](reproduction-claims/rebl-nine-failures/) | CARBON's separate run on the nine bugs that ReBL documents as its failures | 7 claimed, 7 pass |

## Prevalence labels

One author labeled 100 reports, drawn at random (seed 20261102) from the 3,500
sampled reports, with the first three rubrics. The files are in
[`prevalence-labels/single-author/`](prevalence-labels/single-author/):

- `make_audit_sheet.py` draws the 100 reports and writes `audit_sheet.csv`, the
  sheet to fill, and `rubric_codes.md`, the codes of each rubric.
- `audit_filled_author.csv`: the author's labels.
- `compare.py` compares them with the LLM's labels and writes every difference
  to `disagreements.csv`.

| Rubric | Agreement | Cohen's κ |
|---|---:|---:|
| First: the action that triggers the bug | 92/100 | 0.69 |
| Second: can the bug be reproduced through the app's GUI? | 89/100 | 0.68 |
| Third: the gesture that any step needs, including setup | 80/100 | 0.59 |
| Fourth: six rarer gestures (121 reports, see below) | 113/121 | 0.74 |

The fourth rubric gives a gesture to only 21 of the 3,500 reports, none of them
among the 100, so the same author also labeled all 21:

- `make_rubric4_sheets.py` writes `rubric4_audit_sheet.csv`, the 100 random
  reports and the 21 shuffled together, and `rubric4_codes.md`, the rubric's codes.
- `rubric4_audit_filled_author.csv`: the author's labels. The author used the
  codes of rubrics 1-3 here; a code that is not one of the rubric's six gestures
  counts as `none`, as the rubric defines.
- `rubric4_recheck_filled_author.csv`: the 17 rows labeled `swipe_region` or
  `swipe`, labeled again with the rubric's own codes (the blank sheet is
  `rubric4_recheck_sheet.csv`, from `make_rubric4_sheets.py --recheck`).
- `compare_rubric4.py` compares them with the LLM's labels and writes every
  difference to `rubric4_disagreements.csv`. On the 100 random reports, neither
  the LLM nor the author found one of the six gestures; on the 21, they agree on 13.

To reproduce:

```
cd audit/prevalence-labels/single-author
python compare.py audit_filled_author.csv
python compare_rubric4.py rubric4_audit_filled_author.csv rubric4_recheck_filled_author.csv
```

The prevalence counts also use manual verdicts that replace the LLM's labels
for the items they cover: `prevalence/verified_labels.csv` for every gesture or
rotation label of the first rubric and 100 random `none` labels of it, and
`prevalence/verified_scope.csv` for 100 random `not_gui` labels of the second
rubric. `prevalence-labels/to_verify_*.csv` list these items; they are written by
[`prevalence/estimate_sample.py`](prevalence/estimate_sample.py).

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
- The word search, which the prevalence counts in the paper's Table 2 also use.
