#!/usr/bin/env python3
import unittest
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import evidence_gate
import reviewer_simulation as reviewer

class ReviewStatusTests(unittest.TestCase):
    def test_E01_failed_empty_gate_is_not_clear(self):
        report = evidence_gate.evaluate_gate([], [], policy='strict')
        self.assertIs(report['passed'], False)
        self.assertTrue(report['preconditions'])
        out = reviewer.simulate(evidence_gate=report)
        lens = next(x for x in out['lenses'] if x['lens'] == 'evidence')
        self.assertEqual(lens['status'], 'risk')
        self.assertGreater(out['summary']['high_priority'], 0)

    def test_E02_empty_payload_is_rejected(self):
        with self.assertRaises(ValueError):
            reviewer.simulate(evidence_gate={})

    def test_E04_clean_advisory_is_not_strict_clear(self):
        report = evidence_gate.evaluate_gate([], [], policy='advisory')
        out = reviewer.simulate(evidence_gate=report)
        lens = next(x for x in out['lenses'] if x['lens'] == 'evidence')
        self.assertEqual(lens['status'], 'watch')
        self.assertTrue(any(x['code'] == 'evidence:advisory_only'
                            for x in out['questions']))

if __name__ == '__main__':
    unittest.main()
