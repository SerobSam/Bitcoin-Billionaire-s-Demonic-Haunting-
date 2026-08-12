import copy
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "tools" / "validate_gameplay_data.py"
CLASSES = ROOT / "assets" / "gameplay" / "classes.json"
LOOT = ROOT / "assets" / "gameplay" / "loot_tiers.json"


def test_gameplay_data_passes_validator():
    result = subprocess.run([sys.executable, str(VALIDATOR)], capture_output=True, text=True, check=False)
    assert result.returncode == 0, result.stderr
    assert "validated 24 skills" in result.stdout


def test_classes_define_expected_counts():
    data = json.loads(CLASSES.read_text())
    assert len(data["classes"]) == 4
    assert all(len(cls["skills"]) == 6 for cls in data["classes"])
    assert all(len(cls["passives"]) == 12 for cls in data["classes"])


def test_loot_tiers_are_ordered_by_rarity_weight():
    data = json.loads(LOOT.read_text())
    weights = [tier["drop_weight"] for tier in data["tiers"]]
    assert weights == sorted(weights, reverse=True)


def test_skill_ids_are_unique():
    data = json.loads(CLASSES.read_text())
    skill_ids = [skill["id"] for cls in data["classes"] for skill in cls["skills"]]
    assert len(skill_ids) == len(set(skill_ids))
    assert copy.copy(skill_ids) == skill_ids
