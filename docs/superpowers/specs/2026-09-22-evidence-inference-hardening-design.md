# Katedra — evidence & inference hardening

Datum: 22. rujna 2026.  
Status: **nacrt specifikacije za pregled; nije implementirano niti izdanje 2.1**.  
Repo: `danielrisavi77-create/katedra-pkg`  
Pročitana osnova: `main` na `14c339ba7e7e40e477851316026a1901191f82a8`.  
Povezani otvoreni posao: PR #52, head `a40a92afba7fbbaf53ef309a5b63bf8ea9eb7ab6`.

## 1. Namjena i granice odobrenog smjera

Pretvoriti pouke iz višekružnog uređivanja akademskog rada u ponovljive zaštite: točan izvor i verzija, značenje brojke, dopušten zaključak, propagacija ispravka te pouzdana završna isporuka. Korisnik je odobrio smjer i pripremu GitHub plana. Ova specifikacija opisuje predloženu arhitekturu; implementacija i tvrdnje o prolazu novih testova još nisu izvršene.

Uspjeh nije više zelenih oznaka. Uspjeh je da alat razlikuje dokazanu pogrešku, nedovoljan dokaz, stručnu prosudbu i tehničku neizvedenost. Uredan kontrolni primjer ne smije postati lažni nalaz.

**Izvan opsega:** generiranje novih poglavlja, detekcija autorstva/AI-ja, zaobilaženje detektora, automatsko pravno tumačenje, mijenjanje fakultetskih pravila, uklanjanje otvorenih mentorovih komentara, nenajavljeno prihvaćanje Track Changes, automatski merge, promjena tajni ili uključivanje API naplate. Privatni rad, potpis, screenshotovi razgovora i biografski podaci ne ulaze u javni repo.

Broj budućeg izdanja određuje se tek u zasebnom release koraku. `VERSION`, frozen core contract, manifest sposobnosti i tvrdnje u `SKILL.md` sada se ne mijenjaju.

## 2. Što već postoji — ne graditi dvaput

Pregledani su stvarni izvori na navedenom commitu:

| Postojeća komponenta | Stvarni opseg u pregledanom kodu | Potrebna nadogradnja |
|---|---|---|
| `katedra/SKILL.md` | Učenje iz kvarova, vlasništvo popravka, dokaz prije tvrdnje o popravku | Razdvojiti reproducirani kvar alata od novog zahtjeva proizašlog iz uredničkog rada |
| `katedra-lite/scripts/evidence_gate.py` | B13 matrica, veze supports/contradicts/contextualizes, blokirajući izvori i preduvjeti | Dokaz da zaključak odgovara opsegu izvora; očuvanje negativnog statusa kroz potrošače izvještaja |
| `katedra-lite/references/claim_ledger_schema.json` | Zatvorena v1 shema: tekst, lokacija i veze na dokaze | Ne dodavati prešutno nova polja u v1; novi kontekst voditi zasebno |
| `katedra-lite/scripts/consistency_check.py` | Sidra tvrdnji, brojčane razlike, eksplicitna negacija, graf poglavlja | Značenje brojki i ovisnosti; pokrivenost ne smije značiti samo prisutnost dvaju poglavlja |
| `katedra-lite/scripts/reviewer_simulation.py` | Read-only objedinjavanje argumentacije, dokaza, dosljednosti i mentorovih zamjerki | Validirati ulazni ugovor i prenijeti failed/preconditions/advisory stanje, ne čitati samo popis nalaza |
| `katedra-lite/references/artifact_manifest_schema.json` | Identitet artefakta, verzije, SHA-256, snapshotovi | Vezati konkretan rezultat provjere i render uz postojeći identitet artefakta |
| `katedra-lite/scripts/gate.py` | Koraci, izlazni kodovi, preskoci, neprimjenjivost i izričita isključenja | Agregacija za jasno definiran opseg; zastarjeli rezultat nije prolaz |
| `.github/workflows/katedra-verification.yml` | Paketni testovi i zaseban live Claude eval; API billing zadano isključen | Zadržati zaštite i odvojeno izvijestiti što se stvarno mjerilo |

