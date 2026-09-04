#!/usr/bin/env python3
"""Jedan orkestrator provjera po fazama rada.

Zašto postoji
-------------
Do v1.3 je ``references/predaja.md`` tražio da agent zapamti desetak naredbi, u
točnom redoslijedu, sa svojim zastavicama. Preskočena naredba nije proizvodila
nikakvu poruku — provjera koja se nije pokrenula izgleda identično kao provjera
koja je prošla. To je najvjerojatniji način da lanac padne u stvarnoj sesiji, i
jedini kvar u paketu koji se ne vidi ni na jednom izlaznom kodu.

Što radi
--------
Pokreće propisane provjere za fazu, redom, i svaki korak svrstava u jedno od
četiri stanja. Razlika između zadnja dva je bit ove skripte:

* ``ok``          — provjera je prošla;
* ``nalaz``       — provjera je našla problem (izlazni kod 1);
* ``preskočeno``  — ulaz ne postoji; razlog se ISPISUJE, ne prešućuje (pravilo 8);
* ``alat pukao``  — provjera se srušila ili je odbila ulaz (izlazni kod ≥ 2).

Alat koji je pukao **nije** provjera koja je prošla. Prije ovoga su ta dva
stanja u praksi izgledala isto, jer ih je čovjek razlikovao po tekstu na ekranu.

Ne zamjenjuje reference. ``predaja.md`` i dalje nosi ono što alat ne može
provjeriti (potpis izjave, zvanje mentora, Update Field u Wordu).
"""
from __future__ import annotations

import argparse
import json
import os
import shlex
import subprocess
import sys
from datetime import datetime

SKRIPTE = os.path.dirname(os.path.abspath(__file__))
if SKRIPTE not in sys.path:
    sys.path.insert(0, SKRIPTE)

import context  # noqa: E402
import vjestine  # noqa: E402

FAZE = ("plan", "pisanje", "audit", "predaja")

OK, NALAZ, PRESKOCENO, PUKAO = "ok", "nalaz", "preskoceno", "pukao"
ZNAK = {OK: "✅", NALAZ: "❌", PRESKOCENO: "➖", PUKAO: "💥"}


class Korak:
    def __init__(self, kid, naziv, argv, *, blokira=True, treba=(),
                 satelit=None, zasto=""):
        self.kid = kid
        self.naziv = naziv
        self.argv = argv
        self.blokira = blokira
        self.treba = list(treba)
        self.satelit = satelit
        self.zasto = zasto


def _k(*dijelovi):
    return [sys.executable, os.path.join(SKRIPTE, dijelovi[0]), *dijelovi[1:]]


MOD_FAZE = {"plan": "1", "pisanje": "2", "audit": "4", "predaja": "6"}


def _ucitavanje(faza, kat):
    """Prvi korak svake faze: što se mora pročitati na OVOM projektu.

    Ide prije provjera jer je jeftin, savjetodavan i mijenja ono što slijedi —
    provjera pokrenuta bez pročitanog protokola daje nalaz koji nitko ne zna
    protumačiti.
    """
    return Korak("ucitavanje", "što se mora pročitati na ovom projektu",
                 _k("ucitavanje.py", "--mod", MOD_FAZE[faza], "--kat", kat),
                 blokira=False,
                 zasto="popis je izveden iz stanja, ne fiksan (pravilo 25)")


