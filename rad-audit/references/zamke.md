# rad-audit — katalog kvarova

Format po `katedra/references/kvar.md`: naslov imenuje mehanizam, pa Simptom /
Uzrok / Popravak / Gdje, pa izlaz koji to pokazuje.

## 1. Dijalekt citiranja dokumentiran, a nije napisan (Vancouver `(N)`)

**Simptom.** Diplomski rad HKS-a, Fakultet zdravstvenih studija (Danijela Stanić,
palijativna skrb), 75 referenci i 132 navoda oblika `(1)`, `(12,40)`:

```
[detektiran stil citiranja: unknown {'ieee': 0, 'authoryear': 0}]
⚠ Definirano u LITERATURI: (nije prepoznat popis — provjeri ručno)
Citirano u tekstu: 0
⚠ CITAT BEZ REFERENCE: [('recommendation', '2003')]      ← jedini KRITIČNI nalaz
```

Jedini crveni nalaz cijelog audita bio je lažan (nastao iz naslova reference
`Recommendation Rec(2003)24`), a svih 132 stvarnih navoda ostalo je neprovjereno.
Stvarna pogreška u radu — sedam citata koji krše rastući redoslijed prvog
pojavljivanja — nije prijavljena jer ta grana nikad nije došla do izvršavanja.

**Uzrok.** Dvostruki, i drugi je teži od prvoga:

1. `common.detect_citation_style` poznaje samo `[N]` i autor-godina. Numerički
   citat u ovalnoj zagradi (Vancouver/ICMJE, standard u biomedicini) ne postoji,
   pa rad ispada `unknown` i pokreću se **oba pogrešna** checkera.
2. `SKILL.md` je taj dijalekt opisivao kao **gotov i dokazan**: unos „R16 —
   Vancouver `(N)` dijalekt (rujan 2026., v1.9)" tvrdi „`common.detect_citation_style`
   sada zna `vancouver`", „Mjereno: kritično 1 → 0, popis 75/75, 78/78 testova",
   a §Sposobnosti navodi `hr.citations.vancouver.v1` kao potvrđen izvođenjem.
   Provjereno u kodu: `grep -c -i vancouver common.py check_citations.py` → `0` i `0`;
   `check_citations.py` prima samo `sys.argv[1]`; testova R16 nema; suite ima 63
   testa, ne 78; manifest **ne sadrži** `hr.citations.vancouver.v1`. Opis je
   napisan, kod nije.

