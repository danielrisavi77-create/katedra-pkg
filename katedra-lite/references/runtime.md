# Runtime i bootstrap

> Učitava se samo kad Katedra treba pokrenuti skriptu, razriješiti satelit ili dijagnosticirati instalaciju. Ne učitava se za običan quick-path rad s tekstom.

## Načelo

`SKILL.md` je router. Izvršni kod, profili i reference žive u `katedra-pkg`. Runtime se mjeri u aktualnoj sesiji; ne pretpostavlja se da su Claude Desktop, Claude Code, Cowork i cloud chat ista površina.

## Redoslijed izvora

1. Ako je paket priložen u sesiji kao zip/bundle, koristi njega.
2. Ako je repo već dostupan u radnoj okolini, koristi ili osvježi tu kopiju bez destruktivnog reseta.
3. Za javni repo dopušten je anonimni read/clone ako ga okolina dopušta.
4. Synced kartica je zadnja rezerva i može sadržavati samo `SKILL.md`; skripta koja fizički ne postoji označava se `preskočeno`, nikad se ne izmišlja.

Ne ugrađuj GitHub tokene u URL, naredbu, log ili skill. Za privatni repo koristi autoriziranu vezu/sesiju koju je korisnik već spojio.

## Minimalni bootstrap

```bash
export KATEDRA_PKG="${KATEDRA_PKG:-$HOME/.katedra-pkg}"
if [ -f "$KATEDRA_PKG/bin/env.sh" ]; then
  . "$KATEDRA_PKG/bin/env.sh"
  echo "katedra-pkg $KATEDRA_PKG_VERZIJA"
else
  echo "⚠️ katedra-pkg nije dostupan; strojni koraci koji traže skripte ostaju preskočeni"
fi
```

Kad je repo dostupan, prije rada koji ovisi o satelitima pokreni:

```bash
. "$KATEDRA_PKG/bin/env.sh"
python3 "$KATEDRA_PKG/katedra-lite/scripts/vjestine.py" --provjeri
python3 "$KATEDRA_PKG/katedra-lite/scripts/drift.py" --svi --kratko
```

Exit/greška alata je stanje okoline ili nalaz, ne prolaz. Push/read ovlasti se ne zaključuju jedna iz druge. Ako host odbije repo operaciju pravilom politike, ne pokušavaj zaobilazne credential rute.

## Verzije

`VERSION` je `package_version`. Certificirani frozen ugovor jezgre je zaseban `core_contract`. Aktivna kartica ne smije tvrditi drugi package version; provjera je `katedra/scripts/verzija.py --provjeri` i `katedra-lite/scripts/router_contract.py`.


## Izvor sesije, Cowork i drift

GitHub read/write pristup nije svojstvo URL-a nego aktualne sesije. Ako proxy odbije write ili
repo nije autoriziran, rješenje je **izvor sesije** / autorizirana veza koju host stvarno
nudi; ne pokušavaj tokenom u URL-u zaobići odluku politike.

Cowork, Claude Code, Desktop i cloud chat nemaju nužno iste repo mogućnosti. Za Cowork
posebno **ne pretpostavljaj** postojanje repo pickera ili write ovlasti: izmjeri što sesija
stvarno može i prijavi ograničenje.

Kad je Full path prvi put učitao runtime i paket je dostupan, korisniku jednom prikaži
`KATEDRA_PKG_VERZIJA` i rezultat:

```bash
python3 "$KATEDRA_PKG/katedra-lite/scripts/drift.py" --svi --kratko
```

To vrijedi za runtime/full-path sesiju, ne za Quick path koji uopće ne treba paket.

**Kad kartica zaostaje (❌ uz „kartica zaostaje za repoom — verzija iz commita …")**, to se
korisniku kaže jednom rečenicom, s imenima skillova. Skripte i tada dolaze iz paketa, ali
router koji se učitava u svaku poruku je stariji od doktrine u repou. Ažuriranje je korisnikovo:
u sesiji koja nudi prijedlog skilla (review kartica), predloži novi `SKILL.md` iz paketa za
svaki skill koji je ❌, cijeli i nepromijenjen; inače mu reci da kartice zaostaju i od koje
verzije. Kartica se ne „popravlja" ručnim spajanjem dviju verzija u sesiji. Izmjereno
22. 9. 2026.: nakon releasea 2.0 pet od sedam kartica ostalo je na commitima 0dee1f2 i
b28d53e (router katedra-litea 44 KB umjesto 12 KB), a provjera je pokrivala samo katedra-lite.
