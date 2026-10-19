"""Temple guide (Tamil Nadu: Navagraha sthalams and parigaram temples) and the Parigaram page, in English and Tamil.
Called from src/build.py after the other knowledge pages."""
import html
import json
from urllib.parse import quote

import kb
import nakshatra as NK
from parigaram_data import GRAHAS, SECTIONS
from temples_data import TEMPLES
import images_data as IMG

LANGS = ['en', 'ta']
BY = {t['slug']: t for t in TEMPLES}
ORDER = ['sun', 'moon', 'mars', 'mercury', 'jupiter', 'venus', 'saturn', 'rahu', 'ketu']

T = {
    'en': dict(
        menuT='Temple guide', menuP='Parigaram',
        lampT='Light a lamp', lampP='Tap the lamp to offer a light at this temple for your family.', lampDone='You lit a lamp here on {d}. 🙏',
        photo='Photo', painting='Painting', credit='{a}, {lic}, via Wikimedia Commons', mapT='Map of the nine Navagraha temples', mapNote='Schematic map, not to scale. Tap a temple to open its page.',
        day1='Day 1', day2='Day 2', hoursNote='Based on published timings; may change on festival days.',
        idxTitle='Navagraha Temples & Parigaram Temples of Tamil Nadu — Timings, How to Reach | Suba Jathagam',
        idxH1='Temple guide: Navagraha and parigaram temples of Tamil Nadu',
        idxLead='The nine Navagraha temples around Kumbakonam, the Thanjavur Big Temple and the temples families visit for marriage, children, long life and ancestral rites — with the deity, history, the parigaram done there, darshan timings and how to reach.',
        nava='The nine Navagraha temples', navaLead='All nine lie within about 60 km of Kumbakonam, in the Kaveri delta. Most of them are ancient Shiva temples where the planet is worshipped in its own shrine; Suryanar Kovil is the only one built for the Sun himself.',
        other='Other temples for parigaram and darshan',
        cTemple='Temple', cGraha='Graha', cPlace='Place', cKm='From Kumbakonam', cFor='Visited for',
        tour='Planning the Navagraha tour', tourLead='Stay in Kumbakonam. With a car, all nine temples can be covered in one long day or comfortably in two days.',
        tourDays=[('Day 1 — south and west of Kumbakonam', ['suryanar-kovil', 'kanjanur', 'thirunageswaram', 'alangudi', 'thingalur']),
                  ('Day 2 — towards the coast', ['vaitheeswaran-koil', 'thiruvenkadu', 'keezhaperumpallam', 'thirunallar'])],
        tourNote='Tradition prefers starting with Suryanar Kovil (the Sun) and ending at Thirunallar (Saturn). Temples close at midday, roughly 12:00 or 12:30 to 4:00 pm, so plan the morning and evening rounds around that.',
        verify='Timings change on festival days and during eclipses. Please confirm with the temple or the Tamil Nadu HR&CE department (hrce.tn.gov.in) before you travel.',
        tTitle='{n} — {k} | Timings, History, Parigaram | Suba Jathagam',
        fGraha='Navagraha', fDeity='Main deity', fConsort='Goddess', fPlace='Place', fFor='Known for', fBest='Important days', fTime='Darshan timings', fMap='Map',
        hHistory='History and architecture', hLegend='Sthala varalaru — the temple’s story', hFacts='Did you know?', hPadigam='Sung by the saints', hPari='Parigaram done here', hReach='How to reach', hTips='Before you go', hSrc='Sources', hNear='Other temples in this guide',
        openMap='Open in Google Maps', legendNote='As told in temple tradition.',
        pariLink='Remedies for {g} →',
        pTitle='Parigaram — Traditional Remedies for Navagraha, Chevvai, Rahu–Ketu & Sani Dosham | Suba Jathagam',
        pH1='Parigaram: traditional remedies',
        pLead='What Tamil tradition suggests for each of the nine planets and for Chevvai dosham, Rahu–Ketu dosham, Ezharai Sani, delays in marriage, children, long life and ancestral rites — with the temple for each.',
        pWarn='Parigaram is a matter of faith. It is not a substitute for medical, legal or financial help. Simple prayer, a lamp and charity are the heart of every remedy; be careful of anyone who demands large payments or frightens you with a dosha.',
        pTable='The nine grahas at a glance', cDay='Day', cColour='Colour', cGrain='Grain (dhanyam)', cGem='Gem', cSamith='Samith', cDeity='Worship', cMantra='Mantra', cTempleCol='Temple',
        pTableNote='These associations are as commonly listed in Jyotisha and Tamil temple tradition; some texts and families differ.',
        pFind='Check your chart first', pFindLead='Our free horoscope shows whether Chevvai or Rahu–Ketu dosham is present or cancelled, your current Saturn phase and your dasa–bhukti.',
        pCta='Make my horoscope →', templesFor='Temple'),
    'ta': dict(
        menuT='கோயில் வழிகாட்டி', menuP='பரிகாரம்',
        lampT='விளக்கேற்றுங்கள்', lampP='உங்கள் குடும்பத்துக்காக இந்தக் கோயிலில் ஒரு விளக்கேற்ற, விளக்கைத் தொடுங்கள்.', lampDone='{d} அன்று இங்கு விளக்கேற்றினீர்கள். 🙏',
        photo='படம்', painting='ஓவியம்', credit='{a}, {lic}, Wikimedia Commons வழியாக', mapT='ஒன்பது நவக்கிரகக் கோயில்களின் வரைபடம்', mapNote='அளவுக்கு ஏற்ப வரையப்படாத மாதிரி வரைபடம். கோயிலைத் தொட்டால் அதன் பக்கம் திறக்கும்.',
        day1='முதல் நாள்', day2='இரண்டாம் நாள்', hoursNote='வெளியிடப்பட்ட நேரங்களின்படி; திருவிழா நாட்களில் மாறலாம்.',
        idxTitle='தமிழ்நாட்டின் நவக்கிரகக் கோயில்கள், பரிகாரக் கோயில்கள் — நேரம், செல்லும் வழி | சுப ஜாதகம்',
        idxH1='கோயில் வழிகாட்டி: நவக்கிரக மற்றும் பரிகாரக் கோயில்கள்',
        idxLead='கும்பகோணத்தைச் சுற்றியுள்ள ஒன்பது நவக்கிரகக் கோயில்கள், தஞ்சைப் பெரிய கோயில், திருமணம், குழந்தைப் பேறு, நீண்ட ஆயுள், முன்னோர் கடனுக்காகக் குடும்பங்கள் செல்லும் கோயில்கள் — மூலவர், வரலாறு, அங்கு செய்யப்படும் பரிகாரம், தரிசன நேரம், செல்லும் வழி.',
        nava='ஒன்பது நவக்கிரகக் கோயில்கள்', navaLead='ஒன்பதும் காவிரி டெல்டாவில், கும்பகோணத்திலிருந்து சுமார் 60 கி.மீ.க்குள் உள்ளன. பெரும்பாலானவை பழமையான சிவன் கோயில்கள்; அங்கு கிரகத்துக்குத் தனிச் சன்னதி உண்டு. சூரியனுக்கென்றே கட்டப்பட்ட கோயில் சூரியனார் கோயில் மட்டுமே.',
        other='பரிகாரம் மற்றும் தரிசனத்துக்கான பிற கோயில்கள்',
        cTemple='கோயில்', cGraha='கிரகம்', cPlace='ஊர்', cKm='கும்பகோணத்திலிருந்து', cFor='எதற்காக',
        tour='நவக்கிரக யாத்திரைத் திட்டம்', tourLead='கும்பகோணத்தில் தங்குங்கள். காரில் ஒன்பது கோயில்களையும் ஒரு நீண்ட நாளில் அல்லது வசதியாக இரண்டு நாட்களில் தரிசிக்கலாம்.',
        tourDays=[('முதல் நாள் — கும்பகோணத்தின் தெற்கு, மேற்கு', ['suryanar-kovil', 'kanjanur', 'thirunageswaram', 'alangudi', 'thingalur']),
                  ('இரண்டாம் நாள் — கடற்கரை நோக்கி', ['vaitheeswaran-koil', 'thiruvenkadu', 'keezhaperumpallam', 'thirunallar'])],
        tourNote='சூரியனார் கோயிலில் தொடங்கி திருநள்ளாற்றில் (சனி) முடிப்பது மரபு. கோயில்கள் மதியம் சுமார் 12:00 / 12:30 முதல் மாலை 4:00 வரை மூடப்படும்; காலை, மாலைச் சுற்றுகளை அதற்கேற்பத் திட்டமிடுங்கள்.',
        verify='பண்டிகை, கிரகண நாட்களில் நேரம் மாறும். பயணத்துக்கு முன் கோயிலிலோ தமிழ்நாடு இந்து சமய அறநிலையத் துறை (hrce.tn.gov.in) இணையதளத்திலோ உறுதி செய்துகொள்ளுங்கள்.',
        tTitle='{n} — {k} | நேரம், வரலாறு, பரிகாரம் | சுப ஜாதகம்',
        fGraha='நவக்கிரகம்', fDeity='மூலவர்', fConsort='அம்பாள்', fPlace='ஊர்', fFor='சிறப்பு', fBest='முக்கிய நாட்கள்', fTime='தரிசன நேரம்', fMap='வரைபடம்',
        hHistory='வரலாறும் கட்டடக்கலையும்', hLegend='தல வரலாறு', hFacts='உங்களுக்குத் தெரியுமா?', hPadigam='அருளாளர்கள் பாடிய தலம்', hPari='இங்கு செய்யப்படும் பரிகாரம்', hReach='செல்லும் வழி', hTips='செல்லும் முன்', hSrc='ஆதாரங்கள்', hNear='இந்த வழிகாட்டியில் உள்ள பிற கோயில்கள்',
        openMap='Google Maps-ல் திறக்க', legendNote='கோயில் ஐதீகப்படி.',
        pariLink='{g} பரிகாரங்கள் →',
        pTitle='பரிகாரம் — நவக்கிரக, செவ்வாய், ராகு–கேது, சனி தோஷப் பரிகாரங்கள் | சுப ஜாதகம்',
        pH1='பரிகாரம்: மரபு வழிப் பரிகாரங்கள்',
        pLead='ஒன்பது கிரகங்களுக்கும், செவ்வாய் தோஷம், ராகு–கேது தோஷம், ஏழரைச் சனி, திருமணத் தடை, குழந்தைப் பேறு, நீண்ட ஆயுள், முன்னோர் கடன் ஆகியவற்றுக்கும் தமிழ் மரபு சொல்லும் பரிகாரங்கள் — ஒவ்வொன்றுக்குமான கோயிலுடன்.',
        pWarn='பரிகாரம் நம்பிக்கை சார்ந்தது. அது மருத்துவ, சட்ட, நிதி உதவிக்கு மாற்று அல்ல. எளிய வழிபாடு, ஒரு விளக்கு, தானம் — இவையே எல்லாப் பரிகாரங்களின் மையம். பெரும் தொகை கேட்பவர்களிடமும், தோஷத்தைச் சொல்லிப் பயமுறுத்துபவர்களிடமும் எச்சரிக்கையாக இருங்கள்.',
        pTable='ஒன்பது கிரகங்கள் — ஒரே பார்வையில்', cDay='கிழமை', cColour='நிறம்', cGrain='தானியம்', cGem='ரத்தினம்', cSamith='சமித்து', cDeity='வழிபாடு', cMantra='மந்திரம்', cTempleCol='கோயில்',
        pTableNote='இவை ஜோதிட, தமிழ்க் கோயில் மரபில் பொதுவாகச் சொல்லப்படுபவை; சில நூல்களிலும் குடும்பங்களிலும் வேறுபடலாம்.',
        pFind='முதலில் உங்கள் ஜாதகத்தைப் பாருங்கள்', pFindLead='செவ்வாய், ராகு–கேது தோஷம் உள்ளதா அல்லது நிவர்த்தி ஆனதா, தற்போதைய சனி நிலை, தசா–புக்தி ஆகியவற்றை எங்கள் இலவச ஜாதகம் காட்டும்.',
        pCta='என் ஜாதகம் →', templesFor='கோயில்'),
}


