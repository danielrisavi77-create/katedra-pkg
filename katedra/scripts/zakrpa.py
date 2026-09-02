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


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--par", action="append", required=True,
                    metavar="IME:IZVORNI:IZMIJENJENI")
    ap.add_argument("--izlaz", required=True)
    ap.add_argument("--naslov", default="Zakrpa")
    a = ap.parse_args()

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
