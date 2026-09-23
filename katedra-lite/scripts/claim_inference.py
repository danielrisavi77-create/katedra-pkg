#!/usr/bin/env python3
"""Read-only dependency/scope review of explicitly annotated academic claims.

Textual heuristics identify review candidates. They never prove causation, legal
meaning, universal falsehood or a certificate's validity by themselves.
"""
from __future__ import annotations

import argparse
from collections import deque
from datetime import date
import difflib
from pathlib import Path
import re

from jsonschema import Draft202012Validator, FormatChecker
import inference_context as IC
from artifact_state import file_sha256
import numeric_semantics

SCHEMA = Path(__file__).resolve().parent.parent / 'references' / 'claim_inference_schema.json'


def validate_inference(data: dict) -> None:
    IC.validate(data)
    if 'inference' not in data: return
    inf=data['inference']
    errors=list(Draft202012Validator(IC.read_json(SCHEMA),format_checker=FormatChecker()).iter_errors(inf))
    if errors: raise ValueError(f'Invalid claim inference: {errors[0].message}')
    for coll,key in [('nodes','claim_id'),('links','link_id'),('criteria','criterion_id'),('cases','case_id'),('evidence_scopes','scope_id')]:
        ids=[x[key] for x in inf[coll]]
        if len(ids)!=len(set(ids)): raise ValueError(f'Duplicate {key}')
    ids={n['claim_id'] for n in inf['nodes']}
    parents={i:set() for i in ids}
    for e in inf['links']:
        if e['premise'] not in ids or e['conclusion'] not in ids:
            raise ValueError('Dangling claim dependency')
        parents[e['conclusion']].add(e['premise'])
    while parents:
        roots={i for i,p in parents.items() if not p}
        if not roots: raise ValueError('Cyclic claim dependency graph')
        parents={i:p-roots for i,p in parents.items() if i not in roots}
    criteria={c['criterion_id'] for c in inf['criteria']}
    for case in inf['cases']:
        if case['status']=='pilot' and not case['reason'].strip():
            raise ValueError('A pilot exclusion requires a reason')
        keys=[o['criterion_id'] for o in case['observations']]
        if len(keys)!=len(set(keys)) or set(keys)-criteria:
            raise ValueError('Unknown/duplicate case criterion')
    scopes={s['scope_id'] for s in inf['evidence_scopes']}
    for n in inf['nodes']:
        if n['scope_evidence_id'] and n['scope_evidence_id'] not in scopes:
            raise ValueError('Unknown evidence-scope reference')
    for s in inf['evidence_scopes']:
        if date.fromisoformat(s['valid_from'])>date.fromisoformat(s['valid_until']):
            raise ValueError('Evidence validity interval is reversed')


