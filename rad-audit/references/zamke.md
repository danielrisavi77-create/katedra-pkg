# Katalog kvarova — `rad-audit`

Vlastiti katalog motora. Numeracija teče od 1 i neovisna je o katalozima
`rad-docx` (1–23) i `katedra-lite` (24–…). Referenca na kvar uvijek nosi vlasnika:
„rad-audit 1", ne samo „kvar 1".

Format unosa: `katedra/references/kvar.md`.

---

## 1. Domena se detektira zbrajanjem podnizova, pa rad iz medijskih studija ispadne čelična konstrukcija

`domains.detect_domain()` bodovao je svaki paket s `tl.count(k)` za korijene iz rječnika
domene. `count` traži slobodan podniz, bez granice riječi, a rječnik `celik` sadrži korijene
koji su u hrvatskom obične riječi: `stup`, `okvir`, `temelj`, `profil`.

Na diplomskom radu iz medijskih studija (moralne panike oko koncerata, 13 203 riječi) to je
dalo **83 boda za „celik"** i klasifikaciju `čelične konstrukcije / građevinarstvo`. Razlaganje
po ključnoj riječi pokazuje da **nijedan pogodak nije bio pojam iz struke**:

```
stup     30×   dostupan, dostupna, dostupnost, nastup, nastupa
okvir    38×   teorijski okvir, analitički okvir, uokvirivanje
temelj   13×   temelji se, temeljna
profil    2×   profilima (korisnički profil na mreži)
```

Posljedica nije kozmetička. Faza C nastavlja s rječnikom te domene, pa je „Vrijednosti po
jedinici" ostalo prazno, „Kandidati za sukob" vratilo **„nema"**, a ručni podsjetnik na kraju
faze glasio je „površina = Σ(a×b)?" i „broj stupova/greda vs broj okvira?" — nad radom o
glazbi. Stvarni brojčani sukob u tom radu (isti podatak jednom kao **„oko četrdeset pet
zemalja"**, drugi put kao **„iz oko 4 zemalja"**) prošao je neopaženo.

Dva su uzroka i oba su popravljena u `scripts/domains/__init__.py`:

1. **nema granice riječi** — korijeni se sad traže na početku riječi (`(?<!\w)` + korijen),
   čime „nastup" i „dostupan" prestaju biti stupovi. Na istom radu 83 → 38 bodova.
2. **golo zbrajanje nije dokaz struke** — na dovoljno dugom tekstu dvije česte riječi
   prijeđu svaki fiksni prag. Domena se sad prihvaća samo ako uz `min_score` ima i jedan od
   dva dokaza: **≥ 5 različitih** ključnih riječi (`MIN_RAZLICITIH`) ili **≥ 1 domensku
   oznaku** iz `claim_patterns` (IPE 300, S235, RAL 9006, IP44, HTTP 404…). Rad iz medijskih
   studija ima 4 različite i 0 oznaka → `generic`, što je točan odgovor.

`detect_domain_detail()` uz odluku vraća i razlog, pa `numbers_inventory.py` ispisuje
`↳ 'celik' ima 38 bodova, ali samo 4 različitih ključnih riječi (traži se 5) i 0 domenskih
oznaka`. Kriva detekcija je time barem vidljiva, a ne tiha.

Fixtures u `katedra/assets/`: `domena_celik.docx` (stvarni inženjerski rječnik — i prije i
poslije daje `celik`, bez regresije) i `domena_drustvene.docx` (`celik` prije → `generic`
poslije).

## 2. Ključ `Prezime, I. (GODINA)` ne poznaje izvor bez osobnog autora, pa medij i institucija ispadnu citat bez reference

Faza B gradi ključeve iz popisa literature uzorkom `Prezime, I. (GODINA)`. Izvor kojemu je
autor institucija, medij ili platforma nema to lice, pa redak ne uđe u popis definiranih —
a citat u tekstu uđe u popis citiranih. Razlika se onda javi kao kršenje.

Prva pojava (25. 8. 2026., čekaonica `katedra/references/ideje.md`): rad s ministarstvima,
zakonima u *Narodnim novinama*, strategijama i presudama, 8–9 lažnih siročadi, ručna
provjera dala nula.

Druga pojava (3. 9. 2026.): diplomski s korpusom medijskih tekstova. Motor je sam prijavio
`(35 redaka u popisu literature sadrži godinu ali nije prepoznato kao 'Prezime, I.
(GODINA)' — pregledaj ručno format)`, pa izlistao **38 „CITAT BEZ REFERENCE"**:

```
('danas.hr','2025') ('entrio','2025') ('index.hr','2025') ('jta','2025')
('net.hr','2025') ('narod.hr','2025') ('poskok.info','2025') ('vreme.com','2025') …
```

Od tih 38 samo je jedan bio stvaran nalaz (`danas.hr`, izvor doista nije u popisu) i jedan
stvarna pogreška u radu (`('dnevno.hr','3035')` — nemoguća godina, koju alat izlista ali ne
prepoznaje kao nemoguću). Ostalo je šum, i u njemu se ta dva prava nalaza gube.

Isti uzorak radi i obrnuto: `Tonković 2014` prijavljen je kao **siroče**, a citiran je u
obliku `(…, 2020; usp. Tonković, Krolo i Marcelić, 2014, za analizu)` — ključ nije prepoznao
`usp. …, GODINA, za …`.

**Popravljeno u 1.9.2.** `BIBLIO_LINE_RE` ostaje prvi, stroži parser za osobne autore, a
drugi parser uzima naziv institucionalnog autora prije prve parentetizirane godine. Time
točke u nazivima medija/platformi i točka iza kratice više ne prekidaju ključ. Parser
citata uklanja signalnu riječ (`usp.`, `vidi`, `prema`, `cf.`) i kratku napomenu nakon
godine prije gradnje ključa.

