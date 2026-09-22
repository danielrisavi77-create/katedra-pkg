# Ciljani zahvat: dokument, primjer i dokaz nisu isti ulaz

Kada korisnik daje postojeći Word i fotografiju uz „napravi ovako u radu”,
cilj je Word, a fotografija referenca izgleda. Ne generiraj sliku umjesto dokumenta.
Ne kopiraj ime, temu, mentora, potpis, logotip, povjerenstvo ili datum iz tuđeg rada.
Fotografija ne postaje službeni fakultetski profil. Korisnikovo uklanjanje prve
naslovnice nije opće pravilo da svi diplomski radovi moraju imati jednu naslovnicu.

## Postupak

1. Utvrdi točan ciljni artefakt; naziv „FINAL” nije identifikator verzije. Odvoji
   vizualne reference od izvora podataka. Iskoristi postojeći snapshot/diff postupak
   (`diff_versions.py`), a ne novi paralelni dnevnik projekta.
2. Potvrđenu korisnikovu uputu prevedi u najmanji eksplicitni plan izmjene vezan uz
   SHA-256 ulaza. Indeksi dolaze iz `rad-docx/scripts/ciljane_izmjene.py inspect`;
   nisu brojevi fizičkih stranica. Ne popunjavaj plan pretpostavljenim podacima.
3. Za podržan mali zahvat delegiraj `rad-docx/scripts/ciljane_izmjene.py apply`.
   Motor prije pisanja stvara točan snapshot i zatim ponovno čita napisani izlaz.
   Za nepodržano formatiranje ili odjeljak koristi odgovarajući postojeći DOCX
   postupak uz zaseban plan; ne zaobilazi odbijanje proširivanjem opsega bez odluke.
4. Provjeri stvarni diff prema dopuštenom opsegu, zatim renderiraj konačni DOCX i
   pogledaj relevantne stranice. Nakon uklanjanja prve naslovnice uspoređuj s pomakom
   stranica, ne staru prvu s novom prvom. Broj stranica nije dokaz nepromijenjenog tijela.
5. `structural_pass` nije spremnost za predaju: vizualna provjera u ovom motoru ostaje
   `ok: null`. Primijeni postojeći predajni gate. Ne zamjenjuj njegove provjere niti
   preimenuj svjesno uklonjenu godinu s naslovnice u „izgubljeni empirijski podatak”.

## Akademski naziv

`earned` označava prethodno stečeni naziv u životopisu; `awarded` označava naziv
koji opisuje odgovarajuća rubrika dokumentacijske kartice. To nisu automatski iste
vrijednosti. Službeni tekst i prijevod provjeri iz odgovarajućeg izvora ili zabilježi
izričitu korisnikovu odluku. Motor validira lokaciju i postojanje oznake izvora,
**ne dokazuje istinitost titule, završetak studija ni sadržaj povezanog izvora**.

Ne radi globalnu zamjenu `mag.`/`bacc.`. Ne dodaj titulu uz ime na naslovnici ako to
nije zatraženo. Ne mijenjaj priloženu službenu odluku ni sliku potpisa.

## Nejasna snimka

Nepotvrđen prijepis ostaje nepotvrđen. Naknadna korisnikova odluka može odobriti
konkretnu izmjenu, ali ne dokazuje što je govornica rekla niti da je ona mentorica.
Oznaka `user_confirmed` predstavlja korisnikovu odluku, a ne provjerenu transkripciju.

Testovi ugovora mjere izvršene DOCX operacije, ne pouzdanost živog modela pri odabiru
alata. Novi live multimodalni benchmark nije implementiran ovim zahvatom.