def esc(x):
    return html.escape(str(x), quote=True)


def base(l):
    return '/' if l == 'en' else f'/{l}/'


def alts(rel):
    return [(x, base(x) + rel) for x in LANGS]


def tl(slug, l):
    t = BY.get(slug)
    if not t:
        raise KeyError(f'temple {slug} missing from temples_data.py')
    return f'<a href="{base(l)}temples/{slug}.html">{esc(t[l]["name"])}</a>'


def graha(key):
    return next(g for g in GRAHAS if g['key'] == key)


def nav(l):
    D = T[l]
    return f'<p class="chips big"><a href="{base(l)}temples/">{esc(D["menuT"])}</a><a href="{base(l)}parigaram/">{esc(D["menuP"])}</a></p>'


def write(l, title, desc, rel, body, crumbs, ads):
    return kb.page(l, title, desc, base(l) + rel, alts(rel), body + nav(l), crumbs, ads)


def ul(items):
    return '<ul class="tl">' + ''.join(f'<li>{x}</li>' for x in items) + '</ul>'


def paras(text):
    return ''.join(f'<p>{esc(p)}</p>' for p in text.split('\n\n') if p.strip())


DEITY_FOR = {'suryanar-kovil': 'surya', 'srirangam': 'vishnu', 'madurai-meenakshi': 'meenakshi', 'vaitheeswaran-koil': 'murugan'}
DIYA = ('<svg viewBox="0 0 120 120" width="96" height="96" aria-hidden="true">'
        '<g class="flame"><path d="M60 18c9 14 13 23 13 31a13 13 0 0 1-26 0c0-8 4-17 13-31z" fill="url(#fg)"/><path d="M60 34c4 7 6 11 6 15a6 6 0 0 1-12 0c0-4 2-8 6-15z" fill="#fff6c9"/></g>'
        '<defs><radialGradient id="fg" cx="50%" cy="70%" r="60%"><stop offset="0" stop-color="#fff3b0"/><stop offset=".55" stop-color="#ffb627"/><stop offset="1" stop-color="#e2531b"/></radialGradient>'
        '<linearGradient id="bg" x1="0" x2="0" y1="0" y2="1"><stop offset="0" stop-color="#f0c35a"/><stop offset="1" stop-color="#9b5b12"/></linearGradient></defs>'
        '<path d="M20 70h80c-2 18-18 30-40 30S22 88 20 70z" fill="url(#bg)" stroke="#6e3b0a" stroke-width="2"/>'
        '<path d="M60 70c0-4 2-7 4-8" stroke="#3a1f08" stroke-width="3" fill="none"/>'
        '<path d="M14 70h92" stroke="#6e3b0a" stroke-width="4" stroke-linecap="round"/>'
        '<path d="M44 100h32l6 10H38z" fill="url(#bg)" stroke="#6e3b0a" stroke-width="2"/></svg>')


