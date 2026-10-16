# ReActDroid results

ReActDroid is built for crash bugs only.

| Bugs | Success | Fail | Gemini cost |
|---|---:|---:|---:|
| Crash | 3 | 14 | US$11.93 |
| Non-crash | 1 | 82 | US$48.13 |
| Total | 4 | 96 | US$60.06 |

Non-crash fails include 5 bugs whose CI jobs failed; no cost was recorded for them.
Costs are the sum of `cost_usd` in [`reactdroid_audit.csv`](../../../audit/reproduction-claims/gesture-benchmark/reactdroid_audit.csv).
