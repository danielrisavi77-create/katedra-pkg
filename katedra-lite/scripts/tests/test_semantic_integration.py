#!/usr/bin/env python3
"""Real files/CLI and phase-gate integration, including stale and absent evidence."""
from copy import deepcopy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import gate
import inference_context as IC
import numeric_semantics as numeric
from review_fixtures import make_project
from semantic_fixtures import sum_context


def project(root):
    doc,state=make_project(root)
    claims,evidence=IC.ledger_maps(state)
    cid,eid=next(iter(claims)),next(iter(evidence))
    ctx=sum_context()
    for f in ctx['facts']:
        f['claim_id']=cid
        if f['origin']=='source': f['evidence_id']=eid
    ctx['bindings']=IC.capture_bindings(root,doc,state,'original_no_revisions')
    sidecar=state/'inference_context.json'
    sidecar.write_text(json.dumps(ctx,ensure_ascii=False),encoding='utf-8')
    return doc,state,sidecar


class IntegrationTests(unittest.TestCase):
    def test_real_cli_and_stale_source(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d); doc,state,sidecar=project(root); out=state/'numeric.json'
            cmd=[sys.executable,str(Path(numeric.__file__)),'--project-root',str(root),'--rad',str(doc),
                 '--kat',str(state),'--context',str(sidecar),'--view','original_no_revisions','--out',str(out)]
            r=subprocess.run(cmd,capture_output=True,text=True,encoding='utf-8',timeout=30)
            self.assertEqual(r.returncode,0,r.stdout+r.stderr)
            self.assertEqual(json.loads(out.read_text(encoding='utf-8'))['status'],'pass')
            (root/'izvori'/'synthetic.txt').write_text('changed',encoding='utf-8')
            r=subprocess.run(cmd,capture_output=True,text=True,encoding='utf-8',timeout=30)
            self.assertEqual(r.returncode,2,r.stdout+r.stderr)
            self.assertEqual(json.loads(out.read_text(encoding='utf-8'))['status'],'stale')

    def test_missing_context_no_fake_pass(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d); doc,state,sidecar=project(root); sidecar.unlink()
            with self.assertRaises(OSError): numeric.evaluate_file(sidecar,project_root=root,document=doc,state_dir=state,view='original_no_revisions')

    def test_altered_evidence_text_and_link_are_not_accepted(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d); doc,state,sidecar=project(root)
            rows=IC.read_ledger(state/'evidence.jsonl'); rows[0]['text']='changed extracted evidence'
            (state/'evidence.jsonl').write_text(json.dumps(rows[0])+'\n',encoding='utf-8')
            ctx=IC.read_json(sidecar); ctx['bindings']=IC.capture_bindings(root,doc,state,'original_no_revisions')
            sidecar.write_text(json.dumps(ctx),encoding='utf-8')
            r=numeric.evaluate_file(sidecar,project_root=root,document=doc,state_dir=state,view='original_no_revisions')
            self.assertNotEqual(r['status'],'pass')

    def test_duplicate_json_key_rejected(self):
        with self.assertRaises(ValueError): IC.strict_json('{"value":1,"value":2}')
        with self.assertRaises(ValueError): IC.strict_json('{"value":NaN}')

    def test_numeric_gate_explicit_opt_in_in_audit_and_submission(self):
        c={'rad':'rad.docx','pdf':None,'profil':'p.json','tip':'zavrsni','kat':'.katedra'}
        for phase in ('audit','predaja'):
            self.assertNotIn('numeric_semantics',[k.kid for k in gate.koraci(phase,c)])
            steps=gate.koraci(phase,{**c,'inference_context':'.katedra/inference_context.json',
                                    'view':'original_no_revisions','project_root':str(Path.cwd())})
            self.assertEqual([k.kid for k in steps].count('numeric_semantics'),1)
            k=next(k for k in steps if k.kid=='numeric_semantics')
            self.assertTrue(k.blokira); self.assertIn('.katedra/inference_context.json',k.treba)

if __name__=='__main__': unittest.main()
