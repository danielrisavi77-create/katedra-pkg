---
name: rad-orchestrator
description: "Orkestrator faza rada (plan → pisanje → audit → predaja) koji kroz Workflow tool pokreće STVARNE katedra-lite skripte i satelite (rad-audit, rad-docx, fpzg-diplomski, replikacija-pspp): paralelni multi-lens audit s lens budgetom, bidirekcionalni povratak na raniju fazu, zaustavljanje s pitanjima za autora umjesto beskonačne petlje, mod rad_docx za gotov tuđi rad. Aktiviraj na 'pokreni orkestrator', 'provuci rad kroz sve faze', 'audit + predaja u jednom', 'rad-orchestrator', ili kad korisnik želi više Katedrinih skillova po fazi. Ne aktiviraj za jedan izolirani zadatak (samo tipografija) — za to je katedra-lite izravno. (v1.3.0: tvrdi gate po gate.py izlaznom kodu; skripta živi samo u paketu, testirano na 3 fixture-a.) v2.3.1."
---

# RAD-ORCHESTRATOR — više skillova po fazi, kroz stvarne skripte

Ovaj skill NE piše rad i NE zamjenjuje `katedra-lite`. On **pokreće** Workflow (`scripts/rad-orchestrator.js`)
koji u svakoj fazi zove skripte katedra-lite (`stanje_init`, `plan_state`, `rukopis`, `build_docx`, `gate`,
`nalazi_trag`, `napredak`) i satelite, pa se svaki artefakt rađa u `.katedra/` i može ga čitati svaki
sljedeći alat. Slobodan markdown bez `.katedra/` stanja je kvar, ne rezultat.

## 0. Ulazni protokol — prije poziva Workflowa

1. **Dohvati paket** (isti korak kao katedra-lite §0.0 — repo `katedra-pkg`; synced kopija je rezerva):
   ```bash
   export KATEDRA_PKG="$HOME/.katedra-pkg"
   export KATEDRA_PKG_URL="https://github.com/danielrisavi77-create/katedra-pkg.git"            # cloud sesija s priključenim repoom, ako to sučelje nudi
   export KATEDRA_PKG_URL_TOKEN="UPIŠI_URL_S_TOKENOM"   # https://<token>@github.com/danielrisavi77-create/katedra-pkg.git (desktop VM / okolina bez GitHub proxyja)
   # 1) priložen paket u chatu (katedra-pkg*.zip ili *.bundle) uvijek ima prednost — radi u SVAKOJ sesiji, bez GitHuba
   P="$(find /root/.claude/uploads "$HOME/uploads" /mnt/user-data . -maxdepth 4 \( -iname 'katedra*pkg*.zip' -o -iname 'katedra*pkg*.bundle' \) -printf '%T@ %p\n' 2>/dev/null | sort -rn | head -1 | cut -d' ' -f2-)"
   if [ -n "$P" ]; then rm -rf "$KATEDRA_PKG"; case "$P" in *.bundle) git clone -q "$P" "$KATEDRA_PKG";; *) mkdir -p "$KATEDRA_PKG" && unzip -oq "$P" -d "$KATEDRA_PKG" && { [ -f "$KATEDRA_PKG/bin/env.sh" ] || { D="$(ls -d "$KATEDRA_PKG"/*/ | head -1)"; [ -f "$D/bin/env.sh" ] && mv "$D"/* "$D"/.[!.]* "$KATEDRA_PKG"/ 2>/dev/null; }; };; esac; echo "📦 paket iz priloga: $P"; fi
   # 2) git: pull ako postoji, inače clone (prvo bez tokena, pa s tokenom)
   if [ -d "$KATEDRA_PKG/.git" ]; then find "$KATEDRA_PKG" -name __pycache__ -type d -prune -exec rm -rf {} + 2>/dev/null; git -C "$KATEDRA_PKG" pull -q --ff-only 2>/dev/null || true;
   elif [ ! -f "$KATEDRA_PKG/bin/env.sh" ]; then for U in "$KATEDRA_PKG_URL" "$KATEDRA_PKG_URL_TOKEN"; do case "$U" in UPIŠI_*) continue;; esac; git clone -q --depth 1 "$U" "$KATEDRA_PKG" 2>/dev/null && break; done; fi
   # 3) što imamo
   if [ -f "$KATEDRA_PKG/bin/env.sh" ]; then . "$KATEDRA_PKG/bin/env.sh"; echo "katedra-pkg $KATEDRA_PKG_VERZIJA";
   else KATEDRA_SKILL="$(ls -d /root/.claude/skills/synced/*/katedra-lite ~/.claude/skills/katedra-lite 2>/dev/null | head -1)"; echo "⚠️ paket nije dostupan — priloži katedra-pkg-vX.zip u chat (najjednostavnije) ili priključi repo sesiji; do tada synced kopija: $KATEDRA_SKILL (skripte mogu biti starije od ovog SKILL.md-a)"; fi
   ```
   `KATEDRA_SKILL` i `<SLUG>_HOME` koje ovaj korak izveze idu u `args` (`katedra_skill`, `sateliti_dir`
   = `$KATEDRA_PKG`). Svaki idući bash poziv počinje s `. "$KATEDRA_PKG/bin/env.sh"` (Cowork ne pamti
   okolinu između poziva). Ako ni paketa ni synced kopije nema → stani i reci korisniku.
