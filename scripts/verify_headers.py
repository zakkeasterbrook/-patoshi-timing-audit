#!/usr/bin/env python3
"""Verify the raw header chain; this is not full transaction/consensus validation."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import struct

ROOT = Path(__file__).resolve().parents[1]
GENESIS = '000000000019d6689c085ae165831e934ff763ae46a2a6c172b3f1b60a8ce26f'

def hash256(data):
    return hashlib.sha256(hashlib.sha256(data).digest()).digest()

def target(bits):
    """Decode a positive, non-overflowing Bitcoin compact target.

    Match the sign and overflow rules of Bitcoin Core's SetCompact; the
    chain-specific proof-of-work limit is checked separately in verify().
    Compact decoding alone does not require a canonical representation.
    """
    assert type(bits) is int and 0 <= bits <= 0xffffffff, 'compact_target_uint32'
    exponent, mantissa = bits >> 24, bits & 0x007fffff
    assert not bits & 0x00800000, 'negative_compact_target'
    overflow = mantissa != 0 and (exponent > 34
        or (mantissa > 0xff and exponent > 33)
        or (mantissa > 0xffff and exponent > 32))
    assert not overflow, 'overflowing_compact_target'
    decoded = mantissa << (8*(exponent-3)) if exponent >= 3 else mantissa >> (8*(3-exponent))
    assert decoded > 0, 'zero_compact_target'
    return decoded

def compact(value):
    size = (value.bit_length()+7)//8
    word = value << (8*(3-size)) if size <= 3 else value >> (8*(size-3))
    if word & 0x00800000:
        word >>= 8
        size += 1
    return (size << 24) | word

def verify(payload):
    if not __debug__:
        raise RuntimeError('Header verification must run without Python optimization flags')
    assert len(payload) == 50_000*80, 'expected_exactly_50000_headers'
    records = []
    previous_hash = '00'*32
    maximum_target = target(0x1d00ffff)
    retargets = []
    for height in range(50_000):
        header = payload[height*80:(height+1)*80]
        block_hash = hash256(header)[::-1].hex()
        assert header[4:36][::-1].hex() == previous_hash, ('linkage', height)
        timestamp, bits = struct.unpack_from('<II', header, 68)
        declared_target = target(bits)
        assert declared_target <= maximum_target, ('target', height)
        assert int(block_hash, 16) <= declared_target, ('proof_of_work', height)
        if height == 0:
            assert block_hash == GENESIS
            assert bits == 0x1d00ffff
        else:
            past = sorted(r['timestamp'] for r in records[-11:])
            assert timestamp > past[len(past)//2], ('median_time_past', height)
            if height % 2016:
                expected_bits = records[-1]['bits']
            else:
                span = records[-1]['timestamp'] - records[height-2016]['timestamp']
                adjusted_span = max(14*86400//4, min(14*86400*4, span))
                next_target = min(maximum_target, target(records[-1]['bits'])*adjusted_span//(14*86400))
                expected_bits = compact(next_target)
                retargets.append({'height':height, 'actual_timespan_seconds':span, 'expected_bits':expected_bits, 'observed_bits':bits})
            assert bits == expected_bits, ('difficulty_retarget', height, bits, expected_bits)
        records.append({'height':height, 'block_hash':block_hash, 'timestamp':timestamp, 'bits':bits, 'header_hex':header.hex()})
        previous_hash = block_hash
    return records, retargets

def main():
    payload = (ROOT/'data'/'headers_0_49999.bin').read_bytes()
    records, retargets = verify(payload)
    output = ROOT/'build'
    output.mkdir(parents=True, exist_ok=True)
    (output/'headers_0_49999.json').write_text(json.dumps(records, separators=(',',':'))+'\n', encoding='utf-8')
    result = {
        'headers':len(records), 'height_range':[0,49999],
        'sha256_of_raw_headers':hashlib.sha256(payload).hexdigest(),
        'genesis_hash':records[0]['block_hash'], 'final_hash':records[-1]['block_hash'],
        'first_timestamp_utc':datetime.fromtimestamp(records[0]['timestamp'],timezone.utc).isoformat(),
        'last_timestamp_utc':datetime.fromtimestamp(records[-1]['timestamp'],timezone.utc).isoformat(),
        'passed':['exact_80_byte_headers','known_mainnet_genesis','all_previous_hash_links','all_declared_proof_of_work','all_difficulty_transition_rules','all_median_time_past_checks'],
        'not_claimed':['full block or transaction validation','contemporaneous two-hour-future-time validation','independent identification of miners'],
        'retargets':retargets,
    }
    (output/'header_verification.json').write_text(json.dumps(result,indent=2)+'\n', encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k!='retargets'},indent=2))

if __name__ == '__main__':
    main()
