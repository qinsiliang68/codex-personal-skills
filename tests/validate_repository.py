from __future__ import annotations

import hashlib
import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILLS_ROOT = ROOT / "skills"
EXPECTED_SKILLS = {
    "data-topic-plotting",
    "jgsjdq-migration-workflow",
    "parser-output-manual-annotation",
    "repo-development-protocol",
    "repo-file-management",
    "windows-powershell-efficiency",
}
EXPECTED_REPOSITORY = "qinsiliang68/codex-personal-skills"
BANNED_PATH_PARTS = {
    ".system",
    ".codex",
    "cache",
    "memories",
    "plugins",
    "sessions",
}
SECRET_PATTERNS = {
    "private_key": re.compile(
        r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----", re.IGNORECASE
    ),
    "github_token": re.compile(
        r"\b(?:gh[pousr]_[A-Za-z0-9_]{20,}|github_pat_[A-Za-z0-9_]{20,})\b"
    ),
    "common_live_secret": re.compile(
        r"\b(?:sk|rk|pk)_(?:live|test)_[A-Za-z0-9]{16,}\b", re.IGNORECASE
    ),
    "assigned_secret": re.compile(
        r"(?i)\b(?:api[_-]?key|access[_-]?token|secret|password)\s*[:=]\s*"
        r"['\"](?!example|placeholder|your-|your_)[^'\"]{8,}['\"]"
    ),
}
LOCAL_PROFILE_PATTERNS = (
    re.compile(r"(?i)C:\\Users\\[^\\\s`]+"),
    re.compile("/" + r"Users/[^/\s`]+"),
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def parse_frontmatter(path: Path) -> dict[str, str]:
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0] != "---":
        raise AssertionError(f"missing YAML frontmatter: {path}")
    try:
        end = lines.index("---", 1)
    except ValueError as exc:
        raise AssertionError(f"unterminated YAML frontmatter: {path}") from exc

    values: dict[str, str] = {}
    for line in lines[1:end]:
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        values[key.strip()] = value.strip()
    return values


class PublicSkillRepositoryTests(unittest.TestCase):
    def test_repository_contract_files_exist(self) -> None:
        for relative in (
            ".gitattributes",
            ".gitignore",
            "AGENTS.md",
            "CONTRIBUTING.md",
            "LICENSE",
            "README.md",
            "manifest.json",
        ):
            self.assertTrue((ROOT / relative).is_file(), relative)

    def test_expected_personal_skills_are_published(self) -> None:
        self.assertTrue(SKILLS_ROOT.is_dir())
        actual = {path.name for path in SKILLS_ROOT.iterdir() if path.is_dir()}
        self.assertEqual(EXPECTED_SKILLS, actual)

    def test_official_and_runtime_directories_are_absent(self) -> None:
        for path in ROOT.rglob("*"):
            relative_parts = set(path.relative_to(ROOT).parts)
            self.assertFalse(
                relative_parts & BANNED_PATH_PARTS,
                f"banned path component in {path.relative_to(ROOT)}",
            )
            self.assertFalse(path.is_symlink(), f"symlink is not publishable: {path}")

    def test_skill_frontmatter_identity(self) -> None:
        for skill_name in sorted(EXPECTED_SKILLS):
            skill_file = SKILLS_ROOT / skill_name / "SKILL.md"
            self.assertTrue(skill_file.is_file(), skill_file)
            metadata = parse_frontmatter(skill_file)
            self.assertEqual(skill_name, metadata.get("name"))
            self.assertTrue(metadata.get("description"), skill_name)

    def test_windows_powershell_skill_covers_transactional_receipts(self) -> None:
        skill_text = (
            SKILLS_ROOT / "windows-powershell-efficiency" / "SKILL.md"
        ).read_text(encoding="utf-8")
        recipes_text = (
            SKILLS_ROOT
            / "windows-powershell-efficiency"
            / "references"
            / "command-recipes.md"
        ).read_text(encoding="utf-8")
        combined = f"{skill_text}\n{recipes_text}"
        for required in (
            "OrderedDictionary",
            "Measure-Object -Property",
            "[pscustomobject]",
            "status = 'FAILED'",
            "['status'] = 'FAILED'",
            "['status'] = 'PASS'",
        ):
            self.assertIn(required, combined)

    def test_manifest_matches_every_published_skill_file(self) -> None:
        manifest_path = ROOT / "manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        self.assertEqual("1.0.0", manifest.get("schema_version"))
        self.assertEqual(EXPECTED_REPOSITORY, manifest.get("repository"))
        self.assertEqual("public", manifest.get("visibility"))

        entries = manifest.get("skills", [])
        self.assertEqual(EXPECTED_SKILLS, {entry["name"] for entry in entries})
        for entry in entries:
            skill_root = ROOT / entry["path"]
            actual_files = {
                path.relative_to(skill_root).as_posix(): path
                for path in skill_root.rglob("*")
                if path.is_file()
            }
            declared_files = {item["path"]: item for item in entry["files"]}
            self.assertEqual(set(actual_files), set(declared_files), entry["name"])
            for relative, path in actual_files.items():
                declared = declared_files[relative]
                self.assertEqual(path.stat().st_size, declared["bytes"], path)
                self.assertEqual(sha256(path), declared["sha256"], path)

    def test_public_text_has_no_profile_path_or_secret(self) -> None:
        for path in ROOT.rglob("*"):
            if not path.is_file() or ".git" in path.parts:
                continue
            if path.suffix.lower() not in {
                "",
                ".json",
                ".md",
                ".py",
                ".txt",
                ".yaml",
                ".yml",
            }:
                continue
            self.assertLessEqual(path.stat().st_size, 1_000_000, path)
            text = path.read_text(encoding="utf-8")
            for pattern in LOCAL_PROFILE_PATTERNS:
                self.assertIsNone(pattern.search(text), f"local profile path in {path}")
            for label, pattern in SECRET_PATTERNS.items():
                self.assertIsNone(pattern.search(text), f"{label} pattern in {path}")


if __name__ == "__main__":
    unittest.main()
