# Jothidam · ஜோதிடம்

South Indian Vedic horoscope and marriage matching in a single web page, in English and Tamil.

**Horoscope** — Lagna, Rasi, Nakshatra & pada, Tamil month, Panchangam (tithi, yoga, karana), South Indian Rasi and Navamsa charts, planetary table (exalted / debilitated / own / retro / combust), Vimshottari dasa with current bhukti, Chevvai / Rahu–Ketu / Kala Sarpa checks.

**Marriage match** — the 10 Poruthams (Dinam, Ganam, Mahendram, Stree Deergham, Yoni, Rasi, Rasi Adhipathi, Vasyam, Rajju, Vedhai), score out of 10, verdict (Rajju and Vedhai treated as critical), and dosha samyam.

**AI reading** — Google Gemini writes the interpretation in English or Tamil from the computed chart.

## How it works

- All astronomy runs in the browser (bundled [astronomy-engine](https://github.com/cosinekitty/astronomy), MIT). No server.
- Lahiri ayanamsa, mean Rahu/Ketu, whole-sign houses, Vimshottari dasa (365.25-day years).
- Place search: Open-Meteo geocoding (free, no key). It also supplies the time zone; historical offsets (e.g. India's +06:30 war time in 1942–45) come from the browser's time-zone data. You can override latitude, longitude and UTC offset under "Coordinates & time zone".
- Gemini key: each visitor adds their own key via the gear icon. It is stored only in their browser (optional) and sent only to Google.

**Never put your API key in the code or the repository** — a GitHub Pages site is public.

## Host on GitHub Pages

1. Create a new public repository on GitHub, e.g. `jothidam`.
2. Upload `index.html` (and this README) to the repository root: *Add file → Upload files → Commit*.
3. Go to *Settings → Pages*. Under *Build and deployment*, choose *Deploy from a branch*, branch `main`, folder `/ (root)`, and save.
4. After a minute the site is live at `https://<your-username>.github.io/jothidam/`.

## Traditions differ

Porutham rules vary between families and panchangam traditions (for example, whether 5/9 Rasi is acceptable, or which same-star pairs are good). The rules used are marked in the code (`porutham()` inside `index.html`) so they can be adjusted.

Astrology is a traditional belief system; use it for reflection, not for medical, legal or financial decisions.
