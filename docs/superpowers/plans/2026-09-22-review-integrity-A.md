# Katedra A — pouzdan rezultat audita: Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking. Nema raspoloživog neovisnog subagenta u ovoj sesiji; ne pripisivati mu pregled koji nije izvršen.

**Goal:** Spriječiti da nevažeći, odbijeni, savjetodavni, nedovoljno pokriveni ili zastarjeli rezultat provjere postane dokaz spremnosti drugog dokumenta.

**Architecture:** Nadograditi postojeće `evidence_gate.py`, `consistency_check.py` i `reviewer_simulation.py` kao proizvođače/potrošače podataka, bez kopiranja njihovih provjera. Mali zajednički validator i zasebna potvrda izvršenja povezuju postojeće izlaze s manifestom artefakata. Novi način rada uključuje se izričito; potvrđuje samo navedenu provjeru ledgera, ne cjelokupnu akademsku ispravnost rada.

**Tech Stack:** Python 3.12 kao postojeća CI referenca; standardna biblioteka, `jsonschema` iz postojećih testnih ovisnosti, `unittest`, postojeći Bash runner i GitHub konektor. Nema nove runtime usluge ni API poziva modelima.

**Spec:** `docs/superpowers/specs/2026-09-22-evidence-inference-hardening-design.md`, odobrena korisnikovim odgovorom „Da” 22. rujna 2026. Izvorni commit specifikacije: `456497573fb2e0217da5bad960935093b4c31cf7`.

**Status:** Plan za pregled. Kod, regresijski testovi i runtime potvrda opisani ispod još nisu implementirani ili pokrenuti. Kod unutar ovog dokumenta je sadržaj plana, ne dokaz izvedene izmjene.

## Global Constraints

- `katedra-lite` ostaje router i vlasnik argumentacijske konzistentnosti. Ne kopira se motor audita ni motor DOCX-a.
- `VERSION`, frozen core contract, manifest sposobnosti i tvrdnje u `SKILL.md` sada se ne mijenjaju.
- Ne mijenjati značenje postojeće v1 sheme koja ima `additionalProperties: false`.
- Stari projekti ostaju čitljivi postojećim provjerama. Novi sloj bez odgovarajućeg konteksta prikazuje `not_run` ili nedovoljnu pokrivenost, nikada potpuni semantički PASS.
- Ne mijenjati njegovu granu niti prepisivati njegove popravke: otvoreni PR #52 ostaje zaseban.
- Privatni rad, potpis, screenshotovi razgovora i biografski podaci ne ulaze u javni repo.
- Ne uključivati API billing, ne mijenjati secret i ne trošiti live kvotu za dokumentacijski nacrt.
- Nema automatskog mergea ni proglašenja verzije 2.1.

## Review Focus

1. JSON s `passed: "false"`, nepoznatom shemom, dvostrukim ključem ili brojačima koji proturječe matrici: odbiti ulaz, ne ispisati `clear` — zadatak 1.
2. Dva poglavlja s nepovezanim tvrdnjama ili ponovljenim ID-jevima: nema lažne pokrivenosti; uredna usporediva tvrdnja ostaje bez sadržajnog nalaza — zadatak 2.
3. Isti bajtovi pod novim nazivom nasuprot istom nazivu s drugim bajtovima; identitet ne ovisi o `HOME` ili radnoj mapi — zadatak 3.
4. Datoteka promijenjena tijekom provjere, stari pozitivni izlaz nakon pada novog procesa i zabranjena putanja zapisivanja: nema potvrde svježeg prolaza — zadatak 4.
5. Izuzeti koraci, savjetodavna politika, nedostajući alat i neizvedeno ljudsko čitanje: vidljiv ograničeni opseg, bez blanket GO — zadaci 1 i 5.

---

## 0. Pregledana osnova i što ovaj plan ne tvrdi

Ponovno provjeren `main`: `14c339ba7e7e40e477851316026a1901191f82a8`. PR #52: otvoren, draft, head `a40a92afba7fbbaf53ef309a5b63bf8ea9eb7ab6`, ista baza. Dokumentacijska grana: `docs/evidence-inference-hardening-20260922`.

Pregledani su `gate.py`, `artifact_state.py`, `evidence_model.py`, ulazne/izlazne JSON sheme, postojeći gate testovi, `bin/testovi.sh`, specifikacija i popis promijenjenih datoteka #52. Od planiranih izvršnih datoteka #52 dira `bin/testovi.sh`; dira i katalog/changelog koje ažuriramo samo ako reprodukcija opravda novi unos. Ne preuzimati njegov povijesni broj testova kao rezultat naše grane.

Kloniranje ove sesije završilo je DNS greškom za `github.com`. Izvori su čitani GitHub konektorom. Nisu izvršeni ni baseline suite ni RED/GREEN reprodukcije. Dokumentacijske reference na `tests/regression/` ne koristiti kao potvrđene runtime putanje: potvrđen paketni runner izravno pokreće `katedra-lite/scripts/tests/`.

