#!/usr/bin/env python3
"""E11–E18: declared inference scope and transitive freshness with controls."""
from copy import deepcopy
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from semantic_fixtures import context, sum_context


def sh(text): return hashlib.sha256(text.encode('utf-8')).hexdigest()


def example():
    claims={i:{'claim_id':i,'text':text,'evidence':[{'evidence_id':'e'+i,'relation':'supports'}]} for i,text in
            [('a','U dva analizirana slučaja postoji povezanost.'),('b','U uzorku je zabilježena povezanost.'),('c','Zaključak je ograničen na analizirani uzorak.')]}
    ev={'e'+i:{'evidence_id':'e'+i,'text':row['text'],'text_sha256':sh(row['text'])} for i,row in claims.items()}
    nodes=[{'claim_id':i,'reviewed_text_sha256':sh(r['text']),'evidence_state':'confirmed','reviewer':'Example reviewer',
            'evidence_ids':['e'+i],'units':['case1','case2'],'assertion':'descriptive','category':None,
            'complement_of':None,'as_of':None,'scope_evidence_id':None,'features':[]} for i,r in claims.items()]
    links=[{'link_id':p+q,'premise':p,'conclusion':q,'kind':'supports','reviewed_premise_sha256':sh(claims[p]['text']),
            'reviewer':'Example reviewer','causal_basis':None} for p,q in [('a','b'),('b','c')]]
    c=context(); c['inference']={'nodes':nodes,'links':links,'criteria':[],'cases':[],'evidence_scopes':[],
                               'required_claim_ids':['a','b','c']}
    return c,claims,ev


