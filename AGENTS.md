# Repository Instructions

## Purpose

This repository publishes personal Codex skills only. Do not add OpenAI/Codex system skills, plugin-provided skills, caches, memory, sessions, logs, credentials, or private user data.

## Required layout

- Put each skill at `skills/<skill-name>/`.
- Require `skills/<skill-name>/SKILL.md`.
- Require the frontmatter `name` to equal the directory name.
- Keep referenced scripts, templates, examples, and agent metadata inside that skill directory.
- Do not add symlinks or files that depend on untracked local content.

## Change workflow

1. Analyze the requested change and inspect the current skill and tests.
2. Add or update a failing check before behavior changes where practical.
3. Make the smallest coherent edit.
4. Review the public diff for private paths, secrets, internal evidence, and accidental official/plugin content.
5. Run:

   ```powershell
   uv run python scripts/build_manifest.py
   uv run python -m unittest tests.validate_repository -v
   uv run python scripts/build_manifest.py --check
   git diff --check
   ```

6. Commit one rollback-safe semantic unit at a time.

## Publication boundary

Only this repository may be mutated when maintaining this catalog unless the user explicitly expands scope. Do not change the visibility, branches, settings, or contents of any other repository.
