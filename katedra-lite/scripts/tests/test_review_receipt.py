#!/usr/bin/env python3
import tempfile, unittest
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import artifact_state
import review_receipt as rr
from review_fixtures import make_project

class ReceiptTests(unittest.TestCase):
    def test_E05_document_drift_is_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d); document=root/'rad.docx'; document.write_bytes(b'synthetic-document-A')
            artifact_state.record_artifact(root,document)
            claims=root/'claims.jsonl'; claims.write_text('{}\n',encoding='utf-8')
            args=dict(document=document,dependencies={'claims':claims},view='original_no_revisions',
                      config={'policy':'strict'},code_root=Path(rr.__file__).parents[1])
            first=rr.capture_context(root,**args)
            self.assertEqual(first['document']['sha256'], artifact_state.file_sha256(document))
            document.write_bytes(b'synthetic-document-B')
            with self.assertRaises(ValueError):
                rr.capture_context(root,**args)

    def test_E06_dependency_change_changes_context(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d); document=root/'rad.docx'; document.write_bytes(b'doc')
            artifact_state.record_artifact(root,document)
            claims=root/'claims.jsonl'; claims.write_text('A\n',encoding='utf-8')
            args=dict(document=document,dependencies={'claims':claims},view='original_no_revisions',
                      config={'policy':'strict'},code_root=Path(rr.__file__).parents[1])
            before=rr.capture_context(root,**args)
            claims.write_text('B\n',encoding='utf-8')
            after=rr.capture_context(root,**args)
            self.assertNotEqual(before['dependencies']['claims']['sha256'],after['dependencies']['claims']['sha256'])

    def test_fresh_bundle_runs_real_producers(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d); document,state=make_project(root)
            code,receipt=rr.run_bundle(root,document=document,state_dir=state,
                view='original_no_revisions',config={'policy':'strict'},code_root=Path(rr.__file__).parents[1])
            self.assertEqual(code,0)
            self.assertEqual(receipt['status'],'pass')
            self.assertFalse(receipt['coverage']['whole_document'])
            document.write_bytes(document.read_bytes()+b'x')
            with self.assertRaises(ValueError):
                rr.capture_context(root,document=document,
                    dependencies={'claims':state/'claims.jsonl'},view='original_no_revisions',
                    config={'policy':'strict'},code_root=Path(rr.__file__).parents[1])

if __name__=='__main__': unittest.main()
