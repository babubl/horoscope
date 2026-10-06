"""Knowledge pages beyond the nakshatras: festival calendar (+ .ics reminders), daily panchangam per city,
baby-name syllables (namakshara), 12 rasi pages and 'How we calculate'. Called from src/build.py."""
import datetime
import html
import json
import os
import subprocess

from indic_transliteration import sanscript as SC

import nakshatra as NK
from kb_data import EVENT_NAMES, MONTHLY, GMONTHS, NAMA_HK, NAMA_LATIN, NAMA_TA, ELEMENT, QUALITY, ELEMENT_N, QUALITY_N

SITE = NK.SITE
LANGS = NK.LANGS
SCRIPT = {'hi': SC.DEVANAGARI, 'te': SC.TELUGU, 'kn': SC.KANNADA, 'ml': SC.MALAYALAM}
HOME = {  # calendar city per language (same as the app's panchangam home town)
    'en': ('Chennai', 13.0878, 80.2785), 'ta': ('Chennai', 13.0878, 80.2785), 'ml': ('Kochi', 9.9399, 76.2602),
    'te': ('Hyderabad', 17.384, 78.4564), 'kn': ('Bengaluru', 12.9719, 77.5937), 'hi': ('New Delhi', 28.6139, 77.209)}
TRAD = {'en': 'ta', 'ta': 'ta', 'ml': 'ml', 'te': 'te', 'kn': 'kn', 'hi': 'hi'}
YEARS = [2026, 2027]
CITIES = ['Chennai', 'Madurai', 'Coimbatore', 'Tiruchirappalli', 'Salem', 'Tirunelveli', 'Bengaluru', 'Mysuru', 'Mangaluru', 'Hyderabad',
          'Visakhapatnam', 'Vijayawada', 'Tirupati', 'Kochi', 'Thiruvananthapuram', 'Kozhikode', 'Mumbai', 'Pune', 'New Delhi', 'Kolkata',
          'Ahmedabad', 'Jaipur', 'Lucknow', 'Varanasi']

