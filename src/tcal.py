"""Tamil calendar section (English + Tamil): a page per month with every day's Tamil date, tithi and nakshatra,
Pournami & Amavasai dates with timings, and Tamil festivals with what each one is about. Chennai sunrise.
Called from src/build.py."""
import datetime
import json

import kb
import nakshatra as NK
from kb_data import EVENT_NAMES, GMONTHS, MONTHLY

LANGS = ['en', 'ta']
YEARS = [2026, 2027]
CITY = dict(lat=13.0878, lon=80.2785, tz='Asia/Kolkata')
esc = kb.esc

# What each festival is about (one or two lines), for the festivals page.
ABOUT = {
    'pongal': ('The Tamil harvest festival on the first day of Thai: new rice is boiled with milk and jaggery until it overflows — "Pongalo Pongal!" — as thanks to the Sun.',
               'தை முதல் நாள் தமிழர் அறுவடைத் திருநாள்: புது அரிசியைப் பாலும் வெல்லமும் சேர்த்துப் பொங்கவைத்து, "பொங்கலோ பொங்கல்!" என்று சூரியனுக்கு நன்றி செலுத்தும் நாள்.'),
    'puthandu': ('Tamil New Year, the first day of Chithirai, when the Sun enters Mesha. Homes are cleaned, kolams drawn and the new panchangam is read.',
                 'சூரியன் மேஷ ராசியில் நுழையும் சித்திரை முதல் நாள் — தமிழ்ப் புத்தாண்டு. வீடு சுத்தம் செய்து, கோலமிட்டு, புதிய பஞ்சாங்கம் வாசிக்கப்படும்.'),
    'thaipusam': ('The full-moon day of Thai under Pusam star, sacred to Lord Murugan — devotees carry kavadi and milk pots to Palani and other Murugan temples.',
                  'தை மாதப் பூச நட்சத்திரப் பௌர்ணமி — முருகனுக்கு உகந்த நாள்; பக்தர்கள் பழநி உள்ளிட்ட முருகன் கோயில்களுக்குக் காவடி, பால்குடம் ஏந்திச் செல்வர்.'),
    'mahashivaratri': ('The great night of Shiva in Masi: fasting, night-long vigil and four kala poojas in every Shiva temple.',
                       'மாசி மாதச் சிவனின் பெருவிரவு: உண்ணாவிரதம், இரவு முழுவதும் கண்விழிப்பு, சிவன் கோயில்களில் நான்கு கால பூஜை.'),
    'panguniuthiram': ('Uthiram star in Panguni, the day of divine weddings — Shiva–Parvati, Murugan–Deivanai, Rama–Sita; great festivals at Murugan temples.',
                       'பங்குனி மாத உத்திர நட்சத்திரம் — சிவ–பார்வதி, முருகன்–தெய்வானை, ராமர்–சீதை திருமண நாள்; முருகன் கோயில்களில் பெருவிழா.'),
    'chithrapournami': ('The full moon of Chithirai, sacred to Chitragupta; lakhs walk the Girivalam at Tiruvannamalai.',
                        'சித்திரை மாதப் பௌர்ணமி — சித்திரகுப்தருக்கு உகந்த நாள்; திருவண்ணாமலையில் லட்சக்கணக்கானோர் கிரிவலம் செல்வர்.'),
    'vaikasivisakam': ('Visakam star in Vaikasi — the birthday of Lord Murugan.', 'வைகாசி மாத விசாக நட்சத்திரம் — முருகப் பெருமான் அவதரித்த நாள்.'),
    'aadiperukku': ('18th of Aadi: thanksgiving to the Kaveri and all rivers as they swell with the monsoon; women offer prayers at the river banks.',
                    'ஆடி 18 — பருவமழையால் பெருகும் காவிரிக்கும் நதிகளுக்கும் நன்றி செலுத்தும் நாள்; பெண்கள் ஆற்றங்கரையில் வழிபடுவர்.'),
    'aadiamavasai': ('The new moon of Aadi, one of the most important days for tarpanam to ancestors — crowds gather at Rameswaram and river banks.',
                     'ஆடி மாத அமாவாசை — முன்னோர் தர்ப்பணத்துக்கு மிக முக்கியமான நாள்; ராமேஸ்வரம், ஆற்றங்கரைகளில் பெரும் கூட்டம்.'),
    'varalakshmi': ('Married women worship Goddess Varalakshmi for the family’s prosperity, on the Friday before the Aavani full moon.',
                    'குடும்ப நலனுக்காக சுமங்கலிகள் வரலட்சுமியை வழிபடும் விரதம் — ஆவணிப் பௌர்ணமிக்கு முந்தைய வெள்ளி.'),
    'rakhi': ('Aavani Avittam: the day of changing the sacred thread (upakarma).', 'ஆவணி அவிட்டம்: பூணூல் மாற்றும் (உபாகர்மா) நாள்.'),
    'janmashtami': ('Gokulashtami, the birth of Lord Krishna — little footprints are drawn from the doorstep to the pooja room.',
                    'கோகுலாஷ்டமி — கண்ணன் பிறந்த நாள்; வாசல் முதல் பூஜை அறை வரை குழந்தைக் கால் தடங்கள் வரைவர்.'),
    'ganesh': ('Vinayaka Chathurthi: clay Ganesha idols, kozhukattai and modakam.', 'விநாயகர் சதுர்த்தி: களிமண் விநாயகர், கொழுக்கட்டை, மோதகம்.'),
    'mahalaya': ('Mahalaya Amavasai closes the fortnight of the ancestors (Mahalaya Paksham) — the most important tarpanam day of the year.',
                 'மகாளய பட்சத்தை நிறைவு செய்யும் மகாளய அமாவாசை — ஆண்டின் மிக முக்கியமான தர்ப்பண நாள்.'),
    'navaratri': ('Nine nights of the Goddess begin; homes set up the golu (kolu) of dolls.', 'அம்பாளின் ஒன்பது இரவுகள் தொடக்கம்; வீடுகளில் கொலு வைப்பர்.'),
    'saraswati': ('Saraswati Pooja and Ayudha Pooja: books, instruments, tools and vehicles are worshipped.', 'சரஸ்வதி பூஜை, ஆயுத பூஜை: புத்தகங்கள், இசைக்கருவிகள், கருவிகள், வாகனங்களுக்கு வழிபாடு.'),
    'dasara': ('Vijayadasami: victory of good; children begin their learning (Vidyarambham).', 'விஜயதசமி: தீமையை வென்ற நாள்; குழந்தைகளுக்கு வித்யாரம்பம்.'),
    'deepavali_s': ('Deepavali in Tamil Nadu is celebrated at dawn on Naraka Chaturdasi — oil bath, new clothes, sweets and crackers.',
                    'தமிழகத்தில் நரக சதுர்த்தசி விடியலில் தீபாவளி — எண்ணெய்க் குளியல், புத்தாடை, இனிப்பு, பட்டாசு.'),
    'diwali': ('Lakshmi Pooja on the Deepavali new moon.', 'தீபாவளி அமாவாசையில் லட்சுமி பூஜை.'),
    'skanda': ('Kanda Sashti: six days of fasting ending with Soorasamharam, Murugan’s victory over Surapadman — grandest at Thiruchendur.',
               'கந்த சஷ்டி: ஆறு நாள் விரதம், முருகன் சூரபத்மனை வென்ற சூரசம்ஹாரத்தில் நிறைவு — திருச்செந்தூரில் சிறப்பு.'),
    'karthigaideepam': ('Thirukarthigai: rows of lamps in every home; the Maha Deepam is lit atop the Tiruvannamalai hill.',
                        'திருக்கார்த்திகை: வீடுதோறும் விளக்கு வரிசை; திருவண்ணாமலை உச்சியில் மகா தீபம்.'),
    'vaikunta': ('Vaikunta Ekadasi: the Paramapada Vasal (gate of heaven) opens in Vishnu temples — Srirangam above all.',
                 'வைகுண்ட ஏகாதசி: பெருமாள் கோயில்களில், குறிப்பாக ஸ்ரீரங்கத்தில், பரமபத வாசல் திறப்பு.'),
    'arudra': ('Arudra Darshanam in Margazhi: Nataraja’s cosmic dance, celebrated with kali at Chidambaram.', 'மார்கழி ஆருத்ரா தரிசனம்: நடராஜரின் திருநடனம்; சிதம்பரத்தில் சிறப்பு, களி நிவேதனம்.'),
    'rathasaptami': ('Ratha Saptami: the Sun turns his chariot north — the great festival of Suryanar Kovil.', 'ரத சப்தமி: சூரியன் தேரை வடக்கே திருப்பும் நாள் — சூரியனார் கோயிலின் பெருவிழா.'),
    'akshaya': ('Akshaya Tritiya: whatever good is begun today is believed to grow without end.', 'அட்சய திருதியை: இன்று தொடங்கும் நற்செயல்கள் குறையாமல் வளரும் என்பது நம்பிக்கை.'),
    'ramnavami': ('Sri Rama Navami, the birth of Lord Rama.', 'ஸ்ரீ ராம நவமி — ராமர் அவதரித்த நாள்.'),
    'gurupurnima': ('Guru Pournami: honouring one’s teachers and Vyasa.', 'குரு பௌர்ணமி: ஆசிரியர்களையும் வியாசரையும் போற்றும் நாள்.'),
}

