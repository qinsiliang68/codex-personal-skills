---
name: repo-development-protocol
description: Standard development protocol for repository changes. Use before and after any code, schema, pipeline, API, MCP, test, config, script, or documentation modification. Enforces DAA, TDD, small rollback-safe commits, documentation sync, and repo hygiene.
---

# Repo Development Protocol

Use this skill before any change to:

- source code
- tests
- schemas
- migrations
- pipeline stages
- API contracts
- MCP tools
- configs
- scripts
- documentation
- directory structure

The goal is to keep every change analyzed, tested, reversible, documented, and clean.

---

## 0. Scope Tier

Match the ceremony to the task risk.

Use **Tiny** mode for answer-only work, read-only review, spelling fixes, or a single low-risk documentation correction:

- collect only the directly relevant context
- use a one-line DAA summary instead of the full DAA block
- run a lightweight validation if files changed
- do not create commits unless explicitly asked

Use **Normal** mode for ordinary code, config, script, pipeline, test, or documentation changes:

- collect the relevant owner files, tests, and docs
- state the full DAA block before implementation
- prepare a verification path before editing
- update related docs when contracts or commands change

Use **High-risk** mode for schema, migration, stored data, parser/OCR pipeline, retrieval quality, API, MCP, destructive filesystem, dependency, or broad directory-structure changes:

- inspect root and nearest instructions before editing
- verify current behavior before changing it when practical
- add or update tests first unless impossible
- run the strongest local verification available
- keep generated artifacts in documented artifact locations
- stop and ask if data loss, contract breakage, or destructive commands are possible

Do not use the full protocol for a purely explanatory answer unless the user asks for implementation, review, verification, commit, or repository changes.

---

## 1. DAA: Do After Analysis

Do not edit files before enough context has been collected.

Before changing anything, first identify:

- what task is being solved
- which module owns this task
- which files define current behavior
- which tests or validation scripts cover it
- which schema, README, API, MCP, or pipeline contract may be affected
- whether the change may break stored data or existing behavior

Required context to read before modification:

- root `AGENTS.md` when present
- root `README.md` when the change may affect project commands, structure, setup, or contracts
- nearest relevant directory `README.md` when present
- relevant source files
- relevant tests
- relevant schema/API/MCP docs if contracts are affected

For Normal and High-risk tasks, before implementation output:

```text
Task:
Affected module:
Context read:
Context missing:
Assumptions:
Planned files:
Test/verification plan:
Docs impact:
Rollback unit:
```

For Tiny tasks, a short inline summary is enough:

```text
DAA: changing <file/area> because <reason>; verify with <check>.
```

If context is insufficient, inspect more files or ask before editing.

Do not guess project conventions when they can be read from the repository.

Before editing in a git repository, inspect the worktree state with `git status --short` or equivalent.

Do not revert, overwrite, format away, or delete changes made by the user or another tool. If a file already has unrelated edits, read it carefully and preserve those edits.

---

## 2. TDD / Verification First

For behavior changes, bug fixes, schema changes, parser changes, retrieval changes, API changes, MCP changes, or pipeline changes:

1. Define the expected behavior.
2. Add or update a test first when practical.
3. Confirm the test fails for the expected reason when practical.
4. Implement the minimal change.
5. Run the smallest relevant test or validation.
6. Refactor only after the test or verification is green.

If a test is not added before implementation, explicitly state why and name the replacement verification.

If a true failing test is not practical, create one clear verification path:

- smoke test
- schema validation
- golden file check
- CLI command
- API contract check
- MCP tool contract check
- retrieval regression case
- documented manual verification command

Never make a behavior change with no verification path.

For retrieval-related changes, verify relevant metrics or regression cases such as:

- Recall@K
- MRR
- no_match behavior
- wrong_domain behavior
- deprecated_return behavior
- authority ordering

For schema-related changes, verify:

- schema validation
- sample JSON fixtures
- migration behavior
- backward compatibility when required

---

## 3. Small Commit / Minimal Rollback Unit

Plan changes as small semantic units.

A good rollback unit should be easy to understand, test, and revert.

Good units:

- one schema model plus tests
- one parser bug fix plus regression test
- one input adapter plus smoke test
- one pipeline stage output plus report/checkpoint test
- one MCP tool plus contract test
- one docs update tied to one real contract change

