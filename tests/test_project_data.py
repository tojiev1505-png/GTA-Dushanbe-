"""Unit tests for the sample map data and validator."""
from __future__ import annotations
import json
import sys
import unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from validate_project import ValidationError, validate_block, validate_repository  # noqa: E402

class ProjectDataTests(unittest.TestCase):
    """Four deterministic tests requiring no game installation."""
    @classmethod
    def setUpClass(cls) -> None:
        cls.sample_path = ROOT / "map-data" / "blocks" / "center_prototype.json"
        cls.sample = json.loads(cls.sample_path.read_text(encoding="utf-8"))
    def test_repository_block_data_validates(self) -> None:
        paths = validate_repository()
        self.assertIn(self.sample_path, paths)
    def test_sample_has_unique_feature_ids(self) -> None:
        ids = [item["id"] for group in ("roads", "building_footprints") for item in self.sample[group]]
        self.assertEqual(len(ids), len(set(ids)))
    def test_out_of_bounds_road_point_is_rejected(self) -> None:
        data = json.loads(json.dumps(self.sample))
        data["roads"][0]["centerline"][0] = [-1.0, 90.0]
        with self.assertRaisesRegex(ValidationError, "outside bounds"):
            validate_block(data, "test block")
    def test_zero_area_building_polygon_is_rejected(self) -> None:
        data = json.loads(json.dumps(self.sample))
        data["building_footprints"][0]["polygon"] = [[10, 10], [20, 20], [30, 30]]
        with self.assertRaisesRegex(ValidationError, "area must be non-zero"):
            validate_block(data, "test block")

if __name__ == "__main__":
    unittest.main()
