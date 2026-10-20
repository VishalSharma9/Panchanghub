"""Compare our 2026 New Delhi festival dates with canonical 2026 Hindu festival calendar standards."""
import json, os, sys
from datetime import datetime
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.core.calendar import year_festivals
MAP = {"Makara Sankranti": "Makar Sankranti", "Holika Dahan": "Holika Dahan", "Holi": "Holi (Dhulandi)", "Chaitra Navratri": "Chaitra Navratri / Gudi Padwa / Ugadi",
       "Rama Navami *Smarta": "Rama Navami", "Hanuman Jayanti": "Hanuman Jayanti", "Akshaya Tritiya": "Akshaya Tritiya", "Buddha Purnima": "Buddha Purnima",
       "Vat Savitri Vrat": "Vat Savitri Vrat (Amanta)", "Ganga Dussehra": "Ganga Dussehra", "Jagannath Rathyatra": "Jagannath Rath Yatra", "Guru Purnima": "Guru Purnima",
       "Hariyali Teej": "Hariyali Teej", "Nag Panchami": "Nag Panchami", "Rakhi": "Raksha Bandhan", "Krishna Janmashtami": "Krishna Janmashtami",
       "Hartalika Teej": "Hartalika Teej", "Ganesh Chaturthi": "Ganesh Chaturthi", "Anant Chaturdashi": "Anant Chaturdashi", "Navratri Begins": "Sharad Navratri begins",
       "Durga Ashtami": "Durga Ashtami", "Maha Navami": "Maha Navami", "Dussehra": "Dussehra (Vijayadashami)", "Sharad Purnima": "Sharad Purnima",
       "Karwa Chauth": "Karwa Chauth", "Dhanteras": "Dhanteras", "Narak Chaturdashi": "Narak Chaturdashi", "Diwali": "Diwali (Lakshmi Puja)",
       "Govardhan Puja": "Govardhan Puja", "Bhaiya Dooj": "Bhai Dooj", "Chhath Puja": "Chhath Puja", "Kartika Purnima": "Kartika Purnima / Dev Deepawali",
       "Vivah Panchami": "Vivah Panchami", "Dattatreya Jayanti": "Datta Jayanti", "Vasant Panchami": "Vasant Panchami", "Maha Shivaratri": "Maha Shivaratri",
       "Gangaur": "Gangaur", "Yamuna Chhath": "Yamuna Chhath", "Ganga Saptami": "Ganga Saptami", "Sita Navami": "Sita Navami", "Narasimha Jayanti": "Narasimha Jayanti",
       "Narada Jayanti": "Narada Jayanti", "Shani Jayanti": "Shani Jayanti", "Vat Purnima Vrat": "Vat Purnima Vrat", "Gayatri Jayanti": "Gayatri Jayanti",
       "Kajari Teej": "Kajari Teej", "Rishi Panchami": "Rishi Panchami", "Balarama Jayanti": "Balarama Jayanti", "Radha Ashtami": "Radha Ashtami",
       "Pitrupaksha Begins": "Pitrupaksha Begins", "Sarva Pitru Amavasya": "Sarva Pitru Amavasya", "Ahoi Ashtami": "Ahoi Ashtami", "Govatsa Dwadashi": "Govatsa Dwadashi",
       "Kali Chaudas": "Kali Chaudas", "Kansa Vadh": "Kansa Vadh", "Tulasi Vivah": "Tulasi Vivah", "Kalabhairav Jayanti": "Kalabhairav Jayanti", "Gita Jayanti": "Gita Jayanti",
       "Sakat Chauth": "Sakat Chauth", "Mauni Amavas": "Mauni Amavas", "Ratha Saptami": "Ratha Saptami", "Bhishma Ashtami": "Bhishma Ashtami",
       "Sheetala Ashtami": "Sheetala Ashtami", "Hindu Solar calendar Parashurama Jayanti": "Parashurama Jayanti", "Onam": "Onam", "Pongal": "Pongal",
       "Vishwakarma Puja": "Vishwakarma Puja", "Solar New Year": "Solar New Year (Vishu / Puthandu / Pohela Boishakh)", "Gauna Yogini Ekadashi": "Gauna Yogini Ekadashi (Vaishnava)",
       "Gauna Devutthana Ekadashi": "Gauna Devutthana Ekadashi (Vaishnava)", "Shravana Nakshatra Varalakshmi Vrat": "Varalakshmi Vrat", "Kojagara Puja": "Kojagara Puja",
       "Chhoti Holi": "Chhoti Holi", "Pausha Purnima": "Pausha Purnima", "Magha Purnima": "Magha Purnima", "Phalguna Purnima": "Phalguna Purnima",
       "Chaitra Purnima": "Chaitra Purnima", "Vaishakha Purnima": "Vaishakha Purnima", "Jyeshtha Adhika Purnima": "Jyeshtha (Adhika) Purnima", "Jyeshtha Purnima": "Jyeshtha Purnima",
       "Ashadha Purnima": "Ashadha Purnima", "Shravana Purnima": "Shravana Purnima", "Bhadrapada Purnima": "Bhadrapada Purnima", "Ashwina Purnima": "Ashwin Purnima",
       "Margashirsha Purnima": "Margashirsha Purnima"}
def run(verbose=True):
    drik = json.load(open(os.path.join(os.path.dirname(__file__), "drik_festivals_2026_delhi.json")))
    ours = {}
    for e in year_festivals(2026, 28.63556, 77.22444, "Asia/Kolkata")["events"]:
        ours.setdefault(e["name"], []).append(e["date"])
    ok = bad = 0; rows = []
    for d, name in drik:
        if name not in MAP: continue
        dd = datetime.strptime(d + " 2026", "%B %d %Y").date().isoformat()
        got = ours.get(MAP[name], [])
        match = dd in got; ok += match; bad += not match
        rows.append((name, dd, got, match))
    if verbose:
        for r in rows:
            if not r[3]: print("MISMATCH", r)
        print(f"{ok}/{ok+bad} festival dates match")
    return ok, bad, rows
if __name__ == "__main__":
    run()
