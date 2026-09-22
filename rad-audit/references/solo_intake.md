# rad-audit — ulazni protokol u načinu SOLO

<!-- Izdvojeno iz rad-audit/SKILL.md u v2.2.0 (thin router). Sadržaj nepromijenjen. -->

## 0. ULAZNI PROTOKOL (RadPilot v1) — SAMO U NAČINU SOLO

**Prvi output ovog skilla je wizard, ne pipeline i ne objašnjenje pipelinea.** Ne pokreći nijednu skriptu prije nego znaš opseg i imaš datoteke.

### 0.1 Guard — spriječi dupli intake

- Postoji blok `STANJE-RADA` (v. 0.4) ili je rad **već priložen** i opseg jasan? → **PRESKOČI wizard**, potvrdi jednom rečenicom i kreni na fazu A.
- Intake već odradila **katedra-lite** (v. 0.0)? → ne ponavljaj ga.
- Inače → 0.2.

### 0.2 Prva poruka (točno ovaj format)

> 🔍 **Audit rada** — pipeline A–G. Što provjeravam?
>
> 1️⃣ **Puni audit** (A–G) — integritet, citati, brojke, cross-check, jezik, formatiranje
> 2️⃣ **Citati i literatura** (faza B)
> 3️⃣ **Cross-check s izvorima** (faza D) — tvrdnje u radu vs. izvorna građa
> 4️⃣ **Jezik, stil, tipografija** (faza E)
> 5️⃣ **Word formatiranje i polja** (faza F) — SADRŽAJ, natpisi, praznine, „zaključane" tablice
>
> Odgovori brojem (default: 1) i priloži datoteke iz popisa ispod.

### 0.3 Datoteke — reci točno što uploadati

- 📄 **Rad u .docx** — **OBAVEZNO**. PDF ne prolazi: skripte čitaju .docx, iz PDF-a nema polja, stilova ni tracked changesa.
- 🗂️ **SVA izvorna građa** (izvješća, projekt, seminar, podaci, PDF-ovi literature) — **OBAVEZNO za fazu D**. Bez nje cross-check ne postoji i to moram deklarirati u izvještaju.
- 📜 **Upute fakulteta** (PDF) — bez njih provjeravam **dosljednost**, ne **usklađenost s pravilima**. Razlika mora biti jasna korisniku.
- 📝 **Komentari mentora** na raniju verziju, ako postoje.

Fali obavezna stavka → upozori **jednom**, navedi točno što se gubi, i pitaj želi li svejedno nastaviti u smanjenom opsegu. Građa veća od ~10 MB preko Drive konektora → traži upload ZIP-a u chat.

### 0.4 Sažetak + STANJE (ispiši prije prve skripte)

```
STANJE-RADA
mod: audit
opseg: <A-G|B|D|E|F>
tip: <seminarski|zavrsni|diplomski>
datoteke: rad<✅|❌> gradja<✅|❌> upute<✅|❌>
citatni-stil: <auto-detektiran: IEEE|Vancouver|autor-godina>
domena: <celik|elektro|strojarstvo|it|generic>
ogranicenja: <npr. nema izvorne građe → faza D preskočena>
```

### 0.5 Pravila intakea

- Intake gotov u **≤ 2 poruke**, numerirane opcije, bez zida teksta.
- Ništa se ne pita dvaput; ono što je već priloženo ili rečeno se samo potvrđuje.
- Nakon sažetka pokreni pipeline **bez čekanja odobrenja** za dijagnostiku (skripte su read-only). Odobrenje traži samo za **izmjene dokumenta** (faza G i `apply_safe_fixes.py`).

### 0.6 Isporuka i predaja (handoff)

- Kraj audita: izvještaj razvrstan **Kritično / Srednje / Kozmetičko** (`generate_report.py`) + tablica **„RUČNO PROVJERI"** (sve [PROVJERI STR.], pretpostavke za mentora, pravila fakulteta).
- Traži se prepisivanje većih dijelova → **katedra-lite mod 3** (poboljšanje; za FPZG učitava
  `references/glas_fpzg.md`), uz identičan skup citata i brojki.
- Rad ne postoji ili je tek u planu → **katedra-lite mod 1** (plan).
- Nakon audita ponudi pripremu obrane (**katedra-lite mod 5**).
- Aliasi `fpzg-skill-pisanje`, `plan-i-program`, `radpilot` više ne postoje kao samostalni skillovi.

---

> **Doktrina (rujan 2026.).** Ništa se u ovaj SKILL.md ne upisuje kao gotovo prije
> nego što postoji test koji to izvodi. Tri uzastopna unosa (R14, R15, R16) opisivala
> su popravke s izmjerenim brojkama, a u kodu ih nije bilo: `HEADING_RE` nije znao
> „Izvori i literatura", toggle navodnika i dalje je davao `„tekst„`, riječ
> `vancouver` nije se pojavljivala nigdje. Prije svake zakrpe pokreni
> `python3 <KATEDRA>/scripts/zakrpa.py --provjeri-tvrdnje <korijen skilla>` — uspoređuje
> sposobnosti iz manifesta, tvrdnje o broju testova i oznake kvarova s onim što
> test-suite stvarno sadrži. Changelog bez testa je fikcija, a fikcija u SKILL.md je
> gore od nedostajuće značajke: sljedeća sesija je ne provjerava.

Provjera radova u fazama A–G, uz **željezna načela**: izvor istine > dojam; sve verificiraj neovisno; ne izmišljaj; jasne pogreške ispravi odmah, stil tek uz potvrdu tona; nakon SVAKE izmjene ponovno provjeri citate/brojke/polja/validaciju.

Puni proces s objašnjenjima i katalogom zamki: **`references/pipeline.md`** (pročitaj ga prvi put).
Brza tipografska pravila: **`references/typography_hr.md`**.
