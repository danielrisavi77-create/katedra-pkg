# Indeks kataloga zamki

> Generirano iz `references/zamke.md` skriptom `scripts/indeks_zamki.py`.
> **Ne uređuj ručno.** Nakon izmjene kataloga: `indeks_zamki.py --upisi`.
> `bin/testovi.sh` pada ako je ovaj indeks zastario.

Unosa: **86** (isti broj javlja `kvar.py --provjeri`) · uz njih 5 nenumeriranih odjeljaka · s ogradom: **53** · ograda ne pripada (deklarirano): **10** · **duguje ogradu: 28**

Traži bez učitavanja cijelog kataloga:

```bash
python3 katedra-lite/scripts/indeks_zamki.py --trazi 'gate'
sed -n '844,880p' katedra-lite/references/zamke.md   # unos po retku
```

| # | Naslov | Dodiruje | Ograda | Redak |
|---|--------|----------|--------|-------|
| 24 | Ključ s vrijednošću `null` nije „profil to ne propisuje", pa resolver pada i gate tiho … | `fpzg.json`, `_schema.json`, `_resolved_schema.json` | — | 10 |
| 25 | Satelit se traži u četiri putanje, a peta (`synced/<hash>/`) je ona u kojoj Cowork živi | `build_docx.py` | — | 32 |
| 26 | `meta` se koristi u `_renderiraj` koji ga nikad nije primio | — | — | 49 |
| 27 | Grana `startswith('popis')` hvata prije `'popis literature'`, pa rukopis dobiva fantoms… | `check_placeholders.py`, `sazetak.md`, `ideje.md` | — | 65 |
| 28 | Izlazni kod se računa iz broja simbola, a ne iz toga smije li simbol blokirati | `check_rules.py`, `zasto.md` | — | 83 |
| 29 | Kućni stil završnog rada primjenjuje se na seminarski jer uvjet zna samo fakultet, ne t… | `vjestine.json`, `sastavi.py`, `gradi.sh` | — | 102 |
| 30 | Numerički stil u ovalnim zagradama ne postoji, pa rad sa 75 referenci prolazi kao rad b… | `citation_dialects.py`, `_schema.json`, `check_citations.py` | ✅ | 122 |
| 31 | Popis naslova popisa literature je zatvoren, pa nepoznat naslov ruši gate umjesto da ja… | `provjeri_literaturu.py`, `fixture_popis_citirane_literature.docx` | — | 142 |
| 32 | Admisija profila traži datoteku koju isporučeni paket ne nosi, pa se hash ne može osvje… | `fpzg.json`, `faculty_scale_gate.py`, `v1_vs_v2_contract.json` | — | 158 |
| 33 | Shema opsega zna samo ukupni rad, pa se pravila po dijelovima ne mogu ni zapisati ni pr… | `provjeri_hks_fzs.py`, `hks-fzs.json`, `provjeri_dijelove.py` | — | 178 |
| 34 | Faza bez svog artefakta je „nezapočeta" i kad je rad došao gotov | `napredak.py`, `plan.json` | — | 195 |
| 35 | Pravilo „godina s točkom" mjeri se i na stilu u kojem je točka iza godine kraj reference | `provjeri_literaturu.py`, `fixture_popis_citirane_literature.docx` | — | 210 |
| 36 | Skill za učenje dokumentira dvije zastavice koje njegove skripte nemaju | `SKILL.md`, `kvar.py`, `dokaz.py` | ✅ | 228 |
| 37 | Katalog na koji se skill poziva ima 23 unosa, opis vlasnika kaže 31, a učenje citira 32… | `SKILL.md`, `zamke.md`, `kvar.md` | ✅ | 248 |
| 38 | Nepotvrđen izvor dobiva simbol i obrazloženje, ali nijednu naredbu čovjeku, pa se nalaz… | `verify_sources.py`, `kvar.md` | — | 268 |
| 39 | Doktrina ne poznaje lokator koji kod već proizvodi, pa se gotov citat tretira kao nedov… | `evidence_ingest.py`, `SKILL.md`, `pisanje.md` | ✅ | 299 |
| 40 | `inline_shapes` ne vidi sliku koju je autor povukao mišem, pa alat javi „nema što mjeri… | `provjeri_prikaze.py`, `check_rules.py` | — | 326 |
| 41 | Uvod na razini Heading 2 prijavljuje se kao „rad nema tezu" | `check_argument.py` | — | 360 |
| 42 | Alat za dokazivanje popravaka ne poznaje smjer tihog kvara koji sam skill proglašava pr… | `SKILL.md`, `dokaz.py`, `provjeri_prikaze.py` | — | 387 |
| 43 | Doktrina je za 403 na pushu upućivala na read-only GitHub konektor, pa je popravak bio … | `SKILL.md` | ✅ | 415 |
| 44 | Čitač kriterija „zadatak" nije imao granu ispunjeno, pa je pojas 5 bio nedosežljiv svak… | `rubrika.py`, `zadatak.json`, `provjeri_predaju.py` | ✅ | 445 |
| 45 | Opseg se procjenjuje uz pretpostavku A4, a format papira nitko ne mjeri | `check_rules.py` | — | 487 |
| 46 | `_empirijski` se hrani statusom dijela koji time postaje ključan | `stanje.json` | — | 511 |
| 47 | Lokator dokaza poznaje samo stranicu, pa standardi i propisi ispadaju iz lanca | `claim_ledger.py`, `SKILL.md` | ✅ | 540 |
| 48 | Cross-chapter provjera gleda samo tvrdnje iz lanca, pa proturječje u vlastitim brojkama… | `consistency_check.py` | — | 564 |
| 49 | `drift.py` mjeri samo SKILL.md, a kartica i repo razilaze se i u `scripts/` | `drift.py`, `SKILL.md` | ✅ | 591 |
| 50 | Primjerak mjeri veličinu pisma iz natpisa prikaza, jer odlomci tijela nemaju izričitu v… | `primjerci.py`, `resolved_profile.json` | ✅ | 619 |
| 51 | Redni broj pravne reference pred velikim slovom lomi rečenicu, pa se mjeri ritam kojega… | `common.py` | ✅ | 641 |
| 52 | `re.IGNORECASE` gasi strukturni znak, pa svaki izvor s provenijencijom postaje tuđe aut… | — | — | 663 |
| 53 | Rep predaje pripada vrsti rada, a čitao se s razine fakulteta, pa svaki seminarski kasni | `tempo.py`, `efzg.json`, `napredak.py` | ✅ | 690 |
| 54 | Kartica `katedra-lite` nosi samo `SKILL.md`, a router imenuje 44 datoteke koje ne nosi | `SKILL.md`, `gate.py`, `rubrika.py` | ✅ | 710 |
| 55 | `SKILL.md` spremljen kao dopuna gubi router; tri skilla su se tako okrnjila | `SKILL.md` | ✅ | 770 |
| 56 | Doktrina o gateovima postojala je u dva skilla i nikad nije prešla u `katedra-lite` | `check_fields.py`, `rubrika.py`, `provjeri_predaju.py` | — | 794 |
| 57 | `VERSION` zaostaje za commitom, a § 0.0 taj broj ispisuje kao prvo što sesija kaže | `env.sh` | ✅ | 820 |
| 58 | gate je zeleno javljao fazu u kojoj se ništa nije pokrenulo | `gate.py`, `rad.docx`, `test_gate.py` | ✅ | 846 |
| 59 | faza audit nije pokretala audit | `audit.md`, `test_gate.py` | ✅ | 874 |
| 60 | `provjeri_predaju.py` nije bio korak nijednog gatea | `provjeri_predaju.py`, `predaja.md`, `rubrika.py` | ✅ | 888 |
| 61–63 | audit koji se smije ignorirati | `generate_report.py`, `audit_all.py` | — | 899 |
| 64–66 | klase pogrešaka koje nijedan alat nije gledao | `pipeline.md`, `test_all.py` | ✅ | 911 |
| 67–70 | lažni nalazi koji su gate činili neupotrebljivim | — | ✅ | 925 |
| 71 | faza A bez izvršitelja | `SKILL.md`, `check_placeholders.py` | — | 945 |
| 72–73 | alat za provjeru tvrdnji bio je i sam tvrdnja bez pokrića | `engine_contract.json`, `test_all.py`, `SKILL.md` | — | 954 |
| 74 | Trajna napomena o metodi nosila je znak ⚠, pa je svaki rad — i savršeno čist — imao bar… | `check_citations_authoryear.py`, `generate_report.py`, `kvar.py` | — | 965 |
| 75–78 | prvi prolaz kroz STVARNI rad | `test_all.py` | ✅ | 990 |
| 79 | popis literature gutao je sve iza sebe | — | ✅ | 1020 |
| 80–86 | tri stavke koje su ostale nakon v1.9.5 | `izmjeri.py`, `prelomi.json`, `natpisi.json` | ✅ | 1033 |
| — | Nova faza D2 i B2 — dvije klase koje nijedan alat nije gledao | `check_tvrdnja_izvor.py`, `cross_check.py`, `mapa.json` | ✅ | 1073 |
| 87–90 | drugi stvarni rad, druga vrsta rada | — | ✅ | 1100 |
| 91 | pravni rad: svaka jedinica iz popisa bila je siroče | `provjeri_fusnote.py` | ✅ | 1143 |
| 92 | najveći izvor šuma u paketu, nađen tek na stvarnom empirijskom radu | `provjeri_fusnote.py` | ✅ | 1185 |
| — | Korpus na kojem je lanac provjeren | — | ⚪ | 1229 |
| 93–97 | tehnički radovi: popis literature u tri neprepoznata oblika | — | ✅ | 1246 |
| — | Korpus na kojem je lanac provjeren (šest radova, pet fakulteta, četiri stila) | — | ⚪ | 1289 |
| 98–104 | audit paketa nakon rada Znahor | `AUDITskillovanakonradaZnahor.md`, `check_paragraphs.py`, `verify_rewrite.py` | — | 1308 |
| 105 | metapodaci: cijela razina dokumenta koju nitko nije gledao | `provjeri_metapodatke.py` | ✅ | 1389 |
| 106–107 | zatvaranje popisa iz prve dijagnoze | `parafraza.py`, `propagacija.py`, `brojke_iz_rasprave.py` | ✅ | 1856 |
| — | Što lanac i dalje NE provjerava | `check_argument.py`, `stil_pipeline.md` | ⚪ | 1893 |
| 108–111 | zatvaranje popisa „što lanac NE provjerava" | `check_statistika.py`, `check_tablice.py`, `check_hipoteze.py` | ✅ | 1916 |
| — | Što OSTAJE nepokriveno, i zašto | `faculty_scale_gate.py`, `v1_vs_v2_contract.json` | ⚪ | 1978 |
| 112 | „nije se pokrenula" i „ne odnosi se na ovaj rad" bili su isto stanje | `check_tvrdnja_izvor.py`, `mapa.json` | ✅ | 1999 |
| 113 | `kvar.py` je poznavao samo jedan broj po unosu, pa je grupirani unos bio ili nevidljiv … | `kvar.py` | ✅ | 2046 |
| 114 | Katalozi kvarova nisu bili u jedinom ulazu za testove, pa je suite bio zelen nad pokvar… | `testovi.sh`, `kvar.py` | ✅ | 2083 |
| 115 | Otisak motora hashirao je bajtove radnog stabla, pa je isti commit imao dva otiska ovis… | `engine_contract.json`, `testovi.sh`, `test_all.py` | ✅ | 2101 |
| 116 | Naslov u obliku koji registar ne čita bio je tišina, pa je „sljedeći slobodan” pokaziva… | `kvar.py`, `kvar.md`, `test_kvar.py` | ✅ | 2132 |
| 117 | provjera tvrdnji gledala je samo jedan smjer | `generate_report.py`, `check_hipoteze.py`, `check_XXXXX.py` | ✅ | 2173 |
| 118 | Opis skilla je površina odluke, ne changelog | — | ⚪ | 2213 |
| 119 | Provjera tvrdnji rušila se na hrvatskoj konzoli, pa je nalaz koji je NAŠLA izlazio kao … | `check_hipoteze.py`, `testovi.sh` | ✅ | 2245 |
| 120 | Brojka „31 stvarni kvar” stajala je u opisu nad katalogom od 26, a kvar 37 ju je zapisa… | `SKILL.md`, `zamke.md`, `test_zakrpa.py` | ✅ | 2284 |
| 121 | mjerilo je palo, a zaključak je htio pasti na opis | `pokreni_trigger.py`, `trigger_rezultat.json` | ✅ | 2322 |
| 122 | Indeks kataloga čitao je tuđi oblik naslova, a ne svoj, pa je jedanaest unosa izgubilo … | `indeks_zamki.py`, `test_indeks.py`, `testovi.sh` | ✅ | 2420 |
| 123 | „VERSION ne smije zaostajati” bila bi provjera crvena u 28 od 32 stanja, pa je mjerena … | `env.sh`, `test_verzija.py`, `testovi.sh` | ✅ | 2464 |
| 124 | Mjerilo usmjeravanja nije znalo reći da nije moglo mjeriti, i mjerilo je samo jedan uvj… | `drift.py`, `SKILL.md`, `pokreni_trigger.py` | ✅ | 2524 |
| 125 | Broj testova u izvještaju bio je ukovana konstanta, pa je suite tvrdio 6/6 dok je pokre… | `SKILL.md`, `test_zakrpa.py`, `test_kvar.py` | ✅ | 2569 |
| 126 | Provjera tvrdnji tražila je skripte samo u `scripts/`, pa je alat koji postoji prijavil… | `pokreni_trigger.py`, `SKILL.md`, `test_zakrpa.py` | ✅ | 2610 |
| 127 | `drift.py` je karticu koja je uredno jednu verziju iza optuživao da je ručno mijenjana | `drift.py`, `test_drift.py` | ✅ | 2642 |
| 128 | Provjera je potvrdila alat koji se onda nije dao pokrenuti, a neuspjeh je izgledao kao … | `test_trigger.py` | ✅ | 2712 |
| 129 | zbroj po fazama nije trošak jednog rada | `mjera.py`, `SKILL.md` | ✅ | 2778 |
| 130 | Predviđanje iz kvara 121 opovrgnuto mjerenjem: opis nije bio uzrok, prazna mapa jest | `drift.py`, `trigger_evals.json` | ⚪ | 2818 |
| 131 | Prolaz koji je pukao brojio se kao prolaz u kojem skill nije okinuo | `test_trigger.py` | ✅ | 2863 |
| 132 | Popis unosa „bez ograde” mjerio je oblikovanje, ne dug: 47 od 79 naspram izmjerenih 34 | `test_drift.py`, `test_indeks.py` | ✅ | 2894 |
| 133 | kartica i repo razišle su se u jednoj brojci, i ta je brojka lokator | `SKILL.md`, `drift.py`, `zamke.md` | ✅ | 2940 |
| 134 | doktrina je za Cowork ostavila otvorena vrata kojih nema | `SKILL.md` | ✅ | 3024 |
| 135 | Provjera „broj kvara mora postojati” nije čitala kanonski raspon — treći put isti uzorak | `SKILL.md`, `test_zakrpa.py` | ✅ | 3056 |
| 136 | Odziv 6/12 nije bio nalaz o opisu nego o praznoj mapi — mjereno na svih dvanaest upita | `rad.docx` | ⚪ | 3091 |
| 137 | Popravljena je brojka u zaglavlju, a iste dvije naredbe nastavile su dijeliti brojem re… | `indeks_zamki.py`, `kvar.py`, `test_indeks.py` | ✅ | 3132 |
| 138 | Mjerena je samo strana koja je mogla porasti; kad je izmjerena i druga, prag se nije po… | `rad.docx` | ⚪ | 3171 |
| 139 | „Bez ograde” je bio jedan pretinac za tri stanja, pa popis duga nije bio popis posla | `test_indeks.py` | ⚪ | 3221 |
| 140 | Dvadeset šest unosa duguje ogradu; izmjereno je koliko ih uopće ima test koji ih dodiru… | `kvar.md`, `SKILL.md` | ⚪ | 3260 |
| 141 | Pokrivenost izvora mjeri se samo autor-godinom, pa rad koji citira drukcije nema nijeda… | — | — | 3306 |
| 142 | Sklonidba je deklarirana kao moguc lazan nalaz, a isti redak svejedno nosi crveni krizic | — | — | 3344 |
| 143 | Provjera koja nije izvedena ispisuje se kao "0 krsenja", uz razlog koji nije tocan | — | — | 3392 |

