# Builds the split layout: api/ is the server, website/ is the HTML.
FROM python:3.12-slim AS build
RUN apt-get update && apt-get install -y --no-install-recommends gcc g++ && rm -rf /var/lib/apt/lists/*
WORKDIR /build
COPY api/requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 SE_EPHE_PATH=/srv/api/ephe
WORKDIR /srv
COPY --from=build /install /usr/local
COPY api /srv/api
COPY website /srv/website
WORKDIR /srv/api
EXPOSE 8000
HEALTHCHECK CMD python -c "import urllib.request;urllib.request.urlopen('http://127.0.0.1:8000/health')" || exit 1
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