def koraci(faza: str, c: dict) -> list[Korak]:
    """Popis koraka za fazu. Redoslijed je ugovor, ne preporuka."""
    rad, pdf, profil, tip, kat = c["rad"], c["pdf"], c["profil"], c["tip"], c["kat"]
    claims = os.path.join(kat, "claims.jsonl")
    evidence = os.path.join(kat, "evidence.jsonl")
    izvori = os.path.join(kat, "izvori.json")

    if faza == "plan":
        return [
            _ucitavanje(faza, kat),
            Korak("perspektive", "perspective map (2+ perspektive)",
                  _k("perspective_map.py", "--kat", kat, "validate",
                     "--work-type", tip or "diplomski"),
                  zasto="bez njega PLAN GATE blokira uvoz strukture"),
            Korak("plan", "PLAN GATE (teza, struktura, izvori)",
                  _k("plan_state.py", "--kat", kat, "status"),
                  zasto="nijedno poglavlje završnog/diplomskog prije odobrenog plana"),
            Korak("dijelovi", "os dijelova — što rad uopće mora imati",
                  _k("dijelovi.py", "--kat", kat, "--status"),
                  blokira=False,
                  zasto="popis dijelova i ono što nitko ne provjerava"),
            Korak("pretraga", "strategija pretrage i plan čitanja",
                  _k("pretraga.py", "--kat", kat, "status"),
                  blokira=False,
                  zasto="na obrani se pita „kako ste došli do ove literature”"),
            Korak("grill", "sokratski stress-test plana",
                  _k("grill_me.py", "--kat", kat, "status"),
                  blokira=False, zasto="advisory; ne blokira gate"),
        ]

    if faza == "pisanje":
        return [
            _ucitavanje(faza, kat),
            Korak("evidence", "strict evidence gate",
                  _k("evidence_gate.py", "--claims", claims, "--evidence", evidence,
                     "--sources", izvori, "--policy", "strict",
                     "--out", os.path.join(kat, "evidence_gate.json")),
                  treba=[claims, evidence],
                  zasto="unsupported/conflicted/contradicted ne ulaze u tekst"),
            Korak("zamjerke", "otvorene zamjerke mentora",
                  _k("zamjerke.py", "--kat", kat, "provjeri"),
                  treba=[os.path.join(kat, "zamjerke.json")],
                  zasto="zamjerka spomenuta u intakeu pa zaboravljena je najskuplja greška"),
            Korak("jezik", "hrvatski pravopis i gramatika",
                  _k("provjeri_jezik.py", rad,
                     "--json", os.path.join(kat, "jezik.json")),
                  treba=[rad], blokira=False,
                  zasto="ono što mentor zaokruži crvenim"),
            Korak("tempo", "opseg naspram dana do roka",
                  _k("tempo.py", "--kat", kat, "--profil", profil),
                  treba=[os.path.join(kat, "plan.json")], blokira=False,
                  zasto="hodogram postoji tek u modu 6, a tada je kasno"),
            Korak("stil", "tragovi generiranog teksta",
                  _k("check_ai_style.py", rad), treba=[rad], blokira=False),
            Korak("argument", "teza i zaključak",
                  _k("check_argument.py", rad, "--profil", profil,
                     "--json", os.path.join(kat, "arg.json")),
                  treba=[rad, profil], blokira=False,
                  zasto="forma nije argument (željezno pravilo 11)"),
            Korak("dijelovi", "os dijelova — je li koji obavezan dio netaknut",
                  _k("dijelovi.py", "--kat", kat, "--provjeri", "--faza", "pisanje"),
                  blokira=False),
        ]

    if faza == "audit":
        return [
            _ucitavanje(faza, kat),
            Korak("motor", "razrješavanje motora rad-audit",
                  _k("engine.py", "--provjeri"), blokira=False,
                  zasto="izlaz 3/4 = smanjeni opseg, deklarira se, ne prešućuje"),
            Korak("pravila", "usklađenost s profilom fakulteta",
                  _k("check_rules.py", rad, "--profil", profil, "--tip", tip or "zavrsni",
                     "--json", os.path.join(kat, "pravila.json")),
                  treba=[rad, profil]),
            Korak("argument", "teza, zaključak, razina argumenta",
                  _k("check_argument.py", rad, "--profil", profil,
                     "--json", os.path.join(kat, "arg.json")),
                  treba=[rad, profil], blokira=False),
            Korak("stil", "tragovi generiranog teksta",
                  _k("check_ai_style.py", rad), treba=[rad], blokira=False),
            Korak("jezik", "hrvatski pravopis i gramatika",
                  _k("provjeri_jezik.py", rad,
                     "--json", os.path.join(kat, "jezik.json")),
                  treba=[rad], blokira=False),
            Korak("odlomci", "geometrija odlomaka u stvarnom prijelomu",
                  _k("check_paragraphs.py", rad, "--profil", profil),
                  treba=[rad, profil], blokira=False),
            Korak("izracuni", "izbor formule: postotni bod, osnovica, indeks, udjeli",
                  _k("provjeri_izracune.py", rad, "--model",
                     os.path.join(kat, "model.json"),
                     "--json", os.path.join(kat, "izracuni.json")),
                  treba=[rad], blokira=False,
                  zasto="brojka može biti aritmetički točna, a formula kriva"),
            Korak("fusnote", "disciplina fusnota: ibid., skraćeni oblik, numeracija",
                  _k("provjeri_fusnote.py", rad,
                     "--json", os.path.join(kat, "fusnote.json")),
                  treba=[rad], blokira=False,
                  zasto="za legal-footnote profile središnje; bez fusnota alat kaže da nema što"),
            Korak("dosljednost", "cross-chapter proturječja",
                  _k("consistency_check.py", "--claims", claims,
                     "--out", os.path.join(kat, "consistency.json")),
                  treba=[claims], blokira=False),
            # Kvar 48: korak iznad gleda samo tvrdnje iz lanca, pa brojka koju
            # rad izvodi iz vlastitog prikaza („šest od sedam koraka") nikad
            # nije uspoređena sa sobom.
            Korak("brojke_teksta", "brojke koje rad sam izvodi iz svojih prikaza",
                  _k("provjeri_brojke_u_tekstu.py", rad,
                     "--json", os.path.join(kat, "brojke_teksta.json")),
                  treba=[rad], blokira=False,
                  zasto="pita, ne presuđuje: dva ciklusa smiju imati različite brojke"),
            Korak("originalnost", "preklapanje s ingestiranim izvorima",
                  _k("originality_check.py", rad, "--evidence", evidence,
                     "--json", os.path.join(kat, "originality.json")),
                  treba=[rad, evidence], blokira=False,
                  zasto="advisory; NIJE plagijat-detekcija protiv interneta"),
            Korak("literatura", "popis literature protiv kućnog stila",
                  _k("provjeri_literaturu.py", rad, "--profil", profil,
                     "--json", os.path.join(kat, "literatura.json")),
                  treba=[rad, profil], blokira=False,
                  zasto="oblik jedinice, uvlaka, razmak i abecedni red — do v1.4 nitko"),
            Korak("prikazi", "slike i grafikoni: dpi, širina, omjer, pismo",
                  _k("provjeri_prikaze.py", rad,
                     "--json", os.path.join(kat, "prikazi.json")),
                  treba=[rad], blokira=False,
                  zasto="struktura prikaza ide kroz check_rules; ovo mjeri samu sliku"),
            Korak("rubrika", "gdje rad stoji prema kriterijima i što ga drži",
                  _k("rubrika.py", "--kat", kat, "--opsirno",
                     "--json", os.path.join(kat, "rubrika.json")),
                  blokira=False,
                  zasto="ide ZADNJI: agregira artefakte koje su prethodni koraci napisali"),
        ]

    # predaja
    return [
        _ucitavanje(faza, kat),
        Korak("dijelovi", "svi obavezni dijelovi rada napravljeni",
              _k("dijelovi.py", "--kat", kat, "--provjeri", "--faza", "predaja"),
              zasto="rad kojemu fali dio pada formalno, prije nego ga itko pročita"),
        Korak("pravila", "usklađenost s profilom fakulteta",
              _k("check_rules.py", rad, "--profil", profil, "--tip", tip or "zavrsni",
                 "--json", os.path.join(kat, "pravila.json")),
              treba=[rad, profil]),
        Korak("placeholderi", "[TREBA IZVOR] / [PROVJERI STR.] u tekstu, ćelijama i fusnotama",
              _k("check_placeholders.py", rad, "--json",
                 os.path.join(kat, "placeholders.json")),
              treba=[rad]),
        Korak("sazetak", "sažetak protiv rada",
              _k("provjeri_sazetak.py", rad, "--json",
                 os.path.join(kat, "sazetak.json")),
              treba=[rad],
              zasto="mentor ga čita prvi; paritetnu tablicu i dalje mora pročitati čovjek"),
        Korak("engleski", "summary i ključne riječi protiv hrvatskog sažetka",
              _k("provjeri_engleski.py", rad, "--profil", profil, "--json",
                 os.path.join(kat, "engleski.json")),
              treba=[rad], blokira=False),
        Korak("jezik", "hrvatski pravopis i gramatika",
              _k("provjeri_jezik.py", rad,
                 "--json", os.path.join(kat, "jezik.json")),
              treba=[rad],
              zasto="pravopisna pogreška na prvoj stranici stoji koliko i na zadnjoj"),
        Korak("izracuni", "izbor formule: postotni bod, osnovica, indeks, udjeli",
              _k("provjeri_izracune.py", rad, "--model",
                 os.path.join(kat, "model.json"),
                 "--json", os.path.join(kat, "izracuni.json")),
              treba=[rad], blokira=False,
              zasto="brojka može biti aritmetički točna, a formula kriva"),
        Korak("fusnote", "disciplina fusnota: ibid., skraćeni oblik, numeracija",
              _k("provjeri_fusnote.py", rad,
                 "--json", os.path.join(kat, "fusnote.json")),
              treba=[rad], blokira=False,
              zasto="za legal-footnote profile središnje; bez fusnota alat kaže da nema što"),
        Korak("izvori", "pokrivenost citata i popisa",
              _k("verify_sources.py", rad, "--pokrivenost", "--offline"),
              treba=[rad],
              zasto="svaki izvor citiran barem jednom, svaki citat ima izvor"),
        Korak("zamjerke", "sve zamjerke mentora zatvorene",
              _k("zamjerke.py", "--kat", kat, "provjeri"),
              treba=[os.path.join(kat, "zamjerke.json")]),
        Korak("originalnost", "preklapanje s ingestiranim izvorima",
              _k("originality_check.py", rad, "--evidence", evidence,
                 "--json", os.path.join(kat, "originality.json")),
              treba=[rad, evidence], blokira=False),
        Korak("literatura", "popis literature protiv kućnog stila",
              _k("provjeri_literaturu.py", rad, "--profil", profil,
                 "--json", os.path.join(kat, "literatura.json")),
              treba=[rad, profil],
              zasto="oblik bibliografske jedinice mentor vidi prvi"),
        Korak("prikazi", "slike i grafikoni: dpi, širina, omjer, pismo",
              _k("provjeri_prikaze.py", rad,
                 "--json", os.path.join(kat, "prikazi.json")),
              treba=[rad], blokira=False,
              zasto="grafikon skaliran nakon izvoza mijenja veličinu pisma u sebi"),
        Korak("reference", "brojevi stranica protiv stvarnog otiska",
              ["<RAD_DOCX>/scripts/provjeri_reference.py", pdf or "rad.pdf"],
              treba=[pdf] if pdf else ["rad.pdf"], satelit="rad-docx",
              zasto="dokument dosljedan sam sa sobom i dalje može imati sve brojeve krive"),
        Korak("rubrika", "gdje rad stoji prema kriterijima i što ga drži",
              _k("rubrika.py", "--kat", kat, "--opsirno",
                 "--json", os.path.join(kat, "rubrika.json")),
              blokira=False,
              zasto="ide ZADNJI: agregira artefakte koje su prethodni koraci upravo napisali"),
    ]


