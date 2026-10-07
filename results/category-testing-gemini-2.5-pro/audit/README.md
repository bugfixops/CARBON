# Audit sheets: 100-bug capability benchmark

One CSV per configuration, one row per bug. They record every success a tool
claimed, the published audit verdict, and the evidence the run's log holds.
`make_audit_sheets.py` rebuilds them from the logs in the bug folders.

| File | Configuration | Claimed successes | Pass the audit |
|---|---|---:|---:|
| `carbon_audit.csv` | CARBON (Gemini 2.5 Pro) | 92 | 88 |
| `rebl_audit.csv` | ReBL (Gemini 2.5 Pro) | 50 | 34 |
| `carbon_no_annotation_audit.csv` | CARBON-NoAnnotation | 61 | 61 |
| `carbon_no_screenshot_audit.csv` | CARBON-NoScreenshot | 47 | 47 |
| `carbon_no_logcat_audit.csv` | CARBON-NoLogcat (`no_oracle` in the file names) | 94 | 77 |

AdbGPT's and ReActDroid's sheets are in
[`../../baseline-retest-gemini-2.5-pro/audit/`](../../baseline-retest-gemini-2.5-pro/audit/).

## Columns

- `claimed`: the tool's own final verdict in its log (`success`, `fail`, or `none` when the run ended without one).
- `audited`: the published verdict (the log banner's `Status`, the same as `RESULTS.md`).
- `actions`, `duration_s`: criteria 2 and 3, from the log's end marker (the last run when a log
  holds two). A run that ended without one (the budget ran out, or an error) takes its length from
  the harness's `Execution Time` line. Both are blank when the log kept no transcript (seven
  No-Annotation runs, all failures).
- `evidence_kind` (criterion 5, claimed successes only):
  - `logcat`: CARBON's logcat feedback reported a `FATAL EXCEPTION` or `ANR` line during the run (`evidence` quotes it);
  - `screen`: no such line; the claim rests on what the run's screens showed (`evidence` quotes the tool's stated reason);
  - `recording`: confirmed on the screen-recorded audit re-run (five CARBON bugs).
- `audit_note`: why a claimed success was rejected. CARBON's and ReBL's rejections carry the reason; the ablations' are marked "Rejected on audit."

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
