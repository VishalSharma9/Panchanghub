import json
import urllib.parse
import urllib.request
import time
import sys

BASE_URL = "http://127.0.0.1:8080"

BIRTH_PAYLOAD = {
    "date": "1990-05-15",
    "time": "14:30:00",
    "latitude": 28.6139,
    "longitude": 77.2090,
    "timezone": "Asia/Kolkata",
    "name": "Arjun Sharma"
}

MATCH_PAYLOAD = {
    "boy": {
        "date": "1992-08-20",
        "time": "09:15:00",
        "latitude": 28.6139,
        "longitude": 77.2090,
        "timezone": "Asia/Kolkata"
    },
    "girl": {
        "date": "1994-11-12",
        "time": "18:45:00",
        "latitude": 19.0760,
        "longitude": 72.8777,
        "timezone": "Asia/Kolkata"
    }
}

routes_get = [
    # Static & Documentation
    "/api/docs",
    "/api/openapi.json",
    "/static/style.css",
    "/static/app.js",
    "/robots.txt",
    "/sitemap.xml",
    
    # Core Vedic Pages
    "/",
    "/panchang",
    "/calendar",
    "/kundli",
    "/matching",
    "/muhurat",
    "/transits",
    "/horoscope",
    
    # Reverse-Engineered Feature Pages
    "/vargas",
    "/yogas",
    "/reading",
    
    # Daily Panchang Tools
    "/choghadiya",
    "/hora",
    "/rahu-kaal",
    "/lagna-table",
    "/festivals",
    "/sade-sati",
    "/mine",
    "/compare",
    "/names",
    "/week",
    
    # Complementary Astrology Systems
    "/western",
    "/numerology",
    "/tarot",
    "/human-design",
    "/vastu",
    "/iching",
    "/palmistry",
    "/regional",
    "/tools",
    "/widget/panchang",
    
    # Geo & Public APIs
    "/api/cities?q=delhi&limit=5",
    "/api/cities/nearest?lat=28.6139&lon=77.2090",
    "/api/cities/timezone?tz=Asia/Kolkata",
    "/api/cities/stats",
    "/api/panchang?date=2026-10-18&lat=28.6139&lon=77.2090&tz=Asia/Kolkata",
    "/api/choghadiya?date=2026-10-18&lat=28.6139&lon=77.2090&tz=Asia/Kolkata",
    "/api/hora?date=2026-10-18&lat=28.6139&lon=77.2090&tz=Asia/Kolkata",
]

routes_post = [
    ("/api/kundli", BIRTH_PAYLOAD, "JSON"),
    ("/api/kundli/vargas", BIRTH_PAYLOAD, "JSON"),
    ("/api/kundli/yogas", BIRTH_PAYLOAD, "JSON"),
    ("/api/kundli/reading", BIRTH_PAYLOAD, "JSON"),
    ("/api/kundli/dashas/current", BIRTH_PAYLOAD, "JSON"),
    ("/api/kundli/dashas/yogini", BIRTH_PAYLOAD, "JSON"),
    ("/api/kundli/dashas/chara", BIRTH_PAYLOAD, "JSON"),
    ("/api/kundli/ayanamshas", BIRTH_PAYLOAD, "JSON"),
    ("/api/matching", MATCH_PAYLOAD, "JSON"),
    ("/api/kundli/pdf", BIRTH_PAYLOAD, "PDF"),
]

def run_fire_test():
    passed = 0
    failed = 0
    total = len(routes_get) + len(routes_post) + 1  # +1 for cookie test
    start_time = time.time()
    
    print(f"============================================================")
    print(f"       PANCHANGHUB DEEP LIVE FIRE TEST ({total} checks)")
    print(f"============================================================\n")
    
    # 1. GET checks
    print("--- [1/3] Testing GET Routes (Website & Query APIs) ---")
    for r in routes_get:
        url = BASE_URL + r
        try:
            t0 = time.time()
            req = urllib.request.Request(url, headers={"User-Agent": "FireTest/1.0"})
            with urllib.request.urlopen(req, timeout=10) as resp:
                elapsed = (time.time() - t0) * 1000
                status = resp.status
                data = resp.read()
                size = len(data)
                if status == 200 and size > 0:
                    print(f"  [PASS] {status} ({elapsed:5.1f}ms, {size:6d}B) {r}")
                    passed += 1
                else:
                    print(f"  [FAIL] {status} {r} - Empty or non-200")
                    failed += 1
        except Exception as e:
            print(f"  [FAIL] ERROR: {r} -> {e}")
            failed += 1

    # 2. POST checks (Calculations, Yogas, Vargas, Reading, PDF)
    print("\n--- [2/3] Testing POST Calculation Endpoints ---")
    for path, payload, exp_type in routes_post:
        url = BASE_URL + path
        try:
            t0 = time.time()
            req_data = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(
                url, data=req_data,
                headers={"Content-Type": "application/json", "User-Agent": "FireTest/1.0"}
            )
            with urllib.request.urlopen(req, timeout=15) as resp:
                elapsed = (time.time() - t0) * 1000
                status = resp.status
                content = resp.read()
                size = len(content)
                if status == 200:
                    if exp_type == "PDF":
                        if content.startswith(b"%PDF-"):
                            print(f"  [PASS] {status} ({elapsed:5.1f}ms, {size:6d}B PDF) {path}")
                            passed += 1
                        else:
                            print(f"  [FAIL] {path} returned 200 but not valid PDF header!")
                            failed += 1
                    else:
                        j = json.loads(content.decode("utf-8"))
                        keys = list(j.keys()) if isinstance(j, dict) else f"list({len(j)})"
                        print(f"  [PASS] {status} ({elapsed:5.1f}ms) {path} -> keys: {keys}")
                        passed += 1
                else:
                    print(f"  [FAIL] {status} {path}")
                    failed += 1
        except Exception as e:
            print(f"  [FAIL] ERROR: {path} -> {e}")
            failed += 1

    # 3. Cookie Persistence & Unquote Test
    print("\n--- [3/3] Testing Cookie Persistence & Unquoting ---")
    cookie_obj = {
        "city": "Mumbai, Maharashtra, India",
        "lat": 19.0760,
        "lon": 72.8777,
        "tz": "Asia/Kolkata",
        "src": "gps"
    }
    encoded_cookie = urllib.parse.quote(json.dumps(cookie_obj))
    cookie_header = f"ph_loc={encoded_cookie}"
    try:
        t0 = time.time()
        req = urllib.request.Request(
            BASE_URL + "/panchang",
            headers={"User-Agent": "FireTest/1.0", "Cookie": cookie_header}
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            elapsed = (time.time() - t0) * 1000
            html = resp.read().decode("utf-8")
            if "Mumbai" in html and 'data-source="gps"' in html:
                print(f"  [PASS] ({elapsed:5.1f}ms) Cookie 'ph_loc' parsed correctly -> city 'Mumbai' rendered, data-source='gps' (NO reload loop!)")
                passed += 1
            else:
                print(f"  [FAIL] Cookie was not resolved in rendered HTML! Check loc_from.")
                failed += 1
    except Exception as e:
        print(f"  [FAIL] Cookie test failed: {e}")
        failed += 1

    total_time = time.time() - start_time
    print(f"\n============================================================")
    print(f"FIRE TEST RESULTS: {passed}/{total} PASSED ({failed} failed) in {total_time:.2f}s")
    print(f"============================================================")
    
    if failed > 0:
        sys.exit(1)

if __name__ == "__main__":
    run_fire_test()
