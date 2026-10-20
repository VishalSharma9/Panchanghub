"""Minimal Python SDK for the PanchangHub API (stdlib only).

    from panchanghub import PanchangHub
    ph = PanchangHub("http://localhost:8000", lang="hi")
    ph.panchang("2026-10-10", 28.6139, 77.209, "Asia/Kolkata")
    ph.kundli({"date": "1990-05-15", "time": "10:30:00", "latitude": 28.61, "longitude": 77.21, "timezone": "Asia/Kolkata"})
Any endpoint: ph.get("/api/festivals", year=2026, lat=..., lon=..., tz=...) / ph.post("/api/matching", body)
"""
import json, urllib.parse, urllib.request

class PanchangHub:
    def __init__(self, base_url="http://localhost:8000", lang=None, timeout=60):
        self.base = base_url.rstrip("/"); self.lang = lang; self.timeout = timeout
    def _url(self, path, params):
        params = {k: v for k, v in params.items() if v is not None}
        if self.lang and "lang" not in params: params["lang"] = self.lang
        return f"{self.base}{path}" + ("?" + urllib.parse.urlencode(params) if params else "")
    def get(self, path, **params):
        with urllib.request.urlopen(self._url(path, params), timeout=self.timeout) as r: return json.loads(r.read())
    def post(self, path, body, raw=False, **params):
        req = urllib.request.Request(self._url(path, params), data=json.dumps(body).encode(), headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=self.timeout) as r:
            data = r.read(); return data if raw else json.loads(data)
    # convenience wrappers
    def panchang(self, date, lat, lon, tz): return self.get("/api/panchang", date=date, lat=lat, lon=lon, tz=tz)
    def festivals(self, year, lat, lon, tz): return self.get("/api/festivals", year=year, lat=lat, lon=lon, tz=tz)
    def choghadiya(self, date, lat, lon, tz): return self.get("/api/choghadiya", date=date, lat=lat, lon=lon, tz=tz)
    def kundli(self, birth): return self.post("/api/kundli", birth)
    def interpretation(self, birth): return self.post("/api/kundli/interpretation", birth)
    def shadbala(self, birth): return self.post("/api/kundli/shadbala", birth)
    def dashas(self, birth): return self.post("/api/kundli/dashas", birth)
    def matching(self, boy, girl): return self.post("/api/matching", {"boy": boy, "girl": girl})
    def kundli_pdf(self, birth): return self.post("/api/kundli/pdf", birth, raw=True)
    def horoscope(self, sign, period="daily"): return self.get(f"/api/horoscope/{period}/{sign}")
    def numerology(self, name, dob): return self.get("/api/numerology", name=name, dob=dob)
    def human_design(self, birth): return self.post("/api/human-design", birth)
    def ask(self, question): return self.post("/api/ask", {"question": question})