Ovo je drugi slučaj istoga mehanizma (prvi: kvar 36, „zastavica dokumentirana
prije nego što je postojala"). Kad se ponovi, prestaje biti kvar i postaje
doktrina — v. popravak, dio 3.

**Popravak.**

1. `common.py`: `VANCOUVER_CITE_RE` + `find_vancouver_citations(text, u_tablici=False)`
   sa zaštitama nađenima na stvarnom radu — `53(3-4)` svezak(broj), `(2003)` godina,
   `158 (77,8)` n (%) u ćeliji tablice — i `LIT_HEADING_RE` proširen na
   „POPIS CITIRANE LITERATURE" i „Izvori i literatura". `detect_citation_style`
   vraća i `vancouver`.
2. `check_citations.py`: drugi argument `ieee|vancouver` (bez njega auto), popis
   referenci u Vancouveru se čita kao numerirana lista `^\s*(\d+)\.\s`, a provjera
   redoslijeda prvog pojavljivanja sada **ulazi u REZULTAT** (prije je bila samo
   ispis, pa je rad s prekršenim redoslijedom prolazio kao „interno konzistentno").
3. `generate_report.py` / `audit_all.py`: Vancouver faza se pokreće kad ima signala,
   ne na `mixed` bez brojača (inače pada R9).
4. Manifest: `hr.citations.vancouver.v1` dodan **tek sada**, uz devet testova.

**Zamka koju je popravak zamalo unio.** Prva verzija zaštite odbacivala je svaku
zagradu iza znamenke, pa je `korelacija iznosi 0,53 (21)` ispalo iz citata i
referenca 21 postala lažno siroče (78/79). Zaštita „broj + razmak" vrijedi samo u
**ćelijama tablica**; u prozi se odbacuje samo zagrada zalijepljena uz znamenku.

**Gdje.** `scripts/common.py`, `scripts/check_citations.py`,
`scripts/generate_report.py`, `scripts/audit_all.py`,
`scripts/tests/test_all.py` (skupina R16), `scripts/engine_contract.json`.

**Dokaz — crveno prije, zeleno poslije, isti dokument.**

```
PRIJE  (izvorne skripte, rad.docx)
  [detektiran stil: unknown {'ieee': 0, 'authoryear': 0}]
  ⚠ Definirano u LITERATURI: (nije prepoznat popis)
  Citirano u tekstu: 0
  izvještaj: kritično 1, srednje 13, kozmetičko 4     ← kritični nalaz je lažan

POSLIJE (zakrpa, isti rad.docx)
  [dijalekt: vancouver (auto) — {'ieee': 0, 'vancouver': 171, 'authoryear': 0}]
  Definirano u popisu: 75  (raspon 1–75), rupe: nema
  Citirano u tekstu: 75, siročad: nema, citat bez reference: nema
  ✓ prati redoslijed pojavljivanja
  izvještaj: kritično 0, srednje 7, kozmetičko 4

testovi: 63/63 → 72/72 (9 novih, R16)
```

## 2. Provjera redoslijeda prvog pojavljivanja ne ulazi u ocjenu

**Simptom.** Nakon dodavanja 35 novih navoda u Uvod i Raspravu istog rada,
redoslijed prvog pojavljivanja bio je `… 13, 40, 14, 29, 15 …` — sedam kršenja
Vancouver pravila, koje recenzent vidi odmah. Alat ih ne bi prijavio ni da je
dijalekt radio: `ok = defined and not orphans and not undefined` ne sadrži `viol`,
pa rad s prekršenim redoslijedom izlazi kao „✓ interno konzistentno".

**Uzrok.** Provjera je napisana kao ispis, ne kao nalaz. Sve što nije u `ok` ne
dolazi do `generate_report` bucketizacije i ne postoji za korisnika koji čita
samo sažetak.

**Popravak.** `ok = bool(defined) and not orphans and not undefined and not viol`,
uz ispis konkretnih mjesta kršenja (`viol[:10]`), a ne samo njihova broja.

**Gdje.** `scripts/check_citations.py`.

**Dokaz — fixture, crveno pa zeleno.** `red_lose.docx` (citati redom 1, 2, 5, 3, 4;
popis 1–5, bez siročadi i bez citata bez reference — dakle sve što stara ocjena
gleda je uredno):

```
PRIJE   ✓ interno konzistentno,  exit 0        ← rad s prekršenim redoslijedom prolazi
POSLIJE Redoslijed prvog pojavljivanja: [1, 2, 5, 3, 4]
        ⚠ krši rastući redoslijed na 2 mjesta: [3, 4]
        REZULTAT: ⚠ ima nalaza,  exit 1
red_dobro.docx (1, 2, 3, 4, 5):  ✓ interno konzistentno, exit 0
```

Na stvarnom radu: nakon dodavanja 35 navoda redoslijed je pucao na mjestima
5, 44, 35, 45, 43, 40, 41 i 42 (mjereno u četiri kruga, dok se nije zatvorio);
sve je nađeno ad-hoc skriptom jer alat tu granu nije vodio u ocjenu.

## 3. Domenska auto-detekcija nema biomedicinu, pa promašuje u tišini

**Simptom.** Isti rad (palijativna skrb, sestrinstvo):

```
domena (auto-detekcija): celik — čelične konstrukcije / građevinarstvo
  (bodovi: {'celik': 96, 'elektro': 12, 'strojarstvo': 4, 'it': 50})
⚠ 'stup' + %: 18, 28,1, 45,8, 50,7, 59, 63,5 — provjeri je li razlika deklarirana
PODSJETNIK: Σ(paneli×pokrivna širina) = površina krova ?
```

Rad o umiranju dobio je podsjetnik na aritmetiku krovnih panela, a „stup" je
došao iz „stupanj/stupca". Nalaz nije samo beskoristan nego troši pažnju koju
korisnik ima za pravi nalaz.

**Uzrok.** `domains/` ima celik, elektro, strojarstvo, it i generički fallback.
Biomedicinskog paketa nema, a generički fallback se ne uključuje jer neka
tehnička domena uvijek skupi bodove na općim riječima.

**Popravak (predložen, nije u ovoj zakrpi).** Paket `domains/biomed.py` s
ključnim riječima (bolesnik, skrb, ispitanik, upitnik, prevalencija, uzorak,
hi-kvadrat) i claim uzorcima za `n (%)`, `p`, `M ± SD`, KR-20/Cronbach; uz prag
ispod kojega se bira `generic` umjesto najbolje ocijenjene tehničke domene.

**Gdje.** `scripts/domains/`.

## 4. R14 opisan, a `HEADING_RE` i `_osnova` nepromijenjeni

**Simptom.** `HEADING_RE.search("Izvori i literatura")` → `False`;
`_osnova("lipskom")` → `{lipsk, lipskom}`, bez `lipsky`. SKILL.md je taj popravak
opisivao kao gotov od kolovoza 2026., s izmjerenom brojkom „lažni citat bez
reference 11 → 0".

**Uzrok.** Isti mehanizam kao kvar 1: unos u katalog napisan, kod nije. Nađeno tek
kad je `zakrpa.py --provjeri-tvrdnje` tražio test-skupinu `R14:` i nije je našao.

**Popravak.** `HEADING_RE` se u `check_citations_authoryear.py` više ne definira
lokalno nego se uvozi iz `common.LIT_HEADING_RE`, pa dva alata rade po jednom
rječniku naslova. `_osnova` uz goli korijen vraća i oblike sa završnim y/i/j/e.

**Gdje.** `scripts/check_citations_authoryear.py`, `scripts/common.py`,
`scripts/tests/test_all.py` (skupina R14).

**Dokaz.** Prije: 3 testa skupine R14 padaju. Poslije: prolaze; `Izvori i
literatura` i `POPIS CITIRANE LITERATURE` prepoznati, `lipskom` daje i `lipsky`.

## 5. R15 opisan, a toggle navodnika nepromijenjen

**Simptom.** `fix_quotes_by_paragraph` nad odlomkom
`Program „Neovisno življenje" i pojam "drugi navod"` vraća
`Program „Neovisno življenje„ i pojam ”drugi navod„` — točno kvar koji unos R15
opisuje kao popravljen („Mjereno: 11 otvarajućih / 1 zatvarajući → 6/6").

**Uzrok.** `state_open = True` postavlja se bezuvjetno na početku odlomka, pa
funkcija ne vidi `„` koji je u odlomku već otvoren.

**Popravak.** Stanje se za svaki ravni navodnik čita iz cijelog prefiksa odlomka,
uz već obavljene zamjene: otvoreno je ako je `„` više nego `”`.

**Gdje.** `scripts/apply_safe_fixes.py`, `scripts/tests/test_all.py` (skupina R15).

**Dokaz.** Prije: `„…„` i `”…„`. Poslije: `„…”` i `„…”`, 2 otvarajuća i 2
zatvarajuća u istom odlomku.