class InferenceTests(unittest.TestCase):
    def module(self):
        self.assertIsNotNone(importlib.util.find_spec('claim_inference'), 'C engine is not implemented')
        return importlib.import_module('claim_inference')

    def report(self,c=None,cl=None,ev=None):
        if c is None: c,cl,ev=example()
        return self.module().evaluate(c,cl,ev)

    def test_current_reviewed_chain_passes_scoped(self):
        r=self.report(); self.assertEqual(r['status'],'pass'); self.assertFalse(r['coverage']['whole_document'])
        self.assertEqual(r['affected_claim_ids'],[])

    def test_changed_premise_invalidates_all_descendants(self):
        c,cl,ev=example(); cl['a']['text']='Ispravljena premisa.'
        r=self.report(c,cl,ev); self.assertEqual(r['status'],'review_required')
        self.assertEqual(r['affected_claim_ids'],['a','b','c'])

    def test_changed_edge_snapshot_invalidates_conclusion(self):
        c,cl,ev=example(); c['inference']['links'][0]['reviewed_premise_sha256']='0'*64
        self.assertEqual(self.report(c,cl,ev)['affected_claim_ids'],['b','c'])

    def test_unknown_or_contradicted_premise_never_auto_false_or_pass(self):
        for state in ('unknown','contradicted'):
            c,cl,ev=example(); c['inference']['nodes'][0]['evidence_state']=state
            with self.subTest(state=state):
                r=self.report(c,cl,ev); self.assertEqual(r['status'],'review_required')
                self.assertEqual(r['affected_claim_ids'],['a','b','c'])

    def test_independent_re_review_cuts_propagation(self):
        c,cl,ev=example(); cl['a']['text']='Changed premise'
        c['inference']['nodes'][1]['independent_review']={
            'claim_sha256':sh(cl['b']['text']),'evidence_ids':['eb'],'reviewer':'Second reviewer'}
        self.assertEqual(self.report(c,cl,ev)['affected_claim_ids'],['a'])

    def test_stale_independent_review_cannot_clear(self):
        c,cl,ev=example(); cl['a']['text']='Changed premise'
        c['inference']['nodes'][1]['independent_review']={
            'claim_sha256':'0'*64,'evidence_ids':['eb'],'reviewer':'Second reviewer'}
        self.assertIn('c',self.report(c,cl,ev)['affected_claim_ids'])

    def test_dangling_edges_duplicate_ids_and_cycles_rejected(self):
        for case in ('dangling','duplicate','cycle'):
            c,cl,ev=example()
            if case=='dangling': c['inference']['links'][0]['premise']='absent'
            elif case=='duplicate': c['inference']['nodes'][1]['claim_id']='a'
            else:
                e=deepcopy(c['inference']['links'][0]); e.update(link_id='ca',premise='c',conclusion='a')
                c['inference']['links'].append(e)
            with self.subTest(case=case), self.assertRaises(ValueError): self.report(c,cl,ev)

    def test_absent_required_claim_is_unmeasured(self):
        c,cl,ev=example(); c['inference']['required_claim_ids'].append('missing')
        self.assertEqual(self.report(c,cl,ev)['status'],'unmeasured')

    def test_no_nodes_never_passes(self):
        c,cl,ev=example(); c['inference']['nodes']=[]; c['inference']['links']=[]
        self.assertEqual(self.report(c,cl,ev)['status'],'unmeasured')

    def test_absent_evidence_or_context_only_is_not_support(self):
        for case in ('absent','contextualizes','changed_text'):
            c,cl,ev=example()
            if case=='absent': del ev['ea']
            elif case=='contextualizes': cl['a']['evidence'][0]['relation']='contextualizes'
            else: ev['ea']['text']='not the reviewed evidence'
            with self.subTest(case=case): self.assertNotEqual(self.report(c,cl,ev)['status'],'pass')

    def test_generalisation_scope_needs_review_not_claimed_falsehood(self):
        c,cl,ev=example(); c['inference']['links'][0]['kind']='generalises'
        c['inference']['nodes'][1]['units']=['all-of-country']
        r=self.report(c,cl,ev)
        self.assertEqual(r['status'],'review_required'); self.assertIn('scope_overreach',{f['code'] for f in r['findings']})

    def test_in_sample_scope_is_not_overreach(self):
        c,cl,ev=example(); c['inference']['links'][0]['kind']='generalises'
        self.assertEqual(self.report(c,cl,ev)['status'],'pass')

    def test_association_is_not_automatic_causation(self):
        c,cl,ev=example(); c['inference']['links'][0]['kind']='causal'
        self.assertEqual(self.report(c,cl,ev)['status'],'review_required')
        c['inference']['links'][0]['causal_basis']={'evidence_id':'ea','reviewer':'Method reviewer','reason':'Reviewed design and identification assumptions'}
        self.assertEqual(self.report(c,cl,ev)['status'],'pass')

    def test_complement_and_unknown_absence_inference(self):
        c,cl,ev=example(); c['inference']['links'][0]['kind']='complement'
        c['inference']['nodes'][0]['category']='organic'
        c['inference']['nodes'][1]['complement_of']='organic'
        self.assertEqual(self.report(c,cl,ev)['status'],'pass')
        c['inference']['nodes'][1]['category']='uses-mineral-input'
        self.assertIn('unsupported_complement',{f['code'] for f in self.report(c,cl,ev)['findings']})
        c,cl,ev=example(); c['inference']['nodes'][0]['evidence_state']='unknown'
        c['inference']['links'][0]['kind']='absence'
        self.assertIn('unknown_is_not_absence',{f['code'] for f in self.report(c,cl,ev)['findings']})

    def test_method_requirement_vs_included_case(self):
        c,cl,ev=example(); c['inference']['criteria']=[{'criterion_id':'user','description':'Known recipient',
            'required_state':'confirmed','source_locator':'method section 1'}]
        case={'case_id':'plant','status':'included','reason':'','observations':[{'criterion_id':'user','state':'unknown'}]}
        c['inference']['cases']=[case]
        self.assertEqual(self.report(c,cl,ev)['status'],'review_required')
        case['observations'][0]['state']='contradicted'
        self.assertEqual(self.report(c,cl,ev)['status'],'blocked')
        case['status']='pilot'; case['reason']='Pilot infrastructure; not evidence of an operating loop'
        self.assertEqual(self.report(c,cl,ev)['status'],'pass')

    def test_certificate_scope_period_and_features(self):
        c,cl,ev=example()
        c['inference']['evidence_scopes']=[{'scope_id':'cert','kind':'certificate','evidence_id':'ea',
            'holder':'Example','subject':'Waste process','units':['case1','case2'],'features':['process'],
            'valid_from':'2022-01-01','valid_until':'2024-12-31','locator':'certificate section 1','reviewer':'R'}]
        node=c['inference']['nodes'][0];node.update(scope_evidence_id='cert',as_of='2023-01-01',features=['process'])
        self.assertEqual(self.report(c,cl,ev)['status'],'pass')
        node['features']=['all-published-statistics']
        self.assertEqual(self.report(c,cl,ev)['status'],'review_required')
        node['features']=['process'];node['as_of']='2025-01-01'
        self.assertEqual(self.report(c,cl,ev)['status'],'review_required')

    def test_unlinked_certificate_cannot_authorise_scope(self):
        c,cl,ev=example()
        c['inference']['evidence_scopes']=[{'scope_id':'cert','kind':'certificate','evidence_id':'eb',
            'holder':'Example','subject':'Waste','units':['case1','case2'],'features':['process'],
            'valid_from':'2022-01-01','valid_until':'2024-12-31','locator':'section 1','reviewer':'R'}]
        c['inference']['nodes'][0].update(scope_evidence_id='cert',as_of='2023-01-01',features=['process'])
        self.assertEqual(self.report(c,cl,ev)['status'],'review_required')

    def test_declared_causal_assertion_requires_causal_review_link(self):
        c,cl,ev=example();c['inference']['nodes'][1]['assertion']='causal'
        self.assertEqual(self.report(c,cl,ev)['status'],'review_required')

    def test_unrelated_dirty_claim_does_not_invalidate_independent_review(self):
        c,cl,ev=example();cl['a']['text']='Changed premise'
        cl['d']={'claim_id':'d','text':'Unrelated fact','evidence':[{'evidence_id':'eb','relation':'supports'}]}
        n=deepcopy(c['inference']['nodes'][1]);n.update(claim_id='d',reviewed_text_sha256=sh(cl['d']['text']),evidence_state='unknown')
        c['inference']['nodes'].append(n);c['inference']['required_claim_ids'].append('d')
        c['inference']['nodes'][1]['independent_review']={'claim_sha256':sh(cl['b']['text']),'evidence_ids':['eb'],'reviewer':'R2'}
        self.assertEqual(self.report(c,cl,ev)['affected_claim_ids'],['a','d'])

    def test_epistemic_strengthening_only_is_signal(self):
        m=self.module()
        signals=m.epistemic_signals('Podaci mogu upućivati na povezanost.', 'Podaci dokazuju uzročnost.')
        self.assertEqual(signals[0]['severity'],'review_required')
        self.assertEqual(signals[0]['code'],'epistemic_strengthening')

    def test_epistemic_negation_quotes_and_preserved_uncertainty(self):
        m=self.module()
        cases=[('Podaci mogu upućivati na povezanost.','Podaci ne dokazuju uzročnost.'),
               ('Podaci mogu upućivati na povezanost.','Podaci možda upućuju na povezanost.'),
               ('Autor je napisao „može biti povezano”.','Autor je napisao „uzrokuje promjenu”.')]
        for before,after in cases:
            with self.subTest(after=after): self.assertEqual(m.epistemic_signals(before,after),[])

    def test_epistemic_expansion_from_sample_is_signal(self):
        r=self.module().epistemic_signals('U analiziranim slučajevima postoji posrednik.',
                                        'U Hrvatskoj svi subjekti koriste posrednika.')
        self.assertTrue(any(f['code']=='scope_expansion' for f in r))

    def test_no_automatic_semantic_rewriting(self):
        c,cl,ev=example(); saved=deepcopy((c,cl,ev));self.report(c,cl,ev)
        self.assertEqual((c,cl,ev),saved)

if __name__=='__main__': unittest.main()
