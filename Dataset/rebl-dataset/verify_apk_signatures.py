#!/usr/bin/env python3
"""Repeat cryptographic APK verification using Android SDK Build Tools apksigner."""
import argparse
import json
from pathlib import Path
import subprocess
import sys

from validate_rebl_dataset import HERE, sha256


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--apksigner', default='apksigner', help='Path to Android SDK apksigner executable')
    parser.add_argument('--output', type=Path, default=HERE / 'signature_recheck.json')
    args = parser.parse_args()
    manifest = json.loads((HERE / 'manifest.json').read_text())
    results = []
    for entry in manifest['included'] + manifest['excluded']:
        apk = HERE / entry['folder'] / entry['local_apk_name']
        if sha256(apk) != entry['apk_sha256']:
            raise ValueError(f"{entry['label']}: APK does not match audited hash")
        minimum = max(int(entry.get('min_sdk') or 1), 18)
        result = subprocess.run([args.apksigner, 'verify', '--verbose', '--print-certs',
                                 '--min-sdk-version', str(minimum), '--max-sdk-version', '35', str(apk)],
                                capture_output=True, text=True)
        results.append({'label': entry['label'], 'apk_sha256': entry['apk_sha256'],
                        'min_api': minimum, 'max_api': 35, 'exit_code': result.returncode,
                        'stdout': result.stdout, 'stderr': result.stderr})
        print(entry['label'], 'PASS' if result.returncode == 0 else 'FAIL')
    args.output.write_text(json.dumps(results, indent=2) + '\n')
    return int(any(r['exit_code'] for r in results))


if __name__ == '__main__':
    sys.exit(main())
