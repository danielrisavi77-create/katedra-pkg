#!/usr/bin/env python3
import unittest
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import gate

class BoundGateTests(unittest.TestCase):
    def test_legacy_unchanged_and_bound_replaces_consistency(self):
        base={'rad':'rad.docx','pdf':None,'profil':'p.json','tip':'zavrsni','kat':'.katedra'}
        legacy=gate.koraci('audit',base)
        self.assertIn('dosljednost',{x.kid for x in legacy})
        self.assertNotIn('vezani_pregled',{x.kid for x in legacy})
        bound=gate.koraci('audit',{**base,'bound_review':True,'project_root':str(Path.cwd()),'view':'original_no_revisions'})
        ids=[x.kid for x in bound]
        self.assertEqual(ids.count('vezani_pregled'),1)
        self.assertNotIn('dosljednost',ids)
        self.assertTrue(next(x for x in bound if x.kid=='vezani_pregled').blokira)

    def test_bound_predaja_contains_receipt_step(self):
        base={'rad':'rad.docx','pdf':None,'profil':'p.json','tip':'zavrsni','kat':'.katedra',
              'bound_review':True,'project_root':str(Path.cwd()),'view':'original_no_revisions'}
        ids=[x.kid for x in gate.koraci('predaja',base)]
        self.assertEqual(ids.count('vezani_pregled'),1)

    def test_empty_result_is_not_blanket_pass(self):
        code, summary=gate.zakljucak([])
        self.assertNotEqual(code,0)

if __name__=='__main__': unittest.main()
