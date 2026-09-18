# Privatnost projektnog stanja

`.katedra/` je trajno projektno stanje, ali **nije automatski javni git sadržaj**.

## Zadano ponašanje

- Čuvaj stanje lokalno ili u privatnom projektu kojem korisnik svjesno upravlja.
- Ne commitaj automatski mentorove komentare, privatnu građu, osobne profile, lokalne putanje, neobjavljene podatke ili izvedene datoteke samo zato što su u `.katedra/`.
- Prije dijeljenja repoa provjeri sadrži li `.katedra/` osobne ili neobjavljene podatke.

## Preporučeni ignore obrazac za javni/studentov repo

```gitignore
.katedra/isporuke/
.katedra/migrations/
.katedra/zamjerke.json
.katedra/stil_autora.json
.katedra/napredak_povijest.jsonl
.katedra/evidence*.json*
.katedra/claims*.json*
```

Strukturne datoteke poput plana ili minimalnog stanja mogu se verzionirati kad korisnik to želi i kad ne nose osjetljive podatke. Privatnost je jača od pogodnosti reprodukcije.
