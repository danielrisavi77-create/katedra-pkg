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

**Nije popravljeno u ovoj zakrpi.** Popravak traži drugi razred ključeva za izvore bez
osobnog autora (medij / institucija / platforma) i svođenje naziva iz kosih padeža u
nominativ prije usporedbe, a to je zahvat u `check_citations_authoryear.py` koji treba
vlastiti skup fixtura. Ovdje je zapisan da druga pojava ne ostane u čekaonici i da se ne
otkriva treći put. Dok stoji: nalaz faze B nad radom s medijskim ili institucionalnim
korpusom čita se kao **hipoteza**, ne kao popis — i to se korisniku kaže.