def evaluate(data: dict, claims: dict, evidence: dict, *, initial_findings: list[dict] | None=None) -> dict:
    validate_inference(data)
    findings=list(initial_findings or [])
    inf=data.get('inference')
    if inf is None:
        findings.append({'code':'missing_inference','severity':'unmeasured','ids':[], 'message':'No claim-inference annotations'})
        return IC.result_report('katedra_claim_inference',findings,{'declared_claims':0,'reviewed_links':0},affected_claim_ids=[])
    nodes={n['claim_id']:n for n in inf['nodes']}
    dirty=set()

    def add(code,severity,ids,message):
        findings.append({'code':code,'severity':severity,'ids':list(ids),'message':message})

    def has_support(cid, eids):
        row=claims.get(cid,{})
        linked={e.get('evidence_id') for e in row.get('evidence',[]) if e.get('relation')=='supports'}
        return bool(eids) and set(eids)<=linked and all(
            e in evidence and isinstance(evidence[e].get('text'),str) and
            IC.sha_text(evidence[e]['text'])==evidence[e].get('text_sha256') for e in eids)

    if not nodes or not inf['required_claim_ids']:
        add('empty_inference_scope','unmeasured',[], 'No declared inference coverage')
    missing=set(inf['required_claim_ids'])-nodes.keys()
    if missing: add('inference_coverage_gap','unmeasured',sorted(missing),'Required claim has no inference annotation')
    for cid,n in nodes.items():
        if cid not in claims or not isinstance(claims[cid].get('text'),str):
            add('missing_claim','unmeasured',[cid],'Claim is absent from current ledger'); dirty.add(cid);continue
        if n['reviewed_text_sha256']!=IC.sha_text(claims[cid]['text']) or not n['reviewer']:
            add('changed_or_unreviewed_claim','review_required',[cid],'Current claim text has no matching review');dirty.add(cid)
        if n['evidence_state']!='confirmed':
            add('evidence_not_confirmed','review_required',[cid],f"Recorded evidence state is {n['evidence_state']}, not confirmation");dirty.add(cid)
        if not has_support(cid,n['evidence_ids']):
            add('support_unresolved','review_required',[cid],'Claim lacks current linked support; contextualizes is not supports');dirty.add(cid)
    # Numeric contradictions invalidate the claims which used them; B does not have
    # to be present for a qualitative claim graph.
    if data['facts']:
        nr=numeric_semantics.evaluate(data)
        for f in nr['findings']:
            findings.append({**f,'code':'numeric:'+f['code']})
            for fact in data['facts']:
                if fact['fact_id'] in f['ids'] and fact['claim_id'] in nodes: dirty.add(fact['claim_id'])

    def independent(cid):
        n=nodes[cid]; r=n.get('independent_review')
        if not r or cid not in claims or r['claim_sha256']!=IC.sha_text(claims[cid]['text']): return False
        if not has_support(cid,r['evidence_ids']): return False
        # A reuse of the invalidated premise's evidence is not an independent proof.
        invalid_eids={eid for i in dirty for eid in nodes[i]['evidence_ids'] if i!=cid}
        return not (set(r['evidence_ids']) & invalid_eids)

    for e in inf['links']:
        p,q=e['premise'],e['conclusion']; src,dst=nodes[p],nodes[q]
        current_sha=IC.sha_text(claims[p]['text']) if p in claims else None
        if (e['reviewed_premise_sha256']!=current_sha or not e['reviewer']) and not independent(q):
            dirty.add(q);add('dependency_review_stale','review_required',[p,q],'Premise review fingerprint or reviewer is missing/stale')
        if e['kind']=='generalises':
            if src['units'] is None or dst['units'] is None:
                add('scope_unknown','review_required',[p,q],'Cannot compare unannotated populations');dirty.add(q)
            elif not set(dst['units'])<=set(src['units']):
                add('scope_overreach','review_required',[p,q],'Conclusion extends beyond the declared evidence scope');dirty.add(q)
        elif e['kind']=='causal':
            basis=e['causal_basis']
            if not basis or not has_support(p,[basis['evidence_id']]):
                add('causation_needs_design_review','review_required',[p,q],'Association does not establish causation; design review missing');dirty.add(q)
        elif e['kind']=='complement':
            if src['category'] is None or dst['complement_of']!=src['category'] or dst['category'] is not None:
                add('unsupported_complement','review_required',[p,q],'Complement does not establish a new property');dirty.add(q)
        elif e['kind']=='absence' and src['evidence_state']=='unknown':
            add('unknown_is_not_absence','review_required',[p,q],'Absence of public evidence is not evidence of zero/absence');dirty.add(q)
    for case in inf['cases']:
        if case['status']=='pilot': continue
        observed={o['criterion_id']:o['state'] for o in case['observations']}
        for criterion in inf['criteria']:
            state=observed.get(criterion['criterion_id'],'unknown')
            if state!='confirmed':
                add('criterion_mismatch' if state=='contradicted' else 'criterion_unknown',
                    'blocked' if state=='contradicted' else 'review_required',
                    [case['case_id'],criterion['criterion_id']], 'Included case has not met the declared methodological requirement')
    if inf['criteria'] and not inf['cases']:
        add('cases_not_reviewed','unmeasured',[],'Criteria were declared without any cases')
    scopes={s['scope_id']:s for s in inf['evidence_scopes']}
    for cid,n in nodes.items():
        sid=n['scope_evidence_id']
        if not sid: continue
        scope=scopes[sid]
        current=n['as_of']
        invalid=(scope['evidence_id'] not in evidence or current is None or n['units'] is None or
                 not set(n['units'] or [])<=set(scope['units']) or not set(n['features'])<=set(scope['features']))
        if current is not None:
            invalid=invalid or not scope['valid_from']<=current<=scope['valid_until']
        if invalid:
            add('evidence_scope_mismatch','review_required',[cid,sid], 'Claim exceeds declared certificate/regulation/report scope or validity');dirty.add(cid)
    # Linear breadth-first invalidation; a current independent re-review cuts a
    # dependency, never silently promotes a changed premise to true.
    children={cid:[] for cid in nodes}
    for e in inf['links']: children[e['premise']].append(e['conclusion'])
    queue=deque(sorted(dirty))
    while queue:
        p=queue.popleft()
        for q in children[p]:
            if q not in dirty and not independent(q):
                dirty.add(q); queue.append(q)
                add('premise_propagation','review_required',[p,q],'An upstream premise requires renewed review')
    return IC.result_report('katedra_claim_inference',findings,
        {'declared_claims':len(nodes),'required_claims':len(inf['required_claim_ids']),
         'reviewed_links':len(inf['links']), 'cases':len(inf['cases'])},affected_claim_ids=sorted(dirty))


