---
name: rad-audit
description: "Motor audita akademskog .docx-a, faze A–G: integritet, citati i literatura, brojke i statistika, hipoteze, tvrdnja naspram izvora, jezik, Word polja, metapodaci, sigurni ispravci. Aktiviraj na 'audit rada', 'provjeri citate/literaturu', 'usporedi rad s izvorima', 'zašto je tablica zaključana'. U projektu s .katedra/ zove ga katedra-lite mod 4. v2.4.1."
---

# Rad-audit — pipeline za provjeru akademskih radova

## 0.0 DVA ULAZA — utvrdi koji je prije wizarda

Ovaj skill radi u dva načina. Kod je isti, razlikuje se **tko vodi razgovor**.

```bash
cat .katedra/stanje.json 2>/dev/null | head -1 || echo "SOLO"
```

| uvjet | način | ponašanje |
|---|---|---|
| nema `.katedra/`, korisnik je tražio provjeru rada | **SOLO** | vodiš wizard (`references/solo_intake.md`, 0.1–0.6), ti isporučuješ izvještaj |
| postoji `.katedra/stanje.json` **ili** je pozvan `engine.py` iz Katedre | **MOTOR** | **preskoči cijelu sekciju 0** |

**U načinu MOTOR:**

- Wizard se **ne pokreće**. Opseg, tip rada, citatni stil i profil fakulteta dolaze iz `.katedra/stanje.json` — ništa od toga ne pitaj ponovno.
- Izvještaj ide u `.katedra/audit.md` i `.katedra/nalazi.json`, ne u chat. Katedra ga spaja sa svojim nalazima (teza, stil, geometrija) i isporučuje jednom.
- Odobrenje za fazu G traži **Katedra**, ne ti.
- Ograničenja (npr. nema izvorne građe) upiši u JSON, ne samo ispiši.

Praktično: `python3 generate_report.py rad.docx --json .katedra/nalazi.json` je
cijeli ugovor. Katedra ne poziva pojedinačne skripte mimo `engine.py`, a ti ne
pretpostavljaš da si sam u razgovoru.

### Ugovor prema Katedri — `scripts/engine_contract.json`

Katedra od verzije s `rad_audit_contract.py` (CONTRACT_VERSION `"1"`) ne poziva
motor bez **deklariranog manifesta**. Bez njega `engine.py --provjeri` javlja
„nedostaje engine_contract.json", odbija pokrenuti faze A–G i pada u smanjeni
opseg — a to je tiho gubljenje faze D, koja je jedina strojna provjera tvrdnji
prema izvornoj građi.

Manifest je `scripts/engine_contract.json`. Pokazuje na `scripts/katedra_adapter.py`,
koji `generate_report.py` poziva **nepromijenjenog** i samo prevodi oblik izlaza:

| što Katedra traži | što `generate_report.py` daje | tko premošćuje |
|---|---|---|
| `findings` kao **popis** | rječnik grupiran po težini | adapter (izvorna grupacija ostaje pod `findings_by_severity`) |
| `contract_version`, `engine`, `engine_version`, `capabilities` | ne postoje | adapter |
| `counts`, `phase_exit_codes` | ✅ već postoje | — |

**Ne mijenjaj `generate_report.py` da bi zadovoljio ugovor.** Adapter postoji
upravo zato da oblik izlaza za Katedru i samostalni SOLO izlaz ostanu razdvojeni.

`engine_version` nije semantička verzija nego otisak sadržaja skripti motora
(`0.0.0-undeclared+<sha8>`), jer ovaj skill verziju ne deklarira u frontmatteru.
Kad se skripte promijene, otisak se promijeni — to je namjerno.

