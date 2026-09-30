# Jothidam · ஜோதிடம்

South Indian Vedic horoscope and marriage matching in a single web page, in English and Tamil.

**Horoscope** — Lagna, Rasi, Nakshatra & pada, Tamil month, Panchangam (tithi, yoga, karana), South Indian Rasi and Navamsa charts, planetary table (exalted / debilitated / own / retro / combust), Vimshottari dasa with current bhukti, Chevvai / Rahu–Ketu / Kala Sarpa checks.

**Marriage match** — the 10 Poruthams (Dinam, Ganam, Mahendram, Stree Deergham, Yoni, Rasi, Rasi Adhipathi, Vasyam, Rajju, Vedhai), score out of 10, verdict (Rajju and Vedhai treated as critical), and dosha samyam.

**AI reading** — Google Gemini writes the interpretation in English or Tamil from the computed chart.

## How it works

- All astronomy runs in the browser (bundled [astronomy-engine](https://github.com/cosinekitty/astronomy), MIT). No server.
- Lahiri ayanamsa, whole-sign houses, Vimshottari dasa (365.25-day years). Rahu/Ketu mean node by default; true node in settings.
- Accuracy: benchmarked on 400 random charts (1900–2060) against Swiss Ephemeris (Lahiri): planets median 1–3″, worst 23″ (Moon); Lagna median 0.5″, worst 4″; zero sign, nakshatra or Lagna mismatches.
- Tamil calendar: Tamil year (60-year cycle), month and date use the sankranti-before-sunset rule; weekday, panchangam and Janma nazhigai use the local sunrise.
- Current transits: Saturn (Ezharai / Ashtama / Ardhashtama / Kandaka Sani) and Jupiter from the Moon sign.
- Traditional jathagam: a two-page A4 print in Tamil or English with manjal–kungumam side borders, Pillaiyar suzhi, Om with kuthuvilakku, the Janani Janma sloka, traditional birth prose, Rasi and Navamsa charts, Navagraha grid, planet table, dasa–bhukti and panchangam. Father's and mother's names and gothram are optional.
- Share links: the page URL holds the birth details, so a chart or match can be reopened or sent.
- Place search: Open-Meteo geocoding (free, no key). It also supplies the time zone; historical offsets (e.g. India's +06:30 war time in 1942–45) come from the browser's time-zone data. You can override latitude, longitude and UTC offset under "Coordinates & time zone".
- Gemini key: each visitor adds their own key via the gear icon. It is stored only in their browser (optional) and sent only to Google.

**Never put your API key in the code or the repository** — a GitHub Pages site is public.

## Live site

https://babubl.github.io/horoscope/ — served by GitHub Pages from the `gh-pages` branch (kept identical to `main`).

## Traditions differ

Porutham rules follow the common Tamil (Thirukanitha) practice as published by Prokerala, Vikatan, IBC Bakthi and Dheivegam: Dinam good at counts 2, 4, 6, 8, 9, 11, 13, 15, 18, 20, 24, 26; Vasyam from the Tamil girl-to-boy list; Rajju and Vedhai decisive. Traditions still differ on some points (Gana with Rakshasa, same-rasi rules, Yoni gender), and temple Vakya panchangams give slightly different positions than Thirukanitha. The rules used are marked in the code (`porutham()` inside `index.html`) so they can be adjusted.

Astrology is a traditional belief system; use it for reflection, not for medical, legal or financial decisions.
