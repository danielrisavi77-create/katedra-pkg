#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, shutil, subprocess, sys, uuid
from datetime import datetime, timezone
from pathlib import Path
HERE=Path(__file__).resolve().parent
if str(HERE) not in sys.path: sys.path.insert(0,str(HERE))
from artifact_state import current_record, file_sha256
from context import atomic_write_json
from review_contracts import load_report
LIMITATIONS=["supports veze nisu neovisno stručno potvrđene ovim receiptom","nisu izmjerene sve tvrdnje cijelog dokumenta","vizualno i administrativno odobrenje nije dio ovog opsega"]
def _canon(o): return json.dumps(o,sort_keys=True,separators=(",",":"),ensure_ascii=False,allow_nan=False).encode()
def _sha(b): return hashlib.sha256(b).hexdigest()
def _implementation_sha(root):
    root=Path(root).resolve(); rows=[]
    for p in sorted(list(root.rglob("scripts/**/*.py"))+list(root.rglob("references/*schema*.json"))):
        if p.is_file(): rows.append((p.relative_to(root).as_posix(),file_sha256(p)))
    v=root.parent/"VERSION"
    if v.is_file(): rows.append(("../VERSION",file_sha256(v)))
    return _sha(_canon(rows))
def capture_context(project_root,*,document,dependencies,view,config,code_root):
    root=Path(project_root).resolve(); doc=Path(document).resolve(); art,rec=current_record(root,doc)
    if not art or not rec: raise ValueError("dokument nije praćen u artifact manifestu")
    actual=file_sha256(doc)
    if actual!=rec.get("sha256"): raise ValueError("artifact drift: dokument se promijenio nakon track")
    deps={}
    for n,p0 in sorted(dependencies.items()):
        p=Path(p0)
        if not p.is_file(): raise ValueError(f"nedostaje dependency {n}: {p}")
        deps[n]={"sha256":file_sha256(p),"size_bytes":p.stat().st_size}
    try:
        import jsonschema
        jsv=getattr(jsonschema,"__version__","unknown")
    except ImportError as exc: raise ValueError("jsonschema nije dostupan") from exc
    return {"document":{"artifact_id":art["artifact_id"],"version_id":rec["version_id"],"sha256":actual,"size_bytes":doc.stat().st_size},"dependencies":deps,"view":view,"config_sha256":_sha(_canon(config)),"implementation_sha256":_implementation_sha(Path(code_root)),"runtime":{"python":sys.version.split()[0],"jsonschema":jsv}}
def _meta(p,code): return {"sha256":file_sha256(p) if p and Path(p).is_file() else None,"exit_code":code}
def make_receipt(before,after,*,reports,exit_codes):
    parsed={}; invalid=False
    for k in ("evidence","consistency"):
        p=reports.get(k)
        if p and Path(p).is_file():
            try: parsed[k]=load_report(p,k)
            except ValueError: invalid=True
    missing=not all(reports.get(k) and Path(reports[k]).is_file() for k in ("evidence","consistency","reviewer"))
    if before!=after: status="stale"
    elif invalid or missing or any(exit_codes.get(k) is None or exit_codes.get(k)>=2 for k in ("evidence","consistency","reviewer")): status="unmeasured"
    elif exit_codes.get("evidence")==1 or exit_codes.get("reviewer")==1 or not parsed.get("evidence",{}).get("passed",False): status="blocked"
    elif parsed.get("consistency",{}).get("coverage_status")!="sufficient": status="unmeasured"
    else: status="pass"
    cons=parsed.get("consistency",{}); ids={i for e in cons.get("graph",{}).get("edges",[]) for i in e.get("claim_ids",[])}
    return {"schema_version":1,"kind":"katedra_bound_review","scope":"ledger_evidence_consistency","status":status,"before":before,"after":after,"reports":{k:_meta(reports.get(k),exit_codes.get(k)) for k in ("evidence","consistency","reviewer")},"coverage":{"claims":parsed.get("evidence",{}).get("summary",{}).get("claims",0),"compared_claims":len(ids),"comparison_edges":cons.get("summary",{}).get("edges",0),"whole_document":False},"limitations":LIMITATIONS,"created_at":datetime.now(timezone.utc).isoformat()}
