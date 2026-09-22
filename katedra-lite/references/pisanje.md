# MOD 2 i 3 — PISANJE I POBOLJŠANJE

> Mod 2 piše po odobrenom planu. Mod 3 popravlja postojeći tekst i vodi ga
> `references/stil_pipeline.md`. Zajedničko im je sve ispod.
>
> **Jezgra (v2.4).** Ovo je dio koji treba svako pisanje. Dva dodatka se otvaraju na okidač
> (`ucitavanje.py` ih navodi pod NE UČITAVAJ SADA):
> `references/pisanje_dokument.md` (sastavljanje .docx, tko radi dokument, karta premještanja,
> sažetak, redline, lanac zahvata) i `references/pisanje_dokazi.md` (verifikacija izvora,
> evidence/claim ledger, strict gate, produbljivanje bez izmišljanja, B13 rewrite gate).
> Pravilo ostaje isto: dvojba znači otvori, preskočeno štivo je skuplje od suvišnog.

---

## 0. Prije prve rečenice — gdje tekst živi

**Markdown je izvor istine, `.docx` je izvedeni artefakt.** Poglavlja se pišu u
`.katedra/poglavlja/NN-naziv.md`, jedno po datoteci, a dokument se iz njih
SASTAVLJA. Ne piši poglavlje u razgovor pa neka ga student prekopira, i ne upisuj
ga izravno u `.docx`.

```bash
python3 <KATEDRA_SKILL>/scripts/rukopis.py init            # kostur iz plana.json
python3 <KATEDRA_SKILL>/scripts/rukopis.py status          # koliko je napisano
python3 <KATEDRA_SKILL>/scripts/build_docx.py --fakultet <slug> --tip <tip> \
    --rukopis --out ./rad.docx --provjeri
```

Konvencije rukopisa, cijena ručnog uređivanja u Wordu i **tko radi dokument** (FPZG →
`fpzg-diplomski`): `references/pisanje_dokument.md` §0 i §0b. Otvori prije prvog sastavljanja
`.docx`-a. **Student i dalje piše sadržaj:** kostur ne piše nijednu rečenicu rada.

## 1. Kako se piše (mod 2)

### 1.1 Nikad „gdje smo stali"

```bash
python3 <KATEDRA_SKILL>/scripts/plan_state.py next
```

Vraća prvo potpoglavlje sa `status: nije-napisano`, s planiranim opsegom, sadržajem
i izvorima. To je dovoljno da se odmah piše. `nastavi rad` ne znači pitanje korisniku
nego ovaj poziv.

Nakon svakog potpoglavlja:

```bash
python3 <KATEDRA_SKILL>/scripts/plan_state.py mark 4.2 --status napisano --rijeci 820
```

### 1.2 Jedno potpoglavlje po ciklusu

Piši potpoglavlje → self-check (§4) → upiši status → tek onda sljedeće. Pisanje tri
poglavlja odjednom uvijek daje tekst koji se u drugom poglavlju počne ponavljati, a
u trećem izgubi tezu.

### 1.3 Struktura odlomka

Svaki odlomak nosi **jednu ideju** i ima:

1. tematsku rečenicu — o čemu je odlomak
2. objašnjenje pojma — što znači, kako funkcionira
3. primjer ili razradu — konkretno, kontekstualizirano
4. referencu, ako se iznosi tvrdnja koja traži potkrjepu
5. mini zaključak ili prijelaz — što iz ovoga slijedi

Ne staj na razini definicije. Definicija bez implikacije, ograničenja ili usporedbe
je enciklopedijski unos, a ne akademski tekst.

Geometrija odlomka dolazi iz profila fakulteta (`format.odlomak`), a provjerava se
u stvarnom prijelomu, ne procjenom po znakovima:

```bash
python3 <KATEDRA_SKILL>/scripts/profile_resolver.py --fakultet "<alias>" --tip <tip> --profile-out .katedra/resolved_profile.json
python3 <KATEDRA_SKILL>/scripts/check_paragraphs.py ./rad.docx --profil .katedra/resolved_profile.json
```

### 1.4 Struktura rada

**Uvod**: kontekst i relevantnost, istraživačko pitanje, cilj, teza, kratki pregled
strukture poglavlja — šest elemenata, i svi moraju biti tu. **Razrada**: logička
poglavlja, teorija povezana s analizom — ne dva odvojena bloka koji se nikad ne sretnu.
**Zaključak**: sažetak nalaza, direktan odgovor na istraživačko pitanje iz uvoda,
implikacije i preporuke.

