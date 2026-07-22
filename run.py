#!/usr/bin/env python3
"""Thai Answers — numbered menu."""
import pathlib
import subprocess
import sys
import webbrowser

ROOT = pathlib.Path(__file__).resolve().parent

MENU = """
  THAI ANSWERS
  ============
  1) Crawl OpenStreetMap for Chiang Mai massage/spa venues
  2) Build the site into docs/
  3) Open the site in your browser
  0) Quit
"""


def main():
    while True:
        print(MENU)
        choice = input("  Pick a number: ").strip()
        if choice == "1":
            subprocess.run([sys.executable, ROOT / "crawl_osm.py"])
        elif choice == "2":
            subprocess.run([sys.executable, ROOT / "build_site.py"])
        elif choice == "3":
            webbrowser.open((ROOT / "docs" / "index.html").as_uri())
        elif choice == "0":
            return
        else:
            print("  Not a menu number.")


if __name__ == "__main__":
    main()