T = {
    'en': dict(
        calTitle='Hindu Calendar {y} — Ekadashi, Pradosham, Amavasya, Pournami & Festival Dates | Suba Jathagam',
        calH1='Festival & vrat calendar {y}',
        calLead='Every Ekadashi, Pradosham, Amavasya, Pournami, Sankashti Chaturthi and festival in {y}, calculated for {city} from the actual sunrise, sunset and moonrise. Dates can move by a day in other places.',
        calIdxTitle='Hindu Festival Calendar 2026 & 2027 | Suba Jathagam', calIdxH1='Festival & vrat calendar',
        calIdxLead='Year-by-year dates of Ekadashi, Pradosham, Amavasya, Pournami and major festivals, calculated with our own panchangam engine.',
        ics='📅 Add all to my calendar (.ics)', icsHint='Open the file on your phone or import it into Google Calendar — each day gets a reminder the evening before.',
        cDate='Date', cDay='Day', cEvent='Festival / vrat', cTime='Tithi / star timing', festivals='Festivals', monthly='Monthly vrats',
        rule='Rules: Ekadashi, Amavasya and Pournami — the tithi at sunrise; Pradosham — Trayodashi at sunset; Sankashti and Karva Chauth — at moonrise; Shivaratri and Janmashtami — at midnight. Vaishnava Ekadashi and some temple calendars can differ by a day.',
        pTitle='{city} Panchangam Today — Rahu Kalam, Tithi, Nakshatra | Suba Jathagam', pH1='{city} panchangam today',
        pLead='Tithi, nakshatra, yoga, karana, sunrise and today’s Rahu kalam, Yamagandam and Kuligai for {city}. Updates automatically every day.',
        pWeek='Rahu kalam this week', pIdxTitle='Panchangam Today — Rahu Kalam for Your City | Suba Jathagam', pIdxH1='Panchangam today, by city',
        pIdxLead='Pick your city for today’s tithi, nakshatra and Rahu kalam. For any other town, use the panchangam in the app.',
        pOther='Other cities', pApp='Any town, any date →',
        bTitle='Baby Names by Nakshatra — Namakshara Starting Letters for All 27 Stars | Suba Jathagam', bH1='Baby names by nakshatra (namakshara)',
        bLead='Tradition suggests starting a baby’s name with the syllable of the birth nakshatra’s pada. Find your baby’s star and pada with the free horoscope, then pick a name starting with the syllable below.',
        bStar='Nakshatra', bPada='Pada {n}', bFind='Find the baby’s star and pada →',
        rTitle='{r} Rasi ({en}) — Lord, Nakshatras, Marriage Match & Transits | Suba Jathagam', rH1='{r} rasi',
        rLead='{r} ({en}) is rasi number {n} of 12, ruled by {lord}. It is a {el} sign of the {q} kind.',
        rLord='Lord', rEl='Element', rQ='Nature', rNaks='Nakshatras (pada)', rMatch='Good rasis for marriage (bride is {r})', rMatchNote='Rasi porutham and Bhakoot both favourable; always match the full charts.',
        rTransit='Saturn and Jupiter now ({d})', rSat='Saturn is in {s} — house {h} from {r}', rJup='Jupiter is in {s} — house {h} from {r}',
        rIdxTitle='12 Rasis — Lords, Nakshatras, Marriage Match & Transits | Suba Jathagam', rIdxH1='The 12 rasis', rIdxLead='Lord, element, nakshatras and marriage matches of every rasi, with this month’s Saturn and Jupiter transits.',
        hTitle='How Suba Jathagam Calculates Your Horoscope — Method & Accuracy', hH1='How we calculate',
        menu=['Festival calendar', 'Panchangam today', '27 Nakshatras', '12 Rasis', 'Baby names', 'How we calculate']),
    'ta': dict(
        calTitle='{y} விரத நாட்கள், பண்டிகைகள் — ஏகாதசி, பிரதோஷம், அமாவாசை, பௌர்ணமி | சுப ஜாதகம்',
        calH1='{y} விரதம் & பண்டிகை நாட்காட்டி',
        calLead='{y}-ல் வரும் அனைத்து ஏகாதசி, பிரதோஷம், அமாவாசை, பௌர்ணமி, சங்கடஹர சதுர்த்தி, பண்டிகைகள் — {city} நகரின் உண்மையான சூரிய உதயம், அஸ்தமனம், சந்திர உதயம் கொண்டு கணிக்கப்பட்டவை. மற்ற ஊர்களில் ஒரு நாள் மாறலாம்.',
        calIdxTitle='பண்டிகை நாட்காட்டி 2026, 2027 | சுப ஜாதகம்', calIdxH1='விரதம் & பண்டிகை நாட்காட்டி',
        calIdxLead='ஏகாதசி, பிரதோஷம், அமாவாசை, பௌர்ணமி, முக்கியப் பண்டிகைகள் — எங்கள் சொந்த பஞ்சாங்கக் கணிதத்தில்.',
        ics='📅 எல்லாவற்றையும் என் நாட்காட்டியில் சேர் (.ics)', icsHint='கைப்பேசியில் திறக்கவும் அல்லது Google Calendar-ல் import செய்யவும் — ஒவ்வொரு நாளுக்கும் முந்தைய மாலை நினைவூட்டல் வரும்.',
        cDate='தேதி', cDay='கிழமை', cEvent='பண்டிகை / விரதம்', cTime='திதி / நட்சத்திர நேரம்', festivals='பண்டிகைகள்', monthly='மாத விரதங்கள்',
        rule='விதிகள்: ஏகாதசி, அமாவாசை, பௌர்ணமி — சூரிய உதயத்தில் உள்ள திதி; பிரதோஷம் — மாலையில் திரயோதசி; சங்கடஹர சதுர்த்தி — சந்திர உதயத்தில்; சிவராத்திரி, கோகுலாஷ்டமி — நள்ளிரவில். வைணவ ஏகாதசி, கோயில் பஞ்சாங்கங்களில் ஒரு நாள் வேறுபடலாம்.',
        pTitle='இன்றைய பஞ்சாங்கம் {city} — ராகு காலம், திதி, நட்சத்திரம் | சுப ஜாதகம்', pH1='இன்றைய பஞ்சாங்கம் — {city}',
        pLead='{city} நகருக்கு இன்றைய திதி, நட்சத்திரம், யோகம், கரணம், சூரிய உதயம், ராகு காலம், எமகண்டம், குளிகை. தினமும் தானாக மாறும்.',
        pWeek='இந்த வார ராகு காலம்', pIdxTitle='இன்றைய பஞ்சாங்கம் — உங்கள் ஊரின் ராகு காலம் | சுப ஜாதகம்', pIdxH1='இன்றைய பஞ்சாங்கம் — ஊர் வாரியாக',
        pIdxLead='உங்கள் ஊரைத் தேர்ந்தெடுத்து இன்றைய திதி, நட்சத்திரம், ராகு காலம் பாருங்கள். மற்ற ஊர்களுக்கு செயலியில் உள்ள பஞ்சாங்கத்தைப் பயன்படுத்துங்கள்.',
        pOther='மற்ற ஊர்கள்', pApp='எந்த ஊர், எந்த தேதி →',
        bTitle='நட்சத்திரப்படி குழந்தை பெயர் — 27 நட்சத்திரங்களின் பெயர் எழுத்துகள் | சுப ஜாதகம்', bH1='நட்சத்திரப்படி குழந்தை பெயர் எழுத்துகள்',
        bLead='பிறந்த நட்சத்திரத்தின் பாதத்துக்குரிய எழுத்தில் பெயர் தொடங்குவது மரபு. இலவச ஜாதகத்தில் குழந்தையின் நட்சத்திரம், பாதம் அறிந்து, கீழே உள்ள எழுத்தில் தொடங்கும் பெயரைத் தேர்ந்தெடுக்கலாம்.',
        bStar='நட்சத்திரம்', bPada='{n}-ம் பாதம்', bFind='குழந்தையின் நட்சத்திரம், பாதம் அறிய →',
        rTitle='{r} ராசி — அதிபதி, நட்சத்திரங்கள், திருமணப் பொருத்தம், கோசாரம் | சுப ஜாதகம்', rH1='{r} ராசி',
        rLead='12 ராசிகளில் {r} {n}-வது ராசி; இதன் அதிபதி {lord}. இது {el} தத்துவம் கொண்ட {q} ராசி.',
        rLord='அதிபதி', rEl='தத்துவம்', rQ='தன்மை', rNaks='நட்சத்திரங்கள் (பாதம்)', rMatch='திருமணத்துக்குப் பொருந்தும் ராசிகள் (பெண் {r} ராசி)', rMatchNote='ராசிப் பொருத்தமும் பகூடமும் சாதகமானவை; முழு ஜாதகத்துடன் பொருத்தம் பார்க்கவும்.',
        rTransit='சனி, குரு சஞ்சாரம் ({d})', rSat='சனி {s} ராசியில் — {r} ராசிக்கு {h}-ம் இடம்', rJup='குரு {s} ராசியில் — {r} ராசிக்கு {h}-ம் இடம்',
        rIdxTitle='12 ராசிகள் — அதிபதி, நட்சத்திரம், பொருத்தம், கோசாரம் | சுப ஜாதகம்', rIdxH1='12 ராசிகள்', rIdxLead='ஒவ்வொரு ராசியின் அதிபதி, தத்துவம், நட்சத்திரங்கள், திருமணப் பொருத்தம், இந்த மாத சனி–குரு சஞ்சாரம்.',
        hTitle='சுப ஜாதகம் ஜாதகத்தை எப்படிக் கணிக்கிறது — முறை, துல்லியம்', hH1='நாங்கள் எப்படிக் கணிக்கிறோம்',
        menu=['பண்டிகை நாட்காட்டி', 'இன்றைய பஞ்சாங்கம்', '27 நட்சத்திரங்கள்', '12 ராசிகள்', 'குழந்தை பெயர் எழுத்து', 'கணிப்பு முறை']),
    'ml': dict(
        calTitle='{y} വ്രതദിനങ്ങൾ, ആഘോഷങ്ങൾ — ഏകാദശി, പ്രദോഷം, വാവ് | ശുഭ ജാതകം',
        calH1='{y} വ്രത–ആഘോഷ കലണ്ടർ',
        calLead='{y}-ലെ എല്ലാ ഏകാദശി, പ്രദോഷം, അമാവാസി, പൗർണ്ണമി, സങ്കഷ്ടി ചതുർത്ഥി, ആഘോഷങ്ങൾ — {city}-ലെ യഥാർത്ഥ സൂര്യോദയം, അസ്തമയം, ചന്ദ്രോദയം അടിസ്ഥാനമാക്കി. മറ്റ് സ്ഥലങ്ങളിൽ ഒരു ദിവസം മാറാം.',
        calIdxTitle='ആഘോഷ കലണ്ടർ 2026, 2027 | ശുഭ ജാതകം', calIdxH1='വ്രത–ആഘോഷ കലണ്ടർ',
        calIdxLead='ഏകാദശി, പ്രദോഷം, വാവ്, പ്രധാന ആഘോഷങ്ങൾ — ഞങ്ങളുടെ സ്വന്തം പഞ്ചാംഗ ഗണിതത്തിൽ.',
        ics='📅 എല്ലാം എന്റെ കലണ്ടറിൽ ചേർക്കുക (.ics)', icsHint='ഫോണിൽ തുറക്കുക അല്ലെങ്കിൽ Google Calendar-ൽ import ചെയ്യുക — ഓരോ ദിവസത്തിനും തലേന്ന് വൈകിട്ട് ഓർമ്മപ്പെടുത്തൽ.',
        cDate='തീയതി', cDay='ദിവസം', cEvent='ആഘോഷം / വ്രതം', cTime='തിഥി / നക്ഷത്ര സമയം', festivals='ആഘോഷങ്ങൾ', monthly='മാസവ്രതങ്ങൾ',
        rule='നിയമങ്ങൾ: ഏകാദശി, വാവ് — സൂര്യോദയത്തിലെ തിഥി; പ്രദോഷം — സന്ധ്യയിലെ ത്രയോദശി; സങ്കഷ്ടി — ചന്ദ്രോദയത്തിൽ; ശിവരാത്രി, അഷ്ടമിരോഹിണി — അർദ്ധരാത്രിയിൽ. ക്ഷേത്ര പഞ്ചാംഗങ്ങളിൽ ഒരു ദിവസം വ്യത്യാസം ഉണ്ടാകാം.',
        pTitle='ഇന്നത്തെ പഞ്ചാംഗം {city} — രാഹുകാലം, തിഥി, നക്ഷത്രം | ശുഭ ജാതകം', pH1='ഇന്നത്തെ പഞ്ചാംഗം — {city}',
        pLead='{city}-ന് ഇന്നത്തെ തിഥി, നക്ഷത്രം, യോഗം, കരണം, സൂര്യോദയം, രാഹുകാലം, യമകണ്ടം, ഗുളികകാലം. ദിവസവും സ്വയം പുതുക്കും.',
        pWeek='ഈ ആഴ്ചയിലെ രാഹുകാലം', pIdxTitle='ഇന്നത്തെ പഞ്ചാംഗം — നിങ്ങളുടെ നഗരത്തിലെ രാഹുകാലം | ശുഭ ജാതകം', pIdxH1='ഇന്നത്തെ പഞ്ചാംഗം — നഗരം തിരിച്ച്',
        pIdxLead='നിങ്ങളുടെ നഗരം തിരഞ്ഞെടുത്ത് ഇന്നത്തെ തിഥി, നക്ഷത്രം, രാഹുകാലം കാണുക. മറ്റു സ്ഥലങ്ങൾക്ക് ആപ്പിലെ പഞ്ചാംഗം ഉപയോഗിക്കുക.',
        pOther='മറ്റു നഗരങ്ങൾ', pApp='ഏതു സ്ഥലവും, ഏതു തീയതിയും →',
        bTitle='നക്ഷത്രപ്രകാരം കുഞ്ഞുങ്ങളുടെ പേര് — 27 നക്ഷത്രങ്ങളുടെ പേരക്ഷരങ്ങൾ | ശുഭ ജാതകം', bH1='നക്ഷത്രപ്രകാരം പേരക്ഷരങ്ങൾ',
        bLead='ജന്മനക്ഷത്രത്തിന്റെ പാദത്തിനുള്ള അക്ഷരത്തിൽ പേര് തുടങ്ങുന്നത് പാരമ്പര്യമാണ്. സൗജന്യ ജാതകത്തിൽ കുഞ്ഞിന്റെ നക്ഷത്രവും പാദവും അറിഞ്ഞ് താഴെയുള്ള അക്ഷരത്തിൽ തുടങ്ങുന്ന പേര് തിരഞ്ഞെടുക്കാം.',
        bStar='നക്ഷത്രം', bPada='{n}-ാം പാദം', bFind='കുഞ്ഞിന്റെ നക്ഷത്രം, പാദം അറിയാൻ →',
        rTitle='{r} രാശി — നാഥൻ, നക്ഷത്രങ്ങൾ, വിവാഹ പൊരുത്തം, ഗോചരം | ശുഭ ജാതകം', rH1='{r} രാശി',
        rLead='12 രാശികളിൽ {n}-ാമത്തേതാണ് {r}; നാഥൻ {lord}. {el} തത്ത്വമുള്ള {q} രാശി.',
        rLord='നാഥൻ', rEl='തത്ത്വം', rQ='സ്വഭാവം', rNaks='നക്ഷത്രങ്ങൾ (പാദം)', rMatch='വിവാഹത്തിന് ചേരുന്ന രാശികൾ (വധു {r})', rMatchNote='രാശിപ്പൊരുത്തവും ഭകൂടവും അനുകൂലം; മുഴുവൻ ജാതകവും ചേർത്ത് നോക്കുക.',
        rTransit='ശനി, വ്യാഴം ഇപ്പോൾ ({d})', rSat='ശനി {s} രാശിയിൽ — {r} രാശിക്ക് {h}-ാം ഭാവം', rJup='വ്യാഴം {s} രാശിയിൽ — {r} രാശിക്ക് {h}-ാം ഭാവം',
        rIdxTitle='12 രാശികൾ — നാഥൻ, നക്ഷത്രം, പൊരുത്തം, ഗോചരം | ശുഭ ജാതകം', rIdxH1='12 രാശികൾ', rIdxLead='ഓരോ രാശിയുടെയും നാഥൻ, തത്ത്വം, നക്ഷത്രങ്ങൾ, വിവാഹ പൊരുത്തം, ഈ മാസത്തെ ശനി–വ്യാഴ ഗോചരം.',
        hTitle='ശുഭ ജാതകം ജാതകം എങ്ങനെ കണക്കാക്കുന്നു — രീതി, കൃത്യത', hH1='ഞങ്ങൾ എങ്ങനെ കണക്കാക്കുന്നു',
        menu=['ആഘോഷ കലണ്ടർ', 'ഇന്നത്തെ പഞ്ചാംഗം', '27 നക്ഷത്രങ്ങൾ', '12 രാശികൾ', 'പേരക്ഷരം', 'കണക്കുകൂട്ടൽ രീതി']),
    'te': dict(
        calTitle='{y} పండుగలు, వ్రతాలు — ఏకాదశి, ప్రదోషం, అమావాస్య, పౌర్ణమి తేదీలు | శుభ జాతకం',
        calH1='{y} పండుగలు & వ్రతాల క్యాలెండర్',
        calLead='{y}లో అన్ని ఏకాదశులు, ప్రదోషాలు, అమావాస్య, పౌర్ణమి, సంకష్టహర చతుర్థి, పండుగలు — {city} నగరంలో నిజమైన సూర్యోదయం, సూర్యాస్తమయం, చంద్రోదయం ఆధారంగా. ఇతర ఊళ్లలో ఒక రోజు మారవచ్చు.',
        calIdxTitle='పండుగల క్యాలెండర్ 2026, 2027 | శుభ జాతకం', calIdxH1='పండుగలు & వ్రతాల క్యాలెండర్',
        calIdxLead='ఏకాదశి, ప్రదోషం, అమావాస్య, పౌర్ణమి, ప్రధాన పండుగలు — మా స్వంత పంచాంగ గణితంతో.',
        ics='📅 అన్నీ నా క్యాలెండర్‌లో చేర్చు (.ics)', icsHint='ఫోన్‌లో తెరవండి లేదా Google Calendar‌లో import చేయండి — ప్రతి రోజుకి ముందు సాయంత్రం గుర్తుచేస్తుంది.',
        cDate='తేదీ', cDay='వారం', cEvent='పండుగ / వ్రతం', cTime='తిథి / నక్షత్ర సమయం', festivals='పండుగలు', monthly='మాసవారీ వ్రతాలు',
        rule='నియమాలు: ఏకాదశి, అమావాస్య, పౌర్ణమి — సూర్యోదయ తిథి; ప్రదోషం — సాయంత్రం త్రయోదశి; సంకష్టహర చతుర్థి — చంద్రోదయంలో; శివరాత్రి, జన్మాష్టమి — అర్ధరాత్రి. వైష్ణవ ఏకాదశి, ఆలయ పంచాంగాల్లో ఒక రోజు తేడా ఉండవచ్చు.',
        pTitle='నేటి పంచాంగం {city} — రాహుకాలం, తిథి, నక్షత్రం | శుభ జాతకం', pH1='నేటి పంచాంగం — {city}',
        pLead='{city}కి నేటి తిథి, నక్షత్రం, యోగం, కరణం, సూర్యోదయం, రాహుకాలం, యమగండం, గుళిక. ప్రతి రోజు స్వయంగా మారుతుంది.',
        pWeek='ఈ వారం రాహుకాలం', pIdxTitle='నేటి పంచాంగం — మీ నగర రాహుకాలం | శుభ జాతకం', pIdxH1='నేటి పంచాంగం — నగరాల వారీగా',
        pIdxLead='మీ నగరం ఎంచుకుని నేటి తిథి, నక్షత్రం, రాహుకాలం చూడండి. ఇతర ఊళ్లకు యాప్‌లోని పంచాంగం వాడండి.',
        pOther='ఇతర నగరాలు', pApp='ఏ ఊరైనా, ఏ తేదీ అయినా →',
        bTitle='నక్షత్రం ప్రకారం పిల్లల పేర్లు — 27 నక్షత్రాల నామాక్షరాలు | శుభ జాతకం', bH1='నక్షత్రం ప్రకారం పిల్లల పేర్ల అక్షరాలు',
        bLead='జన్మ నక్షత్ర పాదానికి సంబంధించిన అక్షరంతో పేరు మొదలుపెట్టడం సంప్రదాయం. ఉచిత జాతకంలో బిడ్డ నక్షత్రం, పాదం తెలుసుకుని, క్రింది అక్షరంతో మొదలయ్యే పేరు ఎంచుకోండి.',
        bStar='నక్షత్రం', bPada='{n}వ పాదం', bFind='బిడ్డ నక్షత్రం, పాదం తెలుసుకోండి →',
        rTitle='{r} రాశి — అధిపతి, నక్షత్రాలు, వివాహ పొంతన, గోచారం | శుభ జాతకం', rH1='{r} రాశి',
        rLead='12 రాశుల్లో {r} {n}వ రాశి; అధిపతి {lord}. ఇది {el} తత్త్వం గల {q} రాశి.',
        rLord='అధిపతి', rEl='తత్త్వం', rQ='స్వభావం', rNaks='నక్షత్రాలు (పాదం)', rMatch='వివాహానికి సరిపోయే రాశులు (వధువు {r})', rMatchNote='రాశి పొంతన, భకూటం రెండూ అనుకూలం; పూర్తి జాతకాలతో పొంతన చూడండి.',
        rTransit='శని, గురు గోచారం ఇప్పుడు ({d})', rSat='శని {s} రాశిలో — {r} నుండి {h}వ స్థానం', rJup='గురువు {s} రాశిలో — {r} నుండి {h}వ స్థానం',
        rIdxTitle='12 రాశులు — అధిపతి, నక్షత్రాలు, పొంతన, గోచారం | శుభ జాతకం', rIdxH1='12 రాశులు', rIdxLead='ప్రతి రాశి అధిపతి, తత్త్వం, నక్షత్రాలు, వివాహ పొంతన, ఈ నెల శని–గురు గోచారం.',
        hTitle='శుభ జాతకం జాతకాన్ని ఎలా లెక్కిస్తుంది — విధానం, ఖచ్చితత్వం', hH1='మేము ఎలా లెక్కిస్తాము',
        menu=['పండుగల క్యాలెండర్', 'నేటి పంచాంగం', '27 నక్షత్రాలు', '12 రాశులు', 'పిల్లల పేర్ల అక్షరాలు', 'లెక్కింపు విధానం']),
    'kn': dict(
        calTitle='{y} ಹಬ್ಬಗಳು, ವ್ರತಗಳು — ಏಕಾದಶಿ, ಪ್ರದೋಷ, ಅಮಾವಾಸ್ಯೆ, ಹುಣ್ಣಿಮೆ ದಿನಾಂಕಗಳು | ಶುಭ ಜಾತಕ',
        calH1='{y} ಹಬ್ಬ & ವ್ರತಗಳ ಕ್ಯಾಲೆಂಡರ್',
        calLead='{y}ರ ಎಲ್ಲ ಏಕಾದಶಿ, ಪ್ರದೋಷ, ಅಮಾವಾಸ್ಯೆ, ಹುಣ್ಣಿಮೆ, ಸಂಕಷ್ಟಹರ ಚತುರ್ಥಿ, ಹಬ್ಬಗಳು — {city}ನ ನಿಜವಾದ ಸೂರ್ಯೋದಯ, ಸೂರ್ಯಾಸ್ತ, ಚಂದ್ರೋದಯ ಆಧರಿಸಿ. ಇತರ ಊರುಗಳಲ್ಲಿ ಒಂದು ದಿನ ಬದಲಾಗಬಹುದು.',
        calIdxTitle='ಹಬ್ಬಗಳ ಕ್ಯಾಲೆಂಡರ್ 2026, 2027 | ಶುಭ ಜಾತಕ', calIdxH1='ಹಬ್ಬ & ವ್ರತಗಳ ಕ್ಯಾಲೆಂಡರ್',
        calIdxLead='ಏಕಾದಶಿ, ಪ್ರದೋಷ, ಅಮಾವಾಸ್ಯೆ, ಹುಣ್ಣಿಮೆ, ಪ್ರಮುಖ ಹಬ್ಬಗಳು — ನಮ್ಮದೇ ಪಂಚಾಂಗ ಗಣಿತದಿಂದ.',
        ics='📅 ಎಲ್ಲವನ್ನೂ ನನ್ನ ಕ್ಯಾಲೆಂಡರ್‌ಗೆ ಸೇರಿಸಿ (.ics)', icsHint='ಫೋನ್‌ನಲ್ಲಿ ತೆರೆಯಿರಿ ಅಥವಾ Google Calendar‌ಗೆ import ಮಾಡಿ — ಪ್ರತಿ ದಿನದ ಹಿಂದಿನ ಸಂಜೆ ನೆನಪಿಸುತ್ತದೆ.',
        cDate='ದಿನಾಂಕ', cDay='ವಾರ', cEvent='ಹಬ್ಬ / ವ್ರತ', cTime='ತಿಥಿ / ನಕ್ಷತ್ರ ಸಮಯ', festivals='ಹಬ್ಬಗಳು', monthly='ಮಾಸಿಕ ವ್ರತಗಳು',
        rule='ನಿಯಮಗಳು: ಏಕಾದಶಿ, ಅಮಾವಾಸ್ಯೆ, ಹುಣ್ಣಿಮೆ — ಸೂರ್ಯೋದಯದ ತಿಥಿ; ಪ್ರದೋಷ — ಸಂಜೆಯ ತ್ರಯೋದಶಿ; ಸಂಕಷ್ಟಹರ ಚತುರ್ಥಿ — ಚಂದ್ರೋದಯದಲ್ಲಿ; ಶಿವರಾತ್ರಿ, ಜನ್ಮಾಷ್ಟಮಿ — ಮಧ್ಯರಾತ್ರಿ. ವೈಷ್ಣವ ಏಕಾದಶಿ, ದೇವಾಲಯ ಪಂಚಾಂಗಗಳಲ್ಲಿ ಒಂದು ದಿನ ವ್ಯತ್ಯಾಸ ಇರಬಹುದು.',
        pTitle='ಇಂದಿನ ಪಂಚಾಂಗ {city} — ರಾಹುಕಾಲ, ತಿಥಿ, ನಕ್ಷತ್ರ | ಶುಭ ಜಾತಕ', pH1='ಇಂದಿನ ಪಂಚಾಂಗ — {city}',
        pLead='{city}ಗೆ ಇಂದಿನ ತಿಥಿ, ನಕ್ಷತ್ರ, ಯೋಗ, ಕರಣ, ಸೂರ್ಯೋದಯ, ರಾಹುಕಾಲ, ಯಮಗಂಡ, ಗುಳಿಕ. ಪ್ರತಿದಿನ ತಾನಾಗಿ ಬದಲಾಗುತ್ತದೆ.',
        pWeek='ಈ ವಾರದ ರಾಹುಕಾಲ', pIdxTitle='ಇಂದಿನ ಪಂಚಾಂಗ — ನಿಮ್ಮ ನಗರದ ರಾಹುಕಾಲ | ಶುಭ ಜಾತಕ', pIdxH1='ಇಂದಿನ ಪಂಚಾಂಗ — ನಗರವಾರು',
        pIdxLead='ನಿಮ್ಮ ನಗರ ಆರಿಸಿ ಇಂದಿನ ತಿಥಿ, ನಕ್ಷತ್ರ, ರಾಹುಕಾಲ ನೋಡಿ. ಇತರ ಊರುಗಳಿಗೆ ಆ್ಯಪ್‌ನ ಪಂಚಾಂಗ ಬಳಸಿ.',
        pOther='ಇತರ ನಗರಗಳು', pApp='ಯಾವುದೇ ಊರು, ಯಾವುದೇ ದಿನಾಂಕ →',
        bTitle='ನಕ್ಷತ್ರದ ಪ್ರಕಾರ ಮಗುವಿನ ಹೆಸರು — 27 ನಕ್ಷತ್ರಗಳ ನಾಮಾಕ್ಷರ | ಶುಭ ಜಾತಕ', bH1='ನಕ್ಷತ್ರದ ಪ್ರಕಾರ ಹೆಸರಿನ ಅಕ್ಷರಗಳು',
        bLead='ಜನ್ಮ ನಕ್ಷತ್ರದ ಪಾದದ ಅಕ್ಷರದಿಂದ ಹೆಸರು ಆರಂಭಿಸುವುದು ಸಂಪ್ರದಾಯ. ಉಚಿತ ಜಾತಕದಲ್ಲಿ ಮಗುವಿನ ನಕ್ಷತ್ರ, ಪಾದ ತಿಳಿದು ಕೆಳಗಿನ ಅಕ್ಷರದಿಂದ ಆರಂಭವಾಗುವ ಹೆಸರು ಆರಿಸಿ.',
        bStar='ನಕ್ಷತ್ರ', bPada='{n}ನೇ ಪಾದ', bFind='ಮಗುವಿನ ನಕ್ಷತ್ರ, ಪಾದ ತಿಳಿಯಿರಿ →',
        rTitle='{r} ರಾಶಿ — ಅಧಿಪತಿ, ನಕ್ಷತ್ರಗಳು, ಮದುವೆ ಹೊಂದಾಣಿಕೆ, ಗೋಚಾರ | ಶುಭ ಜಾತಕ', rH1='{r} ರಾಶಿ',
        rLead='12 ರಾಶಿಗಳಲ್ಲಿ {r} {n}ನೇ ರಾಶಿ; ಅಧಿಪತಿ {lord}. ಇದು {el} ತತ್ತ್ವದ {q} ರಾಶಿ.',
        rLord='ಅಧಿಪತಿ', rEl='ತತ್ತ್ವ', rQ='ಸ್ವಭಾವ', rNaks='ನಕ್ಷತ್ರಗಳು (ಪಾದ)', rMatch='ಮದುವೆಗೆ ಹೊಂದುವ ರಾಶಿಗಳು (ವಧು {r})', rMatchNote='ರಾಶಿ ಹೊಂದಾಣಿಕೆ ಮತ್ತು ಭಕೂಟ ಎರಡೂ ಅನುಕೂಲ; ಪೂರ್ಣ ಜಾತಕಗಳೊಂದಿಗೆ ನೋಡಿ.',
        rTransit='ಶನಿ, ಗುರು ಗೋಚಾರ ಈಗ ({d})', rSat='ಶನಿ {s} ರಾಶಿಯಲ್ಲಿ — {r}ನಿಂದ {h}ನೇ ಸ್ಥಾನ', rJup='ಗುರು {s} ರಾಶಿಯಲ್ಲಿ — {r}ನಿಂದ {h}ನೇ ಸ್ಥಾನ',
        rIdxTitle='12 ರಾಶಿಗಳು — ಅಧಿಪತಿ, ನಕ್ಷತ್ರ, ಹೊಂದಾಣಿಕೆ, ಗೋಚಾರ | ಶುಭ ಜಾತಕ', rIdxH1='12 ರಾಶಿಗಳು', rIdxLead='ಪ್ರತಿ ರಾಶಿಯ ಅಧಿಪತಿ, ತತ್ತ್ವ, ನಕ್ಷತ್ರಗಳು, ಮದುವೆ ಹೊಂದಾಣಿಕೆ, ಈ ತಿಂಗಳ ಶನಿ–ಗುರು ಗೋಚಾರ.',
        hTitle='ಶುಭ ಜಾತಕ ಜಾತಕವನ್ನು ಹೇಗೆ ಲೆಕ್ಕ ಹಾಕುತ್ತದೆ — ವಿಧಾನ, ನಿಖರತೆ', hH1='ನಾವು ಹೇಗೆ ಲೆಕ್ಕ ಹಾಕುತ್ತೇವೆ',
        menu=['ಹಬ್ಬಗಳ ಕ್ಯಾಲೆಂಡರ್', 'ಇಂದಿನ ಪಂಚಾಂಗ', '27 ನಕ್ಷತ್ರಗಳು', '12 ರಾಶಿಗಳು', 'ಮಗುವಿನ ಹೆಸರಿನ ಅಕ್ಷರ', 'ಲೆಕ್ಕಾಚಾರ ವಿಧಾನ']),
    'hi': dict(
        calTitle='{y} व्रत और त्योहार — एकादशी, प्रदोष, अमावस्या, पूर्णिमा की तिथियाँ | शुभ जातक',
        calH1='{y} व्रत–त्योहार कैलेंडर',
        calLead='{y} की सभी एकादशी, प्रदोष व्रत, अमावस्या, पूर्णिमा, संकष्टी चतुर्थी और त्योहार — {city} के वास्तविक सूर्योदय, सूर्यास्त और चंद्रोदय से गणना। अन्य शहरों में एक दिन का अंतर हो सकता है।',
        calIdxTitle='हिंदू त्योहार कैलेंडर 2026 और 2027 | शुभ जातक', calIdxH1='व्रत–त्योहार कैलेंडर',
        calIdxLead='एकादशी, प्रदोष, अमावस्या, पूर्णिमा और प्रमुख त्योहारों की तिथियाँ — हमारी अपनी पंचांग गणना से।',
        ics='📅 सब मेरे कैलेंडर में जोड़ें (.ics)', icsHint='फ़ोन पर खोलें या Google Calendar में import करें — हर तिथि से पहले की शाम याद दिलाया जाएगा।',
        cDate='तिथि', cDay='वार', cEvent='त्योहार / व्रत', cTime='तिथि / नक्षत्र समय', festivals='त्योहार', monthly='मासिक व्रत',
        rule='नियम: एकादशी, अमावस्या, पूर्णिमा — सूर्योदय की तिथि; प्रदोष — सूर्यास्त के समय त्रयोदशी; संकष्टी और करवा चौथ — चंद्रोदय पर; शिवरात्रि और जन्माष्टमी — मध्यरात्रि में। वैष्णव एकादशी और कुछ मंदिर पंचांगों में एक दिन का अंतर हो सकता है।',
        pTitle='आज का पंचांग {city} — राहु काल, तिथि, नक्षत्र | शुभ जातक', pH1='आज का पंचांग — {city}',
        pLead='{city} के लिए आज की तिथि, नक्षत्र, योग, करण, सूर्योदय, राहु काल, यमगंड और गुलिक काल। हर दिन अपने आप बदलता है।',
        pWeek='इस सप्ताह का राहु काल', pIdxTitle='आज का पंचांग — अपने शहर का राहु काल | शुभ जातक', pIdxH1='आज का पंचांग — शहर अनुसार',
        pIdxLead='अपना शहर चुनें और आज की तिथि, नक्षत्र, राहु काल देखें। अन्य स्थानों के लिए ऐप का पंचांग इस्तेमाल करें।',
        pOther='अन्य शहर', pApp='कोई भी शहर, कोई भी तिथि →',
        bTitle='नक्षत्र अनुसार बच्चों के नाम — 27 नक्षत्रों के नामाक्षर | शुभ जातक', bH1='नक्षत्र अनुसार नामाक्षर',
        bLead='जन्म नक्षत्र के चरण के अक्षर से नाम रखना परंपरा है। मुफ़्त कुंडली से बच्चे का नक्षत्र और चरण जानें, फिर नीचे दिए अक्षर से शुरू होने वाला नाम चुनें।',
        bStar='नक्षत्र', bPada='चरण {n}', bFind='बच्चे का नक्षत्र और चरण जानें →',
        rTitle='{r} राशि — स्वामी, नक्षत्र, विवाह मिलान और गोचर | शुभ जातक', rH1='{r} राशि',
        rLead='12 राशियों में {r} {n}वीं राशि है; इसका स्वामी {lord} है। यह {el} तत्व की {q} राशि है।',
        rLord='स्वामी', rEl='तत्व', rQ='स्वभाव', rNaks='नक्षत्र (चरण)', rMatch='विवाह के लिए अनुकूल राशियाँ (कन्या {r})', rMatchNote='राशि कूट और भकूट दोनों अनुकूल; पूरी कुंडली से मिलान अवश्य करें।',
        rTransit='शनि और गुरु का गोचर ({d})', rSat='शनि {s} राशि में — {r} से {h}वाँ भाव', rJup='गुरु {s} राशि में — {r} से {h}वाँ भाव',
        rIdxTitle='12 राशियाँ — स्वामी, नक्षत्र, मिलान, गोचर | शुभ जातक', rIdxH1='12 राशियाँ', rIdxLead='हर राशि का स्वामी, तत्व, नक्षत्र, विवाह मिलान और इस महीने का शनि–गुरु गोचर।',
        hTitle='शुभ जातक कुंडली की गणना कैसे करता है — पद्धति और सटीकता', hH1='हम गणना कैसे करते हैं',
        menu=['व्रत–त्योहार कैलेंडर', 'आज का पंचांग', '27 नक्षत्र', '12 राशियाँ', 'नामाक्षर', 'गणना पद्धति']),
}

