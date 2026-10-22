"""Multilingual names, labels & 100% full-page neural + dictionary translation:
Hindi, Marathi, Gujarati, Bengali, Tamil, Telugu, Kannada, Malayalam.

- Protects sacred Sanskrit Shlokas & Mantras (both Devanagari and IAST/transliteration) from being altered,
  while translating their meanings/explanations and 100% of the page UI & report text into the selected language.
- Preserves explicit AM / PM time markers across all languages.
- Uses an in-memory + persistent SQLite cache (`i18n_cache.sqlite`) + parallel batched translation.
"""
from __future__ import annotations
from concurrent.futures import ThreadPoolExecutor
import html as _html
import os
import re
import sqlite3
import threading
from typing import Any, Dict, List, Tuple
import httpx

LANGS = {
    "en": "English",
    "hi": "हिन्दी",
    "mr": "मराठी",
    "gu": "ગુજરાતી",
    "bn": "বাংলা",
    "ta": "தமிழ்",
    "te": "తెలుగు",
    "kn": "ಕನ್ನಡ",
    "ml": "മലയാളം",
}

EN = {
    "planets": "Sun,Moon,Mars,Mercury,Jupiter,Venus,Saturn,Rahu,Ketu",
    "signs": "Aries,Taurus,Gemini,Cancer,Leo,Virgo,Libra,Scorpio,Sagittarius,Capricorn,Aquarius,Pisces",
    "rashis": "Mesha,Vrishabha,Mithuna,Karka,Simha,Kanya,Tula,Vrishchika,Dhanu,Makara,Kumbha,Meena",
    "nakshatras": "Ashwini,Bharani,Krittika,Rohini,Mrigashira,Ardra,Punarvasu,Pushya,Ashlesha,Magha,Purva Phalguni,Uttara Phalguni,Hasta,Chitra,Swati,Vishakha,Anuradha,Jyeshtha,Mula,Purva Ashadha,Uttara Ashadha,Shravana,Dhanishta,Shatabhisha,Purva Bhadrapada,Uttara Bhadrapada,Revati",
    "tithis": "Pratipada,Dwitiya,Tritiya,Chaturthi,Panchami,Shashthi,Saptami,Ashtami,Navami,Dashami,Ekadashi,Dwadashi,Trayodashi,Chaturdashi,Purnima,Amavasya",
    "weekdays": "Sunday,Monday,Tuesday,Wednesday,Thursday,Friday,Saturday",
    "varas": "Ravivara,Somavara,Mangalavara,Budhavara,Guruvara,Shukravara,Shanivara",
    "paksha": "Shukla,Krishna",
    "months": "Chaitra,Vaishakha,Jyeshtha,Ashadha,Shravana,Bhadrapada,Ashwin,Kartika,Margashirsha,Pausha,Magha,Phalguna",
    "yogas": "Vishkambha,Priti,Ayushman,Saubhagya,Shobhana,Atiganda,Sukarma,Dhriti,Shula,Ganda,Vriddhi,Dhruva,Vyaghata,Harshana,Vajra,Siddhi,Vyatipata,Variyana,Parigha,Shiva,Siddha,Sadhya,Shubha,Shukla,Brahma,Indra,Vaidhriti",
    "karanas": "Bava,Balava,Kaulava,Taitila,Garaja,Vanija,Vishti,Shakuni,Chatushpada,Naga,Kimstughna",
    "ritus": "Vasanta,Grishma,Varsha,Sharad,Hemanta,Shishira",
    "ayana": "Uttarayana,Dakshinayana",
    "dirs": "East,West,North,South",
}

