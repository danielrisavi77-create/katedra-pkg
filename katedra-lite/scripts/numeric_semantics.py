#!/usr/bin/env python3
"""Check declared numeric meaning and arithmetic, not truth inferred from prose.

All missing semantic context remains unmeasured/review-required. Decimal arithmetic
uses no binary floats, and greater-than/approximate values never become exact amounts.
"""
from __future__ import annotations

import argparse
from decimal import Decimal, localcontext
from pathlib import Path
import re

import inference_context as IC
from artifact_state import file_sha256

UNITS = {'t':('mass',Decimal('1000')), 'kg':('mass',Decimal('1')), 'g':('mass',Decimal('0.001')),
         't/year':('mass-rate',Decimal('1000')), 'kg/year':('mass-rate',Decimal('1')),
         '%':('percent',Decimal('1')), 'pp':('percentage-point',Decimal('1')),
         'EUR':('currency-eur',Decimal('1')), 'ha':('area',Decimal('10000')),
         'm2':('area',Decimal('1')), 'count':('count',Decimal('1'))}
CHANGES = {'relative_change','percentage_point_change','difference'}


def parse_local_number(text: str, locale: str | None) -> Decimal:
    if not isinstance(text,str) or locale not in {'hr','en'}:
        raise ValueError('A number must have an explicit hr/en source locale')
    decimal, grouping = (',','.') if locale=='hr' else ('.',',')
    pattern = rf'-?(?:[0-9]+|[0-9]{{1,3}}(?:{re.escape(grouping)}[0-9]{{3}})+)(?:{re.escape(decimal)}[0-9]+)?'
    if len(text)>82 or not re.fullmatch(pattern,text): raise ValueError('Invalid localized finite decimal')
    return Decimal(text.replace(grouping,'').replace(decimal,'.'))


