"""Nakshatra knowledge pages: one page per star (27) in every language, plus an index page.
Each page lists the star's facts and its best and risky marriage matches, computed with the same
engine the app uses (10 porutham + 36 guna). Called from src/build.py; returns the URLs for the sitemap."""
import html
import json
import os
import subprocess

SITE = 'https://subajathagam.in'
LANGS = ['en', 'ta', 'ml', 'te', 'kn', 'hi']
NATIVE = {'en': 'English', 'ta': 'தமிழ்', 'ml': 'മലയാളം', 'te': 'తెలుగు', 'kn': 'ಕನ್ನಡ', 'hi': 'हिन्दी'}
BRAND = {'en': 'Suba Jathagam', 'ta': 'சுப ஜாதகம்', 'ml': 'ശുഭ ജാതകം', 'te': 'శుభ జాతకం', 'kn': 'ಶುಭ ಜಾತಕ', 'hi': 'शुभ जातक'}
LABELS = ['lordL', 'rasiL', 'ganaL', 'yoniL', 'nadiL', 'rajjuL']

S = {
    'en': dict(ctaShort='Check match', title='{s} Nakshatra — Marriage Matching, Porutham & Guna | Suba Jathagam',
               desc='Best marriage matches for {s} nakshatra: 10 porutham, 36 guna and Rajju for every star. Lord {lord}, {gana} gana, {yoni} yoni.',
               h1='{s} Nakshatra: marriage matching',
               intro='{s} is nakshatra number {n} of 27, ruled by {lord}. People born in {s} belong to the {gana} gana, with {yoni} yoni, {nadi} nadi and {rajju} rajju.',
               brideH="If the bride's star is {s} — best matches", groomH="If the groom's star is {s} — best matches",
               colGroom="Groom's star", colBride="Bride's star", avoidH='Check carefully (Rajju, Vedhai or Nadi)', avoidNone='None',
               note='Scores use the middle pada of each star. Rasi-based checks can change with the pada, so match the two actual birth charts for a final answer.',
               cta='Check your match free →', allH='All 27 nakshatras',
               indexTitle='27 Nakshatras — Marriage Matching, Lords, Gana & Rajju | Suba Jathagam', indexH1='The 27 nakshatras',
               indexLead='Lord, rasi, gana, yoni, nadi and rajju of every nakshatra — and its best marriage matches by 10 porutham and 36 guna.',
               home='Home', lordL='Star lord', rasiL='Rasi (pada)', ganaL='Gana', yoniL='Yoni', nadiL='Nadi', rajjuL='Rajju',
               menu='27 Nakshatras'),
    'ta': dict(ctaShort='பொருத்தம் பார்', title='{s} நட்சத்திரம் — திருமணப் பொருத்தம், குணங்கள் | சுப ஜாதகம்',
               desc='{s} நட்சத்திரத்துக்குப் பொருந்தும் நட்சத்திரங்கள்: 10 பொருத்தம், 36 குண மதிப்பெண், ரஜ்ஜு. அதிபதி {lord}, {gana} கணம், {yoni} யோனி.',
               h1='{s} நட்சத்திரம்: திருமணப் பொருத்தம்',
               intro='27 நட்சத்திரங்களில் {s} {n}-வது நட்சத்திரம்; இதன் அதிபதி {lord}. {s} நட்சத்திரத்தில் பிறந்தவர்கள் {gana} கணம், {yoni} யோனி, {nadi} நாடி, {rajju} வகையைச் சேர்ந்தவர்கள்.',
               brideH='பெண் {s} நட்சத்திரம் என்றால் — சிறந்த பொருத்தங்கள்', groomH='ஆண் {s} நட்சத்திரம் என்றால் — சிறந்த பொருத்தங்கள்',
               colGroom='ஆண் நட்சத்திரம்', colBride='பெண் நட்சத்திரம்', avoidH='கவனமாகப் பார்க்க வேண்டியவை (ரஜ்ஜு / வேதை / நாடி)', avoidNone='இல்லை',
               note='மதிப்பெண்கள் ஒவ்வொரு நட்சத்திரத்தின் நடுப் பாதத்தைக் கொண்டு கணிக்கப்பட்டவை. ராசி சார்ந்த பொருத்தங்கள் பாதத்தைப் பொறுத்து மாறலாம் — சரியான முடிவுக்கு இருவரின் பிறப்பு விவரங்களுடன் பொருத்தம் பாருங்கள்.',
               cta='இலவசமாகப் பொருத்தம் பாருங்கள் →', allH='27 நட்சத்திரங்கள்',
               indexTitle='27 நட்சத்திரங்கள் — பொருத்தம், அதிபதி, கணம், ரஜ்ஜு | சுப ஜாதகம்', indexH1='27 நட்சத்திரங்கள்',
               indexLead='ஒவ்வொரு நட்சத்திரத்துக்கும் அதிபதி, ராசி, கணம், யோனி, நாடி, ரஜ்ஜு — மற்றும் திருமணத்துக்குச் சிறந்த பொருத்தங்கள்.',
               home='முகப்பு', lordL='நட்சத்திர அதிபதி', rasiL='ராசி (பாதம்)', ganaL='கணம்', yoniL='யோனி', nadiL='நாடி', rajjuL='ரஜ்ஜு',
               menu='27 நட்சத்திரங்கள்'),
    'ml': dict(ctaShort='പൊരുത്തം നോക്കുക', title='{s} നക്ഷത്രം — വിവാഹ പൊരുത്തം, സ്വഭാവം | ശുഭ ജാതകം',
               desc='{s} നക്ഷത്രത്തിന് ചേരുന്ന നക്ഷത്രങ്ങൾ: 10 പൊരുത്തം, 36 ഗുണം, രജ്ജു. നാഥൻ {lord}, {gana} ഗണം, {yoni} യോനി.',
               h1='{s} നക്ഷത്രം: വിവാഹ പൊരുത്തം',
               intro='27 നക്ഷത്രങ്ങളിൽ {n}-ാമത്തേതാണ് {s}; ഇതിന്റെ നാഥൻ {lord}. {s} നക്ഷത്രത്തിൽ ജനിച്ചവർ {gana} ഗണം, {yoni} യോനി, {nadi} നാഡി, {rajju} രജ്ജു എന്നിവയിൽ പെടുന്നു.',
               brideH='വധുവിന്റെ നക്ഷത്രം {s} ആണെങ്കിൽ — മികച്ച പൊരുത്തങ്ങൾ', groomH='വരന്റെ നക്ഷത്രം {s} ആണെങ്കിൽ — മികച്ച പൊരുത്തങ്ങൾ',
               colGroom='വരന്റെ നക്ഷത്രം', colBride='വധുവിന്റെ നക്ഷത്രം', avoidH='ശ്രദ്ധിച്ച് നോക്കേണ്ടവ (രജ്ജു / വേധ / നാഡി)', avoidNone='ഇല്ല',
               note='ഓരോ നക്ഷത്രത്തിന്റെയും നടുവിലെ പാദം വെച്ചാണ് ഈ സ്കോറുകൾ. രാശി ആശ്രയിച്ചുള്ള പൊരുത്തങ്ങൾ പാദം അനുസരിച്ച് മാറാം — കൃത്യമായ ഫലത്തിന് ഇരുവരുടെയും ജനന വിവരങ്ങൾ നൽകി പൊരുത്തം നോക്കുക.',
               cta='സൗജന്യമായി പൊരുത്തം നോക്കുക →', allH='27 നക്ഷത്രങ്ങൾ',
               indexTitle='27 നക്ഷത്രങ്ങൾ — പൊരുത്തം, നാഥൻ, ഗണം, രജ്ജു | ശുഭ ജാതകം', indexH1='27 നക്ഷത്രങ്ങൾ',
               indexLead='ഓരോ നക്ഷത്രത്തിന്റെയും നാഥൻ, രാശി, ഗണം, യോനി, നാഡി, രജ്ജു — ഒപ്പം വിവാഹത്തിന് മികച്ച പൊരുത്തങ്ങളും.',
               home='ഹോം', lordL='നക്ഷത്രനാഥൻ', rasiL='രാശി (പാദം)', ganaL='ഗണം', yoniL='യോനി', nadiL='നാഡി', rajjuL='രജ്ജു',
               menu='27 നക്ഷത്രങ്ങൾ'),
    'te': dict(ctaShort='పొంతన చూడండి', title='{s} నక్షత్రం — వివాహ పొంతన, గుణ మేళనం | శుభ జాతకం',
               desc='{s} నక్షత్రానికి సరిపోయే నక్షత్రాలు: 36 గుణాల మేళనం, 10 పొరుత్తాలు, రజ్జు. అధిపతి {lord}, {gana} గణం, {yoni} యోని.',
               h1='{s} నక్షత్రం: వివాహ పొంతన',
               intro='27 నక్షత్రాల్లో {s} {n}వ నక్షత్రం; దీని అధిపతి {lord}. {s} నక్షత్రంలో పుట్టినవారు {gana} గణం, {yoni} యోని, {nadi} నాడి, {rajju} రజ్జుకు చెందుతారు.',
               brideH='వధువు నక్షత్రం {s} అయితే — మంచి పొంతనలు', groomH='వరుడి నక్షత్రం {s} అయితే — మంచి పొంతనలు',
               colGroom='వరుడి నక్షత్రం', colBride='వధువు నక్షత్రం', avoidH='జాగ్రత్తగా చూడవలసినవి (రజ్జు / వేధ / నాడి)', avoidNone='ఏమీ లేవు',
               note='ప్రతి నక్షత్రం మధ్య పాదం ఆధారంగా ఈ స్కోర్లు లెక్కించాం. రాశి ఆధారిత పొంతనలు పాదాన్ని బట్టి మారవచ్చు — ఖచ్చితమైన ఫలితానికి ఇద్దరి జన్మ వివరాలతో పొంతన చూడండి.',
               cta='ఉచితంగా పొంతన చూడండి →', allH='27 నక్షత్రాలు',
               indexTitle='27 నక్షత్రాలు — పొంతన, అధిపతి, గణం, రజ్జు | శుభ జాతకం', indexH1='27 నక్షత్రాలు',
               indexLead='ప్రతి నక్షత్రానికి అధిపతి, రాశి, గణం, యోని, నాడి, రజ్జు — వివాహానికి మంచి పొంతనలతో సహా.',
               home='హోమ్', lordL='నక్షత్ర అధిపతి', rasiL='రాశి (పాదం)', ganaL='గణం', yoniL='యోని', nadiL='నాడి', rajjuL='రజ్జు',
               menu='27 నక్షత్రాలు'),
    'kn': dict(ctaShort='ಹೊಂದಾಣಿಕೆ ನೋಡಿ', title='{s} ನಕ್ಷತ್ರ — ಮದುವೆ ಹೊಂದಾಣಿಕೆ, ಗುಣ ಮಿಲನ | ಶುಭ ಜಾತಕ',
               desc='{s} ನಕ್ಷತ್ರಕ್ಕೆ ಹೊಂದುವ ನಕ್ಷತ್ರಗಳು: 36 ಗುಣ ಮಿಲನ, 10 ಪೊರುತ್ತ, ರಜ್ಜು. ಅಧಿಪತಿ {lord}, {gana} ಗಣ, {yoni} ಯೋನಿ.',
               h1='{s} ನಕ್ಷತ್ರ: ಮದುವೆ ಹೊಂದಾಣಿಕೆ',
               intro='27 ನಕ್ಷತ್ರಗಳಲ್ಲಿ {s} {n}ನೇ ನಕ್ಷತ್ರ; ಇದರ ಅಧಿಪತಿ {lord}. {s} ನಕ್ಷತ್ರದಲ್ಲಿ ಹುಟ್ಟಿದವರು {gana} ಗಣ, {yoni} ಯೋನಿ, {nadi} ನಾಡಿ, {rajju} ರಜ್ಜುಗೆ ಸೇರುತ್ತಾರೆ.',
               brideH='ವಧುವಿನ ನಕ್ಷತ್ರ {s} ಆಗಿದ್ದರೆ — ಉತ್ತಮ ಹೊಂದಾಣಿಕೆಗಳು', groomH='ವರನ ನಕ್ಷತ್ರ {s} ಆಗಿದ್ದರೆ — ಉತ್ತಮ ಹೊಂದಾಣಿಕೆಗಳು',
               colGroom='ವರನ ನಕ್ಷತ್ರ', colBride='ವಧುವಿನ ನಕ್ಷತ್ರ', avoidH='ಎಚ್ಚರಿಕೆಯಿಂದ ನೋಡಬೇಕಾದವು (ರಜ್ಜು / ವೇಧ / ನಾಡಿ)', avoidNone='ಇಲ್ಲ',
               note='ಪ್ರತಿ ನಕ್ಷತ್ರದ ಮಧ್ಯದ ಪಾದವನ್ನು ಆಧರಿಸಿ ಈ ಅಂಕಗಳನ್ನು ಲೆಕ್ಕಿಸಲಾಗಿದೆ. ರಾಶಿ ಆಧಾರಿತ ಹೊಂದಾಣಿಕೆಗಳು ಪಾದದಂತೆ ಬದಲಾಗಬಹುದು — ನಿಖರ ಫಲಿತಾಂಶಕ್ಕೆ ಇಬ್ಬರ ಜನ್ಮ ವಿವರಗಳೊಂದಿಗೆ ಹೊಂದಾಣಿಕೆ ನೋಡಿ.',
               cta='ಉಚಿತವಾಗಿ ಹೊಂದಾಣಿಕೆ ನೋಡಿ →', allH='27 ನಕ್ಷತ್ರಗಳು',
               indexTitle='27 ನಕ್ಷತ್ರಗಳು — ಹೊಂದಾಣಿಕೆ, ಅಧಿಪತಿ, ಗಣ, ರಜ್ಜು | ಶುಭ ಜಾತಕ', indexH1='27 ನಕ್ಷತ್ರಗಳು',
               indexLead='ಪ್ರತಿ ನಕ್ಷತ್ರದ ಅಧಿಪತಿ, ರಾಶಿ, ಗಣ, ಯೋನಿ, ನಾಡಿ, ರಜ್ಜು — ಮದುವೆಗೆ ಉತ್ತಮ ಹೊಂದಾಣಿಕೆಗಳ ಜೊತೆಗೆ.',
               home='ಮುಖಪುಟ', lordL='ನಕ್ಷತ್ರಾಧಿಪತಿ', rasiL='ರಾಶಿ (ಪಾದ)', ganaL='ಗಣ', yoniL='ಯೋನಿ', nadiL='ನಾಡಿ', rajjuL='ರಜ್ಜು',
               menu='27 ನಕ್ಷತ್ರಗಳು'),
    'hi': dict(ctaShort='मिलान करें', title='{s} नक्षत्र — कुंडली मिलान, गुण मिलान और रज्जु | शुभ जातक',
               desc='{s} नक्षत्र से मेल खाने वाले नक्षत्र: 36 गुण मिलान, नाड़ी, रज्जु। स्वामी {lord}, {gana} गण, {yoni} योनि।',
               h1='{s} नक्षत्र: विवाह मिलान',
               intro='27 नक्षत्रों में {s} {n}वाँ नक्षत्र है; इसका स्वामी {lord} है। {s} नक्षत्र में जन्मे लोग {gana} गण, {yoni} योनि, {nadi} नाड़ी और {rajju} रज्जु के होते हैं।',
               brideH='कन्या का नक्षत्र {s} हो तो — सबसे अच्छे मिलान', groomH='वर का नक्षत्र {s} हो तो — सबसे अच्छे मिलान',
               colGroom='वर का नक्षत्र', colBride='कन्या का नक्षत्र', avoidH='ध्यान से देखें (रज्जु / वेध / नाड़ी दोष)', avoidNone='कोई नहीं',
               note='ये अंक हर नक्षत्र के मध्य चरण से निकाले गए हैं। राशि पर आधारित कूट चरण के अनुसार बदल सकते हैं — सटीक परिणाम के लिए दोनों का जन्म विवरण डालकर मिलान करें।',
               cta='मुफ़्त कुंडली मिलान करें →', allH='27 नक्षत्र',
               indexTitle='27 नक्षत्र — मिलान, स्वामी, गण, रज्जु | शुभ जातक', indexH1='27 नक्षत्र',
               indexLead='हर नक्षत्र का स्वामी, राशि, गण, योनि, नाड़ी, रज्जु — और विवाह के लिए सबसे अच्छे मिलान।',
               home='होम', lordL='नक्षत्र स्वामी', rasiL='राशि (चरण)', ganaL='गण', yoniL='योनि', nadiL='नाड़ी', rajjuL='रज्जु',
               menu='27 नक्षत्र'),
}

