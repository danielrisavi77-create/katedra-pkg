# Prioriteti: HARD, GATE, SIGNAL

Ne tretiraj sve provjere kao jednako snažne tvrdnje.

## HARD

HARD je univerzalni integritet/sigurnost i ne preskače se radi brzine:
- ne izmišljaj izvor, stranicu, brojku, citat, rezultat ili pravilo fakulteta;
- priložena građa i provjereni primarni izvori imaju prednost nad modelskim sjećanjem;
- mutacija artefakta traži povratnu točku i provjeru onoga što je moglo biti izgubljeno;
- `preskočeno`, `alat pukao` i `nepoznato` nikad nisu `prošlo`;
- osjetljivi projektni podaci ne objavljuju se niti commitaju automatski;
- deklariraj granicu provjere umjesto da je popuniš pretpostavkom.

## GATE

GATE je proceduralni preduvjet za određenu fazu. Primjeri: plan velikog rada prije pisanja, resolved profile prije formalne predaje, phase gate prije deklaracije spremnosti, manual body-read prije predaje.

Gate može biti izuzet samo ako postojeći alat to podržava, korak je imenovan i razlog ostaje zapisan. Izuzeće znači `dopušten preskok`, ne `prošlo`.

## SIGNAL

SIGNAL je heuristika koja traži pregled, ali sama ne dokazuje kvar. Primjeri: AI-style signali, n-gram sličnost s uzorkom, ritam rečenica, rubrika/napredak score i nepragmatični pragovi izvedeni iz malog broja slučajeva.

Signal se u korisničkom izvještaju opisuje kao razlog za provjeru. Ne koristi se sam kao razlog za blokiranje predaje osim ako službeno pravilo ili zaseban dokaz ne podigne isti problem u HARD/GATE kategoriju.

## Stare numeričke reference

Brojevi nekadašnjih „željeznih pravila” **nisu javni API od v2.0**. U starim komentarima, katalogu kvarova i povijesnim dokumentima mogu ostati kao trag verzije u kojoj su nastali, ali ne određuju današnji prioritet niti se novi tekst smije pozivati samo na broj.

Kad stara referenca kaže npr. „pravilo 8” ili „pravilo 17”, čitaj stvarni opis problema i mapiraj ga na HARD/GATE/SIGNAL. Ako se povijesna formulacija sudara s aktualnim routerom ili službenim pravilom, aktualni router i dokazani izvor pobjeđuju.

Posebno: stara formulacija **„uzorak je jači od profila”** više nije normativna. Ispravno je: pisana mentorova uputa → službene upute → potvrđeni profil → obranjeni primjerci → heuristike. Primjerak je jači samo od nepotvrđene procjene o lokalnoj praksi.
