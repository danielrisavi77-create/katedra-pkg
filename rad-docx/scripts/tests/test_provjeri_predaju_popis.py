#!/usr/bin/env python3
"""rad-docx kvarovi 28 i 29: lažni nalazi provjeri_predaju.py na urednom radu.

Sintetički dokument, bez privatnog rukopisa. Povod: seminarski rad (Libertas,
10. 11. 2026.) s numeriranim naslovom „9. POPIS TABLICA" i proredom 1,5
zadanim u stilu Normal, ne na svakom odlomku.
"""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from docx import Document
from docx.shared import Pt

SKRIPTA = Path(__file__).resolve().parents[1] / "provjeri_predaju.py"


def napravi(put, naslov_popisa="9. POPIS TABLICA", prored_u_stilu=True, prored_na_odlomku=None):
    d = Document()
    if prored_u_stilu:
        d.styles["Normal"].paragraph_format.line_spacing = 1.5
    d.add_heading("1. UVOD", level=1)
    for i in range(6):
        p = d.add_paragraph(f"Odlomak tijela broj {i + 1} s dovoljno teksta da ga ograda tijela uzme u mjerenje proreda.")
        if prored_na_odlomku is not None:
            p.paragraph_format.line_spacing = prored_na_odlomku
    for n, ime in ((1, "Prva tablica"), (2, "Druga tablica")):
        d.add_paragraph(f"Tablica {n}. {ime}", style="Caption")
        t = d.add_table(rows=2, cols=2)
        t.cell(0, 0).text, t.cell(0, 1).text = "A", "B"
        t.cell(1, 0).text, t.cell(1, 1).text = "1", "2"
        d.add_paragraph("Izvor: izrada autorice")
    d.add_heading("8. LITERATURA", level=1)
    d.add_paragraph("Autor, A. (2020.) Naslov. Zagreb: Nakladnik.")
    d.add_heading(naslov_popisa, level=1)
    d.add_paragraph("Tablica 1. Prva tablica\t3")
    d.add_paragraph("Tablica 2. Druga tablica\t4")
    d.save(put)


def pokreni(docx_put, profil):
    r = subprocess.run([sys.executable, str(SKRIPTA), str(docx_put), "--profil", str(profil)],
                       capture_output=True, text=True, encoding="utf-8")
    return r.returncode, r.stdout + r.stderr


class Kvar28NumeriraniPopis(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.profil = self.tmp / "profil.json"
        self.profil.write_text(json.dumps({"format": {"prored": 1.5}}), encoding="utf-8")

    def test_numerirani_naslov_popisa_nije_tijelo(self):
        put = self.tmp / "numeriran.docx"
        napravi(put, "9. POPIS TABLICA")
        kod, izlaz = pokreni(put, self.profil)
        self.assertNotIn("nije neprekinuta", izlaz, izlaz)
        self.assertNotIn("popis prikaza nije nađen", izlaz, izlaz)

    def test_nenumerirani_naslov_i_dalje_radi(self):
        put = self.tmp / "nenumeriran.docx"
        napravi(put, "POPIS TABLICA")
        kod, izlaz = pokreni(put, self.profil)
        self.assertNotIn("nije neprekinuta", izlaz, izlaz)

    def test_stvarna_rupa_se_i_dalje_hvata(self):
        # negativna kontrola: popis s 1 stavkom, tijelo s 2 → mora pasti
        put = self.tmp / "rupa.docx"
        napravi(put, "9. POPIS TABLICA")
        d = Document(put)
        zadnji = d.paragraphs[-1]
        zadnji._p.getparent().remove(zadnji._p)
        d.save(put)
        kod, izlaz = pokreni(put, self.profil)
        self.assertIn("popis prikaza ne odgovara tijelu", izlaz, izlaz)
        self.assertEqual(kod, 1)


class Kvar29ProredUStilu(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.profil = self.tmp / "profil.json"
        self.profil.write_text(json.dumps({"format": {"prored": 1.5}}), encoding="utf-8")

    def test_prored_iz_stila_se_vidi(self):
        put = self.tmp / "stil.docx"
        napravi(put, prored_u_stilu=True)
        kod, izlaz = pokreni(put, self.profil)
        self.assertNotIn("prored nije zadan", izlaz, izlaz)
        self.assertNotIn("prored je", izlaz, izlaz)

    def test_krivi_prored_u_stilu_se_hvata(self):
        # negativna kontrola: stil kaže 1,0 → mora biti greška, ne tišina
        put = self.tmp / "krivi.docx"
        napravi(put, prored_u_stilu=False)
        d = Document(put)
        d.styles["Normal"].paragraph_format.line_spacing = 1.0
        d.save(put)
        kod, izlaz = pokreni(put, self.profil)
        self.assertIn("prored je 1,00, profil traži 1,5", izlaz, izlaz)

    def test_odlomak_ima_prednost_pred_stilom(self):
        put = self.tmp / "odlomak.docx"
        napravi(put, prored_u_stilu=True, prored_na_odlomku=1.0)
        kod, izlaz = pokreni(put, self.profil)
        self.assertIn("prored je 1,00", izlaz, izlaz)


if __name__ == "__main__":
    unittest.main(verbosity=2)
