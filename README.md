# Newton Crime Map

An interactive map of crimes reported in Newton, Massachusetts, built from the Newton Police Department's public weekly incident logs.

**Live site:** https://eisensteinerez.github.io/newton-crime-map/

## What's here

- `index.html`: the whole website (map, filters, charts). Data is built in.
- `data/raw_logs/`: crime rows pulled from each weekly police log (one file per week).
- `data/geocache.json`: map coordinates for each address (US Census geocoder, with OpenStreetMap as backup).
- `scripts/`: the steps that turn the logs into the website.

## Data notes

- Source: Newton Police Department weekly incident logs posted on newtonma.gov.
- Only crime-related calls are kept. Medical calls, alarms, car crashes and patrols are left out.
- Locations are rounded to the block. A log entry is a call for service, not a conviction.