T: Dict[str, Dict[str, str]] = {}
T["hi"] = {
    "planets": "सूर्य,चंद्र,मंगल,बुध,गुरु,शुक्र,शनि,राहु,केतु",
    "signs": "मेष,वृषभ,मिथुन,कर्क,सिंह,कन्या,तुला,वृश्चिक,धनु,मकर,कुंभ,मीन",
    "nakshatras": "अश्विनी,भरणी,कृत्तिका,रोहिणी,मृगशिरा,आर्द्रा,पुनर्वसु,पुष्य,आश्लेषा,मघा,पूर्वा फाल्गुनी,उत्तरा फाल्गुनी,हस्त,चित्रा,स्वाती,विशाखा,अनुराधा,ज्येष्ठा,मूल,पूर्वाषाढ़ा,उत्तराषाढ़ा,श्रवण,धनिष्ठा,शतभिषा,पूर्व भाद्रपद,उत्तर भाद्रपद,रेवती",
    "tithis": "प्रतिपदा,द्वितीया,तृतीया,चतुर्थी,पंचमी,षष्ठी,सप्तमी,अष्टमी,नवमी,दशमी,एकादशी,द्वादशी,त्रयोदशी,चतुर्दशी,पूर्णिमा,अमावस्या",
    "weekdays": "रविवार,सोमवार,मंगलवार,बुधवार,गुरुवार,शुक्रवार,शनिवार",
    "paksha": "शुक्ल,कृष्ण",
    "months": "चैत्र,वैशाख,ज्येष्ठ,आषाढ़,श्रावण,भाद्रपद,आश्विन,कार्तिक,मार्गशीर्ष,पौष,माघ,फाल्गुन",
    "yogas": "विष्कम्भ,प्रीति,आयुष्मान,सौभाग्य,शोभन,अतिगण्ड,सुकर्मा,धृति,शूल,गण्ड,वृद्धि,ध्रुव,व्याघात,हर्षण,वज्र,सिद्धि,व्यतीपात,वरीयान,परिघ,शिव,सिद्ध,साध्य,शुभ,शुक्ल,ब्रह्म,इन्द्र,वैधृति",
    "karanas": "बव,बालव,कौलव,तैतिल,गर,वणिज,विष्टि,शकुनि,चतुष्पद,नाग,किंस्तुघ्न",
    "ritus": "वसंत,ग्रीष्म,वर्षा,शरद,हेमंत,शिशिर",
    "ayana": "उत्तरायण,दक्षिणायन",
    "dirs": "पूर्व,पश्चिम,उत्तर,दक्षिण",
}
T["mr"] = dict(T["hi"], **{
    "planets": "सूर्य,चंद्र,मंगळ,बुध,गुरु,शुक्र,शनि,राहु,केतु",
    "weekdays": "रविवार,सोमवार,मंगळवार,बुधवार,गुरुवार,शुक्रवार,शनिवार",
    "months": "चैत्र,वैशाख,ज्येष्ठ,आषाढ,श्रावण,भाद्रपद,आश्विन,कार्तिक,मार्गशीर्ष,पौष,माघ,फाल्गुन",
    "nakshatras": "अश्विनी,भरणी,कृत्तिका,रोहिणी,मृग,आर्द्रा,पुनर्वसू,पुष्य,आश्लेषा,मघा,पूर्वा फाल्गुनी,उत्तरा फाल्गुनी,हस्त,चित्रा,स्वाती,विशाखा,अनुराधा,ज्येष्ठा,मूळ,पूर्वाषाढा,उत्तराषाढा,श्रवण,धनिष्ठा,शततारका,पूर्वा भाद्रपदा,उत्तरा भाद्रपदा,रेवती",
})
T["gu"] = {
    "planets": "સૂર્ય,ચંદ્ર,મંગળ,બુધ,ગુરુ,શુક્ર,શનિ,રાહુ,કેતુ",
    "signs": "મેષ,વૃષભ,મિથુન,કર્ક,સિંહ,કન્યા,તુલા,વૃશ્ચિક,ધનુ,મકર,કુંભ,મીન",
    "nakshatras": "અશ્વિની,ભરણી,કૃત્તિકા,રોહિણી,મૃગશીર્ષ,આર્દ્રા,પુનર્વસુ,પુષ્ય,આશ્લેષા,મઘા,પૂર્વા ફાલ્ગુની,ઉત્તરા ફાલ્ગુની,હસ્ત,ચિત્રા,સ્વાતિ,વિશાખા,અનુરાધા,જ્યેષ્ઠા,મૂળ,પૂર્વાષાઢા,ઉત્તરાષાઢા,શ્રવણ,ધનિષ્ઠા,શતભિષા,પૂર્વા ભાદ્રપદ,ઉત્તરા ભાદ્રપદ,રેવતી",
    "tithis": "પડવો,બીજ,ત્રીજ,ચોથ,પાંચમ,છઠ,સાતમ,આઠમ,નોમ,દશમ,અગિયારસ,બારસ,તેરસ,ચૌદસ,પૂનમ,અમાસ",
    "weekdays": "રવિવાર,સોમવાર,મંગળવાર,બુધવાર,ગુરુવાર,શુક્રવાર,શનિવાર",
    "paksha": "શુક્લ,કૃષ્ણ",
    "months": "ચैત્ર,વૈશાખ,જેઠ,અષાઢ,શ્રાવણ,ભાદરવો,આસો,કારતક,માગશર,પોષ,મહા,ફાગણ",
    "yogas": "વિષ્કંભ,પ્રીતિ,આયુષ્માન,સૌભાગ્ય,શોભન,અતિગંડ,સુકર્મા,ધૃતિ,શૂળ,ગંડ,વૃદ્ધિ,ધ્રુવ,વ્યાઘાત,હર્ષણ,વજ્ર,સિદ્ધિ,વ્યતીપાત,વરીયાન,પરિઘ,શિવ,સિદ્ધ,સાધ્ય,શુભ,શુક્લ,બ્રહ્મ,ઇન્દ્ર,વૈધૃતિ",
    "karanas": "બવ,બાલવ,કૌલવ,તૈતિલ,ગર,વણિજ,વિષ્ટિ,શકુનિ,ચતુષ્પદ,નાગ,કિંસ્તુઘ્ન",
    "ritus": "વસંત,ગ્રીષ્મ,વર્ષા,શરદ,હેમંત,શિશિર",
    "ayana": "ઉત્તરાયણ,દક્ષિણાયન",
    "dirs": "પૂર્વ,પશ્ચિમ,ઉત્તર,દક્ષિણ",
}
T["bn"] = {
    "planets": "সূর্য,চন্দ্র,মঙ্গল,বুধ,বৃহস্পতি,শুক্র,শনি,রাহু,কেতু",
    "signs": "মেষ,বৃষ,মিথুন,কর্কট,সিংহ,কন্যা,তুলা,বৃশ্চিক,ধনু,মকর,কুম্ভ,মীন",
    "nakshatras": "অশ্বিনী,ভরণী,কৃত্তিকা,রোহিণী,মৃগশিরা,আর্দ্রা,পুনর্বসু,পুষ্যা,অশ্লেষা,মঘা,পূর্বফাল্গুনী,উত্তরফাল্গুনী,হস্তা,চিত্রা,স্বাতী,বিশাখা,অনুরাধা,জ্যেষ্ঠা,মূলা,পূর্বাষাঢ়া,উত্তরাষাঢ়া,শ্রবণা,ধনিষ্ঠা,শতভিষা,পূর্বভাদ্রপদ,উত্তরভাদ্রপদ,রেবতী",
    "tithis": "প্রতিপদ,দ্বিতীয়া,তৃতীয়া,চতুর্থী,পঞ্চমী,ষষ্ঠী,সপ্তমী,অষ্টমী,নবমী,দশমী,একাদশী,দ্বাদশী,ত্রয়োদশী,চতুর্দশী,পূর্ণিমা,অমাবস্যা",
    "weekdays": "রবিবার,সোমবার,মঙ্গলবার,বুধবার,বৃহস্পতিবার,শুক্রবার,শনিবার",
    "paksha": "শুক্ল,কৃষ্ণ",
    "months": "চৈত্র,বৈশাখ,জ্যৈষ্ঠ,আষাঢ়,শ্রাবণ,ভাদ্র,আশ্বিন,কার্তিক,অগ্রহায়ণ,পৌষ,মাঘ,ফাল্গুন",
    "yogas": "বিষ্কম্ভ,প্রীতি,আয়ুষ্মান,সৌভাগ্য,শোভন,অতিগণ্ড,সুকর্মা,ধৃতি,শূল,গণ্ড,বৃদ্ধি,ধ্রুব,ব্যাঘাত,হর্ষণ,বজ্র,সিদ্ধি,ব্যতীপাত,বরীয়ান,পরিঘ,শিব,সিদ্ধ,সাধ্য,শুভ,শুক্ল,ব্রহ্ম,ইন্দ্র,বৈধৃতি",
    "karanas": "বব,বালব,কৌলব,তৈতিল,গর,বণিজ,বিষ্টি,শকুনি,চতুষ্পদ,নাগ,কিংস্তুঘ্ন",
    "ritus": "বসন্ত,গ্রীষ্ম,বর্ষা,শরৎ,হেমন্ত,শীত",
    "ayana": "উত্তরায়ণ,দক্ষিণায়ন",
    "dirs": "পূর্ব,পশ্চিম,উত্তর,দক্ষিণ",
}
T["ta"] = {
    "planets": "சூரியன்,சந்திரன்,செவ்வாய்,புதன்,குரு,சுக்கிரன்,சனி,ராகு,கேது",
    "signs": "மேஷம்,ரிஷபம்,மிதுனம்,கடகம்,சிம்மம்,கன்னி,துலாம்,விருச்சிகம்,தனுசு,மகரம்,கும்பம்,மீனம்",
    "nakshatras": "அஸ்வினி,பரணி,கிருத்திகை,ரோகிணி,மிருகசீரிடம்,திருவாதிரை,புனர்பூசம்,பூசம்,ஆயில்யம்,மகம்,பூரம்,உத்திரம்,அஸ்தம்,சித்திரை,சுவாதி,விசாகம்,அனுஷம்,கேட்டை,மூலம்,பூராடம்,உத்திராடம்,திருவோணம்,அவிட்டம்,சதயம்,பூரட்டாதி,உத்திரட்டாதி,ரேவதி",
    "tithis": "பிரதமை,துவிதியை,திருதியை,சதுர்த்தி,பஞ்சமி,சஷ்டி,சப்தமி,அஷ்டமி,நவமி,தசமி,ஏகாதசி,துவாதசி,திரயோதசி,சதுர்த்தசி,பௌர்ணமி,அமாவாசை",
    "weekdays": "ஞாயிறு,திங்கள்,செவ்வாய்,புதன்,வியாழன்,வெள்ளி,சனி",
    "paksha": "சுக்ல,கிருஷ்ண",
    "months": "சைத்ரம்,வைசாகம்,ஜ்யேஷ்டம்,ஆஷாடம்,ஸ்ராவணம்,பாத்ரபதம்,ஆஸ்வயுஜம்,கார்த்திகம்,மார்கசீர்ஷம்,புஷ்யம்,மாகம்,பால்குனம்",
    "yogas": "விஷ்கம்பம்,ப்ரீதி,ஆயுஷ்மான்,சௌபாக்கியம்,சோபனம்,அதிகண்டம்,சுகர்மம்,திருதி,சூலம்,கண்டம்,விருத்தி,துருவம்,வியாகாதம்,ஹர்ஷணம்,வஜ்ரம்,சித்தி,வியதீபாதம்,வரீயான்,பரிகம்,சிவம்,சித்தம்,சாத்தியம்,சுபம்,சுக்லம்,பிரம்மம்,இந்திரம்,வைதிருதி",
    "karanas": "பவம்,பாலவம்,கௌலவம்,தைதுலம்,கரசை,வணிசை,பத்திரை,சகுனி,சதுஷ்பாதம்,நாகவம்,கிம்ஸ்துக்னம்",
    "ritus": "வசந்த,கிரீஷ்ம,வர்ஷ,சரத்,ஹேமந்த,சிசிர",
    "ayana": "உத்தராயணம்,தட்சிணாயனம்",
    "dirs": "கிழக்கு,மேற்கு,வடக்கு,தெற்கு",
}
T["te"] = {
    "planets": "సూర్యుడు,చంద్రుడు,కుజుడు,బుధుడు,గురువు,శుక్రుడు,శని,రాహువు,కేతువు",
    "signs": "మేషం,వృషభం,మిథునం,కర్కాటకం,సింహం,కన్య,తుల,వృశ్చికం,ధనుస్సు,మకరం,కుంభం,మీనం",
    "nakshatras": "అశ్విని,భరణి,కృత్తిక,రోహిణి,మృగశిర,ఆర్ద్ర,పునర్వసు,పుష్యమి,ఆశ్లేష,మఖ,పుబ్బ,ఉత్తర,హస్త,చిత్త,స్వాతి,విశాఖ,అనూరాధ,జ్యేష్ఠ,మూల,పూర్వాషాఢ,ఉత్తరాషాఢ,శ్రవణం,ధనిష్ఠ,శతభిషం,పూర్వాభాద్ర,ఉత్తరాభాద్ర,రేవతి",
    "tithis": "పాడ్యమి,విదియ,తదియ,చవితి,పంచమి,షష్ఠి,సప్తమి,అష్టమి,నవమి,దశమి,ఏకాదశి,ద్వాదశి,త్రయోదశి,చతుర్దశి,పౌర్ణమి,అమావాస్య",
    "weekdays": "ఆదివారం,సోమవారం,మంగళవారం,బుధవారం,గురువారం,శుక్రవారం,శనివారం",
    "paksha": "శుక్ల,కృష్ణ",
    "months": "చైత్రం,వైశాఖం,జ్యేష్ఠం,ఆషాఢం,శ్రావణం,భాద్రపదం,ఆశ్వయుజం,కార్తీకం,మార్గశిరం,పుష్యం,మాఘం,ఫాల్గుణం",
    "yogas": "విష్కంభ,ప్రీతి,ఆయుష్మాన్,సౌభాగ్య,శోభన,అతిగండ,సుకర్మ,ధృతి,శూల,గండ,వృద్ధి,ధ్రువ,వ్యాఘాత,హర్షణ,వజ్ర,సిద్ధి,వ్యతీపాత,వరీయాన్,పరిఘ,శివ,సిద్ధ,సాధ్య,శుభ,శుక్ల,బ్రహ్మ,ఇంద్ర,వైధృతి",
    "karanas": "బవ,బాలవ,కౌలవ,తైతిల,గరజ,వణిజ,విష్టి,శకుని,చతుష్పాద,నాగ,కింస్తుఘ్న",
    "ritus": "వసంత,గ్రీష్మ,వర్ష,శరద్,హేమంత,శిశిర",
    "ayana": "ఉత్తరాయణం,దక్షిణాయనం",
    "dirs": "తూర్పు,పడమర,ఉత్తరం,దక్షిణం",
}
T["kn"] = {
    "planets": "ಸೂರ್ಯ,ಚಂದ್ರ,ಮಂಗಳ,ಬುಧ,ಗುರು,ಶುಕ್ರ,ಶನಿ,ರಾಹು,ಕೇತು",
    "signs": "ಮೇಷ,ವೃಷಭ,ಮಿಥುನ,ಕರ್ಕಾಟಕ,ಸಿಂಹ,ಕನ್ಯಾ,ತುಲಾ,ವೃಶ್ಚಿಕ,ಧನು,ಮಕರ,ಕುಂಭ,ಮೀನ",
    "nakshatras": "ಅಶ್ವಿನಿ,ಭರಣಿ,ಕೃತ್ತಿಕಾ,ರೋಹಿಣಿ,ಮೃಗಶಿರಾ,ಆರ್ದ್ರಾ,ಪುನರ್ವಸು,ಪುಷ್ಯ,ಆಶ್ಲೇಷಾ,ಮಘಾ,ಪೂರ್ವ ಫಾಲ್ಗುಣಿ,ಉತ್ತರ ಫಾಲ್ಗುಣಿ,ಹಸ್ತ,ಚಿತ್ರಾ,ಸ್ವಾತಿ,ವಿಶಾಖಾ,ಅನುರಾಧಾ,ಜ್ಯೇಷ್ಠಾ,ಮೂಲಾ,ಪೂರ್ವಾಷಾಢಾ,ಉತ್ತರಾಷಾಢಾ,ಶ್ರವಣ,ಧನಿಷ್ಠಾ,ಶತಭಿಷ,ಪೂರ್ವಾಭಾದ್ರ,ಉತ್ತರಾಭಾದ್ರ,ರೇವತಿ",
    "tithis": "ಪಾಡ್ಯ,ಬಿದಿಗೆ,ತದಿಗೆ,ಚೌತಿ,ಪಂಚಮಿ,ಷಷ್ಠಿ,ಸಪ್ತಮಿ,ಅಷ್ಟಮಿ,ನವಮಿ,ದಶಮಿ,ಏಕಾದಶಿ,ದ್ವಾದಶಿ,ತ್ರಯೋದಶಿ,ಚತುರ್ದಶಿ,ಹುಣ್ಣಿಮೆ,ಅಮಾವಾಸ್ಯೆ",
    "weekdays": "ಭಾನುವಾರ,ಸೋಮವಾರ,ಮಂಗಳವಾರ,ಬುಧವಾರ,ಗುರುವಾರ,ಶುಕ್ರವಾರ,ಶನಿವಾರ",
    "paksha": "ಶುಕ್ಲ,ಕೃಷ್ಣ",
    "months": "ಚೈತ್ರ,ವೈಶಾಖ,ಜ್ಯೇಷ್ಠ,ಆಷಾಢ,ಶ್ರಾವಣ,ಭಾದ್ರಪದ,ಆಶ್ವಯುಜ,ಕಾರ್ತಿಕ,ಮಾರ್ಗಶಿರ,ಪುಷ್ಯ,ಮಾಘ,ಫಾಲ್ಗುಣ",
    "yogas": "ವಿಷ್ಕಂಭ,ಪ್ರೀತಿ,ಆಯುಷ್ಮಾನ್,ಸೌಭಾಗ್ಯ,ಶೋಭನ,ಅತಿಗಂಡ,ಸುಕರ್ಮ,ಧೃತಿ,ಶೂಲ,ಗಂಡ,ವೃದ್ಧಿ,ಧ್ರುವ,ವ್ಯಾಘಾತ,ಹರ್ಷಣ,ವಜ್ರ,ಸಿದ್ಧಿ,ವ್ಯತೀಪಾತ,ವರೀಯಾನ್,ಪರಿಘ,ಶಿವ,ಸಿದ್ಧ,ಸಾಧ್ಯ,ಶುಭ,ಶುಕ್ಲ,ಬ್ರಹ್ಮ,ಇಂದ್ರ,ವೈಧೃತಿ",
    "karanas": "ಬವ,ಬಾಲವ,ಕೌಲವ,ತೈತಿಲ,ಗರಜ,ವಣಿಜ,ವಿಷ್ಟಿ,ಶಕುನಿ,ಚತುಷ್ಪಾದ,ನಾಗ,ಕಿಂಸ್ತುಘ್ನ",
    "ritus": "ವಸಂತ,ಗ್ರೀಷ್ಮ,ವರ್ಷ,ಶರದ್,ಹೇಮಂತ,ಶಿಶಿರ",
    "ayana": "ಉತ್ತರಾಯಣ,ದಕ್ಷಿಣಾಯನ",
    "dirs": "ಪೂರ್ವ,ಪಶ್ಚಿಮ,ಉತ್ತರ,ದಕ್ಷಿಣ",
}
T["ml"] = {
    "planets": "സൂര്യൻ,ചന്ദ്രൻ,ചൊവ്വ,ബുധൻ,വ്യാഴം,ശുക്രൻ,ശനി,രാഹു,കേതു",
    "signs": "മേടം,ഇടവം,മിഥുനം,കർക്കടകം,ചിങ്ങം,കന്നി,തുലാം,വൃശ്ചികം,ധനു,മകരം,കുംഭം,മീനം",
    "nakshatras": "അശ്വതി,ഭരണി,കാർത്തിക,രോഹിണി,മകയിരം,തിരുവാതിര,പുണർതം,പൂയം,ആയില്യം,മകം,പൂരം,ഉത്രം,അത്തം,ചിത്തിര,ചോതി,വിശാഖം,അനിഴം,തൃക്കേട്ട,മൂലം,പൂരാടം,ഉത്രാടം,തിരുവോണം,അവിട്ടം,ചതയം,പൂരുരുട്ടാതി,ഉത്രട്ടാതി,രേവതി",
    "tithis": "പ്രഥമ,ദ്വിതീയ,തൃതീയ,ചതുർത്ഥി,പഞ്ചമി,ഷഷ്ഠി,സപ്തമി,അഷ്ടമി,നവമി,ദശമി,ഏകാദശി,ദ്വാദശി,ത്രയോദശി,ചതുർദശി,പൗർണമി,അമാവാസി",
    "weekdays": "ഞായർ,തിങ്കൾ,ചൊവ്വ,ബുധൻ,വ്യാഴം,വെള്ളി,ശനി",
    "paksha": "ശുക്ല,കൃഷ്ണ",
    "months": "ചൈത്രം,വൈശാഖം,ജ്യേഷ്ഠം,ആഷാഢം,ശ്രാവണം,ഭാദ്രപദം,ആശ്വിനം,കാർത്തികം,മാർഗശീർഷം,പൗഷം,മാഘം,ഫാൽഗുനം",
    "yogas": "വിഷ്കംഭം,പ്രീതി,ആയുഷ്മാൻ,സൗഭാഗ്യം,ശോഭനം,അതിഗണ്ഡം,സുകർമ്മം,ധൃതി,ശൂലം,ഗണ്ഡം,വൃദ്ധി,ധ്രുവം,വ്യാഘാതം,ഹർഷണം,വജ്രം,സിദ്ധി,വ്യതീപാതം,വരീയാൻ,പരിഘം,ശിവം,സിദ്ധം,സാധ്യം,ശുഭം,ശുക്ലം,ബ്രഹ്മം,ഇന്ദ്രം,വൈധൃതി",
    "karanas": "ബവം,ബാലവം,കൗലവം,തൈതിലം,ഗരജം,വണിജം,വിഷ്ടി,ശകുനി,ചതുഷ്പാദം,നാഗം,കിംസ്തുഘ്നം",
    "ritus": "വസന്തം,ഗ്രീഷ്മം,വർഷം,ശരത്,ഹേമന്തം,ശിശിരം",
    "ayana": "ഉത്തരായണം,ദക്ഷിണായനം",
    "dirs": "കിഴക്ക്,പടിഞ്ഞാറ്,വടക്ക്,തെക്ക്",
}

