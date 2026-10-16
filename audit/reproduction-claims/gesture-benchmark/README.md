# Audit sheets: 100-bug gesture benchmark

One CSV per configuration, one row per bug. They record every success a tool
claimed, the published audit verdict, and the evidence the run's log holds.

| File | Configuration | Claimed successes | Pass the audit |
|---|---|---:|---:|
| `carbon_audit.csv` | CARBON (Gemini 2.5 Pro) | 92 | 88 |
| `rebl_audit.csv` | ReBL (Gemini 2.5 Pro) | 50 | 34 |
| `carbon_no_annotation_audit.csv` | CARBON-NoAnnotation | 61 | 61 |
| `carbon_no_screenshot_audit.csv` | CARBON-NoScreenshot | 47 | 47 |
| `carbon_no_logcat_audit.csv` | CARBON-NoLogcat (`no_oracle` in the file names) | 94 | 77 |
| `adbgpt_audit.csv` | AdbGPT (Gemini 2.5 Pro) | — (no verdict of its own; all 100 runs audited) | 2 |
| `reactdroid_audit.csv` | ReActDroid (Gemini 2.5 Pro) | 4 | 4 |

The run logs are in [`results/carbon-test-gemini-2.5-pro/`](../../../results/carbon-test-gemini-2.5-pro/)
(CARBON, its ablations and ReBL) and
[`results/baseline-test-gemini-2.5-pro/`](../../../results/baseline-test-gemini-2.5-pro/) (AdbGPT and ReActDroid).

## Columns

The five CARBON and ReBL sheets:

- `claimed`: the tool's own final verdict in its log (`success`, `fail`, or `none` when the run ended without one).
- `audited`: the published verdict (the log banner's `Status`, the same as
  [`results/carbon-test-gemini-2.5-pro/RESULTS.md`](../../../results/carbon-test-gemini-2.5-pro/RESULTS.md)).
- `actions`, `duration_s`: criteria 2 and 3, from the log's end marker (the last run when a log
  holds two). A run that ended without one (the budget ran out, or an error) takes its length from
  the harness's `Execution Time` line. Both are blank when the log kept no transcript (seven
  No-Annotation runs, all failures).
- `evidence_kind` (criterion 5, claimed successes only):
  - `logcat`: CARBON's logcat feedback reported a `FATAL EXCEPTION` or `ANR` line during the run (`evidence` quotes it);
  - `screen`: no such line; the claim rests on what the run's screens showed (`evidence` quotes the tool's stated reason);
  - `recording`: confirmed on the screen-recorded audit re-run (five CARBON bugs).
- `audit_note`: why a claimed success was rejected. CARBON's and ReBL's rejections carry the reason; the ablations' are marked "Rejected on audit."

The AdbGPT and ReActDroid sheets (both tools were audited on every run, with the paper's three checks):

- `status`: how the run ended (`finished`, `spend_cap`, `timeout`, `error`, `llm_error`, or `ci_job_failed` when the CI job failed before or during the run; those bugs count as fails).
- `tool_claim`: the tool's own claim, if any (`replay_finished` for AdbGPT, `crash_detected` for ReActDroid).
- `verdict`: the audit verdict (`SUCCESS` or `FAIL`).
- `criterion_failed`: the first check the run failed: 1, no action reached the device; 2, the reported trigger was not performed; 3, the reported behavior is not visible. It is blank for passes, for `ci_job_failed` bugs, and for two AdbGPT runs whose `evidence` gives the reason.
- `evidence`, `duration_s`, `cost_usd`, and `run_dir` (the run's folder under `results/baseline-test-gemini-2.5-pro/`).

## Crash bugs

ReBL records no logcat, so its five crash-bug passes rest on the screens.
Of CARBON's 13 crash-bug passes, 5 have a logged fatal exception and 8 rest
on the screens (the app closing or restarting, an error screen, or the
failure the report describes). The paper's criterion 5 states this.

## ReBL's 16 rejected claims

All 16 end with an explicit `'result': 'success'`. In 10, the LLM declared
success after performing the report's steps without observing the symptom
("by reaching this screen, we have triggered the condition"). In 6, it cited
a symptom that the log does not show or that is not the reported one.
