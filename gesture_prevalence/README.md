# Gesture-Prevalence Dataset

`random_gesture_bugs.csv` — **3,629 Android bug reports** from open-source GitHub
projects, sampled app- and gesture-neutrally. It measures how often real bug
reports require a UI gesture beyond a basic tap or text input, and how often they
require a **complex/precision gesture** the studied baselines (ReBL, AdbGPT,
ReActDroid) cannot express.

## How it was built
1. **Discovery (no app/gesture terms):** GitHub repository search on the
   `topic:android` tag, faceted by language and recent activity.
2. **Issue collection:** bug-labeled issues (open + closed), capped per project so
   no app dominates. No gesture filtering.
3. **Classification:** a keyword scan over each report's title + body assigns one
   primary gesture and a tier (`complex`, `simple`, or `none`).

Reproduce with `crawl_gesture_prevalence.py` (raw text in `raw_random_bugs.jsonl`).

## Results (3,629 reports)
| Tier | Reports | % |
|---|---|---|
| Complex / precision (baselines cannot express) | 43 | 1.2% |
| Simple (a baseline supports it coarsely) | 288 | 7.9% |
| None (tap / text only) | 3,298 | 90.9% |
| **Any gesture beyond tap/text** | **331** | **9.1%** |

Among the 331 action-related reports, **13.0% (43)** need a complex/precision gesture.

**Complex / precision:** pinch-to-zoom 14 · drag-and-drop 12 · region/coordinate
swipe 8 · quick-tap 5 · picker-scroll 2 · multi-touch 2.

**Simple:** scroll 138 · orientation 63 · swipe 55 · long-press 24 · double-tap 8.

Each bug has one primary gesture, so the tiers do not overlap (43 + 288 + 3,298 = 3,629).

## Files
- `random_gesture_bugs.csv` — labeled dataset (`repo, issue_number, primary_gesture, tier, matched_raw, url, state`)
- `raw_random_bugs.jsonl` — raw crawled report text
- `crawl_gesture_prevalence.py` — crawl + classification script
