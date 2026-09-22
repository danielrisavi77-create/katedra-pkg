# Ciljane DOCX izmjene — ograničeni plan, zaseban izlaz

Motor: `scripts/ciljane_izmjene.py`. Regresije: `scripts/tests/test_ciljane_izmjene.py`.
Ovo je dodatak za već postojeći dokument, ne zamjena za `gradi.py`, `diff_versions.py`
ili predajni gate. Ne šalje e-poštu, ne briše metapodatke, ne transkribira zvuk,
ne tumači fotografije i ne provjerava službene akademske nazive na internetu.

## Uporaba

```bash
python3 rad-docx/scripts/ciljane_izmjene.py inspect rad.docx > inventar.json
python3 rad-docx/scripts/ciljane_izmjene.py apply rad.docx \
  --plan plan.json --out rad-ureden.docx --snapshot rad-snapshot.docx \
  --report provjera.json
python3 rad-docx/scripts/ciljane_izmjene.py verify rad-snapshot.docx rad-ureden.docx \
  --plan plan.json
python3 rad-docx/scripts/tests/test_ciljane_izmjene.py
```

Svaki izlaz/snapshot/izvještaj mora biti nova putanja; nema overwrite zastavice.
Izlaz 0 znači izmjeren **strukturni** prolaz, 1 znači odstupanje od plana, a 2 znači
neispravan/nepodržan ulaz ili da operacija/provjera nije izvedena. `visual_check.ok`
uvijek je `null`: render i ljudski pregled ostaju obavezni prije predaje.

## Plan v1

Primjer strukture (hash i indekse zamijeni stvarnim izlazom `inspect`, vrijednosti
zamjena preuzmi samo iz korisnikove potvrđene upute ili provjerenog izvora):

```json
{
  "version": 1,
  "target_sha256": "<SHA-256 iz inventara ciljnog Worda>",
  "output_kind": "docx",
  "references": [
    {"role": "visual_reference", "id": "<lokalna oznaka primjera>"}
  ],
  "operations": [
    {
      "op": "replace_degree",
      "paragraph": 12,
      "old": "magistra",
      "new": "sveučilišna magistra",
      "context": "awarded",
      "source": {"kind": "user_confirmed", "locator": "<potvrđena odluka>"}
    }
  ]
}
```

Svi indeksi odnose se na **izvorni** dokument, počevši od nule, i kad se u istom planu
uklanja naslovnica. Nepoznata/duplicirana JSON polja, više zahvata u istom odlomku,
stari hash ili prazan plan ne prolaze. Referenca nosi samo ulogu i identifikator:
ne učitava se, ne izvršava i iz nje se ne preuzimaju podaci. `output_kind: image`
i putanja izlaza koja nije `.docx` odbijaju se. Binarni sadržaj ulaza mora stvarno
biti Wordov dokument, ne slika s promijenjenim nastavkom.

### Obični tekst

`replace_text` ima `paragraph`, `old`, `new`. Stari tekst mora se pojaviti točno
jednom u odabranom odlomku. Zamjena dira samo odgovarajuće `w:t` čvorove, zadržava
`w:pPr` i `w:rPr` te okolni tekst. Smije prijeći više tekstualnih segmenata samo ako
nose isto izravno oblikovanje. Mješovito oblikovanje, polja, poveznice, slike,
sidra i prijelomi **u ciljnom odlomku** zahtijevaju drugi postupak, ne spljoštavanje
odlomka dodjelom `p.text`. Takvi sadržaji izvan odabranog mjesta ostaju sačuvani.

### Akademski naziv

`replace_degree` dodatno traži `context: earned|awarded` i `source` s `kind:
official|user_confirmed` te nepraznim `locator`.

- `earned`: obični odlomak u prepoznatom području ŽIVOTOPIS/CURRICULUM VITAE.
- `awarded`: desna ćelija prepoznate dvostupčane dokumentacijske kartice, u retku
  akademskog naziva ili kratice. Ne mijenja lijevu oznaku niti ostale retke.

Granice se određuju iz eksplicitnih naslova. Nestandardna struktura može biti
odbijena; tada se ne smije automatski pretpostaviti kontekst. Motor ne prevodi nazive
niti iz vrste rada zaključuje da je osoba stekla stupanj. `source` je trag odluke,
ne neovisna provjera izvora. `unconfirmed_audio` nije prihvaćen izvor odluke.

### Samo prva naslovnica

```json
{
  "op": "remove_first_cover",
  "end_block": 3,
  "expected_text": ["IZMIŠLJENO SVEUČILIŠTE", "Primjer Autora", "POKAZNI RAD O UČENJU"]
}
```

`end_block` je indeks **prvog zasebnog odlomka s ručnim prijelomom stranice** u
popisu `blocks`. `expected_text` mora potpuno odgovarati nepraznom tekstu prethodnih
odlomaka. Uklanja se samo taj početni blok s prijelomom. Ne traži se "drugi break"
i ne pretpostavlja da ga je sigurno obrisati. Dvostruko uklanjanje nije dopušteno.

U ovoj verziji odbijaju se naslovnice s tablicama, unutarnjim prijelomima, odjeljcima,
sidrima, bilješkama i poljima, kao i posebno zaglavlje prve stranice ili parna/neparna
zaglavlja. To je namjerno ograničenje, ne potvrda da je takav dokument neispravan.
Ručno razdvojen blok može prije renderiranja zauzimati više fizičkih stranica:
**alat ne dokazuje da je uklonjena točno jedna fizička stranica**. To se mjeri renderom.

## Očuvanje i oporavak

Prije pisanja izlaza nastaje byte-identičan snapshot. Izlaz zadržava sve dijelove ZIP
paketa; osim `word/document.xml` svi ostaju byte-identični, uključujući slike, metapodatke,
styles, relacije, footnotes i footere. Nereferencirani mediji se ovdje ne čiste.

`verify` ponovno izvodi odobreni plan nad originalom i uspoređuje kanonski XML cijelog
tijela te ostale dijelove paketa. Hvata promjenu brojke, formatiranja, priloga, dodatno
brisanje ili metadata promjenu koja nije u njegovu opsegu. Nije neovisan dokaz da je
sam plan sadržajno ispravan — zato plan mora biti pregledan prije primjene.

Napisani izlaz ponovno se čita i provjerava. Ako provjera ili zapis izvještaja zakaže,
vlastiti novi izlaz uklanja se, snapshot ostaje. Postojeće putanje/simboličke poveznice
se ne prepisuju. Atomarna objava koristi hardlink u istoj mapi; nepodržan datotečni
sustav vraća grešku, ne nesiguran fallback. Revizije se ne prihvaćaju automatski;
kriptografski potpisan paket se odbija (slika potpisa izvan izmjene ostaje netaknuta).

## Što regresije dokazuju

Sintetički dokumenti dokazuju očuvanje odobrenog opsega, uloga ulaza, konteksta
rubrika, run-formatiranja, odjeljaka, footer polja i medijskih dijelova; namjerno
pokvareni izlazi moraju pasti. Slučaj `p.text` reproducira gubitak dva `w:rPr` čvora
na sintetičkom odlomku, dok ih ciljano uređivanje čuva.

Nijedan privatni rad, potpis ili snimka ne ide u repozitorij. Live odabir alata iz
multimodalnog razgovora, Microsoft Word render i provjera stvarnog fakultetskog
profila nisu dio ovih determinističkih testova.
