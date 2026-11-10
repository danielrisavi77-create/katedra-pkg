#!/usr/bin/env python3
"""katedra-lite kvar 180: neadmitiran profil na disku ne smije se javiti kao „nema profila"."""
from pathlib import Path
import subprocess
import sys
import unittest

SCRIPTS = Path(__file__).resolve().parents[1]
FAK = SCRIPTS.parent / "references" / "fakulteti"


def resolver(*args):
    r = subprocess.run([sys.executable, str(SCRIPTS / "profile_resolver.py"), *args],
                       capture_output=True, text=True, encoding="utf-8")
    return r.returncode, r.stdout + r.stderr


class Kvar180NeadmitiranProfil(unittest.TestCase):
    def test_libertas_postoji_a_nije_admitiran(self):
        self.assertTrue((FAK / "libertas.json").exists())
        kod, izlaz = resolver("--fakultet", "libertas", "--tip", "seminarski")
        self.assertNotEqual(kod, 0)
        self.assertIn("nije admitiran", izlaz, izlaz)
        self.assertIn("--profil-datoteka", izlaz, izlaz)
        self.assertIn("libertas.json", izlaz, izlaz)

    def test_alias_vodi_na_isti_savjet(self):
        kod, izlaz = resolver("--fakultet", "Libertas međunarodno sveučilište", "--tip", "seminarski")
        self.assertIn("nije admitiran", izlaz, izlaz)

    def test_nepostojeci_fakultet_i_dalje_nema_profila(self):
        kod, izlaz = resolver("--fakultet", "nepostojeci-fakultet-xyz", "--tip", "seminarski")
        self.assertNotEqual(kod, 0)
        self.assertIn("nema profila/rute", izlaz, izlaz)

    def test_admitirani_i_dalje_prolazi(self):
        kod, izlaz = resolver("--fakultet", "fpzg", "--tip", "diplomski", "--json")
        self.assertEqual(kod, 0, izlaz)

    def test_savjet_radi(self):
        kod, izlaz = resolver("--fakultet", "libertas", "--tip", "seminarski",
                              "--profil-datoteka", str(FAK / "libertas.json"), "--json")
        self.assertEqual(kod, 0, izlaz)


if __name__ == "__main__":
    unittest.main(verbosity=2)
