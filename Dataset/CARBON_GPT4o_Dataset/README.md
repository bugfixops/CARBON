# CARBON_GPT4o_Dataset — CARBON on GPT-4o

CARBON's **GPT-4o** run over the same 100-bug gesture-diverse benchmark used for the main
results, grouped here so the GPT-4o campaign can be read on its own.

| | |
|---|---|
| Bugs | 100, across the 8 gesture categories |
| Backing LLM | GPT-4o |
| Result | **81 success / 19 failed (81.0%)** — see the caveat below |
| Contents | 100 `carbon_gpt4o_log.txt` files, nothing else |

## Layout

```
CARBON_GPT4o_Dataset/
  double_tap/     21    drag_and_drop/   9    long_press/    9    orientation/   6
  pinch_zoom/     12    quick_tap/       7    scroll/        6    swipe/        30
      <Owner>_<Repo>_<Issue> Tested[ F]/carbon_gpt4o_log.txt
```

The bug folder names are preserved exactly as they appear in the benchmark, including the
nine trailing-` F` variants such as `FossifyOrg_Clock_156 Tested F`. Do not normalise them.

These files are **copies**. Each one also lives beside its bug in
[`../gesture-category-testing/`](../gesture-category-testing/), next to that bug's
`bug_report.txt`, the Gemini 2.5 Pro log (`carbon_log.txt`), and the baseline-tool logs. Go
there for a bug's full context; come here to read the GPT-4o campaign as a set.

Only logs are stored here. The benchmark APKs are not tracked anywhere in this repository —
they are distributed through the Google Drive archive linked from the root
[`README.md`](../../README.md).

## The 81/100 figure, and why it is not directly comparable to 88/100

Both [`../../CARBON_gemini-2.5-pro_vs_gpt-4o.md`](../../CARBON_gemini-2.5-pro_vs_gpt-4o.md)
and [`../../TEST_DATA_SUMMARY_GPT-4O.md`](../../TEST_DATA_SUMMARY_GPT-4O.md) independently
report 81 success / 19 failed (81.0%) over the 100 bugs, with the same per-category split as
the folder counts above. The comparison itself lives in those two files; this README does not
re-derive it.

Those documents also state the methodology difference, and it matters:

- The **GPT-4o** figure resolves each bug by the **agent's own final verdict in the log
  transcript**. Where a bug has several run attempts, a SUCCESS attempt is preferred; failing
  that, the fullest FAILED log is used. The source logs are the 188 runs in
  [`../../Results-retest-merge/`](../../Results-retest-merge/).
- The **Gemini 2.5 Pro** 88/100 is the **audit-confirmed** six-criterion number from the main
  CARBON results table.

So the two numbers are not produced by the same procedure, and the gap between them should not
be read as a clean like-for-like model delta. For the per-bug agreement analysis — 79 both
succeed, 10 both fail, 11 diverge — see `../../CARBON_gemini-2.5-pro_vs_gpt-4o.md`.

Scope note from that document: the comparison covers the 100-bug benchmark only. The 9-bug
ReBL Failure Challenge Set is excluded because no GPT-4o run exists for it, and the other
tools (ReBL, ReActDroid, AdbGPT) are out of scope there by request.

One discrepancy worth flagging rather than silently fixing:
`../../CARBON_gemini-2.5-pro_vs_gpt-4o.md` cites its GPT-4o source as
`TEST_RESULTS_SUMMARY.md`, but the file present in this repository is
`TEST_DATA_SUMMARY_GPT-4O.md`. The numbers in the two documents agree, so this looks like a
stale filename reference; it was left as-is rather than edited.
