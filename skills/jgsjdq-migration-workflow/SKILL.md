---
name: jgsjdq-migration-workflow
description: Code migration workflow for rebuilding old C:\GitHub\jgsjdq projects inside C:\GitHub\new-jgsjdq with strict JSON contracts, calculation/display consistency, DOCX rendering audits, project-management discipline, and AIOps-style quality gates. Use when the user asks how to write new-jgsjdq from old jgsjdq, mentions 施工流程 as coding workflow, A03/A15 calculation-book migration, JSON强形式, display-layer vs calculation-layer consistency, formula/table/Book IR contracts, renderer checks, or AIOps checks for calculation-book pipelines.
---

# JGSJDQ Migration Workflow

Use this skill when rebuilding an old `jgsjdq` project as a strict `new-jgsjdq` project. The goal is not to port scripts mechanically; the goal is to extract engineering truth into typed calculation code, strong JSON artifacts, auditable display data, and a renderer that cannot silently drift from the calculation layer.

## Core Rule

Old `C:\GitHub\jgsjdq` is read-only reference. New work belongs in `C:\GitHub\new-jgsjdq`.

Do not start by inventing a new layout or demo. Start from the old project implementation and output shape, then rebuild it as:

calculation atoms -> formula/table atoms -> Book IR JSON -> checks JSON -> DOCX renderer -> render audit -> visual QA.

For portal-frame work, treat old `src/algorithm/a03_portal_frame_seismic` and `inputs/a03_portal_frame_seismic` as the current source of truth unless the user explicitly says otherwise. Historical `a10` labels are stale for the current portal-frame line. The new repo project code should remain `a03`, not a generic or lightweight demo code.

Use A15 only as the current backend-loop template and lesson set. Do not confuse A15 lightweight output with the full A03 target.

## Standalone Project Rule

New A03 must be independently runnable inside `new-jgsjdq`.

Forbidden runtime dependencies:

- importing old `C:\GitHub\jgsjdq` modules.
- calling old A03 scripts through subprocess, shell, environment variables, path injection, or copied launchers.
- reading old `jgsjdq` source/output files during normal calculation, rendering, or tests.
- delegating calculation, formula generation, table generation, Book IR assembly, or DOCX rendering to another project such as A15, A02, A10, or any legacy template module.

Allowed reference use:

- inspect old `jgsjdq` code, inputs, outputs, and documents during migration analysis.
- translate the old algorithm into new A03-owned Python modules.
- extract truly reusable utilities into neutral shared modules under `src/new_jgsjdq/`, not under another project package.

The final new A03 pipeline must run from new A03 inputs, new A03 config, new A03 calculation modules, shared neutral framework code, and the Open XML SDK renderer. It must still work if old `C:\GitHub\jgsjdq` is absent.

## Office SDK Fidelity Rule

Build the renderer as an Office/Open XML SDK system with the highest practical Word-native fidelity. The target is not "DOCX-like output"; the target is controllable Word document structure.

Use SDK-native constructs for:

- `styles.xml` paragraph/table/run styles.
- `w:pPr`, `w:rPr`, spacing, indentation, outline levels, borders, shading, and section properties.
- OMML equations, not raw LaTeX strings.
- fixed table geometry with `tblGrid`, `tcW`, repeated headers, row controls, cell margins, and semantic cell styles.
- page setup, margins, headers/footers, fields, captions, cross references, and numbering when the project contract explicitly requires them.

Do not use ad hoc XML string injection when the SDK can express the structure. If raw XML is unavoidable, isolate it, validate it, and add a contract test around the exact part.

High-fidelity control means package-level verification: inspect `word/document.xml`, `word/styles.xml`, numbering/section/header/footer parts when present, then run `OpenXmlValidator`, PDF conversion, PNG rendering, and visual review.

## Algorithm-SDK Compatibility Rule

The calculation layer must emit SDK-compatible document data. Do not calculate first and then rely on the renderer to rescue incompatible display fragments.

Require algorithm outputs to be render-ready:

- formula atoms must have an AST that maps cleanly to OMML.
- table atoms must provide plain cell text, formula references, roles, units, and fixed geometry hints that can become Word tables.
- paragraph atoms must provide semantic role, depth role, and style intent instead of raw prose blobs.
- units and conversions must be represented as data, not embedded as ad hoc display hacks.
- long equations must be split or structured by the formula atom when Word-native rendering needs that structure.

If a value, equation, table, or paragraph cannot be rendered faithfully by the SDK, fix the calculation/formula/table/Book IR contract first. Do not patch fidelity by screenshotting text, inserting Markdown, or hiding meaning inside renderer-only string manipulation.

## Bootstrap Reading Order

When entering `C:\GitHub\new-jgsjdq` for this workflow, read the local context before coding:

