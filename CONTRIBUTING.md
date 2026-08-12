# Contributing

## Add a skill

1. Choose a stable lowercase kebab-case name.
2. Create `skills/<skill-name>/SKILL.md` with YAML frontmatter containing the same `name` and a precise `description`.
3. Keep every file required by the Skill under its own directory.
4. Use portable environment variables such as `%USERPROFILE%` instead of publishing a personal user directory.
5. Do not copy Codex `.system` skills or plugin-distributed skills into this repository.
6. Do not include source datasets, private handoffs, credentials, caches, memory, sessions, logs, generated reports, or unrelated repository files.
7. Update the manifest and run all repository checks.

## Update a skill

Treat the live behavior contract and the public copy as distinct assets. Review the diff rather than recursively overwriting a skill directory. Preserve intentional public-path substitutions and document material behavior changes in the commit message.

## Validation

```powershell
uv run python scripts/build_manifest.py
uv run python -m unittest tests.validate_repository -v
uv run python scripts/build_manifest.py --check
git diff --check
```

`manifest.json` is generated. Do not hand-edit its hashes or byte counts.

## Public review checklist

- The change contains only intended personal Skill files.
- Frontmatter identity matches the directory.
- All referenced local resources are either included or clearly documented as external prerequisites.
- No private absolute user path, email address, credential, access token, or private key is present.
- No official/system/plugin Skill is copied or represented as personal work.
- Tests and manifest checks pass from a clean checkout.
