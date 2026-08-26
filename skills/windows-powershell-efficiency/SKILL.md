---
name: windows-powershell-efficiency
description: Use when executing shell, filesystem, repository, testing, build, or diagnostic operations in native Windows PowerShell. Enforces targeted queries, bounded output, literal paths, stable tool selection, and diagnosis before retry. Do not use for answer-only Windows questions that require no shell operation.
---

# Windows PowerShell Efficiency

Operate efficiently and predictably in native Windows PowerShell. Spend tool calls and context on the task, not on shell discovery, output filtering, or avoidable quoting failures.

This skill governs command execution technique. It does not grant permission to modify files, install packages, restart services, delete data, change configuration, or perform any other mutation. Follow the user's authorization, repository instructions, and higher-priority safety rules.

## Operating priorities

Optimize commands in this order:

1. Correctness and preservation of user work.
2. A precise answer to the current question.
3. Minimum scope and bounded output.
4. Native Windows compatibility.
5. Minimum retries and shell complexity.

Prefer a simple, explicit command over a clever one-liner.

## Establish environment facts once

Probe only facts that are required and not already known. During the task, retain a working map of:

- PowerShell version;
- current directory and repository root;
- available commands;
- selected Python or project runtime;
- known target paths;
- relevant working-tree state;
- previous command failures and confirmed causes.

Do not repeat an established probe unless there is concrete evidence that the environment, directory, interpreter, or tool availability changed.

When a concise initial probe is needed, use the recipe in [references/command-recipes.md](references/command-recipes.md).

## Query before exploring

Escalate investigation gradually:

1. Operate directly on a known path.
2. Search expected source or test directories.
3. Use repository-wide indexed search with task-relevant exclusions.
4. Use narrowly filtered filesystem recursion.
5. Search outside the repository only for a concrete reason.

Do not begin with an unbounded recursive listing or a whole-drive search. Prefer `git ls-files` or `rg --files` when available. Search known source directories before the repository root.

Exclude large generated or dependency directories only when they are irrelevant to the task. Do not blanket-exclude `.github`, configuration directories, logs, outputs, or editor settings when the request concerns them.

## Bound terminal output

Before every command, identify the exact question it should answer. If no precise question exists, do not run it.

Filter at the source and request only the fields, lines, files, tests, or diff sections needed for the next decision. Exploratory output should normally stay below roughly 120 lines unless the content itself is evidence the task requires.

Prefer compact modes such as `git status --short`, targeted diffs, selected object properties, and limited file ranges. Avoid formatting commands by default, but use `Format-List` or another final formatter when it is necessary to prevent property truncation or ambiguity.

Remember that `Select-Object -First` limits emitted output but may not prevent an upstream recursive provider from traversing broadly. Reduce the input scope with a known directory, filename filter, depth, or indexed search whenever scan cost matters.

## Use native PowerShell deliberately

Treat PowerShell as the active shell. Do not assume Bash commands or syntax, and do not switch to WSL, Git Bash, `cmd.exe`, or another shell unless the user requests it or the project toolchain genuinely requires it.

Use Windows paths as Windows paths:

- use `-LiteralPath` for known filesystem targets;
- use `Join-Path` to construct paths;
- use `Resolve-Path -LiteralPath` when canonical identity matters;
- quote paths containing spaces;
- avoid unnecessary `/mnt/c/...` or `/c/...` conversions.

Do not assume `&&` unless PowerShell 7 has already been confirmed. For native executables, inspect their output and `$LASTEXITCODE` before deciding whether another command is needed.

In Windows PowerShell, do not pipe a language-level `foreach (...) { ... }` statement directly into another command. Assign its results to a variable first, or wrap the statement in an explicit collecting expression, then pipe the collected result.

Treat `[ordered]@{}` as an `OrderedDictionary`, not as a `[pscustomobject]`. Do not assume `Measure-Object -Property` will read dictionary keys as object properties in Windows PowerShell 5.1. Accumulate numeric totals explicitly while constructing rows, or emit `[pscustomobject]` rows first. For status receipts, initialize failure, perform every fallible calculation, set success last, and force failure again in `catch`; never emit `PASS` together with an error. See [references/command-recipes.md](references/command-recipes.md) for the exact pattern.

Use `rg`, Git, Python, test runners, and project-specific tools for work they perform more reliably than a custom PowerShell pipeline.

## Avoid quoting and script-generation traps

Avoid large nested expressions that combine PowerShell, JSON, regex, Python, backslashes, variables, and multiple quote layers.

For short one-off multiline input, prefer a literal PowerShell here-string piped to the intended program. Create a durable script only when the logic is reusable, belongs to the task, and has a clear owner and lifecycle. Do not create mystery helper files merely to escape a difficult one-liner.

When a command develops multiple escaping layers, simplify its structure before retrying it.

## Diagnose before retrying

A failed command is evidence. Read the error, classify the failure, form one concrete hypothesis, and make one targeted correction that tests that hypothesis.

Do not rotate randomly among PowerShell, Bash, `cmd.exe`, absolute paths, alternative interpreters, or repeated directory scans. A new retry must correspond to a new, explainable hypothesis.

Use [references/error-playbook.md](references/error-playbook.md) when a failure is not immediately clear or when the first targeted correction does not resolve it.

Stop and report the issue when progress requires new authorization, a material scope change, an unavailable external dependency, or repeated attempts that no longer provide new information.

## Edit and validate proportionally

When modifications are authorized, prefer the dedicated patch or structured edit tool. Do not rewrite an entire file for a small change, and do not use broad `Get-Content | Set-Content` replacement pipelines for nontrivial edits because they can alter encoding, line endings, or unintended matches.

Preserve existing user changes and inspect only the relevant diff. Verify progressively:

1. syntax or static check;
2. directly affected test or deterministic reproduction;
3. affected module tests;
4. broader test group;
5. full suite only when justified.

Do not rerun an expensive command merely because its exit state was not read carefully. Narrow subsequent execution to the failing component whenever possible.

## Destructive-operation boundary

This skill never expands authorization for deletion, overwrite, restart, service control, dependency installation, or configuration changes.

Before an authorized destructive filesystem action:

1. resolve the exact literal target;
2. verify that it is inside the intended parent directory;
3. reject drive roots, user-profile roots, workspace roots, and repository roots as recursive targets;
4. avoid unresolved variables, globs, command substitutions, and string-built deletion commands;
5. keep discovery and deletion in one PowerShell context instead of passing computed paths to another shell.

If target identity or scope is uncertain, stop and ask rather than guessing.

## Reference routing

- Read [references/command-recipes.md](references/command-recipes.md) when exact PowerShell patterns are needed for probing, searching, reading, Git inspection, runtime selection, or progressive tests.
- Read [references/error-playbook.md](references/error-playbook.md) when classifying a failure, choosing a targeted diagnostic, or deciding whether another retry is justified.

Do not load either reference when the core rules already answer the task.

## Final self-check

Before finishing a tool-driven task, confirm:

- each command answered a specific question;
- known facts were not repeatedly rediscovered;
- search and output remained appropriately bounded;
- failures were diagnosed rather than blindly retried;
- the selected shell, paths, interpreter, and exit codes were unambiguous;
- any authorized changes were narrowly verified.
