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
python3 "$KATEDRA_PKG/katedra-lite/scripts/drift.py" --kratko
```

Exit/greška alata je stanje okoline ili nalaz, ne prolaz. Push/read ovlasti se ne zaključuju jedna iz druge. Ako host odbije repo operaciju pravilom politike, ne pokušavaj zaobilazne credential rute.

## Verzije

`VERSION` je `package_version`. Certificirani frozen ugovor jezgre je zaseban `core_contract`. Aktivna kartica ne smije tvrditi drugi package version; provjera je `katedra/scripts/verzija.py --provjeri` i `katedra-lite/scripts/router_contract.py`.
