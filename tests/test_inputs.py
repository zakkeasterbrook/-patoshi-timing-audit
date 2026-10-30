"""Input and header rejection tests with known Bitcoin target vectors."""
import hashlib
import json
from pathlib import Path
import struct
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from inputs import HEADER_SHA256, load_inputs, load_labels, validate_labels
from verify_headers import GENESIS, compact, target, verify
from verify_source_labels import check as check_source_labels, extract_labels


class LabelInputTests(unittest.TestCase):
    def test_malformed_label_shapes_and_types_are_rejected(self):
        invalid = [None, {}, {"0": 3}, "3", 3, [True], [False], [3.0], ["3"], [[3]], [None]]
        for value in invalid:
            with self.subTest(value=value), self.assertRaises(ValueError):
                validate_labels(value)

    def test_duplicate_unordered_and_out_of_range_labels_are_rejected(self):
        for labels in ([3, 3], [4, 3], [-1], [50_000]):
            with self.subTest(labels=labels), self.assertRaises(ValueError):
                validate_labels(labels)
        self.assertEqual(validate_labels([0, 3, 49_999]), [0, 3, 49_999])

    def test_malformed_json_and_unexpected_label_digest_are_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "labels.json"
            path.write_text("[3,", encoding="utf-8")
            with self.assertRaises(json.JSONDecodeError):
                load_labels(path)
            path.write_text("[3,4]", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "SHA256 mismatch"):
                load_labels(path)

    def test_source_extraction_does_not_execute_or_coerce_expressions(self):
        self.assertEqual(extract_labels("<?php $patoshiBlocks = array(3, 4, 49999);"), [3, 4, 49_999])
        for body in ("3,3", "4,3", "-1", "50000", "3.0", "true", "3+1", "'3'", "3,,4", ""):
            with self.subTest(body=body), self.assertRaises(ValueError):
                extract_labels("$patoshiBlocks = array(" + body + ");")
        with self.assertRaises(ValueError):
            extract_labels("$patoshiBlocks = array(3); $patoshiBlocks = array(4);")

    def test_source_byte_changes_fail_before_label_extraction(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "source.php"
            source.write_bytes(b"<?php")
            with self.assertRaisesRegex(ValueError, "source size"):
                check_source_labels(source)
            source.write_bytes(b" " * 125_172)
            with self.assertRaisesRegex(ValueError, "source SHA256 mismatch"):
                check_source_labels(source)


class CompactTargetTests(unittest.TestCase):
    def test_known_positive_target_vectors(self):
        vectors = {
            0x01010000: 1,
            0x02008000: 128,
            0x03008000: 32_768,
            0x04008000: 8_388_608,
            0x05009234: 0x92340000,
            0x1d00ffff: 0x00000000ffff0000000000000000000000000000000000000000000000000000,
        }
        for bits, expected in vectors.items():
            with self.subTest(bits=hex(bits)):
                self.assertEqual(target(bits), expected)
                self.assertEqual(compact(expected), bits)

    def test_zero_negative_and_uint256_overflow_are_rejected(self):
        # The latter three are Bitcoin Core's distinct SetCompact overflow
        # boundaries: 33-byte >16-bit, 34-byte >8-bit, and >34-byte targets.
        for bits in (0, 0x1d000000, 0x01000001, 0x1d80ffff,
                     0x21010000, 0x22000100, 0x23000001):
            with self.subTest(bits=hex(bits)), self.assertRaises(AssertionError):
                target(bits)
        for bits in (-1, 0x100000000, True, 1.0):
            with self.subTest(bits=bits), self.assertRaises(AssertionError):
                target(bits)

    def test_valid_noncanonical_compact_decoding_is_not_silently_forbidden(self):
        # Compact decoding permits redundant encodings. Historical chain
        # difficulty equality, not a new decoder rule, enforces expected bits.
        self.assertEqual(target(0x04000001), 256)
        self.assertEqual(compact(256), 0x02010000)


class FrozenHeaderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.payload = (ROOT / "data/headers_0_49999.bin").read_bytes()

    def test_frozen_headers_and_minimal_real_example(self):
        records, labels, retargets, _ = load_inputs()
        self.assertEqual(hashlib.sha256(self.payload).hexdigest(), HEADER_SHA256)
        self.assertEqual(len(records), 50_000)
        self.assertEqual(records[0]["block_hash"], GENESIS)
        self.assertEqual([row["height"] for row in retargets], list(range(2016, 50_000, 2016)))
        self.assertIn(263, labels)
        self.assertIn(264, labels)
        self.assertNotIn(265, labels)
        times = [records[h]["timestamp"] for h in (263, 264, 265)]
        self.assertEqual(times, [1231805421, 1231805980, 1231806051])
        self.assertEqual((times[1]-times[0], times[2]-times[1], times[2]-times[0]), (559, 71, 630))

    def test_missing_partial_and_extra_headers_are_rejected(self):
        for payload in (b"", self.payload[:-80], self.payload[:-1], self.payload+b"\0"):
            with self.subTest(length=len(payload)), self.assertRaises(AssertionError):
                verify(payload)

    def test_broken_previous_hash_link_is_rejected(self):
        corrupt = bytearray(self.payload)
        corrupt[80+4] ^= 1
        with self.assertRaisesRegex(AssertionError, "linkage"):
            verify(corrupt)

    def test_corrupt_nonce_fails_proof_of_work(self):
        corrupt = bytearray(self.payload)
        corrupt[76] ^= 1
        with self.assertRaisesRegex(AssertionError, "proof_of_work"):
            verify(corrupt)

    def test_invalid_targets_and_mainnet_limit_are_rejected_before_hash_check(self):
        for bits in (0, 0x1d80ffff, 0x21010000, 0x1e00ffff):
            with self.subTest(bits=hex(bits)):
                corrupt = bytearray(self.payload)
                struct.pack_into("<I", corrupt, 72, bits)
                with self.assertRaises(AssertionError):
                    verify(corrupt)


if __name__ == "__main__":
    unittest.main()
