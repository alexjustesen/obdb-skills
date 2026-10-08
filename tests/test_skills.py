import json
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "skills"
FIXTURES = ROOT / "tests" / "fixtures"


def run_json(script, *args):
    completed = subprocess.run(
        [sys.executable, str(script), *map(str, args), "--format", "json"]
        if script.name == "audit_dataset.py"
        else [sys.executable, str(script), *map(str, args)],
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(completed.stdout)


class SkillMetadataTests(unittest.TestCase):
    def test_skill_frontmatter_and_directory_names(self):
        skill_files = sorted(SKILLS.glob("*/SKILL.md"))
        self.assertEqual(5, len(skill_files))
        for path in skill_files:
            content = path.read_text(encoding="utf-8")
            match = re.match(r"---\n(.*?)\n---\n", content, re.DOTALL)
            self.assertIsNotNone(match, path)
            name = re.search(r"^name:\s*(.+)$", match.group(1), re.MULTILINE)
            description = re.search(r"^description:\s*(.+)$", match.group(1), re.MULTILINE)
            self.assertEqual(path.parent.name, name.group(1).strip())
            self.assertTrue(description.group(1).strip())

    def test_every_skill_contains_npm_safety_rule(self):
        for path in sorted(SKILLS.glob("*/SKILL.md")):
            content = path.read_text(encoding="utf-8").casefold()
            self.assertIn("npm", content, path)
            self.assertRegex(content, r"never run|do not run")

    def test_contributor_never_generates_ids_for_additions(self):
        content = (SKILLS / "openbrewerydb-contributor" / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("## New breweries never get an ID", content)
        for term in ("uuidgen", "uuid4", "randomUUID", "generate:ids", "placeholder", "`+,`"):
            self.assertIn(term, content)

    def test_pull_request_skill_defines_title_and_per_record_body(self):
        skill = SKILLS / "openbrewerydb-pull-request"
        content = (skill / "SKILL.md").read_text(encoding="utf-8")
        template = (skill / "references" / "pr-body-template.md").read_text(encoding="utf-8")
        self.assertIn("`data: <short description>`", content)
        self.assertIn("--repo openbrewerydb/openbrewerydb", content)
        self.assertIn("--base master", content)
        for heading in ("## Summary", "## Changes", "### Add:", "### Update:", "### Delete:", "## Reviewer notes"):
            self.assertIn(heading, template)
        self.assertIn("| Field | Old value | New value |", template)
        self.assertIn("join our Discord: https://discord.gg/3G3syaD", template)
        for title in re.findall(r"^- `(data: [^`]+)`$", content, re.MULTILINE):
            self.assertLess(len(title), 72, title)

    def test_analysis_skills_are_read_only_and_issue_ready(self):
        for name in (
            "openbrewerydb-data-quality-auditor",
            "openbrewerydb-brewery-discovery",
            "openbrewerydb-entity-linker",
        ):
            content = (SKILLS / name / "SKILL.md").read_text(encoding="utf-8").casefold()
            self.assertIn("read-only", content)
            self.assertIn("issue-ready", content)
            self.assertNotIn("gh issue create", content)

    def test_referenced_skill_resources_exist(self):
        for path in sorted(SKILLS.glob("*/SKILL.md")):
            content = path.read_text(encoding="utf-8")
            resources = re.findall(r"(?:references|scripts)/[a-zA-Z0-9_./-]+\.(?:md|py)", content)
            for resource in resources:
                self.assertTrue((path.parent / resource).is_file(), f"{path}: {resource}")


class HelperTests(unittest.TestCase):
    def test_auditor_reports_deterministic_fixture_defects(self):
        script = SKILLS / "openbrewerydb-data-quality-auditor" / "scripts" / "audit_dataset.py"
        report = run_json(script, FIXTURES / "dataset")
        checks = {finding["check"] for finding in report["findings"]}
        self.assertIn("duplicate_id", checks)
        self.assertIn("duplicate_identity", checks)
        self.assertIn("blank_id", checks)
        self.assertIn("invalid_brewery_type", checks)
        self.assertIn("coordinate_pair_missing", checks)
        self.assertIn("coordinate_possible_swap", checks)
        self.assertIn("invalid_id", checks)
        self.assertIn("invalid_website_url", checks)
        self.assertIn("missing_required_value", checks)
        self.assertEqual("src/config.ts", report["brewery_types_source"])
        self.assertEqual(9, report["source_row_count"])

    def test_auditor_discloses_brewery_type_fallback(self):
        script = SKILLS / "openbrewerydb-data-quality-auditor" / "scripts" / "audit_dataset.py"
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            shutil.copytree(FIXTURES / "dataset" / "data", root / "data")
            report = run_json(script, root)
        fallback = [
            finding for finding in report["findings"]
            if finding["check"] == "brewery_type_source_unavailable"
        ]
        self.assertEqual(1, len(fallback))
        self.assertEqual("fallback snapshot", report["brewery_types_source"])

    def test_discovery_matches_and_limits_reverse_scope(self):
        script = SKILLS / "openbrewerydb-brewery-discovery" / "scripts" / "compare_inventory.py"
        report = run_json(script, FIXTURES / "inventory.csv", FIXTURES / "dataset")
        candidates = {
            item["external"]["record"]["name"]: item for item in report["external_candidates"]
        }
        self.assertEqual("likely_match", candidates["Alpha Brewing"]["classification"])
        self.assertEqual("unmatched_external", candidates["New Brewing"]["classification"])
        reverse_names = {
            item["record"]["name"] for item in report["reverse_unmatched_dataset_records"]
        }
        self.assertNotIn("Outside Brewing", reverse_names)
        self.assertIn("Beta Brewing", reverse_names)
        sibling = [
            item for item in report["reverse_unmatched_dataset_records"]
            if item["record"]["id"] in {"id-5", "id-6"}
        ]
        self.assertEqual(2, len(sibling))
        matched_id = candidates["Alpha Brewing"]["matches"][0]["dataset"]["record"]["id"]
        self.assertEqual("id-1", matched_id)

    def test_discovery_auto_scope_uses_single_city(self):
        script = SKILLS / "openbrewerydb-brewery-discovery" / "scripts" / "compare_inventory.py"
        report = run_json(script, FIXTURES / "inventory_city.csv", FIXTURES / "dataset")
        reverse_names = {
            item["record"]["name"] for item in report["reverse_unmatched_dataset_records"]
        }
        self.assertNotIn("Beta Brewing", reverse_names)
        self.assertNotIn("Outside Brewing", reverse_names)

    def test_discovery_rejects_empty_and_malformed_inventories(self):
        script = SKILLS / "openbrewerydb-brewery-discovery" / "scripts" / "compare_inventory.py"
        for fixture, message in (
            ("inventory_empty.csv", "has no brewery records"),
            ("inventory_malformed.csv", "more values than the header"),
        ):
            completed = subprocess.run(
                [sys.executable, str(script), str(FIXTURES / fixture), str(FIXTURES / "dataset")],
                capture_output=True,
                text=True,
            )
            self.assertEqual(2, completed.returncode)
            self.assertIn(message, completed.stderr)
            self.assertNotIn("Traceback", completed.stderr)

    def test_discovery_does_not_suppress_sparse_siblings(self):
        script = SKILLS / "openbrewerydb-brewery-discovery" / "scripts" / "compare_inventory.py"
        report = run_json(script, FIXTURES / "inventory_sparse.csv", FIXTURES / "dataset")
        reverse_ids = {
            item["record"]["id"] for item in report["reverse_unmatched_dataset_records"]
        }
        self.assertTrue({"id-7", "id-8"}.issubset(reverse_ids))


if __name__ == "__main__":
    unittest.main()
