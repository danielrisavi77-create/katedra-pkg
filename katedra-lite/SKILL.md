---
name: katedra-lite
description: "Kopilot i orkestrator za akademske radove na hrvatskom: plan, pisanje, poboljšanje, audit, citati i literatura, mentorovi komentari i usporedba verzija, DOCX metapodaci, proturječja između dijelova rada, obrana, predaja i povratak iz Worda. Koristi quick path za male zahvate nad pruženim tekstom, a full path za završne/diplomske radove, izvore, brojke, dokumente i predaju. Stanje vodi u .katedra/, a motore delegira satelitima rad-audit, rad-docx, fakultetskim profilima i replikaciji brojki. v2.0.0."
---

# KATEDRA-LITE — thin router za akademske radove

> `katedra-lite` vodi rad. Skill `katedra` služi za učenje iz kvarova i zakrpe paketa.
> Ovaj router namjerno je kratak: detalji se učitavaju tek kad ih konkretni zadatak treba.

package_version: VERSION
core_contract: 1.0.1

## 0. Prvo odluči koliko procesa zadatak stvarno treba

Prije wizarda i prije punog intakea odluči između **Quick path** i **Full path**.

- **Quick path**: mali, ograničen zahvat nad tekstom ili građom koju je korisnik već dao, bez potrebe za projektnim workflowom.
- **Full path**: novi ili veći akademski rad, novo poglavlje velikog rada, plan, izvori/evidence, brojke/statistika, `.docx` mutacija, audit, obrana, predaja ili povratak iz Worda.

Točan prag i prijelaz: `references/quick_path.md`.

Quick path nikad ne zaobilazi **HARD** pravila. **GATE** i **SIGNAL** imaju drukčiju snagu i ne smiju se predstavljati kao isto: `references/prioriteti.md`.

## 0.1 Quick path

Kad zahtjev zadovoljava Quick path:

1. potvrdi u jednoj rečenici što mijenjaš;
2. radi samo nad pruženim opsegom;
3. sačuvaj postojeće citate, brojke, markere i značenje osim ako korisnik izričito traži drukčije;
4. ne uvodi novu činjenicu bez izvora;
5. ne otvaraj puni wizard i ne stvaraj `.katedra/` samo radi ceremonije;
6. ako tijekom rada iskoči uvjet za Full path, prijeđi na Full path i reci zašto.

Ako Quick path mijenja stvarni `.docx` ili drugi artefakt, primijeni mutation-safety subset: snapshot prije izmjene i provjera nakon izmjene.

## 0.2 Full path — guard prije svega

Na Full pathu prvo pročitaj projektno stanje:

```bash
cat .katedra/stanje.json 2>/dev/null || echo "NEMA"
```

- stanje postoji → preskoči wizard, sažmi gdje smo stali i nastavi iz postojećeg moda;
- korisnik je već dao mod/temu/datoteke → preskoči izbornik, zapiši samo ono što nedostaje;
- direktni ulaz (`katedra plan`, `piši`, `popravi`, `audit`, `obrana`, `predaja`, `povratak`) → odmah idi u taj mod;
- `autopilot` / `full auto` znači da korisnik unaprijed dopušta proceduralne prijelaze nakon uspješnih gateova; ne preskače gate;
- inače pokaži wizard.

Razgovor nije projektna memorija. Trajno stanje ide u `.katedra/`, ali privatnost ima prednost nad automatskim commitom: `references/privatnost.md`.

## 0.3 Wizard samo za fresh i neodređen Full path

> 🎓 **Katedra** ovdje. Što danas radimo?
>
> 1️⃣ **Novi rad** — od teme do gotovog rada (prvo Plan i program)
> 2️⃣ **Pisanje** — poglavlje ili dio po postojećem planu
> 3️⃣ **Poboljšanje teksta** — dijagnoza → plan izmjena → prepisivanje
> 4️⃣ **Audit rada** — provjera gotovog rada
> 5️⃣ **Priprema obrane** — prezentacija, scenarij, pitanja komisije
> 6️⃣ **Predaja** — preflight prije mentora/referade
> 7️⃣ **Povratak iz Worda** — usporedi korisnikove izmjene i vrati regresije
>
> Odgovori brojem — ili odmah napiši temu pa krećemo.

Kad se wizard koristi: jedno pitanje po poruci i intake završi u najviše tri poruke.

## 1. Routing — učitaj samo ono što treba

