#!/usr/bin/env python3
import unittest
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import consistency_check as cc

class ReviewCoverageTests(unittest.TestCase):
    def test_E03_two_unrelated_chapters_are_insufficient(self):
        claims = [
            {'claim_id': 'a', 'text': 'Otpad iznosi 20 t.', 'location': {'chapter': '4'}},
            {'claim_id': 'b', 'text': 'Prihod iznosi 30 EUR.', 'location': {'chapter': '6'}},
        ]
        out = cc.evaluate_claims(claims)
        self.assertEqual(out['coverage_status'], 'insufficient')
        self.assertEqual(out['summary']['edges'], 0)

    def test_same_claim_across_chapters_is_measurable(self):
        out = cc.evaluate_claims([
            {'claim_id': 'a', 'text': 'Otpad iznosi 20 t.', 'location': {'chapter': '4'}},
            {'claim_id': 'b', 'text': 'Otpad iznosi 20 t.', 'location': {'chapter': '6'}},
        ])
        self.assertEqual(out['coverage_status'], 'sufficient')
        self.assertEqual(out['summary']['blocking'], 0)

    def test_duplicate_claim_id_is_invalid(self):
        claims = [{'claim_id': 'a', 'text': 'Otpad iznosi 20 t.',
                   'location': {'chapter': c}} for c in ('4', '6')]
        with self.assertRaises(ValueError):
            cc.evaluate_claims(claims)

if __name__ == '__main__':
    unittest.main()
