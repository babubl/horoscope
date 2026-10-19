"""Temple guide (Tamil Nadu: Navagraha sthalams and parigaram temples) and the Parigaram page, in English and Tamil.
Called from src/build.py after the other knowledge pages."""
import html
from urllib.parse import quote

import kb
import nakshatra as NK
from parigaram_data import GRAHAS, SECTIONS
from temples_data import TEMPLES

LANGS = ['en', 'ta']
BY = {t['slug']: t for t in TEMPLES}
ORDER = ['sun', 'moon', 'mars', 'mercury', 'jupiter', 'venus', 'saturn', 'rahu', 'ketu']

T = {
    'en': dict(
        menuT='Temple guide', menuP='Parigaram',
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
        hHistory='History and architecture', hLegend='The temple’s story', hPari='Parigaram done here', hReach='How to reach', hTips='Before you go', hSrc='Sources', hNear='Other temples in this guide',
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
        hHistory='வரலாறும் கட்டடக்கலையும்', hLegend='தல புராணம்', hPari='இங்கு செய்யப்படும் பரிகாரம்', hReach='செல்லும் வழி', hTips='செல்லும் முன்', hSrc='ஆதாரங்கள்', hNear='இந்த வழிகாட்டியில் உள்ள பிற கோயில்கள்',
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
        body = f'''<h1>{esc(D['idxH1'])}</h1>
<p class="lead">{esc(D['idxLead'])}</p>
<h2>{esc(D['nava'])}</h2>
<p>{esc(D['navaLead'])}</p>
<div class="ggrid">{rows}</div>
<!--AD-->
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
            body = f'''<h1>{esc(x['name'])}</h1>
<p class="lead">{esc(x['intro'])}</p>
<div class="tw wrapt"><table class="facts">{ftable}</table></div>
<p class="note">{esc(D['verify'])}</p>
<h2>{esc(D['hHistory'])}</h2>{paras(x['history'])}
<h2>{esc(D['hLegend'])}</h2>{paras(x['legend'])}<p class="note">{esc(D['legendNote'])}</p>
<!--AD-->
<h2>{esc(D['hPari'])}</h2>{ul([esc(i) for i in x['parigaram']])}
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
        body = f'''<h1>{esc(D['pH1'])}</h1>
<p class="lead">{esc(D['pLead'])}</p>
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