PR #52 već obrađuje mjerljivost audita, profile i pojedine brojčane provjere. Ne mijenjati njegovu granu niti prepisivati njegove popravke. Prije svakog implementacijskog PR-a ponovno pročitati aktualni `main` i #52, identificirati preklapanja i testirati zajednički rezultat. Povijesni rezultati iz opisa #52 nisu dokaz za novu granu.

### Dvije hipoteze o konkretnim rubnim slučajevima

U pregledanom `consistency_check.py` status pokrivenosti ovisi o broju poglavlja, a ne o broju usporedivih tvrdnji. Dva nepovezana poglavlja zato mogu biti označena kao dovoljno pokrivena. U `reviewer_simulation.py` evidence leća čita blokirane retke matrice, ali ne prenosi izričito top-level `passed` i `preconditions` iz B13 izvještaja. Oba slučaja prvo reproducirati testom. Ovo nisu tvrdnje da je provedena reprodukcija niti da je izmjeren kvar cijelog završnog gatea.

## 3. Odluka o arhitekturi

Razmotrena su tri pristupa: samo proširiti upute; proširiti postojeće provjere strukturiranim kontekstom; ili izgraditi novi autonomni semantički audit. Predlaže se drugi pristup. Same upute nisu izvršna zaštita, a novi autonomni audit udvostručio bi vlasništvo i obećavao razumijevanje koje testovi ne mogu jamčiti.

`katedra-lite` ostaje router i vlasnik argumentacijske konzistentnosti. Ne kopira se motor audita ni motor DOCX-a. Novi mali pomoćni modul za tipizirani kontekst, ako je potreban, smije se dodati uz postojeće skripte; ne uvodi se sedam paralelnih motora.

- **Katedra Lite:** tvrdnje, značenje izračuna, ovisnosti, opseg zaključivanja, statusi i orkestracija.
- **rad-audit:** čitanje/provjera dokumenta i izvora kroz postojeći verzionirani contract. Promjene samo kod utvrđenog vlasničkog nedostatka, u odvojenom zahvatu.
- **rad-docx:** mutacija dokumenta, geometrija tablica i vizuala, render i provjera metapodataka, uz snapshot.
- **Ljudski/stručni pregled:** odnos izvora i parafraze, pravni doseg, stvarna pripadnost skupu, kauzalnost, prikladnost dizajna i konačno čitanje.

### Kompatibilnost

Ne mijenjati značenje postojeće v1 sheme koja ima `additionalProperties: false`. Predlaže se zaseban verzionirani `inference_context.json` u privatnoj `.katedra/` mapi, vezan identifikatorima za postojeći claim/evidence ledger. Naziv je prijedlog, ne postojeći CLI.

Stari projekti ostaju čitljivi postojećim provjerama. Novi sloj bez odgovarajućeg konteksta prikazuje `not_run` ili nedovoljnu pokrivenost, nikada potpuni semantički PASS. Uključivanje kao obveznog release koraka traži testiranu migraciju i izričito navedene preduvjete; ne preokrenuti sve legacy projekte u neobjašnjiv pad.

## 4. Podatkovni ugovor

Predloženi kontekst sadrži pet cjelina:

1. **Bindings:** postojeći artifact_id/version_id, hash dokumenta, claim-ledgera, evidence-ledgera i snapshota izvora; analizirani view; alat/verzija; konfiguracija i odabrani opseg.
2. **Numeric facts:** fact_id, claim_id, izvor i stvarni lokator, vrijednost, jedinica, vremensko razdoblje, populacija/prostorni i organizacijski obuhvat, pokazatelj, status mjerenja i uloga u toku.
3. **Derivations:** ulazni fact_id-jevi, operacija, rezultat, provjerljive pretpostavke, sastavnice/skupovi i tolerancija. Brojke se ne kopiraju ručno u više tablica.
4. **Claim links:** premise i zaključci, veze prema istim tvrdnjama kroz poglavlja, verzija pregledane premise i stručni status zaključivanja.
5. **Review scope:** zahtijevane provjere i tvrdnje, primjenjivost, izričito izuzeti administrativni koraci, razloga isključenja i stručni pregledi koji još nedostaju.

