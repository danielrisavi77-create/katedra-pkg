# rad-audit — alati i naredbe

<!-- Izdvojeno iz rad-audit/SKILL.md u v2.2.0 (thin router). Sadržaj nepromijenjen. -->

## Alati (skripte, ovise samo o `python-docx`)

Sve su read-only osim što ti daju nalaze. Pokreni pojedinačno ili sve odjednom:

```bash
cd scripts
python3 audit_all.py rad.docx --sources izvori_folder/   # objedinjeni ispis u terminal
python3 generate_report.py rad.docx --sources izvori_folder/   # ISTO + spremljen .md izvještaj
                                                                 # razvrstan Kritično/Srednje/Kozmetičko
                                                                 # (--json izvjestaj.json za strojnu obradu)
# ili pojedinačno:
python3 check_citations.py rad.docx      # B: IEEE [N] — definirano/citirano, siročad, rupe, redoslijed;
                                          #    broji i citate u TABLICAMA i FUSNOTAMA; [2020] (godina u
                                          #    zagradi) se prijavi posebno, ne broji kao citat
python3 check_citations.py rad.docx vancouver   # B: Vancouver (N) — brojanje, rupe u numeraciji, siročad,
                                          #    citat bez reference, rastući redoslijed;
                                          #    decimale „158 (77,8)" i svezak(broj) „53(3-4)" nisu citati
                                          #    NE provjerava FORMAT navoda (razmak iza zareza, en-crtica u
                                          #    rasponu, položaj prema interpunkciji, „i sur." nakon 6 autora)
                                          #    — v. „Poznati opseg”; do v1.9.4 je SKILL.md to tvrdio, kod nije radio
python3 check_placeholders.py rad.docx     # A2: [TREBA IZVOR], [DOPUNITI], [PROVJERI STR.] u tijelu,
                                          #     ćelijama, FUSNOTAMA, endnotama, zaglavljima i podnožjima
python3 osvjezi_contract.py [--upisi]     # uskladi engine_contract.json s otiskom koda (zove ga test_all)

# ── faze dodane u v1.9.5–1.9.10; sve ih zove generate_report.py, ali se
#    pokreću i pojedinačno kad želiš samo jednu ────────────────────────────
python3 provjeri_metapodatke.py rad.docx  # A4: docProps/ — ostavljeni predlošci („Student", „PC"),
                                          #     tragovi alata, app.Company, lokalne putanje, autori
                                          #     praćenih izmjena, dc:creator naspram naslovnice.
                                          #     --postavi upisuje u NOVU datoteku; rsid i povijest
                                          #     izmjena NE dira (v. docstring)
python3 check_uputnice.py rad.docx        # F2: „prikazano u Tablici 3" mora pogađati prikaz koji
                                          #     postoji, i svaki prikaz mora biti uveden rečenicom
python3 check_tablice.py rad.docx         # C4: redak Ukupno naspram zbroja, postoci koji ne daju
                                          #     100, n iz natpisa naspram zbroja stupca
python3 check_statistika.py rad.docx      # C3: p ≥ α opisan kao značajan i obrnuto, p = 0,000,
                                          #     p izvan [0,1], test koji se nigdje ne imenuje
python3 check_hipoteze.py rad.docx        # G1: dobiva li svaka postavljena hipoteza izričitu
                                          #     presudu; NE presuđuje je li presuda točna
python3 mapa_izvora.py rad.docx --izvori izvori/ --izgradi izvori/mapa.json
                                          #     prijedlog mape ključ citata → datoteka izvora
python3 check_tvrdnja_izvor.py rad.docx --izvori izvori/
                                          # D2: brojka mora biti u izvoru koji TA rečenica citira;
                                          #     „pripisano krivom izvoru" je najteži nalaz ovdje
python3 check_reference_exists.py rad.docx --izvori izvori/ [--strogo]
                                          # B2: građa / identifikator (DOI, ISBN, URL) / službena
                                          #     oznaka / NEPOTVRĐENA jedinica
python3 propagacija.py --rukopis .katedra/poglavlja --docx rad.docx
                                          # E3: je li izmijenjena vrijednost stigla u sve tablice i
                                          #     grafikone; traži rukopis, pa NIJE dio audita gotova
                                          #     .docx-a nego moda 3
python3 tests/test_bolesni.py             # rad S POGREŠKAMA mora pasti + negativna kontrola
python3 check_citations_authoryear.py rad.docx  # B: autor-godina (Prezime, 2020) — HEURISTIKA, čitaj docstring;
                                                 #    fusnote/endnote uključene u "citirano"
python3 check_fields.py    rad.docx      # A/F: fldChar balans, TOC/REF/SEQ, pageBreak, autofit, zaštita,
                                          #      NEPRIHVAĆENE IZMJENE/komentari
python3 check_typography.py rad.docx     # E: navodnici „…", ×, –, zarez, jedinice, NBSP
python3 check_repetition.py rad.docx     # E: početci rečenica, fraze, ritam, atribucijski glagoli
python3 <KATEDRA_LITE>/scripts/provjeri_zamke_proze.py rad.docx
                                          # E: spojene rečenice (zarez+veliko), interpunkcijski tik
                                          #    (dvotočka/duga crtica), ponovljen kostur odlomka,
                                          #    stopa i raspon u različitim jedinicama, brojka iz
                                          #    popisa literature bez odjeka, kvantifikator uz citat
python3 numbers_inventory.py rad.docx [--domain celik|elektro|strojarstvo|it|generic]
                                          # C: broj+jedinica po grupama (šira lista jedinica, uklj. V/Hz/%/°)
                                          #    + DETEKCIJA SUKOBA: isti pojam s više različitih vrijednosti
                                          #    iste jedinice → ⚠ (domena auto-detektirana ako --domain nema)
python3 cross_check.py rad.docx izvori_folder/ [--domain ...]   # D: nalaze li se tvrdnje u izvorima
                                                                  #    (ispisuje kontekst oko svakog pogotka)
python3 check_overlap.py rad.docx izvori_folder/   # D: doslovno preklapanje (verbatim-copy) BEZ oznake citata
python3 parafraza.py stari.docx novi.docx --poglavlja "1. UVOD:2. CILJ"
                                          # E/D: koliko je nova verzija STVARNO drukčija od stare
                                          #      (8-grami po poglavlju, prag 20 %); za mentorov
                                          #      zahtjev „smanji podudarnost" — NE zamjenjuje Turnitin
python3 brojke_iz_rasprave.py rad.docx    # C: svaka brojka o vlastitom uzorku u Raspravi/Zaključku
                                          #    mora postojati u Rezultatima ili tablicama; brojka s
                                          #    citatom u istoj rečenici pripisana je literaturi;
                                          #    + zaokruživanje p naspram stvarnih vrijednosti
python3 inventar_tvrdnji.py rad.docx --dosjei fazaD/ --po-seriji 7
                                          # D0: inventar brojčanih/opisnih tvrdnji po
                                          #     numeričkoj referenci (Vancouver/IEEE).
                                          #     Ne provjerava istinitost tvrdnje.
python3 extract_text.py rad.docx         # čist tekst (python-docx, bez XML smeća)
```

