# ReBL results

| Bugs | Success | Fail |
|---|---:|---:|
| Crash | 5 | 12 |
| Non-crash | 29 | 54 |
| Total | 34 | 66 |

## Estimated Gemini cost

ReBL's logs record no token usage, so its cost was not measured. Estimate:
**about US$45–54 for the 100 runs** (US$0.45–0.54 per bug), and US$38–81 if
thinking tokens per call range from 500 to 2,000.

| Thinking tokens per call | 12-message history window | Full history |
|---|---:|---:|
| 500 | US$38 | US$47 |
| ~800 | US$45 | US$54 |
| 2,000 | US$72 | US$81 |

How it was estimated:

- About 2,250 LLM calls in the 100 logs, text only (no screenshots).
- Input: about 20M tokens with the code's default 12-message history window,
  about 27M if the full history was resent. Each prompt was rebuilt from the
  log (few-shot preamble, bug report, history, current screen) at 4 characters
  per token. No prompt reaches Gemini's 200k-token long-prompt rate.
- Output: about 0.17M visible tokens plus thinking tokens, which the logs do
  not show; ~800 per call is AdbGPT's measured mean on the same model.
- gemini-2.5-pro at US$1.25 per 1M input and US$10 per 1M output tokens, the
  rates used for the AdbGPT and ReActDroid costs.
- Calls retried after rate limits are not counted.