- `README.md`
- project `docx_layout.json`
- project `book.py` and task/input model files
- `src/new_jgsjdq/formula/trace.py`
- `src/new_jgsjdq/ir/book.py`
- `dotnet-renderer/Program.cs`
- relevant tests, especially formula/table/renderer contract tests

If a handoff file such as `%USERPROFILE%\Desktop\1111.txt` is provided, read it first because it may contain the latest acceptance rules and local tool paths.

## Project Management Discipline

Use general project-management practices to keep migrations controlled instead of sprawling:

- maintain an explicit task plan for nontrivial migrations and update it as phases change.
- split work into phases: discovery, contract/tests, calculation atoms, formula/table atoms, Book IR, renderer/layout, AIOps gates, visual QA, docs.
- give each phase entry criteria, exit criteria, touched files, verification command, and rollback unit.
- keep WIP narrow: finish one chapter, subsystem, or contract slice before opening many parallel edits.
- maintain a risk list for old-code ambiguity, SDK fidelity, formula rendering, table pagination, standalone dependency leaks, fallback/defaults, and visual QA.
- define "done" before coding each slice: source paths inspected, tests added, artifact produced, audit clean, render checked, and user-facing gap reported.
- use small rollback-safe commits only when the user asks to commit; otherwise keep the same split ready for later.

Do not let project management become paperwork. Use it to protect scope, sequencing, risk, and acceptance evidence.

## Workflow

1. Identify the old project.
   - Map the old module path, project code, input files, sample outputs, and calculation-book chapters.
   - Preserve original project numbering such as `a03`; do not rename it to a generic demo code.
   - For A03, start from the full old portal-frame calculation-book behavior, not the lightweight A15 experiment.
   - Check whether the active case is no-crane; if so, keep `crane.enabled=false` and do not invent crane beam, bracket, wheel-load, or crane-height parameters.
   - Treat old paths as analysis inputs only. Do not design the new project around runtime calls back into the old repo.

2. Read the old behavior before coding.
   - Inspect old algorithm scripts, parameters, formulas, tables, generated document structure, and known output examples.
   - Record what is engineering calculation, what is display prose, what is document layout, and what is legacy glue.
   - Inspect old generated DOCX/Markdown when available; layout and formula failures often appear only in the final XML/rendered document.

3. Define the new contracts first.
   - Add or update registry metadata.
   - Define parameter schema and default sample input.
   - Define JSON artifact contracts for `book_ir.json`, `formula_checks.json`, `table_checks.json`, layout/depth checks, renderer audit, and pipeline events.
   - Use JSON as the durable boundary between calculation, display, renderer, and AIOps checks.
   - Keep generated artifacts under `outputs/<project>/`; do not commit outputs, caches, `bin/obj`, `__pycache__`, or `.venv`.
   - Add a standalone contract test for migrated full projects: the new project must not import old `jgsjdq` modules or execute old project scripts.
   - Record the current slice's definition of done before implementation.

4. Build calculation atoms.
   - Python owns all engineering values, units, substitutions, limits, and conclusions.
   - Do not let C#, DOCX, or frontend code calculate engineering values.
   - Name unit conversions and intermediate variables; avoid hidden `/1000` or display-only scale hacks.
   - Missing required project data must raise a clear error. Do not add `.get(key, fallback)`, silent defaults, broad `try/except`, or graceful fallback branches for required engineering facts.
   - Derived values are allowed only when the derivation is explicit, traceable, and recorded as calculation data. Derivation is not the same as guessing a fallback.

5. Build formula and table atoms from the same source as calculation.
   - Each formula atom should carry symbolic/plain text, substituted text, result, unit, limit, conclusion, and trace/check record.
   - Each table atom should carry source values, roles, units, formulas, and checkable cell text.
   - Do not create display strings that can disagree with computed values.
   - Unit conversions must be named expression-tree nodes such as `unit_convert` or an explicit unit rule. Do not hand-write anonymous `/1000` scaling in display text.
   - Display math blocks should contain math only. Put explanatory Chinese text, notes, and per-meter explanations outside formula blocks.
   - Avoid hand-made multi-line LaTeX helpers such as `aligned`/`gathered` when they cause Word render failures. Prefer renderer-owned wrapping or deliberately split same-denominator expressions into smaller valid math blocks.
   - Table cells must use plain text for math-like labels and units. Do not put `$...$` or raw LaTeX in table cells.

6. Build Book IR as structured document data.
   - Use explicit chapter/section/depth roles, formula groups, table captions, result blocks, and conclusion blocks.
   - Heading numbers may be generated by Python text, but heading level and outline role must be explicit data.
   - Avoid a flat demo block list when migrating a full old project; preserve the old calculation-book structure.
   - Every free-text paragraph must have a semantic paragraph role before it reaches the renderer. Do not pass naked f-string prose as anonymous body text.
   - Every paragraph role must be declared in layout JSON and rendered as an SDK Word paragraph style through `w:pStyle`.
   - Do not expose internal template names such as template A/B/C in user-facing filenames, GUI/API text, terminal summaries, or delivery wording. Public artifacts should look like calculation books, not internal template variants.

