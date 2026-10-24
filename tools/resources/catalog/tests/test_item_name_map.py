import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[4]
BUILDER = ROOT / 'tools/resources/catalog/build_item_names.py'


class MappingTests(unittest.TestCase):
    def run_builder(self, directory, mismatch=False):
        root = Path(directory)
        sources = {
            'dvg': {'501': {'name': '错误身份', 'aegis': 'Other_Item', 'source': 'https://ro.dvg.cn/item_info.php?id=501'},
                    '502': {'name': '赤色药水', 'aegis': 'Orange_Potion', 'source': 'https://ro.dvg.cn/item_info.php?id=502'},
                    '503': {'name': 'Yellow Potion', 'aegis': 'Yellow_Potion', 'source': 'https://ro.dvg.cn/item_info.php?id=503'},
                    '504': {'name': '白色药水', 'aegis': '', 'source': 'https://ro.dvg.cn/item_info.php?id=504'}},
            'ro321': {'501': {'name': '红色药水', 'aegis': 'Red_Potion', 'source': 'https://ro.ro321.com/index.php?page=re_item_db&item_id=501'},
                      '502': {'name': '橙色药水', 'aegis': 'Orange_Potion', 'source': 'https://ro.ro321.com/index.php?page=re_item_db&item_id=502'}}}
        for name, rows in sources.items():
            (root / f'{name}-names.json').write_text(json.dumps(rows, ensure_ascii=False))
        status = {'fetchedAt': '2026-10-24', **{name: {'records': len(rows), 'complete': False} for name, rows in sources.items()}}
        if mismatch:
            status['ro321']['records'] += 1
        (root / 'source-status.json').write_text(json.dumps(status))
        return subprocess.run([sys.executable, str(BUILDER), 'build', '--references', directory, '--output', str(root / 'out')], cwd=ROOT, capture_output=True, text=True)

    def test_source_identity_priority_and_snapshot_hash(self):
        with tempfile.TemporaryDirectory() as directory:
            result = self.run_builder(directory)
            self.assertEqual(result.returncode, 0, result.stderr)
            root = Path(directory)
            mapping = json.loads((root / 'out/zh-CN.json').read_text())
            self.assertEqual(mapping['items']['501']['name'], '红色药水')
            self.assertEqual(mapping['items']['502']['name'], '赤色药水')
            self.assertNotIn('503', mapping['items'])
            self.assertNotIn('504', mapping['items'])
            for name in ['dvg', 'ro321']:
                self.assertEqual(mapping['sources'][name]['sha256'], hashlib.sha256((root / f'{name}-names.json').read_bytes()).hexdigest())

    def test_inconsistent_snapshot_does_not_publish_mapping(self):
        with tempfile.TemporaryDirectory() as directory:
            result = self.run_builder(directory, mismatch=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('record count mismatch', result.stderr)
            self.assertFalse((Path(directory) / 'out/zh-CN.json').exists())
