"""Exercise the offline RPC dependency with real header lookups under PHP.

Set PATOSHI_TEST_PHP to a PHP executable. These tests use the adapter directly;
the pinned upstream source is not needed for these dependency checks.
"""
import hashlib
import json
import os
from pathlib import Path
import shutil
import struct
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]


@unittest.skipUnless(os.environ.get("PATOSHI_TEST_PHP"),
                     "Native adapter checks require PATOSHI_TEST_PHP")
class NativeAdapterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.php = shutil.which(os.environ["PATOSHI_TEST_PHP"])
        if cls.php is None:
            raise AssertionError("PATOSHI_TEST_PHP does not resolve to an executable")
        payload = (ROOT / "data/headers_0_49999.bin").read_bytes()
        cls.rows = []
        for height in (263, 264, 265):
            raw = payload[height * 80:(height + 1) * 80]
            cls.rows.append({
                "height": height,
                "block_hash": hashlib.sha256(hashlib.sha256(raw).digest()).digest()[::-1].hex(),
                "timestamp": struct.unpack_from("<I", raw, 68)[0],
            })

    def invoke(self, code, rows=None):
        with tempfile.TemporaryDirectory(prefix="patoshi_adapter_test_") as directory:
            fixture = Path(directory) / "headers.json"
            fixture.write_text(json.dumps(self.rows if rows is None else rows))
            env = os.environ.copy()
            env["PATOSHI_HEADERS"] = str(fixture)
            completed = subprocess.run(
                [self.php, "-n", "-r", code, str(ROOT / "native/vendor/autoload.php")],
                capture_output=True, text=True, timeout=20, env=env,
            )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(completed.stderr, "")
        return json.loads(completed.stdout)

    def test_real_block_responses_remain_independent_after_later_lookups(self):
        actual = self.invoke(r'''
require $argv[1];
$client = new \Denpa\Bitcoin\Client('unused-offline-address');
$a = $client->getBlock($client->getBlockHash(263));
$firstTime = $a->get('time');
$b = $client->getBlock($client->getBlockHash(264));
$c = $client->getBlock($client->getBlockHash(265));
$again = $client->getBlock($client->getBlockHash(263));
echo json_encode([
    'before' => $firstTime,
    'after' => $a->get('time'),
    'times' => [$a->get('time'), $b->get('time'), $c->get('time')],
    'heights' => [$a->get('height'), $b->get('height'), $c->get('height')],
    'hashes' => [$a->get('hash'), $b->get('hash'), $c->get('hash')],
    'distinct' => $a !== $b && $a !== $c && $b !== $c && $a !== $again,
    'repeat_time' => $again->get('time'),
]);
''')
        self.assertTrue(actual["distinct"])
        self.assertEqual(actual["before"], self.rows[0]["timestamp"])
        self.assertEqual(actual["after"], actual["before"])
        self.assertEqual(actual["repeat_time"], actual["before"])
        self.assertEqual(actual["times"], [row["timestamp"] for row in self.rows])
        self.assertEqual(actual["heights"], [263, 264, 265])
        self.assertEqual(actual["hashes"], [row["block_hash"] for row in self.rows])
        self.assertEqual(actual["times"][1] - actual["times"][0], 559)
        self.assertEqual(actual["times"][2] - actual["times"][1], 71)

    def test_missing_lookups_are_explicit_instead_of_reusing_a_response(self):
        actual = self.invoke(r'''
require $argv[1];
$client = new \Denpa\Bitcoin\Client('unused-offline-address');
$existing = $client->getBlock($client->getBlockHash(263));
$errors = [];
try { $client->getBlockHash(266); }
catch (\Denpa\Bitcoin\OfflineDataMissing $e) { $errors[] = $e->getMessage(); }
try { $client->getBlock(str_repeat('f', 64)); }
catch (\Denpa\Bitcoin\OfflineDataMissing $e) { $errors[] = $e->getMessage(); }
echo json_encode(['errors' => $errors, 'time' => $existing->get('time')]);
''')
        self.assertEqual(actual["errors"], ["Missing height: 266", "Missing hash: " + "f" * 64])
        self.assertEqual(actual["time"], self.rows[0]["timestamp"])

    def test_ambiguous_duplicate_lookups_are_rejected(self):
        code = r'''
require $argv[1];
try {
    new \Denpa\Bitcoin\Client('unused-offline-address');
    echo json_encode(['accepted' => true]);
} catch (\RuntimeException $e) {
    echo json_encode(['error' => $e->getMessage()]);
}
'''
        duplicate_height = dict(self.rows[1], height=263)
        duplicate_hash = dict(self.rows[1], block_hash=self.rows[0]["block_hash"])
        for duplicate in (duplicate_height, duplicate_hash):
            with self.subTest(duplicate=duplicate):
                actual = self.invoke(code, [self.rows[0], duplicate])
                self.assertEqual(actual, {"error": "Duplicate height/hash"})