Vrijednosti za računanje predstavljati točno (`Decimal`/decimalni niz), uz provjeren lokalni zapis; zabraniti NaN i beskonačnost. Ne pogađati je li `1.234` engleska decimala ili hrvatska tisućica kada izvorni kontekst nije poznat. Rasponi, približne vrijednosti i donje granice imaju vlastitu reprezentaciju; `>150` nije isto što i točno `150`.

Status mjerenja razdvaja `actual`, `capacity`, `target`, `planned`, `estimate`; uloga razdvaja `input`, `output`, `stock`, `not_applicable`. Nepoznato polje ne zamijeniti pretpostavkom. Razdoblje i obuhvat moraju se slagati prije jednostavne usporedbe; legitimna vremenska serija izričito je označena.

## 5. Pravila provjere

### 5.1 Identitet, pokrivenost i status

Rezultat vrijedi samo za hashove i view koji su analizirani. Promjena rukopisa, izvora, ledgera, pravila ili relevantne konfiguracije označava ovisne provjere kao zastarjele. Promjena broja stranica invalidira locatore i vizualni nalaz. Preimenovanje bez promjene bajtova ne poništava sadržajni nalaz, ali isporučni manifest mora zabilježiti novu putanju.

Odvojiti stanje izvršenja od stanja dokaza. Neizvedena provjera, nevažeći JSON, nedostupna usluga, istek kvote i zastarjeli artefakt ne znače potvrđenu sadržajnu pogrešku, ali ne smiju dati release PASS. Izričito izuzet JMBAG može biti izvan sadržajnog gatea; ne smije se zato tvrditi da je cijela formalna predaja završena.

Pokrivenost mora navesti što je pregledano, od čega i uz koji opseg. Broj poglavlja ili odsutnost nalaza nisu dovoljan dokaz. Zero claims, zero comparable edges, nepotpun ledger ili nepregledane ključne tvrdnje ne daju tvrdnju o cjelovitosti rada. Zasebno prikazati pokrivenost brojki, izvora i stručnog čitanja.

### 5.2 Brojke i agregacije

Deterministički se mogu provjeriti izračun, jedinica, deklarirani obuhvat i relacije sastavnica. Ne može se samo regexom utvrditi je li redak iz loše pročitanog PDF-a stvarno sastavnica ukupnog iznosa. Ta veza treba lokator i pregled, a nepotvrđena veza daje unknown/review.

Kod preklapanja skupova sustav odbija običan zbroj koji dvaput uračunava istu sastavnicu. Izričita korekcija preklapanja ili dokumentirana unija može proći. Definicija nazivnika mora odgovarati postotku. Promjena udjela iskazuje se u postotnim bodovima; relativna promjena postotka ostaje moguća ako je izričito označena i pravilno izračunana.

### 5.3 Ovisnosti i zaključivanje

Promijenjena/odbačena premisa zahtijeva ponovni pregled svih ovisnih tvrdnji, tranzitivno. Ne proglašava ih automatski neistinitima: zaključak može imati neovisan dokaz. Provjeriti nepoznate reference, duplikate ID-jeva i cikluse; eksplicitno promijenjena premisa ne smije ostaviti zelen stari potomak bez nove provjere.

Dopuna od 100 % daje samo komplement iste kategorije, ne novu karakteristiku te skupine. Planirani kapacitet nije ostvarena obrada. Istodobna promjena dvaju pokazatelja nije dokaz uzročnosti. Nedostatak javno objavljenog podatka nije nula niti dokaz da aktivnost ne postoji.

