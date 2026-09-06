# Indeks kataloga zamki

> Generirano iz `references/zamke.md` skriptom `scripts/indeks_zamki.py`.
> **Ne uređuj ručno.** Nakon izmjene kataloga: `indeks_zamki.py --upisi`.
> `bin/testovi.sh` pada ako je ovaj indeks zastario.

Unosa: **84** (isti broj javlja `kvar.py --provjeri`) · uz njih 5 nenumeriranih odjeljaka · s ogradom: **59** · ograda ne pripada (deklarirano): **12** · **duguje ogradu: 18**

Traži bez učitavanja cijelog kataloga:

```bash
python3 katedra-lite/scripts/indeks_zamki.py --trazi 'gate'
sed -n '844,880p' katedra-lite/references/zamke.md   # unos po retku
```

| # | Naslov | Dodiruje | Ograda | Redak |
|---|--------|----------|--------|-------|
| 24 | Ključ s vrijednošću `null` nije „profil to ne propisuje", pa resolver pada i gate tiho … | `fpzg.json`, `_schema.json`, `_resolved_schema.json` | ✅ | 10 |
| 25 | Satelit se traži u četiri putanje, a peta (`synced/<hash>/`) je ona u kojoj Cowork živi | `build_docx.py`, `test_stari_kvarovi.py`, `vjestine.py` | ✅ | 33 |
| 26 | `meta` se koristi u `_renderiraj` koji ga nikad nije primio | — | — | 51 |
| 27 | Grana `startswith('popis')` hvata prije `'popis literature'`, pa rukopis dobiva fantoms… | `check_placeholders.py`, `sazetak.md`, `ideje.md` | — | 67 |
| 28 | Izlazni kod se računa iz broja simbola, a ne iz toga smije li simbol blokirati | `check_rules.py`, `zasto.md` | — | 85 |
| 29 | Kućni stil završnog rada primjenjuje se na seminarski jer uvjet zna samo fakultet, ne t… | `vjestine.json`, `sastavi.py`, `gradi.sh` | — | 104 |
| 30 | Numerički stil u ovalnim zagradama ne postoji, pa rad sa 75 referenci prolazi kao rad b… | `citation_dialects.py`, `_schema.json`, `check_citations.py` | ✅ | 124 |
| 31 | Popis naslova popisa literature je zatvoren, pa nepoznat naslov ruši gate umjesto da ja… | `provjeri_literaturu.py`, `fixture_popis_citirane_literature.docx`, `test_stari_kvarovi.py` | ✅ | 144 |
| 32 | Admisija profila traži datoteku koju isporučeni paket ne nosi, pa se hash ne može osvje… | `fpzg.json`, `faculty_scale_gate.py`, `v1_vs_v2_contract.json` | ⚪ | 161 |
| 33 | Shema opsega zna samo ukupni rad, pa se pravila po dijelovima ne mogu ni zapisati ni pr… | `provjeri_hks_fzs.py`, `hks-fzs.json`, `provjeri_dijelove.py` | ✅ | 182 |
| 34 | Faza bez svog artefakta je „nezapočeta" i kad je rad došao gotov | `napredak.py`, `plan.json` | — | 200 |
| 35 | Pravilo „godina s točkom" mjeri se i na stilu u kojem je točka iza godine kraj reference | `provjeri_literaturu.py`, `fixture_popis_citirane_literature.docx` | ⚪ | 215 |
| 36 | Skill za učenje dokumentira dvije zastavice koje njegove skripte nemaju | `SKILL.md`, `kvar.py`, `dokaz.py` | ✅ | 234 |
| 37 | Katalog na koji se skill poziva ima 23 unosa, opis vlasnika kaže 31, a učenje citira 32… | `SKILL.md`, `zamke.md`, `kvar.md` | ✅ | 254 |
| 38 | Nepotvrđen izvor dobiva simbol i obrazloženje, ali nijednu naredbu čovjeku, pa se nalaz… | `verify_sources.py`, `kvar.md` | — | 274 |
| 39 | Doktrina ne poznaje lokator koji kod već proizvodi, pa se gotov citat tretira kao nedov… | `evidence_ingest.py`, `SKILL.md`, `pisanje.md` | ✅ | 305 |
| 40 | `inline_shapes` ne vidi sliku koju je autor povukao mišem, pa alat javi „nema što mjeri… | `provjeri_prikaze.py`, `check_rules.py` | — | 332 |
| 41 | Uvod na razini Heading 2 prijavljuje se kao „rad nema tezu" | `check_argument.py` | — | 366 |
| 42 | Alat za dokazivanje popravaka ne poznaje smjer tihog kvara koji sam skill proglašava pr… | `SKILL.md`, `dokaz.py`, `provjeri_prikaze.py` | — | 393 |
| 43 | Doktrina je za 403 na pushu upućivala na read-only GitHub konektor, pa je popravak bio … | `SKILL.md` | ✅ | 421 |
| 44 | Čitač kriterija „zadatak" nije imao granu ispunjeno, pa je pojas 5 bio nedosežljiv svak… | `rubrika.py`, `zadatak.json`, `provjeri_predaju.py` | ✅ | 451 |
| 45 | Opseg se procjenjuje uz pretpostavku A4, a format papira nitko ne mjeri | `check_rules.py` | — | 493 |
| 46 | `_empirijski` se hrani statusom dijela koji time postaje ključan | `stanje.json` | — | 517 |
| 47 | Lokator dokaza poznaje samo stranicu, pa standardi i propisi ispadaju iz lanca | `claim_ledger.py`, `SKILL.md` | ✅ | 546 |
| 48 | Cross-chapter provjera gleda samo tvrdnje iz lanca, pa proturječje u vlastitim brojkama… | `consistency_check.py` | — | 570 |
| 49 | `drift.py` mjeri samo SKILL.md, a kartica i repo razilaze se i u `scripts/` | `drift.py`, `SKILL.md` | ✅ | 597 |
| 50 | Primjerak mjeri veličinu pisma iz natpisa prikaza, jer odlomci tijela nemaju izričitu v… | `primjerci.py`, `resolved_profile.json` | ✅ | 625 |
| 51 | Redni broj pravne reference pred velikim slovom lomi rečenicu, pa se mjeri ritam kojega… | `common.py` | ✅ | 647 |
| 52 | `re.IGNORECASE` gasi strukturni znak, pa svaki izvor s provenijencijom postaje tuđe aut… | `test_stari_kvarovi.py` | ✅ | 669 |
| 53 | Rep predaje pripada vrsti rada, a čitao se s razine fakulteta, pa svaki seminarski kasni | `tempo.py`, `efzg.json`, `napredak.py` | ✅ | 697 |
| 54 | Kartica `katedra-lite` nosi samo `SKILL.md`, a router imenuje 44 datoteke koje ne nosi | `SKILL.md`, `gate.py`, `rubrika.py` | ✅ | 717 |
| 55 | `SKILL.md` spremljen kao dopuna gubi router; tri skilla su se tako okrnjila | `SKILL.md` | ✅ | 777 |
| 56 | Doktrina o gateovima postojala je u dva skilla i nikad nije prešla u `katedra-lite` | `check_fields.py`, `rubrika.py`, `provjeri_predaju.py` | — | 801 |
| 57 | `VERSION` zaostaje za commitom, a § 0.0 taj broj ispisuje kao prvo što sesija kaže | `env.sh` | ✅ | 827 |
| 58 | gate je zeleno javljao fazu u kojoj se ništa nije pokrenulo | `gate.py`, `rad.docx`, `test_gate.py` | ✅ | 853 |
| 59 | faza audit nije pokretala audit | `audit.md`, `test_gate.py` | ✅ | 881 |
| 60 | `provjeri_predaju.py` nije bio korak nijednog gatea | `provjeri_predaju.py`, `predaja.md`, `rubrika.py` | ✅ | 895 |
| 61–63 | audit koji se smije ignorirati | `generate_report.py`, `audit_all.py` | — | 906 |
| 64–66 | klase pogrešaka koje nijedan alat nije gledao | `pipeline.md`, `test_all.py` | ✅ | 918 |
| 67–70 | lažni nalazi koji su gate činili neupotrebljivim | — | ✅ | 932 |
| 71 | faza A bez izvršitelja | `SKILL.md`, `check_placeholders.py` | — | 952 |
| 72–73 | alat za provjeru tvrdnji bio je i sam tvrdnja bez pokrića | `engine_contract.json`, `test_all.py`, `SKILL.md` | — | 961 |
| 74 | Trajna napomena o metodi nosila je znak ⚠, pa je svaki rad — i savršeno čist — imao bar… | `check_citations_authoryear.py`, `generate_report.py`, `kvar.py` | — | 972 |
| 75–78 | prvi prolaz kroz STVARNI rad | `test_all.py` | ✅ | 997 |
| 79 | popis literature gutao je sve iza sebe | — | ✅ | 1027 |
| 80–86 | tri stavke koje su ostale nakon v1.9.5 | `izmjeri.py`, `prelomi.json`, `natpisi.json` | ✅ | 1040 |
| — | Nova faza D2 i B2 — dvije klase koje nijedan alat nije gledao | `check_tvrdnja_izvor.py`, `cross_check.py`, `mapa.json` | ✅ | 1080 |
| 87–90 | drugi stvarni rad, druga vrsta rada | — | ✅ | 1107 |
| 91 | pravni rad: svaka jedinica iz popisa bila je siroče | `provjeri_fusnote.py` | ✅ | 1150 |
| 92 | najveći izvor šuma u paketu, nađen tek na stvarnom empirijskom radu | `provjeri_fusnote.py` | ✅ | 1192 |
| — | Korpus na kojem je lanac provjeren | — | ⚪ | 1236 |
| 93–97 | tehnički radovi: popis literature u tri neprepoznata oblika | — | ✅ | 1253 |
| — | Korpus na kojem je lanac provjeren (šest radova, pet fakulteta, četiri stila) | — | ⚪ | 1296 |
| 98–104 | audit paketa nakon rada Znahor | `AUDITskillovanakonradaZnahor.md`, `check_paragraphs.py`, `verify_rewrite.py` | — | 1315 |
| 105 | metapodaci: cijela razina dokumenta koju nitko nije gledao | `provjeri_metapodatke.py` | ✅ | 1396 |
| 106–107 | zatvaranje popisa iz prve dijagnoze | `parafraza.py`, `propagacija.py`, `brojke_iz_rasprave.py` | ✅ | 1863 |
| — | Što lanac i dalje NE provjerava | `check_argument.py`, `stil_pipeline.md` | ⚪ | 1900 |
| 108–111 | zatvaranje popisa „što lanac NE provjerava" | `check_statistika.py`, `check_tablice.py`, `check_hipoteze.py` | ✅ | 1923 |
| — | Što OSTAJE nepokriveno, i zašto | `faculty_scale_gate.py`, `v1_vs_v2_contract.json` | ⚪ | 1985 |
| 112 | „nije se pokrenula" i „ne odnosi se na ovaj rad" bili su isto stanje | `check_tvrdnja_izvor.py`, `mapa.json` | ✅ | 2006 |
| 113 | `kvar.py` je poznavao samo jedan broj po unosu, pa je grupirani unos bio ili nevidljiv … | `kvar.py` | ✅ | 2053 |
| 114 | Katalozi kvarova nisu bili u jedinom ulazu za testove, pa je suite bio zelen nad pokvar… | `testovi.sh`, `kvar.py` | ✅ | 2090 |
| 115 | Otisak motora hashirao je bajtove radnog stabla, pa je isti commit imao dva otiska ovis… | `engine_contract.json`, `testovi.sh`, `test_all.py` | ✅ | 2108 |
| 116 | Naslov u obliku koji registar ne čita bio je tišina, pa je „sljedeći slobodan” pokaziva… | `kvar.py`, `kvar.md`, `test_kvar.py` | ✅ | 2139 |
| 117 | provjera tvrdnji gledala je samo jedan smjer | `generate_report.py`, `check_hipoteze.py`, `check_XXXXX.py` | ✅ | 2180 |
| 118 | Opis skilla je površina odluke, ne changelog | — | ⚪ | 2220 |
| 119 | Provjera tvrdnji rušila se na hrvatskoj konzoli, pa je nalaz koji je NAŠLA izlazio kao … | `check_hipoteze.py`, `testovi.sh` | ✅ | 2252 |
| 120 | Brojka „31 stvarni kvar” stajala je u opisu nad katalogom od 26, a kvar 37 ju je zapisa… | `SKILL.md`, `zamke.md`, `test_zakrpa.py` | ✅ | 2291 |
| 121 | mjerilo je palo, a zaključak je htio pasti na opis | `pokreni_trigger.py`, `trigger_rezultat.json` | ✅ | 2329 |
| 122 | Indeks kataloga čitao je tuđi oblik naslova, a ne svoj, pa je jedanaest unosa izgubilo … | `indeks_zamki.py`, `test_indeks.py`, `testovi.sh` | ✅ | 2427 |
| 123 | „VERSION ne smije zaostajati” bila bi provjera crvena u 28 od 32 stanja, pa je mjerena … | `env.sh`, `test_verzija.py`, `testovi.sh` | ✅ | 2471 |
| 124 | Mjerilo usmjeravanja nije znalo reći da nije moglo mjeriti, i mjerilo je samo jedan uvj… | `drift.py`, `SKILL.md`, `pokreni_trigger.py` | ✅ | 2531 |
| 125 | Broj testova u izvještaju bio je ukovana konstanta, pa je suite tvrdio 6/6 dok je pokre… | `SKILL.md`, `test_zakrpa.py`, `test_kvar.py` | ✅ | 2576 |
| 126 | Provjera tvrdnji tražila je skripte samo u `scripts/`, pa je alat koji postoji prijavil… | `pokreni_trigger.py`, `SKILL.md`, `test_zakrpa.py` | ✅ | 2617 |
| 127 | `drift.py` je karticu koja je uredno jednu verziju iza optuživao da je ručno mijenjana | `drift.py`, `test_drift.py` | ✅ | 2649 |
| 128 | Provjera je potvrdila alat koji se onda nije dao pokrenuti, a neuspjeh je izgledao kao … | `test_trigger.py` | ✅ | 2719 |
| 129 | zbroj po fazama nije trošak jednog rada | `mjera.py`, `SKILL.md` | ✅ | 2785 |
| 130 | Predviđanje iz kvara 121 opovrgnuto mjerenjem: opis nije bio uzrok, prazna mapa jest | `drift.py`, `trigger_evals.json` | ⚪ | 2825 |
| 131 | Prolaz koji je pukao brojio se kao prolaz u kojem skill nije okinuo | `test_trigger.py` | ✅ | 2870 |
| 132 | Popis unosa „bez ograde” mjerio je oblikovanje, ne dug: 47 od 79 naspram izmjerenih 34 | `test_drift.py`, `test_indeks.py` | ✅ | 2901 |
| 133 | kartica i repo razišle su se u jednoj brojci, i ta je brojka lokator | `SKILL.md`, `drift.py`, `zamke.md` | ✅ | 2947 |
| 134 | doktrina je za Cowork ostavila otvorena vrata kojih nema | `SKILL.md` | ✅ | 3031 |
| 135 | Provjera „broj kvara mora postojati” nije čitala kanonski raspon — treći put isti uzorak | `SKILL.md`, `test_zakrpa.py` | ✅ | 3063 |
| 136 | Odziv 6/12 nije bio nalaz o opisu nego o praznoj mapi — mjereno na svih dvanaest upita | `rad.docx` | ⚪ | 3098 |
| 137 | Popravljena je brojka u zaglavlju, a iste dvije naredbe nastavile su dijeliti brojem re… | `indeks_zamki.py`, `kvar.py`, `test_indeks.py` | ✅ | 3139 |
| 138 | Mjerena je samo strana koja je mogla porasti; kad je izmjerena i druga, prag se nije po… | `rad.docx` | ⚪ | 3178 |
| 139 | „Bez ograde” je bio jedan pretinac za tri stanja, pa popis duga nije bio popis posla | `test_indeks.py` | ⚪ | 3228 |
| 140 | Dvadeset šest unosa duguje ogradu; izmjereno je koliko ih uopće ima test koji ih dodiru… | `kvar.md`, `SKILL.md` | ⚪ | 3267 |
| 141 | Prvih pet novih ograda bile su lažne, i to je pokazala mutacija, ne čitanje | `vjestine.py`, `test_stari_kvarovi.py`, `testovi.sh` | ✅ | 3313 |

