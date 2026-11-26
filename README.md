# Lebensfarben · Vorschau

Entwurf einer neuen Website für Kristin Damaschke, Lebensfarben (Wismar). **Nur Vorschau:** jede Seite hat `noindex, nofollow`, `robots.txt` sperrt alles. Die echte Seite www.lebensfarben.net bleibt unverändert.

- Vorschau: https://cosmo-hl.github.io/lebensfarben-vorschau/
- Analyse, Designkonzept und Umzugsplan: [ANALYSE.md](ANALYSE.md) (auch als Seite `/konzept/`)

## Aufbau

- `build.py` erzeugt alle Seiten nach `dist/` (Python 3, `pip install markdown pillow`), inkl. JSON-LD (Person, ProfessionalService, FAQPage), `llms.txt`, `robots.txt` und einer Prüfung (noindex, eine H1, Bilder vorhanden).
- `scripts/images.py` holt Kristins Bilder von lebensfarben.net und erzeugt 800/1600-px-JPEGs in `site/img/`. Lokal ohne Netz: `python3 scripts/images.py --placeholder`.
- Porträts `kristin-*.jpg`: Fotos von Alexander Tiffert, zugeschnitten auf 4:5, ohne Metadaten.
- `.github/workflows/deploy.yml`: holt fehlende Bilder, baut und veröffentlicht nach `gh-pages` (GitHub Pages, Quelle `gh-pages` / root).
- Schriften selbst gehostet (Cormorant Garamond, Inter; SIL OFL), keine Cookies, kein Tracking, keine externen Anfragen.

## Seiten

`/` · `/wofuer/` · `/somatic-experiencing/` · `/kunsttherapie/` · `/angebot/` · `/ueber-mich/` · `/kunst/` · `/fragen/` · `/kontakt/` · `/impressum/` (Entwurf) · `/datenschutz/` (Entwurf) · `/konzept/`

Die Adressen entsprechen denen der heutigen Seite, damit ein späterer Umzug keine Rankings kostet.