Sposobnosti u manifestu potvrđene su **izvođenjem**, ne čitanjem koda:
`audit.report-json.v1` (izlaz `generate_report.py --json`),
`hr.citations.author-year.v1` i `hr.typography.numbers.v1`
(`tests/test_all.py`, skupine R13 i R8), `hr.citations.vancouver.v1`
(skupina R16, 9 testova + HKS-FZS rad sa 75 referenci), te
`safe-fixes.preserve-page-breaks.v1` (`apply_safe_fixes.py` nad stvarnim radom:
prijelomi, sekcije, odlomci, broj riječi i broj stranica nepromijenjeni).
Ako dodaješ novu sposobnost u manifest, prvo je dokaži testom — Katedra
manifestu vjeruje na riječ i neće provjeravati izvorni kod umjesto tebe.

Provjera da lanac radi:

```bash
python3 <KATEDRA_SKILL>/scripts/engine.py --provjeri
# ✅ contract v1 · engine 0.0.0-undeclared+<sha8> · rad-audit
```

**Nikad oba intakea.** Ako je korisnik već odgovarao na Katedrina pitanja, tvoja
su odgovorena. Dupli wizard je najbrži način da rad izgleda neozbiljno.

## 0. ULAZNI PROTOKOL — SAMO U NAČINU SOLO

**Prvi output u načinu SOLO je wizard, ne pipeline i ne objašnjenje pipelinea.** Prije prve poruke
pročitaj **`references/solo_intake.md`** (guard protiv duplog intakea, točan format prve poruke,
što uploadati, sažetak + STANJE, pravila intakea, isporuka). U načinu MOTOR tu datoteku ne čitaš.

## Kada što

- „Napravi audit rada" → prođi cijeli pipeline (dolje), na kraju izvještaj + (uz potvrdu) ispravci.
- „Provjeri citate/literaturu" → faza B.
- „Usporedi rad s izvorima" → faza D (traži izvornu građu ako je nema).
- „Sredi formatiranje / zašto je tablica zaključana / prazna" → faza F.
- „Jezik/stil" → faza E (za teško prepisivanje delegiraj subagentu uz stroga pravila, pa verificiraj sam).

## Alati

Sve skripte ovise samo o `python-docx` i read-only su. Cijeli pipeline:
`python3 scripts/generate_report.py rad.docx --sources izvori/ [--json izvjestaj.json]`
(isto što i `audit_all.py`, uz spremljen izvještaj razvrstan Kritično/Srednje/Kozmetičko).
Pojedinačne skripte po fazi (citati IEEE/Vancouver, brojke, cross-check, jezik, Word polja,
metapodaci, prikazi, statistika, hipoteze): **`references/alati.md`**. Čitaj je kad pokrećeš
jednu fazu ili tražiš zastavicu; za cijeli audit dovoljan je `generate_report.py`.

## Tijek (A–G)

1. **Prikupi građu** — rad + SVU izvornu građu. Drive konektor vadi ~10 MB; veći ZIP → traži upload u chat.
2. **Kontekst/pravila** — koji fakultet; ima li propisani stil (često nema → dosljednost + potvrda mentora). Stil ([N] vs autor-godina) auto-detektira `common.detect_citation_style` (vidi ispod), ali potvrdi da ima smisla za konkretni rad.
3. **A. Integritet** — `extract_text.py` (NE regex po XML-u), `check_fields.py`, te
   **`check_placeholders.py` iz `katedra-lite`** (`[IME PREZIME]`, `[DOPUNITI]`,
   `[TREBA IZVOR]`, `[PROVJERI STR.]`). Ta je provjera postojala, ali je nije bilo u ovom
   lancu, pa je rad s placeholderom na naslovnici prolazio audit — nađeni su čitanjem, ne
   alatom. Alat koji se ne pokreće jednak je alatu koji ne postoji.
   Pazi i na Word artefakte: split runovi, `_GoBack` presiječe riječ (skriveni tipfeler), TOC omotan u SDT. `check_fields.py` sad javlja i **neprihvaćene tracked changes/komentare** — ako ih ima, prvo pokreni `docx` skillov `accept_changes.py`, inače su brojanje citata/brojki i tekstualna analiza nepouzdani.