## Unosi bez ograde

Nemaju regresijski test i **nisu rekli zašto**. Unos kojemu ograda ne
pripada (mjerenje, bilješka o korpusu) to smije reći rečenicom
„Ograda: nema — <razlog>” i tada ovdje ne stoji; razlog je obavezan,
jer bi inače deklaracija bila način da se dug sakrije. Ovaj popis je
posao, ne stanje.

- 26 — `meta` se koristi u `_renderiraj` koji ga nikad nije primio (redak 51)
- 27 — Grana `startswith('popis')` hvata prije `'popis literature'`, pa rukopis dobiva fantomske naslove (redak 67)
- 28 — Izlazni kod se računa iz broja simbola, a ne iz toga smije li simbol blokirati (redak 85)
- 29 — Kućni stil završnog rada primjenjuje se na seminarski jer uvjet zna samo fakultet, ne tip (redak 104)
- 34 — Faza bez svog artefakta je „nezapočeta" i kad je rad došao gotov (redak 200)
- 38 — Nepotvrđen izvor dobiva simbol i obrazloženje, ali nijednu naredbu čovjeku, pa se nalaz preskače (redak 274)
- 40 — `inline_shapes` ne vidi sliku koju je autor povukao mišem, pa alat javi „nema što mjeriti" (redak 332)
- 41 — Uvod na razini Heading 2 prijavljuje se kao „rad nema tezu" (redak 366)
- 42 — Alat za dokazivanje popravaka ne poznaje smjer tihog kvara koji sam skill proglašava prioritetom (redak 393)
- 45 — Opseg se procjenjuje uz pretpostavku A4, a format papira nitko ne mjeri (redak 493)
- 46 — `_empirijski` se hrani statusom dijela koji time postaje ključan (redak 517)
- 48 — Cross-chapter provjera gleda samo tvrdnje iz lanca, pa proturječje u vlastitim brojkama prolazi (redak 570)
- 56 — Doktrina o gateovima postojala je u dva skilla i nikad nije prešla u `katedra-lite` (redak 801)
- 61–63 — audit koji se smije ignorirati (redak 906)
- 71 — faza A bez izvršitelja (redak 952)
- 72–73 — alat za provjeru tvrdnji bio je i sam tvrdnja bez pokrića (redak 961)
- 74 — Trajna napomena o metodi nosila je znak ⚠, pa je svaki rad — i savršeno čist — imao barem jedan „na… (redak 972)
- 98–104 — audit paketa nakon rada Znahor (redak 1315)
