# PowerShell Error Playbook

Use this reference after reading the actual error. Classify the failure before choosing a diagnostic or retry.

## Retry rule

A retry is justified only when it tests a concrete hypothesis. Record mentally:

```text
observed error
failure category
hypothesis
targeted correction
result
```

Do not repeat the same command or switch shells without new evidence. If a correction fails, reassess the category before trying something else.

## PATH_NOT_FOUND

Typical evidence: a literal file or directory is missing.

Use:

```powershell
Test-Path -LiteralPath $path
```

Then check the expected parent or perform a targeted filename search. Do not search the whole drive merely because one path was wrong.

## COMMAND_NOT_FOUND

Confirm availability once:

```powershell
Get-Command commandName -ErrorAction SilentlyContinue
```

If absent, inspect the project's documented toolchain or known environment. Do not install software or rotate among package managers without authorization and a verified need.

## POWERSHELL_PARSE_ERROR

Reduce nesting and separate the operation into understandable statements. Prefer variables, literal here-strings, and direct tool arguments.

Do not add more escaping layers to an already fragile expression.

## NATIVE_PROGRAM_ERROR

Read stdout, stderr, and `$LASTEXITCODE`. Distinguish a native program failure from a PowerShell pipeline or formatting issue.

Run the smallest diagnostic supported by the program. Do not rerun an expensive operation merely to learn an exit code that was already available.

## PERMISSION_ERROR

Confirm the exact target and the requested operation. Determine whether the failure is filesystem ACL, process elevation, execution policy, locked file, network permission, or application authorization.

Do not work around permission controls, elevate, or broaden access unless the user has authorized the required action.

## ENCODING_ERROR

Inspect the existing file's encoding and line-ending behavior before editing. Avoid whole-file PowerShell rewrite pipelines for a small change.

After an authorized edit, inspect the targeted diff to ensure a logical change did not become a whole-file encoding conversion.

## DEPENDENCY_ERROR

First confirm that the intended project environment and interpreter are active. Inspect the established lockfile or dependency workflow.

Do not alternate randomly among `pip`, `py -m pip`, `python -m pip`, `uv`, Poetry, and Conda. Do not install or upgrade dependencies without authorization.

## TEST_FAILURE

Read the first meaningful assertion, exception, or traceback. Reproduce the smallest failing test or input, then correct the verified cause.

Do not repeatedly rerun the full suite. Expand validation only after the focused failure is understood or fixed.

## UNKNOWN

Collect one additional bounded diagnostic that can distinguish between plausible categories. Examples include the exact resolved path, command source, interpreter path, process exit code, or a short relevant log section.

If the next diagnostic would require broad scanning, mutation, new authority, or significant cost, stop and explain what is missing.

## Stop conditions

Stop retrying and report clearly when:

- the same failure recurs without a new hypothesis;
- the required action is outside the user's authorization;
- resolving the issue would materially expand scope;
- an external dependency or credential is unavailable;
- further commands would be destructive or disproportionately expensive;
- available evidence is insufficient to distinguish the remaining causes safely.
