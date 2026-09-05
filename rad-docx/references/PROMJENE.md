# PROMJENE — rad-docx

# v1.9.3 — provjera koja nije postojala i greška koja to nije

* **Kvar 24 — `str(None)` je niska „None".** Kad prored nigdje nije zadan, `_prevladava`
  vraća `None`, a `str(None)` je istinita niska bez `AUTO`/`POINT`/`MULTIPLE`, pa je grana
  za fiksni prored okidala GREŠKU „prored je fiksan (None)" i zaustavljala predaju. Poruka
  je bila obrnuta od istine, a isti ispis je paralelno nosio točan nalaz kao upozorenje.
  Mjereno: `❌ GREŠKE (1)` → `✅ nijedna greška`, uz zadržano upozorenje. Pogađa svaki
  dokument sastavljen nad tuđim predloškom, jer takav prored nasljeđuje.
* **Kvar 25 i `scripts/provjeri_reference.py`** (novo) — skripta se zove na osam mjesta u
  `katedra-lite` i vodi kao blokirajuća u `gate.py --faza predaja`, a u paketu je nije bilo;
  gate je javljao „treba ponovna instalacija", što je kriva dijagnoza nad potpunim paketom.
  Skripta uspoređuje keširane vrijednosti `PAGEREF` polja iz `.docx`-a sa stvarnim
  prijelomom iz PDF-a. Dokazano na oba smjera: 27/27 točno → izlazni kod 0; isti dokument s
  jednim namjerno pokvarenim brojem → `❌ tvrdi 7 · otisak 1` i izlazni kod 1. Izlazni kod 2
  znači „nije se dalo izmjeriti" i nije isto što i prolaz.
