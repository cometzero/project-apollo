import importlib.util
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('collector', Path(__file__).with_name('collect_snapshot.py'))
collector = importlib.util.module_from_spec(spec)
spec.loader.exec_module(collector)


class SnapshotTests(unittest.TestCase):
    def test_own_process(self):
        p = collector.collect_process('test-only', os.getpid())
        self.assertEqual(p['status'], 'OBSERVED')
        self.assertTrue(any(t['tid'] == os.getpid() for t in p['threads']))
        self.assertTrue(all(t['role'] == 'UNKNOWN' for t in p['threads']))

    def test_unavailable_proc(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = collector.collect_process('qbox', 99, Path(tmp))
        self.assertEqual(p['status'], 'ERROR')
        self.assertIsNone(p['pid'])
        self.assertEqual(p['threads'], [])

    def test_pid_reuse_discards_identity(self):
        real = collector.process_identity
        calls = 0
        def identity(pid, proc=Path('/proc')):
            nonlocal calls
            result = real(pid, proc)
            if proc == Path('/proc'):
                calls += 1
                if calls == 2:
                    return result[0], result[1] + 1
            return result
        with patch.object(collector, 'process_identity', side_effect=identity):
            p = collector.collect_process('qbox', os.getpid())
        self.assertEqual(p['status'], 'ERROR')
        self.assertIsNone(p['pid'])
        self.assertEqual(p['threads'], [])

    def test_foreign_monitor_not_contacted(self):
        p = collector.collect_process('qbox', os.getpid())
        with patch.object(collector, 'QBoxDiagnostics') as diagnostics:
            collector.enrich_qmp(p, {'owner_pid': -1, 'owner_start_ticks': 0})
            diagnostics.assert_not_called()
        self.assertTrue(p['errors'])
        self.assertTrue(all(not t['cpus'] for t in p['threads']))


    def test_qmp_mapping_and_foreign_tid(self):
        for tid, expected in [(os.getpid(), True), (-10, False)]:
            p = collector.collect_process('qbox', os.getpid())
            manifest = {'owner_pid': os.getpid(), 'owner_start_ticks': int(p['start_time'].rsplit(':', 1)[1])}
            with patch.object(collector, 'QBoxDiagnostics') as diagnostics:
                diagnostics.return_value.domains = {'ap': {}}
                diagnostics.return_value.query.return_value = {'result': [{'thread-id': tid, 'cpu-index': 0}]}
                collector.enrich_qmp(p, manifest)
            mapped = any(t['cpus'] for t in p['threads'])
            self.assertEqual(mapped, expected)


if __name__ == '__main__':
    unittest.main()
