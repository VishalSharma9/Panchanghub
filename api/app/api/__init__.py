"""Router registry. To add a feature module (e.g. numerology, KP, Lal Kitab), create
app/core/<feature>.py + app/api/routers/<feature>.py exposing `router`, then list it here."""
ROUTERS = ["core", "panchang", "vedic", "calendar", "geo", "extras", "more", "regional", "studio", "auth"]
ROOT_ALIASES = ["core"]  # also mounted without /api prefix (original spec paths)