T = {
    'en': dict(menu='Tamil calendar', mTitle='Tamil Calendar {mon} {y} — Tamil Date, Tithi, Nakshatra, Pournami, Amavasai | Suba Jathagam',
               mH1='Tamil calendar — {mon} {y}', mLead='Every day of {mon} {y} with its Tamil date, tithi and nakshatra at sunrise in Chennai, with Pournami, Amavasai, Ekadashi, Pradosham and festivals marked.',
               idxTitle='Tamil Calendar 2026 & 2027 — Monthly Tamil Date, Tithi & Festivals | Suba Jathagam', idxH1='Tamil calendar 2026 & 2027',
               idxLead='Month-by-month Tamil calendar with Tamil dates, tithi, nakshatra and every Pournami, Amavasai, Ekadashi, Pradosham and festival — plus separate lists of full and new moons and Tamil festivals.',
               cDate='Date', cDay='Day', cTamil='Tamil date', cTithi='Tithi', cStar='Star', cSpecial='Special', thisMonth='This month', prev='← {m}', next='{m} →',
               paTitle='Pournami & Amavasai {ys} — Full Moon and New Moon Dates with Timings | Suba Jathagam', paH1='Pournami & Amavasai dates',
               paLead='Every full moon (Pournami) and new moon (Amavasai) in {ys}, with the tithi’s start and end times in India. Pournami is the day for Girivalam and Satyanarayana pooja; Amavasai is the day for tarpanam to ancestors.',
               cStart='Tithi starts', cEnd='Tithi ends', pournami='Pournami', amavasai='Amavasai',
               fTitle='Tamil Festivals {ys} — Pongal, Thaipusam, Deepavali & All Pandigai Dates | Suba Jathagam', fH1='Tamil festivals (pandigai)',
               fLead='Dates of every major Tamil festival in {ys}, calculated for Chennai, with what each festival is about.',
               ruleNote='Calculated for Chennai with our own panchangam: the tithi and star shown are those at sunrise. Temple calendars can differ by a day.',
               more='Also see', lists=['Pournami & Amavasai', 'Tamil festivals', 'Festival & vrat calendar']),
    'ta': dict(menu='தமிழ் நாட்காட்டி', mTitle='தமிழ் நாட்காட்டி {mon} {y} — தமிழ்த் தேதி, திதி, நட்சத்திரம், பௌர்ணமி, அமாவாசை | சுப ஜாதகம்',
               mH1='தமிழ் நாட்காட்டி — {mon} {y}', mLead='{mon} {y}-ன் ஒவ்வொரு நாளுக்கும் தமிழ்த் தேதி, சென்னை சூரிய உதயத்தில் உள்ள திதி, நட்சத்திரம் — பௌர்ணமி, அமாவாசை, ஏகாதசி, பிரதோஷம், பண்டிகைகள் குறிக்கப்பட்டுள்ளன.',
               idxTitle='தமிழ் நாட்காட்டி 2026, 2027 — மாதவாரியாகத் தமிழ்த் தேதி, திதி, பண்டிகைகள் | சுப ஜாதகம்', idxH1='தமிழ் நாட்காட்டி 2026, 2027',
               idxLead='தமிழ்த் தேதி, திதி, நட்சத்திரம், அனைத்து பௌர்ணமி, அமாவாசை, ஏகாதசி, பிரதோஷம், பண்டிகைகளுடன் மாதவாரியான தமிழ் நாட்காட்டி — பௌர்ணமி–அமாவாசை, தமிழ்ப் பண்டிகைகளுக்குத் தனிப் பட்டியல்களும் உண்டு.',
               cDate='தேதி', cDay='கிழமை', cTamil='தமிழ்த் தேதி', cTithi='திதி', cStar='நட்சத்திரம்', cSpecial='சிறப்பு', thisMonth='இந்த மாதம்', prev='← {m}', next='{m} →',
               paTitle='பௌர்ணமி, அமாவாசை {ys} — தேதிகளும் நேரங்களும் | சுப ஜாதகம்', paH1='பௌர்ணமி, அமாவாசை நாட்கள்',
               paLead='{ys}-ல் வரும் அனைத்துப் பௌர்ணமி, அமாவாசை நாட்களும், திதி தொடங்கும், முடியும் நேரங்களுடன். பௌர்ணமி — கிரிவலம், சத்யநாராயண பூஜைக்கு உகந்தது; அமாவாசை — முன்னோர் தர்ப்பணத்துக்கு உரியது.',
               cStart='திதி தொடக்கம்', cEnd='திதி முடிவு', pournami='பௌர்ணமி', amavasai='அமாவாசை',
               fTitle='தமிழ்ப் பண்டிகைகள் {ys} — பொங்கல், தைப்பூசம், தீபாவளி உள்ளிட்ட அனைத்துப் பண்டிகை நாட்கள் | சுப ஜாதகம்', fH1='தமிழ்ப் பண்டிகைகள்',
               fLead='{ys}-ல் வரும் முக்கியத் தமிழ்ப் பண்டிகைகளின் தேதிகள் (சென்னைக்குக் கணிக்கப்பட்டவை), ஒவ்வொன்றின் சிறப்புடன்.',
               ruleNote='சென்னைக்கு எங்கள் சொந்தப் பஞ்சாங்கக் கணிதம்: காட்டப்படும் திதியும் நட்சத்திரமும் சூரிய உதயத்தில் உள்ளவை. கோயில் பஞ்சாங்கங்களில் ஒரு நாள் வேறுபடலாம்.',
               more='மேலும் பார்க்க', lists=['பௌர்ணமி, அமாவாசை', 'தமிழ்ப் பண்டிகைகள்', 'பண்டிகை, விரத நாட்காட்டி']),
}