### Opseg prihvata

A pokriva E01–E06 specifikacije te E25/E26 samo u pogledu statusa, isključenja i vezivanja rezultata. E07–E24 ostaju isporuke B–D. Nema novog semantičkog, pravnog ili vizualnog suca. Hash veže provjeru uz bajtove; ne dokazuje da je svaki odlomak dokumenta vjerno upisan u ledger ili da je veza `supports` stručno ispravna.

### Nove i postojeće datoteke

| Datoteka | Zahvat i jedina odgovornost |
|---|---|
| `katedra-lite/scripts/review_contracts.py` | Novo: provjera oblika i međusobne sukladnosti B13/consistency izvještaja |
| `katedra-lite/scripts/reviewer_simulation.py` | Izmjena: potrošiti cijeli status, ne samo retke nalaza |
| `katedra-lite/scripts/consistency_check.py` | Izmjena: minimalna usporedivost i validacija identiteta tvrdnji |
| `katedra-lite/scripts/review_receipt.py` | Novo: snapshot identiteta, vezano izvršenje postojećih CLI-ja i provjera svježine |
| `katedra-lite/references/review_receipt_schema.json` | Novo: stroga verzionirana shema zasebne potvrde; bez proširivanja starih shema |
| `katedra-lite/scripts/gate.py` | Izmjena: opt-in `--bound-review`, pravilno prikazan opseg i isključenja |
| `katedra-lite/scripts/tests/review_fixtures.py` | Novo: zajednički sintetički projekt s pravim ID-jevima i hashovima |
| `katedra-lite/scripts/tests/test_review_status.py` | Novo: E01/E02/E04 i legitimne kontrole |
| `katedra-lite/scripts/tests/test_review_coverage.py` | Novo: E03 i legitimne kontrole |
| `katedra-lite/scripts/tests/test_review_receipt.py` | Novo: E05/E06, promjena tijekom rada, putanje i CLI |
| `katedra-lite/scripts/tests/test_gate_bound_review.py` | Novo: stvarni gate/potrošački spoj i kompatibilnost |
| `katedra-lite/references/audit.md`, `stanje_schema.md` | Izmjena: upotreba, opseg i migracija novog načina |
| `bin/testovi.sh` | Dodati četiri grupe, bez uklanjanja postojećih |

Stare evidence, consistency, reviewer i artifact-manifest sheme ostaju neizmijenjene. `artifact_state.py` i `evidence_model.py` koriste se kao postojeći API, bez promjene identiteta i bez nove kopije njihova koda. Ako izvršitelj otkrije da to nije moguće bez promjene frozen contracta, zaustaviti tu promjenu i prijaviti konkretan razlog.

## Priprema prije zadatka 1

- [ ] Pri odobrenom početku izvršenja uspostaviti izolirani worktree ili zasebnu lokalnu kopiju; prije rada pročitati `using-git-worktrees` i `executing-plans`. Ne resetirati tuđi workspace. Provjeriti aktualni main i #52; promjenu headova zabilježiti kao novu bazu, ne forsirati povijesni SHA.

- [ ] Na čistoj bazi prvo pokrenuti `bash bin/testovi.sh` i sačuvati `.testovi/zadnji.log` izvan repoa prije sljedećeg poziva. Nedostajuća okolina nije regresija proizvoda. Ako puni repo/runtime nisu dostupni, lokalni ciljano izvedeni test nije puni suite; readiness ostaje nepotvrđen.

Izvršitelj zapisuje trenutne refove naredbama `git rev-parse HEAD`, `git status --short` i `git diff --name-only`; bez čistog ili jasno izdvojenog workspacea ne počinje promjene. Dohvat #52 radi čitanja ne daje ovlaštenje za njegovo mijenjanje.

### Zajednički pozitivni fixture

U `katedra-lite/scripts/tests/review_fixtures.py` tijekom zadatka 1 spremiti ovu funkciju. Koristi se za pozitivne B13 testove i stvarni bundle u zadatku 4; ne zaobilazi `validate_records` mockom.