_QUOTED = re.compile(r'„[^”"“]*[”"“]|“[^”]*”|"[^"\n]*"')
_TENTATIVE = re.compile(r'\b(?:može|mogu|mogl\w*|moguć\w*|možda|up[ućc]\w*|may|might|could|suggest\w*)\b',re.I)
_ASSOCIATION = re.compile(r'\b(?:povezan\w*|korelaci\w*|associat\w*|correlat\w*)\b',re.I)
_STRONG = re.compile(r'\b(?:uzroku\w*|dokaz\w*|cause\w*|prove\w*)\b|\bdovodi do\b',re.I)
_NEGATION = re.compile(r'\b(?:ne|nije|nisu|cannot|not|doesn.t|don.t)\b(?:\s+\w+){0,3}\s*$',re.I)
_LIMITED = re.compile(r'\bu (?:analiziranim|promatranim|odabranim)\b|\bu uzorku\b|\bin (?:the )?sample\b',re.I)
_UNIVERSAL = re.compile(r'\b(?:svi|svaki|svaka|all|every)\b|\bu Hrvatskoj\b',re.I)


def _strength(text):
    s=_QUOTED.sub('',text)
    if s.lstrip().startswith('>'): return 0
    if _TENTATIVE.search(s): return 1
    strong=[m for m in _STRONG.finditer(s) if not _NEGATION.search(s[max(0,m.start()-60):m.start()])]
    if strong: return 3
    return 2 if _ASSOCIATION.search(s) else 0


def epistemic_signals(before: str, after: str) -> list[dict]:
    """Candidate review only; quoted or negated strong words are not assertions."""
    a=re.split(r'(?<=[.!?])\s+|\n+',before)
    b=re.split(r'(?<=[.!?])\s+|\n+',after)
    findings=[]
    matcher=difflib.SequenceMatcher(a=a,b=b,autojunk=False)
    for tag,i,j,k,l in matcher.get_opcodes():
        if tag=='equal': continue
        old=' '.join(a[i:j]); new=' '.join(b[k:l])
        o,n=_QUOTED.sub('',old),_QUOTED.sub('',new)
        if not o.strip() or not n.strip() or n.lstrip().startswith('>'): continue
        if _strength(old)>0 and _strength(new)>_strength(old):
            findings.append({'code':'epistemic_strengthening','severity':'review_required','ids':[],
                'message':'Rewrite increased asserted certainty; needs source/design review',
                'before':old,'after':new,'before_sha256':IC.sha_text(old),'after_sha256':IC.sha_text(new)})
        if _LIMITED.search(o) and not _LIMITED.search(n) and _UNIVERSAL.search(n):
            findings.append({'code':'scope_expansion','severity':'review_required','ids':[],
                'message':'Sample-limited statement became a broader generalisation', 'before':old,'after':new,
                'before_sha256':IC.sha_text(old),'after_sha256':IC.sha_text(new)})
    return findings


def evaluate_file(sidecar,*,project_root,document,state_dir,view):
    digest=file_sha256(sidecar);data=IC.read_json(sidecar);validate_inference(data)
    current=IC.capture_bindings(project_root,document,state_dir,view)
    claims,evidence=IC.ledger_maps(state_dir)
    findings=IC.binding_findings(data,current,claims,evidence)
    # C can review a purely qualitative graph with no numeric facts, so validate
    # the source-byte binding for its cited evidence too.
    for n in data.get('inference',{}).get('nodes',[]):
        for eid in n['evidence_ids']:
            e=evidence.get(eid,{})
            if e and current['source_files'].get(str(e.get('source_path','')).replace('\\','/'))!=e.get('source_sha256'):
                findings.append({'code':'stale_inference_source','severity':'stale','ids':[n['claim_id'],eid],
                                 'message':'Claim support points to changed source bytes'})
    r=evaluate(data,claims,evidence,initial_findings=findings)
    after=IC.capture_bindings(project_root,document,state_dir,view)
    if current!=after or digest!=file_sha256(sidecar):
        r['status']='stale';r['findings'].append({'code':'changed_during_review','severity':'stale','ids':[],'message':'Inputs changed during review'})
    r.update(context_sha256=digest,bindings=current)
    return r


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    for name in ('context','project-root','rad','kat','view','out'): ap.add_argument('--'+name,required=True)
    a=ap.parse_args()
    try:
        if Path(a.out).resolve() in {Path(a.context).resolve(),Path(a.rad).resolve()} or Path(a.out).name in {'claims.jsonl','evidence.jsonl','izvori.json'}:
            raise ValueError('Output aliases a review input')
        r=evaluate_file(a.context,project_root=a.project_root,document=a.rad,state_dir=a.kat,view=a.view)
        IC.save_report(a.out,r);print(f"{r['status']}: declared inference scope; human judgments remain explicit")
        return IC.exit_code(r)
    except (OSError,ValueError) as exc:
        print(f'Inference review not measured: {exc}');return 2

if __name__=='__main__': raise SystemExit(main())
