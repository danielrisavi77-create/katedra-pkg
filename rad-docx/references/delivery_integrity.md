# Delivery D — posljednja DOCX isporuka

`scripts/delivery_integrity.py` nadograđuje vlasnika `rad-docx`; koristi postojeći
sigurni loader i no-overwrite/snapshot writer iz `ciljane_izmjene.py`. Nije novi
motor za pisanje rada. Ne zamjenjuje fakultetska pravila ni stručni sadržajni pregled.

## Odvojene provjere

`compare` uspoređuje **uređeni redoslijed** teksta, tablica/ćelija, matematičkih
izraza, živih polja, knjižnih oznaka, hiperlinkova, vizualnih veza i alt-opisa.
Promjena brojke, citata, oznake u grafu ili teksta unutar crteža blokira stilski
zahvat. Dijeljenje runa bez izmjene teksta prolazi; nepoznata promjena ostaje
konzervativno zaustavljena. Numeriranje i neklasificirani ugrađeni dijelovi također
su zaštićeni. Raster se uspoređuje po pikselima, ne po pretpostavci da nova slika
prikazuje istu stvar. Promijenjen raster zato traži zaseban sadržajni zahvat.

`metadata_only` dodatno ne dopušta promjene dijelova izvan metapodataka i njihovih
OPC veza. `format_only` dopušta deklarirane prezentacijske promjene, ne semantičke.
Sadržajna korekcija ide kroz već postojeći odobreni plan ciljane izmjene i ponovno
čitanje: nije dopušteno proglasiti je oblikovanjem radi dobivanja PASS-a.

Geometrija se provjerava po **sekciji**, ne prema veličini prve stranice. Mjere se
širine mreža/stupaca i slika; fiksna visina retka, duga nedjeljiva riječ/URL i
plutajući vizuali daju rizik za pregled. Širina iz XML-a nije dokaz stvarnog
preklapanja ili čitljivosti. Ne postavlja se slijepo `cantSplit` na retke više od
stranice niti header-row na svaku layout tablicu. Konačna ocjena izgleda traži render.

## Sigurno čišćenje točno imenovanih skupina

```sh
python rad-docx/scripts/delivery_integrity.py clean project/edited.docx \
  --out project/clean.docx --snapshot project/pre-clean.docx \
  --groups core application custom thumbnail --report project/privacy.json
```

Izvor ostaje netaknut; postojeći izlaz, snapshot ili izvještaj nikad se ne prepisuje.
`core`, `application`, `custom`, `thumbnail` uklanjaju i odgovarajuće OPC veze i
Content Types zapise. Promjena mora proći usporedbu sadržaja prije objave rezultata.
Komentari, praćene revizije, digitalni potpis i vezanje teksta uz DOCPROPERTY ili
content-control dataBinding traže zasebnu odluku; nikad se automatski ne prihvaćaju
ili brišu. `image_metadata` podržava samo sigurno PNG čišćenje bez orijentacijskog
EXIF-a. JPEG/EMF/SVG i metapodaci ugrađenih objekata nisu prešutno odobreni.

Nužni XML i alt-opisi nisu privatni metapodaci za brisanje. Izvještaj nabraja
pregledane skupine i ono što nije pregledano. Novi Word save može dodati nova
svojstva: pregled je vezan uz posljednje bajtove, ne uz ime datoteke.

## Render i stvarni vizualni pregled

```sh
python rad-docx/scripts/delivery_integrity.py render project/clean.docx \
  --out-dir project/render-final
```

Potreban je `soffice`, `pdfinfo` i `pdftoppm` na PATH-u. Alat radi nad kopijom u
izoliranoj privremenoj mapi i privatnim LibreOffice profilom. Nova izlazna mapa,
SHA-256 izvornog DOCX-a, PDF-a i **svake** PNG stranice te ime/verzija renderera
vežu dokaz uz konkretne datoteke. Izmjena DOCX-a za vrijeme rada je `stale`.
Nedostupni alati/PDF/stranice su `unmeasured`. Sam render nikada ne odobrava izgled.

`render_manifest_schema.json` opisuje strojni zapis. Tek nakon pregleda PNG stranica
u čitljivoj veličini zapisuje se zasebni `visual_review_schema.json`:

```json
{
  "schema_version": 1,
  "kind": "katedra_visual_review",
  "document_sha256": "<SHA-256 posljednjeg DOCX-a>",
  "render_manifest_sha256": "<SHA-256 datoteke render.json>",
  "reviewer": "<ime stvarnog pregledavatelja ili identitet asistenta>",
  "reviewed_pages": [1, 2],
  "decision": "approved",
  "notes": "<što je stvarno pregledano i ograničenja>",
  "reviewed_at": "<ISO 8601 datum i vrijeme s vremenskom zonom>"
}
```

Ovo je predložak, ne izvršivi dokaz. Broj stranica potvrđuje se iz PDF-a; slika
kontaktnog lista ne može predstavljati sve stranice. Nedostajuća stranica, pogrešna
veličina slike, neispunjeni pregled ili stari hash ne prolaze. `approved` je **izjava
imenovanog pregledavatelja**, nije neovisno autenticirana potvrda niti kriptografski
dokaz kvalitete. Sustav to izričito navodi. LibreOffice ne potvrđuje Microsoft Word.

## Završni manifest i gate

`delivery_manifest_schema.json` sadrži prije/poslije datoteku i njihove SHA-256,
`mode`, `metadata_groups`, put render manifesta, put vizualnog pregleda i obrazložena
administrativna isključenja. Putanje su relativne na projektni root iz CLI-ja
(ili mapu manifesta kad root nije zadan), bez `..`, apsolutnih putanja i symlinkova.
Isključiti se mogu samo JMBAG, datumi, potpis, životopis ili administrativni pregled,
ne sadržajna/tehnička provjera radi zelenog rezultata.

```sh
python rad-docx/scripts/delivery_integrity.py check \
  --manifest project/.katedra/delivery.json --project-root project \
  --rad project/clean.docx --out project/fresh-delivery-result.json

python katedra-lite/scripts/gate.py predaja --project-root project \
  --rad clean.docx --delivery-manifest .katedra/delivery.json
```

`gate.py` uključuje D samo izričitim argumentom (audit ili predaja). Rezultat ne može
pripadati nekom drugom DOCX-u od dokumenta gatea. CLI izlaz je 0 samo za izmjeren
opseg PASS, 1 za blokadu, 2 za neizmjeren/zastario/odbijen ulaz. `render` izlaz 0
znači da je proizveden render, **ne** da je predaja odobrena. Cjelovitost cijelog
rukopisa, semantička istinitost i neprovjereni slojevi metapodataka nikad se ne
proglašavaju potvrđenima: `whole_document` ostaje `false`.

Regresije: `scripts/tests/test_delivery_integrity.py` i
`katedra-lite/scripts/tests/test_delivery_integration.py`. Sintetički manifesti u
unit testovima zamjenjuju samo granicu vanjskog pdfinfo mjerenja; nisu vizualni QA.
Stvarni LibreOffice render provjerava se odvojeno. Nije uvedena univerzalna automatska
korekcija svih preklapanja; D ih ne smije sakriti lažnim automatskim odobrenjem.
