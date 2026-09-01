#!/usr/bin/env python3
"""Objedinjeni izvještaj audita: pokreni sve provjere, razvrstaj nalaze po
težini (KRITIČNO/SREDNJE/KOZMETIČKO) i spremi kao Markdown (+ opcionalno JSON).

Uporaba:
  python3 generate_report.py rad.docx --sources izvori/
  python3 generate_report.py rad.docx --sources izvori/ --out izvjestaj.md
  python3 generate_report.py rad.docx --sources izvori/ --json izvjestaj.json

Zašto ovako (a ne da svaka skripta vraća strukturirane podatke): pojedinačne
provjere su namjerno jednostavni read-only ispisi u terminal (lako ih je
pokrenuti zasebno i pratiti tijekom rada). Ovaj alat NE mijenja njihov API —
hvata stdout svake i heuristički bucketira retke sa "⚠" po težini prema
ključnim riječima. To je namjerna pojednostavljenje: sažetak je orijentir za
PRIORITET pregleda, ne zamjena za čitanje. Puni ispis svake faze je uvijek
priložen ispod sažetka (izvor istine > dojam)."""
import sys
import os
import io
import json
import contextlib

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import check_fields
import check_citations
import check_citations_authoryear
import check_typography
import check_repetition
import numbers_inventory
from common import load_docx_text, detect_citation_style

CRITICAL_HINTS = [
    "NEURAVNOTEŽENO", "NEPRIHVAĆENE IZMJENE", "SIROČAD", "CITAT BEZ REFERENCE",
    "NEMA U IZVORIMA", "nije nađeno u izvorima", "BEZ vidljive oznake citata",
    "documentProtection: ⚠ DA", "permStart", "rupe u numeraciji",
    "neparan broj navodnika", "krši rastući redoslijed", "w:lock",
]
COSMETIC_HINTS = [
    "navodni", "crtic", "množenj", "decimal", "nbsp", "zalijepljeno",
    "tipografij", "'x' kao množenje", "inč-oznaka", "bez razmaka",
]


def classify(line):
    low = line.lower()
    for h in CRITICAL_HINTS:
        if h.lower() in low:
            return "kritično"
    for h in COSMETIC_HINTS:
        if h.lower() in low:
            return "kozmetičko"
    return "srednje"


def run_captured(fn, *args):
    """Pokreni fn(*args) hvatajući stdout; nikad ne ruši generate_report ako
    jedna faza baci iznimku (samo to zabilježi u ispisu te faze)."""
    buf = io.StringIO()
    code = 0
    try:
        with contextlib.redirect_stdout(buf):
            code = fn(*args) or 0
    except SystemExit as e:
        code = e.code if isinstance(e.code, int) else (1 if e.code else 0)
    except Exception as e:
        buf.write(f"[greška u modulu: {e}]\n")
        code = 1
    return buf.getvalue(), code


def main(argv):
    path = argv[0]
    sources = argv[argv.index("--sources") + 1] if "--sources" in argv else None
    out_md = argv[argv.index("--out") + 1] if "--out" in argv else \
        os.path.splitext(path)[0] + "_izvjestaj.md"
    out_json = argv[argv.index("--json") + 1] if "--json" in argv else None

    phases = []

    txt, code = run_captured(check_fields.main, path)
    phases.append(("A/F — Polja i formatiranje", txt, code))

    body, cells, _ = load_docx_text(path, include_tables=True)
    style, style_counts = detect_citation_style(body + "\n" + "\n".join(cells))
    style_note = f"[detektiran stil citiranja: {style} {style_counts}]"
    # ISTA logika kao audit_all.py — za "mixed" se pokreću OBA checkera + upozorenje
    # (raniji drift: generate_report je za mixed preskakao IEEE provjeru, pa je alat
    # za finalnu isporuku prijavljivao manje nego terminal-ispis)
    if style in ("ieee", "unknown", "mixed"):
        txt, code = run_captured(check_citations.main, path)
        phases.append(("B — Citiranje (IEEE [N])", style_note + "\n" + txt, code))
    if style in ("authoryear", "unknown", "mixed"):
        txt, code = run_captured(check_citations_authoryear.main, path)
        phases.append(("B — Citiranje (autor-godina)", style_note + "\n" + txt, code))
    if style == "mixed":
        phases.append(("B — Napomena o stilu",
                       "⚠ oba stila citiranja detektirana u sličnoj mjeri — provjeri ručno koristi li "
                       "rad dosljedno JEDAN stil ili je miješanje namjerno (npr. norme u uglatim "
                       "zagradama uz autor-godina tekst)", 1))

    txt, code = run_captured(numbers_inventory.main, path)
    phases.append(("C — Brojčani inventar", txt, code))

    txt, code = run_captured(check_typography.main, path)
    phases.append(("E — Tipografija", txt, code))

    txt, code = run_captured(check_repetition.main, path)
    phases.append(("E — Ponavljanja i ritam", txt, code))

    if sources:
        import cross_check
        import check_overlap
        txt, code = run_captured(cross_check.main, [path, sources])
        phases.append(("D — Cross-check s izvorima", txt, code))
        txt, code = run_captured(check_overlap.main, [path, sources])
        phases.append(("D — Preklapanje (verbatim-copy)", txt, code))
    else:
        phases.append(("D — Cross-check", "[preskočeno — dodaj --sources <folder> s izvornom građom]", 0))

    buckets = {"kritično": [], "srednje": [], "kozmetičko": []}
    for name, ptxt, pcode in phases:
        for line in ptxt.split("\n"):
            if "⚠" in line:
                buckets[classify(line)].append((name, line.strip()))
    total = sum(len(v) for v in buckets.values())

    md = [f"# Sažetak audita — `{os.path.basename(path)}`\n"]
    md.append(f"Ukupno nalaza: **{total}** — kritično {len(buckets['kritično'])}, "
              f"srednje {len(buckets['srednje'])}, kozmetičko {len(buckets['kozmetičko'])}\n")
    for level, label in [("kritično", "🔴 Kritično"), ("srednje", "🟠 Srednje"), ("kozmetičko", "⚪ Kozmetičko")]:
        items = buckets[level]
        md.append(f"\n## {label} ({len(items)})\n")
        md.append("_nema nalaza_" if not items else "\n".join(f"- **[{n}]** {l}" for n, l in items))
    md.append("\n\n---\n\n# Puni ispis po fazama\n")
    md.append("_(sažetak gore je orijentir za prioritet pregleda — ovo ispod je izvor istine; "
               "automatska bucketizacija je heuristika i može krivo svrstati nalaz, uvijek "
               "provjeri puni kontekst prije zaključka)_\n")
    for name, ptxt, pcode in phases:
        md.append(f"\n## {name}\n\n```\n{ptxt.strip()}\n```\n")

    report_text = "\n".join(md)
    with open(out_md, "w", encoding="utf-8") as f:
        f.write(report_text)
    print(f"✔ izvještaj spremljen: {out_md}")
    print(f"  nalaza: kritično {len(buckets['kritično'])}, srednje {len(buckets['srednje'])}, "
          f"kozmetičko {len(buckets['kozmetičko'])}")

    if out_json:
        payload = {
            "path": path,
            "counts": {k: len(v) for k, v in buckets.items()},
            "findings": {k: [{"phase": n, "line": l} for n, l in v] for k, v in buckets.items()},
            "phase_exit_codes": {name: pcode for name, _, pcode in phases},
        }
        with open(out_json, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
        print(f"✔ JSON spremljen: {out_json}")

    return 1 if buckets["kritično"] else 0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(2)
    sys.exit(main(sys.argv[1:]))
