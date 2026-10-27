"""Extra day-panchang fields: gate, pakshi, mantri, agni, chandra vasa, shiva, tamil yoga, aadal, do-ghati.

Rules that are cited, not guessed:
* Pravishte / solar gate — civil days since the Sun entered the current sidereal sign, in the local timezone.
* Ghati clock — 1 ghati = 24 min, 1 pala = 24 sec, 1 vipala = 0.4 sec.
* Agnivasa — Pratipada (and every third tithi) is Prithvi.
* Chandra vasa — rashi direction, East/South/West/North repeating. Tula → West.
* Mantri Mandala — Narada Samhita posts by weekday
  (Raja, Mantri, Senadhipati, Sasyadhipati, Meghadhipati, Rasadhipati, Nirasadhipati).
* Pancha Pakshi — birth bird by janma nakshatra and paksha (standard South-Indian grouping);
  the day's ruling bird by weekday and paksha; night ruler two birds on
  (Vulture, Owl, Crow, Cock, Peacock). Each fifth of the day and of the night,
  the Ruling slot moves to the next bird.
* Shivavasa — tithi number 1–30 mod 7 (Rudrabhisheka tithi table). Amavasya is 30, so with Gowri.
* Tamil yoga — Amritadi weekday × nakshatra table.
* Aadal — Moon's nakshatra counted from the Sun's is 2, 7, 9, 14, 16, 21 or 23.
* Do Ghati — 15 day muhurtas and 15 night muhurtas; the 8th day muhurta is Abhijit, the 11th is Vijaya.
"""
from __future__ import annotations
from datetime import timedelta
from functools import lru_cache

BIRDS = ["Vulture", "Owl", "Crow", "Cock", "Peacock"]
ACTS = ["Ruling", "Eating", "Walking", "Sleeping", "Dying"]
ACT_QUALITY = {"Ruling": "Favourable", "Eating": "Favourable", "Walking": "Mixed", "Sleeping": "Avoid", "Dying": "Avoid"}
# Weekday 0=Sunday. Verified against published Pancha Pakshi day-rulers.
RULING = {
    "Shukla": [1, 2, 3, 4, 0, 1, 0],
    "Krishna": [2, 1, 0, 4, 3, 4, 3],
}
FRIENDS = {
    "Vulture": (["Peacock", "Owl"], ["Crow", "Cock"]),
    "Owl": (["Vulture", "Crow"], ["Cock", "Peacock"]),
    "Crow": (["Cock", "Owl"], ["Vulture", "Peacock"]),
    "Cock": (["Peacock", "Owl"], ["Vulture", "Crow"]),
    "Peacock": (["Vulture", "Cock"], ["Owl", "Crow"]),
}
DIRS = ["East", "South", "West", "North"]
WEEKDAY_LORD = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]

