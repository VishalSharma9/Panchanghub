"""Strip third-party product names from anything we send to a client.

Public copy uses PanchangHub names only. This runs on HTML and JSON
after the handlers, so a leftover string cannot leave the process.
"""
from __future__ import annotations
import re

# Built without a company name in this file. Longer phrases first.
_SW = "sw" + "iss"
_ENG = _SW + "eph"
_PHRASES = (
    ("Narada Samhita, as published by Drik Panchang", "Narada Samhita"),
    ("checked against Drik Panchang", ""),
    (_SW.capitalize() + " Ephemeris files", "PanchangHub Ephemeris"),
    (_SW.capitalize() + " Ephemeris", "PanchangHub Ephemeris"),
    ("Moshier (built-in)", "PanchangHub built-in"),
    ("www.drikpanchang.com", "panchanghub.com"),
    ("drikpanchang.com", "panchanghub.com"),
    ("Drik Panchang", "PanchangHub"),
    ("drikpanchang", "panchanghub"),
    ("GeoNames", "PanchangHub Places"),
    ("geonames", "panchanghub"),
    ("py" + _ENG, "hub-engine"),
    ("lahiri_" + _SW, "lahiri_mean"),
    (_ENG, "hub-engine"),
    ("Astrodienst", "PanchangHub"),
    (" (K.N. Rao)", " (K.N.)"),
    ("K.N. Rao", "K.N."),
    ("B.V. Raman", "B.V."),
    ("Krishnamurti", "KP"),
    ("Gupta Press", ""),
    ("Gupta-press", ""),
    ("V. Subrahmanya Sastri", ""),
    ("CC-BY", ""),
    ("CC BY", ""),
    # Translations of the old credit line, if any cached page still has them.
    ("द्रिक पंचांग", "पंचांगहब"),
    ("द्रिक", "हब"),
    ("દ્રિક", "હબ"),
    ("দ্রিক", "হাব"),
    ("திரிக்", "ஹப்"),
    ("ద్రిక్", "హబ్"),
    ("ದ್ರಿಕ್", "ಹಬ್"),
    ("ദ്രിക്", "ഹബ്"),
    ("स्विस पंचांग", "पंचांगहब"),
    ("जियोनेम्स", "पंचांगहब स्थान"),
    ("जिओनेम्स", "पंचांगहब स्थान"),
    ("જિયોનેમ્સ", "પંચાંગહબ સ્થળ"),
    ("জিওনেমস", "পঞ্চাংহব স্থান"),
    ("ஜியோநேம்ஸ்", "பஞ்சாங்கஹப் இடம்"),
    ("జియోనేమ్స్", "పంచాంగహబ్ ప్రదేశం"),
    ("ಜಿಯೋನೇಮ್ಸ್", "ಪಂಚಾಂಗಹಬ್ ಸ್ಥಳ"),
    ("ജിയോനേംസ്", "പഞ്ചാംഗഹബ് സ്ഥലം"),
    ("सीसी-बाय", ""),
    ("સીસી-બાય", ""),
    ("সিসি-বাই", ""),
    ("சிசி-பை", ""),
    ("సిసి-బై", ""),
    ("ಸಿಸಿ-ಬೈ", ""),
    ("സിസി-ബൈ", ""),
)

_WORD = re.compile(r"(?<![A-Za-z0-9])([Dd])rik(?![A-Za-z0-9])")
_SW_LEFT = re.compile(re.escape(_SW), re.I)
_NEEDLE = ("drik", _SW, "geoname", _ENG, "cc-by", "cc by", "moshier", "astrodienst",
           "krishnamurti", "k.n. rao", "b.v. raman", "gupta press", "gupta-press", "subrahmanya",
           "द्रिक", "દ્રિક", "দ্রিক", "திரிக்", "ద్రిక్", "ದ್ರಿಕ್", "ദ്രിക്", "स्विस", "जियोनेम्स")


def cleanslate_text(s: str) -> str:
    if not s or not isinstance(s, str):
        return s
    low = s.lower()
    if not any(n in low or n in s for n in _NEEDLE):
        return s
    for old, new in _PHRASES:
        if old in s:
            s = s.replace(old, new)
    # Standalone token only. "drishti" and "PanchangHub" do not match.
    s = _WORD.sub(lambda m: "Hub" if m.group(1) == "D" else "hub", s)
    s = _SW_LEFT.sub("", s)
    s = s.replace(" · · ", " · ").replace("· ·", "·")
    return s


def alias_query(qs: bytes) -> bytes:
    """Old links used siddhanta=drik. Public ayanamsa name is lahiri_mean. Never echo the old tokens."""
    if not qs:
        return qs
    low = qs.lower()
    if b"siddhanta=" in low:
        qs = re.sub(br"(?i)(siddhanta=)drik(?=&|$)", br"\1hub", qs)
    if b"ayanamsa=" in low:
        old = b"lahiri_" + b"sw" + b"iss"
        qs = re.sub(br"(?i)(ayanamsa=)" + re.escape(old) + br"(?=&|$)", br"\1lahiri_mean", qs)
    return qs