```python
import json
from pathlib import Path
from docx import Document
from artifact_state import record_artifact
from claim_ledger import zapisi_jsonl
from evidence_model import (file_sha256, stable_source_id, stable_evidence_id,
                            stable_claim_id, text_sha256)

def make_project(root: Path) -> tuple[Path, Path]:
    state = root / '.katedra'
    state.mkdir(parents=True, exist_ok=True)
    sources = root / 'izvori'
    sources.mkdir(exist_ok=True)
    text = 'Otpad iznosi 20 t.'
    source = sources / 'synthetic.txt'
    source.write_text(text + '\n', encoding='utf-8')
    sid = stable_source_id({'autor': 'Synthetic', 'godina': 2020,
                            'naslov': 'Testni izvještaj'})
    locator = {'kind': 'passage', 'passage': 'odlomak 1'}
    eid = stable_evidence_id(sid, locator, text)
    ev = {'schema_version': 1, 'source_id': sid, 'evidence_id': eid,
          'text': text, 'text_sha256': text_sha256(text), 'locator': locator,
          'source_path': 'izvori/synthetic.txt',
          'source_sha256': file_sha256(source)}
    claims = []
    doc = Document()
    for chapter in ('4', '6'):
        location = {'chapter': chapter, 'paragraph': '1'}
        claims.append({'schema_version': 1,
                       'claim_id': stable_claim_id(text, location),
                       'text': text, 'location': location,
                       'evidence': [{'evidence_id': eid, 'relation': 'supports'}]})
        doc.add_heading(chapter + '. Testno poglavlje', level=1)
        doc.add_paragraph(text)
    document = root / 'rad.docx'
    doc.save(document)
    zapisi_jsonl(state / 'claims.jsonl', claims)
    zapisi_jsonl(state / 'evidence.jsonl', [ev])
    snapshot = {'izvori': [{'source_id': sid,
                          'verification': {'status': 'verified'},
                          'quality': {'class': 'primary'}}]}
    (state / 'izvori.json').write_text(json.dumps(snapshot), encoding='utf-8')
    record_artifact(root, document)
    return document, state
```

`verified` je dio sintetičkog testnog snapshota, a ne tvrdnja da je stvarni akademski izvor provjeren. Prvi pozitivni test poziva `evidence_gate.evaluate_files(state / 'claims.jsonl', state / 'evidence.jsonl', sources_path=state / 'izvori.json', policy='strict')`, zatim pravi reviewer i postojeći JSON validator. Očekuje `passed=True`, dvije tvrdnje i nula blokada.

## Zadatak 1: Ne dopustiti pranje negativnog statusa

**Files:** stvoriti `review_contracts.py` i `tests/test_review_status.py`; izmijeniti `reviewer_simulation.py` u `_load_optional`, `simulate` i evidencijskoj leći.

**Interfaces:**

`validate_report(kind: str, payload: object) -> None` i `load_report(path: str, kind: str) -> dict`. `kind` je `evidence` ili `consistency`; nevažeći ulaz podiže `ValueError`. Funkcije moraju validirati i izravni Python poziv, ne samo CLI. Sheme se učitavaju iz `Path(__file__).resolve().parents[1] / 'references'`, ne iz korisnikove radne mape. `jsonschema` učitati tek kada se ova provjera stvarno koristi; nedostajući paket je izričita greška izvršenja, ne fallback na PASS.

- [ ] Napisati RED test koji koristi stvarni postojeći producent, a ne unaprijed izmišljeni nalaz:

```python
import unittest
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import evidence_gate
import reviewer_simulation as reviewer

class ReviewStatusTests(unittest.TestCase):
    def test_E01_failed_empty_gate_is_not_clear(self):
        report = evidence_gate.evaluate_gate([], [], policy='strict')
        self.assertIs(report['passed'], False)
        self.assertTrue(report['preconditions'])
        out = reviewer.simulate(evidence_gate=report)
        lens = next(x for x in out['lenses'] if x['lens'] == 'evidence')
        self.assertEqual(lens['status'], 'risk')
        self.assertGreater(out['summary']['high_priority'], 0)

    def test_E02_empty_payload_is_rejected(self):
        with self.assertRaises(ValueError):
            reviewer.simulate(evidence_gate={})

    def test_E04_clean_advisory_is_not_strict_clear(self):
        report = evidence_gate.evaluate_gate([], [], policy='advisory')
        out = reviewer.simulate(evidence_gate=report)
        lens = next(x for x in out['lenses'] if x['lens'] == 'evidence')
        self.assertEqual(lens['status'], 'watch')
        self.assertTrue(any(x['code'] == 'evidence:advisory_only'
                            for x in out['questions']))

if __name__ == '__main__':
    unittest.main()
```

- [ ] Pokrenuti `python3 katedra-lite/scripts/tests/test_review_status.py -v` na neizmijenjenom kodu. Zabilježiti puni izlaz i pad konkretnih asercija. ImportError, nedostajuća ovisnost ili argparse greška nisu prihvatljiv RED dokaz.

- [ ] Implementirati `validate_report` preko `Draft202012Validator` nad postojećim `evidence_gate_schema.json` i `cross_chapter_consistency_schema.json`; pretvoriti grešku u `ValueError` s vrstom izvještaja i JSON putanjom, bez ispisa cijelog privatnog sadržaja. `load_report` čita UTF-8 i odbija duple ključeve i nestandardne brojeve:

```python
import json

def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f'dvostruki JSON ključ: {key}')
        result[key] = value
    return result

def invalid_constant(value):
    raise ValueError(f'nedopuštena JSON konstanta: {value}')

# U load_report: payload = json.loads(text, object_pairs_hook=unique_object,
#                                    parse_constant=invalid_constant)
# Potom validate_report(kind, payload) i vrati payload.
```