# UI labels for the website
LABELS_EN = [
    "Home", "Panchang", "Calendar", "Choghadiya", "Hora", "Rahu Kaal", "Festivals", "Kundli", "Matching", "Muhurat",
    "Transits", "Sunrise", "Sunset", "Moonrise", "Moonset", "Tithi", "Nakshatra", "Yoga", "Karana", "Paksha",
    "Weekday", "Month", "Today's Panchang", "Auspicious Timings", "Inauspicious Timings", "Language", "Horoscope", "Planet", "Sign", "House",
    "Prashna", "Horary", "Soul Guidance", "Atmakaraka", "Karakamsha", "Ishta Devata", "Dharma Devata", "Palana Devata", "Purushartha", "Mantras", "Remedies", "Sign In", "Sign Out", "Register", "Verified", "Divisional Charts",
]
LABELS = {
    "hi": "होम,पंचांग,कैलेंडर,चौघड़िया,होरा,राहु काल,त्योहार,कुंडली,मिलान,मुहूर्त,गोचर,सूर्योदय,सूर्यास्त,चंद्रोदय,चंद्रास्त,तिथि,नक्षत्र,योग,करण,पक्ष,वार,मास,आज का पंचांग,शुभ मुहूर्त,अशुभ समय,भाषा,राशिफल,ग्रह,राशि,भाव,प्रश्न,होरी,आत्म मार्गदर्शन,आत्मकारक,कारकांश,इष्ट देवता,धर्म देवता,पालन देवता,पुरुषार्थ,मंत्र,उपाय,साइन इन,साइन आउट,पंजीकरण,सत्यापित,वर्ग कुंडलियां",
    "mr": "मुख्यपृष्ठ,पंचांग,दिनदर्शिका,चौघडिया,होरा,राहू काळ,सण,कुंडली,गुणमिलन,मुहूर्त,गोचर,सूर्योदय,सूर्यास्त,चंद्रोदय,चंद्रास्त,तिथी,नक्षत्र,योग,करण,पक्ष,वार,महिना,आजचे पंचांग,शुभ वेळा,अशुभ वेळा,भाषा,राशिभविष्य,ग्रह,राशी,स्थान,प्रश्न,होरी,आत्म मार्गदर्शन,आत्मकारक,कारकांश,इष्ट देवता,धर्म देवता,पालन देवता,पुरुषार्थ,मंत्र,उपाय,साइन इन,साइन आउट,नोंदणी,सत्यापित,वर्ग कुंडल्या",
    "gu": "હોમ,પંચાંગ,કેલેન્ડર,ચોઘડિયા,હોરા,રાહુ કાળ,તહેવારો,કુંડળી,મેળાપક,મુહૂર્ત,ગોચર,સૂર્યોદય,સૂર્યાસ્ત,ચંદ્રોદય,ચંદ્રાસ્ત,તિથિ,નક્ષત્ર,યોગ,કરણ,પક્ષ,વાર,માસ,આજનું પંચાંગ,શુભ સમય,અશુભ સમય,ભાષા,રાશિફળ,ગ્રહ,રાશિ,ભાવ,પ્રશ્ન,હોરી,આત્મ માર્ગદર્શન,આત્મકારક,કારકાંશ,ઇષ્ટ દેવતા,ધર્મ દેવતા,પાલન દેવતા,પુરુષાર્થ,મંત્રો,ઉપાયો,સાઇન ઇન,સાઇન આઉટ,નોંધણી,ચકાસાયેલ,વર્ગ કુંડળીઓ",
    "bn": "হোম,পঞ্জিকা,ক্যালেন্ডার,চৌঘড়িয়া,হোরা,রাহু কাল,উৎসব,কুণ্ডলী,মিলন,মুহূর্ত,গোচর,সূর্যোদয়,সূর্যাস্ত,চন্দ্রোদয়,চন্দ্রাস্ত,তিথি,নক্ষত্র,যোগ,করণ,পক্ষ,বার,মাস,আজকের পঞ্জিকা,শুভ সময়,অশুভ সময়,ভাষা,রাশিফল,গ্রহ,রাশি,ভাব,প্রশ্ন,হোরা,আত্ম নির্দেশনা,আত্মকারক,কারকাংশ,ইষ্ট দেবতা,ধর্ম দেবতা,পালন দেবতা,পুরুষার্থ,মন্ত্র,প্রতিকার,সাইন ইন,সাইন আউট,নিবন্ধন,যাচাইকৃত,বর্গ কুণ্ডলী",
    "ta": "முகப்பு,பஞ்சாங்கம்,நாட்காட்டி,கௌரி/சோகடியா,ஹோரை,ராகு காலம்,பண்டிகைகள்,ஜாதகம்,பொருத்தம்,முகூர்த்தம்,கோசாரம்,சூரிய உதயம்,சூரிய அஸ்தமனம்,சந்திர உதயம்,சந்திர அஸ்தமனம்,திதி,நட்சத்திரம்,யோகம்,கரணம்,பட்சம்,கிழமை,மாதம்,இன்றைய பஞ்சாங்கம்,நல்ல நேரம்,தவிர்க்க வேண்டிய நேரம்,மொழி,ராசிபலன்,கிரகம்,ராசி,பாவம்,பிரஸ்னம்,ஹோரா,ஆன்மீக வழிகாட்டுதல்,ஆத்மகாரகன்,காரகாம்சம்,இஷ்ட தெய்வம்,தர்ம தெய்வம்,பாலன தெய்வம்,புருஷார்த்தம்,மந்திரங்கள்,பரிகாரங்கள்,உள்நுழைக,வெளியேறு,பதிவு செய்க,சரிபார்க்கப்பட்டது,வர்க்க சக்கரங்கள்",
    "te": "హోమ్,పంచాంగం,క్యాలెండర్,చోఘడియా,హోర,రాహు కాలం,పండుగలు,జాతకం,పొంతన,ముహూర్తం,గోచారం,సూర్యోదయం,సూర్యాస్తమయం,చంద్రోదయం,చంద్రాస్తమయం,తిథి,నక్షత్రం,యోగం,కరణం,పక్షం,వారం,మాసం,నేటి పంచాంగం,శుభ సమయాలు,అశుభ సమయాలు,భాష,రాశిఫలం,గ్రహం,రాశి,భావం,ప్రశ్న,హోర,ఆత్మ మార్గదర్శనం,ఆత్మకారక,కారకాంశ,ఇష్ట దైవం,ధర్మ దైవం,పాలన దైవం,పురుషార్థం,మంత్రాలు,పరిహారాలు,సైన్ ఇన్,సైన్ అవుట్,నమోదు,ధృవీకరించబడింది,వర్గ చక్రాలు",
    "kn": "ಮುಖಪುಟ,ಪಂಚಾಂಗ,ಕ್ಯಾಲೆಂಡರ್,ಚೌಘಡಿಯಾ,ಹೋರಾ,ರಾಹು ಕಾಲ,ಹಬ್ಬಗಳು,ಜಾತಕ,ಹೊಂದಾಣಿಕೆ,ಮುಹೂರ್ತ,ಗೋಚಾರ,ಸೂರ್ಯೋದಯ,ಸೂರ್ಯಾಸ್ತ,ಚಂದ್ರೋದಯ,ಚಂದ್ರಾಸ್ತ,ತಿಥಿ,ನಕ್ಷತ್ರ,ಯೋಗ,ಕರಣ,ಪಕ್ಷ,ವಾರ,ಮಾಸ,ಇಂದಿನ ಪಂಚಾಂಗ,ಶುಭ ಸಮಯ,ಅಶುಭ ಸಮಯ,ಭಾಷೆ,ರಾಶಿಫಲ,ಗ್ರಹ,ರಾಶಿ,ಭಾವ,ಪ್ರಶ್ನೆ,ಹೋರಾ,ಆತ್ಮ ಮಾರ್ಗದರ್ಶನ,ಆತ್ಮಕಾರಕ,ಕಾರಕಾಂಶ,ಇಷ್ಟ ದೇವತೆ,ಧರ್ಮ ದೇವತೆ,ಪಾಲನ ದೇವತೆ,ಪುರುಷಾರ್ಥ,ಮಂತ್ರಗಳು,ಪರಿಹಾರಗಳು,ಸೈನ್ ಇನ್,ಸೈನ್ ಔಟ್,ನೋಂದಣಿ,ದೃಢೀಕರಿಸಲಾಗಿದೆ,ವರ್ಗ ಕುಂಡಲಿಗಳು",
    "ml": "ഹോം,പഞ്ചാംഗം,കലണ്ടർ,ചോഘഡിയ,ഹോര,രാഹു കാലം,ഉത്സവങ്ങൾ,ജാതകം,പൊരുത്തം,മുഹൂർത്തം,ഗോചരം,സൂര്യോദയം,സൂര്യാസ്തമയം,ചന്ദ്രോദയം,ചന്ദ്രാസ്തമയം,തിഥി,നക്ഷത്രം,യോഗം,കരണം,പക്ഷം,ആഴ്ച,മാസം,ഇന്നത്തെ പഞ്ചാംഗം,ശുഭ സമയം,അശുഭ സമയം,ഭാഷ,രാശിഫലം,ഗ്രഹം,രാശി,ഭാവം,പ്രശ്നം,ഹോര,ആത്മ മാർഗ്ഗദർശനം,ആത്മകാരകൻ,കാരകാംശം,ഇഷ്ട ദേവത,ധർമ്മ ദേവത,പാലന ദേവത,പുരുഷാർത്ഥം,മന്ത്രങ്ങൾ,പരിഹാരങ്ങൾ,സൈൻ ഇൻ,സൈൻ ഔട്ട്,രജിസ്റ്റർ ചെയ്യുക,സ്ഥിരീകരിച്ചു,വർഗ്ഗ ചക്രങ്ങൾ",
}


