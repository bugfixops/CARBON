#!/usr/bin/env python3
"""Restore the audited, checksum-pinned dataset without changing report provenance.

Reports are rendered from the committed source_report.json snapshots. Live issue
pages are deliberately not substituted into this frozen benchmark. A fresh crawl
requires review, new snapshots, new hashes, and re-running the validator.
"""
import argparse
import json
from pathlib import Path
import shutil
import subprocess
import sys

from validate_rebl_dataset import HERE, inspect_apk, render_report, sha256


def verify_apk(path, entry):
    if path.stat().st_size != entry['apk_bytes']:
        raise ValueError('APK size differs from manifest')
    if sha256(path) != entry['apk_sha256']:
        raise ValueError('APK SHA-256 differs from manifest')
    actual = inspect_apk(path)
    if actual['apk_package'] not in entry['expected_packages']:
        raise ValueError('Wrong Android package')
    for key in ('apk_version_name', 'apk_version_code'):
        if actual[key] != entry[key]:
            raise ValueError(f'APK {key} differs from manifest')
    if not actual['signature_present'] or not actual['main_activity']:
        raise ValueError('Missing signature structure or launch activity')


def download_apk(entry, target):
    temp = target.with_suffix('.apk.part')
    try:
        result = subprocess.run(['curl', '--fail', '--location', '--silent', '--show-error',
                                 '--retry', '2', '--max-time', '300', '--output', str(temp), entry['apk_url']],
                                capture_output=True, text=True)
        if result.returncode:
            raise RuntimeError(result.stderr.strip())
        verify_apk(temp, entry)
        temp.replace(target)
    finally:
        temp.unlink(missing_ok=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, default=HERE)
    parser.add_argument('--only', action='append', default=[], help='Exact ReBL label; repeatable')
    parser.add_argument('--limit', type=int)
    parser.add_argument('--dry-run', action='store_true')
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument('--apk-only', action='store_true')
    modes.add_argument('--br-only', action='store_true')
    parser.add_argument('--force', action='store_true', help='Refetch APKs and re-render reports from audited snapshots')
    args = parser.parse_args()
    man = json.loads((HERE / 'manifest.json').read_text())
    entries = man['included'] + man['excluded']
    missing = set(args.only) - {e['label'] for e in entries}
    if missing:
        parser.error(f'Unknown labels: {sorted(missing)}')
    if args.limit is not None and args.limit <= 0:
        parser.error('--limit must be positive')
    if args.only:
        entries = [e for e in entries if e['label'] in args.only]
    if args.limit:
        entries = entries[:args.limit]
    if args.dry_run:
        for e in entries:
            print(f"{e['label']}: {e['apk_pairing']}; report={e['report_status']}; {e['folder']}/{e['local_apk_name']}")
        return 0
    args.out.mkdir(parents=True, exist_ok=True)
    records = []
    for e in entries:
        record = {'label': e['label'], 'errors': [], 'report_status': e['report_status'],
                  'apk_pairing': e['apk_pairing']}
        dest = args.out / e['folder']
        dest.mkdir(parents=True, exist_ok=True)
        try:
            if not args.br_only:
                apk = dest / e['local_apk_name']
                valid = False
                if apk.exists() and not args.force:
                    try:
                        verify_apk(apk, e)
                        valid = True
                    except Exception:
                        pass  # A bad local copy is repaired from its pinned source.
                if not valid:
                    local = HERE / e['folder'] / e['local_apk_name']
                    if local.resolve() != apk.resolve() and local.exists() and not args.force:
                        verify_apk(local, e)
                        temp = apk.with_suffix('.apk.part')
                        shutil.copyfile(local, temp)
                        temp.replace(apk)
                    else:
                        download_apk(e, apk)
                record['apk'] = 'sha256+zip+manifest checked'
            if not args.apk_only:
                if e['report_status'] == 'unavailable':
                    record['errors'].append('Original report unavailable; no replacement text generated')
                    unavailable = HERE / e['folder'] / 'UNAVAILABLE.md'
                    if unavailable.resolve() != (dest / 'UNAVAILABLE.md').resolve():
                        shutil.copyfile(unavailable, dest / 'UNAVAILABLE.md')
                else:
                    src = HERE / e['folder'] / 'source_report.json'
                    snapshot = json.loads(src.read_text())
                    text = render_report(snapshot)
                    import hashlib
                    if hashlib.sha256(text.encode()).hexdigest() != e['bug_report_sha256']:
                        raise ValueError('Source snapshot does not match locked report hash')
                    report = dest / 'bug_report.txt'
                    if args.force or not report.exists() or sha256(report) != e['bug_report_sha256']:
                        report.write_text(text)
                    if src.resolve() != (dest / 'source_report.json').resolve():
                        shutil.copyfile(src, dest / 'source_report.json')
                    record['report'] = 'matches audited source snapshot'
            # Metadata is copied verbatim. A skip or partial run must never erase provenance.
            target_meta = dest / 'meta.json'
            metadata = json.dumps(e, indent=2, ensure_ascii=False) + '\n'
            if not target_meta.exists() or target_meta.read_text() != metadata:
                target_meta.write_text(metadata)
        except Exception as exc:
            record['errors'].append(f'{type(exc).__name__}: {exc}')
        records.append(record)
        print(e['label'], 'FAILED' if record['errors'] else 'OK', '; '.join(record['errors']))
    # A per-run log records its scope explicitly; it is never evidence for an unselected case.
    summary = {'scope': [e['label'] for e in entries], 'apk_only': args.apk_only,
               'br_only': args.br_only, 'ok': [r for r in records if not r['errors']],
               'failed': [r for r in records if r['errors']]}
    (args.out / 'fetch_report.json').write_text(json.dumps(summary, indent=2) + '\n')
    return int(bool(summary['failed']))


if __name__ == '__main__':
    sys.exit(main())