HOW = {
    'en': [('A jathagam is calculated, not looked up', 'Every chart on Suba Jathagam is computed inside your phone or browser from the date, time and place of birth. Nothing is copied from another website, and your details are never sent to our server.'),
           ('1. Where the planets were', 'We work out the exact positions of the Sun, Moon and planets at the birth moment with astronomy-engine, an open-source astronomical library built on the same planetary models astronomers use (VSOP87 and modern lunar theory). Positions are corrected for nutation and converted to the sidereal zodiac with the Lahiri ayanamsa, the standard adopted by the Government of India.'),
           ('2. Turning the sky into a jathagam', 'Our own code then finds the Lagna from local sidereal time and latitude; rasi and whole-sign houses; nakshatra and pada (13°20′ and 3°20′ each); navamsa; tithi (each 12° of Moon–Sun angle), yoga and karana; Vimshottari dasa and bhukti from the Moon’s progress through its star; Mars, Rahu–Ketu and Kala Sarpa doshas; and the day’s panchangam from the real sunrise and sunset at the birth place.'),
           ('3. Calendars and matching', 'Tamil months follow the sankranti-before-sunset rule, Kerala months the 3/5-of-daylight rule, and Telugu, Kannada and Hindi months the amanta and purnimanta lunar calendars with adhika masa. Matching uses the 10 porutham (counted from the bride’s star) and the 36-guna Ashtakoota with Nadi and Bhakoot dosha exceptions; where traditions differ, the page says so.'),
           ('4. How accurate is it?', 'We compared 400 random charts between 1900 and 2060 with Swiss Ephemeris, the professional reference. Planets matched within a few arc-seconds (median 1–3″), the Lagna within half an arc-second on average, and there were no differences in sign, nakshatra or Lagna.'),
           ('What astronomy can’t settle', 'Calculation is exact; interpretation is tradition. Different schools use different ayanamsas, Rahu node types and porutham rules — you can switch the node type and tradition in Settings. Please treat astrology as guidance, not certainty.')],
    'ta': [('ஜாதகம் கணிக்கப்படுவது — எங்கிருந்தோ எடுக்கப்படுவதல்ல', 'சுப ஜாதகத்தில் ஒவ்வொரு ஜாதகமும் பிறந்த தேதி, நேரம், ஊர் கொண்டு உங்கள் கைப்பேசியிலேயே கணிக்கப்படுகிறது. வேறு இணையதளத்திலிருந்து எதுவும் எடுக்கப்படுவதில்லை; உங்கள் விவரங்கள் எங்கள் சர்வருக்கு அனுப்பப்படுவதில்லை.'),
           ('1. கிரகங்கள் எங்கே இருந்தன', 'பிறந்த நொடியில் சூரியன், சந்திரன், கிரகங்களின் சரியான நிலையை astronomy-engine என்ற திறந்த மூல வானியல் நூலகம் மூலம் கணிக்கிறோம் — வானியலாளர்கள் பயன்படுத்தும் அதே மாதிரிகள். பின்னர் இந்திய அரசு ஏற்றுக்கொண்ட லஹிரி அயனாம்சம் கொண்டு நிராயன நிலைக்கு மாற்றுகிறோம் (திருக்கணிதம்).'),
           ('2. வானிலிருந்து ஜாதகமாக', 'எங்கள் சொந்த நிரல் லக்னம், ராசி, பாவங்கள், நட்சத்திரம், பாதம் (ஒவ்வொன்றும் 13°20′, 3°20′), நவாம்சம், திதி, யோகம், கரணம், விம்சோத்தரி தசா புக்தி, செவ்வாய் / ராகு–கேது / கால சர்ப்ப தோஷம், பிறந்த ஊரின் உண்மையான சூரிய உதயப்படி பஞ்சாங்கம் — அனைத்தையும் கணிக்கிறது.'),
           ('3. நாட்காட்டியும் பொருத்தமும்', 'தமிழ் மாதம் — அஸ்தமனத்துக்கு முன் சங்கிராந்தி விதி; கேரள மாதம் — பகலின் 3/5 விதி; தெலுங்கு, கன்னட, இந்தி — அமாந்த / பூர்ணிமாந்த சந்திர மாதம், அதிக மாசம் உட்பட. பொருத்தம் — பெண் நட்சத்திரத்திலிருந்து எண்ணும் 10 பொருத்தம், 36 குண அஷ்டகூடம் (நாடி, பகூட தோஷ விலக்குகளுடன்).'),
           ('4. எவ்வளவு துல்லியம்?', '1900–2060 இடையிலான 400 ஜாதகங்களை தொழில்முறை தரமான Swiss Ephemeris-உடன் ஒப்பிட்டோம்: கிரக நிலைகள் சில விநாடிகளுக்குள் (சராசரி 1–3″) ஒத்துப்போயின; ராசி, நட்சத்திரம், லக்னம் — ஒன்றில் கூட வேறுபாடு இல்லை.'),
           ('வானியல் தீர்க்க முடியாதது', 'கணிதம் துல்லியமானது; பலன் சொல்வது மரபு. அயனாம்சம், ராகு வகை, பொருத்த விதிகள் மரபுக்கு மரபு மாறும் — அமைப்புகளில் மாற்றலாம். ஜோதிடத்தை வழிகாட்டலாகக் கொள்ளுங்கள், உறுதியாக அல்ல.')],
    'ml': [('ജാതകം കണക്കാക്കുന്നതാണ് — എവിടെനിന്നും എടുക്കുന്നതല്ല', 'ശുഭ ജാതകത്തിലെ ഓരോ ജാതകവും ജനനത്തീയതി, സമയം, സ്ഥലം എന്നിവ ഉപയോഗിച്ച് നിങ്ങളുടെ ഫോണിൽ തന്നെ കണക്കാക്കുന്നു. മറ്റൊരു സൈറ്റിൽ നിന്നും ഒന്നും എടുക്കുന്നില്ല; വിവരങ്ങൾ ഞങ്ങളുടെ സെർവറിലേക്ക് പോകുന്നില്ല.'),
           ('1. ഗ്രഹങ്ങൾ എവിടെയായിരുന്നു', 'ജനന നിമിഷത്തിലെ സൂര്യൻ, ചന്ദ്രൻ, ഗ്രഹങ്ങളുടെ കൃത്യസ്ഥാനം astronomy-engine എന്ന ഓപ്പൺ സോഴ്സ് ജ്യോതിശാസ്ത്ര ലൈബ്രറി ഉപയോഗിച്ച് കണക്കാക്കുന്നു. പിന്നീട് ലാഹിരി അയനാംശം ഉപയോഗിച്ച് നിരയന സ്ഥാനത്തേക്ക് മാറ്റുന്നു (ദൃക്ഗണിതം).'),
           ('2. ആകാശത്തിൽ നിന്ന് ജാതകത്തിലേക്ക്', 'ഞങ്ങളുടെ സ്വന്തം കോഡ് ലഗ്നം, രാശി, ഭാവങ്ങൾ, നക്ഷത്രം, പാദം, നവാംശം, തിഥി, യോഗം, കരണം, വിംശോത്തരി ദശ–അപഹാരം, ദോഷങ്ങൾ, ജനനസ്ഥലത്തെ യഥാർത്ഥ സൂര്യോദയപ്രകാരമുള്ള പഞ്ചാംഗം എന്നിവ കണക്കാക്കുന്നു.'),
           ('3. കലണ്ടറും പൊരുത്തവും', 'കൊല്ലവർഷ മാസം — പകലിന്റെ 3/5 നിയമം; തമിഴ് മാസം — അസ്തമയത്തിന് മുൻപുള്ള സംക്രാന്തി; മറ്റു ഭാഷകൾക്ക് ചാന്ദ്രമാസം. പൊരുത്തം — 10 പൊരുത്തം, പാപസാമ്യം, 36 ഗുണ അഷ്ടകൂടം.'),
           ('4. എത്ര കൃത്യമാണ്?', '1900–2060 കാലത്തെ 400 ജാതകങ്ങൾ Swiss Ephemeris-നോട് താരതമ്യം ചെയ്തു: ഗ്രഹസ്ഥാനങ്ങൾ ഏതാനും സെക്കൻഡുകൾക്കുള്ളിൽ; രാശി, നക്ഷത്രം, ലഗ്നം — ഒന്നിലും വ്യത്യാസമില്ല.'),
           ('ഗണിതത്തിന് പറയാൻ കഴിയാത്തത്', 'കണക്ക് കൃത്യമാണ്; ഫലം പാരമ്പര്യമാണ്. അയനാംശം, രാഹു തരം, പൊരുത്ത നിയമങ്ങൾ സമ്പ്രദായങ്ങൾക്കനുസരിച്ച് മാറാം. ജ്യോതിഷം ഒരു വഴികാട്ടിയായി കാണുക.')],
    'te': [('జాతకం లెక్కిస్తాం — ఎక్కడినుండో తీసుకోము', 'శుభ జాతకంలో ప్రతి జాతకం జన్మ తేదీ, సమయం, స్థలం ఆధారంగా మీ ఫోన్‌లోనే లెక్కించబడుతుంది. మరే వెబ్‌సైట్ నుండీ ఏమీ తీసుకోము; మీ వివరాలు మా సర్వర్‌కు వెళ్ళవు.'),
           ('1. గ్రహాలు ఎక్కడ ఉన్నాయి', 'జన్మ క్షణంలో సూర్యుడు, చంద్రుడు, గ్రహాల ఖచ్చితమైన స్థానాలను astronomy-engine అనే ఓపెన్ సోర్స్ ఖగోళ లైబ్రరీతో లెక్కిస్తాం. తర్వాత భారత ప్రభుత్వం స్వీకరించిన లాహిరి అయనాంశతో నిరయన స్థానాలకు మారుస్తాం (దృక్ గణితం).'),
           ('2. ఆకాశం నుండి జాతకంగా', 'మా స్వంత కోడ్ లగ్నం, రాశి, భావాలు, నక్షత్రం, పాదం, నవాంశ, తిథి, యోగం, కరణం, వింశోత్తరి దశ–అంతర్దశ, దోషాలు, జన్మ స్థలంలోని నిజమైన సూర్యోదయం ప్రకారం పంచాంగం — అన్నీ లెక్కిస్తుంది.'),
           ('3. క్యాలెండర్ మరియు పొంతన', 'తెలుగు మాసాలు — అమాంత చాంద్రమానం, అధిక మాసం సహా; సంవత్సరం — 60 సంవత్సరాల చక్రం, శాలివాహన శకం. పొంతన — 36 గుణాల అష్టకూటం (నాడీ, భకూట దోష పరిహారాలతో), దక్షిణాది 10 పొరుత్తాలు.'),
           ('4. ఎంత ఖచ్చితం?', '1900–2060 మధ్య 400 జాతకాలను Swiss Ephemerisతో పోల్చాం: గ్రహ స్థానాలు కొన్ని సెకన్ల లోపు; రాశి, నక్షత్రం, లగ్నంలో ఒక్క తేడా కూడా లేదు.'),
           ('గణితం చెప్పలేనిది', 'లెక్క ఖచ్చితం; ఫలితం సంప్రదాయం. అయనాంశ, రాహు రకం, పొంతన నియమాలు సంప్రదాయాన్ని బట్టి మారతాయి. జ్యోతిష్యాన్ని మార్గదర్శకంగా తీసుకోండి.')],
    'kn': [('ಜಾತಕವನ್ನು ಲೆಕ್ಕ ಹಾಕುತ್ತೇವೆ — ಎಲ್ಲಿಂದಲೋ ತೆಗೆದುಕೊಳ್ಳುವುದಿಲ್ಲ', 'ಶುಭ ಜಾತಕದ ಪ್ರತಿಯೊಂದು ಜಾತಕವನ್ನೂ ಜನ್ಮ ದಿನಾಂಕ, ಸಮಯ, ಸ್ಥಳದಿಂದ ನಿಮ್ಮ ಫೋನ್‌ನಲ್ಲೇ ಲೆಕ್ಕ ಹಾಕಲಾಗುತ್ತದೆ. ಬೇರೆ ಜಾಲತಾಣದಿಂದ ಏನನ್ನೂ ತೆಗೆದುಕೊಳ್ಳುವುದಿಲ್ಲ; ನಿಮ್ಮ ವಿವರಗಳು ನಮ್ಮ ಸರ್ವರ್‌ಗೆ ಹೋಗುವುದಿಲ್ಲ.'),
           ('1. ಗ್ರಹಗಳು ಎಲ್ಲಿದ್ದವು', 'ಜನನ ಕ್ಷಣದ ಸೂರ್ಯ, ಚಂದ್ರ, ಗ್ರಹಗಳ ನಿಖರ ಸ್ಥಾನಗಳನ್ನು astronomy-engine ಎಂಬ ಮುಕ್ತ ಮೂಲ ಖಗೋಳ ಲೈಬ್ರರಿಯಿಂದ ಲೆಕ್ಕಿಸುತ್ತೇವೆ. ನಂತರ ಲಾಹಿರಿ ಅಯನಾಂಶದಿಂದ ನಿರಯನ ಸ್ಥಾನಕ್ಕೆ ಬದಲಿಸುತ್ತೇವೆ (ದೃಕ್ ಗಣಿತ).'),
           ('2. ಆಕಾಶದಿಂದ ಜಾತಕಕ್ಕೆ', 'ನಮ್ಮದೇ ಕೋಡ್ ಲಗ್ನ, ರಾಶಿ, ಭಾವಗಳು, ನಕ್ಷತ್ರ, ಪಾದ, ನವಾಂಶ, ತಿಥಿ, ಯೋಗ, ಕರಣ, ವಿಂಶೋತ್ತರಿ ದಶೆ–ಭುಕ್ತಿ, ದೋಷಗಳು, ಜನನ ಸ್ಥಳದ ನಿಜವಾದ ಸೂರ್ಯೋದಯದಂತೆ ಪಂಚಾಂಗ — ಎಲ್ಲವನ್ನೂ ಲೆಕ್ಕಿಸುತ್ತದೆ.'),
           ('3. ಕ್ಯಾಲೆಂಡರ್ ಮತ್ತು ಹೊಂದಾಣಿಕೆ', 'ಕನ್ನಡ ಮಾಸಗಳು — ಅಮಾಂತ ಚಾಂದ್ರಮಾನ, ಅಧಿಕ ಮಾಸ ಸಹಿತ; ಸಂವತ್ಸರ — 60ರ ಚಕ್ರ, ಶಾಲಿವಾಹನ ಶಕೆ. ಹೊಂದಾಣಿಕೆ — 36 ಗುಣಗಳ ಅಷ್ಟಕೂಟ (ನಾಡಿ, ಭಕೂಟ ದೋಷ ಪರಿಹಾರಗಳೊಂದಿಗೆ), ದಕ್ಷಿಣದ 10 ಪೊರುತ್ತಗಳು.'),
           ('4. ಎಷ್ಟು ನಿಖರ?', '1900–2060ರ 400 ಜಾತಕಗಳನ್ನು Swiss Ephemeris ಜೊತೆ ಹೋಲಿಸಿದ್ದೇವೆ: ಗ್ರಹ ಸ್ಥಾನಗಳು ಕೆಲವೇ ಸೆಕೆಂಡುಗಳೊಳಗೆ; ರಾಶಿ, ನಕ್ಷತ್ರ, ಲಗ್ನದಲ್ಲಿ ಒಂದೂ ವ್ಯತ್ಯಾಸವಿಲ್ಲ.'),
           ('ಗಣಿತ ಹೇಳಲಾರದ್ದು', 'ಲೆಕ್ಕ ನಿಖರ; ಫಲ ಸಂಪ್ರದಾಯ. ಅಯನಾಂಶ, ರಾಹು ಪ್ರಕಾರ, ಹೊಂದಾಣಿಕೆ ನಿಯಮಗಳು ಸಂಪ್ರದಾಯದಂತೆ ಬದಲಾಗುತ್ತವೆ. ಜ್ಯೋತಿಷ್ಯವನ್ನು ಮಾರ್ಗದರ್ಶನವಾಗಿ ತೆಗೆದುಕೊಳ್ಳಿ.')],
    'hi': [('कुंडली की गणना होती है — कहीं से ली नहीं जाती', 'शुभ जातक पर हर कुंडली जन्म तिथि, समय और स्थान से आपके फ़ोन या ब्राउज़र में ही गणित से बनती है। किसी दूसरी वेबसाइट से कुछ नहीं लिया जाता, और आपका विवरण हमारे सर्वर पर नहीं जाता।'),
           ('1. ग्रह कहाँ थे', 'जन्म के क्षण में सूर्य, चंद्र और ग्रहों की सटीक स्थिति astronomy-engine नामक ओपन-सोर्स खगोलीय लाइब्रेरी से निकाली जाती है — वही ग्रह-मॉडल जो खगोलशास्त्री इस्तेमाल करते हैं। फिर भारत सरकार द्वारा अपनाए गए लाहिड़ी अयनांश से निरयन स्थिति बनाई जाती है (दृक् गणित)।'),
           ('2. आकाश से कुंडली तक', 'हमारा अपना कोड लग्न, राशि, भाव, नक्षत्र और चरण (13°20′ और 3°20′), नवांश, तिथि, योग, करण, विंशोत्तरी महादशा–अंतर्दशा, मांगलिक/कालसर्प दोष और जन्म स्थान के वास्तविक सूर्योदय से पंचांग — सब निकालता है।'),
           ('3. पंचांग और मिलान', 'हिंदी पंचांग — पूर्णिमांत मास, अधिक मास सहित, विक्रम संवत। मिलान — अष्टकूट 36 गुण (नाड़ी और भकूट दोष के परिहार सहित) और दक्षिण भारतीय 10 पोरुत्तम भी।'),
           ('4. कितनी सटीक?', '1900–2060 की 400 कुंडलियों की तुलना पेशेवर मानक Swiss Ephemeris से की गई: ग्रह स्थिति कुछ ही विकला (1–3″) के भीतर; राशि, नक्षत्र या लग्न में एक भी अंतर नहीं।'),
           ('जो गणित तय नहीं करता', 'गणना सटीक है; फलादेश परंपरा है। अयनांश, राहु का प्रकार और मिलान के नियम परंपरा के अनुसार बदलते हैं — सेटिंग्स में बदल सकते हैं। ज्योतिष को मार्गदर्शन मानें, निश्चितता नहीं।')],
}

