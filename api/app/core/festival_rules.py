"""Festival-determination rules (karmakala-vyapti) as summarised from Nirnayasindhu (Kamalakara Bhatta, 1612)
and Dharmasindhu (Kashinatha Upadhyaya, 1790), with the regional/sectarian variants they discuss.
Paraphrased in our own words; used both as documentation (/api/festivals/rules) and by the calendar engine."""
RULES = [
    {"festival": "Ekadashi", "kaal": "sunrise (Arunodaya check)", "smarta": "Observe the day Ekadashi prevails at sunrise; if Dashami touches Arunodaya (96 min before sunrise) and Ekadashi continues to the next sunrise, fast the next day",
     "vaishnava": "Any Dashami at Arunodaya makes the day 'viddha'; fast on the following day (Gauna/Vaishnava Ekadashi)", "source": "Nirnayasindhu pt.2; Dharmasindhu pt.1 (Ekadashi-nirnaya)", "implemented": True},
    {"festival": "Krishna Janmashtami", "kaal": "nishita (midnight)", "smarta": "Ashtami at nishita; Rohini conjunction preferred (Jayanti yoga)",
     "vaishnava": "Ashtami at sunrise, Saptami-viddha rejected (ISKCON/Vaishnava day is often the next day)", "source": "Nirnayasindhu pt.2 (Janmashtami)", "implemented": True},
    {"festival": "Ganesh Chaturthi", "kaal": "madhyahna", "smarta": "Chaturthi spanning madhyahna; if on both days, the first (Tritiya-yukta preferred)", "source": "Dharmasindhu pt.2", "implemented": True},
    {"festival": "Diwali (Lakshmi Puja)", "kaal": "pradosh", "smarta": "Amavasya spanning pradosh; if on both days, the second day when it covers pradosh fully", "source": "Nirnayasindhu pt.2 (Deepavali)", "implemented": True},
    {"festival": "Holika Dahan", "kaal": "pradosh, Bhadra-free", "smarta": "Purnima at pradosh avoiding Bhadra (Vishti); if Bhadra covers pradosh, burn after Bhadra-mukha or on Bhadra-puchha", "source": "Nirnayasindhu pt.2 (Holika)", "implemented": True},
    {"festival": "Raksha Bandhan", "kaal": "aparahna, Bhadra-free", "smarta": "Shravana Purnima in aparahna/pradosh free of Bhadra", "source": "Nirnayasindhu pt.2", "implemented": True},
    {"festival": "Vijayadashami", "kaal": "aparahna", "smarta": "Dashami at aparahna; Shravana nakshatra preferred", "source": "Dharmasindhu pt.2", "implemented": True},
    {"festival": "Maha Shivaratri", "kaal": "nishita", "smarta": "Phalguna Krishna Chaturdashi spanning nishita", "source": "Nirnayasindhu pt.2", "implemented": True},
    {"festival": "Rama Navami", "kaal": "madhyahna", "smarta": "Navami at madhyahna; Ashtami-viddha avoided", "source": "Nirnayasindhu pt.2", "implemented": True},
    {"festival": "Karwa Chauth / Sankashti", "kaal": "moonrise", "smarta": "Chaturthi prevailing at moonrise", "source": "Dharmasindhu pt.2", "implemented": True},
    {"festival": "Pradosh Vrat", "kaal": "pradosh", "smarta": "Trayodashi covering the pradosh period after sunset", "source": "Dharmasindhu pt.1", "implemented": True},
    {"festival": "Shraddha (tithi)", "kaal": "aparahna", "smarta": "Tithi prevailing in aparahna (4th of 5 day-parts)", "source": "Nirnayasindhu pt.3", "implemented": True},
    {"festival": "Regional new year (solar)", "kaal": "sankranti + regional rule", "smarta": "Tamil: before sunset; Kerala: before 3/5 of day; Bengal/Assam: next day if before midnight; Odisha: civil date",
     "source": "Kalaprakasika (1917) on sankranti punya-kala; regional panjika practice", "implemented": True},
    {"festival": "Sankranti punya-kala", "kaal": "varies by sign", "smarta": "Punya-kala of 16 ghatis before/after; Makara & Karka: 40 ghatis after/before; night sankranti shifts to next/previous day",
     "source": "Nirnayasindhu pt.1 (Sankranti-nirnaya); Muhurta Chintamani ch.1", "implemented": True},
    {"festival": "Gujarati New Year (Bestu Varas)", "kaal": "sunrise", "smarta": "Kartika Shukla Pratipada (day after Diwali/Govardhan)", "source": "regional practice", "implemented": True},
    {"festival": "Gudi Padwa / Ugadi", "kaal": "sunrise", "smarta": "Chaitra Shukla Pratipada at sunrise; Adhika masa excluded", "source": "Dharmasindhu pt.1", "implemented": True},
]
