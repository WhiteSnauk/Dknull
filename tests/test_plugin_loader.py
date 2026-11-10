import tempfile
import unittest
from pathlib import Path

from src.plugin_loader import load_plugins


class TestPluginLoader(unittest.TestCase):
    def test_successful_load(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / 'test_plugin.py'
            p.write_text(
                'NAME = "test"\n'
                'def register(registry):\n'
                '    registry["test"] = lambda x: "OK"\n'
            )
            registry = {}
            loaded = load_plugins(Path(td), registry)
            self.assertEqual(loaded, ['test'])
            self.assertIn('test', registry)
            self.assertEqual(registry['test'](None), 'OK')

    def test_import_error(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / 'bad_plugin.py'
            p.write_text('raise ImportError("boom")\n')
            registry = {}
            loaded = load_plugins(Path(td), registry)
            self.assertEqual(loaded, [])

    def test_missing_register(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / 'incomplete.py'
            p.write_text('NAME = "x"\n')
            registry = {}
            self.assertEqual(load_plugins(Path(td), registry), [])

    def test_name_conflict(self):
        with tempfile.TemporaryDirectory() as td:
            p1 = Path(td) / 'a.py'
            p1.write_text(
                'NAME = "same"\n'
                'def register(registry):\n'
                '    registry["same"] = 1\n'
            )
            p2 = Path(td) / 'b.py'
            p2.write_text(
                'NAME = "same"\n'
                'def register(registry):\n'
                '    registry["same"] = 2\n'
            )
            registry = {}
            loaded = load_plugins(Path(td), registry)
            self.assertEqual(loaded, ['same'])
            self.assertEqual(registry['same'], 1)


if __name__ == '__main__':
    unittest.main()