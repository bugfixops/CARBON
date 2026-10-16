# carbon-test-gpt-4o — CARBON on GPT-4o

CARBON's **GPT-4o** run over the same 100-bug gesture-diverse benchmark used for the main
results, grouped here so the GPT-4o campaign can be read on its own.

| | |
|---|---|
| Bugs | 100, across the 8 gesture categories |
| Backing LLM | GPT-4o |
| Results | **81** reproduced, **19** not reproduced; see [`RESULTS.md`](RESULTS.md) |
| Contents | 100 `carbon_gpt4o_log.txt` files (one per bug), [`RESULTS.md`](RESULTS.md), [`CARBON_gemini-2.5-pro_vs_gpt-4o.md`](CARBON_gemini-2.5-pro_vs_gpt-4o.md) and this README |

## Layout

```
carbon-test-gpt-4o/
  double_tap/     21    drag_and_drop/   9    long_press/    9    orientation/   6
  pinch_zoom/     12    quick_tap/       7    scroll/        6    swipe/        30
      <Owner>_<Repo>_<Issue>/carbon_gpt4o_log.txt
```

The bug folder names are the same as in
[`../carbon-test-gemini-2.5-pro/`](../carbon-test-gemini-2.5-pro/), where each bug's
`bug_report.txt`, its Gemini 2.5 Pro log (`carbon_log.txt`) and its ReBL baseline log
(`rebl_log.txt`) live. Go there for a bug's full context; come here to read the GPT-4o
campaign as a set.

Only logs are stored here. The benchmark APKs are not tracked anywhere in this repository —
they are distributed through the Google Drive archive linked from the root
[`README.md`](../../README.md).

## Results

The counts and the reason for every failure are in [`RESULTS.md`](RESULTS.md). The per-bug
comparison with CARBON on Gemini 2.5 Pro is in
[`CARBON_gemini-2.5-pro_vs_gpt-4o.md`](CARBON_gemini-2.5-pro_vs_gpt-4o.md).

Scope note from that comparison: it covers the 100-bug benchmark only. The 9-bug ReBL
Failure Challenge Set is excluded because there is no GPT-4o run for it, and the other tools
(ReBL, ReActDroid, AdbGPT) are out of scope.