def _razrijesi_satelit(korak: Korak) -> tuple[list[str] | None, str]:
    korijen = vjestine.nadi_vjestinu(korak.satelit)
    if not korijen:
        return None, (f"satelit `{korak.satelit}` nije instaliran — "
                      f"ograničenje se upisuje u projekt, ne prešućuje")
    rel = korak.argv[0].split("/", 1)[1]
    put = os.path.join(korijen, rel)
    if not os.path.exists(put):
        return None, f"`{korak.satelit}` nema {rel} — treba ponovna instalacija"
    return [sys.executable, put, *korak.argv[1:]], ""


def pokreni(korak: Korak, cwd: str, suho: bool) -> dict:
    argv, poruka = korak.argv, ""
    if korak.satelit:
        argv, poruka = _razrijesi_satelit(korak)
        if argv is None:
            return {"korak": korak.kid, "naziv": korak.naziv, "stanje": PRESKOCENO,
                    "blokira": korak.blokira, "razlog": poruka, "naredba": None}

    fale = [t for t in korak.treba if t and not os.path.exists(t)]
    if fale:
        return {"korak": korak.kid, "naziv": korak.naziv, "stanje": PRESKOCENO,
                "blokira": korak.blokira,
                "razlog": "nema ulaza: " + ", ".join(os.path.relpath(f, cwd) for f in fale),
                "naredba": " ".join(shlex.quote(a) for a in argv)}

    naredba = " ".join(shlex.quote(a) for a in argv)
    if suho:
        return {"korak": korak.kid, "naziv": korak.naziv, "stanje": "planirano",
                "blokira": korak.blokira, "naredba": naredba, "razlog": korak.zasto}

    try:
        r = subprocess.run(argv, cwd=cwd, capture_output=True, text=True, timeout=900)
    except subprocess.TimeoutExpired:
        return {"korak": korak.kid, "naziv": korak.naziv, "stanje": PUKAO,
                "blokira": korak.blokira, "kod": None, "naredba": naredba,
                "razlog": "provjera nije završila u 15 minuta"}
    except OSError as e:
        return {"korak": korak.kid, "naziv": korak.naziv, "stanje": PUKAO,
                "blokira": korak.blokira, "kod": None, "naredba": naredba,
                "razlog": str(e)}

    kod = r.returncode
    if kod == 0:
        stanje = OK
    elif kod == 1:
        stanje = NALAZ
    elif korak.satelit and kod in (3, 4):
        stanje = PRESKOCENO
    else:
        stanje = PUKAO
    izlaz = (r.stdout or "").strip()
    grijeh = (r.stderr or "").strip()
    return {"korak": korak.kid, "naziv": korak.naziv, "stanje": stanje,
            "blokira": korak.blokira, "kod": kod, "naredba": naredba,
            "razlog": korak.zasto,
            "izlaz": izlaz[-4000:], "greska": grijeh[-2000:]}


