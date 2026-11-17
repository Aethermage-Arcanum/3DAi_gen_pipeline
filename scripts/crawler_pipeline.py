"""Alter Einstieg für Krabbler – leitet nur noch an scripts/creature_pipeline.py weiter (eine Pipeline für alle Skelette).

  python scripts/crawler_pipeline.py creatures/chitin_crawler [gleiche Optionen wie creature_pipeline.py]
"""
import pathlib
import subprocess
import sys

if __name__ == "__main__":
    here = pathlib.Path(__file__).resolve().parent
    raise SystemExit(subprocess.call([sys.executable, str(here / "creature_pipeline.py"), *sys.argv[1:]]))
