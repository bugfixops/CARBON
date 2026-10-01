#!/usr/bin/env python3
"""Check one audited case and PRINT explicit commands for published CARBON.

No device operation or model call is performed. Use a disposable emulator at the
reported Android version and follow REVERIFICATION.md before executing commands.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shlex
import sys


def sha256(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def under(root, relative):
    path = (root / relative).resolve()
    if not path.is_relative_to(root) or not path.is_file():
        raise ValueError('Missing file or path outside dataset: ' + str(relative))
    return path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dataset', required=True, type=Path)
    parser.add_argument('--carbon', required=True, type=Path)
    parser.add_argument('--case', required=True)
    parser.add_argument('--serial', required=True, help='Exact emulator-NNNN serial for published CARBON')
    parser.add_argument('--python', default='python3', help='Python executable in your configured CARBON environment')
    parser.add_argument('--adb', default='adb')
    args = parser.parse_args()
    match = re.fullmatch(r'emulator-(\d+)', args.serial)
    if not match:
        parser.error('Published CARBON requires emulator-NNNN; use an appropriate supervised runner for a physical device.')
    root = args.dataset.resolve()
    carbon = args.carbon.resolve()
    try:
        manifest = json.loads((root / 'manifest.json').read_text())
        matches = [e for e in manifest['included'] + manifest['excluded'] if e['label'] == args.case]
        if len(matches) != 1:
            raise ValueError('Case must match exactly one label in manifest.json')
        e = matches[0]
        if e['report_status'] == 'unavailable':
            raise ValueError('This case has no authentic bug report; no run command will be generated.')
        apk = under(root, e['folder'] + '/' + e['local_apk_name'])
        report = under(root, e['folder'] + '/bug_report.txt')
        meta = json.loads(under(root, e['folder'] + '/meta.json').read_text())
        if meta != e:
            raise ValueError('Per-case metadata differs from manifest')
        if sha256(apk) != e['apk_sha256'] or sha256(report) != e['bug_report_sha256']:
            raise ValueError('APK or report hash differs from audited manifest')
        script = carbon / 'Automation/reproduction.py'
        if not script.is_file():
            raise ValueError('CARBON Automation/reproduction.py was not found')
        code = script.read_text()
        if 'def main(device_port, reprot_file_name)' not in code or 'u2.connect(f"emulator-{device_port}")' not in code:
            raise ValueError('This CARBON checkout has a different command-line interface. Use its explicit supervised runner; this helper covers the audited published interface only.')
        readiness_file = Path(__file__).with_name('case-readiness.json')
        review = next(r for r in json.loads(readiness_file.read_text())['entries'] if r['label'] == e['label'])
        for key in ('apk_sha256', 'bug_report_sha256', 'apk_package', 'main_activity'):
            if review.get(key) != e.get(key):
                raise ValueError('Dataset differs from the reviewed case: ' + key)
    except (OSError, ValueError, KeyError, StopIteration) as exc:
        parser.error(str(exc))
    q = shlex.quote
    print('# Commands only; nothing has been executed.')
    print('# Case:', e['label'], '| review:', review['review_category'])
    print('# APK package:', e['apk_package'], '| version:', e['apk_version_name'], '| SHA-256:', e['apk_sha256'])
    print('# Benchmark Android context:', e.get('android_os'), '| minSdk:', e.get('min_sdk'), '| targetSdk:', e.get('target_sdk'))
    print('# Prefer the original report OS when specified; signature verified only on API', max(int(e.get('min_sdk') or 1), 18), 'through 35.')
    print('# Native ABIs:', ', '.join(e.get('native_abis', [])) or 'No native libraries packaged')
    print('# Review:', review['review_note'])
    print('# Setup:', review['setup_note'])
    print('# First check device API and ABI; use the reported OS and a clean disposable snapshot.')
    prefix = [args.adb, '-s', args.serial]
    for argv in [prefix + ['shell', 'getprop', 'ro.build.version.sdk'], prefix + ['shell', 'getprop', 'ro.product.cpu.abilist']]:
        print(shlex.join(argv))
    print('# After verifying compatibility: install into a snapshot without this package already installed.')
    print(shlex.join(prefix + ['install', '-t', str(apk)]))
    print('# Complete the setup above. Do not pre-grant permissions whose absence triggers the bug.')
    print(shlex.join(prefix + ['shell', 'am', 'start', '-W', '-n', e['apk_package'] + '/' + e['main_activity']]))
    print('# Verify the target app is foreground immediately before running CARBON.')
    print(shlex.join(prefix + ['shell', 'dumpsys', 'activity', 'activities']))
    print('# The next command starts CARBON and can make paid model calls. Capture logcat/video separately.')
    print('cd ' + q(str(carbon / 'Automation')))
    print(shlex.join([args.python, '-u', 'reproduction.py', match[1], str(report)]))
    return 0


if __name__ == '__main__':
    sys.exit(main())