def evaluate(data: dict, *, initial_findings: list[dict] | None = None) -> dict:
    IC.validate(data)
    findings = list(initial_findings or [])
    facts = {f['fact_id']:f for f in data['facts']}
    dids = {d['derivation_id'] for d in data['derivations']}
    checked = 0

    def add(code, severity, ids, message):
        findings.append({'code':code,'severity':severity,'ids':list(ids),'message':message})

    missing = set(data['required_fact_ids'])-facts.keys()
    missing_d = set(data['required_derivation_ids'])-dids
    if not facts or not data['required_fact_ids']:
        add('empty_scope','unmeasured',[], 'No declared numeric coverage')
    if missing or missing_d:
        add('coverage_gap','unmeasured', sorted(missing|missing_d), 'Required numeric annotations/derivations are missing')
    outputs = {d['result'] for d in data['derivations']}
    for fid,f in facts.items():
        if f['review']['decision']!='verified':
            add('annotation_pending','review_required',[fid], 'Semantic annotation has not been reviewed')
        if f['origin']=='derived' and fid not in outputs:
            add('undefined_derived_fact','review_required',[fid], 'Derived fact lacks its calculation')
        if (any(f[k] is None for k in ('unit','metric','period')) or
            any(v is None for v in f['scope'].values()) or
            f['measure_status']=='unknown' or f['flow_role']=='unknown'):
            add('unknown_semantics','review_required',[fid], 'Unknown unit, period, scope, status or flow role')
        if f['value']['kind']!='exact':
            add('non_exact_value','review_required',[fid], 'Bounded, approximate or unknown value is not an exact quantity')
        elif f['unit']=='%' and not Decimal('0')<=Decimal(f['value']['amount'])<=Decimal('100'):
            # Relative growth percentages may exceed 100; their denominator identifies a fact.
            if not any(d['result']==fid and d['operation']=='relative_change' for d in data['derivations']):
                add('invalid_share','blocked',[fid], 'An absolute share lies outside 0–100%')
        if f['unit'] not in UNITS:
            add('unknown_unit','review_required',[fid], 'No verified conversion for this unit')

    def semmatch(rows, *, keys=('metric','period','scope','measure_status','flow_role')):
        for key in keys:
            values=[r[key] for r in rows]
            if all(v is not None and v!='unknown' for v in values) and any(v!=values[0] for v in values[1:]):
                add('semantic_mismatch','blocked',[r['fact_id'] for r in rows],f'Incompatible {key}')

    def values(rows, outunit):
        if outunit not in UNITS: return None
        if any(r['unit'] not in UNITS or r['value']['kind']!='exact' for r in rows): return None
        dim,scale=UNITS[outunit]
        if any(UNITS[r['unit']][0]!=dim for r in rows):
            add('unit_mismatch','blocked',[r['fact_id'] for r in rows], 'Different quantity dimensions cannot be combined')
            return None
        return [Decimal(r['value']['amount'])*UNITS[r['unit']][1]/scale for r in rows]

    with localcontext() as ctx:
        ctx.prec=100
        for d in data['derivations']:
            op=d['operation']; ins=[facts[i] for i in d['inputs']]; out=facts[d['result']]
            ids=[d['derivation_id'], *d['inputs'],d['result']]
            before=len(findings)
            keys=('metric','scope','measure_status','flow_role') if op in CHANGES else ('metric','period','scope','measure_status','flow_role')
            if op=='yield_percent':
                semmatch(ins,keys=('metric','period','scope','measure_status'))
                semmatch([ins[0],out],keys=('metric','period','scope','measure_status'))
                if [f['flow_role'] for f in ins]!=['output','input'] or out['flow_role']!='not_applicable':
                    add('semantic_mismatch','blocked',ids,'Yield explicitly requires output / input')
            else:
                semmatch(ins+[out],keys=keys)
            if op in CHANGES:
                expected_period=ins[0]['period'] if ins[0]['period']==ins[1]['period'] else f"{ins[0]['period']}/{ins[1]['period']}"
                if out['period']!=expected_period:
                    add('semantic_mismatch','blocked',ids,'Change must declare its compared period pair')
            if all(r['unit']=='%' for r in ins):
                if not ins[0]['denominator']:
                    add('unknown_denominator','review_required',ids,'Share denominator is unknown')
                elif any(r['denominator']!=ins[0]['denominator'] for r in ins):
                    add('denominator_mismatch','blocked',ids,'Shares describe different denominators')
            expected=None
            if op in {'identity','sum','union','difference'}:
                if out['unit']=='%' and out['denominator']!=ins[0]['denominator']:
                    add('denominator_mismatch','blocked',ids,'Result share denominator differs from inputs')
                ns=values(ins,out['unit'])
                if ns is not None:
                    if op=='identity': expected=ns[0]
                    elif op=='difference': expected=ns[1]-ns[0]
                    else:
                        members=[r['members'] for r in ins]
                        if any(m is None for m in members) or out['members'] is None:
                            add('unknown_components','review_required',ids,'Reviewed component membership is required')
                        else:
                            sets=[set(m) for m in members]; union=set().union(*sets)
                            if set(out['members'])!=union:
                                add('component_mismatch','blocked',ids,'Result membership differs from union of inputs')
                            if op=='sum' and sum(map(len,sets))!=len(union):
                                add('double_count','blocked',ids,'An input component is counted more than once')
                            if op=='union':
                                overlap=facts[d['overlap']]; semmatch(ins+[overlap])
                                if overlap['members'] is None:
                                    add('unknown_components','review_required',ids,'Overlap membership is unknown')
                                elif set(overlap['members'])!=sets[0]&sets[1]:
                                    add('overlap_mismatch','blocked',ids,'Overlap does not represent the intersection')
                        expected=sum(ns)
                        if op=='union':
                            ov=values([facts[d['overlap']]],out['unit'])
                            expected=expected-ov[0] if ov else None
            elif op in {'relative_change','ratio_percent','yield_percent','percentage_point_change'}:
                ns=values(ins,ins[0]['unit'])
                required_unit='pp' if op=='percentage_point_change' else '%'
                if out['unit']!=required_unit:
                    add('unit_mismatch','blocked',ids,f'Result must be {required_unit}, not {out["unit"]}')
                expected_den=ins[0]['denominator'] if op=='percentage_point_change' else ins[0]['fact_id'] if op=='relative_change' else ins[1]['fact_id']
                if out['denominator']!=expected_den:
                    add('denominator_mismatch','blocked',ids,'Result denominator does not identify the declared base')
                if op=='percentage_point_change' and any(f['unit']!='%' for f in ins):
                    add('unit_mismatch','blocked',ids,'Percentage-point change requires two shares')
                if ns is not None:
                    if op=='percentage_point_change': expected=ns[1]-ns[0]
                    else:
                        base=ns[0] if op=='relative_change' else ns[1]
                        if base==0: add('zero_denominator','blocked',ids,'Division by zero is not a measured percentage')
                        else: expected=((ns[1]-ns[0]) if op=='relative_change' else ns[0])/base*Decimal('100')
            elif op=='complement_percent':
                if ins[0]['unit']!='%' or out['unit']!='%':
                    add('unit_mismatch','blocked',ids,'Only a share has a 100% complement')
                if out['denominator']!=ins[0]['denominator']:
                    add('denominator_mismatch','blocked',ids,'Complement denominator differs')
                if not ins[0]['category']:
                    add('unknown_category','review_required',ids,'Source category is unspecified')
                elif out['complement_of']!=ins[0]['category'] or out['category'] is not None:
                    add('category_mismatch','blocked',ids,'Complement cannot assert a different property')
                ns=values(ins,'%')
                if ns is not None: expected=Decimal('100')-ns[0]
            if expected is not None and out['value']['kind']=='exact':
                checked+=1
                if abs(expected-Decimal(out['value']['amount']))>Decimal(d['tolerance']['absolute']):
                    add('arithmetic_mismatch','blocked',ids,f'Declared {out["value"]["amount"]}; computed {expected}')
            elif len(findings)==before:
                add('calculation_unmeasured','review_required',ids,'Numeric operation requires exact reviewed operands')
    return IC.result_report('katedra_numeric_semantics',findings,
        {'declared_facts':len(facts),'required_facts':len(data['required_fact_ids']),
         'declared_derivations':len(dids),'checked_derivations':checked})