def _build():
    maps = {}
    for lang, tbl in T.items():
        m = {}
        for cat, en in EN.items():
            src = "signs" if cat == "rashis" else "weekdays" if cat == "varas" else cat
            if src not in tbl:
                continue
            for e, t in zip(en.split(","), tbl[src].split(",")):
                m[e] = t
        for e, t in zip(LABELS_EN, LABELS[lang].split(",")):
            m.setdefault(e, t)
        for e, t in zip(EN["paksha"].split(","), tbl["paksha"].split(",")):
            m[e] = t
        m["Paksha"] = LABELS[lang].split(",")[19]
        maps[lang] = m
    return maps


MAPS = _build()
for _l, _m in MAPS.items():
    assert len(_m) > 150, _l

_WORD = re.compile(r"[A-Za-z][A-Za-z']*")
_MULTI = sorted({k for m in MAPS.values() for k in m if " " in k}, key=len, reverse=True)


# ---------------------------------------------------------------------------
# SANSKRIT SHLOKA / MANTRA DETECTOR (NEVER TRANSLATE THE SHLOKA VERSE ITSELF)
# ---------------------------------------------------------------------------
_SHLOKA_PATTERNS = re.compile(
    r"(?:"
    r"ॐ|॥|नमः|नमाम्यहम्|प्रणमाम्यहम्|प्रणतोऽस्मि|विद्महे|धीमहि|प्रचोदयात्|यजामहे|पुष्टिवर्धनम्|मृत्योर्मुक्षीय|प्रसीद\s+प्रसीद|शरणं\s+गतः|"
    r"\bOm\s+(?:Hraam|Shraam|Kraam|Braam|Graam|Draam|Praam|Bhraam|Sraam|Ghrinih|Som\s+Somaaya|Ang\s+Angarakaya|Bum\s+Budhaaya|Brim\s+Brihaspataye|Shum\s+Shukraaya|Tryambakam\s+Yajamahe|Shreem\s+Hreem)\b|"
    r"\b(?:Japaakusuma|Dadhishankhatushaaraabham|Dharaneegarbhasambhootam|Priyangu-kalikaa|Devaanaam\s+cha\s+risheenaam|Himakundamrinaalaabham|Neelaanjanasamaabhaasam|Ardhakaayam\s+mahaaveeryam|Palaashapushpasamkaasham|Ugram\s+Veeram\s+Maha-Vishnum|Urvarukamiva\s+Bandhanan)\b"
    r")",
    re.IGNORECASE,
)


