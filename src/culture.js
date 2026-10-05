// Suba Jathagam — regional culture layer: traditions, print text per language, print themes, place names.
// Loaded before the app script; exposes window.SJC.
(function (root) {
  'use strict';
  const LANGS = [['en', 'English'], ['ta', 'தமிழ்'], ['ml', 'മലയാളം'], ['te', 'తెలుగు'], ['kn', 'ಕನ್ನಡ'], ['hi', 'हिन्दी']];

  // Tradition: Mars dosha houses, default chart style, default matching method, panchangam home town
  const TRADS = {
    ta: { mars: [2, 4, 7, 8, 12], chart: 'south', match: 'porutham' },
    ml: { mars: [2, 4, 7, 8, 12], chart: 'south', match: 'porutham', papa: true },
    te: { mars: [2, 4, 7, 8, 12], chart: 'south', match: 'guna' },
    kn: { mars: [2, 4, 7, 8, 12], chart: 'south', match: 'guna' },
    hi: { mars: [1, 4, 7, 8, 12], chart: 'north', match: 'guna' }
  };
  const PANCH_HOME = {
    en: { name: 'Chennai', ta: 'சென்னை', adm: 'Tamil Nadu', cc: 'IN', lat: 13.0878, lon: 80.2785, tz: 'Asia/Kolkata' },
    ta: { name: 'Chennai', ta: 'சென்னை', adm: 'Tamil Nadu', cc: 'IN', lat: 13.0878, lon: 80.2785, tz: 'Asia/Kolkata' },
    ml: { name: 'Kochi', ta: 'கொச்சி', adm: 'Kerala', cc: 'IN', lat: 9.9399, lon: 76.2602, tz: 'Asia/Kolkata', nat: ['कोच्चि', 'కొచ్చి', 'ಕೊಚ್ಚಿ', 'കൊച്ചി'] },
    te: { name: 'Hyderabad', ta: 'ஹைதராபாத்', adm: 'Telangana', cc: 'IN', lat: 17.384, lon: 78.4564, tz: 'Asia/Kolkata', nat: ['हैदराबाद', 'హైదరాబాద్', 'ಹೈದರಾಬಾದ್', 'ഹൈദരാബാദ്'] },
    kn: { name: 'Bengaluru', ta: 'பெங்களூர்', adm: 'Karnataka', cc: 'IN', lat: 12.9719, lon: 77.5937, tz: 'Asia/Kolkata', nat: ['बेंगलुरु', 'బెంగళూరు', 'ಬೆಂಗಳೂರು', 'ബെംഗളൂരു'] },
    hi: { name: 'New Delhi', ta: 'புது தில்லி', adm: 'Delhi', cc: 'IN', lat: 28.6139, lon: 77.209, tz: 'Asia/Kolkata', nat: ['नई दिल्ली', 'న్యూఢిల్లీ', 'ನವದೆಹಲಿ', 'ന്യൂഡൽഹി'] }
  };
  const POPULAR = {
    en: ['Chennai', 'Bengaluru', 'Hyderabad', 'Mumbai', 'New Delhi', 'Kochi', 'Kolkata', 'Pune', 'Singapore', 'Dubai'],
    ta: ['Chennai', 'Madurai', 'Coimbatore', 'Tiruchirappalli', 'Salem', 'Tirunelveli', 'Thanjavur', 'Bengaluru', 'Singapore', 'Colombo'],
    ml: ['Thiruvananthapuram', 'Kochi', 'Kozhikode', 'Thrissur', 'Kollam', 'Kannur', 'Palakkad', 'Kottayam', 'Dubai', 'Bengaluru'],
    te: ['Hyderabad', 'Visakhapatnam', 'Vijayawada', 'Guntur', 'Tirupati', 'Warangal', 'Nellore', 'Kakinada', 'Bengaluru', 'Chennai'],
    kn: ['Bengaluru', 'Mysuru', 'Mangaluru', 'Hubballi', 'Belagavi', 'Kalaburagi', 'Davangere', 'Udupi', 'Shivamogga', 'Chennai'],
    hi: ['New Delhi', 'Mumbai', 'Lucknow', 'Jaipur', 'Patna', 'Bhopal', 'Varanasi', 'Kanpur', 'Indore', 'Ahmedabad']
  };
  const NAT_IDX = { hi: 0, te: 1, kn: 2, ml: 3 };

  const CC = ['IN', 'LK', 'SG', 'MY', 'AE', 'SA', 'QA', 'KW', 'OM', 'BH', 'GB', 'US', 'CA', 'AU', 'NZ', 'ZA', 'MU', 'FR', 'DE', 'RE'];
  const CN = {
    en: ['India', 'Sri Lanka', 'Singapore', 'Malaysia', 'UAE', 'Saudi Arabia', 'Qatar', 'Kuwait', 'Oman', 'Bahrain', 'UK', 'USA', 'Canada', 'Australia', 'New Zealand', 'South Africa', 'Mauritius', 'France', 'Germany', 'Réunion'],
    ta: ['இந்தியா', 'இலங்கை', 'சிங்கப்பூர்', 'மலேசியா', 'ஐக்கிய அரபு அமீரகம்', 'சவுதி அரேபியா', 'கத்தார்', 'குவைத்', 'ஓமன்', 'பஹ்ரைன்', 'ஐக்கிய இராச்சியம்', 'அமெரிக்கா', 'கனடா', 'ஆஸ்திரேலியா', 'நியூசிலாந்து', 'தென்னாப்பிரிக்கா', 'மொரிசியஸ்', 'பிரான்ஸ்', 'ஜெர்மனி', 'ரீயூனியன்'],
    hi: ['भारत', 'श्रीलंका', 'सिंगापुर', 'मलेशिया', 'यूएई', 'सऊदी अरब', 'क़तर', 'कुवैत', 'ओमान', 'बहरीन', 'ब्रिटेन', 'अमेरिका', 'कनाडा', 'ऑस्ट्रेलिया', 'न्यूज़ीलैंड', 'दक्षिण अफ़्रीका', 'मॉरीशस', 'फ़्रांस', 'जर्मनी', 'रीयूनियन'],
    te: ['భారతదేశం', 'శ్రీలంక', 'సింగపూర్', 'మలేషియా', 'యూఏఈ', 'సౌదీ అరేబియా', 'ఖతార్', 'కువైట్', 'ఒమన్', 'బహ్రెయిన్', 'యునైటెడ్ కింగ్‌డమ్', 'అమెరికా', 'కెనడా', 'ఆస్ట్రేలియా', 'న్యూజిలాండ్', 'దక్షిణాఫ్రికా', 'మారిషస్', 'ఫ్రాన్స్', 'జర్మనీ', 'రీయూనియన్'],
    kn: ['ಭಾರತ', 'ಶ್ರೀಲಂಕಾ', 'ಸಿಂಗಾಪುರ', 'ಮಲೇಷ್ಯಾ', 'ಯುಎಇ', 'ಸೌದಿ ಅರೇಬಿಯಾ', 'ಕತಾರ್', 'ಕುವೈತ್', 'ಒಮಾನ್', 'ಬಹ್ರೇನ್', 'ಯುನೈಟೆಡ್ ಕಿಂಗ್‌ಡಮ್', 'ಅಮೆರಿಕ', 'ಕೆನಡಾ', 'ಆಸ್ಟ್ರೇಲಿಯಾ', 'ನ್ಯೂಜಿಲೆಂಡ್', 'ದಕ್ಷಿಣ ಆಫ್ರಿಕಾ', 'ಮಾರಿಷಸ್', 'ಫ್ರಾನ್ಸ್', 'ಜರ್ಮನಿ', 'ರಿಯೂನಿಯನ್'],
    ml: ['ഇന്ത്യ', 'ശ്രീലങ്ക', 'സിംഗപ്പൂർ', 'മലേഷ്യ', 'യുഎഇ', 'സൗദി അറേബ്യ', 'ഖത്തർ', 'കുവൈറ്റ്', 'ഒമാൻ', 'ബഹ്റൈൻ', 'യുണൈറ്റഡ് കിംഗ്ഡം', 'അമേരിക്ക', 'കാനഡ', 'ഓസ്ട്രേലിയ', 'ന്യൂസിലൻഡ്', 'ദക്ഷിണാഫ്രിക്ക', 'മൗറീഷ്യസ്', 'ഫ്രാൻസ്', 'ജർമ്മനി', 'റീയൂണിയൻ']
  };
  const COUNTRY = {};
  CC.forEach((c, i) => { COUNTRY[c] = {}; for (const l in CN) COUNTRY[c][l] = CN[l][i]; });

  const SN = ['Tamil Nadu', 'Kerala', 'Karnataka', 'Andhra Pradesh', 'Telangana', 'Maharashtra', 'Uttar Pradesh', 'Madhya Pradesh', 'Gujarat', 'Rajasthan', 'Bihar', 'West Bengal', 'Punjab', 'Odisha', 'Haryana', 'Delhi', 'Chhattisgarh', 'Assam', 'Jharkhand', 'Uttarakhand', 'Goa', 'Himachal Pradesh', 'Puducherry', 'Andaman and Nicobar', 'Chandigarh'];
  const ST = {
    ta: ['தமிழ்நாடு', 'கேரளா', 'கர்நாடகா', 'ஆந்திரப் பிரதேசம்', 'தெலங்காணா', 'மகாராஷ்டிரா', 'உத்தரப் பிரதேசம்', 'மத்தியப் பிரதேசம்', 'குஜராத்', 'ராஜஸ்தான்', 'பீகார்', 'மேற்கு வங்காளம்', 'பஞ்சாப்', 'ஒடிசா', 'ஹரியானா', 'தில்லி', 'சத்தீஸ்கர்', 'அசாம்', 'ஜார்க்கண்ட்', 'உத்தராகண்ட்', 'கோவா', 'இமாச்சலப் பிரதேசம்', 'புதுச்சேரி', 'அந்தமான் நிக்கோபார்', 'சண்டிகர்'],
    hi: ['तमिलनाडु', 'केरल', 'कर्नाटक', 'आंध्र प्रदेश', 'तेलंगाना', 'महाराष्ट्र', 'उत्तर प्रदेश', 'मध्य प्रदेश', 'गुजरात', 'राजस्थान', 'बिहार', 'पश्चिम बंगाल', 'पंजाब', 'ओडिशा', 'हरियाणा', 'दिल्ली', 'छत्तीसगढ़', 'असम', 'झारखंड', 'उत्तराखंड', 'गोवा', 'हिमाचल प्रदेश', 'पुदुच्चेरी', 'अंडमान और निकोबार', 'चंडीगढ़'],
    te: ['తమిళనాడు', 'కేరళ', 'కర్ణాటక', 'ఆంధ్రప్రదేశ్', 'తెలంగాణ', 'మహారాష్ట్ర', 'ఉత్తరప్రదేశ్', 'మధ్యప్రదేశ్', 'గుజరాత్', 'రాజస్థాన్', 'బీహార్', 'పశ్చిమ బెంగాల్', 'పంజాబ్', 'ఒడిశా', 'హర్యానా', 'ఢిల్లీ', 'ఛత్తీస్‌గఢ్', 'అస్సాం', 'ఝార్ఖండ్', 'ఉత్తరాఖండ్', 'గోవా', 'హిమాచల్ ప్రదేశ్', 'పుదుచ్చేరి', 'అండమాన్ నికోబార్', 'చండీగఢ్'],
    kn: ['ತಮಿಳುನಾಡು', 'ಕೇರಳ', 'ಕರ್ನಾಟಕ', 'ಆಂಧ್ರಪ್ರದೇಶ', 'ತೆಲಂಗಾಣ', 'ಮಹಾರಾಷ್ಟ್ರ', 'ಉತ್ತರ ಪ್ರದೇಶ', 'ಮಧ್ಯಪ್ರದೇಶ', 'ಗುಜರಾತ್', 'ರಾಜಸ್ಥಾನ', 'ಬಿಹಾರ', 'ಪಶ್ಚಿಮ ಬಂಗಾಳ', 'ಪಂಜಾಬ್', 'ಒಡಿಶಾ', 'ಹರಿಯಾಣ', 'ದೆಹಲಿ', 'ಛತ್ತೀಸ್‌ಗಢ', 'ಅಸ್ಸಾಂ', 'ಜಾರ್ಖಂಡ್', 'ಉತ್ತರಾಖಂಡ', 'ಗೋವಾ', 'ಹಿಮಾಚಲ ಪ್ರದೇಶ', 'ಪುದುಚೇರಿ', 'ಅಂಡಮಾನ್ ನಿಕೋಬಾರ್', 'ಚಂಡೀಗಢ'],
    ml: ['തമിഴ്‌നാട്', 'കേരളം', 'കർണാടക', 'ആന്ധ്രാപ്രദേശ്', 'തെലങ്കാന', 'മഹാരാഷ്ട്ര', 'ഉത്തർപ്രദേശ്', 'മധ്യപ്രദേശ്', 'ഗുജറാത്ത്', 'രാജസ്ഥാൻ', 'ബിഹാർ', 'പശ്ചിമ ബംഗാൾ', 'പഞ്ചാബ്', 'ഒഡീഷ', 'ഹരിയാന', 'ഡൽഹി', 'ഛത്തീസ്ഗഢ്', 'അസം', 'ഝാർഖണ്ഡ്', 'ഉത്തരാഖണ്ഡ്', 'ഗോവ', 'ഹിമാചൽ പ്രദേശ്', 'പുതുച്ചേരി', 'ആൻഡമാൻ നിക്കോബാർ', 'ചണ്ഡീഗഢ്']
  };
  const STATES = {};
  SN.forEach((s, i) => { STATES[s] = {}; for (const l in ST) STATES[s][l] = ST[l][i]; });

  // ---------- print text, one block per language ----------
  const kvKeys = ['name', 'dob', 'tob', 'place', 'lagna', 'rasi', 'star', 'pada', 'gothram', 'naz', 'rise', 'ayan'];
  const kv = arr => Object.fromEntries(kvKeys.map((k, i) => [k, arr[i]]));
  const JT = {
    ta: {
      sloka: 'ஜனனீ ஜன்ம ஸௌக்யானாம் வர்த்தனீ குலஸம்பதாம் ।<br>பதவீ பூர்வ புண்யானாம் லிக்யதே ஜன்மபத்ரிகா ॥',
      invo: 'ஸ்ரீ விநாயகர் துணை', title: 'ஜனன ஜாதகம்', navaT: 'நவக்கிரக துணை', navaS: 'ஓம் நவக்கிரஹ தேவதாப்யோ நம:', bhuktiT: 'நடப்பு தசா புக்திகள்',
      dayFull: ['ஞாயிற்றுக்கிழமை', 'திங்கட்கிழமை', 'செவ்வாய்க்கிழமை', 'புதன்கிழமை', 'வியாழக்கிழமை', 'வெள்ளிக்கிழமை', 'சனிக்கிழமை'],
      son: 'புத்திரனாக', daughter: 'புத்திரியாக', child: 'மகவாக', lagnaRow: 'லக்னம்',
      kv: kv(['பெயர்', 'பிறந்த தேதி', 'பிறந்த நேரம்', 'பிறந்த ஊர்', 'லக்னம்', 'ராசி', 'நட்சத்திரம்', 'பாதம்', 'கோத்திரம்', 'உதயாதி நாழிகை', 'சூரிய உதயம்', 'அயனாம்சம்']),
      rasi: 'ராசி', amsam: 'நவாம்சம்', grahaNilai: 'ஜனன கால கிரக நிலை', dasaIruppu: 'ஜனன கால தசா இருப்பு', dasaTitle: 'விம்சோத்தரி மகா தசைகள்',
      th: ['கிரகம்', 'ராசி', 'பாகை', 'நட்சத்திரம்', 'பாதம்', 'நவாம்சம்', 'நிலை'], dth: ['தசை', 'தொடக்கம்', 'முடிவு'],
      panch: 'பஞ்சாங்கக் குறிப்பு', astrologer: 'ஜோதிடர் கையொப்பம்', date: 'தேதி', subham: 'சுபம்',
      blessing: 'ஸர்வே ஜனா: ஸுகினோ பவந்து', note: 'லஹிரி அயனாம்சம் · திருக்கணித முறை · subajathagam.in',
      dasaLine: (lord, y, m, d) => `<b>${lord}</b> தசை இருப்பு <b>${y}</b> வருடம் <b>${m}</b> மாதம் <b>${d}</b> நாள்`,
      prose: x => `ஸ்வஸ்திஸ்ரீ ${x.tam ? `<b>${x.tam.year}</b> வருஷம் <b>${x.tam.month}</b> மாதம் <b>${x.tam.tdate}</b>-ம் தேதி` : `<b>${x.cal}</b>`} (${x.gdate}) <b>${x.day}</b>, ${x.paksha} <b>${x.tithi}</b> திதி, <b>${x.star}</b> நட்சத்திரம் <b>${x.pada}</b>-ம் பாதம், <b>${x.yoga}</b> யோகம், <b>${x.karana}</b> கரணம் கூடிய சுபதினத்தில், சூரிய உதயாதி நாழிகை <b>${x.naz}</b>-க்கு (<b>${x.time}</b> மணிக்கு), <b>${x.place}</b> நகரில், <b>${x.lagna}</b> லக்னத்தில், <b>${x.rasi}</b> ராசியில்${x.parents ? `, ${x.parents}` : ''} <b>${x.name}</b> ஜனனம்.`,
      parents: (f, m, rel) => f && m ? `திரு. <b>${f}</b> — திருமதி. <b>${m}</b> தம்பதியருக்கு ${rel}` : f ? `திரு. <b>${f}</b> அவர்களுக்கு ${rel}` : m ? `திருமதி. <b>${m}</b> அவர்களுக்கு ${rel}` : ''
    },
    ml: {
      invo: 'ഹരിഃ ശ്രീ ഗണപതയേ നമഃ · അവിഘ്നമസ്തു', title: 'ജാതകം', navaT: 'നവഗ്രഹങ്ങൾ', navaS: 'ഓം നവഗ്രഹ ദേവതാഭ്യോ നമഃ', bhuktiT: 'നടപ്പുദശയിലെ അപഹാരങ്ങൾ',
      dayFull: ['ഞായറാഴ്ച', 'തിങ്കളാഴ്ച', 'ചൊവ്വാഴ്ച', 'ബുധനാഴ്ച', 'വ്യാഴാഴ്ച', 'വെള്ളിയാഴ്ച', 'ശനിയാഴ്ച'],
      son: 'പുത്രനായി', daughter: 'പുത്രിയായി', child: 'സന്താനമായി', lagnaRow: 'ലഗ്നം',
      kv: kv(['പേര്', 'ജനനത്തീയതി', 'ജനനസമയം', 'ജനനസ്ഥലം', 'ലഗ്നം', 'രാശി', 'നക്ഷത്രം', 'പാദം', 'ഗോത്രം', 'ഉദയാൽപരം നാഴിക', 'സൂര്യോദയം', 'അയനാംശം']),
      rasi: 'രാശിചക്രം', amsam: 'നവാംശകം', grahaNilai: 'ജനനസമയ ഗ്രഹസ്ഥിതി', dasaIruppu: 'ജനനസമയ ദശാശിഷ്ടം', dasaTitle: 'വിംശോത്തരി മഹാദശകൾ',
      th: ['ഗ്രഹം', 'രാശി', 'ഭാഗ', 'നക്ഷത്രം', 'പാദം', 'നവാംശം', 'സ്ഥിതി'], dth: ['ദശ', 'ആരംഭം', 'അവസാനം'],
      panch: 'ജനനസമയ പഞ്ചാംഗം', astrologer: 'ജ്യോതിഷിയുടെ ഒപ്പ്', date: 'തീയതി', subham: 'ശുഭം',
      blessing: 'സർവേ ജനാഃ സുഖിനോ ഭവന്തു', note: 'ലാഹിരി അയനാംശം · ദൃക്ഗണിതം · subajathagam.in',
      dasaLine: (lord, y, m, d) => `<b>${lord}</b> ദശ ശിഷ്ടം <b>${y}</b> വർഷം <b>${m}</b> മാസം <b>${d}</b> ദിവസം`,
      prose: x => `ശുഭമസ്തു. <b>${x.cal}</b> (${x.gdate}) <b>${x.day}</b>, ${x.paksha} <b>${x.tithi}</b> തിഥി, <b>${x.star}</b> നക്ഷത്രം <b>${x.pada}</b>-ാം പാദം, <b>${x.yoga}</b> യോഗം, <b>${x.karana}</b> കരണം എന്നിവ ചേർന്ന ശുഭദിനത്തിൽ, ഉദയാൽപരം <b>${x.naz}</b> നാഴികയ്ക്ക് (<b>${x.time}</b>), <b>${x.place}</b> എന്ന സ്ഥലത്ത്, <b>${x.lagna}</b> ലഗ്നത്തിൽ, <b>${x.rasi}</b> രാശിയിൽ${x.parents ? `, ${x.parents}` : ''} <b>${x.name}</b> ജനിച്ചു.`,
      parents: (f, m, rel) => f && m ? `ശ്രീ <b>${f}</b>, ശ്രീമതി <b>${m}</b> ദമ്പതികളുടെ ${rel}` : f ? `ശ്രീ <b>${f}</b>-ന്റെ ${rel}` : m ? `ശ്രീമതി <b>${m}</b>-യുടെ ${rel}` : ''
    },
    te: {
      invo: 'శ్రీ గణేశాయ నమః · శ్రీరస్తు శుభమస్తు అవిఘ్నమస్తు', title: 'జన్మ పత్రిక', navaT: 'నవగ్రహ స్తుతి', navaS: 'ఓం నవగ్రహ దేవతాభ్యో నమః', bhuktiT: 'ప్రస్తుత దశలో అంతర్దశలు',
      dayFull: ['ఆదివారం', 'సోమవారం', 'మంగళవారం', 'బుధవారం', 'గురువారం', 'శుక్రవారం', 'శనివారం'],
      son: 'పుత్రునిగా', daughter: 'పుత్రికగా', child: 'సంతానంగా', lagnaRow: 'లగ్నం',
      kv: kv(['పేరు', 'జన్మ తేదీ', 'జన్మ సమయం', 'జన్మ స్థలం', 'లగ్నం', 'రాశి', 'నక్షత్రం', 'పాదం', 'గోత్రం', 'ఉదయాది ఘడియలు', 'సూర్యోదయం', 'అయనాంశ']),
      rasi: 'రాశి చక్రం', amsam: 'నవాంశ చక్రం', grahaNilai: 'జన్మ కాల గ్రహ స్థితి', dasaIruppu: 'జన్మ కాల దశా శేషం', dasaTitle: 'వింశోత్తరి మహాదశలు',
      th: ['గ్రహం', 'రాశి', 'భాగలు', 'నక్షత్రం', 'పాదం', 'నవాంశ', 'స్థితి'], dth: ['దశ', 'ప్రారంభం', 'ముగింపు'],
      panch: 'జన్మ కాల పంచాంగం', astrologer: 'జ్యోతిష్కుని సంతకం', date: 'తేదీ', subham: 'శుభం',
      blessing: 'సర్వే జనాః సుఖినో భవంతు', note: 'లాహిరి అయనాంశ · దృక్ గణితం · subajathagam.in',
      dasaLine: (lord, y, m, d) => `<b>${lord}</b> దశా శేషం <b>${y}</b> సంవత్సరాలు <b>${m}</b> నెలలు <b>${d}</b> రోజులు`,
      prose: x => `స్వస్తి శ్రీ <b>${x.cal}</b> (${x.gdate}) <b>${x.day}</b>, ${x.paksha} <b>${x.tithi}</b> తిథి, <b>${x.star}</b> నక్షత్రం <b>${x.pada}</b>వ పాదం, <b>${x.yoga}</b> యోగం, <b>${x.karana}</b> కరణం కూడిన శుభ దినమున, సూర్యోదయాది <b>${x.naz}</b> ఘడియలకు (<b>${x.time}</b>), <b>${x.place}</b> ప్రాంతంలో, <b>${x.lagna}</b> లగ్నమున, <b>${x.rasi}</b> రాశియందు${x.parents ? `, ${x.parents}` : ''} <b>${x.name}</b> జన్మించెను.`,
      parents: (f, m, rel) => f && m ? `శ్రీ <b>${f}</b>, శ్రీమతి <b>${m}</b> దంపతులకు ${rel}` : f ? `శ్రీ <b>${f}</b> గారికి ${rel}` : m ? `శ్రీమతి <b>${m}</b> గారికి ${rel}` : ''
    },
    kn: {
      invo: 'ಶ್ರೀ ಗಣೇಶಾಯ ನಮಃ · ಶ್ರೀ ಗುರುಭ್ಯೋ ನಮಃ', title: 'ಜನ್ಮ ಕುಂಡಲಿ', navaT: 'ನವಗ್ರಹ ಸ್ತುತಿ', navaS: 'ಓಂ ನವಗ್ರಹ ದೇವತಾಭ್ಯೋ ನಮಃ', bhuktiT: 'ಪ್ರಸ್ತುತ ದಶೆಯ ಭುಕ್ತಿಗಳು',
      dayFull: ['ಭಾನುವಾರ', 'ಸೋಮವಾರ', 'ಮಂಗಳವಾರ', 'ಬುಧವಾರ', 'ಗುರುವಾರ', 'ಶುಕ್ರವಾರ', 'ಶನಿವಾರ'],
      son: 'ಪುತ್ರನಾಗಿ', daughter: 'ಪುತ್ರಿಯಾಗಿ', child: 'ಮಗುವಾಗಿ', lagnaRow: 'ಲಗ್ನ',
      kv: kv(['ಹೆಸರು', 'ಜನ್ಮ ದಿನಾಂಕ', 'ಜನ್ಮ ಸಮಯ', 'ಜನ್ಮ ಸ್ಥಳ', 'ಲಗ್ನ', 'ರಾಶಿ', 'ನಕ್ಷತ್ರ', 'ಪಾದ', 'ಗೋತ್ರ', 'ಉದಯಾದಿ ಘಳಿಗೆ', 'ಸೂರ್ಯೋದಯ', 'ಅಯನಾಂಶ']),
      rasi: 'ರಾಶಿ ಚಕ್ರ', amsam: 'ನವಾಂಶ ಚಕ್ರ', grahaNilai: 'ಜನ್ಮ ಕಾಲದ ಗ್ರಹ ಸ್ಥಿತಿ', dasaIruppu: 'ಜನ್ಮ ಕಾಲದ ದಶಾ ಶೇಷ', dasaTitle: 'ವಿಂಶೋತ್ತರಿ ಮಹಾದಶೆಗಳು',
      th: ['ಗ್ರಹ', 'ರಾಶಿ', 'ಅಂಶ', 'ನಕ್ಷತ್ರ', 'ಪಾದ', 'ನವಾಂಶ', 'ಸ್ಥಿತಿ'], dth: ['ದಶೆ', 'ಆರಂಭ', 'ಅಂತ್ಯ'],
      panch: 'ಜನ್ಮ ಕಾಲದ ಪಂಚಾಂಗ', astrologer: 'ಜ್ಯೋತಿಷಿಗಳ ಸಹಿ', date: 'ದಿನಾಂಕ', subham: 'ಶುಭಮಸ್ತು',
      blessing: 'ಸರ್ವೇ ಜನಾಃ ಸುಖಿನೋ ಭವಂತು', note: 'ಲಾಹಿರಿ ಅಯನಾಂಶ · ದೃಕ್ ಗಣಿತ · subajathagam.in',
      dasaLine: (lord, y, m, d) => `<b>${lord}</b> ದಶಾ ಶೇಷ <b>${y}</b> ವರ್ಷ <b>${m}</b> ತಿಂಗಳು <b>${d}</b> ದಿನ`,
      prose: x => `ಸ್ವಸ್ತಿ ಶ್ರೀ <b>${x.cal}</b> (${x.gdate}) <b>${x.day}</b>, ${x.paksha} <b>${x.tithi}</b> ತಿಥಿ, <b>${x.star}</b> ನಕ್ಷತ್ರ <b>${x.pada}</b>ನೇ ಪಾದ, <b>${x.yoga}</b> ಯೋಗ, <b>${x.karana}</b> ಕರಣ ಕೂಡಿದ ಶುಭ ದಿನದಂದು, ಸೂರ್ಯೋದಯಾದಿ <b>${x.naz}</b> ಘಳಿಗೆಗೆ (<b>${x.time}</b>), <b>${x.place}</b> ಸ್ಥಳದಲ್ಲಿ, <b>${x.lagna}</b> ಲಗ್ನದಲ್ಲಿ, <b>${x.rasi}</b> ರಾಶಿಯಲ್ಲಿ${x.parents ? `, ${x.parents}` : ''} <b>${x.name}</b> ಜನನ.`,
      parents: (f, m, rel) => f && m ? `ಶ್ರೀ <b>${f}</b> ಮತ್ತು ಶ್ರೀಮತಿ <b>${m}</b> ದಂಪತಿಗಳಿಗೆ ${rel}` : f ? `ಶ್ರೀ <b>${f}</b> ಅವರಿಗೆ ${rel}` : m ? `ಶ್ರೀಮತಿ <b>${m}</b> ಅವರಿಗೆ ${rel}` : ''
    },
    hi: {
      invo: '॥ श्री गणेशाय नमः ॥', title: 'जन्म कुण्डली', navaT: 'नवग्रह', navaS: 'ॐ नवग्रहदेवताभ्यो नमः', bhuktiT: 'वर्तमान महादशा की अंतर्दशाएँ',
      dayFull: ['रविवार', 'सोमवार', 'मंगलवार', 'बुधवार', 'गुरुवार', 'शुक्रवार', 'शनिवार'],
      son: 'पुत्र', daughter: 'पुत्री', child: 'संतान', lagnaRow: 'लग्न',
      kv: kv(['नाम', 'जन्म तिथि', 'जन्म समय', 'जन्म स्थान', 'लग्न', 'राशि', 'नक्षत्र', 'चरण', 'गोत्र', 'इष्टकाल (घटी)', 'सूर्योदय', 'अयनांश']),
      rasi: 'लग्न कुण्डली', amsam: 'नवांश कुण्डली', grahaNilai: 'जन्मकालीन ग्रह स्पष्ट', dasaIruppu: 'जन्म समय दशा शेष', dasaTitle: 'विंशोत्तरी महादशा',
      th: ['ग्रह', 'राशि', 'अंश', 'नक्षत्र', 'चरण', 'नवांश', 'स्थिति'], dth: ['दशा', 'आरंभ', 'समाप्ति'],
      panch: 'जन्मकालीन पंचांग', astrologer: 'ज्योतिषी के हस्ताक्षर', date: 'दिनांक', subham: 'शुभम्',
      blessing: 'सर्वे जनाः सुखिनो भवन्तु', note: 'लाहिड़ी अयनांश · दृक् गणित · subajathagam.in',
      dasaLine: (lord, y, m, d) => `<b>${lord}</b> महादशा शेष <b>${y}</b> वर्ष <b>${m}</b> मास <b>${d}</b> दिन`,
      prose: x => `स्वस्ति श्री <b>${x.cal}</b> (${x.gdate}), <b>${x.day}</b>, ${x.paksha} <b>${x.tithi}</b> तिथि, <b>${x.star}</b> नक्षत्र के <b>${x.pada}</b> चरण, <b>${x.yoga}</b> योग एवं <b>${x.karana}</b> करण से युक्त शुभ दिन, सूर्योदय से <b>${x.naz}</b> घटी पर (<b>${x.time}</b> बजे), <b>${x.place}</b> स्थान पर, <b>${x.lagna}</b> लग्न एवं <b>${x.rasi}</b> राशि में${x.parents ? `, ${x.parents}` : ''} <b>${x.name}</b> का जन्म हुआ।`,
      parents: (f, m, rel) => f && m ? `श्री <b>${f}</b> एवं श्रीमती <b>${m}</b> के ${rel}` : f ? `श्री <b>${f}</b> के ${rel}` : m ? `श्रीमती <b>${m}</b> के ${rel}` : ''
    },
    en: {
      invo: 'Sri Vinayagar Thunai', title: 'Janana Jathagam', navaT: 'Navagraha Thunai', navaS: 'Om Navagraha Devatābhyo Namaḥ', bhuktiT: 'Bhuktis of the current dasa',
      sloka: 'Jananī janma saukhyānām vardhanī kula sampadām ।<br>Padavī pūrva puṇyānām likhyate janma patrikā ॥',
      dayFull: ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'],
      son: 'son', daughter: 'daughter', child: 'child', lagnaRow: 'Lagna',
      kv: kv(['Name', 'Date of birth', 'Time of birth', 'Place of birth', 'Lagna', 'Rasi', 'Nakshatra', 'Pada', 'Gothram', 'Ghatis from sunrise', 'Sunrise', 'Ayanamsa']),
      rasi: 'Rasi', amsam: 'Navamsa', grahaNilai: 'Planetary positions at birth', dasaIruppu: 'Dasa balance at birth', dasaTitle: 'Vimshottari Mahadasas',
      th: ['Planet', 'Rasi', 'Degree', 'Nakshatra', 'Pada', 'Navamsa', 'Status'], dth: ['Dasa', 'From', 'To'],
      panch: 'Panchangam at birth', astrologer: 'Astrologer’s signature', date: 'Date', subham: 'Subham',
      blessing: 'Sarve janāḥ sukhino bhavantu', note: 'Lahiri ayanamsa · Drik ganita · subajathagam.in',
      dasaLine: (lord, y, m, d) => `<b>${lord}</b> dasa balance: <b>${y}</b> years <b>${m}</b> months <b>${d}</b> days`,
      prose: x => `Svasti Śrī. ${x.tam ? `In the Tamil year <b>${x.tam.year}</b>, month of <b>${x.tam.month}</b>, day <b>${x.tam.tdate}</b>` : `On <b>${x.cal}</b>`} (${x.gdate}), on <b>${x.day}</b>, in ${x.paksha} <b>${x.tithi}</b> tithi, <b>${x.star}</b> nakshatra pada <b>${x.pada}</b>, <b>${x.yoga}</b> yoga and <b>${x.karana}</b> karana, at <b>${x.naz}</b> ghatis after sunrise (<b>${x.time}</b>), at <b>${x.place}</b>, in <b>${x.lagna}</b> lagna and <b>${x.rasi}</b> rasi, was born <b>${x.name}</b>${x.parents ? `, ${x.parents}` : ''}.`,
      parents: (f, m, rel) => f && m ? `${rel} of Sri <b>${f}</b> and Smt. <b>${m}</b>` : f ? `${rel} of Sri <b>${f}</b>` : m ? `${rel} of Smt. <b>${m}</b>` : ''
    }
  };
  // English print wording follows the chosen tradition
  const EN_TRAD = {
    ta: { invo: 'Sri Vinayagar Thunai', title: 'Janana Jathagam', navaT: 'Navagraha Thunai', note: 'Lahiri ayanamsa · Thirukanitha · subajathagam.in' },
    ml: { invo: 'Harih Sri Ganapataye Namah · Avighnamastu', title: 'Jathakam', navaT: 'Navagrahas' },
    te: { invo: 'Sri Ganeshaya Namah · Srirastu Shubhamastu Avighnamastu', title: 'Janma Patrika', navaT: 'Navagraha Stuti' },
    kn: { invo: 'Sri Ganeshaya Namah · Sri Gurubhyo Namah', title: 'Janma Kundali', navaT: 'Navagraha Stuti' },
    hi: { invo: '॥ Shri Ganeshaya Namah ॥', title: 'Janma Kundali', navaT: 'Navagraha' }
  };

  // ---------- print themes (by tradition) and sacred symbols (by script) ----------
  const LAMP = `<svg width="15mm" height="22mm" viewBox="0 0 60 88" aria-hidden="true">
  <defs><radialGradient id="fl" cx="50%" cy="70%" r="60%"><stop offset="0" stop-color="#fff7c2"/><stop offset=".45" stop-color="#ffc233"/><stop offset="1" stop-color="#e2461b"/></radialGradient>
  <linearGradient id="br" x1="0" x2="1"><stop offset="0" stop-color="#9a6a12"/><stop offset=".5" stop-color="#f1cf6a"/><stop offset="1" stop-color="#9a6a12"/></linearGradient></defs>
  <ellipse cx="30" cy="13" rx="10" ry="12" fill="#ffd966" opacity=".35"/>
  <path d="M30 2 C35 10 36 16 30 22 C24 16 25 10 30 2Z" fill="url(#fl)"/>
  <path d="M12 26 Q30 36 48 26 Q46 33 30 34 Q14 33 12 26Z" fill="url(#br)"/>
  <rect x="27" y="34" width="6" height="34" rx="2" fill="url(#br)"/>
  <circle cx="30" cy="44" r="4.5" fill="url(#br)"/><circle cx="30" cy="57" r="3.5" fill="url(#br)"/>
  <path d="M14 82 Q30 64 46 82Z" fill="url(#br)"/><rect x="10" y="81" width="40" height="5" rx="2" fill="url(#br)"/>
</svg>`;
  // Kerala nilavilakku: tall brass lamp, several wicks
  const NILA = `<svg width="15mm" height="23mm" viewBox="0 0 60 92" aria-hidden="true">
  <defs><radialGradient id="nfl" cx="50%" cy="70%" r="60%"><stop offset="0" stop-color="#fff7c2"/><stop offset=".45" stop-color="#ffc233"/><stop offset="1" stop-color="#e2461b"/></radialGradient>
  <linearGradient id="nbr" x1="0" x2="1"><stop offset="0" stop-color="#8a5c0c"/><stop offset=".5" stop-color="#f3d77a"/><stop offset="1" stop-color="#8a5c0c"/></linearGradient></defs>
  <ellipse cx="30" cy="12" rx="22" ry="9" fill="#ffd966" opacity=".28"/>
  <path d="M30 2 C33 7 34 11 30 15 C26 11 27 7 30 2Z" fill="url(#nfl)"/>
  <path d="M14 7 C17 11 17 14 14 17 C11 14 11 11 14 7Z" fill="url(#nfl)"/><path d="M46 7 C49 11 49 14 46 17 C43 14 43 11 46 7Z" fill="url(#nfl)"/>
  <path d="M6 17 Q30 28 54 17 Q52 25 30 26 Q8 25 6 17Z" fill="url(#nbr)"/>
  <path d="M27 6 L30 0 L33 6Z" fill="url(#nbr)" opacity=".0"/>
  <rect x="27.5" y="26" width="5" height="50" rx="2" fill="url(#nbr)"/>
  <circle cx="30" cy="36" r="4" fill="url(#nbr)"/><ellipse cx="30" cy="50" rx="6" ry="3" fill="url(#nbr)"/><circle cx="30" cy="63" r="3.5" fill="url(#nbr)"/>
  <path d="M12 88 Q30 70 48 88Z" fill="url(#nbr)"/><rect x="8" y="87" width="44" height="4.5" rx="2" fill="url(#nbr)"/>
</svg>`;
  // Purna kalasha: brass pot, mango leaves, coconut
  const KALASH = `<svg width="15mm" height="22mm" viewBox="0 0 60 88" aria-hidden="true">
  <defs><linearGradient id="kbr" x1="0" x2="1"><stop offset="0" stop-color="#9a6a12"/><stop offset=".5" stop-color="#f1cf6a"/><stop offset="1" stop-color="#9a6a12"/></linearGradient></defs>
  <path d="M30 31 Q20 15 9 17 Q17 28 30 32Z" fill="#2f6b22"/><path d="M30 31 Q40 15 51 17 Q43 28 30 32Z" fill="#2f6b22"/>
  <path d="M30 32 Q15 23 4 30 Q17 36 30 33Z" fill="#3f8a2e"/><path d="M30 32 Q45 23 56 30 Q43 36 30 33Z" fill="#3f8a2e"/>
  <ellipse cx="30" cy="20" rx="9" ry="11" fill="#8a5a2b"/><path d="M24 14 Q30 10 36 14" stroke="#6b4420" stroke-width="1.2" fill="none"/>
  <path d="M30 9 Q33 4 30 1 Q27 4 30 9Z" fill="#6b4420"/>
  <path d="M21 33 h18 l-1.5 5 Q52 45 50 61 Q48 78 30 80 Q12 78 10 61 Q8 45 22.5 38Z" fill="url(#kbr)"/>
  <path d="M12 54 Q30 61 48 54" stroke="#c1121f" stroke-width="2.2" fill="none"/>
  <circle cx="30" cy="67" r="3.2" fill="#c1121f"/><circle cx="21" cy="64" r="1.6" fill="#f0b91e"/><circle cx="39" cy="64" r="1.6" fill="#f0b91e"/>
  <rect x="18" y="80" width="24" height="5" rx="2" fill="url(#kbr)"/>
</svg>`;
  const SWASTIK = `<svg width="12mm" height="12mm" viewBox="0 0 40 40" aria-hidden="true"><g stroke="#c1121f" stroke-width="3.4" fill="none" stroke-linecap="square"><path d="M20 6v28M6 20h28M20 6h12M34 20v12M20 34H8M6 20V8"/></g><g fill="#c1121f"><circle cx="13" cy="13" r="2.2"/><circle cx="27" cy="13" r="2.2"/><circle cx="13" cy="27" r="2.2"/><circle cx="27" cy="27" r="2.2"/></g></svg>`;
  // symbols follow the script of the text; English follows the tradition
  const SYM = {
    ta: { top: 'உ', om: 'ௐ', side: LAMP },
    ml: { top: 'ശ്രീ', om: 'ഓം', side: NILA },
    te: { top: 'శ్రీ', om: 'ఓం', side: KALASH },
    kn: { top: 'ಶ್ರೀ', om: 'ಓಂ', side: KALASH },
    hi: { top: SWASTIK, om: 'ॐ', side: KALASH, svgTop: true }
  };

  root.SJC = { LANGS, TRADS, PANCH_HOME, POPULAR, NAT_IDX, COUNTRY, STATES, JT, EN_TRAD, SYM, LAMP };
})(typeof window !== 'undefined' ? window : globalThis);
