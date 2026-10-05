# Suba Jathagam · சுப ஜாதகம்

Vedic horoscope, marriage matching and panchangam in a single web page — in **English, Tamil, Malayalam, Telugu, Kannada and Hindi**, each with its own tradition:

| Language page | Tradition default | Calendar shown | Chart | Matching first | Mars dosha houses | Print design |
|---|---|---|---|---|---|---|
| `/ta/` தமிழ் | Tamil | Tamil solar (60-year cycle) | South | 10 Porutham | 2, 4, 7, 8, 12 | Manjal–kungumam, Pillaiyar suzhi, kuthuvilakku |
| `/ml/` മലയാളം | Kerala | Kollavarsham (Malayalam era) | South | 10 Porutham + Papasamyam | 2, 4, 7, 8, 12 | Kasavu cream and gold, nilavilakku |
| `/te/` తెలుగు | Telugu | Amanta lunar, samvatsara, Shaka | South | 36 Guna | 2, 4, 7, 8, 12 | Pasupu–kunkuma, mango-leaf thoranam, kalasham |
| `/kn/` ಕನ್ನಡ | Kannada | Amanta lunar, samvatsara, Shaka | South | 36 Guna | 2, 4, 7, 8, 12 | Kumkum red, gold and green, kalasha |
| `/hi/` हिन्दी | North Indian | Purnimanta lunar, Vikram Samvat | North (diamond) | 36 Guna | 1, 4, 7, 8, 12 | Saffron, swastik, kalash |
| `/` English | Tamil (changeable) | follows tradition | follows tradition | follows tradition | follows tradition | follows tradition |

The tradition and chart style can be changed in Settings (gear icon) independently of the language.

**Horoscope** — Lagna, Rasi, Nakshatra & pada, Tamil month, Panchangam (tithi, yoga, karana), South Indian Rasi and Navamsa charts, planetary table (exalted / debilitated / own / retro / combust), Vimshottari dasa with current bhukti, Chevvai / Rahu–Ketu / Kala Sarpa checks.

**Marriage match** — the 10 Poruthams (Dinam, Ganam, Mahendram, Stree Deergham, Yoni, Rasi, Rasi Adhipathi, Vasyam, Rajju, Vedhai), score out of 10, verdict (Rajju and Vedhai treated as critical), and dosha samyam.

**36 Guna (Ashtakoota)** — Varna, Vashya, Tara, Yoni, Graha Maitri, Gana, Bhakoot and Nadi with Nadi/Bhakoot dosha and their common cancellations. Kerala view adds Papasamyam.

**AI reading** — Google Gemini writes the interpretation in the page's language, as an astrologer of the chosen tradition.

## How it works

- All astronomy runs in the browser (bundled [astronomy-engine](https://github.com/cosinekitty/astronomy), MIT). No server.
- Lahiri ayanamsa, whole-sign houses, Vimshottari dasa (365.25-day years). Rahu/Ketu mean node by default; true node in settings.
- Accuracy: benchmarked on 400 random charts (1900–2060) against Swiss Ephemeris (Lahiri): planets median 1–3″, worst 23″ (Moon); Lagna median 0.5″, worst 4″; zero sign, nakshatra or Lagna mismatches.
- Tamil calendar: Tamil year (60-year cycle), month and date use the sankranti-before-sunset rule; weekday, panchangam and Janma nazhigai use the local sunrise.
- Current transits: Saturn (Ezharai / Ashtama / Ardhashtama / Kandaka Sani) and Jupiter from the Moon sign.
- Traditional jathagam: a two-page A4 print in Tamil or English with manjal–kungumam side borders, Pillaiyar suzhi, Om with kuthuvilakku, the Janani Janma sloka, traditional birth prose, Rasi and Navamsa charts, Navagraha grid, planet table, dasa–bhukti and panchangam. Father's and mother's names and gothram are optional.
- Daily panchangam: tithi, nakshatra and yoga with end times, karana, sunrise/sunset, Rahu kalam, Yamagandam, Kuligai and Abhijit for any town and date; a "Today" strip on the home page.
- Place search: 5,400 towns built in (every Tamil Nadu town over 15,000 people, all of India, and diaspora cities) with Tamil names and common spellings (Trichy, Kovai, Tuticorin…), plus online search for villages. A typed town is used automatically even if not picked from the list.
- Print: traditional two-page jathagam and a one-page Thirumana Porutham report, both A4.
- Feedback form: rating, topic and message. Set `web3formsKey` in CONFIG to receive it by email; without it, feedback appears as events in GoatCounter.
- Share links: the page URL holds the birth details, so a chart or match can be reopened or sent.
- Place search: Open-Meteo geocoding (free, no key). It also supplies the time zone; historical offsets (e.g. India's +06:30 war time in 1942–45) come from the browser's time-zone data. You can override latitude, longitude and UTC offset under "Coordinates & time zone".
- Gemini key: each visitor adds their own key via the gear icon. It is stored only in their browser (optional) and sent only to Google.

**Never put your API key in the code or the repository** — a GitHub Pages site is public.

## Live site

https://subajathagam.in — served by GitHub Pages from the `gh-pages` branch (kept identical to `main`).

## Repository layout

| Path | What it is |
|---|---|
| `index.html`, `ta/ ml/ te/ kn/ hi/index.html` | The app, one page per language (built — do not edit by hand) |
| `src/template.html`, `src/engine.js` | App source: UI and the astronomy / porutham / guna engine |
| `src/i18n_src.py` → `src/i18n.js` | Malayalam, Telugu, Kannada and Hindi UI text (Sanskrit lists transliterated): `python3 src/i18n_src.py` |
| `src/culture.js` | Traditions, print wording per language, print symbols, state and country names |
| `src/seo.py` | Search titles, descriptions and the visible FAQ for each language page |
| `src/vendor/` | astronomy-engine 2.1.19 (MIT) |
| `src/build.py` | Builds all language pages, manifests and `sitemap.xml`: `python3 src/build.py` |
| `src/pages.py` | Builds `guide.html`, `about.html`, `privacy.html`, `terms.html`: `python3 src/pages.py` |
| `manifest.webmanifest`, `sw.js`, `icons/` | Installable app and offline support |
| `store/` | Play Store listing text, screenshots, feature graphic and Android publishing steps |

## Switching on ads and the app

Edit `CONFIG` near the top of the script in `src/template.html`, then run `python3 src/build.py`:

- `adsenseClient` and `adSlotBottom` — AdSense publisher and slot ids. Ads appear on the website only, never in the app or on the printed jathagam. Also add `ads.txt` at the site root as AdSense instructs.
- `playStoreUrl` — once the app is live. The website then shows "Get the app · ₹10", and printing the traditional jathagam becomes app-only (the website keeps a watermarked preview).

When changing any cached file, bump `VERSION` in `sw.js` so installed copies update.

## Traditions differ

Porutham rules follow the common Tamil (Thirukanitha) practice as published by Prokerala, Vikatan, IBC Bakthi and Dheivegam: Dinam good at counts 2, 4, 6, 8, 9, 11, 13, 15, 18, 20, 24, 26; Vasyam from the Tamil girl-to-boy list; Rajju and Vedhai decisive. Traditions still differ on some points (Gana with Rakshasa, same-rasi rules, Yoni gender), and temple Vakya panchangams give slightly different positions than Thirukanitha. The rules used are marked in the code (`porutham()` inside `index.html`) so they can be adjusted.

Astrology is a traditional belief system; use it for reflection, not for medical, legal or financial decisions.
