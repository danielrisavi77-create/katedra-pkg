# PROMJENE — rad-docx

# v2.4.3 — dva lažna nalaza u provjeri predaje (Libertas seminarski, 10. 11. 2026.)

* **Kvar 28 — naslov popisa s rednim brojem.** Granica popisnog dijela dopušta „9. POPIS TABLICA" (kao što `KRAJ_TIJELA` već dopušta „8. LITERATURA"). Stvarni rad: `❌ GREŠKE (1)` → `✅ nijedna greška`. Granica: provjerava se samo tekst naslova, ne stil.
* **Kvar 29 — efektivni prored.** `_efektivno()` razrješava odlomak → stil → bazni stil → `pPrDefault`. Upozorenje „prored nije zadan" na radu s 1,5 u stilu nestaje; krivi prored u stilu sada je greška. Ograda `scripts/tests/test_provjeri_predaju_popis.py` (6 testova, baseline 2/6).

# v1.9.3 — provjera koja nije postojala i greška koja to nije

* **Kvar 25 — `str(None)` je niska „None".** Kad prored nigdje nije zadan, `_prevladava`
  vraća `None`, a `str(None)` je istinita niska bez `AUTO`/`POINT`/`MULTIPLE`, pa je grana
  za fiksni prored okidala GREŠKU „prored je fiksan (None)" i zaustavljala predaju. Poruka
  je bila obrnuta od istine, a isti ispis je paralelno nosio točan nalaz kao upozorenje.
  Mjereno: `❌ GREŠKE (1)` → `✅ nijedna greška`, uz zadržano upozorenje. Pogađa svaki
  dokument sastavljen nad tuđim predloškom, jer takav prored nasljeđuje.
* **Kvar 26 i `scripts/provjeri_reference.py`** (novo) — skripta se zove na osam mjesta u
  `katedra-lite` i vodi kao blokirajuća u `gate.py --faza predaja`, a u paketu je nije bilo;
  gate je javljao „treba ponovna instalacija", što je kriva dijagnoza nad potpunim paketom.
  Skripta uspoređuje keširane vrijednosti `PAGEREF` polja iz `.docx`-a sa stvarnim
  prijelomom iz PDF-a. Dokazano na oba smjera: 27/27 točno → izlazni kod 0; isti dokument s
  jednim namjerno pokvarenim brojem → `❌ tvrdi 7 · otisak 1` i izlazni kod 1. Izlazni kod 2
  znači „nije se dalo izmjeriti" i nije isto što i prolaz.

---

## v1.9.5 — 5. 9. 2026.

**`provjeri_povratak.py` napisan.** `katedra-lite/references/povratak.md` i
`references/stil_autora.md` opisivali su cijeli mod 7 i imenovali ovu skriptu kao njegov
motor. Skripte nije bilo, pa se usporedba radila napamet. Alat dijeli razlike na tri
hrpe kako referenca propisuje: **vraćamo** (regresije koje je autor nehotice unio:
raspon `133–150 → 133-150`, hrvatski navodnici u ravne, `×` u `x`, izgubljen citat,
nestao obvezni dio), **pamtimo** (rečenica prepisana bez diranja citata i brojki — glas
autora), **pitamo** (promijenjena brojka ili citat, dodan i obrisan sadržaj).
Izlazni kod 1 na regresiju ili nestali obvezni dio.

**`provjeri_predaju.py` je sada korak gatea**, a ne naredba koje se agent morao sjetiti
(v. `katedra-lite/references/zamke.md`, kvar 60).

## 2026-09-23 — Delivery D kandidat: konačni bajtovi i vizualni dokaz

Dodani `scripts/delivery_integrity.py`, strogi manifesti i sintetičke regresije.
Odvojeni sadržajni paritet, geometrijski rizici, imenovani metadata scope i stvarni
render/pregled svih stranica. Bez implicitnog prihvaćanja revizija ili automatskog
vizualnog PASS-a. Potpun opis ograničenja: `references/delivery_integrity.md`.
