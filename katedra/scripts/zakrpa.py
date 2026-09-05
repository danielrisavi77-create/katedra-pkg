# -*- coding: utf-8 -*-
"""Zakrpa: samo promijenjene datoteke, s uputama i sigurnosnom kopijom.

Zašto ne puni paket
-------------------
Na jednoj stvarnoj izmjeni od 10 datoteka puni je paket imao 203 datoteke i
1,1 MB, a zakrpa 19 datoteka i 145 KB. Uz to puni paket prepisuje i ono što
nitko nije tražio da se mijenja, a kad se ime skilla poklopi — i cijelu tuđu
instalaciju.

Uporaba
-------
    python3 zakrpa.py --izlaz zakrpa/ \\
        --par katedra-lite:/put/baseline/katedra:/put/rad/katedra-lite \\
        --par rad-docx:/put/baseline/rad-docx:/put/rad/rad-docx

`--par IME:IZVORNI:IZMIJENJENI` može se ponoviti. IZVORNI je verzija od koje se
kreće (instalirana ili preuzeta), IZMIJENJENI je ona s izmjenama. IME je ime pod
kojim skill živi na odredištu — ne mora biti isto kao ime mape.

Izlaz je mapa spremna za zip: po jedna podmapa za svaki skill, `UPUTE.md` s
tablicom promjena i `primijeni.sh` koji radi sigurnosnu kopiju svake prepisane
datoteke.
"""
import argparse
import re
import subprocess
import json
import filecmp
import os
import pathlib
import shutil
import sys

PRESKOCI = {"__pycache__", ".git", ".DS_Store"}

PRIMIJENI = r"""#!/usr/bin/env bash
# Primjenjuje zakrpu na postojeću instalaciju skillova.
# Ne briše ništa: svaku datoteku koju prepisuje prvo kopira u .bak-<vrijeme>.
set -euo pipefail

ODREDISTE="${1:-}"
if [ -z "$ODREDISTE" ]; then
  for k in "$HOME/.claude/skills/synced" "$HOME/.claude/skills" "/root/.claude/skills/synced"; do
    [ -d "$k" ] && ODREDISTE="$k" && break
  done
fi
if [ -z "$ODREDISTE" ] || [ ! -d "$ODREDISTE" ]; then
  echo "Ne nalazim mapu sa skillovima." >&2
  echo "Uporaba: bash primijeni.sh /put/do/skills" >&2
  exit 1
fi

IZVOR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PECAT="$(date +%Y%m%d-%H%M%S)"
novih=0; zamijenjenih=0; preskocenih=0

for skill in __SKILLOVI__; do
  [ -d "$IZVOR/$skill" ] || continue
  if [ ! -d "$ODREDISTE/$skill" ]; then
    echo "⚠ preskačem $skill — nije instaliran u $ODREDISTE"
    preskocenih=$((preskocenih+1))
    continue
  fi
  while IFS= read -r rel; do
    src="$IZVOR/$skill/$rel"; dst="$ODREDISTE/$skill/$rel"
    mkdir -p "$(dirname "$dst")"
    if [ -f "$dst" ]; then
      if cmp -s "$src" "$dst"; then echo "   = $skill/$rel (već jednako)"; continue; fi
      cp -p "$dst" "$dst.bak-$PECAT"; cp "$src" "$dst"
      echo "   ~ $skill/$rel   (kopija: $(basename "$dst").bak-$PECAT)"
      zamijenjenih=$((zamijenjenih+1))
    else
      cp "$src" "$dst"; echo "   + $skill/$rel"; novih=$((novih+1))
    fi
  done < <(cd "$IZVOR/$skill" && find . -type f | sed 's|^\./||' | sort)
done

echo
echo "Gotovo: $novih novih, $zamijenjenih zamijenjenih, $preskocenih preskočenih skillova."
echo "Odredište: $ODREDISTE"
"""


def datoteke(korijen):
    korijen = pathlib.Path(korijen)
    for put in korijen.rglob("*"):
        if not put.is_file():
            continue
        if any(d in PRESKOCI for d in put.relative_to(korijen).parts):
            continue
        yield put.relative_to(korijen).as_posix()


def razlika(izvorni, izmijenjeni):
    """(nove, promijenjene, obrisane) relativne putanje."""
    a, b = set(datoteke(izvorni)), set(datoteke(izmijenjeni))
    nove = sorted(b - a)
    obrisane = sorted(a - b)
    promijenjene = sorted(
        r for r in (a & b)
        if not filecmp.cmp(os.path.join(izvorni, r), os.path.join(izmijenjeni, r), shallow=False))
    return nove, promijenjene, obrisane



