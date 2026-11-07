"""Draw the paper's prevalence sample: 3,500 bug reports chosen at random from
the 10,000 GitHub issues of the v2 crawl (raw_v2_issues.jsonl), which has a
fixed target and no data-dependent stopping rule. The seed is fixed; the draw
looks only at the file order, never at report content.

  python make_sample.py            # writes raw_sample3500.jsonl

Every report in the sample is then labelled (llm_label.py --select all) and
counted by estimate_sample.py.
"""
import json
import random
from pathlib import Path

HERE = Path(__file__).resolve().parent
SEED, SIZE = 20261007, 3500


def main():
    recs = [json.loads(line) for line in open(HERE / "raw_v2_issues.jsonl")]
    pick = sorted(random.Random(SEED).sample(range(len(recs)), SIZE))
    with open(HERE / "raw_sample3500.jsonl", "w") as f:
        for i in pick:
            f.write(json.dumps(recs[i]) + "\n")
    projects = {(recs[i].get("owner"), recs[i].get("repo")) for i in pick}
    print(f"{SIZE} of {len(recs)} reports (seed {SEED}), from {len(projects)} projects")


if __name__ == "__main__":
    main()
