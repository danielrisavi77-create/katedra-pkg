#!/usr/bin/env python3
"""Scoped final DOCX integrity, explicit metadata cleanup and byte-bound visual evidence.

A structural PASS is not a visual PASS. Named reviewer attestations record a review;
they are not independently authenticated. Unchanged content is not proof of truth.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from urllib.parse import unquote
import zipfile

from lxml import etree as ET
from PIL import Image, ImageOps

from ciljane_izmjene import EditError, _load, _xml, _write_new, _hash

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
R = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
REL = 'http://schemas.openxmlformats.org/package/2006/relationships'
WP = 'http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing'
A = 'http://schemas.openxmlformats.org/drawingml/2006/main'
C = 'http://schemas.openxmlformats.org/drawingml/2006/chart'
M = 'http://schemas.openxmlformats.org/officeDocument/2006/math'
NS = {'w': W, 'r': R, 'wp': WP, 'a': A, 'c': C, 'm': M}
GROUPS = {'core', 'application', 'custom', 'thumbnail', 'image_metadata'}
META_TYPES = {'core-properties': 'core', 'extended-properties': 'application',
              'custom-properties': 'custom', 'thumbnail': 'thumbnail'}
SKIP_REL = set(META_TYPES) | {'styles', 'stylesWithEffects', 'settings', 'theme', 'fontTable', 'webSettings'}
FORMAT_TAGS = {
    'w:tblW', 'w:tblInd', 'w:tblBorders', 'w:shd', 'w:tblCellMar', 'w:tblLayout',
    'w:tblLook', 'w:jc', 'w:tblStyle', 'w:tblStyleRowBandSize', 'w:tblStyleColBandSize',
    'w:tblGrid', 'w:trHeight', 'w:tblHeader', 'w:cantSplit', 'w:tcW', 'w:tcMar',
    'w:tcBorders', 'w:vAlign', 'w:textDirection', 'w:hideMark', 'w:proofErr',
    'w:sectPr', 'w:lastRenderedPageBreak',
}
FORMAT_TAGS = {f'{{{NS[k.split(":")[0]]}}}{k.split(":")[1]}' for k in FORMAT_TAGS}
STORY = re.compile(r'^word/(?:document|header\d+|footer\d+|footnotes|endnotes)\.xml$')
MAX_JSON = 8 * 1024 * 1024


def _sha(path):
    return _hash(Path(path).read_bytes())


def _canon(obj):
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False).encode('utf-8')


def _keys(obj, required, optional=()):
    if not isinstance(obj, dict) or set(obj) != set(required) | (set(obj) & set(optional)):
        raise EditError('Nedostaju polja ili zapis ima nepoznata polja.')


def _nonempty(s):
    return isinstance(s, str) and bool(s.strip())


def _hex(s):
    return isinstance(s, str) and re.fullmatch('[0-9a-f]{64}', s) is not None


def _json(path):
    path = Path(path)
    if path.stat().st_size > MAX_JSON:
        raise EditError('JSON izvještaj je prevelik.')
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise EditError('Duplicirani JSON ključ.')
            result[key] = value
        return result
    def invalid(value):
        raise EditError('Nedopuštena JSON konstanta: ' + value)
    return json.loads(path.read_text(encoding='utf-8'), object_pairs_hook=pairs, parse_constant=invalid)


def _validate_schema(name, value):
    from jsonschema import Draft202012Validator, FormatChecker
    path = Path(__file__).resolve().parent.parent/'references'/(name+'_schema.json')
    errors = list(Draft202012Validator(_json(path), format_checker=FormatChecker()).iter_errors(value))
    if errors:
        raise EditError('Neispravan '+name+' zapis: '+errors[0].message)


def _inside(base, name):
    """No absolute paths, parent traversal or symlink escapes in untrusted manifests."""
    if not _nonempty(name) or '\\' in name or ':' in name:
        raise EditError('Putanja mora biti relativna POSIX putanja.')
    rel = PurePosixPath(name)
    if rel.is_absolute() or '..' in rel.parts:
        raise EditError('Putanja izlazi iz mape manifesta.')
    base = Path(base).resolve()
    result = base.joinpath(*rel.parts)
    if any(p.is_symlink() for p in [result, *result.parents] if p != base):
        raise EditError('Symlink nije prihvatljiv dokaz artefakta.')
    try:
        result.resolve().relative_to(base)
    except ValueError as exc:
        raise EditError('Putanja izlazi iz mape manifesta.') from exc
    return result


def _part_target(source, target):
    if not target or '\\' in target or ':' in target:
        raise EditError('Neispravna unutarnja OPC putanja.')
    target = unquote(target).split('#', 1)[0]
    if target.startswith('/'):
        parts = []
    else:
        parts = list(PurePosixPath(source).parent.parts) if source else []
    for piece in target.split('/'):
        if piece in ('', '.'):
            continue
        if piece == '..':
            if not parts:
                raise EditError('OPC veza izlazi iz paketa.')
            parts.pop()
        else:
            parts.append(piece)
    return '/'.join(parts)


def _relationships(data):
    result = {}
    for name, raw in data.items():
        if not name.endswith('.rels'):
            continue
        source = '' if name == '_rels/.rels' else str(PurePosixPath(name).parent.parent / PurePosixPath(name).name[:-5])
        entries = {}
        for rel in _xml(raw):
            rid, target, typ = rel.get('Id'), rel.get('Target'), rel.get('Type')
            if not rid or rid in entries or not target or not typ:
                raise EditError('Neispravne/duplicirane OPC veze.')
            external = rel.get('TargetMode') == 'External'
            resolved = target if external else _part_target(source, target)
            if not external and resolved not in data:
                raise EditError('OPC veza nema ciljni dio: ' + resolved)
            entries[rid] = {'target': resolved, 'type': typ.rsplit('/', 1)[-1], 'external': external}
        result[source] = entries
    return result


def _package(path):
    raw, data, root = _load(path)
    for name in data:
        if name.startswith('/') or '\\' in name or '..' in PurePosixPath(name).parts:
            raise EditError('Neispravno ime dijela paketa.')
        if 'vbaproject' in name.casefold() or name.endswith('.bin') and 'activeX' in name:
            raise EditError('Aktivni/makro objekt nije podržan.')
    return raw, data, root, _relationships(data)


def _pixels(raw):
    try:
        with Image.open(io.BytesIO(raw)) as im:
            if im.width * im.height > 40_000_000:
                raise EditError('Slika je prevelika za provjeru.')
            im = ImageOps.exif_transpose(im).convert('RGBA')
            return ('pixels', im.size, _hash(im.tobytes()))
    except EditError:
        raise
    except (OSError, ValueError):
        return ('bytes', _hash(raw))


def _revision_findings(data):
    out = []
    for name, raw in data.items():
        if not name.endswith('.xml'):
            continue
        root = _xml(raw)
        for tag in ('ins', 'del', 'moveFrom', 'moveTo', 'pPrChange', 'rPrChange', 'tblPrChange', 'sectPrChange'):
            if next(root.iter(f'{{{W}}}{tag}'), None) is not None:
                out.append({'code': 'tracked_changes', 'part': name, 'severity': 'blocked'})
                break
        if 'comments' in name.casefold() and len(root):
            out.append({'code': 'comments', 'part': name, 'severity': 'review_required'})
    return out


def _semantic_snapshot(data, rels):
    """Conservative ordered structure; only enumerated presentation properties are omitted."""
    def drawing(node, part):
        identity = []
        for el in node.iter():
            if el.tag in {f'{{{A}}}t', f'{{{W}}}t', f'{{{M}}}t', f'{{{A}}}srcRect'}:
                identity.append(('visual_content', el.tag, tuple(sorted(el.attrib.items())), el.text))
            if el.tag == f'{{{WP}}}docPr':
                identity.append(('identity', tuple(sorted(el.attrib.items()))))
            for attr in (f'{{{R}}}embed', f'{{{R}}}link', f'{{{R}}}id'):
                if el.get(attr):
                    rid = el.get(attr)
                    if rid not in rels.get(part, {}):
                        raise EditError('Vizual ima nerazriješenu vezu.')
                    identity.append(('relationship', rid, rels[part][rid]))
        return ('drawing', identity)

    def tree(node, part):
        if not isinstance(node.tag, str) or node.tag in FORMAT_TAGS:
            return []
        if node.tag == f'{{{W}}}drawing':
            return [drawing(node, part)]
        if node.tag in (f'{{{W}}}pPr', f'{{{W}}}rPr'):
            # Numbering, style identity and visibility are not just typography.
            children = [e for e in node if ET.QName(e).localname in {'pStyle', 'numPr', 'vanish', 'webHidden', 'rStyle'}]
            return [v for child in children for v in tree(child, part)]
        if node.tag == f'{{{W}}}r':
            return [v for child in node for v in tree(child, part)]
        if node.tag in (f'{{{W}}}t', f'{{{M}}}t'):
            return [('text', node.text or '')]
        attrs = tuple(sorted((k, v) for k, v in node.attrib.items()
                             if not k.startswith(f'{{{W}}}rsid') and ET.QName(k).localname != 'Ignorable'))
        children = [v for child in node for v in tree(child, part)]
        merged = []
        for event in children:
            if event[0] == 'text' and merged and merged[-1][0] == 'text':
                merged[-1] = ('text', merged[-1][1] + event[1])
            else:
                merged.append(event)
        return [(node.tag, attrs, node.text if node.tag == f'{{{W}}}instrText' else None, merged)]

    stories = {name: tree(_xml(raw), name) for name, raw in data.items() if STORY.match(name)}
    relations = {part: {rid: item for rid, item in entries.items() if item['type'] not in SKIP_REL}
                 for part, entries in rels.items()}
    relations = {part: entries for part, entries in relations.items() if entries}
    pictures = {n: _pixels(raw) for n, raw in data.items() if n.startswith('word/media/')}
    charts = {}
    for name, raw in data.items():
        if name.startswith('word/charts/') and name.endswith('.xml'):
            root = _xml(raw)
            charts[name] = [(el.tag, tuple(sorted(el.attrib.items())), el.text)
                            for el in root.iter() if isinstance(el.tag, str) and
                            (ET.QName(el).localname in {'v', 'f', 'pt', 'ptCount', 'numFmt', 'axId', 'idx', 'order', 't'})]
    metadata_parts = _metadata_parts(data, rels, GROUPS)
    presentation = {'word/styles.xml', 'word/stylesWithEffects.xml', 'word/settings.xml',
                    'word/fontTable.xml', 'word/webSettings.xml'}
    protected = {name: _hash(raw) for name, raw in data.items()
                 if not (STORY.match(name) or name in metadata_parts or name in presentation
                         or name == '[Content_Types].xml' or name.endswith('.rels')
                         or name.startswith(('word/media/', 'word/charts/', 'word/theme/')))}
    # Semantic properties in styles/settings must not be silently changed by formatting.
    style_semantics = {}
    for name in ('word/styles.xml', 'word/stylesWithEffects.xml', 'word/settings.xml'):
        if name in data:
            root = _xml(data[name])
            style_semantics[name] = [ET.tostring(el, method='c14n').decode('utf-8') for el in root.iter()
                                    if isinstance(el.tag, str) and ET.QName(el).localname in
                                    {'vanish', 'webHidden', 'numPr', 'dataBinding', 'docVars'}]
    return {'stories': stories, 'relationships': relations, 'pictures': pictures,
            'charts': charts, 'protected': protected, 'style_semantics': style_semantics}


def compare_documents(before, after, mode='format_only'):
    if mode not in {'format_only', 'metadata_only'}:
        raise EditError('Sadržajne izmjene zahtijevaju zaseban odobreni plan; nisu stilski zahvat.')
    a, data_a, _, rel_a = _package(before)
    b, data_b, _, rel_b = _package(after)
    sa, sb = _semantic_snapshot(data_a, rel_a), _semantic_snapshot(data_b, rel_b)
    changes = [key for key in sa if sa[key] != sb[key]]
    if mode == 'metadata_only':
        allowed = _metadata_parts(data_a, rel_a, GROUPS) | _metadata_parts(data_b, rel_b, GROUPS)
        allowed |= {n for n in set(data_a) | set(data_b) if n.endswith('.rels') or n.startswith('word/media/')}
        allowed.add('[Content_Types].xml')
        if any(data_a.get(n) != data_b.get(n) for n in (set(data_a) | set(data_b)) - allowed):
            changes.append('non_metadata_parts')
    revisions = _revision_findings(data_b)
    status = 'blocked' if changes or any(x['severity'] == 'blocked' for x in revisions) else 'review_required' if revisions else 'pass'
    return {'schema_version': 1, 'kind': 'katedra_delivery_comparison', 'status': status,
            'scope': 'ordered_content_fields_relationships_visuals', 'whole_document': False,
            'before_sha256': _hash(a), 'after_sha256': _hash(b), 'changed': changes,
            'revision_findings': revisions, 'visual_status': 'unmeasured',
            'limitations': ['Ne dokazuje istinitost teksta.', 'Raster koji se vizualno precrta zahtijeva novi sadržajni pregled.',
                            'Nepodržana semantička promjena nije dopušteno oblikovanje.']}


def geometry_findings(path):
    _, data, root, _ = _package(path)
    results = []
    body = root.find('w:body', NS)

    def measure(block, width, height, label):
        for token in re.findall(r'\S{70,}', ''.join(block.itertext())):
            results.append({'code': 'unbroken_token', 'location': label, 'severity': 'review_required'})
            break
        if block.tag == f'{{{W}}}tbl':
            grid = block.findall('w:tblGrid/w:gridCol', NS)
            widths = [int(c.get(f'{{{W}}}w', '0')) for c in grid]
            w = block.find('w:tblPr/w:tblW', NS)
            declared = int(w.get(f'{{{W}}}w', '0')) if w is not None and w.get(f'{{{W}}}type') == 'dxa' else 0
            indent = block.find('w:tblPr/w:tblInd', NS)
            offset = max(0, int(indent.get(f'{{{W}}}w', '0'))) if indent is not None else 0
            if width and max(sum(widths), declared) + offset > width + 20:
                results.append({'code': 'table_width', 'location': label, 'severity': 'blocked',
                                'available_twips': width, 'table_twips': max(sum(widths), declared) + offset})
            for ri, row in enumerate(block.findall('w:tr', NS)):
                fixed = row.find('w:trPr/w:trHeight', NS)
                if fixed is not None and fixed.get(f'{{{W}}}hRule') == 'exact':
                    results.append({'code': 'fixed_row_height', 'location': f'{label}/row:{ri}', 'severity': 'review_required'})
                for ci, cell in enumerate(row.findall('w:tc', NS)):
                    cell_w = cell.find('w:tcPr/w:tcW', NS)
                    cw = int(cell_w.get(f'{{{W}}}w', '0')) if cell_w is not None and cell_w.get(f'{{{W}}}type') == 'dxa' else 0
                    for child in cell:
                        if child.tag != f'{{{W}}}tcPr':
                            measure(child, min(width, cw) if width and cw else width, height, f'{label}/cell:{ri}:{ci}')
            return
        for extent in block.findall('.//wp:inline/wp:extent', NS):
            if width and int(extent.get('cx', '0')) > width * 635 + 12700:
                results.append({'code': 'image_width', 'location': label, 'severity': 'blocked'})
        if block.find('.//wp:anchor', NS) is not None:
            results.append({'code': 'floating_visual', 'location': label, 'severity': 'review_required'})

    pending = []
    section = 0
    for block in body:
        is_section = block.tag == f'{{{W}}}sectPr'
        props = block if is_section else block.find('w:pPr/w:sectPr', NS)
        if not is_section:
            pending.append(block)
        if props is not None:
            size = props.find('w:pgSz', NS); margin = props.find('w:pgMar', NS)
            if size is None or margin is None:
                results.append({'code': 'section_geometry_unknown', 'location': f'section:{section}', 'severity': 'review_required'})
                width = height = None
            else:
                width = int(size.get(f'{{{W}}}w', '0')) - sum(int(margin.get(f'{{{W}}}{x}', '0')) for x in ('left', 'right', 'gutter'))
                height = int(size.get(f'{{{W}}}h', '0')) - sum(int(margin.get(f'{{{W}}}{x}', '0')) for x in ('top', 'bottom'))
                if width <= 0 or height <= 0:
                    results.append({'code': 'invalid_page_geometry', 'location': f'section:{section}', 'severity': 'blocked'})
            for i, item in enumerate(pending):
                measure(item, width, height, f'section:{section}/block:{i}')
            pending = []; section += 1
    if pending:
        results.append({'code': 'section_geometry_unknown', 'location': 'last-section', 'severity': 'review_required'})
    return results


def _metadata_parts(data, rels, groups):
    selected = set()
    for entries in rels.values():
        for item in entries.values():
            if META_TYPES.get(item['type']) in groups and not item['external']:
                selected.add(item['target'])
    for name, group in (('docProps/core.xml', 'core'), ('docProps/app.xml', 'application'), ('docProps/custom.xml', 'custom')):
        if group in groups and name in data:
            selected.add(name)
    return selected


def _validate_groups(groups):
    if not isinstance(groups, list) or len(groups) != len(set(groups)) or any(x not in GROUPS for x in groups):
        raise EditError('Navedi jedinstvene podržane skupine metapodataka, ne "sve".')


def metadata_findings(path, groups):
    _validate_groups(groups)
    _, data, _, rels = _package(path)
    out = []
    for name in sorted(_metadata_parts(data, rels, groups)):
        if not name.endswith('.xml') or any((el.text or '').strip() or el.attrib for el in _xml(data[name])):
            out.append({'code': 'metadata_present', 'part': name, 'severity': 'blocked'})
    if 'image_metadata' in groups:
        for name, raw in data.items():
            if not name.startswith('word/media/'):
                continue
            try:
                with Image.open(io.BytesIO(raw)) as im:
                    if im.info or im.getexif():
                        out.append({'code': 'image_metadata_present', 'part': name, 'severity': 'blocked'})
            except (OSError, ValueError):
                out.append({'code': 'image_metadata_unmeasured', 'part': name, 'severity': 'review_required'})
    return out


def clean_metadata(source, output, snapshot, groups, report=None):
    _validate_groups(groups)
    if not groups:
        raise EditError('Nije odabrana skupina metapodataka.')
    paths = [Path(source), Path(output), Path(snapshot)] + ([Path(report)] if report else [])
    if len({p.resolve() for p in paths}) != len(paths) or Path(output).suffix.casefold() != '.docx':
        raise EditError('Ulaz, izlaz, snapshot i izvještaj moraju biti različiti; izlaz je DOCX.')
    if any(p.exists() or p.is_symlink() for p in paths[1:]):
        raise EditError('Odredište postoji; ništa nije prepisano.')
    raw, data, _, rels = _package(source)
    if _revision_findings(data):
        raise EditError('Prvo izričito razriješi komentare/revizije; nema automatskog prihvaćanja.')
    for name, content in data.items():
        if name.endswith('.xml'):
            root = _xml(content)
            if next(root.iter(f'{{{W}}}dataBinding'), None) is not None or any(
                    'DOCPROPERTY' in ((el.text or '') + ' ' + (el.get(f'{{{W}}}instr') or '')).upper()
                    for el in root.iter() if isinstance(el.tag, str)):
                raise EditError('Dokument veže vidljivi sadržaj uz svojstva; potreban je zaseban pregled.')
    remove = _metadata_parts(data, rels, groups)
    for entries in rels.values():
        if any(item['target'] in remove and item['type'] not in META_TYPES for item in entries.values()):
            raise EditError('Odabrani metapodatak dijeli dio sa sadržajem dokumenta.')
    modified = {name: content for name, content in data.items() if name not in remove}
    for name, content in list(modified.items()):
        if name.endswith('.rels'):
            root = _xml(content)
            source_part = '' if name == '_rels/.rels' else str(PurePosixPath(name).parent.parent / PurePosixPath(name).name[:-5])
            changed = False
            for item in list(root):
                if item.get('TargetMode') != 'External' and _part_target(source_part, item.get('Target')) in remove:
                    root.remove(item); changed = True
            if changed:
                modified[name] = ET.tostring(root, xml_declaration=True, encoding='UTF-8', standalone=True)
    types = _xml(modified['[Content_Types].xml'])
    for item in list(types):
        if (item.get('PartName') or '').lstrip('/') in remove:
            types.remove(item)
    modified['[Content_Types].xml'] = ET.tostring(types, xml_declaration=True, encoding='UTF-8', standalone=True)
    if 'image_metadata' in groups:
        for name, content in list(modified.items()):
            if name.startswith('word/media/'):
                with Image.open(io.BytesIO(content)) as im:
                    if im.format != 'PNG' or im.getexif().get(274, 1) != 1:
                        raise EditError('Sigurno uklanjanje slikovnih metapodataka podržava samo PNG bez orijentacijskog EXIF-a.')
                    pixels = im.convert('RGBA'); buffer = io.BytesIO(); pixels.save(buffer, format='PNG')
                    modified[name] = buffer.getvalue()
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as archive:
        for name, content in modified.items():
            archive.writestr(name, content)
    created = None
    try:
        _write_new(snapshot, raw)
        created = _write_new(output, buffer.getvalue())
        parity = compare_documents(snapshot, output, mode='metadata_only')
        if parity['status'] != 'pass' or metadata_findings(output, groups):
            raise EditError('Očišćeni izlaz ne prolazi usporedbu/odabrani opseg privatnosti.')
        result = {'schema_version': 1, 'kind': 'katedra_metadata_cleanup', 'status': 'pass',
                  'before_sha256': _hash(raw), 'after_sha256': _sha(output), 'groups': groups,
                  'removed_parts': sorted(remove), 'whole_document': False, 'visual_status': 'unmeasured',
                  'unchecked': sorted((GROUPS - set(groups)) | {'embedded_metadata', 'application_readds_on_save'})}
        if report:
            _write_new(report, _canon(result) + b'\n')
        return result
    except (OSError, ValueError) as exc:
        if created is not None:
            try:
                st = Path(output).stat(follow_symlinks=False)
                if (st.st_dev, st.st_ino) == created:
                    Path(output).unlink()
            except OSError:
                pass
        raise EditError('Izlaz nije objavljen kao valjan; snapshot ostaje za oporavak.') from exc


def _run(args, cwd, timeout=180):
    return subprocess.run(args, cwd=cwd, capture_output=True, text=True, encoding='utf-8', errors='replace',
                          timeout=timeout, shell=False)


def _pdf_page_count(pdf):
    tool = shutil.which('pdfinfo')
    if not tool:
        raise EditError('pdfinfo nije dostupan; cjelovitost PDF stranica nije izmjerena.')
    result = _run([tool, str(Path(pdf).resolve())], Path(pdf).resolve().parent)
    count = re.search(r'^Pages:\s*(\d+)\s*$', result.stdout, re.M)
    if result.returncode or not count:
        raise EditError('PDF nema izmjeren broj stranica.')
    return int(count.group(1))


def render_document(document, output_dir):
    """Fresh isolated LO rendering. It does not fill in a visual approval."""
    raw, _, _, _ = _package(document)
    tools = {name: shutil.which(name) for name in ('soffice', 'pdfinfo', 'pdftoppm')}
    if not all(tools.values()):
        return {'status': 'unmeasured', 'missing_tools': [k for k, v in tools.items() if not v]}
    output = Path(output_dir)
    if output.exists() or output.is_symlink():
        raise EditError('Mapa rendera mora biti nova; nema ponovne uporabe starog rendera.')
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='katedra-render-', dir=output.parent) as tmp:
        stage = Path(tmp); source = stage/'document.docx'; source.write_bytes(raw)
        version = _run([tools['soffice'], '--version'], stage)
        if version.returncode:
            return {'status': 'unmeasured', 'reason': 'renderer_version_unavailable'}
        profile = (stage/'lo-profile').as_uri()
        run = _run([tools['soffice'], '-env:UserInstallation='+profile, '--headless', '--convert-to', 'pdf',
                    '--outdir', str(stage), str(source)], stage)
        pdf = stage/'document.pdf'
        if run.returncode or not pdf.is_file():
            return {'status': 'unmeasured', 'reason': 'renderer_failed', 'exit_code': run.returncode}
        info = _run([tools['pdfinfo'], str(pdf)], stage)
        count = re.search(r'^Pages:\s*(\d+)\s*$', info.stdout, re.M)
        if info.returncode or not count or not 1 <= int(count.group(1)) <= 300:
            return {'status': 'unmeasured', 'reason': 'page_count_unmeasured'}
        images = _run([tools['pdftoppm'], '-png', '-r', '120', str(pdf), str(stage/'page')], stage, timeout=300)
        if images.returncode:
            return {'status': 'unmeasured', 'reason': 'page_images_failed'}
        pngs = sorted(stage.glob('page-*.png'), key=lambda p: int(re.search(r'(\d+)\.png$', p.name).group(1)))
        if len(pngs) != int(count.group(1)):
            return {'status': 'unmeasured', 'reason': 'page_images_incomplete'}
        if _sha(document) != _hash(raw):
            return {'status': 'stale', 'reason': 'document_changed_during_render'}
        payload = stage/'publish'; payload.mkdir()
        shutil.copyfile(pdf, payload/'document.pdf')
        pages = []
        for index, png in enumerate(pngs, 1):
            dest = payload/f'page-{index}.png'; shutil.copyfile(png, dest)
            with Image.open(dest) as im:
                pages.append({'index': index, 'path': dest.name, 'sha256': _sha(dest), 'width': im.width, 'height': im.height})
        manifest = {'schema_version': 1, 'kind': 'katedra_render', 'document_sha256': _hash(raw),
                    'renderer': {'name': 'LibreOffice', 'version': version.stdout.strip()},
                    'pdf': {'path': 'document.pdf', 'sha256': _sha(payload/'document.pdf')}, 'pages': pages,
                    'created_at': datetime.now(timezone.utc).isoformat()}
        (payload/'render.json').write_bytes(_canon(manifest)+b'\n')
        # An atomically-created output directory prevents overwriting any earlier render.
        output.mkdir()
        for item in payload.iterdir():
            _write_new(output/item.name, item.read_bytes())
        return {'status': 'rendered', 'manifest': str(output/'render.json'), 'pages': len(pages),
                'visual_status': 'unmeasured', 'document_sha256': _hash(raw)}


def verify_render(document, manifest_path, review_path):
    base = {'status': 'unmeasured', 'whole_document': False, 'independent_verification': False,
            'reason': 'render_or_visual_review_missing'}
    if not manifest_path:
        return base
    try:
        manifest_path = Path(manifest_path)
        m = _json(manifest_path)
        _validate_schema('render_manifest', m)
        _keys(m, ('schema_version', 'kind', 'document_sha256', 'renderer', 'pdf', 'pages', 'created_at'))
        if type(m['schema_version']) is not int or m['schema_version'] != 1 or m['kind'] != 'katedra_render' or not _hex(m['document_sha256']):
            raise EditError('Neispravan render ugovor.')
        _keys(m['renderer'], ('name', 'version'))
        if not all(_nonempty(v) for v in m['renderer'].values()):
            raise EditError('Renderer nije imenovan/verzioniran.')
        if _sha(document) != m['document_sha256']:
            return {**base, 'status': 'stale', 'reason': 'document_hash_mismatch'}
        _keys(m['pdf'], ('path', 'sha256'))
        pdf = _inside(manifest_path.parent, m['pdf']['path'])
        if not _hex(m['pdf']['sha256']) or _sha(pdf) != m['pdf']['sha256'] or not pdf.read_bytes().startswith(b'%PDF-'):
            return {**base, 'status': 'stale', 'reason': 'pdf_hash_or_type_mismatch'}
        if not isinstance(m['pages'], list) or not 1 <= len(m['pages']) <= 300:
            raise EditError('Nema stranica za vizualnu provjeru.')
        if _pdf_page_count(pdf) != len(m['pages']):
            return {**base, 'reason': 'pdf_page_count_mismatch'}
        seen = set()
        for index, page in enumerate(m['pages'], 1):
            _keys(page, ('index', 'path', 'sha256', 'width', 'height'))
            if type(page['index']) is not int or page['index'] != index or page['path'] in seen:
                raise EditError('Nedostaju/duplicirane su stranice rendera.')
            seen.add(page['path'])
            image = _inside(manifest_path.parent, page['path'])
            if not _hex(page['sha256']) or _sha(image) != page['sha256']:
                return {**base, 'status': 'stale', 'reason': 'page_hash_mismatch'}
            with Image.open(image) as im:
                if (im.width, im.height) != (page['width'], page['height']) or min(im.size) < 800:
                    raise EditError('Slika stranice nije puni čitljiv render.')
        base['renderer'] = m['renderer']
        if not review_path:
            return base
        review = _json(review_path)
        _validate_schema('visual_review', review)
        _keys(review, ('schema_version', 'kind', 'render_manifest_sha256', 'document_sha256', 'reviewer',
                       'reviewed_pages', 'decision', 'notes', 'reviewed_at'))
        if type(review['schema_version']) is not int or review['schema_version'] != 1 or review['kind'] != 'katedra_visual_review':
            raise EditError('Neispravan ugovor vizualnog pregleda.')
        if review['render_manifest_sha256'] != _sha(manifest_path) or review['document_sha256'] != m['document_sha256']:
            return {**base, 'status': 'stale', 'reason': 'review_hash_mismatch'}
        if not _nonempty(review['reviewer']) or not _nonempty(review['notes']) or not _nonempty(review['reviewed_at']):
            raise EditError('Vizualni pregled nije obrazložen i imenovan.')
        if review['reviewed_pages'] != list(range(1, len(m['pages'])+1)):
            return {**base, 'reason': 'not_all_pages_reviewed'}
        if review['decision'] != 'approved':
            return {**base, 'status': 'blocked' if review['decision'] == 'rejected' else 'unmeasured', 'reason': 'visual_review_not_approved'}
        return {**base, 'status': 'pass', 'reason': 'named_all_page_attestation_matches_bytes',
                'reviewer': review['reviewer'], 'pages': len(m['pages'])}
    except (ValueError, OSError, KeyError, TypeError) as exc:
        return {**base, 'reason': 'invalid_evidence: '+str(exc)}


def check_delivery(manifest_path, expected_document=None, project_root=None):
    p = Path(manifest_path)
    data = _json(p)
    _validate_schema('delivery_manifest', data)
    _keys(data, ('schema_version', 'kind', 'before', 'after', 'mode', 'metadata_groups', 'render_manifest', 'visual_review', 'excluded'))
    if type(data['schema_version']) is not int or data['schema_version'] != 1 or data['kind'] != 'katedra_delivery':
        raise EditError('Nepodržani delivery ugovor.')
    _validate_groups(data['metadata_groups'])
    for label in ('before', 'after'):
        _keys(data[label], ('path', 'sha256'))
        if not _hex(data[label]['sha256']):
            raise EditError('Nedostaje dokumentni SHA-256.')
    if not isinstance(data['excluded'], list):
        raise EditError('Isključenja moraju biti izričit popis.')
    for excluded in data['excluded']:
        _keys(excluded, ('item', 'reason'))
        if not all(_nonempty(v) for v in excluded.values()) or excluded['item'] not in {'JMBAG', 'dates', 'signature', 'CV', 'administrative'}:
            raise EditError('Isključiti se mogu samo obrazložena administrativna polja.')
    base_dir = Path(project_root).resolve() if project_root is not None else p.parent
    before, after = (_inside(base_dir, data[key]['path']) for key in ('before', 'after'))
    if expected_document is not None and after.resolve() != Path(expected_document).resolve():
        raise EditError('Delivery manifest ne pripada dokumentu gatea.')
    result = {'schema_version': 1, 'kind': 'katedra_delivery_result', 'scope': 'delivery_integrity',
              'whole_document': False, 'excluded': data['excluded'], 'manifest_sha256': _sha(p)}
    if any(_sha(path) != data[key]['sha256'] for key, path in (('before', before), ('after', after))):
        return {**result, 'status': 'stale', 'reason': 'document_hash_mismatch'}
    comparison = compare_documents(before, after, data['mode'])
    geometry = geometry_findings(after)
    privacy = metadata_findings(after, data['metadata_groups'])
    render = _inside(base_dir, data['render_manifest']) if data['render_manifest'] is not None else None
    review = _inside(base_dir, data['visual_review']) if data['visual_review'] is not None else None
    visual = verify_render(after, render, review)
    if comparison['status'] == 'blocked' or any(x['severity'] == 'blocked' for x in geometry+privacy):
        status = 'blocked'
    elif visual['status'] != 'pass':
        status = visual['status']
    elif comparison['status'] != 'pass' or any(x['severity'] == 'review_required' for x in privacy):
        status = 'review_required'
    else:
        status = 'pass'
    if _sha(p) != result['manifest_sha256'] or _sha(after) != data['after']['sha256'] or _sha(before) != data['before']['sha256']:
        status = 'stale'
    return {**result, 'status': status, 'comparison': comparison, 'geometry': geometry, 'privacy': privacy,
            'visual': visual, 'metadata_scope': data['metadata_groups'],
            'limitations': ['Semantička istinitost rada nije potvrđena.', 'Vizualno odobrenje je imenovana izjava, ne neovisno ovjerena činjenica.',
                            'LibreOffice render ne potvrđuje prikaz u Microsoft Wordu.', 'Nepregledani metapodaci ugrađenih objekata nisu odobreni.']}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    compare = sub.add_parser('compare'); compare.add_argument('before'); compare.add_argument('after')
    compare.add_argument('--mode', choices=('format_only', 'metadata_only'), default='format_only')
    clean = sub.add_parser('clean'); clean.add_argument('source'); clean.add_argument('--out', required=True)
    clean.add_argument('--snapshot', required=True); clean.add_argument('--groups', nargs='+', required=True)
    clean.add_argument('--report')
    render = sub.add_parser('render'); render.add_argument('document'); render.add_argument('--out-dir', required=True)
    check = sub.add_parser('check'); check.add_argument('--manifest', required=True); check.add_argument('--rad')
    check.add_argument('--out'); check.add_argument('--project-root')
    args = parser.parse_args(argv)
    try:
        if args.command == 'compare':
            result = compare_documents(args.before, args.after, args.mode)
        elif args.command == 'clean':
            result = clean_metadata(args.source, args.out, args.snapshot, args.groups, args.report)
        elif args.command == 'render':
            result = render_document(args.document, args.out_dir)
        else:
            result = check_delivery(args.manifest, args.rad, args.project_root)
            if args.out:
                # Fresh per-run reports only: a source or old result cannot be overwritten.
                _write_new(args.out, _canon(result)+b'\n')
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if result['status'] in {'pass', 'rendered'} else 1 if result['status'] == 'blocked' else 2
    except (ValueError, OSError, subprocess.SubprocessError) as exc:
        print(json.dumps({'status': 'unmeasured', 'error': str(exc)}, ensure_ascii=False))
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