FONTS = ('https://fonts.googleapis.com/css2?family=Marcellus&family=Tiro+Tamil&family=Tiro+Telugu&family=Tiro+Kannada&family=Tiro+Devanagari+Hindi'
         '&family=Inter:wght@400;600;700&family=Noto+Sans+Tamil:wght@400;600;700&family=Noto+Sans+Malayalam:wght@400;600;700&family=Noto+Serif+Malayalam:wght@400'
         '&family=Noto+Sans+Telugu:wght@400;600;700&family=Noto+Sans+Kannada:wght@400;600;700&family=Noto+Sans+Devanagari:wght@400;600;700&display=swap')
CSP = ("default-src 'self'; script-src 'self' 'unsafe-inline' https://gc.zgo.at https://pagead2.googlesyndication.com https://*.googlesyndication.com https://*.google.com https://*.gstatic.com https://*.adtrafficquality.google; "
       "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src https://fonts.gstatic.com; img-src 'self' data: https:; "
       "connect-src 'self' https://*.goatcounter.com https://*.google.com https://*.googlesyndication.com https://*.doubleclick.net https://*.adtrafficquality.google; "
       "frame-src https://*.doubleclick.net https://*.google.com https://*.googlesyndication.com https://*.adtrafficquality.google; object-src 'none'; base-uri 'self'; form-action 'self'; upgrade-insecure-requests")


