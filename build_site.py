#!/usr/bin/env python3
"""Build the static answer site into docs/ from catalog.db (+ overrides.json curation layer).

Every published claim keeps its provenance: plain rows = catalogue data (OpenStreetMap),
"Curator —" = human enrichment from overrides.json, "Editorial —" = our own framing.
"""
import html
import json
import pathlib
import sqlite3
import time

ROOT = pathlib.Path(__file__).resolve().parent
DB = ROOT / "catalog.db"
DOCS = ROOT / "docs"
OVERRIDES = ROOT / "overrides.json"

CSS = """
:root { color-scheme: light dark; }
body { font-family: Georgia, 'Times New Roman', serif; font-size: 1.25rem;
       line-height: 1.6; max-width: 46rem; margin: 2rem auto; padding: 0 1rem; }
h1 { line-height: 1.25; }
a { color: #0b63a5; } @media (prefers-color-scheme: dark) { a { color: #7ec3f0; } }
table { border-collapse: collapse; width: 100%; font-size: 1.05rem; }
td, th { border-bottom: 1px solid #8884; padding: .45em .5em; text-align: left;
         vertical-align: top; }
.gap { border: 2px solid #b8860b; border-radius: .5em; padding: .8em 1em; }
.prov { font-size: .95rem; opacity: .75; margin-top: 3rem; }
.note { background: #b8860b22; padding: .1em .3em; border-radius: .3em; }
"""


def page(title, body):
    return (f"<!doctype html><meta charset='utf-8'>"
            f"<meta name='viewport' content='width=device-width, initial-scale=1'>"
            f"<title>{html.escape(title)}</title><style>{CSS}</style>{body}")


def esc(s):
    return html.escape(s or "")


def load_venues():
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    rows = [dict(r) for r in con.execute(
        "SELECT * FROM venues WHERE name IS NOT NULL OR name_en IS NOT NULL "
        "ORDER BY in_old_city DESC, COALESCE(name_en, name)")]
    con.close()
    overrides = json.loads(OVERRIDES.read_text()) if OVERRIDES.exists() else {}
    for r in rows:
        r["curation"] = overrides.get(f"{r['osm_type']}/{r['osm_id']}", {})
    return rows


def venue_rows(venues):
    out = []
    for v in venues:
        name = v.get("name_en") or v.get("name")
        thai = v.get("name") if v.get("name_en") and v.get("name") != v.get("name_en") else ""
        link = f"https://www.openstreetmap.org/?mlat={v['lat']}&mlon={v['lon']}#map=19/{v['lat']}/{v['lon']}"
        bits = []
        if v.get("phone"):
            bits.append(esc(v["phone"]))
        if v.get("website"):
            bits.append(f"<a href='{esc(v['website'])}'>website</a>")
        if v.get("opening_hours"):
            bits.append(esc(v["opening_hours"]))
        cur = v["curation"].get("note")
        if cur:
            bits.append(f"<span class='note'>Curator — {esc(cur)}</span>")
        out.append(f"<tr><td><a href='{link}'>{esc(name)}</a>"
                   f"{('<br><small>' + esc(thai) + '</small>') if thai else ''}</td>"
                   f"<td>{' · '.join(bits)}</td></tr>")
    return "\n".join(out)


# Where the site will live once deployed (e.g. a GitHub Pages URL). While empty,
# feed items carry no url, so subscribers (the wichaa.net answers widget) render
# titles + summaries without ever linking a page that doesn't exist yet.
BASE_URL = ""

ANSWER_SLUG = "thai-massage-old-city-table"
ANSWER_TITLE = ("Where can I get a proper therapeutic Thai massage in Chiang Mai's "
                "old city — on a table with a face cradle?")


