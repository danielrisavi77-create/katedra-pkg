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
