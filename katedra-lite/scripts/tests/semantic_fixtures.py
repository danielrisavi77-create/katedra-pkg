"""Synthetic numeric annotations; not statistics about real organisations."""
from copy import deepcopy


def fact(fid, value, *, members=None, origin='source', **changes):
    row = {'fact_id': fid, 'claim_id': 'claim-' + fid, 'origin': origin,
           'evidence_id': 'evidence-' + fid if origin == 'source' else None,
           'locator': 'table 1, row ' + fid if origin == 'source' else None,
           'value': {'kind': 'exact', 'amount': str(value)}, 'unit': 't',
           'metric': 'waste', 'period': '2023', 'scope': {'organisation': 'Example',
           'population': 'all-sites', 'geography': 'region-X'}, 'measure_status': 'actual',
           'flow_role': 'input', 'denominator': None, 'members': members,
           'category': None, 'complement_of': None,
           'review': {'decision': 'verified', 'reviewer': 'synthetic reviewer'}}
    row.update(changes)
    return row


def context(facts=None, derivations=None):
    facts = facts or []
    derivations = derivations or []
    return {'schema_version': 1, 'bindings': {
        'document': {'artifact_id': 'artifact-example', 'version_id': 'version-example', 'sha256': '0'*64},
        'claims_sha256': '1'*64, 'evidence_sha256': '2'*64, 'sources_sha256': '3'*64,
        'source_files': {}, 'view': 'original_no_revisions'},
        'facts': deepcopy(facts), 'derivations': deepcopy(derivations),
        'required_fact_ids': [r['fact_id'] for r in facts],
        'required_derivation_ids': [r['derivation_id'] for r in derivations]}


def derivation(op='sum', inputs=None, result='total', **changes):
    row = {'derivation_id': 'd1', 'operation': op, 'inputs': inputs or ['a', 'b'],
           'result': result, 'tolerance': {'absolute': '0', 'reason': '', 'reviewer': ''}}
    row.update(changes)
    return row


def sum_context():
    return context([fact('a', '450', members=['kitchen']), fact('b', '150', members=['green']),
                    fact('total', '600', members=['kitchen','green'], origin='derived')],
                   [derivation()])