Bad units:

- schema + retrieval + MCP + docs mixed together
- refactor plus behavior change without separation
- formatting mixed with logic changes
- unrelated README updates
- generated artifacts mixed with source changes

Do not run `git commit` unless explicitly allowed by the user or project rules.

Treat these user phrases as explicit commit authorization:

- `commit`
- `c+p`
- `commit push`
- any clear Chinese request meaning "commit", "submit", "commit and push", or "push after commit"

If the user only asks for code changes, tests, review, or explanation, do not commit.

Before committing, propose the commit split:

```text
Commit 1:
Commit 2:
Commit 3:
```

Preferred commit message style:

```text
feat(schema): add ArticleUnit model
test(retrieval): add no_match regression cases
fix(parser): preserve article boundary after page break
docs(pipeline): update parser README
```

---

## 4. Documentation Sync

Documentation is part of the change.

After every modification, decide whether documentation must be updated.

Update docs when any of these change:

- directory responsibility
- public module contract
- input/output format
- schema field
- API endpoint
- MCP tool signature
- pipeline stage behavior
- command-line usage
- generated artifacts
- config meaning
- dependency relationship
- migration behavior
- quality gate rule
- test command

Usually update one or more of:

- nearest directory `README.md`
- root `README.md`
- `docs/PROJECT_MAP.md`
- schema docs
- API docs
- MCP docs
- `CHANGELOG.md`
- `docs/ADR/*.md` for important architecture decisions

Do not create a new docs path just because it is listed above. Create new documentation files only when the repository already uses that location, the user requests it, or the task creates a durable contract that needs a clear home.

Do not update docs for trivial internal edits that do not affect behavior, contracts, commands, or structure.

At the end of the task, report:

```text
Docs updated:
Docs not updated because:
```

---

## 5. Repo Hygiene / No Garbage Changes

Do not pollute the repository.

Do not create random files, random scripts, random abstractions, random documents, or random generated outputs.

Before creating any new file, directory, dependency, abstraction, script, or document, confirm that it has:

- a clear purpose
- a clear owner module
- a stable location
- a long-term maintenance reason
- a reference from code, tests, docs, or commands
- a cleanup or lifecycle rule if it is temporary or generated

Avoid:

- random files in the repository root
- one-off debug scripts
- temporary `.json`, `.md`, `.txt`, `.py`, `.tmp`, `.bak`, `.old` files committed as source
- generated artifacts mixed with source code
- logs, caches, indexes, reports, or run outputs placed in source directories
- broad refactors unrelated to the task
- new dependencies without strong justification
- new abstractions for only one current use case
- README noise that does not describe real contracts, commands, structure, or behavior
- duplicate helper functions when an existing utility should be reused
- changing formatting across unrelated files

Temporary files must go to an ignored temp/artifact location.

Generated files must go under the agreed artifact/output directory and must not be treated as source unless explicitly required.

Use repository-declared artifact directories exactly. If the repository defines locations such as `test/`, `log/`, `review_artifacts/`, `outputs/`, `tmp/`, or a recycle/archive directory, follow those conventions instead of inventing new root folders.

For the law-database-retrieval parser pipeline, keep the current convention unless the user changes it:

- test or reproducibility samples under `test/`
- runtime logs under `log/`
- pending inputs and curated parser artifacts under `review_artifacts/`
- discarded files under the agreed recycle/archive directory
- source corpus files under their documented corpus directory

A new file is allowed only if this check can be answered clearly:

```text
Why does this file exist?
Who imports or uses it?
Where is it documented?
How is it tested or verified?
Should it be committed, ignored, or deleted after use?
```

If the answer is unclear, do not create the file.

Small commits do not mean many small garbage files.
Small commits mean clean, reversible, meaningful change units.

---

## Required Final Report

End every development task with:

```text
Changed files:
Tests/verification:
Docs updated:
Suggested commit split:
Risks / remaining work:
```

---

## Stop Conditions

Stop before editing if:

- task scope is ambiguous
- required context cannot be found
- tests or verification path are unclear
- schema compatibility is unclear
- stored data may break
- API or MCP contract may change unexpectedly
- destructive commands are required
- generated/source data may be deleted
- the change would require random files or unclear repo pollution
