"""Regression checks for the failures found during the dataset audit."""
import contextlib
import copy
import io
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch
import zipfile

import download_rebl_dataset as download
import validate_rebl_dataset as validate


class DatasetRegressionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.man = json.loads((validate.HERE / 'manifest.json').read_text())
        cls.entry = next(e for e in cls.man['included'] if e['label'] == 'Acv#12')
        cls.apk = validate.HERE / cls.entry['folder'] / cls.entry['local_apk_name']

    def test_source_index_preserves_embedded_hash_and_summary_markers(self):
        rows = validate.parse_index((validate.HERE / 'sources/ReBL_README.md').read_text())
        self.assertEqual((len(rows), sum(r['crash'] for r in rows)), (96, 73))
        self.assertTrue(next(r for r in rows if r['label'] == '(NC)FieldBook#137 *')['summarization_applied_by_rebl'])
        self.assertIn('Field#Book#145', [r['label'] for r in rows])

    def test_package_mismatch_fails_even_with_matching_hash_and_size(self):
        entry = copy.deepcopy(self.entry)
        entry['expected_packages'] = ['com.beemdevelopment.aegis']
        with self.assertRaisesRegex(ValueError, 'Wrong Android package'):
            download.verify_apk(self.apk, entry)

    def test_pk_prefix_and_matching_size_are_not_sufficient(self):
        with tempfile.TemporaryDirectory() as temp:
            apk = Path(temp) / 'fake.apk'
            apk.write_bytes(b'PK' + b'0' * (self.entry['apk_bytes'] - 2))
            entry = dict(self.entry, apk_sha256=validate.sha256(apk))
            with self.assertRaises(zipfile.BadZipFile):
                download.verify_apk(apk, entry)

    def test_same_size_corruption_repaired_and_metadata_preserved(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            args = ['download', '--only', 'Acv#12', '--out', str(root)]
            with patch('sys.argv', args), contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(download.main(), 0)
            dest = root / self.entry['folder']
            metadata = (dest / 'meta.json').read_bytes()
            data = bytearray((dest / self.entry['local_apk_name']).read_bytes())
            data[len(data)//2] ^= 1
            (dest / self.entry['local_apk_name']).write_bytes(data)
            for option in ('--apk-only', '--br-only'):
                with patch('sys.argv', args + [option]), contextlib.redirect_stdout(io.StringIO()):
                    self.assertEqual(download.main(), 0)
                self.assertEqual((dest / 'meta.json').read_bytes(), metadata)
            self.assertEqual(validate.sha256(dest / self.entry['local_apk_name']), self.entry['apk_sha256'])

    def test_unknown_label_is_an_error(self):
        with patch('sys.argv', ['download', '--only', 'NotARealCase#123', '--dry-run']), contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit) as raised:
                download.main()
        self.assertEqual(raised.exception.code, 2)

    def test_gitlab_snapshot_has_all_twelve_non_system_comments(self):
        e = next(e for e in self.man['included'] if e['label'] == 'Fdroid#1821*')
        s = json.loads((validate.HERE / e['folder'] / 'source_report.json').read_text())
        self.assertEqual(s['declared_comments'], 12)
        self.assertEqual(len(s['comments']), 12)
        self.assertFalse(s['notes_has_next_page'])
        self.assertEqual(e['report_status'], 'complete')

    def test_archived_report_excludes_composer_preview(self):
        e = next(e for e in self.man['included'] if e['label'] == 'Transistor#149')
        s = json.loads((validate.HERE / e['folder'] / 'source_report.json').read_text())
        self.assertEqual(len(s['comments']), 5)
        self.assertNotIn('Nothing to preview', validate.render_report(s))

    def test_k9_matches_official_example_except_blank_lines(self):
        official = (validate.HERE / 'sources/ReBL_k9_3255.txt').read_text()
        packaged = (validate.HERE / 'thunderbird_thunderbird-android_3255/bug_report.txt').read_text()
        nonblank = lambda text: [line for line in text.splitlines() if line.strip()]
        self.assertEqual(nonblank(official), nonblank(packaged))

    def test_missing_original_report_is_not_fabricated(self):
        entry = self.man['excluded'][0]
        self.assertEqual(entry['label'], 'CarReport#43')
        self.assertFalse((validate.HERE / entry['folder'] / 'bug_report.txt').exists())
        self.assertTrue((validate.HERE / entry['folder'] / entry['local_apk_name']).exists())


if __name__ == '__main__':
    unittest.main()
