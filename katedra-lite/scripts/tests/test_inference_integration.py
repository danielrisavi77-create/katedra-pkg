#!/usr/bin/env python3
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import gate
import claim_inference as ci
import inference_context as IC
import verify_rewrite as rw
from test_semantic_integration import project


class InferenceIntegrationTests(unittest.TestCase):
    def test_qualitative_cli_uses_actual_ledger_fingerprints(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d); doc,state,sidecar=project(root); claims,evidence=IC.ledger_maps(state)
            ctx=IC.read_json(sidecar)
            nodes=[{'claim_id':cid,'reviewed_text_sha256':IC.sha_text(row['text']), 'reviewer':'R',
                    'evidence_state':'confirmed','evidence_ids':[next(iter(evidence))],'units':['case-X'],
                    'assertion':'descriptive','category':None,'complement_of':None,'as_of':None,
                    'scope_evidence_id':None,'features':[]} for cid,row in claims.items()]
            ctx['inference']={'nodes':nodes,'links':[],'criteria':[],'cases':[],'evidence_scopes':[],
                              'required_claim_ids':list(claims)}
            sidecar.write_text(json.dumps(ctx),encoding='utf-8'); out=state/'claim-inference.json'
            cmd=[sys.executable,str(Path(ci.__file__)),'--context',str(sidecar),'--project-root',str(root),
                 '--rad',str(doc),'--kat',str(state),'--view','original_no_revisions','--out',str(out)]
            r=subprocess.run(cmd,capture_output=True,text=True,encoding='utf-8',timeout=30)
            self.assertEqual(r.returncode,0,r.stdout+r.stderr)
            ctx['facts'][2]['value']['amount']='999'; sidecar.write_text(json.dumps(ctx),encoding='utf-8')
            r=subprocess.run(cmd,capture_output=True,text=True,encoding='utf-8',timeout=30)
            self.assertEqual(r.returncode,1,r.stdout+r.stderr)
            result=IC.read_json(out)
            self.assertTrue(result['affected_claim_ids'])

    def test_claim_gate_is_opt_in_and_blocks_when_inputs_missing(self):
        c={'rad':'rad.docx','pdf':None,'profil':'p.json','tip':'zavrsni','kat':'.katedra'}
        for phase in ('audit','predaja'):
            self.assertNotIn('claim_inference',[k.kid for k in gate.koraci(phase,c)])
            steps=gate.koraci(phase,{**c,'claim_inference_context':'context.json','view':'original_no_revisions'})
            found=[k for k in steps if k.kid=='claim_inference']
            self.assertEqual(len(found),1); self.assertTrue(found[0].blokira)

    def test_rewrite_cli_epistemic_review_requires_review_not_falsehood(self):
        with tempfile.TemporaryDirectory() as d:
            a,b=Path(d)/'before.md',Path(d)/'after.md'
            a.write_text('# Uvod\n\nPodaci mogu upućivati na povezanost.\n',encoding='utf-8')
            b.write_text('# Uvod\n\nPodaci dokazuju uzročnost.\n',encoding='utf-8')
            cmd=[sys.executable,str(Path(rw.__file__)),str(a),str(b),'--zahvat','stil','--epistemic-review']
            r=subprocess.run(cmd,capture_output=True,text=True,encoding='utf-8',timeout=30)
            self.assertEqual(r.returncode,2,r.stdout+r.stderr)
            self.assertIn('epistemic_strengthening',r.stdout)
            self.assertNotIn('sigurno primijeniti',r.stdout)

if __name__=='__main__':unittest.main()
