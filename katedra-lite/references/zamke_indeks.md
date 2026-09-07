# Indeks kataloga zamki

> Generirano iz `references/zamke.md` skriptom `scripts/indeks_zamki.py`.
> **Ne uređuj ručno.** Nakon izmjene kataloga: `indeks_zamki.py --upisi`.
> `bin/testovi.sh` pada ako je ovaj indeks zastario.

Unosa: **89** (isti broj javlja `kvar.py --provjeri`) · uz njih 5 nenumeriranih odjeljaka · s ogradom: **76** · ograda ne pripada (deklarirano): **17** · **duguje ogradu: 1**

Traži bez učitavanja cijelog kataloga:

```bash
python3 katedra-lite/scripts/indeks_zamki.py --trazi 'gate'
sed -n '844,880p' katedra-lite/references/zamke.md   # unos po retku
```

| # | Naslov | Dodiruje | Ograda | Redak |
|---|--------|----------|--------|-------|
| 24 | Ključ s vrijednošću `null` nije „profil to ne propisuje", pa resolver pada i gate tiho … | `fpzg.json`, `_schema.json`, `_resolved_schema.json` | ✅ | 10 |
| 25 | Satelit se traži u četiri putanje, a peta (`synced/<hash>/`) je ona u kojoj Cowork živi | `build_docx.py`, `test_stari_kvarovi.py`, `vjestine.py` | ✅ | 33 |
| 26 | `meta` se koristi u `_renderiraj` koji ga nikad nije primio | `test_stari_kvarovi.py` | ✅ | 51 |
| 27 | Grana `startswith('popis')` hvata prije `'popis literature'`, pa rukopis dobiva fantoms… | `check_placeholders.py`, `sazetak.md`, `ideje.md` | ✅ | 68 |
| 28 | Izlazni kod se računa iz broja simbola, a ne iz toga smije li simbol blokirati | `check_rules.py`, `zasto.md`, `test_stari_kvarovi.py` | ✅ | 87 |
| 29 | Kućni stil završnog rada primjenjuje se na seminarski jer uvjet zna samo fakultet, ne t… | `vjestine.json`, `sastavi.py`, `gradi.sh` | ✅ | 107 |
| 30 | Numerički stil u ovalnim zagradama ne postoji, pa rad sa 75 referenci prolazi kao rad b… | `citation_dialects.py`, `_schema.json`, `check_citations.py` | ✅ | 128 |
| 31 | Popis naslova popisa literature je zatvoren, pa nepoznat naslov ruši gate umjesto da ja… | `provjeri_literaturu.py`, `fixture_popis_citirane_literature.docx`, `test_stari_kvarovi.py` | ✅ | 148 |
| 32 | Admisija profila traži datoteku koju isporučeni paket ne nosi, pa se hash ne može osvje… | `fpzg.json`, `faculty_scale_gate.py`, `v1_vs_v2_contract.json` | ⚪ | 165 |
| 33 | Shema opsega zna samo ukupni rad, pa se pravila po dijelovima ne mogu ni zapisati ni pr… | `provjeri_hks_fzs.py`, `hks-fzs.json`, `provjeri_dijelove.py` | ✅ | 186 |
| 34 | Faza bez svog artefakta je „nezapočeta" i kad je rad došao gotov | `napredak.py`, `plan.json`, `test_stari_kvarovi.py` | ✅ | 204 |
| 35 | Pravilo „godina s točkom" mjeri se i na stilu u kojem je točka iza godine kraj reference | `provjeri_literaturu.py`, `fixture_popis_citirane_literature.docx` | ⚪ | 220 |
| 36 | Skill za učenje dokumentira dvije zastavice koje njegove skripte nemaju | `SKILL.md`, `kvar.py`, `dokaz.py` | ✅ | 239 |
| 37 | Katalog na koji se skill poziva ima 23 unosa, opis vlasnika kaže 31, a učenje citira 32… | `SKILL.md`, `zamke.md`, `kvar.md` | ✅ | 259 |
| 38 | Nepotvrđen izvor dobiva simbol i obrazloženje, ali nijednu naredbu čovjeku, pa se nalaz… | `verify_sources.py`, `kvar.md`, `test_stari_kvarovi.py` | ✅ | 279 |
| 39 | Doktrina ne poznaje lokator koji kod već proizvodi, pa se gotov citat tretira kao nedov… | `evidence_ingest.py`, `SKILL.md`, `pisanje.md` | ✅ | 311 |
| 40 | `inline_shapes` ne vidi sliku koju je autor povukao mišem, pa alat javi „nema što mjeri… | `provjeri_prikaze.py`, `check_rules.py`, `test_stari_kvarovi.py` | ✅ | 338 |
| 41 | Uvod na razini Heading 2 prijavljuje se kao „rad nema tezu" | `check_argument.py`, `test_stari_kvarovi.py` | ✅ | 373 |
| 42 | Alat za dokazivanje popravaka ne poznaje smjer tihog kvara koji sam skill proglašava pr… | `SKILL.md`, `dokaz.py`, `provjeri_prikaze.py` | ✅ | 401 |
| 43 | Doktrina je za 403 na pushu upućivala na read-only GitHub konektor, pa je popravak bio … | `SKILL.md`, `test_stari_kvarovi.py` | ✅ | 430 |
| 44 | Čitač kriterija „zadatak" nije imao granu ispunjeno, pa je pojas 5 bio nedosežljiv svak… | `rubrika.py`, `zadatak.json`, `provjeri_predaju.py` | ✅ | 461 |
| 45 | Opseg se procjenjuje uz pretpostavku A4, a format papira nitko ne mjeri | `check_rules.py`, `test_stari_kvarovi.py` | ✅ | 503 |
| 46 | `_empirijski` se hrani statusom dijela koji time postaje ključan | `stanje.json`, `test_stari_kvarovi.py` | ✅ | 528 |
| 47 | Lokator dokaza poznaje samo stranicu, pa standardi i propisi ispadaju iz lanca | `claim_ledger.py`, `SKILL.md` | ✅ | 558 |
| 48 | Cross-chapter provjera gleda samo tvrdnje iz lanca, pa proturječje u vlastitim brojkama… | `consistency_check.py`, `test_stari_kvarovi.py`, `provjeri_brojke_u_tekstu.py` | ✅ | 582 |
| 49 | `drift.py` mjeri samo SKILL.md, a kartica i repo razilaze se i u `scripts/` | `drift.py`, `SKILL.md`, `test_stari_kvarovi.py` | ✅ | 610 |
| 50 | Primjerak mjeri veličinu pisma iz natpisa prikaza, jer odlomci tijela nemaju izričitu v… | `primjerci.py`, `resolved_profile.json` | ⚪ | 639 |
| 51 | Redni broj pravne reference pred velikim slovom lomi rečenicu, pa se mjeri ritam kojega… | `common.py` | ✅ | 662 |
| 52 | `re.IGNORECASE` gasi strukturni znak, pa svaki izvor s provenijencijom postaje tuđe aut… | `test_stari_kvarovi.py` | ✅ | 684 |
| 53 | Rep predaje pripada vrsti rada, a čitao se s razine fakulteta, pa svaki seminarski kasni | `tempo.py`, `efzg.json`, `napredak.py` | ⚪ | 712 |
| 54 | Kartica `katedra-lite` nosi samo `SKILL.md`, a router imenuje 44 datoteke koje ne nosi | `SKILL.md`, `gate.py`, `rubrika.py` | ✅ | 733 |
| 55 | `SKILL.md` spremljen kao dopuna gubi router; tri skilla su se tako okrnjila | `SKILL.md` | ✅ | 793 |
| 56 | Doktrina o gateovima postojala je u dva skilla i nikad nije prešla u `katedra-lite` | `check_fields.py`, `rubrika.py`, `provjeri_predaju.py` | ✅ | 817 |
| 57 | `VERSION` zaostaje za commitom, a § 0.0 taj broj ispisuje kao prvo što sesija kaže | `env.sh` | ✅ | 844 |
| 58 | gate je zeleno javljao fazu u kojoj se ništa nije pokrenulo | `gate.py`, `rad.docx`, `test_gate.py` | ✅ | 870 |
| 59 | faza audit nije pokretala audit | `audit.md`, `test_gate.py` | ✅ | 898 |
| 60 | `provjeri_predaju.py` nije bio korak nijednog gatea | `provjeri_predaju.py`, `predaja.md`, `rubrika.py` | ✅ | 912 |
| 61–63 | audit koji se smije ignorirati | `generate_report.py`, `audit_all.py`, `test_stari_kvarovi.py` | ✅ | 923 |
| 64–66 | klase pogrešaka koje nijedan alat nije gledao | `pipeline.md`, `test_all.py` | ✅ | 936 |
| 67–70 | lažni nalazi koji su gate činili neupotrebljivim | — | ✅ | 950 |
| 71 | faza A bez izvršitelja | `SKILL.md`, `check_placeholders.py`, `test_stari_kvarovi.py` | ✅ | 970 |
| 72–73 | alat za provjeru tvrdnji bio je i sam tvrdnja bez pokrića | `engine_contract.json`, `test_all.py`, `SKILL.md` | ✅ | 980 |
| 74 | Trajna napomena o metodi nosila je znak ⚠, pa je svaki rad — i savršeno čist — imao bar… | `check_citations_authoryear.py`, `generate_report.py`, `kvar.py` | ✅ | 992 |
| 75–78 | prvi prolaz kroz STVARNI rad | `test_all.py` | ✅ | 1018 |
| 79 | popis literature gutao je sve iza sebe | — | ✅ | 1048 |
| 80–86 | tri stavke koje su ostale nakon v1.9.5 | `izmjeri.py`, `prelomi.json`, `natpisi.json` | ✅ | 1061 |
| — | Nova faza D2 i B2 — dvije klase koje nijedan alat nije gledao | `check_tvrdnja_izvor.py`, `cross_check.py`, `mapa.json` | ✅ | 1101 |
| 87–90 | drugi stvarni rad, druga vrsta rada | — | ✅ | 1128 |
| 91 | pravni rad: svaka jedinica iz popisa bila je siroče | `provjeri_fusnote.py` | ✅ | 1171 |
| 92 | najveći izvor šuma u paketu, nađen tek na stvarnom empirijskom radu | `provjeri_fusnote.py` | ✅ | 1213 |
| — | Korpus na kojem je lanac provjeren | — | ⚪ | 1257 |
| 93–97 | tehnički radovi: popis literature u tri neprepoznata oblika | — | ✅ | 1274 |
| — | Korpus na kojem je lanac provjeren (šest radova, pet fakulteta, četiri stila) | — | ⚪ | 1317 |
| 98–104 | audit paketa nakon rada Znahor | `AUDITskillovanakonradaZnahor.md`, `check_paragraphs.py`, `verify_rewrite.py` | — | 1336 |
| 105 | metapodaci: cijela razina dokumenta koju nitko nije gledao | `provjeri_metapodatke.py` | ✅ | 1427 |
| 106–107 | zatvaranje popisa iz prve dijagnoze | `parafraza.py`, `propagacija.py`, `brojke_iz_rasprave.py` | ✅ | 1894 |
| — | Što lanac i dalje NE provjerava | `check_argument.py`, `stil_pipeline.md` | ⚪ | 1931 |
| 108–111 | zatvaranje popisa „što lanac NE provjerava" | `check_statistika.py`, `check_tablice.py`, `check_hipoteze.py` | ✅ | 1954 |
| — | Što OSTAJE nepokriveno, i zašto | `faculty_scale_gate.py`, `v1_vs_v2_contract.json` | ⚪ | 2016 |
| 112 | „nije se pokrenula" i „ne odnosi se na ovaj rad" bili su isto stanje | `check_tvrdnja_izvor.py`, `mapa.json` | ✅ | 2037 |
| 113 | `kvar.py` je poznavao samo jedan broj po unosu, pa je grupirani unos bio ili nevidljiv … | `kvar.py` | ✅ | 2084 |
| 114 | Katalozi kvarova nisu bili u jedinom ulazu za testove, pa je suite bio zelen nad pokvar… | `testovi.sh`, `kvar.py` | ✅ | 2121 |
| 115 | Otisak motora hashirao je bajtove radnog stabla, pa je isti commit imao dva otiska ovis… | `engine_contract.json`, `testovi.sh`, `test_all.py` | ✅ | 2139 |
| 116 | Naslov u obliku koji registar ne čita bio je tišina, pa je „sljedeći slobodan” pokaziva… | `kvar.py`, `kvar.md`, `test_kvar.py` | ✅ | 2170 |
| 117 | provjera tvrdnji gledala je samo jedan smjer | `generate_report.py`, `check_hipoteze.py`, `check_XXXXX.py` | ✅ | 2211 |
| 118 | Opis skilla je površina odluke, ne changelog | — | ⚪ | 2251 |
| 119 | Provjera tvrdnji rušila se na hrvatskoj konzoli, pa je nalaz koji je NAŠLA izlazio kao … | `check_hipoteze.py`, `testovi.sh` | ✅ | 2283 |
| 120 | Brojka „31 stvarni kvar” stajala je u opisu nad katalogom od 26, a kvar 37 ju je zapisa… | `SKILL.md`, `zamke.md`, `test_zakrpa.py` | ✅ | 2322 |
| 121 | mjerilo je palo, a zaključak je htio pasti na opis | `pokreni_trigger.py`, `trigger_rezultat.json` | ✅ | 2360 |
| 122 | Indeks kataloga čitao je tuđi oblik naslova, a ne svoj, pa je jedanaest unosa izgubilo … | `indeks_zamki.py`, `test_indeks.py`, `testovi.sh` | ✅ | 2458 |
| 123 | „VERSION ne smije zaostajati” bila bi provjera crvena u 28 od 32 stanja, pa je mjerena … | `env.sh`, `test_verzija.py`, `testovi.sh` | ✅ | 2502 |
| 124 | Mjerilo usmjeravanja nije znalo reći da nije moglo mjeriti, i mjerilo je samo jedan uvj… | `drift.py`, `SKILL.md`, `pokreni_trigger.py` | ✅ | 2562 |
| 125 | Broj testova u izvještaju bio je ukovana konstanta, pa je suite tvrdio 6/6 dok je pokre… | `SKILL.md`, `test_zakrpa.py`, `test_kvar.py` | ✅ | 2607 |
| 126 | Provjera tvrdnji tražila je skripte samo u `scripts/`, pa je alat koji postoji prijavil… | `pokreni_trigger.py`, `SKILL.md`, `test_zakrpa.py` | ✅ | 2648 |
| 127 | `drift.py` je karticu koja je uredno jednu verziju iza optuživao da je ručno mijenjana | `drift.py`, `test_drift.py` | ✅ | 2680 |
| 128 | Provjera je potvrdila alat koji se onda nije dao pokrenuti, a neuspjeh je izgledao kao … | `test_trigger.py` | ✅ | 2750 |
| 129 | zbroj po fazama nije trošak jednog rada | `mjera.py`, `SKILL.md` | ✅ | 2816 |
| 130 | Predviđanje iz kvara 121 opovrgnuto mjerenjem: opis nije bio uzrok, prazna mapa jest | `drift.py`, `trigger_evals.json` | ⚪ | 2856 |
| 131 | Prolaz koji je pukao brojio se kao prolaz u kojem skill nije okinuo | `test_trigger.py` | ✅ | 2901 |
| 132 | Popis unosa „bez ograde” mjerio je oblikovanje, ne dug: 47 od 79 naspram izmjerenih 34 | `test_drift.py`, `test_indeks.py` | ✅ | 2932 |
| 133 | kartica i repo razišle su se u jednoj brojci, i ta je brojka lokator | `SKILL.md`, `drift.py`, `zamke.md` | ✅ | 2978 |
| 134 | doktrina je za Cowork ostavila otvorena vrata kojih nema | `SKILL.md` | ✅ | 3062 |
| 135 | Provjera „broj kvara mora postojati” nije čitala kanonski raspon — treći put isti uzorak | `SKILL.md`, `test_zakrpa.py` | ✅ | 3094 |
| 136 | Odziv 6/12 nije bio nalaz o opisu nego o praznoj mapi — mjereno na svih dvanaest upita | `rad.docx` | ⚪ | 3129 |
| 137 | Popravljena je brojka u zaglavlju, a iste dvije naredbe nastavile su dijeliti brojem re… | `indeks_zamki.py`, `kvar.py`, `test_indeks.py` | ✅ | 3170 |
| 138 | Mjerena je samo strana koja je mogla porasti; kad je izmjerena i druga, prag se nije po… | `rad.docx` | ⚪ | 3209 |
| 139 | „Bez ograde” je bio jedan pretinac za tri stanja, pa popis duga nije bio popis posla | `test_indeks.py` | ⚪ | 3259 |
| 140 | Dvadeset šest unosa duguje ogradu; izmjereno je koliko ih uopće ima test koji ih dodiru… | `kvar.md`, `SKILL.md` | ⚪ | 3298 |
| 141 | Prvih pet novih ograda bile su lažne, i to je pokazala mutacija, ne čitanje | `vjestine.py`, `test_stari_kvarovi.py`, `testovi.sh` | ✅ | 3344 |
| 142 | Pad suitea javio je samo brojku, pa se pad koji se ne ponovi nije dao ni dijagnosticira… | — | ⚪ | 3403 |
| 143 | Unos koji o ogradi samo GOVORI ispao je iz popisa duga | `test_indeks.py` | ✅ | 3456 |
| 144 | Riječ „Ograda:” značila je tri različite stvari, a alat je sve tri brojio kao ogradu | `test_stari_kvarovi.py` | ⚪ | 3492 |
| 145 | Mutacijski test izvodio je bytecode PRETHODNE mutacije, jer su se dvije mutacije poklop… | `gate.py`, `testovi.sh` | ✅ | 3540 |
| 146 | Mutacijski harness pročitao je pad alata kao „ništa nije palo”, jer je pad i pali test … | `check_rules.py` | ⚪ | 3597 |

## Unosi bez ograde

Nemaju regresijski test i **nisu rekli zašto**. Unos kojemu ograda ne
pripada (mjerenje, bilješka o korpusu) to smije reći rečenicom
„Ograda: nema — <razlog>” i tada ovdje ne stoji; razlog je obavezan,
jer bi inače deklaracija bila način da se dug sakrije. Ovaj popis je
posao, ne stanje.

- 98–104 — audit paketa nakon rada Znahor (redak 1336)
