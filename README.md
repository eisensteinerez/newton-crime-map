# Newton After Dark

An interactive map of crimes reported in Newton, Massachusetts, built from the Newton Police Department's public weekly incident logs.

**Live site:** https://eisensteinerez.github.io/newton-crime-map/

## What's here

- `index.html`: the whole website (map, filters, charts). Data is built in.
- `data/raw_logs/`: crime rows from the 2023 weekly police logs.
- `data/crimes25.json`, `data/crimes26.json`: crime rows read (by OCR) from the Oct 2025 – Mar 2026 daily logs.
- `data/geocache.json`: map coordinates for each address (US Census geocoder, with OpenStreetMap as backup).
- `scripts/`: `ocr.py` reads a scanned daily log PDF, `parse.py` keeps the crimes, `build2.py` geocodes and builds the data, `assemble2.py` writes `index.html`.

Map tiles: OpenFreeMap (free, no key). Map engine: MapLibre GL.

## Data notes

- Source: Newton Police Department weekly incident logs posted on newtonma.gov.
- Only crime-related calls are kept. Medical calls, alarms, car crashes and patrols are left out.
- Locations are rounded to the block. A log entry is a call for service, not a conviction.