def credit(D, im, kind):
    return f'{esc(D[kind])}: <a href="{IMG.page(im["file"])}" target="_blank" rel="noopener">{esc(D["credit"].format(a=im["author"], lic=im["license"]))}</a>'


def hero(D, slug, alt):
    im = IMG.TEMPLE.get(slug)
    if not im:
        return ''
    return (f'<figure class="hero"><img src="{IMG.url(im["file"], 1280)}" srcset="{IMG.url(im["file"], 640)} 640w, {IMG.url(im["file"], 1280)} 1280w" '
            f'sizes="(max-width: 860px) 100vw, 860px" alt="{esc(alt)}" width="1280" height="720" fetchpriority="high"{f' style="object-position:{im["pos"]}"' if im.get('pos') else ''}><figcaption>{credit(D, im, "photo")}</figcaption></figure>')


def deity_img(D, key, alt):
    im = IMG.DEITY.get(key)
    if not im:
        return ''
    return f'<figure class="deity"><img src="{IMG.url(im["file"], 480)}" alt="{esc(alt)}" loading="lazy" width="240" height="300"><figcaption>{credit(D, im, "painting")}</figcaption></figure>'


def delta_map(l, D, nava):
    """Schematic SVG of the Kaveri-delta Navagraha temples placed by latitude/longitude, with the two-day route."""
    W, H = 640, 420
    lon0, lon1, lat0, lat1 = 79.05, 79.95, 10.78, 11.27
    X = lambda lon: 30 + (lon - lon0) / (lon1 - lon0) * (W - 60)
    Y = lambda lat: 20 + (lat1 - lat) / (lat1 - lat0) * (H - 40)
    kx, ky = X(79.3788), Y(10.9617)  # Kumbakonam
    pts = {t['slug']: (X(t['lon']), Y(t['lat'])) for t in nava}
    out = [f'<svg class="dmap" viewBox="0 0 {W} {H}" role="img" aria-label="{esc(D["mapT"])}">',
           f'<rect x="0" y="0" width="{W}" height="{H}" rx="16" class="land"/>',
           f'<path d="M{X(79.86):.0f} 0 C{X(79.84):.0f} 120 {X(79.87):.0f} 260 {X(79.85):.0f} {H} L{W} {H} L{W} 0Z" class="sea"/>',
           f'<text x="{X(79.9):.0f}" y="{H/2:.0f}" class="seal" transform="rotate(90 {X(79.9):.0f} {H/2:.0f})">Bay of Bengal</text>',
           f'<path d="M0 {Y(10.83):.0f} C {X(79.2):.0f} {Y(10.86):.0f} {X(79.4):.0f} {Y(10.94):.0f} {X(79.6):.0f} {Y(11.0):.0f} S {X(79.8):.0f} {Y(11.12):.0f} {X(79.86):.0f} {Y(11.14):.0f}" class="river"/>']
    for k, cls in ((0, 'r1'), (1, 'r2')):
        seq = [(kx, ky)] + [pts[x] for x in D['tourDays'][k][1] if x in pts]
        out.append('<polyline class="route ' + cls + '" points="' + ' '.join(f'{a:.0f},{b:.0f}' for a, b in seq) + '"/>')
    out.append(f'<g class="town"><circle cx="{kx:.0f}" cy="{ky:.0f}" r="7"/><text x="{kx - 10:.0f}" y="{ky + 22:.0f}" text-anchor="end">{"Kumbakonam" if l == "en" else "கும்பகோணம்"}</text></g>')
    for t in nava:
        x, y = pts[t['slug']]
        g = graha(t['graha'])
        name = g[l]['name'].split(' (')[0]
        anchor = 'end' if x > W - 170 else 'start'
        dx = -12 if anchor == 'end' else 12
        out.append(f'<a href="{base(l)}temples/{t["slug"]}.html"><g class="pin"><circle cx="{x:.0f}" cy="{y:.0f}" r="10"/><text x="{x + dx:.0f}" y="{y + 5:.0f}" text-anchor="{anchor}">{esc(name)}</text></g></a>')
    out.append(f'<g class="legend"><line x1="40" y1="{H - 30}" x2="70" y2="{H - 30}" class="route r1"/><text x="76" y="{H - 25}">{esc(D["day1"])}</text>'
               f'<line x1="170" y1="{H - 30}" x2="200" y2="{H - 30}" class="route r2"/><text x="206" y="{H - 25}">{esc(D["day2"])}</text></g></svg>')
    return ''.join(out)



