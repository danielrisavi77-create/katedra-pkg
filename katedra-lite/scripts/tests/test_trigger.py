#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Testovi za katedra-lite/evals/pokreni_trigger.py — mjerilo usmjeravanja.

Kvar 124: harness je bez instaliranog `claude` CLI-ja padao u
`FileNotFoundError [WinError 2]`, iz kojega se ne vidi da mjerenja uopće nije
bilo. Uz to je radnu mapu imao ukovanu, pa se drugi uvjet iz vlastitog
ograničenja („isti skup, ali s radom u mapi") nije dao izmjeriti.

Sam odziv modela ovdje se ne mjeri — to traži živi model. Mjeri se da harness
kaže istinu o tome je li mogao mjeriti i gdje je mjerio.
"""
import importlib.util
import os
import sys
import tempfile

TU = os.path.dirname(os.path.abspath(__file__))
KORIJEN = os.path.dirname(os.path.dirname(TU))
HARNESS = os.path.join(KORIJEN, "evals", "pokreni_trigger.py")

_spec = importlib.util.spec_from_file_location("pokreni_trigger", HARNESS)
pt = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(pt)

PALO = []
SVE = []


def check(naziv, uvjet, detalj=""):
    # Kvar 125: broj u izvještaju mora se BROJATI, ne tvrditi. Ukovana
    # konstanta („%d/%d" % (6 - len(PALO), 6)) razmakne se čim se doda
    # provjera, i onda suite javlja 6/6 dok ih je pokrenuo sedam. Taj broj
    # čita `zakrpa.py --provjeri-tvrdnje`, pa laž putuje dalje.
    SVE.append(naziv)
    print("  %-8s %s" % ("✓" if uvjet else "✗ FAIL", naziv))
    if not uvjet:
        PALO.append(naziv)
        if detalj:
            print("           detalj: %r" % (detalj,))


class LazniRun:
    """Bilježi kako je subprocess.run pozvan i glumi zadani ishod."""

    def __init__(self, ishod=None):
        self.ishod = ishod
        self.poziv = None

    def __call__(self, cmd, **kw):
        self.poziv = (cmd, kw)
        if isinstance(self.ishod, Exception):
            raise self.ishod
        return self.ishod


class LazniIzlaz:
    def __init__(self, stdout="", returncode=0):
        self.stdout = stdout
        self.returncode = returncode


def main():
    print("=" * 70)
    print("TESTOVI pokreni_trigger.py")
    print("=" * 70)

    stari = pt.subprocess.run

    # R59: alat kojega nema je greška o okolini, ne pad mjerila
    pt.subprocess.run = LazniRun(FileNotFoundError(2, "nema"))
    r = pt.prvi_skill("upit", 5, None)
    check("R59: nedostatak CLI-ja je zapisana greška, ne traceback",
          r["greska"] and "claude" in r["greska"] and r["skill"] is None, r)
    check("R59: zapis ima sve ključeve koje izvještaj čita",
          {"skill", "pozicija", "greska"} <= set(r), sorted(r))

    # R59b: isto vrijedi za timeout
    pt.subprocess.run = LazniRun(pt.subprocess.TimeoutExpired("claude", 5))
    r = pt.prvi_skill("upit", 5, None)
    check("R59: timeout ima iste ključeve", {"skill", "pozicija", "greska"} <= set(r), r)

    # R60: radna mapa se prosljeđuje — bez toga se drugi uvjet ne da izmjeriti
    mapa = tempfile.mkdtemp()
    lazni = LazniRun(LazniIzlaz(""))
    pt.subprocess.run = lazni
    pt.prvi_skill("upit", 5, None, mapa)
    check("R60: --mapa postaje cwd upita", lazni.poziv[1].get("cwd") == mapa,
          lazni.poziv[1].get("cwd"))

    lazni2 = LazniRun(LazniIzlaz(""))
    pt.subprocess.run = lazni2
    pt.prvi_skill("upit", 5, None)
    check("R60: bez --mapa ostaje evals/", lazni2.poziv[1].get("cwd") == str(pt.OVDJE),
          lazni2.poziv[1].get("cwd"))

    # R61: prvi Skill poziv se traži BILO GDJE u prijepisu, ne samo kao prvi alat
    import json as _json
    redci = "\n".join(_json.dumps(x, ensure_ascii=False) for x in [
        {"type": "assistant", "message": {"content": [
            {"type": "tool_use", "name": "Bash", "input": {}}]}},
        {"type": "assistant", "message": {"content": [
            {"type": "tool_use", "name": "Skill", "input": {"skill": "katedra-lite"}}]}},
    ])
    pt.subprocess.run = LazniRun(LazniIzlaz(redci))
    r = pt.prvi_skill("upit", 5, None)
    check("R61: Skill nakon drugog alata i dalje je okidanje",
          r["skill"] == "katedra-lite" and r["pozicija"] == 2, r)

    # R62: alat se traži prije nego se pošalje ijedan upit
    stara_which = pt.shutil.which
    pt.shutil.which = lambda ime: None
    check("R62: nadji_claude() javlja da alata nema", pt.nadji_claude() is None)
    pt.shutil.which = lambda ime: "/put/do/claude"
    check("R62: nadji_claude() vraća put kad alat postoji",
          pt.nadji_claude() == "/put/do/claude")
    pt.shutil.which = stara_which

    pt.subprocess.run = stari
    print("=" * 70)
    print("REZULTATI TESTOVA: %d/%d prošlo"
          % (len(SVE) - len(PALO), len(SVE)))
    print("=" * 70)
    return 1 if PALO else 0


if __name__ == "__main__":
    sys.exit(main())