def evaluate_file(sidecar, *, project_root, document, state_dir, view):
    digest=file_sha256(sidecar)
    data=IC.read_json(sidecar); IC.validate(data)
    current=IC.capture_bindings(project_root,document,state_dir,view)
    claims,evidence=IC.ledger_maps(state_dir)
    r=evaluate(data,initial_findings=IC.binding_findings(data,current,claims,evidence))
    after=IC.capture_bindings(project_root,document,state_dir,view)
    if after!=current or file_sha256(sidecar)!=digest:
        r['findings'].append({'code':'changed_during_review','severity':'stale','ids':[],
                              'message':'An input changed during review'})
        r['status']='stale'
    r.update({'context_sha256':digest,'bindings':current})
    return r


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--context',required=True); ap.add_argument('--project-root',required=True)
    ap.add_argument('--rad',required=True); ap.add_argument('--kat',required=True)
    ap.add_argument('--view',required=True); ap.add_argument('--out',required=True)
    a=ap.parse_args()
    try:
        r=evaluate_file(a.context,project_root=a.project_root,document=a.rad,state_dir=a.kat,view=a.view)
        out=Path(a.out).resolve()
        IC.assert_safe_report_output(a.out, project_root=a.project_root, state_dir=a.kat,
                                     document=a.rad, sidecar=a.context, kind='katedra_numeric_semantics')
        IC.save_report(out,r); print(f"{r['status']}: declared numeric scope only"); return IC.exit_code(r)
    except (OSError,ValueError) as exc:
        print(f'Numeric review not measured: {exc}'); return 2

if __name__=='__main__': raise SystemExit(main())
