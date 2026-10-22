#!/usr/bin/env python3
"""Fetch an attributed OpenStreetMap extract around Dushanbe's Istiklol Monument.

It is used to rebuild building footprints, roads, plazas, parks and mapped trees.
This is OSM-derived geometry, not imagery or photogrammetry.
"""
from __future__ import annotations
import argparse, json, sys, time, urllib.error, urllib.parse, urllib.request
from datetime import datetime, timezone
from pathlib import Path

SOUTH, WEST, NORTH, EAST = 38.58200, 68.77100, 38.60050, 68.79250
ANCHOR_LAT, ANCHOR_LON = 38.59124, 68.78162
ENDPOINTS = (
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
    "https://overpass.private.coffee/api/interpreter",
)

def make_query() -> str:
    bbox = f"{SOUTH},{WEST},{NORTH},{EAST}"
    return f"""[out:json][timeout:90];
(
  way["building"]({bbox});
  way["highway"]({bbox});
  way["place"="square"]({bbox});
  way["area:highway"="pedestrian"]({bbox});
  way["amenity"~"marketplace|fountain|parking"]({bbox});
  way["leisure"~"park|garden|playground|pitch"]({bbox});
  way["landuse"~"grass|forest|recreation_ground|park|meadow"]({bbox});
  way["natural"~"water|wood"]({bbox});
  node["natural"="tree"]({bbox});
);
out body geom;
"""

def counts(elements: list[dict]) -> dict[str, int]:
    result = {"buildings": 0, "roads": 0, "plazas": 0, "green_areas": 0, "water_areas": 0, "trees": 0}
    for element in elements:
        tags = element.get("tags", {})
        if element.get("type") == "node" and tags.get("natural") == "tree":
            result["trees"] += 1
        if element.get("type") != "way":
            continue
        if "building" in tags and tags.get("building") != "no":
            result["buildings"] += 1
        if "highway" in tags:
            result["roads"] += 1
        if tags.get("place") == "square" or tags.get("highway") == "pedestrian" or tags.get("area:highway") == "pedestrian":
            result["plazas"] += 1
        if tags.get("leisure") in {"park", "garden", "playground", "pitch"} or tags.get("landuse") in {"grass", "forest", "recreation_ground", "park", "meadow"} or tags.get("natural") == "wood":
            result["green_areas"] += 1
        if tags.get("natural") == "water":
            result["water_areas"] += 1
    return result

def fetch(output: Path) -> None:
    encoded = urllib.parse.urlencode({"data": make_query()}).encode("utf-8")
    errors = []
    for endpoint in ENDPOINTS:
        for attempt in range(3):
            request = urllib.request.Request(
                endpoint, data=encoded,
                headers={
                    "User-Agent": "GTA-Dushanbe-city-slice/1.0 (OpenStreetMap attribution: https://www.openstreetmap.org/copyright)",
                    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                    "Accept": "application/json",
                }, method="POST")
            try:
                with urllib.request.urlopen(request, timeout=120) as response:
                    payload = json.loads(response.read().decode("utf-8"))
                elements = payload.get("elements")
                if not isinstance(elements, list):
                    raise ValueError("Overpass returned JSON without an elements array")
                summary = counts(elements)
                if summary["buildings"] < 50 or summary["roads"] < 40:
                    raise ValueError(f"Extract seems incomplete: counts={summary}")
                payload["project_metadata"] = {
                    "project": "GTA-Dushanbe",
                    "source": "OpenStreetMap contributors",
                    "source_url": "https://www.openstreetmap.org/copyright",
                    "license": "Open Database License (ODbL) 1.0",
                    "attribution": "© OpenStreetMap contributors",
                    "query_bbox_south_west_north_east": [SOUTH, WEST, NORTH, EAST],
                    "local_coordinate_anchor_lat_lon": [ANCHOR_LAT, ANCHOR_LON],
                    "fetched_utc": datetime.now(timezone.utc).isoformat(),
                    "geometry_note": "Footprints and mapped roads/greens, not photogrammetry or facade scans.",
                    "feature_counts": summary,
                    "overpass_endpoint": endpoint,
                }
                output.parent.mkdir(parents=True, exist_ok=True)
                output.write_text(json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
                print("DUSHANBE_OSM_EXTRACT_OK")
                print(f"Saved: {output}")
                print(json.dumps(summary, ensure_ascii=False))
                return
            except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, ValueError, OSError) as exc:
                errors.append(f"{endpoint} attempt {attempt + 1}: {exc}")
                time.sleep(min(4 * (attempt + 1), 12))
    raise RuntimeError("All Overpass attempts failed:\n" + "\n".join(errors[-9:]))

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        fetch(args.output.resolve())
    except Exception as exc:
        print(f"DUSHANBE_OSM_EXTRACT_FAILED: {exc}", file=sys.stderr)
        raise

if __name__ == "__main__":
    main()