Metodološki kriterij usporediti s istim kriterijem u evidence-kontekstu slučaja. Dokumentirana namjena izlaza i dokumentirana stvarna uporaba različita su polja. Negativan rezultat usporedbe ne smije se popravljati tihim ublažavanjem kriterija nakon što je uzorak odabran; promjenu zahtijeva obrazloženje i korisnički/stručni pregled.

### 5.4 Granice automatizacije

Riječi poput „dokazuje”, „samo”, „svaki”, „u Hrvatskoj” ili „uzrokuje” služe za pronalaženje kandidata za pregled, ne kao samostalni dokaz pogreške. Sustav treba prepoznati barem citat, negaciju, metodičko ograničenje i opis mogućnosti. Rečenica „ovi rezultati ne dokazuju uzročnost” ne smije biti kažnjena zbog riječi „dokazuju”.

Pravni izvor mora imati točan lokator i doseg odredbe. Certifikat ima predmet, nositelja, razdoblje valjanosti i vrstu provjere. Status `supports` koji je unio agent nije neovisna stručna verifikacija. Automatizacija provjerava zapis i njegove deklarirane veze; značenjsku podršku potvrđuje dokumentiran pregled.

## 6. Mutacija, izgled i privatnost

Tri odvojena načina rada:

- **Sadržajna korekcija:** dopuštene promjene tvrdnji i brojki uz dokaz; svi ovisni dijelovi ponovno se provjeravaju.
- **Samo oblikovanje:** isti sadržaj, brojke, formule, citati i redoslijed; sadržaj vizuala provjeriti preko izvornog podatkovnog modela/oznaka, ne samo XML teksta odlomaka.
- **Čišćenje metapodataka:** očuvati vidljivi sadržaj, grafiku, reference i pristupačne opise; očistiti deklarirane skupine metapodataka, provjeriti ZIP i odnose dijelova, pa tek tada hash isporuke.

Tablice: širina mora stati u prostor konkretne sekcije; ne koristiti fiksnu visinu koja reže tekst; zaglavlja ponavljati samo podatkovnim tablicama; redak viši od stranice zahtijeva drukčiji prijelom, a ne slijepu zabranu cijepanja. Naslov tablice držati s početkom tablice, ne nužno s cijelom višestraničnom tablicom. Dugi URL-i i duge riječi imaju kontrolne primjere.

Vizuali: izvor podataka i oznake moraju se slagati; opis povezati s konkretnim elementom/relationship ID-jem, ne njegovim rednim brojem. Logotip nije „Grafikon 1”. Pregled rendera obuhvaća kritične stranice u punoj veličini; kontaktna ploča nije dokaz čitljivosti sitnih oznaka. Bilježiti alat renderiranja; LibreOffice render nije dokaz prikaza u Microsoft Wordu.

Čišćenje: posebno navesti core/custom/application properties, komentare/osobne tragove revizija, thumbnail i metapodatke ugrađenih objekata/slika. Ne obećavati „sve metapodatke” ako pokrivenost ne obuhvaća sve navedene slojeve; nužni strukturni XML, izvori i alt-opisi nisu privatni metapodaci za brisanje. Ne prihvaćati tracked changes niti brisati sadržajno važne komentare bez odluke korisnika. Novi Word save može ponovno dodati svojstva, stoga je posljednji hash nakon posljednje obrade.

## 7. Regresijska matrica — plan, ne rezultat testiranja

Primjeri su sintetički i ne predstavljaju statistike, pravne tvrdnje ili podatke stvarnih poduzeća. Za svaki scenarij trebaju problematičan i legitimni kontrolni primjer. Navedeni su očekivani ishodi, ne ostvareni PASS rezultati.

