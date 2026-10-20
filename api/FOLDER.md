# api/

This folder is the running server. See `../START-HERE.md` for how it connects to `../website/`.

```bash
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8080
```

`app/main.py` mounts the JSON API and then the HTML routes. The HTML files are the sibling `website/` folder. `app/web/__init__.py` locates them.

Deeper notes: `AGENT_REVIEW.md`. Endpoint samples: `README.md`.
