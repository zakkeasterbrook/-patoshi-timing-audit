#!/usr/bin/env python3
"""Run actual PHP and compare every output byte with a fresh Python result."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from reproduce import reproduce
from inputs import SOURCE_SHA256, require

BAD = b"$patoshiBlock2Time = $patoshiBlock1->get('time');"
GOOD = b"$patoshiBlock2Time = $patoshiBlock2->get('time');"


def run(php_name, source_path, output_dir):
    php = shutil.which(str(php_name))
    require(php is not None, "PHP executable not found: " + str(php_name))
    source_path = Path(source_path).resolve()
    source = source_path.read_bytes()
    require(hashlib.sha256(source).hexdigest() == SOURCE_SHA256, "Unrecognized upstream source: refusing execution")
    require(source.count(BAD) == 1, "Expected one defective timestamp assignment")
    output_dir = Path(output_dir).resolve()
    python_summary = reproduce(output_dir)
    version = subprocess.run([php, "-n", "-v"], check=True, capture_output=True, text=True).stdout
    env = os.environ.copy()
    env["PATOSHI_HEADERS"] = str(output_dir / "headers_0_49999.json")
    native_output = output_dir / "native"
    native_output.mkdir(parents=True, exist_ok=True)
    results = {}
    with tempfile.TemporaryDirectory(prefix="patoshi_timing_patch_") as tmp:
        fixed = Path(tmp) / "timestamp_only.php"
        fixed.write_bytes(source.replace(BAD, GOOD))
        cases = [
            ("original", "run_original.php", source_path, "original.csv"),
            ("timestamp_only", "run_original.php", fixed, "timestamp_only.csv"),
            ("stated_rule", "literal_rule.php", source_path, "literal_rule.csv"),
        ]
        for name, entry, selected_source, filename in cases:
            env["PATOSHI_SOURCE"] = str(selected_source)
            completed = subprocess.run(
                [php, "-n", str(ROOT / "native" / entry)], cwd=ROOT / "native", env=env,
                capture_output=True, timeout=90,
            )
            require(completed.returncode == 0, f"PHP failed for {name}: " + completed.stderr.decode(errors="replace"))
            require(not completed.stderr, "Unexpected PHP stderr: " + completed.stderr.decode(errors="replace"))
            for line in completed.stdout.splitlines():
                require(re.fullmatch(rb"\d+,-?\d+", line) is not None, "Unexpected PHP output")
            payload = b"height,header_timestamp_delta_seconds\n" + completed.stdout
            require(payload == (output_dir / filename).read_bytes(), "PHP/Python row mismatch: " + name)
            (native_output / filename).write_bytes(payload)
            results[name] = {
                "exit_code": completed.returncode,
                "rows": len(completed.stdout.splitlines()),
                "every_output_byte_matches_fresh_python": True,
                "csv_sha256": hashlib.sha256(payload).hexdigest(),
                "source_input_sha256": hashlib.sha256(selected_source.read_bytes()).hexdigest(),
                "entrypoint": "native/" + entry,
                "entrypoint_sha256": hashlib.sha256((ROOT / "native" / entry).read_bytes()).hexdigest(),
            }
    report = {
        "status": "pass", "runtime": version, "upstream_source_sha256": SOURCE_SHA256,
        "method": "Actual PHP CLI with -n and a deterministic offline replacement for three RPC/response operations",
        "limitation": "Not the complete original 2022 Composer/Bitcoin Core environment",
        "variants": results, "counts": python_summary["counts"],
    }
    (output_dir / "native_verification.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--php", default="php", help="PHP executable name or full path")
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, default=ROOT / "build")
    args = parser.parse_args()
    print(json.dumps(run(args.php, args.source, args.output_dir), indent=2))
