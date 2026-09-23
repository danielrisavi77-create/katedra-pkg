#!/usr/bin/env python3
"""Strict sidecar IO and exact input binding for numeric/inference review.

Annotations are assertions by the named reviewer, not independently certified facts.
No original manuscript, ledger or source is modified by this module.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
from datetime import datetime, timezone
from decimal import Decimal
import hashlib
import json
from pathlib import Path
from typing import Any

from artifact_state import current_record, file_sha256
from context import atomic_write_json
from review_contracts import invalid_constant, unique_object
from review_receipt import bound_dependencies

HERE = Path(__file__).resolve().parent
SCHEMA = HERE.parent / 'references' / 'inference_context_schema.json'
MAX_JSON = 8 * 1024 * 1024


def strict_json(text: str) -> Any:
    if len(text.encode('utf-8')) > MAX_JSON:
        raise ValueError('JSON exceeds the 8 MiB review limit')
    return json.loads(text, object_pairs_hook=unique_object, parse_constant=invalid_constant)


def read_json(path: str | Path) -> Any:
    p = Path(path)
    if p.stat().st_size > MAX_JSON:
        raise ValueError('JSON exceeds the 8 MiB review limit')
    return strict_json(p.read_text(encoding='utf-8'))


def read_ledger(path: str | Path) -> list[dict]:
    p = Path(path)
    if p.stat().st_size > MAX_JSON:
        raise ValueError('Ledger exceeds the 8 MiB review limit')
    rows = [strict_json(line) for line in p.read_text(encoding='utf-8').splitlines() if line.strip()]
    if not all(isinstance(row, dict) for row in rows):
        raise ValueError('Each ledger row must be an object')
    return rows


def sha_text(text: str) -> str:
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


def validate(data: dict) -> None:
    from jsonschema import Draft202012Validator
    errors = list(Draft202012Validator(read_json(SCHEMA)).iter_errors(data))
    if errors:
        e = errors[0]
        raise ValueError(f"Invalid inference context at {list(e.path)}: {e.message}")
    facts = data['facts']
    ids = [r['fact_id'] for r in facts]
    ds = [r['derivation_id'] for r in data['derivations']]
    if len(ids) != len(set(ids)) or len(ds) != len(set(ds)):
        raise ValueError('Duplicate fact or derivation ID')
    for fact in facts:
        value = fact['value']
        if value['kind'] == 'interval' and Decimal(value['lower']) > Decimal(value['upper']):
            raise ValueError('Interval lower bound is greater than upper bound')
        if fact['origin'] == 'source' and (not fact['evidence_id'] or not fact['locator']):
            raise ValueError('Source facts require evidence ID and locator')
    outputs: set[str] = set()
    graph: dict[str, list[str]] = {}
    for d in data['derivations']:
        t = d['tolerance']
        if Decimal(t['absolute']) < 0 or (Decimal(t['absolute']) > 0 and
                (not t['reason'].strip() or not t['reviewer'].strip())):
            raise ValueError('Nonzero tolerance requires reason and reviewer; tolerance cannot be negative')
        refs = [*d['inputs'], d['result']] + ([d['overlap']] if 'overlap' in d else [])
        if any(r not in ids for r in refs):
            raise ValueError('Unknown fact reference in derivation')
        if d['result'] in outputs or d['result'] in d['inputs']:
            raise ValueError('Derived fact has multiple definitions or self dependency')
        outputs.add(d['result'])
        graph[d['result']] = d['inputs'] + ([d['overlap']] if 'overlap' in d else [])
        n = len(d['inputs'])
        unary = d['operation'] in {'identity','complement_percent'}
        binary = d['operation'] in {'union','difference','percentage_point_change','relative_change','ratio_percent','yield_percent'}
        if (unary and n != 1) or (binary and n != 2) or (d['operation']=='sum' and n < 2):
            raise ValueError('Wrong number of inputs for numeric operation')
        if (d['operation']=='union') != ('overlap' in d):
            raise ValueError('Only a union requires an explicit overlap fact')
    # Iterative cycle detection: no recursion limit on a valid long dependency chain.
    left = {k:set(v) & outputs for k,v in graph.items()}
    while left:
        ready = {k for k,v in left.items() if not v}
        if not ready:
            raise ValueError('Cyclic numeric derivation graph')
        left = {k:v-ready for k,v in left.items() if k not in ready}


def capture_bindings(project_root: str | Path, document: str | Path,
                     state_dir: str | Path, view: str) -> dict:
    root, doc, state = Path(project_root).resolve(), Path(document).resolve(), Path(state_dir).resolve()
    if view not in {'original_no_revisions','accepted_copy','rejected_copy'}:
        raise ValueError('Explicit supported document view is required')
    art, rec = current_record(root, doc)
    if not art or not rec or rec.get('sha256') != file_sha256(doc):
        raise ValueError('Track exact document bytes in artifact manifest before annotating')
    deps = bound_dependencies(root, state)
    return {'document': {'artifact_id': art['artifact_id'], 'version_id': rec['version_id'],
                         'sha256': file_sha256(doc)},
            **{key+'_sha256':file_sha256(deps[key]) for key in ('claims','evidence','sources')},
            'source_files':{name.split(':',1)[1]:file_sha256(path)
                            for name,path in deps.items() if name.startswith('source:')}, 'view':view}


def ledger_maps(state_dir: str | Path) -> tuple[dict, dict]:
    state = Path(state_dir)
    out = []
    for name, key in [('claims.jsonl','claim_id'),('evidence.jsonl','evidence_id')]:
        rows = read_ledger(state / name)
        if any(not isinstance(r.get(key),str) or not r[key].strip() for r in rows):
            raise ValueError(f'Missing {key} in {name}')
        if len({r[key] for r in rows}) != len(rows):
            raise ValueError(f'Duplicate {key} in {name}')
        out.append({r[key]:r for r in rows})
    return out[0], out[1]


def binding_findings(data: dict, current: dict, claims: dict, evidence: dict) -> list[dict]:
    findings = []
    if data['bindings'] != current:
        findings.append({'code':'stale_bindings','severity':'stale','ids':[],
                         'message':'Document, ledger, source bytes or view differ from the reviewed sidecar'})
    for f in data['facts']:
        cid, eid = f['claim_id'], f['evidence_id']
        if cid not in claims or (f['origin']=='source' and eid not in evidence):
            findings.append({'code':'unresolved_evidence','severity':'unmeasured','ids':[f['fact_id']],
                             'message':'Numeric annotation refers to an absent claim or evidence row'})
        elif f['origin']=='source':
            row = evidence[eid]
            actual_source = current['source_files'].get(str(row.get('source_path','')).replace('\\','/'))
            if (not isinstance(row.get('text'), str) or
                    sha_text(row['text']) != row.get('text_sha256') or
                    actual_source is None or actual_source != row.get('source_sha256')):
                findings.append({'code':'stale_evidence','severity':'stale','ids':[f['fact_id']],
                                 'message':'Evidence text or local source no longer matches its stored fingerprint'})
            links = {r['evidence_id'] for r in claims[cid].get('evidence',[]) if r.get('relation') == 'supports'}
            if eid not in links:
                findings.append({'code':'evidence_not_linked','severity':'unmeasured','ids':[f['fact_id']],
                                 'message':'Numeric source is not linked by the existing claim ledger'})
    return findings


def result_report(kind: str, findings: list[dict], coverage: dict, **extra: Any) -> dict:
    severity = {r['severity'] for r in findings}
    status = next((s for s in ('stale','blocked','unmeasured','review_required') if s in severity), 'pass')
    return {'schema_version':1, 'kind':kind, 'status':status, 'findings':findings,
            'coverage':{**coverage,'whole_document':False},
            'limitations':['Structured semantic annotations are not independent source verification.',
                           'No claim of full-manuscript coverage or visual/administrative approval.'], **extra}


def exit_code(report: dict) -> int:
    return 0 if report['status']=='pass' else 1 if report['status']=='blocked' else 2


def assert_safe_report_output(path, *, project_root, state_dir, document, sidecar, kind):
    """A report may replace its own earlier report, never a bound input or an arbitrary file."""
    out = Path(path)
    protected = [Path(document), Path(sidecar), *bound_dependencies(project_root, state_dir).values(),
                 Path(project_root)/'.katedra'/'artifacts.json', Path(state_dir)/'stanje.json',
                 Path(state_dir)/'resolved_profile.json']
    if out.suffix != '.json' or out.is_symlink() or out.resolve() in {p.resolve() for p in protected}:
        raise ValueError('Report path aliases an input or is not a JSON report')
    if out.exists():
        for candidate in protected:
            if candidate.exists() and out.samefile(candidate):
                raise ValueError('Report path is a hardlink to a bound input')
        previous = read_json(out)
        if not isinstance(previous, dict) or previous.get('kind') != kind:
            raise ValueError("Refusing to overwrite a file that is not this tool report")


def save_report(path: str | Path, report: dict) -> None:
    atomic_write_json(str(path), report)


def main() -> int:
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('command', choices=['init'])
    ap.add_argument('--project-root', required=True); ap.add_argument('--rad', required=True)
    ap.add_argument('--kat', required=True); ap.add_argument('--view', required=True)
    ap.add_argument('--out', required=True)
    a=ap.parse_args()
    try:
        out=Path(a.out)
        if out.exists() or out.is_symlink(): raise ValueError('Sidecar already exists; do not overwrite annotations')
        data={'schema_version':1,'bindings':capture_bindings(a.project_root,a.rad,a.kat,a.view),
              'facts':[],'derivations':[],'required_fact_ids':[],'required_derivation_ids':[]}
        validate(data); save_report(out,data)
        print('Empty bound template created; no numeric or semantic review has passed.')
        return 0
    except (OSError, ValueError) as exc:
        print(str(exc)); return 2

if __name__ == '__main__': raise SystemExit(main())
