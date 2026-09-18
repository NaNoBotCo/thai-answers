# Thai Answers

Turn the questions people ask every day in Thailand Facebook groups into evergreen,
source-marked answer pages — backed by a crawled catalogue of real venues plus a
human curation layer.

Stdlib Python only. No accounts, no API keys.

## Run it

```
python3 run.py
```

1. **Crawl** — one Overpass (OpenStreetMap) query pulls every massage/spa venue in
   greater Chiang Mai into `catalog.db`. Safe to re-run; it upserts.
2. **Build** — regenerates the static site in `docs/` (index, venue directory,
   answer pages).
3. **Open** — views `docs/index.html` locally.

Publish by pointing GitHub Pages (or any static host) at `docs/`, same as
nanobotco-lanna. Then answer a Facebook question with one link.

## Curation layer — `overrides.json`

OpenStreetMap knows *where* venues are, not whether they're any good or have a
massage table with a face cradle. That comes from you. Add entries keyed by
`osm_type/osm_id` (shown in the venue's map link):

```json
{
  "node/1234567": {
    "face_cradle_table": true,
    "note": "Verified by phone 2026-07 — two tables with face cradles, therapist trained at Old Medicine Hospital."
  }
}
```

Rebuild and the venue moves into the answer page's "Confirmed" section, with the
note rendered as **Curator —** (catalogue data stays unmarked; our framing is
marked **Editorial —**).

## Widening later (deliberately not built yet)

- More questions: each answer is a facet filter + editorial frame over the same
  catalogue. Add to `build_site.py`.
- More sources: Google Places API (needs key/billing), review mining (ToS-gray),
  crowdsourced verification form. **Facebook group scraping is against FB ToS and
  brittle — the intake for questions is you reading the group, not a crawler.**
- More geography: widen the bbox or add cities.

Data © OpenStreetMap contributors, ODbL — attribution stays on every page.


## Licence

Records, prose and pages: CC BY 4.0. Code: MIT. Attribution is the only
condition — name the work and link back. Anything carried in from elsewhere
keeps its own terms — see [LICENSE](LICENSE) and [NOTICE.txt](NOTICE.txt).

**Using it.** Attribution is the whole of the condition — copy it, adapt it,
sell it, index it, train on it, and say where it came from.
[Open an issue](https://github.com/NaNoBotCo/thai-answers/issues) if something is missing.

---

Contact: Nan · nan@motdang.net · Sponsor: [Ko-fi](https://ko-fi.com/defiantchiangmai) · [Patreon](https://www.patreon.com/nanobotco)