MARK = {'pournami': '🌕', 'amavasya': '🌑', 'ekadashi_s': '🪔', 'ekadashi_k': '🪔', 'pradosham_s': '🔱', 'pradosham_k': '🔱', 'sankashti': '🐘', 'chaturthi': '🐘',
        'shivaratri_m': '🔱', 'shashti': '🦚', 'kiruthigai': '🦚'}


def base(l):
    return '/' if l == 'en' else f'/{l}/'


def alts(rel):
    return [(x, base(x) + rel) for x in LANGS]


def data():
    days = kb.node_json(f"""global.Astronomy=require('./src/vendor/astronomy.browser.min.js');const J=require('./src/engine.js');
const out=[];for(let t=Date.UTC({YEARS[0]},0,1);t<=Date.UTC({YEARS[-1]},11,31);t+=86400000){{const x=new Date(t);
const p=J.dailyPanchang({{y:x.getUTCFullYear(),m:x.getUTCMonth()+1,d:x.getUTCDate(),lat:{CITY['lat']},lon:{CITY['lon']},zone:'{CITY['tz']}'}});
out.push({{d:x.toISOString().slice(0,10),w:p.weekday,tm:p.tamil.month,td:p.tamil.date,ti:p.tithi[0].index,nk:p.nakshatra[0].index}});}}
process.stdout.write(JSON.stringify(out));""")
    evs = kb.node_json(f"""global.Astronomy=require('./src/vendor/astronomy.browser.min.js');const F=require('./src/festivals.js');
const reg={{}};F.EVENTS.forEach(e=>reg[e.id]=e.reg);
process.stdout.write(JSON.stringify(F.compute({json.dumps(CITY)},[{YEARS[0]},1,1],[{YEARS[-1]},12,31]).filter(e=>reg[e.id]==='all'||reg[e.id].split(' ').includes('ta'))));""")
    return days, evs