Provjeriti i relacije koje shema ne izražava: `summary.claims == len(matrix)`, jedinstvene `claim_id`, broj passed redaka i blocked redaka; dopušten je postojeći poseban slučaj strict prazne matrice s jednim blokiranim preduvjetom. Za strict `passed=True` zahtijevati nepraznu matricu, prazne preconditions, nula blocked/would_block i odsutnost razloga blokade u redcima. Za consistency zbrojevi moraju odgovarati grafu i nalazima; dangling ID-jevi u grafu nisu pozitivan dokaz. To ne provjerava istinitost `supports`, samo ugovor producenta.

- [ ] Na početku `simulate` validirati svaki dostavljeni evidence/consistency izvještaj. Za argument/mentor ne izmišljati shemu: zadržati njihovo postojeće ponašanje i izričito ih ne uključiti u vezani opseg A. Odsutan optional input (`None`) ostaje `not_run`.

Dodati pitanja s postojećim formatom `priority/code/question`: `evidence:gate_failed` (high) za svaki `passed=False`; `evidence:precondition:N` (high) za neispunjeni preduvjet; `evidence:advisory_only` (medium) za advisory; postojeći blokirani redci ostaju high; advisory `would_block > 0` daje high `evidence:would_block`. Deduplicirati istovjetna pitanja. Ne mijenjati enum statusa ili izlaznu reviewer shemu. CLI za nevažeći ulaz vraća 2; za high nalaze 1; čisti advisory može vratiti 0, ali leća je watch i nije dokaz strict prolaza.

- [ ] Dopuniti subtestove za `passed='false'`, `schema_version=999`, `preconditions` kao string, dupli ključ, NaN, neusklađene brojače, nepoznati policy i legitimni strict PASS s jednom podržanom tvrdnjom. Pozitivni fixture mora odgovarati stvarnom B13 izlazu, uključujući sva polja evidence stavke iz postojeće sheme; učitati ga kroz pravi CLI. Provjeriti da output prolazi neizmijenjenu reviewer shemu.

- [ ] GREEN: ponoviti novi test, `test_gate.py` i zatim puni runner. Commit samo ovog koraka nakon pregleda diff-a: `fix: preserve evidence gate status in reviewer output`.

## Zadatak 2: Pokrivenost znači izvedenu usporedbu

**Files:** `consistency_check.py`, `tests/test_review_coverage.py`.

**Interfaces:** ostaje `evaluate_claims(claims: list[dict]) -> dict`; bez novih polja u v1 outputu. Zajedničku provjeru ID-jeva i poglavlja pozvati i iz `evaluate_claims`, tako da je CLI ne može zaobići.

- [ ] Napisati i pokrenuti sljedeće testove prije izmjene:

```python
import unittest
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import consistency_check as cc

class ReviewCoverageTests(unittest.TestCase):
    def test_E03_two_unrelated_chapters_are_insufficient(self):
        claims = [
            {'claim_id': 'a', 'text': 'Otpad iznosi 20 t.',
             'location': {'chapter': '4'}},
            {'claim_id': 'b', 'text': 'Prihod iznosi 30 EUR.',
             'location': {'chapter': '6'}},
        ]
        out = cc.evaluate_claims(claims)
        self.assertEqual(out['coverage_status'], 'insufficient')
        self.assertEqual(out['summary']['edges'], 0)

    def test_same_claim_across_chapters_is_measurable(self):
        out = cc.evaluate_claims([
            {'claim_id': 'a', 'text': 'Otpad iznosi 20 t.',
             'location': {'chapter': '4'}},
            {'claim_id': 'b', 'text': 'Otpad iznosi 20 t.',
             'location': {'chapter': '6'}},
        ])
        self.assertEqual(out['coverage_status'], 'sufficient')
        self.assertEqual(out['summary']['blocking'], 0)

    def test_duplicate_claim_id_is_invalid(self):
        claims = [{'claim_id': 'a', 'text': 'Otpad iznosi 20 t.',
                   'location': {'chapter': c}} for c in ('4', '6')]
        with self.assertRaises(ValueError):
            cc.evaluate_claims(claims)

if __name__ == '__main__':
    unittest.main()
```

Run: `python3 katedra-lite/scripts/tests/test_review_coverage.py -v`. RED mora pokazati pogrešno označenu pokrivenost i/ili neodbijen duplikat; legitimna kontrola ne smije biti namjerno pokvarena.

- [ ] Minimalno promijeniti uvjet na `len(nodes) >= 2 and bool(edges)`. U zajedničkoj validaciji odbiti prazne/duple ID-jeve, prazan tekst i prazno poglavlje. Ne mijenjati regexe za brojeve, valute, godine ili negaciju u isporuci A; značenje vremenskih serija pripada B. U tekstualnom izlazu navesti broj poglavlja, usporedivih veza i jedinstvenih tvrdnji uključenih u te veze.

- [ ] U nedovoljnoj pokrivenosti napisati „nije bilo dovoljno usporedivih tvrdnji”, a ne sadržajnu optužbu da je rad proturječan. Ne sugerirati da korisnik izmisli ponavljanja radi prolaza. Mogući izlaz je dokumentirano stručno čitanje izvan ove automatizirane provjere.