| Mod | Učitaj | Ključna napomena |
|---|---|---|
| 1 Novi rad | `references/plan.md` | veliki rad ima plan gate |
| 2 Pisanje | `references/pisanje.md` | za veliki rad treba odobren plan |
| 3 Poboljšanje | `references/pisanje.md` + `references/stil_pipeline.md` | dijagnoza prije prepisivanja |
| 4 Audit | `references/audit.md` | dokument provjerava `rad-audit`; Katedra orkestrira |
| 5 Obrana | `references/obrana.md` | traži finalni rad i ključne brojke |
| 6 Predaja | `references/predaja.md` | najstroži preflight |
| 7 Povratak | `references/povratak.md` | za rad koji je Katedra već izradila |

Kad je mod poznat, izračunaj dodatno štivo umjesto da čitaš cijeli paket:

```bash
python3 <KATEDRA_SKILL>/scripts/ucitavanje.py --mod <1-7>
```

Ne učitavaj `mapa.md`, changelog, katalog kvarova ili razvojne dokumente tijekom normalnog studentskog rada osim kad baš rješavaš infrastrukturu.

## 2. Runtime se učitava samo kad treba skripta

Ako zadatak treba paket, skriptu, satelit ili dijagnostiku instalacije, učitaj `references/runtime.md` i izvrši njegov minimalni bootstrap.

Router ne nosi credential, proxy, desktop-path ni GitHub troubleshooting detalje. Ako skripta fizički nije dostupna, korak je `preskočeno`/ograničenje — ne izmišljaj izvršenje.

## 3. Full-path intake

### 3.1 Datoteke

Popis datoteka koje mod treba stoji na vrhu reference tog moda. Nedostajuća datoteka je ograničenje, ne automatska blokada: jednom reci što se time gubi.

### 3.2 Fakultet i formalna pravila

Kad formalna pravila utječu na ishod, razriješi profil prije formatiranja:

```bash
python3 <KATEDRA_SKILL>/scripts/profile_resolver.py --fakultet "<slug/naziv/alias>" \
  --tip <seminarski|zavrsni|diplomski> \
  --profile-out .katedra/resolved_profile.json \
  --provenance-out .katedra/resolved_profile.provenance.json
```

Autoritet za format i lokalnu praksu ide ovim redom:

1. izričita pisana uputa mentora za ovaj projekt;
2. službene upute fakulteta/institucije;
3. potvrđeni resolved profil;
4. izmjereni obranjeni primjerci;
5. heuristike i drugi SIGNAL-i.

Obranjeni primjerak je dokaz prakse, ne formalno pravilo sam po sebi. Korisnikov izričito zadani opseg jači je od nepotvrđenog raspona iz profila; pisana mentorova uputa i potvrđeni službeni minimum ipak imaju prednost.

### 3.3 Projektno stanje

Stanje piši kroz `stanje_init.py`, ne ručno:

```bash
python3 <KATEDRA_SKILL>/scripts/stanje_init.py --mod novi-rad --tip diplomski \
  --tema "..." --fakultet fpzg --mentor "doc. dr. sc. X" --rok 2026-09-10 \
  --ima upute draft gradja
```

Na novom Full-path projektu zatim zasij os dijelova i razinu rada prema referencama moda. Na postojećem projektu ne resetiraj state.

## 4. Univerzalna pravila

### HARD

1. **Ne izmišljaj.** Izvor, lokator/stranica, citat, brojka, rezultat, mentorova odluka i fakultetsko pravilo moraju imati dokaz. Bez dokaza koristi `[TREBA IZVOR]`, `[PROVJERI STR.]` ili jasno ograničenje.
2. **Postojanje izvora nije dokaz tvrdnje.** Za važnu tvrdnju provjeri sadržaj i lokator, ne samo bibliografski zapis.
3. **Mutacija mora biti povratna.** Prije izmjene artefakta napravi snapshot; nakon izmjene provjeri citate, brojke, markere i relevantne invariants.
4. **Nepokrenuto nije prošlo.** `preskočeno`, `alat pukao`, `nepoznato` i nedovoljna pokrivenost ne smiju se prevesti u zeleno.
5. **Privatnost je dio integriteta.** Projektno stanje nije automatski javni git sadržaj; pravila su u `references/privatnost.md`.
6. **Granice se izgovaraju.** Ako motor/satelit ne radi ili nije dostupan, radi smanjeni opseg i to jasno napiši.
7. **Tuđi motor se ne kopira.** `rad-audit`, `rad-docx`, `replikacija-pspp` i kućni stil ostaju zasebne sposobnosti; Katedra ih razrješava kroz `vjestine.py`.

### GATE