# ---------------------------------------------------------------------------
# --provjeri-tvrdnje: SKILL.md ne smije tvrditi ono što kod ne radi.
#
# Povod (rad-audit, rujan 2026.): SKILL.md je opisivao Vancouver dijalekt kao
# gotov i dokazan — "common.detect_citation_style sada zna vancouver",
# "Mjereno: kritično 1 → 0, 78/78 testova", sposobnost hr.citations.vancouver.v1
# "potvrđena izvođenjem". U kodu: nula pojava riječi vancouver, testova nema,
# suite ima 63 testa, manifest tu sposobnost ne sadrži. Opis je napisan, kod nije.
# Drugi slučaj istog mehanizma (prvi: kvar 36), pa prestaje biti kvar i postaje
# provjera koja se pokreće prije svake zakrpe.
# ---------------------------------------------------------------------------

SPOSOBNOST_RE = re.compile(r"`([a-z][\w.\-]*\.v\d+)`")
TESTOVI_RE = re.compile(r"(\d+)\s*/\s*(\d+)\s+testova")
KVAR_RE = re.compile(r"\*\*(R\d+)\s*[—-]")


def provjeri_tvrdnje(korijen):
    """Vraća popis nalaza (str). Prazan popis = SKILL.md i kod se slažu."""
    # Apsolutni put je obavezan: test suite se pokreće s `cwd` u `scripts/tests`,
    # pa bi relativan korijen ondje pokazivao u prazno. Alat je tada ispisivao
    # „suite se ne može pokrenuti" i obarao provjeru tvrdnji na vlastitom rukovanju
    # putovima — lažni ❌ iz alata koji upravo lovi tvrdnje bez pokrića.
    korijen = pathlib.Path(korijen).resolve()
    skill_md = korijen / "SKILL.md"
    if not skill_md.exists():
        return [f"❌ nema {skill_md}"]
    md = skill_md.read_text(encoding="utf-8")
    nalazi = []

    # 1) sposobnosti spomenute u SKILL.md naspram manifesta
    manifesti = list(korijen.glob("scripts/engine_contract.json"))
    if manifesti:
        man = json.loads(manifesti[0].read_text(encoding="utf-8"))
        u_manifestu = set(man.get("capabilities", []))
        u_opisu = set(SPOSOBNOST_RE.findall(md))
        for c in sorted(u_opisu - u_manifestu):
            nalazi.append(f"❌ SKILL.md spominje sposobnost `{c}`, manifest je NEMA")
        for c in sorted(u_manifestu - u_opisu):
            nalazi.append(f"⚠ manifest nosi `{c}`, SKILL.md je ne spominje")

    # 2) tvrdnja "N/M testova" naspram stvarnog broja testova
    testovi = korijen / "scripts" / "tests" / "test_all.py"
    stvarno = None
    if testovi.exists():
        r = subprocess.run([sys.executable, str(testovi)], capture_output=True,
                           text=True, cwd=str(testovi.parent), timeout=600)
        m = re.search(r"REZULTATI TESTOVA:\s*(\d+)\s*/\s*(\d+)", r.stdout)
        if m:
            stvarno = (int(m.group(1)), int(m.group(2)))
            if stvarno[0] != stvarno[1]:
                nalazi.append(f"❌ testovi ne prolaze: {stvarno[0]}/{stvarno[1]}")
    for m in TESTOVI_RE.finditer(md):
        tvrdi = (int(m.group(1)), int(m.group(2)))
        if stvarno is None:
            nalazi.append(f"❌ SKILL.md tvrdi {tvrdi[0]}/{tvrdi[1]} testova, a suite se ne može pokrenuti")
        elif tvrdi[1] > stvarno[1]:
            nalazi.append(f"❌ SKILL.md tvrdi {tvrdi[0]}/{tvrdi[1]} testova, suite ima {stvarno[1]}")

    # 3) svaki kvar R<N> opisan u SKILL.md mora imati test-skupinu "R<N>:"
    if testovi.exists():
        t = testovi.read_text(encoding="utf-8")
        for oznaka in sorted(set(KVAR_RE.findall(md))):
            if f'"{oznaka}:' not in t and f"'{oznaka}:" not in t:
                nalazi.append(f"❌ SKILL.md opisuje {oznaka}, a testova s oznakom {oznaka}: nema")

    return nalazi


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--par", action="append", metavar="IME:IZVORNI:IZMIJENJENI")
    ap.add_argument("--izlaz")
    ap.add_argument("--naslov", default="Zakrpa")
    ap.add_argument("--provjeri-tvrdnje", metavar="KORIJEN_SKILLA",
                    help="usporedi tvrdnje iz SKILL.md sa stanjem koda i testova")
    a = ap.parse_args()

    if a.provjeri_tvrdnje:
        nalazi = provjeri_tvrdnje(a.provjeri_tvrdnje)
        print("=" * 62)
        print("PROVJERA TVRDNJI —", a.provjeri_tvrdnje)
        print("=" * 62)
        for n in nalazi:
            print(" ", n)
        tvrdo = [n for n in nalazi if n.startswith("❌")]
        print("\nREZULTAT:", "✓ SKILL.md i kod se slažu" if not tvrdo
              else f"❌ {len(tvrdo)} tvrdnja bez pokrića u kodu")
        return 1 if tvrdo else 0

    if not a.par or not a.izlaz:
        sys.exit("❌ --par i --izlaz su obavezni kad se gradi zakrpa")

    izlaz = pathlib.Path(a.izlaz)
    if izlaz.exists():
        shutil.rmtree(izlaz)
    izlaz.mkdir(parents=True)

    redci, imena, upozorenja = [], [], []
    ukupno = 0
    for par in a.par:
        try:
            ime, izvorni, izmijenjeni = par.split(":", 2)
        except ValueError:
            sys.exit(f"❌ --par mora biti IME:IZVORNI:IZMIJENJENI, dobio: {par}")
        for d in (izvorni, izmijenjeni):
            if not os.path.isdir(d):
                sys.exit(f"❌ nema mape: {d}")

        nove, promijenjene, obrisane = razlika(izvorni, izmijenjeni)
        if obrisane:
            upozorenja.append(
                f"`{ime}`: {len(obrisane)} datoteka postoji u izvornoj, a nema ih u "
                "izmijenjenoj verziji. Zakrpa NE briše — ako ih treba maknuti, reci to "
                "izrijekom u uputama: " + ", ".join(obrisane[:6]))
        if not nove and not promijenjene:
            upozorenja.append(f"`{ime}`: nema razlike, preskočeno")
            continue

        imena.append(ime)
        for rel in nove + promijenjene:
            odrediste = izlaz / ime / rel
            odrediste.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(os.path.join(izmijenjeni, rel), odrediste)
            redci.append((ime, rel, "novo" if rel in nove else "mijenjano"))
        ukupno += len(nove) + len(promijenjene)

    if not imena:
        sys.exit("❌ nijedan par nema razliku — nema što pakirati")

    tablica = "\n".join(
        f"| `{ime}/{rel}` | {'**novo**' if v == 'novo' else 'mij.'} |  |"
        for ime, rel, v in redci)
    upute = f"""# {a.naslov}

Samo promijenjene i nove datoteke. Ukupno **{ukupno}** u {len(imena)} skilla.

## Primjena

```bash
bash primijeni.sh /put/do/skills
```

Skripta pravi sigurnosnu kopiju svake datoteke koju prepisuje
(`ime.bak-RRRRMMDD-HHMMSS`) i ispisuje što je napravila. Bez argumenta traži
`~/.claude/skills/synced`. Ručno kopiranje mapa preko postojećih jednako je dobro —
nijedna datoteka se ne briše, samo dodaje ili zamjenjuje.

## Što je gdje

| Datoteka | Novo? | Zašto |
|---|---|---|
{tablica}

> Stupac „Zašto” popuni rukom prije slanja. Zakrpa bez razloga po stavci tjera
> primatelja da čita diff.

## Provjera nakon primjene

> Dopiši naredbe kojima se vidi da je zakrpa sjela.
"""
    if upozorenja:
        upute += "\n## Upozorenja\n\n" + "\n".join(f"- {u}" for u in upozorenja) + "\n"
    (izlaz / "UPUTE.md").write_text(upute, encoding="utf-8")

    sh = PRIMIJENI.replace("__SKILLOVI__", " ".join(imena))
    (izlaz / "primijeni.sh").write_text(sh, encoding="utf-8")
    os.chmod(izlaz / "primijeni.sh", 0o755)

    print("=" * 72)
    print(f"ZAKRPA — {izlaz}")
    print("=" * 72)
    for ime in imena:
        n = sum(1 for i, _, _ in redci if i == ime)
        print(f"  {ime}: {n} datoteka")
    print(f"\n✔ {ukupno} datoteka + UPUTE.md + primijeni.sh")
    for u in upozorenja:
        print(f"⚠ {u}")
    print("\nPopuni stupac \u201eZašto\u201d u UPUTE.md prije slanja.")


if __name__ == "__main__":
    main()
