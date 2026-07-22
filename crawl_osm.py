#!/usr/bin/env python3
"""Fetch massage/spa venues in Chiang Mai from OpenStreetMap (Overpass API) into catalog.db.

Data (c) OpenStreetMap contributors, ODbL. One light query per run; be polite.
"""
import json
import pathlib
import sqlite3
import time
import urllib.parse
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent
DB = ROOT / "catalog.db"
OVERPASS_MIRRORS = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
    "https://overpass.private.coffee/api/interpreter",
]

# south, west, north, east
GREATER_CM = (18.75, 98.93, 18.83, 99.05)
OLD_CITY = (18.7800, 98.9770, 18.7965, 98.9940)  # the moat square, approx

QUERY = """
[out:json][timeout:90];
(
  nwr["shop"="massage"]({s},{w},{n},{e});
  nwr["leisure"="spa"]({s},{w},{n},{e});
  nwr["amenity"="spa"]({s},{w},{n},{e});
);
out center tags;
""".format(s=GREATER_CM[0], w=GREATER_CM[1], n=GREATER_CM[2], e=GREATER_CM[3])

DDL = """
CREATE TABLE IF NOT EXISTS venues(
  osm_type TEXT NOT NULL,
  osm_id   INTEGER NOT NULL,
  name     TEXT,
  name_en  TEXT,
  lat REAL, lon REAL,
  in_old_city INTEGER,
  phone TEXT, website TEXT, opening_hours TEXT,
  tags TEXT,
  fetched_at TEXT,
  PRIMARY KEY (osm_type, osm_id)
);
"""


def in_old_city(lat, lon):
    s, w, n, e = OLD_CITY
    return 1 if (s <= lat <= n and w <= lon <= e) else 0


def main():
    body = urllib.parse.urlencode({"data": QUERY}).encode()
    payload = None
    for url in OVERPASS_MIRRORS:
        req = urllib.request.Request(url, data=body, headers={
            "User-Agent": "thai-answers/0.1 (personal research project)"})
        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                payload = json.load(resp)
            break
        except (urllib.error.URLError, TimeoutError) as e:
            print(f"  {url} failed ({e}); trying next mirror...")
    if payload is None:
        raise SystemExit("all Overpass mirrors failed — try again in a few minutes")

    con = sqlite3.connect(DB)
    con.execute(DDL)
    now = time.strftime("%Y-%m-%d %H:%M:%S")
    kept = 0
    for el in payload.get("elements", []):
        tags = el.get("tags") or {}
        lat = el.get("lat") or (el.get("center") or {}).get("lat")
        lon = el.get("lon") or (el.get("center") or {}).get("lon")
        if lat is None or lon is None:
            continue
        con.execute(
            "INSERT OR REPLACE INTO venues VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
            (el["type"], el["id"],
             tags.get("name"), tags.get("name:en"),
             lat, lon, in_old_city(lat, lon),
             tags.get("phone") or tags.get("contact:phone"),
             tags.get("website") or tags.get("contact:website"),
             tags.get("opening_hours"),
             json.dumps(tags, ensure_ascii=False), now))
        kept += 1
    con.commit()
    total = con.execute("SELECT COUNT(*) FROM venues").fetchone()[0]
    old = con.execute("SELECT COUNT(*) FROM venues WHERE in_old_city=1").fetchone()[0]
    named = con.execute("SELECT COUNT(*) FROM venues WHERE name IS NOT NULL").fetchone()[0]
    print(f"fetched {kept} elements; catalog now {total} venues "
          f"({old} inside the old-city moat, {named} named)")
    con.close()


if __name__ == "__main__":
    main()
