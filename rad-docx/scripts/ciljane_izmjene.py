#!/usr/bin/env python3
"""Ciljane izmjene postojećeg DOCX-a; strukturna provjera NIJE vizualni gate.

inspect INPUT; apply INPUT --plan PLAN --out OUTPUT --snapshot COPY --report JSON;
verify INPUT OUTPUT --plan PLAN. Ne prevodi nazive, ne čita fotografije, ne prihvaća
revizije i ne čisti metapodatke. Izlaz 0 = izmjeren strukturni prolaz, 1 = razlika
izvan plana, 2 = nepodržan/neispravan ulaz ili neizvedena provjera.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import io
import json
import os
from pathlib import Path
import re
import sys
import tempfile
import zipfile

from lxml import etree as ET

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
NS = {'w': W}
XML_SPACE = '{http://www.w3.org/XML/1998/namespace}space'
DOCUMENT = 'word/document.xml'
MAX_UNPACKED = 128 * 1024 * 1024
MAX_XML = 32 * 1024 * 1024
CV_HEADINGS = {'životopis', 'curriculum vitae'}
CARD_HEADINGS = {'temeljna dokumentacijska kartica', 'basic documentation card'}
DEGREE_LABELS = {'akademski naziv', 'kratica akademskoga naziva',
                 'kratica akademskog naziva', 'academic degree', 'academic title',
                 'abbreviation of academic degree', 'abbreviated academic title'}


class EditError(ValueError):
    """The requested operation cannot be safely performed/measured."""


def _hash(data):
    return hashlib.sha256(data).hexdigest()


def _q(name):
    return '{%s}%s' % (W, name)


def _text(node):
    return ''.join(node.itertext()) if node.tag == _q('t') else ''.join(
        t.text or '' for t in node.iter(_q('t')))


def _norm(text):
    return ' '.join(text.split()).casefold()


def _xml(data):
    if len(data) > MAX_XML:
        raise EditError('XML je prevelik za ograničeni zahvat.')
    try:
        root = ET.fromstring(data, ET.XMLParser(resolve_entities=False, no_network=True))
    except ET.XMLSyntaxError as e:
        raise EditError('Neispravan XML.') from e
    if root.getroottree().docinfo.doctype:
        raise EditError('DTD nije podržan.')
    return root


def _load(path):
    try:
        if Path(path).stat().st_size > MAX_UNPACKED:
            raise EditError('Ulazna datoteka je prevelika.')
        raw = Path(path).read_bytes()
        with zipfile.ZipFile(io.BytesIO(raw)) as z:
            names = z.namelist()
            if any(n.startswith('_xmlsignatures/') for n in names):
                raise EditError('Digitalno potpisan paket ne smije se tiho izmijeniti.')
            if len(names) != len(set(names)) or len(names) > 4096:
                raise EditError('Duplicirani/prebrojni dijelovi DOCX paketa.')
            if sum(i.file_size for i in z.infolist()) > MAX_UNPACKED:
                raise EditError('DOCX paket je prevelik za ograničeni zahvat.')
            data = {n: z.read(n) for n in names}
        if DOCUMENT not in data or '[Content_Types].xml' not in data:
            raise EditError('Ulaz nije DOCX dokument.')
        types = _xml(data['[Content_Types].xml'])
        main = [e for e in types if e.get('PartName') == '/word/document.xml']
        if len(main) != 1 or main[0].get('ContentType') != (
                'application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml'):
            raise EditError('Potreban je DOCX, ne makro ili predložak.')
        root = _xml(data[DOCUMENT])
        if root.tag != _q('document') or len(root.findall('w:body', NS)) != 1:
            raise EditError('Nepodržana struktura dokumenta.')
        return raw, data, root
    except (OSError, zipfile.BadZipFile, RuntimeError, KeyError) as e:
        raise EditError('Ulaz se ne može pročitati kao DOCX.') from e


def _context(p, body):
    """Only explicit surrounding headings and recognized card value cells."""
    block = p
    while block.getparent() is not body:
        block = block.getparent()
        if block is None:
            return None
    earlier = list(body)[:list(body).index(block)]
    heading = ''
    for node in reversed(earlier):
        if node.tag != _q('p'):
            continue
        t = re.sub(r'^\d+(?:\.\d+)*[.\s]+', '', _norm(_text(node)))
        if t in CARD_HEADINGS | CV_HEADINGS:
            heading = t
            break
        # Any intervening explicit heading ends the earlier contextual region.
        style = node.find('w:pPr/w:pStyle', NS)
        if (style is not None and re.search(r'heading|naslov', style.get(_q('val'), ''), re.I)) \
                or re.match(r'^\d{1,3}(?:\.\d{1,3})*\.?\s+[^\W\d_]', _text(node)) \
                or (_text(node).isupper() and len(_text(node).split()) <= 10) \
                or t in {'sažetak', 'summary', 'uvod', 'abstract', 'literatura'}:
            break
    if block.tag == _q('p') and heading in CV_HEADINGS:
        return 'earned'
    if block.tag != _q('tbl') or heading not in CARD_HEADINGS:
        return None
    # Nested tables/cells are deliberately not treated as documentation fields.
    cell = p.getparent()
    row = cell.getparent() if cell is not None else None
    if cell is None or cell.tag != _q('tc') or row is None or row.tag != _q('tr'):
        return None
    cells = row.findall('w:tc', NS)
    if row.getparent() is block and len(cells) == 2 and cell is cells[1] \
            and _norm(_text(cells[0])) in DEGREE_LABELS:
        return 'awarded'
    return None


def inspect_document(path):
    raw, _, root = _load(path)
    body = root.find('w:body', NS)
    return {'target_sha256': _hash(raw), 'output_kind': 'docx',
            'paragraphs': [{'index': i, 'text': _text(p), 'degree_context': _context(p, body)}
                           for i, p in enumerate(body.iter(_q('p')))],
            'blocks': [{'index': i, 'kind': ET.QName(b).localname if isinstance(b.tag, str) else '#comment', 'text': _text(b)}
                       for i, b in enumerate(body)]}


def _keys(obj, required, optional=()):
    if not isinstance(obj, dict) or set(obj) - set(required) - set(optional) \
            or set(required) - set(obj):
        raise EditError('Nedostaje obavezno polje ili plan sadrži nepoznato polje.')


def _plain_string(value):
    return isinstance(value, str) and bool(value.strip())


def _validate_plan(plan, raw):
    _keys(plan, ('version', 'target_sha256', 'output_kind', 'operations'), ('references',))
    if type(plan['version']) is not int or plan['version'] != 1:
        raise EditError('Nepodržana verzija plana.')
    if plan['target_sha256'] != _hash(raw):
        raise EditError('Plan ne pripada ovoj verziji dokumenta (SHA-256).')
    if plan['output_kind'] != 'docx':
        raise EditError('Izlaz ciljane DOCX izmjene mora ostati DOCX, ne slika.')
    ops = plan['operations']
    if not isinstance(ops, list) or not 1 <= len(ops) <= 100:
        raise EditError('Plan mora sadržavati 1–100 izričitih operacija.')
    refs = plan.get('references', [])
    if not isinstance(refs, list):
        raise EditError('Reference moraju biti popis.')
    for ref in refs:
        _keys(ref, ('role', 'id'))
        if ref['role'] not in ('visual_reference', 'evidence') or not _plain_string(ref['id']):
            raise EditError('Referenca nije ciljni dokument ni izvor implicitnih izmjena.')
    for op in ops:
        if not isinstance(op, dict):
            raise EditError('Operacija mora biti objekt.')
        if op.get('op') == 'remove_first_cover':
            _keys(op, ('op', 'end_block', 'expected_text'))
        elif op.get('op') == 'replace_text':
            _keys(op, ('op', 'paragraph', 'old', 'new'))
        elif op.get('op') == 'replace_degree':
            _keys(op, ('op', 'paragraph', 'old', 'new', 'context', 'source'))
            _keys(op['source'], ('kind', 'locator'))
            if op['context'] not in ('earned', 'awarded') \
                    or op['source']['kind'] not in ('official', 'user_confirmed') \
                    or not _plain_string(op['source']['locator']):
                raise EditError('Akademski naziv traži kontekst i potvrđen izvor odluke.')
        else:
            raise EditError('Nepodržana operacija.')
    if sum(o['op'] == 'remove_first_cover' for o in ops) > 1:
        raise EditError('Može se ukloniti samo prvi naslovni blok, jednom.')


def _rewrite_text(p, old, new):
    if not _plain_string(old) or not _plain_string(new) or old == new \
            or any(c in old + new for c in '\r\n\t'):
        raise EditError('Zamjena mora imati različit, neprazan stari i novi tekst bez prijeloma.')
    try:
        ET.Element('test').text = new
    except (ValueError, UnicodeError) as e:
        raise EditError('Novi tekst sadrži znak koji nije dopušten u XML-u.') from e
    # Preserve pPr/rPr exactly. Refuse complex paragraphs rather than flatten them.
    if any(c.tag not in (_q('pPr'), _q('r')) for c in p):
        raise EditError('Složeni odlomak nije običan tekst za zamjenu.')
    runs = p.findall('w:r', NS)
    if any(c.tag not in (_q('rPr'), _q('t')) for r in runs for c in r):
        raise EditError('Polja, slike i prijelomi ne smiju se spljoštiti u tekst.')
    nodes = [t for r in runs for t in r.findall('w:t', NS)]
    full = ''.join(t.text or '' for t in nodes)
    if full.count(old) != 1:
        raise EditError('Stari tekst nije pronađen točno jednom u odabranom odlomku.')
    start, end = full.index(old), full.index(old) + len(old)
    pos = 0
    spans = []
    for t in nodes:
        text = t.text or ''
        stop = pos + len(text)
        if pos < end and stop > start:
            spans.append((t, text, max(0, start - pos), min(len(text), end - pos)))
        pos = stop
    formats = [ET.tostring(t.getparent().find('w:rPr', NS))
               if t.getparent().find('w:rPr', NS) is not None else b'' for t, *_ in spans]
    if len(set(formats)) != 1:
        raise EditError('Zamjena presijeca različito oblikovane segmente; razdvoji zahvat.')
    for i, (t, text, a, b) in enumerate(spans):
        t.text = text[:a] + (new if i == 0 else '') + text[b:]
        if t.text and (t.text[0].isspace() or t.text[-1].isspace()):
            t.set(XML_SPACE, 'preserve')


def _cover_prefix(body, op, data):
    end = op['end_block']
    blocks = list(body)
    if type(end) is not int or end < 1 or end >= len(blocks) - 1:
        raise EditError('Neispravna granica prve naslovnice.')
    prefix = blocks[:end + 1]
    boundary = prefix[-1]
    breaks = [(i, b) for i, node in enumerate(prefix) for b in node.iter(_q('br'))
              if b.get(_q('type')) == 'page']
    if len(breaks) != 1 or breaks[0][0] != end or boundary.tag != _q('p') \
            or _text(boundary).strip():
        raise EditError('Granica mora biti prvi zasebni, izričiti prijelom stranice.')
    if any(x.tag not in (_q('p'),) for x in prefix):
        raise EditError('Naslovni blok s tablicom zahtijeva zaseban pregled.')
    if any(x.tag not in {_q(t) for t in ('p', 'pPr', 'r', 'rPr', 'br')}
           for x in boundary.iter()):
        raise EditError('Granični odlomak nije samo prijelom stranice.')
    dangerous = {'sectPr', 'bookmarkStart', 'bookmarkEnd', 'commentRangeStart',
                 'commentRangeEnd', 'commentReference', 'footnoteReference',
                 'endnoteReference', 'fldChar', 'fldSimple', 'instrText', 'hyperlink',
                 'pageBreakBefore', 'sdt', 'altChunk'}
    if any(x.tag in {_q(t) for t in dangerous} for b in prefix for x in b.iter()):
        raise EditError('Naslovnica s odjeljkom/sidrom/poljem nije podržana za uklanjanje.')
    expected = op['expected_text']
    actual = [_text(b) for b in prefix[:-1] if _text(b).strip()]
    if not isinstance(expected, list) or not expected or expected != actual:
        raise EditError('Sadržaj prve naslovnice ne odgovara odobrenom planu.')
    first_section = next(body.iter(_q('sectPr')), None)
    if first_section is not None:
        title = first_section.find('w:titlePg', NS)
        if title is not None and title.get(_q('val'), '1').lower() not in ('0', 'false', 'off'):
            raise EditError('Posebno zaglavlje/podnožje prve stranice zahtijeva zaseban pregled.')
    if 'word/settings.xml' in data:
        settings = _xml(data['word/settings.xml'])
        odd = settings.find('w:evenAndOddHeaders', NS)
        if odd is not None and odd.get(_q('val'), '1').lower() not in ('0', 'false', 'off'):
            raise EditError('Parna/neparna zaglavlja zahtijevaju zaseban pregled.')
    return prefix


def _expected(raw, data, root, plan):
    _validate_plan(plan, raw)
    changed = copy.deepcopy(root)
    body = changed.find('w:body', NS)
    # No silent accept-all, including changes in headers/footnotes.
    revision = re.compile(r'^(?:ins|del|delText|moveFrom|moveTo|cellIns|cellDel|cellMerge|conflictIns|conflictDel|.*Change|.*RangeStart|.*RangeEnd)$')
    for name, payload in data.items():
        if name.startswith('word/') and name.endswith('.xml'):
            r = _xml(payload)
            if any(ET.QName(n).namespace in (W, 'http://schemas.microsoft.com/office/word/2010/wordml')
                   and revision.fullmatch(ET.QName(n).localname)
                   and ET.QName(n).localname not in ('commentRangeStart', 'commentRangeEnd')
                   for n in r.iter() if isinstance(n.tag, str)):
                raise EditError('Dokument s revizijama traži zasebno odabran pogled.')
    paragraphs = list(body.iter(_q('p')))
    removed = []
    for op in plan['operations']:
        if op['op'] == 'remove_first_cover':
            removed = _cover_prefix(body, op, data)
    touched = set()
    for op in plan['operations']:
        if op['op'] == 'remove_first_cover':
            continue
        index = op['paragraph']
        if type(index) is not int or not 0 <= index < len(paragraphs) or index in touched:
            raise EditError('Neispravan ili višestruko odabran odlomak.')
        p = paragraphs[index]
        if any(p is b or b in p.iterancestors() for b in removed):
            raise EditError('Isti dio ne može se istodobno mijenjati i ukloniti.')
        if op['op'] == 'replace_degree' and _context(p, body) != op['context']:
            raise EditError('Kontekst rubrike ne odgovara vrsti akademskog naziva.')
        _rewrite_text(p, op['old'], op['new'])
        touched.add(index)
    for b in removed:
        body.remove(b)
    return changed


def _canonical(root):
    return ET.tostring(root, method='c14n')


def verify_plan(before, after, plan):
    raw, data, root = _load(before)
    afterraw, actual, afterroot = _load(after)
    expected = _expected(raw, data, root, plan)
    other = sorted(n for n in set(data) | set(actual)
                   if n != DOCUMENT and data.get(n) != actual.get(n))
    xml_ok = _canonical(expected) == _canonical(afterroot)
    return {'ok': xml_ok and not other, 'document_matches_plan': xml_ok,
            'changed_other_parts': other, 'before_sha256': _hash(raw),
            'after_sha256': _hash(afterraw),
            'visual_check': {'ok': None, 'reason': 'Potreban je render i pregled konačne verzije.'}}


def _write_new(path, content):
    """Publish fully written bytes without overwriting existing files/symlinks."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix='.ciljane-')
    try:
        with os.fdopen(fd, 'wb') as f:
            f.write(content); f.flush(); os.fsync(f.fileno())
        os.link(tmp, path)  # same filesystem; fails atomically if destination exists
        st = path.stat(follow_symlinks=False)
        return st.st_dev, st.st_ino
    finally:
        os.unlink(tmp)