def _bitni_redci(izlaz: str, koliko: int = 8) -> list[str]:
    """Redci nalaza, ne zadnjih N redaka izlaza.

    Rep izlaza je gotovo uvijek sažetak i uputa, a sam nalaz stoji iznad njega —
    pa je „zadnjih šest redaka" pouzdano odsijecalo baš ono zbog čega je korak
    pao. Prednost imaju redci koji nose oznaku kršenja ili upozorenja.
    """
    redci = [r.rstrip() for r in izlaz.splitlines() if r.strip()]
    oznaceni = [r for r in redci if r.lstrip().startswith(("❌", "⚠️", "💥"))]
    izabrani = oznaceni or redci[-koliko:]
    izrezano = len(izabrani) - koliko
    izabrani = izabrani[:koliko]
    if izrezano > 0:
        izabrani.append(f"… još {izrezano} redaka — pokreni naredbu izravno")
    return izabrani


def _tablica(rezultati: list[dict], faza: str, suho: bool) -> None:
    naslov = f"GATE — faza {faza}" + (" (suhi prolaz)" if suho else "")
    print(naslov)
    print("=" * len(naslov))
    for r in rezultati:
        znak = "·" if r["stanje"] == "planirano" else ZNAK.get(r["stanje"], "?")
        tezina = "blokira" if r["blokira"] else "savjet"
        print(f"{znak} {r['naziv']:<52} {tezina}")
        if r["stanje"] in (PRESKOCENO, PUKAO, "planirano") and r.get("razlog"):
            print(f"     {r['razlog']}")
        if r["stanje"] == PUKAO and r.get("greska"):
            prva = r["greska"].splitlines()[0][:200]
            print(f"     stderr: {prva}")
        if r["stanje"] == NALAZ and r.get("izlaz"):
            for redak in _bitni_redci(r["izlaz"]):
                print(f"     {redak}")


