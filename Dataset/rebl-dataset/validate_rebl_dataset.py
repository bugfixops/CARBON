#!/usr/bin/env python3
"""Offline, fail-closed validation of the packaged ReBL reconstruction."""
import argparse
import csv
import hashlib
import json
from pathlib import Path
import re
import sys
import zipfile

HERE = Path(__file__).resolve().parent


def sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def git_blob_sha(path):
    data = Path(path).read_bytes()
    return hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()


def render_report(snapshot):
    lines = ['Bug Report Title:', snapshot['title'].strip() or '(no title)',
             'Bug Report Issue:', (snapshot.get('body') or '').strip() or '(no description provided)']
    comments = [c['body'] for c in snapshot.get('comments', []) if (c.get('body') or '').strip()]
    if comments:
        lines.append('Comments:')
        for i, body in enumerate(comments, 1):
            lines.extend([f'Comment#{i}:', body.strip(), '---'])
    return ('\n'.join(lines) + '\n').replace('\r\n', '\n').replace('\r', '\n')


def parse_index(text):
    rows = []
    for line in text.splitlines():
        cells = [c.strip() for c in line.strip().strip('|').split('|')]
        label = re.sub(r'\s+', ' ', cells[0]) if cells else ''
        if re.fullmatch(r'(?:\(NC\))?[^|]+#\d+\s*\*?', label):
            rows.append({'label': label, 'crash': not label.startswith('(NC)'),
                         'summarization_applied_by_rebl': '*' in label})
    return rows


def canonical_issue_url(url):
    url = url.lower().rstrip('/').replace('http://', 'https://')
    for old, new in [('github.com/opendatakit/collect', 'github.com/getodk/collect'),
                     ('github.com/k9mail/k-9', 'github.com/thunderbird/thunderbird-android'),
                     ('github.com/themhmoritz3/trainer-app', 'github.com/moritz-herzog/trainer-app'),
                     ('github.com/mozilla-tw/firefoxlite', 'github.com/mozilla-mobile/firefoxlite'),
                     ('gitlab.com/fdroid/fdroidclient/-/issues', 'gitlab.com/fdroid/fdroidclient/issues')]:
        url = url.replace(old, new)
    return re.sub(r'(/issues/\d+).*', r'\1', url)


def inspect_apk(path):
    from androguard.core.apk import APK
    from loguru import logger
    logger.disable('androguard')
    with zipfile.ZipFile(path) as z:
        bad = z.testzip()
        if bad:
            raise ValueError(f'ZIP CRC failure: {bad}')
        names = z.namelist()
        if 'AndroidManifest.xml' not in names or 'classes.dex' not in names:
            raise ValueError('Missing Android manifest or classes.dex')
        if len(names) != len(set(names)):
            raise ValueError('Duplicate ZIP member names')
    a = APK(str(path))
    if not a.is_valid_APK() or not a.get_package():
        raise ValueError('Invalid APK manifest')
    version = a.get_androidversion_name()
    if version and version.startswith('@'):
        version = a.get_res_value(version)
    return dict(apk_package=a.get_package(), apk_version_name=version,
                apk_version_code=a.get_androidversion_code(), min_sdk=a.get_min_sdk_version(),
                target_sdk=a.get_target_sdk_version(), main_activity=a.get_main_activity(),
                signature_present=a.is_signed(),
                native_abis=sorted({n.split('/')[1] for n in names if n.startswith('lib/') and n.endswith('.so')}))


