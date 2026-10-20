# PanchangHub SDKs
* `python/panchanghub.py` — stdlib-only Python client (copy into your project).
* `js/panchanghub.js` — ES module for browsers / Node 18+.
Both accept a `lang` option (hi, mr, gu, bn, ta, te, kn, ml) that localizes names in every response.
For other languages generate a client from the OpenAPI spec at `/api/openapi.json` (e.g. `openapi-generator-cli generate -i http://localhost:8000/api/openapi.json -g go`).