def is_sanskrit_shloka(text: str) -> bool:
    """Return True if `text` is a sacred Sanskrit Shloka/Mantra verse or transliteration that must remain untouched."""
    if not text:
        return False
    s = text.strip()
    if _SHLOKA_PATTERNS.search(s):
        # If it is a pure shloka/mantra line (not a long English paragraph that merely mentions a short mantra)
        # Note: in templates, shlokas are inside <code class="notranslate"> or similar, so this is an extra safety guard.
        if len(s) < 340 and not s.startswith(("Light a ", "Recite ", "Avoid ", "Every ", "Perform ")):
            return True
    return False


# ---------------------------------------------------------------------------
# PERSISTENT SQLITE + RAM TRANSLATION CACHE & PARALLEL NEURAL BATCH ENGINE
# ---------------------------------------------------------------------------
_DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
os.makedirs(_DATA_DIR, exist_ok=True)
_DB_PATH = os.path.join(_DATA_DIR, "i18n_cache.sqlite")
_DB_LOCK = threading.Lock()
_MEM_CACHE: Dict[Tuple[str, str], str] = {}


def _init_db():
    with _DB_LOCK:
        conn = sqlite3.connect(_DB_PATH, timeout=10.0)
        try:
            conn.execute(
                "CREATE TABLE IF NOT EXISTS translations (lang TEXT, src TEXT, dst TEXT, PRIMARY KEY (lang, src))"
            )
            conn.commit()
        finally:
            conn.close()


