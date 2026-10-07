"""Compare two authors' exports from check_labels.html: Cohen's kappa per list,
the disagreements to settle, and, once settled, the verified label files that
estimate_sample.py reads.

  python agreement.py ratings_rater1.csv ratings_rater2.csv
      -> prints kappa; writes disagreements.csv (fill its `final` column)
  python agreement.py ratings_rater1.csv ratings_rater2.csv --resolved recheck_final.csv
      -> writes ../verified_labels.csv and ../verified_scope.csv

The two authors' first-round exports are ratings_rater1.csv and ratings_rater2.csv.
They settled the disagreements, and every item both had changed to quick_tap, together
(recheck.html); recheck_final.csv holds the result.
"""
import argparse
import csv
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
GP = HERE.parent


def load(path):
    return {(r["list"], r["url"]): r for r in csv.DictReader(open(path))}


def kappa(pairs):
    n = len(pairs)
    if n == 0:
        return float("nan")
    po = sum(a == b for a, b in pairs) / n
    ca, cb = Counter(a for a, _ in pairs), Counter(b for _, b in pairs)
    pe = sum(ca[k] * cb[k] for k in set(ca) | set(cb)) / (n * n)
    return (po - pe) / (1 - pe) if pe < 1 else 1.0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("a"); ap.add_argument("b"); ap.add_argument("--resolved")
    args = ap.parse_args()
    A, B = load(args.a), load(args.b)
    keys = sorted(set(A) & set(B))
    missing = [k for k in keys if not A[k]["verdict"] or not B[k]["verdict"]]
    if missing:
        print(f"{len(missing)} items lack a verdict from one rater; finish them first.")
    keys = [k for k in keys if k not in missing]
    for lst in sorted({k[0] for k in keys}) + ["all"]:
        ks = [k for k in keys if lst == "all" or k[0] == lst]
        pairs = [(A[k]["verdict"], B[k]["verdict"]) for k in ks]
        agree = sum(a == b for a, b in pairs)
        print(f"{lst:32s} items {len(ks):4d}  agree {agree:4d}  kappa {kappa(pairs):.3f}")
    dis = [k for k in keys if A[k]["verdict"] != B[k]["verdict"]]
    if not args.resolved:
        with open(HERE / "disagreements.csv", "w", newline="") as f:
            w = csv.writer(f); w.writerow(["list", "url", "kind", "llm_label", "rater_a", "rater_b", "final"])
            for k in dis:
                w.writerow([k[0], k[1], A[k]["kind"], A[k]["llm_label"], A[k]["verdict"], B[k]["verdict"], ""])
        print(f"disagreements.csv: {len(dis)} to settle by discussion (fill `final`), then rerun with --resolved.")
        return
    final = {(r["list"], r["url"]): r["final"] for r in csv.DictReader(open(args.resolved)) if r.get("final")}
    unresolved = [k for k in dis if k not in final]
    if unresolved:
        raise SystemExit(f"{len(unresolved)} disagreements have no `final` value")
    trig, scope = [], []
    for k in keys:
        v = final.get(k, A[k]["verdict"])
        (scope if A[k]["kind"] == "scope" else trig).append((k[1], v))
    with open(GP / "verified_labels.csv", "w", newline="") as f:
        w = csv.writer(f); w.writerow(["url", "verified_label"]); w.writerows(trig)
    with open(GP / "verified_scope.csv", "w", newline="") as f:
        w = csv.writer(f); w.writerow(["url", "verified_scope"]); w.writerows(scope)
    print(f"verified_labels.csv: {len(trig)}; verified_scope.csv: {len(scope)}. Now run ../estimate_sample.py.")


if __name__ == "__main__":
    main()