def esc(x):
    return html.escape(str(x), quote=True)


def slug(name):
    return name.lower().replace(' ', '-')


def compute():
    js = r"""
global.Astronomy = require('./src/vendor/astronomy.browser.min.js');
const J = require('./src/engine.js');
const SPAN = 360 / 27;
function fake(s) {
  const pos = s * SPAN + SPAN / 2, rasi = Math.floor(pos / 30), deg = pos - rasi * 30;
  const pada = Math.floor((pos - s * SPAN) / (SPAN / 4)) + 1;
  return { nakshatra: s, pada, rasi, planets: [{ name: 'Moon', deg, sign: rasi }] };
}
const out = { pairs: [], facts: [] };
for (let s = 0; s < 27; s++) {
  const padas = [];
  for (let p = 0; p < 4; p++) { const pos = s * SPAN + p * SPAN / 4 + 0.1; padas.push(Math.floor(pos / 30)); }
  out.facts.push({ gana: J.GANA[s], yoni: J.YONI[s][0], rajju: J.RAJJU[s], nadi: J.NADI[s], lord: ['Ketu','Venus','Sun','Moon','Mars','Rahu','Jupiter','Saturn','Mercury'][s % 9], padas });
}
for (let g = 0; g < 27; g++) for (let b = 0; b < 27; b++) {
  const G = fake(g), B = fake(b), pr = J.porutham(G, B), ak = J.ashtakoota(G, B);
  const r = k => (pr.items.find(i => i.key === k) || {}).result;
  out.pairs.push([g, b, pr.score, ak.score, r('rajju') === 'good', r('vedhai') === 'good', ak.nadiDosha]);
}
process.stdout.write(JSON.stringify(out));
"""
    return json.loads(subprocess.run(['node', '-'], input=js, capture_output=True, text=True, check=True).stdout)