_init_db()

# Pre-seed _MEM_CACHE with curated MAPS
for _lg, _mp in MAPS.items():
    for _k, _v in _mp.items():
        _MEM_CACHE[(_lg, _k)] = _v

_HAS_ALPHA = re.compile(r"[A-Za-z]{2,}")
_AMPM_RE = re.compile(r"\b(\d{1,2}:\d{2}(?::\d{2})?)\s*(AM|PM)\b", re.IGNORECASE)


def _protect_ampm(text: str) -> Tuple[str, List[str]]:
    """Mask 'HH:MM AM/PM' tokens before neural translation so explicit AM/PM is never lost."""
    tokens: List[str] = []

    def _repl(m):
        idx = len(tokens)
        tokens.append(f"{m.group(1)} {m.group(2).upper()}")
        return f"__TM{idx}__"

    return _AMPM_RE.sub(_repl, text), tokens


def _restore_ampm(text: str, tokens: List[str]) -> str:
    if not tokens:
        return text
    out = text
    for idx, tok in enumerate(tokens):
        # Match case-insensitively or with spaces added by translator
        out = re.sub(rf"__\s*TM\s*{idx}\s*__", tok, out, flags=re.IGNORECASE)
    return out


def _translate_chunk_via_api(lines: List[str], lang: str) -> List[str]:
    """Translate a list of single-line strings in one HTTP request to Google Translate GTX."""
    if not lines:
        return []
    protected_lines = []
    token_lists = []
    for ln in lines:
        p_ln, toks = _protect_ampm(ln)
        protected_lines.append(p_ln)
        token_lists.append(toks)

    joined = "\n".join(protected_lines)
    try:
        r = httpx.post(
            "https://translate.googleapis.com/translate_a/single",
            params={"client": "gtx", "sl": "en", "tl": lang, "dt": "t"},
            data={"q": joined},
            timeout=6.0,
        )
        if r.status_code == 200:
            data = r.json()
            if data and isinstance(data, list) and data[0]:
                full_trans = "".join(seg[0] for seg in data[0] if seg and seg[0])
                out_lines = full_trans.split("\n")
                if len(out_lines) == len(lines):
                    return [
                        _restore_ampm(out_lines[i].strip(), token_lists[i])
                        for i in range(len(lines))
                    ]
    except Exception:
        pass

    # Fallback: translate individually or via word dictionary if line count mismatched
    results = []
    for i, orig in enumerate(lines):
        try:
            r = httpx.post(
                "https://translate.googleapis.com/translate_a/single",
                params={"client": "gtx", "sl": "en", "tl": lang, "dt": "t"},
                data={"q": protected_lines[i]},
                timeout=4.0,
            )
            if r.status_code == 200:
                data = r.json()
                tr = "".join(seg[0] for seg in data[0] if seg and seg[0]).strip()
                results.append(_restore_ampm(tr, token_lists[i]))
                continue
        except Exception:
            pass
        results.append(term_fallback(orig, lang))
    return results


