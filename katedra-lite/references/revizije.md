# Track Changes i pogled dokumenta

Word dokument s neprihvaćenim `w:ins`/`w:del` ne smije se analizirati kao da je običan konačni tekst, jer ekstrakcija može preskočiti umetnuti ili zadržati obrisani sloj.

## Pravilo pogleda

1. Izvornik ostaje netaknut.
2. `revizije.py provjeri` utvrđuje postoje li praćene izmjene.
3. Za strojnu analizu koja treba konačni tekst dopušteno je napraviti **accepted-copy** s `revizije.py prihvati`; rezultat mora biti nova datoteka.
4. U izvještaju napiši koji je pogled analiziran: `original`, `accepted/final` ili drugi eksplicitno dobiveni pogled.
5. Ako zaključak o autorstvu, mentorovoj namjeri ili sadržaju materijalno ovisi o tome treba li izmjenu prihvatiti, nemoj pretpostaviti da je `accept all` korisnikova odluka.

Snapshot prije zahvata i dalje vrijedi. Accepted-copy je tehnička normalizacija za analizu, ne automatsko odobravanje mentorovih prijedloga.

Kad alat ne zna proizvesti traženi Word view, reci da nije izmjereno i koristi view koji se može dokazivo dobiti; ne rekonstruiraj ga nagađanjem iz XML-a.