2. **Provjeri satelite**:
   ```bash
   . "$KATEDRA_PKG/bin/env.sh"; python3 "$KATEDRA_SKILL/scripts/vjestine.py" --provjeri
   ```
   Ako nešto fali, reci koji satelit i što se gubi (rad-audit → faze A–G; rad-docx → predajni docx;
   replikacija-pspp → brojke). Workflow ih traži preko `<SLUG>_HOME`, pa kao susjede katedra-lite ili
   preko `args.sateliti_dir`.
3. **Prikupi args razgovorom s korisnikom** (AskUserQuestion ili chat) — ovo je JEDINO mjesto gdje se
   korisnika pita; agenti unutar workflowa nemaju živog sugovornika i ne smiju simulirati razgovor:
   - `tip` (seminar | zavrsni | diplomski | esej), `tema`, `fakultet` (slug: fpzg/efzg/libertas iz
     registryja, inače npr. `hks-fzs`), `faza` od koje se kreće (plan | pisanje | audit | predaja),
     `empirijski` (bool), `rok` (RRRR-MM-DD, opcionalno)
   - **postojeći gotov rad** → `rad_docx: <apsolutna putanja do .docx>` i `faza: "audit"` (ili
     `"predaja"`). Tada se ne planira ni ne piše: rad.docx je izvor istine, popravci idu samo na kopiju
     (snapshot → fix → verify_rewrite → redline).
   - `full_auto: true` samo ako korisnik izrijekom kaže autopilot/„radi s defaultima" — otvorena polja
     (kolegij, mentor, upute) postaju deklarirane pretpostavke umjesto zaustavljanja.
   - `profil_datoteka` za fakultet izvan registryja ako profil postoji (npr.
     `references/fakulteti/hks-fzs.json`); inače formalni nalazi ostaju „preskočeno" (pravilo 8).
   - `project_root`: APSOLUTNA putanja mape rada (npr. `/home/claude/rad-<slug>`); agenti ne dijele cwd.
4. **Pripremi skriptu tamo gdje je Workflow može čitati** (radna mapa). Prvi redak skripte nosi
   verziju (`// rad-orchestrator v1.3.0`); redoslijed izvora: paket → synced skill:
   ```bash
   . "$KATEDRA_PKG/bin/env.sh" 2>/dev/null
   SRC="$RAD_ORCHESTRATOR_HOME/scripts/rad-orchestrator.js"; [ -f "$SRC" ] || SRC="$(ls /root/.claude/skills/synced/*/rad-orchestrator/scripts/rad-orchestrator.js 2>/dev/null | head -1)"
   [ -f "$SRC" ] && { head -1 "$SRC"; cp "$SRC" ./rad-orchestrator.js; } || echo "⛔ rad-orchestrator.js nije dostupan"
   ```
   Nema skripte ni u paketu ni u synced kopiji → **stani** i traži da korisnik priloži
   `katedra-pkg*.zip`/`*.bundle` ili priključi repo. Skripta se **ne piše napamet ni iz starije
   kopije**: do v2.1.0 ovdje je stajao „Dodatak A" s v1.2.1, dok je paket već bio na v1.3.0 (tvrdi
   gate), pa je rezerva tiho vraćala stariji gate.