- [ ] Dodati CLI kontrole: prazno/jedno poglavlje i nepovezana poglavlja izlaz 2; ista usporediva tvrdnja izlaz 0; stvarna postojeća brojčana kontradikcija izlaz 1; reviewer prenosi `insufficient` kao `nedovoljno_pokriveno`. `sufficient` i dalje znači samo minimalno usporediv ledger, nikad pokriven cijeli dokument. Za puni broj tvrdnji dokumenta nemamo nazivnik.

- [ ] GREEN i commit: `fix: require comparable claims for consistency coverage`.

## Zadatak 3: Potvrda vezana uz točne bajtove i konfiguraciju

**Files:** novo `review_receipt.py`, `review_receipt_schema.json`, `tests/test_review_receipt.py`. Koristi postojeće `artifact_state.current_record`, `artifact_state.file_sha256` i `context.atomic_write_json`.

**Interfaces:** ove potpise implementirati bez stubova:

`capture_context(project_root, *, document, dependencies, view, config, code_root) -> dict`; `make_receipt(before, after, *, reports, exit_codes) -> dict`; `verify_receipt(receipt, current, *, reports) -> dict`. Sve putanje koje funkcije čitaju dolaze iz eksplicitnog poziva, ne iz shell naredbe ili proizvoljne putanje pohranjene u potvrdi.

`dependencies` i `reports` su `dict[str, pathlib.Path]`; `exit_codes` je `dict[str, int | None]`. `before/after/current` su context objekti koje vraća `capture_context`. `verify_receipt` vraća `{'status': 'pass|blocked|unmeasured|stale', 'reasons': list[str], 'relocated': bool}`; `make_receipt` vraća puni zapis opisan ispod. Invalid JSON/schema podiže ValueError. Funkcije ne ažuriraju manifest.

### Točan oblik nove sheme

Root zahtijeva `schema_version:1`, `kind:'katedra_bound_review'`, `scope:'ledger_evidence_consistency'`, `status`, `before`, `after`, `reports`, `coverage`, `limitations`, `created_at`; `additionalProperties:false` na svakoj razini. Vremenska oznaka je UTC informacija, a ne dokaz svježine.

Context zahtijeva `document`, `dependencies`, `view`, `config_sha256`, `implementation_sha256`, `runtime`. Document: `artifact_id`, `version_id`, `sha256`, `size_bytes`. Dependencies je mapa logičkog ID-ja u `{sha256,size_bytes}`. Runtime: `python` i `jsonschema` verzije. `view` je `original_no_revisions`, `accepted_copy` ili `rejected_copy`; vezani runner A prima samo stvarni dokument bez aktivnog tracked layera, a izvedena kopija mora već postojati iz odvojenog odobrenog postupka.

Reports: točno ključevi `evidence`, `consistency`, `reviewer`; svaki `{sha256: string|null, exit_code: integer|null}`. Coverage: `claims`, `compared_claims`, `comparison_edges` kao nenegativni cijeli brojevi, `whole_document: false`. Limitations mora uključiti da nema stručnog dokaza svih `supports` veza, nema mjerenja svih tvrdnji dokumenta ni vizualnog/administrativnog odobrenja. Negativne i nepotpune potvrde također su valjani zapisi, ne pozitivni rezultati.

- [ ] Napisati test svježine nad sintetičkim bajtovima i stvarnim manifestom:

```python
import tempfile
from pathlib import Path
import artifact_state
import review_receipt as rr

with tempfile.TemporaryDirectory() as directory:
    root = Path(directory)
    document = root / 'rad.docx'
    document.write_bytes(b'synthetic-document-A')
    artifact_state.record_artifact(root, document)
    claim_file = root / 'claims.jsonl'
    claim_file.write_text('{}\n', encoding='utf-8')
    args = dict(document=document, dependencies={'claims': claim_file},
                view='original_no_revisions',
                config={'policy': 'strict'}, code_root=Path(rr.__file__).parents[1])
    before = rr.capture_context(root, **args)
    document.write_bytes(b'synthetic-document-B')
    # current_record i dalje opisuje stare bajtove: snapshot se mora odbiti.
    try:
        rr.capture_context(root, **args)
    except ValueError:
        pass
    else:
        raise AssertionError('neprepoznat drift dokumenta')
```

Ovo je test identiteta bajtova, ne test valjanog DOCX-a. Za integraciju u zadatku 4 koristi se stvarni minimalni DOCX. ImportError nove funkcije jest početno stanje nove značajke; nije reprodukcija starog sadržajnog kvara.

- [ ] `capture_context` zahtijeva praćen dokument čiji aktualni SHA odgovara manifestu; ne smije pozvati `record_artifact` kako bi automatski odobrio drift. Hash ovisnosti računa iz stvarnih bajtova, ne iz deklariranog hasha u ledgeru. Konfiguraciju kanonizirati `json.dumps(sort_keys=True, separators=(',', ':'), ensure_ascii=False, allow_nan=False)` pa SHA-256.

