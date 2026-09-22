#!/usr/bin/env python3
"""Bind review outputs to exact document/dependency bytes and fresh execution."""
from __future__ import annotations
import argparse, hashlib, json, os, subprocess, sys, uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

HERE=Path(__file__).resolve().parent
if str(HERE) not in sys.path: sys.path.insert(0,str(HERE))
from artifact_state import current_record, file_sha256
from context import atomic_write_json
from review_contracts import load_report, validate_report

LIMITATIONS=[
 "supports veze nisu neovisno stručno potvrđene ovim receiptom",
 "nisu izmjerene sve tvrdnje cijelog dokumenta",
 "vizualno i administrativno odobrenje nije dio ovog opsega",
]

def _sha_bytes(data: bytes)->str: return hashlib.sha256(data).hexdigest()
def _canon(obj: object)->bytes:
    return json.dumps(obj,sort_keys=True,separators=(",",":"),ensure_ascii=False,allow_nan=False).encode()
def _implementation_sha(code_root: Path)->str:
    root=Path(code_root).resolve(); parts=[]
    for p in sorted(list(root.rglob("scripts/**/*.py"))+list(root.rglob("references/*schema*.json"))):
        if p.is_file():
            parts.append((p.relative_to(root).as_posix(),file_sha256(p)))
    version=root.parent/"VERSION"
    if version.is_file(): parts.append(("../VERSION",file_sha256(version)))
    return _sha_bytes(_canon(parts))

def capture_context(project_root, *, document, dependencies, view, config, code_root)->dict:
    root=Path(project_root).resolve(); doc=Path(document).resolve()
    art, rec=current_record(root,doc)
    if not art or not rec: raise ValueError("dokument nije praćen u artifact manifestu")
    actual=file_sha256(doc)
    if actual!=rec.get("sha256"): raise ValueError("artifact drift: dokument se promijenio nakon track")
    deps={}
    for name,path in sorted(dependencies.items()):
        p=Path(path)
        if not p.is_file(): raise ValueError(f"nedostaje dependency {name}: {p}")
        deps[name]={"sha256":file_sha256(p),"size_bytes":p.stat().st_size}
    try:
        import jsonschema
        jsv=getattr(jsonschema,"__version__","unknown")
    except ImportError as exc:
        raise ValueError("jsonschema nije dostupan") from exc
    return {
      "document":{"artifact_id":art["artifact_id"],"version_id":rec["version_id"],"sha256":actual,"size_bytes":doc.stat().st_size},
      "dependencies":deps,"view":view,
      "config_sha256":_sha_bytes(_canon(config)),
      "implementation_sha256":_implementation_sha(Path(code_root)),
      "runtime":{"python":sys.version.split()[0],"jsonschema":jsv},
    }

def _report_meta(path: Path|None, code: int|None)->dict:
    return {"sha256": file_sha256(path) if path and path.is_file() else None, "exit_code":code}

def make_receipt(before, after, *, reports, exit_codes)->dict:
    evidence=reports.get("evidence"); consistency=reports.get("consistency"); reviewer=reports.get("reviewer")
    parsed={}
    invalid=False
    for kind,path in (("evidence",evidence),("consistency",consistency)):
        if path and Path(path).is_file():
            try: parsed[kind]=load_report(path,kind)
            except ValueError: invalid=True
    if before!=after: status="stale"
    elif invalid or any(exit_codes.get(k) is None or exit_codes.get(k)>=2 for k in ("evidence","consistency","reviewer")) or not all(p and Path(p).is_file() for p in (evidence,consistency,reviewer)):
        status="unmeasured"
    elif exit_codes.get("evidence")==1 or exit_codes.get("reviewer")==1 or not parsed.get("evidence",{}).get("passed",False):
        status="blocked"
    elif parsed.get("consistency",{}).get("coverage_status")!="sufficient":
        status="unmeasured"
    else: status="pass"
    cons=parsed.get("consistency",{})
    claim_ids={cid for e in cons.get("graph",{}).get("edges",[]) for cid in e.get("claim_ids",[])}
    receipt={"schema_version":1,"kind":"katedra_bound_review","scope":"ledger_evidence_consistency","status":status,
      "before":before,"after":after,
      "reports":{k:_report_meta(Path(reports[k]) if reports.get(k) else None,exit_codes.get(k)) for k in ("evidence","consistency","reviewer")},
      "coverage":{"claims":parsed.get("evidence",{}).get("summary",{}).get("claims",0),"compared_claims":len(claim_ids),"comparison_edges":cons.get("summary",{}).get("edges",0),"whole_document":False},
      "limitations":LIMITATIONS,"created_at":datetime.now(timezone.utc).isoformat()}
    return receipt

