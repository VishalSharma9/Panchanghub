"""Build data/places.sqlite from the GeoNames allCountries dump.

Includes every current populated place (cities, towns, villages, localities).
Historical, abandoned and destroyed places are left out. GeoNames is CC-BY.
"""
from __future__ import annotations
import os, sqlite3, sys, zipfile
from zoneinfo import available_timezones

ROOT = os.path.dirname(os.path.abspath(__file__))
ZIP = os.environ.get("GEONAMES_ZIP", "/tmp/allCountries.zip")
ADMIN = os.environ.get("GEONAMES_ADMIN1", "/tmp/admin1CodesASCII.txt")
COUNTRY = os.environ.get("GEONAMES_COUNTRY", "/tmp/countryInfo.txt")
OUT = os.path.join(ROOT, "places.sqlite")
SKIP = {"PPLH", "PPLQ", "PPLW", "PPLCH"}  # historical, abandoned, destroyed, historical capital

def load_countries(path):
    out = {}
    for line in open(path, encoding="utf8"):
        if not line.strip() or line.startswith("#"):
            continue
        p = line.rstrip("\n").split("\t")
        if len(p) > 4:
            out[p[0]] = p[4]
    return out

def load_admin(path):
    out = {}
    for line in open(path, encoding="utf8"):
        p = line.rstrip("\n").split("\t")
        if len(p) >= 2:
            out[p[0]] = p[1]
    return out

def cell_of(lat, lon):
    la = min(719, max(0, int((lat + 90) * 4)))
    lo = int((lon + 180) * 4) % 1440
    return la * 1440 + lo

def main():
    tz_ok = available_timezones()
    countries = load_countries(COUNTRY)
    admin = load_admin(ADMIN)
    if os.path.exists(OUT):
        os.remove(OUT)
    con = sqlite3.connect(OUT)
    con.execute("PRAGMA journal_mode=OFF")
    con.execute("PRAGMA synchronous=OFF")
    con.execute("PRAGMA temp_store=MEMORY")
    con.execute("PRAGMA cache_size=-400000")
    con.execute("""CREATE TABLE places (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL, ascii TEXT NOT NULL, alt TEXT NOT NULL,
        cc TEXT NOT NULL, country TEXT NOT NULL,
        admin TEXT NOT NULL, admin_name TEXT NOT NULL,
        lat REAL NOT NULL, lon REAL NOT NULL, tz TEXT NOT NULL,
        pop INTEGER NOT NULL, fcode TEXT NOT NULL, cell INTEGER NOT NULL)""")
    sql = "INSERT INTO places VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)"
    batch, n, skipped = [], 0, 0
    with zipfile.ZipFile(ZIP) as zf:
        with zf.open("allCountries.txt") as raw:
            for bline in raw:
                p = bline.decode("utf8", "replace").rstrip("\n").split("\t")
                if len(p) < 18 or p[6] != "P" or p[7] in SKIP:
                    continue
                tz = p[17]
                if tz not in tz_ok:
                    skipped += 1
                    continue
                try:
                    lat, lon = float(p[4]), float(p[5])
                except ValueError:
                    continue
                if not (-90 <= lat <= 90 and -180 <= lon <= 180):
                    continue
                pop = int(p[14]) if p[14].isdigit() else 0
                cc, adm = p[8], p[10]
                alt = p[3][:400]
                batch.append((int(p[0]), p[1][:200], (p[2] or p[1])[:200], alt, cc,
                              countries.get(cc, cc), adm, admin.get(f"{cc}.{adm}", ""),
                              lat, lon, tz, pop, p[7], cell_of(lat, lon)))
                if len(batch) >= 8000:
                    con.executemany(sql, batch)
                    n += len(batch)
                    batch.clear()
                    if n % 400000 == 0:
                        print(f"  {n:,} places", flush=True)
    if batch:
        con.executemany(sql, batch)
        n += len(batch)
    print(f"loaded {n:,} (skipped {skipped:,} without a usable timezone)", flush=True)
    print("indexing…", flush=True)
    con.execute("CREATE INDEX idx_places_cell ON places(cell)")
    con.execute("CREATE INDEX idx_places_ascii ON places(ascii)")
    con.execute("""CREATE VIRTUAL TABLE places_fts USING fts5(
        name, ascii, alt, content='places', content_rowid='id',
        tokenize='unicode61 remove_diacritics 2')""")
    con.execute("INSERT INTO places_fts(places_fts) VALUES('rebuild')")
    con.commit()
    con.close()
    print(f"wrote {OUT} ({os.path.getsize(OUT)/1e6:.0f} MB)", flush=True)

if __name__ == "__main__":
    sys.exit(main())