Stil citiranja (IEEE `[N]` vs Vancouver `(N)` vs autor-godina) se auto-detektira (`common.detect_citation_style`)
u `audit_all.py`/`generate_report.py` — pokreće se odgovarajuća skripta. Domena rada (za
`numbers_inventory.py`/`cross_check.py`) se auto-detektira preko `domains/` paketa (celik,
elektro, strojarstvo, it; fallback = generički frekvencijski). `--domain`/override po potrebi.
⚠️ **Biomedicinskog paketa nema.** Rad o palijativnoj skrbi detektiran je kao `celik`
(96 bodova) i dobio podsjetnik na aritmetiku krovnih panela te lažni sukob `'stup' + %`
(iz „stupanj"). Dok `domains/biomed.py` ne postoji, za sestrinstvo, medicinu i srodno
zadaj `--domain generic` ručno.

**Automatski sigurni ispravci** (jedina skripta koja MIJENJA dokument):
```bash
python3 apply_safe_fixes.py rad.docx out.docx            # navodnici, ×, autofit, updateFields
python3 apply_safe_fixes.py rad.docx out.docx --fonts arial --no-indent   # + Arial + bez uvlake
python3 apply_safe_fixes.py rad.docx out.docx --strip-breaks   # + ukloni pageBreakBefore (v. niže)
python3 apply_safe_fixes.py rad.docx --dry-run           # samo prikaži što bi promijenio
```
⚠️ `pageBreakBefore` se **ne uklanja po defaultu**. Većina fakulteta (EFZG i sl.) **propisuje** prijelom prije svakog poglavlja, pa bi tiho uklanjanje prekršilo formalni zahtjev. `--strip-breaks` koristi tek kad si provjerio profil fakulteta (`prijelom_pred_poglavljem`) i kad je prijelom na **natpisu prikaza**, ne na naslovu poglavlja.
Radi samo unutar vidljivog teksta i strukturnih atributa — NE kolabira runove, NE dira polja.
Zaštite od tihog kvarenja (sve verificirano testovima):
- navodnici PO ODLOMKU (reset stanja na svakom top-level `<w:p>`, depth-aware — tekst iza
  inline textboxa se NE preskače); inč-oznake (12", 6") se preskaču; odlomci s neparnim
  brojem navodnika se prijavljuju za ručnu provjeru;
- U+201C se pretvara u hrvatski zatvarajući U+201D SAMO u odlomku koji sadrži i „ —
  engleski "…" par (Abstract!) ostaje netaknut i prijavi se u ispisu;
- hex literali (0x41) se NE pretvaraju u "0 × 41";
- `--no-indent` ubacuje razmak isključivo u `<w:pPr>` (nikad u run-level `rPr` gdje
  `w:after` nije dopušten po schemi), a firstLine=0 mijenja SAMO stil Normal.
Uvijek nakon toga: `validate.py out.docx --original rad.docx`. Sadržajne pogreške (tipfeleri,
stil, cross-check) NISU auto — njih riješi ručno/subagentom uz verifikaciju.

Za izvore u PDF-u prvo: `pdftotext -layout izvor.pdf izvor.txt` (skripte čitaju .txt/.md/.docx).
Za XSD validaciju, prihvaćanje tracked changes i render koristi **docx skill** (apsolutne putanje):
```bash
python3 /root/.claude/skills/docx/scripts/office/validate.py out.docx --original original.docx
python3 /root/.claude/skills/docx/scripts/merge_runs.py unpacked/   # spoji fragmentirane runove nakon Word re-savea
python3 /root/.claude/skills/docx/scripts/accept_changes.py rad.docx out.docx   # prihvati SVE tracked changes
                                                                                  # (obavezno ako check_fields.py javi
                                                                                  #  "NEPRIHVAĆENE IZMJENE/komentare")
```