Fingerprint implementacije neka obuhvati sortiran popis svih `scripts/**/*.py` i `references/*schema*.json` unutar Katedre Lite, plus korijenski `VERSION`, te sadržaj njihovih relativnih naziva i hashova. Namjerno je konzervativan: promjena te implementacije traži novu provjeru. Ne uključivati mtime, `HOME`, apsolutni put, Git ref, privatni sadržaj ni `.pyc`. Time nevezana dokumentacijska izmjena ne čini runtime nalaz zastarjelim.

- [ ] `make_receipt`: before/after razlika daje stale; None/missing output, kriva shema, exit 2 ili viši daju unmeasured; izlaz 1 ili valjan negativni strict/reviewer rezultat daju blocked; samo potpuni strict rezultat uz mjerljivu consistency pokrivenost i tri očekivana izlaza daje pass. Nedovoljna pokrivenost nije tvrdnja da je sadržaj pogrešan. Prioritet je stale, zatim unmeasured, blocked, pass. Ne koristiti samo izlazni kod ili samo JSON.

- [ ] `verify_receipt` ponovno računa hashove triju outputa iz predanih putanja; očekivani status ne vjeruje slijepo pohranjenom `status`. Provjeriti shemu, izvorne statusne relacije, podudaranje runtime/config/code/dependency hashova i dokumenta. Stare byte-identične datoteke pod drugim imenom mogu dati pass uz `relocated=True`, ali nova putanja mora biti evidentirana u postojećem manifestu; ne izmišljati da path-based `artifact_id` ostaje isti.

- [ ] Dodati testove: preimenovanje/kopija uz eksplicitno `record_artifact`; promjena jednog bajta; promjena svakog dependencyja; promjena policy/view; isto iz drugog cwd/HOME; promijenjen source snapshot; lažirani output SHA; dupli JSON ključevi; manifest drift; identične dependency datoteke pod premještenim projektnim korijenom. Testove sve upisati kao zasebne metode u `test_review_receipt.py`.

- [ ] GREEN i commit: `feat: bind review receipts to document and evidence bytes`.

## Zadatak 4: Potvrdu smije stvarati samo svježe izvršenje

**Files:** dovršiti `review_receipt.py` subcommands `run` i `verify`; dopuniti isti testni modul. Nikakav CLI `seal-existing` ne postoji.

**Interface:** `run_bundle(project_root, *, document, state_dir, view, config, code_root) -> tuple[int, dict]`. Pokreće postojeće producente; ne implementira njihove provjere ponovo.

- [ ] Prije promjene napisati test da stara tri pozitivna JSON-a ne mogu nadomjestiti novi proces koji nije proizveo izlaz. Patchirati samo subprocess granicu u unit testu; zaseban integracijski test mora pokrenuti stvarne CLI-je bez tog mocka.

- [ ] Runner stvara jedinstven `.katedra/reviews/<uuid>/` i sljedeće izlaze: `evidence.json`, `consistency.json`, `reviewer.json`, `receipt.json`. Izvornik i njegovi ledgeri ostaju netaknuti. Runner u `<run>/inputs/` kopira samo deklarirane ulaze, uz očuvanje njihove projektno-relativne strukture i položaja `.katedra`, tako da evidence resolver zadrži isto sidrenje unutar izdvojene kopije projekta. Svaki kopirani hash mora odgovarati prethodno zabilježenom izvorniku; u suprotnom stale prije pokretanja. Procesi čitaju izdvojene kopije, ne datoteke koje korisnik uređuje. Novi bound način A zahtijeva samodostatan projekt s lokalnim source snapshotima i relativnim putanjama unutar projekta; apsolutni/vanjski source ulaz daje jasno unmeasured i uputu za postojeći ingest, bez automatskog prepisivanja ledgera. Legacy izvan bound načina zadržava podršku za vanjske izvore. Kopija ne uključuje `.git`, druge radove ni ranije izvještaje.

Pokrenuti, tim redom, postojeće CLI-je s `sys.executable`, `encoding='utf-8'`, `errors='replace'`, `timeout=180`, `shell=False`:

```text
evidence_gate.py --claims <state>/claims.jsonl --evidence <state>/evidence.jsonl --sources <state>/izvori.json --policy strict --out <run>/evidence.json
consistency_check.py --claims <state>/claims.jsonl --out <run>/consistency.json
reviewer_simulation.py --evidence-gate <run>/evidence.json --consistency <run>/consistency.json --out <run>/reviewer.json
```

`<state>` i `<run>` označavaju runtime vrijednosti kopiranog state direktorija u `<run>/inputs/` i generiranog izlaznog direktorija, ne korisničke zamjenske unose u izvršnom kodu. Kod izlaza 1 nastaviti prikupljati dijagnostiku. Ako schema-valjani consistency izlaz sadrži insufficient uz exit 2, smije ga se proslijediti revieweru, ali konačni status ostaje unmeasured. Kad nedostaje output ili je nevažeći, ne pokretati potrošača s datotekom iz ranije sesije.

