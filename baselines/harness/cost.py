"""Cost of the AdbGPT / ReActDroid retest on Gemini 2.5 Pro.

  python harness/cost.py estimate      # projection before running anything
  python harness/cost.py actual        # real spend from results/*/llm_usage.jsonl,
                                       # plus a projection for the cases not yet run

Prices: Vertex AI gemini-2.5-pro, $1.25 / 1M input tokens and $10 / 1M output
tokens (thinking included) for prompts up to 200k tokens.

Estimate inputs (measured where possible):
  * AdbGPT guided-replay prompt: 1,550 tokens median (upstream encoder run on the
    376 screens saved by the earlier run). Its replay keeps one conversation,
    so call k re-sends the k-1 earlier prompts and answers.
  * AdbGPT extraction prompt: ~1,200 tokens of few-shot text + the bug report
    (604 tokens median over the 100 reports).
  * AdbGPT calls per run: median 6 extracted steps (earlier run); scenarios below.
  * ReActDroid prompt: system ~300 + crash description + the last 5
    observation/answer pairs + the current page, ~3,750 tokens.
  * ReActDroid steps: it stops only on a crash, so a run that never sees one
    uses the whole 1,800 s budget, about 70-120 steps at 15-25 s per step.
  * Thinking tokens per call are not visible in the earlier logs (CARBON's
    usage log did not record them), so three levels are shown. The pilot run's
    llm_usage.jsonl replaces these guesses with measured numbers.
"""
import argparse
import glob
import json
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from harness.gemini_client import call_cost, usage_totals  # noqa: E402

MODEL = "gemini-2.5-pro"
THINKING = {"low": 300, "mid": 800, "high": 1500}


def adbgpt_run_cost(guided_calls, thinking, spend_cap):
    extraction_in, extraction_out = 1200 + 604, 600
    cost = call_cost(MODEL, extraction_in, extraction_out + thinking)
    for k in range(1, guided_calls + 1):
        prompt = 1600 * k + 150 * (k - 1)
        cost += call_cost(MODEL, prompt, 150 + thinking)
        if spend_cap and cost >= spend_cap:
            return spend_cap, k + 1
    return cost, guided_calls + 1


def reactdroid_run_cost(steps, thinking, spend_cap):
    cost = steps * call_cost(MODEL, 3750, 70 + thinking)
    return (min(cost, spend_cap) if spend_cap else cost), steps


def estimate(args):
    cap = args.spend_cap
    print(f"Gemini 2.5 Pro, spend cap ${cap:.2f}/run" if cap else "Gemini 2.5 Pro, no spend cap")
    print(f"\nAdbGPT on {args.adbgpt_cases} bugs: typical / long / runaway replay")
    print(f"{'thinking':>9} {'typical(8 calls)':>17} {'long(20)':>9} {'runaway':>8} {'per run':>8} {'total':>8}")
    # scenario mix: share of runs that are typical / long / runaway
    mixes = {"low": (0.75, 0.20, 0.05), "mid": (0.70, 0.20, 0.10), "high": (0.60, 0.20, 0.20)}
    adb_totals = {}
    for level, t in THINKING.items():
        typ, _ = adbgpt_run_cost(8, t, cap)
        lng, _ = adbgpt_run_cost(20, t, cap)
        run, _ = adbgpt_run_cost(90, t, cap)  # stopped by the cap or the 30-min budget
        a, b, c = mixes[level]
        per_run = a * typ + b * lng + c * run
        adb_totals[level] = per_run * args.adbgpt_cases
        print(f"{level:>9} {typ:>16.2f}$ {lng:>8.2f}$ {run:>7.2f}$ {per_run:>7.2f}$ {adb_totals[level]:>7.0f}$")

    print(f"\nReActDroid on {args.reactdroid_cases} bugs (runs that see no crash use the full 1,800 s)")
    print(f"{'thinking':>9} {'steps/run':>10} {'per run':>8} {'total':>8}")
    steps_for = {"low": 70, "mid": 90, "high": 120}
    rd_totals = {}
    for level, t in THINKING.items():
        per_run, _ = reactdroid_run_cost(steps_for[level], t, cap)
        rd_totals[level] = per_run * args.reactdroid_cases
        print(f"{level:>9} {steps_for[level]:>10} {per_run:>7.2f}$ {rd_totals[level]:>7.0f}$")

    print("\nCombined (plus about $5 for a pilot of 2-3 cases per tool):")
    for level in THINKING:
        print(f"  {level:>4}: ${adb_totals[level] + rd_totals[level]:,.0f}")


def actual(args):
    root = Path(args.out)
    for tool in ("adbgpt", "reactdroid"):
        runs = sorted(glob.glob(str(root / tool / "*" / "*" / "run.json")))
        if not runs:
            print(f"{tool}: no runs yet")
            continue
        tot = {"calls": 0, "prompt_tokens": 0, "output_tokens": 0, "thought_tokens": 0, "cost_usd": 0.0}
        cases = set()
        for r in runs:
            usage = usage_totals(os.path.join(os.path.dirname(r), "llm_usage.jsonl"))
            for k in tot:
                tot[k] += usage[k]
            cases.add(json.loads(Path(r).read_text())["case"])
        n = len(runs)
        print(f"{tool}: {n} runs over {len(cases)} cases, ${tot['cost_usd']:.2f} total, "
              f"${tot['cost_usd'] / n:.3f}/run, {tot['calls'] / n:.1f} calls/run, "
              f"{tot['thought_tokens'] / max(tot['calls'], 1):.0f} thinking tokens/call")
        scope = args.adbgpt_cases if tool == "adbgpt" else args.reactdroid_cases
        remaining = max(scope - len(cases), 0)
        if remaining:
            print(f"   projected for the remaining {remaining} cases: ${tot['cost_usd'] / n * remaining:.0f}")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("mode", choices=["estimate", "actual"])
    p.add_argument("--adbgpt-cases", type=int, default=100)
    p.add_argument("--reactdroid-cases", type=int, default=17)
    p.add_argument("--spend-cap", type=float, default=3.0)
    p.add_argument("--out", default=str(HERE.parent / "results"))
    args = p.parse_args()
    estimate(args) if args.mode == "estimate" else actual(args)


if __name__ == "__main__":
    main()