def shell(l, title, desc, canon, alts, body, crumbs, app_href):
    D = S[l]
    langs = ''.join(f'<a href="{href}" hreflang="{x}" lang="{x}"{" class=on" if x == l else ""}>{NATIVE[x]}</a>' for x, href in alts)
    alt_links = ''.join(f'<link rel="alternate" hreflang="{x}" href="{SITE}{href}">\n' for x, href in alts) + f'<link rel="alternate" hreflang="x-default" href="{SITE}{alts[0][1]}">\n'
    crumb_html = ' › '.join(f'<a href="{h}">{esc(t)}</a>' if h else esc(t) for t, h in crumbs)
    ld = {'@context': 'https://schema.org', '@type': 'BreadcrumbList', 'itemListElement': [
        {'@type': 'ListItem', 'position': i + 1, 'name': t, **({'item': SITE + h} if h else {})} for i, (t, h) in enumerate(crumbs)]}
    return f'''<!doctype html>
<html lang="{l}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<meta name="theme-color" content="#6e1216">
<meta http-equiv="Content-Security-Policy" content="{CSP}">
<meta name="referrer" content="strict-origin-when-cross-origin">
<link rel="canonical" href="{SITE}{canon}">
{alt_links}<meta property="og:site_name" content="Suba Jathagam">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{SITE}{canon}">
<meta property="og:image" content="{SITE}/icons/og-image.jpg">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" type="image/png" sizes="32x32" href="/icons/favicon-32.png">
<link rel="apple-touch-icon" href="/icons/apple-touch-icon.png">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="{FONTS}" rel="stylesheet">
<link rel="stylesheet" href="/assets/kb.css">
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>
<!--ADS-->
</head>
<body class="{'indic' if l != 'en' else 'en'}">
<header><div class="wrap bar">
  <a class="brand" href="{'/' if l == 'en' else '/' + l + '/'}"><img src="/icons/icon-192.png" alt="" width="34" height="34"><b>{BRAND[l]}</b></a>
  <a class="btn" href="{app_href}">{esc(D['ctaShort'])}</a>
</div></header>
<main class="wrap">
<nav class="crumbs">{crumb_html}</nav>
{body}
<nav class="langs" aria-label="Language">{langs}</nav>
</main>
<footer><div class="wrap"><a href="{'/' if l == 'en' else '/' + l + '/'}">{BRAND[l]}</a> · <a href="/guide.html">Guide</a> · <a href="/privacy.html">Privacy</a> · <a href="/terms.html">Terms</a></div></footer>
<script>
(function(){{var app=false;try{{app=sessionStorage.getItem('jothidam.app')==='1';}}catch(e){{}}
if(!app&&/^https?:$/.test(location.protocol)&&location.hostname!=='localhost'){{var s=document.createElement('script');s.async=true;s.src='https://gc.zgo.at/count.js';s.setAttribute('data-goatcounter','https://subajathagam.goatcounter.com/count');document.head.appendChild(s);}}}})();
</script>
</body>
</html>
'''