- [ ] Prije prvog procesa na izdvojenoj kopiji provjeriti nepostojanje aktivnih tracked izmjena kroz postojeći `revizije.py provjeri`; ne prihvaćati izmjene. U capture uključiti document, claims, evidence, izvori snapshot, profil ako je predan i sve lokalne datoteke koje evidence zapis navodi kao `source_path`. Rezoluciju izvesti po postojećem evidence API-ju, a potom zahtijevati eksplicitni projektni kontekst: ne dopustiti da istoimeni izvor iz slučajnog cwd-a prikrije nestali izvor projekta. Nepostojeći izvor znači unmeasured. Ne pokretati mrežno osvježavanje izvora.

- [ ] Ponovno izračunati kontekst izvornika i svih izdvojenih ulaza nakon izvršenja; promjena izvornika čini dostavnu potvrdu stale, a promjena izvršnog snapshota također zabranjuje pass. Čitanje izdvojenih kopija sprječava da prolaz bude izračunan nad različitim verzijama tijekom korisnikova uređivanja. Ovo nije kriptografski potpis ni zaštita od napadača koji može mijenjati kod i potvrdu. Potvrdu zapisati atomarno s postojećim `context.atomic_write_json`, s eksplicitnim argumentom `sidro=str(project_root)`. Ne pisati kroz symlink izvan projekta. Ne mijenjati rukopis, manifest ni ulazne ledgere. Logovi ostaju lokalni; javni testovi koriste samo sintetičke podatke.

CLI `run`: potrebni `--project-root`, `--rad`, `--kat`, `--view`; optional `--profil`. CLI `verify`: isti kontekst plus `--receipt` i tri eksplicitne putanje `--evidence-report`, `--consistency-report`, `--reviewer-report`. Putanje i naredbe iz učitane potvrde nikada se ne izvršavaju. Exit 0 je pass u navedenom opsegu, 1 valjan negativan nalaz, 2 nevažeć/nepotpun/zastarjeli dokaz. Stdout i JSON koriste iste statusne riječi.

- [ ] Integracijski fixture: python-docx stvara stvarni minimalni rad; postojeći ingest/ledger API-ji stvaraju izvor, evidence i dvije usporedive tvrdnje, a `record_artifact` prati dokument. Za prije/poslije usporediti SHA svih ulaza; dozvoljeni su samo novi outputi. Provesti stvarni `run`, zatim stvarni `verify`; promijeniti dokument i ponoviti verify koji mora vratiti 2. Dodati kontrole pada procesa, timeouta, starog izlaza, nedostajućeg jsonschema paketa i zabrane izlaska kroz symlink. Test bez podrške za symlink bilježi skip; nije dokaz Windows zaštite.

- [ ] GREEN i commit: `feat: generate fresh bound-review evidence through existing CLIs`.

## Zadatak 5: Uključiti provjeru u gate bez tihog rušenja legacy projekata

**Files:** `gate.py`, `tests/test_gate_bound_review.py`, reference `audit.md` i `stanje_schema.md`.

**Interfaces:** `gate.main(argv=None)` ostaje; novi opt-in argument `--bound-review` vrijedi samo za audit/predaja i zahtijeva `--view`. Ostale faze vraćaju 2 za taj argument. Novi Korak ID je `vezani_pregled` i blokira kada je odabran. `main` tada u kontekst `c` dodaje `project_root`, `bound_review` i `view`; default pozivi `koraci` tih ključeva ne trebaju i koriste `c.get`.

- [ ] Napisati test kompozicije koraka: stari poziv vraća iste stare ID-jeve; opt-in zamjenjuje postojeći `dosljednost` vezanim bundleom na istom mjestu, a u fazi bez `dosljednost` umeće ga prije `rubrika` ili na kraj ako te stavke nema. Nema dva izvršenja iste consistency provjere.

```python
from pathlib import Path
import gate

base = {'rad': 'rad.docx', 'pdf': None, 'profil': 'p.json',
        'tip': 'zavrsni', 'kat': '.katedra'}
legacy = gate.koraci('audit', base)
assert 'dosljednost' in {x.kid for x in legacy}
assert 'vezani_pregled' not in {x.kid for x in legacy}
bound = gate.koraci('audit', {**base, 'bound_review': True,
                             'project_root': str(Path.cwd()),
                             'view': 'original_no_revisions'})
ids = [x.kid for x in bound]
assert ids.count('vezani_pregled') == 1
assert 'dosljednost' not in ids
assert next(x for x in bound if x.kid == 'vezani_pregled').blokira
```

- [ ] Izmjena `koraci` ne dodaje novi katalog validatora: postojeći Korak poziva `review_receipt.py run` s eksplicitnim root/document/state/view/profile. `pokreni` i njegov postojeći exit mapping ostaju kompatibilni. Novi flag ne uključuje se automatski zato što u mapi postoji stara potvrda.