def term_fallback(s: str, lang: str) -> str:
    """Dictionary-based fallback translation."""
    if lang in (None, "", "en") or lang not in MAPS or not isinstance(s, str):
        return s
    m = MAPS[lang]
    if s in m:
        return m[s]
    out = s
    for k in _MULTI:
        if k in out and k in m:
            out = out.replace(k, m[k])
    words = _WORD.findall(out)
    if words and all(w in m for w in words):
        out = _WORD.sub(lambda mm: m[mm.group(0)], out)
    return out


def translate_texts_batch(texts: List[str], lang: str) -> List[str]:
    """Translate a batch of strings into `lang` with 100% coverage while keeping Sanskrit Shlokas untouched."""
    if not texts or lang in (None, "", "en") or lang not in LANGS:
        return list(texts)

    # Identify unique translatable single-line segments
    # If a text has internal newlines, we split by newline, translate each non-empty line, and rejoin.
    unique_lines_needed: List[str] = []
    seen_needed = set()

    def _check_line(ln: str):
        s = ln.strip()
        if not s or not _HAS_ALPHA.search(s) or is_sanskrit_shloka(s):
            return
        if (lang, s) in _MEM_CACHE:
            return
        if s not in seen_needed:
            seen_needed.add(s)
            unique_lines_needed.append(s)

    for txt in texts:
        if not txt or not isinstance(txt, str) or is_sanskrit_shloka(txt):
            continue
        for ln in txt.split("\n"):
            _check_line(ln)

    # Check SQLite cache for unique_lines_needed
    still_missing: List[str] = []
    if unique_lines_needed:
        with _DB_LOCK:
            conn = sqlite3.connect(_DB_PATH, timeout=10.0)
            try:
                cur = conn.cursor()
                for s in unique_lines_needed:
                    row = cur.execute(
                        "SELECT dst FROM translations WHERE lang = ? AND src = ?", (lang, s)
                    ).fetchone()
                    if row and row[0]:
                        _MEM_CACHE[(lang, s)] = row[0]
                    else:
                        still_missing.append(s)
            finally:
                conn.close()

    # Batch translate `still_missing` in parallel chunks
    if still_missing:
        chunks: List[List[str]] = []
        cur_chunk: List[str] = []
        cur_len = 0
        for s in still_missing:
            if cur_chunk and (len(cur_chunk) >= 30 or cur_len + len(s) > 2800):
                chunks.append(cur_chunk)
                cur_chunk = []
                cur_len = 0
            cur_chunk.append(s)
            cur_len += len(s) + 1
        if cur_chunk:
            chunks.append(cur_chunk)

        new_pairs: List[Tuple[str, str, str]] = []
        if len(chunks) == 1:
            translated_chunks = [_translate_chunk_via_api(chunks[0], lang)]
        else:
            with ThreadPoolExecutor(max_workers=min(8, len(chunks))) as ex:
                translated_chunks = list(ex.map(lambda ch: _translate_chunk_via_api(ch, lang), chunks))

        for ch_src, ch_dst in zip(chunks, translated_chunks):
            for src_s, dst_s in zip(ch_src, ch_dst):
                _MEM_CACHE[(lang, src_s)] = dst_s
                new_pairs.append((lang, src_s, dst_s))

        if new_pairs:
            with _DB_LOCK:
                conn = sqlite3.connect(_DB_PATH, timeout=10.0)
                try:
                    conn.executemany(
                        "INSERT OR REPLACE INTO translations (lang, src, dst) VALUES (?, ?, ?)",
                        new_pairs,
                    )
                    conn.commit()
                finally:
                    conn.close()

    # Reconstruct output list preserving leading/trailing whitespace and newlines
    out_texts: List[str] = []
    for txt in texts:
        if not txt or not isinstance(txt, str) or is_sanskrit_shloka(txt):
            out_texts.append(txt)
            continue
        lines = txt.split("\n")
        out_lines = []
        for ln in lines:
            s = ln.strip()
            if not s or not _HAS_ALPHA.search(s) or is_sanskrit_shloka(s):
                out_lines.append(ln)
            else:
                tr = _MEM_CACHE.get((lang, s), s)
                lead = ln[: len(ln) - len(ln.lstrip())]
                trail = ln[len(ln.rstrip()) :]
                out_lines.append(f"{lead}{tr}{trail}")
        out_texts.append("\n".join(out_lines))
    return out_texts


