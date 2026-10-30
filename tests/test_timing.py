"""Specified-by-hand semantic regression tests, without historical reruns.

Run: python3 -m unittest discover -s tests -v

Native tests additionally require PATOSHI_TEST_PHP (an executable) and
PATOSHI_TEST_SOURCE (the pinned, externally retrieved original PHP file).
Their source copies have synthetic label arrays and, for named diagnostic
variants, explicit control-flow changes. All copies are temporary. These
fixtures are integer timestamp/label examples, not valid Bitcoin headers.
"""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
FIXTURES = json.loads((Path(__file__).parent / 'timing_fixtures.json').read_text())
SOURCE_SHA256 = '104d0df1854802a2e0a5333fda51ee657bb2b17006a48f820bc446c21993e119'
BAD_TIME = "$patoshiBlock2Time = $patoshiBlock1->get('time');"
GOOD_TIME = "$patoshiBlock2Time = $patoshiBlock2->get('time');"
BAD_COUNT = 'count($currentStreakBlocks) > 2'
GOOD_COUNT = 'count($currentStreakBlocks) >= 2'
BAD_RESET = '// reset the streak tracker\n\t\t$currentStreakBlocks = array();'
GOOD_RESET = '// retain the next run head\n\t\t$currentStreakBlocks = array($blockHeight);'

spec = importlib.util.spec_from_file_location('release_timing', ROOT/'scripts/timing.py')
timing = importlib.util.module_from_spec(spec)
spec.loader.exec_module(timing)


def compute(fixture):
    return timing.calculate(dict(enumerate(fixture['times'])),
                            fixture['labels'], len(fixture['times'])-1)


def event_rows(result, variant):
    delta = 'published_delta' if variant == 'original' else 'child_delta'
    return [[row['c'],row[delta]] for row in result['events'][variant]]


class SpecifiedRuleTests(unittest.TestCase):
    """The expected child heights and intervals are explicit fixture data."""

    @classmethod
    def setUpClass(cls):
        cls.results = {f['name']:compute(f) for f in FIXTURES}

    def test_each_stated_rule_case_matches_hand_specification(self):
        for fixture in FIXTURES:
            with self.subTest(fixture=fixture['name'], reason=fixture['reason']):
                self.assertEqual(event_rows(self.results[fixture['name']], 'stated_rule'),
                                 fixture['expected'])

    def test_output_threshold_boundaries_are_strict(self):
        # These tuples are (negative, below300 including negatives,
        # nonnegative below300, exactly300). Every case selects one row.
        expected = {'BC_negative':(1,1,0,0), 'BC_zero':(0,1,1,0),
                    'BC_299':(0,1,1,0), 'BC_300':(0,0,0,1)}
        for name, want in expected.items():
            with self.subTest(fixture=name):
                actual=self.results[name]['summary']['stated_rule']
                self.assertEqual(actual['n'],1)
                self.assertEqual(tuple(actual[k] for k in
                    ('negative','less_300','zero_to_299','at_300')),want)

    def test_emulation_preserves_documented_source_defects(self):
        expected = {
            'two_P_run':([],[]),
            'later_run_head':([[4,200]],[[4,100]]),
            'wrong_interval':([[4,630]],[[4,71]]),
            'AB_600':([[4,700]],[]),
            'AB_negative':([[4,-50]],[[4,50]]),
            'terminal_run_flush':([],[]),
        }
        for name, (original, timestamp_only) in expected.items():
            with self.subTest(fixture=name):
                self.assertEqual(event_rows(self.results[name],'original'),original)
                self.assertEqual(event_rows(self.results[name],'timestamp_only'),timestamp_only)

    def test_prefix_limit_and_final_tracker_are_explicit(self):
        end=self.results['terminal_run_flush']
        self.assertEqual(end['final_unflushed_streak'],[1,2,3])
        self.assertEqual(event_rows(end,'stated_rule'),[[4,100]])
        for variant in ('original','timestamp_only','stated_rule'):
            self.assertEqual(event_rows(self.results['child_beyond_prefix'],variant),[])


def native_run(php, entry, source, data_file):
    env=os.environ.copy()
    env.update(PATOSHI_SOURCE=str(source),PATOSHI_HEADERS=str(data_file))
    completed=subprocess.run([str(php),'-n',str(entry)],cwd=ROOT/'native',env=env,
                             capture_output=True,text=True,timeout=20)
    if completed.returncode == 3:
        missing=re.fullmatch(r'PARTIAL_DATA: Missing height: (\d+)\n',completed.stderr)
        maximum=max(row['height'] for row in json.loads(data_file.read_text()))
        if missing is None or int(missing[1]) <= maximum:
            raise AssertionError(('unexpected_partial_execution',completed.stderr))
    elif completed.returncode != 0 or completed.stderr:
        raise AssertionError(('native_execution_failed',completed.returncode,completed.stderr))
    rows=[]
    for line in completed.stdout.splitlines():
        match=re.fullmatch(r'(\d+),(-?\d+)',line)
        if match is None:
            raise AssertionError(('unexpected_native_output',line))
        rows.append([int(match[1]),int(match[2])])
    return {'rows':rows,'exit_code':completed.returncode,'stderr':completed.stderr}