| ID | Problematičan scenarij | Očekivanje i negativna kontrola |
|---|---|---|
| E01 | `passed=false`, prazna matrix, prisutni preconditions | Recenzentska leća prenosi odbijanje; valjan strict PASS ostaje čist |
| E02 | `{}`, kriva shema ili djelomičan izvještaj | Invalid/unmeasured, ne clear; valjan izvještaj se prihvaća |
| E03 | Dva poglavlja bez usporedivih tvrdnji | Nedovoljna cross-chapter pokrivenost; deklarirane usporedive tvrdnje daju mjerljiv rezultat |
| E04 | Adversarial/advisory izvještaj predstavljen kao strict | Nema strict GO; ispravno označen advisory ostaje savjetodavan |
| E05 | Izvještaj za dokument A isporučuje se uz B | Stale/mismatch; isti bajtovi pod drugim imenom zadržavaju sadržajni dokaz |
| E06 | Promijenjen source/claims snapshot bez nove provjere | Invalidirati ovisne provjere; isti snapshot ostaje valjan |
| E07 | Ukupno 600 uključuje 150; izračun zbraja 600 + 150 | Dvostruko brojanje; 450 + 150 = 600 prolazi |
| E08 | Stopa s 40 % na 50 % nazvana je +10 % relativno | Zahtijevati +10 p.b. ili +25 % relativno; obje točne oznake prolaze |
| E09 | 200 t ulaza uspoređuje se sa 70 t izlaza iz druge godine kao ista veličina | Neusporedivost za tu operaciju; deklarirana ulaz/izlaz bilanca iste serije se može računati |
| E10 | Kapacitet 10.000 t/god. prenesen kao ostvarena količina | Pogrešna promjena statusa; ispravno označen kapacitet prolazi |
| E11 | 8 % kategorije A pretvoreno je u tvrdnju da 92 % ima svojstvo B | Nepotkrijepljena implikacija; komplement „nije A” prolazi |
| E12 | Nepoznati primatelj materijala pretvoren je u „nema primatelja” | Unknown nije false; dokumentiran nulti broj primatelja smije biti nula |
| E13 | Uzorak zahtijeva potvrđenog primatelja, slučaj ga nema | Nepodudarnost kriterija; izričito izdvojen pilot bez tvrdnje o ispunjenju kriterija prolazi |
| E14 | Premisa promijenjena, sažetak i zaključak nasljeđuju stari pregled | Tranzitivni review_required; neovisan dokaz potomka dopušta novi pregled |
| E15 | Ovisnosti imaju ciklus ili nepoznat claim_id | Jasan validation failure; ispravan DAG prolazi |
| E16 | „Moguća povezanost” u stilskom zahvatu postaje „uzrokuje” | Review kandidat uz prikaz prije/poslije; očuvana nesigurnost ne daje nalaz |
| E17 | Iz četiri slučaja zaključeno je „svi subjekti” | Stručni pregled opsega; „u analiziranim slučajevima” nije blanket nalaz |
| E18 | Certifikat jedne lokacije potvrđuje sve brojke cijele grupe | Scope mismatch; tvrdnja ograničena na predmet certifikata prolazi |
| E19 | Dvije godine imaju različite ostvarene iznose | Ne smiju automatski postati kontradikcija; različite vrijednosti za isto mjerenje se prijavljuju |
| E20 | Zbroj je veći od zaokružene ukupne vrijednosti unutar opravdane tolerancije | Ne stvarati lažni nalaz; veliko odstupanje izvan tolerancije se prijavljuje |
| E21 | Vizualna dorada mijenja brojku, citat ili oznaku u grafu | Mutation invariant pada; isključivo estetska promjena prolazi |
| E22 | Duga ćelija/fiksna visina reže tekst; redak je viši od stranice | Render pokazuje kvar; ispravan višestranični prijelom prolazi |
| E23 | Alt-opisi rednim brojem pridruženi pogrešnom vizualu | Otkriven mismatch po identitetu; točno pridružen logo/grafikon prolazi |
| E24 | Dupli `docProps/core.xml`, skrivena svojstva ili ponovno dodan autor | ZIP/privacy provjera pada za deklarirani opseg; čista kopija čuva prikaz i reference |
| E25 | Sadržaj je pregledan, administrativna polja izričito izuzeta | Samo scoped GO; isključeni potpis/JMBAG nije ni izmišljen ni označen kao prošao |
| E26 | Nedostaje render/alat/live quota; izvještaj kaže „sve provjereno” | Unmeasured/blocked readiness; potpuni mjerljivi trag može zadovoljiti odgovarajući gate |

