"""Release checks for the stated rule and fail-closed input verification."""
import importlib.util
import itertools
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('timing_release_check', ROOT / 'scripts/timing.py')
timing = importlib.util.module_from_spec(spec)
spec.loader.exec_module(timing)


class ReleaseTests(unittest.TestCase):
    def test_all_small_label_masks_against_triplet_definition(self):
        # 256 label sequences x 6 clocks: every three-label shape and its run context.
        clocks = [list(range(0, 800, step))[:8] for step in (1, 100)]
        clocks += [[i * d for i in range(8)] for d in (299, 300, 599, 600)]
        for mask in itertools.product((False, True), repeat=8):
            for times in clocks:
                labels = [i for i, value in enumerate(mask) if value]
                if not labels:
                    continue  # calculate reports label_min and requires a nonempty list.
                expected = [[c, times[c]-times[c-1]] for c in range(2, 8)
                            if tuple(mask[c-2:c+1]) == (True, True, False)
                            and times[c-1]-times[c-2] < 600]
                actual = timing.calculate(dict(enumerate(times)), labels, 7)
                self.assertEqual([[r['c'], r['child_delta']] for r in actual['events']['stated_rule']], expected)

    def test_optimized_python_rejects_disabled_header_assertions(self):
        with tempfile.TemporaryDirectory() as directory:
            p = subprocess.run([sys.executable, '-O', str(ROOT/'reproduce.py'), '--output-dir', directory],
                               capture_output=True, text=True, timeout=30)
        self.assertNotEqual(p.returncode, 0)
        self.assertIn('Run without -O', p.stderr)

    def test_header_mutation_is_rejected(self):
        code = '''import sys
sys.path.insert(0, sys.argv[1])
from verify_headers import verify
from pathlib import Path
data=bytearray(Path(sys.argv[2]).read_bytes())
data[123*80+68] ^= 1
try:
    verify(bytes(data))
except AssertionError:
    sys.exit(0)
sys.exit(1)
'''
        env = os.environ.copy()
        env.pop('PYTHONOPTIMIZE', None)
        p = subprocess.run([sys.executable, '-I', '-c', code, str(ROOT/'scripts'), str(ROOT/'data/headers_0_49999.bin')],
                           capture_output=True, text=True, timeout=30, env=env)
        self.assertEqual(p.returncode, 0, p.stderr)
