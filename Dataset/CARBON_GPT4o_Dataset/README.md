# CARBON_GPT4o_Dataset — CARBON on GPT-4o

CARBON's **GPT-4o** run over the same 100-bug gesture-diverse benchmark used for the main
results, grouped here so the GPT-4o campaign can be read on its own.

| | |
|---|---|
| Bugs | 100, across the 8 gesture categories |
| Backing LLM | GPT-4o |
| Results | see [`RESULTS.md`](RESULTS.md) — pass/fail counts, the per-category split, and a per-case table with the cause of every failure |
| Contents | 100 `carbon_gpt4o_log.txt` files, plus `RESULTS.md` and this README |

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
[`../category-testing-gemini-2.5-pro/`](../category-testing-gemini-2.5-pro/), next to that bug's
`bug_report.txt`, the Gemini 2.5 Pro log (`carbon_log.txt`), and the baseline-tool logs. Go
there for a bug's full context; come here to read the GPT-4o campaign as a set.

Only logs are stored here. The benchmark APKs are not tracked anywhere in this repository —
they are distributed through the Google Drive archive linked from the root
[`README.md`](../../README.md).

## Results

The pass/fail counts, the per-category split, the full per-case table and the cause of every
failure are in [`RESULTS.md`](RESULTS.md). This README does not restate them, so there is one
tally for this campaign and one place to correct it.

Two things that document states and that are worth knowing before comparing models:

- The **GPT-4o** figure resolves each bug by the **agent's own final verdict in the log
  transcript**. Where a bug has several run attempts, a SUCCESS attempt is preferred; failing
  that, the fullest FAILED log is used. The source logs are the 188 runs in
  [`../../Results-retest-merge/`](../../Results-retest-merge/).
- The **Gemini 2.5 Pro** figure for the same 100 bugs is the **audit-confirmed**
  six-criterion number in the root [`RESULTS.md`](../../RESULTS.md).

The two are not produced by the same procedure, so the gap between them should not be read as
a clean like-for-like model delta. For the per-bug agreement analysis see
[`../CARBON_gemini-2.5-pro_vs_gpt-4o.md`](../CARBON_gemini-2.5-pro_vs_gpt-4o.md).

Scope note from that document: the comparison covers the 100-bug benchmark only. The 9-bug
ReBL Failure Challenge Set is excluded because no GPT-4o run exists for it, and the other
tools (ReBL, ReActDroid, AdbGPT) are out of scope there by request.

One stale reference worth flagging rather than silently fixing:
[`../CARBON_gemini-2.5-pro_vs_gpt-4o.md`](../CARBON_gemini-2.5-pro_vs_gpt-4o.md) cites its
GPT-4o source as `TEST_RESULTS_SUMMARY.md`, a filename that has never been present in this
repository. That source is this folder's [`RESULTS.md`](RESULTS.md), which was previously
`Dataset/TEST_DATA_SUMMARY_GPT-4O.md`. The comparison document is kept unedited by request, so
the stale name remains in it.