Zaključak koji ne odgovara na pitanje iz uvoda je najčešći razlog zašto formalno
uredan rad dobije četvorku. Drugi najčešći razlog jest da je odgovor već potrošen u
raspravi — v. `references/rasprava.md` §6.

**Poglavlja koja imaju vlastiti protokol.** Ne piši ih iz ovoga poglavlja:

| Poglavlje | Protokol | Zašto zaseban |
|---|---|---|
| Metodologija | `references/metodologija.md` | osam odjeljaka; piše se u modu 1, ne kad se dođe do njega po redu |
| Rasprava | `references/rasprava.md` | četiri poteza po nalazu; jedino mjesto gdje se nalaz sudara s literaturom |
| Summary / ključne riječi (EN) | `references/engleski.md` | prevodi se iz **gotovog** hrvatskog sažetka, nikad paralelno |

Popis svih dijelova rada i onoga tko ih provjerava: `references/dijelovi.md`.
Nakon svakog gotovog dijela upiši status:

```bash
python3 <KATEDRA_SKILL>/scripts/dijelovi.py --set <dio>=napravljeno
```

### 1.5 Karta premještanja

Kad mentor traži hrpu strukturnih pomaka (šest do deset odjednom): **prvo karta, pa tek
onda zahvat** — `references/pisanje_dokument.md` §1.5.

---

## 2. Citiranje