GLATIN = ['Mesha', 'Rishabha', 'Mithuna', 'Kataka', 'Simha', 'Kanya', 'Tula', 'Vrischika', 'Dhanus', 'Makara', 'Kumbha', 'Meena']
RASI_SLUG = [x.lower() for x in GLATIN]


def esc(x):
    return html.escape(str(x), quote=True)


def base(l):
    return '/' if l == 'en' else f'/{l}/'


def node_json(js):
    return json.loads(subprocess.run(['node', '-'], input=js, capture_output=True, text=True, check=True, cwd='.').stdout)


def nav_html(l):
    m = T[l]['menu']
    b = base(l)
    links = [(m[0], f'{b}calendar/'), (m[1], f'{b}panchangam/'), (m[2], f'{b}nakshatra/'), (m[3], f'{b}rasi/'), (m[4], f'{b}baby-names.html'), (m[5], f'{b}how-we-calculate.html')]
    return '<nav class="kbnav">' + ''.join(f'<a href="{h}">{esc(t)}</a>' for t, h in links) + '</nav>'


def page(l, title, desc, canon, alts, body, crumbs, ads, extra_head=''):
    p = NK.shell(l, title, desc, canon, alts, body + nav_html(l), crumbs, base(l) + '#match')
    p = p.replace('<!--ADS-->', ads + extra_head)
    os.makedirs(os.path.dirname(canon.lstrip('/')) or '.', exist_ok=True)
    out = canon.lstrip('/') + ('index.html' if canon.endswith('/') else '')
    open(out, 'w').write(p)
    return (canon, alts)