def facts_html(D, x):
    f = x.get('facts')
    if not f:
        return ''
    return f'<h2 class="orn">{esc(D["hFacts"])}</h2><ul class="dyk">' + ''.join(f'<li>{esc(i)}</li>' for i in f) + '</ul>'


def padigam(D, t, l):
    p = t.get('padigam')
    if not p:
        return ''
    line = f'<p class="olai-l" lang="ta">{esc(p["line"])}</p>' if p.get('line') else ''
    return f'<figure class="olai">{line}<figcaption>— {esc(p[l])}</figcaption></figure>'

def generate(I, ads):
    urls = []
    nava = [t for k in ORDER for t in TEMPLES if t.get('graha') == k]
    others = [t for t in TEMPLES if not t.get('graha')]
    for l in LANGS:
        D = T[l]
        home = (NK.S[l]['home'], base(l))
        # ---------------------------------------------------------------- index
        def card(t, rows_):
            return f'<div class="gcard"><h3>{tl(t["slug"], l)}</h3><dl>' + ''.join(f'<dt>{esc(a)}</dt><dd>{esc(v)}</dd>' for a, v in rows_) + '</dl></div>'
        rows = ''.join(card(t, [(D['cGraha'], graha(t['graha'])[l]['name']), (D['cPlace'], t[l]['place']), (D['cKm'], t['km'] + (' km' if l == 'en' else ' கி.மீ.'))]) for t in nava)
        orows = ''.join(card(t, [(D['cFor'], t[l]['known']), (D['cPlace'], t[l]['place'])]) for t in others)
        days = ''.join(f'<h3>{esc(h)}</h3><ol class="tl">' + ''.join(f'<li>{tl(s, l)} — {esc(graha(BY[s]["graha"])[l]["name"])}</li>' for s in ss) + '</ol>' for h, ss in D['tourDays'])
        body = f'''<div class="thoranam" aria-hidden="true"></div>{hero(D, 'thanjavur-big-temple', BY['thanjavur-big-temple'][l]['name'])}<h1>{esc(D['idxH1'])}</h1>
<p class="lead">{esc(D['idxLead'])}</p>
<h2>{esc(D['nava'])}</h2>
<p>{esc(D['navaLead'])}</p>
<div class="ggrid">{rows}</div>
<!--AD-->
<h2>{esc(D['mapT'])}</h2>{delta_map(l, D, nava)}<p class="note">{esc(D['mapNote'])}</p>
<h2>{esc(D['tour'])}</h2>
<p>{esc(D['tourLead'])}</p>
{days}
<p class="note">{esc(D['tourNote'])}</p>
<h2>{esc(D['other'])}</h2>
<div class="ggrid">{orows}</div>
<p class="note">{esc(D['verify'])}</p>
<p><a class="btn big" href="{base(l)}parigaram/">{esc(D['menuP'])} →</a></p>'''
        urls.append(write(l, D['idxTitle'], D['idxLead'][:300], 'temples/', body, [home, (D['menuT'], None)], ads))

        # ---------------------------------------------------------------- one page per temple
        for t in TEMPLES:
            x = t[l]
            g = graha(t['graha']) if t.get('graha') else None
            known = g[l]['name'] if g else x['known']
            facts = []
            if g:
                facts.append((D['fGraha'], esc(g[l]['name'])))
            else:
                facts.append((D['fFor'], esc(x['known'])))
            facts += [(D['fDeity'], esc(x['deity']))]
            if x.get('consort'):
                facts.append((D['fConsort'], esc(x['consort'])))
            facts += [(D['fPlace'], esc(x['place'])), (D['fBest'], esc(x['best'])), (D['fTime'], esc(x['timings'])),
                      (D['fMap'], f'<a href="https://www.google.com/maps/search/?api=1&amp;query={quote(t.get("maps") or t["en"]["name"] + " " + t["en"]["place"])}" target="_blank" rel="noopener">{esc(D["openMap"])}</a>')]
            ftable = ''.join(f'<tr><th>{esc(a)}</th><td>{b}</td></tr>' for a, b in facts)
            pari_link = ''
            sec_ids = [s['id'] for s in SECTIONS if t['slug'] in s['temples']]
            if g or sec_ids:
                anchor = f'#g-{g["key"]}' if g else f'#{sec_ids[0]}'
                label = g[l]['name'] if g else next(s for s in SECTIONS if s['id'] == sec_ids[0])[l]['t']
                pari_link = f'<p><a class="btn big" href="{base(l)}parigaram/{anchor}">{esc(D["pariLink"].format(g=label))}</a></p>'
            near = ''.join(f'<a href="{base(l)}temples/{o["slug"]}.html">{esc(o[l]["name"])}</a>' for o in TEMPLES if o is not t)
            src = ''.join(f'<li><a href="{esc(u)}" rel="nofollow noopener" target="_blank">{esc(u.split("//")[-1].split("/")[0])}</a></li>' for u in t['sources'])
            dk = DEITY_FOR.get(t['slug'], 'shiva')
            hours = f'<p class="opennow" data-hours="{esc(json.dumps(t["hours"]))}" hidden></p>' if t.get('hours') else ''
            body = f'''<div class="thoranam" aria-hidden="true"></div>{hero(D, t['slug'], x['name'])}<h1>{esc(x['name'])}</h1>
{hours}
<div class="introw">{deity_img(D, dk, x['deity'])}<p class="lead">{esc(x['intro'])}</p></div>
<div class="tw wrapt"><table class="facts">{ftable}</table></div>
<p class="note">{esc(D['verify'])}</p>
<h2 class="orn">{esc(D['hLegend'])}</h2><div class="sthala">{paras(x.get('sthala') or x['legend'])}</div><p class="note">{esc(D['legendNote'])}</p>
{padigam(D, t, l)}
{facts_html(D, x)}
<h2 class="orn">{esc(D['hHistory'])}</h2>{paras(x['history'])}
<!--AD-->
<h2 class="orn">{esc(D['hPari'])}</h2>{ul([esc(i) for i in x['parigaram']])}
<div class="lampbox"><button type="button" id="lamp" class="diya" data-temple="{t['slug']}" aria-label="{esc(D['lampT'])}">{DIYA}</button><div><b>{esc(D['lampT'])}</b><p id="lampMsg" data-done="{esc(D['lampDone'])}">{esc(D['lampP'])}</p></div></div>
{pari_link}
<h2>{esc(D['hReach'])}</h2>{paras(x['reach'])}
<h2>{esc(D['hTips'])}</h2>{ul([esc(i) for i in x['tips']])}
<h2>{esc(D['hNear'])}</h2><p class="chips">{near}</p>
<details class="src"><summary>{esc(D['hSrc'])}</summary><ul class="tl">{src}</ul></details>'''
            urls.append(write(l, D['tTitle'].format(n=x['name'], k=known), x['intro'][:300], f'temples/{t["slug"]}.html', body,
                              [home, (D['menuT'], f'{base(l)}temples/'), (x['name'], None)], ads))

        # ---------------------------------------------------------------- parigaram
        cards = ''
        for k in ORDER:
            g = graha(k)
            y = g[l]
            rows = [(D['cDay'], esc(y['day'])), (D['cColour'], esc(y['colour'])), (D['cGrain'], esc(y['grain'])), (D['cDeity'], esc(y['deity'])),
                    (D['cTempleCol'], tl(g['temple'], l)), (D['cMantra'], esc(y['mantra'])), (D['cGem'], esc(y['gem'])), (D['cSamith'], esc(y['samith']))]
            cards += f'<div class="gcard" id="g-{k}"><h3>{esc(y["name"])}</h3><dl>' + ''.join(f'<dt>{esc(a)}</dt><dd>{b}</dd>' for a, b in rows) + '</dl></div>'
        secs = ''
        for s in SECTIONS:
            y = s[l]
            temples = ' · '.join(tl(x, l) for x in s['temples'])
            secs += f'''<section id="{s['id']}"><h2>{esc(y['t'])}</h2><p>{esc(y['p'])}</p>{ul([esc(i) for i in y['li']])}{f'<p class="note">{esc(D["templesFor"])}: {temples}</p>' if temples else ''}</section>'''
            if s['id'] == 'sani':
                secs += '<!--AD-->'
        toc = ''.join(f'<a href="#{s["id"]}">{esc(s[l]["t"])}</a>' for s in SECTIONS)
        body = f'''<div class="thoranam" aria-hidden="true"></div><div class="introw">{deity_img(D, 'navagraha', D['pTable'])}<div><h1>{esc(D['pH1'])}</h1>
<p class="lead">{esc(D['pLead'])}</p></div></div>
<p class="warn">{esc(D['pWarn'])}</p>
<p class="chips">{toc}</p>
<h2>{esc(D['pTable'])}</h2>
<div class="ggrid">{cards}</div>
<p class="note">{esc(D['pTableNote'])}</p>
<div class="box"><b>{esc(D['pFind'])}</b><p>{esc(D['pFindLead'])}</p><p><a class="btn big" href="{base(l)}#horo">{esc(D['pCta'])}</a></p></div>
{secs}
<p><a class="btn big" href="{base(l)}temples/">{esc(D['menuT'])} →</a></p>'''
        urls.append(write(l, D['pTitle'], D['pLead'][:300], 'parigaram/', body, [home, (D['menuP'], None)], ads))
    return urls
