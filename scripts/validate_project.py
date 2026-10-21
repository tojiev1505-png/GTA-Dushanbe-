#!/usr/bin/env python3
"""Validate Dushanbe-GTA planning data using only the Python standard library."""
from __future__ import annotations
import json
import math
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
BLOCKS_DIR = ROOT / "map-data" / "blocks"
REQUIRED_TOP_LEVEL = {
    "schema_version", "project", "block_id", "name", "status",
    "coordinate_system", "source_notes", "bounds", "roads", "building_footprints",
}

class ValidationError(ValueError):
    """Raised when project data does not satisfy the expected schema."""

def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ValidationError(message)

def _is_finite_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)

def _point(value: Any, where: str) -> tuple[float, float]:
    _require(isinstance(value, list) and len(value) == 2, f"{where}: expected [x, y]")
    _require(all(_is_finite_number(item) for item in value), f"{where}: coordinates must be finite numbers")
    return float(value[0]), float(value[1])

def validate_block(data: Any, source: str = "block data") -> None:
    """Validate one block document. Raises ValidationError with a useful message."""
    _require(isinstance(data, dict), f"{source}: top level must be an object")
    missing = REQUIRED_TOP_LEVEL - set(data)
    _require(not missing, f"{source}: missing required keys: {', '.join(sorted(missing))}")
    _require(data["schema_version"] == 1, f"{source}: schema_version must be 1")
    for key in ("project", "block_id", "name"):
        _require(isinstance(data[key], str) and data[key].strip(), f"{source}: {key} must be a non-empty string")
    _require(data["status"] in {"illustrative", "draft", "reviewed"}, f"{source}: unsupported status")
    coordinate_system = data["coordinate_system"]
    _require(isinstance(coordinate_system, dict), f"{source}: coordinate_system must be an object")
    _require(coordinate_system.get("type") == "local_cartesian", f"{source}: coordinate type must be local_cartesian")
    _require(coordinate_system.get("unit") == "metre", f"{source}: coordinate unit must be metre")
    _require(isinstance(coordinate_system.get("origin_note"), str) and coordinate_system["origin_note"].strip(),
             f"{source}: origin_note must explain the coordinate origin")
    _require(isinstance(data["source_notes"], list) and data["source_notes"], f"{source}: source_notes must be a non-empty list")
    _require(all(isinstance(note, str) and note.strip() for note in data["source_notes"]),
             f"{source}: every source note must be a non-empty string")
    bounds = data["bounds"]
    _require(isinstance(bounds, dict), f"{source}: bounds must be an object")
    bound_names = ("min_x", "min_y", "max_x", "max_y")
    _require(all(_is_finite_number(bounds.get(key)) for key in bound_names), f"{source}: bounds must be finite numbers")
    _require(bounds["min_x"] < bounds["max_x"] and bounds["min_y"] < bounds["max_y"],
             f"{source}: bounds must have positive width and height")
    def within_bounds(point: tuple[float, float], where: str) -> None:
        x, y = point
        _require(bounds["min_x"] <= x <= bounds["max_x"] and bounds["min_y"] <= y <= bounds["max_y"],
                 f"{where}: point {point} falls outside bounds")
    roads = data["roads"]
    _require(isinstance(roads, list), f"{source}: roads must be a list")
    seen_ids: set[str] = set()
    for index, road in enumerate(roads):
        where = f"{source}: roads[{index}]"
        _require(isinstance(road, dict), f"{where}: expected object")
        road_id = road.get("id")
        _require(isinstance(road_id, str) and road_id.strip(), f"{where}: id must be a non-empty string")
        _require(road_id not in seen_ids, f"{where}: duplicate id {road_id!r}")
        seen_ids.add(road_id)
        _require(isinstance(road.get("name"), str) and road["name"].strip(), f"{where}: name must be a non-empty string")
        _require(_is_finite_number(road.get("width_m")) and road["width_m"] > 0,
                 f"{where}: width_m must be a positive finite number")
        centerline = road.get("centerline")
        _require(isinstance(centerline, list) and len(centerline) >= 2, f"{where}: centerline needs at least two points")
        for n, value in enumerate(centerline):
            within_bounds(_point(value, f"{where}: centerline[{n}]"), where)
    footprints = data["building_footprints"]
    _require(isinstance(footprints, list), f"{source}: building_footprints must be a list")
    for index, building in enumerate(footprints):
        where = f"{source}: building_footprints[{index}]"
        _require(isinstance(building, dict), f"{where}: expected object")
        building_id = building.get("id")
        _require(isinstance(building_id, str) and building_id.strip(), f"{where}: id must be a non-empty string")
        _require(building_id not in seen_ids, f"{where}: duplicate id {building_id!r}")
        seen_ids.add(building_id)
        _require(isinstance(building.get("name"), str) and building["name"].strip(), f"{where}: name must be a non-empty string")
        _require(_is_finite_number(building.get("height_m")) and building["height_m"] > 0,
                 f"{where}: height_m must be a positive finite number")
        _require(isinstance(building.get("purpose"), str) and building["purpose"].strip(),
                 f"{where}: purpose must be a non-empty string")
        polygon = building.get("polygon")
        _require(isinstance(polygon, list) and len(polygon) >= 3, f"{where}: polygon needs at least three points")
        points = [_point(value, f"{where}: polygon[{n}]") for n, value in enumerate(polygon)]
        for point in points:
            within_bounds(point, where)
        area_twice = sum(points[i][0] * points[(i + 1) % len(points)][1]
                         - points[(i + 1) % len(points)][0] * points[i][1]
                         for i in range(len(points)))
        _require(abs(area_twice) > 0, f"{where}: polygon area must be non-zero")

def validate_repository() -> list[Path]:
    """Validate every block JSON document and return the validated paths."""
    _require(BLOCKS_DIR.is_dir(), f"missing block-data directory: {BLOCKS_DIR.relative_to(ROOT)}")
    files = sorted(BLOCKS_DIR.glob("*.json"))
    _require(bool(files), "no block JSON files found in map-data/blocks")
    for path in files:
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise ValidationError(f"{path.relative_to(ROOT)}: cannot read valid UTF-8 JSON: {exc}") from exc
        validate_block(data, str(path.relative_to(ROOT)))
    return files

def main() -> int:
    try:
        paths = validate_repository()
    except ValidationError as exc:
        print(f"VALIDATION FAILED: {exc}", file=sys.stderr)
        return 1
    for path in paths:
        print(f"VALID: {path.relative_to(ROOT)}")
    print(f"Validated {len(paths)} block data file(s).")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
