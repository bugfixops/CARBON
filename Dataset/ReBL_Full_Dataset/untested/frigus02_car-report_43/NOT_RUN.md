# Not run — input case only

This case is part of the ReBL dataset **inputs** but was never executed in this campaign, so it has no
`carbon_log.txt` and no verdict. It is excluded from the 95-case denominator:

```
96 input cases − 95 executed = 1 (this case)
```

## Why it was not run

The original bug report was never recovered, so there are no reproduction steps to give the agent. The
case therefore holds `meta.json`, the pinned APK and `UNAVAILABLE.md`, but **no** `bug_report.txt` and
**no** `source_report.json`.

Per `meta.json`:

- `"flag": "BUG_REPORT_NOT_FOUND"`
- `"report_status": "unavailable"`
- `"runtime_status": "not_run"`
- `"reason"`: the Bitbucket API returned HTTP 410 (deprecated), the live issue was inaccessible, and
  Wayback queries returned no captures.

`UNAVAILABLE.md` records the same finding and the instruction it was kept under: do not run the case with
invented reproduction steps, and do not include it in completed-case denominators. It also notes that the
absence of a Wayback capture does not prove no archive exists anywhere.

`../../DATASET_PROVENANCE.md` states the same at dataset level: "CarReport#43 still lacks its report."

## What is preserved here

| File | Notes |
|---|---|
| `car-report_43.apk` | The benchmark-pinned ReCDroid APK, kept so the case stays reconstructible if the report is ever recovered |
| `meta.json` | Full metadata, including APK provenance and signature-verification results |
| `UNAVAILABLE.md` | The original record of why the report could not be retrieved |

See `../../README.md` for the campaign as a whole and `../../RETEST_SUMMARY.md` for the 95-case result.
