#!/usr/bin/env python3
"""E07–E11, E19–E20: executable numeric meaning, not citation truth."""
from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from semantic_fixtures import context, fact, derivation, sum_context


class NumericTests(unittest.TestCase):
    def module(self):
        self.assertIsNotNone(importlib.util.find_spec('numeric_semantics'), 'B evaluator is not implemented')
        return importlib.import_module('numeric_semantics')

    def report(self, ctx):
        return self.module().evaluate(ctx)

    def codes(self, ctx):
        return {x['code'] for x in self.report(ctx)['findings']}

    def test_correct_disjoint_sum_passes(self):
        r = self.report(sum_context())
        self.assertEqual(r['status'], 'pass')
        self.assertFalse(r['coverage']['whole_document'])
        self.assertEqual(r['coverage']['checked_derivations'], 1)

    def test_total_plus_component_is_double_count(self):
        c = sum_context(); c['facts'][0]['members'] = ['kitchen', 'green']
        c['facts'][0]['value']['amount'] = '600'; c['facts'][2]['value']['amount'] = '750'
        self.assertIn('double_count', self.codes(c))

    def test_incorrect_sum_is_blocked(self):
        c = sum_context(); c['facts'][2]['value']['amount'] = '601'
        self.assertIn('arithmetic_mismatch', self.codes(c))

    def test_unreviewed_membership_is_not_a_pass(self):
        c = sum_context(); c['facts'][1]['members'] = None
        self.assertEqual(self.report(c)['status'], 'review_required')

    def test_exact_decimal_not_binary_float(self):
        c = sum_context()
        for f, value in zip(c['facts'], ['0.1','0.2','0.3']): f['value']['amount'] = value
        self.assertEqual(self.report(c)['status'], 'pass')

    def test_approved_rounding_tolerance(self):
        c = sum_context(); c['facts'][2]['value']['amount'] = '600.01'
        c['derivations'][0]['tolerance'] = {'absolute':'0.02','reason':'Source rounds components', 'reviewer':'R'}
        self.assertEqual(self.report(c)['status'], 'pass')
        c['facts'][2]['value']['amount'] = '601'
        self.assertIn('arithmetic_mismatch', self.codes(c))

    def test_unexplained_tolerance_rejected(self):
        c = sum_context(); c['derivations'][0]['tolerance']['absolute'] = '2'
        with self.assertRaises(ValueError): self.report(c)

    def test_actual_capacity_and_input_output_not_identical(self):
        for field, value in [('measure_status','capacity'),('flow_role','output'),('period','2024'),('metric','compost')]:
            with self.subTest(field=field):
                c = context([fact('a',200),fact('out',200,origin='derived')],[derivation('identity',['a'],'out')])
                c['facts'][1][field] = value
                self.assertIn('semantic_mismatch', self.codes(c))

    def test_different_organisation_not_comparable(self):
        c = sum_context(); c['facts'][1]['scope']['organisation'] = 'Different'
        self.assertIn('semantic_mismatch', self.codes(c))

    def test_units_converted_only_with_known_dimension(self):
        c = sum_context(); c['facts'][1]['value']['amount'] = '150000'; c['facts'][1]['unit'] = 'kg'
        self.assertEqual(self.report(c)['status'], 'pass')
        c['facts'][1]['unit'] = 'EUR'
        self.assertIn('unit_mismatch', self.codes(c))

    def test_unknown_units_need_review(self):
        c = sum_context(); c['facts'][1]['unit'] = 'truckloads'
        self.assertEqual(self.report(c)['status'], 'review_required')

    def test_bounds_intervals_and_unknown_not_exact_values(self):
        for value in [{'kind':'lower_bound','amount':'150'}, {'kind':'approximate','amount':'150'},
                      {'kind':'interval','lower':'149','upper':'151'}, {'kind':'unknown'}]:
            with self.subTest(value=value):
                c = sum_context(); c['facts'][1]['value'] = value
                self.assertEqual(self.report(c)['status'], 'review_required')

    def test_invalid_numbers_and_unknown_keys_rejected(self):
        for bad in ['NaN','Infinity','1e10','1.234,50',True,1.5]:
            with self.subTest(value=bad):
                c = sum_context(); c['facts'][0]['value']['amount'] = bad
                with self.assertRaises(ValueError): self.report(c)
        c=sum_context(); c['invented']=True
        with self.assertRaises(ValueError): self.report(c)

    def test_negative_tolerance_interval_and_duplicate_ids_rejected(self):
        for change in ('negative','interval','duplicate','dangling'):
            c=sum_context()
            if change=='negative': c['derivations'][0]['tolerance']['absolute']='-1'
            elif change=='interval': c['facts'][0]['value']={'kind':'interval','lower':'2','upper':'1'}
            elif change=='duplicate': c['facts'][1]['fact_id']='a'
            else: c['derivations'][0]['inputs'][0]='missing'
            with self.subTest(change=change), self.assertRaises(ValueError): self.report(c)

    def test_empty_context_and_coverage_gaps_never_pass(self):
        self.assertEqual(self.report(context())['status'],'unmeasured')
        c=sum_context(); c['required_fact_ids'].append('missing')
        self.assertEqual(self.report(c)['status'],'unmeasured')

    def test_semantic_annotation_pending_is_not_verified(self):
        c=sum_context(); c['facts'][0]['review']['decision']='pending'
        self.assertEqual(self.report(c)['status'],'review_required')

    def percent_change(self, op, result):
        a=fact('a','40',unit='%',denominator='all-waste',period='2022')
        b=fact('b','50',unit='%',denominator='all-waste',period='2023')
        out=fact('out',result,unit='pp' if op=='percentage_point_change' else '%',
                 denominator='all-waste' if op=='percentage_point_change' else 'a',
                 period='2022/2023',origin='derived')
        return context([a,b,out],[derivation(op,['a','b'],'out')])

    def test_percentage_points_and_relative_change(self):
        self.assertEqual(self.report(self.percent_change('percentage_point_change','10'))['status'],'pass')
        self.assertEqual(self.report(self.percent_change('relative_change','25'))['status'],'pass')
        self.assertIn('arithmetic_mismatch',self.codes(self.percent_change('relative_change','10')))

    def test_percentage_denominator_is_part_of_meaning(self):
        c=self.percent_change('percentage_point_change','10'); c['facts'][1]['denominator']='food-only'
        self.assertIn('denominator_mismatch',self.codes(c))

    def test_zero_base_not_infinite_relative_growth(self):
        c=self.percent_change('relative_change','25'); c['facts'][0]['value']['amount']='0'
        self.assertIn('zero_denominator',self.codes(c))

    def test_different_years_without_comparison_are_not_contradictions(self):
        c=context([fact('a','40',period='2022'),fact('b','50',period='2023')])
        self.assertEqual(self.report(c)['status'],'pass')
        self.assertEqual(self.report(c)['coverage']['checked_derivations'],0)

    def test_explicit_yield_allows_input_to_output_but_not_different_years(self):
        fs=[fact('input',200),fact('output',70,flow_role='output'),
            fact('yield',35,unit='%',denominator='input',flow_role='not_applicable',origin='derived')]
        c=context(fs,[derivation('yield_percent',['output','input'],'yield')])
        self.assertEqual(self.report(c)['status'],'pass')
        c['facts'][1]['period']='2024'
        self.assertIn('semantic_mismatch',self.codes(c))

    def test_complement_does_not_imply_different_property(self):
        fs=[fact('a',8,unit='%',denominator='area',category='certified'),
            fact('rest',92,unit='%',denominator='area',complement_of='certified',origin='derived')]
        c=context(fs,[derivation('complement_percent',['a'],'rest')])
        self.assertEqual(self.report(c)['status'],'pass')
        c['facts'][1]['complement_of']='uses-fertiliser'
        self.assertIn('category_mismatch',self.codes(c))

    def test_declared_union_subtracts_reviewed_overlap(self):
        fs=[fact('a',600,members=['kitchen','green']),fact('b',150,members=['green']),
            fact('overlap',150,members=['green']),fact('total',600,members=['kitchen','green'],origin='derived')]
        c=context(fs,[derivation('union',['a','b'],'total',overlap='overlap')])
        self.assertEqual(self.report(c)['status'],'pass')
        c['facts'][2]['members']=['unknown-part']
        self.assertIn('overlap_mismatch',self.codes(c))

    def test_identity_share_keeps_denominator(self):
        c=context([fact('a',8,unit='%',denominator='all-area'),
                   fact('out',8,unit='%',denominator='cropland',origin='derived')],
                  [derivation('identity',['a'],'out')])
        self.assertIn('denominator_mismatch',self.codes(c))

    def test_derived_cycle_is_invalid(self):
        c=context([fact('a',1,origin='derived'),fact('b',1,origin='derived')],
                  [derivation('identity',['a'],'b'),derivation('identity',['b'],'a',derivation_id='d2')])
        with self.assertRaises(ValueError): self.report(c)

    def test_locale_is_explicit_and_grouping_valid(self):
        m=self.module()
        self.assertEqual(str(m.parse_local_number('1.234,50','hr')), '1234.50')
        self.assertEqual(str(m.parse_local_number('1,234.50','en')), '1234.50')
        for v,locale in [('1.234',None),('12.34,50','hr'),('1,2,3','en'),('NaN','en')]:
            with self.subTest(v=v),self.assertRaises(ValueError): m.parse_local_number(v,locale)

if __name__=='__main__': unittest.main()