def apply_plan(source, output, plan, *, snapshot, report=None):
    paths = [Path(source), Path(output), Path(snapshot)]
    if report is not None:
        paths.append(Path(report))
    if len({p.resolve() for p in paths}) != len(paths) or paths[1].suffix.lower() != '.docx':
        raise EditError('Ulaz, izlaz, snapshot i izvještaj moraju biti različiti; izlaz je .docx.')
    if any(p.exists() or p.is_symlink() for p in paths[1:]):
        raise EditError('Izlaz/snapshot/izvještaj već postoji; ništa nije prepisano.')
    raw, data, root = _load(source)
    expected = _expected(raw, data, root, plan)
    xml = ET.tostring(expected, encoding='UTF-8', xml_declaration=True, standalone=True)
    buf = io.BytesIO()
    with zipfile.ZipFile(io.BytesIO(raw)) as z, zipfile.ZipFile(buf, 'w') as out:
        out.comment = z.comment
        for info in z.infolist():
            out.writestr(info, xml if info.filename == DOCUMENT else data[info.filename])
    created = None
    try:
        _write_new(snapshot, raw)
        created = _write_new(output, buf.getvalue())
        verified = verify_plan(snapshot, output, plan)
        if not verified['ok']:
            raise EditError('Napisani izlaz ne odgovara odobrenom planu.')
        result = {'status': 'structural_pass',
                  'before_sha256': verified['before_sha256'],
                  'after_sha256': verified['after_sha256'],
                  'plan_sha256': _hash(json.dumps(plan, ensure_ascii=True, sort_keys=True).encode('utf-8')),
                  'operations': len(plan['operations']),
                  'non_document_parts_unchanged': not verified['changed_other_parts'],
                  'visual_check': verified['visual_check']}
        if report is not None:
            _write_new(report, (json.dumps(result, ensure_ascii=False, indent=2) + '\n').encode('utf-8'))
    except (OSError, EditError) as e:
        # Keep the exact snapshot. Do not remove an unrelated concurrent output.
        if created is not None:
            try:
                st = Path(output).stat(follow_symlinks=False)
                if (st.st_dev, st.st_ino) == created:
                    Path(output).unlink()
            except OSError:
                pass
        raise EditError('Pisanje/provjera nije dovršena; snapshot ostaje za oporavak.') from e
    return result