def validate(root, require_complete=False):
    man = json.loads((root / 'manifest.json').read_text())
    entries = man['included'] + man['excluded']
    errors = []
    results = []
    index_path = root / man['index_snapshot']
    index = parse_index(index_path.read_text())
    expected = {r['label']: r for r in index}
    labels = [e['label'] for e in entries]
    if len(labels) != len(set(labels)) or set(labels) != set(expected):
        errors.append('Missing, extra, or duplicate labels compared with pinned ReBL README')
    if len(index) != 96 or sum(e['crash'] for e in index) != 73:
        errors.append('Source index does not contain 73 crash and 23 non-crash cases')
    if len({e['folder'] for e in entries}) != len(entries):
        errors.append('Duplicate folders')
    if man['included_count'] != len(man['included']) or man['excluded_count'] != len(man['excluded']):
        errors.append('Manifest counts do not agree')
    if man['apk_count'] != sum(bool(e.get('local_apk_name')) for e in entries):
        errors.append('APK count does not agree')
    if man['included_bytes'] != sum(e.get('apk_bytes', 0) for e in man['included']):
        errors.append('Included bytes do not agree')
    checksums = {}
    for line in (root / 'SHA256SUMS').read_text().splitlines():
        digest, name = line.split('  ', 1)
        checksums[name] = digest
    for name, digest in checksums.items():
        path = (root / name).resolve()
        if not path.is_relative_to(root.resolve()) or not path.is_file() or sha256(path) != digest:
            errors.append(f'Checksum mismatch or missing file: {name}')
    expected_files = {p.relative_to(root).as_posix() for p in root.rglob('*')
                      if p.is_file() and (p.suffix == '.apk' or p.name in ('bug_report.txt', 'source_report.json', 'meta.json'))}
    if not expected_files <= checksums.keys():
        errors.append('SHA256SUMS is missing packaged APK/report/metadata files')
    mappings = json.loads((root / 'sources/issue_apk_mapping.json').read_text())
    if len(mappings) != len(entries) or {r['label'] for r in mappings} != set(labels):
        errors.append('Issue-to-APK evidence does not cover every entry exactly once')
    signatures = json.loads((root / 'signature_report.json').read_text())['results']
    if len(signatures) != len(entries) or {r['label'] for r in signatures} != set(labels):
        errors.append('Signature evidence does not cover every entry exactly once')
    for e in entries:
        row = {'label': e['label'], 'errors': [], 'warnings': list(e.get('validation_warnings', []))}
        def check(condition, message):
            if not condition:
                row['errors'].append(message)
        if e['label'] in expected:
            for k in ('crash', 'summarization_applied_by_rebl'):
                check(e[k] == expected[e['label']][k], f'Index mismatch: {k}')
        folder = (root / e['folder']).resolve()
        check(folder.is_relative_to(root.resolve()), 'Folder path escapes dataset')
        if row['errors']:
            results.append(row)
            continue
        try:
            evidence = next(r for r in mappings if r['label'] == e['label'])
            check(evidence['issue_url'] == e['issue_url'], 'Mapping evidence has different issue URL')
            check(evidence['apk_pairing'] == e['apk_pairing'], 'Mapping evidence has different qualification')
            table = root / evidence['source_table']
            check(table.is_file(), 'Mapping source table missing')
            if evidence['source_table'].endswith('ReCDroid_tables.json'):
                tables = json.loads(table.read_text())
                check(evidence['record'] in tables['recdroid-journal.xlsx']['sheets']['Basic Information'], 'ReCDroid mapping row missing')
            elif evidence['source_table'].endswith('ReproBot_subjects.csv'):
                with table.open() as stream:
                    check(evidence['record'] in list(csv.DictReader(stream)), 'ReproBot mapping row missing')
            elif table.suffix == '.md':
                records = [[c.strip() for c in line.strip('|').split('|')] for line in table.read_text().splitlines()]
                check(evidence['record'] in records or evidence['record'] in table.read_text().splitlines(), 'Mapping row not present in source table')
            if e['apk_pairing'] == 'benchmark-pinned':
                record_text = json.dumps(evidence['record'])
                source_urls = re.findall(r'https?://[^\s\"<>\)]+', record_text)
                check(canonical_issue_url(e['issue_url']) in [canonical_issue_url(u) for u in source_urls], 'Source table maps the APK to a different issue')
            meta = json.loads((folder / 'meta.json').read_text())
            check(meta == e, 'meta.json differs from manifest entry')
            check(int(e['issue']) == int(re.search(r'#(\d+)\s*\*?$', e['label'])[1]), 'Issue number differs from label')
            if e.get('local_apk_name'):
                path = folder / e['local_apk_name']
                check(path.stat().st_size == e['apk_bytes'], 'APK size mismatch')
                check(sha256(path) == e['apk_sha256'], 'APK SHA-256 mismatch')
                if e.get('apk_git_blob_sha'):
                    check(git_blob_sha(path) == e['apk_git_blob_sha'], 'APK differs from pinned upstream Git blob')
                actual = inspect_apk(path)
                check(actual['apk_package'] in e['expected_packages'], 'Wrong Android package')
                for k, v in actual.items():
                    check(e.get(k) == v, f'APK manifest mismatch: {k}')
                check(actual['signature_present'], 'APK has no signature structure')
                signature = next(r for r in signatures if r['label'] == e['label'])
                check(signature['apk_sha256'] == e['apk_sha256'], 'Signature evidence is for a different binary')
                check(signature['compatible_api_check']['exit_code'] == 0, 'Cryptographic signature verification did not pass')
                check(signature['exit_code'] == e['signature_verification']['default_verify_exit_code'], 'Signature compatibility warning changed')
                check(bool(actual['main_activity']), 'APK has no launchable activity')
            if e['report_status'] != 'unavailable':
                snapshot = json.loads((folder / 'source_report.json').read_text())
                check(snapshot['issue_url'] == e['issue_url'], 'Report source URL mismatch')
                check(snapshot['issue_number'] == e['issue'], 'Report source issue mismatch')
                check(not snapshot.get('is_pull_request'), 'Report is a pull request')
                check(not snapshot.get('notes_has_next_page', False), 'GitLab notes pagination incomplete')
                if snapshot['source'] in ('github-api', 'gitlab-rest+graphql'):
                    check(snapshot['declared_comments'] == len(snapshot['comments']), 'Incomplete comment pagination')
                check((folder / 'bug_report.txt').read_text() == render_report(snapshot), 'Report differs from source snapshot')
                check(sha256(folder / 'bug_report.txt') == e['bug_report_sha256'], 'Report SHA-256 mismatch')
            else:
                check(not (folder / 'bug_report.txt').exists(), 'Unavailable report replaced with fabricated text')
            if require_complete:
                check(e['report_status'] == 'complete', 'Report unavailable, partial, or archival')
                check(e['apk_pairing'] == 'benchmark-pinned', 'APK is not issue-pinned by a benchmark')
                check(not (e.get('version_warning') or e.get('source_table_version_warning')), 'Upstream version metadata disagrees with APK')
                check(e.get('runtime_status') == 'reproduced', 'Runtime reproduction not verified')
        except Exception as exc:
            row['errors'].append(f'{type(exc).__name__}: {exc}')
        results.append(row)
    return {'validation_scope': 'offline static packaging and recorded provenance/signature evidence; signatures are not rerun and runtime is not tested',
            'entries': len(entries), 'errors': errors, 'failed': sum(bool(r['errors']) for r in results),
            'results': results}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=HERE)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--require-complete', action='store_true', help='Fail unless every case has complete live report, benchmark APK, matching version metadata, and runtime reproduction')
    args = parser.parse_args()
    report = validate(args.root, args.require_complete)
    if args.output:
        args.output.write_text(json.dumps(report, indent=2) + '\n')
    print(f"Checked {report['entries']} cases; {report['failed']} failed; {len(report['errors'])} dataset errors")
    for error in report['errors']:
        print('ERROR:', error)
    for r in report['results']:
        for error in r['errors']:
            print(r['label'], error)
    return int(bool(report['errors'] or report['failed']))


if __name__ == '__main__':
    sys.exit(main())