def build_answer(venues):
    inside = [v for v in venues if v["in_old_city"]]
    tabled = [v for v in inside if v["curation"].get("face_cradle_table")]
    tabled_html = ""
    if tabled:
        tabled_html = ("<h2>Confirmed: table with face cradle</h2><table>"
                       "<tr><th>Venue</th><th>Details</th></tr>"
                       + venue_rows(tabled) + "</table>")
    body = f"""
<h1>{esc(ANSWER_TITLE)}</h1>
<p><em>The question, as people actually ask it:</em> a long-time massage client's
therapist retired. She wants a properly trained therapist in the old city who works
the whole body — arms, ribs, under the shoulder blades, not just down the spine —
and uses a massage table with a face hole, because of a bad neck.</p>

<p><em>Editorial —</em> that question is really three separate filters:
<strong>location</strong> (inside the moat), <strong>equipment</strong>
(table with face cradle, not a floor mat — most traditional Thai massage is mat-based),
and <strong>skill/style</strong> (targeted therapeutic work, not a fixed routine).
The first we can answer from open map data today; the other two need on-the-ground
verification, which is exactly what this page accumulates over time.</p>

{tabled_html}

<h2>Every massage venue inside the old-city moat ({len(inside)} known)</h2>
<p>Plain rows are catalogue data from OpenStreetMap — presence, location, and contact
details only. A listing here is <strong>not</strong> a recommendation.</p>
<table><tr><th>Venue</th><th>Details</th></tr>
{venue_rows(inside)}
</table>

<div class='gap'><strong>Known gaps (what the map cannot tell you):</strong>
<ul>
<li><strong>Table vs. floor mat, and face cradles</strong> — not recorded in any open
dataset. Filled venue-by-venue via curator verification (call, visit, or trusted report).</li>
<li><strong>Training</strong> — e.g. Wat Pho or TTM school certification, licensed
physical-therapy crossover. Same enrichment path.</li>
<li><strong>Therapeutic focus</strong> — whether a therapist assesses and targets rather
than running a fixed sequence. Only fillable by verified first-hand reports.</li>
</ul></div>

<p class='prov'>Map data © <a href='https://www.openstreetmap.org/copyright'>OpenStreetMap
contributors</a> (ODbL). Built {time.strftime('%Y-%m-%d')}. Curator notes are marked;
everything else is raw catalogue data.</p>
"""
    return page(ANSWER_TITLE, body)


def build_directory(venues):
    inside = [v for v in venues if v["in_old_city"]]
    outside = [v for v in venues if not v["in_old_city"]]
    body = f"""
<h1>Massage &amp; spa venues — Chiang Mai</h1>
<p>{len(venues)} named venues from OpenStreetMap. Listing ≠ recommendation.</p>
<h2>Inside the old-city moat ({len(inside)})</h2>
<table><tr><th>Venue</th><th>Details</th></tr>{venue_rows(inside)}</table>
<h2>Greater Chiang Mai ({len(outside)})</h2>
<table><tr><th>Venue</th><th>Details</th></tr>{venue_rows(outside)}</table>
<p class='prov'>Map data © <a href='https://www.openstreetmap.org/copyright'>OpenStreetMap
contributors</a> (ODbL). Built {time.strftime('%Y-%m-%d')}.</p>
"""
    return page("Massage venues — Chiang Mai", body)


def build_index():
    body = f"""
<h1>Thai Answers</h1>
<p>Long-form, source-marked answers to the questions people actually ask about
living in and visiting Thailand — built from open data plus verified local knowledge.</p>
<h2>Answers</h2>
<ul><li><a href='answers/{ANSWER_SLUG}.html'>{esc(ANSWER_TITLE)}</a></li></ul>
<h2>Data</h2>
<ul><li><a href='venues.html'>Massage &amp; spa venue directory (Chiang Mai)</a></li></ul>
"""
    return page("Thai Answers", body)


def build_feed(venues):
    """JSON Feed 1.1 (jsonfeed.org) — the machine door for syndication; the
    wichaa.net answers widget is its first subscriber."""
    inside = sum(1 for v in venues if v["in_old_city"])
    item = {
        "id": ANSWER_SLUG,
        "title": ANSWER_TITLE,
        "summary": (f"Every massage venue inside Chiang Mai's old-city moat "
                    f"({inside} known from open map data), plus an honest account of "
                    "what open data can and cannot verify: face-cradle tables, "
                    "training, and therapeutic skill are curator-verified, one venue "
                    "at a time."),
        "content_text": ("The question is really three filters — location, equipment "
                         "(a table with a face cradle, not a floor mat), and targeted "
                         "therapeutic skill. Open map data answers the first; the "
                         "curation layer accumulates the rest."),
        "date_published": "2026-07-14T00:00:00Z",
    }
    if BASE_URL:
        item["url"] = f"{BASE_URL}/answers/{ANSWER_SLUG}.html"
    feed = {
        "version": "https://jsonfeed.org/version/1.1",
        "title": "Thai Answers",
        "description": ("Evergreen, source-marked answers to the questions people "
                        "actually ask about living in and visiting Thailand."),
        "items": [item],
    }
    if BASE_URL:
        feed["home_page_url"] = BASE_URL
        feed["feed_url"] = f"{BASE_URL}/feed.json"
    return feed


def main():
    venues = load_venues()
    (DOCS / "answers").mkdir(parents=True, exist_ok=True)
    (DOCS / "index.html").write_text(build_index())
    (DOCS / "venues.html").write_text(build_directory(venues))
    (DOCS / "answers" / f"{ANSWER_SLUG}.html").write_text(build_answer(venues))
    (DOCS / "feed.json").write_text(
        json.dumps(build_feed(venues), ensure_ascii=False, indent=1))
    inside = sum(1 for v in venues if v["in_old_city"])
    print(f"built docs/ — {len(venues)} named venues ({inside} in old city), "
          f"1 answer page, feed.json")


if __name__ == "__main__":
    main()