def tithi_name(Lx, i):
    if i == 14:
        return Lx['pournami']
    if i == 29:
        return Lx['amavasai']
    return Lx['pakShort'][0 if i < 15 else 1] + ' ' + Lx['tithis'][i % 15]


def fmt_ms(ms):
    if not ms:
        return '—'
    d = datetime.datetime.utcfromtimestamp(ms / 1000 + 330 * 60)
    return f'{d.day:02d}/{d.month:02d} {d.hour:02d}:{d.minute:02d}'


def generate(I, ads):
    days, evs = data()
    by_date = {}
    for e in evs:
        by_date.setdefault(e['date'], []).append(e)
    urls = []
    months = sorted({d['d'][:7] for d in days})
    today = (datetime.datetime.utcnow() + datetime.timedelta(minutes=330)).strftime('%Y-%m')
    for l in LANGS:
        D, Lx = T[l], I[l]
        home = (NK.S[l]['home'], base(l))
        mname = lambda ym: f'{GMONTHS[l][int(ym[5:]) - 1]} {ym[:4]}'
        links = f'<p class="chips"><a href="{base(l)}pournami-amavasai/">🌕 {esc(D["lists"][0])}</a><a href="{base(l)}tamil-festivals/">🪔 {esc(D["lists"][1])}</a><a href="{base(l)}calendar/">📅 {esc(D["lists"][2])}</a></p>'
        # ---------------------------------------------------------------- month pages
        for k, ym in enumerate(months):
            md = [d for d in days if d['d'].startswith(ym)]
            first_w = md[0]['w']
            cells = '<div class="cg-h">' + ''.join(f'<span>{esc(Lx["days"][i][:3] if l == "en" else Lx["days"][i][:2])}</span>' for i in range(7)) + '</div><div class="cg">' + '<i></i>' * first_w
            rows = ''
            for d in md:
                ev = by_date.get(d['d'], [])
                marks = ''.join(MARK.get(e['id'], '') for e in ev)
                fest = [e for e in ev if e['id'] not in MONTHLY]
                cls = ' '.join(x for x in ['po' if d['ti'] == 14 else '', 'am' if d['ti'] == 29 else '', 'fe' if fest else '', 'su' if d['w'] == 0 else ''] if x)
                tdate = f'{Lx["months"][d["tm"]][:3] if l == "en" else Lx["months"][d["tm"]]} {d["td"]}'
                cells += f'<a href="#d{d["d"][8:]}" class="{cls}" data-d="{d["d"]}"><b>{int(d["d"][8:])}</b><small>{esc(tdate)}</small><em>{marks}{"✨" if fest else ""}</em></a>'
                special = ', '.join(esc(EVENT_NAMES[e['id']][l]) for e in ev)
                rows += f'<tr id="d{d["d"][8:]}" class="{cls}" data-d="{d["d"]}"><td><b>{int(d["d"][8:])}</b></td><td>{esc(Lx["days"][d["w"]])}</td><td>{esc(Lx["months"][d["tm"]])} {d["td"]}</td><td>{esc(tithi_name(Lx, d["ti"]))}</td><td>{esc(Lx["naks"][d["nk"]])}</td><td>{special}</td></tr>'
            cells += '</div>'
            nav = ''
            if k > 0:
                nav += f'<a href="{base(l)}tamil-calendar/{months[k - 1]}.html">{esc(D["prev"].format(m=mname(months[k - 1])))}</a>'
            if k < len(months) - 1:
                nav += f'<a href="{base(l)}tamil-calendar/{months[k + 1]}.html">{esc(D["next"].format(m=mname(months[k + 1])))}</a>'
            v = dict(mon=GMONTHS[l][int(ym[5:]) - 1], y=ym[:4])
            body = f'''<h1>{esc(D['mH1'].format(**v))}</h1>
<p class="lead">{esc(D['mLead'].format(**v))}</p>
<p class="mnav">{nav}</p>
<div class="calgrid">{cells}</div>
<p class="legend-c">🌕 {esc(Lx['pournami'])} · 🌑 {esc(Lx['amavasai'])} · 🪔 {esc(EVENT_NAMES['ekadashi_s'][l].split(' (')[0])} · 🔱 {esc(EVENT_NAMES['pradosham_s'][l].split(' (')[0])} · 🐘 {esc(EVENT_NAMES['sankashti'][l])} · 🦚 {esc(EVENT_NAMES['kiruthigai'][l])} / {esc(EVENT_NAMES['shashti'][l])} · ✨ {esc(D['lists'][1])}</p>
<!--AD-->
<div class="tw wrapt"><table class="daytab"><tr><th>{esc(D['cDate'])}</th><th>{esc(D['cDay'])}</th><th>{esc(D['cTamil'])}</th><th>{esc(D['cTithi'])}</th><th>{esc(D['cStar'])}</th><th>{esc(D['cSpecial'])}</th></tr>{rows}</table></div>
<p class="note">{esc(D['ruleNote'])}</p>
<p class="mnav">{nav}</p>
<h2>{esc(D['more'])}</h2>{links}
<script>(function(){{var t=new Date(Date.now()+330*60000).toISOString().slice(0,10);document.querySelectorAll('[data-d="'+t+'"]').forEach(function(e){{e.classList.add('today')}});}})();</script>'''
            urls.append(kb.page(l, D['mTitle'].format(mon=v['mon'], y=v['y']), D['mLead'].format(**v)[:300], f'{base(l)}tamil-calendar/{ym}.html', alts(f'tamil-calendar/{ym}.html'),
                                body, [home, (D['menu'], f'{base(l)}tamil-calendar/'), (mname(ym), None)], ads))
        # ---------------------------------------------------------------- index
        yrs = ''
        for y in YEARS:
            yrs += f'<h2>{y}</h2><p class="chips big">' + ''.join(f'<a href="{base(l)}tamil-calendar/{ym}.html"{" class=on" if ym == today else ""}>{esc(GMONTHS[l][int(ym[5:]) - 1])}</a>' for ym in months if ym.startswith(str(y))) + '</p>'
        body = f'''<h1>{esc(D['idxH1'])}</h1><p class="lead">{esc(D['idxLead'])}</p>
<p><a class="btn big" id="thisMonth" href="{base(l)}tamil-calendar/{today if today in months else months[0]}.html">📅 {esc(D['thisMonth'])}</a></p>
{yrs}{links}
<script>(function(){{var m=new Date(Date.now()+330*60000).toISOString().slice(0,7),a=document.getElementById('thisMonth');if(a&&{json.dumps(months)}.indexOf(m)>=0)a.href='{base(l)}tamil-calendar/'+m+'.html';}})();</script>'''
        urls.append(kb.page(l, D['idxTitle'], D['idxLead'][:300], f'{base(l)}tamil-calendar/', alts('tamil-calendar/'), body, [home, (D['menu'], None)], ads))
        # ---------------------------------------------------------------- pournami & amavasai
        ys = f'{YEARS[0]}–{YEARS[-1]}' if l == 'en' else f'{YEARS[0]}, {YEARS[-1]}'
        sec = ''
        for y in YEARS:
            def table(eid, label):
                rs = ''
                for e in [e for e in evs if e['id'] == eid and e['date'].startswith(str(y))]:
                    dd = e['date']
                    named = [EVENT_NAMES[x['id']][l] for x in by_date.get(dd, []) if x['id'] not in MONTHLY]
                    tm = next((x for x in days if x['d'] == dd), None)
                    rs += f'<tr data-d="{dd}"><td><b>{int(dd[8:])} {esc(GMONTHS[l][int(dd[5:7]) - 1])}</b></td><td>{esc(Lx["days"][e["weekday"]])}</td><td>{esc(Lx["months"][tm["tm"]]) + " " + str(tm["td"]) if tm else ""}</td><td class="tm">{fmt_ms(e.get("start"))}</td><td class="tm">{fmt_ms(e.get("end"))}</td><td>{esc(", ".join(named))}</td></tr>'
                return f'<h3>{label} {y}</h3><div class="tw wrapt"><table><tr><th>{esc(D["cDate"])}</th><th>{esc(D["cDay"])}</th><th>{esc(D["cTamil"])}</th><th>{esc(D["cStart"])}</th><th>{esc(D["cEnd"])}</th><th>{esc(D["cSpecial"])}</th></tr>{rs}</table></div>'
            sec += f'<h2>{y}</h2>' + table('pournami', '🌕 ' + D['pournami']) + table('amavasya', '🌑 ' + D['amavasai'])
        body = f'''<h1>{esc(D['paH1'])} {ys}</h1><p class="lead">{esc(D['paLead'].format(ys=ys))}</p>{sec}<p class="note">{esc(D['ruleNote'])}</p>{links}
<script>(function(){{var t=new Date(Date.now()+330*60000).toISOString().slice(0,10),n=null;document.querySelectorAll('tr[data-d]').forEach(function(r){{if(r.dataset.d<t)r.classList.add('past');}});}})();</script>'''
        urls.append(kb.page(l, D['paTitle'].format(ys=ys), D['paLead'].format(ys=ys)[:300], f'{base(l)}pournami-amavasai/', alts('pournami-amavasai/'), body,
                            [home, (D['menu'], f'{base(l)}tamil-calendar/'), (D['lists'][0], None)], ads))
        # ---------------------------------------------------------------- Tamil festivals
        sec = ''
        for y in YEARS:
            items = ''
            for e in [e for e in evs if e['id'] not in MONTHLY and e['date'].startswith(str(y))]:
                dd = e['date']
                tm = next((x for x in days if x['d'] == dd), None)
                about = ABOUT.get(e['id'])
                items += (f'<div class="fest" data-d="{dd}"><div class="fd"><b>{int(dd[8:])}</b><span>{esc(GMONTHS[l][int(dd[5:7]) - 1][:3] if l == "en" else GMONTHS[l][int(dd[5:7]) - 1])}</span></div>'
                          f'<div><h3>{esc(EVENT_NAMES[e["id"]][l])}</h3><p class="sub">{esc(Lx["days"][e["weekday"]])}{" · " + esc(Lx["months"][tm["tm"]]) + " " + str(tm["td"]) if tm else ""}</p>'
                          f'{"<p>" + esc(about[0 if l == "en" else 1]) + "</p>" if about else ""}</div></div>')
            sec += f'<h2>{y}</h2><div class="festlist">{items}</div>'
        body = f'''<h1>{esc(D['fH1'])} {ys}</h1><p class="lead">{esc(D['fLead'].format(ys=ys))}</p>{sec}<p class="note">{esc(D['ruleNote'])}</p>{links}
<script>(function(){{var t=new Date(Date.now()+330*60000).toISOString().slice(0,10);document.querySelectorAll('.fest').forEach(function(r){{if(r.dataset.d<t)r.classList.add('past');}});}})();</script>'''
        urls.append(kb.page(l, D['fTitle'].format(ys=ys), D['fLead'].format(ys=ys)[:300], f'{base(l)}tamil-festivals/', alts('tamil-festivals/'), body,
                            [home, (D['menu'], f'{base(l)}tamil-calendar/'), (D['lists'][1], None)], ads))
    return urls, days, evs