## 1. Poziv

Workflow tool, `scriptPath: ./rad-orchestrator.js`, `args` kao JSON objekt (ne string):

```json
{"tip":"diplomski","tema":"…","fakultet":"hks-fzs","faza":"audit","empirijski":true,
 "rad_docx":"/…/rad.docx","katedra_skill":"$KATEDRA_PKG/katedra-lite","sateliti_dir":"$KATEDRA_PKG",
 "project_root":"/home/claude/rad-<slug>","profil_datoteka":"…/hks-fzs.json"}
```

Workflow radi u pozadini; rezultat stiže kao notifikacija. **Ne čekaj u petlji i ne pokreći drugi run
dok prvi traje** — dva runa nad istim `project_root` gaze isto `.katedra/` stanje.

## 2. Što workflow vraća i što s tim

| `status` | Značenje | Što napraviti u glavnoj sesiji |
|---|---|---|
| `zavrseno` | sve faze prošle | isporuči artefakte iz `svi_artefakti` (docx, audit-report.md, napredak.html) |
| `ceka_autora` | faza je stala jer nalaze može riješiti samo autor (izvor za tvrdnju, sadržajna odluka, `[PROVJERI STR.]`) | **postavi `pitanja_za_autora` korisniku**; odgovore proslijedi kao `args.odluke_autora` (tekst) i ponovno pozovi s `faza` = `zaustavljeno_u_fazi` |
| `ceka_stvaran_input` | deadlock guard (3 rollbacka bez napretka ili ista faza 3×) | pročitaj `pitanje_za_korisnika`, riješi s korisnikom, ponovi |
| `ceka_odobrenje_plana` / `treba_autora` u planu | završni/diplomski bez odobrenog plana i bez `full_auto` | pokaži `plan.md`, traži odobrenje, pa `plan_state.py odobri` ili `full_auto: true` |
| `nedostaju_obavezna_polja`, `nedostaje_katedra_skill` | args nepotpuni | dopuni i ponovi |

Svaki unos u `povijest` nosi `naredbe_pale` — ako nije prazno, to se korisniku KAŽE (pravilo 8/20), ne
prešućuje. `score`/`pokrivenost` dolaze iz `napredak.py`; score ispod pokrivenosti 0.5 je orijentacijski.

## 3. Željezna pravila orkestracije

1. **Setup nikad ne razgovara.** Razgovor je u glavnoj sesiji; workflow prima gotove odluke kroz `args`.
2. **Treća kategorija nalaza je `treba_autora`**, ne rollback. Audit↔predaja ping-pong zbog nedostajućih
   izvora je besmislen — workflow stane i vrati pitanja.
3. **Postojeći rad se ne prepisuje.** `rad_docx` → izvornik netaknut, snapshot prije svega, popravci na
   kopiji, `verify_rewrite` odlučuje, `redline` pokazuje.
4. **Putanje su apsolutne i dolaze iz args**, nikad iz pretpostavke o sandboxu.
5. **Alat koji je pukao nije provjera koja je prošla** — `naredbe_pale` se čitaju prije zaključka.
6. Vancouver `(n)` citati: od katedra-lite v1.9 dijalekt `vancouver` je u `citation_dialects.py` i
   rad-auditu (R16); profil zdravstvenog fakulteta mora imati `citiranje.stil: vancouver`, inače
   `check_argument` i faza B rad čitaju kao rad bez citata. `provjeri_vancouver.py` ostaje kao
   samostalna kontrola.
7. **Paket se ne mijenja iz workflowa.** Agent koji nađe kvar u katedra-lite/satelitu piše `.katedra/nalazi_paketa.md` (simptom, uzrok, predloženi diff, dokaz prije–poslije) i nastavlja u smanjenom opsegu; zakrpa ide kroz `katedra` (učenje) uz reviziju. U testnom runu 2. 9. 2026. sinteza je popravila `build_docx.py` izravno u paketu — popravak je bio dobar (SEQ natpisi, popis tablica, docDefaults), ali je prošao bez pregleda i bez dokaza u katalogu; zato ovo pravilo.

