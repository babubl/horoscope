# Publishing the Android app

The app is the website packaged as a Trusted Web Activity (TWA): a real Play Store app that opens the site full-screen, works offline and shows no ads. It opens the site with `?source=twa`, which the site uses to hide ads and unlock printing.

## 1. Domain (needed first)

The app must be linked to a site at the **root** of a domain (for `/.well-known/assetlinks.json`), so the custom domain comes before the app.

After buying the domain, add these DNS records at the registrar:

| Type | Host | Value |
|---|---|---|
| A | @ | 185.199.108.153 |
| A | @ | 185.199.109.153 |
| A | @ | 185.199.110.153 |
| A | @ | 185.199.111.153 |
| CNAME | www | babubl.github.io |

Then Claude adds the `CNAME` file to the repo. In GitHub → repo **Settings → Pages**, tick **Enforce HTTPS** once it becomes available (can take up to an hour).

## 2. Build the app package with PWABuilder (about 10 minutes, free)

1. Open https://www.pwabuilder.com and enter `https://subajathagam.in/`.
2. Choose **Package for stores → Android → Generate package**, and set:

| Option | Value |
|---|---|
| Package ID | `in.subajathagam.app` (never change this after publishing) |
| App name | `Suba Jathagam – Kundli & Match` |
| Launcher name | `Suba Jathagam` |
| App version / code | `1.0.0` / `1` |
| Host | `subajathagam.in` |
| Start URL | `/?source=twa` |
| Theme colour | `#6E1216` |
| Background colour | `#F7EFE0` |
| Navigation bar colour | `#6E1216` |
| Display mode | Standalone |
| Orientation | Portrait |
| Notifications | Off |
| Signing key | **Create new** — fill in your name and "Chennai, IN" |

3. Download the zip. It contains:
   - `app-release-bundle.aab` — upload this to Play Console
   - `assetlinks.json` — send this to Claude to publish on the site
   - `signing.keystore` and `signing-key-info.txt` — **back these up somewhere safe** (Google Drive and a USB). Without them you can never update the app.

## 3. Link the app to the site

The site must publish `/.well-known/assetlinks.json` containing two SHA-256 fingerprints:

- the one from PWABuilder's `assetlinks.json` (your upload key), and
- the **app signing key** from Play Console → your app → **Setup → App integrity → App signing**.

Send both to Claude; it goes into the repo. If this step is missing, the app shows a browser address bar at the top.

## 4. Play Console

1. Create the developer account at https://play.google.com/console (US$25 one-time; identity verification takes a few days).
2. **Create app** → name, Tamil default language, App, **Paid**.
3. Fill **Store listing** and **App content** from `LISTING.md` and the images in this folder.
4. **Pricing:** ₹10. A merchant (payments) profile is needed for paid apps.
5. **Testing → Closed testing:** upload the `.aab`, add at least **12 testers** (their Gmail addresses), share the opt-in link, and keep all 12 opted in for **14 days**. Paid apps are free for testers on the list.
6. After 14 days: **Apply for production**, answer the short questionnaire, and roll out.

## After launch

Tell Claude the Play Store link. Setting `playStoreUrl` in `src/template.html` makes the website show "Get the app · ₹10" and turns the jathagam print into an app-only feature (the website keeps a watermarked preview).