7. Render through Open XML SDK.
   - The renderer consumes JSON artifacts and layout config only.
   - It maps declared roles to Word styles, OMML equations, table geometry, outline levels, and page setup.
   - It must not infer style from visible text and must not rewrite formula meaning.
   - Final Word output must use Open XML SDK. Do not use Pandoc or Markdown-to-DOCX as the final delivery route.
   - Layout control must live inside Word-native parts and properties; do not solve Word layout by pre-baking spaces, fake bullets, image screenshots of text, or Markdown tricks.
   - Use a formal black/gray calculation-book visual system unless the user explicitly asks otherwise. Do not reintroduce blue headings, green OK, red NG, or demo palettes.
   - Do not emit `w:keepNext` or `w:keepLines` by default; they can show as black nonprinting markers in Word/WPS. Only emit flow controls when layout JSON explicitly enables them.

8. Run AIOps-style acceptance.
   - Treat every accepted run as replayable: inputs, config, code version, artifacts, checks, renderer audit, and visual outputs must be traceable.
   - Fail or flag by stage: parameter normalization, calculation, formula generation, table generation, Book IR, layout/depth contract, renderer, OpenXML validation, PDF/PNG visual QA.
   - Do not say "done" from file existence alone. A DOCX that exists but contains raw formula text, wrong source path, fallback values, or broken layout is not accepted.

## Required Quality Gates

Before saying a migrated project is acceptable, check:

- registry project code and old-module mapping are correct.
- the project is standalone: no runtime import, subprocess call, path dependency, or file read from old `C:\GitHub\jgsjdq` or another project-specific module.
- all required outputs are produced in the project output directory.
- formulas and displayed substitutions are generated from calculation atoms.
- table values and displayed text are generated from table atoms.
- no Markdown math remains in Word table cells.
- DOCX XML contains no raw `$$`, unexpected `$...$`, `\begin{...}`, or leftover LaTeX fragments such as `\frac`, `\times`, or project-specific raw commands where OMML should exist.
- OMML equation count and expected section/table/image counts are checked when relevant.
- every paragraph/formula/table block has a declared semantic role and layout/depth role.
- declared paragraph styles exist in `styles.xml` and are actually used in `document.xml`.
- unexpected color/fill tokens are absent from DOCX XML when using the formal monochrome profile.
- `w:keepNext`, `w:keepLines`, and body/list `w:numPr` counts are zero unless explicitly allowed by the current layout contract.
- renderer fallback count is zero or treated as a blocking issue.
- OpenXML validation error count is zero.
- visual QA has checked PDF/PNG pages for missing equations, black squares, color drift, overlap, truncation, bad table placement, and broken heading hierarchy.
- if LibreOffice or screenshot rendering is unavailable, perform explicit DOCX structure/XML checks and say visual QA could not be completed.

Preferred local render tools on this Windows machine:

- LibreOffice: `C:\Program Files\LibreOffice\program\soffice.exe`
- Poppler: `%USERPROFILE%\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\poppler\Library\bin\pdftoppm.exe`

## AIOps Check Pattern

Use this review frame for every pipeline:

observability signals -> anomaly detection -> stage attribution -> whitelist-only safe action -> human escalation -> feedback into rules/evals/runbooks.

Minimum artifacts:

- `pipeline_events.jsonl` for stage lifecycle.
- formula/table/layout/render audit JSON.
- stable output manifest with paths and hashes when packaging matters.
- failure-preserving logs; do not silently clean up evidence after an error.
- persistent operations records when the project needs them: `pipeline_runs`, `ops_events`, `model_runtime_metrics`, `alert_incidents`, `ops_action_audits`, `ops_runbooks`, and `quality_snapshots`.

Safe automatic actions may include retrying a render, regenerating derived artifacts, quarantining a failed output, or rebuilding a local index. Require user approval before deleting source data, changing public outputs, uploading private files, mutating legacy reference code, or hiding failed artifacts.

## Implementation Discipline

- Follow DAA: inspect old code, new contracts, tests, and current worktree before editing.
- Follow TDD where practical: add contract tests before implementation, especially for JSON schema, formula/display consistency, table text, renderer fallback, and required artifacts.
- Keep edits in small rollback units.
- Do not commit unless the user explicitly asks for commit/push.
- If the user asks for review only, stay read-only.

## Output Style

When reporting progress to the user, use concrete evidence:

- old source paths inspected
- new files changed
- JSON artifacts produced
- tests/commands run
- render artifacts checked
- remaining gaps ranked by severity

Avoid saying the migration is done just because DOCX exists. It is done only when calculation truth, display JSON, renderer audit, and visual QA agree.