8. **Primjedbe mentora iz maila ulaze u trag prije prvog popravka.** `extract_comments.py
   mail.txt --autor "…" --out .katedra/zamjerke.json` (katedra-lite kvar 168). Primjedba koja
   nije u `zamjerke.json` ne postoji za `zamjerke.py provjeri`, pa se na kraju ne može dokazati
   da je riješena. Na kraju svaka dobiva `zamjerke.py resolve zN --status rijeseno|djelomicno
   --napomena "gdje"`. Ono što traži autorovu potvrdu (npr. koje je baze stvarno pretraživao)
   ostaje `djelomicno`, ne `rijeseno`.
9. **Mentorov zahtjev JEST odluka autora.** U `rad_docx` modu sadržajni nalazi su `treba_autora`.
   Kad korisnik izrijekom traži da se mentorove primjedbe provedu, primjedbe su `odluke_autora`
   i provode se na kopiji. Svaka namjerno promijenjena brojka ili citatni ključ navodi se u
   `verify_rewrite.py --namjerno TOKEN=RAZLOG` (katedra-lite kvar 171). Crveno koje se
   „zanemari" nije provjera.
10. **Nakon svake izmjene koja pomiče prijelom: `revizije.py toc rad_vN.docx rad_vN.docx`.**
    Zatim provjeri popis tablica i grafikona prema renderu. Do kvara 170 alat je na Wordovu
    sadržaju (w:sdt) tiho radio ništa, pa je sadržaj ostajao zastario.
11. **Nezavisni recenzent prije isporuke.** Agent koji nije vidio nastanak verzije čita je
    naspram mentorovih primjedbi (ZADOVOLJENO / DJELOMIČNO / NE) i traži nove probleme. U sesiji
    22. 9. 2026. našao je ono što alati nisu: 24 „…, a ne …" (kvar 169), mehanički ubačene
    veznike „doduše/utoliko" i ograde protiv tvrdnji koje u radu nitko ne iznosi. Vlastiti
    rad ne ocjenjuje onaj tko ga je napisao.

## 1a. Kad Workflow alata nema

Neke sesije (npr. cloud sesija bez Workflow alata) ne mogu pozvati `rad-orchestrator.js`.
Tada glavna sesija sama vodi iste faze **istim skriptama i istim redoslijedom**:

| Faza | Naredbe |
|---|---|
| Setup | `stanje_init.py` (za fakultet izvan registryja dovoljno je `--fakultet-izvan-registryja`), `diff_versions.py --snapshot`, `extract_comments.py` (docx ili mail) |
| Audit | `gate.py --faza audit` → paralelne leće kao subagenti (brojke prema izvornicima, APA/literatura) → `nalazi_trag.py zabiljezi` |
| Popravci | na kopiji; `verify_rewrite.py --namjerno …` → `revizije.py redline` → `revizije.py toc` |
| Provjera | `gate.py` ponovno, `check_ai_style.py` (kohezija i ograde), rad-audit `generate_report.py`, nezavisni recenzent (pravilo 11), `zamjerke.py provjeri` |

Razlika prema Workflowu se mora reći korisniku: nema lens budgeta ni automatskog rollbacka,
pa glavna sesija sama pazi na pravila 2 i 5. Kvar u paketu koji pritom nađe i dalje ide u
`.katedra/nalazi_paketa.md`, pa kroz `katedra` (pravilo 7).

## 4. Što je gdje

- `scripts/rad-orchestrator.js` — Workflow skripta (faze, guardovi, sheme rezultata, promptovi po fazi); jedina kopija
- Ovisi o: `katedra-lite` ≥ v1.9 (s `napredak.py`, `provjeri_vancouver.py`, `provjeri_hks_fzs.py`,
  `sigurni_popravci_hr.py`), satelitima `rad-audit`, `rad-docx`, `fpzg-diplomski`, `replikacija-pspp`
- `tests/run_fixtures.py` + `tests/fixtures/*.json` — tri fixture-a (fpzg-seminarski, efzg-zavrsni,
  hks-fzs-diplomski rad_docx), smoke bez Workflowa i provjera rezultata; zadnji stvarni prolaz i što
  je otkrio: `tests/README.md`
- Povijest nastanka i mjereni nalazi: `katedra-lite/docs/PROMJENE.md` (v1.9, v1.9.1)

---