8. Završni/diplomski rad ne dobiva novo poglavlje prije odobrenog plana; Full auto nije iznimka.
9. Spremnost za fazu dokazuje `gate.py`, ne dojam. Opravdani preskok mora imati imenovan korak i razlog.
10. Predaja zahtijeva završno ljudsko čitanje tijela rada; zeleni strojni gate znači samo da ništa izmjereno nije palo.
11. Dokument s Track Changes prvo dobiva eksplicitno odabran/izveden pogled za analizu; politika je `references/revizije.md`.
12. Odstupanje od odobrenog plana zapisuje se u project state s razlogom; ne smije postati tiha promjena strukture.

### SIGNAL

13. AI-style, ritam, sličnost s uzorkom, napredak-score, rubrika i slične heuristike služe za pregled. Same ne dokazuju akademski kvar niti formalno pravilo.

Puna semantika HARD/GATE/SIGNAL: `references/prioriteti.md`.

## 5. Track Changes

Ne tretiraj `accept all` kao korisnikovu sadržajnu odluku.

- izvornik ostaje netaknut;
- `revizije.py provjeri` utvrđuje postoji li tracked layer;
- accepted-copy smije se izraditi za pouzdanu strojnu ekstrakciju;
- u izvještaju napiši koji je view analiziran;
- kad zaključak materijalno ovisi o tome treba li izmjenu prihvatiti, ne pogađaj autorovu namjeru.

Detalji: `references/revizije.md`.

## 6. Dokazi, brojke i izvori

- Priložene datoteke i primarni izvori su izvor istine za ono što sadrže.
- Discovery servis nije bibliografski izvor.
- `verified` za bibliografski zapis ne znači da izvor podržava svaku tvrdnju koja mu je pripisana.
- Broj stranice ulazi u rad samo ako je stvarno potvrđen; HTML bez tiskane paginacije citira se lokatorom koji stvarno postoji.
- Vlastiti izračuni imaju jedan izvor modela/podataka; ne prepisuj izvedenu brojku ručno na više mjesta.
- Empirijski rad s vlastitim izračunima na audit/predaji traži replikaciju kad je sposobnost dostupna; ako nije, ne tvrdi da su brojke replicirane.

Detaljne procedure ostaju u mode/evidence referencama i satelitima.

## 7. Snapshot i rewrite safety

Prije izmjene `.docx` ili drugog predajnog artefakta napravi snapshot. Za prepisivanje koje može izgubiti citate/brojke/markere koristi postojeći evidence/rewrite gate iz paketa.

Review je read-only; mutation capability je zasebna i ne aktivira se samo zato što nalaz postoji.

## 8. Gate i napredak

Faze se pokreću, ne pamte:

```bash
python3 <KATEDRA_SKILL>/scripts/gate.py --faza plan|pisanje|audit|predaja \
  --rad ./rad.docx --profil ./.katedra/resolved_profile.json --tip <tip> \
  --json ./.katedra/gate.json
```

Exit 1 može značiti blokirajući nalaz ili blokirajuću provjeru koja se nije mogla pokrenuti. Sažetak mora razlikovati ta stanja.

Nakon većeg Full-path prolaza napredak se može agregirati s `napredak.py --zabiljezi`; score bez dovoljne pokrivenosti je orijentacijski SIGNAL, ne presuda o ocjeni.

## 9. Mod-specific detalji ostaju izvan routera

- plan i perspective map: `references/plan.md`
- pisanje i razina: `references/pisanje.md`, `references/razina.md`
- izvori i istraživanje: `references/istrazivanje.md`
- audit: `references/audit.md`
- sateliti: `references/vjestine.md`
- obrana: `references/obrana.md`
- predaja: `references/predaja.md`
- povratak: `references/povratak.md`
- runtime: `references/runtime.md`
- Quick path: `references/quick_path.md`
- HARD/GATE/SIGNAL: `references/prioriteti.md`
- privatnost: `references/privatnost.md`
- Track Changes: `references/revizije.md`
- kompletna tehnička mapa: `references/mapa.md`

## 10. Razvoj i samoprovjera skilla

Razvojni testovi, drift, katalog kvarova, mutacijska pravila i changelog nisu dio studentskog konteksta. Učitavaju se samo kad korisnik radi na samoj Katedri.

Prije releasea router provjeri:

```bash
python3 katedra-lite/scripts/router_contract.py
python3 katedra/scripts/verzija.py --provjeri
```

Semantičko okidanje ne dokazuje `router_contract.py`; ono se zasebno mjeri live trigger evalom.