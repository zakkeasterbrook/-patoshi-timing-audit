"""Isolate contextual header rules after their cryptographic prerequisites.

The ordinary full-input tests validate genuine header hashes and proof of work.
These unit tests deliberately replace hash256 for exactly one modified header
with its original digest. The modified bytes are NOT valid Bitcoin headers;
the narrow stand-in lets MTP/difficulty branches be tested without mining new
proof of work or failing earlier linkage checks.
"""
from pathlib import Path
import struct
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import verify_headers as header_rules


class ContextualHeaderRuleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.payload = (ROOT / 'data/headers_0_49999.bin').read_bytes()

    def timestamp(self, height):
        return struct.unpack_from('<I', self.payload, height * 80 + 68)[0]

    def median_before(self, height):
        past = sorted(self.timestamp(h) for h in range(max(0, height - 11), height))
        return past[len(past) // 2]

    def modified_header(self, height, *, timestamp=None, bits=None):
        original = self.payload[height * 80:(height + 1) * 80]
        changed = bytearray(original)
        if timestamp is not None:
            struct.pack_into('<I', changed, 68, timestamp)
        if bits is not None:
            struct.pack_into('<I', changed, 72, bits)
        changed = bytes(changed)
        self.assertNotEqual(changed, original)
        digest = header_rules.hash256(original)
        declared_target = header_rules.target(struct.unpack_from('<I', changed, 72)[0])
        self.assertLessEqual(declared_target, header_rules.target(0x1d00ffff))
        self.assertLessEqual(int.from_bytes(digest, 'little'), declared_target)
        self.assertEqual(changed[4:36], original[4:36])
        modified = self.payload[:height * 80] + changed + self.payload[(height + 1) * 80:]
        real_hash256 = header_rules.hash256

        def one_header_hash_standin(data):
            return digest if data == changed else real_hash256(data)

        return modified, one_header_hash_standin

    def test_timestamp_must_be_strictly_above_median_time_past(self):
        height = 265
        median = self.median_before(height)
        payload, standin = self.modified_header(height, timestamp=median)
        with patch.object(header_rules, 'hash256', side_effect=standin):
            with self.assertRaises(AssertionError) as caught:
                header_rules.verify(payload)
        self.assertEqual(caught.exception.args[0], ('median_time_past', height))

        # One second above the same median passes this contextual boundary.
        # Lowering this one timestamp cannot raise any later MTP threshold and
        # it is not a retarget endpoint, so the remaining real chain still fits.
        self.assertLess(median + 1, self.timestamp(height))
        payload, standin = self.modified_header(height, timestamp=median + 1)
        with patch.object(header_rules, 'hash256', side_effect=standin):
            records, _ = header_rules.verify(payload)
        self.assertEqual(records[height]['timestamp'], median + 1)
        self.assertEqual(len(records), 50_000)

    def test_non_retarget_height_cannot_change_difficulty(self):
        height, wrong_bits = 1, 0x1d00fffe
        self.assertGreater(self.timestamp(height), self.median_before(height))
        payload, standin = self.modified_header(height, bits=wrong_bits)
        with patch.object(header_rules, 'hash256', side_effect=standin):
            with self.assertRaises(AssertionError) as caught:
                header_rules.verify(payload)
        self.assertEqual(caught.exception.args[0],
                         ('difficulty_retarget', height, wrong_bits, 0x1d00ffff))

    def test_first_nontrivial_retarget_cannot_keep_the_previous_bits(self):
        height, previous_bits, expected_bits = 32_256, 0x1d00ffff, 0x1d00d86a
        self.assertEqual(struct.unpack_from('<I', self.payload, height * 80 + 72)[0], expected_bits)
        self.assertGreater(self.timestamp(height), self.median_before(height))
        payload, standin = self.modified_header(height, bits=previous_bits)
        with patch.object(header_rules, 'hash256', side_effect=standin):
            with self.assertRaises(AssertionError) as caught:
                header_rules.verify(payload)
        self.assertEqual(caught.exception.args[0],
                         ('difficulty_retarget', height, previous_bits, expected_bits))


if __name__ == '__main__':
    unittest.main()
