// Minimal JS/TS-friendly SDK for the PanchangHub API (works in browsers and Node 18+).
// const ph = new PanchangHub("http://localhost:8000", { lang: "ta" });
// await ph.panchang("2026-10-10", 13.08, 80.27, "Asia/Kolkata");
export class PanchangHub {
  constructor(base = "http://localhost:8000", { lang } = {}) { this.base = base.replace(/\/$/, ""); this.lang = lang; }
  url(path, params = {}) {
    const q = new URLSearchParams(Object.entries({ ...(this.lang ? { lang: this.lang } : {}), ...params }).filter(([, v]) => v != null));
    return `${this.base}${path}${q.toString() ? "?" + q : ""}`;
  }
  async get(path, params) { const r = await fetch(this.url(path, params)); if (!r.ok) throw new Error(await r.text()); return r.json(); }
  async post(path, body, params) {
    const r = await fetch(this.url(path, params), { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) });
    if (!r.ok) throw new Error(await r.text()); return r.headers.get("content-type")?.includes("json") ? r.json() : r.arrayBuffer();
  }
  panchang(date, lat, lon, tz) { return this.get("/api/panchang", { date, lat, lon, tz }); }
  festivals(year, lat, lon, tz) { return this.get("/api/festivals", { year, lat, lon, tz }); }
  kundli(birth) { return this.post("/api/kundli", birth); }
  interpretation(birth) { return this.post("/api/kundli/interpretation", birth); }
  matching(boy, girl) { return this.post("/api/matching", { boy, girl }); }
  horoscope(sign, period = "daily") { return this.get(`/api/horoscope/${period}/${sign}`); }
  humanDesign(birth) { return this.post("/api/human-design", birth); }
  ask(question) { return this.post("/api/ask", { question }); }
}