Dokaz je end-to-end fixture s `danas.hr`, `Index.hr`, Ministarstvom, UNESCO-om i
Tonkovićem u obliku `usp. …, 2014, za analizu`: prije 2/5 definiranih, 1 lažno siroče i 3
lažna citata bez reference; poslije 5/5, bez nalaza, exit 0. Guardovi zasebno dokazuju da
stvarno nedostajući medij i nepodudarna godina i dalje ostaju prijavljeni.

## 3. Lokator stranice poznaje samo dvotočku, pa narativni citat u apa-hr dijalektu nestaje

Lokator u `common.LOKATOR` bio je pisan za FPZG oblik `(Becker, 2007: 9)`. Apa-hr piše
`, str. 170`, i taj oblik zagradni parser proguta repnom klauzulom, a narativni nema.
Posljedica je da `Šimović (2008, str. 6)` nije citat, a njegov redak u popisu literature
postaje siroče. Na seminarskom radu iz poreznog računovodstva bilo je pet narativnih i
četiri zagradna citata: siročad je bilo **točno tih pet**, a sva četiri zagradna prošla su
uredno. Nalaz je time izgledao kao autorov propust („polovica literature nije citirana"),
a bio je dijalekt koji alat ne poznaje.

```
PRIJE:   Citirano u tekstu: 5
         ⚠ SIROČAD: [('anić-antić','2012'),('anić-antić','2018'),
                     ('banović','2020'),('bratić','2006'),('šimović','2008')]
POSLIJE: Citirano u tekstu: 10
         SIROČAD: nema
```

Popravak proširuje `LOKATOR` na oba dijalekta (`: 9` i `, str. 170`, uz `s.`, `p.`, `pp.`).
Ograda: uzorak i dalje traži broj iza kratice, pa `(Autor, 2020, prema Ivić)` nije lokator
nego druga stvar. Razlikuje se od kvara 2: ondje izvor **nema osobnog autora**, ovdje ga ima,
a ispada zbog oblika stranice. 84 regresijska testa prolaze nepromijenjeno.

## 4. Točka unutar zagrade i redni broj pred velikim slovom lome rečenicu, pa faza E mjeri staccato kojega nema

`common.sentences` štiti kratice, ali ne i dva česta slučaja u pravnoj i računovodstvenoj
prozi: redni broj iza najavne riječi (`prema članku 6. ZPD-a`) i točku unutar otvorene
zagrade (`(MRS 12, t. 24.)`). Prvi lomi rečenicu na velikom slovu koje slijedi, drugi
proizvodi fragment `24.).` od jedne riječi. Nedostajalo je i pravilo o rednom broju pred
malim slovom, koje `katedra-lite/hr_text.py` ima od početka, pa se lomio i datum
(`od 1.` + `siječnja 2026.`).

```
PRIJE:   rečenica: 305 | medijan: 19   | vrlo kratke (≤8): 73 (24 %)
POSLIJE: rečenica: 270 | medijan: 21.0 | vrlo kratke (≤8): 43 (16 %)
```

Ručno brojenje iste proze daje 193 rečenice i medijan 24, pa je alat prijavljivao staccato
ritam na tekstu kojemu je medijan iznad praga. Popravak dodaje tri pravila zaštite prije
dijeljenja. Ograda koja ostaje: preostalih 16 % kratkih fragmenata nisu rečenice nego
brojevi naslova (`1.2.`, `UVOD 1.1.`) koje ekstrakcija ulijeva u isti tok teksta — to je
kvar ekstrakcije, ne dijeljenja, i mjeri se zasebno. Isti mehanizam u drugom kodu vodi se
kao `katedra-lite` kvar 46.

## 5. Otisak motora se računa iz izvora, a u contract se upisuje rukom, pa svaka zakrpa tiho obori audit

`katedra_adapter.otisak_motora()` hashira sve `*.py` u `scripts/` osim sebe i vraća
`0.0.0-undeclared+<8 znakova>`. `engine_contract.json` istu vrijednost nosi kao statičan
tekst. Svaka izmjena bilo koje skripte motora mijenja otisak, contract ostaje star, i
Katedra odbija rezultat:

```
⚠️  nekompatibilan rezultat (DocumentAuditResult):
    DocumentAuditResult engine_version ne odgovara engine contractu
contract: 0.0.0-undeclared+975259d7 | stvarno: 0.0.0-undeclared+835f7663
```

Zapreka je ispravna po namjeri (contract mora opisivati motor koji stvarno radi), ali nema
dokumentiranog koraka koji contract osvježava, pa popravak jednog kvara u motoru gasi cijeli
audit dok netko ne pogodi uzrok. U ovoj se sesiji to dogodilo odmah nakon popravaka kvarova
3 i 4: `--provjeri` je i dalje javljao ✅ (čita contract, ne otisak), a tek `--audit` je pao,
i to porukom koja ne spominje da je uzrok vlastita izmjena.

```bash
python3 -c "import sys,json; sys.path.insert(0,'rad-audit/scripts'); \
import katedra_adapter as ka; p='rad-audit/scripts/engine_contract.json'; \
c=json.load(open(p)); c['engine_version']=ka.otisak_motora(); \
json.dump(c,open(p,'w'),ensure_ascii=False,indent=2)"
```

Popravak je zasad postupak, ne kod: naredba iznad je **zadnji korak svake zakrpe koja dira
`rad-audit/scripts/`** i tako stoji u `PROMJENE.md`. Ograda: dok se otisak upisuje rukom,
ništa ne sprječava da ga netko osvježi bez pokretanja testova, pa uz njega uvijek ide i
`python3 rad-audit/scripts/tests/test_all.py` (84 provjere).