Parove testirati i izravno i kroz stvarni CLI/potrošača izvještaja. Broj tabličnih scenarija nije broj implementiranih testova. U izvještaju zasebno iskazati stvarno izvršene unit, integracijske, vizualne i live testove.

## 8. Redoslijed malih isporuka

**A — pouzdan status i identitet:** prvo reproducirati E01–E06 u postojećim komponentama. Prioritet je ukloniti mogućnost da nevažeći ili negativni dokaz postane čista recenzentska leća. Postojeći artifact manifest ostaje izvor identiteta. Ovaj korak može postati prvi mali implementacijski PR nakon pregleda specifikacije i plana.

**B — značenje brojki:** validirana dodatna shema/kontekst, izračuni, jedinice, uloge, kapacitet/rezultat, skupovi, zaokruživanje i vremenske serije. Bez uvlačenja neprovjerenog semantičkog tumačenja PDF-tablica.

**C — rasuđivanje i stilske regresije:** deklarirane ovisnosti, promjena premise, kriteriji uzorka, opseg certifikata i pregled povećane sigurnosti tvrdnje. Heuristike ostaju SIGNAL; ne glume kauzalni ili pravni sud.

**D — točna isporuka:** vlasničke rad-docx provjere mutacije, tablica, vizuala, metapodataka i svježeg rendera; orchestration dokaz veže sve uz posljednje bajtove isporuke.

Prije pojedinog PR-a pročitati pripadajuće aktualne satelitske contracte i testove. Njihov puni audit nije proveden tijekom pripreme ovog nacrta. Spajanje ovisi o testiranom zajedničkom headu, a ne o tome jesu li svi koraci zasebno izgledali zeleno.

## 9. Dokaz prihvata, privatnost i troškovi

Svaki potvrđeni kvar treba test koji pada na stvarnom mehanizmu prije izmjene i prolazi poslije, uz legitimne kontrole. Ne zamjenjivati puni paket malom skupinom novih testova. Sačuvati postojeće grupe i dodati nove u aktualni runner. Verzija alata, exit-code, input/output hash, status pokrivenosti i ograničenja idu u dokaz.

Ne prikazivati lokalni test kao GitHub CI niti CI kao živu provjeru Claudea. Bez aktualnog pristupa modelu live eval je neizveden, ne PASS. Ne uključivati API billing, ne mijenjati secret i ne trošiti live kvotu za dokumentacijski nacrt. Trenutačni lokalni runtime nije mogao anonimno klonirati repo zbog DNS-a; izvorne datoteke za ovaj nacrt pročitane su GitHub konektorom. Puni suite nije pokrenut i nema release tvrdnje.

Javno se objavljuju isključivo sintetički tekstovi i minimalni umjetni DOCX/PDF primjeri izrađeni za test. Izvorna dokumentacija incidenta ostaje privatna. Samo uklanjanje imena iz cijelog rada nije dovoljna anonimizacija. Novi scenarij ne ulazi u katalog potvrđenih kvarova alata dok se na vlasničkom kodu ne reproducira; do tada je prihvatni zahtjev/ideja.

## 10. Odluka potrebna za nastavak

Potvrditi ovaj dizajn: nadogradnja postojećih komponenti, zaseban kompatibilni kontekst, strogo razdvojeni deterministički nalazi i stručni pregled, četiri male isporuke, bez promjene #52 ili fakultetskih profila. Nakon pregleda slijedi konkretan implementacijski plan za isporuku A, zatim TDD i zaseban PR. Nema automatskog mergea ni proglašenja verzije 2.1.