def verify_receipt(receipt,current,*,reports)->dict:
    reasons=[]
    if receipt.get("schema_version")!=1 or receipt.get("kind")!="katedra_bound_review": raise ValueError("nevažeći receipt")
    if receipt.get("after")!=current: reasons.append("kontekst se promijenio nakon reviewa")
    for k in ("evidence","consistency","reviewer"):
        p=Path(reports[k])
        expected=(receipt.get("reports",{}).get(k) or {}).get("sha256")
        if not p.is_file() or not expected or file_sha256(p)!=expected: reasons.append(f"{k} report hash mismatch")
    if reasons: return {"status":"stale","reasons":reasons,"relocated":False}
    return {"status":receipt.get("status","unmeasured"),"reasons":[],"relocated":False}

def _run(argv,cwd):
    try:
        r=subprocess.run(argv,cwd=cwd,capture_output=True,text=True,encoding="utf-8",errors="replace",timeout=180,shell=False)
        return r.returncode
    except (OSError,subprocess.TimeoutExpired):
        return 2

def run_bundle(project_root, *, document, state_dir, view, config, code_root)->tuple[int,dict]:
    root=Path(project_root).resolve(); state=Path(state_dir).resolve()
    deps={n:state/f for n,f in {"claims":"claims.jsonl","evidence":"evidence.jsonl","sources":"izvori.json"}.items()}
    before=capture_context(root,document=document,dependencies=deps,view=view,config=config,code_root=Path(code_root))
    run=root/".katedra"/"reviews"/uuid.uuid4().hex; run.mkdir(parents=True)
    reports={k:run/f"{k}.json" for k in ("evidence","consistency","reviewer")}
    codes={}
    codes["evidence"]=_run([sys.executable,str(HERE/"evidence_gate.py"),"--claims",str(deps["claims"]),"--evidence",str(deps["evidence"]),"--sources",str(deps["sources"]),"--policy","strict","--out",str(reports["evidence"])],root)
    codes["consistency"]=_run([sys.executable,str(HERE/"consistency_check.py"),"--claims",str(deps["claims"]),"--out",str(reports["consistency"])],root)
    if reports["evidence"].is_file() and reports["consistency"].is_file():
        codes["reviewer"]=_run([sys.executable,str(HERE/"reviewer_simulation.py"),"--evidence-gate",str(reports["evidence"]),"--consistency",str(reports["consistency"]),"--out",str(reports["reviewer"])],root)
    else: codes["reviewer"]=2
    after=capture_context(root,document=document,dependencies=deps,view=view,config=config,code_root=Path(code_root))
    receipt=make_receipt(before,after,reports=reports,exit_codes=codes)
    atomic_write_json(str(run/"receipt.json"),receipt,sidro=str(root))
    code=0 if receipt["status"]=="pass" else 1 if receipt["status"]=="blocked" else 2
    return code,receipt

def main()->int:
    ap=argparse.ArgumentParser(); sub=ap.add_subparsers(dest="cmd",required=True)
    r=sub.add_parser("run"); r.add_argument("--project-root",required=True); r.add_argument("--rad",required=True); r.add_argument("--kat",required=True); r.add_argument("--view",required=True)
    a=ap.parse_args()
    if a.cmd=="run":
        code,receipt=run_bundle(a.project_root,document=a.rad,state_dir=a.kat,view=a.view,config={"policy":"strict"},code_root=HERE.parent)
        print(json.dumps(receipt,ensure_ascii=False,indent=2)); return code
    return 2
if __name__=="__main__": raise SystemExit(main())