## Unosi bez ograde

Nemaju regresijski test i **nisu rekli zašto**. Unos kojemu ograda ne
pripada (mjerenje, bilješka o korpusu) to smije reći rečenicom
„Ograda: nema — <razlog>” i tada ovdje ne stoji; razlog je obavezan,
jer bi inače deklaracija bila način da se dug sakrije. Ovaj popis je
posao, ne stanje.

- 24 — Ključ s vrijednošću `null` nije „profil to ne propisuje", pa resolver pada i gate tiho preskače (redak 10)
- 25 — Satelit se traži u četiri putanje, a peta (`synced/<hash>/`) je ona u kojoj Cowork živi (redak 32)
- 26 — `meta` se koristi u `_renderiraj` koji ga nikad nije primio (redak 49)
- 27 — Grana `startswith('popis')` hvata prije `'popis literature'`, pa rukopis dobiva fantomske naslove (redak 65)
- 28 — Izlazni kod se računa iz broja simbola, a ne iz toga smije li simbol blokirati (redak 83)
- 29 — Kućni stil završnog rada primjenjuje se na seminarski jer uvjet zna samo fakultet, ne tip (redak 102)
- 31 — Popis naslova popisa literature je zatvoren, pa nepoznat naslov ruši gate umjesto da javi (redak 142)
- 32 — Admisija profila traži datoteku koju isporučeni paket ne nosi, pa se hash ne može osvježiti (redak 158)
- 33 — Shema opsega zna samo ukupni rad, pa se pravila po dijelovima ne mogu ni zapisati ni provjeriti (redak 178)
- 34 — Faza bez svog artefakta je „nezapočeta" i kad je rad došao gotov (redak 195)
- 35 — Pravilo „godina s točkom" mjeri se i na stilu u kojem je točka iza godine kraj reference (redak 210)
- 38 — Nepotvrđen izvor dobiva simbol i obrazloženje, ali nijednu naredbu čovjeku, pa se nalaz preskače (redak 268)
- 40 — `inline_shapes` ne vidi sliku koju je autor povukao mišem, pa alat javi „nema što mjeriti" (redak 326)
- 41 — Uvod na razini Heading 2 prijavljuje se kao „rad nema tezu" (redak 360)
- 42 — Alat za dokazivanje popravaka ne poznaje smjer tihog kvara koji sam skill proglašava prioritetom (redak 387)
- 45 — Opseg se procjenjuje uz pretpostavku A4, a format papira nitko ne mjeri (redak 487)
- 46 — `_empirijski` se hrani statusom dijela koji time postaje ključan (redak 511)
- 48 — Cross-chapter provjera gleda samo tvrdnje iz lanca, pa proturječje u vlastitim brojkama prolazi (redak 564)
- 52 — `re.IGNORECASE` gasi strukturni znak, pa svaki izvor s provenijencijom postaje tuđe autorstvo (redak 663)
- 56 — Doktrina o gateovima postojala je u dva skilla i nikad nije prešla u `katedra-lite` (redak 794)
- 61–63 — audit koji se smije ignorirati (redak 899)
- 71 — faza A bez izvršitelja (redak 945)
- 72–73 — alat za provjeru tvrdnji bio je i sam tvrdnja bez pokrića (redak 954)
- 74 — Trajna napomena o metodi nosila je znak ⚠, pa je svaki rad — i savršeno čist — imao barem jedan „na… (redak 965)
- 98–104 — audit paketa nakon rada Znahor (redak 1308)
- 141 — Pokrivenost izvora mjeri se samo autor-godinom, pa rad koji citira drukcije nema nijedan citat (redak 3306)
- 142 — Sklonidba je deklarirana kao moguc lazan nalaz, a isti redak svejedno nosi crveni krizic (redak 3344)
- 143 — Provjera koja nije izvedena ispisuje se kao "0 krsenja", uz razlog koji nije tocan (redak 3392)
