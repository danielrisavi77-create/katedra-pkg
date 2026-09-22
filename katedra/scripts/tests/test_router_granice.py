#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Testovi za katedra/scripts/router_granice.py — granica veličine svih routera.

Ograda mora pasti na debelom routeru (46 KB rad-orchestrator iz v2.1.0), proći
na tankom i javiti „nije izmjereno" (2) kad SKILL.md-a nema, a ne prolaz.
"""
import contextlib
import importlib.util
import io
import os
import sys
import tempfile
from pathlib import Path

TU = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = os.path.dirname(TU)
KORIJEN = Path(SCRIPTS).parents[1]

_spec = importlib.util.spec_from_file_location("router_granice", os.path.join(SCRIPTS, "router_granice.py"))
rg = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(rg)

PALO = []
SVE = []


def check(naziv, uvjet, detalj=""):
    SVE.append(naziv)
    print("  %-8s %s" % ("✓" if uvjet else "✗ FAIL", naziv))
    if not uvjet:
        PALO.append(naziv)
        if detalj:
            print("           detalj: %r" % (detalj,))


def tiho(fn, *a):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        kod = fn(*a)
    return kod, buf.getvalue()


with tempfile.TemporaryDirectory() as d:
    r = Path(d)
    (r / "rad-audit").mkdir()
    (r / "rad-audit" / "SKILL.md").write_text("x" * 1000, encoding="utf-8")
    (r / "rad-orchestrator").mkdir()
    (r / "rad-orchestrator" / "SKILL.md").write_text("ž" * 46321, encoding="utf-8")
    kod, out = tiho(rg.main, [str(r)])
    check("debeli router (46 321 znak) obara ogradu, izlaz 1", kod == 1, (kod, out))
    check("nalaz imenuje skill i broj znakova", "rad-orchestrator/SKILL.md ima 46321" in out, out)

    (r / "rad-orchestrator" / "SKILL.md").write_text("ž" * 24000, encoding="utf-8")
    kod, out = tiho(rg.main, [str(r)])
    check("točno na granici (24 000) prolazi — broje se znakovi, ne bajtovi", kod == 0, (kod, out))

with tempfile.TemporaryDirectory() as d:
    kod, out = tiho(rg.main, [d])
    check("prazan korijen je 'nije izmjereno' (2), ne prolaz", kod == 2, (kod, out))

kod, out = tiho(rg.main, [str(KORIJEN)])
check("stvarni paket: svi routeri unutar granice", kod == 0, out)

print("")
print("%d/%d" % (len(SVE) - len(PALO), len(SVE)))
sys.exit(1 if PALO else 0)