@unittest.skipUnless(os.environ.get('PATOSHI_TEST_PHP') and os.environ.get('PATOSHI_TEST_SOURCE'),
    'Native PHP fixtures require both PATOSHI_TEST_PHP and PATOSHI_TEST_SOURCE; see docs/regression-tests.md.')
class NativeSourceSemanticTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        requested_php=str(Path(os.environ['PATOSHI_TEST_PHP']).expanduser())
        resolved_php=shutil.which(requested_php)
        if resolved_php is None:
            raise AssertionError('PATOSHI_TEST_PHP is not an executable path or command on PATH: '+requested_php)
        php=Path(resolved_php).resolve()
        source=Path(os.environ['PATOSHI_TEST_SOURCE']).expanduser().resolve()
        original_bytes=source.read_bytes()
        if hashlib.sha256(original_bytes).hexdigest() != SOURCE_SHA256:
            raise AssertionError('External PHP source does not match the pinned published file.')
        original=original_bytes.decode()
        for token in (BAD_TIME,BAD_COUNT,BAD_RESET):
            if original.count(token) != 1:
                raise AssertionError(('ambiguous_source_patch_anchor',token))
        cls.fixture_results={}
        with tempfile.TemporaryDirectory(prefix='patoshi_synthetic_semantics_') as scratch:
            tmp=Path(scratch)
            for fixture in FIXTURES:
                # These hashes are lookup identifiers. There are no serialized
                # headers and no claim that synthetic input satisfies consensus.
                data_file=tmp/'synthetic_lookup_data.json'
                data_file.write_text(json.dumps([
                    {'height':h,'block_hash':f'{h:064x}','timestamp':t}
                    for h,t in enumerate(fixture['times'])]))
                label_text=','.join(map(str,fixture['labels']))
                modified, count=re.subn(r'\$patoshiBlocks = array\([0-9,]+\);',
                    '$patoshiBlocks = array('+label_text+');', original)
                if count != 1:
                    raise AssertionError('Synthetic classification-list substitution failed.')
                variants={
                    'original_logic':modified,
                    'timestamp_only':modified.replace(BAD_TIME,GOOD_TIME),
                    'timestamp_and_count':modified.replace(BAD_TIME,GOOD_TIME).replace(BAD_COUNT,GOOD_COUNT),
                    'timestamp_count_and_head':modified.replace(BAD_TIME,GOOD_TIME).replace(BAD_COUNT,GOOD_COUNT).replace(BAD_RESET,GOOD_RESET),
                }
                results={}
                for name,text in variants.items():
                    path=tmp/('synthetic_labels_'+name+'.php')
                    path.write_text(text)
                    results[name]=native_run(php,ROOT/'native/run_original.php',path,data_file)
                results['direct_rule']=native_run(php,ROOT/'native/literal_rule.php',
                    tmp/'synthetic_labels_original_logic.php',data_file)
                cls.fixture_results[fixture['name']]=results

    def test_python_emulation_matches_actual_php_every_fixture(self):
        for fixture in FIXTURES:
            with self.subTest(fixture=fixture['name']):
                result=compute(fixture)
                native=self.fixture_results[fixture['name']]
                self.assertEqual(event_rows(result,'original'),native['original_logic']['rows'])
                self.assertEqual(event_rows(result,'timestamp_only'),native['timestamp_only']['rows'])

    def test_direct_php_matches_hand_specified_outcomes(self):
        for fixture in FIXTURES:
            with self.subTest(fixture=fixture['name']):
                native=self.fixture_results[fixture['name']]['direct_rule']
                self.assertEqual(native['rows'],fixture['expected'])
                self.assertEqual(native['exit_code'],0)

    def test_run_count_and_discarded_head_are_separate_faults(self):
        first=self.fixture_results['two_P_run']
        self.assertEqual(first['timestamp_only']['rows'],[])
        self.assertEqual(first['timestamp_and_count']['rows'],[[3,100]])
        later=self.fixture_results['later_run_head']
        self.assertEqual(later['timestamp_and_count']['rows'],[[4,100]])
        self.assertEqual(later['timestamp_count_and_head']['rows'],[[4,100],[7,100]])

    def test_missing_final_flush_is_a_synthetic_edge_case(self):
        result=self.fixture_results['terminal_run_flush']
        self.assertEqual(result['timestamp_count_and_head']['rows'],[])
        self.assertEqual(result['direct_rule']['rows'],[[4,100]])

    def test_exhausted_prefix_is_reported_explicitly(self):
        result=self.fixture_results['child_beyond_prefix']
        for variant in ('original_logic','timestamp_only','timestamp_and_count','timestamp_count_and_head'):
            with self.subTest(variant=variant):
                self.assertEqual(result[variant]['rows'],[])
                self.assertEqual(result[variant]['exit_code'],3)
                self.assertEqual(result[variant]['stderr'],'PARTIAL_DATA: Missing height: 4\n')


if __name__=='__main__':
    unittest.main()