- [ ] Ispraviti završnu tekstualnu poruku u `main`: kad postoje `iskljuceno` ili `preskok_dopusten`, ne smije reći da nijedna provjera nije izostala. Poruka glasi „Nema blokirajućih nalaza unutar odabranog opsega; izuzeti/neizvedeni koraci navedeni su odvojeno.” `--suho` nikada ne stvara pozitivni receipt. Testirati i prazan popis rezultata: ne opisivati ga kao cjelovit PASS; suhi plan i prazna provjera ostaju razdvojeni.

- [ ] Zadržati postojeće structured gate JSON polje `sazetak` i stare enum vrijednosti; sve nove detalje nosi zasebni receipt. Ne dodavati `whole_document=True`. U dokumentaciji migracije navesti da opt-in zahtijeva tracking dokumenta i dostupne source snapshote, dok legacy samostalni alati ostaju čitljivi. Minimalna coverage provjera iz zadatka 2 ispravak je starog pogrešnog prolaza, ne zahtjev za novom v1 shemom.

- [ ] Stvarni end-to-end test poziva `gate.main`/CLI s vezanim opsegom; ne lažira završnu funkciju niti JSON. Za vanjske nepotrebne korake smiju se koristiti postojeća eksplicitna isključenja s testnim razlogom; takav rezultat mora ostati scoped. Zasebno zadržati postojeći test praznog projekta koji mora pasti. Potvrditi da isključeni `vezani_pregled` nije označen kao provedena zaštita.

- [ ] GREEN i commit: `fix: expose scoped bound-review readiness in gate`.

## Zadatak 6: Paketni dokaz, preklapanje s #52 i predaja na pregled

**Files:** `bin/testovi.sh`; postojeći `docs/PROMJENE.md` i katalog `references/zamke.md` samo za stvarno reproducirane kvarove, uz aktualan indeks.

- [ ] Dodati nove grupe runneru, uz očuvanje svih postojećih:

```bash
pokreni "katedra-lite: review status" python3 "$KORIJEN/katedra-lite/scripts/tests/test_review_status.py"
pokreni "katedra-lite: review coverage" python3 "$KORIJEN/katedra-lite/scripts/tests/test_review_coverage.py"
pokreni "katedra-lite: bound review receipt" python3 "$KORIJEN/katedra-lite/scripts/tests/test_review_receipt.py"
pokreni "katedra-lite: bound review gate" python3 "$KORIJEN/katedra-lite/scripts/tests/test_gate_bound_review.py"
```

- [ ] Na kandidat headu izvršiti sva četiri testa s `-v`, postojeći `test_gate.py`, pa puni `bin/testovi.sh`. Broj testova i grupa preuzeti iz stvarnog izlaza, ne iz očekivanja 26/28 ili broja E-scenarija. Svaki testni modul završava s `unittest.main()` da ga runner zaista izvrši.

- [ ] Pregledati `git diff --check`; provjeriti da nema promjene frozen v1 shema, `VERSION`, fakultetskih profila, workflowa, tajni, privatnih dokumenata ni neodobrenih satelitskih motora. Ne objaviti logove iz stvarnih radova. U katalog unijeti uzrok/mehanizam, RED/GREEN dokaz i vlasnika samo nakon reprodukcije; ideje bez reprodukcije ne dobivaju oznaku potvrđenog kvara.

- [ ] Ako #52 i dalje nije spojen, u dodatnom izoliranom worktreeu provjeriti zajednički kandidat s njegovim aktualnim headom i ovim promjenama. Zajednički runner mora sadržavati njegove dvije dodane grupe i sve naše; ne prepisati ga našom kopijom. Bez guranja na #52 i bez mergea. Promjene kataloga uskladiti prema najnovijoj numeraciji, bez ručnog lažnog hasha registryja.

- [ ] Predložiti zaseban draft PR za isporuku A tek uz planom traženu provjeru. Dokumentacijski commitovi sami ne trebaju PR koji bi trošio live kvotu. Ne mijenjati postojeći workflow da zaobiđe gate; lokalni unit, CI paketni i live Claude rezultat iskazati odvojeno. Za API billing treba zasebno izričito odobrenje; ovaj plan ga ne daje.

- [ ] Sažetak provedbe mora navesti exact head, što je stvarno reproducirano prije/poslije, sve runove/exit kodove, neizvedene provjere, opseg dokaza i preostale blokatore. Bez tvrdnje „Katedra je sada semantički provjerila cijeli rad”.

## Prihvatni izlaz isporuke A

Očekivani rezultat nakon implementacije jest zaseban PR sa zadacima 1–6, sintetičkim regresijama i svježim dokazima. E01–E06 moraju imati problematične i legitimne kontrole; isporuka D još mora dokazati vizualni i privatnosni preflight. Ne spajati kod automatski.

Korisniku se nakon ovog plana predlaže izravna provedba u istoj sesiji, zadatak po zadatak. Plan se prvo pregledava; sama ranija potvrda specifikacije ne znači da su nepostojeći runtime testovi već odobreni kao prolaz.