def zakljucak(rezultati: list[dict]) -> tuple[int, dict]:
    br = lambda s: sum(1 for r in rezultati if r["stanje"] == s)  # noqa: E731
    blokirajuci = [r for r in rezultati
                   if r["blokira"] and r["stanje"] in (NALAZ, PUKAO)]
    sazetak = {
        "ok": br(OK), "nalaz": br(NALAZ), "preskoceno": br(PRESKOCENO),
        "pukao": br(PUKAO),
        "blokira": [r["korak"] for r in blokirajuci],
    }
    return (1 if blokirajuci else 0), sazetak


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        description="Pokreni sve propisane provjere za jednu fazu rada, redom.")
    ap.add_argument("--faza", required=True, choices=FAZE)
    ap.add_argument("--rad", default="./rad.docx")
    ap.add_argument("--pdf")
    ap.add_argument("--profil", default="./.katedra/resolved_profile.json")
    ap.add_argument("--tip")
    ap.add_argument("--project-root", dest="project_root")
    ap.add_argument("--kat")
    ap.add_argument("--json", dest="kao_json", metavar="PUT",
                    help="zapiši puni izvještaj")
    ap.add_argument("--suho", action="store_true",
                    help="ispiši što bi se pokrenulo, bez pokretanja")
    args = ap.parse_args(argv)

    korijen = context.resolve_project_root(args.project_root)
    kat = context.resolve_state_dir(args.kat, args.project_root)
    c = {
        "rad": os.path.abspath(os.path.join(korijen, args.rad))
        if not os.path.isabs(args.rad) else args.rad,
        "pdf": (os.path.abspath(os.path.join(korijen, args.pdf))
                if args.pdf and not os.path.isabs(args.pdf) else args.pdf),
        "profil": os.path.abspath(os.path.join(korijen, args.profil))
        if not os.path.isabs(args.profil) else args.profil,
        "tip": args.tip,
        "kat": kat,
    }

    rezultati = [pokreni(k, korijen, args.suho) for k in koraci(args.faza, c)]
    _tablica(rezultati, args.faza, args.suho)

    if args.suho:
        return 0

    kod, s = zakljucak(rezultati)
    print(f"\n{s['ok']} prošlo · {s['nalaz']} nalaza · "
          f"{s['preskoceno']} preskočeno · {s['pukao']} alat pukao")
    if s["pukao"]:
        print("💥 alat koji je pukao NIJE provjera koja je prošla — "
              "riješi to prije nego zaključiš da je faza čista.")
    if s["preskoceno"]:
        print("➖ preskočeno je ograničenje projekta: upiši ga u stanje, ne prešuti "
              "(željezno pravilo 8).")
    if kod:
        print(f"❌ blokira: {', '.join(s['blokira'])}")
    else:
        print("✅ nijedna blokirajuća provjera nije pala.")

    if args.kao_json:
        context.atomic_write_json(
            os.path.abspath(os.path.join(korijen, args.kao_json)),
            {"faza": args.faza, "kad": datetime.now().isoformat(timespec="seconds"),
             "sazetak": s, "koraci": rezultati})
    return kod


if __name__ == "__main__":
    sys.exit(main())