def generate(I, ads_head=''):
    data = compute()
    facts, pairs = data['facts'], data['pairs']
    by = {(g, b): (ps, gs, rj, vd, nd) for g, b, ps, gs, rj, vd, nd in pairs}
    names_en = I['en']['naks']
    urls = []
    for l in LANGS:
        D, L = S[l], I[l]
        base = '/' if l == 'en' else f'/{l}/'
        app_href = base + '#match'
        os.makedirs(f'{base.strip("/") + "/" if l != "en" else ""}nakshatra', exist_ok=True)

        def fmt(s, x):
            return D[s].format(**x)

        def span(f):
            out, cur = [], None
            for p, r in enumerate(f['padas'], 1):
                if cur and cur[0] == r:
                    cur[2] = p
                else:
                    cur = [r, p, p]; out.append(cur)
            return ', '.join(f"{L['rasis'][r]} {a}{'–' + str(b) if b != a else ''}" for r, a, b in out)

        def star_vars(s):
            f = facts[s]
            return dict(s=L['naks'][s], n=s + 1, lord=L['pl'][f['lord']], gana=L['gana'][f['gana']], yoni=L['yoniN'][f['yoni']],
                        nadi=L['nadiN'][f['nadi']], rajju=L['rajjuN'][f['rajju']])

        def table(rows, col):
            head = f'<tr><th>{esc(col)}</th><th>{esc(L["poruthamTab"])}</th><th>{esc(L["gunaTab"])}</th><th>{esc(D["rajjuL"])}</th></tr>'
            body = ''.join(f'<tr><td><a href="{base}nakshatra/{slug(names_en[o])}.html">{esc(L["naks"][o])}</a></td><td>{ps}/10</td><td>{gs:g}/36</td><td>{"✓" if rj else "✗"}</td></tr>' for o, ps, gs, rj in rows)
            return f'<div class="tw"><table>{head}{body}</table></div>'

        chips = lambda cur: ''.join(f'<a href="{base}nakshatra/{slug(names_en[o])}.html"{" class=on" if o == cur else ""}>{esc(L["naks"][o])}</a>' for o in range(27))
        for s in range(27):
            v = star_vars(s)
            f = facts[s]
            facts_rows = [(D['lordL'], v['lord']), (D['rasiL'], span(f)), (D['ganaL'], v['gana']), (D['yoniL'], v['yoni']), (D['nadiL'], v['nadi']), (D['rajjuL'], v['rajju'])]
            # bride is this star: rank grooms; groom is this star: rank brides
            def best(fixed_girl):
                rows = []
                for o in range(27):
                    ps, gs, rj, vd, nd = by[(s, o)] if fixed_girl else by[(o, s)]
                    if rj and vd and not nd:
                        rows.append((o, ps, gs, rj))
                rows.sort(key=lambda r: (-r[1], -r[2]))
                return rows[:10]
            avoid = sorted({o for o in range(27) for k in [(s, o), (o, s)] if not by[k][2] or not by[k][3] or by[k][4]})
            body = f'''<h1>{esc(fmt('h1', v))}</h1>
<p class="lead">{esc(fmt('intro', v))}</p>
<div class="tw"><table class="facts">{''.join(f'<tr><th>{esc(a)}</th><td>{esc(b)}</td></tr>' for a, b in facts_rows)}</table></div>
<h2>{esc(fmt('brideH', v))}</h2>
{table(best(True), D['colGroom'])}
<h2>{esc(fmt('groomH', v))}</h2>
{table(best(False), D['colBride'])}
<h2>{esc(D['avoidH'])}</h2>
<p class="chips">{''.join(f'<a href="{base}nakshatra/{slug(names_en[o])}.html">{esc(L["naks"][o])}</a>' for o in avoid) or esc(D['avoidNone'])}</p>
<p class="note">{esc(D['note'])}</p>
<p><a class="btn big" href="{app_href}">{esc(D['cta'])}</a></p>
<!--AD-->
<h2>{esc(D['allH'])}</h2>
<p class="chips">{chips(s)}</p>'''
            canon = f'{base}nakshatra/{slug(names_en[s])}.html'
            alts = [(x, ('/' if x == 'en' else f'/{x}/') + f'nakshatra/{slug(names_en[s])}.html') for x in LANGS]
            crumbs = [(D['home'], base), (D['menu'], f'{base}nakshatra/'), (v['s'], None)]
            page = shell(l, fmt('title', v), fmt('desc', v), canon, alts, body, crumbs, app_href)
            open(canon.lstrip('/'), 'w').write(page.replace('<!--ADS-->', ads_head))
            urls.append((canon, alts))
        # index
        rows = ''.join(f'<tr><td>{s + 1}</td><td><a href="{base}nakshatra/{slug(names_en[s])}.html">{esc(L["naks"][s])}</a></td><td>{esc(L["pl"][facts[s]["lord"]])}</td><td>{esc(span(facts[s]))}</td><td>{esc(L["gana"][facts[s]["gana"]])}</td><td>{esc(L["nadiN"][facts[s]["nadi"]])}</td></tr>' for s in range(27))
        body = f'''<h1>{esc(D['indexH1'])}</h1>
<p class="lead">{esc(D['indexLead'])}</p>
<div class="tw"><table><tr><th>#</th><th>{esc(L['star'])}</th><th>{esc(D['lordL'])}</th><th>{esc(D['rasiL'])}</th><th>{esc(D['ganaL'])}</th><th>{esc(D['nadiL'])}</th></tr>{rows}</table></div>
<p><a class="btn big" href="{app_href}">{esc(D['cta'])}</a></p>
<!--AD-->'''
        canon = f'{base}nakshatra/'
        alts = [(x, ('/' if x == 'en' else f'/{x}/') + 'nakshatra/') for x in LANGS]
        page = shell(l, D['indexTitle'], D['indexLead'], canon, alts, body, [(D['home'], base), (D['menu'], None)], app_href)
        open(canon.lstrip('/') + 'index.html', 'w').write(page.replace('<!--ADS-->', ads_head))
        urls.append((canon, alts))
    return urls