def alts_for(rel):
    return [(x, base(x) + rel) for x in LANGS]


def fmt_time(ms, off=330):
    d = datetime.datetime.utcfromtimestamp((ms + off * 60000) / 1000)
    return d


def generate(I, ads):
    urls = []
    today = datetime.datetime.utcnow() + datetime.timedelta(minutes=330)
    # ------------------------------------------------------------ festival calendar
    cal_data = {}
    for l in LANGS:
        name, lat, lon = HOME[l]
        key = name
        if key not in cal_data:
            js = f"""global.Astronomy=require('./src/vendor/astronomy.browser.min.js');const F=require('./src/festivals.js');
process.stdout.write(JSON.stringify(F.compute({{lat:{lat},lon:{lon},tz:'Asia/Kolkata'}},[{YEARS[0]},1,1],[{YEARS[-1]},12,31])));"""
            cal_data[key] = node_json(js)
    regions = {e['id']: e['reg'] for e in node_json("const F=require('./src/festivals.js');process.stdout.write(JSON.stringify(F.EVENTS.map(e=>({id:e.id,reg:e.reg}))))")}
    for l in LANGS:
        D, Lx = T[l], I[l]
        city, lat, lon = HOME[l]
        city_n = native_city(I, l, city)
        tr = TRAD[l]
        evs = [e for e in cal_data[city] if regions[e['id']] == 'all' or tr in regions[e['id']].split()]
        for y in YEARS:
            ye = [e for e in evs if e['date'].startswith(str(y))]
            ics = ics_text(l, y, ye)
            icsname = f'suba-jathagam-{l}-{y}.ics'
            os.makedirs(f'{base(l).lstrip("/")}calendar', exist_ok=True)
            open(f'{base(l).lstrip("/")}calendar/{icsname}', 'w').write(ics)
            months = ''
            for mo in range(1, 13):
                rows = ''
                for e in [e for e in ye if int(e['date'][5:7]) == mo]:
                    nm = EVENT_NAMES[e['id']][l]
                    fest = e['id'] not in MONTHLY
                    tm = ''
                    if e.get('start') and e.get('end'):
                        s, en = fmt_time(e['start']), fmt_time(e['end'])
                        tm = f'{s.day:02d}/{s.month:02d} {s.hour:02d}:{s.minute:02d} – {en.day:02d}/{en.month:02d} {en.hour:02d}:{en.minute:02d}'
                    dd = e['date']
                    rows += f'<tr class="{"fest" if fest else ""}"><td>{int(dd[8:])} {esc(GMONTHS[l][mo - 1][:3] if l == "en" else GMONTHS[l][mo - 1])}</td><td>{esc(Lx["days"][e["weekday"]])}</td><td>{"<b>" if fest else ""}{esc(nm)}{"</b>" if fest else ""}</td><td class="tm">{tm}</td></tr>'
                if rows:
                    months += f'<h2 id="m{mo}">{esc(GMONTHS[l][mo - 1])} {y}</h2><div class="tw"><table><tr><th>{esc(D["cDate"])}</th><th>{esc(D["cDay"])}</th><th>{esc(D["cEvent"])}</th><th>{esc(D["cTime"])}</th></tr>{rows}</table></div>'
            jump = ''.join(f'<a href="#m{mo}">{esc(GMONTHS[l][mo - 1])}</a>' for mo in range(1, 13) if f'id="m{mo}"' in months)
            other = ''.join(f'<a href="{base(l)}calendar/{yy}.html"{" class=on" if yy == y else ""}>{yy}</a>' for yy in YEARS)
            body = f'''<h1>{esc(D['calH1'].format(y=y))}</h1>
<p class="lead">{esc(D['calLead'].format(y=y, city=city_n))}</p>
<p><a class="btn big" href="{base(l)}calendar/{icsname}" download>{esc(D['ics'])}</a></p>
<p class="note">{esc(D['icsHint'])}</p>
<p class="chips">{other}</p>
<p class="chips">{jump}</p>
<!--AD-->
{months}
<p class="note">{esc(D['rule'])}</p>'''
            urls.append(page(l, D['calTitle'].format(y=y), D['calLead'].format(y=y, city=city_n)[:300], f'{base(l)}calendar/{y}.html', alts_for(f'calendar/{y}.html'), body,
                             [(NK.S[l]['home'], base(l)), (D['menu'][0], f'{base(l)}calendar/'), (str(y), None)], ads))
        # calendar index: upcoming events
        up = [e for e in evs if e['date'] >= today.strftime('%Y-%m-%d') and e['id'] not in MONTHLY][:12]
        rows = ''.join(f'<tr><td>{int(e["date"][8:])} {esc(GMONTHS[l][int(e["date"][5:7]) - 1])} {e["date"][:4]}</td><td>{esc(Lx["days"][e["weekday"]])}</td><td><b>{esc(EVENT_NAMES[e["id"]][l])}</b></td></tr>' for e in up)
        yrs = ''.join(f'<a class="btn big" href="{base(l)}calendar/{yy}.html">{yy}</a> ' for yy in YEARS)
        body = f'''<h1>{esc(D['calIdxH1'])}</h1>
<p class="lead">{esc(D['calIdxLead'])}</p>
<p>{yrs}</p>
<h2>{esc(D['festivals'])}</h2>
<div class="tw"><table>{rows}</table></div>
<!--AD-->'''
        urls.append(page(l, D['calIdxTitle'], D['calIdxLead'], f'{base(l)}calendar/', alts_for('calendar/'), body, [(NK.S[l]['home'], base(l)), (D['menu'][0], None)], ads))

    # ------------------------------------------------------------ panchangam today, per city
    places = load_places()
    cities = [c for c in CITIES if c in places]
    for l in LANGS:
        D, Lx = T[l], I[l]
        tr = TRAD[l]
        keys = ['tithis', 'pournami', 'amavasai', 'naks', 'yogas', 'karanas', 'days', 'months', 'malMonths', 'lunarMonths', 'years60', 'pakShort', 'nextDay', 'till', 'then',
                'kollamFmt', 'samvFmt', 'shakaFmt', 'vikramFmt', 'adhika', 'varusham', 'cal_ta', 'cal_ml', 'cal_te', 'cal_kn', 'cal_hi', 'sunrise', 'sunset', 'tithi', 'star', 'yoga',
                'karana', 'rahuKalam', 'yamagandam', 'kuligai', 'abhijit', 'avoid', 'goodTime', 'weekday']
        DD = {k: Lx[k] for k in keys}
        for c in cities:
            p = places[c]
            cn = native_name(p, l)
            cj = json.dumps({'lat': p['lat'], 'lon': p['lon'], 'tz': p['tz']})
            js = f"""global.Astronomy=require('./src/vendor/astronomy.browser.min.js');const J=require('./src/engine.js');const W=require('./src/panch_widget.js');
const D={json.dumps(DD, ensure_ascii=False)};const c={cj};const t=W.todayYMD(c.tz);
process.stdout.write(JSON.stringify({{a:W.render(J,D,c,t,{json.dumps(tr)}),b:W.week(J,D,c,t),t}}));"""
            pre = node_json(js)
            others = ''.join(f'<a href="{base(l)}panchangam/{slugc(x)}.html"{" class=on" if x == c else ""}>{esc(native_name(places[x], l))}</a>' for x in cities)
            body = f'''<h1>{esc(D['pH1'].format(city=cn))}</h1>
<p class="lead">{esc(D['pLead'].format(city=cn))}</p>
<p class="today-date" id="pdate">{pre['t'][2]:02d}-{pre['t'][1]:02d}-{pre['t'][0]}</p>
<div id="pcard">{pre['a']}</div>
<!--AD-->
<h2>{esc(D['pWeek'])}</h2>
<div id="pweek">{pre['b']}</div>
<p><a class="btn big" href="{base(l)}#panch">{esc(D['pApp'])}</a></p>
<h2>{esc(D['pOther'])}</h2>
<p class="chips">{others}</p>
<script src="/assets/panch.js" defer></script>
<script>window.addEventListener('DOMContentLoaded',function(){{try{{var D={json.dumps(DD, ensure_ascii=False)},c={cj},t=SJPanch.todayYMD(c.tz);
document.getElementById('pcard').innerHTML=SJPanch.render(Jothidam,D,c,t,{json.dumps(tr)});document.getElementById('pweek').innerHTML=SJPanch.week(Jothidam,D,c,t);
document.getElementById('pdate').textContent=String(t[2]).padStart(2,'0')+'-'+String(t[1]).padStart(2,'0')+'-'+t[0];}}catch(e){{}}}});</script>'''
            urls.append(page(l, D['pTitle'].format(city=cn), D['pLead'].format(city=cn), f'{base(l)}panchangam/{slugc(c)}.html', alts_for(f'panchangam/{slugc(c)}.html'), body,
                             [(NK.S[l]['home'], base(l)), (D['menu'][1], f'{base(l)}panchangam/'), (cn, None)], ads))
        lst = ''.join(f'<a href="{base(l)}panchangam/{slugc(x)}.html">{esc(native_name(places[x], l))}</a>' for x in cities)
        body = f'''<h1>{esc(D['pIdxH1'])}</h1><p class="lead">{esc(D['pIdxLead'])}</p><p class="chips big">{lst}</p><p><a class="btn big" href="{base(l)}#panch">{esc(D['pApp'])}</a></p><!--AD-->'''
        urls.append(page(l, D['pIdxTitle'], D['pIdxLead'], f'{base(l)}panchangam/', alts_for('panchangam/'), body, [(NK.S[l]['home'], base(l)), (D['menu'][1], None)], ads))

    # ------------------------------------------------------------ baby names (namakshara)
    names_en = I['en']['naks']
    for l in LANGS:
        D, Lx = T[l], I[l]
        head = f'<tr><th>{esc(D["bStar"])}</th>' + ''.join(f'<th>{esc(D["bPada"].format(n=n))}</th>' for n in range(1, 5)) + '</tr>'
        rows = ''
        for s in range(27):
            cells = ''
            for pd in range(4):
                lat_ = NAMA_LATIN[s][pd]
                if l == 'en':
                    cells += f'<td><b>{lat_}</b></td>'
                else:
                    loc = NAMA_TA[s][pd] if l == 'ta' else SC.transliterate(NAMA_HK[s][pd], SC.HK, SCRIPT[l])
                    cells += f'<td><b class="big">{loc}</b><small>{lat_}</small></td>'
            rows += f'<tr><td><a href="{base(l)}nakshatra/{NK.slug(names_en[s])}.html">{esc(Lx["naks"][s])}</a></td>{cells}</tr>'
        body = f'''<h1>{esc(D['bH1'])}</h1><p class="lead">{esc(D['bLead'])}</p>
<p><a class="btn big" href="{base(l)}#horo">{esc(D['bFind'])}</a></p>
<div class="tw"><table class="nama">{head}{rows}</table></div><!--AD-->'''
        urls.append(page(l, D['bTitle'], D['bLead'][:300], f'{base(l)}baby-names.html', alts_for('baby-names.html'), body, [(NK.S[l]['home'], base(l)), (D['menu'][4], None)], ads))

    # ------------------------------------------------------------ 12 rasi pages
    rd = node_json(f"""global.Astronomy=require('./src/vendor/astronomy.browser.min.js');const J=require('./src/engine.js');
const now=Date.now();const out=[];for(let r=0;r<12;r++){{const c={{rasi:r,lagna:{{sign:r}},planets:[]}};const tr=J.transits(c,now);
const sat=tr.find(x=>x.name==='Saturn'),jup=tr.find(x=>x.name==='Jupiter');const ph=J.saturnPhase(sat.fromMoon);
const good=[];for(let b=0;b<12;b++){{const n=((b-r+12)%12)+1;const rasiOk=[7,3,4,5,9,10,11].includes(n)||(n===1);const bk=![2,12,5,9,6,8].includes(n);if(rasiOk&&bk&&n!==1)good.push(b);}}
out.push({{sat:sat.sign,satH:sat.fromMoon,ph:ph?ph.key:null,jup:jup.sign,jupH:jup.fromMoon,good}});}}process.stdout.write(JSON.stringify(out));""")
    span_cache = NK.compute()['facts']
    dstr = today.strftime('%d-%m-%Y')
    for l in LANGS:
        D, Lx = T[l], I[l]
        cards = ''
        for r in range(12):
            rn = Lx['rasis'][r]
            lord = Lx['pl'][['Mars', 'Venus', 'Mercury', 'Moon', 'Sun', 'Mercury', 'Venus', 'Mars', 'Jupiter', 'Saturn', 'Saturn', 'Jupiter'][r]]
            naks = []
            for s in range(27):
                pads = [i + 1 for i, x in enumerate(span_cache[s]['padas']) if x == r]
                if pads:
                    naks.append(f'<a href="{base(l)}nakshatra/{NK.slug(names_en[s])}.html">{esc(Lx["naks"][s])}</a> {pads[0]}{"–" + str(pads[-1]) if len(pads) > 1 else ""}')
            info = rd[r]
            v = dict(r=rn, en=GLATIN[r], n=r + 1, lord=lord, el=ELEMENT_N[l][ELEMENT[r]], q=QUALITY_N[l][QUALITY[r]])
            ph = Lx.get(info['ph'], '') if info['ph'] else ''
            facts = [(D['rLord'], lord), (D['rEl'], v['el']), (D['rQ'], v['q'])]
            good = ''.join(f'<a href="{base(l)}rasi/{RASI_SLUG[b]}.html">{esc(Lx["rasis"][b])}</a>' for b in info['good'])
            body = f'''<h1>{esc(D['rH1'].format(**v))}</h1><p class="lead">{esc(D['rLead'].format(**v))}</p>
<div class="tw"><table class="facts">{''.join(f'<tr><th>{esc(a)}</th><td>{esc(b)}</td></tr>' for a, b in facts)}<tr><th>{esc(D['rNaks'])}</th><td>{', '.join(naks)}</td></tr></table></div>
<h2>{esc(D['rTransit'].format(d=dstr))}</h2>
<ul class="tl"><li>{esc(D['rSat'].format(s=Lx['rasis'][info['sat']], h=info['satH'], r=rn))}{(' — <b>' + esc(ph) + '</b>') if ph else ''}</li>
<li>{esc(D['rJup'].format(s=Lx['rasis'][info['jup']], h=info['jupH'], r=rn))}{(' — ' + esc(Lx['guruGood'])) if info['jupH'] in (2, 5, 7, 9, 11) else ''}</li></ul>
<h2>{esc(D['rMatch'].format(r=rn))}</h2><p class="chips">{good}</p><p class="note">{esc(D['rMatchNote'])}</p>
<p><a class="btn big" href="{base(l)}#match">{esc(NK.S[l]['cta'])}</a></p><!--AD-->
<h2>{esc(D['menu'][3])}</h2><p class="chips">{''.join(f'<a href="{base(l)}rasi/{RASI_SLUG[b]}.html"{" class=on" if b == r else ""}>{esc(Lx["rasis"][b])}</a>' for b in range(12))}</p>'''
            urls.append(page(l, D['rTitle'].format(**v), D['rLead'].format(**v), f'{base(l)}rasi/{RASI_SLUG[r]}.html', alts_for(f'rasi/{RASI_SLUG[r]}.html'), body,
                             [(NK.S[l]['home'], base(l)), (D['menu'][3], f'{base(l)}rasi/'), (rn, None)], ads))
            cards += f'<tr><td>{r + 1}</td><td><a href="{base(l)}rasi/{RASI_SLUG[r]}.html">{esc(rn)}</a></td><td>{esc(lord)}</td><td>{esc(v["el"])}</td><td>{esc(v["q"])}</td></tr>'
        body = f'''<h1>{esc(D['rIdxH1'])}</h1><p class="lead">{esc(D['rIdxLead'])}</p><div class="tw"><table><tr><th>#</th><th>{esc(Lx['rasi'])}</th><th>{esc(D['rLord'])}</th><th>{esc(D['rEl'])}</th><th>{esc(D['rQ'])}</th></tr>{cards}</table></div><!--AD-->'''
        urls.append(page(l, D['rIdxTitle'], D['rIdxLead'], f'{base(l)}rasi/', alts_for('rasi/'), body, [(NK.S[l]['home'], base(l)), (D['menu'][3], None)], ads))

    # ------------------------------------------------------------ how we calculate
    for l in LANGS:
        D = T[l]
        secs = ''.join(f'<h2>{esc(h)}</h2><p>{esc(p)}</p>' for h, p in HOW[l])
        body = f'<h1>{esc(D["hH1"])}</h1>{secs}<p><a class="btn big" href="{base(l)}#horo">{esc(NK.S[l]["cta"])}</a></p>'
        urls.append(page(l, D['hTitle'], HOW[l][0][1][:300], f'{base(l)}how-we-calculate.html', alts_for('how-we-calculate.html'), body, [(NK.S[l]['home'], base(l)), (D['menu'][5], None)], ads))
    return urls