# tithi number (1–30) mod 7. Cemetery on 1/8/15, with Gowri on 2/9/30.
SHIVA = {
    1: ("in Shmashana", "Avoid"),
    2: ("with Gowri", "Favourable"),
    3: ("in assembly", "Avoid"),
    4: ("at work", "Avoid"),
    5: ("at Kailash", "Favourable"),
    6: ("on Nandi", "Favourable"),
    0: ("at dinner", "Avoid"),
}
AGNI_GLOSS = {"Prithvi": "Earth", "Akasha": "Heaven", "Patala": "Nadir"}
# Amritadi / Tamil yoga. Rows are the 27 nakshatras; columns Sunday..Saturday.
TAMIL_YOGA = [
    ["Siddha", "Siddha", "Siddha", "Marana", "Amrita", "Amrita", "Siddha"],
    ["Prabalarishta", "Siddha", "Siddha", "Siddha", "Siddha", "Siddha", "Siddha"],
    ["Siddha", "Marana", "Siddha", "Amrita", "Marana", "Siddha", "Siddha"],
    ["Siddha", "Amrita", "Amrita", "Siddha", "Marana", "Marana", "Amrita"],
    ["Siddha", "Siddha", "Siddha", "Siddha", "Marana", "Siddha", "Siddha"],
    ["Siddha", "Siddha", "Marana", "Siddha", "Marana", "Siddha", "Siddha"],
    ["Siddha", "Amrita", "Siddha", "Siddha", "Amrita", "Siddha", "Siddha"],
    ["Siddha", "Siddha", "Siddha", "Siddha", "Siddha", "Marana", "Siddha"],
    ["Siddha", "Siddha", "Siddha", "Siddha", "Siddha", "Marana", "Marana"],
    ["Marana", "Marana", "Siddha", "Siddha", "Amrita", "Marana", "Amrita"],
    ["Siddha", "Siddha", "Siddha", "Amrita", "Siddha", "Siddha", "Siddha"],
    ["Amrita", "Siddha", "Amrita", "Amrita", "Marana", "Siddha", "Marana"],
    ["Siddha", "Siddha", "Siddha", "Marana", "Siddha", "Amrita", "Marana"],
    ["Siddha", "Prabalarishta", "Siddha", "Siddha", "Siddha", "Siddha", "Marana"],
    ["Siddha", "Amrita", "Siddha", "Siddha", "Amrita", "Siddha", "Siddha"],
    ["Marana", "Marana", "Marana", "Siddha", "Amrita", "Siddha", "Siddha"],
    ["Marana", "Siddha", "Siddha", "Amrita", "Siddha", "Siddha", "Siddha"],
    ["Marana", "Siddha", "Marana", "Siddha", "Prabalarishta", "Marana", "Siddha"],
    ["Amrita", "Siddha", "Amrita", "Marana", "Siddha", "Amrita", "Siddha"],
    ["Siddha", "Marana", "Siddha", "Amrita", "Siddha", "Prabalarishta", "Siddha"],
    ["Amrita", "Marana", "Prabalarishta", "Amrita", "Siddha", "Siddha", "Siddha"],
    ["Amrita", "Amrita", "Siddha", "Siddha", "Siddha", "Marana", "Siddha"],
    ["Marana", "Siddha", "Siddha", "Prabalarishta", "Siddha", "Siddha", "Siddha"],
    ["Siddha", "Siddha", "Marana", "Siddha", "Marana", "Siddha", "Amrita"],
    ["Siddha", "Siddha", "Marana", "Amrita", "Siddha", "Siddha", "Marana"],
    ["Amrita", "Siddha", "Amrita", "Siddha", "Siddha", "Siddha", "Siddha"],
    ["Amrita", "Siddha", "Siddha", "Marana", "Siddha", "Siddha", "Prabalarishta"],
]
AADAL_COUNTS = {2, 7, 9, 14, 16, 21, 23}
DAY_MUHURTA = ["Rudra", "Ahi", "Mitra", "Pitri", "Vasu", "Jala", "Vishvedeva", "Abhijit", "Brahma", "Indra", "Vijaya", "Nirriti", "Varuna", "Aryaman", "Bhaga"]
DAY_KALA = ["Pratah", "Pratah", "Pratah", "Sangava", "Sangava", "Sangava", "Madhyahna", "Madhyahna", "Madhyahna", "Aparahna", "Aparahna", "Aparahna", "Sayahna", "Sayahna", "Sayahna"]
NIGHT_MUHURTA = ["Girisha", "Ajapada", "Ahirbudhnya", "Pusha", "Ashvini", "Yama", "Agni", "Vidhatri", "Kanda", "Aditi", "Jiva", "Vishnu", "Dyumani", "Brahma", "Samudra"]
NIGHT_KALA = ["Ratri"] * 15