def verify_receipt(receipt,current,*,reports):
    if receipt.get("schema_version")!=1 or receipt.get("kind")!="katedra_bound_review": raise ValueError("nevažeći receipt")
    reasons=[]
    if receipt.get("after")!=current: reasons.append("kontekst se promijenio nakon reviewa")
    for k in ("evidence","consistency","reviewer"):
        p=Path(reports[k]); exp=(receipt.get("reports",{}).get(k) or {}).get("sha256")
        if not p.is_file() or not exp or file_sha256(p)!=exp: reasons.append(f"{k} report hash mismatch")
    return {"status":"stale" if reasons else receipt.get("status","unmeasured"),"reasons":reasons,"relocated":False}
def _run(argv,cwd):
    try: return subprocess.run(argv,cwd=cwd,capture_output=True,text=True,encoding="utf-8",errors="replace",timeout=180,shell=False).returncode
    except (OSError,subprocess.TimeoutExpired): return 2
def run_bundle(project_root,*,document,state_dir,view,config,code_root):
    root=Path(project_root).resolve(); state=Path(state_dir).resolve()
    deps={"claims":state/"claims.jsonl","evidence":state/"evidence.jsonl","sources":state/"izvori.json"}
    before=capture_context(root,document=document,dependencies=deps,view=view,config=config,code_root=code_root)
    run=root/".katedra"/"reviews"/uuid.uuid4().hex; run.mkdir(parents=True)
    inputs=run/"inputs"; snap_state=inputs/".katedra"; snap_state.mkdir(parents=True)
    snap_deps={name:snap_state/path.name for name,path in deps.items()}
    for name,path in deps.items():
        shutil.copy2(path,snap_deps[name])
    # Preserve project-relative source paths used by the evidence ledger.
    for line in snap_deps["evidence"].read_text(encoding="utf-8").splitlines():
        if not line.strip(): continue
        row=json.loads(line); sp=str(row.get("source_path") or "")
        if not sp: continue
        src=Path(sp)
        if src.is_absolute():
            raise ValueError("bound review ne prihvaća apsolutni/vanjski source_path; ponovi ingest unutar projekta")
        source=(root/src).resolve()
        try: rel=source.relative_to(root)
        except ValueError as exc: raise ValueError("source_path izlazi iz projekta") from exc
        if not source.is_file(): raise ValueError(f"nedostaje source datoteka: {sp}")
        target=inputs/rel; target.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(source,target)
    reports={k:run/f"{k}.json" for k in ("evidence","consistency","reviewer")}; codes={}
    codes["evidence"]=_run([sys.executable,str(HERE/"evidence_gate.py"),"--claims",str(snap_deps["claims"]),"--evidence",str(snap_deps["evidence"]),"--sources",str(snap_deps["sources"]),"--policy","strict","--out",str(reports["evidence"])],inputs)
    codes["consistency"]=_run([sys.executable,str(HERE/"consistency_check.py"),"--claims",str(snap_deps["claims"]),"--out",str(reports["consistency"])],inputs)
    codes["reviewer"]=_run([sys.executable,str(HERE/"reviewer_simulation.py"),"--evidence-gate",str(reports["evidence"]),"--consistency",str(reports["consistency"]),"--out",str(reports["reviewer"])],root) if reports["evidence"].is_file() and reports["consistency"].is_file() else 2
    after=capture_context(root,document=document,dependencies=deps,view=view,config=config,code_root=code_root)
    receipt=make_receipt(before,after,reports=reports,exit_codes=codes); atomic_write_json(str(run/"receipt.json"),receipt,sidro=str(root))
    return (0 if receipt["status"]=="pass" else 1 if receipt["status"]=="blocked" else 2),receipt
def main():
    ap=argparse.ArgumentParser(); sub=ap.add_subparsers(dest="cmd",required=True); r=sub.add_parser("run")
    for x in ("project-root","rad","kat","view"): r.add_argument("--"+x,required=True)
    a=ap.parse_args(); code,rec=run_bundle(a.project_root,document=a.rad,state_dir=a.kat,view=a.view,config={"policy":"strict"},code_root=HERE.parent); print(json.dumps(rec,ensure_ascii=False,indent=2)); return code
if __name__=="__main__": raise SystemExit(main())