4. **B. Citiranje** — `check_citations.py` za IEEE `[N]` ili `check_citations_authoryear.py` za autor-godina (auto-izabrano u `audit_all.py`/`generate_report.py`; autor-godina provjera je HEURISTIKA — ključ je prvi-autor+godina, ne pun popis autora, pazi na 2020a/2020b). Fusnote/endnote se pretražuju preko `common.load_supplementary_text`. Uz to ručno: format svake reference (knjiga/članak/norma/web/neobjavljeno; DOI; datum pristupa; „bez godine" = crveni flag).
5. **C. Tehnika** — `numbers_inventory.py` (domena rada se auto-detektira preko `domains/` — celik/elektro/strojarstvo/it/generic; `--domain` override) + ručno aritmetika (površina, paneli, raster×okviri) i granica dokaza.
6. **D. Cross-check** — `cross_check.py rad.docx izvori/` (sad ispisuje ±40 znakova konteksta oko svakog pogotka — provjeri ga, substring-match zna dati lažni pozitivac preko granice rečenice) + `check_overlap.py rad.docx izvori/` (doslovno preklapanje BEZ oznake citata — akademska čestitost, ne cross-check sadržaja). Kad se izvori sukobe: rad mora DEKLARIRATI razliku; prednost kasnijim/izvedbenim izvješćima i fotografiji oznake. Pazi na skrivene atribucije i imena tvrtki koja se javljaju samo u zaglavlju.
7. **E. Jezik/tipografija** — `check_repetition.py`, `check_typography.py`. Razbij obrazac „izvješće navodi", koncentriraj hedžing, spoji staccato. Tipfeler može biti skriven razbijenim runom.
8. **F. Formatiranje** — SADRŽAJ/POPISI kao **TOC polja**, natpisi kao **SEQ**, spomeni kao **REF**; makni `pageBreakBefore` **samo s natpisa prikaza** (praznine/„zaključano") — na naslovu poglavlja je najčešće propisan pa ostaje, tablice `autofit`; fontovi dosljedni (theme + docDefaults + stilovi); uvlaka iz Normal `firstLine` (+ `after` da se odlomci ne stope); `updateFields=true`.
9. **G. Ispravci** — jasne pogreške odmah; stil uz potvrdu. Uređuj po CIJELOM odlomku, ali **nikad ne kolabiraj runove odlomka s poljem** (REF/SEQ). Escape `& < >`, `xml:space="preserve"`.
10. **H. Upute fakulteta** — `generate_report.py` uvijek evidentira ovu fazu.
    Bez izričito odabrane provjerne skripte (`--profil <put>`) vraća kod 3:
    fakultetska pravila nisu provjerena. Lokacija `KATEDRA_LITE` i prisutnost
    susjednog skilla nisu odabir fakulteta. Tek za potvrđeno odabrani HKS-FZS
    smije se zadati `--profil <KATEDRA_LITE>/scripts/provjeri_hks_fzs.py`.
    Nedostajuća izričita putanja ili prekid izvršavanja daju kod 2, bez fallbacka.
    `--profil` ovdje prima pouzdano odabranu Python skriptu, **ne JSON profil**.
    Status i pravila HKS profila ostaju zasebni dokazi: ova zakrpa ne potvrđuje
    izvorne Upute. Neizmjeren redoslijed ima `ok: null`, ne prolaz.
11. **Verifikacija** — nakon svake runde: XSD validacija, fldChar balans, citati, ključne brojke, cross-check spot, tipografija; render ako soffice radi (ako pada u sandboxu — provjeri na XML-u i budi iskren; NE šalji pandoc-PDF kao dokaz fonta). Za predaju korisniku spremi razvrstan izvještaj s `generate_report.py`.

## Poznati opseg (pročitaj prije nego zaključiš da nešto "ne radi")

- `check_citations.py` pokriva numeričke stilove IEEE `[N]` i (od v1.9) Vancouver `(N)`
  — drugi argument `ieee|vancouver`, inače se bira po tekstu; za autor-godina koristi
  `check_citations_authoryear.py` (sve je ožičeno kroz auto-detekciju stila u
  `audit_all.py`/`generate_report.py`). Vancouver NE provjerava format same reference
  (skraćeno ime časopisa, redoslijed polja) ni citate u eksponentu — samo ovalne zagrade.
  Autor-godina provjera je heuristika (v. docstring skripte) — čitaj kao popis za ručnu
  provjeru, ne kao konačnu presudu poput IEEE brojčane provjere.
- `numbers_inventory.py`/`cross_check.py` domenski paketi pokrivaju celik/elektro/
  strojarstvo/it + generički fallback. Za jako specifičnu domenu koja ne odgovara nijednom
  paketu, dodaj novi u `domains/__init__.py` (isti oblik: label/keywords/claim_patterns) —
  automatski se uključuje u auto-detekciju.
- `check_overlap.py` hvata blisko-doslovno podudaranje (n-grami), ne parafrazu/sinonime —
  nije Turnitin-razina alata. Preklapanje samo znači "provjeri je li ovo označeno kao citat",
  ne "ovo je plagijat".
- Nijedan alat ne provjerava žive URL-ove/DOI (mrtvi linkovi) — to je ručna provjera ili
  zahtijeva mrežni pristup izvan ovog read-only pipelinea.
- Nijedan alat ne provjerava **sadrži li izvor tvrdnju** koja mu se pripisuje. `verify_sources.py`
  odgovara samo na „postoji li izvor". Na jednom radu je tvrdnja pripisana knjizi koja
  postoji i uredno prolazi provjeru, a te tvrdnje u njoj nema. Egzistencija nije sadržaj.
- Broj stranice koji je vratio sažetak dokumenta nije mjerenje nego hipoteza: dva dohvata
  istog PDF-a dala su 445 i 446–447 za isti odlomak, a točna je bila 446. Stranica smije doći
  samo iz `pdftotext`/OCR nad datotekom s vidljivim zaglavljima, iz mehaničkog popisa
  zaglavlja, ili iz sekundarnog izvora koji doslovno navodi primarni tekst sa stranicom.
  Ako stranice PDF-a teku 1–N, to je otisak, a ne svezak — brojevi se ne izvode računom.

## Samo-testiranje skripti

Regresije i „bolesni rad mora pasti": `python3 scripts/tests/test_all.py` i
`python3 scripts/tests/test_bolesni.py`; oba su u `bin/testovi.sh` paketa. Pravila za dodavanje
testa uz svaki popravak i popis R-skupina: **`references/samotest.md`**.

## Zlatna pravila pri uređivanju .docx

- Tekst uvijek preko **python-docx**, ne regexom po `<w:t>` (povlači markup: lažni „4A" iz rsid, lažni navodnici iz atributa).
- Odlomak s poljem = **ne diraj runove**; rekonstruiraj tekst-prije + polje + tekst-poslije ili preskoči.
- Delegiraš prepisivanje subagentu → traži JSON {original, rewrite}, pa SAM provjeri da je skup citata `[XX]` po odlomku identičan i da su tehnički tokeni prisutni; odbaci sve što ne prođe.
- `updateFields` u `settings.xml` umetni PRIJE `footnotePr`/`endnotePr` (dakle i prije
  `compat/rsids/mathPr`). Ranija formulacija „prije compat" bila je točna ali nepotpuna:
  umetanje iza `endnotePr` proizvodi dokument koji pada XSD validaciju, jer `CT_Settings`
  traži redoslijed … `updateFields`, `hdrShapeDefaults`, `footnotePr`, `endnotePr`, `compat` …
  Pravilo koje je točno ali nepotpuno gore je od nikakvog, jer se čita kao provjereno.