def slugc(c):
    return c.lower().replace(' ', '-')


_PL = None


def load_places():
    global _PL
    if _PL is None:
        d = json.load(open('data/places.json'))
        _PL = {}
        for p in d['p']:
            if p[3] == 'IN' and p[0] not in _PL:
                _PL[p[0]] = dict(name=p[0], ta=p[1], lat=p[4], lon=p[5], tz=d['tz'][p[6]], nat=p[8] if len(p) > 8 else [])
    return _PL


def native_name(p, l):
    if l == 'en':
        return p['name']
    if l == 'ta':
        return p['ta'] or p['name']
    i = {'hi': 0, 'te': 1, 'kn': 2, 'ml': 3}[l]
    return (p['nat'][i] if p['nat'] and p['nat'][i] else p['name'])


def native_city(I, l, name):
    p = load_places().get(name)
    return native_name(p, l) if p else name


def ics_text(l, y, evs):
    now = datetime.datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')
    lines = ['BEGIN:VCALENDAR', 'VERSION:2.0', 'PRODID:-//Suba Jathagam//Festival calendar//EN', 'CALSCALE:GREGORIAN', 'METHOD:PUBLISH',
             f'X-WR-CALNAME:Suba Jathagam {y}', 'X-WR-TIMEZONE:Asia/Kolkata']
    for e in evs:
        d = e['date'].replace('-', '')
        nd = (datetime.date.fromisoformat(e['date']) + datetime.timedelta(days=1)).strftime('%Y%m%d')
        nm = EVENT_NAMES[e['id']][l].replace(',', '\\,')
        lines += ['BEGIN:VEVENT', f'UID:{e["id"]}-{d}-{l}@subajathagam.in', f'DTSTAMP:{now}', f'DTSTART;VALUE=DATE:{d}', f'DTEND;VALUE=DATE:{nd}',
                  f'SUMMARY:{nm}', 'DESCRIPTION:subajathagam.in', 'TRANSP:TRANSPARENT',
                  'BEGIN:VALARM', 'ACTION:DISPLAY', f'DESCRIPTION:{nm}', 'TRIGGER:-PT6H', 'END:VALARM', 'END:VEVENT']
    lines.append('END:VCALENDAR')
    # fold long lines (RFC 5545, 75 octets)
    out = []
    for ln in lines:
        b = ln.encode('utf-8')
        while len(b) > 73:
            cut = 73
            while (b[cut] & 0xC0) == 0x80:
                cut -= 1
            out.append(b[:cut].decode())
            b = b' ' + b[cut:]
        out.append(b.decode())
    return '\r\n'.join(out) + '\r\n'