def _unique(pairs):
    out = {}
    for key, value in pairs:
        if key in out:
            raise EditError('Duplicirano JSON polje.')
        out[key] = value
    return out


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    inspect = commands.add_parser('inspect'); inspect.add_argument('source')
    apply = commands.add_parser('apply'); apply.add_argument('source')
    for name in ('plan', 'out', 'snapshot', 'report'):
        apply.add_argument('--' + name, required=True)
    verify = commands.add_parser('verify'); verify.add_argument('source'); verify.add_argument('output')
    verify.add_argument('--plan', required=True)
    args = parser.parse_args(argv)
    try:
        if args.command == 'inspect':
            result = inspect_document(args.source)
        else:
            plan = json.loads(Path(args.plan).read_text(encoding='utf-8'), object_pairs_hook=_unique)
            if args.command == 'apply':
                if Path(args.plan).resolve() in {Path(p).resolve() for p in (args.out, args.snapshot, args.report)}:
                    raise EditError('Plan se ne smije prepisati izlazom.')
                result = apply_plan(args.source, args.out, plan, snapshot=args.snapshot, report=args.report)
            else:
                result = verify_plan(args.source, args.output, plan)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 1 if result.get('ok') is False else 0
    except (EditError, OSError, json.JSONDecodeError) as e:
        print(str(e), file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