Format dolazi iz profila (`citiranje.u_tekstu`), ne iz navike. Tablica je samo
ilustracija — **dijalekt i oblik u tekstu uvijek dolaze iz `resolved_profile.json`
(`citiranje.stil`, `citiranje.u_tekstu`), nikad iz ove tablice**; kad se tablica i profil
razlikuju, profil ima pravo, a tablica se ispravlja (v1.9: red FPZG je nosio `str.`, a
profil `fpzg.json` traži dvotočku bez „str." — `(Becker, 2007: 9)`).

| profil | u tekstu | u popisu |
|---|---|---|
| `autor-godina` (FPZG) | `(Lindblom, 1959: 81)` — **dvotočka** pred stranicom, bez „str.", godina bez točke | s uvlakom, `Prezime, Ime (Godina) Naslov. Mjesto: Nakladnik.` |
| `apa-hr` (EFZG) | `(Čavlek, 1998., str. 41)` | bez uvlake, **zarez** iza godine, bez završne točke |
| `ieee` | `[1]`, `[2, 3]`, `[4]–[6]` | brojčani popis prema redoslijedu citiranja |
| `vancouver` (HKS-FZS, MEF) | `(12)`, `(12, 15)`, `(12–15)` — ovalne zagrade, en-crtica u rasponu, razmak iza zareza, prije interpunkcije | `1. Autor A, Autor B. Naslov. Časopis. 2020;12(3):45–50.`, „i sur." nakon 6 autora, po redoslijedu prvog pojavljivanja |
| `legal-footnote` | nadredni broj fusnote | fusnota može sadržavati literaturu, propis, sudsku odluku ili EU akt |

Pravila koja vrijede svugdje:

- **Točan locator uz specifičnu tvrdnju.** Za literaturu je to najčešće stranica; za pravne izvore članak/stavak/točka ili oznaka odluke prema uputama fakulteta.
- Citat ide **odmah uz tvrdnju**, ne na kraj odlomka.
- `(ibid.)` se ne koristi u tekstu.
- **Stranica koja postoji, ali nije potvrđena → `[PROVJERI STR.]`**, i završi u tablici
  „RUČNO PROVJERI". To je PRIVREMENO stanje: lokator čeka provjeru iz same datoteke.
- **Izvor koji stranicu uopće nema se locira po odlomku** — `(Autor, godina: odl. 3)`,
  odnosno `(N, odl. 3)` u numeričkim dijalektima. To je TRAJNO stanje i gotov lokator:
  `[PROVJERI STR.]` ondje ne stoji jer nema što čekati. Vrijedi za mrežne izvještaje,
  HTML članke, institucijske objave i svaki `.txt`/`.md` bez tiskanog prijeloma.
- Tvrdnja koje nema u priloženoj građi → `[TREBA IZVOR]`. **Ništa se ne izmišlja.**

Dopušteni izvori, statusi `verify_sources.py` (`verified/unverified/conflict/invalid`),
taksonomija A–X, produbljivanje bez izmišljanja, evidence i claim ledger te B13 rewrite gate:
`references/pisanje_dokazi.md`. **Otvori ga prije nego ijedna nova tvrdnja s izvorom uđe u
tekst** i prije svake izmjene cijelog `.docx`-a. Ukratko: Google Scholar je discovery
servis, ne izvor; `conflict`/`invalid` ne ulaze u rad; `unverified` ide u RUČNO PROVJERI.

## 3. Stil

Formalan analitički ton, treće lice, bez kolokvijalizama. Precizni pojmovi
(„institucionalni okvir", „normativni okvir") umjesto praznih apstrakcija. Logički
konektori između rečenica i odlomaka. Umjereno duge, argumentacijski bogate rečenice —
ni telegrafske ni nerazumljive.

**Zabranjene prazne fraze:** „kroz povijest", „od davnina", „u današnje vrijeme",
„neupitno je da", „svima je poznato", „od kada postoji čovječanstvo".

**Zabranjeni prazni šavovi:** „Nadalje", „Osim toga", „Također" — zauzimaju mjesto
veze, a ne nose je.

U tekstu rada nema bullet lista. Povezani odlomci. Liste su dopuštene samo u
meta-komentarima i uputama, nikad u samom radu.

### 3.0 Prije prve rečenice: razina i glas autora

**Prvo razina.** Ona odlučuje koji se pojam definira, a koji pretpostavlja:

```bash
python3 <KATEDRA_SKILL>/scripts/razina.py
```

Šest obveza iz ispisa (SMIJE SE PRETPOSTAVITI / DEFINIRAJ / PRETPOSTAVI / OMJER /
DOPRINOS / REČENICA) ulaze u pisanje jednako obvezujuće kao kućni stil. Niža razina nije
lošiji rad nego rad koji više objašnjava i manje tvrdi — ništa u njoj ne dopušta manje
izvora ni slabiju provjeru. Puni protokol i sudari: `references/razina.md`.

### 3.0a Prije prve rečenice: pročitaj glas autora

Ako postoji `.katedra/stil_autora.json`, njegov popis `izbjegavaj` obvezuje jednako kao
kućni stil fakulteta (v. `references/stil_autora.md`). Nema smisla pisati konstrukciju
koju je autor prošli put ručno brisao.

**Konstrukcije koje se ne pišu jer ih autori dosljedno brišu ili kvare:**

| Ne piši | Piši | Zašto |
|---|---|---|
| apozicija između dviju en crtica: „na pet sektora – vojni, politički i okolišni – od kojih…" | „na pet sektora: vojni, politički i okolišni. Svaki od njih…" | autor ju je pokušao pojednostaviti dvotočkom, izgubio zatvornu crticu i ostavio otvorenu apoziciju |
| ograde: „doduše", „svakako", „zapravo", „dakako" | rečenica bez ograde | ne nose značenje; autori ih brišu prvo |
| polja na naslovnici kojih nema u profilu ni u uzoru („Kolegij:") | samo ono što profil ili uzorak mentora izrijekom traže | dodano „jer koristi", obrisano pri prvom čitanju |

Pravilo iza tablice: **konstrukcija koju autor mora popraviti prilika je da nešto pokvari.**
Tri od pet ručnih zahvata na jednom eseju bile su tipografske regresije — spojnica umjesto
en crtice u rasponu stranica, dvotočka bez razmaka, spojnica u rasponu godina koja je
razbila slaganje natpisa s popisom grafikona. Nijednu od njih autor ne bi napravio da mu
rečenica nije smetala.

### 3.0b Sažetak se piše zadnji i provjerava protiv rada

Postupak i paritetna tablica: `references/pisanje_dokument.md` §3.0b
(`provjeri_sazetak.py ./rad.docx --tablica`).

### 3.1 Radni modovi

- **SEMINAR** — 1.500–3.000 riječi, 2–4 poglavlja razrade, 5–10 izvora, fokus na jednom problemu.
- **DIPLOMSKI** — opseg po uputama, dubinska teorija + empirija, metodološki odjeljak, 30+ izvora, koherentnost argumenta kroz cijeli rad.
- **BRUTAL PRECISION** — maksimalna ekonomičnost, svaka rečenica nosi argumentacijsku vrijednost. Za sažetke, recenzije i zahtjevne sekcije.

Deklariraj mod u sažetku prije prvog odlomka.

---

## 4. Self-check nakon svakog potpoglavlja

Prije nego što potpoglavlje proglasiš napisanim:

- [ ] Je li **strict evidence gate PASS** za claimove koji ulaze u ovo potpoglavlje (Source Analysis Matrix bez `unsupported/conflicted/contradicted`)?
- [ ] Je li svaka tvrdnja objašnjena i kontekstualizirana, a ne samo iznesena?
- [ ] Jesu li citati u formatu iz profila, s točnom stranicom?
- [ ] Razvija li se argument, ili se samo nižu informacije?
- [ ] Ima li svaki odlomak tematsku rečenicu i prijelaz?
- [ ] Je li izbjegnuta generička frazeologija (§3)?
- [ ] Nosi li potpoglavlje tezu iz plana, ili je otišlo svojim putem?
- [ ] Je li `provjeri_jezik.py` čist od ❌ nalaza (pravopis i gramatika)?
- [ ] Je li ijedan pojam definiran **suprotno razini** — poznat pojam objašnjen ili uži pojam pretpostavljen (`razina.py`)?
- [ ] Jesu li **otvorene zamjerke mentora** za ovo mjesto riješene?

```bash
python3 <KATEDRA_SKILL>/scripts/extract_comments.py --otvorene .katedra/zamjerke.json
```

**Zatvaranje zamjerki, ne samo bilježenje.** `extract_comments.py` zamjerke OTVARA;
zatvaranje ide kroz `scripts/zamjerke.py`, ne ručnim uređivanjem `zamjerke.json` — ručni upis
ne ostavlja trag zašto je nešto proglašeno riješenim:

```bash
python3 <KATEDRA_SKILL>/scripts/zamjerke.py resolve z23 --status rijeseno \
    --napomena "Dodan odlomak o posljedicama tjelesnog zlostavljanja, poglavlje 3.1."
python3 <KATEDRA_SKILL>/scripts/zamjerke.py provjeri
```

Treći status, `djelomicno`, je za zamjerke adresirane, ali s odlukom koju alat ne smije
donijeti umjesto autora (npr. „treba li sekundarno referiranje" je studentska odluka).
`provjeri` vraća izlazni kod 1 dok god išta ostaje `otvoreno` — koristi kao blokirajuću
provjeru prije mod 6.

Nakon većeg bloka (poglavlje i više):

```bash
python3 <KATEDRA_SKILL>/scripts/check_ai_style.py ./ch4.md
python3 <KATEDRA_SKILL>/scripts/check_argument.py ./rad.docx --profil ./.katedra/resolved_profile.json
```

---

## 5. Poboljšanje postojećeg teksta (mod 3)

**Ne kreći prepisivati prije mjerenja.** „Zvuči robotski" nije jedna mana nego četiri
neovisne, a popravljanje jedne kvari drugu. Cijeli postupak, pragovi i predložak za
delegiranje su u **`references/stil_pipeline.md`** — obavezno pročitaj prije zahvata.

Kratko: izmjeri → ukloni tikove → poveži → prelomi predugo → geometrija odlomaka.
Nakon svakog koraka ponovno izmjeri i pokreni `verify_rewrite.py` s odgovarajućim
`--zahvat --profil ../.katedra/resolved_profile.json`, kako bi se očuvao upravo deklarirani citatni stil. **Nikad sve odjednom.**

Dijagnoza prije prijedloga, prijedlog prije prepisivanja. Prepisivanje bez potvrde
tona je najbrži način da tekst postane točan i mrtav.

---

## 6. Isporuka

Na kraju svake veće isporuke — tablica **„RUČNO PROVJERI"**:

| što | gdje | zašto |
|---|---|---|
| sva `[PROVJERI STR.]` | popis mjesta | stranica nije potvrđena iz izvora |
| sva `[TREBA IZVOR]` | popis mjesta | tvrdnja nema potporu u građi |
| pretpostavke za mentora | | odluke koje je Katedra donijela sama |
| pravila fakulteta sa `status: nepotvrdeno` | | treba potvrditi iz službenih uputa |
| otvorene zamjerke | `zamjerke.json` | još nisu vidljivo riješene u tekstu |

Tekst gotov → mod 4 (`references/audit.md`). Odstupanja od plana upiši prije toga:
`plan_state.py odstupanje --sto … --zasto …`.

Obojani prikaz izmjena (`revizije.py redline`) i lanac redoslijeda zahvata nad tekstom
(renumeracija literature → tekst → tipografija → naslovnice → sekcije → polja):
`references/pisanje_dokument.md`.

---

## Tijek moda — sažeto

> Ovo je bilo u routeru (`SKILL.md` § 2) do v1.7.
> Tijek jednog moda ne treba biti u datoteci koja se učitava u svakoj poruci.

`pisanje.md`. `nastavi rad` = uzmi prvo potpoglavlje iz `plan.json` sa `status: nije-napisano` (`python3 <KATEDRA_SKILL>/scripts/plan_state.py next`), ne pitaj gdje smo stali. Self-check nakon svakog potpoglavlja, pa upiši status i broj riječi.
