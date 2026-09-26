#!/usr/bin/env python3
"""Ograda kvara 178: provjeri_sudar_kvarova.py mora vidjeti isti broj s drugim naslovom."""
import os
import subprocess
import sys
import tempfile

TU = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(TU))
import provjeri_sudar_kvarova as P  # noqa: E402

SVE, PALO = 0, 0


def check(naziv, uvjet, detalj=""):
    global SVE, PALO
    SVE += 1
    if uvjet:
        print(f"  ✓        {naziv}")
    else:
        PALO += 1
        print(f"  ✗ FAIL   {naziv}")
        if detalj != "":
            print(f"           detalj: {detalj}")


BAZA = "# K\n\n## 1. prvi\n\ntekst\n\n## 2–3. raspon\n\ntekst\n\n## 4. četvrti\n"

check("R-S1: isti broj, isti naslov nije sudar", P.sudari(BAZA, BAZA) == [])
check("R-S2: novi broj iznad baze nije sudar",
      P.sudari(BAZA, BAZA + "\n## 5. peti\n") == [])
s = P.sudari(BAZA, BAZA.replace("## 4. četvrti", "## 4. nešto drugo"))
check("R-S3: isti broj, drugi naslov JEST sudar", [n for n, _, _ in s] == [4], s)
s = P.sudari(BAZA, BAZA + "\n## 3. tuđi\n")
check("R-S4: broj unutar raspona u bazi (2–3) s drugim naslovom JEST sudar", 3 in [n for n, _, _ in s], s)
check("R-S5: CRLF u grani nije razlika u naslovu",
      P.sudari(BAZA, BAZA.replace("\n", "\r\n")) == [])

# CLI nad pravim git repoom: baza na main, grana dodaje sudarajući broj
d = tempfile.mkdtemp()
env = dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t",
           GIT_COMMITTER_EMAIL="t@t")


def git(*a):
    return subprocess.run(["git", "-C", d, *a], capture_output=True, text=True, encoding="utf-8",
                          errors="replace", env=env)


git("init", "-q", "-b", "main")
os.makedirs(os.path.join(d, "katedra-lite", "references"))
kat = os.path.join(d, "katedra-lite", "references", "zamke.md")
with open(kat, "w", encoding="utf-8", newline="\n") as f:
    f.write(BAZA)
git("add", "-A")
git("commit", "-q", "-m", "baza")
with open(kat, "a", encoding="utf-8", newline="\n") as f:
    f.write("\n## 4. drugi četvrti\n")
skripta = os.path.join(os.path.dirname(TU), "provjeri_sudar_kvarova.py")


def cli(*a):
    return subprocess.run([sys.executable, "-B", skripta, "--korijen", d, *a], capture_output=True,
                          text=True, encoding="utf-8", errors="replace",
                          env=dict(os.environ, PYTHONIOENCODING="utf-8"))


r = cli("--baza", "main")
check("R-S6: CLI nad radnim stablom sa sudarom vraća 1 i predlaže prvi slobodan broj (5)",
      r.returncode == 1 and "od 5" in r.stdout, (r.returncode, r.stdout[-200:]))
r = cli("--baza", "nepostoji")
check("R-S7: nedostupna baza je 2 (neizmjereno), ne 0", r.returncode == 2, (r.returncode, r.stdout))

print("=" * 70)
print("REZULTATI TESTOVA: %d/%d prošlo" % (SVE - PALO, SVE))
print("=" * 70)
sys.exit(1 if PALO else 0)