def ghati_parts(seconds: float) -> dict:
    if seconds < 0:
        seconds = 0.0
    g = int(seconds // 1440)
    rem = seconds - g * 1440
    p = int(rem // 24)
    v = int(round((rem - p * 24) / 0.4))
    if v >= 60:
        v -= 60
        p += 1
    if p >= 60:
        p -= 60
        g += 1
    return {"ghati": g, "pala": p, "vipala": v, "text": f"{g} ghati {p} pala {v} vipala"}


def birth_bird(nak_index: int, paksha: str) -> str:
    if nak_index < 5:
        b = 0
    elif nak_index < 11:
        b = 1
    elif nak_index < 16:
        b = 2
    elif nak_index < 21:
        b = 3
    else:
        b = 4
    if paksha == "Krishna":
        b = {0: 4, 4: 0, 1: 3, 3: 1, 2: 2}[b]
    return BIRDS[b]


def _periods(start, end, ruling, tz, fmt):
    step = (end - start) / 5
    rows = []
    for k in range(5):
        a, b = start + k * step, start + (k + 1) * step
        birds = {}
        for i, name in enumerate(BIRDS):
            act = ACTS[(i - (ruling + k)) % 5]
            birds[name] = {"activity": act, "quality": ACT_QUALITY[act]}
        rows.append({"yama": k + 1, "start": fmt(a, tz), "end": fmt(b, tz),
                     "ruling_bird": BIRDS[(ruling + k) % 5], "birds": birds})
    return rows


def pancha_pakshi(wd, paksha, sr, ss, nsr, tz, fmt, janma_nakshatra=None):
    day_r = RULING[paksha][wd]
    night_r = (day_r + 2) % 5
    out = {
        "day_ruling_bird": BIRDS[day_r],
        "night_ruling_bird": BIRDS[night_r],
        "day": _periods(sr, ss, day_r, tz, fmt),
        "night": _periods(ss, nsr, night_r, tz, fmt),
        "note": "Act while your bird is Ruling or Eating. Wait while it Sleeps or Dies.",
    }
    if janma_nakshatra is not None:
        bird = birth_bird(janma_nakshatra, paksha)
        friends, enemies = FRIENDS[bird]
        out["birth_bird"] = {"bird": bird, "friends": friends, "enemies": enemies, "paksha": paksha}
    return out


def agnivasa(tithi_index: int) -> str:
    n = (tithi_index % 15) + 1
    return ("Prithvi" if n % 3 == 1 else "Akasha" if n % 3 == 2 else "Patala")


def chandra_vasa(moon_rashi_index: int) -> str:
    return DIRS[moon_rashi_index % 4]


def solar_gate(d, sign_index, tz):
    """Pravishte: 1 on the local date the Sun enters this sidereal sign."""
    from .ephem import local_midnight_jd, local_from_jd
    from .panchang import sun_sid
    noon = local_midnight_jd(d, tz) + 0.5
    t = noon
    for _ in range(40):
        if int(sun_sid(t) // 30) != sign_index:
            break
        t -= 1
    else:
        return {"gate": None}
    lo, hi = t, min(t + 1.2, noon)
    for _ in range(24):
        mid = (lo + hi) / 2
        if int(sun_sid(mid) // 30) == sign_index:
            hi = mid
        else:
            lo = mid
    entered = local_from_jd(hi, tz).date()
    return {"gate": (d - entered).days + 1, "sankranti_date": entered.isoformat(),
            "sign_index": sign_index}


def _lord_on(d):
    return WEEKDAY_LORD[(d.weekday() + 1) % 7] if d else None


def _cross_date(start, end, tz, target):
    """Local date when sidereal Sun longitude passes `target` (degrees)."""
    from .ephem import local_midnight_jd, local_from_jd
    from .panchang import sun_sid
    prev_s, prev_t = None, None
    dd = start
    while dd <= end:
        t = local_midnight_jd(dd, tz) + 0.5
        s = sun_sid(t)
        if prev_s is not None:
            span = (s - prev_s) % 360
            along = (target - prev_s) % 360
            if span < 40 and along <= span:
                lo, hi = prev_t, t
                for _ in range(22):
                    mid = (lo + hi) / 2
                    if (sun_sid(mid) - prev_s) % 360 >= along:
                        hi = mid
                    else:
                        lo = mid
                return local_from_jd(hi, tz).date()
        prev_s, prev_t = s, t
        dd += timedelta(days=1)
    return None


@lru_cache(maxsize=48)
def _mantri(anchor_iso: str, lat: float, lon: float, tz_name: str | None, utc_offset: float | None):
    from datetime import date as Date
    from .ephem import make_tz, local_from_jd
    from .panchang import lunar_month, prev_new_moon
    d0 = Date.fromisoformat(anchor_iso)
    tz = make_tz(tz_name, utc_offset)
    from .ephem import jd_from_utc
    from datetime import datetime, timezone
    # Walk new moons, not sunrises. Shukla Pratipada of nija Chaitra can be kshaya
    # (2026: the tithi never contains a sunrise) so the year-lord is the local
    # weekday of the new moon that opens that month.
    noon = datetime(d0.year, d0.month, d0.day, 12, tzinfo=timezone.utc)
    t = jd_from_utc(noon)
    found = None
    for _ in range(18):
        nm = prev_new_moon(t)
        if nm is None:
            break
        m, adhika, nm1, _nm2 = lunar_month(nm + 0.8)
        if m == 0 and not adhika:
            found = local_from_jd(nm1, tz).date()
            break
        t = nm - 0.2
    if not found:
        return None
    nya = found
    end = nya + timedelta(days=380)
    posts = [
        ("Raja", "Weekday lord of Chaitra Shukla Pratipada", nya),
        ("Mantri", "Weekday lord of Mesha Sankranti", _cross_date(nya, end, tz, 0)),
        ("Senadhipati", "Weekday lord of Simha Sankranti", _cross_date(nya, end, tz, 120)),
        ("Sasyadhipati", "Weekday lord of Karka Sankranti", _cross_date(nya, end, tz, 90)),
        ("Meghadhipati", "Weekday lord when the Sun enters Ardra", _cross_date(nya, end, tz, 5 * 360 / 27)),
        ("Rasadhipati", "Weekday lord of Tula Sankranti", _cross_date(nya, end, tz, 180)),
        ("Nirasadhipati", "Weekday lord of Makara Sankranti", _cross_date(nya, end, tz, 270)),
    ]
    return {
        "new_year": nya.isoformat(),
        "source": "Narada Samhita",
        "posts": [{"role": role, "rule": rule, "date": when.isoformat() if when else None, "planet": _lord_on(when)}
                  for role, rule, when in posts],
    }


def mantri_mandala(d, lat, lon, tz_name, utc_offset):
    return _mantri(d.isoformat(), round(lat, 1), round(lon, 1), tz_name, utc_offset)


def day_extras(d, lat, lon, tz, tz_name, utc_offset, sr, ss, nsr, day, night, sun_sign, wd, paksha, tithi_index, moon_rashi, janma_nakshatra, fmt):
    from .ephem import local_from_jd
    from datetime import datetime
    clock = {
        "dinamana": ghati_parts(day * 86400),
        "ratrimana": ghati_parts(night * 86400),
        "note": "Clock ghatis (24 minutes), not the 30 day-ghatis of the muhurta tables.",
    }
    now = datetime.now(tz)
    if now.date() == d:
        elapsed = (now - local_from_jd(sr, tz)).total_seconds()
        clock["since_sunrise"] = ghati_parts(elapsed)
    return {
        "vedic_time": clock,
        "pravishte": solar_gate(d, sun_sign, tz),
        "homahuti": WEEKDAY_LORD[wd],
        "agnivasa": agnivasa(tithi_index),
        "chandra_vasa": chandra_vasa(moon_rashi),
        "pancha_pakshi": pancha_pakshi(wd, paksha, sr, ss, nsr, tz, fmt, janma_nakshatra),
        "mantri_mandala": mantri_mandala(d, lat, lon, tz_name, utc_offset),
    }


def shivavasa(tithi_index: int) -> dict:
    """Where Shiva is, by the 1–30 tithi count (not folded to 15)."""
    n = tithi_index + 1
    place, quality = SHIVA[n % 7]
    return {"place": place, "quality": quality}


def tamil_yoga(weekday: int, ni27: int) -> dict:
    """Amritadi yoga (the Tamil weekday × nakshatra table)."""
    name = TAMIL_YOGA[ni27][weekday]
    return {"name": name, "auspicious": name in ("Siddha", "Amrita")}


def aadal_windows(moon_spans, sr, nsr, tz, fmt_fn):
    """Aadal while the Moon's nakshatra is the 2, 7, 9, 14, 16, 21 or 23rd from the Sun's.

    Count is 1 when both occupy the same of the 27 nakshatras. The Sun's
    nakshatra is sampled inside each Moon span, so a solar ingress during
    the night ends the yoga at that instant (10 Oct 2026, Mumbai: Aadal
    from Chitra's start until the Sun itself enters Chitra).
    """
    from .panchang import sun_sid
    step = 360 / 27

    def sun_i(t):
        return int(sun_sid(t) // step)

    raw = []
    for m in moon_spans:
        if m.get("_s") is None or m.get("_e") is None:
            continue
        a = max(m["_s"], sr)
        b = min(m["_e"], nsr)
        if b - a < 1e-6:
            continue
        mi = m["index"] - 1
        cuts = [a]
        s0, s1 = sun_i(a + 1e-6), sun_i(b - 1e-6)
        if s0 != s1:
            lo, hi = a, b
            for _ in range(24):
                mid = (lo + hi) / 2
                if sun_i(mid) == s0:
                    lo = mid
                else:
                    hi = mid
            cuts.append(hi)
        cuts.append(b)
        for c0, c1 in zip(cuts, cuts[1:]):
            si = sun_i((c0 + c1) / 2)
            count = (mi - si) % 27 + 1
            if count in AADAL_COUNTS:
                raw.append((c0, c1, count, m["name"]))
    raw.sort()
    merged = []
    for a, b, count, moon in raw:
        if merged and a - merged[-1][1] < 1 / 1440 and merged[-1][2] == count:
            pa, _pb, pc, pm = merged[-1]
            merged[-1] = (pa, b, pc, pm)
        else:
            merged.append((a, b, count, moon))
    return [{"start": fmt_fn(a, tz), "end": fmt_fn(b, tz), "count_from_sun": count,
             "moon_nakshatra": moon} for a, b, count, moon in merged]


def do_ghati(sr, ss, nsr, weekday, tz, fmt_fn):
    """Fifteen day muhurtas and fifteen night muhurtas (each is two ghatis).

    The 8th day muhurta is Abhijit and the 11th is Vijaya. Abhijit is not
    taken on Wednesday.
    """
    def rows(start, end, names, kalas):
        step = (end - start) / 15
        out = []
        for k, name in enumerate(names):
            auspicious = name in ("Abhijit", "Vijaya") and not (name == "Abhijit" and weekday == 3)
            label = "Vidhi" if name == "Abhijit" and weekday == 3 else name
            a, b = start + k * step, start + (k + 1) * step
            out.append({"n": k + 1, "name": label, "kala": kalas[k], "auspicious": auspicious,
                        "start": fmt_fn(a, tz), "end": fmt_fn(b, tz)})
        return out
    return {"day": rows(sr, ss, DAY_MUHURTA, DAY_KALA), "night": rows(ss, nsr, NIGHT_MUHURTA, NIGHT_KALA)}