_NOTRANSLATE_BLOCK_RE = re.compile(
    r"(<script\b[^>]*>.*?</script>|<style\b[^>]*>.*?</style>|<svg\b[^>]*>.*?</svg>|"
    r"<select\b[^>]*id=[\"']?langSel[\"']?[^>]*>.*?</select>|"
    r"<(?P<tag>code|span|div|p|strong|em|b|i)\b[^>]*(?:class=(?:[\"'][^\"']*\bnotranslate\b[^\"']*[\"']|notranslate\b)|translate=(?:[\"']no[\"']|no\b))[^>]*>.*?</(?P=tag)>)",
    flags=re.S | re.I,
)
_PLACEHOLDER_ATTR_RE = re.compile(r'(\bplaceholder=["\'])([^"\']+)(["\'])', flags=re.I)


def localize_html_full(html: str, lang: str) -> str:
    """Translate 100% of visible HTML text nodes and input placeholders into `lang`,
    while strictly preserving `<script>`, `<style>`, `<svg>`, and `.notranslate` / Sanskrit Shlokas."""
    if not html or lang in (None, "", "en") or lang not in LANGS:
        return html

    # 1. Mask all protected blocks (<script>, <style>, <svg>, .notranslate, translate="no")
    protected_blocks: List[str] = []

    def _mask_block(m):
        idx = len(protected_blocks)
        protected_blocks.append(m.group(0))
        return f"<!--__PH_PROT_{idx}__-->"

    masked_html = _NOTRANSLATE_BLOCK_RE.sub(_mask_block, html)

    # 2. Split by HTML tags
    parts = re.split(r"(<[^>]+>)", masked_html)
    text_indices: List[int] = []
    raw_texts: List[str] = []

    for i, part in enumerate(parts):
        if not part or part.startswith("<"):
            continue
        unesc = _html.unescape(part)
        if _HAS_ALPHA.search(unesc) and not is_sanskrit_shloka(unesc):
            text_indices.append(i)
            raw_texts.append(unesc)

    if raw_texts:
        translated_texts = translate_texts_batch(raw_texts, lang)
        for idx, tr in zip(text_indices, translated_texts):
            # Escape <, >, & safely for HTML text node
            parts[idx] = _html.escape(tr, quote=False)

    # 3. Also translate input placeholder="..." attributes
    placeholder_vals: List[str] = []
    for part in parts:
        if part.startswith("<input") or part.startswith("<textarea"):
            for m in _PLACEHOLDER_ATTR_RE.finditer(part):
                val = _html.unescape(m.group(2))
                if _HAS_ALPHA.search(val):
                    placeholder_vals.append(val)
    if placeholder_vals:
        tr_placeholders = dict(zip(placeholder_vals, translate_texts_batch(placeholder_vals, lang)))
        for i, part in enumerate(parts):
            if part.startswith("<input") or part.startswith("<textarea"):
                parts[i] = _PLACEHOLDER_ATTR_RE.sub(
                    lambda m: f"{m.group(1)}{_html.escape(tr_placeholders.get(_html.unescape(m.group(2)), m.group(2)), quote=True)}{m.group(3)}",
                    part,
                )

    rebuilt = "".join(parts)

    # 4. Restore protected blocks untouched
    for idx, blk in enumerate(protected_blocks):
        rebuilt = rebuilt.replace(f"<!--__PH_PROT_{idx}__-->", blk)

    return rebuilt


def term(s: str, lang: str) -> str:
    """Translate one string using cache/neural batch or dictionary."""
    if lang in (None, "", "en") or lang not in MAPS or not isinstance(s, str):
        return s
    if is_sanskrit_shloka(s):
        return s
    if (lang, s) in _MEM_CACHE:
        return _MEM_CACHE[(lang, s)]
    res = translate_texts_batch([s], lang)
    return res[0] if res else term_fallback(s, lang)


SKIP_KEYS = {
    "date", "start", "end", "datetime", "datetime_utc", "timezone", "sunrise", "sunset", "moonrise", "moonset",
    "dms", "url", "id",
    # Never translate sacred Sanskrit Shloka/Mantra keys in JSON responses (their *_meaning keys ARE translated!):
    "beej_mantra", "beej_transliteration", "puranic_mantra", "puranic_shloka", "puranic_transliteration",
    "gayatri_mantra", "prana_pratishtha_shloka", "maha_mrityunjaya_shloka", "raksha_kavacha_shloka",
    "lakshmi_akarshana_shloka", "santana_gopala_shloka", "shloka_remedy", "classical_sloka",
}


def translate(obj: Any, lang: str) -> Any:
    """Walk any JSON-like result and translate all strings into `lang` (except `SKIP_KEYS` and Sanskrit Shlokas)."""
    if lang in (None, "", "en") or lang not in MAPS:
        return obj

    # Collect all translatable strings in a single pass so nested dicts translate in one fast batch
    collected: List[str] = []

    def _collect(node: Any, key_name: str = ""):
        if key_name in SKIP_KEYS:
            return
        if isinstance(node, dict):
            for k, v in node.items():
                _collect(v, k)
        elif isinstance(node, list):
            for v in node:
                _collect(v, key_name)
        elif isinstance(node, str):
            if _HAS_ALPHA.search(node) and not is_sanskrit_shloka(node):
                collected.append(node)

    _collect(obj)
    if collected:
        translate_texts_batch(collected, lang)

    def _apply(node: Any, key_name: str = "") -> Any:
        if key_name in SKIP_KEYS:
            return node
        if isinstance(node, dict):
            return {k: _apply(v, k) for k, v in node.items()}
        if isinstance(node, list):
            return [_apply(v, key_name) for v in node]
        if isinstance(node, str):
            if not _HAS_ALPHA.search(node) or is_sanskrit_shloka(node):
                return node
            return term(node, lang)
        return node

    return _apply(obj)


def label(s: str, lang: str) -> str:
    return term(s, lang)


def glossary(lang: str):
    if lang not in MAPS:
        raise ValueError(f"unsupported lang {lang!r}; choose from {', '.join(LANGS)}")
    out = {}
    for cat, en in EN.items():
        out[cat] = {e: MAPS[lang].get(e, e) for e in en.split(",")}
    out["labels"] = {e: MAPS[lang].get(e, e) for e in LABELS_EN}
    return {"lang": lang, "name": LANGS[lang], "glossary": out}
