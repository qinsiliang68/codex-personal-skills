from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILLS_ROOT = ROOT / "skills"
MANIFEST_PATH = ROOT / "manifest.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def parse_frontmatter(path: Path) -> dict[str, str]:
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0] != "---":
        raise ValueError(f"missing YAML frontmatter: {path}")
    try:
        end = lines.index("---", 1)
    except ValueError as exc:
        raise ValueError(f"unterminated YAML frontmatter: {path}") from exc

    values: dict[str, str] = {}
    for line in lines[1:end]:
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        values[key.strip()] = value.strip()
    return values


def build_manifest() -> dict[str, object]:
    skills: list[dict[str, object]] = []
    for skill_root in sorted(path for path in SKILLS_ROOT.iterdir() if path.is_dir()):
        skill_file = skill_root / "SKILL.md"
        if not skill_file.is_file():
            raise ValueError(f"missing SKILL.md: {skill_root}")
        metadata = parse_frontmatter(skill_file)
        if metadata.get("name") != skill_root.name:
            raise ValueError(
                f"frontmatter name mismatch: {skill_root.name} != {metadata.get('name')}"
            )

        files = []
        for path in sorted(item for item in skill_root.rglob("*") if item.is_file()):
            files.append(
                {
                    "path": path.relative_to(skill_root).as_posix(),
                    "bytes": path.stat().st_size,
                    "sha256": sha256(path),
                }
            )
        skills.append(
            {
                "name": skill_root.name,
                "path": skill_root.relative_to(ROOT).as_posix(),
                "description": metadata["description"],
                "files": files,
            }
        )

    return {
        "schema_version": "1.0.0",
        "repository": "qinsiliang68/codex-personal-skills",
        "visibility": "public",
        "scope": "personal_codex_skills_only",
        "exclusions": [
            "Codex system skills",
            "plugin-provided skills",
            "runtime and plugin caches",
            "memory and sessions",
            "credentials and private user data",
        ],
        "skills": skills,
    }


def serialized_manifest() -> str:
    return json.dumps(build_manifest(), ensure_ascii=False, indent=2) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Build or verify the skill manifest.")
    parser.add_argument(
        "--check",
        action="store_true",
        help="fail if manifest.json does not match the current skill files",
    )
    args = parser.parse_args()
    expected = serialized_manifest()

    if args.check:
        if not MANIFEST_PATH.is_file():
            print("manifest.json is missing", file=sys.stderr)
            return 1
        actual = MANIFEST_PATH.read_text(encoding="utf-8")
        if actual != expected:
            print("manifest.json is stale; run scripts/build_manifest.py", file=sys.stderr)
            return 1
        print("manifest.json is current")
        return 0

    MANIFEST_PATH.write_text(expected, encoding="utf-8", newline="\n")
    print(f"wrote {MANIFEST_PATH} with {len(build_manifest()['skills'])} skills")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
